interface PolicyValidationResult {
    allowed: boolean;
    reason?: string;
}
export declare class PolicyEngine {
    private policies;
    constructor();
    loadPolicies(): Promise<void>;
    validate(request: any): Promise<PolicyValidationResult>;
}
export {};
//# sourceMappingURL=engine.d.ts.map