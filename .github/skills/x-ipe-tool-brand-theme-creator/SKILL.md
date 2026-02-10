---
name: x-ipe-tool-brand-theme-creator
description: Generate design-system.md and component-visualization.html files for custom X-IPE themes based on brand inputs. Use when user wants to create a new theme, define brand colors, or build a design system. Triggers on requests like "create theme", "new brand theme", "generate design system", "add custom theme".
---

# X-IPE Brand Theme Creator

## Purpose

Transform brand colors, typography preferences, and style guidelines into a complete theme package by:
1. Extracting brand identity from web links, images, or text descriptions
2. Deriving a full color palette from minimal input (one accent color minimum)
3. Generating `design-system.md` with structured token definitions for AI agents
4. Generating `component-visualization.html` with visual preview and JSON-LD

---

## About

This meta skill produces theme packages consumed by the X-IPE theme system. Each theme lives in its own directory and contains two files: a markdown design system for agent consumption and an HTML visualization for human review.

### Key Concepts

- **Design System** - Structured token definitions (colors, typography, spacing, shadows) in markdown
- **Component Visualization** - Self-contained HTML file with CSS variables, visual previews, and JSON-LD structured data
- **Color Derivation** - Algorithmic expansion of a single accent color into a full palette using Tailwind CSS scales

### Scope

```yaml
operates_on:
  - "Theme packages in x-ipe-docs/themes/theme-{name}/"
  - "Design tokens (colors, typography, spacing, radius, shadows)"

does_not_handle:
  - "Application-level CSS or component library code"
  - "Runtime theme switching logic"
```

---

## Important Notes

BLOCKING: Output location is `x-ipe-docs/themes/theme-{name}/`. Theme names must use kebab-case with `theme-` prefix.

CRITICAL: Both `design-system.md` and `component-visualization.html` must be generated. Never produce only one file.

CRITICAL: Minimum input is one accent/brand color. All other tokens can be derived. See [references/color-derivation.md](references/color-derivation.md).

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point.

---

## Input Parameters

```yaml
input:
  # Primary inputs
  theme_name: "kebab-case name without 'theme-' prefix (e.g., ocean, corporate)"
  accent_color: "hex color value (e.g., #3b82f6) OR derived from source"

  # Input source (one of)
  source_type: "web_link | image | text_description | direct"
  source_value: "URL, image path, or text description"

  # Optional overrides (with defaults)
  primary_color: "derived: darken accent by 40%"
  secondary_color: "derived: desaturate + darken by 20%"
  neutral_color: "derived: very light tint of accent"
  heading_font: "Inter"
  body_font: "system-ui"
  code_font: "JetBrains Mono"
  border_radius_md: "8px"
```

For detailed extraction procedures per source type, see [references/input-sources.md](references/input-sources.md).

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Theme Name Provided</name>
    <verification>User specified a theme name or one can be derived from input</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Color Source Available</name>
    <verification>At least one of: accent color hex, web URL, image, or text description provided</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>Reference Theme Accessible</name>
    <verification>theme-default exists at x-ipe-docs/themes/theme-default/ for structural reference</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow

| Step | Name | Action | Gate |
|------|------|--------|------|
| 1 | Extract Colors | Process input source to obtain brand colors | Colors extracted |
| 2 | Confirm with User | Present extracted/derived palette for approval | User confirms |
| 3 | Derive Full Palette | Apply color derivation rules for missing tokens | All tokens resolved |
| 4 | Generate design-system.md | Fill design system template with token values | File written |
| 5 | Generate visualization | Fill HTML template, replace all placeholders | File written |
| 6 | Create Theme Folder | Write both files to `x-ipe-docs/themes/theme-{name}/` | Files on disk |
| 7 | Validate | Verify DoD checkpoints | DoD validated |

---

## Execution Procedure

