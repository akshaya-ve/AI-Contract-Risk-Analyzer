"""
Analyze Router — POST /analyze | GET /summary/{contract_id} | GET /risks/{contract_id}
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user, get_db
from backend.database.models import User
from backend.models.request_models import AnalyzeRequest
from backend.models.response_models import (
    AnalysisReport,
    RisksResponse,
    SummaryResponse,
)
from backend.services.analysis_service import get_risks, get_summary, run_full_analysis
from backend.services.analytics_service import log_action
from backend.services.document_service import get_filename
from backend.utils.exceptions import ContractAnalyzerError
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalysisReport,
    status_code=status.HTTP_200_OK,
    summary="Analyse contract risks",
)
async def analyze_contract(
    request: AnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalysisReport:
    """Run full RAG 12-clause risk analysis on contract."""
    logger.info(f"POST /analyze | contract_id='{request.contract_id}' by user '{current_user.email}'")

    try:
        report = await run_full_analysis(
            contract_id=request.contract_id,
            filename=get_filename(request.contract_id),
            db=db,
        )
        log_action(db, current_user.id, "ANALYZE", f"Analyzed contract {request.contract_id}")
        return report

    except ContractAnalyzerError:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in /analyze: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during risk analysis.",
        )


@router.get(
    "/summary/{contract_id}",
    response_model=SummaryResponse,
    summary="Get executive summary",
)
async def get_contract_summary(
    contract_id: str,
    db: Session = Depends(get_db),
) -> SummaryResponse:
    """Retrieve executive summary for an analysed contract."""
    return get_summary(contract_id.strip(), db=db)


@router.get(
    "/risks/{contract_id}",
    response_model=RisksResponse,
    summary="Get per-clause risks",
)
async def get_contract_risks(
    contract_id: str,
    db: Session = Depends(get_db),
) -> RisksResponse:
    """Retrieve per-clause risks for an analysed contract."""
    return get_risks(contract_id.strip(), db=db)
