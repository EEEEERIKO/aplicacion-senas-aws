"""
Authentication and authorization utilities.
JWT token generation, password hashing, and permission validation.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import hashlib

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security scheme
security = HTTPBearer()

# Password constraints for security
MAX_PASSWORD_LENGTH = 128  # Reasonable max to prevent DoS attacks
MIN_PASSWORD_LENGTH = 8    # Minimum for security

def _prehash_password(password: str) -> str:
    """
    Pre-hash password with SHA256 to support longer passwords.
    This allows passwords up to MAX_PASSWORD_LENGTH bytes (beyond bcrypt's 72 byte limit).
    The SHA256 hash is deterministic and always 64 hex chars.
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def hash_password(password: str) -> str:
    """
    Hash a password securely with length validation.
    
    Security considerations:
    - Min 8 chars: Prevents weak passwords
    - Max 128 chars: Prevents DoS attacks with extremely long passwords
    - Uses SHA256 pre-hash + bcrypt for any length support
    - Bcrypt provides resistance to rainbow tables and brute force
    
    Raises:
        ValueError: If password length is invalid
    """
    password_length = len(password)
    
    if password_length < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long")
    
    if password_length > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Password cannot be longer than {MAX_PASSWORD_LENGTH} characters (DoS protection)")
    
    prehashed = _prehash_password(password)
    return pwd_context.hash(prehashed)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    Applies the same SHA256 pre-hash before bcrypt verification.
    """
    prehashed = _prehash_password(plain_password)
    return pwd_context.verify(prehashed, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Get current authenticated user from JWT token.
    Returns user data from token payload.
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role", "user")
    }

async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Verify current user is admin.
    Use this dependency for admin-only endpoints.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Optional authentication (allows both authenticated and anonymous)
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """Get current user if authenticated, None otherwise"""
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
