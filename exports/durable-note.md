# Durable Note Export

Date basis: /tmp/openclaw/openclaw-2026-03-12.log, /tmp/openclaw/openclaw-2026-03-14.log, /tmp/openclaw/openclaw-2026-03-15.log
Overall risk: high
Recurring risk score: 117 (critical)
Filters: minSeverity=low, suppressLowNoise=true

## Suggested durable note
- Compaction timeout or abort detected recurred 1 time(s) across 1 source(s). Next action: Reduce session bloat, inspect compaction settings, and prefer durable handoff artifacts.
- Session fragility signal detected recurred 2 time(s) across 1 source(s). Next action: Treat this session as fragile; create a handoff and consider reset/new-session recovery.
- A command used `python` but only `python3` may exist recurred 14 time(s) across 3 source(s). Next action: Replace `python` with `python3` in scripts/cron jobs on this host.
- A file-read operation targeted a missing file recurred 8 time(s) across 3 source(s). Next action: Check whether the file should be created first or conditionally skipped.
- An exact-text edit failed because the source content changed recurred 7 time(s) across 3 source(s). Next action: Re-read the file and apply a fresh patch against current contents.

## Why it matters
- Use this block when a pattern is no longer a one-off and should be promoted into durable operating memory.
