@startuml module-view
title "E-Commerce Platform Architecture"
direction top-to-bottom
text-align center
component-height 1
component-width 1.5

' ===========================================
' Presentation Layer
' ===========================================
layer "Presentation" as presentation {
  style "justify-content: center"
  
  module "User Interfaces" {
    style "justify-content: space-evenly; column-gap: 12px"
    component "Web Application"
    component "Mobile App"
    component "Admin Dashboard"
  }
}

' ===========================================
' Business Logic Layer
' ===========================================
layer "Business Logic" as business {
  text-align left
  component-height 1.5
  component-width 2
  style "flex-direction: row; justify-content: space-between; column-gap: 16px"
  
  virtual-box {
    module "Core Services" {
      style "flex-direction: column; row-gap: 8px"
      component "Order Service" <<service>>
      component "Product Catalog" <<service>>
      component "User Management" <<service>>
    }
  }
  
  virtual-box {
    module "Integration Services" {
      style "justify-content: space-evenly"
      component "Payment Gateway" <<api>>
      component "Shipping API" <<api>>
      component "Notification Service" <<service>>
    }
    
    module "Cross-Cutting Concerns" {
      style "justify-content: flex-start; column-gap: 8px"
      component "Authentication"
      component "Logging"
      component "Caching"
    }
  }
}

' ===========================================
' Data Layer
' ===========================================
layer "Data" as data {
  style "flex-direction: row; justify-content: space-evenly"
  
  module "Primary Storage" {
    style "justify-content: space-around; align-items: flex-end"
    component "PostgreSQL" <<db>>
    component "Redis Cache" <<db>>
    component "Elasticsearch" <<db>>
  }
  
  module "External Systems" {
    style "justify-content: space-around; align-items: flex-end"
    component "Message Queue" <<icon>>
    component "File Storage" <<icon>>
    component "CDN" <<icon>>
  }
}

@enduml
