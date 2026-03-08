from __future__ import annotations

ALLOWED = {
    "cpra_violation": "allowed",
    "native_format_violation": "allowed",
    "fee_dispute": "analysis_only",
}
BLOCKED = {"spoliation", "criminal_fraud"}


def validate_claims(claims: list[str]) -> None:
    for c in claims:
        key = c.strip().lower()
        if key in BLOCKED:
            raise ValueError(f"Blocked claim type: {key}")
