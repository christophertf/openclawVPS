from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path

from app.cpra.parser import load_case_yaml
from app.cpra.deadline_math import compute_deadlines
from app.gates.evidentiary_gate import validate_claims


def _run_dir(case_dir: Path) -> Path:
    stamp = datetime.now(UTC).strftime("run_%Y%m%d_%H%M%S")
    out = case_dir / "02_OUTPUT" / stamp
    out.mkdir(parents=True, exist_ok=True)
    return out


def analyze_case(case_yaml: Path) -> dict:
    case_data = load_case_yaml(case_yaml)
    validate_claims(case_data.get("claims", []))
    findings = compute_deadlines(case_data)

    case_dir = case_yaml.parent
    out = _run_dir(case_dir)

    events_path = out / "cpra_events.json"
    findings_path = out / "cpra_findings.json"
    report_path = out / "cpra_report.md"

    events_path.write_text(json.dumps(case_data, indent=2), encoding="utf-8")
    findings_path.write_text(json.dumps(findings, indent=2), encoding="utf-8")

    lines = [
        "# CPRA Compliance Report (MVP)",
        "",
        f"- Request received: `{findings['request_received_datetime']}`",
        f"- Determination deadline (10 days): `{findings['determination_deadline']}`",
        f"- Extension claimed: `{findings['extension_claimed']}`",
        f"- Extended deadline (+14 days): `{findings['extended_deadline']}`",
        f"- Effective deadline: `{findings['effective_deadline']}`",
        f"- Determination on time: `{findings['determination_on_time']}`",
        "",
        "## Notes",
        "- Output is factual deadline math only (no legal conclusions).",
        "- Verify timezone and business-day logic before legal filing use.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "events_path": str(events_path),
        "findings_path": str(findings_path),
        "report_path": str(report_path),
    }
