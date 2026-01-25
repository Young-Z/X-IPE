@startuml module-view
title "E-Commerce Web Application"
direction top-to-bottom
grid 12 x 6

' ===========================================
' Presentation Layer
' ===========================================
layer "Presentation" {
  color "#fce7f3"
  border-color "#ec4899"
  rows 2
  
  module "Web UI" {
    cols 6
    rows 2
    grid 2 x 2
    align center center
    gap 8px
    component "Product Catalog" { cols 1, rows 1 }
    component "Shopping Cart" { cols 1, rows 1 }
    component "Checkout Flow" { cols 1, rows 1 }
    component "User Dashboard" { cols 1, rows 1 }
  }
  
  module "Mobile App" {
    cols 6
    rows 2
    grid 2 x 2
    align center center
    gap 8px
    component "Product Browser" { cols 1, rows 1 }
    component "Cart Manager" { cols 1, rows 1 }
    component "Order Tracker" { cols 1, rows 1 }
    component "Push Notifications" { cols 1, rows 1 }
  }
}

' ===========================================
' Business Logic Layer
' ===========================================
layer "Business Logic" {
  color "#dbeafe"
  border-color "#3b82f6"
  rows 2
  
  module "Order Services" {
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "Order Manager" { cols 1, rows 1 }
    component "Payment Processor" { cols 1, rows 1 }
    component "Shipping Calculator" { cols 1, rows 1 }
  }
  
  module "Product Services" {
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "Catalog Service" { cols 1, rows 1 }
    component "Inventory Tracker" { cols 1, rows 1 }
    component "Pricing Engine" { cols 1, rows 1 }
  }
  
  module "User Services" {
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "Auth Service" { cols 1, rows 1 }
    component "Profile Manager" { cols 1, rows 1 }
    component "Wishlist Service" { cols 1, rows 1 }
  }
}

' ===========================================
' Data Layer
' ===========================================
layer "Data" {
  color "#dcfce7"
  border-color "#22c55e"
  rows 2
  
  module "Databases" {
    cols 6
    rows 2
    grid 2 x 2
    align center center
    gap 8px
    component "Orders DB" { cols 1, rows 1 } <<db>>
    component "Products DB" { cols 1, rows 1 } <<db>>
    component "Users DB" { cols 1, rows 1 } <<db>>
    component "Analytics DB" { cols 1, rows 1 } <<db>>
  }
  
  module "External Services" {
    cols 6
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "Payment Gateway" { cols 1, rows 1 } <<api>>
    component "Shipping API" { cols 1, rows 1 } <<api>>
    component "Email Service" { cols 1, rows 1 } <<api>>
  }
}

@enduml
