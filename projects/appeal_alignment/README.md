# Appeal Hearing Transcript Alignment

## Project Overview

This project automates the alignment of audio transcripts from appeal hearings with their corresponding official meeting minutes (typically in PDF format). The system uses Whisper AI for audio transcription and OpenAI's GPT-4o-mini to intelligently align and structure the transcript according to the authoritative minutes document.

### Purpose

Municipal appeal hearings (such as Housing Code Advisory and Appeals Board meetings) generate:
1. **Audio recordings** of the entire meeting
2. **Official minutes** (PDF) with structured agenda items, case numbers, addresses, and decisions

This project bridges these two sources by:
- Transcribing the audio using Whisper AI
- Parsing the official minutes to extract the authoritative agenda structure
- Mapping transcript segments to their corresponding agenda items
- Using an LLM to refine and correct the alignment

The result is a structured markdown document where each agenda item has:
- The official minutes summary
- The verbatim transcript of what was said
- Fees, fines, and verdicts from the minutes

---

## Project Structure

```
appeal_alignment/
├── audio/                  # Audio files (optional, can be anywhere)
├── transcripts/           # Raw and processed transcripts (optional)
├── outputs/               # Aligned outputs (optional)
├── scripts/               # Python and shell scripts
│   ├── batch_supplement.py    # Main transcription & alignment script
│   ├── llm_guardrail.py       # LLM-based refinement script
│   └── run_all.sh             # Pipeline orchestration script
├── logs/                  # Processing logs
├── minutes/               # Meeting minutes (PDF and TXT)
├── 2025/                  # Data organized by year
│   ├── apr/              # April hearings
│   ├── may/              # May hearings
│   ├── jun/              # June hearings
│   ├── jul/              # July hearings
│   └── aug/              # August hearings
└── README.md             # This file
```

---

## How It Works

### Two-Stage Pipeline

#### Stage 1: Transcription & Initial Alignment (`batch_supplement.py`)

**What it does:**
1. Recursively scans for audio files (`.mp3`, `.m4a`, `.wav`, etc.)
2. Finds corresponding minutes files (PDF or TXT) in the same folder or by date
3. Parses the minutes to extract agenda items (item numbers, case numbers, addresses, owners, inspectors)
4. Transcribes audio using Whisper AI (CUDA-accelerated if available)
5. Maps transcript chunks to agenda items using:
   - Inline cues (e.g., "item number 7")
   - Case numbers mentioned in the transcript
   - Addresses mentioned in the transcript
6. Outputs:
   - `<base>_raw.txt` - Full raw transcript
   - `<base>_items.md` - Initial alignment with agenda structure

**Key Features:**
- **Minutes-first approach**: Builds agenda from the official minutes, not from the transcript
- **Smart mapping**: Reassigns transcript blocks based on inline cues and metadata
- **Noise filtering**: Excludes "Uncontested" bulk items to focus on contested cases
- **Flexible input**: Works with audio files anywhere in the directory tree

#### Stage 2: LLM Refinement (`llm_guardrail.py`)

**What it does:**
1. Reads the PDF minutes (authoritative source)
2. Reads the initial alignment from Stage 1
3. Calls OpenAI GPT-4o-mini to:
   - Parse the minutes structure correctly
   - Realign transcript text to match the minutes exactly
   - Fill in missing items
   - Correct misalignments
   - Preserve verbatim transcript content (no hallucination)
4. Outputs:
   - `<base>_items.llm.md` - Corrected alignment
   - `<base>_items.llm.log` - Summary of changes made

**Key Features:**
- **Authoritative structure**: Uses the PDF minutes as the single source of truth
- **Intelligent realignment**: Fixes errors from Stage 1 using context and metadata
- **JSON response format**: Structured output with markdown and change notes
- **Robust error handling**: Handles malformed JSON, saves error logs for debugging

---

## Recent Changes & Improvements

### Problem Identified

