"""
Auth Service — handles user registration, authentication, and user profile management.
"""

from typing import Optional
from sqlalchemy.orm import Session

from backend.database.models import User
from backend.models.request_models import UserCreate, UserLogin
from backend.models.response_models import Token, UserResponse
from backend.utils.exceptions import ContractAnalyzerError
from backend.utils.logger import get_logger
from backend.utils.security import create_access_token, hash_password, verify_password

logger = get_logger(__name__)


def register_user(db: Session, user_in: UserCreate) -> UserResponse:
    """Register a new user in the system."""
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise ContractAnalyzerError("Email already registered", status_code=400)
    
    # First user registered automatically becomes admin
    user_count = db.query(User).count()
    is_admin = (user_count == 0)

    user = User(
        email=user_in.email.lower(),
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        is_admin=is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"Registered user: {user.email} (is_admin={is_admin})")
    return UserResponse.from_orm_user(user)


def authenticate_user(db: Session, credentials: UserLogin) -> Token:
    """Authenticate user credentials and return JWT token."""
    user = db.query(User).filter(User.email == credentials.email.lower()).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise ContractAnalyzerError("Incorrect email or password", status_code=401)
    
    if not user.is_active:
        raise ContractAnalyzerError("User account is inactive", status_code=403)

    access_token = create_access_token(data={"sub": user.id, "email": user.email, "is_admin": user.is_admin})
    logger.info(f"Authenticated user: {user.email}")
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm_user(user),
    )


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Retrieve a user by ID."""
    return db.query(User).filter(User.id == user_id).first()
