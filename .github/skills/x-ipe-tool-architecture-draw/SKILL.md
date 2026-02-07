---
name: tool-architecture-draw
description: Generate architecture diagrams (Module View and Application Landscape) from idea context. Uses Architecture DSL syntax for version-controlled, grid-based layouts. Invoked by x-ipe-task-based-idea-to-architecture. Triggers on requests like "draw architecture", "create module diagram", "visualize landscape".
---

# Tool: Architecture Draw

## Purpose

AI Agents follow this skill to generate architecture diagrams from idea context to:
1. Analyze system structure and select appropriate diagram type
2. Generate Architecture DSL code (module-view or landscape-view)
3. Render visual HTML diagrams from DSL
4. Save versioned artifacts to the idea folder

---

## Important Notes

BLOCKING: If you have NOT learned `x-ipe-tool-architecture-dsl` skill, learn it first. This skill generates diagrams, not DSL syntax definitions.

CRITICAL: Focus ONLY on architectural structure. Do NOT include UI/UX mockups, user interaction flows, screen layouts, or visual styling preferences. UI mockups are handled by `x-ipe-tool-frontend-design`.

---

## About

Architecture Draw generates professional architecture diagrams from idea summaries using the Architecture DSL format. It produces grid-based, version-controlled diagram artifacts stored alongside idea documentation.

**Key Concepts:**
- **Module View** - Layered architecture decomposition showing internal structure (layers, modules, components)
- **Landscape View** - Enterprise integration showing how applications connect (zones, apps, databases, flows)
- **Architecture DSL** - Domain-specific language for defining diagrams with grid-based layouts
- **12-Column Grid** - All module-view diagrams use a 12-column grid; module cols must sum to 12 per layer

---

## When to Use

```yaml
triggers:
  - "draw architecture"
  - "create module diagram"
  - "visualize landscape"
  - "generate architecture diagram"

not_for:
  - "UI/UX mockups (use x-ipe-tool-frontend-design)"
  - "DSL syntax reference (use x-ipe-tool-architecture-dsl)"
```

---

## Input Parameters

```yaml
input:
  operation: "generate-diagram"
  context:
    idea_folder: "path to idea folder (required)"
    diagram_type: "module-view | landscape-view | auto (default: auto)"
    architecture_context: "extracted from idea summary"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Idea folder exists</name>
    <verification>Current Idea Folder path is set and directory exists</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Idea summary available</name>
    <verification>idea-summary-vN.md exists with architecture-relevant content</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Diagram type determined</name>
    <verification>Explicitly set to module-view/landscape-view, or auto-detect enabled</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: Validate Context

**When:** Starting diagram generation

```xml
<operation name="validate-context">
  <action>
    1. Verify Current Idea Folder exists
    2. Load latest idea-summary-vN.md
    3. Extract architecture-relevant content:
       - System components mentioned
       - Integration points
       - Technology stack
       - Data flows
  </action>
  <constraints>
    - BLOCKING: Do not proceed if idea folder or summary is missing
  </constraints>
  <output>Validated context with extracted architecture information</output>
</operation>
```

### Operation: Analyze and Select Diagram Type

**When:** Architecture context is validated

```xml
<operation name="analyze-and-select">
  <action>
    1. Determine if single application or multi-application ecosystem
       - Single application = module-view
       - Multi-application = landscape-view
    2. Identify 2-4 primary structural groupings (layers or zones)
    3. List main building blocks (components or apps)
    4. Map relationships and data flows between elements
  </action>
  <constraints>
    - CRITICAL: Use structure extraction mapping below
  </constraints>
  <output>Selected diagram type with structural analysis</output>
</operation>
```

**Structure Extraction Mapping:**

| Idea Content | Architecture Element |
|--------------|---------------------|
| "frontend", "UI", "templates" | Presentation Layer |
| "API", "services", "business logic" | Business Layer |
| "database", "storage", "files" | Data Layer |
| "connects to", "integrates with" | Flow/Dependency |
| "external system", "third party" | External Zone |

**Type Selection Matrix:**

| Condition | Diagram Type |
|-----------|--------------|
| Single app with internal structure | `module-view` |
| Multiple apps with integrations | `landscape-view` |
| Library/SDK architecture | `module-view` |
| Enterprise system map | `landscape-view` |
| Microservice internals | `module-view` |
| Microservice ecosystem | `landscape-view` |

### Operation: Generate Module View DSL

**When:** Diagram type is `module-view`

```xml
<operation name="generate-module-view">
  <action>
    1. Define document grid: always 12 columns, rows = layer_count * 2
    2. Create layer blocks with color, border-color, and rows
    3. Add modules within each layer (cols MUST sum to 12)
    4. Add components within each module using internal grid
    5. Wrap in @startuml/@enduml tags
  </action>
  <constraints>
    - BLOCKING: Module cols MUST sum to 12 within each layer
    - CRITICAL: Every layer requires rows property
    - CRITICAL: Use suggested colors (see below)
  </constraints>
  <output>Valid module-view DSL code</output>
</operation>
```

**Module View Template:**

```architecture-dsl
@startuml module-view
title "{Idea Name} Architecture"
direction top-to-bottom
grid 12 x {layer_count * 2}

