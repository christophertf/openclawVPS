import path from "node:path";
import {
    WORKSPACE_ROOT,
    safeRead,
} from "@/app/lib/data";
import { PageHeader } from "@/app/components/ui";

export const dynamic = "force-dynamic";

export default async function AgentsPage() {
    const [agentsRaw, soulRaw, identityRaw, userRaw, capRaw] =
        await Promise.all([
            safeRead(path.join(WORKSPACE_ROOT, "AGENTS.md")),
            safeRead(path.join(WORKSPACE_ROOT, "SOUL.md")),
            safeRead(path.join(WORKSPACE_ROOT, "IDENTITY.md")),
            safeRead(path.join(WORKSPACE_ROOT, "USER.md")),
            safeRead(
                path.join(WORKSPACE_ROOT, "STOCK-CAPABILITY-MAP.md")
            ),
        ]);

    const sections = [
        {
            title: "Identity",
            icon: "🐾",
            content: identityRaw,
            file: "IDENTITY.md",
        },
        {
            title: "Soul",
            icon: "💫",
            content: soulRaw,
            file: "SOUL.md",
        },
        {
            title: "User Profile",
            icon: "👤",
            content: userRaw,
            file: "USER.md",
        },
        {
            title: "Agent Rules",
            icon: "📜",
            content: agentsRaw,
            file: "AGENTS.md",
        },
        {
            title: "Capability Map",
            icon: "🗺️",
            content: capRaw,
            file: "STOCK-CAPABILITY-MAP.md",
        },
    ];

    return (
        <div className="space-y-6">
            <PageHeader
                icon="🤖"
                title="Agents & Identity"
                subtitle="Who CLAW is, operating rules, and capability inventory"
            />

            {/* Quick cards for Identity + User */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {sections.slice(0, 3).map((s) => (
                    <div key={s.file} className="glass-card p-5">
                        <h2 className="flex items-center gap-2 text-base font-bold mb-3">
                            <span>{s.icon}</span> {s.title}
                        </h2>
                        <pre className="memory-log rounded-lg bg-zinc-950/50 p-3 border border-zinc-800/30 max-h-48 overflow-y-auto whitespace-pre-wrap text-xs">
                            {s.content ?? "File not found."}
                        </pre>
                        <p className="mt-2 text-[10px] font-mono text-zinc-600">
                            {s.file}
                        </p>
                    </div>
                ))}
            </div>

            {/* Larger sections */}
            {sections.slice(3).map((s) => (
                <div key={s.file} className="glass-card p-6">
                    <h2 className="section-header flex items-center gap-2 text-lg font-bold mb-4">
                        <span>{s.icon}</span> {s.title}
                    </h2>
                    <pre className="memory-log rounded-xl bg-zinc-950/50 p-4 border border-zinc-800/30 max-h-96 overflow-y-auto whitespace-pre-wrap">
                        {s.content ?? "File not found."}
                    </pre>
                    <p className="mt-2 text-[10px] font-mono text-zinc-600">
                        {s.file}
                    </p>
                </div>
            ))}
        </div>
    );
}
