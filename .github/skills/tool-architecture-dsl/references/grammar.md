# Architecture DSL Grammar Reference (v2 - Grid-Based)

Complete grammar specification for the Architecture DSL v2 with Bootstrap-inspired 12-column grid system.

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v2.0 | 01-24-2026 | Grid-based layout system (`grid`, `cols`, `rows`, `align`, `gap`) |
| v1.0 | 01-24-2026 | Initial flexbox-based system |

## Document Structure

```
document     := header elements* footer
header       := '@startuml' view-type
view-type    := 'module-view' | 'landscape-view'
footer       := '@enduml'
elements     := (title | theme | direction | grid | text-align | side-column | layer | zone | flow | comment)*
```

### Header

Every DSL document starts with `@startuml` followed by the view type:

```architecture-dsl
@startuml module-view
```

or

```architecture-dsl
@startuml landscape-view
```

**View types:**
- `module-view` - For layered architecture diagrams (layers, modules, components)
- `landscape-view` - For application landscape diagrams (zones, apps, databases, flows)

### Footer

Every DSL document ends with `@enduml`:

```architecture-dsl
@enduml
```

---

## Common Properties

### title

Sets the diagram title. Must be a quoted string.

```
title := 'title' string
string := '"' [^"]* '"'
```

**Example:**
```architecture-dsl
title "AI Platform Architecture"
```

### theme

Specifies the theme to use for rendering. The theme name must match a folder name in `x-ipe-docs/themes/`.

```
theme := 'theme' string
string := '"' [a-zA-Z0-9_-]+ '"'
```

**Example:**
```architecture-dsl
theme "theme-default"
```

**Usage:**
- Renderer loads theme from `x-ipe-docs/themes/{theme-name}/design-system.md`
- If not specified, renderer uses `theme-default`
- Theme defines colors, fonts, and styling tokens

### direction

Controls overall layout direction.

```
direction := 'direction' ('top-to-bottom' | 'left-to-right')
```

**Values:**
- `top-to-bottom` - Layers/zones stack vertically (default)
- `left-to-right` - Layers/zones flow horizontally

**Example:**
```architecture-dsl
direction top-to-bottom
```

### canvas

Specifies explicit width and height for the diagram container. When set, the diagram will render at this exact size instead of auto-sizing.

```
canvas := 'canvas' size ',' size
size := number ('px' | '%')?
number := [0-9]+
```

**Format:** `canvas WIDTH, HEIGHT` or `canvas WIDTH HEIGHT`

**Examples:**
```architecture-dsl
canvas 1200px, 600px   ' Fixed size diagram
canvas 800px, 400px    ' Smaller diagram
canvas 100%, 500px     ' Full width, fixed height
```

**Usage:**
- Use when you need precise control over diagram dimensions
- Useful for embedding in presentations or fixed-layout documents
- If not specified, diagram auto-sizes with max-width of 1200px

### grid (v2 - Document Level)

Defines the document-level grid dimensions.

```
grid := 'grid' number 'x' number
number := [0-9]+
```

**Format:** `grid COLUMNS x ROWS`

**Example:**
```architecture-dsl
grid 12 x 6   ' 12 columns, 6 rows
```

**Usage:**
- Columns: Always use 12 for Bootstrap-like alignment
- Rows: Sum of all layer `rows` values

### text-align

Controls text alignment for titles and labels. Can appear at document, layer, or module level.

```
text-align := 'text-align' ('left' | 'center' | 'right')
```

**Inheritance:** Values inherit downward. A module inherits from its layer, which inherits from document level.

**Example:**
```architecture-dsl
text-align center

layer "App" {
  text-align left   ' Overrides for this layer
}
```

### comment

Single-line and multi-line comments are supported.

```
comment := single-line-comment | multi-line-comment
single-line-comment := "'" [^\n]*
multi-line-comment := "/'" .* "'/"
```

**Examples:**
```architecture-dsl
' This is a single-line comment

/'
This is a
multi-line comment
'/
```

---

## Module View Elements (v2)

Module View is for layered architecture diagrams showing structural decomposition.

### layer

Defines an architectural layer.

```
layer := 'layer' string ('as' alias)? '{' layer-content* '}'
layer-content := rows | module | color | border-color | text-align | comment
alias := identifier
identifier := [a-zA-Z_][a-zA-Z0-9_]*
```

