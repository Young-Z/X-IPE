---
name: x-ipe-tool-draw-layered-architecture
description: Render layered architecture diagrams (Module View) from Architecture DSL definitions. Default style is corporate. Integrates with X-IPE theme system. Triggers on requests like "draw architecture", "render module view", "generate layered diagram".
---

# Layered Architecture Diagram Renderer

## Purpose

AI Agents follow this skill to render Architecture DSL into HTML diagrams to:
1. Transform `module-view` Architecture DSL into self-contained HTML files
2. Apply corporate or default styling via HTML templates
3. Integrate with X-IPE theme system for design tokens

---

## Important Notes

BLOCKING: Always use `templates/module-view-corporate.html` as the default template. Never use `module-view.html` unless DSL explicitly contains `style "default"`.

CRITICAL: No Invention Rule - You MUST NOT add any content that does not exist in the DSL. Do not invent layer headers/titles, add extra components, add tooltips/descriptions, or add classes/variants not specified by stereotypes.

CRITICAL: Corporate style ignores DSL `color` and `border-color` properties. They only apply with `style "default"`.

---

## About

Transforms Architecture DSL `module-view` code blocks into self-contained HTML diagrams using a 12-column grid system.

**Key Concepts:**
- **Module View** - A layered architecture diagram type defined in Architecture DSL
- **Corporate Style** - Default template with fixed color scheme (white backgrounds, dark badges)
- **Grid System** - 12-column layout: Document (12xN), Layer (full width), Module (cols sum to 12), Component (within module grid)

**Available Styles:**

| Style | Template | Default |
|-------|----------|---------|
| `corporate` | `module-view-corporate.html` | Yes |
| `default` | `module-view.html` | No |

**Corporate Style Colors:**

| Element | Color | Note |
|---------|-------|------|
| Layer BG | `#ffffff` | Always white |
| Layer BG Highlight | `#eff6ff` | Use `.layer-highlight` class |
| Border | `#374151` | Gray border |
| Badge BG | `#1f2937` | Dark gray |
| Badge Text | `#ffffff` | White text |

---

## When to Use

```yaml
triggers:
  - "draw layered architecture"
  - "render module view"
  - "generate architecture diagram from DSL"
  - "convert architecture DSL to HTML"

not_for:
  - "Generate DSL syntax from requirements → use x-ipe-tool-architecture-dsl"
  - "Render landscape/system diagrams → use x-ipe-tool-draw-system-landscape"
```

---

## Input Parameters

```yaml
input:
  dsl_source: "architecture-dsl code block with view-type: module-view"
  options:
    output_path: "path to save HTML file (default: same directory as DSL with .html extension)"
    theme: "theme name from x-ipe-docs/themes/ (default: theme-default)"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Valid Architecture DSL</name>
    <verification>Input contains a valid architecture-dsl code block with view-type module-view</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Template Available</name>
    <verification>templates/module-view-corporate.html or templates/module-view.html exists</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: Render Diagram

**When:** Agent receives Architecture DSL with `module-view` type to render as HTML

```xml
<operation name="render_diagram">
  <action>
    1. Parse DSL: Extract title, style (default: corporate), theme (default: theme-default), and structure (Layers, Modules, Components)
    2. Load theme: Read design tokens from x-ipe-docs/themes/${theme_name}/design-system.md
    3. Select template: Use module-view-corporate.html unless DSL contains style "default"
    4. Map DSL elements to HTML:
       - title "..." to h1.diagram-title at top
       - layer "..." to layer with side label
       - module "..." to module with title
       - component "..." to component with text
    5. Map DSL properties to CSS classes (see references/dsl-to-css.md):
       - cols N to class="cols-N"
       - rows N to class="rows-N"
       - grid C x R to class="grid-CxR"
    6. Apply component variant classes based on stereotypes:
       - icon/folder/file/db to component-icon
       - full to component component-full
       - highlight to component component-highlight
       - (none) to component
    7. Verify: Check every cols, rows, grid value matches DSL exactly
    8. Save to output_path or same directory as DSL with .html extension
  </action>
  <constraints>
    - BLOCKING: Only render content present in the DSL; never invent elements
    - BLOCKING: Corporate style ignores DSL color and border-color properties
    - CRITICAL: Module cols values must sum to 12 per layer
    - CRITICAL: Document grid is always 12 columns fixed
  </constraints>
  <output>Self-contained HTML file at specified output path</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    file_path: "path/to/output.html"
    style: "corporate | default"
    theme: "theme name applied"
    layers_count: "number of layers rendered"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>HTML File Generated</name>
    <verification>Self-contained HTML file exists at output path</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>DSL-HTML Property Match</name>
    <verification>Every cols, rows, grid, component, and stereotype value in DSL matches the generated HTML exactly</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>No Invented Content</name>
    <verification>HTML contains only elements defined in the DSL source</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Correct Template Used</name>
    <verification>Corporate template used unless DSL explicitly specifies style "default"</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INVALID_DSL` | DSL code block is missing or malformed | Validate DSL syntax before rendering |
| `TEMPLATE_NOT_FOUND` | HTML template file not found in templates/ | Check templates/ directory exists with required files |
| `THEME_NOT_FOUND` | Theme directory not found in x-ipe-docs/themes/ | Fall back to theme-default |
| `COLS_MISMATCH` | Module cols do not sum to 12 in a layer | Fix DSL source to ensure cols sum to 12 per layer |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/module-view-corporate.html` | Corporate style template (default) |
| `templates/module-view.html` | Default style template |

---

## Examples

See [examples/](examples/) for DSL-to-HTML examples and [references/dsl-to-css.md](references/dsl-to-css.md) for the complete property mapping.

**Related Skills:**
- [x-ipe-tool-architecture-dsl](../x-ipe-tool-architecture-dsl/SKILL.md) - DSL syntax generation
- [x-ipe-tool-draw-system-landscape](../x-ipe-tool-draw-system-landscape/SKILL.md) - Landscape diagrams
