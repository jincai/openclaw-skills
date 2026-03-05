# Infographic Design System

## Color Palette

### Section Accent Colors (for numbered circles, badges, borders)
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
| White       | `#ffffff` | Card background |
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
| Light | `#cccccc` | Text on dark background |
| Gold  | `#f5c542` | Accent text on dark background |

## Typography

```css
font-family: -apple-system, 'PingFang SC', 'Noto Sans SC', 'Helvetica Neue', sans-serif;
```

### Scale
| Element | Size | Weight |
|---------|------|--------|
| Main title | 28-32px | 900 |
| Subtitle | 15-17px | 400 |
| Section title | 14-15px | 800 |
| Body text | 12.5-13px | 400 |
| Small text (English, labels) | 11-12px | 400 |
| Footer | 10-12px | 400/700 |
| Minimum size | 12px | — |

## Layout Patterns

### Page Structure
```
┌─────────────────────────┐
│       HEADER            │  Badge + Title + Subtitle
│    ─────────────        │  Divider line
├─────────────────────────┤
│  CALLOUT BOX            │  Yellow bg, gold left border
├────────────┬────────────┤
│  CARD 1    │  CARD 2    │  2-column grid (optional)
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

### Numbered Card Pattern
```
┌──┐ ┌────────────────────┐
│ 1│ │ 🔍 Section Title   │
│  │ │ English subtitle    │
└──┘ │ Body text here...   │
     └────────────────────┘
```
- Left: colored circle (44px) with white number
- Right: white card with border, rounded corners (12px)
- Shadow: `3px 3px 0 rgba(0,0,0,0.05)`

### Callout/Quote Box
```css
background: #fffbe6;
border-left: 4px solid #f5c542;
border-radius: 0 10px 10px 0;
padding: 14px 18px;
```

### Takeaway Section
```css
background: #1a1a1a;
color: #faf6f0;
border-radius: 14px;
padding: 22px 24px;
```

## Component Library

### Badge
```html
<div style="display:inline-block; background:#222; color:#faf6f0;
  font-size:11px; padding:4px 14px; border-radius:12px; letter-spacing:2px;">
  BADGE TEXT
</div>
```

### 2×2 Grid Card
```html
<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
  <div style="border-radius:10px; padding:12px; background:#EBF3FB;">
    <div style="font-size:14px; font-weight:800; color:#4A90D9;">Label</div>
    <div style="font-size:12px; font-weight:700;">Title</div>
    <div style="font-size:11.5px; color:#666;">Description</div>
  </div>
  <!-- repeat -->
</div>
```

### Dark Pattern Cards (for bottom section)
```html
<div style="flex:1; background:#222; color:#fff; border-radius:8px;
  padding:10px; text-align:center;">
  <div style="font-size:16px;">🎯</div>
  <div style="font-size:12px; font-weight:700;">Name</div>
  <div style="font-size:10px; color:#aaa;">Description</div>
</div>
```

## Spacing Rules
- Page padding: `44-48px` top/bottom, `38-42px` sides
- Card padding: `14-16px`
- Grid gap: `14-16px`
- Section margin-bottom: `16-24px`
- No fixed height — content determines page length
