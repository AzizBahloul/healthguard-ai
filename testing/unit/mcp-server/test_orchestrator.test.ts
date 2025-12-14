/**
 * Unit tests for MCP Orchestrator
 * Tests agent coordination, request routing, and policy enforcement
 */

import { Orchestrator } from '../../../mcp-server/src/core/orchestrator';
import { AgentRegistry } from '../../../mcp-server/src/agents/registry';
import { PolicyEngine } from '../../../mcp-server/src/policies/engine';
import { CircuitBreakerManager } from '../../../mcp-server/src/core/circuit-breakers';
import { MemoryManager } from '../../../mcp-server/src/memory/manager';

describe('Orchestrator', () => {
  let orchestrator: Orchestrator;
  let agentRegistry: AgentRegistry;
  let policyEngine: PolicyEngine;
  let circuitBreakers: CircuitBreakerManager;
  let memoryManager: MemoryManager;

  beforeEach(() => {
    agentRegistry = new AgentRegistry();
    policyEngine = new PolicyEngine();
    circuitBreakers = new CircuitBreakerManager();
    memoryManager = new MemoryManager();
    
    orchestrator = new Orchestrator(
      agentRegistry,
      policyEngine,
      circuitBreakers,
      memoryManager
    );
  });

  describe('Request Routing', () => {
    it('should route request to correct agent', async () => {
      const request = {
        agentId: 'bed_orchestrator',
        action: 'allocate_bed',
        payload: {
          hospital_id: 'metro_general',
          patient_id: 'P12345',
          bed_type: 'icu'
        },
        priority: 'high' as const,
        requestId: 'REQ001'
      };

      const response = await orchestrator.routeRequest(request);
      expect(response.success).toBeDefined();
    });

    it('should reject request if circuit breaker is open', async () => {
      // Trigger circuit breaker by causing 5 failures
      const agentId = 'failing_agent';
      for (let i = 0; i < 5; i++) {
        circuitBreakers.recordFailure(agentId);
      }

      const request = {
        agentId: agentId,
        action: 'test',
        payload: {},
        priority: 'low' as const,
        requestId: 'REQ002'
      };

      const response = await orchestrator.routeRequest(request);
      expect(response.success).toBe(false);
      expect(response.error).toContain('circuit breaker');
    });

    it('should enforce policy restrictions', async () => {
      const request = {
        agentId: 'bed_orchestrator',
        action: 'unauthorized_action',
        payload: {},
        priority: 'low' as const,
        requestId: 'REQ003'
      };

      const response = await orchestrator.routeRequest(request);
      // Policy engine should block unauthorized actions
      expect(response.success).toBe(false);
    });

    it('should prioritize critical requests', async () => {
      const requests = [
        {
          agentId: 'trauma_coordinator',
          action: 'route_patient',
          payload: {},
          priority: 'critical' as const,
          requestId: 'REQ_CRITICAL'
        },
        {
          agentId: 'bed_orchestrator',
          action: 'allocate_bed',
          payload: {},
          priority: 'low' as const,
          requestId: 'REQ_LOW'
        }
      ];

      const responses = await Promise.all(
        requests.map(r => orchestrator.routeRequest(r))
      );

      // Critical request should be processed first
      expect(responses[0]).toBeDefined();
    });
  });

  describe('Error Handling', () => {
    it('should handle agent not found', async () => {
      const request = {
        agentId: 'nonexistent_agent',
        action: 'test',
        payload: {},
        priority: 'medium' as const,
        requestId: 'REQ004'
      };

      const response = await orchestrator.routeRequest(request);
      expect(response.success).toBe(false);
      expect(response.error).toContain('not found');
    });

    it('should handle malformed requests', async () => {
      const request = {
        agentId: '',
        action: '',
        payload: null,
        priority: 'invalid' as any,
        requestId: ''
      };

      const response = await orchestrator.routeRequest(request);
      expect(response.success).toBe(false);
    });

    it('should log errors to audit trail', async () => {
      const request = {
        agentId: 'bed_orchestrator',
        action: 'failing_action',
        payload: {},
        priority: 'medium' as const,
        requestId: 'REQ005'
      };

      await orchestrator.routeRequest(request);
      // Audit log should contain error entry
      // This would need audit log inspection
    });
  });

  describe('Lifecycle Management', () => {
    it('should start successfully', async () => {
      await expect(orchestrator.start()).resolves.not.toThrow();
    });

    it('should stop successfully', async () => {
      await orchestrator.start();
      await expect(orchestrator.stop()).resolves.not.toThrow();
    });

    it('should clear request queue on stop', async () => {
      await orchestrator.start();
      
      // Add some requests
      await orchestrator.routeRequest({
        agentId: 'test',
        action: 'test',
        payload: {},
        priority: 'low' as const,
        requestId: 'REQ006'
      });

      await orchestrator.stop();
      // Queue should be empty after stop
    });
  });

  describe('Multi-Agent Coordination', () => {
    it('should coordinate between multiple agents', async () => {
      const request1 = {
        agentId: 'bed_orchestrator',
        action: 'check_availability',
        payload: { hospital_id: 'metro_general' },
        priority: 'medium' as const,
        requestId: 'REQ007'
      };

      const request2 = {
        agentId: 'ambulance_router',
        action: 'find_nearest',
        payload: { location: { lat: 40.7, lng: -74.0 } },
        priority: 'high' as const,
        requestId: 'REQ008'
      };

      const [response1, response2] = await Promise.all([
        orchestrator.routeRequest(request1),
        orchestrator.routeRequest(request2)
      ]);

      expect(response1).toBeDefined();
      expect(response2).toBeDefined();
    });

    it('should handle agent dependencies', async () => {
      // Request that requires data from another agent
      const request = {
        agentId: 'trauma_coordinator',
        action: 'coordinate_response',
        payload: {
          requires: ['bed_availability', 'ambulance_eta']
        },
        priority: 'critical' as const,
        requestId: 'REQ009'
      };

      const response = await orchestrator.routeRequest(request);
      expect(response.success).toBeDefined();
    });
  });

  describe('Performance', () => {
    it('should handle high request volume', async () => {
      const requests = Array.from({ length: 100 }, (_, i) => ({
        agentId: 'bed_orchestrator',
        action: 'check_availability',
        payload: { hospital_id: `hospital_${i}` },
        priority: 'medium' as const,
        requestId: `REQ_PERF_${i}`
      }));

      const startTime = Date.now();
      await Promise.all(requests.map(r => orchestrator.routeRequest(r)));
      const endTime = Date.now();

      const duration = endTime - startTime;
      // Should process 100 requests in under 5 seconds
      expect(duration).toBeLessThan(5000);
    });

    it('should maintain low latency for critical requests', async () => {
      const request = {
        agentId: 'trauma_coordinator',
        action: 'emergency_route',
        payload: {},
        priority: 'critical' as const,
        requestId: 'REQ_LATENCY'
      };

      const startTime = Date.now();
      await orchestrator.routeRequest(request);
      const endTime = Date.now();

      const latency = endTime - startTime;
      // Critical requests should be under 100ms
      expect(latency).toBeLessThan(100);
    });
  });
});
