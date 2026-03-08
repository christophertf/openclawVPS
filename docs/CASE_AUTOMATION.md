# CASE_AUTOMATION

## Intake Source (authoritative)
- `/home/claw/CASE_FILES`

## Processing Snapshot
- `/home/claw/CASE_MASTER` (hardlinked refresh each run)

## Outputs
- `/home/claw/.openclaw/workspace/reports/case_pipeline/status.json`
- `/home/claw/.openclaw/workspace/reports/case_pipeline/inventory.csv`
- `/home/claw/.openclaw/workspace/reports/case_pipeline/exact_duplicates.csv`
- `/home/claw/.openclaw/workspace/reports/case_pipeline/near_duplicates.csv`
- `/home/claw/.openclaw/workspace/reports/case_pipeline/fragment_candidates.txt`
- `/home/claw/.openclaw/workspace/reports/case_pipeline/CASE_ACTIONS.md`
- `/home/claw/.openclaw/workspace/reports/case_pipeline/CASE_QUESTIONS.md`

## Automation
Cron jobs installed:
- Every 10 minutes: iterative pipeline run with progress append

Behavior now:
- Exact duplicates are auto-moved out of `/home/claw/CASE_FILES` into recoverable trash:
  - `/home/claw/.trash/case_dedupe/exact_auto/<run-tag>/...`
- Near-duplicate candidates are queued for decision in:
  - `/home/claw/.openclaw/workspace/reports/case_pipeline/near_approvals.json`
  - status values: `pending`, `keep_a`, `keep_b`, `skip`
- Approved near decisions are applied on the next cron run.

## Manual run
```bash
/home/claw/.openclaw/workspace/scripts/case_pipeline.sh
```

## Your workflow
1. Add files locally to `CASE_FILES`
2. Sync to VPS (`/home/claw/CASE_FILES`)
3. Tell CLAW to proceed
