#!/usr/bin/env bash
set -euo pipefail
python3 watchclaw.py --log-dir /tmp/openclaw --latest 3 --out . --suppress-low-noise
printf '\nGenerated:\n'
printf ' - reports/operator-summary.md\n'
printf ' - reports/handoff.md\n'
printf ' - reports/dashboard.html\n'
printf ' - exports/durable-note.md\n'
