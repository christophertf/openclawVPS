import fs from "node:fs/promises";
import path from "node:path";
import { execSync } from "node:child_process";
import Link from "next/link";
import TerminalWindow from "@/app/components/TerminalWindow";
import {
  WORKSPACE_ROOT,
  safeRead,
  toUtc,
  discoverProjects,
  getSystemHealth,
  parseChangeFeed,
  getMemoryFiles,
  parseCrontab,
  cronToHuman,
  type ChangeFeedEntry,
  type CronJob,
} from "@/app/lib/data";

export const dynamic = "force-dynamic";

type HeartbeatSnapshot = {
  everyMinutes: number;
  lastRunAt: string;
  lastResult: string;
  minutesAgo: number | null;
  state: "on-schedule" | "overdue" | "unknown";
};

function parseEveryMinutes(raw?: string): number {
  if (!raw) return 30;
  const m = raw.trim().match(/^(\d+)([mhd])$/i);
  if (!m) return 30;
  const n = parseInt(m[1], 10);
  const unit = m[2].toLowerCase();
  if (unit === "m") return n;
  if (unit === "h") return n * 60;
  if (unit === "d") return n * 24 * 60;
  return 30;
}

async function getHeartbeatSnapshot(): Promise<HeartbeatSnapshot> {
  const fallback: HeartbeatSnapshot = {
    everyMinutes: 30,
    lastRunAt: "n/a",
    lastResult: "No heartbeat events found.",
    minutesAgo: null,
    state: "unknown",
  };

  const openclawRaw = await safeRead(path.resolve(WORKSPACE_ROOT, "../openclaw.json"));
  const everyMinutes = (() => {
    try {
      if (!openclawRaw) return 30;
      const cfg = JSON.parse(openclawRaw);
      return parseEveryMinutes(cfg?.agents?.defaults?.heartbeat?.every);
    } catch {
      return 30;
    }
  })();

  const sessionsDir = path.resolve(WORKSPACE_ROOT, "../agents/main/sessions");
  const marker = "Read HEARTBEAT.md if it exists";

  try {
    const files = await fs.readdir(sessionsDir);
    const withMtime = await Promise.all(
      files
        .filter((f) => f.endsWith(".jsonl"))
        .map(async (f) => {
          const full = path.join(sessionsDir, f);
          const st = await fs.stat(full);
          return { full, mtimeMs: st.mtimeMs };
        })
    );

    const recent = withMtime.sort((a, b) => b.mtimeMs - a.mtimeMs).slice(0, 8);

    let best: { ts: number; result: string } | null = null;

    for (const file of recent) {
      const raw = await safeRead(file.full);
      if (!raw || !raw.includes(marker)) continue;

      const events: { ts: number; role: string; text: string }[] = [];
      for (const line of raw.split("\n").filter(Boolean)) {
        try {
          const obj = JSON.parse(line);
          const msg = obj?.message;
          const role = msg?.role;
          if (!role || !Array.isArray(msg?.content)) continue;

          const text = msg.content
            .filter((c: { type?: string; text?: string }) => c?.type === "text" && typeof c?.text === "string")
            .map((c: { text: string }) => c.text)
            .join("\n")
            .trim();
          if (!text) continue;

          const ts = new Date(obj?.timestamp ?? msg?.timestamp).getTime();
          if (!Number.isFinite(ts)) continue;

          events.push({ ts, role, text });
        } catch {
          // skip malformed line
        }
      }

      events.sort((a, b) => a.ts - b.ts);

      for (let i = 0; i < events.length; i++) {
        const ev = events[i];
        if (ev.role !== "user" || !ev.text.includes(marker)) continue;

        let result = "No assistant response captured.";
        for (let j = i + 1; j < events.length; j++) {
          if (events[j].role === "assistant") {
            result = events[j].text.split("\n").map((x) => x.trim()).filter(Boolean).join(" ");
            break;
          }
        }

        if (!best || ev.ts > best.ts) {
          best = { ts: ev.ts, result };
        }
      }
    }

    if (!best) return { ...fallback, everyMinutes };

    const minutesAgo = Math.max(0, Math.floor((Date.now() - best.ts) / 60000));
    const overdueAfter = everyMinutes + 10;

    return {
      everyMinutes,
      lastRunAt: toUtc(best.ts),
      lastResult: best.result.length > 170 ? `${best.result.slice(0, 167)}…` : best.result,
      minutesAgo,
      state: minutesAgo <= overdueAfter ? "on-schedule" : "overdue",
    };
  } catch {
    return { ...fallback, everyMinutes };
  }
}

