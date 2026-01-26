---
name: x-ipe-brand-theme-creator
description: Generate design-system.md and component-visualization.html files for custom X-IPE themes based on brand inputs. Use when user wants to create a new theme, define brand colors, or build a design system. Triggers on requests like "create theme", "new brand theme", "generate design system", "add custom theme".
---

# X-IPE Brand Theme Creator

Generate complete theme packages (`design-system.md` + `component-visualization.html`) for X-IPE themes based on brand inputs from multiple sources.

## Purpose

Transform brand colors, typography preferences, and style guidelines into:
1. **design-system.md** - Structured token definitions for AI agents
2. **component-visualization.html** - Visual preview for humans + JSON-LD for parsing

## Important Notes

- Output location: `x-ipe-docs/themes/theme-{name}/`
- Required files: `design-system.md`, `component-visualization.html`
- Theme names must use kebab-case with `theme-` prefix
- Minimum input: One accent/brand color (can be derived from web/image/text)
- Use theme-default as structural reference

---

## Input Sources

This skill accepts **three types of input sources** to extract brand information:

### 1. Web Link Input
Extract colors and styles from an existing website or brand page.

**Capabilities:**
- Use `web_fetch` tool or similar MCP capability to retrieve page content
- Extract primary brand colors from CSS, meta tags, or visible elements
- Identify font families from stylesheets
- Detect accent colors from buttons, links, and interactive elements
- Parse Open Graph or brand-specific meta tags

**Extraction Steps:**
1. Fetch the web page using `web_fetch` tool
2. Look for:
   - CSS variables in `:root` or body
   - `<meta name="theme-color" content="...">` tags
   - Primary brand colors in headers, navigation, CTAs
   - Font-family declarations in CSS
   - Button/link colors for accent extraction
3. Build color palette from extracted values

**Example:**
```
Input: "Create theme from https://stripe.com"
→ Extract: Primary (#0a2540), Accent (#635bff), Font (Söhne)
```

### 2. Image Input
Extract colors from brand assets, logos, or design mockups.

**Capabilities:**
- Analyze images to extract dominant colors
- Use Claude's vision capabilities to identify:
  - Primary brand colors
  - Accent/highlight colors
  - Background colors
  - Color relationships and contrast
- Suggest complementary colors for full palette

**Extraction Steps:**
1. Accept image file (logo, brand guide, screenshot)
2. Analyze using vision capabilities to identify:
   - Dominant colors (by area coverage)
   - Accent colors (small but prominent)
   - Text colors
   - Background colors
3. Extract hex values and map to theme tokens

**Example:**
```
Input: Company logo image (blue and orange)
→ Extract: Primary (#1e40af), Accent (#f97316), Neutral (#f8fafc)
```

### 3. Text Description Input
Generate colors from verbal brand descriptions.

**Capabilities:**
- Interpret color descriptions ("ocean blue", "forest green")
- Map adjectives to design characteristics:
  - "Professional" → Darker, more saturated primary
  - "Playful" → Brighter accents, larger radius
  - "Minimalist" → Subtle colors, smaller radius
  - "Bold" → High contrast, vibrant accents
- Suggest typography based on brand personality

**Interpretation Guide:**
| Description | Color Direction | Typography |
|-------------|-----------------|------------|
| Professional, Corporate | Dark blues/grays, subtle accents | Inter, SF Pro |
| Creative, Playful | Vibrant, warm accents | Poppins, Quicksand |
| Luxury, Premium | Deep colors, gold/bronze accents | Playfair Display, Cormorant |
| Tech, Modern | Cool blues/purples, clean lines | Space Grotesk, DM Sans |
| Natural, Organic | Greens, earth tones | Lora, Source Serif |
| Minimalist | Neutral grays, single accent | system-ui, Helvetica |

**Example:**
```
Input: "A warm, friendly brand for a coffee shop with earthy tones"
→ Generate: Primary (#44403c), Accent (#d97706), Neutral (#faf5f0)
```

---

## Input Collection

### From Direct Input
| Input | Required | Example |
|-------|----------|---------|
| Theme Name | Yes | `ocean`, `corporate`, `sunset` |
| Accent Color | Yes (or derived) | `#3b82f6` (blue) |

### From Source Extraction
| Source Type | How to Process |
|-------------|----------------|
| Web Link | Use `web_fetch` → parse CSS/HTML → extract colors |
| Image | Use vision analysis → extract dominant colors |
| Text | Interpret description → map to color palette |

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

### Step 1: Identify Input Source
Determine the input type and process accordingly:

