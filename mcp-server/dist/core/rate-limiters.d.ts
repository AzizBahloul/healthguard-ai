export declare class RateLimiterManager {
    private limiters;
    constructor();
    initialize(): Promise<void>;
    checkLimit(key: string): boolean;
}
//# sourceMappingURL=rate-limiters.d.ts.map