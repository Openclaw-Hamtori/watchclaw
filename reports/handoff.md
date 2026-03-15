# Watchclaw Handoff

## Current read
- Sources scanned: 3
- Overall risk: high
- Recurring risk score: 117 (critical)
- Incident count: 36

## What the next session should know
- [high] Compaction timeout or abort detected × 1 across 1 source(s) → Reduce session bloat, inspect compaction settings, and prefer durable handoff artifacts.
- [medium] Session fragility signal detected × 2 across 1 source(s) → Treat this session as fragile; create a handoff and consider reset/new-session recovery.
- [low] A command used `python` but only `python3` may exist × 14 across 3 source(s) → Replace `python` with `python3` in scripts/cron jobs on this host.
- [low] A file-read operation targeted a missing file × 8 across 3 source(s) → Check whether the file should be created first or conditionally skipped.
- [low] An exact-text edit failed because the source content changed × 7 across 3 source(s) → Re-read the file and apply a fresh patch against current contents.

## Recommended next checks
- verify whether the top pattern is recurring or one-off
- compare incidents against recent config changes and session context growth
- copy confirmed conclusions into durable operating notes
