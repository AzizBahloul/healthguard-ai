# 🏥 HealthGuard AI
## Advanced Multi-Region Healthcare Intelligence Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-brightgreen.svg)](https://www.docker.com/)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

---

## Overview

**HealthGuard AI** is a production-grade, AI-powered healthcare coordination platform that intelligently manages emergency medical resources across hospital networks. It uses MCP (Model Context Protocol) to govern autonomous agents that assist with:

- 🚑 **Emergency Routing**: Intelligent ambulance routing and trauma center selection
- 🏥 **Resource Allocation**: Real-time bed capacity management and optimization
- 📊 **Predictive Analytics**: Forecasting demand surges and capacity bottlenecks
- 🤝 **Multi-Hospital Coordination**: Regional load balancing and patient transfers
- 👨‍⚕️ **Human-in-the-Loop**: All critical decisions require human approval

## Key Features

### AI Agent Control (MCP Server)
- **13 Specialized Agents**: Trauma, cardiac, bed allocation, ambulance routing, etc.
- **Circuit Breakers**: Automatic safety shutoffs to prevent cascading failures
- **Rate Limiting**: Fair resource allocation and abuse prevention
- **Policy Engine**: HIPAA/GDPR compliant with full audit trails

### Backend Services
- **RESTful API**: FastAPI with async support
- **Event Streaming**: Kafka for real-time event processing
- **Multiple Databases**: PostgreSQL, Redis, Neo4j, Qdrant
- **WebSocket Support**: Real-time updates to frontends

### Frontend
- **Command Center**: Real-time monitoring dashboard
- **Decision Review**: AI recommendation inspector
- **Interactive Maps**: Ambulance tracking and hospital status
- **Alert Management**: Prioritized notification system

### Infrastructure
- **Docker Compose**: Complete local development environment
- **Monitoring**: Prometheus + Grafana dashboards
- **Logging**: ELK stack (Elasticsearch, Kibana)
- **Zero Trust**: Multi-layer security architecture

## Quick Start

### Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- 8GB+ RAM
- 20GB+ disk space

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/healthguard-ai.git
cd healthguard-ai

# Copy environment file
cp .env.example .env

# Run initialization script
chmod +x scripts/setup/init-dev-environment.sh
./scripts/setup/init-dev-environment.sh
```

The script will:
1. ✅ Check prerequisites
2. ✅ Create directory structure
3. ✅ Start infrastructure (databases, message queues)
4. ✅ Build and start application services
5. ✅ Initialize monitoring stack

### Access Services

Once running, access the platform:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Backend API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **MCP Server** | http://localhost:3000 | - |
| **Command Center** | http://localhost:5173 | - |
| **Grafana** | http://localhost:3001 | admin/admin |
| **Prometheus** | http://localhost:9090 | - |
| **Neo4j** | http://localhost:7474 | neo4j/healthguard_dev |
| **Kibana** | http://localhost:5601 | - |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  Command Center │ Hospital Portal │ Ambulance App          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                     API Gateway                             │
│         Auth │ Rate Limiting │ Request Validation          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                  MCP Server (Control Plane)                 │
│  Orchestrator │ 13 Agents │ Policies │ Tools │ Memory      │
│  • Trauma Coordinator    • Bed Orchestrator                 │
│  • Cardiac Router        • Ambulance Router                 │
│  • Surge Detector        • Regional Coordinator             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Backend Services                          │
│  Event Bus │ Intelligence │ Integrations │ Safety          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Data Layer                                │
│  PostgreSQL │ Redis │ Kafka │ Qdrant │ Neo4j              │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
healthguard-ai/
├── mcp-server/          # AI agent orchestration (TypeScript)
│   ├── core/            # Orchestrator, circuit breakers, rate limiters
│   ├── policies/        # Safety, privacy, consent, liability rules
│   ├── agents/          # 13 specialized AI agents
│   ├── tools/           # Sensors, actuators, validators
│   ├── memory/          # Vector stores, graph memory
│   └── reasoning/       # Decision chains, prompts
│
├── backend/             # FastAPI backend (Python)
│   ├── api/v1/          # REST endpoints
│   ├── services/        # Business logic
│   ├── db/              # Database models
│   └── events/          # Kafka producers/consumers
│
├── frontend/            # React frontend (TypeScript)
│   ├── apps/            # Command center, hospital portal
│   └── packages/        # Shared components
│
├── ml/                  # Machine learning pipeline
│   ├── models/          # Forecasting, classification, optimization
│   └── pipelines/       # Training, evaluation, monitoring
│
├── infrastructure/      # DevOps configuration
│   ├── terraform/       # Cloud infrastructure
│   ├── kubernetes/      # K8s manifests
│   └── monitoring/      # Prometheus, Grafana
│
├── docs/                # Documentation
│   ├── architecture/    # System design docs
│   ├── api/             # API specifications
│   └── runbooks/        # Operational guides
│
└── compliance/          # Regulatory compliance
    ├── regulatory/      # HIPAA, GDPR
    ├── ethics/          # AI ethics framework
    └── audit/           # Audit trails, compliance certs
```

