interface Agent {
    id: string;
    name: string;
    type: string;
    status: 'active' | 'inactive';
}
export declare class AgentRegistry {
    private agents;
    constructor();
    loadAgents(): Promise<void>;
    registerAgent(agent: Agent): void;
    getAgent(agentId: string): Agent | undefined;
    getAgentCount(): number;
    getAllAgents(): Agent[];
}
export {};
//# sourceMappingURL=registry.d.ts.map