# Examples — Constructor App Reverse Engineering

> Worked examples for each of the 4 operations. Each example shows input, processing, and output.

---

## Example 1: provide_framework

**Scenario:** Build an RE framework for a Python FastAPI microservices project.

### Input

```yaml
operation: provide_framework
context:
  request_context:
    app_name: "order-service"
    repo_path: "/repos/order-service"
    language: "python"
    repo_type: "microservices"
    source_paths: ["src/", "services/", "tests/"]
  output_format: "markdown"
```

### Processing

1. Load `templates/playbook-template.md` (base 8-section layout)
2. Load `templates/mixin-python.md` (Python overlays: FastAPI endpoints, Pydantic models, pytest)
3. Load `templates/mixin-microservices.md` (microservices overlays: service landscape, inter-service communication)
4. Compose framework: merge base + Python overlays + microservices overlays
5. Map each section to its sub-skill:
   - Section 1 → `x-ipe-tool-rev-eng-architecture-recovery` (with landscape view overlay from microservices mixin)
   - Section 2 → `x-ipe-tool-rev-eng-api-contract-extraction` (with FastAPI extraction from Python mixin)
   - ...and so on for all 8 sections

### Output

```yaml
operation_output:
  success: true
  operation: "provide_framework"
  result:
    framework_document:
      title: "order-service — Reverse Engineering Report"
      sections:
        - id: "section-01"
          title: "Architecture Recovery"
          sub_skill: "x-ipe-tool-rev-eng-architecture-recovery"
          subsections: ["1.1 Conceptual Level", "1.2 Logical Level", "1.3 Physical Level", "1.4 Data Flow Level"]
          overlays: ["Service Landscape View (microservices)", "Python package layout"]
        - id: "section-02"
          title: "API Contract Extraction"
          sub_skill: "x-ipe-tool-rev-eng-api-contract-extraction"
          subsections: ["2.1 Internal APIs", "2.2 External APIs", "2.3 Per-API-Group", "2.4 Schema Docs"]
          overlays: ["FastAPI endpoints", "Pydantic models", "Inter-service contracts"]
        # ... sections 3-8
    toc_structure:
      - { id: "section-01", title: "Architecture Recovery", sub_skill: "x-ipe-tool-rev-eng-architecture-recovery", depth: 2 }
      - { id: "section-02", title: "API Contract Extraction", sub_skill: "x-ipe-tool-rev-eng-api-contract-extraction", depth: 2 }
      - { id: "section-03", title: "Business Logic Mapping", sub_skill: "x-ipe-tool-rev-eng-business-logic-mapping", depth: 2 }
      - { id: "section-04", title: "Data Model Analysis", sub_skill: "x-ipe-tool-rev-eng-data-model-analysis", depth: 2 }
      - { id: "section-05", title: "Dependency Analysis", sub_skill: "x-ipe-tool-rev-eng-dependency-analysis", depth: 2 }
      - { id: "section-06", title: "Infrastructure Analysis", sub_skill: "x-ipe-tool-rev-eng-infrastructure-analysis", depth: 2 }
      - { id: "section-07", title: "Security & Auth Patterns", sub_skill: "x-ipe-tool-rev-eng-security-auth-pattern", depth: 2 }
      - { id: "section-08", title: "Testing Strategy", sub_skill: "x-ipe-tool-rev-eng-testing-strategy", depth: 2 }
    writes_to: "x-ipe-docs/memory/.working/framework/order-service-re-framework.md"
  errors: []
```

---

## Example 2: design_rubric

**Scenario:** Design quality rubric for the order-service RE report, user emphasizes API contracts and security.

### Input

```yaml
operation: design_rubric
context:
  framework: { ... }  # From Example 1 output
  overview: "Order-service is a FastAPI-based microservice handling order CRUD, payment integration, and event publishing to RabbitMQ."
  user_request: "Focus on API contracts and security patterns — we need to understand the payment integration security."
```

### Processing

1. Parse user_request for emphasis keywords: "API contracts", "security patterns", "payment integration"
2. Map emphasis to sections: Section 2 (API Contracts) → high weight, Section 7 (Security) → high weight
3. Generate per-section criteria with adjusted weights

