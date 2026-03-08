#!/usr/bin/env python3
"""
batch_supplement.py — Minutes-first agenda & transcript mapper (recursive scan)

- Accepts EITHER --scan or --root (aliases).
- Recursively finds audio anywhere under the path.
- Minutes-first: builds agenda (allowed sections only) then splits transcript by those items.
- Smart mapping: reassigns transcript blocks by inline "item X", matching CASE #, or ADDRESS.
- Writes outputs next to the audio: <date_or_stem>_raw.txt and <date_or_stem>_items.md
- Whisper runs on CUDA if available. Batch size is configurable.

Deps (in your venv):
  pip install -U openai-whisper PyPDF2
Optional: apt install poppler-utils  (for faster/more reliable PDF text via pdftotext)
"""
import os, re, sys, argparse, subprocess
from pathlib import Path
from typing import Dict, Optional, List, Tuple, Set

# ---------- config / regex ----------
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
AUDIO_EXTS = {".mp3", ".m4a", ".wav", ".mp4", ".aac", ".wma", ".flac", ".mkv", ".mov"}

CASE_RE = re.compile(r"\b\d{2}-\d{6}\b")
ADDR_RE = re.compile(r"\b\d{3,6}\s+[A-Za-z0-9 .'\-]+")
OWNER_RE = re.compile(r"Owner:?\s*([^\n,]+)", re.IGNORECASE)
INSP_RE  = re.compile(r"Inspector:?\s*([^\n,]+)", re.IGNORECASE)

FEE_KEYS = [
    "fee","fine","cost","penalt","verdict","appeal","decision","invoice",
    "upheld","denied","approved","carried","motion","waive","reduced","reduction"
]

ALLOWED_SECTION_KEYS = [
    "CONSENT", "PUBLIC HEARINGS", "PUBLIC HEARING",
    "NOTICE", "NOTICE & ORDER", "NOTICE AND ORDER",
    "COST RECOVERY", "APPEALS", "REGULAR AGENDA"
]
BLOCKED_SECTION_KEYS = ["UNCONTESTED"]

NUMBER_WORDS = {
    1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten",
    11:"eleven",12:"twelve",13:"thirteen",14:"fourteen",15:"fifteen",16:"sixteen",17:"seventeen",
    18:"eighteen",19:"nineteen",20:"twenty",21:"twenty one",22:"twenty two",23:"twenty three",
    24:"twenty four",25:"twenty five",26:"twenty six",27:"twenty seven",28:"twenty eight",
    29:"twenty nine",30:"thirty"
}

# ---------- helpers ----------
def extract_date_from_name(name: str) -> Optional[str]:
    m = DATE_RE.search(name)
    return m.group(1) if m else None

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def detect_device() -> str:
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"

