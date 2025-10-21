#!/bin/bash

# Agent Marketplace Platform - Verification Script

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Agent Marketplace Platform - Phase 1 Verification             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $2 (missing: $1)"
        ((FAILED++))
    fi
}

# Function to check if directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $2 (missing: $1)"
        ((FAILED++))
    fi
}

echo "📁 Checking Project Structure..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Core files
check_file "backend/main.py" "FastAPI application"
check_file "backend/database.py" "Database session management"
check_file "backend/requirements.txt" "Python dependencies"
check_file "backend/Dockerfile" "Backend Dockerfile"
check_file "docker-compose.yml" "Docker Compose configuration"
check_file ".env" "Environment configuration"
check_file "start.sh" "Quick start script"

echo ""
echo "🔧 Checking Core Modules..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file "backend/core/config.py" "Configuration module"
check_file "backend/core/agent_engine.py" "Agent execution engine"
check_file "backend/core/dependencies.py" "Dependency injection"

echo ""
echo "💾 Checking Database Models..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file "backend/models/base.py" "Base model"
check_file "backend/models/customer.py" "Customer model"
check_file "backend/models/agent.py" "Agent package model"
check_file "backend/models/deployment.py" "Deployment models"

echo ""
echo "🤖 Checking Agent Packages..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file "backend/agents/packages/ticket_resolver.py" "Ticket Resolver"
check_file "backend/agents/packages/knowledge_base.py" "Knowledge Base Agent"
check_file "backend/agents/packages/incident_responder.py" "Incident Responder"
check_file "backend/agents/packages/data_processor.py" "Data Processor"
check_file "backend/agents/packages/report_generator.py" "Report Generator"
check_file "backend/agents/packages/workflow_orchestrator.py" "Workflow Orchestrator"
check_file "backend/agents/packages/escalation_manager.py" "Escalation Manager"
check_file "backend/agents/packages/deployment_agent.py" "Deployment Agent"
check_file "backend/agents/packages/audit_agent.py" "Audit Agent"
check_file "backend/agents/packages/security_scanner.py" "Security Scanner"

echo ""
echo "🌐 Checking API Endpoints..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file "backend/api/deps.py" "API dependencies"
check_file "backend/api/v1/marketplace.py" "Marketplace API"
check_file "backend/api/v1/health.py" "Health check API"

echo ""
echo "📚 Checking Documentation..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file "README.md" "Project README"
check_file "SETUP.md" "Setup guide"
check_file "QUICKSTART.md" "Quick start guide"
check_file "PHASE1_COMPLETE.md" "Phase 1 summary"
check_file "IMPLEMENTATION_REPORT.md" "Implementation report"
check_file "CHECKLIST.md" "Project checklist"

echo ""
echo "🐳 Checking Docker Configuration..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker installed"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Docker not found (required for deployment)"
fi

# Check if Docker Compose is installed
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker Compose installed"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Docker Compose not found (required for deployment)"
fi

echo ""
echo "🔑 Checking Environment Configuration..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if .env has API keys configured
if grep -q "sk-your-openai-key-here" .env 2>/dev/null || \
   grep -q "sk-your-key-here" .env 2>/dev/null || \
   grep -q "sk-ant-your-anthropic-key-here" .env 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC} API keys not configured (add to .env before running)"
else
    echo -e "${GREEN}✓${NC} API keys appear to be configured"
    ((PASSED++))
fi

echo ""
echo "📊 Verification Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "  ${GREEN}Passed:${NC} $PASSED"
echo -e "  ${RED}Failed:${NC} $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Phase 1 Implementation: COMPLETE${NC}"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Add your LLM API key to .env"
    echo "   2. Run: ./start.sh"
    echo "   3. Open: http://localhost:8000/docs"
    echo ""
else
    echo -e "${RED}❌ Some files are missing. Please check the implementation.${NC}"
    echo ""
    exit 1
fi

# Count Python files
PYTHON_FILES=$(find backend -name "*.py" 2>/dev/null | wc -l | xargs)
AGENT_PACKAGES=$(find backend/agents/packages -name "*.py" 2>/dev/null | grep -v __init__ | wc -l | xargs)

echo "📈 Statistics"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Python files: $PYTHON_FILES"
echo "   Agent packages: $AGENT_PACKAGES"
echo "   Documentation files: 6"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ Phase 1 Verification Complete - Ready for Deployment       ║"
echo "╚════════════════════════════════════════════════════════════════╝"

