#!/usr/bin/env bash

# HealthGuard AI - Production Deployment Script
# Supports: AWS, Azure, GCP, Docker, Kubernetes
# Usage: ./deploy.sh [platform] [environment]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PLATFORM="${1:-local}"
ENVIRONMENT="${2:-production}"

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        HealthGuard AI - Production Deployment                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Platform: $PLATFORM"
echo "Environment: $ENVIRONMENT"
echo ""

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
else
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create .env from .env.production template"
    exit 1
fi

# Validate production configuration
validate_production_config() {
    echo -e "${YELLOW}[1/8] Validating production configuration...${NC}"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        # Check critical secrets
        if [ "$JWT_SECRET" = "GENERATE_64_CHAR_RANDOM_STRING" ] || [ -z "$JWT_SECRET" ]; then
            echo -e "${RED}❌ JWT_SECRET not configured!${NC}"
            exit 1
        fi
        
        if [ "$ENCRYPTION_KEY" = "GENERATE_32_CHAR_RANDOM_STRING" ] || [ -z "$ENCRYPTION_KEY" ]; then
            echo -e "${RED}❌ ENCRYPTION_KEY not configured!${NC}"
            exit 1
        fi
        
        if [ "$DATABASE_PASSWORD" = "CHANGE_THIS_IN_PRODUCTION" ] || [ -z "$DATABASE_PASSWORD" ]; then
            echo -e "${RED}❌ DATABASE_PASSWORD not configured!${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✓ Configuration validated${NC}"
}

# Check dependencies
check_dependencies() {
    echo -e "${YELLOW}[2/8] Checking dependencies...${NC}"
    
    local deps=("docker" "docker-compose")
    
    case $PLATFORM in
        aws)
            deps+=("aws")
            ;;
        azure)
            deps+=("az")
            ;;
        gcp)
            deps+=("gcloud")
            ;;
        kubernetes|k8s)
            deps+=("kubectl" "helm")
            ;;
    esac
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            echo -e "${RED}❌ $dep is not installed!${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✓ All dependencies installed${NC}"
}

# Build Docker images
build_images() {
    echo -e "${YELLOW}[3/8] Building Docker images...${NC}"
    
    cd "$PROJECT_ROOT"
    
    # Build backend
    echo "Building backend..."
    docker build -t healthguard-backend:$ENVIRONMENT -f backend/Dockerfile backend/
    
    # Build MCP server
    echo "Building MCP server..."
    docker build -t healthguard-mcp:$ENVIRONMENT -f mcp-server/Dockerfile mcp-server/
    
    # Build frontend
    echo "Building frontend..."
    docker build -t healthguard-frontend:$ENVIRONMENT -f frontend/Dockerfile frontend/
    
    echo -e "${GREEN}✓ Images built successfully${NC}"
}

# Run tests
run_tests() {
    echo -e "${YELLOW}[4/8] Running tests...${NC}"
    
    # Python tests
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    python -m pytest testing/unit/backend/test_smoke.py -v --tb=short
    
    # TypeScript tests
    cd "$PROJECT_ROOT/mcp-server"
    npm test
    
    echo -e "${GREEN}✓ All tests passed${NC}"
}

# Deploy to AWS
deploy_aws() {
    echo -e "${YELLOW}[5/8] Deploying to AWS...${NC}"
    
    # Login to ECR
    aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
    
    # Tag and push images
    for service in backend mcp frontend; do
        docker tag healthguard-$service:$ENVIRONMENT "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/healthguard-$service:latest"
        docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/healthguard-$service:latest"
    done
    
    # Deploy to ECS
    aws ecs update-service --cluster healthguard-production --service healthguard-backend --force-new-deployment
    aws ecs update-service --cluster healthguard-production --service healthguard-mcp --force-new-deployment
    aws ecs update-service --cluster healthguard-production --service healthguard-frontend --force-new-deployment
    
    echo -e "${GREEN}✓ Deployed to AWS ECS${NC}"
}

# Deploy to Azure
deploy_azure() {
    echo -e "${YELLOW}[5/8] Deploying to Azure...${NC}"
    
    # Login to ACR
    az acr login --name healthguard
    
    # Tag and push images
    for service in backend mcp frontend; do
        docker tag healthguard-$service:$ENVIRONMENT healthguard.azurecr.io/$service:latest
        docker push healthguard.azurecr.io/$service:latest
    done
    
    # Deploy to Container Apps
    az containerapp update \\
        --name healthguard-backend \\
        --resource-group healthguard-production \\
        --image healthguard.azurecr.io/backend:latest
    
    az containerapp update \\
        --name healthguard-mcp \\
        --resource-group healthguard-production \\
        --image healthguard.azurecr.io/mcp:latest
    
    az containerapp update \\
        --name healthguard-frontend \\
        --resource-group healthguard-production \\
        --image healthguard.azurecr.io/frontend:latest
    
    echo -e "${GREEN}✓ Deployed to Azure Container Apps${NC}"
}

