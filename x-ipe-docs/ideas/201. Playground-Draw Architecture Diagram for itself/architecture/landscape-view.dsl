@startuml landscape-view
title "X-IPE Integration Landscape"
app-height 1.5
app-width 2

' ===========================================
' External Systems Zone
' ===========================================
zone "External Systems" {
  style "justify-content: space-evenly; column-gap: 24px"
  app-height 1.5
  app-width 2
  
  app "Copilot CLI" as copilot {
    tech: Node.js
    platform: Terminal
    status: healthy
  }
  
  app "GitHub" as github {
    tech: REST API
    platform: Cloud
    status: healthy
  }
  
  app "MCP Servers" as mcp {
    tech: MCP Protocol
    platform: Local/Cloud
    status: healthy
  }
}

' ===========================================
' X-IPE Application Zone
' ===========================================
zone "X-IPE Application" {
  style "justify-content: space-evenly; column-gap: 24px"
  
  app "Flask Backend" as flask {
    tech: Python/Flask
    platform: Local
    status: healthy
  }
  
  app "Web Frontend" as frontend {
    tech: JavaScript
    platform: Browser
    status: healthy
  }
  
  app "WebSocket Terminal" as terminal {
    tech: xterm.js
    platform: Browser
    status: healthy
  }
}

' ===========================================
' Skills & Configuration Zone
' ===========================================
zone "Skills & Configuration" {
  style "justify-content: space-evenly; column-gap: 24px"
  
  app "GitHub Skills" as skills {
    tech: Markdown
    platform: .github/skills/
    status: healthy
  }
  
  app "Tools Config" as toolsconfig {
    tech: JSON
    platform: x-ipe-docs/config/
    status: healthy
  }
  
  app "Themes" as themes {
    tech: Markdown/HTML
    platform: docs/themes/
    status: healthy
  }
}

' ===========================================
' Storage Zone
' ===========================================
zone "Storage" {
  style "justify-content: space-around"
  
  database "Project Files" as projectfiles
  database "Ideas Folder" as ideasfolder
  database "Session Data" as sessiondata
}

' ===========================================
' Action Flows
' ===========================================

' External to X-IPE
copilot --> flask : "Execute Commands"
copilot --> terminal : "Stream Output"
github --> skills : "Load Skills"
mcp --> flask : "Tool Calls"

' X-IPE Internal
frontend --> flask : "API Requests"
frontend --> terminal : "Terminal Input"
flask --> frontend : "Render Templates"
terminal --> flask : "Process Commands"

' X-IPE to Config
flask --> skills : "Load Task Skills"
flask --> toolsconfig : "Read Config"
flask --> themes : "Apply Themes"

' X-IPE to Storage
flask --> projectfiles : "Read/Write Files"
flask --> ideasfolder : "Manage Ideas"
flask --> sessiondata : "Session State"

@enduml
