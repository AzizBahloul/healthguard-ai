# HealthGuard AI - Production Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Cloud CLI tools (AWS CLI, Azure CLI, or gcloud)
- kubectl (for Kubernetes deployments)
- Active cloud account with appropriate permissions

### 1. Configure Environment

Copy the production environment template:
```bash
cp .env.production .env
```

Edit `.env` and configure:
- **DEPLOYMENT_PLATFORM**: Choose `aws`, `azure`, `gcp`, `kubernetes`, or `docker`
- **LLM_MODE**: Choose `local`, `api`, or `hybrid`
- **Cloud credentials**: Add your cloud provider credentials
- **Security secrets**: Generate secure secrets for production

**Generate secure secrets:**
```bash
# JWT Secret (64 characters)
openssl rand -hex 32

# Encryption Key (32 characters)
openssl rand -hex 16

# Database Password (strong password)
openssl rand -base64 32
```

### 2. Deploy

Run the automated deployment script:
```bash
./scripts/deployment/deploy.sh <platform> <environment>
```

**Examples:**
```bash
# Deploy to AWS production
./scripts/deployment/deploy.sh aws production

# Deploy to Azure staging
./scripts/deployment/deploy.sh azure staging

# Deploy locally with Docker
./scripts/deployment/deploy.sh docker development
```

---

## 📋 Platform-Specific Deployment

### AWS Deployment

**Using ECS (Easiest)**
```bash
# 1. Configure AWS credentials
aws configure

# 2. Create ECR repositories
aws ecr create-repository --repository-name healthguard-backend
aws ecr create-repository --repository-name healthguard-mcp
aws ecr create-repository --repository-name healthguard-frontend

# 3. Deploy
./scripts/deployment/deploy.sh aws production
```

**Using EKS (For GPU/Local LLM)**
```bash
# 1. Create EKS cluster
eksctl create cluster -f infrastructure/deploy/aws-config.yaml

# 2. Deploy with kubectl
kubectl apply -f infrastructure/kubernetes/base/
kubectl apply -f infrastructure/kubernetes/overlays/production/
```

**Using Terraform (Recommended)**
```bash
cd infrastructure/terraform/aws
terraform init
terraform plan
terraform apply
```

**Resources Created:**
- ECS Cluster with 3 services (backend, mcp, frontend)
- RDS PostgreSQL (db.r6g.xlarge, multi-AZ)
- ElastiCache Redis (3-node cluster)
- Application Load Balancer
- CloudWatch Logs & Alarms
- Secrets Manager
- S3 buckets for backups
- VPC with private subnets

**Estimated Cost:** ~$800-1,200/month

---

### Azure Deployment

**Using Container Apps (Easiest)**
```bash
# 1. Login to Azure
az login

# 2. Create resource group
az group create --name healthguard-production --location eastus

# 3. Create container registry
az acr create --resource-group healthguard-production --name healthguard --sku Premium

# 4. Deploy
./scripts/deployment/deploy.sh azure production
```

**Using AKS (For GPU/Local LLM)**
```bash
# 1. Create AKS cluster
az aks create \
  --resource-group healthguard-production \
  --name healthguard-cluster \
  --node-count 3 \
  --enable-managed-identity \
  --generate-ssh-keys

# 2. Deploy with kubectl
az aks get-credentials --resource-group healthguard-production --name healthguard-cluster
kubectl apply -f infrastructure/kubernetes/base/
```

**Resources Created:**
- Container Apps (3 services with auto-scaling)
- Azure Database for PostgreSQL (GP_Gen5_8)
- Azure Cache for Redis (Premium P2)
- Application Gateway
- Key Vault for secrets
- Application Insights
- Azure Storage for backups

**Estimated Cost:** ~$700-1,000/month

---

### GCP Deployment

**Using Cloud Run (Easiest)**
```bash
# 1. Login to GCP
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Enable required APIs
gcloud services enable run.googleapis.com sql-component.googleapis.com redis.googleapis.com

# 3. Deploy
./scripts/deployment/deploy.sh gcp production
```

**Using GKE (For GPU/Local LLM)**
```bash
# 1. Create GKE cluster
gcloud container clusters create healthguard-production \
  --region us-central1 \
  --num-nodes 3 \
  --machine-type n2-standard-4 \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 20

# 2. Deploy with kubectl
gcloud container clusters get-credentials healthguard-production --region us-central1
kubectl apply -f infrastructure/kubernetes/base/
```

**Resources Created:**
- Cloud Run services (3 services with auto-scaling)
- Cloud SQL PostgreSQL (db-custom-8-32768)
- Memorystore Redis (10GB, high availability)
- Cloud Load Balancing
- Secret Manager
- Cloud Storage for backups
- Cloud Logging & Monitoring

**Estimated Cost:** ~$600-900/month

---

### Docker Compose (Local/Small Scale)

**For local testing or small deployments:**
```bash
# 1. Build images
docker-compose -f docker-compose.production.yml build

# 2. Start services
docker-compose -f docker-compose.production.yml up -d

# 3. Check status
docker-compose -f docker-compose.production.yml ps

# 4. View logs
docker-compose -f docker-compose.production.yml logs -f backend
```

**Services included:**
- Backend API (FastAPI)
- MCP Server (AI orchestration)
- Frontend (React/Vite)
- PostgreSQL database
- Redis cache
- Kafka message queue
- Prometheus (metrics)
- Grafana (dashboards)
- Nginx reverse proxy

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Grafana: http://localhost:3001

---

### Kubernetes (Self-Managed)

