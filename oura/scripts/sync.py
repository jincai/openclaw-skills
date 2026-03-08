#!/usr/bin/env python3
"""
Oura Ring Health Data Sync — Direct API, no third-party SDK.

Usage:
    python3 sync.py                     # Sync today
    python3 sync.py --date 2026-03-07   # Sync specific date
    python3 sync.py --days 7            # Sync last 7 days
    python3 sync.py --weekly            # Generate weekly report
"""

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE_DIR = Path(__file__).resolve().parent.parent
HEALTH_DIR = BASE_DIR / "health"
API_BASE = "https://api.ouraring.com/v2/usercollection"


def api_get(endpoint: str, token: str, params: dict) -> list:
    """Fetch data from Oura API v2. Returns list of records."""
    query = "&".join(f"{k}={v}" for k, v in params.items() if v)
    url = f"{API_BASE}/{endpoint}?{query}"
    req = Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("data", [])
    except HTTPError as e:
        print(f"  API error {endpoint}: {e.code}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  API error {endpoint}: {e}", file=sys.stderr)
        return []


def find_day(items: list, day_str: str) -> dict | None:
    for item in items:
        if item.get("day") == day_str:
            return item
    return None


def fmt_dur(seconds: int | float | None) -> str:
    if not seconds:
        return "—"
    m = int(seconds) // 60
    return f"{m // 60}h{m % 60:02d}m"