The original system was not strictly following the PDF minutes structure. Issues included:
- Agenda parsing was missing items due to complex table formats in PDFs
- Transcript chunks were misaligned to wrong agenda items
- LLM processing failed on 3 out of 5 files due to JSON parsing errors
- The system tried to infer structure from transcripts instead of using minutes as authoritative source

### Changes Made

#### 1. **Improved Agenda Parsing** (`batch_supplement.py`, lines 160-253)

**Before:**
- Rigid regex patterns that only matched specific table formats
- Missed items in different table layouts (Notice & Order Appeals, Contested Cases, etc.)
- Failed to extract items from multi-line table cells

**After:**
- Liberal detection approach: finds any line starting with a number (1-50) that contains agenda keywords
- Collects context from surrounding lines (15+ lines)
- Extracts case numbers and addresses from context
- Deduplicates and sorts items by number
- Philosophy: "Catch most items, let LLM fix the details"

**Why:**
- PDF minutes have multiple table formats that are hard to parse perfectly with regex
- `pdftotext` breaks multi-line table cells across lines inconsistently
- A more forgiving approach is more robust and maintainable

#### 2. **Enhanced Error Handling** (`llm_guardrail.py`, lines 119-148, 188-236)

**Before:**
- Direct `json.loads()` that crashed on malformed JSON
- No fallback for JSON wrapped in markdown code blocks
- No error logging for debugging

**After:**
- New `extract_json_from_response()` function with multiple fallback strategies:
  1. Try direct JSON parsing
  2. Extract from markdown code blocks (```json ... ```)
  3. Search for JSON objects in text
- Saves error details to `.llm.error` files with raw LLM response
- Better error messages for debugging

**Why:**
- LLMs sometimes return JSON with unescaped characters or wrapped in code blocks
- Robust error handling prevents pipeline crashes
- Error logs help diagnose and fix issues

#### 3. **Strengthened Minutes-First Philosophy**

**Before:**
- System tried to infer structure from both minutes and transcript
- Transcript cues could override minutes structure
- Unclear which source was authoritative

**After:**
- Stage 1: Best-effort extraction from minutes, smart transcript mapping
- Stage 2: LLM uses minutes as single source of truth, realigns everything
- Clear separation: Stage 1 is fast/approximate, Stage 2 is accurate/authoritative

---

## Installation & Setup

### Prerequisites

```bash
# Python 3.8+
python3 --version

# Install system dependencies (Ubuntu/Debian)
sudo apt install -y poppler-utils ffmpeg

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -U openai-whisper PyPDF2 openai python-dotenv torch
```

### Configuration

1. **Set OpenAI API Key** (for Stage 2):
```bash
export OPENAI_API_KEY="sk-..."
# Or create a .env file:
echo "OPENAI_API_KEY=sk-..." > .env
```

2. **Organize your files**:
```
2025/
  apr/
    apr9.pdf                    # Minutes PDF
    sacramento_xxx.mp3          # Audio file
  may/
    may14.pdf
    sacramento_yyy.mp3
```

---

## Usage

### Option 1: Full Pipeline (Recommended)

Run both stages on all files:

```bash
./scripts/run_all.sh
```

This will:
1. Run `batch_supplement.py` on all audio files
2. Run `llm_guardrail.py` on all outputs
3. Generate logs in `./logs/`

### Option 2: Stage 1 Only (Transcription & Initial Alignment)

```bash
# Process all audio files
python scripts/batch_supplement.py --scan ./2025

# Process specific date
python scripts/batch_supplement.py --scan ./2025 --only "2025-04-09"

# Process specific file
python scripts/batch_supplement.py --scan ./2025 --only "4b116fa9"

# Debug: Show detected agenda items without transcribing
python scripts/batch_supplement.py --scan ./2025 --agenda-debug --only "apr"
```

**Options:**
- `--scan` or `--root`: Directory to recursively scan for audio files
- `--model`: Whisper model (default: `large-v3`, options: `medium`, `large-v2`, etc.)
- `--batch-size`: Whisper batch size for CUDA (default: 24)
- `--language`: Force language (default: `en`)
- `--only`: Filter by date (YYYY-MM-DD) or filename substring
- `--agenda-debug`: Print detected agenda items without transcribing
- `--debug-minutes`: Write first 200 lines of minutes to debug file

