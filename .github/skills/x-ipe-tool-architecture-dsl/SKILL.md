---
name: x-ipe-tool-architecture-dsl
description: Generate Architecture DSL from requirements or refine existing DSL. Use for layered architectures (Module View) or application landscapes (Landscape View). Triggers on "architecture diagram", "layer diagram", "module view", "landscape view", "draw architecture".
version: 3.0
---

# Architecture DSL Tool

## Purpose

AI Agents follow this skill to generate Architecture DSL definitions to:
1. Create layered architecture diagrams (Module View) from requirements
2. Create application landscape diagrams (Landscape View) from system descriptions
3. Refine or update existing Architecture DSL definitions

---

## Important Notes

BLOCKING: Module `cols` within a layer MUST sum to 12. Violation produces invalid diagrams.
CRITICAL: IPE natively renders Architecture DSL in markdown via `architecture-dsl` code blocks -- no HTML files needed.
CRITICAL: Stereotyped components render at half width (0.5x) and 1.5x height. Use horizontal grid (`grid N x 1`) for stereotype-only modules.

---

## About

Architecture DSL is a domain-specific language for defining software architecture diagrams using a Bootstrap-inspired 12-column grid system. It supports two view types: Module View (layered decomposition) and Landscape View (application integration).

**Key Concepts:**
- **Module View** - Layered architecture with layers, modules, and components arranged in a 12-column grid
- **Landscape View** - Application integration diagrams with zones, apps, databases, and action flows
- **Grid System** - 12-column layout where module `cols` must sum to 12 per layer
- **Stereotypes** - Component decorators (`<<file>>`, `<<folder>>`, `<<model>>`, `<<service>>`, `<<icon>>`, `<<api>>`, `<<db>>`) that alter rendering size

**IPE Markdown Embedding:**

````markdown
```architecture-dsl
@startuml module-view
title "Your Architecture"
...
@enduml
```
````

---

## When to Use

```yaml
triggers:
  - "architecture diagram"
  - "layer diagram"
  - "module view"
  - "landscape view"
  - "draw architecture"
  - "system architecture"
  - "application landscape"

not_for:
  - "flowcharts -> use Mermaid"
  - "sequence diagrams -> use Mermaid"
  - "class/ER diagrams -> use Mermaid"
```

---

## Input Parameters

```yaml
input:
  operation: "generate_module_view | generate_landscape_view | refine_dsl"
  context:
    requirements: "text description or structured requirements"
    existing_dsl: "optional - current DSL to refine"
  options:
    theme: "theme name (default: theme-default)"
    canvas: "optional explicit dimensions (e.g., 1200px, 600px)"
    direction: "top-to-bottom | left-to-right (default: top-to-bottom)"
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Requirements Available</name>
    <verification>Text description, idea summary, or existing DSL provided as input</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>View Type Determined</name>
    <verification>Either module-view (layered) or landscape-view (integration) identified</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: Generate Module View

**When:** Creating a layered architecture diagram from requirements.

```xml
<operation name="generate_module_view">
  <action>
    1. Identify architectural layers (standard: Presentation, Business, Data)
    2. Calculate document grid: cols = 12, rows = sum of all layer rows
    3. Allocate module cols per layer (must sum to 12):
       - 2 equal: 6 + 6
       - 3 equal: 4 + 4 + 4
       - 1 wide + 1 narrow: 8 + 4
       - 1 wide + 2 narrow: 6 + 3 + 3
    4. Plan component grid per module:
       - 1-2 components: grid 2 x 1
       - 3-4 components: grid 2 x 2
       - 5-6 components: grid 3 x 2 or grid 2 x 3
       - 7-9 components: grid 3 x 3
    5. Apply layer colors (see references/layout-principles.md)
    6. Use multi-line names with \n for long labels
    7. Validate output against checklist
  </action>
  <constraints>
    - BLOCKING: Module cols MUST sum to 12 per layer
    - BLOCKING: Every layer MUST have rows declaration
    - BLOCKING: Stereotype-only modules MUST use horizontal grid (grid N x 1)
    - Document MUST start with @startuml module-view and end with @enduml
    - Document MUST have grid declaration at document level
  </constraints>
  <output>Complete Architecture DSL in architecture-dsl code block</output>
</operation>
```

### Operation: Generate Landscape View

**When:** Creating an application integration diagram showing how systems connect.

```xml
<operation name="generate_landscape_view">
  <action>
    1. Identify application zones/domains from requirements
    2. Define apps with tech, platform, and status properties
    3. Define databases and data stores
    4. Create action flows between components using verb-based labels
    5. Validate alias uniqueness and flow target existence
  </action>
  <constraints>
    - Flow labels MUST be action-focused (e.g., "Submit Order", not "order data")
    - All aliases MUST be unique
    - Flow sources and targets MUST reference defined aliases
    - App status MUST be one of: healthy, warning, critical
  </constraints>
  <output>Complete Architecture DSL in architecture-dsl code block</output>
