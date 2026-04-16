# ═══════════════════════════════════════════════════════════
# SKILL META - Knowledge Skill (x-ipe-knowledge)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-knowledge-constructor-app-reverse-engineering
skill_type: x-ipe-knowledge
version: "1.0.0"
status: candidate
created: 2025-07-14
updated: 2025-07-14

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Domain expert for application reverse engineering reports — provides framework scaffolding, rubric design, knowledge-gap analysis, and draft assembly via the 4-operation constructor interface (provide_framework, design_rubric, request_knowledge, fill_structure).

triggers:
  - "Build an application reverse engineering report framework"
  - "Design quality rubric for an RE report"
  - "Identify knowledge gaps in an RE report draft"
  - "Assemble gathered RE knowledge into a structured draft"

not_for:
  - "Orchestration decisions (belongs to x-ipe-assistant-knowledge-librarian-DAO)"
  - "Executing reverse engineering sub-skills (belongs to x-ipe-tool-rev-eng-* skills)"
  - "Writing to persistent memory (belongs to x-ipe-knowledge-keeper-memory)"
  - "Web or memory extraction (belongs to extractor-web / extractor-memory)"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "Which operation to perform: provide_framework | design_rubric | request_knowledge | fill_structure"
      validation: "Must match one of the 4 defined operations"

    - name: context
      type: object
      description: "Full context passed by the assistant orchestrator (operation-specific fields)"
      validation: "All required context fields for the specified operation must be present"

  optional:
    - name: output_format
      type: string
      default: "markdown"
      description: "Desired output format hint for provide_framework"

