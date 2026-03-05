#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="/home/claw/.openclaw/workspace/reports/case_pipeline/logs"
mkdir -p "$LOG_DIR"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$LOG_DIR/run-$TS.log"

python3 /home/claw/.openclaw/workspace/scripts/case_pipeline.py | tee -a "$LOG"

echo "$TS completed" >> /home/claw/.openclaw/workspace/reports/case_pipeline/runs.log
