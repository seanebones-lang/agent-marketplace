# Stripe Billing Integration Guide

Complete Stripe integration for subscription management and payments.

## Overview

The Agent Marketplace Platform includes full Stripe integration for:
- Subscription management
- Payment processing
- Usage-based billing
- Customer portal
- Webhook handling

---

## Setup

### 1. Install Stripe

```bash
pip install stripe==11.1.0
```

### 2. Configure Environment Variables

Add to `.env`:
```bash
STRIPE_SECRET_KEY=sk_test_your_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

### 3. Run Database Migration

```bash
cd backend
alembic upgrade head
```

This adds `stripe_customer_id` and `stripe_subscription_id` fields to the customers table.

---

## API Endpoints

### Create Checkout Session

Create a Stripe Checkout session for subscription signup.

```bash
POST /api/v1/billing/checkout/session
Authorization: Bearer {token}

{
  "price_id": "price_1234567890",
  "success_url": "https://yourapp.com/success",
  "cancel_url": "https://yourapp.com/cancel"
}
```

**Response:**
```json
{
  "session_id": "cs_test_1234567890",
  "url": "https://checkout.stripe.com/pay/cs_test_1234567890"
}
```

### Get Subscription

Get current subscription information.

```bash
GET /api/v1/billing/subscription
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "sub_1234567890",
  "status": "active",
  "current_period_start": 1698000000,
  "current_period_end": 1700592000,
  "cancel_at_period_end": false,
  "plan_name": "Pro Plan",
  "plan_amount": 99.00
}
```

### Cancel Subscription

Cancel subscription at the end of the billing period.

```bash
POST /api/v1/billing/subscription/cancel
Authorization: Bearer {token}
```

**Response:**
```json
{
  "message": "Subscription will be cancelled at period end",
  "cancel_at": 1700592000
}
```

### Resume Subscription

Resume a cancelled subscription.

```bash
POST /api/v1/billing/subscription/resume
Authorization: Bearer {token}
```

### Get Payment Methods

List customer's payment methods.

```bash
GET /api/v1/billing/payment-methods
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": "pm_1234567890",
    "type": "card",
    "card_brand": "visa",
    "card_last4": "4242",
    "card_exp_month": 12,
    "card_exp_year": 2025
  }
]
```

### Get Invoices

Retrieve customer invoices.

```bash
GET /api/v1/billing/invoices?limit=10
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": "in_1234567890",
    "amount_due": 99.00,
    "amount_paid": 99.00,
    "status": "paid",
    "created": 1698000000,
    "invoice_pdf": "https://pay.stripe.com/invoice/..."
  }
]
```

### Record Usage

Record usage for metered billing.

```bash
POST /api/v1/billing/usage/record?subscription_item_id=si_1234567890
Authorization: Bearer {token}

{
  "quantity": 100,
  "timestamp": 1698000000,
  "action": "increment"
}
```

### Customer Portal

Create a Stripe Customer Portal session.

```bash
GET /api/v1/billing/portal?return_url=https://yourapp.com/dashboard
Authorization: Bearer {token}
```

**Response:**
```json
{
  "url": "https://billing.stripe.com/session/..."
}
```

### Webhook Endpoint

Handle Stripe webhook events.

```bash
POST /api/v1/billing/webhook
Stripe-Signature: {signature}

{webhook payload}
```

---

## Stripe Dashboard Setup

### 1. Create Products and Prices

In Stripe Dashboard:
1. Go to **Products** → **Add Product**
2. Create pricing tiers:
   - **Free**: $0/month
   - **Basic**: $29/month
   - **Pro**: $99/month
   - **Enterprise**: $499/month

3. Note the Price IDs (e.g., `price_1234567890`)

### 2. Configure Webhook

1. Go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. URL: `https://your-api.com/api/v1/billing/webhook`
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the webhook secret to `.env`

### 3. Enable Customer Portal

1. Go to **Settings** → **Billing** → **Customer portal**
2. Enable customer portal
3. Configure allowed actions:
   - Update payment method
   - Cancel subscription
   - View invoices

