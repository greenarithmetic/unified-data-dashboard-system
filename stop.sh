#!/bin/bash

# Unified Data Dashboard System - Stop Script

echo "🛑 Stopping Unified Data Dashboard System..."

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found"
    exit 1
fi

# Stop services
docker-compose down

echo ""
echo "✅ Services stopped"
echo ""
echo "📋 To remove all data (WARNING: irreversible):"
echo "   docker-compose down -v"
echo ""
echo "🚀 To start again:"
echo "   ./start.sh"