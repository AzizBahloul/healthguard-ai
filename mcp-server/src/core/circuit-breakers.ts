import { logger } from '../utils/logger';

interface CircuitBreakerState {
  state: 'closed' | 'open' | 'half-open';
  failureCount: number;
  lastFailureTime?: Date;
  successCount: number;
}

export class CircuitBreakerManager {
  private breakers: Map<string, CircuitBreakerState>;

  constructor() {
    this.breakers = new Map();
  }

  async initialize(): Promise<void> {
    logger.info('Initializing circuit breakers...');
    // Load circuit breaker configurations
    logger.info('Circuit breakers initialized');
  }

  isOpen(agentId: string): boolean {
    const breaker = this.breakers.get(agentId);
    return breaker?.state === 'open';
  }

  recordSuccess(agentId: string): void {
    const breaker = this.breakers.get(agentId) || this.createBreaker(agentId);
    breaker.successCount++;
    breaker.failureCount = 0;
    this.breakers.set(agentId, breaker);
  }

  recordFailure(agentId: string): void {
    const breaker = this.breakers.get(agentId) || this.createBreaker(agentId);
    breaker.failureCount++;
    breaker.lastFailureTime = new Date();

    // Open circuit if threshold exceeded
    if (breaker.failureCount >= 5) {
      breaker.state = 'open';
      logger.warn(`Circuit breaker opened for agent: ${agentId}`);
    }

    this.breakers.set(agentId, breaker);
  }

  private createBreaker(agentId: string): CircuitBreakerState {
    return {
      state: 'closed',
      failureCount: 0,
      successCount: 0
    };
  }
}
