# Vercel Deployment Guide
## Agent Marketplace Platform - Frontend Deployment

**Version**: 2.1.0  
**Date**: October 21, 2025  
**Platform**: Vercel (Next.js)

---

## Quick Start

### Prerequisites

1. **Vercel Account**
   - Sign up at https://vercel.com
   - Install Vercel CLI: `npm install -g vercel`

2. **GitHub Repository**
   - Repository: https://github.com/seanebones-lang/AGENTICteam
   - Access token configured

3. **Backend API**
   - Backend deployed and accessible
   - API URL available
   - WebSocket URL available

---

## Deployment Methods

### Method 1: Vercel CLI (Recommended)

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Login to Vercel
vercel login

# 3. Link to Vercel project (first time only)
vercel link

# 4. Set environment variables
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://api.yourdomain.com

vercel env add NEXT_PUBLIC_WS_URL production
# Enter: wss://api.yourdomain.com

vercel env add NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY production
# Enter: pk_live_...

# 5. Deploy to production
vercel --prod
```

### Method 2: GitHub Integration (Automated)

```bash
# 1. Push to GitHub (already done)
git push origin main

# 2. Connect GitHub repository to Vercel:
#    - Go to https://vercel.com/new
#    - Import your GitHub repository
#    - Select "frontend" as root directory
#    - Configure environment variables
#    - Deploy

# 3. Automatic deployments on push
#    - Main branch → Production
#    - Other branches → Preview
```

### Method 3: Vercel Dashboard (Manual)

1. Go to https://vercel.com/new
2. Import Git Repository
3. Select: `seanebones-lang/AGENTICteam`
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
5. Add Environment Variables (see below)
6. Click "Deploy"

---

## Environment Variables

### Required Variables

Add these in Vercel Dashboard → Settings → Environment Variables:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com

# Stripe Configuration
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...

# Optional: Analytics
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_SENTRY_DSN=https://...
```

### Setting via CLI

```bash
# Production environment
vercel env add NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_WS_URL production
vercel env add NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY production

# Preview environment
vercel env add NEXT_PUBLIC_API_URL preview
vercel env add NEXT_PUBLIC_WS_URL preview
vercel env add NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY preview

# Development environment
vercel env add NEXT_PUBLIC_API_URL development
vercel env add NEXT_PUBLIC_WS_URL development
vercel env add NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY development
```

---

## GitHub Actions Setup

### Configure Secrets

Go to GitHub Repository → Settings → Secrets and variables → Actions

Add the following secrets:

```bash
# GitHub Token
GH_TOKEN=<your-github-token>

# Vercel Credentials
VERCEL_TOKEN=<your-vercel-token>
VERCEL_ORG_ID=<your-org-id>
VERCEL_PROJECT_ID=<your-project-id>
```

### Get Vercel Credentials

```bash
# 1. Get Vercel Token
# Go to: https://vercel.com/account/tokens
# Create new token with full access

# 2. Get Organization ID
vercel whoami
# Copy the "id" field

# 3. Get Project ID
cd frontend
vercel link
cat .vercel/project.json
# Copy "projectId"
```

### Workflow File

The workflow file is already created at:
`.github/workflows/vercel-deploy.yml`

It will automatically:
- Deploy to production on push to `main`
- Deploy preview on pull requests
- Run build checks
- Install dependencies

---

## Domain Configuration

### Custom Domain Setup

1. **Add Domain in Vercel**
   ```bash
   vercel domains add yourdomain.com
   ```

2. **Configure DNS**
   
   Add these records to your DNS provider:
   
   ```
   Type: A
   Name: @
   Value: 76.76.21.21
   
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```

3. **SSL Certificate**
   - Automatically provisioned by Vercel
   - Let's Encrypt certificate
   - Auto-renewal enabled

### Subdomain for API

```
Type: A
Name: api
Value: <your-backend-ip>

Type: CNAME
Name: api
Value: <your-backend-domain>
```

---

## Build Configuration

### Next.js Configuration

File: `frontend/next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL,
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY,
  },
  
  // Image optimization
  images: {
    domains: ['yourdomain.com'],
    formats: ['image/avif', 'image/webp'],
  },
  
  // Headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ];
  },
  
  // Redirects
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/',
        permanent: true,
      },
    ];
  },
  
  // Rewrites for API proxy
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

### Vercel Configuration

File: `vercel.json` (root level)

```json
{
  "version": 2,
  "name": "agent-marketplace",
  "framework": "nextjs",
  "buildCommand": "cd frontend && npm run build",
  "devCommand": "cd frontend && npm run dev",
  "installCommand": "cd frontend && npm install",
  "outputDirectory": "frontend/.next",
  "regions": ["iad1"],
  "functions": {
    "frontend/**/*.{js,ts,tsx}": {
      "maxDuration": 30
    }
  }
}
```

---

## Deployment Checklist

### Pre-Deployment

- [x] Frontend code complete
- [x] Environment variables configured
- [x] Backend API deployed and accessible
- [x] Domain configured
- [x] SSL certificate ready
- [x] GitHub repository connected

### Deployment Steps

```bash
# 1. Ensure all changes are committed
git status
git add -A
git commit -m "Prepare for Vercel deployment"
git push origin main

# 2. Deploy via CLI
cd frontend
vercel --prod

# 3. Verify deployment
curl https://yourdomain.com
curl https://yourdomain.com/api/health

# 4. Test functionality
# - Open browser to https://yourdomain.com
# - Test authentication
# - Test agent execution
# - Test WebSocket connection
```

### Post-Deployment

- [ ] Verify homepage loads
- [ ] Test API connectivity
- [ ] Test WebSocket connection
- [ ] Verify authentication flow
- [ ] Test agent execution
- [ ] Check analytics integration
- [ ] Monitor error rates
- [ ] Set up alerts

---

## Monitoring & Analytics

### Vercel Analytics

Enable in Vercel Dashboard:
1. Go to Project → Analytics
2. Enable Web Analytics
3. Add to `frontend/src/app/layout.tsx`:

```typescript
import { Analytics } from '@vercel/analytics/react';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

