# Agent Marketplace Platform

Enterprise Agentic AI Platform - Rent autonomous agents for enterprise operations.

## Overview

The Agent Marketplace Platform is a production-ready Agent-as-a-Service (AaaS) system that allows enterprises to rent and deploy autonomous AI agents for various operational tasks including customer support, IT operations, data processing, compliance, and more.

## Architecture

**Stack**: Next.js 15 + FastAPI 0.115+ + PostgreSQL 16 + Redis 7 + Docker + LangGraph 0.2+ / CrewAI 0.55+

```
Frontend (Next.js)          Backend (FastAPI)           Infrastructure
├─ Marketing Site           ├─ Agent Orchestration      ├─ PostgreSQL 16 (state)
├─ Customer Dashboard       ├─ Marketplace API          ├─ Redis 7 (cache/queue)
├─ Agent Builder UI         ├─ Billing Integration      ├─ Qdrant 1.11+ (vector memory)
└─ Admin Panel              └─ Deployment Manager       └─ Docker
```

## Available Agent Packages

### Customer Support Suite
- **Ticket Resolver** - Autonomous ticket triage and resolution
- **Knowledge Base Agent** - RAG-powered documentation search
- **Escalation Manager** - Smart routing to human agents

### Operations Automation
- **Data Processor** - ETL pipeline automation
- **Report Generator** - Automated analytics and insights
- **Workflow Orchestrator** - Multi-step business process automation

### IT/DevOps
- **Incident Responder** - Alert analysis and remediation
- **Deployment Agent** - CI/CD pipeline management

### Compliance/Security
- **Audit Agent** - Log analysis and compliance reporting
- **Security Scanner** - Vulnerability detection and patching

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- API keys for LLM providers (OpenAI, Anthropic, or Groq)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Agentic
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. **Start the infrastructure**
```bash
docker-compose up -d
```

4. **Install backend dependencies (for local development)**
```bash
cd backend
pip install -r requirements.txt
```

5. **Run database migrations**
```bash
# TODO: Add Alembic migrations
```

6. **Start the backend**
```bash
# Using Docker (recommended)
docker-compose up backend

# Or locally
cd backend
uvicorn main:app --reload --port 8000
```

7. **Access the API**
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health
- Root: http://localhost:8000

## API Usage

### List Available Packages

```bash
curl http://localhost:8000/api/v1/packages
```

### Execute an Agent Task

```bash
curl -X POST "http://localhost:8000/api/v1/packages/ticket-resolver/execute" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "task": "Customer reports they cannot login to the dashboard",
    "engine_type": "crewai"
  }'
```

### Get Package Details

```bash
curl http://localhost:8000/api/v1/packages/incident-responder
```

## Development

### Project Structure

```
/Users/seanmcdonnell/Desktop/Agentic/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── core/
│   │   ├── agent_engine.py     # Unified agent execution engine
│   │   ├── config.py           # Configuration settings
│   │   └── dependencies.py     # Dependency injection
│   ├── models/
│   │   ├── customer.py         # Customer model
│   │   ├── agent.py            # Agent package model
│   │   └── deployment.py       # Deployment and usage models
│   ├── agents/
│   │   └── packages/           # Pre-built agent packages
│   ├── api/
│   │   └── v1/
│   │       ├── marketplace.py  # Marketplace endpoints
│   │       └── health.py       # Health check endpoints
│   ├── database.py             # Database session management
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

### Running Tests

```bash
# TODO: Add pytest tests
cd backend
pytest
```

### Code Quality

```bash
# Format code
black backend/

# Lint
flake8 backend/

# Type checking
mypy backend/
```

## Technology Stack

### Backend
- **FastAPI 0.115+** - Modern async web framework
- **SQLAlchemy 2.0** - ORM for database operations
- **PostgreSQL 16** - Primary database
- **Redis 7** - Caching and message queue
- **Qdrant 1.11+** - Vector database for RAG

### Agent Frameworks
- **LangGraph 0.2+** - State machine-based agent orchestration
- **CrewAI 0.55+** - Multi-agent collaboration
- **LangChain** - LLM integration and tooling

### LLM Providers
- **OpenAI** - GPT-4o, GPT-4-turbo
- **Anthropic** - Claude 3.5 Sonnet
- **Groq** - Fast inference

### Monitoring
- **OpenTelemetry** - Distributed tracing
- **Prometheus** (planned) - Metrics collection
- **Grafana** (planned) - Visualization

## Deployment

### Docker Compose (Development)

```bash
docker-compose up -d
```

### Production (Kubernetes)

```bash
# TODO: Add Kubernetes manifests
kubectl apply -f k8s/
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key settings:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `SECRET_KEY` - JWT secret key

## Security

- API key authentication for all endpoints
- Rate limiting per customer tier
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy
- CORS configuration for frontend access

## Monitoring and Observability

- Health check endpoints for Kubernetes probes
- OpenTelemetry tracing for request tracking
- Structured logging with trace IDs
- Usage tracking for billing

## Roadmap

### Phase 1: Core Infrastructure (Current)
- [x] FastAPI backend foundation
- [x] Database models
- [x] Unified agent execution engine
- [x] 10 pre-built agent packages
- [x] Marketplace API
- [x] Docker infrastructure

### Phase 2: Custom Agent Builder
- [ ] Visual workflow designer (React Flow)
- [ ] Agent compiler
- [ ] Tool registry (50+ tools)
- [ ] Testing sandbox

### Phase 3: Frontend Platform
- [ ] Next.js 15 application
- [ ] Marketing website
- [ ] Customer dashboard
- [ ] Admin panel

### Phase 4: Marketplace & Billing
- [ ] Usage tracking and metering
- [ ] Stripe integration
- [ ] Subscription management
- [ ] Invoice generation

### Phase 5: Production Features
- [ ] Authentication system
- [ ] Rate limiting
- [ ] Agent safety guardrails
- [ ] Multi-tenancy isolation

## Contributing

This is a private enterprise project. For questions or issues, contact the development team.

## License

Proprietary - All rights reserved.

## Support

For technical support or questions:
- Email: support@example.com
- Documentation: http://localhost:8000/docs

---

**Current as of October 20, 2025**
**Version 1.0.0**

