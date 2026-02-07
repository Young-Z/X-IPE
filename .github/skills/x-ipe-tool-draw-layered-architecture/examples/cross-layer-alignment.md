# Cross-Layer Alignment Example

Demonstrates how matching `cols` values create vertical alignment across layers.

## DSL Input

```architecture-dsl
@startuml module-view
title "Microservices with Aligned Data Stores"
direction top-to-bottom
grid 12 x 8

layer "API Gateway" {
  color "#fef3c7"
  border-color "#f97316"
  rows 2
  
  module "Gateway" {
    cols 12
    grid 4 x 1
    align center center
    gap 12px
    component "Auth Middleware" { cols 1, rows 1 }
    component "Rate Limiter" { cols 1, rows 1 }
    component "Router" { cols 1, rows 1 }
    component "Load Balancer" { cols 1, rows 1 }
  }
}

layer "Microservices" {
  color "#dbeafe"
  border-color "#3b82f6"
  rows 3
  
  module "User Service" {
    cols 4
    grid 1 x 3
    align center center
    gap 8px
    component "UserController" { cols 1, rows 1 }
    component "UserService" { cols 1, rows 1 }
    component "UserRepository" { cols 1, rows 1 }
  }
  
  module "Order Service" {
    cols 4
    grid 1 x 3
    align center center
    gap 8px
    component "OrderController" { cols 1, rows 1 }
    component "OrderService" { cols 1, rows 1 }
    component "OrderRepository" { cols 1, rows 1 }
  }
  
  module "Product Service" {
    cols 4
    grid 1 x 3
    align center center
    gap 8px
    component "ProductController" { cols 1, rows 1 }
    component "ProductService" { cols 1, rows 1 }
    component "ProductRepository" { cols 1, rows 1 }
  }
}

layer "Data Layer" {
  color "#dcfce7"
  border-color "#22c55e"
  rows 2
  
  module "User DB" {
    cols 4
    grid 1 x 1
    align center center
    component "PostgreSQL" { cols 1, rows 1 }
  }
  
  module "Order DB" {
    cols 4
    grid 1 x 1
    align center center
    component "MongoDB" { cols 1, rows 1 }
  }
  
  module "Product DB" {
    cols 4
    grid 1 x 1
    align center center
    component "Elasticsearch" { cols 1, rows 1 }
  }
}

@enduml
```

## Alignment Analysis

### Layer 1: API Gateway
- Gateway module: `cols 12` (full width)

### Layer 2: Microservices
- User Service: `cols 4` (columns 1-4)
- Order Service: `cols 4` (columns 5-8)
- Product Service: `cols 4` (columns 9-12)

### Layer 3: Data Layer
- User DB: `cols 4` (columns 1-4) → **Aligns with User Service**
- Order DB: `cols 4` (columns 5-8) → **Aligns with Order Service**
- Product DB: `cols 4` (columns 9-12) → **Aligns with Product Service**

## Visual Result

The matching `cols 4` values in Microservices and Data Layer create perfect vertical alignment:

| Column Range | Microservices Layer | Data Layer |
|--------------|---------------------|------------|
| 1-4 | User Service | User DB |
| 5-8 | Order Service | Order DB |
| 9-12 | Product Service | Product DB |

## Key Pattern

To achieve vertical alignment:
1. Use the same `cols` value for related modules across layers
2. Position modules in the same order within each layer
3. The grid system automatically aligns boundaries

This pattern is useful for:
- Service-to-database relationships
- Frontend-to-backend mappings
- Any vertical dependency visualization
