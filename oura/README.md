# oura

Sync and analyze Oura Ring health data — sleep, readiness, resilience, activity, stress, heart rate, SpO2, workouts. Includes sleep debt tracking and weekly reports.

## What it does

Pulls your health data from Oura Ring API v2 and writes it to readable markdown files. Claude can then reference your health data in conversation, give personalized advice, and track trends.

When you ask things like:

- "我昨晚睡得怎么样"
- "最近一周睡眠欠债多少"
- "show me my health data for today"
- "give me a weekly health report"

Claude syncs the latest data and answers based on real numbers.

## Features

- **Zero dependencies**: Pure Python stdlib — no pip install, no third-party SDK
- **Direct API**: Calls Oura API v2 directly via `urllib`, avoids buggy SDK issues
- **Sleep debt tracking**: Weekly report calculates cumulative sleep debt against 7.5h target
- **Complete data**: Sleep stages, latency, 6 sleep sub-scores, resilience, stress ratio, HR stats
- **1Password support**: Optional integration with 1Password Service Account for secure token storage
- **Cron-friendly**: Designed for daily automated sync + reporting

## Data coverage

| Category | Fields |
|----------|--------|
| Sleep | Duration, stages (deep/REM/light/awake), bedtime/wake, latency, score + 6 sub-scores |
| Readiness | Score, temp deviation, HRV balance, resting HR, recovery index, sleep/activity balance |
| Resilience | Level, sleep recovery, daytime recovery, stress |
| Activity | Steps, calories, distance, active/low/sedentary time, score |
| Stress | High stress minutes, recovery minutes, ratio |
| Heart Rate | Resting, min, max, avg (stats only — not raw 1000+ data points) |
| SpO2 | Average blood oxygen % |
| Workouts | Activity type, duration, distance, calories |
| Weekly | Sleep debt table, readiness trend, activity summary, stress summary |

## Setup

### 1. Get your Oura token

Go to [cloud.ouraring.com/personal-access-tokens](https://cloud.ouraring.com/personal-access-tokens) and create a Personal Access Token. It never expires unless you revoke it.

### 2. Run a sync

```bash
# Set your token
export OURA_TOKEN="your_token_here"

# Sync today's data
python3 scripts/sync.py

# Sync last 7 days
python3 scripts/sync.py --days 7

# Generate weekly report
python3 scripts/sync.py --weekly
```

### Optional: 1Password Service Account

For automated/headless setups where you don't want to store the token in plaintext:

1. Create a 1Password Service Account with read access to a dedicated vault
2. Store your Oura token in that vault
3. Run with:

```bash
OURA_TOKEN=$(OP_SERVICE_ACCOUNT_TOKEN=$(cat ~/.openclaw/.op-token) op read "op://Agent/oura/password") \
  python3 scripts/sync.py
```

## Usage

### Daily sync

```bash
# Today
python3 scripts/sync.py

# Specific date
python3 scripts/sync.py --date 2026-03-07

# Last N days
python3 scripts/sync.py --days 14
```

### Weekly report

```bash
# Current week (ending today)
python3 scripts/sync.py --weekly

# Specific week (ending on date)
python3 scripts/sync.py --weekly --date 2026-03-08
```

### Custom output directory

```bash
python3 scripts/sync.py --days 7 --output-dir /path/to/health
```

### OpenClaw cron (daily at 10:00)

```bash
openclaw cron add \
  --name "oura-daily-report" \
  --cron "0 10 * * *" \
  --tz "Asia/Shanghai" \
  --announce --channel telegram --to "YOUR_CHAT_ID" \
  --timeout-seconds 120 \
  --message 'Sync Oura data and send daily health report:
OURA_TOKEN=<token> python3 ~/.openclaw/workspace/skills/oura/scripts/sync.py --days 2
Then read the health files and send a report with analysis and suggestions.'
```

## Output examples

### Daily (`health/2026-03-08.md`)

```markdown
# Health — 2026-03-08 Sunday

## Sleep: 5h12m
Deep: 0h49m | REM: 1h17m | Light: 3h05m | Awake: 0h34m
Bedtime: 02:34 | Wake: 08:21
Latency: 14m
Score: 65
Efficiency: 95 | Restfulness: 72 | Timing: 52 | Total: 50 | Deep: 58 | REM: 69

## Readiness: 69
Temp: -0.5°C
HRV: 88 | Resting HR: 89 | Recovery: 52 | Body Temp: 87
Sleep Bal: 29 | Prev Night: 59 | Activity Bal: 95 | Prev Activity: 70

## Resilience: adequate
Sleep Recovery: 43 | Daytime Recovery: 44 | Stress: 47

## Stress
High Stress: 15m | Recovery: 90m | Ratio: 1:6.0

## Heart Rate (bpm)
Resting: 58 | Min: 58 | Max: 93 | Avg: 85

## SpO2: 98%
```

### Weekly (`health/weekly-2026-03-08.md`)

Includes sleep debt table, readiness trend, activity summary, and stress summary with weekly totals.

## File structure

```
oura/
├── SKILL.md              # Instructions for Claude / OpenClaw
├── README.md             # This file
├── health/               # Synced data (gitignored)
│   ├── 2026-03-08.md
│   └── weekly-2026-03-08.md
└── scripts/
    └── sync.py           # Main sync script (zero dependencies)
```

## Requirements

- **Python 3.10+** (uses `match` syntax and `X | Y` type unions)
- **Oura Ring** with an active account
- For 1Password integration: `op` CLI v2.18+

## Known quirks

- **Oura API filters sleep by `bedtime_start`, not `day`**: If you fall asleep at 2 AM on March 8, the API considers that a March 7 query. This script handles it by querying ±1 day and filtering by the `day` field.
- **Heart rate endpoint returns 1000+ records per day**: This script only computes stats (resting/min/max/avg) to avoid slow syncs.
- **No data days**: If you didn't wear the ring, that day will be skipped.

## License

MIT
