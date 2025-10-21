# Deploy Agent Marketplace to Vercel - Fresh Start

## The Issue
The "demo-app" project in Vercel is still connected to the old restaurant demo repository, not your AGENTICteam repository.

## Solution: Create Brand New Vercel Project

### Step 1: Go to Vercel Dashboard
https://vercel.com/dashboard

### Step 2: Create New Project
1. Click **Add New...** button (top right)
2. Select **Project**
3. Click **Import Git Repository**

### Step 3: Select AGENTICteam Repository
1. Find: `seanebones-lang/AGENTICteam`
2. Click **Import**

### Step 4: Configure Project Settings

**Project Name**: `agent-marketplace-bizbot`

**Framework Preset**: Next.js

**Root Directory**: Leave blank (or `./`)

**Build and Output Settings**:
```
Build Command: cd frontend && npm run build
Output Directory: frontend/.next
Install Command: cd frontend && npm install
```

### Step 5: Add Environment Variables

Click **Environment Variables** and add these 3:

**Variable 1:**
```
Name: NEXT_PUBLIC_API_URL
Value: https://api.bizbot.store
Environment: Production, Preview, Development
```

**Variable 2:**
```
Name: NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
Value: pk_live_51S40C8CHzMTnpYNot9Qlzd98VpmyGsQpm2n32CZtWfAKWyYng2BU0F8QfsLSksSeYLvcLdw6pnXH7QCCYRhoV9yr00dujwaMSO
Environment: Production
```

**Variable 3:**
```
Name: NEXT_PUBLIC_APP_URL
Value: https://bizbot.store
Environment: Production
```

### Step 6: Deploy
Click **Deploy** button

Wait 2-3 minutes for the build to complete.

### Step 7: Add Custom Domain

Once deployed successfully:

1. Go to **Settings** → **Domains**
2. Click **Add**
3. Enter: `bizbot.store`
4. Click **Add**
5. Vercel will verify your DNS (already configured in IONOS)
6. SSL certificate will be issued automatically

7. Click **Add** again
8. Enter: `www.bizbot.store`
9. Click **Add**

### Step 8: Delete Old demo-app Project (Optional)

1. Go to the old "demo-app" project
2. Settings → General → Delete Project
3. Confirm deletion

---

## What You Should See

After deployment completes:
- Build logs show: "Agent Marketplace" pages (not restaurant pages)
- Routes include: `/dashboard`, `/agents`, `/marketplace` (not `/kitchen`, `/pos`)
- https://bizbot.store loads your Agent Marketplace
- Title: "Agent Marketplace Platform" (not "Bella Vista Bistro")

---

## Verification Checklist

✅ New project created from AGENTICteam repository  
✅ Build completes successfully  
✅ Environment variables added  
✅ bizbot.store domain added  
✅ SSL certificate active  
✅ Site loads at https://bizbot.store  
✅ Shows Agent Marketplace (not restaurant demo)  

---

## Current Repository Info

**Correct Repository**: `https://github.com/seanebones-lang/AGENTICteam`  
**Latest Commit**: `b84ed71` (Fix Vercel build)  
**Branch**: `main`  

The old demo-app is pulling from a different repository (commit 6bfb1eb doesn't exist in AGENTICteam).

---

## Quick Start

1. https://vercel.com/dashboard
2. Add New → Project
3. Import: `AGENTICteam`
4. Configure build settings (above)
5. Add environment variables (above)
6. Deploy
7. Add domain: `bizbot.store`

**This should take 5 minutes total.**

