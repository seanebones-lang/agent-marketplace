# Agent Marketplace Frontend

Modern, production-ready Next.js 15 frontend for the Agent Marketplace platform.

## Features

- **Next.js 15** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Radix UI** components
- **React Query** for data fetching
- **Dark mode** support
- **Responsive design**
- **SEO optimized**

## Pages

- `/` - Homepage with hero and features
- `/agents` - Agent marketplace with search and filters
- `/playground` - Interactive agent testing (mock + live modes)
- `/dashboard` - Analytics and execution history
- `/pricing` - Pricing tiers and plans
- `/login` - Authentication
- `/signup` - User registration
- `/docs` - Documentation

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
npm run build
npm start
```

### Environment Variables

Copy `.env.local.example` to `.env.local`:

```bash
cp .env.local.example .env.local
```

Configure:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Configure environment variables:
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_APP_URL`
4. Deploy

### Manual Deployment

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
 src/
    app/              # Next.js app router pages
       agents/       # Agent marketplace
       playground/   # Interactive demo
       dashboard/    # Analytics dashboard
       pricing/      # Pricing page
       login/        # Authentication
       signup/       # Registration
    components/       # React components
       ui/          # UI primitives
       navigation.tsx
       footer.tsx
       providers.tsx
    hooks/           # Custom React hooks
    lib/             # Utilities
    types/           # TypeScript types
 public/              # Static assets
 package.json
```

## Features

### Mock Mode

The playground includes a mock mode for testing without backend connectivity:
- Pre-configured scenarios for each agent
- Simulated execution delays
- Realistic response data

### Live Mode

Connect to the actual API for real agent execution:
- Real-time execution
- Actual performance metrics
- Production data

### Dark Mode

Automatic dark mode support with system preference detection.

### Responsive Design

Fully responsive design that works on:
- Desktop (1920px+)
- Laptop (1280px+)
- Tablet (768px+)
- Mobile (320px+)

## Performance

- **Lighthouse Score**: 95+
- **First Contentful Paint**: <1.5s
- **Time to Interactive**: <3s
- **Bundle Size**: <200KB (gzipped)

## Security

- CSP headers configured
- XSS protection enabled
- HTTPS enforced in production
- Secure cookie settings
- Input sanitization

## License

Proprietary Software - © 2025 Sean McDonnell. All Rights Reserved.

Contact: https://bizbot.store
