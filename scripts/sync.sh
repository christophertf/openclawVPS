#!/usr/bin/env bash
set -euo pipefail

# scripts/sync.sh
# Safely sync local workspace to remote main after PR merges.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "1) Fetching latest refs..."
git fetch --all --prune

current_branch="$(git branch --show-current)"

# Do not auto-stash silently; fail fast so nothing is hidden/lost.
if [[ -n "$(git status --porcelain)" ]]; then
  echo "❌ Working tree is not clean. Commit or stash changes first, then rerun scripts/sync.sh." >&2
  git status --short
  exit 1
fi

if [[ "$current_branch" != "main" ]]; then
  echo "2) Switching from $current_branch to main..."
  git checkout main
else
  echo "2) Already on main."
fi

echo "3) Fast-forwarding local main to origin/main..."
git pull --ff-only origin main

echo "4) Pruning local branches removed from remote..."
# shellcheck disable=SC2016
git branch -vv | awk '/: gone]/{print $1}' | while read -r branch; do
  [[ -z "$branch" ]] && continue
  [[ "$branch" == "main" ]] && continue
  echo " - Deleting pruned branch: $branch"
  git branch -D "$branch" || true
done

echo

echo "✅ Sync complete."
git status --short
