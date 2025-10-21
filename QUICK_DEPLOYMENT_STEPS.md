# Quick Deployment Steps - bizbot.store

## Current Status
✅ DNS configured in IONOS  
✅ Code pushed to GitHub  
⏳ Waiting for Vercel domain setup  

---

## Next 3 Steps (5 minutes)

### 1. Add Domain in Vercel

1. Go to: https://vercel.com/dashboard
2. Click your project: `agenticteamdemo`
3. Settings → Domains
4. Click "Add"
5. Type: `bizbot.store`
6. Click "Add"
7. Repeat for: `www.bizbot.store`

### 2. Add Environment Variables

Settings → Environment Variables → Add:

```
NEXT_PUBLIC_API_URL = https://api.bizbot.store
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY = pk_live_51S40C8CHzMTnpYNot9Qlzd98VpmyGsQpm2n32CZtWfAKWyYng2BU0F8QfsLSksSeYLvcLdw6pnXH7QCCYRhoV9yr00dujwaMSO
NEXT_PUBLIC_APP_URL = https://bizbot.store
```

Set all to: Production, Preview, Development

### 3. Redeploy

Deployments → Latest → Three dots (...) → Redeploy

---

## What You'll See

**Immediately**: Vercel starts building  
**After 2-3 minutes**: Build completes  
**After 5-60 minutes**: DNS propagates, https://bizbot.store goes live  

---

## Then: Deploy Backend (15 minutes)

### Easiest: Railway

```bash
npm install -g @railway/cli
railway login
cd /Users/seanmcdonnell/Desktop/Agentic/backend
railway init
railway add --plugin postgresql
railway add --plugin redis
railway up
```

Then in Railway dashboard:
- Add all environment variables from `.env`
- Settings → Domains → Add `api.bizbot.store`

---

## Full Instructions

See: `VERCEL_SETUP_INSTRUCTIONS.md`

---

## Need Help?

**Check build status**: https://vercel.com/dashboard  
**Check DNS**: https://dnschecker.org/?domain=bizbot.store  
**Test site**: https://bizbot.store (after DNS propagates)

