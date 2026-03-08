from __future__ import annotations

from datetime import datetime, timedelta


ALLOWED_TYPES = {"determination", "extension", "production", "denial"}


def compute_deadlines(case_data: dict) -> dict:
    req = datetime.fromisoformat(case_data["request_received_datetime"])
    determination_deadline = req + timedelta(days=10)
    extension_deadline = determination_deadline + timedelta(days=14)

    responses = case_data.get("agency_responses", [])
    normalized = []
    has_extension = False

    for r in responses:
        r_type = r.get("response_type", "").strip().lower()
        if r_type not in ALLOWED_TYPES:
            raise ValueError(f"Invalid response_type: {r_type}")
        ts = datetime.fromisoformat(r["response_datetime"])
        has_extension = has_extension or r_type == "extension"
        normalized.append({**r, "_dt": ts, "response_type": r_type})

    det_on_time = any(
        r["response_type"] in {"determination", "denial"} and r["_dt"] <= determination_deadline
        for r in normalized
    )

    if has_extension:
        limit = extension_deadline
    else:
        limit = determination_deadline

    findings = {
        "request_received_datetime": req.isoformat(),
        "determination_deadline": determination_deadline.isoformat(),
        "extension_claimed": has_extension,
        "extended_deadline": extension_deadline.isoformat(),
        "effective_deadline": limit.isoformat(),
        "determination_on_time": det_on_time,
    }
    return findings