def have_pdftotext() -> bool:
    try:
        subprocess.run(["pdftotext", "-v"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

# ---------- minutes IO ----------
def pdf_to_text_with_pdftotext(pdf_path: Path) -> str:
    tmp = pdf_path.with_suffix(".tmp.txt")
    subprocess.run(["pdftotext", "-layout", str(pdf_path), str(tmp)], check=True)
    txt = tmp.read_text(encoding="utf-8", errors="ignore")
    try:
        tmp.unlink()
    except Exception:
        pass
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

def find_minutes_for_audio(audio_path: Path, scan_root: Path):
    # Prefer a minutes file in the same folder
    sibs = list(audio_path.parent.glob("*"))
    prefer = [p for p in sibs if p.is_file() and p.suffix.lower() in [".pdf", ".txt"]
              and "minutes" in p.stem.lower()]
    generic = [p for p in sibs if p.is_file() and p.suffix.lower() in [".pdf", ".txt"]]
    for p in prefer + generic:
        txt = read_minutes_file(p)
        if txt and len(txt.strip()) > 50:
            return txt, p

    # Else match by date anywhere under scan root
    d = extract_date_from_name(audio_path.name)
    if d:
        p = next((x for x in scan_root.rglob(f"{d}*_minutes.txt")), None)
        if p:
            return p.read_text(encoding="utf-8", errors="ignore"), p
        p = next((x for x in scan_root.rglob(f"{d}*.pdf")), None)
        if p:
            txt = read_minutes_file(p)
            if txt:
                return txt, p

    return "", None

# ---------- agenda model ----------
class AgendaItem:
    def __init__(self, num: int, summary: str, start_idx: int, end_idx: int):
        self.num = num
        self.summary = summary
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.case_numbers: Set[str] = set()
        self.addresses: Set[str] = set()

    def enrich_from_summary(self):
        for m in CASE_RE.finditer(self.summary):
            self.case_numbers.add(m.group(0))
        for m in ADDR_RE.finditer(self.summary):
            self.addresses.add(m.group(0).strip())

    def enrich_heading(self) -> str:
        parts = [f"Item {self.num}"]
        m = CASE_RE.search(self.summary)
        if m:
            parts.append(m.group(0))
        m = ADDR_RE.search(self.summary)
        if m:
            parts.append(m.group(0).strip())
        m = OWNER_RE.search(self.summary)
        if m:
            parts.append("Owner: " + m.group(1).strip())
        m = INSP_RE.search(self.summary)
        if m:
            parts.append("Inspector: " + m.group(1).strip())
        return "## " + " — ".join(parts)

# ---------- minutes parsing (improved table-aware parser) ----------
def parse_agenda(minutes_text: str) -> List[AgendaItem]:
    """
    Parse agenda items from minutes PDF text.
    This is a best-effort parser - the LLM guardrail will fix any issues.
    """
    if not minutes_text:
        return []

    raw_lines = minutes_text.replace("\t", "    ").splitlines()
    lines = [re.sub(r"\s+", " ", L).strip() for L in raw_lines]

    # Gate allowed/blocked regions
    allowed_flags = [True] * len(lines)
    current_allowed: Optional[bool] = None
    for i, line in enumerate(lines):
        up = line.upper()
        allow_hit = any(k in up for k in ALLOWED_SECTION_KEYS)
        block_hit = any(k in up for k in BLOCKED_SECTION_KEYS)
        if allow_hit and not block_hit:
            current_allowed = True
        elif block_hit:
            current_allowed = False
        if current_allowed is not None:
            allowed_flags[i] = current_allowed

    # Collect all potential item markers
    # We'll be very liberal here and let the LLM fix it later
    potential_items: List[Tuple[int, int, str]] = []  # (line_idx, item_num, context)
    
    # Pattern 1: Lines that start with a number (possibly an item)
    LEADING_NUM_RE = re.compile(r'^\s*(\d{1,2})[\s.:#)-]')
    
    for i, line in enumerate(lines):
        if not allowed_flags[i]:
            continue
        
        # Skip obvious noise
        if any(noise in line.lower() for noise in [
            "city of sacramento page", "floor hearing room", "published by",
            "city clerk", "regular meeting draft minutes"
        ]):
            continue
        
        # Look for lines starting with numbers
        m = LEADING_NUM_RE.match(line)
        if m:
            num = int(m.group(1))
            if 1 <= num <= 50:
                # Collect context (this line + next 15 lines)
                context_lines = lines[i:min(i+15, len(lines))]
                context = " ".join(context_lines).strip()
                
                # Check if this looks like an agenda item (has keywords)
                context_lower = context.lower()
                if any(kw in context_lower for kw in [
                    "approval", "minutes", "case", "inspector", "address", "owner",
                    "invoice", "appeal", "notice", "order", "cost", "recovery",
                    "apn", "street", " st ", " ave", " blvd", " ct ", " dr ",
                    "cddchc", "cddchb", "motion", "board"
                ]):
                    potential_items.append((i, num, context))

    # Deduplicate by item number (keep first occurrence)
    seen_nums = set()
    items: List[AgendaItem] = []
    
    for idx, (line_i, num, context) in enumerate(potential_items):
        if num in seen_nums:
            continue
        seen_nums.add(num)
        
        # Determine end line (next item or end of document)
        next_items = [x for x in potential_items[idx+1:] if x[1] not in seen_nums]
        end_i = next_items[0][0] if next_items else len(lines)
        
        # Build summary from context
        summary = context[:300]  # First 300 chars
        
        it = AgendaItem(num, summary, line_i, end_i)
        
        # Enrich with case numbers and addresses
        for m in CASE_RE.finditer(context):
            it.case_numbers.add(m.group(0))
        for m in ADDR_RE.finditer(context):
            it.addresses.add(m.group(0).strip())
        
        items.append(it)
    
    # Sort by item number
    items.sort(key=lambda x: x.num)
    
    return items


# ---------- transcript mapping ----------
def fees_from_window(lines: List[str]) -> List[str]:
    out, seen = [], set()
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        low = s.lower()
        money = bool(re.search(r"\$\s?\d[\d,]*(?:\.\d{2})?", s))
        if money or any(k in low for k in FEE_KEYS):
            if low not in seen:
                seen.add(low)
                out.append(s)
    return out

def item_patterns_for(nums: List[int]) -> re.Pattern:
    parts = []
    for n in nums:
        word = NUMBER_WORDS.get(n, "")
        parts.append(rf"\b(?:we\s+will\s+now\s+have\s+)?item\s+(?:number\s+)?{n}\b")
        parts.append(rf"\bitem\s*#\s*{n}\b")
        if word:
            parts.append(rf"\b(?:agenda\s+)?item\s+(?:number\s+)?{re.escape(word)}\b")
    return re.compile("|".join(parts), re.IGNORECASE)

def slice_from_first_agenda_marker(text: str, nums: List[int]) -> str:
    pat = item_patterns_for(nums[:1]) if nums else None
    if not pat:
        return text.strip()
    m = pat.search(text)
    return text[m.start():].strip() if m else text.strip()

def split_transcript_by_agenda(text: str, agenda_nums: List[int]) -> Dict[int, str]:
    if not agenda_nums:
        return {1: text.strip()}
    pat = item_patterns_for(agenda_nums)
    matches = []
    for m in pat.finditer(text):
        span = text[m.start():m.end()]
        found = None
        for n in agenda_nums:
            if re.search(rf"\b{n}\b", span):
                found = n; break
            w = NUMBER_WORDS.get(n, "")
            if w and re.search(rf"\b{re.escape(w)}\b", span, re.IGNORECASE):
                found = n; break
        if found is not None:
            matches.append((m.start(), found))
    if not matches:
        return {agenda_nums[0]: text.strip()}
    first_pos = {}
    for pos, n in matches:
        if n not in first_pos:
            first_pos[n] = pos
    ordered = [(first_pos[n], n) for n in agenda_nums if n in first_pos]
    ordered.sort(key=lambda x: x[0])
    blocks: Dict[int, str] = {}
    for i, (pos, n) in enumerate(ordered):
        end = ordered[i+1][0] if i+1 < len(ordered) else len(text)
        blocks[n] = text[pos:end].strip()
    for n in agenda_nums:
        blocks.setdefault(n, "")
    return blocks

INLINE_ITEM_RE = re.compile(r"\bitem\s+(?:number\s+)?(\d{1,2})\b", re.IGNORECASE)

def normalize_addr(a: str) -> str:
    return re.sub(r"\s+", " ", a.lower()).strip()

def build_case_addr_index(items: List[AgendaItem]):
    case_to_item: Dict[str, int] = {}
    addr_to_item: Dict[str, int] = {}
    for it in items:
        for c in it.case_numbers:
            case_to_item[c] = it.num
        for a in it.addresses:
            addr_to_item[normalize_addr(a)] = it.num
    return case_to_item, addr_to_item

def reassign_blocks(blocks: Dict[int, str], items: List[AgendaItem]) -> Dict[int, str]:
    case_map, addr_map = build_case_addr_index(items)
    valid_nums = {it.num for it in items}
    new_blocks = {n: "" for n in valid_nums}
    for n, txt in blocks.items():
        if not txt.strip():
            continue
        reassigned = False

        head = txt[:1200]
        m = INLINE_ITEM_RE.search(head)
        if m:
            X = int(m.group(1))
            if X in valid_nums and X != n:
                new_blocks[X] = (new_blocks[X] + "\n\n" + txt).strip() if new_blocks[X] else txt
                reassigned = True
        if reassigned:
            continue

        for c in set(CASE_RE.findall(txt)):
            if c in case_map and case_map[c] != n:
                dest = case_map[c]
                new_blocks[dest] = (new_blocks[dest] + "\n\n" + txt).strip() if new_blocks[dest] else txt
                reassigned = True
                break
        if reassigned:
            continue

        for a in ADDR_RE.findall(txt):
            key = normalize_addr(a)
            if key in addr_map and addr_map[key] != n:
                dest = addr_map[key]
                new_blocks[dest] = (new_blocks[dest] + "\n\n" + txt).strip() if new_blocks[dest] else txt
                reassigned = True
                break

        if not reassigned:
            new_blocks[n] = (new_blocks[n] + "\n\n" + txt).strip() if new_blocks[n] else txt
    return new_blocks

# ---------- whisper ----------
def run_whisper(audio_path: Path, model_name: str, device: str, batch_size: int, language: str) -> str:
    try:
        import whisper
    except ImportError:
        sys.stderr.write("Install whisper first: pip install -U openai-whisper\n"); raise

    print(f"[info] transcribing {audio_path} (device={device}, model={model_name}, batch={batch_size})")
    model = whisper.load_model(model_name, device=device)

    # Try with batch_size; fall back if this whisper build doesn't accept it
    try:
        result = model.transcribe(
            str(audio_path),
            fp16=(device == "cuda"),
            batch_size=batch_size,   # may not exist in some builds
            language=language
        )
    except TypeError:
        print("[warn] this whisper build doesn't support batch_size; retrying without it")
        result = model.transcribe(
            str(audio_path),
            fp16=(device == "cuda"),
            language=language
        )

    return (result.get("text") or "").strip()


# ---------- MD assembly ----------
def fees_from_minutes_slice(lines: List[str]) -> List[str]:
    return fees_from_window(lines)

def make_markdown(base_title: str, agenda: List[AgendaItem], transcript_blocks: Dict[int, str], minutes_lines: List[str]) -> str:
    md = [f"# Hearing Items – {base_title}\n"]
    for it in agenda:
        md.append("\n" + it.enrich_heading() + "\n")
        if it.summary.strip():
            md.append("**Minutes summary (for matchup only):**  " + it.summary.strip() + "\n")
        else:
            md.append("**Minutes summary:** (no entry found)\n")

        body = (transcript_blocks.get(it.num) or "").strip()
        if body:
            md.append("### Transcript (verbatim)\n")
            md.append("```\n" + body + "\n```\n")
        else:
            md.append("_No transcript content found for this item._\n")

        window = minutes_lines[it.start_idx:it.end_idx]
        fees = fees_from_minutes_slice(window)
        md.append("### Fees, Fines & Verdicts\n")
        if fees:
            for f in fees:
                md.append("- " + f)
        else:
            md.append("(no entries in minutes)\n")
        md.append("---")
    return "\n".join(md).rstrip() + "\n"

# ---------- IO ----------
def gather_audio(scan_root: Path) -> List[Path]:
    return [p for p in scan_root.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_EXTS]

def choose_output_basename(audio_path: Path, minutes_path: Optional[Path]) -> str:
    d = extract_date_from_name(audio_path.name)
    if not d and minutes_path is not None:
        d = extract_date_from_name(minutes_path.name)
    return d or audio_path.stem

def name_matches_only(audio_path: Path, only: str) -> bool:
    if not only:
        return True
    d = extract_date_from_name(audio_path.name)
    if d and d == only:
        return True
    return (only in audio_path.name)

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", default=None, help="directory to recursively scan for hearings (alias of --root)")
    ap.add_argument("--root", default=".", help="directory to recursively scan for hearings (alias of --scan)")
    ap.add_argument("--model", default="large-v3", help="whisper model (e.g., medium, large-v3)")
    ap.add_argument("--batch-size", type=int, default=24,
                help="Whisper batch size (ignored on builds that don't support it)")
    ap.add_argument("--language", default="en", help="ISO language to force (default: en)")
    ap.add_argument("--only", default="", help="only process a specific date (YYYY-MM-DD) or substring of filename")
    ap.add_argument("--agenda-debug", action="store_true", help="print detected agenda items (with line numbers) and skip transcription")
    ap.add_argument("--debug-minutes", action="store_true", help="write first 200 lines of minutes to *_minutes_debug.txt")
    args = ap.parse_args()

    scan_arg = args.scan if args.scan is not None else args.root
    scan_root = Path(os.path.expanduser(scan_arg)).resolve()

    device = detect_device()
    print(f"[info] device: {device}")
    print(f"[info] scanning: {scan_root}")

    audios = gather_audio(scan_root)
    if not audios:
        print(f"[warn] no audio found under {scan_root}")
        return

    for idx, audio in enumerate(sorted(audios), 1):
        if not name_matches_only(audio, args.only):
            continue

        print(f"\n[run {idx}/{len(audios)}] {audio}")
        minutes_text, minutes_path = find_minutes_for_audio(audio, scan_root)
        minutes_lines = [L.rstrip() for L in minutes_text.splitlines()] if minutes_text else []
        agenda = parse_agenda(minutes_text)

        if args.agenda_debug:
            if not agenda:
                print("[agenda] (no items parsed)")
            else:
                for it in agenda:
                    print(f"[agenda] line {it.start_idx}: Item {it.num} — {it.summary}")
            continue  # skip transcription in agenda-debug mode

        if args.debug_minutes and minutes_lines:
            dbg = audio.parent / (choose_output_basename(audio, minutes_path) + "_minutes_debug.txt")
            dbg.write_text("\n".join(minutes_lines[:200]), encoding="utf-8")
            print(f"[debug] wrote {dbg}")

        # Whisper
        try:
            full = run_whisper(audio, args.model, device, args.batch_size, args.language)
        except Exception as e:
            print(f"[error] whisper failed for {audio.name}: {e}")
            continue

        # Map transcript to agenda items
        agenda_nums = [it.num for it in agenda] or [1]
        full_trim = slice_from_first_agenda_marker(full, agenda_nums)
        blocks = split_transcript_by_agenda(full_trim, agenda_nums)
        if agenda:
            blocks = reassign_blocks(blocks, agenda)

        # Write outputs
        out_dir = audio.parent
        ensure_dir(out_dir)
        base = choose_output_basename(audio, minutes_path)
        (out_dir / f"{base}_raw.txt").write_text(full_trim, encoding="utf-8")
        md = make_markdown(base, agenda if agenda else [AgendaItem(1, "(no minutes)", 0, 0)], blocks, minutes_lines)
        (out_dir / f"{base}_items.md").write_text(md, encoding="utf-8")
        print(f"[ok] wrote {(out_dir / f'{base}_items.md')}")

    print("\n[done]")

if __name__ == "__main__":
    main()
