# Architecture DSL Cheatsheet

Quick reference for generating Architecture DSL diagrams.

## Document Structure

```
@startuml {view-type}      ' module-view or landscape-view
title "..."
grid 12 x {rows}           ' module-view only
...elements...
@enduml
```

---

## Module View

### Layer Syntax
```
layer "Name" {
  color "#hex"
  border-color "#hex"
  rows N
  ...modules...
}
```

### Module Syntax
```
module "Name" {
  cols N              ' MUST sum to 12 across layer
  rows N
  grid C x R          ' Internal component grid
  align H V           ' left|center|right + top|center|bottom
  gap Npx
  ...components...
}
```

### Component Syntax
```
component "Name" { cols N, rows N }
component "Name" { cols N, rows N } <<stereotype>>
```

### Color Palette
| Layer | Background | Border |
|-------|------------|--------|
| Presentation | `#fce7f3` | `#ec4899` |
| Service | `#fef3c7` | `#f97316` |
| Business | `#dbeafe` | `#3b82f6` |
| Data | `#dcfce7` | `#22c55e` |

---

## Landscape View

### Zone Syntax
```
zone "Name" {
  ...apps and databases...
}
```

### App Syntax
```
app "Name" as alias {
  tech: Technology
  platform: Platform
  status: healthy | warning | critical
}
```

### Database Syntax
```
database "Name" as alias
```

### Flow Syntax
```
alias1 --> alias2 : "Action Label"
```

---

## Quick Examples

### Minimal Module View
```architecture-dsl
@startuml module-view
title "Simple App"
grid 12 x 4

layer "Frontend" {
  rows 2
  module "UI" { cols 12, grid 2 x 1, component "Home" { cols 1, rows 1 }, component "Settings" { cols 1, rows 1 } }
}

layer "Backend" {
  rows 2
  module "API" { cols 12, grid 1 x 1, component "Server" { cols 1, rows 1 } }
}
@enduml
```

### Minimal Landscape View
```architecture-dsl
@startuml landscape-view
title "Simple Integration"

zone "Apps" {
  app "Website" as web { tech: React, status: healthy }
  app "API" as api { tech: Node, status: healthy }
}

zone "Data" {
  database "DB" as db
}

web --> api : "Call API"
api --> db : "Query"
@enduml
```

---

## Validation Rules

| Rule | Requirement |
|------|-------------|
| Cols | Must sum to 12 per layer |
| Rows | Required on every layer |
| Grid | Document must have `grid C x R` |
| Alias | Must be unique, defined before use |
| Status | healthy, warning, or critical |

---

## Common Patterns

### 3 Equal Modules
```
module "A" { cols 4 }
module "B" { cols 4 }
module "C" { cols 4 }
```

### 2 Unequal Modules
```
module "Wide" { cols 8 }
module "Narrow" { cols 4 }
```

### Vertical Stack (1 column, N rows)
```
module "Stack" {
  grid 1 x 3
  component "Top" { cols 1, rows 1 }
  component "Middle" { cols 1, rows 1 }
  component "Bottom" { cols 1, rows 1 }
}
```

### Spanning Component
```
grid 2 x 2
component "A" { cols 1, rows 1 }
component "B" { cols 1, rows 1 }
component "Wide" { cols 2, rows 1 }  ' Spans full width
```
