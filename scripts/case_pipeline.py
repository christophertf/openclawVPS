#!/usr/bin/env python3
import csv
import hashlib
import json
import os
import re
import shutil
from datetime import datetime, UTC
from zoneinfo import ZoneInfo
from pathlib import Path

SRC = Path('/home/claw/CASE_FILES')
MASTER = Path('/home/claw/CASE_MASTER')
OUT = Path('/home/claw/.openclaw/workspace/reports/case_pipeline')
TRASH = Path('/home/claw/.trash/case_dedupe')
OUT.mkdir(parents=True, exist_ok=True)
TRASH.mkdir(parents=True, exist_ok=True)

LOCAL_TZ = ZoneInfo('America/Los_Angeles')
TS_UTC = datetime.now(UTC)
TS = TS_UTC.strftime('%Y-%m-%dT%H:%M:%SZ')
TS_LOCAL = TS_UTC.astimezone(LOCAL_TZ).strftime('%Y-%m-%d %H:%M %Z')
RUN_TAG = TS_UTC.strftime('%Y%m%dT%H%M%SZ')

CACHE_FILE = OUT / 'hash_cache.json'
STATE_FILE = OUT / 'state.json'
PROGRESS_FILE = OUT / 'CASE_PROGRESS.md'
APPROVALS_FILE = OUT / 'near_approvals.json'
NEAR_CANDIDATES_FILE = OUT / 'near_candidates.json'
FOCUS_FILE = OUT / 'CURRENT_FOCUS.md'
STEP2_LOG_FILE = OUT / 'STEP2-ORGANIZE-ITERATIVE-LOG.md'


def sha256_file(p: Path, chunk=1024 * 1024):
    h = hashlib.sha256()
    with p.open('rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def move_to_trash(abs_path: Path, reason: str):
    rel = abs_path.relative_to(SRC)
    dst = TRASH / reason / RUN_TAG / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(abs_path), str(dst))
    return str(dst)


def scan_and_hash():
    if MASTER.exists():
        shutil.rmtree(MASTER)
    MASTER.mkdir(parents=True, exist_ok=True)
    os.system(f"cp -al '{SRC}/.' '{MASTER}/'")

    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text())
        except Exception:
            cache = {}
    else:
        cache = {}

    files = []
    changed = 0
    for p in MASTER.rglob('*'):
        if not p.is_file():
            continue
        st = p.stat()
        rel = str(p.relative_to(MASTER))
        mtime = int(st.st_mtime)
        size = st.st_size
        hit = cache.get(rel)
        if hit and hit.get('mtime') == mtime and hit.get('size') == size and hit.get('sha256'):
            digest = hit['sha256']
        else:
            digest = sha256_file(p)
            cache[rel] = {'mtime': mtime, 'size': size, 'sha256': digest}
            changed += 1
        files.append({'path': rel, 'size': size, 'mtime': mtime, 'ext': p.suffix.lower(), 'sha256': digest})

    live = {f['path'] for f in files}
    for k in list(cache.keys()):
        if k not in live:
            del cache[k]
    CACHE_FILE.write_text(json.dumps(cache))
    return files, changed


def canonical_choice(group):
    return sorted(group, key=lambda x: (len(x['path']), -x['mtime']))[0]


def apply_near_approvals(state):
    applied = 0
    if not APPROVALS_FILE.exists():
        return applied
    try:
        data = json.loads(APPROVALS_FILE.read_text())
    except Exception:
        return applied

    items = data.get('items', [])
    for it in items:
        status = it.get('status', 'pending')
        a = it.get('a')
        b = it.get('b')
        if status not in ('keep_a', 'keep_b'):
            continue

        target = b if status == 'keep_a' else a
        target_abs = SRC / target
        if target_abs.exists() and target_abs.is_file():
            move_to_trash(target_abs, 'near_approved')
            it['status'] = 'applied'
            it['appliedAt'] = TS
            applied += 1
            state['moved_near_total'] = int(state.get('moved_near_total', 0)) + 1

    APPROVALS_FILE.write_text(json.dumps(data, indent=2))
    return applied


def norm_name(n):
    n = n.lower()
    n = re.sub(r'\(\d+\)', '', n)
    n = re.sub(r'[_\-\s]+', ' ', n)
    n = re.sub(r'\b(copy|final|v\d+|rev\d+|redacted)\b', '', n)
    return re.sub(r'\s+', ' ', n).strip()


