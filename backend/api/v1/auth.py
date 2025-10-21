"""
Authentication API Endpoints

This module provides authentication and authorization endpoints.
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from database import get_db
from models.customer import Customer
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_api_key,
    verify_bearer_token
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours


class RegisterRequest(BaseModel):
    """User registration request"""
    name: str
    email: EmailStr
    password: str
    tier: str = "free"


class RegisterResponse(BaseModel):
    """User registration response"""
    id: int
    name: str
    email: str
    api_key: str
    tier: str
    message: str = "Registration successful"


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class APIKeyResponse(BaseModel):
    """API key response"""
    api_key: str
    message: str = "New API key generated"


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new customer account.
    
    Args:
        request: Registration request data
        db: Database session
        
    Returns:
        Registration response with API key
        
    Raises:
        HTTPException: If email already exists
    """
    # Check if email already exists
    existing = db.query(Customer).filter(Customer.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate API key
    api_key = generate_api_key()
    
    # Create customer
    customer = Customer(
        name=request.name,
        email=request.email,
        api_key=api_key,
        tier=request.tier
    )
    
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    return RegisterResponse(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        api_key=api_key,
        tier=customer.tier
    )


@router.post("/token", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login and get access token.
    
    Args:
        form_data: OAuth2 password form data
        db: Database session
        
    Returns:
        Access and refresh tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find customer by email
    customer = db.query(Customer).filter(Customer.email == form_data.username).first()
    
    if not customer or not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": customer.email, "customer_id": customer.id, "tier": customer.tier}
    )
    refresh_token = create_refresh_token(
        data={"sub": customer.email, "customer_id": customer.id}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token request
        db: Database session
        
    Returns:
        New access and refresh tokens
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    # Decode refresh token
    payload = decode_token(request.refresh_token)
    
    # Verify it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get customer
    email = payload.get("sub")
    customer = db.query(Customer).filter(Customer.email == email).first()
    
    if not customer or not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(
        data={"sub": customer.email, "customer_id": customer.id, "tier": customer.tier}
    )
    refresh_token = create_refresh_token(
        data={"sub": customer.email, "customer_id": customer.id}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/api-key/regenerate", response_model=APIKeyResponse)
async def regenerate_api_key(
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Regenerate API key for authenticated customer.
    
    Args:
        token_data: Decoded JWT token data
        db: Database session
        
    Returns:
        New API key
        
    Raises:
        HTTPException: If customer not found
    """
    customer_id = token_data.get("customer_id")
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Generate new API key
    new_api_key = generate_api_key()
    customer.api_key = new_api_key
    
    db.commit()
    
    return APIKeyResponse(api_key=new_api_key)


@router.get("/me")
async def get_current_user(
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information.
    
    Args:
        token_data: Decoded JWT token data
        db: Database session
        
    Returns:
        Customer information
        
    Raises:
        HTTPException: If customer not found
    """
    customer_id = token_data.get("customer_id")
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "tier": customer.tier,
        "is_active": customer.is_active,
        "created_at": customer.created_at
    }