**Properties:**
- `rows` - Number of document grid rows this layer occupies (required in v2)
- `color` - Layer background color (hex)
- `border-color` - Layer border color (hex)

**Example:**
```architecture-dsl
layer "Presentation" as presentation {
  color "#fce7f3"
  border-color "#ec4899"
  rows 2
  
  module "Web UI" { ... }
}
```

### rows (Layer Level)

Specifies how many document grid rows the layer occupies.

```
rows := 'rows' number
number := [0-9]+
```

**Example:**
```architecture-dsl
layer "Business" {
  rows 2   ' This layer occupies 2 rows of the document grid
}
```

### module

Defines a module within a layer.

```
module := 'module' string ('as' alias)? '{' module-content* '}'
module-content := cols | rows | grid | align | gap | component | color | text-align | comment
```

**Properties:**
- `cols` - Number of layer columns (out of 12) this module occupies
- `rows` - Number of layer rows this module spans
- `grid` - Internal grid for components (`grid C x R`)
- `align` - Component alignment within module (`align H V`)
- `gap` - Gap between components

**Example:**
```architecture-dsl
module "Frontend JS" {
  cols 8
  rows 2
  grid 2 x 3
  align center center
  gap 8px
  
  component "Workplace" { cols 1, rows 1 }
  component "Terminal" { cols 1, rows 1 }
}
```

### cols (Module/Component Level)

Specifies column span in parent grid.

```
cols := 'cols' number
number := [0-9]+
```

**Rules:**
- Module `cols` must sum to 12 within a layer
- Component `cols` are relative to module's internal `grid`

**Example:**
```architecture-dsl
' Layer with 3 modules (4 + 4 + 4 = 12)
module "Core" { cols 4 }
module "Config" { cols 4 }
module "Extension" { cols 4 }
```

### rows (Module/Component Level)

Specifies row span in parent grid.

```
rows := 'rows' number
number := [0-9]+
```

**Example:**
```architecture-dsl
' Module spanning 2 layer rows
module "Services" {
  cols 4
  rows 2
}

' Component spanning 2 module rows
component "Tall Item" { cols 1, rows 2 }
```

### grid (Module Level)

Defines internal grid for components within a module.

```
grid := 'grid' number 'x' number
```

**Format:** `grid COLUMNS x ROWS`

**Examples:**
```architecture-dsl
' Vertical stack: 1 column, 3 rows
grid 1 x 3

' 2x2 grid
grid 2 x 2

' Wide grid for 6 components (2 rows of 3)
grid 3 x 2
```

### align (Module Level)

Specifies horizontal and vertical alignment of components within module.

```
align := 'align' h-align v-align
h-align := 'left' | 'center' | 'right'
v-align := 'top' | 'center' | 'bottom'
```

**Example:**
```architecture-dsl
module "Services" {
  align center center   ' Center both horizontally and vertically
}
```

### gap (Module Level)

Specifies gap between components.

```
gap := 'gap' size
size := number 'px' | number 'rem'
```

**Example:**
```architecture-dsl
module "Services" {
  gap 8px
}
```

### component

Defines a component within a module.

```
component := 'component' string ('{' component-props '}')? stereotype?
component-props := cols-prop (',' rows-prop)?
cols-prop := 'cols' number
rows-prop := 'rows' number
stereotype := '<<' identifier '>>'
```

**Examples:**
```architecture-dsl
' Simple component (default: cols 1, rows 1)
component "Service A"

' Component with explicit positioning
component "Service B" { cols 1, rows 1 }

' Wide component spanning 2 columns
component "Wide Service" { cols 2, rows 1 }

' Tall component spanning 2 rows
component "Tall Service" { cols 1, rows 2 }

' Component with stereotype
component "API Client" { cols 1, rows 1 } <<service>>
```

**Stereotypes** are optional decorators:
- `<<model>>` - Data model
- `<<service>>` - Service component
- `<<icon>>` - Visual/icon component
- `<<api>>` - API endpoint
- `<<db>>` - Database related
- `<<file>>` - File reference
- `<<folder>>` - Folder reference

**Stereotype Sizing Rule:**
Stereotyped components render with different proportions than regular components:
- **Width**: 0.5× (half width of a regular component)
- **Height**: 1.5× (one and a half times the height of a regular component)

Since stereotyped components are **half-width**, they fit **more components per row**. Prefer **horizontal layout** (`grid N x 1` where N = component count) for stereotype-only modules:

