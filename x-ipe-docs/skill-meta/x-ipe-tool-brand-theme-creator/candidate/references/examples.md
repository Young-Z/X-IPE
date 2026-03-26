# Examples: X-IPE Brand Theme Creator

## Example 1: Web Link Input

**User Request:**
> "Create a theme based on https://stripe.com"

**Processing Steps:**
1. Fetch web page using `web_fetch`
2. Extract CSS variables and computed styles
3. Identify brand colors from navigation, buttons, backgrounds

**Extracted Values:**
```
From Stripe.com:
- Header/Nav: #0a2540 (dark navy)
- CTA Buttons: #635bff (purple/indigo)
- Body text: #425466 (gray-blue)
- Background: #f6f9fc (light gray)
- Font: Söhne (fallback to Inter)
```

**Color Mapping:**
```
Primary:   #0a2540  (extracted from header)
Secondary: #425466  (extracted from body text)
Accent:    #635bff  (extracted from CTA buttons)
Neutral:   #f6f9fc  (extracted from background)
```

**Generated Theme:** `theme-stripe-inspired`

---

## Example 2: Image Input (Logo Analysis)

**User Request:**
> "Create a theme from this company logo" (image of logo with teal and coral)

**Vision Analysis:**
```
Dominant colors detected:
1. Teal (#0d9488) - 45% coverage - Primary brand color
2. Coral (#f97316) - 15% coverage - Accent highlight
3. White (#ffffff) - 40% coverage - Background
```

**Color Mapping:**
```
Primary:   #134e4a  (darkened teal for text)
Secondary: #64748b  (neutral gray for secondary text)
Accent:    #0d9488  (teal from logo)
Neutral:   #f0fdfa  (light teal tint)
```

