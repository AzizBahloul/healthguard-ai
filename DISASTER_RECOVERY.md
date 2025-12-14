# Disaster Recovery Plan

## Objectives

- **RPO (Recovery Point Objective)**: Zero data loss
- **RTO (Recovery Time Objective)**: <5 minutes for critical systems

## Multi-Region Architecture

### Active Regions
- **Primary**: us-east-1 (N. Virginia)
- **Secondary**: eu-west-1 (Ireland)
- **Tertiary**: ap-south-1 (Mumbai)

## Backup Strategy

### Continuous Backups
- PostgreSQL: WAL streaming replication
- Redis: AOF persistence + RDB snapshots
- Kafka: Multi-region replication

### Snapshot Backups
- Daily full snapshots at 2:00 AM UTC
- Retained for 30 days
- Encrypted with AWS KMS

## Failover Procedures

### Automatic Failover
1. Health checks detect primary region failure
2. Route53 updates DNS to secondary region (<30s)
3. Secondary region promoted to primary
4. Alerts sent to on-call team

### Manual Failover
```bash
cd infrastructure/terraform/environments/production
terraform workspace select eu-west-1
./scripts/emergency/manual-failover.sh --from us-east-1 --to eu-west-1
```

## Recovery Testing

- Monthly DR drills
- Quarterly full failover tests
- Annual multi-region failure simulation

## Degraded Mode Operations

If multi-region fails, system enters degraded mode:
1. **Full AI**: All systems operational
2. **Limited AI**: Non-critical agents disabled
3. **Emergency Only**: Life-critical agents only
4. **Manual Mode**: AI advisory only
5. **Offline Mode**: Local hospital operations

## Contact

DR Coordinator: dr-team@healthguard-ai.com
Emergency Hotline: +1-555-HEALTH-DR
