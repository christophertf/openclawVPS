import path from "node:path";
import { WORKSPACE_ROOT, safeRead } from "@/app/lib/data";
import { PageHeader } from "@/app/components/ui";

export const dynamic = "force-dynamic";

export default async function SettingsPage() {
    const [heartbeat, caseAuto] = await Promise.all([
        safeRead(path.join(WORKSPACE_ROOT, "docs/HEARTBEAT.md")),
        safeRead(path.join(WORKSPACE_ROOT, "docs/CASE_AUTOMATION.md")),
    ]);

    // System info
    const sysInfo = {
        workspace: WORKSPACE_ROOT,
        nodeVersion: process.version,
        platform: process.platform,
        arch: process.arch,
        uptime: `${Math.floor(process.uptime() / 3600)}h ${Math.floor((process.uptime() % 3600) / 60)}m`,
        memUsed: `${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)} MB`,
    };

    return (
        <div className="space-y-6">
            <PageHeader
                icon="⚙️"
                title="Settings"
                subtitle="System configuration, heartbeat, and workspace info"
            />

            {/* System Info */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    💻 System Information
                </h2>
                <div className="grid gap-3 md:grid-cols-2">
                    {Object.entries(sysInfo).map(([key, val]) => (
                        <div
                            key={key}
                            className="flex items-center justify-between rounded-lg bg-zinc-900/40 border border-zinc-800/30 px-4 py-2.5"
                        >
                            <span className="text-sm text-zinc-400 capitalize">
                                {key.replace(/([A-Z])/g, " $1")}
                            </span>
                            <span className="font-mono text-sm text-zinc-200">
                                {val}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Heartbeat Config */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    💓 Heartbeat Configuration
                </h2>
                <pre className="memory-log rounded-xl bg-zinc-950/50 p-4 border border-zinc-800/30 max-h-60 overflow-y-auto whitespace-pre-wrap">
                    {heartbeat ?? "HEARTBEAT.md not found."}
                </pre>
            </div>

            {/* Case Automation */}
            {caseAuto && (
                <div className="glass-card p-6">
                    <h2 className="section-header text-lg font-bold mb-4">
                        🗂️ Case Automation
                    </h2>
                    <pre className="memory-log rounded-xl bg-zinc-950/50 p-4 border border-zinc-800/30 max-h-60 overflow-y-auto whitespace-pre-wrap">
                        {caseAuto}
                    </pre>
                </div>
            )}

            {/* About */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    ℹ️ About Mission Control
                </h2>
                <div className="text-sm text-zinc-400 space-y-2">
                    <p>
                        CLAW Mission Control v2.0 — a real-time operational
                        dashboard for the OpenClaw workspace.
                    </p>
                    <p>
                        Data is read directly from workspace files on each page
                        load. Reload to refresh.
                    </p>
                    <p className="text-zinc-600">
                        Built with Next.js 16 · Running on {sysInfo.platform}/{sysInfo.arch}
                    </p>
                </div>
            </div>
        </div>
    );
}
