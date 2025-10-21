# BYOK (Bring Your Own Key) Pricing Model

## Overview

The BYOK tier allows you to use your own Anthropic API key while accessing our full platform features. Unlike other tiers, you pay Anthropic directly for token usage, and we charge only a minimal platform fee.

---

## Pricing Structure

### Platform Fee: $0.002 per execution

This covers:
-  Platform infrastructure and hosting
-  API gateway and request routing
-  Security and authentication
-  Usage analytics and monitoring
-  Webhook integrations
-  Team collaboration tools
-  Priority support
-  Audit logging and compliance

### Token Costs: Paid directly to Anthropic

You pay Anthropic's standard rates:
- **Haiku 3.5:** $0.80/$4.00 per 1M tokens
- **Sonnet 4:** $3.00/$15.00 per 1M tokens  
- **Sonnet 4.5:** $3.00/$15.00 per 1M tokens
- **Opus 4.1:** $15.00/$75.00 per 1M tokens

---

## Cost Comparison

### Example: 1,000 input tokens + 500 output tokens (Sonnet 4)

**BYOK Tier:**
- Platform fee: $0.002
- Anthropic tokens: $0.0105 (paid directly to Anthropic)
- **Total: $0.0125**

**Standard Tier:**
- Platform execution: $0.056
- **Total: $0.056**

**You Save: 77.7%** with BYOK on this example!

---

## When BYOK Makes Sense

###  Perfect For:

1. **High-Volume Users**
   - 10,000+ executions/month
   - Savings scale dramatically with volume
   - Example: 10K executions = $20 platform fee + Anthropic costs vs $560 on Standard

2. **Enterprise Customers**
   - Existing Anthropic contracts
   - Need direct billing relationship
   - Custom rate agreements with Anthropic
   - Compliance requirements for direct vendor relationships

3. **Cost-Conscious Power Users**
   - Want maximum control over costs
   - Already have Anthropic API access
   - Prefer transparent, predictable pricing

4. **Multi-Model Users**
   - Want to use different Claude models
   - Need flexibility to switch models
   - Testing and optimization workflows

###  Not Ideal For:

1. **Low-Volume Users**
   - < 1,000 executions/month
   - Solo tier ($0.005/exec) may be cheaper
   - Overhead of managing API keys

2. **Users Without Anthropic Accounts**
   - Need to set up Anthropic account first
   - May prefer all-in-one billing

3. **Simplicity Seekers**
   - Want single bill
   - Prefer not to manage API keys

---

## Monthly Cost Examples

### Scenario 1: Light Usage (1,000 executions/month)
**Average: 1,000 input + 500 output tokens per execution**

| Tier | Cost | Breakdown |
|------|------|-----------|
| SOLO | $8.00 | All-inclusive |
| BASIC | $12.00 | All-inclusive |
| BYOK | **$12.50** | $2 platform + ~$10.50 Anthropic |
| STANDARD | $56.00 | All-inclusive |

**Winner:** SOLO (for light usage)

---

### Scenario 2: Medium Usage (5,000 executions/month)
**Average: 1,000 input + 500 output tokens per execution**

| Tier | Cost | Breakdown |
|------|------|-----------|
| BASIC | $60.00 | All-inclusive |
| BYOK | **$62.50** | $10 platform + ~$52.50 Anthropic |
| STANDARD | $280.00 | All-inclusive |

**Winner:** BASIC (slightly cheaper than BYOK)

---

### Scenario 3: High Usage (10,000 executions/month)
**Average: 1,000 input + 500 output tokens per execution**

| Tier | Cost | Breakdown |
|------|------|-----------|
| BASIC | $120.00 | All-inclusive |
| BYOK | **$125.00** | $20 platform + ~$105 Anthropic |
| STANDARD | $560.00 | All-inclusive |

**Winner:** BASIC (still competitive)

---

### Scenario 4: Enterprise Usage (50,000 executions/month)
**Average: 1,000 input + 500 output tokens per execution**

| Tier | Cost | Breakdown |
|------|------|-----------|
| BASIC | $600.00 | All-inclusive |
| BYOK | **$625.00** | $100 platform + ~$525 Anthropic |
| STANDARD | $2,800.00 | All-inclusive |
| PREMIUM | $4,480.00 | All-inclusive |

**Winner:** BASIC (best value), BYOK close second

---

### Scenario 5: Massive Scale (100,000 executions/month)
**Average: 1,000 input + 500 output tokens per execution**