```architecture-dsl
' ✅ CORRECT: Horizontal for 3 stereotyped components (they're half-width)
module "Project Files" { 
  cols 4
  grid 3 x 1   ' 3 columns × 1 row = HORIZONTAL
  component "x-ipe-docs/" { cols 1, rows 1 } <<folder>>
  component "src/" { cols 1, rows 1 } <<folder>>
  component "static/" { cols 1, rows 1 } <<folder>>
}
```

### color

Sets the background color of a layer or module.

```
color := 'color' string
string := '"' ('#'? [0-9a-fA-F]{6} | color-name) '"'
```

**Suggested Layer Colors:**

| Layer | Light Background | Border |
|-------|------------------|--------|
| Presentation | `#fce7f3` | `#ec4899` |
| Service | `#fef3c7` | `#f97316` |
| Business | `#dbeafe` | `#3b82f6` |
| Data | `#dcfce7` | `#22c55e` |

### border-color

Sets the border color of a layer.

```
border-color := 'border-color' string
```

### side-column (Optional)

Defines a vertical column that spans all layers. Used for cross-cutting concerns.

```
side-column := 'side-column' position '{' side-column-content* '}'
position := '"left"' | '"right"'
side-column-content := title | color | component | separator | comment
separator := '---'
```

**Example:**
```architecture-dsl
side-column "left" {
  title "Shared Types"
  color "#c4b5fd"
  
  component "Entities"
  component "Enums"
}
```

---

## Landscape View Elements

Landscape View is for application integration diagrams showing how systems connect.

### zone

Defines an application zone or domain.

```
zone := 'zone' string '{' zone-content* '}'
zone-content := app | database | comment
```

**Example:**
```architecture-dsl
zone "Frontend" {
  app "Website" as web { ... }
  app "Mobile App" as mobile { ... }
}
```

### app

Defines an application within a zone.

```
app := 'app' string ('as' alias)? '{' app-props* '}'
app-props := tech-prop | platform-prop | status-prop
tech-prop := 'tech:' value
platform-prop := 'platform:' value
status-prop := 'status:' status-value
status-value := 'healthy' | 'warning' | 'critical'
value := [^\n,}]+
```

**Properties:**
- `tech:` - Technology stack (Java, Python, React, etc.)
- `platform:` - Deployment platform (AWS, Azure, On-prem, etc.)
- `status:` - Health status (healthy, warning, critical)

**Examples:**
```architecture-dsl
app "API Gateway" as api {
  tech: Node.js
  platform: AWS Lambda
  status: healthy
}

app "Legacy System" as legacy {
  tech: COBOL
  status: warning
}
```

### database

Defines a database or data store.

```
database := 'database' string ('as' alias)?
```

**Example:**
```architecture-dsl
database "User Database" as userdb
database "Order Store" as orderdb
```

### flow

Defines an action flow (connection) between applications or databases.

```
flow := alias '-->' alias ':' string
```

The label should describe the **action** being performed.

**Good labels (action-focused):**
- `"Submit Order"`
- `"Validate User"`
- `"Sync Inventory"`

**Examples:**
```architecture-dsl
web --> api : "Submit Order"
api --> userdb : "Validate User"
api --> orderdb : "Persist Order"
```

---

## Validation Rules (v2)

### 1. Document Structure (SYNTAX)

- Document MUST start with `@startuml <view-type>`
- Document MUST end with `@enduml`
- View type MUST be `module-view` or `landscape-view`

### 2. Grid Rules (GRID)

- Document MUST have `grid C x R` declaration
- Layer MUST have `rows N` declaration
- Module MUST have `cols N` declaration
- **Module `cols` within a layer MUST sum to 12**
- Component `cols` MUST not exceed module grid columns
- Component `rows` MUST not exceed module grid rows

**Error:** `Module cols sum to 10, expected 12`

### 3. View Type Consistency (VIEW_TYPE)

- Module View elements (`layer`, `module`, `component`) cannot appear in `landscape-view`
- Landscape View elements (`zone`, `app`, `database`, `flow`) cannot appear in `module-view`

### 4. Alias Uniqueness (ALIAS_UNIQUE)

- All aliases within a document MUST be unique

### 5. Flow Target Existence (ALIAS_DEFINED)

- Flow sources and targets MUST reference defined aliases

### 6. Status Values (STATUS_VALUES)

- App status MUST be one of: `healthy`, `warning`, `critical`

---

## Error Messages

