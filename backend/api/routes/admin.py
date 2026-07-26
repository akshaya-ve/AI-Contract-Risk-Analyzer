"""
Admin Router — GET /admin/stats system health, storage, and audit logs.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_admin, get_db
from backend.database.models import User
from backend.models.response_models import AdminStatsResponse
from backend.services.analytics_service import get_admin_system_stats

router = APIRouter()


@router.get(
    "/admin/stats",
    response_model=AdminStatsResponse,
    summary="Get system administration statistics & logs",
)
async def get_admin_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminStatsResponse:
    """Return administrative system metrics, storage usage, and audit logs."""
    return get_admin_system_stats(db)
