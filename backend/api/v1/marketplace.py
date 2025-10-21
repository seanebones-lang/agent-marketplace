"""Marketplace API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import time

from database import get_db
from api.deps import get_current_customer
from models.customer import Customer
from core.agent_engine import agent_engine

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
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Execute a task using the specified agent package.
    
    Args:
        package_id: Package identifier
        request: Task execution request
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
    
    # Execute agent task
    start_time = time.time()
    
    try:
        result = await agent_engine.execute(
            package_id=package_id,
            task=request.task,
            engine_type=request.engine_type,
            timeout=request.timeout
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Generate execution ID
        import uuid
        execution_id = str(uuid.uuid4())
        
        # TODO: Log usage to database for billing
        
        return TaskExecutionResponse(
            execution_id=execution_id,
            status=result.status,
            result=result.output,
            tokens_used=result.tokens_used,
            cost=result.cost,
            duration_ms=result.duration_ms,
            metadata={
                "customer_id": customer.id,
                "package_id": package_id,
                "engine_type": request.engine_type,
                **result.metadata
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )


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

