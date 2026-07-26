"""
SQLAlchemy ORM models for Users, Contracts, Clause Analyses, Chat History, and Audit Logs.
"""

from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship

from backend.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contracts = relationship("Contract", back_populates="owner", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String(64), primary_key=True)  # contract_id hash
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_size_kb = Column(Float, nullable=False)
    page_count = Column(Integer, default=1)
    chunk_count = Column(Integer, default=0)
    
    # Analysis summary fields
    overall_risk_level = Column(String(20), default="Pending")
    risk_score = Column(Integer, default=0)
    executive_summary = Column(Text, nullable=True)
    key_concerns = Column(JSON, default=list)
    missing_clauses = Column(JSON, default=list)
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    analyzed_at = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="contracts")
    clauses = relationship("ClauseAnalysis", back_populates="contract", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="contract", cascade="all, delete-orphan")


class ClauseAnalysis(Base):
    __tablename__ = "clause_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = Column(String(64), ForeignKey("contracts.id"), nullable=False)
    clause_type = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)  # Found, Not Found, Needs Review
    risk_level = Column(String(20), nullable=False)  # Low, Medium, High, Unknown
    confidence_score = Column(Float, default=0.95)
    summary = Column(Text, nullable=False)
    extracted_text = Column(Text, nullable=True)
    suggested_improvement = Column(Text, nullable=True)
    page_reference = Column(String(100), nullable=True)

    contract = relationship("Contract", back_populates="clauses")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = Column(String(64), ForeignKey("contracts.id"), nullable=False)
    sender = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # List of source docs
    timestamp = Column(DateTime, default=datetime.utcnow)

    contract = relationship("Contract", back_populates="chat_messages")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # UPLOAD, ANALYZE, CHAT, LOGIN, etc.
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