### Performance Monitoring

```typescript
// frontend/src/lib/monitoring.ts
export function reportWebVitals(metric: any) {
  console.log(metric);
  
  // Send to analytics service
  if (process.env.NODE_ENV === 'production') {
    // Send to your analytics endpoint
    fetch('/api/analytics/vitals', {
      method: 'POST',
      body: JSON.stringify(metric),
    });
  }
}
```

### Error Tracking

Install Sentry:

```bash
cd frontend
npm install @sentry/nextjs
```

Configure:

```javascript
// sentry.client.config.js
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 1.0,
});
```

---

## Troubleshooting

### Build Failures

```bash
# Check build logs
vercel logs <deployment-url>

# Test build locally
cd frontend
npm run build

# Clear cache and rebuild
rm -rf .next node_modules
npm install
npm run build
```

### Environment Variable Issues

```bash
# List all environment variables
vercel env ls

# Pull environment variables locally
vercel env pull .env.local

# Verify variables in build
vercel logs <deployment-url> | grep "NEXT_PUBLIC"
```

### API Connection Issues

```bash
# Test API from Vercel
curl https://yourdomain.com/api/health

# Check CORS headers
curl -I https://api.yourdomain.com/api/health

# Verify WebSocket connection
wscat -c wss://api.yourdomain.com/api/v1/ws/test
```

### Performance Issues

```bash
# Analyze bundle size
cd frontend
npm run build
npx @next/bundle-analyzer

# Check lighthouse score
lighthouse https://yourdomain.com --view

# Monitor Core Web Vitals
# Go to Vercel Dashboard → Analytics → Web Vitals
```

---

## Scaling & Optimization

### Vercel Pro Features

- **Edge Functions**: Deploy functions closer to users
- **Edge Middleware**: Run code before requests reach your app
- **Image Optimization**: Automatic image optimization
- **Analytics**: Real-time analytics and insights
- **Monitoring**: Performance and error monitoring

### Performance Optimization

1. **Enable Edge Functions**
   ```typescript
   // frontend/src/middleware.ts
   export const config = {
     matcher: '/api/:path*',
   };
   
   export function middleware(request: Request) {
     // Edge middleware logic
   }
   ```

2. **Optimize Images**
   ```typescript
   import Image from 'next/image';
   
   <Image
     src="/logo.png"
     alt="Logo"
     width={200}
     height={50}
     priority
   />
   ```

3. **Enable ISR (Incremental Static Regeneration)**
   ```typescript
   export async function generateStaticParams() {
     // Generate static pages
   }
   
   export const revalidate = 3600; // Revalidate every hour
   ```

---

## Security Best Practices

### Content Security Policy

```typescript
// next.config.js
const ContentSecurityPolicy = `
  default-src 'self';
  script-src 'self' 'unsafe-eval' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self';
  connect-src 'self' https://api.yourdomain.com wss://api.yourdomain.com;
`;

module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: ContentSecurityPolicy.replace(/\s{2,}/g, ' ').trim(),
          },
        ],
      },
    ];
  },
};
```

### Rate Limiting

Use Vercel Edge Middleware:

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const rateLimiter = new Map();

export function middleware(request: NextRequest) {
  const ip = request.ip || 'anonymous';
  const limit = rateLimiter.get(ip) || 0;
  
  if (limit > 100) {
    return new NextResponse('Too Many Requests', { status: 429 });
  }
  
  rateLimiter.set(ip, limit + 1);
  
  // Reset after 1 minute
  setTimeout(() => rateLimiter.delete(ip), 60000);
  
  return NextResponse.next();
}
```

---

## Cost Estimation

### Vercel Pricing Tiers

| Tier | Price | Bandwidth | Build Minutes | Team Members |
|------|-------|-----------|---------------|--------------|
| Hobby | Free | 100 GB | 100 min | 1 |
| Pro | $20/mo | 1 TB | 400 min | Unlimited |
| Enterprise | Custom | Custom | Custom | Custom |

### Estimated Costs

For **10,000 monthly active users**:

- **Bandwidth**: ~500 GB/month
- **Build Minutes**: ~200 min/month
- **Edge Requests**: ~1M/month
- **Estimated Cost**: $20-40/month (Pro tier)

---

## Support & Resources

### Documentation

- Vercel Docs: https://vercel.com/docs
- Next.js Docs: https://nextjs.org/docs
- Deployment Guide: https://vercel.com/docs/deployments

### Community

- Vercel Discord: https://vercel.com/discord
- Next.js Discord: https://nextjs.org/discord
- GitHub Discussions: https://github.com/vercel/next.js/discussions

### Contact

- **Project Owner**: Sean McDonnell
- **Website**: https://bizbot.store
- **Repository**: https://github.com/seanebones-lang/AGENTICteam

---

## Conclusion

Your Agent Marketplace Platform frontend is now ready for Vercel deployment with:

✅ Automated CI/CD pipeline  
✅ Environment configuration  
✅ Custom domain support  
✅ SSL certificates  
✅ Performance optimization  
✅ Security hardening  
✅ Monitoring & analytics  
✅ Scalable infrastructure

**Next Steps**:
1. Configure Vercel secrets in GitHub
2. Deploy via GitHub Actions or Vercel CLI
3. Configure custom domain
4. Enable monitoring
5. Go live! 🚀

---

**Deployment Status**: Ready for Production  
**Last Updated**: October 21, 2025  
**Version**: 2.1.0

