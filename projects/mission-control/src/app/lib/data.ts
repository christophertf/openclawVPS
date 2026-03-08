import fs from "node:fs/promises";
import path from "node:path";

export const WORKSPACE_ROOT = path.resolve(
    process.cwd(),
    "../.."
);

/* ── Safe file read ── */
export async function safeRead(filePath: string): Promise<string | null> {
    try {
        return await fs.readFile(filePath, "utf8");
    } catch {
        return null;
    }
}

/* ── Timestamp helpers ── */
const TZ = "America/Los_Angeles";

export function toUtc(ts?: number): string {
    if (!ts) return "n/a";
    return new Date(ts).toLocaleString("en-US", {
        timeZone: TZ,
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false,
    }) + " PT";
}

export function timeAgo(dateStr: string): string {
    try {
        const then = new Date(
            dateStr.replace(" UTC", "Z").replace(" ", "T")
        );
        const now = new Date();
        const diffMs = now.getTime() - then.getTime();
        const mins = Math.floor(diffMs / 60000);
        const hours = Math.floor(mins / 60);
        const days = Math.floor(hours / 24);
        if (days > 0) return `${days}d ago`;
        if (hours > 0) return `${hours}h ago`;
        if (mins > 0) return `${mins}m ago`;
        return "just now";
    } catch {
        return "";
    }
}

export function formatBytes(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/* ── Claim helpers ── */
export function categorizeClaimId(claimId: string): string {
    if (claimId.startsWith("init-")) return "Initiation";
    if (claimId.startsWith("entry-") || claimId.startsWith("inspection-"))
        return "Inspection";
    if (claimId.startsWith("notice-")) return "Notice";
    if (claimId.startsWith("evid-")) return "Evidence";
    if (claimId.startsWith("selective-")) return "Selective";
    if (claimId.startsWith("escalation-")) return "Escalation";
    if (claimId.startsWith("admin-")) return "Admin";
    if (claimId.startsWith("remedy-")) return "Remedy";
    return "Other";
}

export function categoryClass(cat: string): string {
    const map: Record<string, string> = {
        Initiation: "cat-initiation",
        Inspection: "cat-inspection",
        Notice: "cat-notice",
        Evidence: "cat-evidence",
        Selective: "cat-selective",
        Escalation: "cat-escalation",
        Admin: "cat-admin",
        Remedy: "cat-remedy",
    };
    return map[cat] ?? "";
}

export function extractConfidence(text: string): string {
    const hit = text.match(/\b(Medium-High|High|Medium|Low)\b confidence/i);
    if (hit) return hit[1];
    const alt = text.match(/Confidence\s*[:=]\s*(High|Medium|Low)/i);
    return alt?.[1] ?? "unknown";
}

export function extractSummary(text: string): string {
    const marker = text.match(
        /Executive summary[\s\S]*?\n\n([\s\S]{60,600})/i
    );
    if (marker?.[1]) return marker[1].trim().split("\n")[0];
    const firstParagraph = text
        .split("\n\n")
        .map((x) => x.trim())
        .find((x) => x.length > 80);
    return firstParagraph?.slice(0, 350) ?? "No summary found yet.";
}

/* ── Change feed parser ── */
export type ChangeFeedEntry = {
    timestamp: string;
    actor: string;
    description: string;
};

export function parseChangeFeed(text: string): ChangeFeedEntry[] {
    const lines = text.split("\n").filter((l) => /^\d{4}-/.test(l.trim()));
    return lines.map((line) => {
        const match = line.match(
            /^(\d{4}-\d{2}-\d{2}T[\d:]+Z)\s+(?:\[([^\]]+)\]|(\S+?):)\s*(.*)/
        );
        if (match) {
            return {
                timestamp: match[1],
                actor: match[2] || match[3] || "System",
                description: match[4]?.trim() || line,
            };
        }
        return { timestamp: "", actor: "System", description: line };
    });
}

/* ── Claim parser ── */
export type ClaimEntry = {
    id: string;
    title: string;
    hypothesis: string;
    confidence: string;
    category: string;
};

