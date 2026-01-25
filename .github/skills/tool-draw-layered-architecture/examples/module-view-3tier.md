# Module View Example: 3-Tier Architecture

## DSL Input

```architecture-dsl
@startuml module-view
title "3-Tier Web Application"
direction top-to-bottom
grid 12 x 6

layer "Presentation" {
  color "#fce7f3"
  border-color "#ec4899"
  rows 2
  
  module "Web UI" {
    cols 12
    grid 3 x 1
    align center center
    gap 12px
    component "React App" { cols 1, rows 1 }
    component "Redux Store" { cols 1, rows 1 }
    component "Router" { cols 1, rows 1 }
  }
}

layer "Business" {
  color "#dbeafe"
  border-color "#3b82f6"
  rows 2
  
  module "API Layer" {
    cols 6
    grid 1 x 2
    align center center
    gap 8px
    component "Express Server" { cols 1, rows 1 }
    component "REST Controllers" { cols 1, rows 1 }
  }
  
  module "Services" {
    cols 6
    grid 1 x 2
    align center center
    gap 8px
    component "AuthService" { cols 1, rows 1 }
    component "UserService" { cols 1, rows 1 }
  }
}

layer "Data" {
  color "#dcfce7"
  border-color "#22c55e"
  rows 2
  
  module "Persistence" {
    cols 12
    grid 3 x 1
    align center center
    gap 12px
    component "PostgreSQL" { cols 1, rows 1 }
    component "Prisma ORM" { cols 1, rows 1 }
    component "Redis Cache" { cols 1, rows 1 }
  }
}

@enduml
```

## Grid Analysis

| Layer | Modules | Cols Sum | Valid |
|-------|---------|----------|-------|
| Presentation | Web UI (12) | 12 | ✓ |
| Business | API Layer (6) + Services (6) | 12 | ✓ |
| Data | Persistence (12) | 12 | ✓ |

## Template Variables

```
{{TITLE}} = "3-Tier Web Application"
{{ROW_COUNT}} = 6
{{FONT_HEADING}} = Inter (from theme)
{{COLOR_PRIMARY}} = #0f172a (from theme)
```

## Rendered HTML Structure

```html
<div class="diagram">
    <h1 class="diagram-title">3-Tier Web Application</h1>
    <div class="diagram-content">
        <!-- Presentation Layer -->
        <div class="layer layer-presentation rows-2" data-label="Presentation">
            <div class="module cols-12">
                <h3 class="module-title">Web UI</h3>
                <div class="module-content grid-3x1 align-center align-middle">
                    <div class="component">React App</div>
                    <div class="component">Redux Store</div>
                    <div class="component">Router</div>
                </div>
            </div>
        </div>
        
        <!-- Business Layer -->
        <div class="layer layer-business rows-2" data-label="Business">
            <div class="module cols-6">
                <h3 class="module-title">API Layer</h3>
                <div class="module-content grid-1x2 align-center align-middle">
                    <div class="component">Express Server</div>
                    <div class="component">REST Controllers</div>
                </div>
            </div>
            <div class="module cols-6">
                <h3 class="module-title">Services</h3>
                <div class="module-content grid-1x2 align-center align-middle">
                    <div class="component">AuthService</div>
                    <div class="component">UserService</div>
                </div>
            </div>
        </div>
        
        <!-- Data Layer -->
        <div class="layer layer-data rows-2" data-label="Data">
            <div class="module cols-12">
                <h3 class="module-title">Persistence</h3>
                <div class="module-content grid-3x1 align-center align-middle">
                    <div class="component">PostgreSQL</div>
                    <div class="component">Prisma ORM</div>
                    <div class="component">Redis Cache</div>
                </div>
            </div>
        </div>
    </div>
</div>
```
