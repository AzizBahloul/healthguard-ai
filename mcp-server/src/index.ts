import express, { Express, Request, Response, NextFunction } from 'express';
import helmet from 'helmet';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import { config } from 'dotenv';
import { logger } from './utils/logger';
import { loadConfig } from './config/loader';
import { Orchestrator } from './core/orchestrator';
import { CircuitBreakerManager } from './core/circuit-breakers';
import { RateLimiterManager } from './core/rate-limiters';
import { PolicyEngine } from './policies/engine';
import { AgentRegistry } from './agents/registry';
import { ToolRegistry } from './tools/registry';
import { MemoryManager } from './memory/manager';
import { healthRouter } from './routes/health';
import { agentRouter } from './routes/agents';
import { mcpRouter } from './routes/mcp';

config();

class MCPServer {
  private app: Express;
  private port: number;
  private orchestrator: Orchestrator;
  private circuitBreakers: CircuitBreakerManager;
  private rateLimiters: RateLimiterManager;
  private policyEngine: PolicyEngine;
  private agentRegistry: AgentRegistry;
  private toolRegistry: ToolRegistry;
  private memoryManager: MemoryManager;

  constructor() {
    this.app = express();
    this.port = parseInt(process.env.MCP_PORT || '3000', 10);
    
    // Initialize core components
    this.circuitBreakers = new CircuitBreakerManager();
    this.rateLimiters = new RateLimiterManager();
    this.policyEngine = new PolicyEngine();
    this.agentRegistry = new AgentRegistry();
    this.toolRegistry = new ToolRegistry();
    this.memoryManager = new MemoryManager();
    this.orchestrator = new Orchestrator(
      this.agentRegistry,
      this.policyEngine,
      this.circuitBreakers,
      this.memoryManager
    );
  }

  async initialize(): Promise<void> {
    try {
      logger.info('Initializing HealthGuard MCP Server...');

      // Load configuration
      await loadConfig();

      // Setup middleware
      this.setupMiddleware();

      // Initialize components
      await this.initializeComponents();

      // Setup routes
      this.setupRoutes();

      // Setup error handling
      this.setupErrorHandling();

      logger.info('MCP Server initialized successfully');
    } catch (error) {
      logger.error('Failed to initialize MCP Server:', error);
      throw error;
    }
  }

  private setupMiddleware(): void {
    // Security
    this.app.use(helmet());

    // CORS
    this.app.use(cors({
      origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:5173'],
      credentials: true
    }));

    // Body parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // Request logging
    this.app.use((req: Request, res: Response, next: NextFunction) => {
      logger.info(`${req.method} ${req.path}`, {
        ip: req.ip,
        userAgent: req.get('user-agent')
      });
      next();
    });

    // Global rate limiting
    const globalLimiter = rateLimit({
      windowMs: 60 * 1000, // 1 minute
      max: 1000,
      message: 'Too many requests from this IP, please try again later.'
    });
    this.app.use(globalLimiter);
  }

  private async initializeComponents(): Promise<void> {
    // Initialize circuit breakers
    await this.circuitBreakers.initialize();
    logger.info('Circuit breakers initialized');

    // Initialize rate limiters
    await this.rateLimiters.initialize();
    logger.info('Rate limiters initialized');

    // Load policies
    await this.policyEngine.loadPolicies();
    logger.info('Policies loaded');

    // Register agents
    await this.agentRegistry.loadAgents();
    logger.info(`Loaded ${this.agentRegistry.getAgentCount()} agents`);

    // Register tools
    await this.toolRegistry.loadTools();
    logger.info(`Loaded ${this.toolRegistry.getToolCount()} tools`);

    // Initialize memory systems
    await this.memoryManager.initialize();
    logger.info('Memory systems initialized');

    // Start orchestrator
    await this.orchestrator.start();
    logger.info('Orchestrator started');
  }

  private setupRoutes(): void {
    // Health check
    this.app.use('/health', healthRouter);

    // Agent management
    this.app.use('/api/v1/agents', agentRouter(this.agentRegistry));

    // MCP protocol endpoints
    this.app.use('/api/v1/mcp', mcpRouter(this.orchestrator));

    // Root endpoint
    this.app.get('/', (req: Request, res: Response) => {
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

  private setupErrorHandling(): void {
    // 404 handler
    this.app.use((req: Request, res: Response) => {
      res.status(404).json({
        error: 'Not Found',
        message: `Route ${req.method} ${req.path} not found`
      });
    });

    // Global error handler
    this.app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
      logger.error('Unhandled error:', err);
      
      res.status(500).json({
        error: 'Internal Server Error',
        message: process.env.NODE_ENV === 'development' ? err.message : 'An unexpected error occurred',
        ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
      });
    });
  }

  async start(): Promise<void> {
    await this.initialize();

    this.app.listen(this.port, () => {
      logger.info(`🏥 HealthGuard MCP Server running on port ${this.port}`);
      logger.info(`📊 Health check: http://localhost:${this.port}/health`);
      logger.info(`🤖 Agents: ${this.agentRegistry.getAgentCount()}`);
      logger.info(`🛠️  Tools: ${this.toolRegistry.getToolCount()}`);
    });
  }

  async shutdown(): Promise<void> {
    logger.info('Shutting down MCP Server...');

    try {
      await this.orchestrator.stop();
      await this.memoryManager.shutdown();
      logger.info('MCP Server shut down gracefully');
      process.exit(0);
    } catch (error) {
      logger.error('Error during shutdown:', error);
      process.exit(1);
    }
  }
}

// Main execution
const server = new MCPServer();

// Handle shutdown signals
process.on('SIGTERM', () => server.shutdown());
process.on('SIGINT', () => server.shutdown());

// Start server
server.start().catch((error) => {
  logger.error('Failed to start MCP Server:', error);
  process.exit(1);
});

export { MCPServer };
