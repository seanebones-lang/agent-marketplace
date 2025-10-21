# Vercel Deployment Guide

Complete guide for deploying the Agent Marketplace frontend to Vercel.

## Prerequisites

- GitHub repository: https://github.com/seanebones-lang/AGENTICteam
- Vercel account
- GitHub Personal Access Token (generate at: https://github.com/settings/tokens)

## Quick Deployment

### Option 1: Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/new
   - Sign in with GitHub

2. **Import Repository**
   - Click "Import Project"
   - Select "Import Git Repository"
   - Enter repository URL: `https://github.com/seanebones-lang/AGENTICteam`
   - Click "Continue"

3. **Configure Project**
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

4. **Environment Variables**
   Add the following environment variables:
   
   ```
   NEXT_PUBLIC_API_URL=https://api.agentic.bizbot.store
   NEXT_PUBLIC_APP_URL=https://agentic.bizbot.store
   NEXT_PUBLIC_ENABLE_ANALYTICS=true
   NEXT_PUBLIC_ENABLE_LIVE_MODE=true
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete (2-3 minutes)
   - Your site will be live at: `https://your-project.vercel.app`

### Option 2: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Navigate to frontend directory
cd /Users/seanmcdonnell/Desktop/Agentic/frontend

# Deploy to production
vercel --prod

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? [Your account]
# - Link to existing project? No
# - Project name? agent-marketplace
# - Directory? ./
# - Override settings? No
```

## Custom Domain Setup

### 1. Add Custom Domain

In Vercel Dashboard:
1. Go to Project Settings > Domains
2. Add domain: `agentic.bizbot.store`
3. Follow DNS configuration instructions

### 2. DNS Configuration

Add these records to your DNS provider:

```
Type    Name    Value                       TTL
A       @       76.76.21.21                 Auto
CNAME   www     cname.vercel-dns.com        Auto
```

### 3. SSL Certificate

- Vercel automatically provisions SSL certificates
- HTTPS will be enabled within 24 hours
- Certificate auto-renews

## Environment Variables

### Production Variables

Set these in Vercel Dashboard > Settings > Environment Variables:

```env
# API Configuration
NEXT_PUBLIC_API_URL=https://api.agentic.bizbot.store
NEXT_PUBLIC_APP_URL=https://agentic.bizbot.store

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_LIVE_MODE=true

# Optional: Analytics
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_POSTHOG_KEY=phc_xxxxxxxxxxxxx
```

### Preview/Development Variables

For preview deployments, you can set different values:

```env
NEXT_PUBLIC_API_URL=https://api-staging.agentic.bizbot.store
NEXT_PUBLIC_APP_URL=https://preview.agentic.bizbot.store
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_LIVE_MODE=false
```

## Deployment Settings

### Build Settings

In `vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "outputDirectory": ".next"
}
```

### Regions

Multi-region deployment configured for:
- **iad1** (US East - Washington, D.C.)
- **sfo1** (US West - San Francisco)
- **fra1** (EU - Frankfurt)

### Performance Optimizations

Enabled in `next.config.js`:
- SWC minification
- Image optimization (AVIF, WebP)
- Code splitting
- CSS optimization
- Package imports optimization

## GitHub Integration

### Automatic Deployments

Vercel automatically deploys:
- **Production**: Pushes to `main` branch
- **Preview**: Pull requests and other branches

### Branch Protection

Recommended GitHub branch protection rules for `main`:
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date
- Include administrators

### Deployment Hooks

Get webhook URL from Vercel Dashboard > Settings > Git:
- Use for manual deployments
- Integrate with CI/CD pipelines
- Trigger from external services

## Monitoring & Analytics

### Vercel Analytics

Enable in Dashboard > Analytics:
- Real User Monitoring (RUM)
- Web Vitals tracking
- Performance insights
- Traffic analytics

### Speed Insights

Enable in Dashboard > Speed Insights:
- Core Web Vitals
- Performance score
- Recommendations

### Logs

View deployment logs:
- Dashboard > Deployments > [Select deployment] > Logs
- Real-time build logs
- Runtime logs
- Error tracking

## Troubleshooting

### Build Failures

**Issue**: Build fails with module not found
```bash
# Solution: Clear cache and redeploy
vercel --prod --force
```

**Issue**: Environment variables not working
- Check variable names (must start with `NEXT_PUBLIC_`)
- Verify variables are set in correct environment
- Redeploy after adding variables

### Performance Issues

**Issue**: Slow page loads
- Enable Vercel Analytics to identify bottlenecks
- Check image optimization settings
- Review bundle size in build logs

**Issue**: High latency
- Verify multi-region deployment is active
- Check DNS configuration
- Enable Edge Functions if needed

### Domain Issues

**Issue**: Domain not resolving
- Verify DNS records are correct
- Wait 24-48 hours for DNS propagation
- Check domain registrar settings

**Issue**: SSL certificate pending
- Wait up to 24 hours for provisioning
- Verify domain ownership
- Check DNS CAA records

## CI/CD Integration

### GitHub Actions

Workflow already configured in `.github/workflows/vercel-deploy.yml`:

```yaml
name: Vercel Frontend Deployment

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Vercel CLI
        run: npm install --global vercel@latest
      - name: Pull Vercel Environment
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
        working-directory: ./frontend
      - name: Build Project
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
        working-directory: ./frontend
      - name: Deploy to Vercel
        run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
        working-directory: ./frontend
