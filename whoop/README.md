# whoop

Sync WHOOP health data (recovery, sleep, strain, workouts) to readable markdown files. Supports both local and remote/server authorization flows.

## What it does

Pulls your health data from the WHOOP API and writes it to markdown files. Claude can then reference your recovery, sleep, strain, and workout data in conversation.

When you ask things like:

- "我今天恢复怎么样"
- "最近睡眠欠债多少"
- "show me my recovery score"
- "give me a weekly health report"

Claude syncs the latest data and answers based on real numbers.

## Features

- **Zero dependencies**: Pure Python stdlib (`urllib`, `json`, `http.server`) + `curl`
- **One-time OAuth**: Authorize once, tokens auto-refresh forever (via `offline` scope)
- **Local + Remote auth**: Works on your laptop (automatic) or a headless server (manual code exchange)
- **Complete data**: Recovery, HRV, sleep stages, strain, workouts with HR zones, weekly reports
- **1Password support**: Optional — works fine with just environment variables
- **Cron-friendly**: Designed for daily automated sync + reporting

## Data coverage

| Category | Fields |
|----------|--------|
| Recovery | Score (🔴🟡🟢), HRV (RMSSD), Resting HR, SpO2, Skin Temp |
| Sleep | Performance/Efficiency/Consistency, Stages (Light/Deep/REM/Awake), Respiratory Rate, Sleep Need (baseline + debt + strain), Balance (surplus/deficit) |
| Day Strain | Strain (0-21), Calories (kJ + kcal), Avg/Max HR |
| Workouts | Sport name, Duration, Strain, Calories, Avg/Max HR, Distance, Elevation (↑gain / net), HR Zones |
| Weekly | Averages for recovery/HRV/RHR, sleep performance/duration, strain, workout count |

## Setup

### 1. Create a WHOOP Developer App

1. Go to [developer-dashboard.whoop.com](https://developer-dashboard.whoop.com/)
2. Sign in with your WHOOP account
3. Click **Create Application**
   - **Name**: anything (e.g. "My Health Sync")
   - **Redirect URI**: `http://localhost:9527/callback`
   - **Scopes**: select all `read:*` scopes + `offline`
4. Note your **Client ID** and **Client Secret**

> ⚠️ Redirect URI must be exactly `http://localhost:9527/callback`.

### 2. Store credentials

**Option A: Environment Variables (simplest)**

```bash
export WHOOP_CLIENT_ID="your-client-id"
export WHOOP_CLIENT_SECRET="your-client-secret"
```

**Option B: 1Password (for OpenClaw users)**

Create a Login item in your 1Password vault:
- Name: `whoop`
- Username: `<Client ID>`
- Password: `<Client Secret>`

The scripts auto-read from 1Password if `~/.openclaw/.op-token` exists.

### 3. Authorize (one-time)

#### 🖥️ Local machine (browser on same machine)

```bash
python3 scripts/auth.py
```

Opens a URL → you authorize in browser → callback auto-caught → tokens saved ✅

#### 🌐 Remote server (headless VPS)

```bash
# Step 1: Get the auth URL
python3 scripts/auth.py --print-url

# Step 2: Open URL in your local browser, authorize, then copy the callback URL
# The browser will redirect to localhost:9527 (which won't load — that's fine)
# Copy the full URL from the address bar, then:

python3 scripts/auth.py --callback-url "http://localhost:9527/callback?code=xxx&state=yyy"
# Or just the code:
python3 scripts/auth.py --code "the-code-value"
```

**That's it — you only authorize once.** Tokens auto-refresh on every sync via the `offline` scope. As long as you sync at least once every few months, you'll never need to re-authorize.

## Usage

```bash
# Sync today
python3 scripts/sync.py

# Sync specific date
python3 scripts/sync.py --date 2026-03-07

# Sync last 7 days
python3 scripts/sync.py --days 7

# Weekly summary report
python3 scripts/sync.py --weekly

# Custom output directory
python3 scripts/sync.py --output-dir /path/to/health
```

Output: `health/whoop-YYYY-MM-DD.md` (or `~/.openclaw/workspace/health/` by default)

### OpenClaw cron (daily at 10:00)

```bash
openclaw cron add \
  --name whoop-daily \
  --schedule "0 10 * * *" \
  --timezone Asia/Shanghai \
  --task "Run: python3 ~/.openclaw/workspace/skills/whoop/scripts/sync.py --days 2. Then read the generated markdown files and send me the latest day's report."
```

## Output example

```markdown
# WHOOP — 2026-03-09

## Recovery 🟢
- **Recovery Score**: 66%
- **HRV (RMSSD)**: 41.4 ms
- **Resting HR**: 62.0 bpm
- **SpO2**: 96.3%
- **Skin Temp**: 33.7°C

## Sleep
- **Performance**: 🟡 61%
- **Efficiency**: 90%
- **Total in Bed**: 5h47m
- **Stages**: Light 2h08m | Deep 1h25m | REM 1h38m | Awake 35m
- **Sleep Need**: 9h41m
- **Balance**: 4h29m deficit

## Day Strain
- **Strain**: 0.1 / 21.0
- **Calories**: 2233 kJ (534 kcal)

## Workouts
- Walking · 16m28s · Strain 4.9 · Avg HR 114 bpm
```

## Token refresh

Tokens auto-refresh using the `offline` scope refresh token. The refresh token is **rolling** — each refresh returns a new one, keeping the chain alive indefinitely.

**You only need to re-authorize if:**
- You manually revoke the app in WHOOP settings
- You stop syncing for many months (refresh token expires from disuse)
- WHOOP changes their OAuth policy (rare)

If `sync.py` reports `Token refresh failed (403)`, just re-run `auth.py`.

> Token exchange uses `curl` internally to bypass Cloudflare blocking Python's default User-Agent (error 1010).

## File structure

```
whoop/
├── SKILL.md              # Instructions for Claude / OpenClaw
├── README.md             # This file
├── scripts/
│   ├── auth.py           # OAuth authorization (local + remote modes)
│   └── sync.py           # Daily sync + weekly reports
└── data/
    ├── tokens.json       # OAuth tokens (auto-refreshed, gitignored)
    └── .auth_state       # Temp state for remote auth (auto-cleaned)
```

## Requirements

- **Python 3.10+** (uses `match` syntax and `X | Y` type unions)
- **curl** (for token exchange — avoids Cloudflare blocks)
- **WHOOP membership** with an active account
- For 1Password: `op` CLI v2.18+

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No tokens found` | Run `auth.py` first |
| `Token refresh failed (403)` | Re-run `auth.py` to re-authorize |
| `error code: 1010` | Cloudflare block — should be fixed (uses curl). Check network/proxy |
| `State mismatch` | Restart `auth.py` and use its URL (don't mix URLs from different runs) |
| `No data for date` | WHOOP may not have data yet (sleep finalizes after waking) |
| Port 9527 in use | `kill $(lsof -ti:9527)` then retry |

## License

MIT