### Output

```yaml
operation_output:
  success: true
  operation: "design_rubric"
  result:
    rubric_metrics:
      - { section_id: "section-01", criteria: "All 4 abstraction levels documented with diagrams", weight: 1.0, threshold: "≥3 diagrams" }
      - { section_id: "section-02", criteria: "All REST endpoints documented with req/res schemas", weight: 1.5, threshold: "100% endpoint coverage" }
      - { section_id: "section-03", criteria: "Core business rules with code citations", weight: 1.0, threshold: "≥5 business rules identified" }
      - { section_id: "section-04", criteria: "Database schema + DTO mappings documented", weight: 1.0, threshold: "≥1 ER diagram" }
      - { section_id: "section-05", criteria: "All dependencies with versions and purposes", weight: 1.0, threshold: "100% deps from requirements.txt" }
      - { section_id: "section-06", criteria: "CI/CD + container config documented", weight: 1.0, threshold: "Dockerfile + pipeline documented" }
      - { section_id: "section-07", criteria: "Auth flow + payment security documented with code paths", weight: 1.5, threshold: "Auth mechanism + payment integration security" }
      - { section_id: "section-08", criteria: "Test framework + coverage metrics", weight: 1.0, threshold: "Coverage % reported" }
    acceptance_criteria:
      - { section_id: "section-02", checks: ["All endpoints listed", "Request/response schemas present", "Inter-service contracts documented"] }
      - { section_id: "section-07", checks: ["Auth mechanism identified", "Payment integration security analyzed", "Secret management documented"] }
      # ... other sections
    writes_to: "x-ipe-docs/memory/.working/rubric/order-service-re-rubric.md"
  errors: []
```

---

## Example 3: request_knowledge

**Scenario:** Three sections are empty, two are partial. Identify gaps and suggest extractors.

### Input

```yaml
operation: request_knowledge
context:
  framework: { ... }  # From Example 1
  current_state:
    filled_sections: ["section-01", "section-05", "section-08"]
    empty_sections: ["section-03", "section-04", "section-06"]
    partial_sections: ["section-02", "section-07"]
  rubric: { ... }  # From Example 2
```

### Processing

1. Walk framework sections against current_state
2. Section 2 (partial, high weight 1.5) → needs inter-service contract docs → suggest `x-ipe-tool-rev-eng-api-contract-extraction`
3. Section 3 (empty, weight 1.0) → needs business logic mapping → suggest `x-ipe-tool-rev-eng-business-logic-mapping`
4. Section 4 (empty, weight 1.0) → needs data model analysis → suggest `x-ipe-tool-rev-eng-data-model-analysis`
5. Section 6 (empty, weight 1.0) → needs infrastructure analysis → suggest `x-ipe-tool-rev-eng-infrastructure-analysis`
6. Section 7 (partial, high weight 1.5) → needs payment security details → suggest `x-ipe-tool-rev-eng-security-auth-pattern`
7. Sort by priority (weight × urgency)

### Output

```yaml
operation_output:
  success: true
  operation: "request_knowledge"
  result:
    knowledge_requests:
      - target_section: "section-02"
        what_needed: "Extract inter-service API contracts from src/api/ and services/ — specifically the payment gateway integration endpoints with request/response schemas"
        suggested_extractor: "x-ipe-tool-rev-eng-api-contract-extraction"
        priority: 1.5
      - target_section: "section-07"
        what_needed: "Analyze authentication middleware in src/middleware/auth.py and payment security patterns in services/payment/ — document JWT validation flow and payment token handling"
        suggested_extractor: "x-ipe-tool-rev-eng-security-auth-pattern"
        priority: 1.5
      - target_section: "section-03"
        what_needed: "Map business rules in src/domain/ and services/order/ — identify order state machine, validation rules, and payment processing workflow"
        suggested_extractor: "x-ipe-tool-rev-eng-business-logic-mapping"
        priority: 1.0
      - target_section: "section-04"
        what_needed: "Analyze SQLAlchemy models in src/models/ and Pydantic schemas in src/schemas/ — produce ER diagram and DTO mapping"
        suggested_extractor: "x-ipe-tool-rev-eng-data-model-analysis"
        priority: 1.0
      - target_section: "section-06"
        what_needed: "Analyze Dockerfile, docker-compose.yml, and .github/workflows/ — document build pipeline, container configuration, and deployment strategy"
        suggested_extractor: "x-ipe-tool-rev-eng-infrastructure-analysis"
        priority: 1.0
    writes_to: "x-ipe-docs/memory/.working/plan/order-service-re-plan.md"
  errors: []
```

