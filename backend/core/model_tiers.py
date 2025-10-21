"""
Model Tier Configuration for Agent Marketplace
Supports Claude models with automatic cost optimization
"""
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ModelTier(str, Enum):
    """Available model tiers for agent execution"""
    SOLO = "solo"  # Haiku 3.5 - Minimal features, lowest cost
    BASIC = "basic"  # Haiku 3.5 - Fast & Economical
    SILVER = "silver"  # Sonnet 4 - Enhanced features
    STANDARD = "standard"  # Sonnet 4 - Balanced Performance
    PREMIUM = "premium"  # Sonnet 4.5 - Advanced Agents
    ELITE = "elite"  # Opus 4.1 - Maximum Intelligence
    BYOK = "byok"  # Bring Your Own Key


class ModelConfig(BaseModel):
    """Configuration for a specific model"""
    name: str = Field(..., description="Model identifier")
    display_name: str = Field(..., description="Human-readable name")
    model_id: str = Field(..., description="Anthropic model ID")
    input_cost_per_1m: float = Field(..., description="Cost per 1M input tokens in USD")
    output_cost_per_1m: float = Field(..., description="Cost per 1M output tokens in USD")
    max_tokens: int = Field(default=4096, description="Maximum output tokens")
    context_window: int = Field(default=200000, description="Maximum context window")
    description: str = Field(..., description="Model capabilities description")
    recommended_for: list[str] = Field(default_factory=list, description="Recommended use cases")


# Model tier configurations based on latest Anthropic pricing (Oct 2025)
MODEL_CONFIGS: Dict[ModelTier, ModelConfig] = {
    ModelTier.SOLO: ModelConfig(
        name="solo",
        display_name="Solo (Haiku 3.5)",
        model_id="claude-3-5-haiku-20241022",
        input_cost_per_1m=0.80,
        output_cost_per_1m=4.00,
        max_tokens=2048,  # Limited output
        context_window=100000,  # Limited context
        description="Entry-level tier with minimal features for individual users and testing",
        recommended_for=[
            "Individual developers",
            "Testing and prototyping",
            "Learning and experimentation",
            "Very simple tasks"
        ]
    ),
    ModelTier.BASIC: ModelConfig(
        name="basic",
        display_name="Basic (Haiku 3.5)",
        model_id="claude-3-5-haiku-20241022",
        input_cost_per_1m=0.80,
        output_cost_per_1m=4.00,
        max_tokens=4096,
        context_window=200000,
        description="Fastest and most cost-effective model for simple tasks",
        recommended_for=[
            "Simple data processing",
            "Basic ticket classification",
            "Quick responses",
            "High-volume low-complexity tasks"
        ]
    ),
    ModelTier.SILVER: ModelConfig(
        name="silver",
        display_name="Silver (Sonnet 4)",
        model_id="claude-sonnet-4-20250514",
        input_cost_per_1m=3.00,
        output_cost_per_1m=15.00,
        max_tokens=6144,
        context_window=200000,
        description="Enhanced performance with priority support and advanced features",
        recommended_for=[
            "Growing teams",
            "Regular agent usage",
            "Enhanced support needs",
            "Moderate complexity tasks"
        ]
    ),
    ModelTier.STANDARD: ModelConfig(
        name="standard",
        display_name="Standard (Sonnet 4)",
        model_id="claude-sonnet-4-20250514",
        input_cost_per_1m=3.00,
        output_cost_per_1m=15.00,
        max_tokens=8192,
        context_window=200000,
        description="Balanced performance for most enterprise tasks",
        recommended_for=[
            "General purpose agents",
            "Incident response",
            "Knowledge base queries",
            "Standard workflows"
        ]
    ),
    ModelTier.PREMIUM: ModelConfig(
        name="premium",
        display_name="Premium (Sonnet 4.5)",
        model_id="claude-sonnet-4.5-20250514",
        input_cost_per_1m=3.00,  # ≤200K tokens
        output_cost_per_1m=15.00,
        max_tokens=8192,
        context_window=200000,
        description="Optimized for building agents and complex coding tasks",
        recommended_for=[
            "Advanced agent orchestration",
            "Complex code generation",
            "Multi-step reasoning",
            "Security analysis"
        ]
    ),
    ModelTier.ELITE: ModelConfig(
        name="elite",
        display_name="Elite (Opus 4.1)",
        model_id="claude-opus-4.1-20250514",
        input_cost_per_1m=15.00,
        output_cost_per_1m=75.00,
        max_tokens=8192,
        context_window=200000,
        description="Maximum intelligence for complex and creative tasks",
        recommended_for=[
            "Complex problem solving",
            "Advanced security audits",
            "Creative content generation",
            "Mission-critical decisions"
        ]
    ),
    ModelTier.BYOK: ModelConfig(
        name="byok",
        display_name="Bring Your Own Key",
        model_id="user-provided",
        input_cost_per_1m=0.0,  # User pays directly to Anthropic
        output_cost_per_1m=0.0,
        max_tokens=8192,
        context_window=200000,
        description="Use your own Anthropic API key with minimal platform fee ($0.002/execution) - you pay Anthropic directly for tokens",
        recommended_for=["Enterprise customers", "High-volume users", "Custom billing requirements", "Cost-conscious power users"]
    )
}


