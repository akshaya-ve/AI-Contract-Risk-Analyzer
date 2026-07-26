"""
Embedding model factory.

Supports two providers, selected via the LLM_PROVIDER environment variable:
  - "gemini"  → GoogleGenerativeAIEmbeddings (text-embedding-004)
  - "openai"  → OpenAIEmbeddings            (text-embedding-3-small)

The factory returns a LangChain-compatible embedding object, which means
the rest of the RAG pipeline (vector_store, pipeline) is 100% provider-agnostic.

Design:
  - @lru_cache ensures the embedding model is instantiated once per process.
  - Raises clear errors if the required API key is missing.
  - The LangChain Embeddings interface exposes:
      embed_documents(texts: list[str]) -> list[list[float]]
      embed_query(text: str)            -> list[float]
"""

from functools import lru_cache
from typing import Union

from langchain_core.embeddings import Embeddings

from backend.config import get_settings
from backend.utils.exceptions import EmbeddingError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_embedding_model() -> Embeddings:
    """
    Returns a cached LangChain-compatible embedding model.

    The model is chosen based on the LLM_PROVIDER setting:
      - "gemini" → GoogleGenerativeAIEmbeddings
      - "openai" → OpenAIEmbeddings

    Returns:
        A LangChain Embeddings instance.

    Raises:
        EmbeddingError: If the required API key is not configured.
    """
    settings = get_settings()
    provider = settings.LLM_PROVIDER.lower()

    logger.info(f"Loading embedding model for provider: '{provider}'")

    if provider == "gemini":
        return _load_gemini_embeddings(settings)
    elif provider == "openai":
        return _load_openai_embeddings(settings)
    else:
        raise EmbeddingError(
            f"Unknown LLM_PROVIDER: '{provider}'. Must be 'gemini' or 'openai'."
        )


# ─── Provider Loaders ────────────────────────────────────────────────────────


def _load_gemini_embeddings(settings) -> Embeddings:
    """Initialise Google Generative AI embeddings."""
    if not settings.GOOGLE_API_KEY:
        raise EmbeddingError(
            "GOOGLE_API_KEY is not set. "
            "Get your key at https://aistudio.google.com/app/apikey"
        )

    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        model = GoogleGenerativeAIEmbeddings(
            model=settings.GEMINI_EMBEDDING_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
        )
        logger.info(
            f"Gemini embedding model loaded: {settings.GEMINI_EMBEDDING_MODEL}"
        )
        return model

    except ImportError as e:
        raise EmbeddingError(
            "langchain-google-genai is not installed. "
            "Run: pip install langchain-google-genai"
        ) from e
    except Exception as e:
        raise EmbeddingError(f"Failed to load Gemini embeddings: {e}") from e


def _load_openai_embeddings(settings) -> Embeddings:
    """Initialise OpenAI embeddings."""
    if not settings.OPENAI_API_KEY:
        raise EmbeddingError(
            "OPENAI_API_KEY is not set. "
            "Get your key at https://platform.openai.com/api-keys"
        )

    try:
        from langchain_openai import OpenAIEmbeddings

        model = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
        )
        logger.info(
            f"OpenAI embedding model loaded: {settings.OPENAI_EMBEDDING_MODEL}"
        )
        return model

    except ImportError as e:
        raise EmbeddingError(
            "langchain-openai is not installed. "
            "Run: pip install langchain-openai"
        ) from e
    except Exception as e:
        raise EmbeddingError(f"Failed to load OpenAI embeddings: {e}") from e


# ─── Utility ─────────────────────────────────────────────────────────────────


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Convenience wrapper: embed a list of text strings.

    Args:
        texts: Non-empty list of strings to embed.

    Returns:
        List of float vectors, one per input text.

    Raises:
        EmbeddingError: On API failure or empty input.
    """
    if not texts:
        raise EmbeddingError("embed_texts() called with an empty list.")

    try:
        model = get_embedding_model()
        vectors = model.embed_documents(texts)
        logger.debug(f"Embedded {len(texts)} texts → vectors of dim {len(vectors[0])}")
        return vectors
    except EmbeddingError:
        raise
    except Exception as e:
        raise EmbeddingError(str(e)) from e


def embed_query(query: str) -> list[float]:
    """
    Convenience wrapper: embed a single query string.

    Uses embed_query() (not embed_documents()) — some providers optimise
    query embeddings separately from document embeddings.

    Args:
        query: The user's question or search text.

    Returns:
        A single float vector.

    Raises:
        EmbeddingError: On API failure.
    """
    if not query.strip():
        raise EmbeddingError("embed_query() called with an empty string.")

    try:
        model = get_embedding_model()
        vector = model.embed_query(query)
        logger.debug(f"Query embedded → dim={len(vector)}")
        return vector
    except EmbeddingError:
        raise
    except Exception as e:
        raise EmbeddingError(str(e)) from e
