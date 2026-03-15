# Watchclaw Operator Summary

- Sources scanned: **3**
- Overall risk: **HIGH**
- Recurring risk score: **117** (`critical`)
- Incident count: **36**
- Severity breakdown: `{"low": 33, "medium": 2, "high": 1}`

## Source summary
- `/tmp/openclaw/openclaw-2026-03-12.log` → 20 incidents / {'low': 18, 'medium': 2}
- `/tmp/openclaw/openclaw-2026-03-14.log` → 8 incidents / {'low': 8}
- `/tmp/openclaw/openclaw-2026-03-15.log` → 8 incidents / {'low': 7, 'high': 1}

## Pattern summary
- [high] Compaction timeout or abort detected × 1 across 1 source(s)
  - sample: `{"0":"{\"subsystem\":\"agent/embedded\"}","1":"[compaction-diag] end runId=2a2145fd-0019-4b04-ba1b-57a12c38052b sessionKey=agent:main:telegram:direct:1629239187 diagId=cmp-mmr84zvo-RSOUrA trigger=manual provider=opena...`
  - next: Reduce session bloat, inspect compaction settings, and prefer durable handoff artifacts.
- [medium] Session fragility signal detected × 2 across 1 source(s)
  - sample: `{"0":"{\"subsystem\":\"gateway/channels/telegram\"}","1":"[telegram] Polling stall detected (no getUpdates for 105.86s); forcing restart.","_meta":{"runtime":"node","runtimeVersion":"25.8.0","hostname":"unknown","name...`
  - next: Treat this session as fragile; create a handoff and consider reset/new-session recovery.
- [low] A command used `python` but only `python3` may exist × 14 across 3 source(s)
  - sample: `{"0":"[tools] exec failed: zsh:1: command not found: python\n\nCommand not found","_meta":{"runtime":"node","runtimeVersion":"25.8.0","hostname":"unknown","name":"openclaw","date":"2026-03-12T00:00:36.929Z","logLevelI...`
  - next: Replace `python` with `python3` in scripts/cron jobs on this host.
- [low] A file-read operation targeted a missing file × 8 across 3 source(s)
  - sample: `{"0":"[tools] read failed: ENOENT: no such file or directory, access '/Users/chaesung/.openclaw/workspace/memory/2026-03-12.md'","_meta":{"runtime":"node","runtimeVersion":"25.8.0","hostname":"unknown","name":"opencla...`
  - next: Check whether the file should be created first or conditionally skipped.
- [low] An exact-text edit failed because the source content changed × 7 across 3 source(s)
  - sample: `{"0":"[tools] edit failed: Could not find the exact text in /Users/chaesung/Desktop/Presence_GPT/presence-test-app/ios/PresenceTestApp.xcodeproj/project.pbxproj. The old text must match exactly including all whitespac...`
  - next: Re-read the file and apply a fresh patch against current contents.
- [low] A command expected ripgrep (`rg`) but it is unavailable × 4 across 3 source(s)
  - sample: `{"0":"[tools] exec failed: zsh:1: command not found: rg\n\nCommand not found","_meta":{"runtime":"node","runtimeVersion":"25.8.0","hostname":"unknown","name":"openclaw","date":"2026-03-13T07:06:41.715Z","logLevelId":5...`
  - next: Use `grep` fallback or install `rg` if desired.

## Operator read
- High-severity runtime risk was detected. Treat the current workflow as potentially fragile until verified.
- This looks recurring enough to deserve durable notes and a concrete mitigation plan, not just ad-hoc observation.
