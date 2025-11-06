"""Authentication endpoints - Register, Login, Token"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, EmailStr
from typing import Optional
import boto3
from boto3.dynamodb.conditions import Key
import os
import uuid
from datetime import datetime
from app.core.auth import (
    hash_password, 
    verify_password, 
    create_access_token,
    get_current_user,
    get_current_admin,
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH
)
from pydantic import validator

router = APIRouter(prefix="/auth", tags=["authentication"])

# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    language_preference: str = "pt_BR"
    # NOTE: Role is NOT included in public registration for security
    # All new users are created as "user" role by default
    # Only admins can promote users to admin role via a separate endpoint
    
    @validator('password')
    def password_length(cls, v):
        if len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(f'Password must be at least {MIN_PASSWORD_LENGTH} characters')
        if len(v) > MAX_PASSWORD_LENGTH:
            raise ValueError(f'Password must not exceed {MAX_PASSWORD_LENGTH} characters')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

def get_dynamodb_table():
    """Get DynamoDB table"""
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=os.getenv('DYNAMO_ENDPOINT_URL', 'http://localhost:4566'),
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
    )
    return dynamodb.Table('aplicacion-senas-content')

def normalize_email(email: str) -> str:
    """
    Normalize email to lowercase for case-insensitive comparison.
    Emails should always be stored and compared in lowercase.
    """
    return email.lower().strip()

def check_email_exists(table, email: str) -> bool:
    """
    Check if an email already exists in the database.
    Returns True if email exists, False otherwise.
    Performs case-insensitive comparison.
    """
    normalized_email = normalize_email(email)
    
    try:
        # Scan all users (LocalStack limitation with complex FilterExpressions)
        response = table.scan(
            FilterExpression='entity_type = :et',
            ExpressionAttributeValues={':et': 'user'}
        )
        
        all_users = response.get('Items', [])
        
        # Check if any user has this email (case-insensitive)
        for user in all_users:
            if normalize_email(user.get('email', '')) == normalized_email:
                return True
        
        return False
        
    except Exception as e:
        print(f"Warning: Email existence check failed: {e}")
        # In case of error, assume email doesn't exist (fail-open for development)
        return False

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user.
    Creates user account and returns JWT token.
    Email is case-insensitive (stored in lowercase).
    """
    try:
        table = get_dynamodb_table()
        
        # Normalize email to lowercase
        normalized_email = normalize_email(user_data.email)
        
        # Check if email already exists (case-insensitive)
        if check_email_exists(table, normalized_email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + 'Z'
        hashed_pw = hash_password(user_data.password)
        
        user_item = {
            'PK': f'USER#{user_id}',
            'SK': 'METADATA',
            'entity_type': 'user',
            'user_id': user_id,
            'email': normalized_email,  # Store email in lowercase
            'name': user_data.name,
            'password_hash': hashed_pw,
            'language_preference': user_data.language_preference,
            'role': 'user',  # SECURITY: Always create as 'user', admins must be promoted
            'is_active': True,
            'created_at': now,
            'updated_at': now
        }
        
        table.put_item(Item=user_item)
        
        # Generate token
        token_data = {
            "sub": user_id,
            "email": normalized_email,  # Use normalized email in token
            "role": "user"  # Always 'user' for new registrations
        }
        access_token = create_access_token(token_data)
        
        # Return user without password
        user_response = {k: v for k, v in user_item.items() if k != 'password_hash'}
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Login with email and password.
    Returns JWT token on success.
    Email is case-insensitive.
    """
    try:
        table = get_dynamodb_table()
        
        # Normalize email to lowercase for case-insensitive comparison
        normalized_email = normalize_email(credentials.email)
        
        # Find user by email (using scan for development)
        # NOTE: LocalStack has issues with complex FilterExpressions, so we scan all users and filter in Python
        response = table.scan(
            FilterExpression='entity_type = :et',
            ExpressionAttributeValues={
                ':et': 'user'
            }
        )
        
        # Filter by email in Python (case-insensitive, workaround for LocalStack limitation)
        all_users = response.get('Items', [])
        items = [u for u in all_users if normalize_email(u.get('email', '')) == normalized_email]
        
        if not items:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        user = items[0]
        
        # Verify password
        if not verify_password(credentials.password, user.get('password_hash', '')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user.get('is_active', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Generate token
        token_data = {
            "sub": user['user_id'],
            "email": user['email'],
            "role": user.get('role', 'user')
        }
        access_token = create_access_token(token_data)
        
        # Return user without password
        user_response = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information.
    Requires valid JWT token.
    """
    try:
        table = get_dynamodb_table()
        response = table.get_item(
            Key={'PK': f'USER#{current_user["user_id"]}', 'SK': 'METADATA'}
        )
        
        user = response.get('Item')
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove password hash
        user_response = {k: v for k, v in user.items() if k != 'password_hash'}
        return user_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def list_all_users():
    """
    List all users in the database (for debugging/admin purposes).
    WARNING: In production, this should be admin-protected.
    """
    try:
        table = get_dynamodb_table()
        
        # Scan for all users
        response = table.scan(
            FilterExpression='entity_type = :et',
            ExpressionAttributeValues={':et': 'user'}
        )
        
        users = response.get('Items', [])
        
        # Remove password hashes
        clean_users = []
        for user in users:
            clean_user = {k: v for k, v in user.items() if k != 'password_hash'}
            clean_users.append(clean_user)
        
        return {
            "total": len(clean_users),
            "users": clean_users
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/users/{user_id}/role", dependencies=[Depends(get_current_admin)])
async def update_user_role(
    user_id: str,
    role: str = Query(..., description="New role: 'user' or 'admin'"),
    current_user: dict = Depends(get_current_admin)
):
    """
    Update user role (admin only).
    Only administrators can promote users to admin or demote admins to users.
    """
    if role not in ['user', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be either 'user' or 'admin'"
        )
    
    try:
        table = get_dynamodb_table()
        
        # Get the user
        response = table.get_item(
            Key={'PK': f'USER#{user_id}', 'SK': 'METADATA'}
        )
        
        user_item = response.get('Item')
        if not user_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent self-demotion (admin demoting themselves)
        if current_user['user_id'] == user_id and role == 'user':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote yourself from admin role"
            )
        
        # Update role
        user_item['role'] = role
        user_item['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        
        table.put_item(Item=user_item)
        
        # Return updated user (without password)
        clean_user = {k: v for k, v in user_item.items() if k != 'password_hash'}
        
        return {
            "message": f"User role updated to '{role}'",
            "user": clean_user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
