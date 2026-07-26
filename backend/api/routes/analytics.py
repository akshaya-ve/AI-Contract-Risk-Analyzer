"""
Analytics Router — GET /analytics dashboard metrics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user, get_db
from backend.database.models import User
from backend.models.response_models import AnalyticsResponse
from backend.services.analytics_service import get_analytics_metrics

router = APIRouter()


@router.get(
    "/analytics",
    response_model=AnalyticsResponse,
    summary="Get risk analytics and contract statistics",
)
async def get_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalyticsResponse:
    """Return dashboard analytics, risk distributions, and clause frequency stats."""
    user_id = None if current_user.is_admin else current_user.id
    return get_analytics_metrics(db, user_id=user_id)
