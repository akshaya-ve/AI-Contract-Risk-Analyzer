"""
Contracts Router — List user contracts, retrieve contract detail, delete contract, download PDF report.
"""

from pathlib import Path
from typing import list
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user, get_db
from backend.database.models import Contract as ORMContract, User
from backend.models.response_models import ContractListItem
from backend.rag.vector_store import delete_contract as delete_vector_contract
from backend.services.analytics_service import log_action
from backend.services.report_service import generate_pdf_report
from backend.utils.exceptions import DocumentNotFoundError
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "/contracts",
    response_model=list[ContractListItem],
    summary="List all uploaded contracts for current user",
)
async def list_contracts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ContractListItem]:
    """Retrieve list of contracts owned by the current user."""
    query = db.query(ORMContract)
    if not current_user.is_admin:
        query = query.filter(ORMContract.user_id == current_user.id)
    
    contracts = query.order_by(ORMContract.uploaded_at.desc()).all()
    return [
        ContractListItem(
            id=c.id,
            filename=c.filename,
            file_size_kb=c.file_size_kb,
            page_count=c.page_count,
            overall_risk_level=c.overall_risk_level,
            risk_score=c.risk_score,
            uploaded_at=c.uploaded_at,
            analyzed_at=c.analyzed_at,
        )
        for c in contracts
    ]


@router.delete(
    "/contracts/{contract_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a contract by ID",
)
async def delete_contract(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete contract from DB and vector database."""
    contract = db.query(ORMContract).filter(ORMContract.id == contract_id).first()
    if not contract:
        raise DocumentNotFoundError(contract_id)

    if contract.user_id and contract.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this contract")

    # Delete from ChromaDB vector store
    delete_vector_contract(contract_id)

    # Delete from SQL DB
    db.delete(contract)
    db.commit()

    log_action(db, current_user.id, "DELETE_CONTRACT", f"Deleted contract {contract_id}")
    return {"message": f"Contract '{contract_id}' deleted successfully."}


@router.get(
    "/contracts/{contract_id}/report",
    summary="Download PDF Risk Assessment Report",
)
async def download_report(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate and download the executive PDF report for a contract."""
    contract = db.query(ORMContract).filter(ORMContract.id == contract_id).first()
    if not contract:
        raise DocumentNotFoundError(contract_id)

    pdf_path: Path = generate_pdf_report(contract_id, db=db)
    log_action(db, current_user.id, "DOWNLOAD_REPORT", f"Downloaded report for {contract_id}")

    media_type = "application/pdf" if pdf_path.suffix == ".pdf" else "text/html"
    return FileResponse(
        path=pdf_path,
        filename=pdf_path.name,
        media_type=media_type,
    )