```

### Required GitHub Secrets

Add these secrets in GitHub repository settings:

1. **VERCEL_TOKEN**: Your Vercel access token
   - Get from: https://vercel.com/account/tokens
   - Value: `[Your Vercel token]`

2. **VERCEL_ORG_ID**: Your Vercel organization ID
   - Get from: Vercel Dashboard > Settings > General
   - Value: `[Your org ID]`

3. **VERCEL_PROJECT_ID**: Your project ID
   - Get from: Project Settings > General
   - Value: `[Your project ID]`

## Production Checklist

Before going live:

- [ ] Custom domain configured and verified
- [ ] SSL certificate active
- [ ] Environment variables set correctly
- [ ] Analytics enabled
- [ ] Error tracking configured
- [ ] Performance monitoring active
- [ ] GitHub integration working
- [ ] Preview deployments tested
- [ ] Production deployment successful
- [ ] DNS propagated (24-48 hours)
- [ ] All pages loading correctly
- [ ] API endpoints responding
- [ ] Authentication working
- [ ] Dark mode functioning
- [ ] Mobile responsive
- [ ] SEO metadata correct
- [ ] Security headers active
- [ ] CORS configured properly

## Post-Deployment

### Verification Steps

1. **Test Homepage**
   - Visit: https://agentic.bizbot.store
   - Verify hero section loads
   - Check navigation works
   - Test dark mode toggle

2. **Test Agent Marketplace**
   - Visit: https://agentic.bizbot.store/agents
   - Verify agents load
   - Test search and filters
   - Click through to agent details

3. **Test Playground**
   - Visit: https://agentic.bizbot.store/playground
   - Test mock mode execution
   - Test live mode (if API is ready)
   - Verify WebSocket connections

4. **Test Authentication**
   - Visit: https://agentic.bizbot.store/login
   - Test login flow
   - Test signup flow
   - Verify redirects work

5. **Test Dashboard**
   - Visit: https://agentic.bizbot.store/dashboard
   - Verify charts render
   - Check real-time updates
   - Test data refresh

### Performance Verification

Run Lighthouse audit:
```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run audit
lighthouse https://agentic.bizbot.store --view
```

Target scores:
- Performance: 90+
- Accessibility: 95+
- Best Practices: 95+
- SEO: 95+

### Monitoring Setup

1. **Vercel Analytics**
   - Enable in dashboard
   - Set up alerts for errors
   - Configure performance budgets

2. **External Monitoring**
   - Set up UptimeRobot or Pingdom
   - Configure status page
   - Set up alert notifications

3. **Error Tracking**
   - Integrate Sentry (optional)
   - Configure error alerts
   - Set up error grouping

## Scaling Considerations

### Traffic Scaling

Vercel automatically scales:
- Serverless functions scale to zero
- Edge network handles global traffic
- No configuration needed

### Cost Optimization

Monitor usage in Dashboard > Usage:
- Function invocations
- Bandwidth usage
- Build minutes
- Team seats

### Performance Optimization

As traffic grows:
- Enable Edge Functions for dynamic content
- Implement ISR (Incremental Static Regeneration)
- Use Edge Middleware for auth
- Optimize images and assets
- Implement caching strategies

## Support

### Vercel Support

- Documentation: https://vercel.com/docs
- Community: https://github.com/vercel/vercel/discussions
- Support: support@vercel.com

### Project Support

- Repository: https://github.com/seanebones-lang/AGENTICteam
- Issues: https://github.com/seanebones-lang/AGENTICteam/issues
- Contact: https://bizbot.store

## Next Steps

After successful deployment:

1. **Backend Deployment**
   - Deploy FastAPI backend to cloud provider
   - Configure API endpoints
   - Set up database connections
   - Enable CORS for frontend domain

2. **Integration Testing**
   - Test frontend-backend integration
   - Verify WebSocket connections
   - Test authentication flow
   - Validate API responses

3. **Production Launch**
   - Announce launch
   - Monitor performance
   - Gather user feedback
   - Iterate and improve

---

**Deployment Status**: Ready for Production

**Last Updated**: 2025-10-21

**Maintained By**: Sean McDonnell (https://bizbot.store)
