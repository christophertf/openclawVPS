import { categoryClass } from "@/app/lib/data";

/* ── Confidence Badge ── */
export function ConfidenceBadge({ level }: { level: string }) {
    const normalized = level.toLowerCase().replace(/\s+/g, "-");
    return (
        <span
            className={`confidence-${normalized} inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold`}
        >
            {level}
        </span>
    );
}

/* ── Category Pill ── */
export function CategoryPill({ category }: { category: string }) {
    return (
        <span className={`category-pill border ${categoryClass(category)}`}>
            {category}
        </span>
    );
}

/* ── Stat Card ── */
export function StatCard({
    value,
    label,
    sublabel,
    variant = "cyan",
    icon,
}: {
    value: string | number;
    label: string;
    sublabel?: string;
    variant?: "cyan" | "purple" | "emerald" | "amber" | "rose";
    icon: string;
}) {
    return (
        <div className={`stat-card ${variant}`}>
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                        {label}
                    </p>
                    <p className="stat-number mt-1">{value}</p>
                    {sublabel && (
                        <p className="mt-1 text-xs text-zinc-500">{sublabel}</p>
                    )}
                </div>
                <span className="text-2xl opacity-60">{icon}</span>
            </div>
        </div>
    );
}

/* ── Progress Ring ── */
export function ProgressRing({
    percent,
    size = 100,
}: {
    percent: number;
    size?: number;
}) {
    const radius = 38;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percent / 100) * circumference;

    return (
        <div
            className="progress-ring-container"
            style={{ width: size, height: size }}
        >
            <svg
                className="progress-ring"
                width={size}
                height={size}
                viewBox="0 0 100 100"
            >
                <defs>
                    <linearGradient
                        id="progressGradient"
                        x1="0%"
                        y1="0%"
                        x2="100%"
                        y2="100%"
                    >
                        <stop offset="0%" stopColor="#00e5ff" />
                        <stop offset="100%" stopColor="#a855f7" />
                    </linearGradient>
                </defs>
                <circle className="progress-ring-bg" cx="50" cy="50" r={radius} />
                <circle
                    className="progress-ring-fill"
                    cx="50"
                    cy="50"
                    r={radius}
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                />
            </svg>
            <div className="progress-ring-text">{percent}%</div>
        </div>
    );
}

/* ── Health Status Badge ── */
export function HealthBadge({
    status,
    detail,
}: {
    status: "ok" | "warning" | "error";
    detail: string;
}) {
    const cls =
        status === "ok"
            ? "ok-badge"
            : status === "warning"
                ? "warning-badge"
                : "error-badge";
    const icon = status === "ok" ? "✓" : status === "warning" ? "⚠️" : "❌";
    return (
        <span className={cls}>
            {icon} {detail}
        </span>
    );
}

/* ── Page Header ── */
export function PageHeader({
    icon,
    title,
    subtitle,
}: {
    icon: string;
    title: string;
    subtitle?: string;
}) {
    return (
        <div className="mb-6">
            <h1 className="flex items-center gap-3 text-2xl font-black tracking-tight md:text-3xl">
                <span>{icon}</span>
                <span className="gradient-text">{title}</span>
            </h1>
            {subtitle && (
                <p className="mt-1 text-sm text-zinc-500">{subtitle}</p>
            )}
        </div>
    );
}

/* ── Empty State ── */
export function EmptyState({
    icon,
    message,
}: {
    icon: string;
    message: string;
}) {
    return (
        <div className="flex flex-col items-center justify-center py-12 text-center">
            <span className="text-4xl mb-3 opacity-40">{icon}</span>
            <p className="text-sm text-zinc-500">{message}</p>
        </div>
    );
}
