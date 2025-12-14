"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ToolRegistry = void 0;
const logger_1 = require("../utils/logger");
class ToolRegistry {
    tools;
    constructor() {
        this.tools = new Map();
    }
    async loadTools() {
        logger_1.logger.info('Loading tools...');
        // Register sample tools
        this.tools.set('hospital_state', { type: 'sensor' });
        this.tools.set('alert_dispatcher', { type: 'actuator' });
        this.tools.set('data_validator', { type: 'validator' });
        logger_1.logger.info(`Loaded ${this.tools.size} tools`);
    }
    getToolCount() {
        return this.tools.size;
    }
}
exports.ToolRegistry = ToolRegistry;
//# sourceMappingURL=registry.js.map