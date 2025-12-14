import { logger } from '../utils/logger';
import * as fs from 'fs/promises';
import * as path from 'path';

interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'inactive';
}

export class AgentRegistry {
  private agents: Map<string, Agent>;

  constructor() {
    this.agents = new Map();
  }

  async loadAgents(): Promise<void> {
    logger.info('Loading agents...');
    
    try {
      const agentDirs = ['critical', 'operational', 'predictive', 'coordination'];
      let totalAgents = 0;

      for (const dir of agentDirs) {
        const agentPath = path.join(process.cwd(), 'agents', dir);
        try {
          const files = await fs.readdir(agentPath);
          totalAgents += files.filter((f: string) => f.endsWith('.agent.yaml')).length;
        } catch (error) {
          // Directory might not exist yet
        }
      }

      // Register sample agents
      this.registerAgent({
        id: 'trauma_coordinator',
        name: 'Trauma Coordinator',
        type: 'critical',
        status: 'active'
      });

      this.registerAgent({
        id: 'bed_orchestrator',
        name: 'Bed Orchestrator',
        type: 'operational',
        status: 'active'
      });

      logger.info(`Registered ${this.agents.size} agents`);
    } catch (error) {
      logger.warn('Could not load agents from directory, using defaults');
    }
  }

  registerAgent(agent: Agent): void {
    this.agents.set(agent.id, agent);
  }

  getAgent(agentId: string): Agent | undefined {
    return this.agents.get(agentId);
  }

  getAgentCount(): number {
    return this.agents.size;
  }

  getAllAgents(): Agent[] {
    return Array.from(this.agents.values());
  }
}
