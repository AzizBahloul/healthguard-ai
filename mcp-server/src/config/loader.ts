import * as yaml from 'yaml';
import * as fs from 'fs/promises';
import { logger } from '../utils/logger';

export async function loadConfig(): Promise<void> {
  try {
    const configPath = './core/mcp.config.yaml';
    const configFile = await fs.readFile(configPath, 'utf-8');
    const config = yaml.parse(configFile);
    
    // Store config in process.env or global state
    logger.info('Configuration loaded successfully');
  } catch (error) {
    logger.error('Failed to load configuration:', error);
    throw error;
  }
}
