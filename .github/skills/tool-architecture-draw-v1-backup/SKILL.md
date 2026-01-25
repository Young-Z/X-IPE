---
name: tool-architecture-draw
description: Generate architecture diagrams (Module View and Application Landscape) from idea context. Uses Architecture DSL syntax for version-controlled, grid-based layouts. Invoked by task-type-idea-to-architecture. Triggers on requests like "draw architecture", "create module diagram", "visualize landscape".
---

# Tool: Architecture Draw

## Purpose

Generate professional architecture diagrams from idea context by:
1. Reading the idea summary and architectural needs
2. Analyzing system structure for appropriate diagram type
3. Generating Architecture DSL code
4. Creating visual HTML rendering
5. Saving artifacts to the idea folder

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `tool-architecture-dsl` skill, learn it first for DSL syntax reference.
- This skill focuses on **generating diagrams**, not defining DSL syntax.

### ⚠️ Architecture Focus Only

**When generating diagrams, focus ONLY on architectural structure:**

| Focus On | Ignore |
|----------|--------|
| System layers and modules | UI/UX mockups |
| Component decomposition | User interaction flows |
| Integration relationships | Visual styling preferences |
| Application landscape | Screen layouts |
| Data flow between systems | Color schemes for UI |

**Rationale:** Architecture diagrams show system structure, not user interfaces. UI mockups are handled by `tool-frontend-design`.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Tool Type | Architecture Draw |
| Used By | task-type-idea-to-architecture |
| Output Format | Architecture DSL + HTML |

---

## Tool Required Input Attributes

| Attribute | Default Value | Description |
|-----------|---------------|-------------|
| Current Idea Folder | N/A | **Required from context** - path to idea folder |
| Diagram Type | auto | `module-view`, `landscape-view`, or `auto` (detect) |
| Architecture Context | N/A | Extracted architecture info from idea summary |

---

## Supported Diagram Types

### 1. Module View

**Use For:** Layered architecture decomposition showing internal structure.

**Elements:**
- **Layers** - Horizontal tiers (Presentation, Business, Data)
- **Modules** - Logical groupings within layers
- **Components** - Individual services, files, classes

**When to Use:**
- Single application architecture
- Microservice internal structure
- Library/SDK organization
- Framework component layout

### 2. Application Landscape (Landscape View)

**Use For:** Enterprise integration showing how applications connect.

**Elements:**
- **Zones** - Application domains (Frontend, Backend, Data)
- **Apps** - Individual applications with tech/platform/status
- **Databases** - Data stores
- **Flows** - Action-based connections between systems

**When to Use:**
- Multi-application ecosystem
- Enterprise integration map
- System-to-system communication
- Infrastructure overview

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | `Current Idea Folder` is set | Yes |
| 2 | Idea summary exists with architecture context | Yes |
| 3 | Diagram type determined (or auto-detect) | Yes |

---

## Execution Flow

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Validate Context | Verify idea folder and summary exist | Context validated |
| 2 | Analyze Architecture | Extract structure from idea | Architecture understood |
| 3 | Select Diagram Type | Choose module-view or landscape-view | Type selected |
| 4 | Generate DSL | Create Architecture DSL code | DSL generated |
| 5 | Validate DSL | Check syntax and rules | DSL valid |
| 6 | Render HTML | Generate visual diagram | HTML created |
| 7 | Save Artifacts | Store DSL and HTML | Artifacts saved |

---

## Execution Procedure

### Step 1: Validate Context

**Action:** Verify the idea folder and architecture context

```
1. Validate Current Idea Folder exists
2. Load latest idea-summary-vN.md
3. Extract architecture-relevant content:
   - System components mentioned
   - Integration points
   - Technology stack
   - Data flows
```

### Step 2: Analyze Architecture

**Action:** Understand the system structure from idea context

**Analysis Questions:**
```
1. Is this a single application or multi-application ecosystem?
   → Single = Module View
   → Multi = Landscape View

2. What are the main structural layers/zones?
   → Identify 2-4 primary groupings

3. What are the key components/apps?
   → List main building blocks

4. What are the relationships between components?
   → Identify dependencies and data flows
```

