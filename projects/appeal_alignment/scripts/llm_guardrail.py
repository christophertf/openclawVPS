#!/usr/bin/env python3
"""
llm_guardrail.py — Minutes-first fixer for *_items.md using OpenAI API

What it does
------------
- For each hearing folder, loads:
  - minutes PDF/TXT (prefers same dir; otherwise matches by date)
  - your outputs: <base>_items.md (preferred) OR <base>_raw.txt
- Calls an OpenAI model to:
  - Parse minutes to get the authoritative agenda (count, order, item #s/titles)
  - Fix/realign transcript per item, fill missing, keep verbatim text blocks
  - Output corrected Markdown as <base>_items.llm.md and a compact change report

Usage
-----
export OPENAI_API_KEY=sk-...
python scripts/llm_guardrail.py --scan ./2025 --model gpt-4o-mini
# or a bigger model:
python scripts/llm_guardrail.py --scan ./2025 --model gpt-4o
"""

import os, re, sys, argparse, subprocess, json
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
from typing import Optional, Tuple

# ---------- minutes IO (same as batch script) ----------
def have_pdftotext() -> bool:
    try:
        subprocess.run(["pdftotext", "-v"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def pdf_to_text_with_pdftotext(pdf_path: Path) -> str:
    tmp = pdf_path.with_suffix(".tmp.txt")
    subprocess.run(["pdftotext", "-layout", str(pdf_path), str(tmp)], check=True)
    txt = tmp.read_text(encoding="utf-8", errors="ignore")
    try: tmp.unlink()
    except Exception: pass
    return txt

def pdf_to_text_with_pypdf2(pdf_path: Path) -> str:
    import PyPDF2
    out = []
    with open(pdf_path, "rb") as f:
        r = PyPDF2.PdfReader(f)
        for p in r.pages:
            out.append(p.extract_text() or "")
    return "\n".join(out)

def read_minutes_file(path: Path) -> Optional[str]:
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".pdf":
        if have_pdftotext():
            return pdf_to_text_with_pdftotext(path)
        try:
            return pdf_to_text_with_pypdf2(path)
        except Exception:
            return None
    return None

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
def extract_date_from_name(name: str) -> Optional[str]:
    m = DATE_RE.search(name)
    return m.group(1) if m else None

def find_minutes_for_base(base: str, folder: Path) -> Tuple[str, Optional[Path]]:
    # 1) prefer obvious "minutes" file in same folder
    cand = sorted([p for p in folder.glob("*") if p.suffix.lower() in [".pdf",".txt"] and "minutes" in p.stem.lower()])
    for p in cand:
        txt = read_minutes_file(p)
        if txt and len(txt.strip())>50: return txt, p
    # 2) try any pdf/txt in folder
    for p in sorted([p for p in folder.glob("*") if p.suffix.lower() in [".pdf",".txt"]]):
        txt = read_minutes_file(p)
        if txt and len(txt.strip())>50: return txt, p
    # 3) match by date in name
    d = extract_date_from_name(base)
    if d:
        p = next((x for x in folder.rglob(f"{d}*_minutes.txt")), None)
        if p: return p.read_text(encoding="utf-8", errors="ignore"), p
        p = next((x for x in folder.rglob(f"{d}*.pdf")), None)
        if p:
            txt = read_minutes_file(p)
            if txt: return txt, p
    return "", None

# ---------- OpenAI client ----------
def get_client():
    try:
        from openai import OpenAI
    except ImportError:
        sys.stderr.write("pip install openai\n")
        raise
    return OpenAI()

SYSTEM_PROMPT = """You are a careful clerk. You will:
1) Parse the minutes to build the authoritative agenda: item numbers in order, titles, case #s, addresses, and whether the item is consent/uncontested/contested.
2) Compare with provided transcript/markdown. Reassign any transcript text to the correct item using inline cues (e.g., 'Item 4', case #, address, owner/inspector) and DO NOT hallucinate text not present in transcript.
3) Produce a single corrected Markdown with:
   - H1: 'Hearing Items – <base>'
   - For each item, in strict numeric order, output:
     ## Item N — <best short title if minutes have one>
     **Minutes summary (for matchup only):** <one-line summary from minutes>
     ### Transcript (verbatim)
     ``` 
     <verbatim transcript chunk for this item; if none, leave block empty and write: (no transcript captured)>
     ```
     ### Fees, Fines & Verdicts
     - Keep any fee/fine/decision lines you can find in minutes (verbatim, no inventing).
4) If minutes include a large 'Uncontested' block as a single item (e.g., 'Item 15 – Uncontested Cost Recovery'), include it as one item with a brief summary, but do not fabricate transcript content.
5) Return JSON with fields:
   { "markdown": "...", "notes": "what you changed/fixed in one short paragraph" }"""

def extract_json_from_response(text: str) -> dict:
    """
    Extract JSON from LLM response, handling cases where it's wrapped in markdown code blocks.
    """
    # Try direct parsing first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try extracting from markdown code blocks
    json_block_match = re.search(r'```(?:json)?\s*(\{.+?\})\s*```', text, re.DOTALL)
    if json_block_match:
        try:
            return json.loads(json_block_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try finding JSON object in the text
    json_match = re.search(r'\{.+\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    raise ValueError(f"Could not extract valid JSON from response: {text[:200]}...")

def call_llm(model: str, base: str, minutes_text: str, md_or_raw: str, mode: str):
    client = get_client()
    msgs = [
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":f"<base>{base}</base>\n<minutes>\n{minutes_text}\n</minutes>\n<{mode}>\n{md_or_raw}\n</{mode}>"}
    ]
    resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=msgs,
        response_format={"type":"json_object"}
    )
    return resp.choices[0].message.content


# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", default=".", help="directory to recursively scan")
    ap.add_argument("--model", default="gpt-4o-mini", help="OpenAI model (e.g., gpt-4o-mini, gpt-4o)")
    ap.add_argument("--only", default="", help="limit to date (YYYY-MM-DD) or filename substring")
    args = ap.parse_args()

    root = Path(args.scan).resolve()
    print(f"[guardrail] scanning {root}")
    items = sorted(root.rglob("*_items.md"))
    raws  = sorted(root.rglob("*_raw.txt"))

    # Index raws by base for fallback when items.md missing
    raw_map = {p.stem[:-4]: p for p in raws if p.stem.endswith("_raw")}  # remove "_raw"
    count = 0

    for md_path in items:
        base = md_path.stem[:-6]  # drop "_items"
        if args.only and not (args.only in md_path.name or args.only in base):
            continue
        folder = md_path.parent
        minutes_text, minutes_file = find_minutes_for_base(base, folder)
        if not minutes_text.strip():
            print(f"[skip] no minutes found for {md_path}")
            continue
        md_text = md_path.read_text(encoding="utf-8", errors="ignore")
        try:
            print(f"[fix] {md_path}")
            out_json = call_llm(args.model, base, minutes_text, md_text, mode="items_md")
            data = extract_json_from_response(out_json)
            fixed_md = data.get("markdown","").strip()
            notes = data.get("notes","").strip()
        except Exception as e:
            print(f"[err] LLM failed on {md_path.name}: {e}")
            # Write error details for debugging
            err_log = folder / f"{base}_items.llm.error"
            err_log.write_text(f"Error: {e}\n\nRaw response:\n{out_json if 'out_json' in locals() else 'No response'}\n", encoding="utf-8")
            continue


        out_md = folder / f"{base}_items.llm.md"
        out_log = folder / f"{base}_items.llm.log"
        out_md.write_text(fixed_md + "\n", encoding="utf-8")
        out_log.write_text(notes + "\n", encoding="utf-8")
        print(f"[ok] wrote {out_md.name} (+ log)")

        count += 1

    # Fallback: if there are raw transcripts without items.md, we can still build from raw
    for raw_path in raws:
        base = raw_path.stem[:-4]  # drop "_raw"
        if (raw_path.parent / f"{base}_items.md").exists():
            continue  # already handled above
        if args.only and not (args.only in raw_path.name or args.only in base):
            continue
        folder = raw_path.parent
        minutes_text, minutes_file = find_minutes_for_base(base, folder)
        if not minutes_text.strip():
            print(f"[skip] no minutes found for {raw_path}")
            continue
        raw_text = raw_path.read_text(encoding="utf-8", errors="ignore")
        try:
            print(f"[build] {raw_path} -> {base}_items.llm.md")
            out_json = call_llm(args.model, base, minutes_text, raw_text, mode="raw")
            data = extract_json_from_response(out_json)
            fixed_md = data.get("markdown","").strip()
            notes = data.get("notes","").strip()
        except Exception as e:
            print(f"[err] LLM failed on {raw_path.name}: {e}")
            # Write error details for debugging
            err_log = folder / f"{base}_items.llm.error"
            err_log.write_text(f"Error: {e}\n\nRaw response:\n{out_json if 'out_json' in locals() else 'No response'}\n", encoding="utf-8")
            continue

        out_md = folder / f"{base}_items.llm.md"
        out_log = folder / f"{base}_items.llm.log"
        out_md.write_text(fixed_md + "\n", encoding="utf-8")
        out_log.write_text(notes + "\n", encoding="utf-8")
        print(f"[ok] wrote {out_md.name} (+ log)")
        count += 1

    print(f"[done] processed {count} file(s)")

if __name__ == "__main__":
    main()
