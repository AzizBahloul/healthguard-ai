export declare class CircuitBreakerManager {
    private breakers;
    constructor();
    initialize(): Promise<void>;
    isOpen(agentId: string): boolean;
    recordSuccess(agentId: string): void;
    recordFailure(agentId: string): void;
    private createBreaker;
}
//# sourceMappingURL=circuit-breakers.d.ts.map