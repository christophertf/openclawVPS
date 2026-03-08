# Long-Term Memory (Curated Context)

## User Profile (Chris)
- **Preferences:** Concise responses, 24-hour time, Celsius, factual sequencing. 
- **Rule of Thumb:** "If it ain't broke, don't fix it" — non-intervention when things work.
- **Permissions:** CLAW is explicitly authorized to spawn helper sub-agents when beneficial for throughput or quality (confirmed 2026-02-26).
- **Environment Context:** Desktop runs Ubuntu 24.04.3 LTS, i9-13900KF, 32GB RAM, RTX 4070 SUPER.

## Architecture Context (OpenClaw)
- **Session Strategy:** Discord channels are used effectively as separate workstreams/contexts (e.g. `#case-research`, `#ops`). The Telegram DM operates as the primary control plane.
- **Workspace State:** A major normalization occurred on 2026-03-05 to fix git drift, implement this `MEMORY.md` file, and activate heartbeats.

## Active Projects & Workstreams

### 1) Housing Code & Case Research
- **Recent Findings (2026-03-01):** Extensively searched portals for **1018 Open Housing** cases concerning rule families B59/B31. Identified 461 matches.
- **Key Outlier:** Every other case found *always* has comments or text. Chris's case is the only one inexplicably missing any descriptive notes. That lane is exhausted.
- **Current Objective/Next Steps:** Proceeding with automated probing on alternative sources (e.g., Accela SAC, County CitizenAccess). A base reference pool of 1176 records (open_vacant) is staged at `CASE_FILES/research/case_crawler/output/casefile_reference_pool_open_vacant.csv`.

### 2) Appeal Alignment 
- **Domain:** Project directory at `projects/appeal_alignment/`.
- **Status:** Analyzing meeting transcripts, agendas, and alignment checks across late 2024 to late 2025. Automated scripts (e.g., `align_with_llm.py` and `hearing_align.py`) are staged in the `scripts/` folder.

---
*Note to CLAW: Update this file periodically via Heartbeat routines. Do not let "mental notes" replace permanent file storage.*
