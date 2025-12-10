#!/bin/bash

# Unified Data Dashboard System - Startup Script
set -e

echo "🚀 Starting Unified Data Dashboard System..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration"
    echo "   nano .env"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Installing..."
    # Try to install docker-compose
    if command -v apt-get &> /dev/null; then
        apt-get update && apt-get install -y docker-compose
    elif command -v yum &> /dev/null; then
        yum install -y docker-compose
    elif command -v apk &> /dev/null; then
        apk add docker-compose
    else
        echo "⚠️  Please install docker-compose manually"
        echo "   https://docs.docker.com/compose/install/"
        exit 1
    fi
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    echo "   https://docs.docker.com/engine/install/"
    exit 1
fi

# Start Docker daemon if not running
if ! docker info &> /dev/null; then
    echo "⚠️  Docker daemon not running. Starting..."
    if command -v systemctl &> /dev/null; then
        sudo systemctl start docker
    elif command -v service &> /dev/null; then
        sudo service docker start
    else
        echo "⚠️  Please start Docker daemon manually"
        exit 1
    fi
    sleep 3
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check services
echo "🔍 Checking services status..."
docker-compose ps

echo ""
echo "✅ Unified Data Dashboard System is starting!"
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
echo "   Status:        docker-compose ps"
echo ""
echo "🔧 Initial setup:"
echo "   1. Open http://localhost:3000"
echo "   2. Configure Google Sheets API credentials"
echo "   3. Edit datasets.json for your data sources"
echo "   4. Check reports.json for custom reports"
echo ""
echo "📝 For detailed setup instructions, see README.md"