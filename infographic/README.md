# infographic

Generate professional, mobile-friendly infographic images from articles, tweets, or any structured content using HTML + Playwright high-DPI screenshot.

## What it does

When you ask Claude things like:

- "这篇文章生成一张信息图"
- "帮我做一张可以发微信群的总结图"
- "create an infographic from this article"
- "make a visual summary for social media"

This skill designs an HTML page with a structured layout (header → callout → numbered cards → takeaway → footer), then takes a 3x Retina screenshot to produce a crisp PNG optimized for mobile viewing.

## Features

- **Mobile-optimized**: 750px CSS width × 3x DPI = 2250px physical — sharp on any phone
- **Chinese-first**: Uses system PingFang SC / Noto Sans SC — zero external font dependencies
- **Self-contained HTML**: No CDN, no Google Fonts, works fully offline
- **Design system included**: Consistent color palette, typography scale, and reusable components
- **Telegram lossless delivery**: Bundled script sends via `sendDocument` API to bypass Telegram's image compression (which caps at 2048px)
- **Content-adaptive height**: No fixed page height — image is exactly as tall as the content

## Example output

A typical infographic from a 7-point article produces a ~2250×5300px PNG at ~800KB.

## Usage

### With Claude (recommended)

Just share an article and say "生成信息图" — Claude reads the skill and handles everything automatically.

### Standalone

```bash
# 1. Write your HTML infographic (see references/design-system.md for components)

# 2. Take a high-DPI screenshot
node scripts/screenshot.js input.html output.png 3 750
# → output.png at 2250px wide, 3x DPI

# 3. (Optional) Send to Telegram without compression
export TELEGRAM_CHAT_ID="your_chat_id"
bash scripts/send_telegram.sh output.png "Caption text"
```

### Screenshot script options

```
node scripts/screenshot.js <input.html> <output.png> [scaleFactor] [viewportWidth]

  input.html      Path to the HTML file
  output.png      Output PNG path
  scaleFactor     Device pixel ratio (default: 3)
  viewportWidth   CSS viewport width (default: 750)
```

## File structure

```
infographic/
├── SKILL.md                  # Instructions for Claude
├── README.md                 # This file
├── references/
│   └── design-system.md      # Color palette, typography, component library
└── scripts/
    ├── screenshot.js          # Playwright high-DPI screenshot tool
    └── send_telegram.sh       # Telegram lossless image delivery
```

## Requirements

- **Node.js** (v18+)
- **Playwright** with Chromium: `npx playwright install chromium`
- For Telegram delivery: `curl` + Telegram bot token

## Design philosophy

1. **Scannable, not readable** — infographics are glanced at, not studied
2. **Visual hierarchy** — eyes flow naturally: title → callout → cards → takeaway
3. **Consistent color coding** — 7 accent colors, one per section
4. **Mobile-first** — designed for WeChat/Telegram/Twitter sharing
5. **Self-contained** — single HTML file, no external dependencies

## License

MIT
