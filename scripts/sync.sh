#!/usr/bin/env bash
set -euo pipefail

# scripts/sync.sh
# Run this after a Pull Request is merged on GitHub to securely sync the workspace.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "1. Fetching latest from remote and pruning dead branches..."
git fetch --all --prune

current_branch=$(git branch --show-current)
if [[ "$current_branch" != "main" ]]; then
  echo "2. Switching from $current_branch to main branch..."
  # Stash any uncommitted tracking files just in case
  git stash -q || true
  git checkout main
fi

echo "3. Pulling latest main from origin..."
git pull --rebase origin main

echo "4. Cleaning up local branches that were squashed/merged..."
# If we were on a task branch and we just pulled main, we can safely delete
# the task branch if it's no longer on the remote (pruned).
git fetch -p
for branch in $(git branch -vv | awk '/: gone]/{print $1}'); do
  echo " - Deleting pruned branch: $branch"
  git branch -D "$branch" || true
done

echo
echo "✅ Workspace is completely synced with GitHub!"
git status --short
