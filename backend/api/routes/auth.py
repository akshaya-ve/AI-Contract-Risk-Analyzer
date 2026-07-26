"""
Auth Router — User Registration, Login, and Current User Profile endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user, get_db
from backend.database.models import User
from backend.models.request_models import UserCreate, UserLogin
from backend.models.response_models import Token, UserResponse
from backend.services.auth_service import authenticate_user, register_user
from backend.services.analytics_service import log_action

router = APIRouter()


@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(user_in: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """Create a new user account."""
    user = register_user(db, user_in)
    log_action(db, user.id, "REGISTER", f"User registered: {user.email}")
    return user


@router.post(
    "/auth/login",
    response_model=Token,
    summary="Authenticate and receive JWT token",
)
async def login(credentials: UserLogin, db: Session = Depends(get_db)) -> Token:
    """Login with email & password to receive bearer token."""
    token = authenticate_user(db, credentials)
    log_action(db, token.user.id, "LOGIN", f"User logged in: {credentials.email}")
    return token


@router.get(
    "/auth/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return currently authenticated user details."""
    return UserResponse.from_orm_user(current_user)
