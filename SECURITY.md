# Security Policy

## Overview

HealthGuard AI implements a defense-in-depth security model with zero-trust architecture for healthcare data protection.

## Security Layers

### 1. Network Security
- TLS 1.3 for all communications
- Mutual TLS for service-to-service
- Network microsegmentation
- DDoS protection via CloudFlare

### 2. Authentication & Authorization
- Multi-factor authentication required
- JWT tokens (15min expiry)
- Role-based access control (RBAC)
- Audit logging of all access

### 3. Data Protection
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- PHI tokenization
- Automated PHI redaction

### 4. Compliance
- HIPAA compliant
- GDPR compliant
- SOC2 Type II certified
- Regular penetration testing

## Reporting Security Issues

**DO NOT** create public GitHub issues for security vulnerabilities.

Email: security@healthguard-ai.com

PGP Key: [keys/security-public.asc](./keys/security-public.asc)

## Security Testing

- Quarterly external penetration tests
- Monthly internal red team exercises
- Continuous vulnerability scanning
- Bug bounty program: https://bugcrowd.com/healthguard-ai

## Incident Response

See [docs/runbooks/incident_response.md](./docs/runbooks/incident_response.md)
