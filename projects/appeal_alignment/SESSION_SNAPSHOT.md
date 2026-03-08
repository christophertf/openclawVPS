# Session Snapshot — Appeal Alignment Project
**Date:** March 5, 2026

## Update — 2026-03-05 13:47 UTC

- Framework sanity check passed for `scripts/align_with_llm.py`.
- Batch run completed across all 14 meetings using LLM alignment (`--cases-only`).
- Result: PASS 14 / FAIL 0.
- Canonical outputs refreshed in each meeting folder: `aligned.md`, `aligned.json`.
- Meeting folders normalized to minimal working set: `agenda.txt`, `transcript.txt`, `aligned.md`, `aligned.json` (plus optional PDF).

**Session goal:** Audit project state, fix tooling, consolidate scattered files, download missing agendas, reorganize into clean structure, and prepare project for VPS deployment.

---

## What This Project Does

Automates alignment of Sacramento Housing Code Advisory and Appeals Board (HCAB) meeting audio recordings with their official agenda/minutes. The output is a structured document where each agenda item (case number, address, owner, inspector) is matched to the verbatim section of the transcript where it was discussed.

**Two-stage pipeline:**
1. **Transcription** — Whisper AI converts audio to text (already done for all meetings)
2. **Alignment** — `hearing_align.py` matches transcript segments to agenda items using text similarity scoring

---

## What Was Done This Session

### 1. Fixed `hearing_align.py` — Added `--transcript` flag
**Problem:** The script only accepted `--audio` and would re-transcribe from scratch, ignoring the transcripts we already had.

**Fix:** Added `--transcript` flag that accepts a plain-text transcript file and skips Whisper entirely. It splits the prose into sentence-level pseudo-segments and assigns estimated timestamps using a configurable words-per-minute rate (`--wpm`, default 130).

Also fixed two pre-existing bugs in the script:
- `render_simple()` was defined twice; removed the dead first copy which had a `\\n` escape bug
- The `if __name__ == "__main__": main()` block was placed before `render_simple()` was defined, causing a `NameError` at runtime. Moved it to end of file.

**Usage:**
```bash
.venv/bin/python scripts/hearing_align.py \
  --transcript meetings/2025-09-10/2025-09-10_transcript.txt \
  --minutes meetings/2025-09-10/agenda.txt \
  --out meetings/2025-09-10/
```

**Outputs per run:**
- `<base>_aligned.md` — detailed alignment with scores and discrepancy notes
- `<base>_aligned.json` — machine-readable version with timestamps
- `<base>_simple.md` — clean human-readable view: agenda item → matched transcript

---

### 2. Discovered and Consolidated Scattered Files
Found three folders that had been placed inside the project directory with significant related content:

| Folder | What it was |
|---|---|
| `appeal_v2.0/` | An earlier iteration of the whole pipeline — duplicate scripts, duplicate audio, plus some partial LLM outputs from a previous run |
| `transcripts (2)/` | 2025 transcripts in SRT format (with timestamps) + processed `_paul_cases/` extractions and a `_summary/` with amounts.csv and invoices.csv |
| `transcripts_2024/` | 8 x 2024 hearing transcripts in SRT + TXT format + `_paul_cases/2024/` |

**Key discovery from the 2024 transcripts:** The transcript-inferred dates were wrong for several files. The Granicus database (see section 4) gave us the authoritative dates:
- `9a1f9844` — transcript said "Nov 27, 2023" → actually **Jun 12, 2024**
- `e9a8ea12` — transcript said "Feb 21, 2024" → actually **Mar 13, 2024**
- `d3fc5c83` — listed in wrong folder as "Jun 12" → actually **Aug 14, 2024**
- `9e9b0e02` — transcript said "Nov 13, 2024" → actually **Dec 11, 2024**