def fmt_time(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        return datetime.fromisoformat(iso).strftime("%H:%M")
    except (ValueError, TypeError):
        return "—"


def sync_day(token: str, day: date) -> str | None:
    """Sync one day's data, return markdown content or None."""
    ds = day.isoformat()
    prev = (day - timedelta(days=1)).isoformat()
    nxt = (day + timedelta(days=1)).isoformat()
    display = day.strftime("%Y-%m-%d %A")

    sections = [f"# Health — {display}"]

    # ── Sleep ──
    daily_sleep = find_day(api_get("daily_sleep", token, {"start_date": ds, "end_date": ds}), ds)
    # Sleep periods: query prev→nxt because API filters by bedtime_start, not day
    sleep_periods = api_get("sleep", token, {"start_date": prev, "end_date": nxt})
    period = None
    for p in sleep_periods:
        if p.get("day") == ds and p.get("type") == "long_sleep":
            period = p
            break
    if not period:
        for p in sleep_periods:
            if p.get("day") == ds:
                period = p
                break

    if daily_sleep or period:
        total = period.get("total_sleep_duration") if period else None
        lines = [f"## Sleep{': ' + fmt_dur(total) if total else ''}"]

        if period:
            stages = []
            for key, label in [("deep_sleep_duration", "Deep"), ("rem_sleep_duration", "REM"),
                                ("light_sleep_duration", "Light"), ("awake_time", "Awake")]:
                v = period.get(key)
                if v is not None:
                    stages.append(f"{label}: {fmt_dur(v)}")
            if stages:
                lines.append(" | ".join(stages))

            times = []
            bt = fmt_time(period.get("bedtime_start"))
            wk = fmt_time(period.get("bedtime_end"))
            if bt != "—":
                times.append(f"Bedtime: {bt}")
            if wk != "—":
                times.append(f"Wake: {wk}")
            if times:
                lines.append(" | ".join(times))

            # Latency
            latency = period.get("latency")
            if latency is not None:
                lines.append(f"Latency: {int(latency) // 60}m")

        if daily_sleep:
            score = daily_sleep.get("score")
            if score is not None:
                lines.append(f"Score: {score}")
            contrib = daily_sleep.get("contributors", {})
            parts = []
            for key, label in [("efficiency", "Efficiency"), ("restfulness", "Restfulness"),
                                ("timing", "Timing"), ("total_sleep", "Total"),
                                ("deep_sleep", "Deep"), ("rem_sleep", "REM")]:
                v = contrib.get(key)
                if v is not None:
                    parts.append(f"{label}: {v}")
            if parts:
                lines.append(" | ".join(parts))

        sections.append("\n".join(lines))

    # ── Readiness ──
    readiness = find_day(api_get("daily_readiness", token, {"start_date": ds, "end_date": ds}), ds)
    if readiness:
        score = readiness.get("score")
        lines = [f"## Readiness: {score}" if score else "## Readiness"]
        temp = readiness.get("temperature_deviation")
        if temp is not None:
            lines.append(f"Temp: {'+' if temp >= 0 else ''}{temp:.1f}°C")
        contrib = readiness.get("contributors", {})
        row1 = []
        for key, label in [("hrv_balance", "HRV"), ("resting_heart_rate", "Resting HR"),
                            ("recovery_index", "Recovery"), ("body_temperature", "Body Temp")]:
            v = contrib.get(key)
            if v is not None:
                row1.append(f"{label}: {v}")
        if row1:
            lines.append(" | ".join(row1))
        row2 = []
        for key, label in [("sleep_balance", "Sleep Bal"), ("previous_night", "Prev Night"),
                            ("activity_balance", "Activity Bal"), ("previous_day_activity", "Prev Activity")]:
            v = contrib.get(key)
            if v is not None:
                row2.append(f"{label}: {v}")
        if row2:
            lines.append(" | ".join(row2))
        sections.append("\n".join(lines))

    # ── Resilience ──
    resilience = find_day(api_get("daily_resilience", token, {"start_date": ds, "end_date": ds}), ds)
    if resilience:
        level = resilience.get("level", "?")
        lines = [f"## Resilience: {level}"]
        contrib = resilience.get("contributors", {})
        parts = []
        for key, label in [("sleep_recovery", "Sleep Recovery"), ("daytime_recovery", "Daytime Recovery"),
                            ("stress", "Stress")]:
            v = contrib.get(key)
            if v is not None:
                parts.append(f"{label}: {v:.0f}")
        if parts:
            lines.append(" | ".join(parts))
        sections.append("\n".join(lines))

    # ── Activity ──
    activity = find_day(api_get("daily_activity", token, {"start_date": ds, "end_date": ds}), ds)
    if activity:
        steps = activity.get("steps")
        cal = activity.get("total_calories")
        header_parts = []
        if steps:
            header_parts.append(f"{steps:,} steps")
        if cal:
            header_parts.append(f"{int(cal):,} cal")
        lines = [f"## Activity{': ' + ' | '.join(header_parts) if header_parts else ''}"]
        detail = []
        dist = activity.get("equivalent_walking_distance")
        if dist and dist > 0:
            detail.append(f"Distance: {dist / 1000:.1f}km")
        high = activity.get("high_activity_time", 0) or 0
        med = activity.get("medium_activity_time", 0) or 0
        if high + med > 0:
            detail.append(f"Active: {(high + med) // 60}m")
        low = activity.get("low_activity_time", 0) or 0
        if low > 0:
            detail.append(f"Low: {low // 60}m")
        sedentary = activity.get("sedentary_time", 0) or 0
        if sedentary > 0:
            detail.append(f"Sedentary: {sedentary // 60}m")
        if detail:
            lines.append(" | ".join(detail))
        score = activity.get("score")
        if score:
            lines.append(f"Score: {score}")
        sections.append("\n".join(lines))

    # ── Stress ──
    stress = find_day(api_get("daily_stress", token, {"start_date": ds, "end_date": ds}), ds)
    if stress:
        parts = []
        sh = stress.get("stress_high")
        rh = stress.get("recovery_high")
        if sh is not None:
            parts.append(f"High Stress: {sh // 60}m")
        if rh is not None:
            parts.append(f"Recovery: {rh // 60}m")
        if sh and rh and sh > 0:
            ratio = rh / sh
            parts.append(f"Ratio: 1:{ratio:.1f}")
        if parts:
            sections.append("## Stress\n" + " | ".join(parts))

    # ── Heart Rate (stats only, skip raw 1000+ records) ──
    hr_data = api_get("heartrate", token,
                       {"start_datetime": f"{ds}T00:00:00", "end_datetime": f"{ds}T23:59:59"})
    if hr_data:
        bpms = [e["bpm"] for e in hr_data if e.get("bpm")]
        rest_bpms = [e["bpm"] for e in hr_data if e.get("bpm") and e.get("source") in ("rest", "sleep")]
        if bpms:
            parts = []
            if rest_bpms:
                rest_sorted = sorted(rest_bpms)
                resting = rest_sorted[max(0, len(rest_sorted) * 5 // 100)]
                parts.append(f"Resting: {resting}")
            parts.append(f"Min: {min(bpms)}")
            parts.append(f"Max: {max(bpms)}")
            parts.append(f"Avg: {sum(bpms) // len(bpms)}")
            sections.append("## Heart Rate (bpm)\n" + " | ".join(parts))

    # ── SpO2 ──
    spo2 = find_day(api_get("daily_spo2", token, {"start_date": ds, "end_date": ds}), ds)
    if spo2:
        pct = spo2.get("spo2_percentage", {})
        avg = pct.get("average") if pct else None
        if avg:
            sections.append(f"## SpO2: {avg:.0f}%")

    # ── Workouts ──
    workouts = [w for w in api_get("workout", token, {"start_date": ds, "end_date": ds}) if w.get("day") == ds]
    if workouts:
        lines = ["## Workouts"]
        for w in workouts:
            name = w.get("label") or w.get("activity", "workout").replace("_", " ").title()
            parts = [f"**{name}**"]
            start = w.get("start_datetime")
            end = w.get("end_datetime")
            if start and end:
                try:
                    dur = (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds()
                    parts[0] += f" — {fmt_dur(dur)}"
                except (ValueError, TypeError):
                    pass
            dist = w.get("distance")
            if dist and dist > 0:
                parts.append(f"{dist / 1000:.1f}km")
            cal = w.get("calories")
            if cal and cal > 0:
                parts.append(f"{int(cal)}cal")
            lines.append("- " + ", ".join(parts))
        sections.append("\n".join(lines))

    if len(sections) <= 1:
        print(f"  {ds}: No data", file=sys.stderr)
        return None

    return "\n\n".join(sections) + "\n"


def generate_weekly(token: str, end: date) -> str:
    """Generate weekly summary from last 7 days of data."""
    start = end - timedelta(days=6)
    prev = (start - timedelta(days=1)).isoformat()
    nxt = (end + timedelta(days=1)).isoformat()

    # Collect sleep data
    sleep_periods = api_get("sleep", token, {"start_date": prev, "end_date": nxt})
    daily_sleeps = api_get("daily_sleep", token, {"start_date": start.isoformat(), "end_date": end.isoformat()})
    daily_readiness = api_get("daily_readiness", token, {"start_date": start.isoformat(), "end_date": end.isoformat()})
    daily_activity = api_get("daily_activity", token, {"start_date": start.isoformat(), "end_date": end.isoformat()})
    daily_stress = api_get("daily_stress", token, {"start_date": start.isoformat(), "end_date": end.isoformat()})

    TARGET_SLEEP = 7.5 * 3600  # 7.5 hours in seconds

    lines = [f"# Weekly Health Report — {start.isoformat()} to {end.isoformat()}", ""]

    # ── Sleep Debt Table ──
    lines.append("## Sleep Debt")
    lines.append(f"| Date | Duration | Bedtime | Wake | Score | Debt |")
    lines.append("|------|----------|---------|------|-------|------|")
    total_debt = 0
    sleep_durations = []
    for d in range(7):
        day = start + timedelta(days=d)
        ds = day.isoformat()
        period = None
        for p in sleep_periods:
            if p.get("day") == ds and p.get("type") == "long_sleep":
                period = p
                break
        daily = find_day(daily_sleeps, ds)
        dur = period.get("total_sleep_duration", 0) if period else 0
        score = daily.get("score", "—") if daily else "—"
        bt = fmt_time(period.get("bedtime_start")) if period else "—"
        wk = fmt_time(period.get("bedtime_end")) if period else "—"
        debt = TARGET_SLEEP - dur if dur > 0 else 0
        total_debt += debt
        if dur > 0:
            sleep_durations.append(dur)
        debt_str = f"+{fmt_dur(debt)}" if debt > 0 else f"-{fmt_dur(-debt)}" if debt < 0 else "0"
        dur_str = fmt_dur(dur) if dur > 0 else "—"
        lines.append(f"| {ds} | {dur_str} | {bt} | {wk} | {score} | {debt_str} |")

    lines.append("")
    avg_sleep = sum(sleep_durations) / len(sleep_durations) if sleep_durations else 0
    lines.append(f"**Average sleep:** {fmt_dur(avg_sleep)}")
    lines.append(f"**Total sleep debt:** {fmt_dur(total_debt)} (target: 7h30m/night)")
    lines.append(f"**Avg nightly deficit:** {fmt_dur(total_debt / 7)}")
    lines.append("")

    # ── Readiness Trend ──
    lines.append("## Readiness Trend")
    scores = []
    for d in range(7):
        ds = (start + timedelta(days=d)).isoformat()
        r = find_day(daily_readiness, ds)
        s = r.get("score") if r else None
        scores.append((ds, s))
        lines.append(f"- {ds}: {s if s else '—'}")
    valid = [s for _, s in scores if s]
    if valid:
        lines.append(f"**Average:** {sum(valid) / len(valid):.0f}")
    lines.append("")

    # ── Activity Summary ──
    lines.append("## Activity Summary")
    total_steps = 0
    total_cal = 0
    for d in range(7):
        ds = (start + timedelta(days=d)).isoformat()
        a = find_day(daily_activity, ds)
        if a:
            steps = a.get("steps", 0) or 0
            cal = a.get("total_calories", 0) or 0
            total_steps += steps
            total_cal += int(cal)
            lines.append(f"- {ds}: {steps:,} steps, {int(cal):,} cal")
    lines.append(f"**Weekly total:** {total_steps:,} steps, {total_cal:,} cal")
    lines.append(f"**Daily avg:** {total_steps // 7:,} steps")
    lines.append("")

    # ── Stress Summary ──
    lines.append("## Stress Summary")
    total_stress = 0
    total_recovery = 0
    for d in range(7):
        ds = (start + timedelta(days=d)).isoformat()
        s = find_day(daily_stress, ds)
        if s:
            sh = s.get("stress_high", 0) or 0
            rh = s.get("recovery_high", 0) or 0
            total_stress += sh
            total_recovery += rh
    lines.append(f"**Total high stress:** {total_stress // 60}m")
    lines.append(f"**Total recovery:** {total_recovery // 60}m")
    if total_stress > 0:
        lines.append(f"**Recovery ratio:** 1:{total_recovery / total_stress:.1f}")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Sync Oura Ring health data.")
    parser.add_argument("--date", type=str, help="Specific date (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, help="Sync last N days")
    parser.add_argument("--weekly", action="store_true", help="Generate weekly report")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory")
    args = parser.parse_args()

    token = os.environ.get("OURA_TOKEN")
    if not token:
        print("Error: OURA_TOKEN required.", file=sys.stderr)
        print("Get token: https://cloud.ouraring.com/personal-access-tokens", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.output_dir) if args.output_dir else HEALTH_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.weekly:
        end = date.fromisoformat(args.date) if args.date else date.today()
        content = generate_weekly(token, end)
        out_file = out_dir / f"weekly-{end.isoformat()}.md"
        out_file.write_text(content)
        print(f"Weekly report: {out_file}")
        return

    if args.days:
        days = [date.today() - timedelta(days=i) for i in range(args.days)]
    elif args.date:
        days = [date.fromisoformat(args.date)]
    else:
        days = [date.today()]

    print(f"Syncing {len(days)} day(s)...")
    for day in sorted(days):
        content = sync_day(token, day)
        if content:
            out_file = out_dir / f"{day.isoformat()}.md"
            out_file.write_text(content)
            print(f"  {day.isoformat()}: OK")

    print("Done.")


if __name__ == "__main__":
    main()
