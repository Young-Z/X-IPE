# Corporate Style Example - Enterprise Platform

This example demonstrates the corporate template style for professional architecture diagrams.

## Style Characteristics

- **White/light blue layer backgrounds** with solid gray borders
- **Black header bar** with white text for section titles
- **Dark pill badges** for component labels  
- **Side labels** with vertical text for layer identification
- **Icon components** for data/infrastructure items
- **Virtual-box** for transparent logical grouping

## DSL Input

```architecture-dsl
@startuml module-view
title "Enterprise Platform"
style "corporate"
theme "theme-default"

layer "Presentation" {
    module "Web Application" cols 4 grid 1x3 {
        component "Dashboard"
        component "Admin Panel"
        component "Reports"
    }
    module "Frontend Components" cols 8 grid 2x2 {
        component "Navigation"
        component "Forms"
        component "Data Tables"
        component "Charts"
    }
}

layer "Business" highlight {
    module "Domain Services" cols 6 grid 1x3 {
        component "User Service"
        component "Order Service"
        component "Notification Service"
    }
    module "Integration" cols 6 grid 2x2 {
        component "REST API"
        component "GraphQL"
        component "Webhooks"
        component "Events"
    }
}

layer "Data" {
    module "Databases" cols 6 grid 2x1 {
        component "PostgreSQL" icon "database"
        component "Redis Cache" icon "chart"
    }
    module "Storage" cols 6 grid 2x1 {
        component "File Storage" icon "folder"
        component "Cloud Backup" icon "cloud"
    }
}

@enduml
```

## Rendered Output

See: `examples/enterprise-platform-corporate.html`

## Key Features

### 1. Style Declaration
```
style "corporate"
```
Tells the renderer to use `module-view-corporate.html` template.

### 2. Layer Highlight
```
layer "Business" highlight {
```
Applies light blue background (`#eff6ff`) to emphasize the layer.

### 3. Layer Header
Each layer gets a black background header bar with the section title.

### 4. Icon Components
```
component "PostgreSQL" icon "database"
```
Renders as icon + label layout for data layer items.

### 5. Virtual Box Grouping
Use `virtual-box` class for transparent logical grouping without visual borders.

## Template Mapping

| DSL Property | Corporate Template Class |
|--------------|-------------------------|
| `style "corporate"` | Uses `module-view-corporate.html` |
| `highlight` | `.layer-highlight` (light blue bg) |
| `icon "..."` | `.component-icon` |
| virtual grouping | `.virtual-box` (no visual) |
| stacked items | `.component-full` |
