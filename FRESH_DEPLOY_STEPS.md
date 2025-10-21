# Fresh Deployment Steps

## After Creating New GitHub Repository

Once you create `agent-marketplace` repository on GitHub, run these commands:

```bash
cd /Users/seanmcdonnell/Desktop/Agentic

# Add new remote
git remote add origin https://github.com/seanebones-lang/agent-marketplace.git

# Push all code
git push -u origin main --force
```

## Then Deploy to Vercel

1. Go to: https://vercel.com/new
2. Click **Import Git Repository**
3. Select: `seanebones-lang/agent-marketplace`
4. Click **Import**

### Configure Settings:

```
Project Name: agent-marketplace-bizbot
Framework Preset: Next.js
Root Directory: frontend
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

### Add Environment Variables:

```
NEXT_PUBLIC_API_URL = https://api.bizbot.store
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY = pk_live_51S40C8CHzMTnpYNot9Qlzd98VpmyGsQpm2n32CZtWfAKWyYng2BU0F8QfsLSksSeYLvcLdw6pnXH7QCCYRhoV9yr00dujwaMSO
NEXT_PUBLIC_APP_URL = https://bizbot.store
```

### Deploy

Click **Deploy** button

### Add Domain

After successful deployment:
1. Settings → Domains
2. Add: `bizbot.store`
3. Add: `www.bizbot.store`

Done!

