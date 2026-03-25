# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-architecture-dsl
skill_type: x-ipe-tool
version: "4.0"
status: candidate
created: 2026-01-24
updated: 2026-03-25

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Generate and validate Architecture DSL definitions (Module View and Landscape View)
  using a Bootstrap-inspired 12-column grid system. v4.0 adds a bundled Python lint
  script (scripts/lint_dsl.py) for deterministic grammar validation after generation.

triggers:
  - "architecture diagram"
  - "layer diagram"
  - "module view"
  - "landscape view"
  - "draw architecture"
  - "validate dsl"
  - "lint dsl"

not_for:
  - "flowcharts: use Mermaid"
  - "sequence diagrams: use Mermaid"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "The operation to perform"
      validation: "Must be one of: generate_module_view, generate_landscape_view, refine_dsl, lint"

  optional:
    - name: dsl_content
      type: string
      default: null
      description: "DSL content to validate (for lint operation) or refine"

    - name: dsl_file_path
      type: string
      default: null
      description: "Path to DSL file (alternative to inline content)"

outputs:
  state:
    - name: status
      value: success | failure

  artifacts:
    - name: dsl_output
      type: string
      description: "Generated or refined DSL content"
    - name: lint_report
      type: object
      description: "Validation report with errors/warnings from lint_dsl.py"

  data:
    - name: operation_output
      type: object
      description: "Structure containing result, success status, and errors"

# ─────────────────────────────────────────────────────────────
# CHANGE DESCRIPTION (v3.0 → v4.0)
# ─────────────────────────────────────────────────────────────
change_description: |
  Add scripts/lint_dsl.py — a Python lint script that validates Architecture DSL code
  against the grammar specification (references/grammar.md). The script implements all
  error codes (E001-E009) and warnings (W001). The SKILL.md DoD is updated to call
  the linter as a deterministic validation step instead of relying solely on sub-agent
  text-parsing validation.

  Pattern reference: ontology-1.0.4/scripts/ontology.py

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    # STRUCTURE
    - id: AC-S01
      category: structure
      criterion: scripts/lint_dsl.py exists in skill folder
      test: file_exists
      expected: file at .github/skills/x-ipe-tool-architecture-dsl/scripts/lint_dsl.py

    - id: AC-S02
      category: structure
      criterion: lint_dsl.py is a standalone Python 3 script with no external dependencies
      test: execution
      expected: "python3 scripts/lint_dsl.py --help exits 0"

    - id: AC-S03
      category: structure
      criterion: SKILL.md updated with lint operation and DoD lint step
      test: content_check
      expected: "SKILL.md contains lint operation and DoD references lint_dsl.py"

    # BEHAVIOR — Error detection
    - id: AC-B01
      category: behavior
      criterion: "E001 — detects missing @startuml header"
      test: execution
      expected: "returns E001 for input without @startuml"

    - id: AC-B02
      category: behavior
      criterion: "E002 — detects missing @enduml footer"
      test: execution
      expected: "returns E002 for input without @enduml"

    - id: AC-B03
      category: behavior
      criterion: "E003 — detects invalid view type"
      test: execution
      expected: "returns E003 for @startuml invalid-view"

    - id: AC-B04
      category: behavior
      criterion: "E005 — detects module cols not summing to 12"
      test: execution
      expected: "returns E005 for cols summing to 10"

    - id: AC-B05
      category: behavior
      criterion: "E006 — detects missing rows in layer"
      test: execution
      expected: "returns E006 for layer without rows"

    - id: AC-B06
      category: behavior
      criterion: "E007 — detects duplicate aliases"
      test: execution
      expected: "returns E007 for duplicate alias"

    - id: AC-B07
      category: behavior
      criterion: "E008 — detects undefined alias in flow"
      test: execution
      expected: "returns E008 for flow referencing undefined alias"

    - id: AC-B08
      category: behavior
      criterion: "E009 — detects invalid status values"
      test: execution
      expected: "returns E009 for status: broken"

    - id: AC-B09
      category: behavior
      criterion: "W001 — detects empty containers"
      test: execution
      expected: "returns W001 for empty layer"

    - id: AC-B10
      category: behavior
      criterion: "Valid DSL passes with 0 errors"
      test: execution
      expected: "returns exit code 0 and no errors for valid module-view example"

  should:
    - id: AC-B11
      category: behavior
      criterion: "JSON output mode supported"
      test: execution
      expected: "--format json produces valid JSON"

    - id: AC-B12
      category: behavior
      criterion: "E004 — detects missing grid declaration in module-view"
      test: execution
      expected: "returns E004 for module-view without grid"

  could:
    - id: AC-B13
      category: behavior
      criterion: "stdin input mode supported"
      test: execution
      expected: "echo DSL | python3 lint_dsl.py - works"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Valid module-view passes lint"
      given: "examples/module-view-v2.dsl as input"
      when: "python3 scripts/lint_dsl.py examples/module-view-v2.dsl"
      then: "exit code 0, 0 errors, 0 warnings"

    - name: "Valid landscape-view passes lint"
      given: "examples/landscape-view.dsl as input"
      when: "python3 scripts/lint_dsl.py examples/landscape-view.dsl"
      then: "exit code 0, 0 errors"

  error_cases:
    - name: "Missing header detected"
      given: "DSL file starting with 'title' instead of @startuml"
      when: "python3 scripts/lint_dsl.py bad.dsl"
      then: "exit code 1, E001 in output"

    - name: "Cols not summing to 12"
      given: "Module-view with cols 4 + 4 + 3 = 11"
      when: "python3 scripts/lint_dsl.py bad.dsl"
      then: "exit code 1, E005 in output"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "lint_dsl.py exits 0 on valid examples"
    - "lint_dsl.py exits 1 and reports errors on invalid DSL"
    - "All E001-E009 error codes implemented"
    - "W001 warning code implemented"
    - "No external Python dependencies required"
