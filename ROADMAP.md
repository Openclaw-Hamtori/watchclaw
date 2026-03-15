# Watchclaw Roadmap

## Product direction
Watchclaw should start as a **local-first operator tool** for OpenClaw and similar agent runtimes.

## Why this deployment path
For the first release, the best deployment surface is not a public SaaS yet.
The highest-leverage path is:
1. local CLI
2. optional lightweight local web UI
3. packaged GitHub repo for install/use by advanced operators

Reason:
- fastest path to real utility
- avoids premature cloud/auth complexity
- matches the current evidence-first workflow
- lets us validate recurring pain with minimal cost

## Deployment plan
### Phase 1 — local operator tool
- Python CLI
- scans one or more logs
- generates JSON + markdown reports
- install/run from repo

### Phase 2 — local dashboard
- tiny local web UI or static report viewer
- timeline view across recent logs
- recurring-pattern highlights
- copy/export handoff artifact

### Phase 3 — hosted/team mode (only if warranted)
- hosted ingestion endpoint
- team dashboard
- issue/webhook integrations
- multi-runtime support

## Likely first deployment target
- **GitHub repo + local execution**
- optionally packaged later as:
  - Homebrew tap
  - pipx-installable CLI
  - small local desktop/web wrapper

## Decision
Do not rush to hosted SaaS deployment before proving local operator value.
GitHub-distributed local tool is the correct first deployment target.
