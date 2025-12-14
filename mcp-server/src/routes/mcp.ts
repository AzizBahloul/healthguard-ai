import { Router } from 'express';
import { Orchestrator } from '../core/orchestrator';
import { v4 as uuidv4 } from 'uuid';

export function mcpRouter(orchestrator: Orchestrator): Router {
  const router = Router();

  router.post('/execute', async (req, res) => {
    try {
      const { agentId, action, payload, priority = 'medium' } = req.body;

      if (!agentId || !action) {
        return res.status(400).json({
          error: 'Missing required fields: agentId and action'
        });
      }

      const request = {
        agentId,
        action,
        payload,
        priority,
        requestId: uuidv4()
      };

      const response = await orchestrator.routeRequest(request);
      
      res.json(response);
    } catch (error) {
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Internal server error'
      });
    }
  });

  router.get('/status', (req, res) => {
    res.json({
      status: 'operational',
      timestamp: new Date().toISOString()
    });
  });

  return router;
}
