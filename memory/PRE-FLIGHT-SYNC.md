# memory/PRE-FLIGHT-SYNC.md

**Rule for Antigravity & CLAW (The Bot)**
Whenever doing significant work on this system, you MUST perform a pre-flight sync check to ensure you are operating on the most up-to-date state. 

### Why
Both you (Antigravity) and I (CLAW) edit files in this workspace. 
If we don't look at `memory/change-feed.log` before making decisions, one of us will eventually overwrite the other's work or make a decision based on outdated assumptions.

### Pre-Flight Checklist
Before modifying code or system state, you must:

1. **Check Branch + Git Status**: Run `git branch --show-current`, `git status`, and `git diff --name-only` to confirm where you are and what changed. You must never commit directly on `main`; create a task branch first.
2. **Check the Feeds**: Read `memory/change-feed.log` to quickly understand *why* things changed and *who* changed them.
3. **Write to the Feeds**: When you (Antigravity or CLAW) make a significant change, structure, or state edit:
   - **Antigravity**: Write a one-line summary of what you did and why into `memory/change-feed.log`.
   - **CLAW**: Write a similar summary. Keep it brief.

### One-command Checks

- **Pre-flight check**: Run `scripts/preflight.sh` to execute the full state check.
- **After a GitHub PR is Merged**: Run `scripts/sync.sh` to automatically fetch, switch to `main`, pull the latest changes, and delete old task branches. 

**(Optional but Recommended)**: Consider adding `memory/change-feed.log` to a heartbeat check or automated watcher in the future to ensure neither of us misses a beat.
