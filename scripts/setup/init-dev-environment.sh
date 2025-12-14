#!/bin/bash
# Complete initialization script for HealthGuard AI

set -e  # Exit on error

echo "🏥 HealthGuard AI - Complete System Initialization"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "\n${BLUE}1. Checking prerequisites...${NC}"

command -v docker >/dev/null 2>&1 || { echo "❌ Docker not found. Please install Docker."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose not found. Please install Docker Compose."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "⚠️  Node.js not found. Will run in Docker only."; }
command -v python3 >/dev/null 2>&1 || { echo "⚠️  Python not found. Will run in Docker only."; }

echo -e "${GREEN}✓ Prerequisites checked${NC}"

# Create necessary directories
echo -e "\n${BLUE}2. Creating directory structure...${NC}"

# MCP Server
mkdir -p mcp-server/{src,logs}
mkdir -p mcp-server/src/{config,core,agents,tools,memory,policies,reasoning,routes,utils}

# Backend
mkdir -p backend/{api/v1,core,db,events,services,integrations,workers,logs}

# Frontend
mkdir -p frontend/{apps/command_center,packages}

# ML
mkdir -p ml/{datasets,models,pipelines,experiments,inference,explainability}

# Infrastructure
mkdir -p infrastructure/{terraform,kubernetes,monitoring/{prometheus,grafana},logging,security,ci_cd}

# Testing
mkdir -p testing/{unit,integration,e2e,load,chaos,security,compliance}

# Docs
mkdir -p docs/{architecture,api,runbooks,training}

# Compliance
mkdir -p compliance/{regulatory,ethics,legal,audit}

# Scripts
mkdir -p scripts/{setup,deployment,maintenance,emergency}

# Logs
mkdir -p logs

echo -e "${GREEN}✓ Directory structure created${NC}"

# Create environment file
echo -e "\n${BLUE}3. Setting up environment variables...${NC}"

if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠️  Please review and update .env file with your configuration${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Build and start infrastructure
echo -e "\n${BLUE}4. Starting infrastructure services...${NC}"

echo "Starting databases and message queues..."
docker-compose up -d postgres redis kafka zookeeper qdrant neo4j

echo "Waiting for services to be healthy..."
sleep 15

# Check service health
echo -e "\n${BLUE}5. Checking service health...${NC}"

docker-compose ps

echo -e "${GREEN}✓ Infrastructure services started${NC}"

# Initialize databases
echo -e "\n${BLUE}6. Initializing databases...${NC}"

# Wait for Postgres
until docker-compose exec -T postgres pg_isready -U healthguard; do
  echo "Waiting for postgres..."
  sleep 2
done

echo -e "${GREEN}✓ Databases ready${NC}"

# Build application services
echo -e "\n${BLUE}7. Building application services...${NC}"

echo "Building MCP Server..."
docker-compose build mcp-server

echo "Building Backend API..."
docker-compose build backend

echo -e "${GREEN}✓ Application services built${NC}"

# Start application services
echo -e "\n${BLUE}8. Starting application services...${NC}"

docker-compose up -d mcp-server backend

sleep 10

# Verify applications are running
echo -e "\n${BLUE}9. Verifying applications...${NC}"

echo "Checking MCP Server..."
curl -f http://localhost:3000/health || echo "⚠️  MCP Server not responding yet"

echo "Checking Backend API..."
curl -f http://localhost:8000/health || echo "⚠️  Backend API not responding yet"

# Start monitoring services
echo -e "\n${BLUE}10. Starting monitoring services...${NC}"

docker-compose up -d prometheus grafana

echo -e "${GREEN}✓ Monitoring services started${NC}"

# Display service URLs
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 HealthGuard AI is ready!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📊 Service URLs:${NC}"
echo "  • MCP Server:        http://localhost:3000"
echo "  • MCP Health:        http://localhost:3000/health"
echo "  • Backend API:       http://localhost:8000"
echo "  • API Docs:          http://localhost:8000/docs"
echo "  • Prometheus:        http://localhost:9090"
echo "  • Grafana:           http://localhost:3001 (admin/admin)"
echo "  • Neo4j Browser:     http://localhost:7474"
echo ""
echo -e "${BLUE}📦 Databases:${NC}"
echo "  • PostgreSQL:        localhost:5432"
echo "  • Redis:             localhost:6379"
echo "  • Kafka:             localhost:9093"
echo "  • Qdrant:            localhost:6333"
echo "  • Neo4j:             localhost:7687"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "  1. Review logs: docker-compose logs -f"
echo "  2. Access API docs: http://localhost:8000/docs"
echo "  3. Monitor health: http://localhost:3000/health"
echo "  4. View metrics: http://localhost:9090"
echo ""
echo -e "${YELLOW}🛑 To stop all services:${NC}"
echo "  docker-compose down"
echo ""
echo -e "${YELLOW}🔥 To reset everything:${NC}"
echo "  docker-compose down -v  # WARNING: Deletes all data!"
echo ""
