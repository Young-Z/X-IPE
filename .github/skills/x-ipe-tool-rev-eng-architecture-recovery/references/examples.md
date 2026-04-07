# Usage Examples — Architecture Recovery

> Examples showing how the orchestrator interacts with this tool skill.

---

## Example 1: Full Architecture Extraction Flow

```yaml
# Step 1: Extract architecture from codebase
Orchestrator: extract(
  repo_path="/path/to/repo",
  phase1_output=".x-ipe-checkpoint/phase1/",
  phase2_output=".x-ipe-checkpoint/phase2/",
  output_dir=".x-ipe-checkpoint/section-01/"
)
→ {
    success: true,
    extracted_content: ".x-ipe-checkpoint/section-01/",
    # Created files:
    #   index.md
    #   01-conceptual-landscape.md (Architecture DSL)
    #   02-logical-module-view.md (Architecture DSL)
    #   03-physical-classes.md (Mermaid classDiagram)
    #   04-data-flow-sequences.md (Mermaid sequenceDiagram)
  }

# Step 2: Validate extracted content
Orchestrator: validate(
  content_path=".x-ipe-checkpoint/section-01/",
  section_id="1-architecture-recovery"
)
→ {
    passed: true,
    criteria: [
      { id: "REQ-1", status: "pass", feedback: "4 levels documented" },
      { id: "REQ-2", status: "pass", feedback: "Architecture DSL module view present" },
      { id: "REQ-3", status: "pass", feedback: "DSL blocks found in levels 1-2" },
      { id: "REQ-4", status: "pass", feedback: "All 6 modules have responsibilities" },
      { id: "REQ-5", status: "pass", feedback: "All components cite source directories" }
    ],
    missing_info: []
  }

# Step 3: Collect and execute architecture-relevant tests
Orchestrator: collect_tests(
  repo_path="/path/to/repo",
  phase2_output=".x-ipe-checkpoint/phase2/"
)
→ {
    collected_tests: [
      { path: "tests/test_integration_auth.py", claim: "auth module → service boundary" },
      { path: "tests/test_api_routes.py", claim: "request flow through handler → service" }
    ]
  }

Orchestrator: execute_tests(repo_path="/path/to/repo")
→ {
    tests_run: 2, tests_passed: 2, tests_failed: 0,
    claim_mapping: [
      { test: "test_integration_auth.py", claim: "auth module boundary", result: "confirmed" },
      { test: "test_api_routes.py", claim: "handler→service flow", result: "confirmed" }
    ]
  }

# Step 4: Package into final output
Orchestrator: package(
  content_path=".x-ipe-checkpoint/section-01/",
  output_dir="output/section-01-architecture-recovery/"
)
→ {
    package_path: "output/section-01-architecture-recovery/",
    # Final structure:
    #   section-01-architecture-recovery/
    #   ├── index.md
    #   ├── 01-conceptual-landscape.md
    #   ├── 02-logical-module-view.md
    #   ├── 03-physical-classes.md
    #   ├── 04-data-flow-sequences.md
    #   ├── screenshots/
    #   └── tests/
  }
```

---

## Example 2: Architecture DSL Integration

```yaml
# During extract operation, Level 2 invokes x-ipe-tool-architecture-dsl
# Input to architecture-dsl skill:
{
  operation: "generate_module_view",
  context: {
    layers: ["Presentation", "Business", "Data"],
    modules: [
      { name: "API Handler", layer: "Presentation", cols: 6, dir: "src/handlers/" },
      { name: "WebSocket", layer: "Presentation", cols: 6, dir: "src/ws/" },
      { name: "Auth Service", layer: "Business", cols: 4, dir: "src/services/auth/" },
      { name: "Order Service", layer: "Business", cols: 4, dir: "src/services/orders/" },
      { name: "Notification", layer: "Business", cols: 4, dir: "src/services/notify/" },
      { name: "User Repo", layer: "Data", cols: 6, dir: "src/repositories/user/" },
      { name: "Order Repo", layer: "Data", cols: 6, dir: "src/repositories/order/" }
    ]
  }
}

# Output: Architecture DSL block in 02-logical-module-view.md
# @startuml module-view
# ...columns sum to 12 per layer...
# @enduml
```

---

## Example 3: Handling Missing Architecture Level

```yaml
# Small codebase — only 2 levels are meaningful
Orchestrator: extract(...)
→ {
    # 01-conceptual-landscape.md — created
    # 02-logical-module-view.md — created
    # 03-physical-classes.md — "No significant class hierarchies detected"
    # 04-data-flow-sequences.md — "Single request path; see logical view"
  }

Orchestrator: validate(...)
→ {
    passed: true,  # 2 levels documented satisfies REQ-1
    criteria: [
      { id: "REQ-1", status: "pass", feedback: "2 levels (conceptual + logical)" },
      { id: "OPT-1", status: "incomplete", feedback: "Physical level minimal" },
      { id: "OPT-2", status: "incomplete", feedback: "Data flow minimal" }
    ]
  }
# Validation passes — [REQ] criteria met, [OPT] noted as incomplete
```

---

## Example 4: Phase 2 Cross-Reference

```yaml
# Phase 2 test knowledge reveals module boundaries
# From Section 8 test-to-module mapping:
{
  "test_auth_service.py": {
    module: "auth",
    mocks: ["user_repository", "token_service"],
    # → reveals: auth service depends on user_repo and token_service
    # → confirms: auth is isolated from direct DB access
  }
}

# This feeds into Level 2 (Logical) module relationships:
# Auth Service → User Repository (confirmed by test mock boundary)
# Auth Service → Token Service (confirmed by test mock boundary)
```
