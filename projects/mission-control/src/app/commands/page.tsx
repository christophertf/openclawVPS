import { getProjectRegistry } from "@/app/lib/data";
import { PageHeader } from "@/app/components/ui";

export const dynamic = "force-dynamic";

type Command = {
    command: string;
    description: string;
    what_happens: string[];
    example?: string;
    category: "project" | "channel" | "system" | "query";
};

const COMMANDS: Command[] = [
    // ── Project Commands ──
    {
        command: "Create new project",
        description: "Spin up a new project with a linked Discord channel",
        what_happens: [
            "Creates projects/<project-name>/ folder in workspace",
            "Adds a README.md with project overview",
            "Registers in projects.json with channel mapping",
            "Links to specified Discord channel (new or existing)",
            "Project appears in Mission Control automatically",
        ],
        example: '"Hey CLAW, create a new project called budget-analysis and link it to #budget"',
        category: "project",
    },
    {
        command: "Link channel to project",
        description: "Map an existing Discord channel to an existing project folder",
        what_happens: [
            "Updates projects.json with the channel↔project mapping",
            "CLAW scopes file reads/writes to that project when working in that channel",
            "Multiple projects can share a channel (e.g. #case-research)",
        ],
        example: '"Link #case-research to the appeal_alignment project"',
        category: "channel",
    },
    {
        command: "Unlink channel",
        description: "Remove the channel↔project mapping without deleting anything",
        what_happens: [
            "Removes the channel entry from projects.json",
            "Project folder and files remain untouched",
            "Channel continues to exist on Discord",
        ],
        example: '"Unlink #old-channel from the project"',
        category: "channel",
    },
    {
        command: "Archive project",
        description: "Mark a project as archived — keeps files, stops active work",
        what_happens: [
            "Sets status to \"archived\" in projects.json",
            "Project still visible in Mission Control but grayed out",
            "No new work will be done unless explicitly reactivated",
        ],
        example: '"Archive the appeal_alignment project"',
        category: "project",
    },
    {
        command: "Show project status",
        description: "Quick summary of a specific project or all projects",
        what_happens: [
            "CLAW reads the project README, recent files, and registry",
            "Returns: file count, linked channel, start date, last activity",
        ],
        example: '"What\'s the status of forensic_cpra_engine?"',
        category: "query",
    },
    // ── System Commands ──
    {
        command: "Run heartbeat",
        description: "Manually trigger the heartbeat check cycle",
        what_happens: [
            "CLAW reads HEARTBEAT.md for pending tasks",
            "Checks all watchdog/cron health",
            "Reports status or executes due tasks",
        ],
        example: '"Run heartbeat now"',
        category: "system",
    },
    {
        command: "Write to journal",
        description: "Add an entry to today's daily memory file",
        what_happens: [
            "Appends to memory/YYYY-MM-DD.md (creates if needed)",
            "Timestamped entry with context",
            "Visible in Mission Control → Memory & Journal",
        ],
        example: '"Log that we finished the Stage 1 claims pass today"',
        category: "system",
    },
    {
        command: "Update memory",
        description: "Add or modify long-term memory in MEMORY.md",
        what_happens: [
            "CLAW edits MEMORY.md with new persistent context",
            "Only done in main sessions (security: no shared contexts)",
            "Survives session restarts — this is CLAW's long-term brain",
        ],
        example: '"Remember that Chris prefers 24-hour time"',
        category: "system",
    },
    {
        command: "Show system health",
        description: "Quick health check of all core systems",
        what_happens: [
            "Checks: MEMORY.md, HEARTBEAT.md, daily memory, pipeline, change feed, git",
            "Reports pass/warn/fail for each",
            "Same data shown on Mission Control dashboard",
        ],
        example: '"Health check" or "System status"',
        category: "system",
    },
    {
        command: "Spawn sub-agent",
        description: "Launch an isolated worker for a specific task",
        what_happens: [
            "Creates a separate session with scoped context",
            "Worker operates independently, delivers output to a channel",
            "Does NOT have access to MEMORY.md (security)",
            "Use when: task needs isolation, would clutter main session, or needs parallel execution",
        ],
        example: '"Spawn a sub-agent to research court filing deadlines and post results in #case-research"',
        category: "system",
    },
    // ── Query Commands ──
    {
        command: "List projects",
        description: "Show all registered projects with their channels and status",
        what_happens: [
            "Reads projects.json registry",
            "Returns table of: project, channel, status, start date",
        ],
        example: '"List all projects" or "What projects do I have?"',
        category: "query",
    },
    {
        command: "Show change feed",
        description: "Recent activity across the workspace",
        what_happens: [
            "Reads memory/change-feed.log",
            "Returns last N entries with actor, timestamp, description",
        ],
        example: '"What happened today?" or "Show recent activity"',
        category: "query",
    },
    {
        command: "Show cron jobs",
        description: "List all scheduled automation tasks",
        what_happens: [
            "Reads crontab and state/ directory",
            "Returns: job name, schedule, command, last run status",
        ],
        example: '"What cron jobs are running?"',
        category: "query",
    },
];

