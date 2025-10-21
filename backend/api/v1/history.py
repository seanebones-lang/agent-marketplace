"""
Execution History API Endpoints

This module provides endpoints for viewing agent execution history.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models.deployment import UsageLog
from core.security import verify_bearer_token


router = APIRouter(prefix="/history", tags=["History"])


class ExecutionHistoryItem(BaseModel):
    """Execution history item model"""
    id: int
    package_id: str
    execution_time_ms: int
    tokens_used: int
    cost: float
    status: str
    error_message: Optional[str]
    created_at: str


class ExecutionDetail(BaseModel):
    """Detailed execution information"""
    id: int
    package_id: str
    deployment_id: Optional[int]
    execution_time_ms: int
    tokens_used: int
    cost: float
    status: str
    error_message: Optional[str]
    metadata: Optional[dict]
    created_at: str


@router.get("/executions", response_model=List[ExecutionHistoryItem])
async def get_execution_history(
    package_id: Optional[str] = None,
    status: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Get execution history.
    
    Args:
        package_id: Filter by package ID
        status: Filter by status (success, failed, timeout)
        days: Number of days to include
        limit: Maximum number of results
        offset: Pagination offset
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        List of execution history items
    """
    customer_id = token_data.get("customer_id")
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Build query
    query = db.query(UsageLog).filter(
        UsageLog.customer_id == customer_id,
        UsageLog.created_at >= cutoff_date
    )
    
    if package_id:
        query = query.filter(UsageLog.package_id == package_id)
    
    if status:
        query = query.filter(UsageLog.status == status)
    
    # Get results
    logs = query.order_by(
        UsageLog.created_at.desc()
    ).limit(limit).offset(offset).all()
    
    return [
        ExecutionHistoryItem(
            id=log.id,
            package_id=log.package_id,
            execution_time_ms=log.execution_time_ms,
            tokens_used=log.tokens_used,
            cost=log.cost,
            status=log.status,
            error_message=log.error_message,
            created_at=log.created_at.isoformat()
        )
        for log in logs
    ]


@router.get("/executions/{execution_id}", response_model=ExecutionDetail)
async def get_execution_detail(
    execution_id: int,
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Get detailed execution information.
    
    Args:
        execution_id: Execution ID
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        Detailed execution information
        
    Raises:
        HTTPException: If execution not found or unauthorized
    """
    customer_id = token_data.get("customer_id")
    
    log = db.query(UsageLog).filter(
        UsageLog.id == execution_id,
        UsageLog.customer_id == customer_id
    ).first()
    
    if not log:
        raise HTTPException(
            status_code=404,
            detail="Execution not found"
        )
    
    return ExecutionDetail(
        id=log.id,
        package_id=log.package_id,
        deployment_id=log.deployment_id,
        execution_time_ms=log.execution_time_ms,
        tokens_used=log.tokens_used,
        cost=log.cost,
        status=log.status,
        error_message=log.error_message,
        metadata=log.metadata,
        created_at=log.created_at.isoformat()
    )


@router.get("/executions/package/{package_id}", response_model=List[ExecutionHistoryItem])
async def get_package_execution_history(
    package_id: str,
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(100, ge=1, le=1000),
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Get execution history for a specific package.
    
    Args:
        package_id: Package identifier
        days: Number of days to include
        limit: Maximum number of results
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        List of execution history items
    """
    customer_id = token_data.get("customer_id")
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    logs = db.query(UsageLog).filter(
        UsageLog.customer_id == customer_id,
        UsageLog.package_id == package_id,
        UsageLog.created_at >= cutoff_date
    ).order_by(
        UsageLog.created_at.desc()
    ).limit(limit).all()
    
    return [
        ExecutionHistoryItem(
            id=log.id,
            package_id=log.package_id,
            execution_time_ms=log.execution_time_ms,
            tokens_used=log.tokens_used,
            cost=log.cost,
            status=log.status,
            error_message=log.error_message,
            created_at=log.created_at.isoformat()
        )
        for log in logs
    ]


@router.delete("/executions/{execution_id}")
async def delete_execution(
    execution_id: int,
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Delete an execution record.
    
    Args:
        execution_id: Execution ID
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If execution not found or unauthorized
    """
    customer_id = token_data.get("customer_id")
    
    log = db.query(UsageLog).filter(
        UsageLog.id == execution_id,
        UsageLog.customer_id == customer_id
    ).first()
    
    if not log:
        raise HTTPException(
            status_code=404,
            detail="Execution not found"
        )
    
    db.delete(log)
    db.commit()
    
    return {"message": "Execution deleted successfully"}


@router.get("/stats/summary")
async def get_execution_summary(
    days: int = Query(30, ge=1, le=365),
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Get execution summary statistics.
    
    Args:
        days: Number of days to include
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        Execution summary statistics
    """
    customer_id = token_data.get("customer_id")
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    logs = db.query(UsageLog).filter(
        UsageLog.customer_id == customer_id,
        UsageLog.created_at >= cutoff_date
    ).all()
    
    if not logs:
        return {
            "total_executions": 0,
            "successful": 0,
            "failed": 0,
            "timeout": 0,
            "total_cost": 0.0,
            "total_tokens": 0,
            "avg_execution_time_ms": 0.0
        }
    
    successful = sum(1 for log in logs if log.status == "success")
    failed = sum(1 for log in logs if log.status == "failed")
    timeout = sum(1 for log in logs if log.status == "timeout")
    
    return {
        "total_executions": len(logs),
        "successful": successful,
        "failed": failed,
        "timeout": timeout,
        "total_cost": sum(log.cost for log in logs),
        "total_tokens": sum(log.tokens_used for log in logs),
        "avg_execution_time_ms": sum(log.execution_time_ms for log in logs) / len(logs)
    }