class TierPricing(BaseModel):
    """Pricing configuration for marketplace tiers"""
    tier: ModelTier
    base_cost_per_execution: float = Field(..., description="Base cost per agent execution in USD")
    markup_percentage: float = Field(default=20.0, description="Marketplace markup percentage")
    included_tokens: int = Field(default=10000, description="Tokens included in base price")
    
    def calculate_execution_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate total cost for an execution"""
        if self.tier == ModelTier.BYOK:
            return 0.0  # User pays Anthropic directly
        
        config = MODEL_CONFIGS[self.tier]
        
        # Calculate token costs
        input_cost = (input_tokens / 1_000_000) * config.input_cost_per_1m
        output_cost = (output_tokens / 1_000_000) * config.output_cost_per_1m
        token_cost = input_cost + output_cost
        
        # Apply markup
        total_cost = token_cost * (1 + self.markup_percentage / 100)
        
        return round(total_cost, 4)


# Marketplace pricing tiers (5% below market rates for competitive advantage)
TIER_PRICING: Dict[ModelTier, TierPricing] = {
    ModelTier.SOLO: TierPricing(
        tier=ModelTier.SOLO,
        base_cost_per_execution=0.005,  # $0.005 per execution
        markup_percentage=14.0,  # 14% markup (5% below standard 20%)
        included_tokens=5000  # Limited tokens for solo tier
    ),
    ModelTier.BASIC: TierPricing(
        tier=ModelTier.BASIC,
        base_cost_per_execution=0.0095,  # $0.0095 (5% below $0.01)
        markup_percentage=14.0,  # 14% markup
        included_tokens=10000
    ),
    ModelTier.SILVER: TierPricing(
        tier=ModelTier.SILVER,
        base_cost_per_execution=0.038,  # $0.038 (5% below $0.04)
        markup_percentage=14.0,  # 14% markup
        included_tokens=15000
    ),
    ModelTier.STANDARD: TierPricing(
        tier=ModelTier.STANDARD,
        base_cost_per_execution=0.0475,  # $0.0475 (5% below $0.05)
        markup_percentage=14.0,  # 14% markup
        included_tokens=20000
    ),
    ModelTier.PREMIUM: TierPricing(
        tier=ModelTier.PREMIUM,
        base_cost_per_execution=0.076,  # $0.076 (5% below $0.08)
        markup_percentage=14.0,  # 14% markup
        included_tokens=25000
    ),
    ModelTier.ELITE: TierPricing(
        tier=ModelTier.ELITE,
        base_cost_per_execution=0.2375,  # $0.2375 (5% below $0.25)
        markup_percentage=14.0,  # 14% markup
        included_tokens=30000
    ),
    ModelTier.BYOK: TierPricing(
        tier=ModelTier.BYOK,
        base_cost_per_execution=0.002,  # $0.002 platform fee per execution
        markup_percentage=0.0,  # No markup on tokens (user pays Anthropic directly)
        included_tokens=0  # Unlimited based on user's Anthropic plan
    )
}


def get_model_for_tier(tier: ModelTier, custom_api_key: Optional[str] = None) -> tuple[str, Optional[str]]:
    """
    Get the appropriate model ID and API key for a given tier
    
    Args:
        tier: The model tier to use
        custom_api_key: Optional custom API key for BYOK tier
        
    Returns:
        Tuple of (model_id, api_key)
    """
    config = MODEL_CONFIGS[tier]
    
    if tier == ModelTier.BYOK:
        if not custom_api_key:
            raise ValueError("BYOK tier requires a custom API key")
        return config.model_id, custom_api_key
    
    return config.model_id, None  # Use system API key


def estimate_cost(
    tier: ModelTier,
    estimated_input_tokens: int,
    estimated_output_tokens: int
) -> Dict[str, Any]:
    """
    Estimate the cost for an agent execution
    
    Args:
        tier: Model tier to use
        estimated_input_tokens: Expected input tokens
        estimated_output_tokens: Expected output tokens
        
    Returns:
        Dictionary with cost breakdown
    """
    if tier == ModelTier.BYOK:
        pricing = TIER_PRICING[tier]
        config = MODEL_CONFIGS[ModelTier.STANDARD]  # Use standard for Anthropic cost estimation
        
        # Calculate what user will pay Anthropic directly
        anthropic_input_cost = (estimated_input_tokens / 1_000_000) * 3.00  # Anthropic's actual rate
        anthropic_output_cost = (estimated_output_tokens / 1_000_000) * 15.00  # Anthropic's actual rate
        anthropic_total = anthropic_input_cost + anthropic_output_cost
        
        # Platform fee
        platform_fee = pricing.base_cost_per_execution
        
        return {
            "tier": tier.value,
            "model": "user-provided",
            "platform_fee_usd": platform_fee,
            "anthropic_cost_estimate_usd": round(anthropic_total, 4),
            "total_cost_estimate_usd": round(platform_fee + anthropic_total, 4),
            "note": "Platform fee charged by us, token costs billed directly by Anthropic",
            "breakdown": {
                "platform_fee": platform_fee,
                "anthropic_tokens": round(anthropic_total, 4),
                "you_save_vs_standard": f"~{round((TIER_PRICING[ModelTier.STANDARD].calculate_execution_cost(estimated_input_tokens, estimated_output_tokens) - (platform_fee + anthropic_total)) / (platform_fee + anthropic_total) * 100, 1)}%"
            },
            "input_tokens": estimated_input_tokens,
            "output_tokens": estimated_output_tokens
        }
    
    pricing = TIER_PRICING[tier]
    config = MODEL_CONFIGS[tier]
    
    cost = pricing.calculate_execution_cost(estimated_input_tokens, estimated_output_tokens)
    
    return {
        "tier": tier.value,
        "model": config.display_name,
        "estimated_cost_usd": cost,
        "base_cost": pricing.base_cost_per_execution,
        "token_cost": cost - pricing.base_cost_per_execution,
        "markup_percentage": pricing.markup_percentage,
        "input_tokens": estimated_input_tokens,
        "output_tokens": estimated_output_tokens,
        "input_cost_per_1m": config.input_cost_per_1m,
        "output_cost_per_1m": config.output_cost_per_1m
    }


def get_tier_comparison() -> list[Dict[str, Any]]:
    """Get a comparison of all available tiers"""
    comparison = []
    
    for tier in ModelTier:
        config = MODEL_CONFIGS[tier]
        pricing = TIER_PRICING[tier]
        
        comparison.append({
            "tier": tier.value,
            "display_name": config.display_name,
            "model_id": config.model_id,
            "description": config.description,
            "recommended_for": config.recommended_for,
            "input_cost_per_1m": config.input_cost_per_1m,
            "output_cost_per_1m": config.output_cost_per_1m,
            "base_cost_per_execution": pricing.base_cost_per_execution,
            "context_window": config.context_window,
            "max_tokens": config.max_tokens
        })
    
    return comparison

