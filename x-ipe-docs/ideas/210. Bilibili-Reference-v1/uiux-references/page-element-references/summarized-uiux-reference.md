# UIUX Reference Summary — Bilibili Homepage

**Source:** https://www.bilibili.com/
**Captured:** 2026-02-16T03:08:38Z
**Area:** Header channel section + video feed (1517×589px)

---

## Typography

| Token | Value |
|-------|-------|
| Font Family | PingFang SC, HarmonyOS_Regular, Helvetica Neue, Microsoft YaHei, sans-serif |
| Title (video) | 15px / weight 500 / line-height 22px / color rgb(24,25,28) |
| Category Link | 14px / weight 400 / color rgb(97,102,109) |
| Author Info | 13px / color rgb(148,153,160) |
| Stats Overlay | 13px / color rgb(255,255,255) |

## Color Palette

| Role | Value | Usage |
|------|-------|-------|
| Text Primary | rgb(24, 25, 28) | Titles, main text |
| Text Secondary | rgb(97, 102, 109) | Category links, sidebar links |
| Text Tertiary | rgb(148, 153, 160) | Author info, dates |
| BG Primary | rgb(255, 255, 255) | Header channel section |
| BG Secondary | rgb(241, 242, 243) | Page body background |
| BG Tag | rgb(246, 247, 248) | Category pill background |
| Border Tag | rgb(241, 242, 243) | Category pill border |
| Icon Dynamic | rgb(255, 146, 18) | 动态 orange circle |
| Icon Popular | rgb(240, 119, 117) | 热门 coral/pink circle |
| White on Dark | rgb(255, 255, 255) | Stats text on gradient overlay |
| Gradient Overlay | linear-gradient(rgba(0,0,0,0), rgba(0,0,0,0.8)) | Thumbnail bottom stats |

## Layout Structure

- **Header Channel Section** (1723×120px, white bg, padding: 0 140px)
  - Left: Icon buttons (动态 orange + 热门 pink, 46×46px circles)
  - Center: Category grid (2 rows, ~14 items/row, 10px gap)
  - Right: Sidebar links (专栏, 直播, etc.)
- **Content Section** (below channel)
  - Left: Hero carousel (565×477px, border-radius 6px)
  - Right: Video card grid (3 columns × 2 rows, 273×228px each)
  - Far right: Refresh button (换一换)

## Key Components

1. **Category Pill** — Rounded tag (border-radius:6px, 74×30px, light gray bg, 1px border)
2. **Video Card** — Thumbnail + gradient stats overlay + title + author (273×228px)
3. **Stats Overlay** — Gradient black overlay at thumbnail bottom (38px, play/danmaku/duration)
4. **Hero Carousel** — Featured banner with dots pagination + arrow navigation
5. **Icon Buttons** — Colored circles (46px) with white SVG icons + text labels below

## Resources

- Video thumbnails: `i0.hdslb.com/bfs/archive/*.jpg` (672×378 covers)
- Carousel banners: `i0.hdslb.com/bfs/banner/*.png` (976×550 slides)
- No custom fonts (system fonts only)
