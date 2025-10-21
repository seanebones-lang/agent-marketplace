"""
Usage Tracking Service
Tracks agent executions for billing, analytics, and monitoring
"""
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
import tiktoken

from models.execution import ExecutionHistory, UsageAggregate
from core.logging import get_logger

logger = get_logger(__name__)


class UsageTracker:
    """
    Service for tracking agent usage and calculating costs
    
    Features:
    - Execution logging
    - Token counting
    - Cost calculation
    - Stripe usage record creation
    - Analytics aggregation
    """
    
    # Token costs per model (USD per 1K tokens)
    TOKEN_COSTS = {
        "claude-sonnet-4-20250514": {
            "input": 0.003,   # $3 per 1M input tokens
            "output": 0.015   # $15 per 1M output tokens
        },
        "claude-3-5-sonnet-20241022": {
            "input": 0.003,
            "output": 0.015
        },
        "gpt-4-turbo": {
            "input": 0.01,
            "output": 0.03
        },
        "gpt-4o": {
            "input": 0.005,
            "output": 0.015
        }
    }
    
    # Default model if not specified
    DEFAULT_MODEL = "claude-sonnet-4-20250514"
    
    def __init__(self, db: Session):
        self.db = db
        self.tokenizer = None
    
    def count_tokens(self, text: str, model: str = DEFAULT_MODEL) -> int:
        """
        Count tokens in text using tiktoken
        
        Args:
            text: Text to count tokens for
            model: Model name for tokenizer
            
        Returns:
            Number of tokens
        """
        try:
            # Use cl100k_base encoding for Claude/GPT-4
            if not self.tokenizer:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
            
            tokens = self.tokenizer.encode(text)
            return len(tokens)
        
        except Exception as e:
            logger.error(f"Token counting error: {e}")
            # Fallback: estimate 1 token per 4 characters
            return len(text) // 4
    
    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str = DEFAULT_MODEL
    ) -> float:
        """
        Calculate execution cost based on token usage
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model used for execution
            
        Returns:
            Cost in USD
        """
        costs = self.TOKEN_COSTS.get(model, self.TOKEN_COSTS[self.DEFAULT_MODEL])
        
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        total_cost = input_cost + output_cost
        
        return round(total_cost, 6)  # Round to 6 decimal places
    
    async def log_execution(
        self,
        customer_id: str,
        package_id: str,
        package_name: str,
        status: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        duration_ms: int = 0,
        customer_tier: Optional[str] = None,
        model_used: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExecutionHistory:
        """
        Log an agent execution to the database
        
        Args:
            customer_id: Customer UUID
            package_id: Agent package ID
            package_name: Agent package name
            status: Execution status (success, failed, timeout)
            input_data: Input parameters
            output_data: Output results
            error_message: Error message if failed
            duration_ms: Execution duration in milliseconds
            customer_tier: Customer tier at time of execution
            model_used: LLM model used
            metadata: Additional metadata
            
        Returns:
            ExecutionHistory record
        """
        try:
            # Count tokens
            input_tokens = 0
            output_tokens = 0
            
            if input_data:
                input_text = str(input_data)
                input_tokens = self.count_tokens(input_text, model_used or self.DEFAULT_MODEL)
            
            if output_data:
                output_text = str(output_data)
                output_tokens = self.count_tokens(output_text, model_used or self.DEFAULT_MODEL)
            
            total_tokens = input_tokens + output_tokens
            
            # Calculate cost
            cost = self.calculate_cost(
                input_tokens,
                output_tokens,
                model_used or self.DEFAULT_MODEL
            )
            
            # Create execution record
            execution = ExecutionHistory(
                customer_id=customer_id,
                package_id=package_id,
                package_name=package_name,
                status=status,
                input_data=input_data,
                output_data=output_data,
                error_message=error_message,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                cost=cost,
                duration_ms=duration_ms,
                customer_tier=customer_tier,
                model_used=model_used or self.DEFAULT_MODEL,
                metadata=metadata or {},
                created_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            
            self.db.add(execution)
            self.db.commit()
            self.db.refresh(execution)
            
            logger.info(
                f"Logged execution: customer={customer_id}, package={package_id}, "
                f"tokens={total_tokens}, cost=${cost:.6f}, status={status}"
            )
            
            # Send to Stripe for usage-based billing (async)
            if status == "success":
                asyncio.create_task(
                    self._report_to_stripe(customer_id, package_id, cost, total_tokens)
                )
            
            return execution
        
        except Exception as e:
            logger.error(f"Failed to log execution: {e}")
            self.db.rollback()
            raise
    
    async def _report_to_stripe(
        self,
        customer_id: str,
        package_id: str,
        cost: float,
        tokens: int
    ):
        """
        Report usage to Stripe for metered billing
        
        Args:
            customer_id: Customer UUID
            package_id: Package ID
            cost: Execution cost
            tokens: Token count
        """
        try:
            # TODO: Implement Stripe usage record creation
            # This would use stripe.SubscriptionItem.create_usage_record()
            logger.debug(f"Would report to Stripe: customer={customer_id}, cost=${cost:.6f}")
        
        except Exception as e:
            logger.error(f"Failed to report to Stripe: {e}")
    
    def get_usage_stats(
        self,
        customer_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        package_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get usage statistics for a customer
        
        Args:
            customer_id: Customer UUID
            start_date: Start of date range
            end_date: End of date range
            package_id: Optional package filter
            
        Returns:
            Usage statistics dictionary
        """
        try:
            query = self.db.query(ExecutionHistory).filter(
                ExecutionHistory.customer_id == customer_id
            )
            
            if start_date:
                query = query.filter(ExecutionHistory.created_at >= start_date)
            
            if end_date:
                query = query.filter(ExecutionHistory.created_at <= end_date)
            
            if package_id:
                query = query.filter(ExecutionHistory.package_id == package_id)
            
            # Calculate aggregates
            stats = query.with_entities(
                func.count(ExecutionHistory.id).label('total_executions'),
                func.sum(ExecutionHistory.total_tokens).label('total_tokens'),
                func.sum(ExecutionHistory.cost).label('total_cost'),
                func.avg(ExecutionHistory.duration_ms).label('avg_duration_ms'),
                func.count(func.distinct(ExecutionHistory.package_id)).label('unique_packages')
            ).first()
            
            # Count by status
            status_counts = dict(
                query.with_entities(
                    ExecutionHistory.status,
                    func.count(ExecutionHistory.id)
                ).group_by(ExecutionHistory.status).all()
            )
            
            return {
                "total_executions": stats.total_executions or 0,
                "total_tokens": stats.total_tokens or 0,
                "total_cost": float(stats.total_cost or 0.0),
                "avg_duration_ms": int(stats.avg_duration_ms or 0),
                "unique_packages": stats.unique_packages or 0,
                "status_breakdown": status_counts,
                "success_rate": (
                    (status_counts.get('success', 0) / stats.total_executions * 100)
                    if stats.total_executions else 0.0
                )
            }
        
        except Exception as e:
            logger.error(f"Failed to get usage stats: {e}")
            return {}
    
    def get_top_packages(
        self,
        customer_id: str,
        limit: int = 10,
        start_date: Optional[datetime] = None
    ) -> list:
        """
        Get top packages by usage for a customer
        
        Args:
            customer_id: Customer UUID
            limit: Number of packages to return
            start_date: Optional start date filter
            
        Returns:
            List of packages with usage stats
        """
        try:
            query = self.db.query(
                ExecutionHistory.package_id,
                ExecutionHistory.package_name,
                func.count(ExecutionHistory.id).label('execution_count'),
                func.sum(ExecutionHistory.total_tokens).label('total_tokens'),
                func.sum(ExecutionHistory.cost).label('total_cost')
            ).filter(
                ExecutionHistory.customer_id == customer_id
            )
            
            if start_date:
                query = query.filter(ExecutionHistory.created_at >= start_date)
            
            results = query.group_by(
                ExecutionHistory.package_id,
                ExecutionHistory.package_name
            ).order_by(
                func.count(ExecutionHistory.id).desc()
            ).limit(limit).all()
            
            return [
                {
                    "package_id": r.package_id,
                    "package_name": r.package_name,
                    "execution_count": r.execution_count,
                    "total_tokens": r.total_tokens or 0,
                    "total_cost": float(r.total_cost or 0.0)
                }
                for r in results
            ]
        
        except Exception as e:
            logger.error(f"Failed to get top packages: {e}")
            return []
    
    def get_daily_usage(
        self,
        customer_id: str,
        days: int = 30
    ) -> list:
        """
        Get daily usage for the past N days
        
        Args:
            customer_id: Customer UUID
            days: Number of days to retrieve
            
        Returns:
            List of daily usage records
        """
        try:
            # Use pre-aggregated data for better performance
            results = self.db.query(UsageAggregate).filter(
                UsageAggregate.customer_id == customer_id,
                UsageAggregate.period_type == 'daily',
                UsageAggregate.period_start >= datetime.utcnow() - timedelta(days=days)
            ).order_by(UsageAggregate.period_start).all()
            
            return [r.to_dict() for r in results]
        
        except Exception as e:
            logger.error(f"Failed to get daily usage: {e}")
            return []


# Singleton instance
_usage_tracker: Optional[UsageTracker] = None


def get_usage_tracker(db: Session) -> UsageTracker:
    """Get or create usage tracker instance"""
    global _usage_tracker
    if _usage_tracker is None or _usage_tracker.db != db:
        _usage_tracker = UsageTracker(db)
    return _usage_tracker

