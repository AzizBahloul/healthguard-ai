"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.MCPServer = void 0;
const express_1 = __importDefault(require("express"));
const helmet_1 = __importDefault(require("helmet"));
const cors_1 = __importDefault(require("cors"));
const express_rate_limit_1 = __importDefault(require("express-rate-limit"));
const dotenv_1 = require("dotenv");
const logger_1 = require("./utils/logger");
const loader_1 = require("./config/loader");
const orchestrator_1 = require("./core/orchestrator");
const circuit_breakers_1 = require("./core/circuit-breakers");
const rate_limiters_1 = require("./core/rate-limiters");
const engine_1 = require("./policies/engine");
const registry_1 = require("./agents/registry");
const registry_2 = require("./tools/registry");
const manager_1 = require("./memory/manager");
const health_1 = require("./routes/health");
const agents_1 = require("./routes/agents");
const mcp_1 = require("./routes/mcp");
(0, dotenv_1.config)();
class MCPServer {
    app;
    port;
    orchestrator;
    circuitBreakers;
    rateLimiters;
    policyEngine;
    agentRegistry;
    toolRegistry;
    memoryManager;
    constructor() {
        this.app = (0, express_1.default)();
        this.port = parseInt(process.env.MCP_PORT || '3000', 10);
        // Initialize core components
        this.circuitBreakers = new circuit_breakers_1.CircuitBreakerManager();
        this.rateLimiters = new rate_limiters_1.RateLimiterManager();
        this.policyEngine = new engine_1.PolicyEngine();
        this.agentRegistry = new registry_1.AgentRegistry();
        this.toolRegistry = new registry_2.ToolRegistry();
        this.memoryManager = new manager_1.MemoryManager();
        this.orchestrator = new orchestrator_1.Orchestrator(this.agentRegistry, this.policyEngine, this.circuitBreakers, this.memoryManager);
    }
    async initialize() {
        try {
            logger_1.logger.info('Initializing HealthGuard MCP Server...');
            // Load configuration
            await (0, loader_1.loadConfig)();
            // Setup middleware
            this.setupMiddleware();
            // Initialize components
            await this.initializeComponents();
            // Setup routes
            this.setupRoutes();
            // Setup error handling
            this.setupErrorHandling();
            logger_1.logger.info('MCP Server initialized successfully');
        }
        catch (error) {
            logger_1.logger.error('Failed to initialize MCP Server:', error);
            throw error;
        }
    }
    setupMiddleware() {
        // Security
        this.app.use((0, helmet_1.default)());
        // CORS
        this.app.use((0, cors_1.default)({
            origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:5173'],
            credentials: true
        }));
        // Body parsing
        this.app.use(express_1.default.json({ limit: '10mb' }));
        this.app.use(express_1.default.urlencoded({ extended: true, limit: '10mb' }));
        // Request logging
        this.app.use((req, res, next) => {
            logger_1.logger.info(`${req.method} ${req.path}`, {
                ip: req.ip,
                userAgent: req.get('user-agent')
            });
            next();
        });
        // Global rate limiting
        const globalLimiter = (0, express_rate_limit_1.default)({
            windowMs: 60 * 1000, // 1 minute
            max: 1000,
            message: 'Too many requests from this IP, please try again later.'
        });
        this.app.use(globalLimiter);
    }
    async initializeComponents() {
        // Initialize circuit breakers
        await this.circuitBreakers.initialize();
        logger_1.logger.info('Circuit breakers initialized');
        // Initialize rate limiters
        await this.rateLimiters.initialize();
        logger_1.logger.info('Rate limiters initialized');
        // Load policies
        await this.policyEngine.loadPolicies();
        logger_1.logger.info('Policies loaded');
        // Register agents
        await this.agentRegistry.loadAgents();
        logger_1.logger.info(`Loaded ${this.agentRegistry.getAgentCount()} agents`);
        // Register tools
        await this.toolRegistry.loadTools();
        logger_1.logger.info(`Loaded ${this.toolRegistry.getToolCount()} tools`);
        // Initialize memory systems
        await this.memoryManager.initialize();
        logger_1.logger.info('Memory systems initialized');
        // Start orchestrator
        await this.orchestrator.start();
        logger_1.logger.info('Orchestrator started');
    }
    setupRoutes() {
        // Health check
        this.app.use('/health', health_1.healthRouter);
        // Agent management
        this.app.use('/api/v1/agents', (0, agents_1.agentRouter)(this.agentRegistry));
        // MCP protocol endpoints
        this.app.use('/api/v1/mcp', (0, mcp_1.mcpRouter)(this.orchestrator));
        // Root endpoint
        this.app.get('/', (req, res) => {
            res.json({
                name: 'HealthGuard MCP Server',
                version: '1.0.0',
                status: 'operational',
                endpoints: {
                    health: '/health',
                    agents: '/api/v1/agents',
                    mcp: '/api/v1/mcp',
                    docs: '/api/docs'
                }
            });
        });
    }
    setupErrorHandling() {
        // 404 handler
        this.app.use((req, res) => {
            res.status(404).json({
                error: 'Not Found',
                message: `Route ${req.method} ${req.path} not found`
            });
        });
        // Global error handler
        this.app.use((err, req, res, next) => {
            logger_1.logger.error('Unhandled error:', err);
            res.status(500).json({
                error: 'Internal Server Error',
                message: process.env.NODE_ENV === 'development' ? err.message : 'An unexpected error occurred',
                ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
            });
        });
    }
    async start() {
        await this.initialize();
        this.app.listen(this.port, () => {
            logger_1.logger.info(`🏥 HealthGuard MCP Server running on port ${this.port}`);
            logger_1.logger.info(`📊 Health check: http://localhost:${this.port}/health`);
            logger_1.logger.info(`🤖 Agents: ${this.agentRegistry.getAgentCount()}`);
            logger_1.logger.info(`🛠️  Tools: ${this.toolRegistry.getToolCount()}`);
        });
    }
    async shutdown() {
        logger_1.logger.info('Shutting down MCP Server...');
        try {
            await this.orchestrator.stop();
            await this.memoryManager.shutdown();
            logger_1.logger.info('MCP Server shut down gracefully');
            process.exit(0);
        }
        catch (error) {
            logger_1.logger.error('Error during shutdown:', error);
            process.exit(1);
        }
    }
}
exports.MCPServer = MCPServer;
// Main execution
const server = new MCPServer();
// Handle shutdown signals
process.on('SIGTERM', () => server.shutdown());
process.on('SIGINT', () => server.shutdown());
// Start server
server.start().catch((error) => {
    logger_1.logger.error('Failed to start MCP Server:', error);
    process.exit(1);
});
//# sourceMappingURL=index.js.map