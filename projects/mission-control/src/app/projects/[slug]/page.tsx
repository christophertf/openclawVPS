import fs from "node:fs/promises";
import path from "node:path";
import Link from "next/link";
import {
    WORKSPACE_ROOT,
    safeRead,
    toUtc,
    timeAgo,
    extractConfidence,
    extractSummary,
    categorizeClaimId,
    parseAllClaims,
    type DrReport,
    type ClaimEntry,
} from "@/app/lib/data";
import {
    PageHeader,
    StatCard,
    ProgressRing,
    ConfidenceBadge,
    CategoryPill,
    EmptyState,
} from "@/app/components/ui";

export const dynamic = "force-dynamic";

type Props = {
    params: Promise<{ slug: string }>;
};

async function getProjectData(slug: string) {
    const projPath = path.join(WORKSPACE_ROOT, "projects", slug);
    const readme = await safeRead(path.join(projPath, "README.md"));

    let name = slug
        .replace(/[-_]/g, " ")
        .replace(/\b\w/g, (c) => c.toUpperCase());
    if (readme) {
        const titleMatch = readme.match(/^#\s+(.+)/m);
        if (titleMatch) name = titleMatch[1].trim();
    }

    // list all files in the project
    let files: string[] = [];
    try {
        const entries = await fs.readdir(projPath, { recursive: true });
        files = (entries as string[]).filter(
            (f) =>
                !f.startsWith(".") &&
                !f.startsWith("node_modules") &&
                !f.startsWith(".venv")
        );
    } catch {
        /* empty */
    }

    // Check for claim engine data (special handling for forensic_cpra_engine, appeal_alignment, etc.)
    const claimData = await getClaimEngineData();

    return {
        slug,
        name,
        readme,
        files,
        projPath,
        ...claimData,
    };
}

async function getClaimEngineData() {
    const stage1Path = path.join(
        WORKSPACE_ROOT,
        "reports/claim_engine/stage1_claims_pass1.md"
    );
    const drDir = path.join(WORKSPACE_ROOT, "reports/claim_engine/dr");
    const pipelinePath = path.join(
        WORKSPACE_ROOT,
        "reports/case_pipeline/status.json"
    );

    const [stage1, pipelineRaw] = await Promise.all([
        safeRead(stage1Path),
        safeRead(pipelinePath),
    ]);

    let pipeline: Record<string, unknown> | null = null;
    try {
        pipeline = pipelineRaw ? JSON.parse(pipelineRaw) : null;
    } catch {
        pipeline = null;
    }

    let drFiles: string[] = [];
    try {
        drFiles = (await fs.readdir(drDir))
            .filter((f) => f.endsWith(".md"))
            .sort();
    } catch {
        drFiles = [];
    }

    const drReports: DrReport[] = [];
    for (const file of drFiles) {
        const full = path.join(drDir, file);
        const [text, stat] = await Promise.all([
            safeRead(full),
            fs.stat(full),
        ]);
        if (!text) continue;
        const claimId = file.replace(/\.md$/, "");
        drReports.push({
            file,
            claimId,
            updatedAt: toUtc(stat.mtimeMs),
            confidence: extractConfidence(text),
            summary: extractSummary(text),
            category: categorizeClaimId(claimId),
        });
    }

    const allClaims: ClaimEntry[] = stage1
        ? parseAllClaims(stage1)
        : [];

    const stage1Top10 = stage1
        ? stage1
            .split("\n")
            .filter((l) => /^\d+\.\s`/.test(l.trim()))
            .map((x) => x.trim().replace(/^\d+\.\s`|`$/g, ""))
            .slice(0, 10)
        : [];

    const categoryCounts: Record<string, number> = {};
    const confidenceCounts: Record<string, number> = {
        high: 0,
        medium: 0,
        low: 0,
    };
    for (const c of allClaims) {
        categoryCounts[c.category] =
            (categoryCounts[c.category] ?? 0) + 1;
        const key = c.confidence.toLowerCase();
        if (key in confidenceCounts) confidenceCounts[key]++;
    }

    return {
        allClaims,
        stage1Top10,
        drReports,
        pipeline,
        categoryCounts,
        confidenceCounts,
    };
}

export default async function ProjectDetailPage({ params }: Props) {
    const { slug } = await params;
    const data = await getProjectData(slug);
    const p = (data.pipeline ?? {}) as Record<string, unknown>;
    const hasClaims = data.allClaims.length > 0;

    const progressPct = Number(p.progress_percent ?? 0);
    const totalFilesCurrent = Number(p.total_files_current ?? 0);
    const totalFilesBaseline = Number(p.baseline_total_files ?? 0);
    const nearPending = Number(p.near_candidates_pending ?? 0);
    const exactMoved = Number(p.moved_exact_total ?? 0);
    const nearMoved = Number(p.moved_near_total ?? 0);
    const fragmentCandidates = Number(p.fragment_candidates ?? 0);
    const filesRemoved = Number(p.progress_files_removed ?? 0);
    const pipelineTimestamp = String(p.timestamp_utc ?? "n/a");

    return (
        <div className="space-y-6">
            {/* Breadcrumb + Header */}
            <div>
                <div className="flex items-center gap-2 text-xs text-zinc-500 mb-3">
                    <Link
                        href="/projects"
                        className="hover:text-cyan-400 transition-colors"
                    >
                        Projects
                    </Link>
                    <span>/</span>
                    <span className="text-zinc-300">{data.slug}</span>
                </div>
                <PageHeader
                    icon="📂"
                    title={data.name}
                    subtitle={`projects/${data.slug} · ${data.files.length} files`}
                />
            </div>

            {/* Case-specific stats (if claim data exists) */}
            {hasClaims && (
                <>
                    <div className="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-5">
                        <StatCard
                            value={data.allClaims.length}
                            label="Stage 1 Claims"
                            sublabel="Hypotheses identified"
                            variant="cyan"
                            icon="🔍"
                        />
                        <StatCard
                            value={data.drReports.length}
                            label="Deep Research"
                            sublabel="Reports completed"
                            variant="purple"
                            icon="🧬"
                        />
                        <StatCard
                            value={data.confidenceCounts.high}
                            label="High Confidence"
                            sublabel="Ready for Stage 2"
                            variant="emerald"
                            icon="✅"
                        />
                        <StatCard
                            value={nearPending}
                            label="Near Dupes"
                            sublabel="Pending review"
                            variant="amber"
                            icon="📋"
                        />
                        <div className="col-span-2 md:col-span-1">
                            <StatCard
                                value={totalFilesCurrent.toLocaleString()}
                                label="Case Files"
                                sublabel={`of ${totalFilesBaseline.toLocaleString()} baseline`}
                                variant="rose"
                                icon="🗂️"
                            />
                        </div>
                    </div>

                    {/* Pipeline + Claim Distribution */}
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                        <div className="glass-card p-6">
                            <h2 className="section-header text-lg font-bold">
                                📊 Case Pipeline
                            </h2>
                            <div className="mt-5 flex items-center gap-6">
                                <ProgressRing percent={progressPct} />
                                <div className="space-y-2 text-sm">
                                    <div className="flex items-center gap-2">
                                        <span className="w-2 h-2 rounded-full bg-emerald-400" />
                                        <span className="text-zinc-400">Exact moved:</span>
                                        <span className="font-semibold text-zinc-200">
                                            {exactMoved}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className="w-2 h-2 rounded-full bg-amber-400" />
                                        <span className="text-zinc-400">Near moved:</span>
                                        <span className="font-semibold text-zinc-200">
                                            {nearMoved}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className="w-2 h-2 rounded-full bg-rose-400" />
                                        <span className="text-zinc-400">Fragments:</span>
                                        <span className="font-semibold text-zinc-200">
                                            {fragmentCandidates}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className="w-2 h-2 rounded-full bg-cyan-400" />
                                        <span className="text-zinc-400">Removed:</span>
                                        <span className="font-semibold text-zinc-200">
                                            {filesRemoved}
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <p className="mt-4 text-[10px] font-mono text-zinc-600">
                                Last run: {pipelineTimestamp}{" "}
                                <span className="text-zinc-700">
                                    ({timeAgo(pipelineTimestamp)})
                                </span>
                            </p>
                        </div>

                        <div className="glass-card p-6 lg:col-span-2">
                            <h2 className="section-header text-lg font-bold">
                                📈 Claim Distribution
                            </h2>
                            <div className="mt-5 grid gap-2.5 md:grid-cols-2">
                                {Object.entries(data.categoryCounts)
                                    .sort(([, a], [, b]) => b - a)
                                    .map(([cat, count]) => {
                                        const pct = Math.round(
                                            (count / data.allClaims.length) * 100
                                        );
                                        return (
                                            <div key={cat}>
                                                <div className="flex items-center justify-between mb-1">
                                                    <CategoryPill category={cat} />
                                                    <span className="text-xs text-zinc-400 font-mono">
                                                        {count} ({pct}%)
                                                    </span>
                                                </div>
                                                <div className="h-1.5 rounded-full bg-zinc-800/50 overflow-hidden">
                                                    <div
                                                        className="h-full rounded-full"
                                                        style={{
                                                            width: `${pct}%`,
                                                            background: `linear-gradient(90deg, rgba(0,229,255,0.6), rgba(168,85,247,0.6))`,
                                                        }}
                                                    />
                                                </div>
                                            </div>
                                        );
                                    })}
                            </div>
                        </div>
                    </div>

                    {/* Top 10 Priorities */}
                    <div className="glass-card p-6">
                        <h2 className="section-header text-lg font-bold">
                            🎯 Top 10 Priority Claims
                        </h2>
                        <p className="mt-1 text-xs text-zinc-500">
                            Ranked for immediate deep research
                        </p>
                        <div className="mt-5 grid gap-2 md:grid-cols-2">
                            {data.stage1Top10.map((claimId, i) => {
                                const claim = data.allClaims.find(
                                    (c) => c.id === claimId
                                );
                                const hasReport = data.drReports.some(
                                    (r) => r.claimId === claimId
                                );
                                return (
                                    <div key={claimId} className="priority-item">
                                        <span
                                            className={`priority-rank ${i < 3 ? "top-3" : "mid"}`}
                                        >
                                            {i + 1}
                                        </span>
                                        <div className="min-w-0 flex-1">
                                            <p className="font-mono text-sm text-zinc-200 truncate">
                                                {claimId}
                                            </p>
                                            {claim && (
                                                <p className="text-[11px] text-zinc-500 truncate">
                                                    {claim.title}
                                                </p>
                                            )}
                                        </div>
                                        <div className="flex items-center gap-2 flex-shrink-0">
                                            {claim && (
                                                <ConfidenceBadge level={claim.confidence} />
                                            )}
                                            {hasReport && (
                                                <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                                                    DR
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Deep Research Reports */}
                    <div className="glass-card p-6">
                        <h2 className="section-header text-lg font-bold">
                            🧬 Deep Research Reports
                        </h2>
                        <p className="mt-1 text-xs text-zinc-500">
                            {data.drReports.length} reports
                        </p>
                        <div className="mt-5 grid gap-4 lg:grid-cols-2">
                            {data.drReports.map((r) => (
                                <article
                                    key={r.file}
                                    className={`dr-card ${r.confidence.toLowerCase().replace(/\s+/g, "-")}`}
                                >
                                    <div className="flex flex-wrap items-center gap-2 mb-3">
                                        <CategoryPill category={r.category} />
                                        <ConfidenceBadge level={r.confidence} />
                                    </div>
                                    <h3 className="font-mono text-sm font-semibold text-zinc-100">
                                        {r.claimId}
                                    </h3>
                                    <p className="mt-2 text-sm text-zinc-400 leading-relaxed line-clamp-3">
                                        {r.summary}
                                    </p>
                                    <div className="mt-3 flex items-center justify-between text-[10px] text-zinc-600 font-mono">
                                        <span>dr/{r.file}</span>
                                        <span>{r.updatedAt}</span>
                                    </div>
                                </article>
                            ))}
                        </div>
                    </div>

                    {/* All Claims */}
                    <div className="glass-card p-6">
                        <h2 className="section-header text-lg font-bold">
                            📋 All Stage 1 Claims ({data.allClaims.length})
                        </h2>
                        <div className="mt-5 space-y-6">
                            {Object.entries(data.categoryCounts)
                                .sort(([, a], [, b]) => b - a)
                                .map(([cat]) => {
                                    const claims = data.allClaims.filter(
                                        (c) => c.category === cat
                                    );
                                    return (
                                        <div key={cat}>
                                            <div className="flex items-center gap-3 mb-3">
                                                <CategoryPill category={cat} />
                                                <span className="text-xs text-zinc-500 font-mono">
                                                    {claims.length} claim
                                                    {claims.length !== 1 ? "s" : ""}
                                                </span>
                                            </div>
                                            <div className="grid gap-1.5 md:grid-cols-2">
                                                {claims.map((c) => {
                                                    const hasReport = data.drReports.some(
                                                        (r) => r.claimId === c.id
                                                    );
                                                    return (
                                                        <div
                                                            key={c.id}
                                                            className="flex items-center gap-3 px-3 py-2 rounded-lg bg-zinc-900/30 border border-zinc-800/30 hover:border-zinc-700/50 transition-colors"
                                                        >
                                                            <div className="min-w-0 flex-1">
                                                                <p className="font-mono text-xs text-zinc-300 truncate">
                                                                    {c.id}
                                                                </p>
                                                                <p className="text-[10px] text-zinc-600 truncate">
                                                                    {c.title}
                                                                </p>
                                                            </div>
                                                            <div className="flex items-center gap-1.5 flex-shrink-0">
                                                                <ConfidenceBadge
                                                                    level={c.confidence}
                                                                />
                                                                {hasReport && (
                                                                    <span className="text-[9px] px-1 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                                                                        DR
                                                                    </span>
                                                                )}
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    );
                                })}
                        </div>
                    </div>
                </>
            )}

            {/* README */}
            {data.readme && !hasClaims && (
                <div className="glass-card p-6">
                    <h2 className="section-header text-lg font-bold mb-4">
                        📄 README
                    </h2>
                    <pre className="memory-log rounded-xl bg-zinc-950/50 p-4 border border-zinc-800/30 max-h-96 overflow-y-auto whitespace-pre-wrap">
                        {data.readme}
                    </pre>
                </div>
            )}

            {/* Project Files */}
            <div className="glass-card p-6">
                <h2 className="section-header text-lg font-bold mb-4">
                    📁 Project Files ({data.files.length})
                </h2>
                <div className="grid gap-1 md:grid-cols-2 lg:grid-cols-3 max-h-72 overflow-y-auto pr-2">
                    {data.files.slice(0, 60).map((f) => (
                        <div
                            key={f}
                            className="flex items-center gap-2 px-2 py-1.5 rounded text-xs font-mono text-zinc-500 hover:bg-zinc-800/30 transition-colors"
                        >
                            <span className="text-zinc-600">
                                {(f as string).endsWith("/") ? "📁" : "📄"}
                            </span>
                            <span className="truncate">{f as string}</span>
                        </div>
                    ))}
                    {data.files.length > 60 && (
                        <p className="text-xs text-zinc-600 px-2 py-1">
                            + {data.files.length - 60} more files
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}
