from pathlib import Path

from app.claim_loop.report import run_claim_loop


def test_claim_loop_outputs(tmp_path: Path):
    case = tmp_path / "case"
    (case / "02_OUTPUT").mkdir(parents=True)
    (case / "notes.txt").write_text("Monitoring fee and photo references via email.", encoding="utf-8")

    out = run_claim_loop(case, max_claims=4)
    assert out["claims_count"] >= 1
    assert Path(out["jsonl_path"]).exists()
    assert Path(out["review_path"]).exists()