**What was extracted before those folders went to REMOVE:**
- All SRT (timestamped) and TXT transcripts → `transcripts/` and `transcripts/2024/`
- `_paul_cases/` outputs → `outputs/paul_cases/2024/` and `outputs/paul_cases/2025/`
- `_summary/` files (amounts.csv, invoices.csv, noteworthy_hits.txt) → `outputs/summary/`
- Partial LLM outputs from `appeal_v2.0/data/raw/` → `outputs/`

The three folders (including all duplicate scripts and audio) were moved to `REMOVE/` for manual deletion review.

Also found 8 x 2024 MP3 files sitting loose in `/home/fuckit/` (home directory) — pulled into the project.

---

### 3. Identified That Agendas Are Better Than Minutes PDFs
**Problem:** The Granicus "Minutes" viewer links point to a single-page approval document — not the detailed case breakdown we need for alignment.

**Discovery:** The Granicus **Agenda** viewer (`GeneratedAgendaViewer.php`) has exactly what we need: item numbers, case numbers, addresses, invoice amounts, owner names, inspector names — all structured in HTML.

**What we now use:** For each meeting, we scrape the Granicus agenda page and save it as `agenda.txt`. This is the authoritative source for alignment. The format looks like:

```
Housing Code Advisory and Appeals Board
Meeting Date: 2024-01-10

## Item 1 — Approval of Minutes for December 13, 2023
...
## Item 2 — Notice & Order Appeal
Location: District 1
Case No. 23-042298, Address: 4012 CLAIREWOOD WY; Owner: LEILA B REYES. Contact: ELIJAH PROK, Inspector
```

For 2025 meetings where we already had minutes PDFs (jan08.pdf, may14.pdf, etc.), those were converted to text via `pdftotext` and saved as `agenda.txt`.

---

### 4. Scraped Granicus for All Meeting Metadata
Visited `https://sacramento.granicus.com/ViewPublisher.php?view_id=65` and extracted the full archive listing — every HCAB meeting with dates, durations, clip IDs, and MP3 URLs.

**Key findings:**
- We have audio for 14 meetings (8 x 2024, 6 x 2025 including Sep 10)
- All 14 have agendas available on Granicus
- There are 3 additional recent meetings we have no audio for: Oct 8 2025, Dec 10 2025, Jan 14 2026 — user decision: not downloading more audio yet

Scraped `agenda.txt` for all 8 x 2024 meetings using `scripts/setup_meetings.py`.

---

### 5. Full Project Reorganization — `meetings/YYYY-MM-DD/`
**Before:** Files were scattered across `2025/apr/`, `2025/jan/`, `audio/`, `minutes/`, `transcripts/`, `transcripts/2024/`, `outputs/`, and loose in home directory.

**After:** Every meeting lives in its own self-contained folder under `meetings/`:

```
meetings/
├── 2024-01-10/
│   ├── audio.mp3              # source recording
│   ├── agenda.txt             # scraped from Granicus
│   ├── sacramento_89ed5d7c...srt   # transcript with timestamps
│   └── sacramento_89ed5d7c...txt   # plain text transcript
├── 2024-02-21/ ...
├── 2024-03-13/ ...
├── 2024-06-12/ ...
├── 2024-08-14/ ...
├── 2024-10-09/ ...
├── 2024-11-13/ ...
├── 2024-12-11/ ...
├── 2025-01-08/
│   ├── audio.mp3
│   ├── agenda.txt             # extracted from jan08.pdf
│   ├── minutes.pdf            # original PDF kept for reference
│   ├── sacramento_f7fbfc4f..._raw.txt
│   ├── sacramento_f7fbfc4f..._transcript.txt
│   ├── sacramento_f7fbfc4f....srt
│   └── sacramento_f7fbfc4f....txt
├── 2025-04-09/    # most complete — has stage1 + LLM output
├── 2025-05-14/ ...
├── 2025-06-11/ ...
├── 2025-08-13/ ...
└── 2025-09-10/    # has alignment output from this session
```

Each meeting folder will eventually also contain:
- `<uuid>_items.md` — stage 1 alignment output
- `<uuid>_aligned.md` / `_simple.md` — hearing_align.py output
- `<uuid>_items.llm.md` — LLM guardrail output (final)

