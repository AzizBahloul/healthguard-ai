"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CircuitBreakerManager = void 0;
const logger_1 = require("../utils/logger");
class CircuitBreakerManager {
    breakers;
    constructor() {
        this.breakers = new Map();
    }
    async initialize() {
        logger_1.logger.info('Initializing circuit breakers...');
        // Load circuit breaker configurations
        logger_1.logger.info('Circuit breakers initialized');
    }
    isOpen(agentId) {
        const breaker = this.breakers.get(agentId);
        return breaker?.state === 'open';
    }
    recordSuccess(agentId) {
        const breaker = this.breakers.get(agentId) || this.createBreaker(agentId);
        breaker.successCount++;
        breaker.failureCount = 0;
        this.breakers.set(agentId, breaker);
    }
    recordFailure(agentId) {
        const breaker = this.breakers.get(agentId) || this.createBreaker(agentId);
        breaker.failureCount++;
        breaker.lastFailureTime = new Date();
        // Open circuit if threshold exceeded
        if (breaker.failureCount >= 5) {
            breaker.state = 'open';
            logger_1.logger.warn(`Circuit breaker opened for agent: ${agentId}`);
        }
        this.breakers.set(agentId, breaker);
    }
    createBreaker(agentId) {
        return {
            state: 'closed',
            failureCount: 0,
            successCount: 0
        };
    }
}
exports.CircuitBreakerManager = CircuitBreakerManager;
//# sourceMappingURL=circuit-breakers.js.map