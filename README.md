# Watchclaw

Watchclaw is a lightweight agent-ops watchdog for long-running assistant systems.

## Why this exists
Modern agent workflows fail in messy ways:
- compaction timeouts
- stuck sessions
- retry loops
- silent degradation in direct-message channels
- weak handoff / continuity after a reset or new session

Watchclaw focuses on one job first:
**turn messy runtime evidence into operator-readable risk summaries and handoff artifacts.**

## MVP scope
The first MVP should:
1. ingest OpenClaw logs and related evidence files
2. detect known failure patterns (timeout / compaction / handshake / session fragility)
3. classify risk level
4. generate a short operator summary
5. generate a handoff note for the next session

## Initial user
A power user or small team running OpenClaw-like agent workflows who needs reliability and continuity more than dashboards-for-show.

## Initial product shape
- local-first
- file-driven
- evidence-first
- operator-readable summaries over noisy logs

## Current status
See `STATUS.md` and `PRD.md`.
