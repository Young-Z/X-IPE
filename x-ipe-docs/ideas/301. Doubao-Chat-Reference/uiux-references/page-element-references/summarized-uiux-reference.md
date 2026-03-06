# UIUX Reference Summary — Doubao Chat

**Source:** https://www.doubao.com/chat/
**Captured:** 2026-03-05T14:09:28.065Z

---

## Color Palette

| Role | Hex | Usage |
|------|-----|-------|
| Background | `#ffffff` | Main content area |
| Sidebar Background | `#f3f4f6` | Left navigation panel |
| Primary | `#0057ff` | Active nav items, highlights |
| Accent | `#232629` | Login button, dark elements |
| Text Primary | `#000000` | Headings, body text |
| Chip Background | `rgba(0,0,0,0.04)` | Suggestion pill buttons |
| Secondary | `#0065fd` | Badges, links |
| Text Secondary | `rgba(0,0,0,0.85)` | Body text, button labels |
| Text Muted | `rgba(0,0,0,0.5)` | Footer links, icons |
| Text Dimmed | `rgba(0,0,0,0.3)` | Section labels, inactive elements |

## Typography

| Style | Size | Weight | Usage |
|-------|------|--------|-------|
| Heading XL | 28px | 600 | Hero greeting text |
| Body | 14px | 400-500 | Navigation items, buttons, chips |
| Label SM | 12px | 600 | Section labels (历史对话) |
| Label XS | 10px | 600 | Badges (Seedance 2.0, 新) |
| Font Family | system-ui, sans-serif | — | System default |

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| Pill/Button | 12px | Chips, buttons, nav items |
| Card | 24px | Chat input wrapper |
| Nav Item | 10px | Sidebar navigation items |
| Circle | 9999px | Avatar, attachment button |
| Badge | 4-6px | Small badges |

## Shadows

| Token | Value | Usage |
|-------|-------|-------|
| Input Wrapper | `0 2px 4px rgba(0,0,0,0.02), 0 4px 16px rgba(0,0,0,0.04), 0 8px 32px rgba(0,0,0,0.08)` | Chat input container — subtle 3-layer elevation |

## Layout Structure

```
┌─────────────────────────────────────────────────┐
│ ┌──────────┐ ┌────────────────────────────────┐ │
│ │ Sidebar  │ │ Header (dark-mode | download | │ │
│ │ 280px    │ │         login)                 │ │
│ │          │ ├────────────────────────────────┤ │
│ │ • Brand  │ │                                │ │
│ │ • 新对话  │ │   "你好，我是豆包"               │ │
│ │ • AI创作  │ │                                │ │
│ │ • 更多    │ │   [chip] [chip] [chip]         │ │
│ │          │ │   [chip] [chip] [chip]         │ │
│ │ 历史对话  │ │   [chip] [chip] [chip]         │ │
│ │          │ │                                │ │
│ │          │ │  ┌──────────────────────────┐  │ │
│ │          │ │  │ Chat Input (24px radius) │  │ │
│ │          │ │  │ [📎][⚡快速][🖼图像]...   │  │ │
│ │ 关于豆包  │ │  └──────────────────────────┘  │ │
│ └──────────┘ └────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## Key Design Patterns

1. **Sidebar + Main Split** — Fixed 280px sidebar (gray bg) + flexible main area (white bg)
2. **Centered Content** — Hero text + chips vertically centered in available space
3. **Suggestion Chips** — 3×3 grid of rounded pills with very subtle background (4% black)
4. **Floating Input** — Chat input has multi-layer shadow for depth, 24px border-radius
5. **Action Toolbar** — Horizontal scrollable row of feature buttons inside input wrapper
6. **Minimal Borders** — Relies on background color differences and shadows, not borders
7. **Active State** — Blue tint background + blue text for active sidebar items

## Static Resources

| Type | Description | Status |
|------|-------------|--------|
| Brand Avatar | 36×36 circular image | Not downloaded |
| SVG Icons | Navigation, toolbar, feature icons | Identified, not extracted |
| Font | system-ui (system default) | No custom fonts |
