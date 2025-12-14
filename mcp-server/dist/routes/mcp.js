"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.mcpRouter = mcpRouter;
const express_1 = require("express");
const uuid_1 = require("uuid");
function mcpRouter(orchestrator) {
    const router = (0, express_1.Router)();
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
                requestId: (0, uuid_1.v4)()
            };
            const response = await orchestrator.routeRequest(request);
            res.json(response);
        }
        catch (error) {
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
//# sourceMappingURL=mcp.js.map