---

## Usage-Based Billing

For metered billing (e.g., per API call):

### 1. Create Metered Price

In Stripe Dashboard:
1. Create a new price
2. Select **Usage is metered**
3. Set unit amount (e.g., $0.01 per unit)
4. Note the Price ID

### 2. Record Usage

```python
from backend.api.v1.billing import record_usage

# After each agent execution
await record_usage(
    usage=UsageRecord(
        quantity=1,  # 1 execution
        timestamp=int(time.time())
    ),
    subscription_item_id="si_1234567890"
)
```

---

## Webhook Event Handling

The platform automatically handles these events:

### checkout.session.completed
- Creates Stripe customer
- Updates customer tier
- Activates subscription

### customer.subscription.deleted
- Downgrades customer to free tier
- Deactivates premium features

### invoice.payment_failed
- Sends payment failure notification
- Optionally suspends account

---

## Testing

### Test Cards

Use Stripe test cards:
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **3D Secure**: `4000 0027 6000 3184`

### Test Webhook

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local
stripe listen --forward-to localhost:8000/api/v1/billing/webhook

# Trigger test event
stripe trigger checkout.session.completed
```

---

## Frontend Integration

### React Example

```typescript
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe('pk_test_your_publishable_key');

async function handleSubscribe(priceId: string) {
  // Create checkout session
  const response = await fetch('/api/v1/billing/checkout/session', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      price_id: priceId,
      success_url: window.location.origin + '/success',
      cancel_url: window.location.origin + '/cancel'
    })
  });
  
  const { session_id } = await response.json();
  
  // Redirect to Stripe Checkout
  const stripe = await stripePromise;
  await stripe.redirectToCheckout({ sessionId: session_id });
}
```

---

## Security Best Practices

### 1. Verify Webhook Signatures

Always verify webhook signatures:
```python
stripe.Webhook.construct_event(
    payload, 
    sig_header, 
    webhook_secret
)
```

### 2. Use Environment Variables

Never hardcode API keys:
```python
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
```

### 3. Validate Amounts

Always validate amounts server-side:
```python
if amount < minimum_amount:
    raise ValueError("Amount too low")
```

### 4. Handle Idempotency

Use idempotency keys for critical operations:
```python
stripe.Charge.create(
    amount=1000,
    currency="usd",
    idempotency_key="unique_key_123"
)
```

---

## Troubleshooting

### Webhook Not Receiving Events

1. Check webhook URL is publicly accessible
2. Verify webhook secret is correct
3. Check Stripe Dashboard → Webhooks → Logs

### Payment Declined

1. Check test card number
2. Verify billing address
3. Check Stripe Dashboard → Payments → Logs

### Subscription Not Activating

1. Check webhook is receiving `checkout.session.completed`
2. Verify customer_id in metadata
3. Check database for subscription update

---

## Production Checklist

- [ ] Replace test keys with live keys
- [ ] Configure production webhook endpoint
- [ ] Enable Stripe Radar for fraud prevention
- [ ] Set up email notifications
- [ ] Configure tax collection
- [ ] Test subscription lifecycle
- [ ] Set up monitoring and alerts
- [ ] Document refund policy
- [ ] Configure dunning (failed payment retry)
- [ ] Set up revenue recognition

---

## Pricing Tiers

### Recommended Structure

**Free Tier**
- 10 agent executions/month
- Basic support
- Community access

**Basic - $29/month**
- 100 executions/month
- Email support
- All agent packages

**Pro - $99/month**
- 1,000 executions/month
- Priority support
- Custom agents
- Analytics dashboard

**Enterprise - $499/month**
- Unlimited executions
- Dedicated support
- Custom integrations
- SLA guarantee

---

## Support

For Stripe integration issues:
- Stripe Documentation: https://stripe.com/docs
- Stripe Support: https://support.stripe.com
- Test Dashboard: https://dashboard.stripe.com/test

---

**The platform is now fully integrated with Stripe for production-ready billing!** 💳

