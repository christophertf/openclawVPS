#!/usr/bin/env python3
"""
One-time setup script:
 1. Scrapes agenda text from Granicus for all meetings
 2. Reorganizes everything into meetings/YYYY-MM-DD/ folders
 3. Moves 2024 MP3s from home dir into project
 4. Rebuilds meetings_checklist.csv
"""

import os
import re
import shutil
import csv
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).parent.parent
MEETINGS_DIR = ROOT / "meetings"
HOME = Path("/home/fuckit")

# ---------------------------------------------------------------------------
# All known meetings: date -> {uuid, clip_id, notes}
# ---------------------------------------------------------------------------
MEETINGS = [
    # 2024
    {"date": "2024-01-10", "uuid": "sacramento_89ed5d7c-92b9-43bc-8113-7c3f989736a9", "clip_id": "5780", "duration": "01h 27m"},
    {"date": "2024-02-21", "uuid": "sacramento_d227d153-df8d-4508-b2a0-f3d1679a7a09", "clip_id": "5828", "duration": "01h 48m"},
    {"date": "2024-03-13", "uuid": "sacramento_e9a8ea12-f485-412f-b787-c16840afb98f", "clip_id": "5851", "duration": "01h 19m"},
    {"date": "2024-06-12", "uuid": "sacramento_9a1f9844-31ca-40a9-a765-620009459976", "clip_id": "5951", "duration": "03h 01m"},
    {"date": "2024-08-14", "uuid": "sacramento_d3fc5c83-cd5d-4586-8549-9e1476053613", "clip_id": "6012", "duration": "02h 22m"},
    {"date": "2024-10-09", "uuid": "sacramento_e77c0d05-577e-495c-82c8-2c186cc58592", "clip_id": "6074", "duration": "01h 10m"},
    {"date": "2024-11-13", "uuid": "sacramento_1b2df796-9cb0-4cf6-8c85-c9d5e9592a21", "clip_id": "6105", "duration": "01h 17m"},
    {"date": "2024-12-11", "uuid": "sacramento_9e9b0e02-c42a-4528-95b4-280b3cd75583", "clip_id": "6130", "duration": "01h 41m"},
    # 2025
    {"date": "2025-01-08", "uuid": "sacramento_f7fbfc4f-216c-40fc-8e39-e413983021f2", "clip_id": "6142", "duration": "02h 09m"},
    {"date": "2025-04-09", "uuid": "sacramento_4b116fa9-dccf-4811-a3bb-e399c1ab6ad8", "clip_id": "6368", "duration": "03h 00m"},
    {"date": "2025-05-14", "uuid": "sacramento_30366163-19a5-4f9e-8fd2-af0995c63f75", "clip_id": "6404", "duration": "02h 14m"},
    {"date": "2025-06-11", "uuid": "sacramento_3c0066af-e64e-4589-aa16-4b7b0d05dc5e", "clip_id": "6432", "duration": "02h 27m"},
    {"date": "2025-08-13", "uuid": "sacramento_462f75df-b24b-4a59-83f6-c9c06af56c81", "clip_id": "6484", "duration": "01h 16m"},
    {"date": "2025-09-10", "uuid": "2025-09-10_hearing",                               "clip_id": "6510", "duration": "03h 25m"},
]

# ---------------------------------------------------------------------------
# Agenda scraper
# ---------------------------------------------------------------------------
class AgendaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []
        self._in_blockquote = 0
        self._in_table = False
        self._current = {}
        self._cell_idx = 0
        self._cell_text = ""
        self._in_td = False

    def handle_starttag(self, tag, attrs):
        if tag == "blockquote": self._in_blockquote += 1
        if tag == "table" and self._in_blockquote: self._in_table = True; self._current = {}; self._cell_idx = 0
        if tag == "td" and self._in_table: self._in_td = True; self._cell_text = ""
        if tag == "tr" and self._in_table: self._cell_idx = 0

    def handle_endtag(self, tag):
        if tag == "blockquote": self._in_blockquote -= 1
        if tag == "table" and self._in_table:
            self._in_table = False
            if self._current.get("number"):
                self.items.append(dict(self._current))
        if tag == "td" and self._in_td:
            self._in_td = False
            text = re.sub(r'\s+', ' ', self._cell_text).strip()
            if self._cell_idx == 0 and re.match(r'^\d+\.$', text):
                self._current["number"] = text.rstrip('.')
            elif self._cell_idx == 1:
                if not self._current.get("title"):
                    self._current["title"] = text
                elif text.startswith("Location:"):
                    self._current["location"] = text[9:].strip()
                elif text.startswith("Recommendation:"):
                    self._current["recommendation"] = text[15:].strip()
            self._cell_idx += 1

    def handle_data(self, data):
        if self._in_td:
            self._cell_text += data


