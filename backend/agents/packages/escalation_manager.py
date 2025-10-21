"""Escalation Management Agent"""
from pydantic import BaseModel
from typing import Dict, Any
from core.agent_engine import AgentPackage


class EscalationManagerAgent:
    """Smart routing to human agents"""
    
    PACKAGE_ID = "escalation-manager"
    
    def __init__(self):
        self.package = AgentPackage(
            id=self.PACKAGE_ID,
            name="Escalation Manager",
            category="customer-support",
            config={
                "role": "Escalation Specialist",
                "goal": "Route complex issues to appropriate human agents",
                "backstory": "Expert in issue triage and escalation"
            },
            tools=[
                {"name": "skill_matcher", "description": "Match issues to agent skills", "enabled": True},
                {"name": "priority_calculator", "description": "Calculate priority", "enabled": True}
            ],
            pricing={"per_escalation": 0.25, "monthly_subscription": 100.00}
        )
    
    def get_package_info(self) -> Dict[str, Any]:
        return {
            "id": self.package.id,
            "name": self.package.name,
            "category": self.package.category,
            "description": "Intelligent escalation routing with skill matching",
            "pricing": self.package.pricing
        }

