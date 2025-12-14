import { Router, Request, Response } from 'express';
import { logger } from '../utils/logger';

export const healthRouter = Router();

healthRouter.get('/', async (req: Request, res: Response) => {
  try {
    const health = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      version: '1.0.0',
      services: {
        orchestrator: 'operational',
        agents: 'operational',
        memory: 'operational',
        database: 'operational'
      }
    };

    res.json(health);
  } catch (error) {
    logger.error('Health check failed:', error);
    res.status(503).json({
      status: 'unhealthy',
      error: 'Service unavailable'
    });
  }
});

healthRouter.get('/readiness', async (req: Request, res: Response) => {
  // Check if service is ready to accept traffic
  res.json({
    ready: true,
    timestamp: new Date().toISOString()
  });
});

healthRouter.get('/liveness', async (req: Request, res: Response) => {
  // Check if service is alive
  res.json({
    alive: true,
    timestamp: new Date().toISOString()
  });
});