async function getDashboardData() {
  const [changeFeedRaw, identityRaw] = await Promise.all([
    safeRead(path.join(WORKSPACE_ROOT, "memory/change-feed.log")),
    safeRead(path.join(WORKSPACE_ROOT, "docs/IDENTITY.md")),
  ]);

  const projects = await discoverProjects();
  const healthChecks = await getSystemHealth();
  const heartbeat = await getHeartbeatSnapshot();
  const changeFeed: ChangeFeedEntry[] = changeFeedRaw
    ? parseChangeFeed(changeFeedRaw).reverse().slice(0, 5)
    : [];
  const memoryFiles = await getMemoryFiles();

  let cronJobs: CronJob[] = [];
  try {
    const crontab = execSync("crontab -l 2>/dev/null", { encoding: "utf8" });
    cronJobs = parseCrontab(crontab);
  } catch {
    cronJobs = [];
  }

  let scriptCount = 0;
  try {
    const scripts = await fs.readdir(path.join(WORKSPACE_ROOT, "scripts"));
    scriptCount = scripts.length;
  } catch { /* empty */ }

  let agentName = "CLAW";
  if (identityRaw) {
    const nameMatch = identityRaw.match(/\*\*Name:\*\*\s*(.+)/);
    if (nameMatch) agentName = nameMatch[1].trim();
  }

  const healthOk = healthChecks.filter((h) => h.status === "ok").length;
  const healthTotal = healthChecks.length;

  return {
    generatedAt: toUtc(Date.now()),
    agentName,
    projects,
    healthChecks,
    healthOk,
    healthTotal,
    heartbeat,
    changeFeed,
    memoryFiles,
    cronJobs,
    scriptCount,
  };
}

