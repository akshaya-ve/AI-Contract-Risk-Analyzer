"""
Security utilities for password hashing and JWT token creation/decoding.
"""

from datetime import datetime, timedelta
import hashlib
import os
from typing import Optional

import jwt
from backend.config import get_settings
from backend.utils.exceptions import ContractAnalyzerError

settings = get_settings()

# Fallback password hashing helper using SHA-256 + salt if passlib/bcrypt has native library issues
def hash_password(password: str) -> str:
    """Hash password using SHA-256 + salt."""
    salt = os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
    return f"{salt}${hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against stored salt$hash."""
    try:
        salt, stored_hash = hashed_password.split("$")
        computed_hash = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
        return computed_hash == stored_hash
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ContractAnalyzerError("Token has expired", status_code=401)
    except jwt.InvalidTokenError:
        raise ContractAnalyzerError("Invalid authentication token", status_code=401)
