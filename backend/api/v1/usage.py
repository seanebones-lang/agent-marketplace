"""
Usage and Execution History API Endpoints
Provides access to execution history and usage statistics
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from database import get_db
from api.deps import get_current_customer
from models.customer import Customer
from models.execution import ExecutionHistory, UsageAggregate
from core.usage_tracker import get_usage_tracker
from core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


class ExecutionHistoryResponse(BaseModel):
    """Execution history response"""
    id: str
    customer_id: str
    package_id: str
    package_name: str
    status: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    duration_ms: int
    customer_tier: Optional[str]
    model_used: Optional[str]
    created_at: str
    completed_at: Optional[str]
    
    class Config:
        from_attributes = True


class UsageStatsResponse(BaseModel):
    """Usage statistics response"""
    total_executions: int
    total_tokens: int
    total_cost: float
    avg_duration_ms: int
    unique_packages: int
    status_breakdown: dict
    success_rate: float


class PackageUsageResponse(BaseModel):
    """Package usage response"""
    package_id: str
    package_name: str
    execution_count: int
    total_tokens: int
    total_cost: float


class DailyUsageResponse(BaseModel):
    """Daily usage response"""
    date: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    total_tokens: int
    total_cost: float
    avg_duration_ms: int


@router.get("/executions", response_model=List[ExecutionHistoryResponse])
async def list_executions(
    limit: int = Query(default=50, le=1000),
    offset: int = Query(default=0, ge=0),
    package_id: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    List execution history for the authenticated customer
    
    Args:
        limit: Maximum number of records to return (max 1000)
        offset: Number of records to skip
        package_id: Filter by package ID
        status: Filter by status (success, failed, timeout)
        start_date: Filter by start date
        end_date: Filter by end date
        customer: Authenticated customer
        db: Database session
        
    Returns:
        List of execution history records
    """
    try:
        query = db.query(ExecutionHistory).filter(
            ExecutionHistory.customer_id == customer.id
        )
        
        # Apply filters
        if package_id:
            query = query.filter(ExecutionHistory.package_id == package_id)
        
        if status:
            query = query.filter(ExecutionHistory.status == status)
        
        if start_date:
            query = query.filter(ExecutionHistory.created_at >= start_date)
        
        if end_date:
            query = query.filter(ExecutionHistory.created_at <= end_date)
        
        # Order by most recent first
        query = query.order_by(ExecutionHistory.created_at.desc())
        
        # Apply pagination
        executions = query.offset(offset).limit(limit).all()
        
        return [execution.to_dict() for execution in executions]
    
    except Exception as e:
        logger.error(f"Failed to list executions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve execution history")


@router.get("/executions/{execution_id}", response_model=ExecutionHistoryResponse)
async def get_execution(
    execution_id: str,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific execution
    
    Args:
        execution_id: Execution UUID
        customer: Authenticated customer
        db: Database session
        
    Returns:
        Execution history record
    """
    try:
        execution = db.query(ExecutionHistory).filter(
            ExecutionHistory.id == execution_id,
            ExecutionHistory.customer_id == customer.id
        ).first()
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return execution.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get execution: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve execution")


@router.get("/stats", response_model=UsageStatsResponse)
async def get_usage_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    package_id: Optional[str] = None,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for the authenticated customer
    
    Args:
        start_date: Start of date range
        end_date: End of date range
        package_id: Filter by package ID
        customer: Authenticated customer
        db: Database session
        
    Returns:
        Usage statistics
    """
    try:
        tracker = get_usage_tracker(db)
        stats = tracker.get_usage_stats(
            customer_id=str(customer.id),
            start_date=start_date,
            end_date=end_date,
            package_id=package_id
        )
        
        return stats
    
    except Exception as e:
        logger.error(f"Failed to get usage stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve usage statistics")


@router.get("/packages/top", response_model=List[PackageUsageResponse])
async def get_top_packages(
    limit: int = Query(default=10, le=50),
    days: int = Query(default=30, le=365),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get top packages by usage
    
    Args:
        limit: Number of packages to return (max 50)
        days: Number of days to look back (max 365)
        customer: Authenticated customer
        db: Database session
        
    Returns:
        List of top packages with usage stats
    """
    try:
        tracker = get_usage_tracker(db)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        packages = tracker.get_top_packages(
            customer_id=str(customer.id),
            limit=limit,
            start_date=start_date
        )
        
        return packages
    
    except Exception as e:
        logger.error(f"Failed to get top packages: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve top packages")


@router.get("/daily", response_model=List[DailyUsageResponse])
async def get_daily_usage(
    days: int = Query(default=30, le=365),
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get daily usage for the past N days
    
    Args:
        days: Number of days to retrieve (max 365)
        customer: Authenticated customer
        db: Database session
        
    Returns:
        List of daily usage records
    """
    try:
        tracker = get_usage_tracker(db)
        usage = tracker.get_daily_usage(
            customer_id=str(customer.id),
            days=days
        )
        
        # Transform to response format
        return [
            {
                "date": record["period_start"],
                "total_executions": record["total_executions"],
                "successful_executions": record["successful_executions"],
                "failed_executions": record["failed_executions"],
                "total_tokens": record["total_tokens"],
                "total_cost": record["total_cost"],
                "avg_duration_ms": record["avg_duration_ms"]
            }
            for record in usage
        ]
    
    except Exception as e:
        logger.error(f"Failed to get daily usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve daily usage")


@router.get("/cost/current-month")
async def get_current_month_cost(
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get current month's cost
    
    Args:
        customer: Authenticated customer
        db: Database session
        
    Returns:
        Current month cost and projections
    """
    try:
        # Get start of current month
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        
        tracker = get_usage_tracker(db)
        stats = tracker.get_usage_stats(
            customer_id=str(customer.id),
            start_date=month_start,
            end_date=now
        )
        
        # Calculate daily average
        days_elapsed = (now - month_start).days + 1
        daily_avg = stats["total_cost"] / days_elapsed if days_elapsed > 0 else 0
        
        # Project end of month
        days_in_month = 30  # Simplified
        projected_cost = daily_avg * days_in_month
        
        return {
            "current_cost": stats["total_cost"],
            "total_executions": stats["total_executions"],
            "days_elapsed": days_elapsed,
            "daily_average": round(daily_avg, 2),
            "projected_month_end": round(projected_cost, 2),
            "period": {
                "start": month_start.isoformat(),
                "end": now.isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to get current month cost: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cost information")


@router.delete("/executions/{execution_id}")
async def delete_execution(
    execution_id: str,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Delete an execution record (soft delete by marking as deleted)
    
    Args:
        execution_id: Execution UUID
        customer: Authenticated customer
        db: Database session
        
    Returns:
        Success message
    """
    try:
        execution = db.query(ExecutionHistory).filter(
            ExecutionHistory.id == execution_id,
            ExecutionHistory.customer_id == customer.id
        ).first()
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Soft delete by updating metadata
        if not execution.metadata:
            execution.metadata = {}
        execution.metadata["deleted"] = True
        execution.metadata["deleted_at"] = datetime.utcnow().isoformat()
        
        db.commit()
        
        return {"message": "Execution deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete execution: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete execution")

