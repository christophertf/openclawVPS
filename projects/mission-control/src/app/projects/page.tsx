import Link from "next/link";
import { discoverProjects, getProjectRegistry } from "@/app/lib/data";
import { PageHeader } from "@/app/components/ui";

export const dynamic = "force-dynamic";

export default async function ProjectsPage() {
    const [projects, registry] = await Promise.all([
        discoverProjects(),
        getProjectRegistry(),
    ]);

    // Build a lookup: slug → registry entry
    const regMap = new Map(registry.projects.map((r) => [r.slug, r]));

    return (
        <div className="space-y-6">
            <PageHeader
                icon="📂"
                title="Projects"
                subtitle="All active workstreams and project spaces"
            />

            <div className="grid gap-4 md:grid-cols-2">
                {projects.map((p) => {
                    const reg = regMap.get(p.slug);
                    return (
                        <Link
                            key={p.slug}
                            href={`/projects/${p.slug}`}
                            className="project-card group"
                        >
                            <div className="flex items-start justify-between mb-2">
                                <h2 className="text-lg font-bold text-zinc-100 group-hover:text-cyan-300 transition-colors">
                                    {p.name}
                                </h2>
                                <span className="text-xs text-zinc-600 font-mono flex-shrink-0 ml-3">
                                    {p.fileCount} files
                                </span>
                            </div>
                            {p.description && (
                                <p className="text-sm text-zinc-400 leading-relaxed mb-3">
                                    {p.description}
                                </p>
                            )}
                            <div className="flex items-center gap-2 flex-wrap">
                                {p.hasReadme && (
                                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/20">
                                        README
                                    </span>
                                )}
                                {reg?.channel && (
                                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/15 text-purple-400 border border-purple-500/20 font-mono">
                                        {reg.channel}
                                    </span>
                                )}
                                {reg?.status && (
                                    <span
                                        className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${reg.status === "active"
                                                ? "bg-cyan-500/15 text-cyan-400 border border-cyan-500/20"
                                                : "bg-zinc-700/30 text-zinc-500 border border-zinc-700/30"
                                            }`}
                                    >
                                        {reg.status}
                                    </span>
                                )}
                                {!reg && (
                                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/20">
                                        unregistered
                                    </span>
                                )}
                                <span className="text-[10px] font-mono text-zinc-600">
                                    projects/{p.slug}
                                </span>
                            </div>
                        </Link>
                    );
                })}

                {projects.length === 0 && (
                    <div className="glass-card p-8 col-span-full flex flex-col items-center text-center">
                        <span className="text-4xl mb-3 opacity-40">📂</span>
                        <p className="text-sm text-zinc-500">
                            No projects found in workspace.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
