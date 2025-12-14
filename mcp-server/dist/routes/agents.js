"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.agentRouter = agentRouter;
const express_1 = require("express");
function agentRouter(registry) {
    const router = (0, express_1.Router)();
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
//# sourceMappingURL=agents.js.map