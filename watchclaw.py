#!/usr/bin/env python3
import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

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
SCORE_PER_SEVERITY = {"low": 1, "medium": 4, "high": 10}


@dataclass
class Incident:
    source: str
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
                        source=str(path),
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
        fingerprint = (incident.source, incident.pattern_id, incident.line)
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


def recurring_risk_score(incidents: List[Incident]) -> Dict[str, object]:
    if not incidents:
        return {"score": 0, "band": "none"}

    score = 0
    patterns = Counter(i.pattern_id for i in incidents)
    source_counts = Counter(i.source for i in incidents)
    unique_sources = len(source_counts)

    for incident in incidents:
        score += SCORE_PER_SEVERITY[incident.severity]
    for pattern_id, count in patterns.items():
        if count > 1:
            score += (count - 1) * 2
    if unique_sources > 1:
        score += (unique_sources - 1) * 3

    if score >= 40:
        band = "critical"
    elif score >= 20:
        band = "high"
    elif score >= 8:
        band = "medium"
    else:
        band = "low"
    return {"score": score, "band": band}


def top_patterns(incidents: List[Incident]) -> List[Dict[str, object]]:
    grouped: Dict[str, Dict[str, object]] = {}
    for incident in incidents:
        if incident.pattern_id not in grouped:
            grouped[incident.pattern_id] = {
                "pattern_id": incident.pattern_id,
                "severity": incident.severity,
                "summary": incident.summary,
                "count": 0,
                "sources": set(),
                "firstLine": incident.line_no,
                "sample": incident.line,
                "next_action": incident.next_action,
            }
        grouped[incident.pattern_id]["count"] += 1
        grouped[incident.pattern_id]["sources"].add(incident.source)

    items = list(grouped.values())
    for item in items:
        item["sourceCount"] = len(item["sources"])
        item["sources"] = sorted(item["sources"])

    items.sort(key=lambda x: (-SEVERITY_RANK[str(x["severity"])] , -int(x["count"]), -int(x["sourceCount"]), int(x["firstLine"])))
    return items


def source_summary(incidents: List[Incident]) -> List[Dict[str, object]]:
    grouped: Dict[str, Counter] = {}
    for incident in incidents:
        grouped.setdefault(incident.source, Counter())
        grouped[incident.source][incident.severity] += 1
    rows = []
    for source, counter in sorted(grouped.items()):
        rows.append({
            "source": source,
            "incidentCount": sum(counter.values()),
            "severityBreakdown": dict(counter),
        })
    return rows


