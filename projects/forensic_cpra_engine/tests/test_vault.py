from pathlib import Path
import json

from app.evidence_vault.vault import ingest_case_bundle


def test_vault_manifest_is_deterministic(tmp_path: Path):
    case = tmp_path / "case"
    originals = case / "00_ORIGINALS_IMMUTABLE"
    originals.mkdir(parents=True)
    (originals / "a.txt").write_text("alpha", encoding="utf-8")
    (originals / "b.txt").write_text("beta", encoding="utf-8")

    res1 = ingest_case_bundle(case)
    m1 = json.loads(Path(res1["manifest_path"]).read_text(encoding="utf-8"))

    res2 = ingest_case_bundle(case)
    m2 = json.loads(Path(res2["manifest_path"]).read_text(encoding="utf-8"))

    list1 = [{k: f[k] for k in ("relative_path", "size_bytes", "sha256")} for f in m1["files"]]
    list2 = [{k: f[k] for k in ("relative_path", "size_bytes", "sha256")} for f in m2["files"]]
    assert list1 == list2
