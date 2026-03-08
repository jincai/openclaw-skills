---
name: oura
description: Sync and analyze Oura Ring health data — sleep, readiness, resilience, activity, stress, heart rate, SpO2, workouts. Supports daily sync, weekly reports, and sleep debt tracking. Use when user asks about health, sleep, HRV, recovery, or fitness data.
user-invocable: true
metadata:
  openclaw:
    primaryEnv: OURA_TOKEN
    requires:
      env: ["OURA_TOKEN"]
---

# Oura Ring Health Sync

Direct Oura API v2 integration — no third-party SDK, zero dependencies beyond Python stdlib.

## Syncing Data

```bash
# Sync today
OURA_TOKEN=<token> python3 {baseDir}/scripts/sync.py

# Sync specific date
OURA_TOKEN=<token> python3 {baseDir}/scripts/sync.py --date 2026-03-07

# Sync last N days
OURA_TOKEN=<token> python3 {baseDir}/scripts/sync.py --days 14

# Weekly report (sleep debt + trends)
OURA_TOKEN=<token> python3 {baseDir}/scripts/sync.py --weekly
OURA_TOKEN=<token> python3 {baseDir}/scripts/sync.py --weekly --date 2026-03-08
```

## With 1Password Service Account

```bash
OURA_TOKEN=$(OP_SERVICE_ACCOUNT_TOKEN=$(cat ~/.openclaw/.op-token) op read "op://Agent/oura/password") \
  python3 {baseDir}/scripts/sync.py --days 2
```

## Reading Health Data

Daily files: `{baseDir}/health/YYYY-MM-DD.md`
Weekly reports: `{baseDir}/health/weekly-YYYY-MM-DD.md`

To answer health questions, read the relevant files. If missing, sync first.

## Data Coverage

| Category | Fields |
|----------|--------|
| Sleep | Duration, stages (deep/REM/light/awake), bedtime/wake, latency, score + 6 sub-scores |
| Readiness | Score, temp deviation, HRV balance, resting HR, recovery index, sleep/activity balance |
| Resilience | Level, sleep recovery, daytime recovery, stress |
| Activity | Steps, calories, distance, active/low/sedentary time, score |
| Stress | High stress minutes, recovery minutes, ratio |
| Heart Rate | Resting, min, max, avg (stats only, not raw data) |
| SpO2 | Average blood oxygen % |
| Workouts | Activity type, duration, distance, calories |
| Weekly | Sleep debt table, readiness trend, activity summary, stress summary |

## Cron Setup

Schedule daily sync + report via OpenClaw cron.
