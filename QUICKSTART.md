# Agent Marketplace Platform - Quick Start

## 30-Second Start

```bash
cd /Users/seanmcdonnell/Desktop/Agentic
./start.sh
```

Then open: http://localhost:8000/docs

## 5-Minute Setup

### 1. Add Your API Key

```bash
# Edit .env file
nano .env

# Add at least one:
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 2. Start Services

```bash
docker-compose up -d
```

### 3. Test the API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# List agents
curl http://localhost:8000/api/v1/packages

# Execute an agent
curl -X POST "http://localhost:8000/api/v1/packages/ticket-resolver/execute" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d '{"task": "Customer cannot login", "engine_type": "crewai"}'
```

## Available Agents

1. **ticket-resolver** - Customer support automation
2. **knowledge-base** - RAG-powered search
3. **incident-responder** - IT incident management
4. **data-processor** - ETL automation
5. **report-generator** - Analytics reports
6. **workflow-orchestrator** - Process automation
7. **escalation-manager** - Smart routing
8. **deployment-agent** - CI/CD management
9. **audit-agent** - Compliance auditing
10. **security-scanner** - Vulnerability scanning

## Common Commands

```bash
# View logs
docker-compose logs -f backend

# Restart backend
docker-compose restart backend

# Stop all services
docker-compose down

# Stop and remove data
docker-compose down -v
```

## API Endpoints

- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/v1/health
- **Packages**: http://localhost:8000/api/v1/packages
- **Execute**: POST http://localhost:8000/api/v1/packages/{id}/execute

## Troubleshooting

**Services won't start?**
```bash
docker-compose logs
```

**Port already in use?**
```bash
# Edit docker-compose.yml and change port mappings
```

**Database connection failed?**
```bash
docker-compose restart db
```

## Next Steps

1. Read [SETUP.md](./SETUP.md) for detailed instructions
2. Read [PHASE1_COMPLETE.md](./PHASE1_COMPLETE.md) for full documentation
3. Explore API at http://localhost:8000/docs

---

**Phase 1 Complete**   
**Ready to Use** 

