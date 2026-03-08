from __future__ import annotations

import json
import shutil
from datetime import datetime, UTC
from pathlib import Path

from app.evidence_vault.manifest import sha256_file


def ingest_case_bundle(case_dir: Path) -> dict:
    originals = case_dir / "00_ORIGINALS_IMMUTABLE"
    vault = case_dir / "00_VAULT"
    logs = case_dir / "03_LOGS"
    logs.mkdir(parents=True, exist_ok=True)
    vault.mkdir(parents=True, exist_ok=True)

    if not originals.exists() or not originals.is_dir():
        raise FileNotFoundError(f"Missing originals folder: {originals}")

    files = sorted([p for p in originals.rglob("*") if p.is_file()], key=lambda p: p.relative_to(originals).as_posix())

    manifest_files = []
    for src in files:
        rel = src.relative_to(originals)
        dst = vault / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            try:
                dst.chmod(0o644)
            except PermissionError:
                pass
        shutil.copy2(src, dst)
        try:
            dst.chmod(0o444)
        except PermissionError:
            pass

        manifest_files.append(
            {
                "relative_path": rel.as_posix(),
                "size_bytes": src.stat().st_size,
                "mtime_epoch": int(src.stat().st_mtime),
                "sha256": sha256_file(dst),
            }
        )

    manifest = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "case_dir": str(case_dir),
        "source_dir": str(originals),
        "vault_dir": str(vault),
        "file_count": len(manifest_files),
        "files": manifest_files,
    }

    manifest_path = vault / "CHAIN_OF_CUSTODY_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return {
        "ingested_count": len(manifest_files),
        "manifest_path": str(manifest_path),
    }
