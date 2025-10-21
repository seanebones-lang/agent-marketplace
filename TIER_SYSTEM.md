# Agent Marketplace - Model Tier System

## Overview

The Agent Marketplace supports **5 distinct model tiers** powered by Anthropic's Claude AI models, ranging from fast and economical to maximum intelligence. Each tier is optimized for different use cases and budgets.

## Available Tiers

### 1. BYOK (Bring Your Own Key) 🔑

**Model:** User-provided Anthropic API key  
**Cost:** $0.00 (you pay Anthropic directly)  
**Best For:** Enterprise customers, high-volume users, custom billing requirements

#### Benefits:
- ✅ Zero marketplace markup
- ✅ Direct billing with Anthropic
- ✅ Full control over API usage
- ✅ Access to all Claude models
- ✅ No token limits from marketplace

#### How to Use:
1. Get your API key from https://console.anthropic.com/
2. Include it in the `X-Custom-API-Key` header
3. Specify `tier: "byok"` in your request
4. You'll be billed directly by Anthropic

#### Security:
- Your API key is **never stored**
- Transmitted securely via HTTPS
- Used only for request duration

---

### 2. BASIC (Haiku 3.5) ⚡

**Model:** `claude-3-5-haiku-20241022`  
**Input:** $0.80 per 1M tokens  
**Output:** $4.00 per 1M tokens  
**Base Cost:** $0.01 per execution  
**Markup:** 20%

#### Best For:
- Simple data processing
- Basic ticket classification
- Quick responses
- High-volume low-complexity tasks

#### Capabilities:
- 200K context window
- 4K max output tokens
- Fastest response time
- Most economical option

---

### 3. STANDARD (Sonnet 4) 🎯

**Model:** `claude-sonnet-4-20250514`  
**Input:** $3.00 per 1M tokens  
**Output:** $15.00 per 1M tokens  
**Base Cost:** $0.05 per execution  
**Markup:** 20%

#### Best For:
- General purpose agents
- Incident response
- Knowledge base queries
- Standard workflows

#### Capabilities:
- 200K context window
- 8K max output tokens
- Balanced performance
- **Recommended default tier**

---

### 4. PREMIUM (Sonnet 4.5) 🚀

**Model:** `claude-sonnet-4.5-20250514`  
**Input:** $3.00 per 1M tokens (≤200K)  
**Output:** $15.00 per 1M tokens (≤200K)  
**Base Cost:** $0.08 per execution  
**Markup:** 20%

#### Best For:
- Advanced agent orchestration
- Complex code generation
- Multi-step reasoning
- Security analysis

#### Capabilities:
- 200K context window
- 8K max output tokens
- Optimized for agents
- Best for coding tasks

---

### 5. ELITE (Opus 4.1) 💎

**Model:** `claude-opus-4.1-20250514`  
**Input:** $15.00 per 1M tokens  
**Output:** $75.00 per 1M tokens  
**Base Cost:** $0.25 per execution  
**Markup:** 20%

#### Best For:
- Complex problem solving
- Advanced security audits
- Creative content generation
- Mission-critical decisions

#### Capabilities:
- 200K context window
- 8K max output tokens
- Maximum intelligence
- Highest quality output

---

## Cost Comparison

### Example: 1,000 input tokens + 500 output tokens

| Tier | Model | Cost per Execution | Monthly (1000 exec) |
|------|-------|-------------------|---------------------|
| BYOK | User Key | $0.00* | $0.00* |
| BASIC | Haiku 3.5 | $0.013 | $13.00 |
| STANDARD | Sonnet 4 | $0.059 | $59.00 |
| PREMIUM | Sonnet 4.5 | $0.089 | $89.00 |
| ELITE | Opus 4.1 | $0.295 | $295.00 |

*BYOK: You pay Anthropic directly at their standard rates

---

## API Usage

### Estimate Cost

```bash
curl -X POST "https://api.agentic.bizbot.store/api/v1/tiers/estimate" \
  -H "Content-Type: application/json" \
  -d '{
    "tier": "standard",
    "input_tokens": 1000,
    "output_tokens": 500
  }'
```

### List All Tiers

```bash
curl "https://api.agentic.bizbot.store/api/v1/tiers/"
```

### Get Tier Details

```bash
curl "https://api.agentic.bizbot.store/api/v1/tiers/standard"
```

### Compare Tiers

```bash
curl "https://api.agentic.bizbot.store/api/v1/tiers/compare?input_tokens=1000&output_tokens=500"
```

### Execute with Specific Tier

```bash
curl -X POST "https://api.agentic.bizbot.store/api/v1/agents/execute" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "agent_id": "security-scanner",
    "task": "Scan https://example.com for vulnerabilities",
    "tier": "premium"
  }'
```

### Execute with BYOK

```bash
curl -X POST "https://api.agentic.bizbot.store/api/v1/agents/execute" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Custom-API-Key: YOUR_ANTHROPIC_KEY" \
  -d '{
    "agent_id": "security-scanner",
    "task": "Scan https://example.com for vulnerabilities",
    "tier": "byok"
  }'
```

---

## Tier Selection Guide

### Choose BYOK if:
- You have an existing Anthropic contract
- You need enterprise-level control
- You want to avoid marketplace markup
- You have high-volume usage

### Choose BASIC if:
- You need fast, simple responses
- Cost is the primary concern
- Tasks are straightforward
- High volume, low complexity

### Choose STANDARD if:
- You need balanced performance
- General purpose workloads
- Most common use case
- **Default recommendation**

### Choose PREMIUM if:
- Building complex agents
- Code generation tasks
- Multi-step reasoning
- Advanced orchestration

### Choose ELITE if:
- Mission-critical tasks
- Maximum intelligence needed
- Complex problem solving
- Creative/strategic work

---

## Pricing Details

### Base Costs
Each execution includes a base cost plus token usage:
- **BYOK:** $0.00 base (you pay Anthropic)
- **BASIC:** $0.01 base + tokens
- **STANDARD:** $0.05 base + tokens
- **PREMIUM:** $0.08 base + tokens
- **ELITE:** $0.25 base + tokens

### Markup
All paid tiers include a 20% marketplace markup on token costs to cover:
- Infrastructure and hosting
- API management and rate limiting
- Monitoring and logging
- Support and maintenance
- Security and compliance

### BYOK Advantage
With BYOK, you pay $0 to the marketplace and only pay Anthropic's standard rates directly.

---

## Token Estimation

### Average Token Counts

| Task Type | Input Tokens | Output Tokens |
|-----------|--------------|---------------|
| Simple query | 100-500 | 200-500 |
| Ticket resolution | 500-1500 | 500-1000 |
| Security scan | 1000-3000 | 1000-2000 |
| Code generation | 1000-5000 | 2000-4000 |
| Complex analysis | 3000-10000 | 3000-8000 |

### Token Calculation
- **Input tokens:** Your prompt + context + system instructions
- **Output tokens:** Agent's response
- **1 token ≈ 0.75 words** (English)

---

## Best Practices

1. **Start with STANDARD** - It's the best balance for most workloads
2. **Use BASIC for bulk operations** - Simple, repetitive tasks
3. **Reserve ELITE for critical tasks** - When quality matters most
4. **Consider BYOK for enterprise** - If you have high volume
5. **Monitor your usage** - Use analytics to optimize tier selection

---

## Support

For questions about tier selection or pricing:
- 📧 Email: support@bizbot.store
- 📞 Phone: (817) 675-9898
- 🌐 Web: https://bizbot.store

---

**Last Updated:** October 21, 2025  
**Pricing Source:** Anthropic Official Pricing (https://www.anthropic.com/pricing)

