# Mimic Strategy — Doubao Chat

**Source:** https://www.doubao.com/chat/
**Target Accuracy:** 99%

---

## 6-Dimension Validation Rubric

### 1. Layout ✅ Confident

| Aspect | Reference Value | Validation |
|--------|----------------|------------|
| Overall | Sidebar (280px fixed) + Main (flex-1) horizontal split | Must match exact widths |
| Sidebar | flex-col, 12px padding, full viewport height | Check padding, overflow |
| Main | flex-col, centered content, bottom-pinned input | Verify vertical centering |
| Header | flex-row, space-between, 56px height, z-index:30 | Right-aligned buttons |
| Chip Grid | 3 rows × 3 columns, centered, 8px gaps | Check wrap behavior |
| Input | 800px width, centered, 124px height | Must be bottom-positioned |

### 2. Typography ✅ Confident

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| Hero Heading | system-ui | 28px | 600 | rgb(0,0,0) |
| Nav Items | system-ui | 14px | 400 | rgba(0,0,0,0.85) |
| Active Nav | system-ui | 14px | 600 | rgb(0,87,255) |
| Suggestion Chips | system-ui | 14px | 400 | rgb(0,0,0) |
| Section Labels | system-ui | 12px | 600 | rgba(0,0,0,0.3) |
| Badge Text | system-ui | 10px | 600 | rgb(0,101,253) |
| Button Text | system-ui | 14px | 500 | varies |
| Placeholder | system-ui | 16px | 400 | rgba(0,0,0,0.35) |

### 3. Color Palette ✅ Confident

| Token | Value | Must Match |
|-------|-------|------------|
| Main BG | #ffffff | Exact |
| Sidebar BG | #f3f4f6 | Exact |
| Primary Blue | #0057ff | Exact (active items) |
| Primary Blue BG | rgba(0,87,255,0.06) | Exact (active item bg) |
| Dark Accent | #232629 | Exact (login button) |
| Chip BG | rgba(0,0,0,0.04) | Exact |
| Secondary Blue | #0065fd | Exact (badges) |
| Text Primary | #000000 | Exact |
| Text Secondary | rgba(0,0,0,0.85) | Exact |
| Text Muted | rgba(0,0,0,0.5) | Exact |
| Text Dimmed | rgba(0,0,0,0.3) | Exact |

### 4. Spacing ✅ Confident

| Element | Property | Value |
|---------|----------|-------|
| Sidebar | padding | 12px |
| Brand Logo | margin-bottom | 16px |
| Nav Items | height | 38px |
| Nav Items | gap | 6px |
| Chip Grid | gap (row & col) | 8px |
| Chip | height | 42px |
| Chip | padding | 0 16px |
| Input Wrapper | border-radius | 24px |
| Buttons | border-radius | 12px |
| Header | height | 56px |
| Toolbar Buttons | height | 32px |
| Toolbar | gap | 4px |

### 5. Visual Effects ✅ Confident

| Effect | Value | Validation |
|--------|-------|------------|
| Input Shadow | `0 2px 4px rgba(0,0,0,0.02), 0 4px 16px rgba(0,0,0,0.04), 0 8px 32px rgba(0,0,0,0.08)` | 3-layer subtle shadow |
| Chip Hover | Likely slight bg change | Verify on hover |
| Active Nav BG | rgba(0,87,255,0.06) | Tinted blue background |
| Border Radius | 12px (pills), 24px (cards), 10px (nav) | Consistent roundedness |
| No Hard Borders | Uses background-color differences, not borders | Clean, borderless design |

### 6. Static Resources ⚠️ Uncertain

| Resource | Status | Action Needed |
|----------|--------|---------------|
| Brand Avatar (36×36) | Not captured | Download or use placeholder |
| SVG Icons | Identified but not extracted | Extract from page or use equivalents |
| Custom Fonts | None (system-ui) | No action needed |

---

## Critical Mimic Notes

1. **Sidebar gray is NOT pure gray** — it's `#f3f4f6` (slight blue tint), not `#f0f0f0`
2. **Active blue is NOT standard blue** — it's `#0057ff`, distinct from typical `#007bff`
3. **Chip background is semi-transparent black** — `rgba(0,0,0,0.04)`, not a solid gray
4. **Input shadow has 3 layers** — each progressively stronger and wider
5. **Login button is near-black** — `#232629`, not pure black
6. **Text colors use 4 opacity levels** — 1.0, 0.85, 0.5, 0.3 on black base
7. **No horizontal borders between sidebar items** — clean separation via spacing only
