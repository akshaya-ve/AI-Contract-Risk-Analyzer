"""
Response models (Pydantic schemas) for all API endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    UNKNOWN = "Unknown"


class ClauseStatus(str, Enum):
    FOUND = "Found"
    NOT_FOUND = "Not Found"
    NEEDS_REVIEW = "Needs Review"


# ─── Auth Responses ──────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime

    @classmethod
    def from_orm_user(cls, user: Any) -> "UserResponse":
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
        )


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ─── Upload Response ─────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    contract_id: str
    filename: str
    file_size_kb: float
    page_count: int
    chunk_count: int
    message: str = "Contract uploaded and indexed successfully."
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


# ─── Risk Clause ──────────────────────────────────────────────────────────────

class RiskClause(BaseModel):
    clause_type: str
    status: ClauseStatus
    risk_level: RiskLevel
    confidence_score: float = Field(default=0.92, ge=0.0, le=1.0)
    summary: str
    extracted_text: Optional[str] = None
    suggested_improvement: Optional[str] = None
    page_reference: Optional[str] = None


class MissingClause(BaseModel):
    clause_type: str
    importance: str
    recommendation: str


# ─── Analysis Report ─────────────────────────────────────────────────────────

class AnalysisReport(BaseModel):
    contract_id: str
    filename: str
    overall_risk_level: RiskLevel
    risk_score: int = Field(ge=0, le=100)
    executive_summary: str
    clauses: list[RiskClause] = Field(default_factory=list)
    missing_clauses: list[MissingClause] = Field(default_factory=list)
    key_concerns: list[str] = Field(default_factory=list)
    key_obligations: list[str] = Field(default_factory=list)
    key_deadlines: list[str] = Field(default_factory=list)
    financial_commitments: list[str] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class ContractListItem(BaseModel):
    id: str
    filename: str
    file_size_kb: float
    page_count: int
    overall_risk_level: str
    risk_score: int
    uploaded_at: datetime
    analyzed_at: Optional[datetime] = None


class RisksResponse(BaseModel):
    contract_id: str
    overall_risk_level: RiskLevel
    risk_score: int
    clauses: list[RiskClause]
    missing_clauses: list[MissingClause]


class SummaryResponse(BaseModel):
    contract_id: str
    filename: str
    overall_risk_level: RiskLevel
    risk_score: int
    executive_summary: str
    key_concerns: list[str]
    key_obligations: list[str] = Field(default_factory=list)
    key_deadlines: list[str] = Field(default_factory=list)
    financial_commitments: list[str] = Field(default_factory=list)
    analyzed_at: datetime


# ─── Chat Response ───────────────────────────────────────────────────────────

class SourceDocument(BaseModel):
    content: str
    page: Optional[int] = None
    chunk_index: Optional[int] = None
    relevance_score: Optional[float] = None


class ChatResponse(BaseModel):
    contract_id: str
    question: str
    answer: str
    confidence: float = 0.95
    sources: list[SourceDocument] = Field(default_factory=list)
    answered_at: datetime = Field(default_factory=datetime.utcnow)


# ─── Analytics & Admin Responses ──────────────────────────────────────────────

class AnalyticsResponse(BaseModel):
    total_contracts: int
    average_risk_score: float
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    risk_distribution: dict[str, int]
    clause_frequency: dict[str, int]
    monthly_uploads: list[dict[str, Any]]


class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_contracts: int
    total_chunks: int
    total_storage_mb: float
    recent_logs: list[dict[str, Any]]


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str
    version: str
    llm_provider: str


class ErrorResponse(BaseModel):
    error: str
    type: str
