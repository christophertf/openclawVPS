#!/usr/bin/env bash
# Usage: bash scripts/run_all.sh [SCAN_ROOT] [WHISPER_MODEL] [LLM_MODEL]
# Defaults: SCAN_ROOT=./2025  WHISPER_MODEL=large-v3  LLM_MODEL=gpt-4o-mini

set -u
SCAN_ROOT="${1:-./2025}"
WHISPER_MODEL="${2:-large-v3}"
LLM_MODEL="${3:-gpt-4o-mini}"

cd "$(dirname "$0")/.."

# Logs
ts="$(date +%Y%m%d-%H%M%S)"
BATCH_LOG="logs/batch_${ts}.log"
LLM_LOG="logs/guardrail_${ts}.log"
MASTER_LOG="logs/run_${ts}.log"

{
  echo "=== START $(date) ==="
  echo "[info] scan root: $SCAN_ROOT"
  echo "[info] whisper model: $WHISPER_MODEL"
  echo "[info] guardrail model: $LLM_MODEL"
} | tee -a "$MASTER_LOG"

# Activate venv
source .venv/bin/activate

# Step 1: Local Whisper batch (GPU)
{
  echo "[batch] $(date) starting"
  python -m py_compile scripts/batch_supplement.py || echo "[batch] warn: syntax check failed but continuing"
  python scripts/batch_supplement.py --scan "$SCAN_ROOT" --model "$WHISPER_MODEL"
  echo "[batch] $(date) done"
} | tee -a "$BATCH_LOG" | tee -a "$MASTER_LOG"

# Step 2: LLM guardrail fixups (uses OPENAI_API_KEY from .env or env)
{
  echo "[guardrail] $(date) starting"
  python scripts/llm_guardrail.py --scan "$SCAN_ROOT" --model "$LLM_MODEL"
  echo "[guardrail] $(date) done"
} | tee -a "$LLM_LOG" | tee -a "$MASTER_LOG"

echo "=== FINISH $(date) ===" | tee -a "$MASTER_LOG"