def sample_similarity(pa: Path, pb: Path):
    sa, sb = pa.stat().st_size, pb.stat().st_size
    if sa == 0 or sb == 0:
        return 0.0
    spots_a = [0, max(0, sa // 2 - 32768), max(0, sa - 65536)]
    spots_b = [0, max(0, sb // 2 - 32768), max(0, sb - 65536)]
    total = 0
    match = 0
    with pa.open('rb') as fa, pb.open('rb') as fb:
        for oa, ob in zip(spots_a, spots_b):
            fa.seek(oa); fb.seek(ob)
            ba = fa.read(65536)
            bb = fb.read(65536)
            l = min(len(ba), len(bb))
            if l == 0:
                continue
            total += l
            match += sum(1 for i in range(l) if ba[i] == bb[i])
    return (match / total) if total else 0.0


def build_near_candidates(files, limit=2000):
    by_stem = {}
    for f in files:
        stem = norm_name(Path(f['path']).stem)
        by_stem.setdefault((stem, f['ext']), []).append(f)

    pairs = []
    for (_, _), group in by_stem.items():
        if len(group) < 2:
            continue
        group = sorted(group, key=lambda x: x['size'])
        for i in range(len(group) - 1):
            a, b = group[i], group[i + 1]
            if a['size'] == 0:
                continue
            ratio = abs(b['size'] - a['size']) / a['size']
            if ratio <= 0.02 and a['sha256'] != b['sha256']:
                pairs.append({
                    'id': hashlib.sha1(f"{a['path']}|{b['path']}".encode()).hexdigest()[:12],
                    'a': a['path'],
                    'b': b['path'],
                    'size_a': a['size'],
                    'size_b': b['size'],
                    'delta_ratio': round(ratio, 6),
                    'status': 'pending'
                })

    pairs = sorted(pairs, key=lambda x: x['delta_ratio'])[:limit]
    return pairs


# state
if STATE_FILE.exists():
    try:
        state = json.loads(STATE_FILE.read_text())
    except Exception:
        state = {}
else:
    state = {}

# 0) apply approved near actions first
approved_applied = apply_near_approvals(state)

prev_status = state.get('lastStatus', {}) if isinstance(state, dict) else {}
prev_total_files = int(prev_status.get('total_files_current', 0) or 0)
prev_exact_total = int(state.get('moved_exact_total', 0) or 0)
prev_near_total = int(state.get('moved_near_total', 0) or 0)

# 1) scan
files, changed_hashed = scan_and_hash()
initial_file_count = len(files)
initial_total_bytes = sum(f['size'] for f in files)

if 'baseline_total_files' not in state:
    state['baseline_total_files'] = initial_file_count
if 'moved_exact_total' not in state:
    state['moved_exact_total'] = 0
if 'moved_near_total' not in state:
    state['moved_near_total'] = 0

# 2) exact duplicate auto-clean (move extras to trash)
by_hash = {}
for f in files:
    by_hash.setdefault(f['sha256'], []).append(f)

moved_exact_this_run = 0
for group in by_hash.values():
    if len(group) < 2:
        continue
    keep = canonical_choice(group)
    for item in group:
        if item['path'] == keep['path']:
            continue
        src_abs = SRC / item['path']
        if src_abs.exists() and src_abs.is_file():
            move_to_trash(src_abs, 'exact_auto')
            moved_exact_this_run += 1

state['moved_exact_total'] = int(state.get('moved_exact_total', 0)) + moved_exact_this_run

# 3) rescan after moves
files, changed_hashed_after = scan_and_hash()

# 4) recalc maps
by_hash = {}
for f in files:
    by_hash.setdefault(f['sha256'], []).append(f)
exact_groups = [g for g in by_hash.values() if len(g) > 1]

frag_re = re.compile(r'(part\s*\d+|p\d+\b|chunk\s*\d+|split|segment)', re.I)
fragments = [f for f in files if frag_re.search(Path(f['path']).name)]

near_candidates = build_near_candidates(files)

# auto-resolve ultra-close near-duplicates conservatively
moved_near_auto_this_run = 0
removed_paths = set()
for cand in near_candidates:
    if cand['delta_ratio'] > 0.02:  # <=2.0% size delta only (aggressive pass)
        continue
    a_rel, b_rel = cand['a'], cand['b']
    if a_rel in removed_paths or b_rel in removed_paths:
        continue
    pa = SRC / a_rel
    pb = SRC / b_rel
    if not (pa.exists() and pb.exists()):
        continue
    try:
        sim = sample_similarity(pa, pb)
    except Exception:
        continue
    if sim >= 0.98:
        # keep shorter path/name, move the other
        keep, drop = (a_rel, b_rel) if len(a_rel) <= len(b_rel) else (b_rel, a_rel)
        drop_abs = SRC / drop
        if drop_abs.exists() and drop_abs.is_file():
            move_to_trash(drop_abs, 'near_auto')
            removed_paths.add(drop)
            cand['status'] = 'applied_auto_keep_a' if keep == a_rel else 'applied_auto_keep_b'
            cand['auto_similarity'] = round(sim, 5)
            moved_near_auto_this_run += 1

if moved_near_auto_this_run:
    state['moved_near_total'] = int(state.get('moved_near_total', 0)) + moved_near_auto_this_run
    files, changed_hashed_after = scan_and_hash()
    near_candidates = build_near_candidates(files)

# merge statuses from existing approvals
existing = {}
if APPROVALS_FILE.exists():
    try:
        for it in json.loads(APPROVALS_FILE.read_text()).get('items', []):
            existing[it.get('id')] = it
    except Exception:
        pass
for it in near_candidates:
    if it['id'] in existing and it.get('status') == 'pending':
        it['status'] = existing[it['id']].get('status', 'pending')

APPROVALS_FILE.write_text(json.dumps({'updatedAt': TS, 'items': near_candidates}, indent=2))
NEAR_CANDIDATES_FILE.write_text(json.dumps({'updatedAt': TS, 'count': len(near_candidates), 'items': near_candidates}, indent=2))

# 5) outputs
inv_csv = OUT / 'inventory.csv'
with inv_csv.open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['path', 'size', 'mtime', 'ext', 'sha256'])
    w.writeheader(); w.writerows(files)

ex_csv = OUT / 'exact_duplicates.csv'
with ex_csv.open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['sha256', 'count'])
    for g in sorted(exact_groups, key=lambda x: len(x), reverse=True):
        w.writerow([g[0]['sha256'], len(g)])

frag_txt = OUT / 'fragment_candidates.txt'
frag_txt.write_text('\n'.join(sorted(f['path'] for f in fragments)))

remaining_files = len(files)
processed = max(0, int(state['baseline_total_files']) - remaining_files)
progress_pct = 0.0 if state['baseline_total_files'] == 0 else round((processed / state['baseline_total_files']) * 100, 2)

status = {
    'timestamp_utc': TS,
    'source': str(SRC),
    'master': str(MASTER),
    'baseline_total_files': int(state['baseline_total_files']),
    'total_files_current': remaining_files,
    'total_bytes_current': sum(f['size'] for f in files),
    'changed_hashed_this_run': changed_hashed_after,
    'moved_exact_this_run': moved_exact_this_run,
    'moved_exact_total': int(state['moved_exact_total']),
    'approved_near_applied_this_run': approved_applied,
    'auto_near_moved_this_run': moved_near_auto_this_run,
    'moved_near_total': int(state['moved_near_total']),
    'exact_duplicate_groups_remaining': len(exact_groups),
    'exact_duplicate_files_remaining': sum(len(g) - 1 for g in exact_groups),
    'near_candidates_pending': sum(1 for x in near_candidates if x.get('status') == 'pending'),
    'fragment_candidates': len(fragments),
    'progress_files_removed': processed,
    'progress_percent': progress_pct,
    'outputs': {
        'inventory': str(inv_csv),
        'exact_duplicates': str(ex_csv),
        'fragment_candidates': str(frag_txt),
        'near_approvals': str(APPROVALS_FILE),
        'near_candidates': str(NEAR_CANDIDATES_FILE)
    }
}
(OUT / 'status.json').write_text(json.dumps(status, indent=2))

state['lastRunAt'] = TS
state['lastStatus'] = status
STATE_FILE.write_text(json.dumps(state, indent=2))

# actions / questions / progress
actions = OUT / 'CASE_ACTIONS.md'
questions = OUT / 'CASE_QUESTIONS.md'
actions.write_text(
    f"# CASE_ACTIONS\n\nLast run: {TS}\n\n"
    f"- Applied approved near actions this run: {approved_applied}.\n"
    f"- Auto-moved ultra-close near duplicates this run: {moved_near_auto_this_run}.\n"
    f"- Auto-moved exact duplicates this run: {moved_exact_this_run}.\n"
    f"- Remaining exact duplicate extras: {status['exact_duplicate_files_remaining']}.\n"
    f"- Pending near-candidate approvals: {status['near_candidates_pending']}.\n"
)

questions.write_text(
    f"# CASE_QUESTIONS\n\nLast run: {TS}\n\n"
    "Open questions captured without stopping processing:\n\n"
    "1. For pending near candidates, choose status in `near_approvals.json`: keep_a / keep_b / skip.\n"
    "2. Confirm if any subfolders should be protected from auto-cleaning.\n"
)

if not PROGRESS_FILE.exists():
    PROGRESS_FILE.write_text('# CASE_PROGRESS\n\n')
with PROGRESS_FILE.open('a') as f:
    f.write(
        f"## {TS}\n"
        f"- files now: {remaining_files} (baseline: {state['baseline_total_files']})\n"
        f"- moved exact this run: {moved_exact_this_run}; total exact moved: {state['moved_exact_total']}\n"
        f"- near approvals applied this run: {approved_applied}; auto-near moved this run: {moved_near_auto_this_run}; total near moved: {state['moved_near_total']}\n"
        f"- exact duplicate extras remaining: {status['exact_duplicate_files_remaining']}\n"
        f"- pending near approvals: {status['near_candidates_pending']}\n"
        f"- progress: {progress_pct}%\n\n"
    )

if not STEP2_LOG_FILE.exists():
    STEP2_LOG_FILE.write_text('# STEP2 ORGANIZE ITERATIVE LOG\n\n')

file_delta = (remaining_files - prev_total_files) if prev_total_files else 0
exact_total_delta = int(state['moved_exact_total']) - prev_exact_total
near_total_delta = int(state['moved_near_total']) - prev_near_total

with STEP2_LOG_FILE.open('a') as f:
    f.write(
        f"## {TS}\n"
        f"- pass_mode: aggressive\n"
        f"- files_before: {prev_total_files if prev_total_files else 'n/a'}\n"
        f"- files_after: {remaining_files}\n"
        f"- file_count_delta_this_run: {file_delta if prev_total_files else 'n/a (first tracked run)'}\n"
        f"- moved_exact_this_run: {moved_exact_this_run}\n"
        f"- moved_exact_total_delta: {exact_total_delta}\n"
        f"- moved_near_this_run: {approved_applied + moved_near_auto_this_run}\n"
        f"- moved_near_total_delta: {near_total_delta}\n"
        f"- exact_duplicate_files_remaining: {status['exact_duplicate_files_remaining']}\n"
        f"- pending_near_candidates: {status['near_candidates_pending']}\n\n"
    )

# maintain explicit current-focus note for dashboard transparency
focus_text = (
    "# CURRENT_FOCUS\n\n"
    f"Updated: {TS_LOCAL} ({TS})\n\n"
    "- Keep CASE_FILES as source-of-truth intake\n"
    "- Auto-remove exact duplicates (recoverable trash)\n"
    "- Queue near-duplicates for your approval decisions\n"
    "- Preserve traceability via status/progress/action logs\n"
)
FOCUS_FILE.write_text(focus_text)

# visual dashboard (minimal text)
pending = status['near_candidates_pending']
remaining_exact = status['exact_duplicate_files_remaining']
bar = int(progress_pct)
html = f"""<!doctype html>
<html><head><meta charset='utf-8'><title>Case Momentum Dashboard</title>
<style>
body{{font-family:Inter,Arial,sans-serif;background:#0b1020;color:#e8eefc;margin:24px}}
.grid{{display:grid;grid-template-columns:repeat(4,minmax(180px,1fr));gap:12px}}
.card{{background:#111a33;border:1px solid #26345f;border-radius:12px;padding:14px}}
.big{{font-size:28px;font-weight:700}}
.label{{color:#9cb0de;font-size:12px;text-transform:uppercase;letter-spacing:.08em}}
.meter{{height:20px;background:#1a2547;border-radius:999px;overflow:hidden;border:1px solid #2c3f76}}
.fill{{height:100%;width:{bar}%;background:linear-gradient(90deg,#22c55e,#84cc16)}}
small{{color:#9cb0de}}
</style></head><body>
<h1>Case Momentum Dashboard</h1>
<small>Last run: {TS_LOCAL} (UTC: {TS})</small>
<div class='grid'>
  <div class='card'><div class='label'>Current Files</div><div class='big'>{remaining_files}</div></div>
  <div class='card'><div class='label'>Exact Dups Removed (Total)</div><div class='big'>{state['moved_exact_total']}</div></div>
  <div class='card'><div class='label'>Near Decisions Applied</div><div class='big'>{state['moved_near_total']}</div></div>
  <div class='card'><div class='label'>Pending Near Approvals</div><div class='big'>{pending}</div></div>
</div>
<h2>Overall Progress (file-count reduction from baseline)</h2>
<div class='meter'><div class='fill'></div></div>
<p><b>{progress_pct}%</b> complete &nbsp; • &nbsp; baseline {state['baseline_total_files']} → now {remaining_files}</p>
<h2>Quality Queue</h2>
<div class='grid'>
  <div class='card'><div class='label'>Exact Duplicates Remaining</div><div class='big'>{remaining_exact}</div></div>
  <div class='card'><div class='label'>Fragment Candidates</div><div class='big'>{status['fragment_candidates']}</div></div>
  <div class='card'><div class='label'>Changed Files Hashed (This Run)</div><div class='big'>{status['changed_hashed_this_run']}</div></div>
  <div class='card'><div class='label'>Near Candidates Pending</div><div class='big'>{pending}</div></div>
</div>
<h2>Current Focus</h2>
<pre style='background:#111a33;border:1px solid #26345f;border-radius:10px;padding:12px;color:#cfe0ff'>{focus_text}</pre>
<p><small>Approvals file: {APPROVALS_FILE}</small></p>
</body></html>"""
(OUT / 'dashboard.html').write_text(html)

print(json.dumps(status))
