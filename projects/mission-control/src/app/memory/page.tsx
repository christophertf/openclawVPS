import path from "node:path";
import {
    WORKSPACE_ROOT,
    safeRead,
    getMemoryFiles,
    formatBytes,
} from "@/app/lib/data";
import { PageHeader, EmptyState } from "@/app/components/ui";

export const dynamic = "force-dynamic";

export default async function MemoryPage() {
    const [memoryLong, changeFeedRaw] = await Promise.all([
        safeRead(path.join(WORKSPACE_ROOT, "docs/MEMORY.md")),
        safeRead(path.join(WORKSPACE_ROOT, "memory/change-feed.log")),
    ]);

    const memoryFiles = await getMemoryFiles();

    return (
        <div className="space-y-6">
            <PageHeader
                icon="🧠"
                title="Memory & Journal"
                subtitle="Long-term memory, daily journal entries, and change feed"
            />

            {/* Long-term Memory */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    📖 Long-Term Memory (MEMORY.md)
                </h2>
                {memoryLong ? (
                    <pre className="memory-log rounded-xl bg-zinc-950/50 p-4 border border-zinc-800/30 max-h-96 overflow-y-auto whitespace-pre-wrap">
                        {memoryLong}
                    </pre>
                ) : (
                    <EmptyState icon="📖" message="MEMORY.md not found" />
                )}
            </div>

            {/* Daily Journal Entries */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    📓 Daily Journal
                </h2>
                <p className="text-xs text-zinc-500 mb-4">
                    {memoryFiles.length} entries found in memory/
                </p>

                {memoryFiles.length === 0 ? (
                    <EmptyState icon="📓" message="No daily memory files found" />
                ) : (
                    <div className="space-y-3">
                        {memoryFiles.map((mf) => (
                            <details
                                key={mf.filename}
                                className="group rounded-xl bg-zinc-900/40 border border-zinc-800/30 hover:border-zinc-700/40 transition-colors"
                            >
                                <summary className="flex items-center justify-between cursor-pointer px-4 py-3">
                                    <div className="flex items-center gap-3">
                                        <span className="text-sm">📅</span>
                                        <span className="font-mono text-sm text-zinc-200">
                                            {mf.date}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <span className="text-[10px] text-zinc-600">
                                            {formatBytes(mf.size)}
                                        </span>
                                        <span className="text-[10px] text-zinc-600 font-mono">
                                            {mf.filename}
                                        </span>
                                        <span className="text-zinc-600 group-open:rotate-90 transition-transform">
                                            ▸
                                        </span>
                                    </div>
                                </summary>
                                <div className="px-4 pb-4">
                                    <pre className="memory-log rounded-lg bg-zinc-950/50 p-3 border border-zinc-800/20 max-h-64 overflow-y-auto whitespace-pre-wrap text-xs">
                                        {mf.preview}
                                        {mf.size > 300 && (
                                            <span className="text-zinc-600">
                                                {"\n\n"}... (preview truncated,{" "}
                                                {formatBytes(mf.size)} total)
                                            </span>
                                        )}
                                    </pre>
                                </div>
                            </details>
                        ))}
                    </div>
                )}
            </div>

            {/* Change Feed */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    📜 Change Feed Log
                </h2>
                {changeFeedRaw ? (
                    <pre className="memory-log rounded-xl bg-zinc-950/50 p-4 border border-zinc-800/30 max-h-72 overflow-y-auto whitespace-pre-wrap">
                        {changeFeedRaw}
                    </pre>
                ) : (
                    <EmptyState
                        icon="📜"
                        message="Change feed log not found"
                    />
                )}
            </div>
        </div>
    );
}
