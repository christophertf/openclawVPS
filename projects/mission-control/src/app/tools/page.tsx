import path from "node:path";
import {
    WORKSPACE_ROOT,
    safeRead,
} from "@/app/lib/data";
import { PageHeader } from "@/app/components/ui";

export const dynamic = "force-dynamic";

export default async function ToolsPage() {
    const [toolsRaw, stockRaw, stockCapRaw] = await Promise.all([
        safeRead(path.join(WORKSPACE_ROOT, "TOOLS.md")),
        safeRead(path.join(WORKSPACE_ROOT, "STOCK-STUFF.md")),
        safeRead(
            path.join(WORKSPACE_ROOT, "STOCK-CAPABILITY-MAP.md")
        ),
    ]);

    // Parse stock skills from STOCK-STUFF.md
    const skills: { name: string; status: string }[] = [];
    if (stockRaw) {
        const skillSection = stockRaw.match(
            /## 3\) Stock skills.*?\n([\s\S]*?)(?=\n## |\n$)/
        );
        if (skillSection) {
            const lines = skillSection[1].split("\n");
            for (const line of lines) {
                const match = line.match(
                    /- `(\w[\w-]*)`.+?\((\w[\w\s/,-]*)\)/
                );
                if (match) {
                    skills.push({
                        name: match[1],
                        status: match[2].trim(),
                    });
                }
            }
        }
    }

    // Parse capability families
    const capFamilies: { name: string; items: string[] }[] = [];
    if (stockCapRaw) {
        const sections = stockCapRaw.split(/^## /m).slice(1);
        for (const section of sections.slice(0, 5)) {
            const title = section.split("\n")[0].trim();
            const items = section
                .split("\n")
                .filter((l) => l.trim().startsWith("- "))
                .map((l) => l.replace(/^-\s+/, "").trim());
            if (items.length > 0) {
                capFamilies.push({ name: title, items });
            }
        }
    }

    return (
        <div className="space-y-6">
            <PageHeader
                icon="🔧"
                title="Tools & Capabilities"
                subtitle="Local configuration, stock skills, and capability inventory"
            />

            {/* Skills Grid */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    🧩 Stock Skills
                </h2>
                <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                    {skills.map((s) => {
                        const isConfirmed = s.status
                            .toLowerCase()
                            .includes("confirmed");
                        const isPass = s.status.toLowerCase().includes("pass");
                        const isReady = s.status.toLowerCase().includes("ready");
                        return (
                            <div
                                key={s.name}
                                className="flex items-center justify-between rounded-xl bg-zinc-900/40 border border-zinc-800/30 px-4 py-3 hover:border-zinc-700/40 transition-colors"
                            >
                                <span className="font-mono text-sm text-zinc-200">
                                    {s.name}
                                </span>
                                <span
                                    className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${isConfirmed || isPass
                                            ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20"
                                            : isReady
                                                ? "bg-cyan-500/15 text-cyan-400 border border-cyan-500/20"
                                                : "bg-amber-500/15 text-amber-400 border border-amber-500/20"
                                        }`}
                                >
                                    {s.status}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Capability Families */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    🗺️ Capability Map
                </h2>
                <div className="grid gap-4 md:grid-cols-2">
                    {capFamilies.map((fam) => (
                        <div
                            key={fam.name}
                            className="rounded-xl bg-zinc-900/40 border border-zinc-800/30 p-4"
                        >
                            <h3 className="text-sm font-semibold text-zinc-200 mb-2">
                                {fam.name}
                            </h3>
                            <ul className="space-y-1">
                                {fam.items.map((item, i) => {
                                    const confirmed = item
                                        .toLowerCase()
                                        .includes("confirmed");
                                    const ready = item
                                        .toLowerCase()
                                        .includes("ready");
                                    const blocked = item
                                        .toLowerCase()
                                        .includes("blocked");
                                    return (
                                        <li
                                            key={i}
                                            className="flex items-start gap-2 text-xs text-zinc-400"
                                        >
                                            <span className="mt-0.5">
                                                {confirmed
                                                    ? "🟢"
                                                    : ready
                                                        ? "🔵"
                                                        : blocked
                                                            ? "🔴"
                                                            : "⚪"}
                                            </span>
                                            <span>{item}</span>
                                        </li>
                                    );
                                })}
                            </ul>
                        </div>
                    ))}
                </div>
            </div>

            {/* Local Tools Config */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    🔧 Local Configuration (TOOLS.md)
                </h2>
                <pre className="memory-log rounded-xl bg-zinc-950/50 p-4 border border-zinc-800/30 max-h-72 overflow-y-auto whitespace-pre-wrap">
                    {toolsRaw ?? "TOOLS.md not found."}
                </pre>
            </div>
        </div>
    );
}