def scrape_agenda(clip_id, date):
    url = f"https://sacramento.granicus.com/GeneratedAgendaViewer.php?view_id=65&clip_id={clip_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  [warn] fetch failed for {date}: {e}")
        return None

    parser = AgendaParser()
    parser.feed(html)

    lines = [f"Housing Code Advisory and Appeals Board", f"Meeting Date: {date}", ""]
    for item in parser.items:
        lines.append(f"## Item {item['number']} — {item['title']}")
        if item.get("location"):
            lines.append(f"Location: {item['location']}")
        if item.get("recommendation"):
            lines.append(item["recommendation"])
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# File discovery helpers
# ---------------------------------------------------------------------------
def find_file(patterns):
    """Return first existing path from a list of candidate paths/globs."""
    for p in patterns:
        p = Path(p)
        if p.exists():
            return p
        parent = p.parent
        if parent.exists():
            matches = list(parent.glob(p.name))
            if matches:
                return matches[0]
    return None


def meeting_dir(date):
    d = MEETINGS_DIR / date
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    MEETINGS_DIR.mkdir(exist_ok=True)

    for m in MEETINGS:
        date = m["date"]
        uuid = m["uuid"]
        clip_id = m["clip_id"]
        short_uuid = uuid.replace("sacramento_", "")
        mdir = meeting_dir(date)
        print(f"\n[{date}]")

        # --- Audio ---
        audio_candidates = [
            ROOT / "2025" / date[5:7].lstrip("0").lower()[:3] / f"{uuid}.mp3",
            ROOT / "audio" / f"{uuid}.mp3",
            HOME / f"{uuid}.mp3",
            ROOT / "REMOVE" / "appeal_v2.0" / "2000" / f"{uuid}.mp3",
        ]
        # match month folder by date
        year = date[:4]
        month_dirs = {
            "01":"jan","02":"feb","03":"mar","04":"apr","05":"may","06":"jun",
            "07":"jul","08":"aug","09":"sep","10":"oct","11":"nov","12":"dec"
        }
        month_folder = month_dirs.get(date[5:7], "")
        audio_candidates.insert(0, ROOT / year / month_folder / f"{uuid}.mp3")
        # Sep 10 special case
        audio_candidates.append(ROOT / "audio" / "2025-09-10_hearing.mp3")

        audio_src = find_file(audio_candidates)
        audio_dst = mdir / "audio.mp3"
        if audio_src and not audio_dst.exists():
            shutil.copy2(audio_src, audio_dst)
            print(f"  audio: {audio_src.name} -> meetings/{date}/audio.mp3")
        elif audio_dst.exists():
            print(f"  audio: already present")
        else:
            print(f"  audio: NOT FOUND")

        # --- Agenda / Minutes ---
        agenda_dst = mdir / "agenda.txt"
        if not agenda_dst.exists():
            # Check for existing minutes PDF to convert
            pdf_candidates = [
                ROOT / year / month_folder / f"{month_folder}{date[8:10]}.pdf",
                ROOT / year / month_folder / f"{month_folder}{date[5:7]}2025.pdf",
                ROOT / "minutes" / f"{date}_minutes.pdf",
            ]
            pdf_src = find_file(pdf_candidates)
            if pdf_src:
                # Copy PDF and also extract text
                shutil.copy2(pdf_src, mdir / "minutes.pdf")
                os.system(f'pdftotext -layout "{pdf_src}" "{mdir}/agenda.txt" 2>/dev/null')
                print(f"  agenda: extracted from {pdf_src.name}")
            else:
                # Scrape from Granicus
                print(f"  agenda: scraping from Granicus (clip {clip_id})...")
                text = scrape_agenda(clip_id, date)
                if text:
                    agenda_dst.write_text(text, encoding="utf-8")
                    print(f"  agenda: scraped OK ({len(text)} chars)")
                else:
                    print(f"  agenda: FAILED to scrape")
        else:
            print(f"  agenda: already present")

        # --- Transcripts ---
        for suffix in ["_raw.txt", "_transcript.txt", ".srt", ".txt"]:
            src_candidates = [
                ROOT / "transcripts" / f"{uuid}{suffix}",
                ROOT / "transcripts" / "2024" / f"{uuid}{suffix}",
                ROOT / "transcripts" / f"{date}{suffix.replace('_raw','_raw').replace('_transcript','_transcript')}",
            ]
            # Special case for sep10
            if "2025-09-10" in uuid or date == "2025-09-10":
                src_candidates += [
                    ROOT / "transcripts" / f"2025-09-10_raw.txt",
                    ROOT / "transcripts" / f"2025-09-10_transcript.txt",
                ]
            src = find_file(src_candidates)
            if src:
                clean_suffix = suffix.lstrip("_")
                dst_name = f"transcript_{clean_suffix}" if not suffix.startswith("_") else f"transcript{suffix}"
                dst = mdir / src.name  # keep original filename for easy cross-ref
                if not dst.exists():
                    shutil.copy2(src, dst)

        # --- Existing outputs ---
        for pattern in [f"{date}_items.md", f"{date}_cases.llm.md", f"{date}_cases.llm.error",
                         f"{date}_cases.llm.log", f"{date}_raw.txt",
                         f"{uuid}_aligned.md", f"{uuid}_simple.md", f"2025-09-10_transcript_aligned.md",
                         f"2025-09-10_transcript_simple.md", f"2025-09-10_items.md"]:
            src = find_file([ROOT / "outputs" / pattern])
            if src:
                dst = mdir / src.name
                if not dst.exists():
                    shutil.copy2(src, dst)

        print(f"  -> meetings/{date}/ : {[f.name for f in mdir.iterdir()]}")

    # --- Rebuild CSV ---
    rebuild_csv()
    print("\n[done] meetings/ organized, checklist updated.")


