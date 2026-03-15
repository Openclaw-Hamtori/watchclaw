# Watchclaw

Watchclaw is a local-first agent-ops watchdog for long-running assistant systems.

It turns messy runtime evidence into:
- operator-readable risk summaries
- next-session handoff artifacts
- durable-note exports
- a lightweight HTML dashboard

## Why this exists
Modern agent workflows fail in messy ways:
- compaction timeouts
- stuck or fragile sessions
- handshake/probe problems
- repeated tool/runtime friction
- weak continuity after resets or new sessions

Watchclaw focuses on one job first:
**convert scattered runtime evidence into something an operator can actually use.**

## Current capability
- single-log scan
- multi-log scan
- recurring-risk score
- operator summary (`reports/operator-summary.md`)
- handoff artifact (`reports/handoff.md`)
- durable note export (`exports/durable-note.md`)
- lightweight HTML dashboard (`reports/dashboard.html`)
- config-based execution

## Quick start
```bash
git clone https://github.com/Openclaw-Hamtori/watchclaw.git
cd watchclaw
python3 watchclaw.py --log-dir /tmp/openclaw --latest 3 --out .
```

For a lower-noise run:
```bash
python3 watchclaw.py --log-dir /tmp/openclaw --latest 3 --out . --suppress-low-noise
```

## Outputs
- `incidents/latest.json`
- `reports/operator-summary.md`
- `reports/handoff.md`
- `reports/dashboard.html`
- `exports/durable-note.md`

## Initial user
A power user or small team running OpenClaw-like agent workflows who needs reliability and continuity more than dashboards-for-show.

## Product direction
Watchclaw starts as a **GitHub-distributed local tool**.
If it proves real operator value, it can later become:
- a pipx/Homebrew-installable CLI
- a lightweight local dashboard app
- eventually a hosted/team tool

## Status
See:
- `STATUS.md`
- `PRD.md`
- `ROADMAP.md`
- `RELEASE-CHECKLIST.md`
