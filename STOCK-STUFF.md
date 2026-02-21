# STOCK-STUFF.md

Purpose: single inventory of what OpenClaw includes by default (stock), what is present in this workspace, and what we should verify before expanding.

## 1) Stock platform surfaces (from OpenClaw docs)

### Core runtime
- Gateway service (message routing + sessions + tools)
- Control UI (browser dashboard)
- CLI command surface (`openclaw ...`)
- Session model + memory + tool orchestration

### Built-in automation
- Heartbeat loop (main-session periodic checks)
- Cron scheduler (main or isolated jobs, persisted under `~/.openclaw/cron/`)
- Hooks / system events / webhook-capable delivery modes

### Built-in tool families
- Filesystem + runtime (`read/write/edit/exec/process`)
- Web (`web_search`, `web_fetch`)
- Browser automation (`browser`)
- Canvas + nodes (`canvas`, `nodes`)
- Messaging + channel actions (`message`)
- Sessions/subagents (`sessions_*`, `session_status`, `agents_list`)
- Memory tools (`memory_search`, `memory_get`)
- Image analysis (`image`)
- TTS (`tts`)

### Channels (stock docs coverage)
- Telegram, WhatsApp, Discord, Slack, Signal, iMessage, plus plugin channels

### Model/auth surface
- Provider/model routing via `provider/model`
- OAuth + API-key paths (including OpenAI Codex OAuth)

## 2) Workspace stock files (identity + behavior layer)

These are the default/expected workspace primitives and are present here:
- `AGENTS.md` (operating rules)
- `SOUL.md` (persona)
- `USER.md` (user profile + preferences)
- `IDENTITY.md` (agent identity)
- `TOOLS.md` (local notes)
- `HEARTBEAT.md` (heartbeat checklist placeholder)
- `memory/YYYY-MM-DD.md` (daily memory)
- `memory/PRE-FLIGHT-SYNC.md` (local sync protocol)
- `memory/change-feed.log` (cross-agent change ledger)

Notes:
- `IDENTITY.md` is part of the stock workspace model and is active.
- `canvas/` is an optional stock workspace folder for node Canvas UI files (not required to exist until used).

## 3) Stock skills currently ready (eligible on this host)

From `openclaw skills list --eligible`:

- `healthcheck`
- `openai-image-gen`
- `openai-whisper-api`
- `skill-creator`
- `tmux`
- `weather`

Note: `mcporter` and `clawhub` binaries exist on disk, but the OpenClaw skill eligibility check currently marks those bundled skills as missing requirements in this host profile.

## 4) What is already configured/working in this build

- Telegram pairing and messaging path working
- OpenAI Codex OAuth model active
- Workspace git discipline in place (branch protections, hooks, preflight/sync scripts)
- Shared Antigravity/CLAW change-feed process active

## 5) Stock verification checklist (phase we can execute)

Use this as the work-through order for “what we have”.

1. Identity + memory bootstrap files load correctly
2. Gateway + Control UI reachable
3. Model/auth confirmed stable
4. Telegram send/receive stable
5. Heartbeat behavior confirmed (`HEARTBEAT.md` flow)
6. Cron add/list/run/runs lifecycle confirmed
7. Browser tool smoke test
8. Canvas tool smoke test (if node available)
9. Nodes status/describe (if node paired)
10. Image + TTS + web tools smoke tests
11. Session/subagent tool smoke tests
12. Git workflow enforcement (hook + branch protections) re-check

## 6) Confirmed-ready tools (explicitly confirmed with Chris)

- `weather` — confirmed accessible + usable in live run for Sacramento, CA (2026-02-21 UTC session).
  - Data source path used: `wttr.in`
  - Current conditions: supported (temp, feels-like, humidity, wind, pressure, visibility, condition)
  - Forecast horizon: 3 days via JSON (`format=j1`)
  - Time resolution: 8 hourly points/day (3-hour steps)
  - Extra fields available: astronomy (sun/moon phase, rise/set), UV, snow, precip
  - Practical limits: no historical weather archive, no severe-alert authority, no deep meteorological modeling

- `healthcheck` — confirmed accessible + usable in live run (2026-02-21 UTC session).
  - `openclaw security audit --deep` executed successfully.
  - Result summary: 0 critical, 3 warnings, 1 info.
  - `openclaw update status` executed successfully (channel: stable; install: pnpm).

## 7) Skill smoke-test results (this session)

- `tmux`: PASS (created/captured/killed temp session)
- `healthcheck`: PASS (OpenClaw status/diagnostics command executed)
- `weather`: PASS (network fetch path executed; no error)
- `openai-whisper-api`: SHOULD WORK (API key detected), NOT TESTED YET (defer live test until first real need)
- `openai-image-gen`: READY (skill eligible; generation test pending explicit image prompt run)
- `skill-creator`: READY (skill eligible; functional test should be done when we create/update a real skill artifact)

## 8) Boundaries for this doc

- This file is “stock-first”: only default platform/workspace capabilities.
- No expansion/custom plugins beyond what is already present.
- Add new sections only when we move into the next phase ("what we can have").
