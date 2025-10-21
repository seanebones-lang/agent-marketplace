# Agent Marketplace Frontend

Next.js 15 frontend application for the Agent Marketplace Platform.

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript 5.6
- **Styling**: Tailwind CSS 3.4
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod
- **Icons**: Lucide React
- **Charts**: Recharts

## Getting Started

### Prerequisites

- Node.js 18+ and npm 9+
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.local.example .env.local

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # React components
│   │   ├── ui/          # Reusable UI components
│   │   ├── layout/      # Layout components
│   │   └── features/    # Feature-specific components
│   ├── lib/             # Utility functions
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API services
│   ├── stores/          # Zustand stores
│   ├── types/           # TypeScript types
│   └── styles/          # Global styles
├── public/              # Static assets
└── package.json
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler check

## Features

### Phase 2 (Current)
- [ ] Homepage and marketing pages
- [ ] Agent marketplace browsing
- [ ] Agent detail pages
- [ ] User authentication
- [ ] Dashboard layout

### Phase 3 (Planned)
- [ ] Customer dashboard
- [ ] Agent execution interface
- [ ] Usage analytics
- [ ] Billing management
- [ ] Admin panel

## Development Guidelines

### Code Style

- Use TypeScript for all files
- Follow ESLint and Prettier rules
- Use functional components with hooks
- Prefer composition over inheritance

### Component Structure

```typescript
// components/MyComponent.tsx
import { FC } from 'react';

interface MyComponentProps {
  title: string;
  onAction: () => void;
}

export const MyComponent: FC<MyComponentProps> = ({ title, onAction }) => {
  return (
    <div>
      <h1>{title}</h1>
      <button onClick={onAction}>Action</button>
    </div>
  );
};
```

### API Integration

```typescript
// services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

export const getAgents = async () => {
  const response = await api.get('/api/v1/packages');
  return response.data;
};
```

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```bash
# Build image
docker build -t agent-marketplace-frontend .

# Run container
docker run -p 3000:3000 agent-marketplace-frontend
```

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXT_PUBLIC_APP_NAME` - Application name
- `NEXT_PUBLIC_APP_VERSION` - Application version

## Contributing

See main project README for contribution guidelines.

## License

Proprietary - All rights reserved.

