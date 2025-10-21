# Vercel Setup Instructions for bizbot.store

## Current Status
- DNS Records: Updated in IONOS
- GitHub: Latest code pushed (commit aae7220)
- Vercel: Needs domain configuration

---

## Step-by-Step Vercel Configuration

### 1. Access Your Vercel Project

Go to: https://vercel.com/dashboard

Find your project: `agenticteamdemo`

### 2. Check Latest Build Status

- Click on the project
- Look at the latest deployment
- If it shows "Build Failed", click "Redeploy" after the UI fix we just pushed

### 3. Add Custom Domain (bizbot.store)

**In Vercel Dashboard**:

1. Click on your project `agenticteamdemo`
2. Go to **Settings** tab
3. Click **Domains** in the left sidebar
4. Click **Add** button
5. Enter: `bizbot.store`
6. Click **Add**

Vercel will show you one of these:

**Option A: Valid Configuration Detected**
- Vercel detects your DNS records
- Click "Add" to confirm
- SSL certificate will be issued automatically (takes 1-2 minutes)

**Option B: Configuration Required**
- Vercel will show required DNS records
- Verify they match what you added in IONOS:
  ```
  A Record: @ → 76.76.21.21
  ```

### 4. Add WWW Subdomain

Repeat the process:
1. Click **Add** again
2. Enter: `www.bizbot.store`
3. Click **Add**

Vercel will automatically redirect www to root domain.

### 5. Configure Environment Variables

**In Vercel Dashboard**:

1. Go to **Settings** → **Environment Variables**
2. Add these variables:

```bash
# API Configuration
NEXT_PUBLIC_API_URL
Value: https://api.bizbot.store
Environment: Production, Preview, Development

# Stripe Public Key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
Value: pk_live_51S40C8CHzMTnpYNot9Qlzd98VpmyGsQpm2n32CZtWfAKWyYng2BU0F8QfsLSksSeYLvcLdw6pnXH7QCCYRhoV9yr00dujwaMSO
Environment: Production

# App URL
NEXT_PUBLIC_APP_URL
Value: https://bizbot.store
Environment: Production
```

**Important**: After adding environment variables, you must redeploy for them to take effect.

### 6. Redeploy with New Environment Variables

1. Go to **Deployments** tab
2. Click the three dots (...) on the latest deployment
3. Click **Redeploy**
4. Check "Use existing Build Cache" (optional)
5. Click **Redeploy**

---

## Verification Steps

### 1. Check Build Success
- Wait for deployment to complete (1-3 minutes)
- Status should show "Ready"
- No build errors

### 2. Check Domain Status
- Go to Settings → Domains
- Both domains should show:
  - bizbot.store: Valid Configuration
  - www.bizbot.store: Valid Configuration
- SSL certificate should be "Active"

### 3. Test Your Site

**Open in browser**:
- https://bizbot.store
- https://www.bizbot.store

**You should see**:
- Your Agent Marketplace homepage
- No SSL warnings
- Fast load times

### 4. Test API Connection

**Important**: The frontend is trying to connect to `https://api.bizbot.store`

This will fail until you deploy the backend. You'll see:
- Homepage works
- Login/Dashboard might show "API connection error"

This is expected and normal until backend is deployed.

---

## Next: Deploy Backend

### Option 1: Railway (Recommended)

**Why Railway**:
- Easiest setup
- Built-in PostgreSQL + Redis
- Automatic deployments from GitHub
- $5/month to start

**Steps**:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy from backend directory
cd /Users/seanmcdonnell/Desktop/Agentic/backend
railway init

# Link to new project
# Select: Create new project
# Name: agent-marketplace-backend

# Add PostgreSQL
railway add --plugin postgresql

# Add Redis
railway add --plugin redis

# Deploy
railway up
```

**After deployment**:
1. Go to Railway dashboard
2. Click on your service
3. Go to Settings → Domains
4. Generate domain (e.g., `agent-marketplace-backend.up.railway.app`)
5. Add custom domain: `api.bizbot.store`

**Add Environment Variables in Railway**:
- Copy all variables from `backend/.env`
- Add them in Railway dashboard → Variables
- Railway will auto-inject DATABASE_URL and REDIS_URL

### Option 2: Render

**Steps**:
1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repository
4. Root Directory: `backend`
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Add PostgreSQL database
8. Add Redis instance
9. Add environment variables
10. Add custom domain: `api.bizbot.store`

### Option 3: DigitalOcean App Platform

**Steps**:
1. Go to https://cloud.digitalocean.com/apps
2. Create App
3. Connect GitHub
4. Select repository
5. Configure:
   - Type: Web Service
   - Source Directory: `/backend`
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `uvicorn main:app --host 0.0.0.0 --port 8080`
6. Add PostgreSQL database
7. Add Redis database
8. Add environment variables
9. Add domain: `api.bizbot.store`

---

## DNS Configuration for Backend

Once you have your backend deployed, add this to IONOS:

```
Type: CNAME
Host Name: api
Value: your-backend-url.railway.app (or render.com, etc.)
```

Or if the provider gives you an IP:

```
Type: A
Host Name: api
Value: [IP address from provider]
```

---

## Final Checklist

### Frontend (Vercel)
- [ ] Project deployed successfully
- [ ] bizbot.store domain added
- [ ] www.bizbot.store domain added
- [ ] SSL certificates active
- [ ] Environment variables configured
- [ ] Site loads at https://bizbot.store

### Backend (Railway/Render/DO)
- [ ] Service deployed
- [ ] PostgreSQL connected
- [ ] Redis connected
- [ ] Environment variables set
- [ ] Health check passes: `/api/v1/health`
- [ ] Custom domain configured: api.bizbot.store
- [ ] SSL certificate active

### DNS (IONOS)
- [ ] A record for @ → 76.76.21.21
- [ ] CNAME for www → cname.vercel-dns.com
- [ ] CNAME for api → [backend-provider-url]

### Integration
- [ ] Frontend can reach backend API
- [ ] Stripe webhook configured
- [ ] CORS allows bizbot.store
- [ ] Rate limiting working
- [ ] Authentication working

---

## Troubleshooting

### "Domain Not Found" in Vercel

**Solution**: Wait 5-60 minutes for DNS propagation, then try adding domain again.

### "Invalid Configuration" in Vercel

**Solution**: 
1. Check DNS records in IONOS
2. Use `dig bizbot.store` to verify DNS
3. Wait for propagation

### Build Still Failing

**Solution**:
```bash
cd /Users/seanmcdonnell/Desktop/Agentic
git pull origin main
vercel --prod
```

### Frontend Loads But API Errors

**Solution**: This is normal until backend is deployed. Deploy backend next.

---

## Quick Commands

```bash
# Check DNS propagation
dig bizbot.store
dig www.bizbot.store
dig api.bizbot.store

# Test backend health (after deployment)
curl https://api.bizbot.store/api/v1/health

# View Vercel logs
vercel logs --follow

# Redeploy Vercel
vercel --prod --force

# Deploy to Railway
cd backend && railway up
```

---

## Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **DNS Checker**: https://dnschecker.org
- **SSL Checker**: https://www.ssllabs.com/ssltest/

---

## What You Should See Right Now

1. Go to https://vercel.com/dashboard
2. Find `agenticteamdemo` project
3. Latest deployment should be building or ready
4. Once ready, add domains as described above
5. Within 1 hour, https://bizbot.store should load your site

**Current Status**: DNS configured, waiting for Vercel domain setup.

**Next Action**: Add bizbot.store domain in Vercel dashboard.

