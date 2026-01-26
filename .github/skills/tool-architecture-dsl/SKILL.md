---
name: tool-architecture-dsl
description: Generate Architecture DSL from requirements or refine existing DSL. Use for layered architectures (Module View) or application landscapes (Landscape View). Triggers on "architecture diagram", "layer diagram", "module view", "landscape view", "draw architecture".
version: 2.0
---

# Architecture DSL Tool

Generate Architecture DSL definitions for software architecture diagrams.

## IPE Markdown Support

**IPE natively renders Architecture DSL** in markdown files. Embed directly using:

````markdown
```architecture-dsl
@startuml module-view
title "Your Architecture"
...
@enduml
```
````

This renders as an **interactive diagram** in the IPE viewer - no HTML files needed for ideation documents.

## When to Use

| Use Architecture DSL | Use Mermaid |
|---------------------|-------------|
| Layered/tiered architecture | Flowcharts |
| Application landscapes | Sequence diagrams |
| System integration maps | Class/ER diagrams |

---

## Quick Reference

### Document Structure

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

### Critical Rules

| Rule | Requirement |
|------|-------------|
| **Module cols** | MUST sum to 12 per layer |
| **grid C x R** | C = columns, R = rows |
| **Layer rows** | Required for each layer |
| **Multi-line names** | Use `\n` in names to wrap text |
| **canvas** | Optional: explicit width/height (e.g., `canvas 1200px, 600px`) |

### Grid Syntax

```
grid 12 x 6    → Document: 12 cols, 6 rows
rows 2         → Layer occupies 2 document rows
cols 4         → Module takes 4/12 width
grid 2 x 3     → Module internal: 2 cols × 3 rows
```

### Multi-line Names

For long names in layers, modules, or components, use `\n` to break lines:

```architecture-dsl
layer "Platform Services\n(BUILD + CONFIGURE)" {
  ...
  module "Source\nConnectors" {
    ...
    component "Azure\nOpenAI" { cols 1, rows 1 }
  }
}
```

Renders as:
- Layer label: "PLATFORM SERVICES" on line 1, "(BUILD + CONFIGURE)" on line 2
- Module title: "Source" on line 1, "Connectors" on line 2
- Component: "Azure" on line 1, "OpenAI" on line 2

---

## Stereotype Components

Components with stereotypes (`<<file>>`, `<<folder>>`, `<<icon>>`, etc.) render at **half width** (0.5×) and **1.5× height**.

### Layout Rule for Stereotypes

Since stereotyped components are **half-width**, they fit **more per row**:

| Module cols | Regular components/row | Stereotyped components/row |
|-------------|------------------------|---------------------------|
| 4 | 2-3 | 4-6 |
| 8 | 4-6 | 8-12 |
| 12 | 6-8 | 12-16 |

**Prefer HORIZONTAL layout for stereotype-only modules:**

```architecture-dsl
' ✅ CORRECT: Horizontal for 3 stereotyped components
module "Project Files" { 
  cols 4
  rows 2
  grid 3 x 1   ' 3 columns × 1 row = HORIZONTAL
  align center center
  component "x-ipe-docs/" { cols 1, rows 1 } <<folder>>
  component "src/" { cols 1, rows 1 } <<folder>>
  component "static/" { cols 1, rows 1 } <<folder>>
}

' ❌ WRONG: Vertical wastes horizontal space
module "Project Files" { 
  cols 4
  rows 2
  grid 1 x 3   ' 1 column × 3 rows = vertical (wastes space)
  ...
}
```

**Available Stereotypes:** `<<file>>`, `<<folder>>`, `<<model>>`, `<<service>>`, `<<icon>>`, `<<api>>`, `<<db>>`

---

## Module View Generation

### Step 1: Identify Layers

Standard tiers: Presentation → Business/Application → Data

### Step 2: Calculate Grid

```
Document rows = sum of all layer rows
Document cols = always 12
```

### Step 3: Allocate Module Cols

| Split | Cols per module |
|-------|-----------------|
| 2 equal | 6 + 6 |
| 3 equal | 4 + 4 + 4 |
| 1 wide + 1 narrow | 8 + 4 |
| 1 wide + 2 narrow | 6 + 3 + 3 |

### Step 4: Plan Component Grid

```
Module internal grid = ceil(sqrt(component_count)) x needed_rows
```

For N components:
- 1-2: `grid 2 x 1`
- 3-4: `grid 2 x 2`
- 5-6: `grid 3 x 2` or `grid 2 x 3`
- 7-9: `grid 3 x 3`

---

## Landscape View Generation

```architecture-dsl
@startuml landscape-view
title "Title"

zone "Zone Name" {
  app "App" as alias {
    tech: Technology
    platform: Platform
    status: healthy | warning | critical
  }
  database "DB" as alias
}

' Action flows (verb-based labels)
alias1 --> alias2 : "Action Description"

@enduml
```

---

## Layer Colors

| Layer | Background | Border |
|-------|------------|--------|
| Presentation | `#fce7f3` | `#ec4899` |
| Business | `#dbeafe` | `#3b82f6` |
| Data | `#dcfce7` | `#22c55e` |

---

## Translation Patterns

| Input | Output |
|-------|--------|
| "3 layers: X, Y, Z" | 3 layers with `rows 2` each, `grid 12 x 6` |
| "split into 3 parts" | 3 modules with `cols 4` |
| "one wide, one narrow" | `cols 8` + `cols 4` |
| "stack vertically" | `grid 1 x N` |
| "X connects to Y" | `x --> y : "Action"` |

---

## Validation Checklist

Before outputting DSL:

- [ ] `@startuml` and `@enduml` present
- [ ] `grid C x R` declared at document level
- [ ] Each layer has `rows N`
- [ ] Each module has `cols N`
- [ ] Module `cols` sum to 12 per layer
- [ ] Stereotype modules use horizontal grid (`grid N x 1`)
- [ ] Aliases unique, flows reference valid aliases

---

## References

- [references/grammar.md](references/grammar.md) - Complete DSL grammar
- [references/layout-principles.md](references/layout-principles.md) - Detailed layout guidelines
- [examples/](examples/) - Example DSL files
