import path from "node:path";
import {
    WORKSPACE_ROOT,
    safeRead,
    parseChangeFeed,
} from "@/app/lib/data";
import { PageHeader, EmptyState } from "@/app/components/ui";

export const dynamic = "force-dynamic";

export default async function ActivityPage() {
    const changeFeedRaw = await safeRead(
        path.join(WORKSPACE_ROOT, "memory/change-feed.log")
    );

    const entries = changeFeedRaw
        ? parseChangeFeed(changeFeedRaw).reverse()
        : [];

    // Group by date
    const grouped: Record<
        string,
        { timestamp: string; actor: string; description: string }[]
    > = {};
    for (const e of entries) {
        const date = e.timestamp.split("T")[0] || "Unknown";
        if (!grouped[date]) grouped[date] = [];
        grouped[date].push(e);
    }

    return (
        <div className="space-y-6">
            <PageHeader
                icon="📡"
                title="Live Feed"
                subtitle={`${entries.length} total change feed entries`}
            />

            {entries.length === 0 ? (
                <div className="glass-card p-8">
                    <EmptyState icon="📡" message="No activity entries found" />
                </div>
            ) : (
                Object.entries(grouped).map(([date, items]) => (
                    <div key={date} className="glass-card p-6">
                        <h2 className="flex items-center gap-3 text-base font-bold mb-4">
                            <span className="font-mono text-cyan-400">{date}</span>
                            <span className="text-xs text-zinc-600 font-normal">
                                {items.length} event{items.length !== 1 ? "s" : ""}
                            </span>
                        </h2>
                        <div className="space-y-0">
                            {items.map((entry, i) => (
                                <div key={i} className="timeline-item">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span
                                            className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${entry.actor === "CLAW"
                                                    ? "bg-cyan-500/15 text-cyan-400"
                                                    : entry.actor === "Antigravity"
                                                        ? "bg-purple-500/15 text-purple-400"
                                                        : "bg-zinc-700/50 text-zinc-400"
                                                }`}
                                        >
                                            {entry.actor}
                                        </span>
                                        <span className="font-mono text-[10px] text-zinc-600">
                                            {entry.timestamp.split("T")[1]?.replace("Z", "")}
                                        </span>
                                    </div>
                                    <p className="text-sm text-zinc-400 leading-relaxed">
                                        {entry.description}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                ))
            )}
        </div>
    );
}