layer "{Layer Name}" {
  color "{layer_color}"
  border-color "{border_color}"
  rows 2

  module "{Module Name}" {
    cols {N}
    rows 2
    grid {C} x {R}
    align center center
    gap 8px

    component "{Component Name}" { cols 1, rows 1 }
  }
}

@enduml
```

**Suggested Colors:**

| Layer | Background | Border |
|-------|------------|--------|
| Presentation | `#fce7f3` | `#ec4899` |
| Service | `#fef3c7` | `#f97316` |
| Business | `#dbeafe` | `#3b82f6` |
| Data | `#dcfce7` | `#22c55e` |

### Operation: Generate Landscape View DSL

**When:** Diagram type is `landscape-view`

```xml
<operation name="generate-landscape-view">
  <action>
    1. Create zone blocks for each application domain
    2. Add apps with tech, platform, and status properties
    3. Add databases in data zones
    4. Define action flows between aliases
    5. Wrap in @startuml/@enduml tags
  </action>
  <constraints>
    - BLOCKING: All aliases must be unique
    - CRITICAL: Flow labels must use action verbs ("Submit Order"), not protocols ("HTTP")
    - CRITICAL: Flow targets must reference defined aliases
  </constraints>
  <output>Valid landscape-view DSL code</output>
</operation>
```

**Landscape View Template:**

```architecture-dsl
@startuml landscape-view
title "{Ecosystem Name}"

zone "{Zone Name}" {
  app "{App Name}" as {alias} {
    tech: {Technology}
    platform: {Platform}
    status: healthy
  }
}

zone "Data" {
  database "{DB Name}" as {alias}
}

{source} --> {target} : "{Action Description}"

@enduml
```

### Operation: Validate DSL

**When:** DSL code has been generated

```xml
<operation name="validate-dsl">
  <action>
    1. Verify @startuml and @enduml tags present
    2. Check grid declaration (module-view)
    3. Verify module cols sum to 12 in each layer
    4. Verify every layer has rows property
    5. Confirm all aliases are unique
    6. Confirm flow targets reference defined aliases
  </action>
  <constraints>
    - BLOCKING: Fix all validation errors before rendering
  </constraints>
  <output>Validated DSL or list of errors to fix</output>
</operation>
```

### Operation: Render HTML

**When:** DSL validation passes

```xml
<operation name="render-html">
  <action>
    1. Parse DSL structure into element tree
    2. Calculate grid positions from layout properties
    3. Generate CSS Grid layout with proper sizing
    4. Apply colors and styling from DSL properties
    5. Create responsive HTML container
  </action>
  <output>Complete HTML file with rendered diagram</output>
</operation>
```

### Operation: Save Artifacts

**When:** HTML rendering is complete

```xml
<operation name="save-artifacts">
  <action>
    1. Create architecture/ subdirectory in idea folder
    2. Save DSL file: {type}-{name}-v{version}.dsl
    3. Save HTML file: {type}-{name}-v{version}.html
    4. Create README.md with diagram explanation
  </action>
  <constraints>
    - CRITICAL: Follow naming convention: {type}-{name}-v{version}.{ext}
  </constraints>
  <output>Saved artifact paths</output>
</operation>
```

**Directory Structure:**

```
{Current Idea Folder}/
  idea-summary-vN.md
  architecture/
    {diagram-name}.dsl
    {diagram-name}.html
    README.md
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    diagram_type: "module-view | landscape-view"
    dsl_path: "{idea_folder}/architecture/{name}.dsl"
    html_path: "{idea_folder}/architecture/{name}.html"
    elements:
      layers: N          # module-view only
      modules: N         # module-view only
      components: N      # module-view only
      zones: N           # landscape-view only
      apps: N            # landscape-view only
      flows: N           # landscape-view only
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Architecture context extracted</name>
    <verification>Structural elements identified from idea summary</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Diagram type selected</name>
    <verification>module-view or landscape-view chosen with rationale</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>DSL generated and validated</name>
    <verification>All validation rules pass (grid, cols, aliases, flows)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>HTML rendering created</name>
    <verification>Visual diagram renders correctly from DSL</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Artifacts saved</name>
    <verification>DSL and HTML files exist in {idea_folder}/architecture/</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `E001: Missing idea folder` | Idea folder path not set or missing | Verify context and set correct path |
| `E002: No idea summary` | idea-summary-vN.md not found | Complete ideation before drawing |
| `E003: No architecture content` | Summary lacks system structure info | Extract architecture from idea or ask user |
| `E005: Cols sum mismatch` | Module cols do not sum to 12 | Adjust module cols to total 12 per layer |
| `E006: Missing rows` | Layer missing rows property | Add `rows N` to every layer definition |
| `E007: Duplicate alias` | Two elements share same alias | Rename to unique aliases |
| `E008: Undefined alias in flow` | Flow references non-existent alias | Add `as alias` to element definition |

---

## Templates

| File | Purpose |
|------|---------|
| See Operations section | Module View and Landscape View DSL templates inline |

---

## Examples

See [examples/](examples/) for complete diagram examples:
- `module-view-webapp.dsl` - Standard web application
- `landscape-view-enterprise.dsl` - Enterprise integration map

See [references/](references/) for additional documentation:
- `dsl-cheatsheet.md` - DSL syntax quick reference
- `patterns.md` - Architecture patterns and anti-patterns
