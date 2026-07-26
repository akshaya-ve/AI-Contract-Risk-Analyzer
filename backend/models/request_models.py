"""
Request models (Pydantic schemas) for all API endpoints.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Request schema for user registration."""
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, description="Password (min 6 chars)")
    full_name: Optional[str] = Field(None, description="Full name of the user")

    @field_validator("email")
    @classmethod
    def lower_email(cls, v: str) -> str:
        return v.lower().strip()


class UserLogin(BaseModel):
    """Request schema for user login."""
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., description="User password")

    @field_validator("email")
    @classmethod
    def lower_email(cls, v: str) -> str:
        return v.lower().strip()


class AnalyzeRequest(BaseModel):
    """Request body for POST /analyze."""
    contract_id: str = Field(
        ...,
        description="Unique contract identifier returned from /upload.",
        min_length=1,
    )

    @field_validator("contract_id")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class ChatRequest(BaseModel):
    """Request body for POST /chat."""
    contract_id: str = Field(..., description="Contract ID")
    question: str = Field(
        ...,
        description="Natural-language question about the contract.",
        min_length=3,
        max_length=1000,
    )

    @field_validator("contract_id", "question")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()
