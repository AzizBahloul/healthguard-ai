"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MemoryManager = void 0;
const logger_1 = require("../utils/logger");
class MemoryManager {
    shortTerm;
    midTerm;
    longTerm;
    constructor() {
        this.shortTerm = new Map();
        this.midTerm = new Map();
        this.longTerm = new Map();
    }
    async initialize() {
        logger_1.logger.info('Initializing memory systems...');
        // Initialize vector stores, graph memory, etc.
        logger_1.logger.info('Memory systems initialized');
    }
    async shutdown() {
        logger_1.logger.info('Shutting down memory systems...');
        this.shortTerm.clear();
        this.midTerm.clear();
        logger_1.logger.info('Memory systems shut down');
    }
    store(key, value, duration = 'short') {
        switch (duration) {
            case 'short':
                this.shortTerm.set(key, value);
                break;
            case 'mid':
                this.midTerm.set(key, value);
                break;
            case 'long':
                this.longTerm.set(key, value);
                break;
        }
    }
    retrieve(key) {
        return this.shortTerm.get(key) || this.midTerm.get(key) || this.longTerm.get(key);
    }
}
exports.MemoryManager = MemoryManager;
//# sourceMappingURL=manager.js.map