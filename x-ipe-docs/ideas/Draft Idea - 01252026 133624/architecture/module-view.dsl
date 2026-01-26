@startuml module-view
title "Enterprise Knowledge Base - Layered Architecture"
direction top-to-bottom
grid 12 x 10

' ===========================================
' Consumer Layer (rows 2)
' ===========================================
layer "Consumer Interfaces" {
  color "#fef3c7"
  border-color "#f59e0b"
  rows 2
  
  module "AI Consumers" { 
    cols 6
    rows 2
    grid 2 x 2
    align center center
    gap 8px
    component "Internal Chatbots" { cols 1, rows 1 }
    component "GitHub Copilot" { cols 1, rows 1 }
    component "Automation Agents" { cols 1, rows 1 }
    component "Customer AI" { cols 1, rows 1 }
  }
  
  module "Human Consumers" { 
    cols 6
    rows 2
    grid 2 x 2
    align center center
    gap 8px
    component "Employee Portal" { cols 1, rows 1 }
    component "Search UI" { cols 1, rows 1 }
    component "Mobile App" { cols 1, rows 1 }
    component "Admin Console" { cols 1, rows 1 }
  }
}

' ===========================================
' API Gateway Layer (rows 2)
' ===========================================
layer "API Gateway" {
  color "#fce7f3"
  border-color "#ec4899"
  rows 2
  
  module "Gateway Services" { 
    cols 4
    rows 2
    grid 1 x 2
    align center center
    gap 8px
    component "Authentication" { cols 1, rows 1 }
    component "Rate Limiting" { cols 1, rows 1 }
  }
  
  module "API Endpoints" { 
    cols 8
    rows 2
    grid 2 x 2
    align center center
    gap 8px
    component "REST API" { cols 1, rows 1 }
    component "GraphQL API" { cols 1, rows 1 }
    component "Streaming API" { cols 1, rows 1 }
    component "Webhook Handler" { cols 1, rows 1 }
  }
}

' ===========================================
' RAG Engine Layer (rows 2)
' ===========================================
layer "RAG Engine" {
  color "#dbeafe"
  border-color "#3b82f6"
  rows 2
  
  module "Query Processing" { 
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "Query Parser" { cols 1, rows 1 }
    component "Intent Classifier" { cols 1, rows 1 }
    component "Query Expander" { cols 1, rows 1 }
  }
  
  module "Retrieval Pipeline" { 
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "Hybrid Search" { cols 1, rows 1 }
    component "Semantic Ranker" { cols 1, rows 1 }
    component "Context Builder" { cols 1, rows 1 }
  }
  
  module "Generation" { 
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "Prompt Engine" { cols 1, rows 1 }
    component "LLM Router" { cols 1, rows 1 }
    component "Citation Generator" { cols 1, rows 1 }
  }
}

' ===========================================
' Knowledge Processing Layer (rows 2)
' ===========================================
layer "Knowledge Processing" {
  color "#e0e7ff"
  border-color "#6366f1"
  rows 2
  
  module "Ingestion Pipeline" { 
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "Source Connectors" { cols 1, rows 1 }
    component "Document Parser" { cols 1, rows 1 }
    component "Content Cleaner" { cols 1, rows 1 }
  }
  
  module "Embedding Pipeline" { 
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "Chunking Engine" { cols 1, rows 1 }
    component "Embedding Model" { cols 1, rows 1 }
    component "Index Manager" { cols 1, rows 1 }
  }
  
  module "Knowledge Services" { 
    cols 4
    rows 2
    grid 1 x 3
    align center center
    gap 8px
    component "Graph Builder" { cols 1, rows 1 }
    component "Freshness Checker" { cols 1, rows 1 }
    component "Metadata Enricher" { cols 1, rows 1 }
  }
}

' ===========================================
' Data Layer (rows 2)
' ===========================================
layer "Data Storage" {
  color "#dcfce7"
  border-color "#22c55e"
  rows 2
  
  module "Vector Storage" { 
    cols 4
    rows 2
    grid 1 x 2
    align center center
    gap 8px
    component "Pinecone/Milvus" { cols 1, rows 1 } <<db>>
    component "Vector Index" { cols 1, rows 1 } <<db>>
  }
  
  module "Document Storage" { 
    cols 4
    rows 2
    grid 1 x 2
    align center center
    gap 8px
    component "PostgreSQL" { cols 1, rows 1 } <<db>>
    component "S3/Blob Store" { cols 1, rows 1 } <<db>>
  }
  
  module "Knowledge Graph" { 
    cols 4
    rows 2
    grid 1 x 2
    align center center
    gap 8px
    component "Neo4j/Neptune" { cols 1, rows 1 } <<db>>
    component "Graph Index" { cols 1, rows 1 } <<db>>
  }
}

@enduml
