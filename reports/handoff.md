# Watchclaw Handoff

## Current read
- Parsed log: `/tmp/openclaw/openclaw-2026-03-15.log`
- Overall risk: high
- Incident count: 7

## What the next session should know
- [high] Compaction timeout or abort detected × 1 → Reduce session bloat, inspect compaction settings, and prefer durable handoff artifacts.
- [low] A command used `python` but only `python3` may exist × 3 → Replace `python` with `python3` in scripts/cron jobs on this host.
- [low] A file-read operation targeted a missing file × 1 → Check whether the file should be created first or conditionally skipped.
- [low] An exact-text edit failed because the source content changed × 1 → Re-read the file and apply a fresh patch against current contents.
- [low] A command expected ripgrep (`rg`) but it is unavailable × 1 → Use `grep` fallback or install `rg` if desired.

## Recommended next checks
- verify whether the top pattern is recurring or one-off
- compare incidents against recent config changes and session context growth
- copy confirmed conclusions into durable operating notes
