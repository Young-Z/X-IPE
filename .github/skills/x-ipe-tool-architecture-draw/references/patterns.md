# Architecture Diagram Patterns

Common architecture patterns for generating DSL diagrams.

---

## Pattern: 3-Tier Architecture

**When:** Standard web application structure

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

---

## Pattern: Microservice Landscape

**When:** Multiple services with integrations

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

---

## Pattern: Hexagonal/Ports & Adapters

**When:** Clean architecture style

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
