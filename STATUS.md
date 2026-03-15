# Watchclaw STATUS

## What it is
Lightweight agent-ops watchdog for log-based failure detection, operator summaries, and handoff artifacts.

## Current state
- project initialized on Desktop in its own git repo
- README / PRD / STATUS / roadmap docs created
- local CLI built and tested against real OpenClaw logs
- single-log and multi-log scan modes working
- operator summary and handoff outputs improved beyond raw error listing
- deployment direction fixed: GitHub-distributed local tool first, hosted/team mode later only if justified

## What is working
- scans one OpenClaw log or latest N logs from a directory
- emits:
  - `incidents/latest.json`
  - `reports/operator-summary.md`
  - `reports/handoff.md`
- detected real issues in local logs including compaction timeout and session fragility

## Main risks
- overbuilding dashboard before proving core signal value
- generic observability drift
- poor classification quality on noisy logs
- current heuristics still overweight some low-signal tool failures

## Next 3 actions
1. add recurring-risk score across multiple logs
2. reduce low-signal noise and sharpen known OpenClaw issue families
3. prepare remote repo publishing path and lightweight packaging direction
