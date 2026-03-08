#!/usr/bin/env python3
"""
Appeal Hearing Transcript Alignment (single-file tool)

Usage:
  python hearing_align.py --audio path/to/audio.mp3 --minutes path/to/minutes.md --out /path/to/output_dir [--model base]

Outputs (in --out):
  - <basename>_aligned.md  (human-readable alignment)
  - <basename>_aligned.json (machine-readable with timestamps and scores)

Dependencies:
  - One of:
      * faster-whisper  (preferred, GPU-friendly)
      * openai-whisper  (fallback; pip install -U openai-whisper)
  - FFmpeg present on system for Whisper audio handling.

Notes:
  - Alignment uses stdlib-only text similarity (token overlap & keyword scoring) for robustness.
  - You can iterate on minutes structure by ensuring section headers (Markdown "##", or lines like "ITEM 1", "APPEAL OF ...").
"""

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional, Dict
from pathlib import Path


# --------------------------- Small utilities ---------------------------

STOPWORDS = {
    # Minimal English stopword list (kept short on purpose for legal-ish text)
    "the","a","an","and","or","but","if","in","on","at","to","for","from","by","of","with","as","is","it","that","this","those","these",
    "be","are","was","were","been","being","so","we","you","they","he","she","i","me","my","our","your","their","his","her","them",
    "do","does","did","done","can","could","should","would","may","might","must","will","shall","not","no","yes","there","here",
    "about","into","over","under","than","then","also","any","some","such","per","via","etc"
}

def normalize_text(s: str) -> str:
    # Collapse whitespace, strip control chars
    s = re.sub(r'\s+', ' ', s, flags=re.S).strip()
    return s

def tokenize(s: str) -> List[str]:
    s = s.lower()
    s = re.sub(r"[^a-z0-9'\- ]+", ' ', s)
    toks = [t.strip("-' ") for t in s.split() if t.strip("-' ")]
    return toks

def content_tokens(s: str) -> List[str]:
    return [t for t in tokenize(s) if t not in STOPWORDS and not t.isdigit() and len(t) > 1]

