/**
 * Unit tests for Circuit Breaker Manager
 * Tests circuit breaker state management and failure handling
 */
import { CircuitBreakerManager } from '../../../mcp-server/src/core/circuit-breakers';

describe('CircuitBreakerManager', () => {
  let manager: CircuitBreakerManager;

  beforeEach(() => {
    manager = new CircuitBreakerManager();
  });

  describe('initialization', () => {
    it('should initialize without errors', async () => {
      await expect(manager.initialize()).resolves.not.toThrow();
    });

    it('should start with all circuits closed', () => {
      expect(manager.isOpen('test-agent')).toBe(false);
    });
  });

  describe('failure recording', () => {
    it('should record single failure', () => {
      manager.recordFailure('test-agent');
      expect(manager.isOpen('test-agent')).toBe(false);
    });

    it('should open circuit after threshold failures', () => {
      const agentId = 'test-agent';
      
      // Record 5 failures to reach threshold
      for (let i = 0; i < 5; i++) {
        manager.recordFailure(agentId);
      }
      
      expect(manager.isOpen(agentId)).toBe(true);
    });

    it('should keep different agents isolated', () => {
      manager.recordFailure('agent-1');
      manager.recordFailure('agent-1');
      manager.recordFailure('agent-1');
      manager.recordFailure('agent-1');
      manager.recordFailure('agent-1');
      
      expect(manager.isOpen('agent-1')).toBe(true);
      expect(manager.isOpen('agent-2')).toBe(false);
    });
  });

  describe('success recording', () => {
    it('should record success', () => {
      manager.recordSuccess('test-agent');
      expect(manager.isOpen('test-agent')).toBe(false);
    });

    it('should reset failure count on success', () => {
      const agentId = 'test-agent';
      
      // Record some failures
      manager.recordFailure(agentId);
      manager.recordFailure(agentId);
      manager.recordFailure(agentId);
      
      // Record success - should reset
      manager.recordSuccess(agentId);
      
      // Should not open even after more failures up to threshold
      manager.recordFailure(agentId);
      manager.recordFailure(agentId);
      expect(manager.isOpen(agentId)).toBe(false);
    });
  });

  describe('circuit state management', () => {
    it('should maintain closed state for healthy agents', () => {
      const agentId = 'healthy-agent';
      
      for (let i = 0; i < 10; i++) {
        manager.recordSuccess(agentId);
      }
      
      expect(manager.isOpen(agentId)).toBe(false);
    });

    it('should open circuit for unhealthy agents', () => {
      const agentId = 'unhealthy-agent';
      
      for (let i = 0; i < 5; i++) {
        manager.recordFailure(agentId);
      }
      
      expect(manager.isOpen(agentId)).toBe(true);
    });

    it('should handle mixed success and failure', () => {
      const agentId = 'mixed-agent';
      
      manager.recordSuccess(agentId);
      manager.recordFailure(agentId);
      manager.recordSuccess(agentId);
      manager.recordFailure(agentId);
      
      expect(manager.isOpen(agentId)).toBe(false);
    });
  });

  describe('multiple agents', () => {
    it('should manage multiple agents independently', async () => {
      await manager.initialize();
      
      // Agent 1 - healthy
      manager.recordSuccess('agent-1');
      manager.recordSuccess('agent-1');
      
      // Agent 2 - unhealthy
      for (let i = 0; i < 5; i++) {
        manager.recordFailure('agent-2');
      }
      
      // Agent 3 - moderate
      manager.recordFailure('agent-3');
      manager.recordSuccess('agent-3');
      
      expect(manager.isOpen('agent-1')).toBe(false);
      expect(manager.isOpen('agent-2')).toBe(true);
      expect(manager.isOpen('agent-3')).toBe(false);
    });
  });

  describe('edge cases', () => {
    it('should handle non-existent agent check', () => {
      expect(manager.isOpen('non-existent')).toBe(false);
    });

    it('should handle rapid successive failures', () => {
      const agentId = 'rapid-fail';
      
      for (let i = 0; i < 10; i++) {
        manager.recordFailure(agentId);
      }
      
      expect(manager.isOpen(agentId)).toBe(true);
    });

    it('should handle rapid successive successes', () => {
      const agentId = 'rapid-success';
      
      for (let i = 0; i < 100; i++) {
        manager.recordSuccess(agentId);
      }
      
      expect(manager.isOpen(agentId)).toBe(false);
    });
  });
});
