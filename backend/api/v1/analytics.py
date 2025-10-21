"""
Analytics API Endpoints

This module provides usage analytics and dashboard data.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from database import get_db
from models.customer import Customer
from models.deployment import UsageLog
from core.security import verify_bearer_token


router = APIRouter(prefix="/analytics", tags=["Analytics"])


class UsageStats(BaseModel):
    """Usage statistics model"""
    total_executions: int
    total_cost: float
    total_tokens: int
    avg_execution_time_ms: float
    success_rate: float


class PackageStats(BaseModel):
    """Per-package statistics"""
    package_id: str
    executions: int
    cost: float
    tokens: int
    avg_time_ms: float
    success_rate: float


class TimeSeriesPoint(BaseModel):
    """Time series data point"""
    timestamp: str
    value: float


class DashboardData(BaseModel):
    """Dashboard overview data"""
    total_executions: int
    total_cost: float
    executions_today: int
    cost_today: float
    top_packages: List[PackageStats]
    recent_executions: List[dict]


@router.get("/overview", response_model=UsageStats)
async def get_usage_overview(
    days: int = Query(30, ge=1, le=365),
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Get usage overview statistics.
    
    Args:
        days: Number of days to include
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        Usage statistics
    """
    customer_id = token_data.get("customer_id")
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get usage logs
    logs = db.query(UsageLog).filter(
        UsageLog.customer_id == customer_id,
        UsageLog.created_at >= cutoff_date
    ).all()
    
    if not logs:
        return UsageStats(
            total_executions=0,
            total_cost=0.0,
            total_tokens=0,
            avg_execution_time_ms=0.0,
            success_rate=0.0
        )
    
    # Calculate statistics
    total_executions = len(logs)
    total_cost = sum(log.cost for log in logs)
    total_tokens = sum(log.tokens_used for log in logs)
    avg_execution_time = sum(log.execution_time_ms for log in logs) / total_executions
    successful = sum(1 for log in logs if log.status == "success")
    success_rate = (successful / total_executions) * 100
    
    return UsageStats(
        total_executions=total_executions,
        total_cost=total_cost,
        total_tokens=total_tokens,
        avg_execution_time_ms=avg_execution_time,
        success_rate=success_rate
    )


@router.get("/packages", response_model=List[PackageStats])
async def get_package_statistics(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=100),
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Get per-package statistics.
    
    Args:
        days: Number of days to include
        limit: Maximum number of packages to return
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        List of package statistics
    """
    customer_id = token_data.get("customer_id")
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Query package statistics
    package_stats = db.query(
        UsageLog.package_id,
        func.count(UsageLog.id).label('executions'),
        func.sum(UsageLog.cost).label('cost'),
        func.sum(UsageLog.tokens_used).label('tokens'),
        func.avg(UsageLog.execution_time_ms).label('avg_time'),
        func.sum(func.case((UsageLog.status == 'success', 1), else_=0)).label('successes')
    ).filter(
        UsageLog.customer_id == customer_id,
        UsageLog.created_at >= cutoff_date
    ).group_by(
        UsageLog.package_id
    ).order_by(
        func.count(UsageLog.id).desc()
    ).limit(limit).all()
    
    results = []
    for stat in package_stats:
        success_rate = (stat.successes / stat.executions * 100) if stat.executions > 0 else 0
        
        results.append(PackageStats(
            package_id=stat.package_id,
            executions=stat.executions,
            cost=float(stat.cost or 0),
            tokens=int(stat.tokens or 0),
            avg_time_ms=float(stat.avg_time or 0),
            success_rate=success_rate
        ))
    
    return results


@router.get("/timeseries/executions", response_model=List[TimeSeriesPoint])
async def get_executions_timeseries(
    days: int = Query(30, ge=1, le=365),
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Get executions time series data.
    
    Args:
        days: Number of days to include
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        Time series data points
    """
    customer_id = token_data.get("customer_id")
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Query daily execution counts
    daily_stats = db.query(
        func.date(UsageLog.created_at).label('date'),
        func.count(UsageLog.id).label('count')
    ).filter(
        UsageLog.customer_id == customer_id,
        UsageLog.created_at >= cutoff_date
    ).group_by(
        func.date(UsageLog.created_at)
    ).order_by(
        func.date(UsageLog.created_at)
    ).all()
    
    return [
        TimeSeriesPoint(
            timestamp=stat.date.isoformat(),
            value=float(stat.count)
        )
        for stat in daily_stats
    ]


