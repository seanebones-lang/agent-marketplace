#!/bin/bash

# Agent Marketplace Platform - Quick Start Script

echo "🚀 Starting Agent Marketplace Platform..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your API keys."
    echo ""
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "📦 Starting infrastructure services..."
docker-compose up -d db redis qdrant

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

echo ""
echo "🔧 Building backend..."
docker-compose build backend

echo ""
echo "🚀 Starting backend..."
docker-compose up -d backend

echo ""
echo "✅ Agent Marketplace Platform is starting!"
echo ""
echo "📍 Services:"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/api/v1/health"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo "   - Qdrant: localhost:6333"
echo ""
echo "📝 View logs:"
echo "   docker-compose logs -f backend"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""

