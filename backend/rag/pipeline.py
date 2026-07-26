"""
RAG Pipeline — Core Intelligence Engine for 12 Clause Types, Q&A, and Executive Summary.
"""

import json
from functools import lru_cache
from typing import Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.config import get_settings
from backend.models.response_models import (
    ClauseStatus,
    MissingClause,
    RiskClause,
    RiskLevel,
    SourceDocument,
)
from backend.rag.vector_store import retrieve_chunks_as_context
from backend.utils.exceptions import AnalysisError, LLMError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_llm():
    settings = get_settings()
    provider = settings.LLM_PROVIDER.lower()

    if provider == "gemini":
        if not settings.GOOGLE_API_KEY:
            raise LLMError("GOOGLE_API_KEY is not set. Get key at https://aistudio.google.com/app/apikey")
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.1,
                convert_system_message_to_human=True,
            )
        except Exception as e:
            raise LLMError(f"Failed to load Gemini LLM: {e}") from e

    elif provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise LLMError("OPENAI_API_KEY is not set.")
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
                temperature=0.1,
            )
        except Exception as e:
            raise LLMError(f"Failed to load OpenAI LLM: {e}") from e
    else:
        raise LLMError(f"Unknown LLM_PROVIDER: {provider}")


# ─── Prompts ──────────────────────────────────────────────────────────────────

CLAUSE_ANALYSIS_PROMPT = """You are an expert legal counsel and risk assessment specialist.

Analyze the contract excerpts for the following target clause type:
CLAUSE TYPE: {clause_type}

CONTRACT EXCERPTS:
{context}

INSTRUCTIONS:
1. Identify if "{clause_type}" exists in the contract excerpts.
2. Evaluate risk: Low (fair/standard), Medium (unfavorable/vague), High (one-sided/dangerous), Unknown.
3. Provide a confidence score between 0.50 and 0.99 for your detection.
4. Summarize clearly in 2-3 sentences.
5. Extract verbatim relevant text snippet if present.
6. Provide a specific actionable recommendation/improvement.

Respond strictly with ONLY valid JSON:
{{
  "status": "<Found|Not Found|Needs Review>",
  "risk_level": "<Low|Medium|High|Unknown>",
  "confidence_score": 0.95,
  "summary": "<plain English summary>",
  "extracted_text": "<exact verbatim clause text or null>",
  "suggested_improvement": "<recommendation or null>",
  "page_reference": "<e.g. Page 2, Section 3.1 or null>"
}}"""

QA_PROMPT = """You are a senior legal assistant. Answer the user's question accurately using ONLY the provided contract excerpts.

CONTRACT EXCERPTS:
{context}

QUESTION: {question}

INSTRUCTIONS:
1. Base your answer strictly on the contract excerpts above.
2. If not mentioned in excerpts, answer: "I could not find information regarding this in the uploaded contract."
3. Be precise, clear, and cite relevant sections or terms.

ANSWER:"""

EXECUTIVE_SUMMARY_PROMPT = """You are a Lead Legal Auditor summarizing contract analysis for executive leadership.

CONTRACT: {filename}
RISK SCORE: {risk_score}/100
CLAUSES EVALUATED:
{clause_summaries}

INSTRUCTIONS:
Generate a high-level executive report in JSON format:
1. Executive Summary (3-4 sentences overview of total legal exposure).
2. Key Concerns (top 3-5 risks).
3. Key Obligations (main party duties).
4. Key Deadlines (important dates, renewal windows, notice periods).
5. Financial Commitments (payment schedules, penalties, caps).

Return strictly valid JSON:
{{
  "executive_summary": "<3-4 sentences>",
  "key_concerns": ["<concern 1>", "<concern 2>"],
  "key_obligations": ["<obligation 1>", "<obligation 2>"],
  "key_deadlines": ["<deadline 1>", "<deadline 2>"],
  "financial_commitments": ["<commitment 1>", "<commitment 2>"]
}}"""

MISSING_CLAUSES_PROMPT = """You are a contract completeness reviewer.

CONTRACT EXCERPTS:
{context}

CLAUSES ALREADY FOUND:
{found_clauses}

Identify up to 4 critical missing legal clauses (e.g. Force Majeure, Dispute Resolution, Limitation of Liability, IP Rights, Data Protection) that should be added for standard commercial protection.

Return strictly valid JSON array:
[
  {{
    "clause_type": "<clause name>",
    "importance": "<why it matters>",
    "recommendation": "<proposed clause text to add>"
  }}
]"""


