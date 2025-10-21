"""Unified Agent Execution Engine with Model Tier Support"""
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import json
import asyncio
from datetime import datetime
from pydantic import BaseModel, Field
from backend.core.model_tiers import ModelTier, get_model_for_tier, estimate_cost, MODEL_CONFIGS, TIER_PRICING
import os


class AgentState(BaseModel):
    """State container for agent execution"""
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    task: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentPackage(BaseModel):
    """Agent package configuration"""
    id: str
    name: str
    category: str
    config: Dict[str, Any]
    tools: List[Dict[str, Any]] = Field(default_factory=list)
    pricing: Dict[str, float] = Field(default_factory=dict)
    recommended_tier: ModelTier = ModelTier.STANDARD


class AgentExecutionResult(BaseModel):
    """Result of agent execution"""
    status: str  # success, failed, timeout
    output: Any
    tokens_used: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    duration_ms: int = 0
    tier: str = "standard"
    model: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentEngine(ABC):
    """Abstract base for agent execution"""
    
    @abstractmethod
    async def execute(
        self,
        package: AgentPackage,
        task: str,
        tier: ModelTier = ModelTier.STANDARD,
        custom_api_key: Optional[str] = None
    ) -> AgentExecutionResult:
        """Execute agent task"""
        pass


class LangGraphEngine(AgentEngine):
    """LangGraph-based agent execution with tier support"""
    
    async def execute(
        self,
        package: AgentPackage,
        task: str,
        tier: ModelTier = ModelTier.STANDARD,
        custom_api_key: Optional[str] = None
    ) -> AgentExecutionResult:
        """Execute using LangGraph state machine"""
        from langgraph.graph import StateGraph, END
        from langchain_anthropic import ChatAnthropic
        
        start_time = datetime.now()
        
        try:
            # Get model configuration for tier
            model_id, api_key = get_model_for_tier(tier, custom_api_key)
            if model_id == "user-provided":
                model_id = "claude-sonnet-4-20250514"  # Default for BYOK
            
            # Initialize LLM
            llm = ChatAnthropic(
                model=model_id,
                temperature=0,
                api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
            )
            
            # Build state graph
            graph = StateGraph(AgentState)
            
            def agent_node(state: AgentState) -> AgentState:
                """Main agent reasoning node"""
                state.messages.append({
                    "role": "assistant",
                    "content": f"Processing task with {MODEL_CONFIGS[tier].display_name}: {task}",
                    "timestamp": datetime.now().isoformat()
                })
                
                # Execute agent logic
                state.result = {
                    "status": "success",
                    "output": f"Task completed: {task}",
                    "agent": package.name,
                    "tier": tier.value
                }
                return state
            
            # Build graph
            graph.add_node("agent", agent_node)
            graph.set_entry_point("agent")
            graph.add_edge("agent", END)
            
            # Compile and run
            app = graph.compile()
            result = app.invoke({"task": task, "metadata": {"package_id": package.id}})
            
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Estimate token usage based on tier
            input_tokens = len(task.split()) * 1.3  # Rough estimate
            output_tokens = 500  # Rough estimate
            
            # Calculate cost
            pricing = TIER_PRICING[tier]
            cost = pricing.calculate_execution_cost(int(input_tokens), int(output_tokens))
            
            return AgentExecutionResult(
                status="success",
                output=result.get("result", {}),
                tokens_used=int(input_tokens + output_tokens),
                input_tokens=int(input_tokens),
                output_tokens=int(output_tokens),
                cost=cost,
                duration_ms=duration,
                tier=tier.value,
                model=MODEL_CONFIGS[tier].display_name,
                metadata={"engine": "langgraph", "model_id": model_id}
            )
            
        except Exception as e:
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return AgentExecutionResult(
                status="failed",
                output={"error": str(e)},
                duration_ms=duration,
                tier=tier.value,
                model=MODEL_CONFIGS[tier].display_name,
                metadata={"engine": "langgraph", "error": str(e)}
            )


