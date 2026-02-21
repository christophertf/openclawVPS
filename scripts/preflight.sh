#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== Current branch =="
git branch --show-current || true

echo
echo "== Git status (short) =="
git status --short || true

echo
echo "== Changed files (working tree) =="
git diff --name-only || true

echo
echo "== Recent change feed (last 30 lines) =="
if [[ -f "memory/change-feed.log" ]]; then
  tail -n 30 memory/change-feed.log
else
  echo "memory/change-feed.log not found"
fi
