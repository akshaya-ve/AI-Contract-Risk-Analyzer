"""
Analysis Service — Orchestrates 12-clause analysis, DB persistence, and caching.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.database.models import ClauseAnalysis as ORMClauseAnalysis, Contract as ORMContract
from backend.models.response_models import (
    AnalysisReport,
    MissingClause,
    RiskClause,
    RiskLevel,
    RisksResponse,
    SummaryResponse,
)
from backend.rag.pipeline import (
    analyze_clause,
    compute_risk_score,
    detect_missing_clauses,
    generate_executive_summary,
)
from backend.rag.vector_store import contract_exists
from backend.utils.exceptions import DocumentNotFoundError
from backend.utils.logger import get_logger

logger = get_logger(__name__)

_analysis_cache: dict[str, AnalysisReport] = {}


async def run_full_analysis(
    contract_id: str,
    filename: str,
    db: Optional[Session] = None,
) -> AnalysisReport:
    """Run full 12-clause risk analysis pipeline and save to DB."""
    if not contract_exists(contract_id):
        raise DocumentNotFoundError(contract_id)

    settings = get_settings()
    logger.info(f"Starting 12-clause analysis for contract '{contract_id}'")
    start_time = datetime.utcnow()

    # 1. Analyze 12 clauses concurrently
    clauses = await _analyze_clauses_concurrently(
        contract_id=contract_id,
        clause_types=settings.RISK_CLAUSES,
        filename=filename,
    )

    # 2. Compute risk score
    risk_score, overall_risk_level = compute_risk_score(clauses)

    # 3. Detect missing clauses
    found_clause_types = [c.clause_type for c in clauses if c.status.value == "Found"]
    missing_clauses = await asyncio.get_event_loop().run_in_executor(
        None, detect_missing_clauses, contract_id, found_clause_types
    )

    # 4. Executive summary & obligations
    summary_data = await asyncio.get_event_loop().run_in_executor(
        None, generate_executive_summary, filename, clauses, risk_score
    )

    exec_summary = summary_data.get("executive_summary", "Contract analysis complete.")
    key_concerns = summary_data.get("key_concerns", [])
    key_obligations = summary_data.get("key_obligations", [])
    key_deadlines = summary_data.get("key_deadlines", [])
    financial_commitments = summary_data.get("financial_commitments", [])

    report = AnalysisReport(
        contract_id=contract_id,
        filename=filename,
        overall_risk_level=overall_risk_level,
        risk_score=risk_score,
        executive_summary=exec_summary,
        clauses=clauses,
        missing_clauses=missing_clauses,
        key_concerns=key_concerns,
        key_obligations=key_obligations,
        key_deadlines=key_deadlines,
        financial_commitments=financial_commitments,
        analyzed_at=datetime.utcnow(),
    )

    _analysis_cache[contract_id] = report

    # 5. Persist to DB if session provided
    if db:
        try:
            contract_record = db.query(ORMContract).filter(ORMContract.id == contract_id).first()
            if contract_record:
                contract_record.overall_risk_level = overall_risk_level.value
                contract_record.risk_score = risk_score
                contract_record.executive_summary = exec_summary
                contract_record.key_concerns = key_concerns
                contract_record.missing_clauses = [m.dict() for m in missing_clauses]
                contract_record.analyzed_at = datetime.utcnow()

                # Delete existing clauses and save fresh
                db.query(ORMClauseAnalysis).filter(ORMClauseAnalysis.contract_id == contract_id).delete()
                for c in clauses:
                    db_clause = ORMClauseAnalysis(
                        contract_id=contract_id,
                        clause_type=c.clause_type,
                        status=c.status.value,
                        risk_level=c.risk_level.value,
                        confidence_score=c.confidence_score,
                        summary=c.summary,
                        extracted_text=c.extracted_text,
                        suggested_improvement=c.suggested_improvement,
                        page_reference=c.page_reference,
                    )
                    db.add(db_clause)
                db.commit()
                logger.info(f"Persisted analysis for '{contract_id}' to SQL database.")
        except Exception as e:
            logger.error(f"Failed to persist analysis to DB: {e}")
            db.rollback()

    elapsed = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Analysis complete for '{contract_id}' in {elapsed:.1f}s (score={risk_score})")
    return report


def get_summary(contract_id: str, db: Optional[Session] = None) -> SummaryResponse:
    if contract_id in _analysis_cache:
        report = _analysis_cache[contract_id]
        return SummaryResponse(
            contract_id=report.contract_id,
            filename=report.filename,
            overall_risk_level=report.overall_risk_level,
            risk_score=report.risk_score,
            executive_summary=report.executive_summary,
            key_concerns=report.key_concerns,
            key_obligations=report.key_obligations,
            key_deadlines=report.key_deadlines,
            financial_commitments=report.financial_commitments,
            analyzed_at=report.analyzed_at,
        )

    if db:
        contract = db.query(ORMContract).filter(ORMContract.id == contract_id).first()
        if contract and contract.analyzed_at:
            return SummaryResponse(
                contract_id=contract.id,
                filename=contract.filename,
                overall_risk_level=RiskLevel(contract.overall_risk_level),
                risk_score=contract.risk_score,
                executive_summary=contract.executive_summary or "",
                key_concerns=contract.key_concerns or [],
                key_obligations=[],
                key_deadlines=[],
                financial_commitments=[],
                analyzed_at=contract.analyzed_at,
            )

    raise DocumentNotFoundError(f"No analysis found for '{contract_id}'. Run POST /analyze first.")


def get_risks(contract_id: str, db: Optional[Session] = None) -> RisksResponse:
    if contract_id in _analysis_cache:
        report = _analysis_cache[contract_id]
        return RisksResponse(
            contract_id=report.contract_id,
            overall_risk_level=report.overall_risk_level,
            risk_score=report.risk_score,
            clauses=report.clauses,
            missing_clauses=report.missing_clauses,
        )

    if db:
        contract = db.query(ORMContract).filter(ORMContract.id == contract_id).first()
        if contract and contract.analyzed_at:
            orm_clauses = db.query(ORMClauseAnalysis).filter(ORMClauseAnalysis.contract_id == contract_id).all()
            clauses = [
                RiskClause(
                    clause_type=c.clause_type,
                    status=c.status,
                    risk_level=c.risk_level,
                    confidence_score=c.confidence_score,
                    summary=c.summary,
                    extracted_text=c.extracted_text,
                    suggested_improvement=c.suggested_improvement,
                    page_reference=c.page_reference,
                ) for c in orm_clauses
            ]
            missing = [MissingClause(**m) for m in (contract.missing_clauses or [])]
            return RisksResponse(
                contract_id=contract.id,
                overall_risk_level=RiskLevel(contract.overall_risk_level),
                risk_score=contract.risk_score,
                clauses=clauses,
                missing_clauses=missing,
            )

    raise DocumentNotFoundError(f"No risks found for '{contract_id}'. Run POST /analyze first.")


def invalidate_cache(contract_id: str) -> None:
    _analysis_cache.pop(contract_id, None)


async def _analyze_clauses_concurrently(contract_id: str, clause_types: list[str], filename: str) -> list[RiskClause]:
    max_workers = min(len(clause_types), 4)
    futures_map = {}
    results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for ct in clause_types:
            f = executor.submit(analyze_clause, contract_id, ct, filename)
            futures_map[f] = ct

        for f in as_completed(futures_map):
            ct = futures_map[f]
            try:
                results[ct] = f.result()
            except Exception as e:
                logger.error(f"Clause {ct} failed: {e}")
                results[ct] = RiskClause(
                    clause_type=ct,
                    status="Needs Review",
                    risk_level="Unknown",
                    confidence_score=0.5,
                    summary=f"Automatic analysis for {ct} failed. Manual review recommended.",
                )

    return [results[ct] for ct in clause_types if ct in results]
