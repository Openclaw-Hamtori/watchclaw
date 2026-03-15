#!/usr/bin/env python3
import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

PATTERNS = [
    {
        "id": "compaction_timeout",
        "severity": "high",
        "regex": re.compile(r"compaction.*reason=timeout|Compaction failed: Compaction timed out|compaction wait aborted", re.I),
        "summary": "Compaction timeout or abort detected",
    },
    {
        "id": "handshake_timeout",
        "severity": "high",
        "regex": re.compile(r"handshake.*timeout|probe.*timeout|close 1000", re.I),
        "summary": "Handshake / probe timeout signal detected",
    },
    {
        "id": "session_fragility",
        "severity": "medium",
        "regex": re.compile(r"invalid session header|polling stall|stale response|using current snapshot", re.I),
        "summary": "Session fragility signal detected",
    },
    {
        "id": "tool_failure",
        "severity": "medium",
        "regex": re.compile(r"error \[tools\]|exec failed:|edit failed:|read failed:", re.I),
        "summary": "Tool failure detected",
    },
]

@dataclass
class Incident:
    pattern_id: str
    severity: str
    summary: str
    line: str
    line_no: int


def scan_file(path: Path) -> List[Incident]:
    incidents: List[Incident] = []
    try:
        lines = path.read_text(errors="ignore").splitlines()
    except Exception:
        return incidents
    for idx, line in enumerate(lines, start=1):
        for pattern in PATTERNS:
            if pattern["regex"].search(line):
                incidents.append(Incident(
                    pattern_id=pattern["id"],
                    severity=pattern["severity"],
                    summary=pattern["summary"],
                    line=line.strip(),
                    line_no=idx,
                ))
    return incidents


def write_outputs(out_dir: Path, incidents: List[Incident], source: Path) -> None:
    incidents_dir = out_dir / "incidents"
    reports_dir = out_dir / "reports"
    incidents_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    latest = {
        "source": str(source),
        "incidentCount": len(incidents),
        "incidents": [asdict(i) for i in incidents],
    }
    (incidents_dir / "latest.json").write_text(json.dumps(latest, ensure_ascii=False, indent=2))

    by_severity = {}
    for incident in incidents:
        by_severity.setdefault(incident.severity, 0)
        by_severity[incident.severity] += 1

    summary_lines = [
        "# Watchclaw Operator Summary",
        "",
        f"- Source: `{source}`",
        f"- Incident count: **{len(incidents)}**",
        f"- Severity breakdown: `{json.dumps(by_severity, ensure_ascii=False)}`",
        "",
        "## Top incidents",
    ]
    for incident in incidents[:10]:
        summary_lines += [
            f"- [{incident.severity}] {incident.summary} (line {incident.line_no})",
            f"  - `{incident.line}`",
        ]
    (reports_dir / "operator-summary.md").write_text("\n".join(summary_lines) + "\n")

    handoff_lines = [
        "# Watchclaw Handoff",
        "",
        "## Current read",
        f"- Parsed log: `{source}`",
        f"- Incident count: {len(incidents)}",
        "",
        "## What the next session should know",
    ]
    if not incidents:
        handoff_lines.append("- No known incident patterns detected in this scan.")
    else:
        top = incidents[:5]
        for incident in top:
            handoff_lines.append(f"- {incident.summary}: line {incident.line_no}")
    handoff_lines += [
        "",
        "## Recommended next checks",
        "- confirm whether these incidents are recurring or one-off",
        "- compare against session state and recent config changes",
        "- save any confirmed diagnosis into durable notes",
    ]
    (reports_dir / "handoff.md").write_text("\n".join(handoff_lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Watchclaw log scanner")
    parser.add_argument("scan", nargs="?", default="scan")
    parser.add_argument("--log", required=True, help="Path to OpenClaw log file")
    parser.add_argument("--out", default=".", help="Output directory")
    args = parser.parse_args()

    log_path = Path(args.log).expanduser()
    out_dir = Path(args.out).expanduser()
    incidents = scan_file(log_path)
    write_outputs(out_dir, incidents, log_path)
    print(json.dumps({"ok": True, "incidents": len(incidents), "source": str(log_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