export function parseAllClaims(text: string): ClaimEntry[] {
    const claims: ClaimEntry[] = [];
    const blocks = text.split(/###\s+\d+\)/);
    for (const block of blocks) {
        const idMatch = block.match(/claim_id:\s*`([^`]+)`/);
        const titleMatch = block.match(/claim_title:\s*(.+)/);
        const hypMatch = block.match(/claim_hypothesis:\s*(.+)/);
        const confMatch = block.match(
            /confidence_prevalidation:\s*(high|medium-high|medium|low)/i
        );
        if (idMatch) {
            const id = idMatch[1];
            claims.push({
                id,
                title: titleMatch?.[1]?.trim() ?? id,
                hypothesis: hypMatch?.[1]?.trim() ?? "",
                confidence: confMatch?.[1] ?? "unknown",
                category: categorizeClaimId(id),
            });
        }
    }
    return claims;
}

/* ── DR Report type ── */
export type DrReport = {
    file: string;
    claimId: string;
    updatedAt: string;
    confidence: string;
    summary: string;
    category: string;
};

/* ── Project discovery ── */
export type ProjectInfo = {
    slug: string;
    name: string;
    description: string;
    path: string;
    hasReadme: boolean;
    fileCount: number;
};

export async function discoverProjects(): Promise<ProjectInfo[]> {
    const projectsDir = path.join(WORKSPACE_ROOT, "projects");
    const projects: ProjectInfo[] = [];

    try {
        const dirs = await fs.readdir(projectsDir, { withFileTypes: true });
        for (const dir of dirs) {
            if (!dir.isDirectory()) continue;

            const projPath = path.join(projectsDir, dir.name);
            const readmePath = path.join(projPath, "README.md");
            const readme = await safeRead(readmePath);

            let name = dir.name
                .replace(/[-_]/g, " ")
                .replace(/\b\w/g, (c) => c.toUpperCase());
            let description = "";

            if (readme) {
                const titleMatch = readme.match(/^#\s+(.+)/m);
                if (titleMatch) name = titleMatch[1].trim();

                // Try to grab the first real paragraph after a heading
                const overviewMatch = readme.match(
                    /##\s+(?:Project\s+)?Overview\s*\n+([\s\S]*?)(?:\n\n|\n##|$)/
                );
                if (overviewMatch) {
                    description = overviewMatch[1].trim().replace(/^#+\s.*/gm, "").trim().slice(0, 200);
                } else {
                    // Fallback: first paragraph after the title
                    const paraMatch = readme.match(/^#[^#].*?\n\n([\s\S]*?)(?:\n\n|\n##|$)/);
                    if (paraMatch) {
                        description = paraMatch[1].trim().replace(/^#+\s.*/gm, "").trim().slice(0, 200);
                    }
                }
            }

            let fileCount = 0;
            try {
                const allFiles = await fs.readdir(projPath, { recursive: true });
                fileCount = allFiles.length;
            } catch {
                /* empty */
            }

            projects.push({
                slug: dir.name,
                name,
                description,
                path: projPath,
                hasReadme: readme !== null,
                fileCount,
            });
        }
    } catch {
        /* empty */
    }

    return projects;
}

/* ── Memory files ── */
export type MemoryFile = {
    filename: string;
    date: string;
    size: number;
    preview: string;
};

export async function getMemoryFiles(): Promise<MemoryFile[]> {
    const memDir = path.join(WORKSPACE_ROOT, "memory");
    const files: MemoryFile[] = [];

    try {
        const entries = await fs.readdir(memDir);
        for (const f of entries.filter((e) => e.endsWith(".md"))) {
            const full = path.join(memDir, f);
            const [content, stat] = await Promise.all([
                safeRead(full),
                fs.stat(full),
            ]);
            const dateMatch = f.match(/(\d{4}-\d{2}-\d{2})/);
            files.push({
                filename: f,
                date: dateMatch?.[1] ?? f.replace(".md", ""),
                size: stat.size,
                preview: content?.slice(0, 300) ?? "",
            });
        }
    } catch {
        /* empty */
    }

    return files.sort((a, b) => b.date.localeCompare(a.date));
}

/* ── Cron parser ── */
export type CronJob = {
    schedule: string;
    command: string;
    logFile: string;
    description: string;
};

export function parseCrontab(raw: string): CronJob[] {
    const lines = raw
        .split("\n")
        .filter((l) => l.trim() && !l.trim().startsWith("#") && !l.includes("="));
    return lines.map((line) => {
        const parts = line.trim().split(/\s+/);
        const schedule = parts.slice(0, 5).join(" ");
        const command = parts.slice(5).join(" ");

        const logMatch = command.match(/>> ?(\S+)/);
        const logFile = logMatch?.[1] ?? "";

        let description = "Unknown job";
        if (command.includes("casefilecleanup_watchdog"))
            description = "Case file cleanup watchdog";
        else if (command.includes("safe_cleanup"))
            description = "Safe cleanup (ops)";
        else if (command.includes("daily_report"))
            description = "Daily report generation";
        else if (command.includes("find") && command.includes(".log"))
            description = "Weekly log archival";

        return { schedule, command, logFile, description };
    });
}

export function cronToHuman(schedule: string): string {
    const [min, hour, dom, , dow] = schedule.split(" ");
    if (min.startsWith("*/")) {
        const n = parseInt(min.replace("*/", ""));
        return `Every ${n} min`;
    }
    if (hour.startsWith("*/")) {
        const n = parseInt(hour.replace("*/", ""));
        return `Every ${n} hours`;
    }
    const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    if (dow !== "*") {
        return `Weekly on ${days[parseInt(dow)] ?? dow} at ${hour.padStart(2, "0")}:${min.padStart(2, "0")}`;
    }
    if (dom !== "*") {
        return `Monthly on day ${dom} at ${hour.padStart(2, "0")}:${min.padStart(2, "0")}`;
    }
    return `Daily at ${hour.padStart(2, "0")}:${min.padStart(2, "0")}`;
}

/* ── System health check ── */
export type HealthCheck = {
    label: string;
    status: "ok" | "warning" | "error";
    detail: string;
};

export async function getSystemHealth(): Promise<HealthCheck[]> {
    const checks: HealthCheck[] = [];

    // docs/MEMORY.md
    const memory = await safeRead(path.join(WORKSPACE_ROOT, "docs/MEMORY.md"));
    checks.push({
        label: "MEMORY.md",
        status: memory ? "ok" : "error",
        detail: memory ? `${memory.length} bytes` : "Not found",
    });

    // docs/HEARTBEAT.md
    const heartbeat = await safeRead(
        path.join(WORKSPACE_ROOT, "docs/HEARTBEAT.md")
    );
    checks.push({
        label: "Heartbeat",
        status: heartbeat ? "ok" : "error",
        detail: heartbeat ? "Configured" : "Missing",
    });

    // Daily memory
    const memDir = path.join(WORKSPACE_ROOT, "memory");
    try {
        const memFiles = (await fs.readdir(memDir))
            .filter((f) => /^\d{4}-\d{2}-\d{2}\.md$/.test(f))
            .sort()
            .reverse();
        if (memFiles.length > 0) {
            checks.push({
                label: "Daily Memory",
                status: "ok",
                detail: memFiles[0],
            });
        } else {
            checks.push({
                label: "Daily Memory",
                status: "warning",
                detail: "No daily notes",
            });
        }
    } catch {
        checks.push({
            label: "Daily Memory",
            status: "error",
            detail: "Cannot read memory dir",
        });
    }

    // Pipeline
    const pipeline = await safeRead(
        path.join(WORKSPACE_ROOT, "data/processed/reports/case_pipeline/status.json")
    );
    checks.push({
        label: "Pipeline",
        status: pipeline ? "ok" : "warning",
        detail: pipeline ? "Active" : "No data",
    });

    // Change feed
    const feed = await safeRead(
        path.join(WORKSPACE_ROOT, "memory/change-feed.log")
    );
    checks.push({
        label: "Change Feed",
        status: feed ? "ok" : "warning",
        detail: feed
            ? `${feed.split("\n").filter((l) => /^\d{4}-/.test(l)).length} entries`
            : "Empty",
    });

    // Git
    try {
        const gitDir = path.join(WORKSPACE_ROOT, ".git");
        await fs.access(gitDir);
        checks.push({
            label: "Git Repository",
            status: "ok",
            detail: "Initialized",
        });
    } catch {
        checks.push({
            label: "Git Repository",
            status: "error",
            detail: "Not found",
        });
    }

    return checks;
}

/* ── Project Registry (channel↔project mapping) ── */
export type ProjectRegistryEntry = {
    slug: string;
    channel: string;
    status: string;
    started: string;
};

export type MetaChannel = {
    name: string;
    purpose: string;
};

export type ProjectRegistry = {
    projects: ProjectRegistryEntry[];
    meta_channels: MetaChannel[];
};

export async function getProjectRegistry(): Promise<ProjectRegistry> {
    const raw = await safeRead(path.join(WORKSPACE_ROOT, "metadata/projects.json"));
    if (!raw) return { projects: [], meta_channels: [] };
    try {
        return JSON.parse(raw) as ProjectRegistry;
    } catch {
        return { projects: [], meta_channels: [] };
    }
}
