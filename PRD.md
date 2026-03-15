# Watchclaw PRD v0.1

## 1. Problem
Agent operators often notice failure too late. The raw logs exist, but they are too noisy and too scattered to quickly answer:
- what failed?
- how bad is it?
- is this recurring?
- what should I do next?
- what must the next session know?

## 2. Target user
- solo power users running OpenClaw or similar agent systems
- small teams operating long-running assistant workflows
- people who care about continuity, operator trust, and failure triage

## 3. MVP goals
- parse recent OpenClaw log files
- detect a small set of concrete failure signatures
- emit:
  - machine-readable structured incidents
  - human-readable operator summary
  - handoff note for next session

## 4. Non-goals (for MVP)
- multi-tenant cloud dashboard
- deep analytics warehouse
- fancy auth system
- broad provider integrations

## 5. Key signals to detect
- manual/auto compaction timeout
- session stuck / session fragility hints
- auth / handshake timeout hints
- repeated tool failures
- oversized-context risk hints

## 6. MVP outputs
1. `incidents/latest.json`
2. `reports/operator-summary.md`
3. `reports/handoff.md`

## 7. Product edge
Watchclaw is not trying to be generic observability. It is an operator-focused reliability lens for agent workflows.

## 8. Success criteria
- can scan a local log and extract meaningful incidents
- can produce a compact operator-readable summary
- can produce a usable next-session handoff artifact
- useful on the real OpenClaw logs already on this machine

## 9. Immediate build plan
1. build a local CLI in Python
2. add pattern detection for the current OpenClaw failure family
3. generate reports from real logs
4. iterate on signal quality
