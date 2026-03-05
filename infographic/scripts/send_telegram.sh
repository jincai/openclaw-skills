#!/bin/bash
# Send an image as a Telegram document (no compression).
#
# Usage: send_telegram.sh <image_path> [caption]
#
# Requires:
#   - TELEGRAM_BOT_TOKEN env var, OR openclaw.json with channels.telegram.botToken
#   - TELEGRAM_CHAT_ID env var, OR pass as 3rd argument

IMAGE_PATH="$1"
CAPTION="${2:-}"
CHAT_ID="${TELEGRAM_CHAT_ID:-$3}"

if [ -z "$IMAGE_PATH" ]; then
  echo "Usage: send_telegram.sh <image_path> [caption] [chat_id]"
  exit 1
fi

# Resolve bot token
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
  TELEGRAM_BOT_TOKEN=$(python3 -c "
import json, os
cfg = json.load(open(os.path.expanduser('~/.openclaw/openclaw.json')))
print(cfg['channels']['telegram']['botToken'])
" 2>/dev/null)
fi

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
  echo "Error: TELEGRAM_BOT_TOKEN not set and not found in openclaw.json"
  exit 1
fi

if [ -z "$CHAT_ID" ]; then
  echo "Error: Set TELEGRAM_CHAT_ID or pass chat_id as 3rd argument"
  exit 1
fi

RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendDocument" \
  -F chat_id="${CHAT_ID}" \
  -F document=@"${IMAGE_PATH}" \
  -F caption="${CAPTION}")

OK=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ok',''))" 2>/dev/null)

if [ "$OK" = "True" ]; then
  echo "✅ Sent to chat ${CHAT_ID}"
else
  echo "❌ Failed: $RESPONSE"
  exit 1
fi
