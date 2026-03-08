from __future__ import annotations

from pathlib import Path
import yaml


def load_case_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("case.yaml must parse to an object")
    if "request_received_datetime" not in data:
        raise ValueError("Missing request_received_datetime")
    data.setdefault("agency_responses", [])
    return data