def rebuild_csv():
    rows = []
    for m in MEETINGS:
        date = m["date"]
        mdir = MEETINGS_DIR / date
        files = {f.name for f in mdir.iterdir()} if mdir.exists() else set()

        has_audio    = "audio.mp3" in files
        has_agenda   = "agenda.txt" in files or "minutes.pdf" in files
        has_raw      = any("_raw.txt" in f for f in files)
        has_trans    = any("_transcript.txt" in f for f in files)
        has_srt      = any(f.endswith(".srt") for f in files)
        has_stage1   = any("_items.md" in f for f in files)
        has_llm      = any("_cases.llm.md" in f or "_items.llm.md" in f for f in files)
        has_aligned  = any("_aligned.md" in f or "_simple.md" in f for f in files)

        if has_aligned or has_llm:
            status = "COMPLETE" if has_llm else "ALIGNED"
        elif has_stage1:
            status = "PARTIAL"
        elif has_trans or has_raw or has_srt:
            status = "TRANSCRIBED"
        elif has_audio and has_agenda:
            status = "READY"
        elif has_audio:
            status = "NEEDS_AGENDA"
        else:
            status = "AUDIO_MISSING"

        rows.append({
            "date": date,
            "duration": m["duration"],
            "audio": "Y" if has_audio else "N",
            "agenda": "Y" if has_agenda else "N",
            "transcript_raw": "Y" if has_raw else "N",
            "transcript_txt": "Y" if has_trans else "N",
            "transcript_srt": "Y" if has_srt else "N",
            "stage1_items": "Y" if has_stage1 else "N",
            "stage2_llm": "Y" if has_llm else "N",
            "aligned_output": "Y" if has_aligned else "N",
            "status": status,
            "folder": f"meetings/{date}/",
        })

    csv_path = ROOT / "meetings_checklist.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"[csv] wrote {csv_path}")


if __name__ == "__main__":
    main()
