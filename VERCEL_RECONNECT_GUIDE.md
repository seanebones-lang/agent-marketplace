# Quick Guide: Reconnect Vercel to AGENTICteam Repository

## The Issue
Your Vercel project is connected to an old repository (Bella Vista Bistro demo) instead of your Agent Marketplace code in the AGENTICteam repository.

## Solution: 2 Options

---

## Option 1: Via Vercel Dashboard (Easiest - 2 minutes)

### Step 1: Disconnect Old Repository
1. Go to: https://vercel.com/dashboard
2. Click on your project (the one with bizbot.store)
3. Click **Settings** (top menu)
4. Click **Git** (left sidebar)
5. Scroll down to **Disconnect Git Repository**
6. Click **Disconnect**
7. Confirm the disconnection

### Step 2: Connect to AGENTICteam
1. After disconnecting, you'll see **Connect Git Repository**
2. Click **Connect**
3. Select **GitHub**
4. Find and select: `seanebones-lang/AGENTICteam`
5. Click **Connect**

### Step 3: Update Build Settings
1. Still in **Settings**
2. Click **General** (left sidebar)
3. Scroll to **Build & Development Settings**
4. Update these:
   ```
   Framework Preset: Next.js
   Root Directory: (leave blank)
   Build Command: cd frontend && npm run build
   Output Directory: frontend/.next
   Install Command: cd frontend && npm install
   ```
5. Click **Save**

### Step 4: Deploy
1. Go to **Deployments** tab
2. Vercel should auto-deploy from the new repository
3. Or click **Redeploy** on the latest deployment

---

## Option 2: Via Terminal (Alternative)

If you prefer command line:

```bash
# Install Vercel CLI
sudo npm install -g vercel

# Login to Vercel
vercel login

# Go to frontend directory
cd /Users/seanmcdonnell/Desktop/Agentic/frontend

# Link to existing project
vercel link

# When prompted:
# - Set up and deploy: Y
# - Which scope: [your account]
# - Link to existing project: Y
# - Project name: [select your existing project]

# Deploy to production
vercel --prod
```

---

## What This Does

✅ Keeps your existing Vercel project  
✅ Keeps bizbot.store domain configuration  
✅ Keeps environment variables  
✅ Just switches the source code to AGENTICteam  
✅ Deploys the correct Agent Marketplace application  

---

## After Reconnecting

You should see:
- Vercel pulls code from `AGENTICteam` repository
- New deployment starts automatically
- Build completes successfully (with our fixes)
- https://bizbot.store shows your Agent Marketplace
- No more "Bella Vista Bistro"!

---

## Verification

Once deployed, check:
1. https://bizbot.store loads
2. Title shows "Agent Marketplace" (not Bella Vista)
3. Homepage shows your agent marketplace UI
4. No build errors in Vercel dashboard

---

## If You Need Help

The Vercel dashboard method (Option 1) is the easiest and most visual. Just follow the steps above and you'll have it reconnected in 2 minutes.

**Current Repository**: `seanebones-lang/AGENTICteam`  
**Domain**: bizbot.store  
**Latest Commit**: b84ed71 (with build fixes)

