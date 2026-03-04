#!/usr/bin/env python3
"""
OpenClaw Log Query Tool

Parses OpenClaw gateway logs (both plain-text and structured JSON) and outputs
a clean, noise-filtered timeline for a given time window.

Usage:
    python query_logs.py --from "19:20" --to "20:00" [--date 2026-03-04] [--log-dir ~/.openclaw/logs] [--verbose]
    python query_logs.py --from "2026-03-04 19:20" --to "2026-03-04 20:00"
    python query_logs.py --last 30m
    python query_logs.py --last 2h

Time can be:
  - HH:MM           → today, Beijing time
  - YYYY-MM-DD HH:MM → specific date, Beijing time
  - --last Nm/Nh    → last N minutes/hours from now
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BJT = timezone(timedelta(hours=8))
UTC = timezone.utc

# Noise patterns to filter out (substrings in the message)
NOISE_PATTERNS = [
    "cron: timer armed",
    "cron: started",  # keep only if verbose
]

# Category colors/labels for grouping
CATEGORIES = {
    "error":    ("ERROR",    ["isError=true", "error=", "failed", "FAILED", "rate limit", "UNAVAILABLE"]),
    "restart":  ("RESTART",  ["SIGTERM", "SIGUSR1", "restart", "shutting down", "drain timeout", "falling back"]),
    "plugin":   ("PLUGIN",   ["plugin", "Downloading", "Installing", "Extracting", "camofox", "acpx"]),
    "telegram": ("TELEGRAM", ["telegram", "sendMessage"]),
    "acp":      ("ACP",      ["acp", "identity reconcile"]),
    "config":   ("CONFIG",   ["config change", "Config overwrite", "reload", "Migrated", "Updating provider"]),
    "ws":       ("WS",       ["webchat", "⇄ res"]),
    "health":   ("HEALTH",   ["health-monitor"]),
    "cron":     ("CRON",     ["cron"]),
    "agent":    ("AGENT",    ["agent", "embedded run"]),
    "gateway":  ("GATEWAY",  ["listening on", "agent model", "log file", "canvas host", "heartbeat", "browser/server", "Browser control", "bonjour"]),
}


def categorize(msg: str) -> str:
    msg_lower = msg.lower()
    for cat, (_, keywords) in CATEGORIES.items():
        for kw in keywords:
            if kw.lower() in msg_lower:
                return cat
    return "other"


def parse_time_arg(s: str, default_date: str | None = None) -> datetime:
    """Parse a time argument into a Beijing-time datetime."""
    s = s.strip()
    # Full datetime
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.replace(tzinfo=BJT)
        except ValueError:
            continue
    # Time only
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            t = datetime.strptime(s, fmt).time()
            date_str = default_date or datetime.now(BJT).strftime("%Y-%m-%d")
            dt = datetime.strptime(f"{date_str} {t.strftime('%H:%M:%S')}", "%Y-%m-%d %H:%M:%S")
            return dt.replace(tzinfo=BJT)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse time: {s}")


def parse_last_arg(s: str) -> tuple[datetime, datetime]:
    """Parse --last Nm or Nh into (from, to) datetimes."""
    m = re.match(r"(\d+)\s*(m|min|h|hr|hour)s?$", s.strip(), re.IGNORECASE)
    if not m:
        raise ValueError(f"Cannot parse --last: {s}. Use e.g. 30m or 2h")
    val = int(m.group(1))
    unit = m.group(2).lower()
    if unit.startswith("h"):
        delta = timedelta(hours=val)
    else:
        delta = timedelta(minutes=val)
    now = datetime.now(BJT)
    return (now - delta, now)


def parse_log_timestamp(line: str) -> datetime | None:
    """Extract timestamp from a plain-text log line."""
    # Format: 2026-03-04T11:37:50.845+08:00 or 2026-03-04T11:37:50.845Z
    m = re.match(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\.?\d*([+-]\d{2}:\d{2}|Z)", line)
    if not m:
        return None
    ts_str = m.group(1)
    tz_str = m.group(2)
    dt = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")
    if tz_str == "Z":
        dt = dt.replace(tzinfo=UTC)
    else:
        sign = 1 if tz_str[0] == "+" else -1
        hours, mins = int(tz_str[1:3]), int(tz_str[4:6])
        dt = dt.replace(tzinfo=timezone(timedelta(hours=sign * hours, minutes=sign * mins)))
    return dt.astimezone(BJT)


def parse_json_log_timestamp(obj: dict) -> datetime | None:
    """Extract timestamp from a structured JSON log entry."""
    ts_str = obj.get("_meta", {}).get("date", "")
    if not ts_str:
        return None
    # Always UTC in JSON logs
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            dt = datetime.strptime(ts_str, fmt).replace(tzinfo=UTC)
            return dt.astimezone(BJT)
        except ValueError:
            continue
    return None


def extract_message_plain(line: str) -> tuple[str, str]:
    """Extract subsystem and message from plain-text log line."""
    # Remove timestamp prefix
    rest = re.sub(r"^\d{4}-\d{2}-\d{2}T[\d:.]+[+-Z][\d:]*\s*", "", line).strip()
    # Extract [subsystem] prefix
    m = re.match(r"\[([^\]]+)\]\s*(.*)", rest)
    if m:
        return m.group(1), m.group(2)
    return "", rest


def extract_message_json(obj: dict) -> tuple[str, str]:
    """Extract subsystem and message from structured JSON log entry."""
    # Get subsystem from _meta.name
    name = obj.get("_meta", {}).get("name", "")
    subsys = ""
    if "subsystem" in name:
        try:
            subsys = json.loads(name).get("subsystem", name)
        except (json.JSONDecodeError, TypeError):
            subsys = name
    else:
        subsys = name

    # Get message from field "1" or "0"
    msg = obj.get("1", obj.get("0", ""))
    if isinstance(msg, dict):
        msg = json.dumps(msg, ensure_ascii=False)
    msg = str(msg)

    # If field "2" exists and is a string, it might be the actual message
    field2 = obj.get("2", "")
    if isinstance(field2, str) and field2 and not isinstance(obj.get("1"), str):
        msg = field2

    return subsys[:40], msg[:300]


def is_noise(msg: str, verbose: bool) -> bool:
    """Check if a message is noise that should be filtered."""
    for pattern in NOISE_PATTERNS:
        if pattern in msg:
            return not verbose
    return False


def query_plain_logs(log_path: Path, t_from: datetime, t_to: datetime, verbose: bool) -> list[dict]:
    """Parse a plain-text log file and return matching entries."""
    results = []
    if not log_path.exists():
        return results

    # Also handle multi-line entries (like Doctor warnings box)
    current_entry = None
    with open(log_path, "r", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            ts = parse_log_timestamp(line)
            if ts:
                # Flush previous entry
                if current_entry and t_from <= current_entry["ts"] <= t_to:
                    if not is_noise(current_entry["msg"], verbose):
                        results.append(current_entry)
                subsys, msg = extract_message_plain(line)
                current_entry = {"ts": ts, "subsys": subsys, "msg": msg}
            elif current_entry and (line.startswith("│") or line.startswith("├") or line.startswith("◇") or line.startswith("┌")):
                # Multi-line continuation (box drawing)
                current_entry["msg"] += " " + line.strip("│├◇┌┐─╮╯ ")

        # Flush last entry
        if current_entry and t_from <= current_entry["ts"] <= t_to:
            if not is_noise(current_entry["msg"], verbose):
                results.append(current_entry)

    return results


def query_json_logs(log_path: Path, t_from: datetime, t_to: datetime, verbose: bool) -> list[dict]:
    """Parse a structured JSON log file and return matching entries."""
    results = []
    if not log_path.exists():
        return results

    with open(log_path, "r", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = parse_json_log_timestamp(obj)
            if ts is None:
                continue
            if not (t_from <= ts <= t_to):
                continue
            subsys, msg = extract_message_json(obj)
            if is_noise(msg, verbose):
                continue
            results.append({"ts": ts, "subsys": subsys, "msg": msg})

    return results


def format_output(entries: list[dict], verbose: bool) -> str:
    """Format entries into a readable timeline."""
    if not entries:
        return "No log entries found in the specified time range."

    # Sort by timestamp
    entries.sort(key=lambda e: e["ts"])

    lines = []
    lines.append(f"## OpenClaw Log: {entries[0]['ts'].strftime('%Y-%m-%d %H:%M:%S')} ~ {entries[-1]['ts'].strftime('%H:%M:%S')} (Beijing Time)")
    lines.append(f"Total: {len(entries)} entries\n")

    # Group by category for summary
    cat_counts: dict[str, int] = {}
    error_entries = []
    for e in entries:
        cat = categorize(e["msg"])
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        if cat == "error":
            error_entries.append(e)

    # Summary
    lines.append("### Summary")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        label = CATEGORIES.get(cat, (cat.upper(), []))[0]
        lines.append(f"- {label}: {count}")
    lines.append("")

    # Errors highlight
    if error_entries:
        lines.append("### Errors")
        for e in error_entries:
            t = e["ts"].strftime("%H:%M:%S")
            lines.append(f"- `{t}` [{e['subsys']}] {e['msg']}")
        lines.append("")

    # Full timeline
    lines.append("### Timeline")
    prev_minute = ""
    for e in entries:
        t = e["ts"].strftime("%H:%M:%S")
        minute = e["ts"].strftime("%H:%M")
        cat = categorize(e["msg"])
        label = CATEGORIES.get(cat, (cat.upper(), []))[0]

        # Add separator between minutes for readability
        if minute != prev_minute and prev_minute:
            lines.append("")
        prev_minute = minute

        subsys_str = f"[{e['subsys']}] " if e["subsys"] else ""
        msg_display = e["msg"][:200] if not verbose else e["msg"]
        lines.append(f"`{t}` **{label}** {subsys_str}{msg_display}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Query OpenClaw logs for a time range")
    parser.add_argument("--from", dest="time_from", help="Start time (HH:MM or YYYY-MM-DD HH:MM)")
    parser.add_argument("--to", dest="time_to", help="End time (HH:MM or YYYY-MM-DD HH:MM)")
    parser.add_argument("--last", help="Last N minutes/hours (e.g. 30m, 2h)")
    parser.add_argument("--date", help="Date (YYYY-MM-DD), defaults to today")
    parser.add_argument("--log-dir", default=os.path.expanduser("~/.openclaw/logs"),
                        help="OpenClaw log directory")
    parser.add_argument("--runtime-log-dir", default="/tmp/openclaw",
                        help="Runtime log directory")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Include noise entries (cron heartbeats, etc)")
    parser.add_argument("--category", "-c", help="Filter by category (error, restart, plugin, telegram, acp, config, etc)")
    args = parser.parse_args()

    # Determine time range
    if args.last:
        t_from, t_to = parse_last_arg(args.last)
    elif args.time_from and args.time_to:
        default_date = args.date or datetime.now(BJT).strftime("%Y-%m-%d")
        t_from = parse_time_arg(args.time_from, default_date)
        t_to = parse_time_arg(args.time_to, default_date)
    else:
        parser.error("Specify --from/--to or --last")
        return

    log_dir = Path(args.log_dir)
    runtime_dir = Path(args.runtime_log_dir)

    # Collect entries from all log sources
    all_entries: list[dict] = []

    # 1. Plain-text gateway logs
    for log_file in ["gateway.log", "gateway.err.log"]:
        path = log_dir / log_file
        all_entries.extend(query_plain_logs(path, t_from, t_to, args.verbose))

    # 2. Structured JSON runtime logs (date-based files)
    # Check all dates in range
    d = t_from.date()
    while d <= t_to.date():
        json_log = runtime_dir / f"openclaw-{d.isoformat()}.log"
        all_entries.extend(query_json_logs(json_log, t_from, t_to, args.verbose))
        d += timedelta(days=1)

    # Deduplicate (same timestamp + same message)
    seen = set()
    unique = []
    for e in all_entries:
        key = (e["ts"].strftime("%H:%M:%S"), e["msg"][:80])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    # Filter by category if specified
    if args.category:
        unique = [e for e in unique if categorize(e["msg"]) == args.category]

    print(format_output(unique, args.verbose))


if __name__ == "__main__":
    main()
