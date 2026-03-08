"use client";

import { useEffect, useState, useRef } from "react";

type LogEntry = {
    label: string;
    lines: string[];
    mtime: string;
    size: number;
};

type LogPayload = {
    entries: LogEntry[];
    timestamp: string;
};

const POLL_INTERVAL = 5000; // 5 seconds

export default function TerminalWindow() {
    const [data, setData] = useState<LogPayload | null>(null);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        let running = true;

        async function poll() {
            try {
                const res = await fetch("/api/logs", { cache: "no-store" });
                if (res.ok) {
                    const payload = await res.json();
                    setData(payload);
                }
            } catch { /* ignore */ }
            if (running) setTimeout(poll, POLL_INTERVAL);
        }

        poll();
        return () => { running = false; };
    }, []);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [data]);

    // Flatten all entries into a single timeline. 
    // We sort by mtime so the most recently updated log source is at the bottom.
    const allLines = data?.entries
        .sort((a, b) => new Date(a.mtime).getTime() - new Date(b.mtime).getTime())
        .flatMap(e => e.lines.map(l => ({ label: e.label, text: l }))) || [];

    return (
        <div className="glass-card overflow-hidden flex flex-col" style={{ height: "100%" }}>
            {/* Tab bar / header */}
            <div className="flex items-center gap-1 px-3 pt-2 pb-2 border-b border-zinc-800/40 flex-shrink-0">
                <div className="flex gap-1.5 mr-3">
                    <span className="w-2.5 h-2.5 rounded-full bg-red-500/60" />
                    <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/60" />
                    <span className="w-2.5 h-2.5 rounded-full bg-green-500/60" />
                </div>
                <span className="text-[11px] font-mono text-zinc-400">System Unified Feed </span>
                {data && (
                    <span className="ml-auto flex items-center gap-1.5 text-[9px] text-emerald-500/70">
                        <span className="pulse-dot bg-emerald-500" style={{ width: 5, height: 5 }} />
                        watching {data.entries.length} targets
                    </span>
                )}
            </div>

            {/* Terminal body - Single Unified Pane */}
            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto p-3 font-mono text-[11px] leading-relaxed break-words whitespace-pre-wrap"
                style={{ background: "rgba(0,0,0,0.4)" }}
            >
                {!data && (
                    <div className="text-zinc-600">connecting...</div>
                )}
                {data && allLines.length === 0 && (
                    <div className="text-zinc-600">no active system events</div>
                )}
                {allLines.map((line, i) => {
                    const isSuccess = line.text.includes("[done]") || line.text.includes("OK") || line.text.includes("complete");
                    const isError = line.text.includes("[error]") || line.text.includes("ERROR") || line.text.includes("FAIL");
                    const isWarn = line.text.includes("[warn]") || line.text.includes("WARNING");

                    const textColor = isSuccess ? "text-emerald-400"
                        : isError ? "text-red-400"
                            : isWarn ? "text-amber-400"
                                : "text-zinc-400";

                    return (
                        <div key={i} className="flex items-start gap-3 hover:bg-white/5 px-1 py-0.5 rounded transition-colors">
                            <span className="text-zinc-600 w-28 flex-shrink-0 text-right select-none uppercase tracking-wider text-[9px] pt-0.5">
                                [{line.label}]
                            </span>
                            <span className={`flex-1 ${textColor}`}>
                                {line.text}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
