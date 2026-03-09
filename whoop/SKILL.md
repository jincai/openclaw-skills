# WHOOP Health Data Sync

Sync WHOOP health data (recovery, sleep, strain, workouts) to local markdown files.
Pure Python, zero dependencies — uses only stdlib (`urllib`, `json`, `http.server`) + `curl`.

## What's Synced

| Category | Metrics |
|----------|---------|
| **Recovery** | Score (🔴🟡🟢), HRV (RMSSD), Resting HR, SpO2, Skin Temp |
| **Sleep** | Performance/Efficiency/Consistency, Stages (Light/Deep/REM/Awake), Respiratory Rate, Sleep Need breakdown (baseline + debt + strain), Balance (surplus/deficit) |
| **Day Strain** | Strain (0-21), Calories (kJ + kcal), Avg/Max HR |
| **Workouts** | Sport name, Duration, Strain, Calories, Avg/Max HR, Distance, Elevation (↑gain / net), HR Zones |
| **Weekly** | Averages for recovery/HRV/RHR, sleep performance/duration, strain, workout count |

## Setup

### Step 1: Create WHOOP Developer App

1. Go to https://developer-dashboard.whoop.com/
2. Sign in with your WHOOP account
3. Click **Create Application**
   - **Name**: anything (e.g. "My Health Sync")
   - **Redirect URI**: `http://localhost:9527/callback`
   - **Scopes**: select all `read:*` scopes + `offline`
4. Note your **Client ID** and **Client Secret**

> ⚠️ Redirect URI must be exactly `http://localhost:9527/callback` — this is what `auth.py` listens on.

### Step 2: Store Credentials

**Option A: 1Password (recommended for OpenClaw users)**

1. In 1Password, create a **Login** item in your Agent vault:
   - Name: `whoop`
   - Username: `<your Client ID>`
   - Password: `<your Client Secret>`
2. The scripts auto-read from 1P via Service Account (reads `~/.openclaw/.op-token`)

**Option B: Environment Variables**

```bash
export WHOOP_CLIENT_ID="your-client-id"
export WHOOP_CLIENT_SECRET="your-client-secret"
```

Pass inline when running the scripts. **Don't add to ~/.zshrc** — use 1P or pass per-command.

### Step 3: Authorize (one-time OAuth flow)

Authorization works differently depending on where OpenClaw runs:

#### 🖥️ Local Machine (browser on same machine)

Your browser can reach `localhost:9527` directly — fully automatic:

```bash
python3 scripts/auth.py
```

1. Script prints an authorization URL — open it in your browser
2. Log in to WHOOP and click **Authorize**
3. Browser redirects to `localhost:9527/callback` — script catches it automatically
4. Tokens saved ✅

#### 🌐 Remote Server (OpenClaw on VPS/server, browser on your laptop)

The server can't receive the `localhost:9527` callback from your browser. Two-step manual flow:

**Step A — Get the authorization URL:**

```bash
python3 scripts/auth.py --print-url
```

Open the printed URL in your **local browser**, log in and authorize.

**Step B — After authorizing, the browser redirects to `localhost:9527/callback?code=xxx&state=yyy` which won't load (that's fine!).**

Copy the full URL from your browser's address bar, then either:

```bash
# Option 1: Paste the full callback URL
python3 scripts/auth.py --callback-url "http://localhost:9527/callback?code=xxx&state=yyy"

# Option 2: Extract just the 'code' parameter
python3 scripts/auth.py --code "the-code-value"
```

**Or tell your agent:** paste the callback URL directly in chat, or save the code to 1Password — the agent can read it from there.

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
python3 scripts/sync.py --output-dir /tmp/whoop-data
```

Output: `~/.openclaw/workspace/health/whoop-YYYY-MM-DD.md`

## Cron (automated daily sync)

```bash
openclaw cron add \
  --name whoop-daily \
  --schedule "0 10 * * *" \
  --timezone Asia/Shanghai \
  --task "Run: python3 ~/.openclaw/workspace/skills/whoop/scripts/sync.py --days 2. Then read the generated markdown files and send me the latest day's report."
```

This syncs yesterday + today at 10:00 AM daily (WHOOP finalizes sleep data after waking).

## File Structure

```
skills/whoop/
├── SKILL.md              # This file
├── scripts/
│   ├── auth.py           # OAuth authorization (local + remote modes)
│   └── sync.py           # Daily sync + weekly reports
└── data/
    ├── tokens.json       # OAuth tokens (auto-refreshed, chmod 600)
    └── .auth_state       # Temp state for remote auth flow (auto-cleaned)
```

## Token Refresh — 授权一次，永久自动续期

**正常情况下只需授权一次，后续完全自动。**

工作原理：
- Access token 有效期 **1 小时**，每次 `sync.py` 运行时自动检测过期并 refresh
- Refresh token 是**滚动更新**的：每次刷新都会返回新的 refresh token，旧的作废
- 只要 cron 每天跑（每天至少 refresh 一次），token 链就永远不会断

什么时候需要重新授权：
- **WHOOP 端主动撤销**（你在 WHOOP app/网站里手动撤销了应用授权）
- **长时间未使用**（比如停了几个月没跑 sync，refresh token 可能过期）
- **WHOOP 更新了 OAuth 策略**（极少发生）

如果 sync.py 报 `Token refresh failed (403)`，重新跑一次 `auth.py` 即可。

> Token exchange 使用 `curl` 发请求，避免 Python urllib 被 WHOOP 的 Cloudflare CDN 拦截（error 1010）。

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No tokens found` | Run `auth.py` first |
| `Token refresh failed (403)` | Re-run `auth.py` to re-authorize |
| `Token exchange failed: 403` + `error code: 1010` | Cloudflare block — should be fixed (uses curl). If still failing, check network/proxy |
| `State mismatch` | You opened a different auth URL than what auth.py generated. Restart auth.py and use its URL |
| `No data for date` | WHOOP may not have data yet (sleep scores finalize after waking) |
| `1Password read failed` | Check `~/.openclaw/.op-token` exists, or use env vars instead |
| Port 9527 in use | `kill $(lsof -ti:9527)` then retry |

## Agent Notes

When the user asks to re-authorize WHOOP:
1. **Local**: run `auth.py` in background, capture its auth URL (use `-u` for unbuffered stdout), send the URL to the user
2. **Remote**: run `auth.py --print-url`, send the URL, then wait for user to provide the callback URL or code
3. After authorization, verify by running `sync.py --days 1` to confirm tokens work
