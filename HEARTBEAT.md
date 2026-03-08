# HEARTBEAT.md

CLAW: During a heartbeat event, perform the following background checks. 

1. **Memory Maintenance (Crucial):** Read any recent `memory/YYYY-MM-DD.md` files (from the last 1-3 days). If there are significant decisions, system findings, new preferences, or major project milestones, **distill them into `MEMORY.md`**.
2. **Profile Review (Daily):** Check `USER.md`, `IDENTITY.md`, and `SOUL.md`. If you've learned anything new about the human (preferences, timezone, context, projects) or about yourself (working style, personality), **update the relevant file**. These files are how you know who you're working with and who you are — stale profiles = blind sessions.
3. **Pipeline Monitoring:** Check if the case pipeline has generated any new status errors or requires attention. Just a brief glance.
4. **Change Feed:** Append a one-liner to `memory/change-feed.log` if you made any updates during this heartbeat.
5. **No Hallucinations:** If nothing has happened and everything is stable, do NOT invent tasks. Simply reply `HEARTBEAT_OK`.

*Keep updates concise to limit token burn.*