export default async function Home() {
  const d = await getDashboardData();

  return (
    <div className="space-y-3">
      {/* Top bar — compact */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-lg">🐾</span>
          <h1 className="text-lg font-bold text-zinc-100">{d.agentName}</h1>
          <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${d.healthOk === d.healthTotal
            ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20"
            : "bg-amber-500/15 text-amber-400 border border-amber-500/20"
            }`}>
            {d.healthOk}/{d.healthTotal} healthy
          </span>
        </div>
        <span className="font-mono text-[11px] text-zinc-600" suppressHydrationWarning>{d.generatedAt}</span>
      </div>

      {/* Row 1: Counters bar */}
      <div className="grid grid-cols-2 gap-2">
        {[
          { label: "Projects", value: d.projects.length, color: "text-cyan-400", href: "/projects" },
          { label: "Active Cron Hooks", value: d.cronJobs.length, color: "text-amber-400", href: "/cron" },
        ].map((s) => (
          <Link key={s.label} href={s.href}
            className="rounded-lg bg-zinc-900/40 border border-zinc-800/30 px-3 py-2 flex items-center justify-between hover:border-zinc-700/40 transition-colors"
          >
            <span className="text-[11px] text-zinc-500">{s.label}</span>
            <span className={`text-sm font-bold ${s.color}`}>{s.value}</span>
          </Link>
        ))}
      </div>

      {/* Row 2: Live terminal (Moved up) */}
      <div style={{ height: 350 }}>
        <TerminalWindow />
      </div>

      {/* Row 3: Last project + Active automation */}
      <div className="grid gap-3 lg:grid-cols-2">
        {/* Recent Activity */}
        <div className="glass-card p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] uppercase tracking-wider text-zinc-600 font-semibold">Recent Activity</span>
            <Link href="/activity" className="text-[10px] text-cyan-400 hover:text-cyan-300">Full feed →</Link>
          </div>
          <div className="space-y-2 max-h-44 overflow-y-auto pr-1">
            {d.changeFeed.map((entry, i) => (
              <div key={i} className="flex items-start gap-2">
                <span className={`text-[9px] font-semibold px-1 py-0.5 rounded flex-shrink-0 mt-0.5 ${entry.actor === "CLAW" ? "bg-cyan-500/15 text-cyan-400"
                  : entry.actor.startsWith("Antigravity") ? "bg-purple-500/15 text-purple-400"
                    : "bg-zinc-700/50 text-zinc-400"
                  }`}>{entry.actor}</span>
                <p className="text-[11px] text-zinc-400 line-clamp-1">{entry.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Active automation */}
        <div className="glass-card p-4 flex flex-col space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase tracking-wider text-zinc-600 font-semibold">Scheduled Automation</span>
            <Link href="/cron" className="text-[10px] text-cyan-400 hover:text-cyan-300">Details →</Link>
          </div>

          <div className="flex flex-wrap gap-2">
            {d.cronJobs.map((job, i) => (
              <div key={i} className="flex items-center gap-2 rounded-lg bg-zinc-900/30 border border-zinc-800/20 px-2.5 py-1.5">
                <span className="pulse-dot flex-shrink-0" style={{ width: 6, height: 6 }} />
                <span className="text-xs text-zinc-300">{job.description}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/20 font-mono">
                  {cronToHuman(job.schedule)}
                </span>
              </div>
            ))}
          </div>

          <div className="pt-2 border-t border-zinc-800/40">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] text-zinc-500 font-semibold">Agent Heartbeat</span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded-full border font-semibold ${d.heartbeat.state === "on-schedule"
                ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/25"
                : d.heartbeat.state === "overdue"
                  ? "bg-amber-500/15 text-amber-400 border-amber-500/25"
                  : "bg-zinc-700/30 text-zinc-400 border-zinc-700/40"
                }`}>
                {d.heartbeat.state === "on-schedule" ? "On schedule" : d.heartbeat.state === "overdue" ? "Overdue" : "Unknown"}
              </span>
            </div>
            <p className="text-[11px] text-zinc-400">
              Run: <span className="font-mono text-zinc-300">{d.heartbeat.lastRunAt}</span>
              {d.heartbeat.minutesAgo !== null && (
                <span className="text-zinc-500"> ({d.heartbeat.minutesAgo}m ago)</span>
              )}
              <span className="text-zinc-600 ml-2">Cadence: {d.heartbeat.everyMinutes}m</span>
            </p>
          </div>
        </div>
      </div>

      {/* Row 4: Activity + Journal — side by side, capped height */}
      <div className="grid gap-3 lg:grid-cols-2">
        {/* Last active project */}
        <div className="glass-card p-4 space-y-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] uppercase tracking-wider text-zinc-600 font-semibold">Last Active Project</span>
            <Link href="/projects" className="text-[10px] text-cyan-400 hover:text-cyan-300">All →</Link>
          </div>
          {d.projects.length > 0 && (
            <Link href={`/projects/${d.projects[0].slug}`} className="group flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-zinc-100 group-hover:text-cyan-300 transition-colors">
                  {d.projects[0].name}
                </h3>
                {d.projects[0].description && (
                  <p className="text-xs text-zinc-500 line-clamp-1 mt-0.5">{d.projects[0].description}</p>
                )}
              </div>
              <span className="text-xs text-zinc-600 font-mono ml-3">{d.projects[0].fileCount} files</span>
            </Link>
          )}
        </div>

        {/* Latest Journal */}
        <div className="glass-card p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] uppercase tracking-wider text-zinc-600 font-semibold">Latest Journal</span>
            <Link href="/memory" className="text-[10px] text-cyan-400 hover:text-cyan-300">All entries →</Link>
          </div>
          <div className="space-y-2 max-h-44 overflow-y-auto pr-1">
            {d.memoryFiles.slice(0, 4).map((mf) => (
              <Link key={mf.filename} href={`/memory?file=${mf.filename}`}
                className="block rounded-lg bg-zinc-900/30 border border-zinc-800/20 px-3 py-2 hover:border-zinc-700/40 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs text-zinc-200">{mf.date}</span>
                  <span className="text-[10px] text-zinc-600">{mf.filename}</span>
                </div>
                <p className="text-[11px] text-zinc-500 line-clamp-1 mt-0.5">
                  {mf.preview.replace(/^#.*\n/m, "").trim()}
                </p>
              </Link>
            ))}
          </div>
        </div>
      </div>

    </div>
  );
}
