"""
Application configuration using pydantic-settings.
All settings are loaded from environment variables / .env file.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central settings object. Values are read from environment variables
    or the .env file at the project root.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Application ────────────────────────────────────────────────────────
    APP_NAME: str = "AI Contract Risk Analyzer"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # ─── Security / Auth ────────────────────────────────────────────────────
    SECRET_KEY: str = "super-secret-key-change-in-production-contract-analyzer-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ─── Database ────────────────────────────────────────────────────────────
    # Defaults to SQLite for immediate local zero-config testing; set to postgresql:// in .env for prod
    DATABASE_URL: str = "sqlite:///./contract_analyzer.db"

    # ─── Server ──────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8501",
    ]

    # ─── LLM Provider ────────────────────────────────────────────────────────
    LLM_PROVIDER: Literal["gemini", "openai"] = "gemini"

    # Google Gemini
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"

    # OpenAI (optional)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ─── ChromaDB ────────────────────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "contracts"

    # ─── File Upload ─────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    REPORTS_DIR: str = "./reports"
    MAX_FILE_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx"]

    # ─── RAG / Chunking ──────────────────────────────────────────────────────
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RETRIEVER_TOP_K: int = 5

    # ─── 12 Monitored Risk Clauses ───────────────────────────────────────────
    RISK_CLAUSES: list[str] = [
        "Termination Clause",
        "Confidentiality",
        "Auto Renewal",
        "Payment Terms",
        "Unlimited Liability",
        "Indemnification",
        "Non-Compete",
        "Intellectual Property",
        "Force Majeure",
        "Governing Law",
        "Dispute Resolution",
        "Jurisdiction",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
