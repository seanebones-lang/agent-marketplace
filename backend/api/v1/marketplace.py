"""Marketplace API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import time
import uuid

from database import get_db
from api.deps import get_current_customer
from models.customer import Customer
from core.agent_engine import agent_engine
from core.rate_limiter import get_rate_limiter
from core.usage_tracker import UsageTracker, UsageRecord
from core.logging import get_logger

logger = get_logger(__name__)

# Import all agent packages
from agents.packages import (
    TicketResolverAgent,
    KnowledgeBaseAgent,
    IncidentResponderAgent,
    DataProcessorAgent,
    ReportGeneratorAgent,
    WorkflowOrchestratorAgent,
    EscalationManagerAgent,
    DeploymentAgent,
    AuditAgent,
    SecurityScannerAgent
)

router = APIRouter()


class AgentPackageResponse(BaseModel):
    """Agent package listing response"""
    id: str
    name: str
    category: str
    description: str
    pricing: dict
    features: Optional[List[str]] = None
    metrics: Optional[dict] = None


class TaskExecutionRequest(BaseModel):
    """Task execution request"""
    task: str
    engine_type: Optional[str] = "langgraph"  # langgraph or crewai
    timeout: Optional[int] = 300


class TaskExecutionResponse(BaseModel):
    """Task execution response"""
    execution_id: str
    status: str
    result: dict
    tokens_used: int
    cost: float
    duration_ms: int
    metadata: dict


# Initialize all agent packages
AGENT_PACKAGES = {
    "ticket-resolver": TicketResolverAgent(),
    "knowledge-base": KnowledgeBaseAgent(),
    "incident-responder": IncidentResponderAgent(),
    "data-processor": DataProcessorAgent(),
    "report-generator": ReportGeneratorAgent(),
    "workflow-orchestrator": WorkflowOrchestratorAgent(),
    "escalation-manager": EscalationManagerAgent(),
    "deployment-agent": DeploymentAgent(),
    "audit-agent": AuditAgent(),
    "security-scanner": SecurityScannerAgent()
}

# Register packages with agent engine
for package_id, agent_instance in AGENT_PACKAGES.items():
    agent_engine.register_package(agent_instance.package)


@router.get("/packages", response_model=List[AgentPackageResponse])
async def list_packages(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all available agent packages.
    
    Args:
        category: Optional filter by category
        db: Database session
        
    Returns:
        List of agent packages
    """
    packages = []
    
    for package_id, agent_instance in AGENT_PACKAGES.items():
        package_info = agent_instance.get_package_info()
        
        # Filter by category if specified
        if category and package_info["category"] != category:
            continue
        
        packages.append(AgentPackageResponse(**package_info))
    
    return packages


