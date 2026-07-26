"""
Document chunking — splits extracted contract text into overlapping chunks
for embedding and storage in ChromaDB.

Why RecursiveCharacterTextSplitter?
  Legal contracts have deeply nested structure: sections → sub-sections →
  paragraphs → sentences. The recursive splitter tries to honour natural
  boundaries (paragraphs, then sentences, then words) before hard-splitting
  on character count, producing far more semantically coherent chunks than a
  naive fixed-size splitter.

Each chunk is enriched with metadata so ChromaDB can surface accurate source
references in the chat UI (contract_id, page_number, chunk_index).
"""

from dataclasses import dataclass
from typing import Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import get_settings
from backend.utils.logger import get_logger
from backend.utils.text_extractor import ExtractionResult

logger = get_logger(__name__)


# ─── Data Structures ──────────────────────────────────────────────────────────


@dataclass
class DocumentChunk:
    """
    A single chunk ready for embedding and storage.

    Attributes:
        chunk_id:    Unique ID within this contract (e.g. "abc123_chunk_0").
        content:     The actual text of this chunk.
        contract_id: Parent contract identifier.
        page_number: Source page/section number (for UI citation).
        chunk_index: Position in the document (0-indexed).
        filename:    Original filename (stored in metadata for display).
    """

    chunk_id: str
    content: str
    contract_id: str
    page_number: Optional[int]
    chunk_index: int
    filename: str

    def to_metadata(self) -> dict:
        """Return a flat metadata dict for ChromaDB storage."""
        return {
            "contract_id": self.contract_id,
            "page_number": self.page_number or 0,
            "chunk_index": self.chunk_index,
            "filename": self.filename,
        }


# ─── Chunker ─────────────────────────────────────────────────────────────────


def chunk_document(
    extraction_result: ExtractionResult,
    contract_id: str,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> list[DocumentChunk]:
    """
    Split a contract's full text into overlapping chunks for RAG.

    The splitter tries separators in this priority order:
      1. Double newline      → paragraph boundary
      2. Single newline      → line boundary
      3. Period + space      → sentence boundary
      4. Space               → word boundary
      5. Character           → hard split (last resort)

    Args:
        extraction_result: Output of text_extractor.extract_document().
        contract_id:       Unique identifier for this contract.
        chunk_size:        Override default CHUNK_SIZE from settings.
        chunk_overlap:     Override default CHUNK_OVERLAP from settings.

    Returns:
        List of DocumentChunk objects ready for embedding.

    Raises:
        ValueError: If the document has no text after extraction.
    """
    settings = get_settings()
    effective_chunk_size = chunk_size or settings.CHUNK_SIZE
    effective_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    if not extraction_result.full_text.strip():
        raise ValueError(
            f"Cannot chunk empty document: {extraction_result.filename}"
        )

    logger.info(
        f"Chunking '{extraction_result.filename}' | "
        f"chunk_size={effective_chunk_size}, overlap={effective_overlap}"
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=effective_chunk_size,
        chunk_overlap=effective_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        is_separator_regex=False,
    )

    raw_chunks: list[str] = splitter.split_text(extraction_result.full_text)

    # ── Build DocumentChunk objects with metadata ────────────────────────────
    chunks: list[DocumentChunk] = []
    for idx, raw_text in enumerate(raw_chunks):
        # Infer page number from [Page N] headers embedded by the extractor
        page_number = _infer_page_number(raw_text, extraction_result)

        chunk = DocumentChunk(
            chunk_id=f"{contract_id}_chunk_{idx}",
            content=raw_text.strip(),
            contract_id=contract_id,
            page_number=page_number,
            chunk_index=idx,
            filename=extraction_result.filename,
        )
        chunks.append(chunk)

    logger.info(
        f"Chunking complete: {len(chunks)} chunks from "
        f"{extraction_result.total_pages} pages"
    )
    return chunks


# ─── Private Helpers ─────────────────────────────────────────────────────────


def _infer_page_number(
    chunk_text: str,
    extraction_result: ExtractionResult,
) -> Optional[int]:
    """
    Attempt to extract the page number from a [Page N] header in the chunk text.

    The text_extractor embeds '[Page N]' markers between pages. If a chunk
    starts with or contains such a marker, we parse the number from it.
    Falls back to None if no marker is present (the chunk spans a page
    boundary or originates from a DOCX section).

    Args:
        chunk_text:        Text content of the chunk.
        extraction_result: Full extraction result (used for total_pages fallback).

    Returns:
        Page number as int, or None if not determinable.
    """
    import re

    # Look for [Page N] anywhere in the chunk (the marker may not be at the start
    # if chunk_overlap pulls in text from the previous page)
    match = re.search(r"\[Page\s+(\d+)\]", chunk_text)
    if match:
        page_num = int(match.group(1))
        # Sanity check: page number must be within the document's range
        if 1 <= page_num <= extraction_result.total_pages:
            return page_num

    return None
