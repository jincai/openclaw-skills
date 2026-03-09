# Infographic Design System

## Core Design Philosophy (from Impeccable)

**Bold intentionality over safe defaults.** Every design choice must be deliberate — commit to a clear aesthetic direction and execute with precision. Avoid "AI slop": generic gradients, cyan-on-dark, purple-to-blue, neon accents.

**The Squint Test:** Blur your eyes. Can you still identify the most important element, the second most important, and clear groupings? If everything looks the same weight, you have a hierarchy problem.

**Less is more:** Fewer sizes with more contrast beats many similar sizes. A 5-level hierarchy covers all needs.

## Color Palette

### Design Principles
- **Never use pure black (#000) or pure white (#fff)** — always tint; pure extremes never appear in nature
- **Tint neutrals toward your accent hue** — even subtle 1% chroma creates subconscious cohesion
- **Dominant color + sharp accent > evenly distributed palette** — commit, don't hedge
- **Reduce saturation at extremes** — light/dark variants need lower chroma to avoid garish results
- **No gray text on colored backgrounds** — use a shade of the background color instead

### Section Accent Colors
| Name   | Hex       | Use Case |
|--------|-----------|----------|
| Blue   | `#4A90D9` | Section 1, trust/tech |
| Orange | `#E8734A` | Section 2, energy/action |
| Green  | `#5BB978` | Section 3, growth/positive |
| Purple | `#9B6BB9` | Section 4, creativity |
| Gold   | `#E8A84A` | Section 5, highlight/warning |
| Red    | `#D94A6B` | Section 6, urgent/important |
| Teal   | `#3AAFA9` | Section 7, calm/balance |

### Background Colors
| Name        | Hex       | Use Case |
|-------------|-----------|----------|
| Cream       | `#faf6f0` | Page background (paper feel) |
| White       | `#fefefe` | Card background (tinted, not pure) |
| Light Blue  | `#EBF3FB` | Highlight box |
| Light Orange| `#FDF0EB` | Highlight box |
| Light Green | `#EDF7F0` | Highlight box |
| Light Purple| `#F3EDF7` | Highlight box |
| Yellow      | `#fffbe6` | Callout/quote box |
| Dark        | `#1a1a1a` | Takeaway section background |

### Text Colors
| Name  | Hex       | Use Case |
|-------|-----------|----------|
| Black | `#1a1a1a` | Headings, primary text |
| Dark  | `#333333` | Subheadings |
| Body  | `#444444` | Body text |
| Muted | `#888888` | Subtitles, English labels |
| Light | `#e8e4df` | Text on dark background (tinted cream, not pure white) |
| Gold  | `#f5c542` | Accent text on dark background |

## Typography

### Font Stack
```css
font-family: -apple-system, 'PingFang SC', 'Noto Sans SC', 'Helvetica Neue', sans-serif;
```

### Design Principles
- **Use fewer sizes with more contrast** — muddy hierarchy comes from too many similar sizes (14, 15, 16, 18...)
- **Vertical rhythm**: line-height is the base unit for ALL vertical spacing; spacing should be multiples of it
- **Weight creates hierarchy**: Bold (800-900) vs Regular (400) is more effective than slight size differences
- **Increase line-height for light-on-dark text** — perceived weight is lighter, needs more breathing room

### Scale (5-level hierarchy, clear contrast between each)
| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| Main title | 28-32px | 900 | 1.2 |
| Section title | 15-16px | 800 | 1.3 |
| Body text | 13px | 400 | 1.6 |
| Small text (English, labels) | 11-12px | 400 | 1.4 |
| Minimum size | 12px | — | — |

**Ratio**: Title-to-body is roughly 2.2:1 — enough contrast to create clear hierarchy at a glance.

## Spatial Design

### Principles
- **Use 4pt base grid**: 4, 8, 12, 16, 24, 32, 48px — more granular than 8pt
- **Use `gap` for sibling spacing** — eliminates margin collapse issues
- **Generous whitespace signals quality** — cramped layouts feel cheap
- **Group related items tightly, separate groups generously** — proximity = relationship

### Spacing Rules
| Element | Value |
|---------|-------|
| Page padding (top/bottom) | 44-48px |
| Page padding (sides) | 38-42px |
| Card padding | 14-16px |
| Grid gap | 14-16px |
| Section margin-bottom | 20-28px |
| Between tightly related items | 4-8px |
| Between distinct groups | 24-32px |

### Key Rule
No fixed page height — content determines length. No empty filler space at bottom.

## Layout Patterns

### Page Structure
```
┌─────────────────────────┐
│       HEADER            │  Badge + Title + Subtitle
│    ─────────────        │  Divider line
├─────────────────────────┤
│  CALLOUT BOX            │  Yellow bg, gold left border
├────────────┬────────────┤
│  CARD 1    │  CARD 2    │  2-column grid
├────────────┴────────────┤
│  FULL-WIDTH CARD        │  Spans both columns
├─────────────────────────┤
│  CARD 3    │  CARD 4    │  Continue grid
├─────────────────────────┤
│  ██ TAKEAWAY BOX ██     │  Dark background
├─────────────────────────┤
│       FOOTER            │  Source + Brand
└─────────────────────────┘
```

### Hierarchy Through Multiple Dimensions (not size alone)
| Tool | Strong | Weak |
|------|--------|------|
| Size | 3:1 ratio+ | <2:1 |
| Weight | Bold vs Regular | Medium vs Regular |
| Color | High contrast | Similar tones |
| Position | Top/left (primary) | Bottom/right |
| Space | Surrounded by whitespace | Crowded |

**Combine at least 3 dimensions** for any important element.

### Numbered Card Pattern
```
┌──┐ ┌────────────────────┐
│ 1│ │ Section Title      │
│  │ │ English subtitle    │
└──┘ │ Body text here...   │
     └────────────────────┘
```
- Left: colored circle (44px) with white number
- Right: white card with subtle border, rounded corners (12px)
- Shadow: `3px 3px 0 rgba(0,0,0,0.05)` — subtle, not heavy

### Callout/Quote Box
```css
background: #fffbe6;
border-left: 4px solid #f5c542;
border-radius: 0 10px 10px 0;
padding: 14px 18px;
```

### Takeaway Section (dark)
```css
background: #1a1a1a;
color: #e8e4df;          /* tinted cream, not pure white */
border-radius: 14px;
padding: 22px 24px;
line-height: 1.7;        /* extra breathing room on dark bg */
```

## Component Library

### Badge
```html
<div style="display:inline-block; background:#222; color:#e8e4df;
  font-size:11px; padding:4px 14px; border-radius:12px; letter-spacing:2px;
  font-weight:600;">
  BADGE TEXT
</div>
```

### 2-Column Grid
```html
<div style="display:grid; grid-template-columns:1fr 1fr; gap:14px;">
  <div style="border-radius:10px; padding:14px; background:#EBF3FB;">
    <div style="font-size:15px; font-weight:800; color:#4A90D9;">Label</div>
    <div style="font-size:13px; color:#444; margin-top:6px;">Description</div>
  </div>
</div>
```

### Dark Bottom Cards
```html
<div style="flex:1; background:#222; color:#e8e4df; border-radius:8px;
  padding:12px; text-align:center;">
  <div style="font-size:15px; font-weight:800;">Title</div>
  <div style="font-size:12px; color:#aaa; margin-top:4px;">Description</div>
</div>
```

## Anti-Patterns (Never Do)

- ❌ Emoji as section icons (use colored shapes, SVG, or text symbols instead)
- ❌ Pure black/white anywhere
- ❌ Gradient text for "impact" — decorative, not meaningful
- ❌ Cyan-on-dark, purple-to-blue gradients, neon accents (AI slop aesthetics)
- ❌ Dark mode with glowing accents as default
- ❌ Gray text on colored backgrounds
- ❌ Many similar font sizes (14, 15, 16, 17...) — pick 5 and commit
- ❌ Evenly distributed colors — commit to a dominant + accent
- ❌ Heavy drop shadows — keep shadows subtle or use none
- ❌ Marketing-style flashy layouts (floating decorations, scattered icons, over-the-top gradients)

## Style Presets

### Default: Clean Editorial
Cream background, clear hierarchy, numbered cards, professional but warm.

### Blueprint (爷's preferred)
Blue-tinted scheme, engineering/spec-sheet feel, structured grid, monospace labels for data points. Use when content is technical or data-heavy.

### Minimal
Maximum whitespace, 2-3 colors only, large typography, few elements per section. Use for short/impactful content.
