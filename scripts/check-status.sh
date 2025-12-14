#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏥 HealthGuard AI - System Status Check${NC}"
echo "========================================"
echo ""

# Check Docker containers
echo -e "${BLUE}Docker Containers:${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}Service Health Checks:${NC}"
echo ""

# Check MCP Server
echo -n "MCP Server (http://localhost:3000): "
if curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${RED}✗ DOWN${NC}"
fi

# Check Backend API
echo -n "Backend API (http://localhost:8000): "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${RED}✗ DOWN${NC}"
fi

# Check Frontend
echo -n "Frontend (http://localhost:5173): "
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${RED}✗ DOWN${NC}"
fi

# Check PostgreSQL
echo -n "PostgreSQL (localhost:5432): "
if docker exec healthguard-ai-postgres-1 pg_isready -U healthguard > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${RED}✗ DOWN${NC}"
fi

# Check Redis
echo -n "Redis (localhost:6379): "
if docker exec healthguard-ai-redis-1 redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${RED}✗ DOWN${NC}"
fi

# Check Prometheus
echo -n "Prometheus (http://localhost:9090): "
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${RED}✗ DOWN${NC}"
fi

# Check Grafana
echo -n "Grafana (http://localhost:3001): "
if curl -s http://localhost:3001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HEALTHY${NC}"
else
    echo -e "${RED}✗ DOWN${NC}"
fi

echo ""
echo -e "${BLUE}Quick Links:${NC}"
echo "  Frontend Dashboard: http://localhost:5173"
echo "  Backend API: http://localhost:8000/docs"
echo "  MCP Server: http://localhost:3000/health"
echo "  Grafana: http://localhost:3001 (admin/admin)"
echo "  Prometheus: http://localhost:9090"
echo "  Kibana: http://localhost:5601"
echo ""
