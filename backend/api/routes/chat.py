"""
Chat Router — POST /chat
"""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user, get_db
from backend.database.models import ChatMessage as ORMChatMessage, User
from backend.models.request_models import ChatRequest
from backend.models.response_models import ChatResponse, SourceDocument
from backend.rag.pipeline import answer_question
from backend.services.analytics_service import log_action
from backend.utils.exceptions import ContractAnalyzerError
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question about the contract",
)
async def chat_with_contract(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    """Ask natural language question and return grounded answer with sources."""
    logger.info(f"POST /chat | contract_id='{request.contract_id}' question='{request.question[:40]}...'")

    try:
        loop = asyncio.get_event_loop()
        answer, source_docs, confidence = await loop.run_in_executor(
            None,
            answer_question,
            request.contract_id,
            request.question,
        )

        response = ChatResponse(
            contract_id=request.contract_id,
            question=request.question,
            answer=answer,
            confidence=confidence,
            sources=source_docs,
        )

        # Save user question & assistant response to DB
        user_msg = ORMChatMessage(
            contract_id=request.contract_id,
            sender="user",
            content=request.question,
        )
        assistant_msg = ORMChatMessage(
            contract_id=request.contract_id,
            sender="assistant",
            content=answer,
            sources=[s.dict() for s in source_docs],
        )
        db.add(user_msg)
        db.add(assistant_msg)
        db.commit()

        log_action(db, current_user.id, "CHAT", f"Asked question on contract {request.contract_id}")
        return response

    except ContractAnalyzerError:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in POST /chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while answering the question.",
        )
