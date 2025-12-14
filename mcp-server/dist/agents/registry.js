"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.AgentRegistry = void 0;
const logger_1 = require("../utils/logger");
const fs = __importStar(require("fs/promises"));
const path = __importStar(require("path"));
class AgentRegistry {
    agents;
    constructor() {
        this.agents = new Map();
    }
    async loadAgents() {
        logger_1.logger.info('Loading agents...');
        try {
            const agentDirs = ['critical', 'operational', 'predictive', 'coordination'];
            let totalAgents = 0;
            for (const dir of agentDirs) {
                const agentPath = path.join(process.cwd(), 'agents', dir);
                try {
                    const files = await fs.readdir(agentPath);
                    totalAgents += files.filter((f) => f.endsWith('.agent.yaml')).length;
                }
                catch (error) {
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
            logger_1.logger.info(`Registered ${this.agents.size} agents`);
        }
        catch (error) {
            logger_1.logger.warn('Could not load agents from directory, using defaults');
        }
    }
    registerAgent(agent) {
        this.agents.set(agent.id, agent);
    }
    getAgent(agentId) {
        return this.agents.get(agentId);
    }
    getAgentCount() {
        return this.agents.size;
    }
    getAllAgents() {
        return Array.from(this.agents.values());
    }
}
exports.AgentRegistry = AgentRegistry;
//# sourceMappingURL=registry.js.map