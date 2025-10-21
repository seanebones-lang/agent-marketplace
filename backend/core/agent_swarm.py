"""
Real-Time Agent Collaboration Swarm System
100+ agents collaborating in real-time for complex tasks
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Agent roles in swarm"""
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    ENGINEER = "engineer"
    REVIEWER = "reviewer"
    EXECUTOR = "executor"
    VALIDATOR = "validator"


class SwarmState(str, Enum):
    """Swarm execution states"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    COORDINATING = "coordinating"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentTask:
    """Individual agent task"""
    task_id: str
    agent_id: str
    role: AgentRole
    description: str
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class SwarmConfig:
    """Swarm configuration"""
    max_agents: int = 100
    max_parallel_tasks: int = 20
    timeout_seconds: int = 300
    enable_auto_scaling: bool = True
    min_agents_per_role: Dict[AgentRole, int] = field(default_factory=lambda: {
        AgentRole.COORDINATOR: 1,
        AgentRole.RESEARCHER: 2,
        AgentRole.ANALYST: 2,
        AgentRole.ENGINEER: 3,
        AgentRole.REVIEWER: 2,
        AgentRole.EXECUTOR: 5,
        AgentRole.VALIDATOR: 2
    })


@dataclass
class Swarm:
    """Agent swarm instance"""
    swarm_id: str
    task_description: str
    config: SwarmConfig
    state: SwarmState = SwarmState.INITIALIZING
    agents: Dict[str, AgentTask] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class AgentSwarm:
    """
    Real-time multi-agent swarm coordination system
    Manages 100+ agents collaborating on complex tasks
    """
    
    def __init__(self, config: Optional[SwarmConfig] = None):
        self.config = config or SwarmConfig()
        self.active_swarms: Dict[str, Swarm] = {}
        self.agent_pool: Dict[AgentRole, List[str]] = {role: [] for role in AgentRole}
        
        # Performance tracking
        self.swarm_metrics: Dict[str, Dict[str, Any]] = {}
    
    async def spawn_swarm(
        self,
        task_description: str,
        task_complexity: float = 0.5
    ) -> Swarm:
        """
        Spawn a new agent swarm for a complex task
        
        Args:
            task_description: Description of the task
            task_complexity: Complexity score (0-1)
        
        Returns:
            Swarm instance
        """
        swarm_id = str(uuid.uuid4())
        
        # Create swarm configuration based on complexity
        swarm_config = self._dynamic_swarm_config(task_complexity)
        
        swarm = Swarm(
            swarm_id=swarm_id,
            task_description=task_description,
            config=swarm_config,
            state=SwarmState.INITIALIZING
        )
        
        self.active_swarms[swarm_id] = swarm
        
        logger.info(f"Spawned swarm {swarm_id} for task: {task_description[:100]}")
        
        # Initialize swarm
        await self._initialize_swarm(swarm)
        
        return swarm
    
    def _dynamic_swarm_config(self, complexity: float) -> SwarmConfig:
        """Generate swarm configuration based on task complexity"""
        # Scale agent counts based on complexity
        base_config = SwarmConfig()
        
        if complexity < 0.3:
            # Simple task - small swarm
            base_config.min_agents_per_role = {
                AgentRole.COORDINATOR: 1,
                AgentRole.RESEARCHER: 1,
                AgentRole.ENGINEER: 2,
                AgentRole.REVIEWER: 1,
                AgentRole.EXECUTOR: 2,
            }
        elif complexity < 0.7:
            # Medium task - standard swarm
            pass  # Use defaults
        else:
            # Complex task - large swarm
            base_config.min_agents_per_role = {
                AgentRole.COORDINATOR: 2,
                AgentRole.RESEARCHER: 5,
                AgentRole.ANALYST: 3,
                AgentRole.ENGINEER: 10,
                AgentRole.REVIEWER: 3,
                AgentRole.EXECUTOR: 15,
                AgentRole.VALIDATOR: 3
            }
            base_config.max_agents = 150
            base_config.max_parallel_tasks = 30
        
        return base_config
    
    async def _initialize_swarm(self, swarm: Swarm):
        """Initialize swarm with agents"""
        swarm.state = SwarmState.INITIALIZING
        
        # Spawn agents for each role
        for role, min_count in swarm.config.min_agents_per_role.items():
            for i in range(min_count):
                agent_id = f"{role.value}_{i}_{swarm.swarm_id[:8]}"
                
                task = AgentTask(
                    task_id=str(uuid.uuid4()),
                    agent_id=agent_id,
                    role=role,
                    description=f"{role.value} for: {swarm.task_description}"
                )
                
                swarm.agents[agent_id] = task
        
        logger.info(f"Initialized swarm {swarm.swarm_id} with {len(swarm.agents)} agents")
        
        swarm.state = SwarmState.ACTIVE
    
    async def execute_swarm(self, swarm_id: str) -> Dict[str, Any]:
        """
        Execute swarm task with all agents
        
        Args:
            swarm_id: Swarm identifier
        
        Returns:
            Aggregated results from all agents
        """
        swarm = self.active_swarms.get(swarm_id)
        if not swarm:
            raise ValueError(f"Swarm {swarm_id} not found")
        
        try:
            swarm.state = SwarmState.COORDINATING
            
            # Phase 1: Research
            research_results = await self._execute_phase(
                swarm,
                [AgentRole.RESEARCHER, AgentRole.ANALYST]
            )
            
            swarm.state = SwarmState.EXECUTING
            
            # Phase 2: Engineering
            engineering_results = await self._execute_phase(
                swarm,
                [AgentRole.ENGINEER, AgentRole.EXECUTOR],
                context=research_results
            )
            
            swarm.state = SwarmState.REVIEWING
            
            # Phase 3: Review & Validation
            review_results = await self._execute_phase(
                swarm,
                [AgentRole.REVIEWER, AgentRole.VALIDATOR],
                context={**research_results, **engineering_results}
            )
            
            # Synthesize results
            final_results = await self._synthesize_results(
                swarm,
                research_results,
                engineering_results,
                review_results
            )
            
            swarm.state = SwarmState.COMPLETED
            swarm.completed_at = datetime.utcnow()
            swarm.results = final_results
            
            logger.info(f"Swarm {swarm_id} completed successfully")
            
            return final_results
        
        except Exception as e:
            logger.error(f"Swarm {swarm_id} failed: {e}")
            swarm.state = SwarmState.FAILED
            raise
    
    async def _execute_phase(
        self,
        swarm: Swarm,
        roles: List[AgentRole],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a phase with specific agent roles"""
        # Get agents for this phase
        phase_agents = [
            agent for agent in swarm.agents.values()
            if agent.role in roles
        ]
        
        logger.info(f"Executing phase with {len(phase_agents)} agents: {roles}")
        
        # Execute agents in parallel (with concurrency limit)
        semaphore = asyncio.Semaphore(swarm.config.max_parallel_tasks)
        
        async def execute_agent_with_limit(agent: AgentTask):
            async with semaphore:
                return await self._execute_agent(agent, context)
        
        # Execute all agents
        results = await asyncio.gather(
            *[execute_agent_with_limit(agent) for agent in phase_agents],
            return_exceptions=True
        )
        
        # Aggregate results
        phase_results = {}
        for agent, result in zip(phase_agents, results):
            if isinstance(result, Exception):
                logger.error(f"Agent {agent.agent_id} failed: {result}")
                agent.status = "failed"
                agent.error = str(result)
            else:
                agent.status = "completed"
                agent.result = result
                phase_results[agent.agent_id] = result
        
        return phase_results
    
    async def _execute_agent(
        self,
        agent: AgentTask,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute a single agent task"""
        agent.started_at = datetime.utcnow()
        agent.status = "running"
        
        try:
            # Simulate agent execution (would be actual LLM call in production)
            await asyncio.sleep(0.1)  # Simulate work
            
            result = {
                "agent_id": agent.agent_id,
                "role": agent.role.value,
                "output": f"Result from {agent.role.value}",
                "confidence": 0.85,
                "context_used": bool(context)
            }
            
            agent.completed_at = datetime.utcnow()
            
            return result
        
        except Exception as e:
            logger.error(f"Agent {agent.agent_id} execution failed: {e}")
            raise
    
    async def _synthesize_results(
        self,
        swarm: Swarm,
        research_results: Dict[str, Any],
        engineering_results: Dict[str, Any],
        review_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize results from all phases"""
        # Aggregate insights from all agents
        all_results = {
            "research": research_results,
            "engineering": engineering_results,
            "review": review_results
        }
        
        # Calculate metrics
        total_agents = len(swarm.agents)
        successful_agents = sum(1 for a in swarm.agents.values() if a.status == "completed")
        
        execution_time = (
            (swarm.completed_at or datetime.utcnow()) - swarm.created_at
        ).total_seconds()
        
        synthesis = {
            "swarm_id": swarm.swarm_id,
            "task": swarm.task_description,
            "results": all_results,
            "metrics": {
                "total_agents": total_agents,
                "successful_agents": successful_agents,
                "success_rate": successful_agents / total_agents if total_agents > 0 else 0,
                "execution_time_seconds": execution_time,
                "agents_per_second": total_agents / execution_time if execution_time > 0 else 0
            },
            "summary": f"Swarm of {total_agents} agents completed task in {execution_time:.1f}s"
        }
        
        return synthesis
    
    async def spawn_team(
        self,
        role: str,
        count: int,
        swarm_id: Optional[str] = None
    ) -> List[AgentTask]:
        """Spawn a team of agents with specific role"""
        team = []
        
        for i in range(count):
            agent_id = f"{role}_{i}_{uuid.uuid4().hex[:8]}"
            
            task = AgentTask(
                task_id=str(uuid.uuid4()),
                agent_id=agent_id,
                role=AgentRole(role) if role in [r.value for r in AgentRole] else AgentRole.EXECUTOR,
                description=f"{role} agent {i}"
            )
            
            team.append(task)
        
        logger.info(f"Spawned team of {count} {role} agents")
        
        return team
    
    def get_swarm_status(self, swarm_id: str) -> Dict[str, Any]:
        """Get current status of a swarm"""
        swarm = self.active_swarms.get(swarm_id)
        if not swarm:
            return {"error": "Swarm not found"}
        
        return {
            "swarm_id": swarm.swarm_id,
            "state": swarm.state.value,
            "total_agents": len(swarm.agents),
            "completed_agents": sum(1 for a in swarm.agents.values() if a.status == "completed"),
            "failed_agents": sum(1 for a in swarm.agents.values() if a.status == "failed"),
            "created_at": swarm.created_at.isoformat(),
            "completed_at": swarm.completed_at.isoformat() if swarm.completed_at else None
        }


# Global swarm manager
_swarm_manager: Optional[AgentSwarm] = None


def get_swarm_manager() -> AgentSwarm:
    """Get or create global swarm manager"""
    global _swarm_manager
    
    if _swarm_manager is None:
        _swarm_manager = AgentSwarm()
    
    return _swarm_manager


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_swarm():
        manager = get_swarm_manager()
        
        # Spawn swarm for complex task
        swarm = await manager.spawn_swarm(
            task_description="Analyze and refactor entire codebase architecture",
            task_complexity=0.9
        )
        
        print(f"Swarm spawned: {swarm.swarm_id}")
        print(f"Agents: {len(swarm.agents)}")
        
        # Execute swarm
        results = await manager.execute_swarm(swarm.swarm_id)
        
        print(f"\nResults:")
        print(f"Summary: {results['summary']}")
        print(f"Success rate: {results['metrics']['success_rate']:.1%}")
        print(f"Execution time: {results['metrics']['execution_time_seconds']:.1f}s")
    
    asyncio.run(test_swarm())