</operation>
```

### Operation: Refine DSL

**When:** Updating or correcting an existing Architecture DSL definition.

```xml
<operation name="refine_dsl">
  <action>
    1. Parse existing DSL and identify view type
    2. Apply requested changes (add/remove/modify elements)
    3. Recalculate grid dimensions if layers or modules changed
    4. Verify module cols still sum to 12 per layer
    5. Validate output against checklist
  </action>
  <constraints>
    - BLOCKING: Preserve existing structure unless change is explicitly requested
    - Recalculate document grid rows when layer rows change
  </constraints>
  <output>Updated Architecture DSL in architecture-dsl code block</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    view_type: "module-view | landscape-view"
    dsl: "complete DSL content in architecture-dsl code block"
    validation: "all checklist items passed"
  errors: []
```

---

## Definition of Done

CRITICAL: Use a sub-agent to validate DoD checkpoints independently. The sub-agent MUST parse the generated DSL and verify every checkpoint below against the grammar specification at [references/grammar.md](references/grammar.md).

```xml
<definition_of_done>
  <validation_sub_agent>
    <role>architecture-dsl-validator</role>
    <goal>Parse generated DSL output and validate it meets the Architecture DSL specification</goal>
    <model_hint>sonnet</model_hint>
    <instructions>
      1. Read the complete DSL grammar from references/grammar.md
      2. Read the layout principles from references/layout-principles.md
      3. Parse the generated DSL output line by line
      4. Validate EVERY checkpoint below against the grammar rules
      5. For each checkpoint: report PASS or FAIL with specific line references
      6. IF any FAIL: return the list of violations with fix suggestions
      7. The generating agent MUST fix all violations before output is accepted
    </instructions>
  </validation_sub_agent>

  <checkpoint required="true">
    <name>Structure Valid</name>
    <verification>@startuml and @enduml present, grid declared at document level</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Grid Rules Satisfied</name>
    <verification>Each layer has rows, each module has cols, module cols sum to 12 per layer</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Component Grid Valid</name>
    <verification>Each module's internal grid dimensions can contain all declared components (cols x rows >= component count)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Stereotypes Correct</name>
    <verification>Stereotype-only modules use horizontal grid (grid N x 1)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Aliases Valid</name>
    <verification>All aliases unique, all flow targets reference defined aliases</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Syntax Conforms to Grammar</name>
    <verification>Every keyword, property, and nesting level matches references/grammar.md specification</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output Embedded</name>
    <verification>DSL wrapped in architecture-dsl code block for IPE rendering</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Module cols sum != 12 | Incorrect cols allocation | Adjust module cols to sum to 12 |
| Missing rows in layer | Layer lacks rows declaration | Add `rows N` to every layer |
| Missing grid declaration | Document-level grid absent | Add `grid 12 x N` at document level |
| Undefined alias in flow | Flow references non-existent alias | Define alias with `as` keyword before using in flow |
| Duplicate alias | Same alias used for multiple elements | Use unique alias names |
| Invalid status value | Status not in allowed set | Use `healthy`, `warning`, or `critical` |
| Vertical stereotype layout | Stereotype module uses grid 1 x N | Change to horizontal grid N x 1 |

---

## Templates

### Module View Structure

```architecture-dsl
@startuml module-view
title "Title"
theme "theme-default"
direction top-to-bottom
canvas 1200px, 600px
grid 12 x 6

layer "Name" {
  color "#hex"
  border-color "#hex"
  rows 2

  module "Name" {
    cols 4
    rows 2
    grid 2 x 3
    align center center
    gap 8px
    component "Name" { cols 1, rows 1 }
  }
}

@enduml
```

### Landscape View Structure

```architecture-dsl
@startuml landscape-view
title "Title"
theme "theme-default"

zone "Zone Name" {
  app "App" as alias {
    tech: Technology
    platform: Platform
    status: healthy | warning | critical
  }
  database "DB" as alias
}

alias1 --> alias2 : "Action Description"

@enduml
```

### Translation Patterns

| Input | Output |
|-------|--------|
| "3 layers: X, Y, Z" | 3 layers with `rows 2` each, `grid 12 x 6` |
| "split into 3 parts" | 3 modules with `cols 4` |
| "one wide, one narrow" | `cols 8` + `cols 4` |
| "stack vertically" | `grid 1 x N` |
| "X connects to Y" | `x --> y : "Action"` |

---

## Examples

- [references/grammar.md](references/grammar.md) - Complete DSL grammar specification
- [references/layout-principles.md](references/layout-principles.md) - Grid layout guidelines and color suggestions
- [examples/module-view-v2.dsl](examples/module-view-v2.dsl) - Module View example
- [examples/landscape-view.dsl](examples/landscape-view.dsl) - Landscape View example