| Error Code | Message | Fix |
|------------|---------|-----|
| E001 | Missing @startuml header | Add `@startuml module-view` or `@startuml landscape-view` |
| E002 | Missing @enduml footer | Add `@enduml` at end of document |
| E003 | Invalid view type '{type}' | Use `module-view` or `landscape-view` |
| E004 | Missing grid declaration | Add `grid 12 x N` at document level |
| E005 | Module cols sum to {N}, expected 12 | Adjust module `cols` to sum to 12 |
| E006 | Missing rows declaration in layer | Add `rows N` to layer |
| E007 | Duplicate alias '{alias}' | Use unique alias names |
| E008 | Undefined alias '{alias}' in flow | Define alias before using in flow |
| E009 | Invalid status '{status}' | Use `healthy`, `warning`, or `critical` |
| W001 | Empty container '{name}' | Add child elements or remove container |

---

## Complete Example (v2)

### Module View

```architecture-dsl
@startuml module-view
title "X-IPE Application Architecture"
theme "theme-default"
direction top-to-bottom
grid 12 x 6

' Presentation Layer
layer "Presentation" {
  color "#fce7f3"
  border-color "#ec4899"
  rows 2
  
  module "Jinja2 Templates" { 
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "index.html" { cols 1, rows 1 }
    component "settings.html" { cols 1, rows 1 }
    component "base.html" { cols 1, rows 1 }
  }
  
  module "Frontend JS Modules" { 
    cols 8
    rows 2
    grid 2 x 3
    align center center
    gap 8px
    component "Workplace Manager" { cols 1, rows 1 }
    component "Terminal" { cols 1, rows 1 }
    component "Stage Toolbox" { cols 1, rows 1 }
    component "Content Renderer" { cols 1, rows 1 }
    component "Event Bus" { cols 2, rows 1 }
  }
}

' Business Logic Layer
layer "Business Logic" {
  color "#dbeafe"
  border-color "#3b82f6"
  rows 2
  
  module "Core Services" { 
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "FileService" { cols 1, rows 1 }
    component "IdeasService" { cols 1, rows 1 }
    component "TerminalService" { cols 1, rows 1 }
  }
  
  module "Configuration Services" { 
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "ConfigService" { cols 1, rows 1 }
    component "SettingsService" { cols 1, rows 1 }
    component "ToolsConfigService" { cols 1, rows 1 }
  }
  
  module "Extension Services" { 
    cols 4
    rows 2
    grid 1 x 2
    align center center
    gap 8px
    component "ThemesService" { cols 1, rows 1 }
    component "SkillsService" { cols 1, rows 1 }
  }
}

' Data Layer
layer "Data" {
  color "#dcfce7"
  border-color "#22c55e"
  rows 2
  
  module "Project Files" { 
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "x-ipe-docs/" { cols 1, rows 1 } <<folder>>
    component "src/" { cols 1, rows 1 } <<folder>>
    component "static/" { cols 1, rows 1 } <<folder>>
  }
  
  module "Configuration" { 
    cols 4
    rows 2
    grid 1 x 2
    align center center
    gap 8px
    component "x-ipe-docs/config/tools.json" { cols 1, rows 1 } <<file>>
    component ".x-ipe.yaml" { cols 1, rows 1 } <<file>>
  }
  
  module "Session Data" { 
    cols 4
    rows 2
    grid 1 x 1
    align center center
    gap 8px
    component "instance/" { cols 1, rows 1 } <<folder>>
  }
}

@enduml
```

### Landscape View

```architecture-dsl
@startuml landscape-view
title "Enterprise Integration"
theme "theme-default"

zone "Customer Touchpoints" {
  app "Website" as web {
    tech: React
    platform: AWS CloudFront
    status: healthy
  }
  
  app "Mobile App" as mobile {
    tech: React Native
    platform: App Store
    status: healthy
  }
}

zone "Core Systems" {
  app "API Gateway" as api {
    tech: Node.js
    platform: AWS Lambda
    status: healthy
  }
  
  app "Order Management" as orders {
    tech: Java
    platform: Kubernetes
    status: healthy
  }
}

zone "Data Stores" {
  database "Orders DB" as ordersdb
  database "Customer DB" as customerdb
}

' Action flows
web --> api : "Submit Order"
mobile --> api : "Browse Products"
api --> orders : "Process Order"
orders --> ordersdb : "Persist Order"
orders --> customerdb : "Validate Customer"

@enduml
```
