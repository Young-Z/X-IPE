# Template Placeholders Reference

Complete list of placeholders used in `component-visualization-template.html`.

---

## Placeholder Table

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
- JSON-LD structured data block for AI parsing
- No external dependencies except fonts

---

## Anti-Patterns

- Never leave `{{PLACEHOLDER}}` strings in generated files
- Never use RGB or HSL instead of hex colors
- Never skip semantic colors (success/warning/error/info)
- Never omit the CSS variables block
- Never omit JSON-LD structured data in visualization file
- Never generate only design-system.md without component-visualization.html
