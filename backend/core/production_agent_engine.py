"""
Production Agent Engine - Integrates all real AI agents
"""
import os
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

# Import all production agents
from backend.agents.packages.security_scanner import create_security_scanner_agent, SecurityScanResult
from backend.agents.packages.incident_responder import create_incident_responder_agent, IncidentAnalysis
from backend.agents.packages.ticket_resolver import create_ticket_resolver_agent, TicketAnalysis
from backend.agents.packages.knowledge_base import create_knowledge_base_agent, KnowledgeResponse


class ProductionAgentEngine:
    """
    Production-ready agent execution engine with real AI agents
    """
    
    def __init__(self):
        # Get API key from environment
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize production agents
        self.agents = {
            "security-scanner": create_security_scanner_agent(self.api_key),
            "incident-responder": create_incident_responder_agent(self.api_key),
            "ticket-resolver": create_ticket_resolver_agent(self.api_key),
            "knowledge-base": create_knowledge_base_agent(
                self.api_key,
                qdrant_host=os.getenv("QDRANT_HOST", "localhost"),
                qdrant_port=int(os.getenv("QDRANT_PORT", "6333"))
            )
        }
        
        # Agent metadata
        self.agent_metadata = {
            "security-scanner": {
                "name": "Security Scanner",
                "category": "Security",
                "description": "Automated security vulnerability scanning and compliance checking",
                "version": "2.1.0",
                "status": "production",
                "price_per_execution": 0.05,
                "avg_duration_ms": 2300,
                "success_rate": 99.8
            },
            "incident-responder": {
                "name": "Incident Responder",
                "category": "Operations",
                "description": "Intelligent incident triage and root cause analysis",
                "version": "2.0.0",
                "status": "production",
                "price_per_execution": 0.08,
                "avg_duration_ms": 1800,
                "success_rate": 99.5
            },
            "ticket-resolver": {
                "name": "Ticket Resolver",
                "category": "Support",
                "description": "Automated ticket classification and resolution",
                "version": "1.9.0",
                "status": "production",
                "price_per_execution": 0.03,
                "avg_duration_ms": 1200,
                "success_rate": 98.9
            },
            "knowledge-base": {
                "name": "Knowledge Base",
                "category": "Knowledge",
                "description": "Intelligent knowledge management with RAG",
                "version": "2.2.0",
                "status": "production",
                "price_per_execution": 0.04,
                "avg_duration_ms": 800,
                "success_rate": 99.2
            }
        }
    
    def get_available_agents(self) -> list[Dict[str, Any]]:
        """Get list of available production agents"""
        return [
            {
                "id": agent_id,
                **metadata
            }
            for agent_id, metadata in self.agent_metadata.items()
        ]
    
    def get_agent_details(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific agent"""
        if agent_id in self.agent_metadata:
            return {
                "id": agent_id,
                **self.agent_metadata[agent_id]
            }
        return None
    
    async def execute_agent(
        self,
        agent_id: str,
        input_data: Dict[str, Any],
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a production agent
        
        Args:
            agent_id: ID of the agent to execute
            input_data: Input data for the agent
            customer_id: Optional customer ID for billing
            
        Returns:
            Execution result with status, output, and metadata
        """
        start_time = datetime.now()
        
        # Check if agent exists
        if agent_id not in self.agents:
            return {
                "status": "error",
                "error": f"Agent not found: {agent_id}",
                "agent_id": agent_id,
                "execution_time_ms": 0
            }
        
        # Get agent
        agent = self.agents[agent_id]
        metadata = self.agent_metadata[agent_id]
        
        try:
            # Execute agent based on type
            if agent_id == "security-scanner":
                result = await agent.execute(input_data)
                output = result.dict()
                
            elif agent_id == "incident-responder":
                result = await agent.execute(input_data)
                output = result.dict()
                
            elif agent_id == "ticket-resolver":
                result = await agent.execute(input_data)
                output = result.dict()
                
            elif agent_id == "knowledge-base":
                result = await agent.execute(input_data)
                output = result.dict()
            
            else:
                output = {"error": "Agent execution not implemented"}
            
            # Calculate execution time
            execution_time = datetime.now() - start_time
            execution_time_ms = int(execution_time.total_seconds() * 1000)
            
            # Calculate cost
            cost = metadata["price_per_execution"]
            
            return {
                "status": "success",
                "agent_id": agent_id,
                "agent_name": metadata["name"],
                "output": output,
                "execution_time_ms": execution_time_ms,
                "cost": cost,
                "timestamp": datetime.now().isoformat(),
                "customer_id": customer_id
            }
        
        except Exception as e:
            execution_time = datetime.now() - start_time
            execution_time_ms = int(execution_time.total_seconds() * 1000)
            
            return {
                "status": "error",
                "agent_id": agent_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time_ms": execution_time_ms,
                "timestamp": datetime.now().isoformat()
            }
    
    def is_agent_available(self, agent_id: str) -> bool:
        """Check if an agent is available"""
        return agent_id in self.agents
    
    def get_agent_status(self, agent_id: str) -> str:
        """Get agent status"""
        if agent_id in self.agent_metadata:
            return self.agent_metadata[agent_id]["status"]
        return "not_found"


# Global production engine instance
production_engine = ProductionAgentEngine()

