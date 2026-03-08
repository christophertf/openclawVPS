#!/usr/bin/env python3
import argparse
import json
import os
import re
from pathlib import Path
from collections import Counter

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from openai import OpenAI

AGENDA_RE = re.compile(r"^\s*##\s*Item\s*(\d+)\s*[—-]\s*(.+?)\s*$", re.M)


def parse_agenda(agenda_text: str, cases_only=False):
    items = []
    for m in AGENDA_RE.finditer(agenda_text):
        items.append({"item_number": int(m.group(1)), "title": m.group(2).strip()})
    if not items:
        # fallback: numbered lines
        for line in agenda_text.splitlines():
            m = re.match(r"^\s*(\d{1,2})\s*[\).:-]\s*(.+)$", line)
            if m:
                items.append({"item_number": int(m.group(1)), "title": m.group(2).strip()})
    items = sorted({x["item_number"]: x for x in items}.values(), key=lambda x: x["item_number"])
    if cases_only:
        keep=[]
        for it in items:
            t=it['title'].lower()
            if ('approval of minutes' in t) or ('approval minutes' in t):
                continue
            keep.append(it)
        items=keep
    return items


def chunk_transcript(text: str, max_chars=700):
    raw_blocks = [b.strip() for b in re.split(r"\n{2,}", text) if b.strip()]
    chunks = []
    cid = 1
    for blk in raw_blocks:
        if len(blk) <= max_chars:
            chunks.append({"id": cid, "text": blk})
            cid += 1
            continue
        # split long blocks by sentence-ish boundaries
        parts = re.split(r"(?<=[.!?])\s+", blk)
        cur = ""
        for p in parts:
            if not cur:
                cur = p
            elif len(cur) + 1 + len(p) <= max_chars:
                cur += " " + p
            else:
                chunks.append({"id": cid, "text": cur.strip()})
                cid += 1
                cur = p
        if cur.strip():
            chunks.append({"id": cid, "text": cur.strip()})
            cid += 1
    return chunks


def build_prompt(agenda_items, chunks, previous_errors=None, notes_text=""):
    agenda_json = json.dumps(agenda_items, ensure_ascii=False)
    chunks_json = json.dumps(chunks, ensure_ascii=False)
    err = ""
    if previous_errors:
        err = "\nPrevious validation errors to fix:\n- " + "\n- ".join(previous_errors)
    return f"""
You are aligning a hearing transcript to agenda items.
Use agenda as authoritative structure.
Assign EVERY transcript chunk exactly once to exactly one agenda item.
Do not omit chunks. Do not duplicate chunk assignment.
Keep item order by agenda item_number.
If a chunk is procedural/preamble/roll-call/transition and not clearly tied to a specific item, assign it to the nearest plausible agenda item (usually Item 1 for opening admin or the currently active item). No chunk may remain unassigned.

Historical alignment notes (learned rules):
{notes_text or '(none)'}

Return ONLY JSON object:
{{
  "items": [
    {{
      "item_number": <int>,
      "title": "<string>",
      "chunk_ids": [<int>, ...],
      "confidence": <0..1>,
      "notes": "<short reason>"
    }}
  ],
  "global_notes": "<short summary>"
}}

Agenda items:
{agenda_json}

Transcript chunks (id + verbatim text):
{chunks_json}
{err}
""".strip()


def call_llm(client, model, prompt):
    r = client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a precise transcript alignment engine."},
            {"role": "user", "content": prompt},
        ],
    )
    return json.loads(r.choices[0].message.content)