| Tier | Cost | Breakdown |
|------|------|-----------|
| BASIC | $1,200.00 | All-inclusive |
| BYOK | **$1,250.00** | $200 platform + ~$1,050 Anthropic |
| STANDARD | $5,600.00 | All-inclusive |

**Winner:** BASIC (most economical at scale)

---

## Why We Charge a Platform Fee

### Industry Standard

Most BYOK platforms charge between $5-$20/month subscription OR $0.001-$0.005 per request:

- **Writingmate.ai:** $6.99/month for BYOK
- **Command.ai:** $0.003-$0.005 per request
- **Retool:** $10/month + usage fees
- **Our Model:** $0.002 per execution (competitive!)

### What You Get

Your $0.002/execution covers:

1. **Infrastructure** ($0.0005)
   - API gateway
   - Load balancing
   - CDN and caching
   - Database operations

2. **Security** ($0.0003)
   - Authentication/authorization
   - Encryption
   - Rate limiting
   - DDoS protection

3. **Features** ($0.0007)
   - Analytics dashboard
   - Webhook integrations
   - Team collaboration
   - Audit logging

4. **Support** ($0.0005)
   - Priority email support
   - Documentation
   - API updates
   - Bug fixes

---

## BYOK + Monthly Subscription Option

For even better value, combine BYOK with a monthly subscription:

### BYOK Pro: $19/month + $0.001/execution

- **50% lower execution fee** ($0.001 vs $0.002)
- Unlimited team members
- White-label options
- Dedicated support
- Custom integrations
- SLA guarantees

**Break-even:** 19,000 executions/month  
**Savings at 50K executions:** $50/month  
**Savings at 100K executions:** $100/month

---

## How to Get Started with BYOK

### Step 1: Get Your Anthropic API Key
1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Generate a new key
5. Add credits to your account

### Step 2: Configure in Our Platform
1. Go to Settings > API Keys
2. Select "BYOK" tier
3. Enter your Anthropic API key
4. Test connection
5. Start using agents!

### Step 3: Monitor Usage
- View real-time usage in dashboard
- Track costs in both platforms
- Set billing alerts
- Export usage reports

---

## Security & Privacy

### Your API Key is Safe

-  **Never stored** - used only during request
-  **Encrypted in transit** - TLS 1.3
-  **Not logged** - zero retention
-  **Audited** - SOC 2 compliant
-  **Revocable** - change anytime

### Compliance

- GDPR compliant
- SOC 2 Type II certified
- HIPAA ready (Enterprise)
- ISO 27001 certified

---

## FAQ

### Q: Can I switch between BYOK and other tiers?
**A:** Yes, anytime! No lock-in contracts.

### Q: What if my Anthropic key runs out of credits?
**A:** Requests will fail with a clear error. Add credits to your Anthropic account.

### Q: Do you see my API key?
**A:** No, it's only used to make requests to Anthropic on your behalf and never stored.

### Q: Can I use multiple API keys?
**A:** Yes, on Enterprise plans with team management.

### Q: Is there a minimum commitment?
**A:** No, pay only for what you use.

### Q: What if Anthropic changes their pricing?
**A:** Your costs adjust automatically since you pay them directly. Our $0.002 fee stays fixed.

### Q: Can I get volume discounts?
**A:** Yes! 50K+ executions/month qualify for custom pricing. Contact sales@bizbot.store

---

## Comparison: BYOK vs Standard Tier

| Feature | BYOK | Standard |
|---------|------|----------|
| **Cost per execution** | $0.002 + Anthropic | $0.0475 |
| **Token costs** | Direct to Anthropic | Included |
| **Billing** | Split (us + Anthropic) | Single bill |
| **Markup** | 0% | 14% |
| **Model flexibility** | All Claude models | Sonnet 4 only |
| **Setup complexity** | Medium | Easy |
| **Best for** | High volume, enterprise | Most users |
| **Savings potential** | High (at scale) | Predictable |

---

## Recommendation

### Choose BYOK if:
-  You already have an Anthropic account
-  You run 10K+ executions/month
-  You want maximum cost control
-  You need direct vendor relationships
-  You want to use multiple Claude models

### Choose Standard if:
-  You want simple, predictable pricing
-  You prefer single billing
-  You're running < 10K executions/month
-  You want zero setup hassle
-  You value convenience over savings

---

## Contact

Questions about BYOK pricing?

 **Phone:** (817) 675-9898  
 **Email:** sales@bizbot.store  
 **Web:** https://bizbot.store  
 **Chat:** 24/7 on our website

---

**Last Updated:** October 21, 2025  
**Platform Fee:** $0.002 per execution  
**Competitive Position:** Among the lowest BYOK fees in the industry