```xml
<procedure name="brand-theme-creator">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Extract Colors</name>
    <action>
      1. Determine input source type (web link, image, text, or direct hex)
      2. Extract colors based on source type:
         IF source_type = web_link: use web_fetch to retrieve page, extract from CSS variables, meta tags, header/nav/CTA colors
         ELSE IF source_type = image: use vision capabilities to identify dominant + accent colors by area coverage
         ELSE IF source_type = text_description: parse brand adjectives, map to color direction and typography per interpretation guide
         ELSE: use provided hex values directly
      3. Map extracted values to theme tokens (primary, secondary, accent, neutral)
    </action>
    <constraints>
      - BLOCKING: For web links, always use web_fetch - never guess colors
      - CRITICAL: Extract hex values only; no RGB or HSL in theme tokens
    </constraints>
    <output>Extracted color values mapped to theme token roles</output>
  </step_1>

  <step_2>
    <name>Confirm with User</name>
    <action>
      1. Present extracted/interpreted colors to user
      2. Ask for theme name if not already provided
      3. Offer customization options (typography, border radius)
    </action>
    <constraints>
      - BLOCKING: Do not proceed to generation without user confirmation
    </constraints>
    <output>Confirmed color palette and configuration</output>
  </step_2>

  <step_3>
    <name>Derive Full Palette</name>
    <action>
      1. Apply color derivation rules for any unspecified tokens
      2. Select appropriate Tailwind neutral scale (slate, gray, zinc, stone, etc.)
      3. Resolve semantic colors (success=#22c55e, warning=#f59e0b, error=#ef4444, info=#3b82f6)
      4. Compute accent variants (light bg at 10% opacity, focus ring at 15% opacity)
      5. Verify contrast ratios: primary/secondary on white >= 4.5:1, accent on white >= 3:1
    </action>
    <output>Complete token set with all colors, typography, spacing, radius, shadows</output>
  </step_3>

  <step_4>
    <name>Generate design-system.md</name>
    <action>
      1. Load template from templates/design-system-template.md
      2. Fill all token sections: colors, typography, spacing, radius, shadows
      3. Include component specs (buttons, cards, form inputs)
      4. Add CSS variables block
    </action>
    <output>Completed design-system.md content</output>
  </step_4>

  <step_5>
    <name>Generate component-visualization.html</name>
    <action>
      1. Load template from templates/component-visualization-template.html
      2. Replace all {{PLACEHOLDERS}} with resolved token values
      3. Include JSON-LD structured data block with all tokens
      4. Verify no unreplaced placeholder strings remain
    </action>
    <constraints>
      - BLOCKING: All placeholders must be replaced; see references/template-placeholders.md
      - CRITICAL: JSON-LD block must be present for AI parsing
    </constraints>
    <output>Completed component-visualization.html content</output>
  </step_5>

  <step_6>
    <name>Create Theme Folder</name>
    <action>
      1. Create directory x-ipe-docs/themes/theme-{name}/
      2. Write design-system.md
      3. Write component-visualization.html
    </action>
    <output>Theme directory with both files on disk</output>
  </step_6>

  <step_7>
    <name>Validate</name>
    <action>
      1. Confirm theme directory exists with both files
      2. Verify no {{PLACEHOLDER}} strings remain in generated files
      3. Verify JSON-LD block is present in HTML file
      4. Check that theme appears in /api/themes response
      5. Test that 4 color swatches display correctly
    </action>
    <success_criteria>
      - Both files exist at correct path
      - No unreplaced placeholders
      - Theme discoverable by API
    </success_criteria>
    <output>Validated theme package</output>
  </step_7>

</procedure>
```

---

## Output Result

```yaml
task_completion_output:
  category: standalone
  status: completed | blocked
  next_task_based_skill: null
  require_human_review: "yes"
  task_output_links:
    - "x-ipe-docs/themes/theme-{name}/design-system.md"
    - "x-ipe-docs/themes/theme-{name}/component-visualization.html"
  theme_name: "theme-{name}"
  source_type: "web_link | image | text_description | direct"
  colors_confirmed: "true | false"
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently.

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Design System Created</name>
    <verification>design-system.md exists at x-ipe-docs/themes/theme-{name}/ with all token sections populated</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Visualization Created</name>
    <verification>component-visualization.html exists with no unreplaced {{PLACEHOLDER}} strings</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>JSON-LD Present</name>
    <verification>component-visualization.html contains JSON-LD structured data block</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Colors in Hex</name>
    <verification>All color tokens use hex format (not RGB or HSL)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Contrast Verified</name>
    <verification>Primary/secondary on white >= 4.5:1 ratio; accent on white >= 3:1</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>User Confirmed Palette</name>
    <verification>Extracted/derived colors were presented to and confirmed by user before generation</verification>
  </checkpoint>
</definition_of_done>
```

---

## Templates

| File | Purpose | When to Use |
|------|---------|-------------|
| `templates/design-system-template.md` | Markdown design system structure with token placeholders | Generating design-system.md |
| `templates/component-visualization-template.html` | HTML preview with CSS variables and JSON-LD | Generating component-visualization.html |

---

## Examples

See [references/examples.md](references/examples.md) for concrete theme generation examples covering web link, image, text, and minimal input scenarios.

### References

- [references/input-sources.md](references/input-sources.md) - Detailed extraction procedures per source type
- [references/color-derivation.md](references/color-derivation.md) - Color derivation rules, defaults, and Tailwind scale mapping
- [references/color-scales.md](references/color-scales.md) - Full Tailwind CSS color scale values
- [references/template-placeholders.md](references/template-placeholders.md) - Complete placeholder table and output file structure
