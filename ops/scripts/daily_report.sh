#!/usr/bin/env bash
set -euo pipefail
TS=$(date -u +%Y%m%d)
OUT="/home/claw/.openclaw/workspace/ops/reports/daily_${TS}.md"
{
  echo "# Daily Ops Report (${TS} UTC)"
  echo
  echo "## Disk"
  df -h
  echo
  echo "## Recent cleanup logs"
  ls -1t /home/claw/.openclaw/workspace/ops/logs/safe_cleanup_*.log 2>/dev/null | head -n 5
  echo
  echo "## Top growth areas (/home/claw top 20)"
  (du -x -h /home/claw 2>/dev/null | sort -h | tail -n 20) || true
} > "$OUT"
echo "$OUT"