@startuml module-view
title "X-IPE Application Architecture"
direction top-to-bottom
grid 12 x 6   ' 12 columns x 6 rows

' ===========================================
' Presentation Layer (rows 2)
' ===========================================
layer "Presentation" {
  color "#fce7f3"
  border-color "#ec4899"
  rows 2
  
  module "Jinja2 Templates" { 
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "index.html" { cols 1, rows 1 }
    component "settings.html" { cols 1, rows 1 }
    component "base.html" { cols 1, rows 1 }
  }
  
  module "Frontend JS Modules" { 
    cols 8
    rows 2
    grid 2 x 3
    align center center
    gap 8px
    ' Row 1: primary modules
    component "Workplace Manager" { cols 1, rows 1 }
    component "Terminal" { cols 1, rows 1 }
    ' Row 2: supporting modules
    component "Stage Toolbox" { cols 1, rows 1 }
    component "Content Renderer" { cols 1, rows 1 }
    ' Row 3: spans full width (5th component fills row)
    component "Event Bus" { cols 2, rows 1 }
  }
}

' ===========================================
' Business Logic Layer (rows 2)
' ===========================================
layer "Business Logic" {
  color "#dbeafe"
  border-color "#3b82f6"
  rows 2
  
  module "Core Services" { 
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "FileService" { cols 1, rows 1 }
    component "IdeasService" { cols 1, rows 1 }
    component "TerminalService" { cols 1, rows 1 }
  }
  
  module "Configuration Services" { 
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "ConfigService" { cols 1, rows 1 }
    component "SettingsService" { cols 1, rows 1 }
    component "ToolsConfigService" { cols 1, rows 1 }
  }
  
  module "Extension Services" { 
    cols 4
    rows 2
    grid 1 x 2   ' only 2 real components, use 1x2
    align center center
    gap 8px
    component "ThemesService" { cols 1, rows 1 }
    component "SkillsService" { cols 1, rows 1 }
    ' No fake components - leave as is
  }
}

' ===========================================
' Data Layer (rows 2)
' ===========================================
layer "Data" {
  color "#dcfce7"
  border-color "#22c55e"
  rows 2
  
  module "Project Files" { 
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "x-ipe-docs/" { cols 1, rows 1 } <<folder>>
    component "src/" { cols 1, rows 1 } <<folder>>
    component "static/" { cols 1, rows 1 } <<folder>>
  }
  
  module "Configuration" { 
    cols 4
    rows 2
    grid 1 x 2
    align center center
    gap 8px
    component "x-ipe-docs/config/tools.json" { cols 1, rows 1 } <<file>>
    component ".x-ipe.yaml" { cols 1, rows 1 } <<file>>
  }
  
  module "Session Data" { 
    cols 4
    rows 2
    grid 1 x 1
    align center center
    gap 8px
    component "instance/" { cols 1, rows 1 } <<folder>>
  }
}

@enduml