---

### 6. New Script: `scripts/setup_meetings.py`
A one-time setup/reorganization script that:
- Discovers audio files from all old locations
- Scrapes agendas from Granicus or extracts from existing PDFs
- Copies transcripts into meeting folders
- Copies existing outputs into meeting folders
- Regenerates `meetings_checklist.csv`

Can be re-run safely — skips files already present.

---

### 7. `meetings_checklist.csv` — Live Tracking File
The checklist file in the project root tracks the status of every meeting at a glance. Open in any spreadsheet app.

**Columns:**
`date | duration | audio | agenda | transcript_raw | transcript_txt | transcript_srt | stage1_items | stage2_llm | aligned_output | status | folder`

**Status values:**
- `TRANSCRIBED` — audio + agenda + transcript ready, alignment not yet run
- `ALIGNED` — `hearing_align.py` output exists, no LLM guardrail yet
- `PARTIAL` — stage 1 run, LLM attempted but errored
- `COMPLETE` — LLM guardrail output exists

---

## Current State — All 14 Meetings

```
date        duration  audio  agenda  transcript  status       notes
2024-01-10  01h 27m   Y      Y       SRT only    TRANSCRIBED  ready to align
2024-02-21  01h 48m   Y      Y       SRT only    TRANSCRIBED  ready to align
2024-03-13  01h 19m   Y      Y       SRT only    TRANSCRIBED  ready to align
2024-06-12  03h 01m   Y      Y       SRT only    TRANSCRIBED  ready to align
2024-08-14  02h 22m   Y      Y       SRT only    TRANSCRIBED  ready to align
2024-10-09  01h 10m   Y      Y       SRT only    TRANSCRIBED  ready to align
2024-11-13  01h 17m   Y      Y       SRT only    TRANSCRIBED  ready to align
2024-12-11  01h 41m   Y      Y       SRT only    TRANSCRIBED  ready to align
2025-01-08  02h 09m   Y      Y       TXT+SRT     TRANSCRIBED  ready to align
2025-04-09  03h 00m   Y      Y       TXT+SRT     COMPLETE     LLM ran w/ JSON error; output saved but needs review
2025-05-14  02h 14m   Y      Y       TXT+SRT     TRANSCRIBED  ready to align
2025-06-11  02h 27m   Y      Y       TXT+SRT     TRANSCRIBED  ready to align
2025-08-13  01h 16m   Y      Y       TXT only    TRANSCRIBED  ready to align; no SRT
2025-09-10  03h 25m   Y      Y       TXT only    ALIGNED      hearing_align output done; no LLM pass yet
```

**13 of 14 meetings are ready to run alignment on right now.**

---

## Transcript File Formats — What We Have

Each meeting may have multiple transcript formats:

| Extension | Format | Source | Has Timestamps? |
|---|---|---|---|
| `_raw.txt` | continuous prose, one long paragraph | old pipeline (batch_supplement.py) | No |
| `_transcript.txt` | continuous prose, cleaner | old pipeline | No |
| `.txt` | one sentence per line | old pipeline (from transcripts 2 folder) | No |
| `.srt` | subtitle format, `HH:MM:SS,ms --> HH:MM:SS,ms` | Whisper with timestamps | **Yes** |

**For the 8 x 2024 meetings, we only have SRT + .txt (no _transcript.txt or _raw.txt).** This is fine — `hearing_align.py --transcript` works with any of the plain-text formats. The SRT files can also be parsed if we want proper timestamps.

**Recommendation:** Use `_transcript.txt` or `.txt` for `--transcript` input when available. For 2024 meetings, use the `.txt` file in the meeting folder.

---

## What's Next — Prioritized

### Step 1: Run `hearing_align.py` on All 13 Remaining Meetings
Every meeting has audio + agenda + transcript — they're all ready. This is the main thing to do.