**Structure Extraction:**

| Idea Content | Architecture Element |
|--------------|---------------------|
| "frontend", "UI", "templates" | Presentation Layer |
| "API", "services", "business logic" | Business Layer |
| "database", "storage", "files" | Data Layer |
| "connects to", "integrates with" | Flow/Dependency |
| "external system", "third party" | External Zone |

### Step 3: Select Diagram Type

**Decision Matrix:**

| Condition | Diagram Type |
|-----------|--------------|
| Single app with internal structure | `module-view` |
| Multiple apps with integrations | `landscape-view` |
| Library/SDK architecture | `module-view` |
| Enterprise system map | `landscape-view` |
| Microservice internals | `module-view` |
| Microservice ecosystem | `landscape-view` |

### Step 4: Generate DSL

**Action:** Create Architecture DSL based on diagram type

#### For Module View:

```architecture-dsl
@startuml module-view
title "{Idea Name} Architecture"
direction top-to-bottom
grid 12 x {layer_count * 2}

' Layer template (repeat for each layer)
layer "{Layer Name}" {
  color "{layer_color}"
  border-color "{border_color}"
  rows 2
  
  module "{Module Name}" {
    cols {N}        ' Must sum to 12 across layer
    rows 2
    grid {C} x {R}  ' Internal component grid
    align center center
    gap 8px
    
    component "{Component Name}" { cols 1, rows 1 }
  }
}

@enduml
```

**Grid Math Rules:**
- Document: Always 12 columns
- Rows: 2 per layer (total = layers × 2)
- Module `cols` MUST sum to 12 within each layer
- Components fill module's internal grid

**Suggested Colors:**

| Layer | Background | Border |
|-------|------------|--------|
| Presentation | `#fce7f3` | `#ec4899` |
| Service | `#fef3c7` | `#f97316` |
| Business | `#dbeafe` | `#3b82f6` |
| Data | `#dcfce7` | `#22c55e` |

#### For Landscape View:

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

' Action flows (action-focused labels)
{source} --> {target} : "{Action Description}"

@enduml
```

**Flow Label Guidelines:**
- Use action verbs: "Submit Order", "Validate User"
- NOT protocols: "HTTP", "REST", "JDBC"
- Describe WHAT happens, not HOW

### Step 5: Validate DSL

**Action:** Check DSL against validation rules

**Validation Checklist:**

| Rule | Check |
|------|-------|
| SYNTAX | `@startuml` and `@enduml` present |
| GRID | `grid C x R` declared (module-view) |
| COLS | Module cols sum to 12 in each layer |
| ROWS | Each layer has `rows N` |
| ALIAS | All aliases unique |
| FLOW | Flow targets are defined aliases |

**Common Errors:**
```
E005: Module cols sum to 10, expected 12
→ Fix: Adjust cols to sum to 12

E008: Undefined alias 'api' in flow
→ Fix: Add `as api` to app definition
```

### Step 6: Render HTML

**Action:** Generate visual HTML from DSL

**HTML Template Structure:**
```html
<!DOCTYPE html>
<html>
<head>
  <title>{Diagram Title}</title>
  <style>
    /* Grid-based layout CSS */
    .architecture-container { ... }
    .layer { ... }
    .module { ... }
    .component { ... }
  </style>
</head>
<body>
  <div class="architecture-container">
    <!-- Rendered diagram -->
  </div>
</body>
</html>
```

**Rendering Approach:**
1. Parse DSL structure
2. Calculate grid positions
3. Generate CSS Grid layout
4. Apply colors and styling
5. Create responsive container

### Step 7: Save Artifacts

**Action:** Store all artifacts in idea folder

**Directory Structure:**
```
{Current Idea Folder}/
├── idea-summary-vN.md
├── architecture/
│   ├── {diagram-name}.dsl       (Architecture DSL source)
│   ├── {diagram-name}.html      (Rendered visual)
│   └── README.md                (Diagram explanation)
```

**Naming Convention:**
```
{type}-{name}-v{version}.{ext}

