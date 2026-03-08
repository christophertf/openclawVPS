from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from app.claim_loop.models import ClaimRecord, EvidenceRef


RULES = [
    {
        "id": "CLM-001",
        "type": "record_completeness",
        "text": "Monitoring fee actions appear in timeline; verify whether corresponding monitoring reports are fully present in case records.",
        "must": ["monitoring", "fee"],
        "nice": ["report", "order imposing"],
        "next": "Confirm/deny existence and location of all monitoring reports supporting listed monitoring fee actions.",
        "limitations": "Keyword evidence from timeline/events; full document inventory reconciliation may still be needed.",
    },
    {
        "id": "CLM-002",
        "type": "record_completeness",
        "text": "Case activity repeatedly references photos; verify all referenced photos/declarations are present and linked to event entries.",
        "must": ["photo"],
        "nice": ["photograph declaration", "take photos"],
        "next": "Confirm/deny that every photo reference has retrievable source file, timestamp, and case linkage.",
        "limitations": "References found by text; binary photo package completeness not yet cryptographically reconciled to every mention.",
    },
    {
        "id": "CLM-003",
        "type": "communications_integrity",
        "text": "External email/message activity appears in timeline; verify underlying communications and attachments are preserved in official case file.",
        "must": ["email"],
        "nice": ["external message", "outlook"],
        "next": "Confirm/deny retention of all external communications, including attachments and message metadata.",
        "limitations": "Current pass checks narrative entries; mailbox export parity check pending.",
    },
    {
        "id": "CLM-004",
        "type": "notice_reliability",
        "text": "Repeated returned/undeliverable mail entries suggest notice-delivery reliability issues that should be reconciled against enforcement steps.",
        "must": ["return to sender"],
        "nice": ["unclaimed", "not deliverable"],
        "next": "Confirm/deny how notice failures were handled before subsequent enforcement escalation.",
        "limitations": "This flags delivery-risk pattern only; legal sufficiency requires procedural record review.",
    },
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_event_text(case_dir: Path) -> Iterable[tuple[str, str, str, str]]:
    events_path = Path("/home/claw/CASE_FILES/timeline/events.json")
    if events_path.exists():
        data = json.loads(events_path.read_text(encoding="utf-8"))
        for i, ev in enumerate(data):
            summary = str(ev.get("summary") or "")
            details = str(ev.get("details") or "")
            ts = str(ev.get("timestamp") or ev.get("date") or ev.get("datetime") or "")
            text = f"{summary}\n{details}".strip()
            if text:
                yield (str(events_path), f"event_index:{i}", ts, text)

    # Also scan local markdown/text notes in case bundle
    for p in sorted(case_dir.rglob("*")):
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".yaml", ".yml", ".json"}:
            try:
                raw = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            lines = raw.splitlines()
            for idx, line in enumerate(lines, start=1):
                if line.strip():
                    yield (str(p), f"line:{idx}", "", line.strip())


def mine_claims(case_dir: Path, max_claims: int = 20) -> list[ClaimRecord]:
    corpus = list(_iter_event_text(case_dir))
    claims: list[ClaimRecord] = []

    for rule in RULES:
        evidence: list[EvidenceRef] = []
        for path, line_ref, ts, text in corpus:
            low = text.lower()
            if all(m in low for m in rule["must"]):
                if any(n in low for n in rule["nice"]):
                    evidence.append(
                        EvidenceRef(
                            path=path,
                            quote=text[:500],
                            timestamp=ts,
                            page_or_line=line_ref,
                            sha256=_sha256(Path(path)) if Path(path).exists() else "",
                        )
                    )
            if len(evidence) >= 8:
                break

        status = "supported" if len(evidence) >= 2 else "unproven"
        confidence = 0.82 if status == "supported" else 0.35

        claims.append(
            ClaimRecord(
                claim_id=rule["id"],
                claim_text=rule["text"],
                claim_type=rule["type"],
                status=status,
                confidence=confidence,
                evidence=evidence,
                counter_evidence=[],
                law_refs=[],
                next_action=rule["next"],
                limitations=rule["limitations"],
            )
        )

    # keep best supported first
    claims.sort(key=lambda c: (c.status != "supported", -len(c.evidence), c.claim_id))
    return claims[:max_claims]