outputs:
  state:
    - name: status
      value: success | failure

  data:
    - name: operation_output
      type: object
      description: "Structured result with success, operation name, result data, writes_to path, and errors"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    # STRUCTURE
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
      test: file_exists + yaml_parse
      expected: name starts with 'x-ipe-knowledge-constructor-app-reverse-engineering'

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists with ≥1 example per operation
      test: file_exists
      expected: file contains at least 4 worked examples

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 600 lines
      test: line_count
      expected: < 600

    - id: AC-S04
      category: structure
      criterion: templates/ folder contains playbook-template.md + 9 mixin files
      test: file_exists
      expected: 10 template files present

    # CONTENT
    - id: AC-C01
      category: content
      criterion: All required sections present in order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, About, When to Use,
         Input Parameters, Input Initialization, Definition of Ready,
         Operations (4), Output Result, Definition of Done, Error Handling,
         Examples]

    - id: AC-C02
      category: content
      criterion: All 4 operations defined with typed contracts
      test: content_check
      expected: "provide_framework, design_rubric, request_knowledge, fill_structure each with Input, Output, Writes To, Constraints"

    - id: AC-C03
      category: content
      criterion: Each operation contains phase backbone (博学之→笃行之)
      test: content_check
      expected: "All 5 phases present inside each operation"

    - id: AC-C04
      category: content
      criterion: Each operation declares writes_to path within .working/
      test: content_check
      expected: "writes_to field present in every operation contract, all within .working/"

    - id: AC-C05
      category: content
      criterion: Stateless service note in Important Notes
      test: content_check
      expected: "Contains 'Operations are stateless services'"

    - id: AC-C06
      category: content
      criterion: Error Handling table present
      test: table_parse
      expected: columns [Error, Cause, Resolution]

    - id: AC-C07
      category: content
      criterion: provide_framework maps 8 RE sections to x-ipe-tool-rev-eng-* sub-skills
      test: content_check
      expected: "8 sections each with a mapped sub-skill name"

    - id: AC-C08
      category: content
      criterion: request_knowledge suggested_extractor can be x-ipe-tool-rev-eng-* sub-skill
      test: content_check
      expected: "suggested_extractor includes rev-eng sub-skills, not just extractor-web/extractor-memory"

  should:
    - id: AC-C09
      category: content
      criterion: When to Use includes explicit triggers
      test: yaml_parse
      expected: triggers list is not empty

    - id: AC-C10
      category: content
      criterion: Key Concepts section in About
      test: content_check
      expected: "Operation Contract, Stateless Service, writes_to Discipline"

    - id: AC-C11
      category: content
      criterion: Input Initialization subsection present under Input Parameters
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

    - id: AC-C12
      category: content
      criterion: Operation contract types are domain-specific (not generic string/object)
      test: content_check
      expected: Input and Output types reference RE-domain types

  could:
    - id: AC-C13
      category: content
      criterion: Templates cross-reference x-ipe-tool-rev-eng-* sub-skills
      test: content_check
      expected: playbook-template.md maps sections to sub-skills

    - id: AC-C14
      category: content
      criterion: Constraints per operation are actionable
      test: content_check
      expected: Each constraint is testable

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-meta-skill-creator
      relationship: creator

    - name: x-ipe-assistant-knowledge-librarian-DAO
      relationship: orchestrator
      description: "Assistant that coordinates and calls this knowledge skill's operations"

    - name: x-ipe-tool-rev-eng-architecture-recovery
      relationship: downstream
      description: "Sub-skill for architecture recovery extraction"

    - name: x-ipe-tool-rev-eng-api-contract-extraction
      relationship: downstream
      description: "Sub-skill for API contract extraction"

    - name: x-ipe-tool-rev-eng-business-logic-mapping
      relationship: downstream
      description: "Sub-skill for business logic mapping"

    - name: x-ipe-tool-rev-eng-data-model-analysis
      relationship: downstream
      description: "Sub-skill for data model analysis"

    - name: x-ipe-tool-rev-eng-dependency-analysis
      relationship: downstream
      description: "Sub-skill for dependency analysis"

    - name: x-ipe-tool-rev-eng-infrastructure-analysis
      relationship: downstream
      description: "Sub-skill for infrastructure analysis"

    - name: x-ipe-tool-rev-eng-security-auth-pattern
      relationship: downstream
      description: "Sub-skill for security and auth pattern extraction"

    - name: x-ipe-tool-rev-eng-testing-strategy
      relationship: downstream
      description: "Sub-skill for testing strategy extraction"

  artifacts:
    - path: "x-ipe-docs/memory/.working/"
      description: "Working directory for intermediate outputs (framework, rubric, plan, draft)"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "provide_framework success"
      given: "request_context with app_name, repo_path, language=python, repo_type=single-module"
      when: "execute provide_framework"
      then: "success=true, framework_document with 8 RE sections, toc_structure mapping sections to sub-skills, written to .working/framework/"

    - name: "design_rubric success"
      given: "framework from provide_framework, overview text, user_request"
      when: "execute design_rubric"
      then: "success=true, rubric_metrics[] with per-section criteria, written to .working/rubric/"

    - name: "request_knowledge success with gaps"
      given: "framework, current_state with 3 empty sections, rubric"
      when: "execute request_knowledge"
      then: "success=true, knowledge_requests[] with 3 items, suggested_extractor includes rev-eng sub-skills, written to .working/plan/"

    - name: "request_knowledge no gaps"
      given: "framework, current_state with all sections filled, rubric"
      when: "execute request_knowledge"
      then: "success=true, knowledge_requests=[] (empty)"

    - name: "fill_structure success"
      given: "framework, gathered_knowledge[] covering all sections, rubric"
      when: "execute fill_structure"
      then: "success=true, completed_draft written to .working/draft/"

  error_cases:
    - name: "Invalid operation name"
      given: "operation='nonexistent'"
      when: "execute operation"
      then: "success=false, errors contains INVALID_OPERATION"

    - name: "Missing required context"
      given: "context missing request_context for provide_framework"
      when: "execute provide_framework"
      then: "success=false, errors contains INPUT_VALIDATION_FAILED"

    - name: "Unknown language in request_context"
      given: "request_context with language='cobol'"
      when: "execute provide_framework"
      then: "success=true, framework uses base playbook only (no language mixin)"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All 4 operation outputs match contract types"
    - "Results written to declared .working/ paths only"
    - "provide_framework maps all 8 sections to rev-eng sub-skills"
    - "request_knowledge suggests rev-eng sub-skills as extractors"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
