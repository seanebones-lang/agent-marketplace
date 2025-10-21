"""
Cost Optimization Engine for LLM Model Selection
Dynamically selects optimal models based on task complexity and budget
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ModelProvider(str, Enum):
    """LLM model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    OLLAMA = "ollama"


@dataclass
class ModelPricing:
    """Model pricing information (per 1M tokens)"""
    provider: ModelProvider
    model_id: str
    input_cost: float  # Cost per 1M input tokens
    output_cost: float  # Cost per 1M output tokens
    context_window: int
    speed_score: float  # 0-10, higher is faster
    quality_score: float  # 0-10, higher is better
    supports_streaming: bool = True
    supports_function_calling: bool = True


class ModelRegistry:
    """Registry of available models with pricing"""
    
    MODELS = {
        # OpenAI Models
        "gpt-4o": ModelPricing(
            provider=ModelProvider.OPENAI,
            model_id="gpt-4o",
            input_cost=2.50,
            output_cost=10.00,
            context_window=128000,
            speed_score=8.0,
            quality_score=9.5
        ),
        "gpt-4o-mini": ModelPricing(
            provider=ModelProvider.OPENAI,
            model_id="gpt-4o-mini",
            input_cost=0.15,
            output_cost=0.60,
            context_window=128000,
            speed_score=9.0,
            quality_score=8.5
        ),
        "gpt-4-turbo": ModelPricing(
            provider=ModelProvider.OPENAI,
            model_id="gpt-4-turbo",
            input_cost=10.00,
            output_cost=30.00,
            context_window=128000,
            speed_score=7.0,
            quality_score=9.8
        ),
        
        # Anthropic Models
        "claude-3-5-sonnet": ModelPricing(
            provider=ModelProvider.ANTHROPIC,
            model_id="claude-3-5-sonnet-20241022",
            input_cost=3.00,
            output_cost=15.00,
            context_window=200000,
            speed_score=8.5,
            quality_score=9.8
        ),
        "claude-3-5-haiku": ModelPricing(
            provider=ModelProvider.ANTHROPIC,
            model_id="claude-3-5-haiku-20241022",
            input_cost=0.80,
            output_cost=4.00,
            context_window=200000,
            speed_score=9.5,
            quality_score=8.8
        ),
        "claude-3-opus": ModelPricing(
            provider=ModelProvider.ANTHROPIC,
            model_id="claude-3-opus-20240229",
            input_cost=15.00,
            output_cost=75.00,
            context_window=200000,
            speed_score=6.0,
            quality_score=10.0
        ),
        
        # Groq Models (Fast inference)
        "groq-llama-3.3-70b": ModelPricing(
            provider=ModelProvider.GROQ,
            model_id="llama-3.3-70b-versatile",
            input_cost=0.59,
            output_cost=0.79,
            context_window=128000,
            speed_score=10.0,
            quality_score=8.5
        ),
        "groq-mixtral-8x7b": ModelPricing(
            provider=ModelProvider.GROQ,
            model_id="mixtral-8x7b-32768",
            input_cost=0.24,
            output_cost=0.24,
            context_window=32768,
            speed_score=10.0,
            quality_score=7.5
        ),
        
        # Ollama (Self-hosted, free)
        "ollama-llama3": ModelPricing(
            provider=ModelProvider.OLLAMA,
            model_id="llama3:latest",
            input_cost=0.0,
            output_cost=0.0,
            context_window=8192,
            speed_score=6.0,
            quality_score=7.0
        ),
    }
    
    @classmethod
    def get_model(cls, model_id: str) -> Optional[ModelPricing]:
        """Get model pricing information"""
        return cls.MODELS.get(model_id)
    
    @classmethod
    def list_models(
        cls,
        provider: Optional[ModelProvider] = None,
        max_cost: Optional[float] = None
    ) -> List[ModelPricing]:
        """List available models with optional filtering"""
        models = list(cls.MODELS.values())
        
        if provider:
            models = [m for m in models if m.provider == provider]
        
        if max_cost:
            models = [m for m in models if m.input_cost <= max_cost]
        
        return models


class TaskComplexity(str, Enum):
    """Task complexity levels"""
    TRIVIAL = "trivial"  # Simple Q&A, classification
    SIMPLE = "simple"  # Basic reasoning, short generation
    MODERATE = "moderate"  # Multi-step reasoning, medium generation
    COMPLEX = "complex"  # Advanced reasoning, long generation
    EXPERT = "expert"  # Expert-level analysis, critical tasks


