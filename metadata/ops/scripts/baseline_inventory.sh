#!/usr/bin/env bash
set -euo pipefail
TS=$(date -u +%Y%m%dT%H%M%SZ)
OUT="/home/claw/.openclaw/workspace/ops/reports/baseline_${TS}.md"
{
  echo "# Baseline Inventory (${TS})"
  echo
  echo "## Disk"
  df -h
  echo
  echo "## Largest dirs under /home/claw (top 30)"
  (du -x -h /home/claw 2>/dev/null | sort -h | tail -n 30) || true
  echo
  echo "## Largest files under /home/claw (top 30)"
  (find /home/claw -xdev -type f -printf '%s %p\n' 2>/dev/null | sort -nr | head -n 30 | awk '{printf "%.2f MB %s\n", $1/1024/1024, $2}') || true
} > "$OUT"
echo "$OUT"