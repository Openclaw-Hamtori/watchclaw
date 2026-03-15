# Watchclaw Usage

## Single log
```bash
python3 watchclaw.py --log /tmp/openclaw/openclaw-2026-03-15.log --out .
```

## Latest 3 logs from a directory
```bash
python3 watchclaw.py --log-dir /tmp/openclaw --latest 3 --out .
```

## Lower-noise scan
```bash
python3 watchclaw.py --log-dir /tmp/openclaw --latest 3 --out . --suppress-low-noise --min-severity low
```

## Config file
```bash
mkdir -p ~/.config/watchclaw
cp config.example.json ~/.config/watchclaw/config.json
python3 watchclaw.py
```

## Outputs
- `incidents/latest.json`
- `reports/operator-summary.md`
- `reports/handoff.md`
- `exports/durable-note.md`

## Current best use
Use Watchclaw after:
- suspicious OpenClaw runtime failures
- compaction failures
- gateway/session instability
- before starting a fresh session when you want a durable handoff artifact