### Option 3: Stage 2 Only (LLM Refinement)

```bash
# Refine all existing alignments
python scripts/llm_guardrail.py --scan ./2025

# Refine specific file
python scripts/llm_guardrail.py --scan ./2025 --only "4b116fa9"

# Use different model
python scripts/llm_guardrail.py --scan ./2025 --model gpt-4o
```

**Options:**
- `--scan`: Directory to recursively scan for `*_items.md` files
- `--model`: OpenAI model (default: `gpt-4o-mini`, options: `gpt-4o`, `gpt-4-turbo`)
- `--only`: Filter by date or filename substring

---

## Output Files

For each audio file, the system generates:

```
2025/apr/
  apr9.pdf                                          # Input: Minutes PDF
  sacramento_4b116fa9-xxx.mp3                       # Input: Audio file
  sacramento_4b116fa9-xxx_raw.txt                   # Stage 1: Raw transcript
  sacramento_4b116fa9-xxx_items.md                  # Stage 1: Initial alignment
  sacramento_4b116fa9-xxx_items.llm.md              # Stage 2: Corrected alignment ✓
  sacramento_4b116fa9-xxx_items.llm.log             # Stage 2: Change summary
  sacramento_4b116fa9-xxx_items.llm.error           # Stage 2: Error log (if failed)
```

**Primary output:** `*_items.llm.md` - This is the final, corrected alignment.

### Output Format

```markdown
# Hearing Items – sacramento_4b116fa9-xxx

## Item 1 — Approval of Minutes

**Minutes summary (for matchup only):** Approval of Minutes for January 08, 2025...

### Transcript (verbatim)
```
[Verbatim transcript of what was said during this item]
```

### Fees, Fines & Verdicts
- Moved by consent unanimously 3-0

---

## Item 2 — 24-036756 — 6125 RIVERSIDE BL — Owner: G&SL LLC

**Minutes summary (for matchup only):** Case 24-036756, Inspector Daniel Lowther...

### Transcript (verbatim)
```
[Verbatim transcript of the hearing for this case]
```

### Fees, Fines & Verdicts
- Invoice CDDCHC21592 in the amount of $1,550
- Motion carried unanimously 3-0
```

---

## Troubleshooting

### Issue: No agenda items detected

**Symptoms:**
```
[agenda] (no items parsed)
```

**Solutions:**
1. Check if minutes PDF is in the same folder as audio
2. Run with `--debug-minutes` to inspect extracted text
3. Run with `--agenda-debug` to see what's being detected
4. Verify PDF is readable: `pdftotext -layout your_minutes.pdf -`

### Issue: LLM processing fails with JSON error

**Symptoms:**
```
[err] LLM failed on xxx: Expecting value: line 1 column 1 (char 0)
```

**Solutions:**
1. Check `.llm.error` file for raw LLM response
2. Verify OpenAI API key is set: `echo $OPENAI_API_KEY`
3. Try with a different model: `--model gpt-4o`
4. Check API quota/billing at platform.openai.com

### Issue: Transcript chunks misaligned

**Symptoms:**
- Item 7 transcript appears under Item 3
- Missing transcript for some items

**Solutions:**
1. This is expected in Stage 1 - run Stage 2 (LLM guardrail) to fix
2. Check if transcript mentions item numbers correctly (e.g., "item number 7")
3. Verify case numbers and addresses are in the minutes
4. The LLM will realign based on context and metadata

### Issue: CUDA out of memory

**Symptoms:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**
1. Reduce batch size: `--batch-size 16` or `--batch-size 8`
2. Use smaller Whisper model: `--model medium` or `--model base`
3. Force CPU: Set `CUDA_VISIBLE_DEVICES=""` before running

---

## Performance Notes

