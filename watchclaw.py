#!/usr/bin/env python3
import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

PATTERNS = [
    {
        "id": "compaction_timeout",
        "severity": "high",
        "regex": re.compile(r"compaction.*reason=timeout|Compaction failed: Compaction timed out|compaction wait aborted", re.I),
        "summary": "Compaction timeout or abort detected",
        "next_action": "Reduce session bloat, inspect compaction settings, and prefer durable handoff artifacts.",
    },
    {
        "id": "handshake_timeout",
        "severity": "high",
        "regex": re.compile(r"handshake.*timeout|probe.*timeout|close 1000", re.I),
        "summary": "Handshake / probe timeout signal detected",
        "next_action": "Inspect gateway reachability, auth/handshake logs, and timeout semantics.",
    },
    {
        "id": "session_fragility",
        "severity": "medium",
        "regex": re.compile(r"invalid session header|polling stall|stale response|using current snapshot", re.I),
        "summary": "Session fragility signal detected",
        "next_action": "Treat this session as fragile; create a handoff and consider reset/new-session recovery.",
    },
    {
        "id": "tool_failure_python_missing",
        "severity": "low",
        "regex": re.compile(r"command not found: python", re.I),
        "summary": "A command used `python` but only `python3` may exist",
        "next_action": "Replace `python` with `python3` in scripts/cron jobs on this host.",
    },
    {
        "id": "tool_failure_rg_missing",
        "severity": "low",
        "regex": re.compile(r"command not found: rg", re.I),
        "summary": "A command expected ripgrep (`rg`) but it is unavailable",
        "next_action": "Use `grep` fallback or install `rg` if desired.",
    },
    {
        "id": "tool_failure_file_missing",
        "severity": "low",
        "regex": re.compile(r"read failed: ENOENT|no such file or directory", re.I),
        "summary": "A file-read operation targeted a missing file",
        "next_action": "Check whether the file should be created first or conditionally skipped.",
    },
    {
        "id": "tool_failure_edit_mismatch",
        "severity": "low",
        "regex": re.compile(r"edit failed: Could not find the exact text", re.I),
        "summary": "An exact-text edit failed because the source content changed",
        "next_action": "Re-read the file and apply a fresh patch against current contents.",
    },
]

SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Incident:
    pattern_id: str
    severity: str
    summary: str
    line: str
    line_no: int
    next_action: str


def compact_line(line: str, max_len: int = 220) -> str:
    text = " ".join(line.strip().split())
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def scan_file(path: Path) -> List[Incident]:
    incidents: List[Incident] = []
    try:
        lines = path.read_text(errors="ignore").splitlines()
    except Exception:
        return incidents

    for idx, line in enumerate(lines, start=1):
        for pattern in PATTERNS:
            if pattern["regex"].search(line):
                incidents.append(
                    Incident(
                        pattern_id=pattern["id"],
                        severity=pattern["severity"],
                        summary=pattern["summary"],
                        line=compact_line(line),
                        line_no=idx,
                        next_action=pattern["next_action"],
                    )
                )
                break
    return incidents


def dedupe_incidents(incidents: List[Incident]) -> List[Incident]:
    seen = set()
    deduped: List[Incident] = []
    for incident in incidents:
        fingerprint = (incident.pattern_id, incident.line)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        deduped.append(incident)
    return deduped


def overall_risk(incidents: List[Incident]) -> str:
    if any(i.severity == "high" for i in incidents):
        return "high"
    if sum(1 for i in incidents if i.severity == "medium") >= 2:
        return "medium"
    if incidents:
        return "low"
    return "none"


def top_patterns(incidents: List[Incident]) -> List[Dict[str, object]]:
    grouped: Dict[str, Dict[str, object]] = {}
    for incident in incidents:
        if incident.pattern_id not in grouped:
            grouped[incident.pattern_id] = {
                "pattern_id": incident.pattern_id,
                "severity": incident.severity,
                "summary": incident.summary,
                "count": 0,
                "firstLine": incident.line_no,
                "sample": incident.line,
                "next_action": incident.next_action,
            }
        grouped[incident.pattern_id]["count"] += 1

    items = list(grouped.values())
    items.sort(key=lambda x: (-SEVERITY_RANK[str(x["severity"])] , -int(x["count"]), int(x["firstLine"])))
    return items


def write_outputs(out_dir: Path, incidents: List[Incident], source: Path) -> None:
    incidents_dir = out_dir / "incidents"
    reports_dir = out_dir / "reports"
    incidents_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    deduped = dedupe_incidents(incidents)
    grouped = top_patterns(deduped)
    sev_counts = Counter(i.severity for i in deduped)
    risk = overall_risk(deduped)

    latest = {
        "source": str(source),
        "incidentCount": len(deduped),
        "overallRisk": risk,
        "severityBreakdown": dict(sev_counts),
        "topPatterns": grouped,
        "incidents": [asdict(i) for i in deduped],
    }
    (incidents_dir / "latest.json").write_text(json.dumps(latest, ensure_ascii=False, indent=2))

    summary_lines = [
        "# Watchclaw Operator Summary",
        "",
        f"- Source: `{source}`",
        f"- Overall risk: **{risk.upper()}**",
        f"- Incident count: **{len(deduped)}**",
        f"- Severity breakdown: `{json.dumps(dict(sev_counts), ensure_ascii=False)}`",
        "",
        "## Pattern summary",
    ]
    if not grouped:
        summary_lines.append("- No known incident patterns detected.")
    else:
        for item in grouped[:8]:
            summary_lines += [
                f"- [{item['severity']}] {item['summary']} × {item['count']} (first seen line {item['firstLine']})",
                f"  - sample: `{item['sample']}`",
                f"  - next: {item['next_action']}",
            ]

    summary_lines += [
        "",
        "## Operator read",
    ]
    if risk == "high":
        summary_lines.append("- High-severity runtime risk was detected. Treat the current workflow as potentially fragile until verified.")
    elif risk == "medium":
        summary_lines.append("- No immediate critical signal, but multiple medium-grade issues suggest the workflow needs review.")
    elif risk == "low":
        summary_lines.append("- Only lower-grade issues were found; likely operational friction more than system instability.")
    else:
        summary_lines.append("- No known incident signatures were detected in this scan.")

    (reports_dir / "operator-summary.md").write_text("\n".join(summary_lines) + "\n")

    handoff_lines = [
        "# Watchclaw Handoff",
        "",
        "## Current read",
        f"- Parsed log: `{source}`",
        f"- Overall risk: {risk}",
        f"- Incident count: {len(deduped)}",
        "",
        "## What the next session should know",
    ]
    if not grouped:
        handoff_lines.append("- No known incident patterns detected in this scan.")
    else:
        for item in grouped[:5]:
            handoff_lines.append(
                f"- [{item['severity']}] {item['summary']} × {item['count']} → {item['next_action']}"
            )

    handoff_lines += [
        "",
        "## Recommended next checks",
        "- verify whether the top pattern is recurring or one-off",
        "- compare incidents against recent config changes and session context growth",
        "- copy confirmed conclusions into durable operating notes",
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
    print(json.dumps({"ok": True, "incidents": len(dedupe_incidents(incidents)), "source": str(log_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