# Deploy to GCP
deploy_gcp() {
    echo -e "${YELLOW}[5/8] Deploying to GCP...${NC}"
    
    # Configure Docker for GCR
    gcloud auth configure-docker
    
    # Tag and push images
    for service in backend mcp frontend; do
        docker tag healthguard-$service:$ENVIRONMENT gcr.io/$GCP_PROJECT_ID/healthguard-$service:latest
        docker push gcr.io/$GCP_PROJECT_ID/healthguard-$service:latest
    done
    
    # Deploy to Cloud Run
    gcloud run deploy healthguard-backend \\
        --image gcr.io/$GCP_PROJECT_ID/healthguard-backend:latest \\
        --platform managed \\
        --region $GCP_REGION \\
        --allow-unauthenticated
    
    gcloud run deploy healthguard-mcp \\
        --image gcr.io/$GCP_PROJECT_ID/healthguard-mcp:latest \\
        --platform managed \\
        --region $GCP_REGION \\
        --no-allow-unauthenticated
    
    gcloud run deploy healthguard-frontend \\
        --image gcr.io/$GCP_PROJECT_ID/healthguard-frontend:latest \\
        --platform managed \\
        --region $GCP_REGION \\
        --allow-unauthenticated
    
    echo -e "${GREEN}✓ Deployed to GCP Cloud Run${NC}"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    echo -e "${YELLOW}[5/8] Deploying to Kubernetes...${NC}"
    
    cd "$PROJECT_ROOT/infrastructure/kubernetes"
    
    # Apply base manifests
    kubectl apply -f base/
    
    # Apply production overlay
    kubectl apply -f overlays/production/
    
    # Wait for rollout
    kubectl rollout status deployment/healthguard-backend
    kubectl rollout status deployment/healthguard-mcp
    kubectl rollout status deployment/healthguard-frontend
    
    echo -e "${GREEN}✓ Deployed to Kubernetes${NC}"
}

# Deploy with Docker Compose
deploy_docker() {
    echo -e "${YELLOW}[5/8] Deploying with Docker Compose...${NC}"
    
    cd "$PROJECT_ROOT"
    
    docker-compose -f docker-compose.production.yml up -d
    
    echo -e "${GREEN}✓ Deployed with Docker Compose${NC}"
}

# Run database migrations
run_migrations() {
    echo -e "${YELLOW}[6/8] Running database migrations...${NC}"
    
    cd "$PROJECT_ROOT/backend"
    source ../venv/bin/activate
    
    # Run migrations
    python -c "from db.database import init_db; import asyncio; asyncio.run(init_db())"
    
    echo -e "${GREEN}✓ Migrations completed${NC}"
}

# Health check
health_check() {
    echo -e "${YELLOW}[7/8] Running health checks...${NC}"
    
    local backend_url=""
    
    case $PLATFORM in
        aws)
            backend_url="https://api.healthguard.example.com"
            ;;
        azure)
            backend_url="https://healthguard-backend.azurecontainerapps.io"
            ;;
        gcp)
            backend_url="https://healthguard-backend-xxxxx-uc.a.run.app"
            ;;
        local|docker)
            backend_url="http://localhost:8000"
            ;;
    esac
    
    if [ -n "$backend_url" ]; then
        echo "Checking $backend_url/health..."
        for i in {1..10}; do
            if curl -sf "$backend_url/health" > /dev/null; then
                echo -e "${GREEN}✓ Backend is healthy${NC}"
                return 0
            fi
            echo "Waiting for backend... ($i/10)"
            sleep 5
        done
        
        echo -e "${RED}❌ Health check failed${NC}"
        return 1
    fi
}

# Print deployment info
print_deployment_info() {
    echo -e "${YELLOW}[8/8] Deployment Summary${NC}"
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  Deployment Successful!                        ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Platform: $PLATFORM"
    echo "Environment: $ENVIRONMENT"
    echo "Version: $APP_VERSION"
    echo ""
    
    case $PLATFORM in
        aws)
            echo "Backend: https://api.healthguard.example.com"
            echo "Frontend: https://healthguard.example.com"
            echo "Monitoring: https://console.aws.amazon.com/cloudwatch"
            ;;
        azure)
            echo "Backend: https://healthguard-backend.azurecontainerapps.io"
            echo "Frontend: https://healthguard.example.com"
            echo "Monitoring: https://portal.azure.com"
            ;;
        gcp)
            echo "Cloud Console: https://console.cloud.google.com"
            ;;
        local|docker)
            echo "Backend: http://localhost:8000"
            echo "Frontend: http://localhost:5173"
            echo "MCP: http://localhost:3000"
            ;;
    esac
    
    echo ""
    echo "Logs: ./scripts/deployment/logs.sh"
    echo "Rollback: ./scripts/deployment/rollback.sh"
    echo ""
}

# Main deployment flow
main() {
    validate_production_config
    check_dependencies
    build_images
    
    # Skip tests for local development
    if [ "$ENVIRONMENT" != "development" ]; then
        run_tests
    fi
    
    # Deploy based on platform
    case $PLATFORM in
        aws)
            deploy_aws
            ;;
        azure)
            deploy_azure
            ;;
        gcp)
            deploy_gcp
            ;;
        kubernetes|k8s)
            deploy_kubernetes
            ;;
        docker|local)
            deploy_docker
            ;;
        *)
            echo -e "${RED}Unknown platform: $PLATFORM${NC}"
            echo "Supported: aws, azure, gcp, kubernetes, docker"
            exit 1
            ;;
    esac
    
    if [ "$PLATFORM" != "local" ]; then
        run_migrations
    fi
    
    health_check
    print_deployment_info
}

# Run main function
main "$@"