def jaccard(a: List[str], b: List[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)

def top_keywords(tokens: List[str], k: int = 12) -> List[str]:
    from collections import Counter
    c = Counter(tokens)
    # favor longer tokens slightly
    scored = [(tok, freq * (1 + 0.05*len(tok))) for tok, freq in c.items()]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [tok for tok, _ in scored[:k]]

def split_lines(s: str) -> List[str]:
    return [ln.rstrip() for ln in s.splitlines()]

# --------------------------- Data structures ---------------------------

@dataclass
class Segment:
    start: float
    end: float
    text: str

@dataclass
class MinutesSection:
    title: str
    body: str
    start_line: int
    end_line: int

@dataclass
class AlignmentHit:
    section_index: int
    seg_start_idx: int
    seg_end_idx: int
    score: float
    minute_title: str
    minute_excerpt: str
    transcript_excerpt: str
    time_range: Tuple[float, float]
    missing_in_minutes: List[str]
    missing_in_transcript: List[str]

# --------------------------- Whisper transcription ---------------------------

def transcribe(audio_path: str, model_name: str = "base") -> List[Segment]:
    """
    Returns a list of segments with start/end and text.
    Tries faster-whisper first, falling back to openai-whisper if unavailable.
    """
    try:
        from faster_whisper import WhisperModel
        model_size = model_name
        compute_type = "float16"  # good default; will fall back if unsupported
        device = "cuda" if _has_cuda() else "cpu"
        try:
            wm = WhisperModel(model_size, device=device, compute_type=compute_type)
        except Exception:
            # Fallback for CPU without float16
            compute_type = "int8" if device == "cpu" else "float32"
            wm = WhisperModel(model_size, device=device, compute_type=compute_type)

        segments, _ = wm.transcribe(audio_path, vad_filter=True, word_timestamps=False)
        out = []
        for seg in segments:
            out.append(Segment(start=float(seg.start), end=float(seg.end), text=normalize_text(seg.text)))
        return out

    except Exception as e_faster:
        print(f"[info] faster-whisper not available or failed ({e_faster}); trying openai-whisper...", file=sys.stderr)
        try:
            import whisper  # openai-whisper
            model = whisper.load_model(model_name)
            result = model.transcribe(audio_path, word_timestamps=False, verbose=False)
            out = []
            for seg in result.get('segments', []):
                out.append(Segment(start=float(seg['start']), end=float(seg['end']), text=normalize_text(seg['text'])))
            return out
        except Exception as e_whisper:
            print(f"[error] Both faster-whisper and openai-whisper failed.\n  faster-whisper error: {e_faster}\n  openai-whisper error: {e_whisper}", file=sys.stderr)
            raise

def _has_cuda() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False

# --------------------------- Minutes parsing ---------------------------

HEADER_PATTERNS = [
    re.compile(r'^\s*#{1,6}\s+(.+)$'),                  # Markdown headers
    re.compile(r'^\s*(ITEM\s+\d+[:.\- ]+.*)$', re.I),    # ITEM 1: ...
    re.compile(r'^\s*(APPEAL\s+OF\s+.+)$', re.I),        # APPEAL OF ...
    re.compile(r'^\s*(ROLL\s+CALL|PUBLIC\s+COMMENT|MINUTES|HEARING|ADJOURNMENT)\s*$', re.I),  # common sections
]

def parse_minutes(minutes_text: str) -> List[MinutesSection]:
    lines = split_lines(minutes_text)
    n = len(lines)
    # Identify headers
    headers: List[Tuple[int, str]] = []
    for i, ln in enumerate(lines):
        title = None
        for pat in HEADER_PATTERNS:
            m = pat.match(ln)
            if m:
                title = m.group(1) if m.lastindex else ln.strip()
                break
        # Heuristic: ALL CAPS line 3+ chars long is likely a header
        if not title and ln.strip().isupper() and len(ln.strip()) >= 3 and len(ln.strip()) <= 120:
            title = ln.strip()
        if title:
            headers.append((i, title.strip()))

    # If no headers found, split by blank lines into coarse sections
    if not headers:
        sections = []
        start = 0
        for i, ln in enumerate(lines + ['']):
            if ln.strip() == '' and (i - start) >= 3:
                body = '\n'.join(lines[start:i]).strip()
                if body:
                    sections.append(MinutesSection(title=f"Section {len(sections)+1}", body=body, start_line=start, end_line=i-1))
                start = i+1
        if not sections and minutes_text.strip():
            sections = [MinutesSection(title="All Minutes", body=minutes_text.strip(), start_line=0, end_line=n-1)]
        return sections

    # Build sections from headers
    sections: List[MinutesSection] = []
    for idx, (hline, title) in enumerate(headers):
        start = hline + 1
        end = headers[idx+1][0] - 1 if idx+1 < len(headers) else (n-1)
        body = '\n'.join(lines[start:end+1]).strip()
        sections.append(MinutesSection(title=title, body=body, start_line=hline, end_line=end))
    return sections

# --------------------------- Alignment core ---------------------------

def rolling_windows(segments: List[Segment], min_secs: float = 45.0, max_secs: float = 240.0) -> List[Tuple[int,int,List[str]]]:
    """
    Build rolling windows of transcript tokens spanning between min_secs and max_secs.
    Returns list of (start_idx, end_idx, tokens).
    """
    out = []
    n = len(segments)
    for i in range(n):
        cur_tokens = []
        t0 = segments[i].start
        j = i
        while j < n and (segments[j].end - t0) < max_secs:
            cur_tokens += content_tokens(segments[j].text)
            dur = segments[j].end - t0
            if dur >= min_secs:
                out.append((i, j, cur_tokens.copy()))
            j += 1
    return out

def align(minutes_sections: List[MinutesSection], segments: List[Segment]) -> List[AlignmentHit]:
    # Precompute transcript windows
    windows = rolling_windows(segments)
    hits: List[AlignmentHit] = []

    # Basic minute-section tokens & keywords
    m_tokens = [content_tokens(s.body + " " + s.title) for s in minutes_sections]
    m_keywords = [top_keywords(toks, k=12) for toks in m_tokens]

    for si, sec in enumerate(minutes_sections):
        best = None
        sec_toks = m_tokens[si]
        sec_keys = set(m_keywords[si])

        for (i, j, win_toks) in windows:
            base = jaccard(sec_toks, win_toks)
            # Keyword boost: reward presence of section keywords
            if sec_keys:
                overlap = len(sec_keys & set(win_toks)) / max(1, len(sec_keys))
            else:
                overlap = 0.0
            score = 0.65*base + 0.35*overlap
            if (best is None) or (score > best[0]):
                best = (score, i, j, win_toks)

        if best is None:
            continue

        score, i, j, win_toks = best
        # Extract excerpts
        tr_text = normalize_text(' '.join(seg.text for seg in segments[i:j+1]))
        t_start = segments[i].start
        t_end = segments[j].end

        # Compute "discrepancies" as token-set differences (heuristic)
        sec_set = set(sec_toks)
        win_set = set(win_toks)
        missing_in_minutes = sorted(list((win_set - sec_set)))[0:20]
        missing_in_transcript = sorted(list((sec_set - win_set)))[0:20]

        excerpt_minutes = (sec.body[:500] + ('...' if len(sec.body) > 500 else '')) if sec.body else ''
        excerpt_transcript = (tr_text[:500] + ('...' if len(tr_text) > 500 else '')) if tr_text else ''

        hits.append(AlignmentHit(
            section_index=si,
            seg_start_idx=i,
            seg_end_idx=j,
            score=round(score, 4),
            minute_title=sec.title.strip(),
            minute_excerpt=excerpt_minutes,
            transcript_excerpt=excerpt_transcript,
            time_range=(round(t_start,2), round(t_end,2)),
            missing_in_minutes=missing_in_minutes,
            missing_in_transcript=missing_in_transcript,
        ))

    # Sort hits by section order
    hits.sort(key=lambda h: h.section_index)
    return hits

# --------------------------- Rendering ---------------------------

def fmt_time(seconds: float) -> str:
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def render_markdown(basename: str, minutes_sections: List[MinutesSection], segments: List[Segment], hits: List[AlignmentHit]) -> str:
    lines = []
    lines.append(f"# Aligned Transcript vs Minutes — {basename}\n")
    lines.append("> Auto-generated alignment. Scores indicate textual similarity; review is recommended.\n")

    for hit in hits:
        sec = minutes_sections[hit.section_index]
        lines.append(f"\n---\n")
        lines.append(f"## Minutes Section: {sec.title}")
        lines.append(f"Time window matched in audio: `{fmt_time(hit.time_range[0])} – {fmt_time(hit.time_range[1])}` (score {hit.score})\n")

        lines.append("### Minutes (excerpt)")
        lines.append("```text")
        lines.append(sec.body.strip() if sec.body.strip() else "[No body text detected]")
        lines.append("```\n")

        lines.append("### Transcript (matched excerpt)")
        tr_text = ' '.join(segments[hit.seg_start_idx + k].text for k in range(0, hit.seg_end_idx - hit.seg_start_idx + 1))
        lines.append("```text")
        lines.append(tr_text.strip())
        lines.append("```\n")

        # Simple discrepancy summary (keywords missing on each side)
        if hit.missing_in_minutes or hit.missing_in_transcript:
            lines.append("### Discrepancies (keyword heuristic)")
            if hit.missing_in_minutes:
                lines.append(f"- Present in audio but not in minutes (sample): {', '.join(hit.missing_in_minutes[:12])}")
            if hit.missing_in_transcript:
                lines.append(f"- Present in minutes but not in audio (sample): {', '.join(hit.missing_in_transcript[:12])}")
            lines.append("")

    return "\n".join(lines).strip() + "\n"

def render_json(minutes_sections: List[MinutesSection], segments: List[Segment], hits: List[AlignmentHit]) -> Dict:
    return {
        "minutes_sections": [
            {"index": i, "title": s.title, "body": s.body, "start_line": s.start_line, "end_line": s.end_line}
            for i, s in enumerate(minutes_sections)
        ],
        "segments": [
            {"index": i, "start": seg.start, "end": seg.end, "text": seg.text}
            for i, seg in enumerate(segments)
        ],
        "alignments": [
            {
                **asdict(hit),
                "time_range_fmt": [fmt_time(hit.time_range[0]), fmt_time(hit.time_range[1])]
            }
            for hit in hits
        ]
    }

# --------------------------- Plain-text transcript loader ---------------------------

def load_transcript_text(path: str, words_per_minute: float = 130.0) -> List[Segment]:
    """
    Load a plain-text transcript (no timestamps) and split into pseudo-segments
    by sentence, assigning estimated timestamps based on speaking rate.
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    # Split into sentences on . ? ! followed by whitespace + capital, or newlines
    raw = re.split(r'(?<=[.?!])\s+(?=[A-Z])|(?<=[.?!])\s*\n+\s*', text)
    segments = []
    t = 0.0
    secs_per_word = 60.0 / words_per_minute
    for chunk in raw:
        chunk = normalize_text(chunk)
        if not chunk:
            continue
        word_count = len(chunk.split())
        duration = max(1.0, word_count * secs_per_word)
        segments.append(Segment(start=round(t, 2), end=round(t + duration, 2), text=chunk))
        t += duration
    return segments


# --------------------------- Main CLI ---------------------------

def main():
    ap = argparse.ArgumentParser(description="Align appeal hearing audio transcript to official minutes.")
    ap.add_argument("--audio", help="Path to audio file (mp3/wav/m4a/etc). Not needed if --transcript is given.")
    ap.add_argument("--transcript", help="Path to existing plain-text transcript (.txt). Skips Whisper transcription.")
    ap.add_argument("--minutes", required=True, help="Path to minutes file (txt/md)")
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--model", default="base", help="Whisper model size (tiny, base, small, medium, large-v2, etc.)")
    ap.add_argument("--minwin", type=float, default=45.0, help="Min window seconds for transcript matching")
    ap.add_argument("--maxwin", type=float, default=240.0, help="Max window seconds for transcript matching")
    ap.add_argument("--wpm", type=float, default=130.0, help="Estimated speaking rate (words/min) for timestamp estimation when using --transcript")
    args = ap.parse_args()

    if not args.audio and not args.transcript:
        print("[error] provide either --audio or --transcript", file=sys.stderr)
        sys.exit(2)

    minutes_path = args.minutes
    out_dir = args.out

    if not os.path.isfile(minutes_path):
        print(f"[error] minutes file not found: {minutes_path}", file=sys.stderr)
        sys.exit(2)
    os.makedirs(out_dir, exist_ok=True)

    # Read minutes
    with open(minutes_path, "r", encoding="utf-8", errors="ignore") as f:
        minutes_text = f.read()

    # Get segments — from existing transcript or by transcribing audio
    if args.transcript:
        if not os.path.isfile(args.transcript):
            print(f"[error] transcript file not found: {args.transcript}", file=sys.stderr)
            sys.exit(2)
        print(f"[info] loading transcript from {args.transcript} ...", file=sys.stderr)
        segments = load_transcript_text(args.transcript, words_per_minute=args.wpm)
        base = Path(args.transcript).stem
    else:
        audio_path = args.audio
        if not os.path.isfile(audio_path):
            print(f"[error] audio file not found: {audio_path}", file=sys.stderr)
            sys.exit(2)
        print("[info] transcribing audio ...", file=sys.stderr)
        segments = transcribe(audio_path, model_name=args.model)
        base = Path(audio_path).stem

    if not segments:
        print("[error] no transcript segments produced", file=sys.stderr)
        sys.exit(3)

    # Parse minutes
    print("[info] parsing minutes ...", file=sys.stderr)
    minutes_sections = parse_minutes(minutes_text)
    if not minutes_sections:
        print("[warn] minutes produced no sections; creating a single catch-all section", file=sys.stderr)
        minutes_sections = [MinutesSection(title="All Minutes", body=minutes_text.strip(), start_line=0, end_line=len(split_lines(minutes_text))-1)]

    # Align
    print("[info] aligning ...", file=sys.stderr)
    hits = align(minutes_sections, segments)

    # Render
    md = render_markdown(base, minutes_sections, segments, hits)
    js = render_json(minutes_sections, segments, hits)

    md_path = os.path.join(out_dir, f"{base}_aligned.md")
    json_path = os.path.join(out_dir, f"{base}_aligned.json")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(js, f, indent=2)

    simple_md = render_simple(base, minutes_sections, segments, hits)
    simple_path = os.path.join(out_dir, f"{base}_simple.md")
    with open(simple_path, "w", encoding="utf-8") as f:
        f.write(simple_md)

    print(f"[done] wrote:\n  {md_path}\n  {json_path}\n  {simple_path}")


def render_simple(basename: str, minutes_sections: List[MinutesSection], segments: List[Segment], hits: List[AlignmentHit]) -> str:
    lines = []
    lines.append(f"# Simple Minutes → Transcript — {basename}\n")
    lines.append("_Each minutes entry followed by its matched transcript window._\n")

    for hit in hits:
        sec = minutes_sections[hit.section_index]
        tr_text = " ".join(segments[i].text for i in range(hit.seg_start_idx, hit.seg_end_idx + 1)).strip()

        lines.append("\n---\n")
        lines.append(f"## {sec.title}")
        lines.append(f"Time: {fmt_time(hit.time_range[0])} – {fmt_time(hit.time_range[1])}  |  Score: {hit.score}")
        lines.append("\n### Minutes")
        lines.append(sec.body.strip() if sec.body.strip() else "[No body text detected]")
        lines.append("\n### Transcript")
        lines.append(tr_text)

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
