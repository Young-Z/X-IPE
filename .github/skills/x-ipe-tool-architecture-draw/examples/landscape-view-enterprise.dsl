@startuml landscape-view
title "Retail Enterprise Landscape"

' ===========================================
' Customer Touchpoints Zone
' ===========================================
zone "Customer Touchpoints" {
  app "E-Commerce Website" as website {
    tech: React
    platform: AWS CloudFront
    status: healthy
  }
  
  app "Mobile App" as mobile {
    tech: React Native
    platform: App Store / Play Store
    status: healthy
  }
  
  app "In-Store Kiosk" as kiosk {
    tech: Electron
    platform: Windows
    status: healthy
  }
}

' ===========================================
' Integration Zone
' ===========================================
zone "Integration Layer" {
  app "API Gateway" as gateway {
    tech: Kong
    platform: Kubernetes
    status: healthy
  }
  
  app "Event Bus" as events {
    tech: Apache Kafka
    platform: AWS MSK
    status: healthy
  }
}

' ===========================================
' Core Services Zone
' ===========================================
zone "Core Services" {
  app "Order Management" as orders {
    tech: Java/Spring
    platform: Kubernetes
    status: healthy
  }
  
  app "Inventory Service" as inventory {
    tech: Go
    platform: Kubernetes
    status: healthy
  }
  
  app "Customer Service" as customers {
    tech: Node.js
    platform: Kubernetes
    status: healthy
  }
  
  app "Payment Service" as payments {
    tech: Java
    platform: Kubernetes
    status: healthy
  }
}

' ===========================================
' Legacy Systems Zone
' ===========================================
zone "Legacy Systems" {
  app "ERP System" as erp {
    tech: COBOL
    platform: Mainframe
    status: warning
  }
  
  app "Warehouse Management" as wms {
    tech: VB.NET
    platform: Windows Server
    status: warning
  }
}

' ===========================================
' Data Zone
' ===========================================
zone "Data Stores" {
  database "Orders Database" as ordersdb
  database "Inventory Database" as inventorydb
  database "Customer Database" as customersdb
  database "Analytics Warehouse" as analytics
}

' ===========================================
' External Partners Zone
' ===========================================
zone "External Partners" {
  app "Payment Provider" as stripe {
    tech: External API
    platform: Stripe
    status: healthy
  }
  
  app "Shipping Provider" as fedex {
    tech: External API
    platform: FedEx
    status: healthy
  }
}

' ===========================================
' Action Flows
' ===========================================

' Customer → Gateway
website --> gateway : "Browse Products"
website --> gateway : "Submit Order"
mobile --> gateway : "Track Order"
kiosk --> gateway : "Check Inventory"

' Gateway → Services
gateway --> orders : "Create Order"
gateway --> inventory : "Query Stock"
gateway --> customers : "Authenticate User"

' Service → Service
orders --> payments : "Process Payment"
orders --> inventory : "Reserve Stock"
orders --> events : "Publish Order Event"
inventory --> events : "Publish Stock Update"

' Events → Consumers
events --> erp : "Sync Order Data"
events --> wms : "Dispatch to Warehouse"
events --> analytics : "Stream Events"

' Services → Data
orders --> ordersdb : "Persist Order"
inventory --> inventorydb : "Update Stock"
customers --> customersdb : "Store Profile"

' External Integrations
payments --> stripe : "Charge Card"
orders --> fedex : "Schedule Delivery"

' Legacy → Data
erp --> analytics : "Batch Export"
wms --> inventorydb : "Sync Levels"

@enduml