**Command pattern for each meeting:**
```bash
.venv/bin/python scripts/hearing_align.py \
  --transcript meetings/YYYY-MM-DD/<transcript_file>.txt \
  --minutes meetings/YYYY-MM-DD/agenda.txt \
  --out meetings/YYYY-MM-DD/
```

**Or write a batch script** (suggested — see Step 1a below):
```bash
# Example batch runner
for dir in meetings/2024-*/; do
  date=$(basename "$dir")
  uuid=$(ls "$dir"*.txt 2>/dev/null | grep -v agenda | head -1)
  .venv/bin/python scripts/hearing_align.py \
    --transcript "$uuid" \
    --minutes "$dir/agenda.txt" \
    --out "$dir"
done
```

**Note on 2024 meetings:** These only have SRT + .txt transcripts (no _transcript.txt). Use the `.txt` file (line-per-sentence format). The alignment will work — it just won't have real timestamps, only estimated ones.

### Step 1a: Consider Using SRT Transcripts for Better Timestamps
The SRT files have real Whisper timestamps (e.g. `00:01:23,500 --> 00:01:27,200`). `hearing_align.py` currently doesn't parse SRT — it only handles plain text. Adding an `--srt` flag or an SRT parser to `load_transcript_text()` would give real timestamps in the output instead of estimated ones.

This matters most for the 2024 meetings where SRT is the only timestamped format available.

### Step 2: Review Apr 9, 2025 LLM Output
The `meetings/2025-04-09/2025-04-09_cases.llm.md` file exists but was generated during a run that logged a JSON error. The error log is at `2025-04-09_cases.llm.error`. Review whether the output is usable or needs to be regenerated.

### Step 3: Run LLM Guardrail (`llm_guardrail.py`) on All Meetings
After `hearing_align.py` has run on everything, `llm_guardrail.py` does a second pass using GPT-4o-mini to:
- Correct misalignments using context
- Fill in missing items
- Produce the final clean output

The previous run (Sept 30, 2025) had JSON parsing errors on 3/5 files. The error handling in `llm_guardrail.py` was improved before that run but still had issues. **Before running again, review `scripts/llm_guardrail.py`** to confirm the JSON extraction fallbacks are solid.

```bash
.venv/bin/python scripts/llm_guardrail.py --scan ./meetings
```

Requires `OPENAI_API_KEY` in `.env`.

### Step 4: Clean Up Legacy Directories
The following directories still exist and are no longer needed once you're satisfied the new `meetings/` structure has everything:

- `REMOVE/` — review then `rm -rf REMOVE/`
- `2025/` — old month-based source folder, audio is now in `meetings/`
- `audio/` — only had Sep 10 hearing, now in `meetings/2025-09-10/`
- `minutes/` — Sep 10 minutes, now in `meetings/2025-09-10/`
- `transcripts/` — all files copied into `meetings/`, can be archived
- `outputs/` — contents copied into `meetings/2025-04-09/` and `meetings/2025-09-10/`

**Don't delete until you've confirmed `meetings_checklist.csv` shows everything is in place.**

### Step 5: Add SRT Parser to `hearing_align.py` (Optional but Recommended for 2024)
Add a `load_transcript_srt()` function that parses SRT format into `Segment` objects with real timestamps:

```python
def load_transcript_srt(path: str) -> List[Segment]:
    segments = []
    with open(path) as f:
        content = f.read()
    blocks = re.split(r'\n\n+', content.strip())
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) < 3:
            continue
        times = re.match(r'(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)', lines[1])
        if not times:
            continue
        def to_secs(t):
            h,m,s = t.replace(',','.').split(':')
            return float(h)*3600 + float(m)*60 + float(s)
        start = to_secs(times.group(1))
        end   = to_secs(times.group(2))
        text  = ' '.join(lines[2:])
        segments.append(Segment(start=start, end=end, text=normalize_text(text)))
    return segments
```

Then add `--srt` argument alongside `--transcript` in `main()`.

---

## Project File Structure (Current)