const CATEGORY_META: Record<string, { icon: string; label: string; color: string }> = {
    project: { icon: "📂", label: "Project Management", color: "cyan" },
    channel: { icon: "💬", label: "Channel & Linking", color: "purple" },
    system: { icon: "⚙️", label: "System Operations", color: "emerald" },
    query: { icon: "🔍", label: "Information Queries", color: "amber" },
};

const COLOR_MAP: Record<string, string> = {
    cyan: "border-cyan-500/30 bg-cyan-500/8",
    purple: "border-purple-500/30 bg-purple-500/8",
    emerald: "border-emerald-500/30 bg-emerald-500/8",
    amber: "border-amber-500/30 bg-amber-500/8",
};

const ACCENT_MAP: Record<string, string> = {
    cyan: "text-cyan-400",
    purple: "text-purple-400",
    emerald: "text-emerald-400",
    amber: "text-amber-400",
};

export default async function CommandsPage() {
    const registry = await getProjectRegistry();

    const categories = ["project", "channel", "system", "query"];

    return (
        <div className="space-y-6">
            <PageHeader
                icon="📋"
                title="Command Reference"
                subtitle="How to work with CLAW — what you can say and what it does"
            />

            {/* Quick overview: Channel ↔ Project Map */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    🔗 Channel ↔ Project Map
                </h2>
                <p className="text-xs text-zinc-500 mb-4">
                    Every project is linked to a Discord channel. When CLAW works in a channel, it scopes to that project.
                </p>

                <div className="grid gap-3 md:grid-cols-2">
                    {registry.projects.map((p) => (
                        <div
                            key={p.slug}
                            className="flex items-center justify-between rounded-xl bg-zinc-900/40 border border-zinc-800/30 px-4 py-3 hover:border-zinc-700/40 transition-colors"
                        >
                            <div className="flex items-center gap-3">
                                <span className="text-sm">📂</span>
                                <div>
                                    <p className="font-mono text-sm text-zinc-200">{p.slug}</p>
                                    <p className="text-[10px] text-zinc-600">Started {p.started}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-[11px] px-2 py-0.5 rounded-full bg-purple-500/15 text-purple-400 border border-purple-500/20 font-mono">
                                    {p.channel}
                                </span>
                                <span
                                    className={`text-[10px] px-1.5 py-0.5 rounded-full font-semibold ${p.status === "active"
                                            ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20"
                                            : "bg-zinc-700/30 text-zinc-500 border border-zinc-700/30"
                                        }`}
                                >
                                    {p.status}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>

                {registry.meta_channels.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-zinc-800/30">
                        <p className="text-[10px] text-zinc-600 uppercase tracking-wider font-semibold mb-2">
                            Meta Channels (not project-linked)
                        </p>
                        {registry.meta_channels.map((mc) => (
                            <div
                                key={mc.name}
                                className="flex items-center gap-3 text-xs text-zinc-500"
                            >
                                <span className="font-mono text-zinc-400">{mc.name}</span>
                                <span>— {mc.purpose}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* How It Works */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    💡 How It Works
                </h2>
                <div className="grid gap-4 md:grid-cols-3">
                    <div className="rounded-xl bg-zinc-900/40 border border-zinc-800/30 p-4">
                        <div className="text-2xl mb-2">1️⃣</div>
                        <h3 className="text-sm font-semibold text-zinc-200 mb-1">You talk in a channel</h3>
                        <p className="text-xs text-zinc-500">
                            Discord channels are your workspaces. Each one maps to a project folder.
                        </p>
                    </div>
                    <div className="rounded-xl bg-zinc-900/40 border border-zinc-800/30 p-4">
                        <div className="text-2xl mb-2">2️⃣</div>
                        <h3 className="text-sm font-semibold text-zinc-200 mb-1">CLAW scopes to that project</h3>
                        <p className="text-xs text-zinc-500">
                            File reads, writes, and context are automatically scoped to <code className="text-cyan-400">projects/&lt;name&gt;/</code>
                        </p>
                    </div>
                    <div className="rounded-xl bg-zinc-900/40 border border-zinc-800/30 p-4">
                        <div className="text-2xl mb-2">3️⃣</div>
                        <h3 className="text-sm font-semibold text-zinc-200 mb-1">Mission Control shows everything</h3>
                        <p className="text-xs text-zinc-500">
                            All projects, channels, activity, and health — one dashboard to see it all.
                        </p>
                    </div>
                </div>
            </div>

            {/* Command Reference by Category */}
            {categories.map((cat) => {
                const meta = CATEGORY_META[cat];
                const cmds = COMMANDS.filter((c) => c.category === cat);
                const borderColor = COLOR_MAP[meta.color];
                const textColor = ACCENT_MAP[meta.color];

                return (
                    <div key={cat} className="glass-card p-6">
                        <h2 className="section-header text-lg font-bold mb-4">
                            {meta.icon} {meta.label}
                        </h2>
                        <div className="space-y-4">
                            {cmds.map((cmd) => (
                                <div
                                    key={cmd.command}
                                    className={`rounded-xl border p-4 ${borderColor} transition-colors hover:border-zinc-600/40`}
                                >
                                    <div className="flex items-start justify-between mb-2">
                                        <h3 className={`text-sm font-bold ${textColor}`}>
                                            {cmd.command}
                                        </h3>
                                    </div>
                                    <p className="text-sm text-zinc-400 mb-3">{cmd.description}</p>

                                    <div className="mb-3">
                                        <p className="text-[10px] text-zinc-600 uppercase tracking-wider font-semibold mb-1.5">
                                            What happens:
                                        </p>
                                        <ul className="space-y-1">
                                            {cmd.what_happens.map((step, i) => (
                                                <li key={i} className="flex items-start gap-2 text-xs text-zinc-400">
                                                    <span className="text-zinc-600 mt-0.5 flex-shrink-0">→</span>
                                                    <span>{step}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    {cmd.example && (
                                        <div className="rounded-lg bg-zinc-950/50 border border-zinc-800/20 px-3 py-2">
                                            <p className="text-[10px] text-zinc-600 uppercase tracking-wider font-semibold mb-1">
                                                Example:
                                            </p>
                                            <p className="text-xs text-zinc-400 italic font-mono">
                                                {cmd.example}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                );
            })}

            {/* Quick Tips */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    ⚡ Quick Tips
                </h2>
                <div className="space-y-2.5">
                    {[
                        { tip: "Telegram DM is the primary control plane", detail: "Use it for direct commands, sensitive work, and system admin." },
                        { tip: "MEMORY.md is only loaded in main sessions", detail: "For security — personal context doesn't leak to shared channels." },
                        { tip: "Each session starts fresh", detail: "CLAW reads workspace files for continuity. Mental notes don't survive restarts." },
                        { tip: "Sub-agents are isolated", detail: "They can't see MEMORY.md. Use them for parallel or scoped tasks." },
                        { tip: "Reload Mission Control for fresh data", detail: "All data reads from workspace files on each page load." },
                    ].map((t, i) => (
                        <div key={i} className="flex items-start gap-3 rounded-lg bg-zinc-900/30 border border-zinc-800/20 px-4 py-3">
                            <span className="text-cyan-400 mt-0.5 flex-shrink-0">💡</span>
                            <div>
                                <p className="text-sm text-zinc-200 font-medium">{t.tip}</p>
                                <p className="text-xs text-zinc-500">{t.detail}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
