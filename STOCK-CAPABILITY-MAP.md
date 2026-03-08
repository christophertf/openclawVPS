# STOCK-CAPABILITY-MAP.md

Purpose: full stock capability map for this environment.

Status legend:
- CONFIRMED = tested live with Chris in this session
- READY = available now but not yet live-tested together
- BLOCKED = stock capability exists but currently unavailable due to setup/config/prereqs
- N/A = not applicable on this host profile

## A) Core runtime + platform

- Gateway runtime: READY
- Control UI: READY
- Session routing + memory system: READY
- Model auth (OpenAI Codex OAuth): CONFIRMED
- Telegram channel messaging path: CONFIRMED

## B) Stock tool families (OpenClaw-native)

- Filesystem/runtime tools (`read/write/edit/exec/process`): CONFIRMED
- Memory tools (`memory_search/memory_get`): READY
- Web tools (`web_search/web_fetch`): READY
- Image tool (`image`): READY
- TTS tool (`tts`): READY
- Browser tool (`browser`): READY
- Canvas tool (`canvas`): READY (requires node target context for full value)
- Nodes tool (`nodes`): READY (capabilities depend on paired node + permissions)
- Sessions/subagents tools: READY
- Message tool: CONFIRMED (Telegram)

## C) Automation

- Heartbeat framework: READY
- Cron scheduler: READY
- Hook system (internal hooks): READY

## D) Stock skills on this host profile

Eligible now (`openclaw skills list --eligible`):
- healthcheck (CONFIRMED)
- weather (CONFIRMED)
- tmux (CONFIRMED smoke)
- openai-whisper-api (SHOULD WORK, NOT TESTED YET; defer live test until first real need; later migrate to local/offline transcription to reduce API cost)
- openai-image-gen (READY)
- skill-creator (READY)

Not eligible yet (stock exists, prerequisites missing):
- Many bundled skills blocked by missing binaries, OS constraints, missing API keys, or channel config.

## E) Node/media-style capabilities (where your “camera/screen/contact/reminder” observation came from)

### Node/media actions (stock capability exists)
- Camera snapshot (`camera_snap` path): READY/BLOCKED depending on paired node + permission + foreground
- Camera clip (`camera_clip` path): READY/BLOCKED depending on paired node + permission + foreground
- Screen record (`screen_record` path): READY/BLOCKED depending on paired node + permission + foreground
- Location (`location_get`): READY/BLOCKED depending on node permission

### Contact/calendar/reminder-style entries
- Current warning indicates deny list entries in config use names that are ineffective in this runtime.
- Meaning: policy list includes command names not recognized by current command surface.
- This is a config hygiene issue, not proof of currently active callable capabilities.

## F) Known current blockers/mismatches

1. `gateway.nodes.denyCommands` contains ineffective command names in `~/.openclaw/openclaw.json`.
2. Node-dependent actions are not fully confirmable until node pairing/permissions/foreground state are validated.
3. Skill universe is larger than eligible-now subset due to prerequisites (bin/env/os/config).

## G) What this map gives us

This is the “big list” baseline:
- what exists stock,
- what is confirmed live,
- what is blocked,
- and why blocked.

We can now move line-by-line from READY/BLOCKED to CONFIRMED with explicit tests.
