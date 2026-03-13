#!/usr/bin/env bash
set -euo pipefail

BEGIN="# CLAW_ALWAYS_ON_START"
END="# CLAW_ALWAYS_ON_END"

TMP=$(mktemp)
crontab -l 2>/dev/null > "$TMP" || true

# remove existing block
awk -v b="$BEGIN" -v e="$END" '
  $0==b{skip=1; next}
  $0==e{skip=0; next}
  !skip{print}
' "$TMP" > "$TMP.cleaned"

cat >> "$TMP.cleaned" <<'CRON'
# CLAW_ALWAYS_ON_START
*/30 * * * * /usr/bin/flock -n /tmp/claw_always_on_all.lock /home/claw/.openclaw/workspace/scripts/always_on_runner.sh all >> /home/claw/.openclaw/workspace/reports/always_on/cron.log 2>&1
15 * * * * /usr/bin/flock -n /tmp/claw_always_on_report.lock /home/claw/.openclaw/workspace/scripts/always_on_runner.sh reporting >> /home/claw/.openclaw/workspace/reports/always_on/cron.log 2>&1
# CLAW_ALWAYS_ON_END
CRON

crontab "$TMP.cleaned"
rm -f "$TMP" "$TMP.cleaned"
echo "Installed ALWAYS_ON cron block"
