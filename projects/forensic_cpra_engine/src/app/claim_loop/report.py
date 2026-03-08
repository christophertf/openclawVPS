from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path

from app.claim_loop.mine import mine_claims


def _run_dir(case_dir: Path) -> Path:
    stamp = datetime.now(UTC).strftime("run_%Y%m%d_%H%M%S")
    out = case_dir / "02_OUTPUT" / stamp
    out.mkdir(parents=True, exist_ok=True)
    return out


def run_claim_loop(case_dir: Path, max_claims: int = 20) -> dict:
    out = _run_dir(case_dir)
    claims = mine_claims(case_dir, max_claims=max_claims)

    jsonl_path = out / "claims_log.jsonl"
    md_path = out / "claims_review.md"

    with jsonl_path.open("w", encoding="utf-8") as f:
        for c in claims:
            f.write(json.dumps(c.to_dict(), ensure_ascii=False) + "\n")

    lines = ["# Claims Review", "", "Conservative, evidence-linked candidate claims.", ""]
    for c in claims:
        lines += [
            f"## {c.claim_id} — {c.claim_type}",
            f"- Status: **{c.status}**",
            f"- Confidence: **{c.confidence:.2f}**",
            f"- Claim: {c.claim_text}",
            f"- Next action: {c.next_action}",
            f"- Limitations: {c.limitations}",
            "- Evidence:",
        ]
        if not c.evidence:
            lines.append("  - (none found yet)")
        else:
            for e in c.evidence[:6]:
                lines.append(f"  - `{e.path}` ({e.page_or_line})")
                if e.timestamp:
                    lines.append(f"    - ts: `{e.timestamp}`")
                lines.append(f"    - sha256: `{e.sha256}`")
                lines.append(f"    - quote: {e.quote[:240].replace(chr(10), ' ')}")
        lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "claims_count": len(claims),
        "jsonl_path": str(jsonl_path),
        "review_path": str(md_path),
        "run_dir": str(out),
    }
