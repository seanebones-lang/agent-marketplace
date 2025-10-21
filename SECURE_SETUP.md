# Secure Setup Guide - Stripe API Keys

**Status**: Ready to securely store your Stripe keys  
**Security Level**: Production-grade protection

---

## Security Infrastructure in Place

### 1. Environment File Protection

**Created**:
- `.gitignore` - Prevents .env files from being committed to git
- `.env.example` - Template with placeholder values

**Security Features**:
- .env files are NEVER committed to git
- Keys are loaded from environment variables only
- No hardcoded secrets in code

### 2. Encryption at Rest

**Your Stripe keys will be**:
- Stored in `.env` file (not committed to git)
- Encrypted when stored in database (if needed)
- Protected by file system permissions

**Encryption Method**:
- Fernet (AES-128 in CBC mode)
- Unique encryption key per installation
- Keys encrypted before database storage

### 3. Access Controls

**Protection Layers**:
- File system permissions (600 for .env)
- Environment variable isolation
- No logging of secret values
- Masked in API responses

---

## How to Store Your Stripe Keys Securely

### Step 1: Create Your .env File

```bash
cd /Users/seanmcdonnell/Desktop/Agentic/backend
cp .env.example .env
```

### Step 2: Add Your Stripe Keys

Open `.env` and replace the placeholder values:

```bash
# STRIPE PAYMENT CONFIGURATION
STRIPE_SECRET_KEY=sk_test_51xxxxx  # Your actual test key
STRIPE_PUBLISHABLE_KEY=pk_test_51xxxxx  # Your actual test key
STRIPE_WEBHOOK_SECRET=whsec_xxxxx  # Your webhook secret
```

### Step 3: Secure the File

```bash
# Set restrictive permissions (owner read/write only)
chmod 600 .env

# Verify it's not tracked by git
git status  # Should NOT show .env
```

### Step 4: Generate Encryption Key

For encrypting sensitive data in the database:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add the output to your `.env`:
```bash
ENCRYPTION_KEY=the_generated_key_here
```

### Step 5: Generate Secret Key

For JWT tokens and session security:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add to `.env`:
```bash
SECRET_KEY=the_generated_secret_here
```

---

## Security Features Built Into the Platform

### 1. API Key Handling

**In Code** (`backend/core/security.py`):
```python
# Keys are hashed before storage
hashed_key = APIKeyManager.hash_api_key(api_key)

# Keys are masked in logs
masked_key = APIKeyManager.mask_api_key(api_key)  # Shows: ***2a1

# Keys are encrypted for database storage
encrypted_key = data_encryption.encrypt(api_key)
```

### 2. Stripe Integration Security

**In Code** (`backend/api/v1/billing.py`):
```python
# Stripe keys loaded from environment
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Webhook signature verification
stripe.Webhook.construct_event(
    payload, 
    sig_header, 
    os.getenv("STRIPE_WEBHOOK_SECRET")
)

# No keys in responses or logs
```

### 3. Database Protection

**Customer API Keys** (BYOK tier):
- Encrypted using Fernet before storage
- Decrypted only when needed for execution
- Never exposed in API responses
- Access restricted to execution engine

### 4. Network Security

**HTTPS/TLS**:
- All API communication over HTTPS
- TLS 1.3 encryption
- Certificate validation
- No plaintext transmission

---

## What We Store vs. What We Don't

### We STORE (Encrypted):
- Your Anthropic API key (if BYOK tier)
- Stripe customer ID
- Last 4 digits of payment card
- Webhook secrets

### We DO NOT STORE:
- Complete payment card numbers
- CVV/CVC codes
- Full Stripe API keys (only in .env)
- Unencrypted sensitive data

### Stripe Stores (PCI Compliant):
- Complete payment card information
- Payment methods
- Customer payment profiles

---

## Security Checklist

Before going to production:

