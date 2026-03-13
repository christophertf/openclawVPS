#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="/home/claw/.openclaw/workspace"
STATE_DIR="$WORKSPACE/state/always_on"
REPORT_DIR="$WORKSPACE/reports/always_on"
MEM_LOG="$WORKSPACE/memory/change-feed.log"
STATUS_JSON="$STATE_DIR/status.json"
RUN_LOG="$REPORT_DIR/runs.log"

mkdir -p "$STATE_DIR" "$REPORT_DIR"

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log(){ echo "[$(ts)] $*" | tee -a "$RUN_LOG" >/dev/null; }

init_state(){
  if [[ ! -f "$STATUS_JSON" ]]; then
    cat > "$STATUS_JSON" <<'JSON'
{
  "updatedAt": null,
  "phase": "phase-1",
  "state": "running",
  "modelRouting": {
    "default": "openai-codex/gpt-5.3-codex",
    "legal": "grok-legal",
    "cheap": "router-cheap",
    "verify": "router-verify"
  },
  "loops": {
    "ingest": "pending",
    "research": "pending",
    "validation": "pending",
    "reporting": "pending"
  },
  "metrics": {
    "ticks": 0,
    "errors": 0,
    "lastIngestFiles": 0,
    "lastPipelineStatusAgeHours": null
  },
  "blockers": []
}
JSON
  fi
}

update_json(){
  python3 - "$STATUS_JSON" "$1" "$2" <<'PY'
import json,sys,datetime
p,key,val = sys.argv[1],sys.argv[2],sys.argv[3]
with open(p) as f: s=json.load(f)
now=datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
s['updatedAt']=now
if key.startswith('loops.'):
    _,k=key.split('.',1)
    s.setdefault('loops',{})[k]=val
elif key.startswith('metrics.'):
    _,k=key.split('.',1)
    try:
        if val in ('null','None'): v=None
        elif '.' in val: v=float(val)
        else: v=int(val)
    except:
        v=val
    s.setdefault('metrics',{})[k]=v
else:
    s[key]=val
with open(p,'w') as f: json.dump(s,f,indent=2)
PY
}

inc_metric(){
  python3 - "$STATUS_JSON" "$1" <<'PY'
import json,sys,datetime
p,k=sys.argv[1],sys.argv[2]
with open(p) as f:s=json.load(f)
now=datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
s['updatedAt']=now
m=s.setdefault('metrics',{})
m[k]=int(m.get(k,0) or 0)+1
with open(p,'w') as f: json.dump(s,f,indent=2)
PY
}

loop_ingest(){
  log "ingest:start"
  local count
  count=$(find "$WORKSPACE/memory" -maxdepth 1 -type f -name '*.md' | wc -l | tr -d ' ')
  printf '%s\n' "$(ts) files_memory_md=$count" > "$STATE_DIR/ingest_snapshot.txt"
  
  # Real ingest stub: Capture current workspace git status
  git -C "$WORKSPACE" status --short > "$STATE_DIR/git_workspace_status.txt"
  
  update_json loops.ingest ok
  update_json metrics.lastIngestFiles "$count"
  log "ingest:ok files_memory_md=$count"
}

loop_research(){
  log "research:start"
  # lightweight: capture recent case docs existence and TODO counts
  local todos
  todos=$(grep -Rho "TODO\|FIXME\|OPEN QUESTION" "$WORKSPACE/reports" 2>/dev/null | wc -l | tr -d ' ' || true)
  printf '%s\n' "$(ts) report_markers=$todos" > "$STATE_DIR/research_snapshot.txt"
  update_json loops.research ok
  log "research:ok markers=$todos"
}

loop_validation(){
  log "validation:start"
  local p="$WORKSPACE/reports/case_pipeline/status.json"
  if [[ -f "$p" ]]; then
    local age_h
    age_h=$(python3 - <<'PY'
import os,time
p='/home/claw/.openclaw/workspace/reports/case_pipeline/status.json'
age=(time.time()-os.path.getmtime(p))/3600
print(f"{age:.1f}")
PY
)
    update_json metrics.lastPipelineStatusAgeHours "$age_h"
    log "validation:ok pipeline_status_age_h=$age_h"
  else
    update_json metrics.lastPipelineStatusAgeHours null
    log "validation:ok pipeline_status_optional_missing"
  fi
  update_json loops.validation ok
}

loop_reporting(){
  log "reporting:start"
  update_json loops.reporting ok
  python3 - <<'PY'
import json,datetime
s='/home/claw/.openclaw/workspace/state/always_on/status.json'
out='/home/claw/.openclaw/workspace/reports/always_on/LATEST.md'
with open(s) as f: d=json.load(f)
now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
lines=[
    '# ALWAYS-ON STATUS',
    f'- Updated: {now}',
    f"- Phase: {d.get('phase')}",
    f"- State: {d.get('state')}",
    f"- Loops: {d.get('loops')}",
    f"- Metrics: {d.get('metrics')}",
    f"- Blockers: {d.get('blockers')}",
]
open(out,'w').write('\n'.join(lines)+'\n')
PY
  log "reporting:ok"
}

main(){
  init_state
  inc_metric ticks
  case "${1:-all}" in
    ingest) loop_ingest ;;
    research) loop_research ;;
    validation) loop_validation ;;
    reporting) loop_reporting ;;
    all)
      loop_ingest
      loop_research
      loop_validation
      loop_reporting
      ;;
    *)
      echo "Usage: $0 {all|ingest|research|validation|reporting}" >&2
      exit 1
      ;;
  esac
}

main "$@"
