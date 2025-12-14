export declare class MemoryManager {
    private shortTerm;
    private midTerm;
    private longTerm;
    constructor();
    initialize(): Promise<void>;
    shutdown(): Promise<void>;
    store(key: string, value: any, duration?: 'short' | 'mid' | 'long'): void;
    retrieve(key: string): any;
}
//# sourceMappingURL=manager.d.ts.map