# MCP Server: AI Agent Control Plane

## Overview

The MCP (Model Context Protocol) Server provides centralized governance, orchestration, and safety controls for all AI agents in the HealthGuard AI system.

## Architecture

```
┌─────────────────────────────────────────┐
│         Core Orchestrator               │
│  Request Routing │ Agent Coordination   │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼────┐ ┌──▼────┐ ┌─▼──────┐
│ Agents │ │ Tools │ │ Memory │
└───┬────┘ └──┬────┘ └─┬──────┘
    │         │         │
    └─────────┼─────────┘
              │
    ┌─────────▼─────────┐
    │     Policies      │
    │ Safety │ Privacy  │
    └───────────────────┘
```

## Components

### Core
- **orchestrator.yaml**: Master coordination logic
- **circuit_breakers.yaml**: Automatic safety shutoffs
- **rate_limiters.yaml**: Request throttling

### Policies
- Safety rules for medical decisions
- Privacy rules (HIPAA/GDPR)
- Escalation procedures
- Audit requirements

### Agents
- **Critical**: Life-threatening decisions (trauma, cardiac, stroke)
- **Operational**: Resource management (beds, ambulances, staff)
- **Predictive**: Forecasting (demand, surges, capacity)
- **Coordination**: Multi-agent orchestration

### Tools
- **Sensors**: Read-only data access
- **Actuators**: Controlled actions
- **Validators**: Data quality checks

### Memory
- **Vector Stores**: Semantic search over past incidents
- **Graph Memory**: Relationship tracking
- **Time-based**: Short/mid/long-term memory

## Running

```bash
npm install
npm run dev          # Development
npm run build        # Production build
npm start            # Production
npm test             # Run tests
```

## Configuration

Edit `core/mcp.config.yaml` for global settings.
