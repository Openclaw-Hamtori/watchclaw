# Watchclaw STATUS

## What it is
Lightweight agent-ops watchdog for log-based failure detection, operator summaries, and handoff artifacts.

## Current state
- project initialized
- git repo initialized
- README + PRD written
- next step: build first local CLI against real OpenClaw logs

## Main risks
- overbuilding dashboard before proving core signal value
- generic observability drift
- poor classification quality on noisy logs

## Next 3 actions
1. build `watchclaw.py`
2. test against `/tmp/openclaw/openclaw-2026-03-15.log`
3. review outputs and tighten incident heuristics
