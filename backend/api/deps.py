"""API dependencies"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from database import get_db
from models.customer import Customer


async def get_current_customer(
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Customer:
    """
    Validate API key and return current customer.
    
    Args:
        x_api_key: API key from request header
        db: Database session
        
    Returns:
        Customer object
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    customer = db.query(Customer).filter(
        Customer.api_key == x_api_key,
        Customer.is_active == 1
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return customer

