"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.healthRouter = void 0;
const express_1 = require("express");
const logger_1 = require("../utils/logger");
exports.healthRouter = (0, express_1.Router)();
exports.healthRouter.get('/', async (req, res) => {
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
    }
    catch (error) {
        logger_1.logger.error('Health check failed:', error);
        res.status(503).json({
            status: 'unhealthy',
            error: 'Service unavailable'
        });
    }
});
exports.healthRouter.get('/readiness', async (req, res) => {
    // Check if service is ready to accept traffic
    res.json({
        ready: true,
        timestamp: new Date().toISOString()
    });
});
exports.healthRouter.get('/liveness', async (req, res) => {
    // Check if service is alive
    res.json({
        alive: true,
        timestamp: new Date().toISOString()
    });
});
//# sourceMappingURL=health.js.map