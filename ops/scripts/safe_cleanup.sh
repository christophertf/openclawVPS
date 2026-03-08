#!/usr/bin/env bash
set -euo pipefail
TS=$(date -u +%Y%m%dT%H%M%SZ)
LOG="/home/claw/.openclaw/workspace/ops/logs/safe_cleanup_${TS}.log"
exec > >(tee -a "$LOG") 2>&1

echo "[start] $TS"

# 1) Python cache noise
find /home/claw -type d -name '__pycache__' -prune -print -exec rm -rf {} + 2>/dev/null || true
find /home/claw -type f -name '*.pyc' -print -delete 2>/dev/null || true

# 2) Common temp/bak noise in user space
find /home/claw -type f \( -name '*.tmp' -o -name '*.bak' -o -name '*~' \) -mtime +3 -print -delete 2>/dev/null || true

# 3) Pip/NPM cache cleanup (safe)
pip cache purge 2>/dev/null || true
npm cache verify 2>/dev/null || true

# 4) Trim oversized local log files >100MB by keeping last 20k lines
while IFS= read -r f; do
  echo "[trim] $f"
  tail -n 20000 "$f" > "${f}.trim" && mv "${f}.trim" "$f"
done < <(find /home/claw -type f -name '*.log' -size +100M 2>/dev/null)

# 5) Snapshot disk after cleanup

df -h

echo "[done] $(date -u +%Y%m%dT%H%M%SZ)"
