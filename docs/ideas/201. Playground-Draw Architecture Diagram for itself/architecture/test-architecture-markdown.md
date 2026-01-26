# Architecture DSL Test

This markdown file demonstrates the Architecture DSL rendering in markdown preview.

## Simple Architecture Diagram

```architecture-dsl
@startuml module-view
title "Simple 3-Tier Architecture"
grid 12 x 3

layer "Presentation" {
  color "#fce7f3"
  border-color "#ec4899"
  rows 1
  
  module "Web UI" {
    cols 12
    grid 3 x 1
    component "React App" { cols 1, rows 1 }
    component "Dashboard" { cols 1, rows 1 }
    component "Admin Panel" { cols 1, rows 1 }
  }
}

layer "Business Logic" {
  color "#dbeafe"
  border-color "#3b82f6"
  rows 1
  
  module "API Services" {
    cols 6
    grid 2 x 1
    component "REST API" { cols 1, rows 1 }
    component "GraphQL" { cols 1, rows 1 }
  }
  
  module "Core Services" {
    cols 6
    grid 2 x 1
    component "Auth Service" { cols 1, rows 1 }
    component "User Service" { cols 1, rows 1 }
  }
}

layer "Data" {
  color "#dcfce7"
  border-color "#22c55e"
  rows 1
  
  module "Storage" {
    cols 12
    grid 3 x 1
    component "PostgreSQL" { cols 1, rows 1 } <<db>>
    component "Redis Cache" { cols 1, rows 1 } <<db>>
    component "S3 Storage" { cols 1, rows 1 } <<folder>>
  }
}
@enduml
```

## Notes

The diagram above should render as a layered architecture diagram with:
- Pink Presentation layer with Web UI module
- Blue Business Logic layer with API and Core services
- Green Data layer with storage components (showing icons)