**Recommended scale:** Teal (matching logo's primary color)

**Generated Theme:** `theme-coral-teal`

---

## Example 3: Text Description Input

**User Request:**
> "Create a theme for a luxury fashion brand - elegant, sophisticated, with gold accents"

**Interpretation:**
```
Keywords: luxury, fashion, elegant, sophisticated, gold
→ Color direction: Deep, rich colors with metallic accent
→ Typography: Serif or elegant sans-serif
→ Border radius: Smaller (2-4px) for refined look
```

**Generated Palette:**
```
Primary:   #1c1917  (near-black stone for elegance)
Secondary: #57534e  (warm gray)
Accent:    #d97706  (amber/gold)
Neutral:   #faf5f0  (warm off-white)
```

**Typography Suggestion:**
```
Heading: Playfair Display (elegant serif)
Body: Source Sans Pro (clean, readable)
```

**Generated Theme:** `theme-luxury-gold`

---

## Example 4: Minimal Input (Accent Only)

**User Request:**
> "Create a theme called ocean with accent #0ea5e9"

**Input Processing:**
```
Theme Name: ocean
Accent: #0ea5e9 (Sky 500)
```

**Color Derivation:**
```
- Primary: #0c4a6e (Sky 900 - darkened accent)
- Secondary: #475569 (Slate 600 - neutral gray)
- Neutral: #e0f2fe (Sky 100 - light tint)
- Scale: Sky (blue family matches accent)
```

**Generated Output:**
```markdown
# Design System: Ocean Theme

A calming ocean-inspired theme with sky blue accents and clean aesthetics.

---

## Core Tokens

### Color Palette

#### Primary Colors
```
Primary:     #0c4a6e  (Sky 900 - Main text, headings)
Secondary:   #475569  (Slate 600 - Secondary text)
Accent:      #0ea5e9  (Sky 500 - CTAs, highlights)
Neutral:     #e0f2fe  (Sky 100 - Backgrounds, borders)
```

#### Neutral Scale (Sky)
```
sky-50:   #f0f9ff   (Lightest background)
sky-100:  #e0f2fe   (Card backgrounds)
sky-200:  #bae6fd   (Borders, dividers)
...
```
```

**Files Created:**
- `x-ipe-docs/themes/theme-ocean/design-system.md`
- `x-ipe-docs/themes/theme-ocean/component-visualization.html`

---

## Example 5: Corporate Theme with Custom Typography

**User Request:**
> "Create a corporate theme with:
> - Accent: #6366f1 (indigo)
> - Heading font: Poppins
> - More rounded corners (12px)"

**Input Processing:**
```
Theme Name: corporate
Accent: #6366f1 (Indigo 500)
Heading Font: Poppins
Border Radius (md): 12px
```

**Color Derivation:**
```
- Primary: #312e81 (Indigo 900)
- Secondary: #64748b (Slate 500)
- Neutral: #e0e7ff (Indigo 100)
- Scale: Indigo + Slate
```

**Generated Typography Section:**
```markdown
### Typography

#### Font Families
```css
--font-heading: 'Poppins', system-ui, sans-serif;
--font-body: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
```
```

---

## Example 6: Mixed Input (Web + Description)

**User Request:**
> "Create a theme inspired by anthropic.com but make it warmer and more approachable"

**Processing Steps:**
1. Fetch anthropic.com colors via `web_fetch`
2. Apply "warmer, approachable" modifications

**Extracted from Anthropic:**
```
Primary text: #141413 (near black)
Background: #faf9f5 (warm white)
Accent: #d97757 (terracotta orange)
```

**Modification for "warmer, approachable":**
```
- Keep warm neutral background: #faf9f5
- Soften primary slightly: #292524 (stone-800)
- Brighten accent: #ea580c (orange-600)
- Increase border-radius: 10px (more friendly)
```

**Generated Theme:** `theme-anthropic-warm`

---

## Web Extraction Patterns

When using `web_fetch`, look for these patterns:

### CSS Variables
```css
:root {
  --brand-primary: #...;
  --brand-accent: #...;
}
```

### Meta Tags
```html
<meta name="theme-color" content="#0ea5e9">
<meta name="msapplication-TileColor" content="#0ea5e9">
```

### Common Element Styles
```
Header/Nav background → Primary color candidate
Button backgrounds → Accent color candidate
Body text → Secondary color candidate
Page background → Neutral color candidate
```

---

## Tailwind Color Reference

Use these Tailwind CSS color families for neutral scales:

| Accent Color Family | Recommended Scale |
|---------------------|-------------------|
| Red/Rose/Pink | Rose or Slate |
| Orange/Amber | Orange or Stone |
| Yellow/Lime | Amber or Zinc |
| Green/Emerald/Teal | Emerald or Slate |
| Cyan/Sky | Sky or Slate |
| Blue/Indigo | Indigo or Slate |
| Violet/Purple | Violet or Slate |
| Fuchsia/Pink | Fuchsia or Slate |
| Gray/Slate/Zinc | Same family |

## Contrast Checking

After generating, verify accessibility:

| Combination | Required Ratio | Check |
|-------------|---------------|-------|
| Primary on White | 4.5:1 | Body text |
| Secondary on White | 4.5:1 | Body text |
| Accent on White | 3:1 | Large text only |
| White on Accent | 4.5:1 | Button text |

Use https://webaim.org/resources/contrastchecker/ to verify.

---

## Example 7: Web Link with Component Extraction

**User Request:**
> "Create a theme based on https://linear.app"

**Processing Steps:**
1. Fetch web page using `web_fetch`
2. Extract colors: dark background (#1b1b25), purple accent (#5e6ad2), white text
3. Extract component patterns from CSS:

**Extracted Components:**
```
Buttons:
  - Background: #5e6ad2 (purple accent)
  - Border-radius: 6px
  - Padding: 6px 12px (compact)
  - Font-weight: 500
  - Font-size: 13px
  - Hover: lighten to #6c78e0
  - Shadow: none (flat design)

Cards:
  - Background: rgba(255,255,255,0.04) (translucent)
  - Border: 1px solid rgba(255,255,255,0.08)
  - Border-radius: 8px
  - Padding: 16px
  - Shadow: none

Inputs:
  - Border: 1px solid rgba(255,255,255,0.1)
  - Border-radius: 6px
  - Padding: 8px 12px
  - Focus: 0 0 0 2px #5e6ad2

Links:
  - Color: #5e6ad2
  - Hover: #7c85e8
  - Decoration: none

Badges:
  - Background: rgba(94, 106, 210, 0.15)
  - Padding: 2px 6px
  - Radius: 4px
  - Font-size: 12px

Navigation:
  - Height: 48px
  - Background: #1b1b25
  - Padding: 0 12px
  - Item gap: 4px
```

**Generated Theme:** `theme-linear-inspired`

---

## Example 8: Image Input with Component Identification

**User Request:**
> "Create a theme from this brand guide screenshot" (shows buttons, cards, and form examples)

**Vision Analysis:**
```
Colors detected:
  - Deep blue (#1a365d) - primary
  - Bright green (#38a169) - accent
  - White backgrounds

Components identified:
  - Buttons: Pill-shaped (very rounded), green background
  - Cards: Subtle shadow, 16px border-radius, no visible border
  - Inputs: Rounded corners (~8px), thin gray borders
```

**Component Mapping:**
```
Buttons: radius=9999px, shadow=none
Cards: radius=16px, shadow=md, border=none
Inputs: radius=8px, border=1px solid #e2e8f0
```

**Generated Theme:** `theme-brand-guide`

---

## Example 9: Text Description with Component Style

**User Request:**
> "Create a minimal, modern theme called 'zen' — clean lines, lots of whitespace, very subtle"

**Keyword Interpretation:**
```
Minimal + Modern:
  Colors: neutral grays, single subtle accent
  Typography: system-ui, light weights
  Components: ghost buttons, borderless cards, underline-only inputs
```

**Derived Components:**
```
Buttons:
  - Primary: ghost/outline style, no background, accent border
  - Radius: 4px (subtle)
  - Shadow: none
  - Hover: very light accent background

Cards:
  - Border: none
  - Shadow: none
  - Padding: 32px (spacious)
  - Radius: 8px

Inputs:
  - Border: bottom-only (1px solid scale-200)
  - Radius: 0px (modern underline style)
  - Focus: accent bottom border

Links:
  - Color: accent
  - Decoration: none
  - Hover: underline
```

**Generated Theme:** `theme-zen`