**If Web Link provided:**
```
1. Use `web_fetch` tool to retrieve the page
2. Search for CSS variables, theme-color meta tags
3. Identify primary brand color (header/nav background)
4. Find accent color (buttons, links, CTAs)
5. Extract font families from stylesheets
6. Map extracted values to theme tokens
```

**If Image provided:**
```
1. Use vision capabilities to analyze the image
2. Identify dominant colors by area coverage
3. Detect accent colors (small but prominent)
4. Note any visible typography or font styles
5. Suggest color harmony (complementary, analogous)
6. Convert observations to hex values
```

**If Text Description provided:**
```
1. Parse adjectives and brand personality keywords
2. Map keywords to color direction (see interpretation guide)
3. Select base color family from Tailwind palette
4. Choose typography that matches brand voice
5. Set border radius based on personality (playful=larger, corporate=smaller)
```

### Step 2: Collect Additional Inputs
- Ask for theme name if not provided
- Confirm extracted colors with user
- Offer customization options (typography, radius)

### Step 3: Derive Missing Colors
- Apply color derivation rules for unspecified colors
- Select appropriate neutral scale (slate, gray, zinc, etc.)
- Ensure proper contrast ratios

### Step 4: Generate design-system.md
- Use template structure from [templates/design-system-template.md](templates/design-system-template.md)
- Fill in all token values
- Include component specs (buttons, cards, inputs)
- Add CSS variables block

### Step 5: Generate component-visualization.html
- Use template from [templates/component-visualization-template.html](templates/component-visualization-template.html)
- Replace all `{{PLACEHOLDERS}}` with actual values
- Include JSON-LD structured data with all tokens
- Ensure visual components render correctly

### Step 6: Create Theme Folder
- Create `x-ipe-docs/themes/theme-{name}/`
- Write `design-system.md`
- Write `component-visualization.html`

### Step 7: Verify Theme Discovery
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

### From Web Link:
```
User: "Create a theme from https://stripe.com"

Processing:
1. web_fetch("https://stripe.com")
2. Extract: Header=#0a2540, CTA=#635bff, Text=#425466, BG=#f6f9fc
3. Map to theme tokens

Output:
- Theme name: theme-stripe-inspired
- Primary: #0a2540 (from header)
- Accent: #635bff (from CTAs)
- Secondary: #425466 (from text)
- Neutral: #f6f9fc (from background)
```

### From Image:
```
User: "Create a theme from this logo" (teal + coral image)

Processing:
1. Vision analysis of image
2. Extract: Teal=#0d9488 (45%), Coral=#f97316 (15%), White=#fff (40%)
3. Map to theme tokens

Output:
- Theme name: theme-coral-teal
- Primary: #134e4a (darkened teal)
- Accent: #0d9488 (teal from logo)
- Neutral: #f0fdfa (light teal)
```

### From Text Description:
```
User: "Create a theme for a modern tech startup - clean, innovative, blue"

Processing:
1. Keywords: modern, tech, clean, innovative, blue
2. Map to: Cool blues, sans-serif fonts, medium radius

Output:
- Theme name: theme-tech-modern
- Primary: #0f172a (dark slate)
- Accent: #3b82f6 (blue-500)
- Secondary: #64748b (slate-500)
- Font: Space Grotesk
```

### Minimal (Accent Only):
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

### Input Processing
- ❌ Skipping `web_fetch` and guessing website colors
- ❌ Not confirming extracted colors with user
- ❌ Ignoring contrast when deriving from images
- ❌ Taking text descriptions too literally (e.g., "blue ocean" ≠ literal ocean color)

### Theme Generation
- ❌ Creating themes without `theme-` prefix
- ❌ Using RGB or HSL instead of hex colors
- ❌ Skipping semantic colors (success/warning/error/info)
- ❌ Missing CSS variables block
- ❌ Not checking accessibility contrast ratios
- ❌ Generating only design-system.md without component-visualization.html
- ❌ Leaving `{{PLACEHOLDER}}` strings in generated files
- ❌ Missing JSON-LD structured data in visualization file

### Best Practices
- ✅ Always fetch web content before extracting colors
- ✅ Use vision capabilities for accurate image color extraction
- ✅ Confirm extracted/interpreted colors with user before generation
- ✅ Verify accessibility contrast ratios after generation
- ✅ Generate both design-system.md AND component-visualization.html

## Example

See [references/examples.md](references/examples.md) for concrete theme generation examples.

## Templates

- [templates/design-system-template.md](templates/design-system-template.md) - Markdown structure
- [templates/component-visualization-template.html](templates/component-visualization-template.html) - HTML preview with placeholders
