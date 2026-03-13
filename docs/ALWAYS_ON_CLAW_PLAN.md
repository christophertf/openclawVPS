# ALWAYS-ON CLAW PLAN (v1)

Updated: 2026-03-12 UTC
Owner: Claw

## Goal
Run CLAW as a proactive VPS operator: continuous ingest, research, validation, and reporting with explicit blocker escalation.

## Model Routing Policy
- Default ops + housekeeping: `openai-codex/gpt-5.3-codex`
- Legal deep analysis lane: `grok-legal` (OpenRouter)
- Low-cost extraction lane: `router-cheap` (OpenRouter)
- Cross-check lane: `router-verify` (OpenRouter)

## Phase 1 (start now)
1. Create durable state + run logs
2. Stand up scheduler skeleton (non-destructive)
3. Add daily digests + blocker alerts
4. Track KPIs in a machine-readable file

## Phase 2
1. Delta ingest on case sources
2. Hypothesis generation + novelty ranking
3. Validation matrix updates + contradiction detection

## Phase 3
1. Weekly self-tuning reports
2. Prompt/routing A/B checks
3. Promote successful tuning rules

## Guardrails
- No destructive actions without explicit approval
- Evidence-first outputs
- Cost/budget-aware routing
- Always escalate blockers when self-fix fails
