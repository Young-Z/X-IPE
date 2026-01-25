# Landscape View Example: Enterprise Integration

## DSL Input

```architecture-dsl
@startuml landscape-view
title "Enterprise Integration Landscape"

zone "Customer Touchpoints" {
  app "Website" as web {
    tech: React
    platform: AWS CloudFront
    status: healthy
  }
  
  app "Mobile App" as mobile {
    tech: React Native
    platform: iOS/Android
    status: healthy
  }
  
  app "IVR System" as ivr {
    tech: VB6
    platform: Windows
    status: warning
  }
}

zone "Core Services" {
  app "API Gateway" as api {
    tech: Node.js
    platform: AWS Lambda
    status: healthy
  }
  
  app "Order Service" as orders {
    tech: Java/Spring
    platform: Kubernetes
    status: healthy
  }
  
  app "Legacy ERP" as erp {
    tech: COBOL
    platform: Mainframe
    status: critical
  }
}

zone "Data Stores" {
  database "Orders DB" as ordersdb
  database "Customer DB" as customerdb
  database "Analytics DW" as analytics
}

web --> api : "Submit Order"
mobile --> api : "Browse Products"
ivr --> api : "Check Status"
api --> orders : "Process Order"
api --> erp : "Sync Inventory"
orders --> ordersdb : "Persist Order"
orders --> customerdb : "Validate Customer"
erp --> analytics : "Push Metrics"

@enduml
```

## Element Inventory

### Apps

| Alias | Name | Tech | Platform | Status |
|-------|------|------|----------|--------|
| web | Website | React | AWS CloudFront | healthy |
| mobile | Mobile App | React Native | iOS/Android | healthy |
| ivr | IVR System | VB6 | Windows | warning |
| api | API Gateway | Node.js | AWS Lambda | healthy |
| orders | Order Service | Java/Spring | Kubernetes | healthy |
| erp | Legacy ERP | COBOL | Mainframe | critical |

### Databases

| Alias | Name |
|-------|------|
| ordersdb | Orders DB |
| customerdb | Customer DB |
| analytics | Analytics DW |

### Flows

| Source | Target | Action |
|--------|--------|--------|
| web | api | Submit Order |
| mobile | api | Browse Products |
| ivr | api | Check Status |
| api | orders | Process Order |
| api | erp | Sync Inventory |
| orders | ordersdb | Persist Order |
| orders | customerdb | Validate Customer |
| erp | analytics | Push Metrics |

## Template Variables

```
{{TITLE}} = "Enterprise Integration Landscape"
{{FONT_HEADING}} = Inter (from theme)
{{COLOR_PRIMARY}} = #0f172a (from theme)
{{COLOR_ACCENT}} = #3b82f6 (from theme)
```

## Rendered HTML Structure

```html
<div class="landscape">
    <h1 class="landscape-title">Enterprise Integration Landscape</h1>
    
    <div class="zones">
        <!-- Customer Touchpoints Zone -->
        <div class="zone">
            <h3 class="zone-title">Customer Touchpoints</h3>
            <div class="zone-content">
                <div class="app" id="web">
                    <span class="app-status healthy"></span>
                    <h4 class="app-name">Website</h4>
                    <div class="app-meta">
                        <div>Tech: React</div>
                        <div>Platform: AWS CloudFront</div>
                    </div>
                </div>
                <div class="app" id="mobile">
                    <span class="app-status healthy"></span>
                    <h4 class="app-name">Mobile App</h4>
                    <div class="app-meta">
                        <div>Tech: React Native</div>
                        <div>Platform: iOS/Android</div>
                    </div>
                </div>
                <div class="app" id="ivr">
                    <span class="app-status warning"></span>
                    <h4 class="app-name">IVR System</h4>
                    <div class="app-meta">
                        <div>Tech: VB6</div>
                        <div>Platform: Windows</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Core Services Zone -->
        <div class="zone">
            <h3 class="zone-title">Core Services</h3>
            <div class="zone-content">
                <div class="app" id="api">
                    <span class="app-status healthy"></span>
                    <h4 class="app-name">API Gateway</h4>
                    <div class="app-meta">
                        <div>Tech: Node.js</div>
                        <div>Platform: AWS Lambda</div>
                    </div>
                </div>
                <div class="app" id="orders">
                    <span class="app-status healthy"></span>
                    <h4 class="app-name">Order Service</h4>
                    <div class="app-meta">
                        <div>Tech: Java/Spring</div>
                        <div>Platform: Kubernetes</div>
                    </div>
                </div>
                <div class="app" id="erp">
                    <span class="app-status critical"></span>
                    <h4 class="app-name">Legacy ERP</h4>
                    <div class="app-meta">
                        <div>Tech: COBOL</div>
                        <div>Platform: Mainframe</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Data Stores Zone -->
        <div class="zone">
            <h3 class="zone-title">Data Stores</h3>
            <div class="zone-content">
                <div class="database" id="ordersdb">
                    <div class="database-icon">🗄️</div>
                    <div class="database-name">Orders DB</div>
                </div>
                <div class="database" id="customerdb">
                    <div class="database-icon">🗄️</div>
                    <div class="database-name">Customer DB</div>
                </div>
                <div class="database" id="analytics">
                    <div class="database-icon">📊</div>
                    <div class="database-name">Analytics DW</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="flows">
        <h3 class="flows-title">Action Flows</h3>
        <div class="flow-list">
            <div class="flow">
                <span class="flow-source">Website</span>
                <span class="flow-arrow">→</span>
                <span class="flow-target">API Gateway</span>
                <span class="flow-action">"Submit Order"</span>
            </div>
            <div class="flow">
                <span class="flow-source">Mobile App</span>
                <span class="flow-arrow">→</span>
                <span class="flow-target">API Gateway</span>
                <span class="flow-action">"Browse Products"</span>
            </div>
            <!-- ... additional flows ... -->
        </div>
    </div>
</div>
```
