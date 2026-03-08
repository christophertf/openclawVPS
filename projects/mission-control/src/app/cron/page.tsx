import path from "node:path";
import { execSync } from "node:child_process";
import {
    WORKSPACE_ROOT,
    safeRead,
    parseCrontab,
    formatBytes,
} from "@/app/lib/data";
import { PageHeader, EmptyState } from "@/app/components/ui";
import fs from "node:fs/promises";

export const dynamic = "force-dynamic";

async function getCronData() {
    let crontabRaw = "";
    try {
        crontabRaw = execSync("crontab -l 2>/dev/null", {
            encoding: "utf8",
        });
    } catch {
        crontabRaw = "";
    }

    const jobs = parseCrontab(crontabRaw);

    // Read state files
    const stateDir = path.join(WORKSPACE_ROOT, "state");
    const stateFiles: { name: string; size: number; content: string }[] =
        [];
    try {
        const entries = await fs.readdir(stateDir);
        for (const f of entries) {
            const full = path.join(stateDir, f);
            const stat = await fs.stat(full);
            const content = (await safeRead(full)) ?? "";
            stateFiles.push({
                name: f,
                size: stat.size,
                content: content.slice(0, 500),
            });
        }
    } catch {
        /* empty */
    }

    // Read scripts
    const scriptsDir = path.join(WORKSPACE_ROOT, "scripts");
    const scripts: { name: string; size: number; preview: string }[] =
        [];
    try {
        const entries = await fs.readdir(scriptsDir);
        for (const f of entries) {
            const full = path.join(scriptsDir, f);
            const stat = await fs.stat(full);
            const content = (await safeRead(full)) ?? "";
            scripts.push({
                name: f,
                size: stat.size,
                preview:
                    content
                        .split("\n")
                        .filter((l) => l.startsWith("#") || l.startsWith("//"))
                        .slice(0, 3)
                        .join("\n") || "(no header comments)",
            });
        }
    } catch {
        /* empty */
    }

    // Case automation
    const caseAutomation = await safeRead(
        path.join(WORKSPACE_ROOT, "CASE_AUTOMATION.md")
    );

    return { crontabRaw, jobs, stateFiles, scripts, caseAutomation };
}

function cronHumanize(schedule: string): string {
    const parts = schedule.split(/\s+/);
    if (parts.length < 5) return schedule;
    const [min, hr, dom, mon, dow] = parts;

    if (min.startsWith("*/"))
        return `Every ${min.slice(2)} minutes`;
    if (hr.startsWith("*/"))
        return `Minute ${min}, every ${hr.slice(2)} hours`;
    if (dow !== "*" && dow === "0")
        return `Weekly on Sundays at ${hr}:${min}`;
    if (dom === "*" && mon === "*" && dow === "*")
        return `Daily at ${hr}:${min.padStart(2, "0")}`;
    return schedule;
}

export default async function CronPage() {
    const data = await getCronData();

    return (
        <div className="space-y-6">
            <PageHeader
                icon="⏱️"
                title="Cron & Automation"
                subtitle="Scheduled tasks, scripts, and automation state"
            />

            {/* Cron Jobs */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    🕐 Active Cron Jobs ({data.jobs.length})
                </h2>
                {data.jobs.length === 0 ? (
                    <EmptyState icon="🕐" message="No cron jobs found" />
                ) : (
                    <div className="space-y-3">
                        {data.jobs.map((job, i) => (
                            <div
                                key={i}
                                className="rounded-xl bg-zinc-900/40 border border-zinc-800/30 p-4 hover:border-zinc-700/40 transition-colors"
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <h3 className="text-sm font-semibold text-zinc-200">
                                        {job.description}
                                    </h3>
                                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-400 border border-cyan-500/20 font-mono">
                                        {cronHumanize(job.schedule)}
                                    </span>
                                </div>
                                <code className="block text-[11px] font-mono text-zinc-500 bg-zinc-950/50 rounded-lg p-2 overflow-x-auto">
                                    {job.command}
                                </code>
                                {job.logFile && (
                                    <p className="mt-1.5 text-[10px] text-zinc-600 font-mono">
                                        📝 Log: {job.logFile}
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {/* Raw crontab */}
                <details className="mt-4">
                    <summary className="text-xs text-zinc-500 cursor-pointer hover:text-zinc-400">
                        Raw crontab ▸
                    </summary>
                    <pre className="mt-2 memory-log rounded-lg bg-zinc-950/50 p-3 border border-zinc-800/30 text-[11px] overflow-x-auto">
                        {data.crontabRaw || "(empty)"}
                    </pre>
                </details>
            </div>

            {/* Scripts */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    📜 Workspace Scripts ({data.scripts.length})
                </h2>
                <div className="grid gap-3 md:grid-cols-2">
                    {data.scripts.map((s) => (
                        <div
                            key={s.name}
                            className="rounded-xl bg-zinc-900/40 border border-zinc-800/30 p-4 hover:border-zinc-700/40 transition-colors"
                        >
                            <div className="flex items-center justify-between mb-2">
                                <span className="font-mono text-sm text-zinc-200">
                                    {s.name}
                                </span>
                                <span className="text-[10px] text-zinc-600">
                                    {formatBytes(s.size)}
                                </span>
                            </div>
                            <p className="text-[11px] text-zinc-500 font-mono">
                                {s.preview}
                            </p>
                        </div>
                    ))}
                </div>
            </div>

            {/* State Files */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    📊 Automation State
                </h2>
                <div className="space-y-3">
                    {data.stateFiles.map((sf) => (
                        <details
                            key={sf.name}
                            className="group rounded-xl bg-zinc-900/40 border border-zinc-800/30 hover:border-zinc-700/40 transition-colors"
                        >
                            <summary className="flex items-center justify-between cursor-pointer px-4 py-3">
                                <span className="font-mono text-sm text-zinc-300">
                                    {sf.name}
                                </span>
                                <div className="flex items-center gap-3">
                                    <span className="text-[10px] text-zinc-600">
                                        {formatBytes(sf.size)}
                                    </span>
                                    <span className="text-zinc-600 group-open:rotate-90 transition-transform">
                                        ▸
                                    </span>
                                </div>
                            </summary>
                            <div className="px-4 pb-4">
                                <pre className="memory-log rounded-lg bg-zinc-950/50 p-3 border border-zinc-800/20 max-h-48 overflow-y-auto whitespace-pre-wrap text-xs">
                                    {sf.content}
                                </pre>
                            </div>
                        </details>
                    ))}
                </div>
            </div>

            {/* Case Automation Config */}
            {data.caseAutomation && (
                <div className="glass-card p-6">
                    <h2 className="section-header text-lg font-bold mb-4">
                        ⚙️ Case Automation Config
                    </h2>
                    <pre className="memory-log rounded-xl bg-zinc-950/50 p-4 border border-zinc-800/30 max-h-72 overflow-y-auto whitespace-pre-wrap">
                        {data.caseAutomation}
                    </pre>
                </div>
            )}
        </div>
    );
}
