"""
Custom exception hierarchy for the AI Contract Risk Analyzer.
All domain-specific errors inherit from ContractAnalyzerError,
making it easy to catch at the API boundary.
"""


class ContractAnalyzerError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# ─── Document / File Errors ──────────────────────────────────────────────────

class UnsupportedFileTypeError(ContractAnalyzerError):
    """Raised when an uploaded file is not PDF or DOCX."""

    def __init__(self, filename: str):
        super().__init__(
            message=f"Unsupported file type: '{filename}'. Only PDF and DOCX are accepted.",
            status_code=415,
        )


class DocumentExtractionError(ContractAnalyzerError):
    """Raised when text extraction from a document fails."""

    def __init__(self, filename: str, detail: str = ""):
        msg = f"Failed to extract text from '{filename}'."
        if detail:
            msg += f" Detail: {detail}"
        super().__init__(message=msg, status_code=422)


class EmptyDocumentError(ContractAnalyzerError):
    """Raised when an uploaded document contains no extractable text."""

    def __init__(self, filename: str):
        super().__init__(
            message=f"Document '{filename}' appears to be empty or contains no extractable text.",
            status_code=422,
        )


# ─── RAG / Vector Store Errors ───────────────────────────────────────────────

class DocumentNotFoundError(ContractAnalyzerError):
    """Raised when a contract ID does not exist in the vector store."""

    def __init__(self, contract_id: str):
        super().__init__(
            message=f"No contract found with ID: '{contract_id}'. Please upload the document first.",
            status_code=404,
        )


class EmbeddingError(ContractAnalyzerError):
    """Raised when generating embeddings fails."""

    def __init__(self, detail: str = ""):
        msg = "Failed to generate embeddings."
        if detail:
            msg += f" Detail: {detail}"
        super().__init__(message=msg, status_code=502)


class VectorStoreError(ContractAnalyzerError):
    """Raised when ChromaDB operations fail."""

    def __init__(self, detail: str = ""):
        msg = "Vector store operation failed."
        if detail:
            msg += f" Detail: {detail}"
        super().__init__(message=msg, status_code=503)


# ─── LLM / Analysis Errors ───────────────────────────────────────────────────

class LLMError(ContractAnalyzerError):
    """Raised when the LLM API call fails."""

    def __init__(self, detail: str = ""):
        msg = "LLM request failed."
        if detail:
            msg += f" Detail: {detail}"
        super().__init__(message=msg, status_code=502)


class AnalysisError(ContractAnalyzerError):
    """Raised when contract risk analysis fails."""

    def __init__(self, detail: str = ""):
        msg = "Contract analysis failed."
        if detail:
            msg += f" Detail: {detail}"
        super().__init__(message=msg, status_code=500)