### Stage 1 (Whisper Transcription)
- **GPU (CUDA)**: ~10-15 minutes per hour of audio (large-v3 model)
- **CPU**: ~60-90 minutes per hour of audio
- **Memory**: 4-8 GB GPU RAM (large-v3), 8-16 GB system RAM

### Stage 2 (LLM Refinement)
- **Time**: ~30-60 seconds per file (depends on transcript length)
- **Cost**: ~$0.01-0.05 per file (gpt-4o-mini), ~$0.10-0.50 per file (gpt-4o)
- **API calls**: 1 call per file

### Typical Hearing
- **Audio length**: 1-3 hours
- **Total processing time**: 15-45 minutes (GPU) or 90-270 minutes (CPU)
- **Total cost**: $0.05-0.15 per hearing (gpt-4o-mini)

---

## Technical Details

### Whisper Configuration
- **Model**: `large-v3` (best accuracy) or `medium` (faster)
- **Language**: English (`en`)
- **FP16**: Enabled on CUDA for speed
- **Batch size**: 24 (adjustable)

### LLM Configuration
- **Model**: `gpt-4o-mini` (cost-effective) or `gpt-4o` (highest quality)
- **Temperature**: 0.2 (low randomness for consistency)
- **Response format**: JSON object with `markdown` and `notes` fields
- **System prompt**: Instructs LLM to use minutes as authoritative source

### Agenda Parsing Strategy
1. Extract text from PDF using `pdftotext -layout` (preferred) or PyPDF2 (fallback)
2. Filter allowed sections (CONSENT, PUBLIC HEARINGS, COST RECOVERY, etc.)
3. Block excluded sections (UNCONTESTED)
4. Find lines starting with numbers (1-50) that contain agenda keywords
5. Collect context (15+ lines) for each potential item
6. Extract case numbers (format: `XX-XXXXXX`) and addresses
7. Deduplicate by item number, sort numerically

### Transcript Mapping Strategy
1. Split transcript by "item number X" mentions
2. Reassign blocks based on:
   - Inline item mentions in first 1200 characters
   - Case numbers found in transcript
   - Addresses found in transcript
3. Map to agenda items from minutes
4. LLM refines alignment using full context

---

## Future Improvements

### Potential Enhancements
1. **Better PDF parsing**: Use `pdfplumber` or `camelot` for table extraction
2. **Speaker diarization**: Identify who's speaking (inspector, appellant, board member)
3. **Timestamp alignment**: Link transcript segments to audio timestamps
4. **Web interface**: Upload audio/minutes, view aligned output
5. **Batch processing**: Process multiple hearings in parallel
6. **Quality metrics**: Confidence scores for alignment accuracy

### Known Limitations
1. **Complex table formats**: Some PDF table layouts are hard to parse reliably
2. **Multi-line cells**: `pdftotext` breaks table cells across lines inconsistently
3. **Uncontested items**: Currently excluded (too many, not individually discussed)
4. **Audio quality**: Poor audio quality affects Whisper accuracy
5. **Accents/names**: Whisper may misspell names, addresses, or technical terms

---

## Contributing

### Reporting Issues
1. Include the audio filename and date
2. Attach the minutes PDF (if possible)
3. Share relevant log files or error messages
4. Describe expected vs. actual behavior

### Code Style
- Python 3.8+ with type hints
- Follow PEP 8 style guide
- Add docstrings to functions
- Keep functions focused and testable

---

## License

[Specify your license here]

---

## Contact

[Your contact information]

---

## Acknowledgments

- **OpenAI Whisper**: Audio transcription
- **OpenAI GPT-4o-mini**: Intelligent alignment
- **pdftotext (Poppler)**: PDF text extraction
- **PyPDF2**: Fallback PDF parsing

---

## Version History

### v2.0 (Current)
- Improved agenda parsing with liberal detection strategy
- Enhanced LLM error handling with multiple fallback strategies
- Strengthened minutes-first philosophy
- Added comprehensive error logging
- Better documentation

### v1.0 (Original)
- Initial implementation
- Basic Whisper transcription
- Simple agenda parsing
- LLM-based refinement