```
appeal_alignment/
├── meetings/                    # PRIMARY — one folder per meeting
│   ├── 2024-01-10/
│   │   ├── audio.mp3
│   │   ├── agenda.txt           # scraped from Granicus
│   │   ├── sacramento_89ed5d7c....srt
│   │   └── sacramento_89ed5d7c....txt
│   ├── 2024-02-21/ ... (same structure)
│   ├── ... (8 x 2024 meetings)
│   ├── 2025-01-08/
│   │   ├── audio.mp3
│   │   ├── agenda.txt
│   │   ├── minutes.pdf
│   │   ├── sacramento_f7fbfc4f..._raw.txt
│   │   ├── sacramento_f7fbfc4f..._transcript.txt
│   │   ├── sacramento_f7fbfc4f....srt
│   │   └── sacramento_f7fbfc4f....txt
│   ├── 2025-04-09/              # most complete — has LLM output
│   │   ├── audio.mp3
│   │   ├── agenda.txt
│   │   ├── 2025-04-09_items.md
│   │   ├── 2025-04-09_cases.llm.md
│   │   ├── 2025-04-09_cases.llm.error
│   │   ├── 2025-04-09_cases.llm.log
│   │   └── sacramento_4b116fa9...{_raw,_transcript,.srt,.txt}
│   ├── 2025-05-14/ ...
│   ├── 2025-06-11/ ...
│   ├── 2025-08-13/ ...
│   └── 2025-09-10/              # has hearing_align output
│       ├── audio.mp3
│       ├── agenda.txt
│       ├── minutes.pdf
│       ├── 2025-09-10_items.md
│       ├── 2025-09-10_transcript_aligned.md
│       ├── 2025-09-10_transcript_simple.md
│       ├── 2025-09-10_raw.txt
│       └── 2025-09-10_transcript.txt
│
├── meetings_checklist.csv       # live status tracking — open in spreadsheet
├── scripts/
│   ├── hearing_align.py         # MAIN TOOL — alignment (fixed this session)
│   ├── batch_supplement.py      # old stage 1 — transcription + initial alignment
│   ├── llm_guardrail.py         # stage 2 — LLM correction pass
│   ├── run_all.sh               # orchestration script
│   └── setup_meetings.py        # one-time reorganization script (this session)
│
├── outputs/                     # legacy — contents moved to meetings/ folders
│   ├── paul_cases/2024/         # per-meeting "paul case" extractions (2024)
│   ├── paul_cases/2025/         # per-meeting "paul case" extractions (2025)
│   └── summary/                 # amounts.csv, invoices.csv, noteworthy_hits.txt
│
├── transcripts/                 # legacy — contents copied to meetings/ folders
│   ├── 2024/                    # 2024 SRT + TXT transcripts
│   └── *.txt / *.srt            # 2025 transcripts
│
├── 2025/                        # legacy source — apr/aug/jan/jun/may folders
├── audio/                       # legacy — just the Sep 10 recording
├── minutes/                     # legacy — just the Sep 10 minutes PDF
├── logs/                        # pipeline run logs from Sept 30, 2025
├── REMOVE/                      # staged for deletion — review before rm -rf
│   ├── appeal_v2.0/             # old pipeline version
│   ├── transcripts (2)/         # old transcript folder (contents extracted)
│   └── transcripts_2024/        # old 2024 folder (contents extracted)
└── .env                         # OPENAI_API_KEY
```

---

## Key Commands Reference

```bash
# Activate environment
source .venv/bin/activate

# Run alignment on a single meeting (using existing transcript)
python scripts/hearing_align.py \
  --transcript meetings/2025-01-08/sacramento_f7fbfc4f-216c-40fc-8e39-e413983021f2_transcript.txt \
  --minutes meetings/2025-01-08/agenda.txt \
  --out meetings/2025-01-08/

# Run alignment on a 2024 meeting (SRT/txt only)
python scripts/hearing_align.py \
  --transcript meetings/2024-01-10/sacramento_89ed5d7c-92b9-43bc-8113-7c3f989736a9.txt \
  --minutes meetings/2024-01-10/agenda.txt \
  --out meetings/2024-01-10/

# Run LLM guardrail on all meetings (requires OPENAI_API_KEY)
python scripts/llm_guardrail.py --scan ./meetings

# Update checklist after running alignment
python -c "import sys; sys.path.insert(0,'scripts'); from setup_meetings import rebuild_csv; rebuild_csv()"

# Check what's in a meeting folder
ls meetings/2024-01-10/
```

