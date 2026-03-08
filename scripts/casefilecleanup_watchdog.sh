#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_BIN="/home/claw/.npm-global/bin/openclaw"
CHANNEL_ID="1476517943952019517"
SESSION_KEY="agent:main:discord:channel:1476517943952019517"
CASE_ROOT="/home/claw/CASE_FILES"
STATE_DIR="/home/claw/.openclaw/workspace/state"
STATE_FILE="$STATE_DIR/casefilecleanup_watchdog.json"
RUN_LOG="/home/claw/.openclaw/workspace/state/casefilecleanup_watchdog.log"
STALL_MINUTES=20
MAX_RESTARTS=10

mkdir -p "$STATE_DIR"

now_epoch=$(date -u +%s)
now_iso=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

restarts=0
last_kick=0
if [[ -f "$STATE_FILE" ]]; then
  restarts=$(python3 - <<'PY'
import json
from pathlib import Path
p=Path('/home/claw/.openclaw/workspace/state/casefilecleanup_watchdog.json')
try:
  j=json.loads(p.read_text())
  print(int(j.get('restarts',0)))
except Exception:
  print(0)
PY
)
  last_kick=$(python3 - <<'PY'
import json
from pathlib import Path
p=Path('/home/claw/.openclaw/workspace/state/casefilecleanup_watchdog.json')
try:
  j=json.loads(p.read_text())
  print(int(j.get('lastKickEpoch',0)))
except Exception:
  print(0)
PY
)
fi

if [[ ! -d "$CASE_ROOT" ]]; then
  printf "%s watchdog: case root missing, no action\n" "$now_iso" >> "$RUN_LOG"
  exit 0
fi

latest_mtime=$(find "$CASE_ROOT" -type f -printf '%T@\n' 2>/dev/null | sort -nr | head -n1)
if [[ -z "${latest_mtime:-}" ]]; then
  printf "%s watchdog: no files under case root, no action\n" "$now_iso" >> "$RUN_LOG"
  exit 0
fi
mtime=${latest_mtime%.*}
age_min=$(( (now_epoch - mtime) / 60 ))

if (( age_min < STALL_MINUTES )); then
  printf "%s watchdog: healthy (age=%sm), no action\n" "$now_iso" "$age_min" >> "$RUN_LOG"
  exit 0
fi

if (( restarts >= MAX_RESTARTS )); then
  printf "%s watchdog: stalled (age=%sm) but max restarts reached (%s), no action\n" "$now_iso" "$age_min" "$MAX_RESTARTS" >> "$RUN_LOG"
  exit 0
fi

# Avoid kick storms: minimum 10 min between kicks
if (( now_epoch - last_kick < 600 )); then
  printf "%s watchdog: stalled (age=%sm) but last kick too recent, no action\n" "$now_iso" "$age_min" >> "$RUN_LOG"
  exit 0
fi

next=$((restarts + 1))
msg="Watchdog restart ${next}/${MAX_RESTARTS}: casefilecleanup appears stalled (no update in ${age_min} minutes). Resume Step 2 organization and append to STEP2-ORGANIZE-ITERATIVE-LOG.md. Continue building on prior runs."

$OPENCLAW_BIN cron add \
  --agent main \
  --session isolated \
  --at 1m \
  --announce \
  --channel discord \
  --to "$CHANNEL_ID" \
  --name "casefilecleanup-watchdog-restart-${next}" \
  --message "$msg" \
  --delete-after-run \
  --json >/tmp/casefilecleanup_watchdog_last.json

python3 - <<PY
import json, time
from pathlib import Path
p=Path('$STATE_FILE')
state={'restarts': $next, 'lastKickEpoch': int(time.time()), 'updatedAt': '$now_iso'}
p.write_text(json.dumps(state, indent=2))
PY

printf "%s watchdog: stalled (age=%sm), scheduled restart %s/%s\n" "$now_iso" "$age_min" "$next" "$MAX_RESTARTS" >> "$RUN_LOG"