---

## Example 4: fill_structure

**Scenario:** All knowledge has been gathered. Assemble into final draft.

### Input

```yaml
operation: fill_structure
context:
  framework: { ... }  # From Example 1
  gathered_knowledge:
    - section_id: "section-01"
      content: "## Architecture Recovery\n### 1.1 Conceptual Level\n..."
      source: "x-ipe-tool-rev-eng-architecture-recovery"
      metadata: { extracted_at: "2025-07-14", confidence: "high" }
    - section_id: "section-02"
      content: "## API Contract Extraction\n### 2.1 Internal APIs\nPOST /orders - Create order..."
      source: "x-ipe-tool-rev-eng-api-contract-extraction"
      metadata: { extracted_at: "2025-07-14", confidence: "high" }
    - section_id: "section-03"
      content: "## Business Logic Mapping\n### 3.1 Domain Model\nOrder entity..."
      source: "x-ipe-tool-rev-eng-business-logic-mapping"
      metadata: { extracted_at: "2025-07-14", confidence: "medium" }
    # ... sections 4-8
    - section_id: "section-06"
      content: ""
      source: "x-ipe-tool-rev-eng-infrastructure-analysis"
      metadata: { extracted_at: "2025-07-14", confidence: "low" }
  rubric: { ... }  # From Example 2
```

### Processing

1. Index gathered_knowledge by section_id
2. For each framework section, merge content into stub
3. Section 6 has empty content → mark as `[INCOMPLETE: Infrastructure analysis returned no content — re-run with broader source_paths or use extractor-memory for existing infrastructure docs]`
4. All other sections have content → evaluate against rubric
5. Compose final draft with metadata header

### Output

```yaml
operation_output:
  success: true
  operation: "fill_structure"
  result:
    completed_draft: |
      ---
      title: order-service — Reverse Engineering Report
      generated: 2025-07-14
      completeness: 7/8 sections (87.5%)
      ---

      # order-service — Reverse Engineering Report

      ## 1. Architecture Recovery
      ### 1.1 Conceptual Level
      ...

      ## 2. API Contract Extraction
      ### 2.1 Internal APIs
      POST /orders - Create order...

      ## 3. Business Logic Mapping
      ...

      ## 4. Data Model Analysis
      ...

      ## 5. Dependency Analysis
      ...

      ## 6. Infrastructure Analysis
      [INCOMPLETE: Infrastructure analysis returned no content — re-run with broader source_paths or use extractor-memory for existing infrastructure docs]

      ## 7. Security & Auth Patterns
      ...

      ## 8. Testing Strategy
      ...
    completeness_ratio: 0.875
    writes_to: "x-ipe-docs/memory/.working/draft/order-service-re-draft.md"
  errors: []
```

---

## Example 5: Error — Invalid Operation

### Input

```yaml
operation: "analyze"
context: { ... }
```

### Output

```yaml
operation_output:
  success: false
  operation: "analyze"
  result: null
  errors:
    - code: "INVALID_OPERATION"
      message: "Operation 'analyze' is not recognized. Valid operations: provide_framework, design_rubric, request_knowledge, fill_structure"
```

---

## Example 6: request_knowledge — No Gaps

### Input

```yaml
operation: request_knowledge
context:
  framework: { ... }
  current_state:
    filled_sections: ["section-01", "section-02", "section-03", "section-04", "section-05", "section-06", "section-07", "section-08"]
    empty_sections: []
    partial_sections: []
  rubric: { ... }
```

### Output

```yaml
operation_output:
  success: true
  operation: "request_knowledge"
  result:
    knowledge_requests: []
    writes_to: "x-ipe-docs/memory/.working/plan/app-re-plan.md"
  errors: []
```
