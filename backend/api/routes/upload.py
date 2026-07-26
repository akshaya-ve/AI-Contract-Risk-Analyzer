"""
Upload Router — POST /upload
"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user, get_db
from backend.database.models import Contract as ORMContract, User
from backend.models.response_models import ErrorResponse, UploadResponse
from backend.services.analytics_service import log_action
from backend.services.document_service import process_uploaded_file
from backend.utils.exceptions import ContractAnalyzerError
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a legal contract",
)
async def upload_contract(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UploadResponse:
    """Upload PDF or DOCX file, extract text, chunk, embed, and persist to DB."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided in the upload.",
        )

    logger.info(f"Upload request received for '{file.filename}' by user '{current_user.email}'")

    try:
        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Uploaded file '{file.filename}' is empty.",
            )

        response = await process_uploaded_file(
            filename=file.filename,
            file_content=file_content,
        )

        # Persist / update Contract record in SQL DB
        contract_record = db.query(ORMContract).filter(ORMContract.id == response.contract_id).first()
        if not contract_record:
            contract_record = ORMContract(
                id=response.contract_id,
                user_id=current_user.id,
                filename=response.filename,
                file_size_kb=response.file_size_kb,
                page_count=response.page_count,
                chunk_count=response.chunk_count,
            )
            db.add(contract_record)
        else:
            contract_record.user_id = current_user.id
            contract_record.filename = response.filename
            contract_record.file_size_kb = response.file_size_kb
            contract_record.page_count = response.page_count
            contract_record.chunk_count = response.chunk_count

        db.commit()
        log_action(db, current_user.id, "UPLOAD", f"Uploaded {file.filename} (ID: {response.contract_id})")

        return response

    except ContractAnalyzerError:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the file: {str(e)}",
        )
