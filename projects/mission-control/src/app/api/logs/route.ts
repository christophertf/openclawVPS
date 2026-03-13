import { NextResponse } from "next/server";
import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

// Log sources to watch — each with a label and file path
const LOG_SOURCES = [
    {
        label: "change-feed",
        path: "/home/claw/.openclaw/workspace/memory/change-feed.log",
    },
    {
        label: "dev-server",
        path: "/home/claw/.openclaw/workspace/projects/mission-control/.next/dev/logs/next-development.log",
    },
];

const LINES_PER_LOG = 20;

const HIDDEN_PATTERNS = [
    /Download the React DevTools for a better development experience/i,
    /React DevTools/i,
    /Compiled in\s*\d+ms/i,
];

function shouldHideLine(line: string): boolean {
    const s = line.trim();
    if (!s) return true;
    return HIDDEN_PATTERNS.some((p) => p.test(s));
}

function cleanLines(lines: string[]): string[] {
    return lines.map((l) => l.trimEnd()).filter((l) => !shouldHideLine(l));
}

export const dynamic = "force-dynamic";

export async function GET() {
    const entries: { label: string; lines: string[]; mtime: string; size: number }[] = [];

    for (const src of LOG_SOURCES) {
        try {
            if (!fs.existsSync(src.path)) continue;
            const stat = fs.statSync(src.path);
            if (stat.size === 0) continue;

            const tail = execSync(`tail -n ${LINES_PER_LOG} "${src.path}"`, {
                encoding: "utf8",
                timeout: 3000,
            });

            const lines = cleanLines(tail.split("\n"));
            if (lines.length === 0) continue;

            entries.push({
                label: src.label,
                lines,
                mtime: stat.mtime.toISOString(),
                size: stat.size,
            });
        } catch {
            // skip unreadable logs
        }
    }

    // Grab the most recently modified ops/cron log and create a dynamic pane for it
    try {
        const opsDir = "/home/claw/.openclaw/workspace/ops/logs";
        if (fs.existsSync(opsDir)) {
            const opFiles = fs.readdirSync(opsDir).filter(f => f.endsWith('.log') && f.startsWith('cron_'));
            if (opFiles.length > 0) {
                const opStats = opFiles.map(f => ({ name: f, mtime: fs.statSync(path.join(opsDir, f)).mtimeMs }));
                opStats.sort((a, b) => b.mtime - a.mtime);

                const latest = opStats[0];
                const tail = execSync(`tail -n ${LINES_PER_LOG} "${path.join(opsDir, latest.name)}"`, { encoding: "utf8", timeout: 3000 });
                const lines = cleanLines(tail.split('\n'));
                if (lines.length > 0) {
                    entries.push({
                        label: `ops: ${latest.name.replace('cron_', '').replace('.log', '').replace(/_/g, '-')}`,
                        lines,
                        mtime: new Date(latest.mtime).toISOString(),
                        size: fs.statSync(path.join(opsDir, latest.name)).size,
                    });
                }
            }
        }
    } catch {
        // skip
    }

    // Also grab the most recent CLAW session's last few commands
    try {
        const sessDir = "/home/claw/.openclaw/agents/main/sessions";
        const files = fs.readdirSync(sessDir)
            .filter((f) => f.endsWith(".jsonl"))
            .map((f) => ({
                name: f,
                mtime: fs.statSync(path.join(sessDir, f)).mtimeMs,
            }))
            .sort((a, b) => b.mtime - a.mtime);

        if (files.length > 0) {
            const latest = path.join(sessDir, files[0].name);
            const tail = execSync(`tail -n 40 "${latest}"`, {
                encoding: "utf8",
                timeout: 3000,
            });

            // Extract tool_use and text entries 
            const lines: string[] = [];
            for (const line of tail.split("\n").filter(Boolean)) {
                try {
                    const obj = JSON.parse(line);
                    const msg = obj?.message;
                    if (!msg?.role) continue;
                    const ts = obj?.timestamp ? new Date(obj.timestamp).toLocaleTimeString("en-US", {
                        timeZone: "America/Los_Angeles",
                        hour12: false,
                    }) : "";

                    if (msg.role === "assistant" && Array.isArray(msg.content)) {
                        for (const part of msg.content) {
                            if (part.type === "tool_use") {
                                lines.push(`[${ts}] 🔧 ${part.name}(${JSON.stringify(part.input).slice(0, 80)}…)`);
                            } else if (part.type === "text" && part.text) {
                                const preview = part.text.split("\n")[0].slice(0, 100);
                                if (preview.trim()) lines.push(`[${ts}] 💬 ${preview}`);
                            }
                        }
                    } else if (msg.role === "tool" && Array.isArray(msg.content)) {
                        for (const part of msg.content) {
                            if (part.type === "text" && part.text) {
                                const short = part.text.split("\n")[0].slice(0, 80);
                                lines.push(`[${ts}]    ↳ ${short}`);
                            }
                        }
                    }
                } catch {
                    // skip
                }
            }

            const cleanedLiveLines = cleanLines(lines);
            if (cleanedLiveLines.length > 0) {
                entries.unshift({
                    label: "claw-live",
                    lines: cleanedLiveLines.slice(-15),
                    mtime: new Date(files[0].mtime).toISOString(),
                    size: 0,
                });
            }
        }
    } catch {
        // skip
    }

    // Grab Antigravity live commands feed
    try {
        const agLogPath = "/home/claw/.openclaw/workspace/ops/logs/antigravity-live.log";
        if (fs.existsSync(agLogPath)) {
            const stat = fs.statSync(agLogPath);
            const tail = execSync(`tail -n 15 "${agLogPath}"`, {
                encoding: "utf8",
                timeout: 3000,
            });
            const lines = cleanLines(tail.split("\n"));
            if (lines.length > 0) {
                // remove duplicates that might appear rapidly
                const deduped: string[] = [];
                for (const l of lines) {
                    if (deduped.length === 0 || deduped[deduped.length - 1] !== l) {
                        deduped.push(l);
                    }
                }
                entries.unshift({
                    label: "antigravity-live (model-35)",
                    lines: deduped.slice(-15),
                    mtime: stat.mtime.toISOString(),
                    size: stat.size,
                });
            }
        }
    } catch {
        // skip
    }

    // Sort so live feeds are first, then by most recently modified
    entries.sort((a, b) => {
        const aLive = a.label.includes("-live");
        const bLive = b.label.includes("-live");
        if (aLive && !bLive) return -1;
        if (!aLive && bLive) return 1;
        if (aLive && bLive) return a.label.localeCompare(b.label); // sort live feeds alphabetically
        return new Date(b.mtime).getTime() - new Date(a.mtime).getTime();
    });

    return NextResponse.json({ entries, timestamp: new Date().toISOString() });
}
