import { Router } from 'express';
import { AgentRegistry } from '../agents/registry';

export function agentRouter(registry: AgentRegistry): Router {
  const router = Router();

  router.get('/', (req, res) => {
    const agents = registry.getAllAgents();
    res.json({
      agents,
      total: agents.length
    });
  });

  router.get('/:agentId', (req, res) => {
    const agent = registry.getAgent(req.params.agentId);
    if (!agent) {
      return res.status(404).json({ error: 'Agent not found' });
    }
    res.json(agent);
  });

  return router;
}