@router.get("/timeseries/cost", response_model=List[TimeSeriesPoint])
async def get_cost_timeseries(
    days: int = Query(30, ge=1, le=365),
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Get cost time series data.
    
    Args:
        days: Number of days to include
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        Time series data points
    """
    customer_id = token_data.get("customer_id")
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Query daily cost totals
    daily_stats = db.query(
        func.date(UsageLog.created_at).label('date'),
        func.sum(UsageLog.cost).label('total_cost')
    ).filter(
        UsageLog.customer_id == customer_id,
        UsageLog.created_at >= cutoff_date
    ).group_by(
        func.date(UsageLog.created_at)
    ).order_by(
        func.date(UsageLog.created_at)
    ).all()
    
    return [
        TimeSeriesPoint(
            timestamp=stat.date.isoformat(),
            value=float(stat.total_cost or 0)
        )
        for stat in daily_stats
    ]


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Get dashboard overview data.
    
    Args:
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        Dashboard data
    """
    customer_id = token_data.get("customer_id")
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Total statistics
    total_executions = db.query(func.count(UsageLog.id)).filter(
        UsageLog.customer_id == customer_id
    ).scalar()
    
    total_cost = db.query(func.sum(UsageLog.cost)).filter(
        UsageLog.customer_id == customer_id
    ).scalar() or 0
    
    # Today's statistics
    executions_today = db.query(func.count(UsageLog.id)).filter(
        UsageLog.customer_id == customer_id,
        UsageLog.created_at >= today_start
    ).scalar()
    
    cost_today = db.query(func.sum(UsageLog.cost)).filter(
        UsageLog.customer_id == customer_id,
        UsageLog.created_at >= today_start
    ).scalar() or 0
    
    # Top packages (last 30 days)
    cutoff_30days = datetime.utcnow() - timedelta(days=30)
    package_stats = db.query(
        UsageLog.package_id,
        func.count(UsageLog.id).label('executions'),
        func.sum(UsageLog.cost).label('cost'),
        func.sum(UsageLog.tokens_used).label('tokens'),
        func.avg(UsageLog.execution_time_ms).label('avg_time'),
        func.sum(func.case((UsageLog.status == 'success', 1), else_=0)).label('successes')
    ).filter(
        UsageLog.customer_id == customer_id,
        UsageLog.created_at >= cutoff_30days
    ).group_by(
        UsageLog.package_id
    ).order_by(
        func.count(UsageLog.id).desc()
    ).limit(5).all()
    
    top_packages = []
    for stat in package_stats:
        success_rate = (stat.successes / stat.executions * 100) if stat.executions > 0 else 0
        top_packages.append(PackageStats(
            package_id=stat.package_id,
            executions=stat.executions,
            cost=float(stat.cost or 0),
            tokens=int(stat.tokens or 0),
            avg_time_ms=float(stat.avg_time or 0),
            success_rate=success_rate
        ))
    
    # Recent executions
    recent_logs = db.query(UsageLog).filter(
        UsageLog.customer_id == customer_id
    ).order_by(
        UsageLog.created_at.desc()
    ).limit(10).all()
    
    recent_executions = [
        {
            "id": log.id,
            "package_id": log.package_id,
            "status": log.status,
            "cost": log.cost,
            "execution_time_ms": log.execution_time_ms,
            "created_at": log.created_at.isoformat()
        }
        for log in recent_logs
    ]
    
    return DashboardData(
        total_executions=total_executions,
        total_cost=float(total_cost),
        executions_today=executions_today,
        cost_today=float(cost_today),
        top_packages=top_packages,
        recent_executions=recent_executions
    )


@router.get("/export")
async def export_usage_data(
    days: int = Query(30, ge=1, le=365),
    format: str = Query("json", regex="^(json|csv)$"),
    token_data: dict = Depends(verify_bearer_token),
    db: Session = Depends(get_db)
):
    """
    Export usage data.
    
    Args:
        days: Number of days to include
        format: Export format (json or csv)
        token_data: Decoded JWT token
        db: Database session
        
    Returns:
        Exported data
    """
    customer_id = token_data.get("customer_id")
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    logs = db.query(UsageLog).filter(
        UsageLog.customer_id == customer_id,
        UsageLog.created_at >= cutoff_date
    ).all()
    
    data = [
        {
            "id": log.id,
            "package_id": log.package_id,
            "execution_time_ms": log.execution_time_ms,
            "tokens_used": log.tokens_used,
            "cost": log.cost,
            "status": log.status,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]
    
    if format == "csv":
        # Convert to CSV format
        import csv
        import io
        
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        return {
            "format": "csv",
            "data": output.getvalue()
        }
    
    return {
        "format": "json",
        "data": data
    }