**For any Kubernetes cluster:**
```bash
# 1. Configure kubectl
kubectl config use-context YOUR_CLUSTER

# 2. Create namespace
kubectl create namespace healthguard-production

# 3. Create secrets
kubectl create secret generic healthguard-secrets \
  --from-literal=database-password=YOUR_DB_PASSWORD \
  --from-literal=jwt-secret=YOUR_JWT_SECRET \
  --from-literal=encryption-key=YOUR_ENCRYPTION_KEY \
  --from-literal=redis-password=YOUR_REDIS_PASSWORD \
  -n healthguard-production

# 4. Deploy
kubectl apply -f infrastructure/kubernetes/base/ -n healthguard-production

# 5. Check status
kubectl get pods -n healthguard-production
kubectl get svc -n healthguard-production
```

---

## 🤖 LLM Configuration

### Local LLM (Ollama)

**Best for:** Cost-sensitive deployments, data privacy

**Setup:**
1. Set `LLM_MODE=local` in `.env`
2. Install Ollama on GPU-enabled nodes
3. Pull models:
```bash
ollama pull llama2
ollama pull mistral
```

**Advantages:**
- No API costs
- Complete data privacy
- No rate limits

**Requirements:**
- GPU nodes (NVIDIA T4 or better)
- 16GB+ GPU memory for large models
- Higher infrastructure costs

---

### API-based LLM (OpenAI/Anthropic)

**Best for:** High performance, low operational overhead

**Setup:**
1. Set `LLM_MODE=api` in `.env`
2. Add API keys:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

**Advantages:**
- Best performance
- No GPU infrastructure needed
- Easy to scale

**Costs:**
- ~$0.50-2.00 per 1000 requests
- Predictable per-request pricing

---

### Hybrid Mode

**Best for:** Cost optimization with performance

**Setup:**
1. Set `LLM_MODE=hybrid` in `.env`
2. Configure both local and API credentials
3. System automatically routes:
   - Critical/urgent requests → API (fast)
   - Routine analysis → Local (cost-effective)

---

## 📊 Monitoring & Observability

### CloudWatch/Azure Monitor/Cloud Logging

**Access logs:**
```bash
# AWS
aws logs tail /aws/ecs/healthguard-backend --follow

# Azure
az monitor app-insights query \
  --app healthguard-insights \
  --analytics-query "requests | where timestamp > ago(1h)"

# GCP
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

### Grafana Dashboards

**Access:** http://your-domain:3001

**Default dashboards:**
- System Overview
- API Performance
- Database Metrics
- AI Agent Activity
- Error Tracking

### Sentry Error Tracking

**Configure:**
```bash
SENTRY_DSN=https://...@sentry.io/...
```

---

## 🔒 Security Checklist

- [ ] Change all default passwords
- [ ] Generate unique JWT_SECRET (64+ characters)
- [ ] Generate unique ENCRYPTION_KEY (32+ characters)
- [ ] Enable SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Enable database encryption at rest
- [ ] Enable audit logging
- [ ] Configure backup retention (7 years for HIPAA)
- [ ] Set up intrusion detection
- [ ] Configure WAF rules
- [ ] Enable MFA for admin accounts
- [ ] Restrict database access to VPC only
- [ ] Rotate secrets regularly

---

## 🔄 Maintenance

### Database Backups

**Automated:** Daily backups with 30-day retention
**Manual backup:**
```bash
# AWS
aws rds create-db-snapshot --db-instance-identifier healthguard-db --db-snapshot-identifier manual-backup-$(date +%Y%m%d)

# Azure
az postgres server-arc backup create --name backup-$(date +%Y%m%d) --resource-group healthguard-production

# GCP
gcloud sql backups create --instance=healthguard-db-production
```

### Scaling

**Auto-scaling configured:**
- CPU > 70% → scale up
- Memory > 80% → scale up
- Gradual scale down after 5 minutes

**Manual scaling:**
```bash
# AWS ECS
aws ecs update-service --cluster healthguard-production --service healthguard-backend --desired-count 10

# Kubernetes
kubectl scale deployment healthguard-backend --replicas=10
```

### Rolling Updates

**Zero-downtime deployments:**
```bash
# Deploy new version
./scripts/deployment/deploy.sh aws production

# Rollback if needed
./scripts/deployment/rollback.sh
```

---

## 🆘 Troubleshooting

### Backend not starting

**Check logs:**
```bash
docker-compose logs backend
kubectl logs -f deployment/healthguard-backend
```

**Common issues:**
- Database connection: Verify DATABASE_URL
- Missing secrets: Check JWT_SECRET, ENCRYPTION_KEY
- Port conflict: Ensure port 8000 available

### Database connection errors

**Verify connectivity:**
```bash
# Test PostgreSQL connection
psql -h YOUR_DB_HOST -U healthguard -d healthguard

# Check network access
nc -zv YOUR_DB_HOST 5432
```

### High memory usage

**Check metrics:**
```bash
# Docker
docker stats

# Kubernetes
kubectl top pods
```

**Solutions:**
- Increase resource limits
- Optimize database queries
- Enable Redis caching
- Scale horizontally

---

## 📞 Support

**Documentation:** `/docs`
**Issues:** GitHub Issues
**Security:** security@healthguard.ai
**Emergency:** PagerDuty integration

---

## 📈 Performance Benchmarks

**Expected performance (production):**
- API response time: <200ms (p95)
- Database query time: <50ms (p95)
- Concurrent users: 10,000+
- Requests per second: 1,000+
- Uptime: 99.9%+

---

## ✅ Post-Deployment Checklist

- [ ] All services healthy
- [ ] Database migrations completed
- [ ] SSL certificates valid
- [ ] Monitoring dashboards accessible
- [ ] Backup system operational
- [ ] Load testing completed
- [ ] Security scan passed
- [ ] Documentation updated
- [ ] Team trained on runbooks
- [ ] Incident response plan reviewed