---

## Sharing to VPS

Use **rsync** to copy the project to your VPS. It skips audio, venv, and other local-only files automatically.

### rsync Command

```bash
rsync -av \
  --exclude='.venv/' \
  --exclude='*.mp3' \
  --exclude='*.m4a' \
  --exclude='*.wav' \
  --exclude='*.pdf' \
  --exclude='.env' \
  --exclude='__pycache__/' \
  --exclude='logs/' \
  --exclude='.playwright-mcp/' \
  /home/fuckit/appeal_alignment/ user@yourserver.com:/home/user/appeal_alignment/
```

Run this any time you want to sync updates. What gets transferred: scripts, agendas, transcripts, alignment outputs, checklist — all text files (~10MB total). What stays local: audio (~8GB), `.venv/` (7GB), PDFs, API keys.

---

### What the VPS Needs to Run Scripts

The VPS does **not** need Whisper — transcription is already done. It only needs:

```bash
# Python 3.9+ (usually pre-installed)
python3 --version

# Only one dependency for LLM guardrail
pip install openai

# Create .env with your OpenAI key
echo "OPENAI_API_KEY=sk-..." > /home/user/appeal_alignment/.env
```

**Scripts and what they need:**

| Script | Dependencies | Notes |
|---|---|---|
| `hearing_align.py` | stdlib only | No pip install needed |
| `setup_meetings.py` | stdlib only | No pip install needed |
| `llm_guardrail.py` | `openai` + `.env` | `pip install openai` |

**To run alignment on all remaining meetings on VPS:**
```bash
cd /home/user/appeal_alignment

# Run alignment on a single meeting
python3 scripts/hearing_align.py \
  --transcript meetings/2024-01-10/sacramento_89ed5d7c-92b9-43bc-8113-7c3f989736a9.txt \
  --minutes meetings/2024-01-10/agenda.txt \
  --out meetings/2024-01-10/

# Run LLM guardrail on all meetings (after alignment)
python3 scripts/llm_guardrail.py --scan ./meetings
```

**Note:** Audio files (`audio.mp3`) are not on the VPS — they stay local. This is fine because transcription is done and `hearing_align.py --transcript` doesn't need audio.

---

## Notes & Gotchas

- **The `.env` file** contains `OPENAI_API_KEY`. Required for `llm_guardrail.py`. Never commit this file.
- **The 2024 transcripts** were only transcribed once (old pipeline) and saved as SRT + plain .txt. They do NOT have `_raw.txt` or `_transcript.txt` variants. This is fine for alignment.
- **Apr 9, 2025** is the only meeting with an existing LLM output. The output has a JSON error flag but `2025-04-09_cases.llm.md` exists — check if it's actually usable before re-running.
- **Sep 10, 2025** has a `hearing_align.py` output (`_simple.md`, `_aligned.md`) but no LLM guardrail pass. The alignment scores in the output indicate quality — check how well it matched before deciding if LLM is needed.
- **The `REMOVE/` folder** still exists. Nothing has been permanently deleted. Review its contents before running `rm -rf REMOVE/`.
- **`setup_meetings.py`** is idempotent — safe to re-run. It won't overwrite existing files.
- **Granicus agenda scraping** — the URL pattern is `https://sacramento.granicus.com/GeneratedAgendaViewer.php?view_id=65&clip_id=XXXX`. All clip IDs are recorded in `setup_meetings.py`. If agendas need refreshing, re-run the script with the relevant folder deleted first.
