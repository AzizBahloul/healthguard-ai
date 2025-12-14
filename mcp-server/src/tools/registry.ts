import { logger } from '../utils/logger';

export class ToolRegistry {
  private tools: Map<string, any>;

  constructor() {
    this.tools = new Map();
  }

  async loadTools(): Promise<void> {
    logger.info('Loading tools...');
    
    // Register sample tools
    this.tools.set('hospital_state', { type: 'sensor' });
    this.tools.set('alert_dispatcher', { type: 'actuator' });
    this.tools.set('data_validator', { type: 'validator' });

    logger.info(`Loaded ${this.tools.size} tools`);
  }

  getToolCount(): number {
    return this.tools.size;
  }
}
