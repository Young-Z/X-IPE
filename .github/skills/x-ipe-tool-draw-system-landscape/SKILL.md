---
name: x-ipe-tool-draw-system-landscape
description: Render system landscape diagrams (Landscape View) from Architecture DSL definitions. Creates self-contained HTML visualizations showing application integration maps with zones, apps, databases, and action flows. Integrates with X-IPE theme system. Triggers on requests like "draw landscape", "render landscape view", "system landscape diagram".
---

# System Landscape Diagram Renderer

## Purpose

AI Agents follow this skill to render Architecture DSL landscape-view definitions into HTML diagrams to:
1. Generate self-contained HTML landscape visualizations from architecture-dsl code blocks
2. Apply theme tokens from the X-IPE design system for brand consistency
3. Render zones, apps, databases, and action flows as styled interactive diagrams

---

## Important Notes

BLOCKING: Only processes `landscape-view` DSL. For `module-view`, use `x-ipe-tool-draw-layered-architecture` instead.
CRITICAL: All theme tokens must be resolved before rendering. Defaults to `theme-default` if no theme specified.
CRITICAL: All app and database aliases must be unique within the DSL document.

---

## About

This tool transforms Architecture DSL `landscape-view` code into production-grade, self-contained HTML files showing application integration maps.

**Key Concepts:**
- **Landscape View** - A diagram type showing application zones, apps, databases, and their integration flows
- **Zone** - A container section grouping related apps and databases
- **Flow** - A directional action relationship between two apps or databases
- **Theme Tokens** - CSS custom properties from the design system applied to diagram styling

---

## When to Use

```yaml
triggers:
  - "draw landscape"
  - "render landscape view"
  - "system landscape diagram"
  - "application integration map"

not_for:
  - "module-view diagrams -> use x-ipe-tool-draw-layered-architecture"
  - "DSL syntax authoring -> use x-ipe-tool-architecture-dsl"
  - "theme creation -> use theme-factory"
```

---

## Input Parameters

```yaml
input:
  operation: "render"
  dsl:
    source: "architecture-dsl code block with @startuml landscape-view header"
  theme:
    name: "string - theme name from DSL or 'theme-default'"
    path: "x-ipe-docs/themes/{name}/design-system.md"
  output:
    directory: "target directory for generated HTML file"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Valid DSL Input</name>
    <verification>Architecture DSL code block exists with @startuml landscape-view header</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Theme Available</name>
    <verification>Theme design-system.md exists at x-ipe-docs/themes/{name}/design-system.md</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Template Exists</name>
    <verification>templates/landscape-view.html is present in skill folder</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output Directory</name>
    <verification>Target output directory exists or can be created</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: Render Landscape

**When:** Agent receives an architecture-dsl code block with `@startuml landscape-view` header.

```xml
<operation name="render_landscape">
  <action>
    1. Extract theme name from DSL `theme` property
       - If `theme "{name}"` specified: use `x-ipe-docs/themes/{name}/design-system.md`
       - If no theme specified: default to `x-ipe-docs/themes/theme-default/design-system.md`
    2. Load theme tokens from design-system.md:
       - --color-primary: Zone titles, app names
       - --color-secondary: Subtitles, meta text
       - --color-accent: Highlights, flow arrows
       - --color-neutral: Backgrounds, borders
       - --font-heading: Zone/app titles
       - --font-body: Meta text
    3. Parse DSL hierarchical structure: Document > Zones > Apps/Databases > Flows
    4. Extract elements:
       - Zones: name, title, contained apps/databases
       - Apps: alias, display name, tech stack, platform, status (healthy/warning/critical)
       - Databases: alias, display name
       - Flows: source alias, target alias, action label
    5. Apply parsed values to templates/landscape-view.html using mapping rules from references/landscape-mapping.md
    6. Apply element styling (see Element Styling reference below)
    7. Save generated HTML to output directory
  </action>
  <constraints>
    - BLOCKING: Validate all aliases are unique before rendering
    - BLOCKING: Validate all flow source/target references exist as defined aliases
    - BLOCKING: All apps/databases must belong to a zone
  </constraints>
  <output>Self-contained HTML file at the specified output path</output>
</operation>
```

### Element Styling Reference

**Zone Styles** - Container sections grouping related apps and databases:
- Background: white, border-radius: 12px, padding: 20px
- Box shadow: 0 2px 8px rgba(0,0,0,0.05), border: 1px solid #e2e8f0

**App Styles** - Applications with tech stack, platform, and health status:
- Background: #f8fafc, border-radius: 8px, padding: 16px, min-width: 160px

**Status Indicators:**

| Status | Color | Effect |
|--------|-------|--------|
| `healthy` | `#22c55e` | Green glow |
| `warning` | `#f97316` | Orange glow |
| `critical` | `#ef4444` | Red glow + pulse animation |

**Database Styles** - Distinct visual treatment from apps:
- Background: linear-gradient(135deg, #f0f9ff, #e0f2fe), border: 2px solid #0ea5e9

**Flow Styles** - Action relationships between applications:
- Display: flex, gap: 8px, padding: 8px 12px, background: #f8fafc

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    file_path: "path to generated HTML file"
    view_type: "landscape-view"
    zones_count: "number of zones rendered"
    apps_count: "number of apps rendered"
    flows_count: "number of flows rendered"
  errors: []
```

**Output Locations:**
- Feature architecture: `x-ipe-docs/requirements/FEATURE-XXX/architecture/`
- Standalone diagrams: `playground/architecture/`
- Idea exploration: `x-ipe-docs/ideas/idea-XXX/architecture/`

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>HTML File Generated</name>
    <verification>Self-contained HTML file exists at the output path</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All Zones Rendered</name>
    <verification>Every zone from DSL appears in the HTML output</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All Apps and Databases Rendered</name>
    <verification>Every app and database from DSL appears within its parent zone</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>All Flows Rendered</name>
    <verification>Every flow from DSL appears with correct source, target, and label</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Theme Applied</name>
    <verification>Design system tokens are reflected in the generated styles</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `INVALID_VIEW_TYPE` | DSL header is not `landscape-view` | Redirect to `x-ipe-tool-draw-layered-architecture` for `module-view` |
| `THEME_NOT_FOUND` | Specified theme does not exist | Fall back to `theme-default` |
| `DUPLICATE_ALIAS` | Two or more elements share the same alias | Rename aliases to be unique |
| `INVALID_FLOW_REF` | Flow references a non-existent alias | Correct source/target to match defined aliases |
| `ORPHAN_ELEMENT` | App or database not inside any zone | Move element into appropriate zone |
| `TEMPLATE_MISSING` | landscape-view.html template not found | Verify skill templates/ folder is intact |

---

## Templates

| File | Purpose |
|------|---------|
| `templates/landscape-view.html` | Base HTML template for landscape view rendering |

---

## Examples

See [examples/](examples/) for complete DSL-to-HTML rendering examples.
See [references/landscape-mapping.md](references/landscape-mapping.md) for DSL-to-CSS element mapping rules.

**Related Skills:**
- [x-ipe-tool-architecture-dsl](../x-ipe-tool-architecture-dsl/SKILL.md) - DSL syntax reference
- [x-ipe-tool-draw-layered-architecture](../x-ipe-tool-draw-layered-architecture/SKILL.md) - Module view diagrams
- [theme-factory](../theme-factory/SKILL.md) - Theme management