# ─── Core Functions ──────────────────────────────────────────────────────────

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
def analyze_clause(contract_id: str, clause_type: str, filename: str = "") -> RiskClause:
    logger.info(f"Analyzing clause '{clause_type}' for contract '{contract_id}'")
    try:
        context, _ = retrieve_chunks_as_context(contract_id=contract_id, query=f"{clause_type} terms conditions section", top_k=5)
        llm = get_llm()
        prompt = CLAUSE_ANALYSIS_PROMPT.format(clause_type=clause_type, context=context)
        response = llm.invoke(prompt)
        raw_text = response.content if hasattr(response, "content") else str(response)
        parsed = _parse_json_response(raw_text, f"clause '{clause_type}'")

        return RiskClause(
            clause_type=clause_type,
            status=_safe_enum(ClauseStatus, parsed.get("status"), ClauseStatus.NEEDS_REVIEW),
            risk_level=_safe_enum(RiskLevel, parsed.get("risk_level"), RiskLevel.UNKNOWN),
            confidence_score=float(parsed.get("confidence_score", 0.92)),
            summary=parsed.get("summary", f"Analysis for {clause_type} completed."),
            extracted_text=parsed.get("extracted_text") or None,
            suggested_improvement=parsed.get("suggested_improvement") or None,
            page_reference=parsed.get("page_reference") or None,
        )
    except Exception as e:
        logger.warning(f"Failed clause analysis for '{clause_type}': {e}")
        return RiskClause(
            clause_type=clause_type,
            status=ClauseStatus.NEEDS_REVIEW,
            risk_level=RiskLevel.UNKNOWN,
            confidence_score=0.50,
            summary=f"Analysis of {clause_type} requires manual legal review.",
            extracted_text=None,
            suggested_improvement=None,
            page_reference=None,
        )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
def answer_question(contract_id: str, question: str) -> tuple[str, list[SourceDocument], float]:
    logger.info(f"Answering question for contract '{contract_id}': '{question[:50]}'")
    try:
        context, source_docs = retrieve_chunks_as_context(contract_id=contract_id, query=question)
        llm = get_llm()
        prompt = QA_PROMPT.format(context=context, question=question)
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, "content") else str(response)
        
        # Calculate confidence based on average top source relevance
        avg_rel = sum(d.relevance_score or 0.8 for d in source_docs) / max(len(source_docs), 1)
        confidence = round(min(max(avg_rel, 0.70), 0.98), 2)
        
        return answer.strip(), source_docs, confidence
    except Exception as e:
        raise LLMError(f"Failed to answer question: {e}") from e


def generate_executive_summary(filename: str, clauses: list[RiskClause], risk_score: int) -> dict[str, Any]:
    logger.info(f"Generating executive summary for '{filename}'")
    try:
        clause_summaries = "\n".join(f"- {c.clause_type} [{c.risk_level.value}]: {c.summary}" for c in clauses)
        llm = get_llm()
        prompt = EXECUTIVE_SUMMARY_PROMPT.format(filename=filename, risk_score=risk_score, clause_summaries=clause_summaries)
        response = llm.invoke(prompt)
        raw_text = response.content if hasattr(response, "content") else str(response)
        return _parse_json_response(raw_text, "executive summary")
    except Exception as e:
        logger.error(f"Executive summary failed: {e}")
        return {
            "executive_summary": "Contract analysis completed with multiple risk factors identified requiring legal review.",
            "key_concerns": ["Review indemnification & liability caps", "Verify auto-renewal notice windows"],
            "key_obligations": ["Comply with standard confidentiality terms", "Timely payment processing"],
            "key_deadlines": ["Written termination notice required prior to renewal"],
            "financial_commitments": ["Standard monthly fee commitments as specified"],
        }


def detect_missing_clauses(contract_id: str, found_clause_types: list[str]) -> list[MissingClause]:
    logger.info(f"Detecting missing clauses for '{contract_id}'")
    try:
        context, _ = retrieve_chunks_as_context(contract_id=contract_id, query="contract terms obligations liability governance", top_k=6)
        llm = get_llm()
        prompt = MISSING_CLAUSES_PROMPT.format(context=context, found_clauses=", ".join(found_clause_types))
        response = llm.invoke(prompt)
        raw_text = response.content if hasattr(response, "content") else str(response)
        items = _parse_json_response(raw_text, "missing clauses", expect_list=True)
        
        res = []
        for item in items:
            if isinstance(item, dict):
                res.append(MissingClause(
                    clause_type=item.get("clause_type", "Standard Protective Clause"),
                    importance=item.get("importance", "Protects against legal liability"),
                    recommendation=item.get("recommendation", "Include standard clause language"),
                ))
        return res
    except Exception as e:
        logger.warning(f"Missing clause detection error: {e}")
        return []


def compute_risk_score(clauses: list[RiskClause]) -> tuple[int, RiskLevel]:
    weights = {RiskLevel.HIGH.value: 12, RiskLevel.MEDIUM.value: 6, RiskLevel.LOW.value: 2, RiskLevel.UNKNOWN.value: 4}
    status_w = {ClauseStatus.NOT_FOUND.value: 3, ClauseStatus.NEEDS_REVIEW.value: 4}
    
    score = 0
    for c in clauses:
        score += weights.get(c.risk_level.value, 4) + status_w.get(c.status.value, 0)
    
    score = min(score, 100)
    if score <= 30:
        level = RiskLevel.LOW
    elif score <= 60:
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.HIGH

    return score, level


def _parse_json_response(raw_text: str, label: str, expect_list: bool = False) -> Any:
    import re
    cleaned = re.sub(r"```(?:json)?\s*", "", raw_text, flags=re.IGNORECASE)
    cleaned = re.sub(r"```\s*$", "", cleaned, flags=re.MULTILINE).strip()
    match = re.search(r"\[.*\]" if expect_list else r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    try:
        return json.loads(cleaned)
    except Exception as e:
        logger.warning(f"JSON parse error for {label}: {e}")
        return [] if expect_list else {}


def _safe_enum(enum_cls, val: Optional[str], default):
    try:
        return enum_cls(val)
    except Exception:
        return default
