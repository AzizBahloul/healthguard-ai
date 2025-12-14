# HealthGuard AI: System Overview

## What is HealthGuard AI?

HealthGuard AI is an advanced multi-region healthcare intelligence platform that coordinates emergency medical resources across hospital networks using AI-powered agents governed by Model Context Protocol (MCP).

## Core Capabilities

- **Real-time Resource Allocation**: Intelligent bed assignment, ambulance routing, and equipment tracking
- **Predictive Analytics**: Forecasting demand surges, capacity bottlenecks, and equipment failures
- **Multi-Hospital Coordination**: Regional load balancing and inter-facility transfers
- **Human-in-the-Loop Control**: All critical decisions require human approval
- **Compliance-First**: HIPAA/GDPR compliant with full audit trails

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  Command Center │ Hospital Portal │ Ambulance App │ Mobile │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                     API Gateway                             │
│         Auth │ Rate Limiting │ Request Validation          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    MCP Server (Control Plane)               │
│  Orchestrator │ Agents │ Policies │ Tools │ Memory         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Backend Services                          │
│  Event Bus │ Intelligence │ Integrations │ Safety          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   Data Layer                                │
│  PostgreSQL │ Redis │ Kafka │ Vector DB │ Graph DB        │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for setup instructions.

## Documentation

- [Architecture Details](./docs/architecture/system_design.md)
- [API Reference](./docs/api/openapi.yaml)
- [Security Model](./SECURITY.md)
- [Disaster Recovery](./DISASTER_RECOVERY.md)

## Project Status: Phase 1 Implementation

Current focus: Foundation setup with core MCP orchestrator and basic agent capabilities.