def repair_mapping(mapping, agenda_items, chunks):
    """Force total chunk coverage + uniqueness deterministically.
    - Drops duplicate chunk assignments from later items
    - Appends unassigned chunks to nearest prior item by chunk order
    """
    items = mapping.get("items") or []
    by_num = {it.get("item_number"): it for it in items}
    ordered_nums = [x["item_number"] for x in agenda_items]
    for n in ordered_nums:
        by_num.setdefault(n, {"item_number": n, "title": next((a['title'] for a in agenda_items if a['item_number']==n), f"Item {n}"), "chunk_ids": [], "confidence": 0.7, "notes": "auto-created"})

    seen=set()
    # de-dup while preserving first assignment by item order
    for n in ordered_nums:
        it=by_num[n]
        cids=[]
        for c in it.get("chunk_ids") or []:
            if c in seen:
                continue
            seen.add(c)
            cids.append(c)
        it["chunk_ids"]=cids

    allowed=[c["id"] for c in chunks]
    missing=[c for c in allowed if c not in seen]

    # choose item boundaries from assigned chunk ranges
    ranges=[]
    for n in ordered_nums:
        cids=by_num[n].get("chunk_ids") or []
        if cids:
            ranges.append((n,min(cids),max(cids)))

    def nearest_item(cid):
        if not ranges:
            return ordered_nums[0]
        prev=[r for r in ranges if r[1] <= cid]
        if prev:
            prev.sort(key=lambda x:x[1])
            return prev[-1][0]
        return ordered_nums[0]

    for cid in missing:
        n=nearest_item(cid)
        by_num[n].setdefault("chunk_ids",[]).append(cid)

    repaired_items=[by_num[n] for n in ordered_nums]
    for it in repaired_items:
        it["chunk_ids"]=sorted(it.get("chunk_ids") or [])
        if not isinstance(it.get("confidence"), (int,float)):
            it["confidence"]=0.7
    mapping["items"]=repaired_items
    return mapping


def validate(mapping, agenda_items, chunks, min_conf=0.0):
    errors = []
    items = mapping.get("items") or []
    agenda_nums = [x["item_number"] for x in agenda_items]
    got_nums = [x.get("item_number") for x in items]

    if sorted(got_nums) != sorted(agenda_nums):
        errors.append(f"agenda item mismatch: expected {agenda_nums}, got {got_nums}")

    allowed = {c["id"] for c in chunks}
    assigned = []
    for it in items:
        cids = it.get("chunk_ids") or []
        if not isinstance(cids, list):
            errors.append(f"item {it.get('item_number')} chunk_ids is not a list")
            continue
        for c in cids:
            if c not in allowed:
                errors.append(f"item {it.get('item_number')} references unknown chunk id {c}")
            assigned.append(c)
        conf = it.get("confidence", 0)
        try:
            conf = float(conf)
        except Exception:
            conf = 0
        if conf < min_conf:
            errors.append(f"item {it.get('item_number')} low confidence {conf:.2f}")

    cnt = Counter(assigned)
    dup = [k for k, v in cnt.items() if v > 1]
    if dup:
        errors.append(f"duplicate chunk assignment: {dup[:20]}")

    missing = sorted(allowed - set(assigned))
    if missing:
        errors.append(f"unassigned chunks: {missing[:30]}{'...' if len(missing) > 30 else ''}")

    return errors


def _num_word(n:int)->str:
    words={1:'one',2:'two',3:'three',4:'four',5:'five',6:'six',7:'seven',8:'eight',9:'nine',10:'ten',11:'eleven',12:'twelve',13:'thirteen',14:'fourteen',15:'fifteen'}
    return words.get(n,str(n))


def _trim_to_item_marker(text:str, item_number:int)->str:
    # hard trim to first explicit item marker for this item
    w=_num_word(item_number)
    pats=[
        rf"\bitem\s+number\s+{item_number}\b",
        rf"\bitem\s+number\s+{w}\b",
        rf"\bagenda\s+item\s+number\s+{item_number}\b",
        rf"\bagenda\s+item\s+number\s+{w}\b",
        rf"\bagenda\s+item\s+{item_number}\b",
        rf"\bitem\s+{item_number}\b",
    ]
    idx=None
    low=text.lower()
    for p in pats:
        m=re.search(p, low, re.I)
        if m:
            idx=m.start()
            break
    if idx is not None and idx>0:
        return text[idx:].lstrip()
    return text