class CostOptimizer:
    """
    Intelligent model selection based on task requirements and budget
    """
    
    def __init__(self):
        self.registry = ModelRegistry()
        self.usage_stats: Dict[str, Dict[str, Any]] = {}
    
    def estimate_complexity(
        self,
        task_description: str,
        input_tokens: int,
        output_tokens: int,
        requires_reasoning: bool = False,
        requires_accuracy: bool = False
    ) -> TaskComplexity:
        """
        Estimate task complexity based on various factors
        
        Args:
            task_description: Description of the task
            input_tokens: Estimated input token count
            output_tokens: Estimated output token count
            requires_reasoning: Whether task requires multi-step reasoning
            requires_accuracy: Whether high accuracy is critical
        
        Returns:
            TaskComplexity level
        """
        complexity_score = 0.0
        
        # Token-based scoring
        if input_tokens > 10000 or output_tokens > 2000:
            complexity_score += 2.0
        elif input_tokens > 5000 or output_tokens > 1000:
            complexity_score += 1.0
        
        # Reasoning requirement
        if requires_reasoning:
            complexity_score += 2.0
        
        # Accuracy requirement
        if requires_accuracy:
            complexity_score += 1.5
        
        # Keyword-based scoring
        complex_keywords = [
            "analyze", "evaluate", "compare", "synthesize", "critique",
            "design", "architect", "optimize", "debug", "refactor"
        ]
        
        task_lower = task_description.lower()
        keyword_matches = sum(1 for kw in complex_keywords if kw in task_lower)
        complexity_score += keyword_matches * 0.5
        
        # Map score to complexity level
        if complexity_score >= 5.0:
            return TaskComplexity.EXPERT
        elif complexity_score >= 3.5:
            return TaskComplexity.COMPLEX
        elif complexity_score >= 2.0:
            return TaskComplexity.MODERATE
        elif complexity_score >= 0.5:
            return TaskComplexity.SIMPLE
        else:
            return TaskComplexity.TRIVIAL
    
    def select_optimal_model(
        self,
        complexity: TaskComplexity,
        budget: Optional[float] = None,
        max_latency_ms: Optional[int] = None,
        min_quality_score: float = 7.0,
        preferred_provider: Optional[ModelProvider] = None
    ) -> Tuple[str, ModelPricing, Dict[str, Any]]:
        """
        Select the optimal model based on requirements
        
        Args:
            complexity: Task complexity level
            budget: Maximum budget per task (USD)
            max_latency_ms: Maximum acceptable latency
            min_quality_score: Minimum quality score required
            preferred_provider: Preferred model provider
        
        Returns:
            Tuple of (model_id, model_pricing, selection_metadata)
        """
        # Define model preferences by complexity
        complexity_preferences = {
            TaskComplexity.TRIVIAL: ["gpt-4o-mini", "groq-mixtral-8x7b", "ollama-llama3"],
            TaskComplexity.SIMPLE: ["gpt-4o-mini", "claude-3-5-haiku", "groq-llama-3.3-70b"],
            TaskComplexity.MODERATE: ["gpt-4o", "claude-3-5-haiku", "groq-llama-3.3-70b"],
            TaskComplexity.COMPLEX: ["claude-3-5-sonnet", "gpt-4o", "gpt-4-turbo"],
            TaskComplexity.EXPERT: ["claude-3-opus", "gpt-4-turbo", "claude-3-5-sonnet"]
        }
        
        # Get candidate models
        candidates = complexity_preferences.get(complexity, ["gpt-4o-mini"])
        
        # Filter by constraints
        viable_models = []
        for model_id in candidates:
            model = self.registry.get_model(model_id)
            if not model:
                continue
            
            # Check quality requirement
            if model.quality_score < min_quality_score:
                continue
            
            # Check provider preference
            if preferred_provider and model.provider != preferred_provider:
                continue
            
            # Estimate cost (assuming 1000 input, 500 output tokens as baseline)
            estimated_cost = self._estimate_cost(model, 1000, 500)
            
            # Check budget constraint
            if budget and estimated_cost > budget:
                continue
            
            # Check latency constraint (approximate based on speed score)
            if max_latency_ms:
                estimated_latency = self._estimate_latency(model, 1000, 500)
                if estimated_latency > max_latency_ms:
                    continue
            
            viable_models.append((model_id, model, estimated_cost))
        
        # If no viable models, fall back to cheapest option
        if not viable_models:
            logger.warning(
                f"No models meet constraints for {complexity}, falling back to gpt-4o-mini"
            )
            model_id = "gpt-4o-mini"
            model = self.registry.get_model(model_id)
            estimated_cost = self._estimate_cost(model, 1000, 500)
            viable_models = [(model_id, model, estimated_cost)]
        
        # Select best model based on cost-performance ratio
        best_model = self._select_best_model(viable_models)
        model_id, model, estimated_cost = best_model
        
        metadata = {
            "complexity": complexity.value,
            "estimated_cost": estimated_cost,
            "quality_score": model.quality_score,
            "speed_score": model.speed_score,
            "provider": model.provider.value,
            "selection_reason": self._get_selection_reason(complexity, model)
        }
        
        logger.info(
            f"Selected model: {model_id} for {complexity} task",
            extra=metadata
        )
        
        return model_id, model, metadata
    
    def _estimate_cost(
        self,
        model: ModelPricing,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Estimate cost for a model given token counts"""
        input_cost = (input_tokens / 1_000_000) * model.input_cost
        output_cost = (output_tokens / 1_000_000) * model.output_cost
        return input_cost + output_cost
    
    def _estimate_latency(
        self,
        model: ModelPricing,
        input_tokens: int,
        output_tokens: int
    ) -> int:
        """Estimate latency in milliseconds"""
        # Rough approximation: higher speed score = lower latency
        base_latency = 5000  # 5 seconds baseline
        speed_factor = model.speed_score / 10.0
        token_factor = (input_tokens + output_tokens) / 1000.0
        
        estimated_latency = (base_latency / speed_factor) * token_factor
        return int(estimated_latency)
    
    def _select_best_model(
        self,
        viable_models: List[Tuple[str, ModelPricing, float]]
    ) -> Tuple[str, ModelPricing, float]:
        """Select best model from viable options"""
        # Calculate score: (quality * speed) / cost
        def score_model(model_tuple):
            model_id, model, cost = model_tuple
            if cost == 0:
                cost = 0.01  # Avoid division by zero for free models
            return (model.quality_score * model.speed_score) / cost
        
        return max(viable_models, key=score_model)
    
    def _get_selection_reason(
        self,
        complexity: TaskComplexity,
        model: ModelPricing
    ) -> str:
        """Generate human-readable selection reason"""
        reasons = []
        
        if complexity in [TaskComplexity.EXPERT, TaskComplexity.COMPLEX]:
            reasons.append("high-quality model for complex task")
        elif complexity == TaskComplexity.TRIVIAL:
            reasons.append("cost-effective model for simple task")
        
        if model.speed_score >= 9.0:
            reasons.append("fast inference")
        
        if model.input_cost < 1.0:
            reasons.append("low cost")
        
        return ", ".join(reasons) if reasons else "best available option"
    
    def track_usage(
        self,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int,
        success: bool
    ):
        """Track model usage for optimization"""
        if model_id not in self.usage_stats:
            self.usage_stats[model_id] = {
                "total_requests": 0,
                "successful_requests": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_latency_ms": 0,
                "total_cost": 0.0
            }
        
        stats = self.usage_stats[model_id]
        stats["total_requests"] += 1
        if success:
            stats["successful_requests"] += 1
        stats["total_input_tokens"] += input_tokens
        stats["total_output_tokens"] += output_tokens
        stats["total_latency_ms"] += latency_ms
        
        # Calculate cost
        model = self.registry.get_model(model_id)
        if model:
            cost = self._estimate_cost(model, input_tokens, output_tokens)
            stats["total_cost"] += cost
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Generate usage report with recommendations"""
        report = {
            "models": {},
            "total_cost": 0.0,
            "total_requests": 0,
            "recommendations": []
        }
        
        for model_id, stats in self.usage_stats.items():
            avg_latency = stats["total_latency_ms"] / max(stats["total_requests"], 1)
            success_rate = stats["successful_requests"] / max(stats["total_requests"], 1)
            
            report["models"][model_id] = {
                **stats,
                "avg_latency_ms": avg_latency,
                "success_rate": success_rate
            }
            
            report["total_cost"] += stats["total_cost"]
            report["total_requests"] += stats["total_requests"]
        
        # Generate recommendations
        if report["total_cost"] > 100:
            report["recommendations"].append(
                "Consider using more cost-effective models for simple tasks"
            )
        
        return report


# Example usage
if __name__ == "__main__":
    optimizer = CostOptimizer()
    
    # Example 1: Simple task with budget constraint
    complexity = optimizer.estimate_complexity(
        task_description="Classify customer support ticket",
        input_tokens=500,
        output_tokens=50,
        requires_reasoning=False,
        requires_accuracy=True
    )
    
    model_id, model, metadata = optimizer.select_optimal_model(
        complexity=complexity,
        budget=0.01,
        max_latency_ms=2000
    )
    
    print(f"Selected: {model_id}")
    print(f"Metadata: {metadata}")
    
    # Example 2: Complex task requiring high quality
    complexity = optimizer.estimate_complexity(
        task_description="Analyze and refactor complex codebase architecture",
        input_tokens=15000,
        output_tokens=3000,
        requires_reasoning=True,
        requires_accuracy=True
    )
    
    model_id, model, metadata = optimizer.select_optimal_model(
        complexity=complexity,
        min_quality_score=9.0
    )
    
    print(f"\nSelected: {model_id}")
    print(f"Metadata: {metadata}")
    
    # Track usage
    optimizer.track_usage(model_id, 15000, 3000, 8500, True)
    
    # Get report
    report = optimizer.get_usage_report()
    print(f"\nUsage Report: {report}")

