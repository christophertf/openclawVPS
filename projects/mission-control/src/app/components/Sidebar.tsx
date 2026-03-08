"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

type NavItem = {
    href: string;
    label: string;
    icon: string;
    badge?: string;
};

const NAV_ITEMS: NavItem[] = [
    { href: "/", label: "Dashboard", icon: "⚡" },
    { href: "/projects", label: "Projects", icon: "📂" },
    { href: "/agents", label: "Agents & Identity", icon: "🤖" },
    { href: "/memory", label: "Memory & Journal", icon: "🧠" },
    { href: "/cron", label: "Cron & Automation", icon: "⏱️" },
    { href: "/activity", label: "Live Feed", icon: "📡" },
    { href: "/commands", label: "Command Reference", icon: "📋" },
    { href: "/tools", label: "Tools & Capabilities", icon: "🔧" },
    { href: "/settings", label: "Settings", icon: "⚙️" },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="sidebar">
            {/* Brand */}
            <div className="sidebar-brand">
                <div className="brand-icon">🐾</div>
                <div>
                    <h1 className="brand-title">CLAW</h1>
                    <span className="brand-subtitle">Mission Control</span>
                </div>
            </div>

            {/* Status indicator */}
            <div className="sidebar-status">
                <div className="pulse-dot" />
                <span className="status-text">System Online</span>
            </div>

            {/* Navigation */}
            <nav className="sidebar-nav">
                {NAV_ITEMS.map((item) => {
                    const isActive =
                        item.href === "/"
                            ? pathname === "/"
                            : pathname.startsWith(item.href);
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`nav-item ${isActive ? "nav-item-active" : ""}`}
                        >
                            <span className="nav-icon">{item.icon}</span>
                            <span className="nav-label">{item.label}</span>
                            {item.badge && <span className="nav-badge">{item.badge}</span>}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer */}
            <div className="sidebar-footer">
                <div className="footer-line">v2.0 — OpenClaw</div>
                <div className="footer-line dim">Workspace Dashboard</div>
            </div>
        </aside>
    );
}
