@startuml landscape-view
title "Enterprise Application Landscape"
app-height 1
app-width 1.5

' ===========================================
' Front-End Processing Zone
' ===========================================
zone "Front-End Processing" {
  style "flex-direction: column; row-gap: 16px"
  app-height 1.5
  app-width 2.5
  
  app "Website" as web {
    tech: Java/Spring
    platform: Windows Server
    status: healthy
  }
  
  app "IVR System" as ivr {
    tech: VB6
    platform: Windows
    status: warning
  }
  
  app "Mobile App" as mobile {
    tech: React Native
    platform: iOS/Android
    status: healthy
  }
}

' ===========================================
' Back-End Processing Zone
' ===========================================
zone "Back-End Processing" {
  style "justify-content: space-evenly; column-gap: 24px"
  
  app "ERP-HRM" as hrm {
    tech: C
    platform: Unix
    status: healthy
  }
  
  app "INTRANET Portal" as intranet {
    tech: Java
    platform: Linux
    status: healthy
  }
  
  app "ERP-Financials" as finance {
    tech: COBOL
    platform: Mainframe
    status: critical
  }
  
  app "Monitoring" as monitor {
    tech: Python
    platform: Docker
    status: healthy
  }
}

' ===========================================
' Data Domain Zone
' ===========================================
zone "Data Domain" {
  style "justify-content: space-around"
  
  database "ERP-Marketing DB" as mktdb
  database "ERP-HRM DB" as hrmdb
  database "ERP-Financials DB" as findb
  database "Analytics Warehouse" as analytics
}

' ===========================================
' Action Flows (what operations occur)
' ===========================================

' Frontend to Backend
web --> hrm : "Submit Leave Request"
web --> hrm : "Query Employee Profile"
web --> finance : "View Payslip"

ivr --> hrm : "Verify Employee ID"
ivr --> finance : "Check Account Balance"

mobile --> intranet : "Access Documents"
mobile --> hrm : "Clock In/Out"

' Backend to Backend
intranet --> hrm : "Notify Approval"
hrm --> finance : "Sync Payroll Records"
monitor --> hrm : "Health Check"
monitor --> finance : "Health Check"

' Backend to Data
hrm --> hrmdb : "Persist Employee Data"
hrm --> findb : "Sync Payroll Records"
finance --> findb : "Update Ledger"
intranet --> mktdb : "Fetch Campaigns"

' Analytics flows
hrm --> analytics : "Push HR Metrics"
finance --> analytics : "Push Financial Metrics"

@enduml