## Development

### Running Locally (without Docker)

**MCP Server:**
```bash
cd mcp-server
npm install
npm run dev
```

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f mcp-server
docker-compose logs -f backend
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# MCP Server tests
cd mcp-server
npm test
```

## MCP Agents

| Agent | Type | Purpose | Confidence Threshold |
|-------|------|---------|---------------------|
| trauma_coordinator | Critical | Route trauma patients | 90% |
| cardiac_router | Critical | Route cardiac patients | 90% |
| stroke_pathway | Critical | Route stroke patients | 90% |
| bed_orchestrator | Operational | Allocate hospital beds | 80% |
| ambulance_router | Operational | Route ambulances | 80% |
| blood_optimizer | Operational | Manage blood inventory | 80% |
| staff_scheduler | Operational | Schedule medical staff | 70% |
| equipment_monitor | Operational | Track medical equipment | 70% |
| demand_forecaster | Predictive | Forecast resource demand | 70% |
| surge_detector | Predictive | Detect patient surges | 75% |
| capacity_planner | Predictive | Plan capacity needs | 70% |
| regional_coordinator | Coordination | Regional load balancing | 80% |
| disaster_response | Coordination | Disaster coordination | 90% |

## API Endpoints

### Emergency Routing
```http
POST /api/v1/emergency/trauma
POST /api/v1/emergency/cardiac
POST /api/v1/emergency/stroke
GET  /api/v1/emergency/active
```

### Hospital Management
```http
GET  /api/v1/hospitals/beds
GET  /api/v1/hospitals/{hospital_id}
GET  /api/v1/hospitals
```

### Ambulance Operations
```http
GET  /api/v1/ambulances/active
POST /api/v1/ambulances/route
GET  /api/v1/ambulances/{ambulance_id}
```

## Monitoring & Observability

### Metrics (Prometheus)
- Request latency (p50, p95, p99)
- Agent decision accuracy
- Circuit breaker states
- Rate limit violations
- Resource utilization

### Dashboards (Grafana)
- System overview
- Agent performance
- Hospital capacity heatmap
- Alert timeline

### Logging (ELK)
- Application logs
- Audit logs
- Decision logs
- Error tracking

## Security

### Defense in Depth
1. **MCP Policy Enforcement**: Safety rules, privacy protection
2. **Backend Validation**: Business rule checking
3. **Database Constraints**: Data integrity
4. **Circuit Breakers**: Automatic failsafes
5. **Human Oversight**: Required approvals

### Zero Trust Architecture
- JWT authentication
- Role-based access control (RBAC)
- Encrypted communication (TLS 1.3)
- Audit logging
- Time-bound permissions

## Compliance

- ✅ **HIPAA**: PHI protection, encryption, audit trails
- ✅ **GDPR**: Data minimization, right to erasure
- ✅ **SOC2**: Security controls, monitoring
- ✅ **Medical Device**: FDA guidance compliance

## Roadmap

### Phase 1: Foundation ✅ (Current)
- Core MCP orchestrator
- Basic agents (trauma, bed, ambulance)
- Backend API
- Command center UI

### Phase 2: Enhanced Agents (Q1 2024)
- All 13 agents operational
- Advanced forecasting models
- EHR integrations

### Phase 3: Advanced Features (Q2 2024)
- Federated learning
- Social media monitoring
- IoT sensor integration

### Phase 4: Production Hardening (Q3 2024)
- Multi-region deployment
- Load testing
- Security certification
- Disaster recovery

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@healthguard-ai.com
- 💬 Discussions: GitHub Discussions
- 🐛 Issues: GitHub Issues
- 📖 Documentation: [docs/](./docs/)

## Acknowledgments

- Built with [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
- Healthcare protocols from [ACS TQIP](https://www.facs.org/quality-programs/trauma/tqp/)
- Inspired by real-world healthcare coordination challenges

---

**⚠️ Important Notice**: This is a development platform. For production use in healthcare settings, ensure full compliance with local regulations, obtain necessary certifications, and conduct thorough clinical validation.

**Made with ❤️ for better healthcare outcomes**
Advanced Multi-Region Healthcare Intelligence Platform
