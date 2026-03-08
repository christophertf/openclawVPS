from __future__ import annotations

import argparse
from pathlib import Path

from app.evidence_vault.vault import ingest_case_bundle
from app.cpra.report import analyze_case
from app.claim_loop.report import run_claim_loop


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forensic-cpra")
    sub = parser.add_subparsers(dest="domain", required=True)

    vault = sub.add_parser("vault", help="Evidence vault operations")
    vault_sub = vault.add_subparsers(dest="action", required=True)
    ingest = vault_sub.add_parser("ingest", help="Ingest immutable originals into read-only vault")
    ingest.add_argument("--case-dir", required=True, help="Path to case bundle directory")

    cpra = sub.add_parser("cpra", help="CPRA operations")
    cpra_sub = cpra.add_subparsers(dest="action", required=True)
    analyze = cpra_sub.add_parser("analyze", help="Analyze CPRA timeline from case.yaml")
    analyze.add_argument("--case", required=True, help="Path to case.yaml")

    claim = sub.add_parser("claim-loop", help="Agentic claim discovery loop")
    claim_sub = claim.add_subparsers(dest="action", required=True)
    claim_run = claim_sub.add_parser("run", help="Discover and log candidate claims")
    claim_run.add_argument("--case-dir", required=True, help="Path to case bundle directory")
    claim_run.add_argument("--max-claims", type=int, default=20, help="Maximum claims to log")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.domain == "vault" and args.action == "ingest":
        case_dir = Path(args.case_dir).resolve()
        result = ingest_case_bundle(case_dir)
        print(f"Ingested {result['ingested_count']} files")
        print(f"Manifest: {result['manifest_path']}")
        return 0

    if args.domain == "cpra" and args.action == "analyze":
        case_path = Path(args.case).resolve()
        out = analyze_case(case_path)
        print(f"Report: {out['report_path']}")
        print(f"Events JSON: {out['events_path']}")
        print(f"Findings JSON: {out['findings_path']}")
        return 0

    if args.domain == "claim-loop" and args.action == "run":
        case_dir = Path(args.case_dir).resolve()
        out = run_claim_loop(case_dir, max_claims=args.max_claims)
        print(f"Claims: {out['claims_count']}")
        print(f"JSONL: {out['jsonl_path']}")
        print(f"Review: {out['review_path']}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
