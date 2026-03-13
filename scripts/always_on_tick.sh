#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="/home/claw/.openclaw/workspace"
STATE="$WORKSPACE/state/always_on/status.json"
REPORT_DIR="$WORKSPACE/reports/always_on"
mkdir -p "$REPORT_DIR"

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "[$TS] tick: always_on phase-1 heartbeat" >> "$REPORT_DIR/runs.log"

python3 - <<'PY'
import json,datetime
p='/home/claw/.openclaw/workspace/state/always_on/status.json'
with open(p) as f:
    s=json.load(f)
s['updatedAt']=datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z'
s['state']='running'
for k in s.get('loops',{}):
    if s['loops'][k]=='pending':
        s['loops'][k]='initialized'
with open(p,'w') as f:
    json.dump(s,f,indent=2)
PY

echo "[$TS] tick: status updated" >> "$REPORT_DIR/runs.log"
