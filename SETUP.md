# Agent Marketplace Platform - Setup Guide

## Phase 1 Implementation Complete 

This guide will help you set up and test the Agent Marketplace Platform Phase 1 implementation.

## What's Included

### Backend Infrastructure
-  FastAPI 0.115+ application with async support
-  PostgreSQL 16 database with SQLAlchemy models
-  Redis 7 for caching and queuing
-  Qdrant 1.11+ vector database for RAG
-  OpenTelemetry instrumentation
-  Docker and Docker Compose configuration

### Core Agent Engine
-  Unified execution engine supporting LangGraph and CrewAI
-  Async task execution with timeout handling
-  Error recovery and retry logic
-  Cost tracking and usage metering

### Pre-Built Agent Packages (10 Total)

**Customer Support Suite:**
1. Ticket Resolver - Autonomous ticket triage and resolution
2. Knowledge Base Agent - RAG-powered documentation search
3. Escalation Manager - Smart routing to human agents

**Operations Automation:**
4. Data Processor - ETL pipeline automation
5. Report Generator - Automated analytics and insights
6. Workflow Orchestrator - Multi-step business process automation

**IT/DevOps:**
7. Incident Responder - Alert analysis and remediation
8. Deployment Agent - CI/CD pipeline management

**Compliance/Security:**
9. Audit Agent - Log analysis and compliance reporting
10. Security Scanner - Vulnerability detection and patching

### API Endpoints
-  `GET /api/v1/packages` - List all agent packages
-  `GET /api/v1/packages/{id}` - Get package details
-  `POST /api/v1/packages/{id}/execute` - Execute agent task
-  `GET /api/v1/categories` - List categories
-  `GET /api/v1/health` - Health check

## Prerequisites

### Required
- Docker Desktop (latest version)
- Docker Compose v2+
- At least one LLM API key (OpenAI, Anthropic, or Groq)

### Optional (for local development)
- Python 3.11+
- pip or poetry
- PostgreSQL client tools

## Installation Steps

### 1. Clone and Navigate

```bash
cd /Users/seanmcdonnell/Desktop/Agentic
```

### 2. Configure Environment Variables

```bash
# Edit .env file with your API keys
nano .env

# Required: Add at least one LLM API key
OPENAI_API_KEY=sk-your-actual-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
# OR
GROQ_API_KEY=gsk_your-actual-key-here
```

### 3. Start the Platform

**Option A: Using the quick start script (recommended)**
```bash
./start.sh
```

**Option B: Manual Docker Compose**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
```

### 4. Verify Installation

```bash
# Check health
curl http://localhost:8000/api/v1/health

# Expected response:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "timestamp": "2025-10-20T...",
#   "services": {
#     "database": "healthy",
#     "redis": "healthy",
#     "qdrant": "healthy"
#   }
# }
```

## Testing the API

### 1. Access API Documentation

Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 2. List Available Agents

```bash
curl http://localhost:8000/api/v1/packages | jq
```

Expected: List of 10 agent packages with details

### 3. Get Specific Agent Details

```bash
curl http://localhost:8000/api/v1/packages/ticket-resolver | jq
```

### 4. Execute an Agent Task

**Note:** Authentication is currently simplified. In production, you'll need a valid API key.

```bash
# Ticket Resolver Example
curl -X POST "http://localhost:8000/api/v1/packages/ticket-resolver/execute" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d '{
    "task": "Customer reports they cannot login to the dashboard. Error message: Invalid credentials",
    "engine_type": "crewai",
    "timeout": 60
  }' | jq
```

```bash
# Incident Responder Example
curl -X POST "http://localhost:8000/api/v1/packages/incident-responder/execute" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d '{
    "task": "High CPU usage alert on production server. CPU at 95% for 10 minutes.",
    "engine_type": "langgraph"
  }' | jq
```

```bash
# Knowledge Base Search Example
curl -X POST "http://localhost:8000/api/v1/packages/knowledge-base/execute" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d '{
    "task": "How do I reset my password?",
    "engine_type": "langgraph"
  }' | jq
```

### 5. List Categories

```bash
curl http://localhost:8000/api/v1/categories | jq
```

## Database Setup

### Create Test Customer

```bash
# Connect to PostgreSQL
docker exec -it agentic-db psql -U user -d agentic

# Create test customer
INSERT INTO customers (org_name, tier, api_key, email, is_active)
VALUES (
  'Test Organization',
  'gold',
  'test-key',
  'test@example.com',
  1
);

# Exit
\q
```

### View Database Tables

```bash
docker exec -it agentic-db psql -U user -d agentic -c "\dt"
```

Expected tables:
- customers
- agent_packages
- deployments
- usage_logs

## Troubleshooting

### Services Not Starting

```bash
# Check Docker status
docker ps

# View logs
docker-compose logs backend
docker-compose logs db

# Restart services
docker-compose restart
```

### Database Connection Issues

```bash
# Check PostgreSQL is healthy
docker exec -it agentic-db pg_isready -U user -d agentic

# Verify connection string in .env
cat .env | grep DATABASE_URL
```

### API Key Errors

```bash
# Verify API keys are set
docker exec -it agentic-backend env | grep API_KEY

# Check logs for authentication errors
docker-compose logs backend | grep -i "api"
```

### Port Conflicts

If ports 8000, 5432, 6379, or 6333 are already in use:

```bash
# Edit docker-compose.yml to use different ports
# Example: Change "8000:8000" to "8001:8000"
```

## Development Workflow

### Local Python Development

```bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally (without Docker)
uvicorn main:app --reload --port 8000
```

### Adding New Agent Packages

1. Create new file in `backend/agents/packages/`
2. Follow the pattern from existing agents
3. Register in `backend/agents/packages/__init__.py`
4. Add to `AGENT_PACKAGES` dict in `backend/api/v1/marketplace.py`

### Database Migrations (Future)

```bash
# Initialize Alembic (not yet implemented)
cd backend
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head
```

## Performance Testing

### Load Testing with Apache Bench

```bash
# Install Apache Bench
brew install httpd  # macOS

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/api/v1/health/
```

### Monitor Resource Usage

```bash
# Docker stats
docker stats

# Backend container logs
docker-compose logs -f --tail=100 backend
```

## Next Steps

### Phase 2: Custom Agent Builder
- Visual workflow designer with React Flow
- Agent compiler (workflow → LangGraph)
- Tool registry with 50+ pre-built tools
- Testing sandbox

### Phase 3: Frontend Platform
- Next.js 15 application
- Marketing website
- Customer dashboard
- Admin panel

### Phase 4: Production Features
- Authentication system (JWT + OAuth)
- Usage tracking and billing (Stripe)
- Rate limiting per tier
- Agent safety guardrails

## Monitoring and Logs

### View Real-Time Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Database only
docker-compose logs -f db
```

### OpenTelemetry Traces

OpenTelemetry is instrumented but not yet exported. To view traces:

1. Set up Jaeger or Zipkin
2. Configure `OTEL_EXPORTER_OTLP_ENDPOINT` in .env
3. View traces at http://localhost:16686 (Jaeger)

## Stopping the Platform

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Stop specific service
docker-compose stop backend
```

## Support

For issues or questions:
1. Check logs: `docker-compose logs backend`
2. Verify health: `curl http://localhost:8000/api/v1/health`
3. Review this guide
4. Contact the development team

---

**Phase 1 Complete**   
**Ready for Phase 2 Development**   
**Current as of October 20, 2025**