def write_outputs(out_dir: Path, incidents: List[Incident], sources: List[Path]) -> None:
    incidents_dir = out_dir / "incidents"
    reports_dir = out_dir / "reports"
    exports_dir = out_dir / "exports"
    incidents_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    exports_dir.mkdir(parents=True, exist_ok=True)

    deduped = dedupe_incidents(incidents)
    grouped = top_patterns(deduped)
    sev_counts = Counter(i.severity for i in deduped)
    risk = overall_risk(deduped)
    recurring = recurring_risk_score(deduped)
    source_rows = source_summary(deduped)

    latest = {
        "sources": [str(s) for s in sources],
        "incidentCount": len(deduped),
        "overallRisk": risk,
        "recurringRisk": recurring,
        "severityBreakdown": dict(sev_counts),
        "sourceSummary": source_rows,
        "topPatterns": grouped,
        "incidents": [asdict(i) for i in deduped],
    }
    (incidents_dir / "latest.json").write_text(json.dumps(latest, ensure_ascii=False, indent=2))

    summary_lines = [
        "# Watchclaw Operator Summary",
        "",
        f"- Sources scanned: **{len(sources)}**",
        f"- Overall risk: **{risk.upper()}**",
        f"- Recurring risk score: **{recurring['score']}** (`{recurring['band']}`)",
        f"- Incident count: **{len(deduped)}**",
        f"- Severity breakdown: `{json.dumps(dict(sev_counts), ensure_ascii=False)}`",
        "",
        "## Source summary",
    ]
    if source_rows:
        for row in source_rows:
            summary_lines.append(f"- `{row['source']}` → {row['incidentCount']} incidents / {row['severityBreakdown']}")
    else:
        summary_lines.append("- No source incidents detected.")

    summary_lines += ["", "## Pattern summary"]
    if not grouped:
        summary_lines.append("- No known incident patterns detected.")
    else:
        for item in grouped[:8]:
            summary_lines += [
                f"- [{item['severity']}] {item['summary']} × {item['count']} across {item['sourceCount']} source(s)",
                f"  - sample: `{item['sample']}`",
                f"  - next: {item['next_action']}",
            ]

    summary_lines += ["", "## Operator read"]
    if risk == "high":
        summary_lines.append("- High-severity runtime risk was detected. Treat the current workflow as potentially fragile until verified.")
    elif risk == "medium":
        summary_lines.append("- No immediate critical signal, but multiple medium-grade issues suggest the workflow needs review.")
    elif risk == "low":
        summary_lines.append("- Only lower-grade issues were found; likely operational friction more than system instability.")
    else:
        summary_lines.append("- No known incident signatures were detected in this scan.")
    if recurring["band"] in {"high", "critical"}:
        summary_lines.append("- This looks recurring enough to deserve durable notes and a concrete mitigation plan, not just ad-hoc observation.")

    (reports_dir / "operator-summary.md").write_text("\n".join(summary_lines) + "\n")

    handoff_lines = [
        "# Watchclaw Handoff",
        "",
        "## Current read",
        f"- Sources scanned: {len(sources)}",
        f"- Overall risk: {risk}",
        f"- Recurring risk score: {recurring['score']} ({recurring['band']})",
        f"- Incident count: {len(deduped)}",
        "",
        "## What the next session should know",
    ]
    if not grouped:
        handoff_lines.append("- No known incident patterns detected in this scan.")
    else:
        for item in grouped[:5]:
            handoff_lines.append(
                f"- [{item['severity']}] {item['summary']} × {item['count']} across {item['sourceCount']} source(s) → {item['next_action']}"
            )

    handoff_lines += [
        "",
        "## Recommended next checks",
        "- verify whether the top pattern is recurring or one-off",
        "- compare incidents against recent config changes and session context growth",
        "- copy confirmed conclusions into durable operating notes",
    ]
    (reports_dir / "handoff.md").write_text("\n".join(handoff_lines) + "\n")

    durable_lines = [
        "# Durable Note Export",
        "",
        f"Date basis: {', '.join(str(s) for s in sources)}",
        f"Overall risk: {risk}",
        f"Recurring risk score: {recurring['score']} ({recurring['band']})",
        "",
        "## Suggested durable note",
    ]
    if grouped:
        for item in grouped[:5]:
            durable_lines.append(
                f"- {item['summary']} recurred {item['count']} time(s) across {item['sourceCount']} source(s). Next action: {item['next_action']}"
            )
    else:
        durable_lines.append("- No durable incidents suggested from this scan.")
    durable_lines += [
        "",
        "## Why it matters",
        "- Use this block when a pattern is no longer a one-off and should be promoted into durable operating memory.",
    ]
    (exports_dir / "durable-note.md").write_text("\n".join(durable_lines) + "\n")


def resolve_sources(log: str = "", log_dir: str = "", latest: int = 0) -> List[Path]:
    if log:
        return [Path(log).expanduser()]
    if log_dir:
        base = Path(log_dir).expanduser()
        files = sorted(base.glob("openclaw-*.log"))
        return files[-latest:] if latest > 0 else files
    return []


def main():
    parser = argparse.ArgumentParser(description="Watchclaw log scanner")
    parser.add_argument("scan", nargs="?", default="scan")
    parser.add_argument("--log", help="Path to a single OpenClaw log file")
    parser.add_argument("--log-dir", help="Directory containing OpenClaw log files")
    parser.add_argument("--latest", type=int, default=0, help="When using --log-dir, scan only the latest N logs")
    parser.add_argument("--out", default=".", help="Output directory")
    args = parser.parse_args()

    sources = resolve_sources(args.log or "", args.log_dir or "", args.latest)
    if not sources:
        raise SystemExit("No log sources found. Use --log or --log-dir.")

    out_dir = Path(args.out).expanduser()
    incidents: List[Incident] = []
    for source in sources:
        incidents.extend(scan_file(source))

    write_outputs(out_dir, incidents, sources)
    print(json.dumps({"ok": True, "sources": len(sources), "incidents": len(dedupe_incidents(incidents))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
