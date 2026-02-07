---
name: x-ipe-tool-frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use when the user asks to build web components, pages, artifacts, posters, or applications. Triggers on requests like "build landing page", "create dashboard UI", "design web component".
---

# Frontend Design

## Purpose

AI Agents follow this skill to create frontend interfaces that:
1. Deliver production-grade, functional UI with distinctive aesthetics
2. Integrate with the X-IPE theme system for brand consistency
3. Avoid generic "AI slop" patterns (overused fonts, cliched color schemes, predictable layouts)

---

## Important Notes

BLOCKING: Load the selected theme from `x-ipe-docs/config/tools.json` BEFORE any design work.
CRITICAL: Choose a clear conceptual direction and execute with precision. Bold maximalism and refined minimalism both work -- the key is intentionality, not intensity.
CRITICAL: NEVER use generic AI aesthetics: Inter/Roboto/Arial fonts, purple gradients on white, cookie-cutter layouts. Every design must be unique and context-specific.

---

## About

This tool creates self-contained HTML/CSS/JS frontends with exceptional aesthetic quality. It reads the X-IPE theme system for design tokens (colors, typography, spacing) and applies them creatively to produce memorable, polished interfaces.

**Key Concepts:**
- **Design Tokens** - CSS variables sourced from the theme's `design-system.md` (colors, fonts, spacing, radii, shadows)
- **Aesthetic Direction** - A deliberate visual tone (brutalist, art deco, editorial, organic, etc.) chosen per-project to avoid sameness
- **Theme Integration** - Reading the selected theme config and mapping its tokens to CSS custom properties

---

## When to Use

```yaml
triggers:
  - "build landing page"
  - "create dashboard UI"
  - "design web component"
  - "create mockup"
  - "style this page"
  - "beautify the UI"
  - "create HTML artifact"
  - "build a poster"

not_for:
  - "generate architecture diagram (use tool-architecture-draw)"
  - "create presentation slides (use pptx skill)"
```

---

## Input Parameters

```yaml
input:
  operation: "design"
  context:
    description: "What to build (component, page, application)"
    purpose: "Problem the interface solves, target audience"
    tone: "Aesthetic direction (optional, agent picks if omitted)"
    constraints: "Framework, performance, accessibility requirements"
  theme:
    source: "x-ipe-docs/config/tools.json"
    design_system: "{theme-folder-path}/design-system.md"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Frontend requirements provided</name>
    <verification>User has described what to build (component, page, or application)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Theme config accessible</name>
    <verification>x-ipe-docs/config/tools.json exists and contains selected-theme entry</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Design system file exists</name>
    <verification>design-system.md exists at the theme-folder-path specified in config</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: Load Theme

**When:** Always -- before any design work begins.

```xml
<operation name="load_theme">
  <action>
    1. Read theme name: `cat x-ipe-docs/config/tools.json | jq '.["selected-theme"]["theme-name"]'`
    2. Read theme path: `cat x-ipe-docs/config/tools.json | jq -r '.["selected-theme"]["theme-folder-path"]'`
    3. Load design system: `cat "${theme_path}/design-system.md"`
    4. Extract tokens into this mapping:
       - Color Palette (Primary, Secondary, Accent, Neutral) --> --color-{name}
       - Typography (Font Families) --> --font-heading, --font-body
       - Spacing section --> --space-{size}
       - Border Radius section --> --radius-{size}
       - Shadows section --> --shadow-{size}
  </action>
  <constraints>
    - BLOCKING: Theme must be loaded before any design decisions
    - The theme provides the palette; the agent uses it CREATIVELY
  </constraints>
  <output>Design tokens ready for CSS custom properties</output>
</operation>
```

### Operation: Design Thinking

**When:** After theme is loaded, before writing any code.

```xml
<operation name="design_thinking">
  <action>
    1. Identify PURPOSE: What problem does the interface solve? Who uses it?
    2. Choose TONE: Pick a deliberate aesthetic direction -- brutally minimal, maximalist chaos,
       retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine,
       brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, or another direction.
    3. Note CONSTRAINTS: Framework, performance, accessibility requirements.
    4. Define DIFFERENTIATION: The one memorable element someone will recall.
  </action>
  <constraints>
    - BLOCKING: Must commit to a clear direction before coding
    - Never converge on common choices (Space Grotesk, etc.) across generations
    - Vary between light/dark themes, fonts, and aesthetics across projects
  </constraints>
  <output>Aesthetic direction document (mental model for implementation)</output>
