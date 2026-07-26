"""
Document Service — orchestrates the full contract upload pipeline.

Responsibilities:
  1. Validate file type and size.
  2. Save the raw file to the upload directory.
  3. Extract text (PDF/DOCX) via text_extractor.
  4. Chunk the extracted text via chunker.
  5. Embed and store chunks in ChromaDB via vector_store.
  6. Return an UploadResponse with metadata for the API layer.

The service generates a deterministic contract_id from the filename +
file content hash so that re-uploading the same file overwrites the
previous version rather than creating a duplicate.

This module has NO knowledge of HTTP — it works purely with domain
objects and raises domain exceptions, keeping routes thin.
"""

import hashlib
import os
from pathlib import Path

import aiofiles

from backend.config import get_settings
from backend.models.response_models import UploadResponse
from backend.rag.chunker import chunk_document
from backend.rag.vector_store import delete_contract, store_chunks
from backend.utils.exceptions import DocumentExtractionError, EmptyDocumentError
from backend.utils.logger import get_logger
from backend.utils.text_extractor import ExtractionResult, extract_document, validate_file

logger = get_logger(__name__)

# ─── Filename Registry ───────────────────────────────────────────────────────
# Maps contract_id → original filename so the analysis service can display
# the real filename in the report (contract_id is a hash, not readable).
_filename_registry: dict[str, str] = {}


# ─── Public API ──────────────────────────────────────────────────────────────


async def process_uploaded_file(
    filename: str,
    file_content: bytes,
) -> UploadResponse:
    """
    Full upload pipeline: validate → save → extract → chunk → embed → store.

    Args:
        filename:     Original filename from the HTTP upload.
        file_content: Raw bytes of the uploaded file.

    Returns:
        UploadResponse with contract_id, page_count, chunk_count, etc.

    Raises:
        UnsupportedFileTypeError: Invalid extension.
        DocumentExtractionError:  Extraction or size failure.
        EmptyDocumentError:       No text found in document.
        VectorStoreError:         ChromaDB write failure.
        EmbeddingError:           Embedding API failure.
    """
    settings = get_settings()

    # ── 1. Validate before touching disk ─────────────────────────────────────
    validate_file(
        filename=filename,
        file_size_bytes=len(file_content),
        max_size_mb=settings.MAX_FILE_SIZE_MB,
        allowed_extensions=settings.ALLOWED_EXTENSIONS,
    )
    logger.info(f"Processing upload: '{filename}' ({len(file_content)/1024:.1f} KB)")

    # ── 2. Generate deterministic contract_id ─────────────────────────────────
    contract_id = _generate_contract_id(filename, file_content)
    logger.info(f"contract_id = '{contract_id}'")

    # ── 3. Save file to disk ──────────────────────────────────────────────────
    file_path = await _save_file(
        file_content=file_content,
        filename=filename,
        contract_id=contract_id,
        upload_dir=settings.UPLOAD_DIR,
    )

    # ── 4. Extract text ───────────────────────────────────────────────────────
    extraction: ExtractionResult = extract_document(file_path)
    logger.info(
        f"Extracted: {extraction.total_pages} pages, "
        f"{extraction.total_chars:,} chars"
    )

    # ── 5. Chunk document ─────────────────────────────────────────────────────
    chunks = chunk_document(
        extraction_result=extraction,
        contract_id=contract_id,
    )
    logger.info(f"Chunked into {len(chunks)} chunks")

    # ── 6. Delete stale data if contract already exists (re-upload) ───────────
    delete_contract(contract_id)

    # ── 7. Embed + store in ChromaDB ─────────────────────────────────────────
    stored_count = store_chunks(chunks)
    logger.info(f"Stored {stored_count} chunks in ChromaDB")

    # ── 8. Register filename for later retrieval by analysis service ──────────────
    _filename_registry[contract_id] = filename

    # ── 9. Build response ───────────────────────────────────────────────────
    return UploadResponse(
        contract_id=contract_id,
        filename=filename,
        file_size_kb=round(len(file_content) / 1024, 2),
        page_count=extraction.total_pages,
        chunk_count=stored_count,
        message="Contract uploaded and indexed successfully.",
    )


def get_upload_path(contract_id: str, filename: str) -> Path:
    """
    Return the full filesystem path where an uploaded contract is stored.

    Args:
        contract_id: The contract's unique identifier.
        filename:    The original filename.

    Returns:
        Absolute Path to the stored file.
    """
    settings = get_settings()
    suffix = Path(filename).suffix.lower()
    return Path(settings.UPLOAD_DIR) / f"{contract_id}{suffix}"


def get_filename(contract_id: str) -> str:
    """
    Look up the original filename for a given contract_id.

    Args:
        contract_id: The contract identifier.

    Returns:
        Original filename string, or the contract_id itself as fallback.
    """
    return _filename_registry.get(contract_id, contract_id)


# ─── Private Helpers ─────────────────────────────────────────────────────────


def _generate_contract_id(filename: str, file_content: bytes) -> str:
    """
    Generate a deterministic 12-character hex ID from filename + content hash.

    Using a content-based ID means:
      - Re-uploading the same file → same ID → overwrites old embeddings.
      - Uploading a modified version of the same filename → different ID.

    Args:
        filename:     Original filename.
        file_content: Raw file bytes.

    Returns:
        12-character lowercase hex string.
    """
    combined = filename.encode("utf-8") + file_content
    return hashlib.sha256(combined).hexdigest()[:12]


async def _save_file(
    file_content: bytes,
    filename: str,
    contract_id: str,
    upload_dir: str,
) -> Path:
    """
    Asynchronously write uploaded file bytes to the upload directory.

    File is stored as <contract_id><original_extension> to avoid
    filename collisions and make cleanup trivial.

    Args:
        file_content: Raw bytes to write.
        filename:     Original filename (used for extension).
        contract_id:  Used as the stored filename stem.
        upload_dir:   Directory to write into.

    Returns:
        Path to the saved file.

    Raises:
        DocumentExtractionError: If the write fails.
    """
    os.makedirs(upload_dir, exist_ok=True)
    suffix = Path(filename).suffix.lower()
    file_path = Path(upload_dir) / f"{contract_id}{suffix}"

    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)
        logger.debug(f"File saved to: {file_path}")
        return file_path
    except OSError as e:
        raise DocumentExtractionError(filename, f"Failed to save file: {e}") from e
