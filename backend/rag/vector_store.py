"""
Vector store CRUD operations — ChromaDB interface for the RAG pipeline.

Responsibilities:
  - Store document chunks + their embeddings into ChromaDB.
  - Retrieve the most semantically similar chunks for a query.
  - Delete all chunks belonging to a given contract (for re-upload scenarios).
  - Check whether a contract already exists in the store.

All operations go through this module so the rest of the codebase never
imports chromadb directly — making it easy to swap the vector store later.
"""

from typing import Optional

from backend.config import get_settings
from backend.database.chroma_client import get_chroma_client, get_or_create_collection
from backend.models.response_models import SourceDocument
from backend.rag.chunker import DocumentChunk
from backend.rag.embeddings import embed_query, embed_texts
from backend.utils.exceptions import DocumentNotFoundError, VectorStoreError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


# ─── Write Operations ────────────────────────────────────────────────────────


def store_chunks(chunks: list[DocumentChunk]) -> int:
    """
    Embed and store a list of document chunks in ChromaDB.

    Uses batched upserts to handle large contracts efficiently.
    If chunks for the same contract_id already exist, they are overwritten
    (upsert semantics) — this covers the re-upload case.

    Args:
        chunks: List of DocumentChunk objects from the chunker.

    Returns:
        Number of chunks successfully stored.

    Raises:
        VectorStoreError: On ChromaDB write failure.
    """
    if not chunks:
        logger.warning("store_chunks() called with empty chunk list.")
        return 0

    settings = get_settings()
    contract_id = chunks[0].contract_id

    logger.info(
        f"Storing {len(chunks)} chunks for contract '{contract_id}' → ChromaDB"
    )

    try:
        client = get_chroma_client()
        collection = get_or_create_collection(client, settings.CHROMA_COLLECTION_NAME)

        # ── Embed all chunks in one batched call ─────────────────────────────
        texts = [chunk.content for chunk in chunks]
        embeddings = embed_texts(texts)

        ids = [chunk.chunk_id for chunk in chunks]
        metadatas = [chunk.to_metadata() for chunk in chunks]

        # ── Upsert (add or update) ───────────────────────────────────────────
        # ChromaDB upsert handles duplicates gracefully
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        logger.info(f"Stored {len(chunks)} chunks for contract '{contract_id}'.")
        return len(chunks)

    except VectorStoreError:
        raise
    except Exception as e:
        raise VectorStoreError(
            f"Failed to store chunks for contract '{contract_id}': {e}"
        ) from e


# ─── Read Operations ─────────────────────────────────────────────────────────


def retrieve_relevant_chunks(
    contract_id: str,
    query: str,
    top_k: Optional[int] = None,
) -> list[SourceDocument]:
    """
    Retrieve the top-K most semantically similar chunks for a query.

    Performs:
      1. Embed the query with the same model used at index time.
      2. Query ChromaDB with a contract_id filter (scoped to this contract).
      3. Return results as SourceDocument objects (used by the RAG pipeline
         and surfaced directly in the ChatResponse to the frontend).

    Args:
        contract_id: The contract to search within.
        query:       The user's question or clause type to search for.
        top_k:       Number of results to return (defaults to RETRIEVER_TOP_K).

    Returns:
        List of SourceDocument ordered by relevance (most similar first).

    Raises:
        DocumentNotFoundError: If no chunks exist for this contract_id.
        VectorStoreError:      On ChromaDB query failure.
    """
    settings = get_settings()
    k = top_k or settings.RETRIEVER_TOP_K

    # ── Verify the contract exists ───────────────────────────────────────────
    if not contract_exists(contract_id):
        raise DocumentNotFoundError(contract_id)

    logger.info(
        f"Retrieving top-{k} chunks for contract '{contract_id}' | "
        f"query='{query[:60]}...'"
    )

    try:
        client = get_chroma_client()
        collection = get_or_create_collection(client, settings.CHROMA_COLLECTION_NAME)

        # ── Embed the query ──────────────────────────────────────────────────
        query_vector = embed_query(query)

        # ── Query with a where filter scoped to this contract ────────────────
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=k,
            where={"contract_id": {"$eq": contract_id}},
            include=["documents", "metadatas", "distances"],
        )

        # ── Parse ChromaDB response ──────────────────────────────────────────
        source_docs: list[SourceDocument] = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc_text, meta, distance in zip(documents, metadatas, distances):
            # ChromaDB cosine distance → similarity score (0 = identical, 2 = opposite)
            # Convert: similarity = 1 - (distance / 2) to get a 0–1 score
            similarity = round(1.0 - (distance / 2.0), 4)

            source_docs.append(
                SourceDocument(
                    content=doc_text,
                    page=meta.get("page_number") or None,
                    chunk_index=meta.get("chunk_index"),
                    relevance_score=similarity,
                )
            )

        logger.info(
            f"Retrieved {len(source_docs)} chunks for contract '{contract_id}'."
        )
        return source_docs

    except (DocumentNotFoundError, VectorStoreError):
        raise
    except Exception as e:
        raise VectorStoreError(
            f"Query failed for contract '{contract_id}': {e}"
        ) from e