Examples:
- module-view-app-architecture-v1.dsl
- landscape-view-enterprise-v1.dsl
- module-view-app-architecture-v1.html
```

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Architecture context extracted from idea | Yes |
| 2 | Appropriate diagram type selected | Yes |
| 3 | DSL code generated and validated | Yes |
| 4 | HTML rendering created | Yes |
| 5 | Artifacts saved to `{idea_folder}/architecture/` | Yes |

---

## Skill Output

```yaml
diagram_type: module-view | landscape-view
dsl_path: {Current Idea Folder}/architecture/{name}.dsl
html_path: {Current Idea Folder}/architecture/{name}.html
elements:
  layers: N          # for module-view
  modules: N         # for module-view
  components: N      # for module-view
  zones: N           # for landscape-view
  apps: N            # for landscape-view
  flows: N           # for landscape-view
```

---

## DSL Quick Reference

### Module View Syntax

```architecture-dsl
@startuml module-view
title "Title"
direction top-to-bottom
grid 12 x 6

layer "Layer Name" {
  color "#hex"
  border-color "#hex"
  rows 2
  
  module "Module Name" {
    cols 4              ' Sum to 12
    rows 2
    grid 2 x 2          ' Internal grid
    align center center
    gap 8px
    
    component "Name" { cols 1, rows 1 }
    component "Wide" { cols 2, rows 1 }   ' Spans 2 cols
  }
}

@enduml
```

### Landscape View Syntax

```architecture-dsl
@startuml landscape-view
title "Title"

zone "Zone Name" {
  app "App Name" as alias {
    tech: Technology
    platform: Platform
    status: healthy | warning | critical
  }
  
  database "DB Name" as alias
}

alias1 --> alias2 : "Action Label"

@enduml
```

---

## Patterns

### Pattern: 3-Tier Architecture

**When:** Standard web application structure
**Generate:**
```architecture-dsl
@startuml module-view
title "3-Tier Architecture"
grid 12 x 6

layer "Presentation" { rows 2
  module "UI" { cols 12, grid 3 x 1 }
}
layer "Business" { rows 2
  module "Services" { cols 12, grid 3 x 1 }
}
layer "Data" { rows 2
  module "Persistence" { cols 12, grid 2 x 1 }
}
@enduml
```

### Pattern: Microservice Landscape

**When:** Multiple services with integrations
**Generate:**
```architecture-dsl
@startuml landscape-view
title "Microservice Landscape"

zone "API Gateway" {
  app "Gateway" as gw { tech: Kong }
}
zone "Services" {
  app "User Service" as user { tech: Node.js }
  app "Order Service" as order { tech: Java }
}
zone "Data" {
  database "User DB" as userdb
  database "Order DB" as orderdb
}

gw --> user : "Route /users"
gw --> order : "Route /orders"
user --> userdb : "Persist"
order --> orderdb : "Persist"
@enduml
```

### Pattern: Hexagonal/Ports & Adapters

**When:** Clean architecture style
**Generate:**
```architecture-dsl
@startuml module-view
title "Hexagonal Architecture"
grid 12 x 6

layer "Adapters (Input)" { rows 2
  module "HTTP" { cols 4 }
  module "CLI" { cols 4 }
  module "Events" { cols 4 }
}
layer "Core Domain" { rows 2
  module "Use Cases" { cols 6 }
  module "Entities" { cols 6 }
}
layer "Adapters (Output)" { rows 2
  module "Repository" { cols 6 }
  module "External APIs" { cols 6 }
}
@enduml
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Cols not summing to 12 | DSL validation fails | Always ensure cols = 12 |
| Missing rows on layers | Layout breaks | Every layer needs `rows N` |
| Protocol labels on flows | Not action-focused | Use "Submit Order", not "REST" |
| Too many layers (>5) | Diagram too complex | Consolidate or split diagrams |
| Empty modules | Visual gaps | Either populate or remove |
| Mixing view types | Confusing diagram | One type per diagram |

---

## Examples

See [examples/](examples/) for complete diagram examples:
- `module-view-webapp.dsl` - Standard web application
- `landscape-view-enterprise.dsl` - Enterprise integration map

See [references/](references/) for additional documentation:
- `dsl-cheatsheet.md` - Quick syntax reference
