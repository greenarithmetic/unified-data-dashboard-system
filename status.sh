#!/bin/bash

# Unified Data Dashboard System - Status Script

echo "🔍 Unified Data Dashboard System Status"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found"
    exit 1
fi

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running"
    echo ""
    docker-compose ps
    echo ""
    echo "📊 Access URLs:"
    echo "   Frontend:      http://localhost:3000"
    echo "   Backend API:   http://localhost:8000"
    echo "   API Docs:      http://localhost:8000/docs"
    echo "   Superset:      http://localhost:8088"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs:     docker-compose logs -f"
    echo "   Stop:          docker-compose down"
    echo "   Restart:       docker-compose restart"
else
    echo "⚠️  Services are not running"
    echo ""
    echo "🚀 To start services:"
    echo "   ./start.sh"
fi