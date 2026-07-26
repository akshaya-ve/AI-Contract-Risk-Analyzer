"""
FastAPI dependency injection — DB sessions, JWT authentication, and current_user resolution.
"""

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import User
from backend.services.auth_service import get_user_by_id
from backend.utils.security import decode_access_token
from backend.utils.exceptions import ContractAnalyzerError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to validate JWT token and inject the current User object.
    Falls back to a default demo user if unauthenticated for local zero-config convenience.
    """
    if not token:
        # Fallback for unauthenticated access: get or create default local user
        demo_user = db.query(User).filter(User.email == "demo@analyzer.ai").first()
        if not demo_user:
            demo_user = User(
                email="demo@analyzer.ai",
                full_name="Demo User",
                hashed_password="demo_hashed_password",
                is_admin=True,
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
        return demo_user

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
        return user
    except ContractAnalyzerError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency that requires admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this action.",
        )
    return current_user


async def verify_content_type_multipart(
    content_type: str = Header(default=""),
) -> None:
    """Validate that file upload requests use multipart/form-data."""
    if content_type and "multipart/form-data" not in content_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File uploads must use multipart/form-data encoding.",
        )
