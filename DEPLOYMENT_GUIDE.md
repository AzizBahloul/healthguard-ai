# HealthGuard AI: Deployment Guide

## Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- Node.js 20+
- Python 3.11+
- Terraform 1.5+ (for cloud deployment)
- kubectl 1.28+ (for Kubernetes deployment)

## Local Development Setup

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/healthguard-ai.git
cd healthguard-ai
./scripts/setup/init-dev-environment.sh
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Infrastructure

```bash
docker-compose up -d postgres redis kafka minio
```

### 4. Run MCP Server

```bash
cd mcp-server
npm install
npm run dev
```

### 5. Run Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 6. Run Frontend

```bash
cd frontend/apps/command_center
npm install
npm run dev
```

## Production Deployment

### Cloud Infrastructure (AWS)

```bash
cd infrastructure/terraform/environments/production
terraform init
terraform plan
terraform apply
```

### Kubernetes Deployment

```bash
cd infrastructure/kubernetes
kubectl apply -f base/
kubectl apply -f overlays/production/
```

## Health Checks

- MCP Server: http://localhost:3000/health
- Backend API: http://localhost:8000/health
- Frontend: http://localhost:5173
- Grafana Dashboard: http://localhost:3001

## Monitoring

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)
- Kibana: http://localhost:5601

## Troubleshooting

See [docs/runbooks/troubleshooting.md](./docs/training/troubleshooting.md)