def render_markdown(base, agenda_items, mapping, chunk_map):
    by_num = {it["item_number"]: it for it in (mapping.get("items") or [])}
    out = [f"# Hearing Items — {base}", ""]
    for ag in agenda_items:
        n = ag["item_number"]
        t = ag["title"]
        it = by_num.get(n, {"chunk_ids": [], "confidence": 0, "notes": "missing mapping"})
        cids = it.get("chunk_ids") or []
        text = "\n\n".join(chunk_map[c] for c in cids if c in chunk_map).strip()
        text = _trim_to_item_marker(text, n)
        if not text:
            text = "(no transcript assigned)"
        out.append(f"## Item {n} — {t}")
        out.append(f"**Alignment confidence:** {float(it.get('confidence', 0)):.2f}")
        out.append("")
        out.append("### Transcript (verbatim chunks)")
        out.append("```")
        out.append(text)
        out.append("```")
        if it.get("notes"):
            out.append("")
            out.append(f"_Notes: {it['notes']}_")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="LLM-first transcript-to-agenda alignment with validation loop")
    ap.add_argument("--meeting-dir", required=True, help="Path to one meeting directory")
    ap.add_argument("--transcript", default="", help="Transcript filename (defaults to *_transcript.txt then *.txt then *_raw.txt)")
    ap.add_argument("--agenda", default="agenda.txt", help="Agenda filename")
    ap.add_argument("--model", default="gpt-4o-mini")
    ap.add_argument("--cases-only", action="store_true", help="Drop non-case agenda items like approval of minutes")
    ap.add_argument("--notes-file", default="scripts/alignment_notes.md", help="Persistent notes file for iterative improvements")
    ap.add_argument("--max-iter", type=int, default=8)
    ap.add_argument("--min-confidence", type=float, default=0.0)
    args = ap.parse_args()

    mdir = Path(args.meeting_dir).resolve()
    if not mdir.exists():
        raise SystemExit(f"meeting dir not found: {mdir}")

    agenda_path = mdir / args.agenda
    if not agenda_path.exists():
        raise SystemExit(f"agenda not found: {agenda_path}")

    if args.transcript:
        transcript_path = mdir / args.transcript
    else:
        cands = sorted(mdir.glob("*_transcript.txt"))
        if not cands:
            cands = [p for p in sorted(mdir.glob("*.txt")) if p.name != "agenda.txt" and not p.name.endswith("_raw.txt")]
        if not cands:
            cands = sorted(mdir.glob("*_raw.txt"))
        if not cands:
            raise SystemExit("no transcript txt found")
        transcript_path = cands[0]

    agenda_text = agenda_path.read_text(encoding="utf-8", errors="ignore")
    transcript_text = transcript_path.read_text(encoding="utf-8", errors="ignore")

    agenda_items = parse_agenda(agenda_text, cases_only=args.cases_only)
    if not agenda_items:
        raise SystemExit("failed to parse agenda items")

    chunks = chunk_transcript(transcript_text)
    chunk_map = {c["id"]: c["text"] for c in chunks}

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set")

    client = OpenAI()
    prev_errors = []
    final_mapping = None
    notes_path = Path(args.notes_file)
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    notes_text = notes_path.read_text(encoding='utf-8', errors='ignore') if notes_path.exists() else ''

    for i in range(1, args.max_iter + 1):
        print(f"[iter {i}] aligning {mdir.name} ({len(agenda_items)} items, {len(chunks)} chunks)")
        prompt = build_prompt(agenda_items, chunks, prev_errors, notes_text=notes_text)
        mapping = call_llm(client, args.model, prompt)
        mapping = repair_mapping(mapping, agenda_items, chunks)
        errs = validate(mapping, agenda_items, chunks, min_conf=args.min_confidence)
        if not errs:
            final_mapping = mapping
            print(f"[iter {i}] PASS")
            # write back learned notes
            gnotes = (mapping.get('global_notes') or '').strip()
            if gnotes:
                with notes_path.open('a', encoding='utf-8') as nf:
                    nf.write(f"\n## {mdir.name} PASS\n- {gnotes}\n")
            break
        prev_errors = errs
        print(f"[iter {i}] FAIL: {len(errs)} issue(s)")
        for e in errs[:8]:
            print(" -", e)
        with notes_path.open('a', encoding='utf-8') as nf:
            nf.write(f"\n## {mdir.name} iter {i} FAIL\n")
            for e in errs[:12]:
                nf.write(f"- {e}\n")

    if final_mapping is None:
        raise SystemExit("Failed to reach pass criteria within max iterations")

    base = transcript_path.stem
    out_json = mdir / f"{base}_llm_aligned.json"
    out_md = mdir / f"{base}_llm_aligned.md"

    out_json.write_text(json.dumps(final_mapping, indent=2, ensure_ascii=False), encoding="utf-8")
    out_md.write_text(render_markdown(base, agenda_items, final_mapping, chunk_map), encoding="utf-8")
    print(f"[ok] wrote {out_json.name}")
    print(f"[ok] wrote {out_md.name}")


if __name__ == "__main__":
    main()
