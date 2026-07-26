"""
Analytics & Admin Service — Metrics, Risk Distribution, Audit Logging, and System Statistics.
"""

import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.config import get_settings
from backend.database.models import AuditLog, ClauseAnalysis, Contract, User
from backend.models.response_models import AdminStatsResponse, AnalyticsResponse
from backend.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def log_action(db: Session, user_id: str, action: str, details: str = "") -> None:
    """Log an audit action to the database."""
    try:
        log_entry = AuditLog(user_id=user_id, action=action, details=details)
        db.add(log_entry)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")


def get_analytics_metrics(db: Session, user_id: Optional[str] = None) -> AnalyticsResponse:
    """Compute dashboard analytics & risk distribution metrics."""
    query = db.query(Contract)
    if user_id:
        query = query.filter(Contract.user_id == user_id)

    contracts = query.all()
    total = len(contracts)

    if total == 0:
        return AnalyticsResponse(
            total_contracts=0,
            average_risk_score=0.0,
            high_risk_count=0,
            medium_risk_count=0,
            low_risk_count=0,
            risk_distribution={"High": 0, "Medium": 0, "Low": 0},
            clause_frequency={},
            monthly_uploads=[],
        )

    avg_score = round(sum(c.risk_score for c in contracts) / total, 1)
    high_cnt = sum(1 for c in contracts if c.overall_risk_level == "High")
    med_cnt = sum(1 for c in contracts if c.overall_risk_level == "Medium")
    low_cnt = sum(1 for c in contracts if c.overall_risk_level == "Low")

    # Clause frequencies
    clause_query = db.query(ClauseAnalysis.clause_type, func.count(ClauseAnalysis.id))\
                     .filter(ClauseAnalysis.risk_level == "High")\
                     .group_by(ClauseAnalysis.clause_type).all()
    
    clause_freq = {ct: count for ct, count in clause_query}

    # Monthly uploads simulation/data
    monthly_uploads = [
        {"month": "Jan", "count": max(1, total // 4)},
        {"month": "Feb", "count": max(2, total // 3)},
        {"month": "Mar", "count": max(1, total // 2)},
        {"month": "Apr", "count": total},
    ]

    return AnalyticsResponse(
        total_contracts=total,
        average_risk_score=avg_score,
        high_risk_count=high_cnt,
        medium_risk_count=med_cnt,
        low_risk_count=low_cnt,
        risk_distribution={"High": high_cnt, "Medium": med_cnt, "Low": low_cnt},
        clause_frequency=clause_freq,
        monthly_uploads=monthly_uploads,
    )


def get_admin_system_stats(db: Session) -> AdminStatsResponse:
    """Compute admin dashboard system stats and audit logs."""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_contracts = db.query(Contract).count()
    total_chunks = db.query(func.sum(Contract.chunk_count)).scalar() or 0

    # Calculate upload directory size
    total_bytes = 0
    if os.path.exists(settings.UPLOAD_DIR):
        for f in os.listdir(settings.UPLOAD_DIR):
            fp = os.path.join(settings.UPLOAD_DIR, f)
            if os.path.isfile(fp):
                total_bytes += os.path.getsize(fp)
    
    storage_mb = round(total_bytes / (1024 * 1024), 2)

    # Recent audit logs
    recent_logs_orm = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(15).all()
    recent_logs = [
        {
            "id": log.id,
            "user_id": log.user_id or "System",
            "action": log.action,
            "details": log.details,
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for log in recent_logs_orm
    ]

    return AdminStatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_contracts=total_contracts,
        total_chunks=total_chunks,
        total_storage_mb=storage_mb,
        recent_logs=recent_logs,
    )
