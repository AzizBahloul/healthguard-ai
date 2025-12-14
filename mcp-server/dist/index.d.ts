declare class MCPServer {
    private app;
    private port;
    private orchestrator;
    private circuitBreakers;
    private rateLimiters;
    private policyEngine;
    private agentRegistry;
    private toolRegistry;
    private memoryManager;
    constructor();
    initialize(): Promise<void>;
    private setupMiddleware;
    private initializeComponents;
    private setupRoutes;
    private setupErrorHandling;
    start(): Promise<void>;
    shutdown(): Promise<void>;
}
export { MCPServer };
//# sourceMappingURL=index.d.ts.map