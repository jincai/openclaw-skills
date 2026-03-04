# openclaw-logs

Query and analyze OpenClaw gateway logs. Supports time range filtering, category grouping, automatic noise suppression, and timezone normalization.

## What it does

When you ask Claude things like:

- "openclaw 最近 30 分钟发生了什么"
- "查一下 19:20 到 20:00 的日志"
- "openclaw 有什么报错"

This skill runs a Python script that parses all OpenClaw log sources, deduplicates entries, filters noise, and outputs a structured timeline with category labels and error highlights.

## Features

- **Multi-source**: Reads `gateway.log`, `gateway.err.log`, and structured JSON runtime logs
- **Time range**: `--from "19:20" --to "20:00"` or `--last 30m`
- **Category filter**: `--category error|restart|plugin|telegram|acp|config|agent|gateway`
- **Noise suppression**: Filters cron heartbeats and other repetitive entries (override with `--verbose`)
- **Timezone normalization**: Mixed UTC/+08:00 timestamps are all converted to Beijing time
- **Deduplication**: Same event from multiple log files appears only once

## Standalone usage

```bash
# Last 30 minutes
python3 scripts/query_logs.py --last 30m

# Specific time range (Beijing time)
python3 scripts/query_logs.py --from "19:20" --to "20:00"

# Only errors
python3 scripts/query_logs.py --last 1h --category error

# Cross-day query
python3 scripts/query_logs.py --from "2026-03-03 23:00" --to "2026-03-04 02:00"
```

## Output format

```
## OpenClaw Log: 2026-03-04 19:20:59 ~ 20:00:00 (Beijing Time)
Total: 42 entries

### Summary
- ERROR: 11
- RESTART: 8
- TELEGRAM: 12
...

### Errors
- `19:20:59` [agent/embedded] API rate limit reached
- `19:37:50` [gateway] acp startup identity reconcile failed
...

### Timeline
`19:20:59` **ERROR** [agent/embedded] embedded run agent end: isError=true ...
`19:32:38` **PLUGIN** [openclaw] Downloading @askjo/camofox-browser…
`19:37:18` **RESTART** [gateway] received SIGUSR1; restarting
...
```

## Requirements

- Python 3.9+
- OpenClaw gateway logs at default paths (`~/.openclaw/logs/` and `/tmp/openclaw/`)
