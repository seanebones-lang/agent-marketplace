"""
API endpoints for model tier information and pricing
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from backend.core.model_tiers import (
    ModelTier,
    get_tier_comparison,
    estimate_cost,
    MODEL_CONFIGS,
    TIER_PRICING
)

router = APIRouter(prefix="/tiers", tags=["Model Tiers"])


@router.get("/")
async def list_tiers():
    """
    Get a list of all available model tiers with pricing and capabilities
    
    Returns comprehensive information about each tier including:
    - Model specifications
    - Pricing per million tokens
    - Recommended use cases
    - Context window and token limits
    """
    return {
        "tiers": get_tier_comparison(),
        "note": "BYOK (Bring Your Own Key) tier allows you to use your own Anthropic API key"
    }


@router.get("/{tier}")
async def get_tier_details(tier: str):
    """
    Get detailed information about a specific tier
    
    Args:
        tier: Tier name (byok, basic, standard, premium, elite)
    """
    try:
        tier_enum = ModelTier(tier.lower())
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Tier '{tier}' not found. Available tiers: {[t.value for t in ModelTier]}"
        )
    
    config = MODEL_CONFIGS[tier_enum]
    pricing = TIER_PRICING[tier_enum]
    
    return {
        "tier": tier_enum.value,
        "display_name": config.display_name,
        "model_id": config.model_id,
        "description": config.description,
        "recommended_for": config.recommended_for,
        "pricing": {
            "input_cost_per_1m_tokens": config.input_cost_per_1m,
            "output_cost_per_1m_tokens": config.output_cost_per_1m,
            "base_cost_per_execution": pricing.base_cost_per_execution,
            "markup_percentage": pricing.markup_percentage,
            "included_tokens": pricing.included_tokens
        },
        "capabilities": {
            "context_window": config.context_window,
            "max_output_tokens": config.max_tokens
        },
        "notes": {
            "byok": "BYOK tier requires you to provide your own Anthropic API key" if tier_enum == ModelTier.BYOK else None
        }
    }


@router.post("/estimate")
async def estimate_execution_cost(
    tier: str = Query(..., description="Tier to estimate cost for"),
    input_tokens: int = Query(..., description="Expected input tokens", ge=1),
    output_tokens: int = Query(..., description="Expected output tokens", ge=1)
):
    """
    Estimate the cost of an agent execution for a given tier
    
    Args:
        tier: Model tier (byok, basic, standard, premium, elite)
        input_tokens: Expected number of input tokens
        output_tokens: Expected number of output tokens
        
    Returns:
        Detailed cost breakdown including base cost, token cost, and total
    """
    try:
        tier_enum = ModelTier(tier.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier '{tier}'. Available tiers: {[t.value for t in ModelTier]}"
        )
    
    return estimate_cost(tier_enum, input_tokens, output_tokens)


@router.get("/compare")
async def compare_tiers(
    input_tokens: int = Query(1000, description="Input tokens for comparison"),
    output_tokens: int = Query(500, description="Output tokens for comparison")
):
    """
    Compare costs across all tiers for a given token usage
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        Cost comparison across all tiers
    """
    comparison = []
    
    for tier in ModelTier:
        cost_estimate = estimate_cost(tier, input_tokens, output_tokens)
        comparison.append(cost_estimate)
    
    # Sort by cost (excluding BYOK which is $0)
    comparison.sort(key=lambda x: x.get("estimated_cost_usd", 0))
    
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tiers": comparison,
        "recommendation": "Use BASIC for simple tasks, STANDARD for most workloads, PREMIUM for complex agents, ELITE for mission-critical tasks"
    }


@router.get("/byok/info")
async def byok_information():
    """
    Get information about the Bring Your Own Key (BYOK) tier
    
    Returns detailed information about how BYOK works and its benefits
    """
    pricing = TIER_PRICING[ModelTier.BYOK]
    
    return {
        "tier": "byok",
        "display_name": "Bring Your Own Key",
        "description": "Use your own Anthropic API key with minimal platform fee - you pay Anthropic directly for tokens",
        "pricing": {
            "platform_fee_per_execution": pricing.base_cost_per_execution,
            "token_markup": "0% (you pay Anthropic directly)",
            "note": f"Only ${pricing.base_cost_per_execution} per execution to cover platform costs"
        },
        "benefits": [
            f"Minimal platform fee (${pricing.base_cost_per_execution}/execution) - among the lowest in the industry",
            "Zero markup on token costs - you pay Anthropic's standard rates directly",
            "Full control over your API usage and billing relationship",
            "Access to all Claude models based on your Anthropic plan",
            "Ideal for enterprise customers with existing Anthropic contracts",
            "No token limits imposed by the marketplace",
            "Significant savings at high volume (10K+ executions/month)"
        ],
        "what_platform_fee_covers": [
            "API gateway and request routing",
            "Security, authentication, and encryption",
            "Usage analytics and monitoring dashboard",
            "Webhook integrations and automations",
            "Team collaboration tools",
            "Priority support",
            "Audit logging and compliance",
            "Platform maintenance and updates"
        ],
        "requirements": [
            "Valid Anthropic API key",
            "Active Anthropic account with sufficient credits",
            "API key must have access to Claude models"
        ],
        "how_to_use": {
            "step_1": "Obtain an API key from https://console.anthropic.com/",
            "step_2": "Include your API key in the 'X-Custom-API-Key' header when making requests",
            "step_3": "Specify 'byok' as the tier in your agent execution request",
            "step_4": "You will be billed by us for platform fees ($0.002/execution) and by Anthropic for token usage"
        },
        "cost_example": {
            "scenario": "1,000 input + 500 output tokens (Sonnet 4)",
            "platform_fee": pricing.base_cost_per_execution,
            "anthropic_cost_estimate": 0.0105,
            "total_estimate": round(pricing.base_cost_per_execution + 0.0105, 4),
            "vs_standard_tier": {
                "standard_cost": 0.056,
                "byok_cost": round(pricing.base_cost_per_execution + 0.0105, 4),
                "savings_percent": "77.7%"
            }
        },
        "security": {
            "storage": "Your API key is NEVER stored by our system",
            "transmission": "Keys are transmitted securely via HTTPS/TLS 1.3",
            "usage": "Keys are only used for the duration of your agent execution",
            "compliance": "SOC 2 Type II, GDPR compliant, ISO 27001 certified"
        },
        "when_to_use": {
            "perfect_for": [
                "High-volume users (10K+ executions/month)",
                "Enterprise customers with existing Anthropic contracts",
                "Cost-conscious power users",
                "Users needing direct vendor relationships",
                "Multi-model experimentation"
            ],
            "not_ideal_for": [
                "Low-volume users (< 1K executions/month)",
                "Users preferring single billing",
                "Those without Anthropic accounts"
            ]
        },
        "pricing_reference": {
            "anthropic_rates": {
                "haiku_3_5": "$0.80/$4.00 per 1M tokens",
                "sonnet_4": "$3.00/$15.00 per 1M tokens",
                "sonnet_4_5": "$3.00/$15.00 per 1M tokens",
                "opus_4_1": "$15.00/$75.00 per 1M tokens"
            },
            "anthropic_pricing_url": "https://www.anthropic.com/pricing"
        }
    }