@router.get("/packages/{package_id}", response_model=AgentPackageResponse)
async def get_package(
    package_id: str,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific agent package.
    
    Args:
        package_id: Package identifier
        db: Database session
        
    Returns:
        Agent package details
    """
    agent_instance = AGENT_PACKAGES.get(package_id)
    
    if not agent_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Package not found: {package_id}"
        )
    
    package_info = agent_instance.get_package_info()
    return AgentPackageResponse(**package_info)


@router.post("/packages/{package_id}/execute", response_model=TaskExecutionResponse)
async def execute_task(
    package_id: str,
    request: TaskExecutionRequest,
    http_request: Request,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Execute a task using the specified agent package with rate limiting and usage tracking.
    
    Args:
        package_id: Package identifier
        request: Task execution request
        http_request: HTTP request for rate limiter access
        customer: Authenticated customer
        db: Database session
        
    Returns:
        Task execution result
    """
    # Validate package exists
    if package_id not in AGENT_PACKAGES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Package not found: {package_id}"
        )
    
    # Get customer tier
    customer_tier = getattr(customer, 'tier', 'solo')
    customer_id = str(customer.id)
    
    # Get rate limiter from app state
    rate_limiter = getattr(http_request.app.state, "rate_limiter", None)
    
    if rate_limiter:
        # Check concurrent execution limit
        concurrent_allowed, concurrent_count = await rate_limiter.check_concurrent_limit(
            customer_id=customer_id,
            tier=customer_tier
        )
        
        if not concurrent_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Concurrent execution limit exceeded",
                    "message": f"You have {concurrent_count} concurrent executions running. Your {customer_tier} tier allows a maximum of concurrent executions.",
                    "tier": customer_tier,
                    "current": concurrent_count
                }
            )
        
        # Check agent-specific rate limit
        agent_allowed, agent_metadata = await rate_limiter.check_agent_limit(
            customer_id=customer_id,
            agent_id=package_id,
            tier=customer_tier
        )
        
        if not agent_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Agent rate limit exceeded",
                    "message": f"You have exceeded the rate limit for {package_id} on your {customer_tier} tier",
                    "metadata": agent_metadata
                },
                headers={
                    "X-RateLimit-Limit": str(agent_metadata.get("limit", 0)),
                    "X-RateLimit-Remaining": str(agent_metadata.get("remaining", 0)),
                    "X-RateLimit-Reset": str(agent_metadata.get("reset", 0)),
                    "Retry-After": str(agent_metadata.get("retry_after", 60))
                }
            )
        
        # Increment concurrent counter
        await rate_limiter.increment_concurrent(customer_id)
    
    # Execute agent task
    start_time = time.time()
    execution_id = str(uuid.uuid4())
    execution_status = "failed"
    result_data = {}
    tokens_used = 0
    cost = 0.0
    
    try:
        result = await agent_engine.execute(
            package_id=package_id,
            task=request.task,
            engine_type=request.engine_type,
            timeout=request.timeout
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        execution_status = result.status
        result_data = result.output
        tokens_used = result.tokens_used
        cost = result.cost
        
        # Log usage to database for billing
        usage_tracker = UsageTracker()
        usage_record = UsageRecord(
            customer_id=customer.id,
            package_id=package_id,
            task_input={"task": request.task, "engine_type": request.engine_type},
            task_output=result.output,
            status=result.status,
            tokens_used=result.tokens_used,
            cost=result.cost,
            duration_ms=result.duration_ms,
            metadata={
                "execution_id": execution_id,
                "tier": customer_tier,
                "timeout": request.timeout
            }
        )
        
        try:
            usage_tracker.record_usage(db, usage_record)
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")
            # Don't fail the request if usage tracking fails
        
        # Record token usage for rate limiting
        if rate_limiter:
            await rate_limiter.record_token_usage(customer_id, result.tokens_used)
        
        return TaskExecutionResponse(
            execution_id=execution_id,
            status=result.status,
            result=result.output,
            tokens_used=result.tokens_used,
            cost=result.cost,
            duration_ms=result.duration_ms,
            metadata={
                "customer_id": str(customer.id),
                "package_id": package_id,
                "engine_type": request.engine_type,
                "tier": customer_tier,
                **result.metadata
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like rate limits)
        raise
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        
        # Log failed execution
        usage_tracker = UsageTracker()
        usage_record = UsageRecord(
            customer_id=customer.id,
            package_id=package_id,
            task_input={"task": request.task, "engine_type": request.engine_type},
            task_output={"error": str(e)},
            status="failed",
            tokens_used=0,
            cost=0.0,
            duration_ms=duration_ms,
            metadata={"execution_id": execution_id, "tier": customer_tier, "error": str(e)}
        )
        
        try:
            usage_tracker.record_usage(db, usage_record)
        except Exception as log_error:
            logger.error(f"Failed to record failed execution: {log_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )
    finally:
        # Always decrement concurrent counter
        if rate_limiter:
            await rate_limiter.decrement_concurrent(customer_id)


@router.get("/categories")
async def list_categories():
    """
    List all available agent categories.
    
    Returns:
        List of unique categories
    """
    categories = set()
    for agent_instance in AGENT_PACKAGES.values():
        package_info = agent_instance.get_package_info()
        categories.add(package_info["category"])
    
    return {"categories": sorted(list(categories))}

