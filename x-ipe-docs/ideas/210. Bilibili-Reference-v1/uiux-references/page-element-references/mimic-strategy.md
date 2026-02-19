# Mimic Strategy — Bilibili Homepage

## 6-Dimension Validation Rubric

### 1. Layout ✅ Confident
- Grid-based category navigation (2 rows, 10px gap)
- Flex layout for icon buttons (46px circles) and sidebar links
- Content split: 565px carousel left + 3×2 video grid right
- Video cards: 273×228px, flex-column
- Page-level padding: 0 140px on header channel

### 2. Typography ✅ Confident
- System font stack: PingFang SC, HarmonyOS_Regular, Helvetica Neue, Microsoft YaHei, sans-serif
- Title: 15px/500 weight, Author: 13px, Category: 14px/400
- Stats overlay: 13px white on dark gradient
- Line-height: 22px for titles, standard for body

### 3. Color Palette ✅ Confident
- Neutral grays: #18191c (text), #61666d (secondary), #9499a0 (tertiary)
- Backgrounds: #fff (sections), #f1f2f3 (page), #f6f7f8 (tags)
- Accent: #ff9212 (dynamic icon orange), #f07775 (popular icon coral)
- Stats overlay: linear-gradient transparent to 80% black

### 4. Spacing ✅ Confident
- Category grid gap: 10px
- Header channel padding: 0 140px
- Category pill: 74×30px centered text
- Stats overlay padding: 16px 8px 6px
- Card info section: minimal padding

### 5. Visual Effects ✅ Confident
- Border-radius: 6px on category pills, video covers, carousel
- Icon circles: 50% border-radius (perfect circles)
- Carousel arrows: 8px border-radius, semi-transparent white bg
- Stats gradient overlay: rgba(0,0,0,0) to rgba(0,0,0,0.8)
- No box-shadows on cards (flat design)

### 6. Static Resources ✅ Confident
- System fonts only (no custom @font-face)
- Video thumbnails from hdslb.com CDN (672×378)
- Carousel banners from hdslb.com CDN (976×550)
- SVG icons inline for play/danmaku/duration/category icons

## Mimic Priority

1. **Category pill grid** — Most distinctive element. 2-row grid with exact border, bg, border-radius
2. **Video card with stats overlay** — Gradient overlay on thumbnail bottom is signature Bilibili style
3. **Icon buttons** — Orange/coral circles with labels are brand-specific
4. **Color palette** — Neutral gray system with specific accent colors
5. **Typography hierarchy** — 15px/500 title → 13px secondary info pattern