</operation>
```

### Operation: Implement Frontend

**When:** After design direction is established.

```xml
<operation name="implement_frontend">
  <action>
    1. Create self-contained HTML with theme tokens as CSS custom properties in :root
    2. Apply aesthetic guidelines:
       - TYPOGRAPHY: Distinctive, characterful font choices. Pair a display font with a refined body font.
         Use theme fonts as base; add complementary display fonts for creative impact.
       - COLOR: Commit to a cohesive palette via CSS variables. Dominant colors with sharp accents
         outperform timid, evenly-distributed palettes. Use theme colors boldly.
       - MOTION: CSS-only animations for HTML; Motion library for React. Focus on high-impact moments:
         orchestrated page load with staggered reveals, scroll-triggering, surprising hover states.
       - SPATIAL COMPOSITION: Unexpected layouts, asymmetry, overlap, diagonal flow, grid-breaking
         elements, generous negative space OR controlled density.
       - BACKGROUNDS: Create atmosphere and depth -- gradient meshes, noise textures, geometric patterns,
         layered transparencies, dramatic shadows, decorative borders, grain overlays.
    3. Match implementation complexity to the aesthetic vision:
       - Maximalist designs need elaborate code with extensive animations and effects
       - Minimalist designs need restraint, precision, and careful attention to spacing and typography
    4. Write to the appropriate output location
  </action>
  <constraints>
    - BLOCKING: Code must be production-grade and functional
    - CRITICAL: Every output must be visually striking, cohesive, and meticulously refined
  </constraints>
  <output>Self-contained HTML file with embedded CSS/JS</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    file_path: "x-ipe-docs/requirements/FEATURE-XXX/mockups/{name}.html | playground/mockups/{name}.html"
    theme_applied: "{theme-name}"
    aesthetic_direction: "{chosen tone}"
    format: "self-contained HTML with embedded CSS/JS"
  output_locations:
    feature_mockup: "x-ipe-docs/requirements/FEATURE-XXX/mockups/"
    standalone_mockup: "playground/mockups/"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Theme tokens applied</name>
    <verification>CSS :root contains all design tokens from theme's design-system.md</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Self-contained output</name>
    <verification>HTML file works standalone in a browser with no missing dependencies</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>No generic aesthetics</name>
    <verification>No Inter/Roboto/Arial fonts, no purple-gradient-on-white, no cookie-cutter patterns</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Production-grade code</name>
    <verification>Code is functional, responsive, and follows chosen aesthetic direction consistently</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `THEME_CONFIG_MISSING` | `x-ipe-docs/config/tools.json` not found | Create config with default theme or prompt user to run project init |
| `DESIGN_SYSTEM_MISSING` | `design-system.md` not found at theme path | Fall back to `x-ipe-docs/themes/theme-default/design-system.md` |
| `THEME_TOKENS_INCOMPLETE` | Design system missing required token sections | Use sensible defaults for missing tokens; log warning |

---

## Templates

### HTML Output Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{Feature Name}</title>
    <link href="https://fonts.googleapis.com/css2?family={ThemeHeadingFont}:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --color-primary: {from theme};
            --color-secondary: {from theme};
            --color-accent: {from theme};
            --color-neutral: {from theme};
            --font-heading: '{from theme}', sans-serif;
            --font-body: {from theme};
            --radius-md: {from theme};
            --shadow-md: {from theme};
        }
    </style>
</head>
<body>
    <!-- Implementation -->
</body>
</html>
```

### Theme File Structure

```
x-ipe-docs/themes/
  {theme-name}/
    design-system.md              -- Token definitions (REQUIRED)
    component-visualization.html  -- Visual reference (optional)
```

### API Endpoints

```
GET /api/themes              -- List all themes + selected
GET /api/themes/{name}       -- Get theme details + design_system content
GET /api/config/tools        -- Get config including themes.selected
```

---

## Examples

See [references/examples.md](references/examples.md) for theme-integrated mockup examples.