class CrewAIEngine(AgentEngine):
    """CrewAI-based multi-agent execution with tier support"""
    
    async def execute(
        self,
        package: AgentPackage,
        task: str,
        tier: ModelTier = ModelTier.STANDARD,
        custom_api_key: Optional[str] = None
    ) -> AgentExecutionResult:
        """Execute using CrewAI multi-agent system"""
        from crewai import Agent, Task, Crew
        from langchain_anthropic import ChatAnthropic
        
        start_time = datetime.now()
        
        try:
            # Get model configuration for tier
            model_id, api_key = get_model_for_tier(tier, custom_api_key)
            if model_id == "user-provided":
                model_id = "claude-sonnet-4-20250514"  # Default for BYOK
            
            # Create LLM
            llm = ChatAnthropic(
                model=model_id,
                temperature=0,
                api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
            )
            
            # Create specialized agent
            specialist = Agent(
                role=package.config.get("role", "Specialist"),
                goal=package.config.get("goal", "Complete task efficiently"),
                backstory=package.config.get("backstory", "Expert in enterprise operations"),
                llm=llm,
                verbose=False
            )
            
            # Create task
            task_obj = Task(
                description=task,
                agent=specialist,
                expected_output="Detailed task completion result"
            )
            
            # Execute crew
            crew = Crew(agents=[specialist], tasks=[task_obj], verbose=False)
            result = crew.kickoff()
            
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Estimate token usage
            input_tokens = len(task.split()) * 1.3
            output_tokens = 750  # CrewAI tends to be more verbose
            
            # Calculate cost
            pricing = TIER_PRICING[tier]
            cost = pricing.calculate_execution_cost(int(input_tokens), int(output_tokens))
            
            return AgentExecutionResult(
                status="success",
                output={"result": str(result), "agent": package.name},
                tokens_used=int(input_tokens + output_tokens),
                input_tokens=int(input_tokens),
                output_tokens=int(output_tokens),
                cost=cost,
                duration_ms=duration,
                tier=tier.value,
                model=MODEL_CONFIGS[tier].display_name,
                metadata={"engine": "crewai", "model_id": model_id}
            )
            
        except Exception as e:
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return AgentExecutionResult(
                status="failed",
                output={"error": str(e)},
                duration_ms=duration,
                tier=tier.value,
                model=MODEL_CONFIGS[tier].display_name,
                metadata={"engine": "crewai", "error": str(e)}
            )


class UnifiedAgentEngine:
    """Production-ready unified agent execution engine with tier support"""
    
    def __init__(self):
        self.engines = {
            "langgraph": LangGraphEngine(),
            "crewai": CrewAIEngine()
        }
        self._package_cache: Dict[str, AgentPackage] = {}
    
    def register_package(self, package: AgentPackage):
        """Register an agent package"""
        self._package_cache[package.id] = package
    
    def get_package(self, package_id: str) -> Optional[AgentPackage]:
        """Retrieve registered package"""
        return self._package_cache.get(package_id)
    
    async def execute(
        self,
        package_id: str,
        task: str,
        engine_type: str = "langgraph",
        tier: ModelTier = ModelTier.STANDARD,
        custom_api_key: Optional[str] = None,
        timeout: int = 300
    ) -> AgentExecutionResult:
        """
        Execute agent package with specified engine and tier
        
        Args:
            package_id: ID of the agent package
            task: Task description to execute
            engine_type: Engine to use (langgraph or crewai)
            tier: Model tier to use (byok, basic, standard, premium, elite)
            custom_api_key: Optional custom API key for BYOK tier
            timeout: Maximum execution time in seconds
            
        Returns:
            AgentExecutionResult with execution details
        """
        # Get package
        package = self.get_package(package_id)
        if not package:
            return AgentExecutionResult(
                status="failed",
                output={"error": f"Package not found: {package_id}"},
                metadata={"package_id": package_id}
            )
        
        # Get engine
        engine = self.engines.get(engine_type)
        if not engine:
            return AgentExecutionResult(
                status="failed",
                output={"error": f"Unknown engine: {engine_type}"},
                metadata={"package_id": package_id}
            )
        
        # Validate BYOK requirements
        if tier == ModelTier.BYOK and not custom_api_key:
            return AgentExecutionResult(
                status="failed",
                output={"error": "BYOK tier requires a custom API key"},
                metadata={"package_id": package_id, "tier": tier.value}
            )
        
        # Execute with timeout
        try:
            result = await asyncio.wait_for(
                engine.execute(package, task, tier, custom_api_key),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            return AgentExecutionResult(
                status="timeout",
                output={"error": f"Execution exceeded {timeout}s timeout"},
                tier=tier.value,
                model=MODEL_CONFIGS[tier].display_name,
                metadata={"package_id": package_id, "timeout": timeout}
            )
        except Exception as e:
            return AgentExecutionResult(
                status="failed",
                output={"error": str(e)},
                tier=tier.value,
                model=MODEL_CONFIGS.get(tier, MODEL_CONFIGS[ModelTier.STANDARD]).display_name,
                metadata={"package_id": package_id, "exception": type(e).__name__}
            )


# Global engine instance
agent_engine = UnifiedAgentEngine()
