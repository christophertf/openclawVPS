# SYSTEM CLEANUP & AUTOMATION PLAN

Updated: 2026-03-04 UTC
Owner: Claw

## Objective
Stabilize and de-clutter the host with repeatable maintenance jobs, visibility, and a no-repeat task loop.

## Phases
1. Baseline inventory (disk, top space consumers, temp/cache growth)
2. Safe cleanup pass (user-space caches/log noise/transient files)
3. Automation (scheduled cron jobs)
4. Reporting (daily/weekly summaries)
5. Continuous refinement (task backlog + completion tracking)

## Guardrails
- Prefer safe cleanup of transient data only.
- No destructive deletion of user project outputs.
- Keep logs for all automated runs.
- Record every run outcome in reports.

## Scheduled jobs
- Every 6h: safe cleanup pass
- Daily: deep user-cache cleanup + report
- Weekly: heavier archive/compression of old logs

## Success criteria
- Disk usage trend stable/down over 7 days.
- No recurring temp/cache bloat spikes.
- Reports generated automatically and readable.