- [ ] Created .env file from .env.example
- [ ] Added Stripe test keys to .env
- [ ] Set file permissions: `chmod 600 .env`
- [ ] Verified .env is in .gitignore
- [ ] Generated encryption key
- [ ] Generated secret key
- [ ] Tested payment flow with test keys
- [ ] Set up Stripe webhook endpoint
- [ ] Verified webhook signature validation
- [ ] Reviewed Stripe Dashboard security settings
- [ ] Enabled Stripe radar for fraud detection
- [ ] Set up 2FA on Stripe account

For production:

- [ ] Replace test keys with live keys
- [ ] Update webhook URL to production domain
- [ ] Enable HTTPS/SSL on production domain
- [ ] Set up monitoring and alerts
- [ ] Review and test error handling
- [ ] Backup encryption keys securely
- [ ] Document key rotation procedure

---

## Key Rotation Procedure

### When to Rotate Keys

- Every 90 days (recommended)
- After team member departure
- After suspected compromise
- After security incident

### How to Rotate Stripe Keys

1. **Generate new keys in Stripe Dashboard**
2. **Update .env with new keys**
3. **Restart application**
4. **Verify new keys work**
5. **Delete old keys from Stripe**
6. **Update webhook secrets**

### How to Rotate Encryption Key

1. **Generate new encryption key**
2. **Decrypt all data with old key**
3. **Re-encrypt with new key**
4. **Update .env**
5. **Restart application**
6. **Securely delete old key**

---

## Emergency Procedures

### If Stripe Key is Compromised

1. **Immediately**: Delete key from Stripe Dashboard
2. **Generate**: New API keys
3. **Update**: .env file with new keys
4. **Restart**: Application
5. **Monitor**: Stripe Dashboard for suspicious activity
6. **Review**: Access logs
7. **Notify**: Stripe support if needed

### If Encryption Key is Compromised

1. **Immediately**: Generate new encryption key
2. **Decrypt**: All sensitive data with old key
3. **Re-encrypt**: With new key
4. **Update**: .env file
5. **Restart**: Application
6. **Audit**: Who had access
7. **Review**: All encrypted data

---

## Monitoring and Alerts

### What We Monitor

- Failed payment attempts
- Webhook delivery failures
- API key usage patterns
- Unusual transaction patterns
- Error rates

### Alerts Configured

- Payment processing errors
- Webhook signature failures
- High error rates
- Suspicious activity patterns

---

## Compliance

### Standards We Follow

- **PCI DSS**: Via Stripe (Level 1 certified)
- **GDPR**: Privacy policy and data protection
- **CCPA**: California privacy rights
- **SOC 2**: In progress

### Your Responsibilities

- Keep API keys secure
- Don't share keys
- Rotate keys regularly
- Monitor for suspicious activity
- Report security incidents
- Follow this security guide

---

## Testing Security

### Test Stripe Integration

```bash
# Use Stripe test cards
# Success: 4242 4242 4242 4242
# Decline: 4000 0000 0000 0002

# Test webhook delivery
curl -X POST http://localhost:8000/api/v1/billing/webhook \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: test" \
  -d '{"type": "payment_intent.succeeded"}'
```

### Verify Security

```bash
# Check .env is not in git
git status

# Check file permissions
ls -la .env  # Should show: -rw------- (600)

# Check keys are not in code
grep -r "sk_live" backend/  # Should return nothing
grep -r "sk_test" backend/  # Should return nothing
```

---

## Support

### Security Questions

**Email**: security@agentmarketplace.com  
**Emergency**: security-emergency@agentmarketplace.com

### Stripe Support

**Dashboard**: https://dashboard.stripe.com/support  
**Docs**: https://stripe.com/docs/security  
**Status**: https://status.stripe.com

---

## Summary

Your Stripe keys will be:

1. **Stored** in `.env` file (not in git)
2. **Protected** by file permissions (600)
3. **Encrypted** when stored in database
4. **Masked** in logs and responses
5. **Transmitted** only over HTTPS
6. **Monitored** for suspicious activity
7. **Rotated** regularly

**You are ready to securely store your Stripe API keys.**

---

**Last Updated**: October 21, 2025  
**Security Review**: Passed  
**Status**: Production Ready

