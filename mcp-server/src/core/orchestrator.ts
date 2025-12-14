import { logger, auditLogger } from '../utils/logger';
import { AgentRegistry } from '../agents/registry';
import { PolicyEngine } from '../policies/engine';
import { CircuitBreakerManager } from './circuit-breakers';
import { MemoryManager } from '../memory/manager';

interface AgentRequest {
  agentId: string;
  action: string;
  payload: any;
  priority: 'critical' | 'high' | 'medium' | 'low';
  requestId: string;
}

interface AgentResponse {
  success: boolean;
  data?: any;
  error?: string;
  confidence?: number;
}

export class Orchestrator {
  private agentRegistry: AgentRegistry;
  private policyEngine: PolicyEngine;
  private circuitBreakers: CircuitBreakerManager;
  private memoryManager: MemoryManager;
  private requestQueue: Map<string, AgentRequest[]>;

  constructor(
    agentRegistry: AgentRegistry,
    policyEngine: PolicyEngine,
    circuitBreakers: CircuitBreakerManager,
    memoryManager: MemoryManager
  ) {
    this.agentRegistry = agentRegistry;
    this.policyEngine = policyEngine;
    this.circuitBreakers = circuitBreakers;
    this.memoryManager = memoryManager;
    this.requestQueue = new Map();
  }

  async start(): Promise<void> {
    logger.info('Orchestrator starting...');
    // Initialize request queue processing
    logger.info('Orchestrator started successfully');
  }

  async stop(): Promise<void> {
    logger.info('Orchestrator stopping...');
    this.requestQueue.clear();
    logger.info('Orchestrator stopped');
  }

  async routeRequest(request: AgentRequest): Promise<AgentResponse> {
    try {
      // Log request for audit
      auditLogger.info('Agent request received', {
        requestId: request.requestId,
        agentId: request.agentId,
        priority: request.priority
      });

      // Check if circuit breaker is open
      if (this.circuitBreakers.isOpen(request.agentId)) {
        logger.warn(`Circuit breaker open for agent: ${request.agentId}`);
        return {
          success: false,
          error: 'Agent temporarily unavailable - circuit breaker open'
        };
      }

      // Validate against policies
      const policyCheck = await this.policyEngine.validate(request);
      if (!policyCheck.allowed) {
        return {
          success: false,
          error: `Policy violation: ${policyCheck.reason}`
        };
      }

      // Route to agent
      const agent = this.agentRegistry.getAgent(request.agentId);
      if (!agent) {
        return {
          success: false,
          error: `Agent not found: ${request.agentId}`
        };
      }

      // Execute agent logic (simplified for now)
      const response: AgentResponse = {
        success: true,
        data: { message: 'Agent executed successfully' },
        confidence: 0.85
      };

      // Log successful execution
      auditLogger.info('Agent request completed', {
        requestId: request.requestId,
        agentId: request.agentId,
        success: response.success
      });

      return response;
    } catch (error) {
      logger.error('Orchestrator error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
}
