#!/bin/bash

# Unified Data Dashboard System - Start Script
# This script starts the complete system with Apache Superset integration

set -e

echo "=========================================="
echo "Unified Data Dashboard System (UDDS)"
echo "With Apache Superset Integration"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure it:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Check Docker Compose (try both docker-compose and docker compose)
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found!"
    echo "Please install Docker Compose:"
    echo "  https://docs.docker.com/compose/install/"
    exit 1
fi

# Determine which command to use
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    DOCKER_COMPOSE_CMD="docker compose"
fi

echo "✅ Docker Compose found (using: $DOCKER_COMPOSE_CMD)"

# Check Docker daemon
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon not running!"
    echo "Please start Docker daemon first."
    exit 1
fi

echo "✅ Docker daemon is running"

# Pull latest images
echo "📦 Pulling latest Docker images..."
$DOCKER_COMPOSE_CMD pull

# Build and start services
echo "🚀 Starting services..."
$DOCKER_COMPOSE_CMD up -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Checking service status..."
$DOCKER_COMPOSE_CMD ps

echo ""
echo "=========================================="
echo "✅ System started successfully!"
echo "=========================================="
echo ""
echo "Access the following services:"
echo ""
echo "📊 Frontend (React):"
echo "  http://localhost:3000"
echo ""
echo "🔧 Backend API:"
echo "  http://localhost:8000/api/v1"
echo "  Documentation: http://localhost:8000/docs"
echo ""
echo "🎯 Apache Superset (Primary Analytics Tool):"
echo "  http://localhost:8088"
echo "  Login: admin"
echo "  Password: admin"
echo ""
echo "🗄️ PostgreSQL:"
echo "  localhost:5432"
echo "  Database: udds"
echo "  User: udds"
echo ""
echo "🔴 Redis:"
echo "  localhost:6379"
echo ""
echo "=========================================="
echo "Useful commands:"
echo "  $DOCKER_COMPOSE_CMD logs -f [service]  # View logs"
echo "  $DOCKER_COMPOSE_CMD ps                 # Check status"
echo "  $DOCKER_COMPOSE_CMD down               # Stop services"
echo "  $DOCKER_COMPOSE_CMD restart [service]  # Restart service"
echo "=========================================="

# Check Superset health
echo ""
echo "⏳ Checking Superset health..."
sleep 30

if curl -s -f http://localhost:8088/health > /dev/null; then
    echo "✅ Superset is healthy and running"
else
    echo "⚠️  Superset health check failed, but may still be starting"
    echo "   Check logs: $DOCKER_COMPOSE_CMD logs -f superset"
fi

echo ""
echo "🎉 System is ready! Open your browser to start using UDDS."