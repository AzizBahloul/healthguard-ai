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
export declare class Orchestrator {
    private agentRegistry;
    private policyEngine;
    private circuitBreakers;
    private memoryManager;
    private requestQueue;
    constructor(agentRegistry: AgentRegistry, policyEngine: PolicyEngine, circuitBreakers: CircuitBreakerManager, memoryManager: MemoryManager);
    start(): Promise<void>;
    stop(): Promise<void>;
    routeRequest(request: AgentRequest): Promise<AgentResponse>;
}
export {};
//# sourceMappingURL=orchestrator.d.ts.map