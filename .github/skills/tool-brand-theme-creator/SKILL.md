---
name: tool-brand-theme-creator
description: Generate design-system.md and component-visualization.html files for custom X-IPE themes based on brand inputs. Use when user wants to create a new theme, define brand colors, or build a design system. Triggers on requests like "create theme", "new brand theme", "generate design system", "add custom theme".
---

# Brand Theme Creator

Generate complete theme packages (`design-system.md` + `component-visualization.html`) for X-IPE themes based on brand inputs.

## Purpose

Transform brand colors, typography preferences, and style guidelines into:
1. **design-system.md** - Structured token definitions for AI agents
2. **component-visualization.html** - Visual preview for humans + JSON-LD for parsing

## Important Notes

- Output location: `docs/themes/theme-{name}/`
- Required files: `design-system.md`, `component-visualization.html`
- Theme names must use kebab-case with `theme-` prefix
- Minimum input: One accent/brand color
- Use theme-default as structural reference

## Input Collection

Gather these inputs from user (provide sensible defaults if not specified):

### Required
| Input | Description | Example |
|-------|-------------|---------|
| Theme Name | Kebab-case identifier | `ocean`, `corporate`, `sunset` |
| Accent Color | Primary brand/CTA color | `#3b82f6` (blue) |

### Optional (with defaults)
| Input | Default | Description |
|-------|---------|-------------|
| Primary Color | Derived dark shade | Main text color |
| Secondary Color | Derived medium shade | Secondary text |
| Neutral Color | Derived light shade | Backgrounds, borders |
| Heading Font | `Inter` | Font for headings |
| Body Font | `system-ui` | Font for body text |
| Code Font | `JetBrains Mono` | Font for code |
| Border Radius | `8px` (md) | Default corner rounding |

## Color Derivation

When only accent color provided, derive others:

```
Given: Accent = #3b82f6 (blue)

1. Primary: Darken accent by 40% → #1e3a5f (dark blue)
2. Secondary: Desaturate + darken by 20% → #64748b (slate)
3. Neutral: Very light tint of accent → #e0f2fe (light blue)
4. Semantic colors: Use standard palette (green/amber/red/blue)
```

For neutral scale, use Tailwind color scales closest to derived colors.

## Execution Procedure

1. **Collect Inputs**
   - Ask for theme name and accent color (minimum)
   - Offer to customize typography, radius, other colors

2. **Derive Missing Colors**
   - Apply color derivation rules for unspecified colors
   - Select appropriate neutral scale (slate, gray, zinc, etc.)

3. **Generate design-system.md**
   - Use template structure from [templates/design-system-template.md](templates/design-system-template.md)
   - Fill in all token values
   - Include component specs (buttons, cards, inputs)
   - Add CSS variables block

4. **Generate component-visualization.html**
   - Use template from [templates/component-visualization-template.html](templates/component-visualization-template.html)
   - Replace all `{{PLACEHOLDERS}}` with actual values
   - Include JSON-LD structured data with all tokens
   - Ensure visual components render correctly

5. **Create Theme Folder**
   - Create `docs/themes/theme-{name}/`
   - Write `design-system.md`
   - Write `component-visualization.html`

6. **Verify Theme Discovery**
   - Confirm theme appears in `/api/themes` response
   - Test that 4 color swatches display correctly

## Template Placeholders

When generating `component-visualization.html`, replace these placeholders:

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

## Output Structure

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

## Quick Generation

For rapid theme creation with minimal input:

```
User: "Create a theme called ocean with accent #0ea5e9"

Output:
- Theme name: theme-ocean
- Accent: #0ea5e9 (sky-500)
- Primary: #0c4a6e (sky-900) 
- Secondary: #475569 (slate-600)
- Neutral: #e0f2fe (sky-100)
- Scale: Sky + Slate
```

## Anti-Patterns

- ❌ Creating themes without `theme-` prefix
- ❌ Using RGB or HSL instead of hex colors
- ❌ Skipping semantic colors (success/warning/error/info)
- ❌ Missing CSS variables block
- ❌ Not checking accessibility contrast ratios
- ❌ Generating only design-system.md without component-visualization.html
- ❌ Leaving `{{PLACEHOLDER}}` strings in generated files
- ❌ Missing JSON-LD structured data in visualization file

## Example

See [references/examples.md](references/examples.md) for concrete theme generation examples.

## Templates

- [templates/design-system-template.md](templates/design-system-template.md) - Markdown structure
- [templates/component-visualization-template.html](templates/component-visualization-template.html) - HTML preview with placeholders
