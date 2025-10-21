# Vercel Deployment Guide - bizbot.store

**Domain**: bizbot.store  
**Platform**: Vercel  
**Status**: Ready to Deploy

---

## Quick Fix for Current Error

The build is failing due to path resolution. Here's the immediate fix:

### Step 1: Update Frontend Package.json

Add `baseUrl` to ensure proper path resolution:

```bash
cd /Users/seanmcdonnell/Desktop/Agentic/frontend
```

### Step 2: Redeploy

```bash
cd /Users/seanmcdonnell/Desktop/Agentic
git add .
git commit -m "Fix Vercel build: Update path resolution for UI components"
git push origin main
```

Vercel will automatically redeploy.

---

## Complete Deployment Steps

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

### 3. Deploy Frontend

```bash
cd /Users/seanmcdonnell/Desktop/Agentic/frontend
vercel --prod
```

**During deployment, answer**:
- Set up and deploy: `Y`
- Which scope: Select your account
- Link to existing project: `Y` (if exists) or `N`
- Project name: `agenticteamdemo`
- Directory: `./` (current directory)
- Override settings: `N`

### 4. Configure Environment Variables in Vercel

Go to: https://vercel.com/your-username/agenticteamdemo/settings/environment-variables

**Add these variables**:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://api.bizbot.store

# Stripe (Public key only for frontend)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key_here
```

### 5. Deploy Backend (Separate Service)

**Option A: Deploy Backend to Railway/Render/DigitalOcean**

The backend needs:
- PostgreSQL database
- Redis instance
- Long-running process support
- Environment variables

**Recommended**: Railway.app (easiest for FastAPI + PostgreSQL + Redis)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
cd /Users/seanmcdonnell/Desktop/Agentic/backend
railway init

# Add PostgreSQL
railway add --plugin postgresql

# Add Redis
railway add --plugin redis

# Deploy
railway up
```

**Option B: Use Vercel for Backend (Serverless)**

Note: Vercel has limitations for FastAPI (cold starts, timeouts)

```bash
cd /Users/seanmcdonnell/Desktop/Agentic/backend
vercel --prod
```

### 6. Connect Domain bizbot.store

**In Vercel Dashboard**:

1. Go to your project: https://vercel.com/your-username/agenticteamdemo
2. Click "Settings" → "Domains"
3. Add domain: `bizbot.store`
4. Add subdomain: `www.bizbot.store`
5. Add API subdomain: `api.bizbot.store` (for backend)

**DNS Configuration**:

Add these records to your domain registrar (where you bought bizbot.store):

```
Type    Name    Value
A       @       76.76.21.21
CNAME   www     cname.vercel-dns.com
CNAME   api     your-backend-url.vercel.app
```

Or use Vercel nameservers:
```
ns1.vercel-dns.com
ns2.vercel-dns.com
```

---

## Environment Variables Setup

### Frontend (.env.local in Vercel)

```bash
NEXT_PUBLIC_API_URL=https://api.bizbot.store
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_51S40C8CHzMTnpYNot9Qlzd98VpmyGsQpm2n32CZtWfAKWyYng2BU0F8QfsLSksSeYLvcLdw6pnXH7QCCYRhoV9yr00dujwaMSO
```

### Backend (Railway/Render Environment Variables)

```bash
# Application
ENVIRONMENT=production
FRONTEND_URL=https://bizbot.store

# Database (provided by Railway/Render)
DATABASE_URL=postgresql://...

# Redis (provided by Railway/Render)
REDIS_URL=redis://...

# LLM Provider
ANTHROPIC_API_KEY=your_anthropic_key

# Security
SECRET_KEY=OZVrb6Akn17kiBbexIUsgF7RCAZJniuiRofnvm5sUKA
ENCRYPTION_KEY=YeI44lil-nUivS5_wnsnNqF52NWPS2gT-ey89IyVIS0=

# Stripe (Use your actual keys from .env file)
STRIPE_SECRET_KEY=sk_live_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

---

## Recommended Architecture

```
bizbot.store (Frontend - Vercel)
    ↓
api.bizbot.store (Backend - Railway/Render)
    ↓
├── PostgreSQL (Railway/Render)
├── Redis (Railway/Render)
└── Qdrant (Cloud or Self-hosted)
```

---

## Fixing Current Vercel Error

The error is: `Module not found: Can't resolve '@/components/ui/card'`

**Quick Fix**:

1. Ensure `tsconfig.json` has proper paths (already done)
2. Ensure `next.config.js` doesn't override paths
3. Commit and push:

```bash
cd /Users/seanmcdonnell/Desktop/Agentic
git add .
git commit -m "Fix: Ensure UI component paths are properly resolved"
git push origin main
```

Vercel will auto-redeploy.

**If still failing**, check:
- All UI components exist in `frontend/src/components/ui/`
- No circular imports
- All imports use `@/components/ui/...` format

---

## Post-Deployment Checklist

### Frontend (Vercel)
- [ ] Domain connected: bizbot.store
- [ ] SSL certificate active
- [ ] Environment variables set
- [ ] Build successful
- [ ] Homepage loads

### Backend (Railway/Render)
- [ ] API deployed
- [ ] Database connected
- [ ] Redis connected
- [ ] Environment variables set
- [ ] Health check passes: `/api/v1/health`
- [ ] Metrics endpoint: `/api/v1/metrics`

### Domain Configuration
- [ ] bizbot.store → Frontend
- [ ] www.bizbot.store → Frontend
- [ ] api.bizbot.store → Backend
- [ ] SSL certificates active for all

### Stripe Configuration
- [ ] Webhook URL updated: `https://api.bizbot.store/api/v1/billing/webhook`
- [ ] Webhook secret added to backend env
- [ ] Test payment flow
- [ ] Live mode activated

### Security
- [ ] CORS configured for bizbot.store
- [ ] Rate limiting active
- [ ] Security headers enabled
- [ ] API keys secured in environment variables
- [ ] No secrets in git repository

---

## Troubleshooting

### Build Fails on Vercel

**Check**:
1. All dependencies in `package.json`
2. Node version compatibility
3. Build command is correct
4. No missing imports

**View logs**:
```bash
vercel logs
```

### Backend Connection Issues

**Check**:
1. CORS allows bizbot.store
2. API URL is correct in frontend
3. Backend is running
4. Database is connected

**Test backend**:
```bash
curl https://api.bizbot.store/api/v1/health
```

### Domain Not Resolving

**Check**:
1. DNS propagation (can take 24-48 hours)
2. Nameservers are correct
3. A/CNAME records are correct

**Test DNS**:
```bash
dig bizbot.store
nslookup bizbot.store
```

---

## Support

### Vercel Support
- Dashboard: https://vercel.com/dashboard
- Docs: https://vercel.com/docs
- Discord: https://vercel.com/discord

### Railway Support
- Dashboard: https://railway.app/dashboard
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

---

## Quick Commands

```bash
# Deploy frontend
cd frontend && vercel --prod

# Deploy backend (Railway)
cd backend && railway up

# View logs
vercel logs --follow

# Check domain status
vercel domains ls

# Add domain
vercel domains add bizbot.store
```

---

**Next Step**: Fix the current build error by ensuring all imports are correct, then Vercel will auto-deploy to bizbot.store.
