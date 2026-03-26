# Template Placeholders Reference

Complete list of placeholders used in `component-visualization-template.html`.

---

## Placeholder Table

### Core Token Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{THEME_NAME}}` | Display name | Ocean Theme |
| `{{THEME_ID}}` | kebab-case ID | ocean |
| `{{DESCRIPTION}}` | One-line description | A calm, aquatic theme |
| `{{PRIMARY}}` | Primary hex color | #0c4a6e |
| `{{SECONDARY}}` | Secondary hex color | #475569 |
| `{{ACCENT}}` | Accent hex color | #0ea5e9 |
| `{{NEUTRAL}}` | Neutral hex color | #e0f2fe |
| `{{SUCCESS}}` | Success color | #22c55e |
| `{{WARNING}}` | Warning color | #f59e0b |
| `{{ERROR}}` | Error color | #ef4444 |
| `{{INFO}}` | Info color | #3b82f6 |
| `{{SCALE_NAME}}` | Neutral scale name | Sky |
| `{{SCALE_PREFIX}}` | CSS variable prefix | sky |
| `{{SCALE_50}}` through `{{SCALE_900}}` | Scale values | #f0f9ff, etc. |
| `{{HEADING_FONT}}` | Heading font family | Inter |
| `{{HEADING_FONT_ENCODED}}` | URL-encoded font | Inter |
| `{{BODY_FONT}}` | Body font family | system-ui, sans-serif |
| `{{RADIUS_SM}}` | Small radius | 4px |
| `{{RADIUS_MD}}` | Medium radius | 8px |
| `{{RADIUS_LG}}` | Large radius | 12px |
| `{{ACCENT_LIGHT_BG}}` | Accent hover (10% opacity) | rgba(14, 165, 233, 0.1) |
| `{{ACCENT_FOCUS_RING}}` | Focus ring (15% opacity) | rgba(14, 165, 233, 0.15) |

### Component Placeholders

| Placeholder | Description | Default | Example |
|-------------|-------------|---------|---------|
| `{{BTN_PADDING}}` | Button padding | 12px 24px | 10px 20px |
| `{{BTN_RADIUS}}` | Button border-radius | uses {{RADIUS_MD}} | 8px |
| `{{BTN_FONT_WEIGHT}}` | Button font weight | 600 | 500 |
| `{{BTN_FONT_SIZE}}` | Button font size | 14px | 15px |
| `{{BTN_SHADOW}}` | Button box-shadow | 0 1px 2px 0 rgb(0 0 0 / 0.05) | none |
| `{{BTN_HOVER_DARKEN}}` | Button hover background | accent-dark | #4f46e5 |
| `{{BTN_SECONDARY_BG}}` | Secondary button background | scale-100 | #f1f5f9 |
| `{{BTN_SECONDARY_BORDER}}` | Secondary button border color | scale-200 | #e2e8f0 |
| `{{CARD_RADIUS}}` | Card border-radius | 12px | 16px |
| `{{CARD_PADDING}}` | Card padding | 24px | 20px |
| `{{CARD_SHADOW}}` | Card box-shadow | 0 1px 2px 0 rgb(0 0 0 / 0.05) | 0 4px 6px -1px rgb(0 0 0 / 0.1) |
| `{{CARD_BORDER}}` | Card border | 1px solid scale-200 | none |
| `{{INPUT_RADIUS}}` | Input border-radius | uses {{RADIUS_MD}} | 8px |
| `{{INPUT_PADDING}}` | Input padding | 12px 16px | 10px 14px |
| `{{INPUT_BORDER}}` | Input border color | scale-200 | #d1d5db |
| `{{INPUT_FOCUS_RING}}` | Input focus ring | 0 0 0 3px accent 26% | 0 0 0 2px accent 20% |
| `{{LINK_COLOR}}` | Link color | uses {{ACCENT}} | #3b82f6 |
| `{{LINK_HOVER_COLOR}}` | Link hover color | accent-dark | #2563eb |
| `{{LINK_DECORATION}}` | Link text-decoration | none | underline |
| `{{LINK_HOVER_DECORATION}}` | Link hover text-decoration | underline | none |
| `{{BADGE_BG}}` | Badge background | accent-light-bg | rgba(59, 130, 246, 0.1) |
| `{{BADGE_COLOR}}` | Badge text color | accent-dark | #1d4ed8 |
| `{{BADGE_PADDING}}` | Badge padding | 2px 8px | 4px 12px |
| `{{BADGE_RADIUS}}` | Badge border-radius | 9999px | 4px |
| `{{BADGE_FONT_SIZE}}` | Badge font size | 12px | 11px |
| `{{NAV_HEIGHT}}` | Navigation height | 64px | 56px |
| `{{NAV_BG}}` | Navigation background | #ffffff | #0a2540 |
| `{{NAV_PADDING}}` | Navigation item padding | 0 16px | 0 12px |
| `{{NAV_ITEM_GAP}}` | Navigation item gap | 24px | 16px |

---

## Output File Structure

### design-system.md

```markdown
# Design System: {Theme Name}

{One-line description of the theme's character}

---

## Core Tokens

### Color Palette
#### Primary Colors
#### Neutral Scale
#### Semantic Colors
#### Accent Variants

### Typography
#### Font Families
#### Font Sizes
#### Font Weights
#### Line Heights

### Spacing
### Border Radius
### Shadows

---

## Component Specs
### Buttons
### Cards
### Form Inputs
### Links
### Badges
### Navigation

---

## Usage Guidelines
### Accessibility
### Best Practices

---

## CSS Variables
```

### component-visualization.html

Self-contained HTML file with:
- All CSS variables in `:root`
- Google Fonts CDN import (heading font + JetBrains Mono)
- Visual sections: Color palette, Typography, Spacing, Border radius, Shadows, Components
- JSON-LD structured data block for AI parsing (including component specs)
- No external dependencies except fonts

---

## Anti-Patterns

- Never leave `{{PLACEHOLDER}}` strings in generated files
- Never use RGB or HSL instead of hex colors
- Never skip semantic colors (success/warning/error/info)
- Never omit the CSS variables block
- Never omit JSON-LD structured data in visualization file
- Never generate only design-system.md without component-visualization.html
- Never skip component specs section — always include at least buttons, cards, and inputs
