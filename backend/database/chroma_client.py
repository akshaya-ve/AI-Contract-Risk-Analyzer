"""
ChromaDB persistent client — Singleton pattern.

A single ChromaDB client is shared across the entire application lifecycle.
Using a module-level singleton avoids re-initialising the database connection
on every request, which is expensive and can cause file-lock issues on Windows.
"""

from functools import lru_cache

import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.PersistentClient:
    """
    Returns a cached, persistent ChromaDB client.

    The client is initialised once and reused for all subsequent calls.
    Data is persisted to disk at CHROMA_PERSIST_DIR so documents survive
    server restarts.

    Returns:
        chromadb.PersistentClient: Ready-to-use ChromaDB client.
    """
    settings = get_settings()

    logger.info(f"Initialising ChromaDB at: {settings.CHROMA_PERSIST_DIR}")

    client = chromadb.PersistentClient(
        path=settings.CHROMA_PERSIST_DIR,
        settings=ChromaSettings(
            anonymized_telemetry=False,   # disable usage telemetry
            allow_reset=True,             # needed for test teardown
        ),
    )

    logger.info("ChromaDB client initialised successfully.")
    return client


def get_or_create_collection(
    client: chromadb.PersistentClient,
    collection_name: str,
) -> chromadb.Collection:
    """
    Get an existing ChromaDB collection or create it if it doesn't exist.

    Collections are the ChromaDB equivalent of a table — each collection
    holds embeddings + metadata + documents.

    Args:
        client:          The persistent ChromaDB client.
        collection_name: Name of the collection (from settings).

    Returns:
        chromadb.Collection: The ready-to-use collection.
    """
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},  # cosine similarity for semantic search
    )
    logger.debug(f"Collection '{collection_name}' ready (count={collection.count()}).")
    return collection