# ─── Utility Operations ──────────────────────────────────────────────────────


def contract_exists(contract_id: str) -> bool:
    """
    Check whether any chunks for a contract_id exist in ChromaDB.

    Args:
        contract_id: The contract identifier to check.

    Returns:
        True if at least one chunk exists, False otherwise.
    """
    try:
        settings = get_settings()
        client = get_chroma_client()
        collection = get_or_create_collection(client, settings.CHROMA_COLLECTION_NAME)

        results = collection.get(
            where={"contract_id": {"$eq": contract_id}},
            limit=1,
            include=[],   # we only need to know if results exist
        )
        exists = len(results.get("ids", [])) > 0
        logger.debug(f"contract_exists('{contract_id}') → {exists}")
        return exists

    except Exception as e:
        logger.error(f"contract_exists check failed: {e}")
        return False


def get_chunk_count(contract_id: str) -> int:
    """
    Return the total number of chunks stored for a given contract.

    Args:
        contract_id: The contract identifier.

    Returns:
        Integer chunk count (0 if not found).
    """
    try:
        settings = get_settings()
        client = get_chroma_client()
        collection = get_or_create_collection(client, settings.CHROMA_COLLECTION_NAME)

        results = collection.get(
            where={"contract_id": {"$eq": contract_id}},
            include=[],
        )
        count = len(results.get("ids", []))
        logger.debug(f"get_chunk_count('{contract_id}') → {count}")
        return count

    except Exception as e:
        logger.error(f"get_chunk_count failed: {e}")
        return 0


def delete_contract(contract_id: str) -> bool:
    """
    Delete all chunks belonging to a contract from ChromaDB.

    Used when a contract is re-uploaded (to avoid stale data).

    Args:
        contract_id: The contract to delete.

    Returns:
        True if deletion succeeded, False otherwise.
    """
    try:
        settings = get_settings()
        client = get_chroma_client()
        collection = get_or_create_collection(client, settings.CHROMA_COLLECTION_NAME)

        collection.delete(where={"contract_id": {"$eq": contract_id}})
        logger.info(f"Deleted all chunks for contract '{contract_id}'.")
        return True

    except Exception as e:
        logger.error(f"Failed to delete contract '{contract_id}': {e}")
        return False


def retrieve_chunks_as_context(
    contract_id: str,
    query: str,
    top_k: Optional[int] = None,
) -> tuple[str, list[SourceDocument]]:
    """
    High-level helper: retrieve chunks and format them as a single context string.

    This is what the RAG pipeline's prompt template receives as {context}.

    Args:
        contract_id: The contract to search.
        query:       The query to search for.
        top_k:       Number of chunks to retrieve.

    Returns:
        Tuple of (context_string, source_documents).
        context_string: numbered, formatted chunks for the LLM prompt.
        source_documents: raw SourceDocument objects for the API response.
    """
    source_docs = retrieve_relevant_chunks(contract_id, query, top_k)

    context_parts: list[str] = []
    for i, doc in enumerate(source_docs, start=1):
        page_info = f" [Page {doc.page}]" if doc.page else ""
        context_parts.append(f"[Excerpt {i}{page_info}]\n{doc.content}")

    context_string = "\n\n---\n\n".join(context_parts)
    return context_string, source_docs
