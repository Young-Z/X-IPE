# Examples: Brand Theme Creator

## Example 1: Minimal Input (Accent Only)

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
- `docs/themes/theme-ocean/design-system.md`

---

## Example 2: Corporate Theme with Custom Typography

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

**Generated Border Radius:**
```markdown
### Border Radius

```
rounded-sm:   4px    (Subtle rounding)
rounded-md:   12px   (Standard rounding)
rounded-lg:   16px   (Card corners)
...
```
```

---

## Example 3: Full Brand Specification

**User Request:**
> "Create a theme for my brand:
> - Name: sunset
> - Primary: #1e1b4b (dark indigo)
> - Secondary: #6b7280 (gray)
> - Accent: #f97316 (orange)
> - Neutral: #fff7ed (orange tint)
> - Heading: Montserrat
> - Body: Open Sans"

**Input Processing:**
```
Theme Name: sunset
Primary: #1e1b4b
Secondary: #6b7280
Accent: #f97316
Neutral: #fff7ed
Heading Font: Montserrat
Body Font: 'Open Sans'
```

**No Derivation Needed** - all colors provided.

**Generated Output Excerpt:**
```markdown
# Design System: Sunset Theme

A warm, vibrant theme with sunset orange accents and deep indigo foundations.

---

## Core Tokens

### Color Palette

#### Primary Colors
```
Primary:     #1e1b4b  (Indigo 950 - Main text, headings)
Secondary:   #6b7280  (Gray 500 - Secondary text)
Accent:      #f97316  (Orange 500 - CTAs, highlights)
Neutral:     #fff7ed  (Orange 50 - Backgrounds, borders)
```

#### Neutral Scale (Orange)
```
orange-50:   #fff7ed   (Lightest background)
orange-100:  #ffedd5   (Card backgrounds)
...
```

### Typography

#### Font Families
```css
--font-heading: 'Montserrat', system-ui, sans-serif;
--font-body: 'Open Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
```
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
