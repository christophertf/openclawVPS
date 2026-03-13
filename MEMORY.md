# Long-Term Memory (Curated Context)

## User Profile
- Name: Chris
- Prefers direct, concise responses.
- Wants CLAW to proactively escalate blockers instead of burying them in routine logs.
- Strategic goal: CLAW should behave like an always-on VPS operator (proactive, automated, continuously improving), not a reactive chat-only assistant.

## Platform + Operations
- OpenRouter integration is enabled in OpenClaw config (`/home/claw/.openclaw/openclaw.json`).
- Routing aliases available:
  - `grok-legal`
  - `router-cheap`
  - `router-verify`
- Model switching was verified live by switching to `grok-legal` and back to default Codex.

## Working Rule
- Record major capability changes immediately in:
  1) `memory/YYYY-MM-DD.md` (event log)
  2) `MEMORY.md` (curated long-term)
  3) `memory/change-feed.log` (audit trail)
