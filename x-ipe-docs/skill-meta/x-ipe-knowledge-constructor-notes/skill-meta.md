# ═══════════════════════════════════════════════════════════
# SKILL META - Knowledge Skill (x-ipe-knowledge)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-knowledge-constructor-notes
skill_type: x-ipe-knowledge
version: "1.0.0"
status: candidate
created: 2025-07-18
updated: 2025-07-18

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Domain expert for general knowledge notes construction — provides framework scaffolding, rubric design, gap-driven extraction requests, and draft assembly via a 4-operation interface called by the Knowledge Librarian assistant.

triggers:
  - "provide_framework for a notes knowledge base"
  - "design_rubric for notes sections"
  - "request_knowledge to fill notes gaps"
  - "fill_structure to assemble notes draft"

not_for:
  - "Orchestration decisions (belongs to x-ipe-assistant-knowledge-librarian-DAO)"
  - "Persistent memory writes (belongs to x-ipe-knowledge-keeper-memory)"
  - "User manual construction (belongs to x-ipe-knowledge-constructor-user-manual)"
  - "Application reverse engineering (belongs to x-ipe-knowledge-constructor-app-reverse-engineering)"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "Which operation to perform: provide_framework | design_rubric | request_knowledge | fill_structure"
      validation: "Must match one of the four defined operations"

    - name: context
      type: object
      description: "Full context passed by the assistant orchestrator (operation-specific fields)"
      validation: "All required context fields for the specified operation must be present"

  optional:
    - name: output_format
      type: string
      default: "markdown"
      description: "Format hint for provide_framework output"

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
      expected: name starts with 'x-ipe-knowledge-'

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists
      test: file_exists
      expected: file contains at least 1 example per operation (4 total)

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 600 lines
      test: line_count
      expected: < 500 (target), < 600 (max)

    - id: AC-S04
      category: structure
      criterion: templates/ contains notes-specific templates
      test: file_exists
      expected: general-template.md and overview-template.md exist

    # CONTENT — Operations structure
    - id: AC-C01
      category: content
      criterion: All required sections present in order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, About, When to Use,
         Input Parameters, Input Initialization, Definition of Ready,
         Operations (provide_framework, design_rubric, request_knowledge, fill_structure),
         Output Result, Definition of Done, Error Handling, Examples]

    - id: AC-C02
      category: content
      criterion: All 4 operations defined with typed contracts
      test: content_check
      expected: "Each operation has Input, Output, Writes To, Constraints fields"

    - id: AC-C03
      category: content
      criterion: Each operation contains phase backbone (博学之→笃行之)
      test: content_check
      expected: "All 5 phases present inside each operation: 博学之, 审问之, 慎思之, 明辨之, 笃行之"

    - id: AC-C04
      category: content
      criterion: Each operation declares writes_to path within .working/
      test: content_check
      expected: "writes_to field present: framework/, rubric/, plan/, draft/"

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

  should:
    - id: AC-C07
      category: content
      criterion: When to Use includes explicit triggers
      test: yaml_parse
      expected: triggers list is not empty

    - id: AC-C08
      category: content
      criterion: Key Concepts section in About
      test: content_check
      expected: "Operation Contract, Stateless Service, writes_to Discipline"

    - id: AC-C09
      category: content
      criterion: Input Initialization subsection present under Input Parameters
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

    - id: AC-C10
      category: content
      criterion: Operation contract types are domain-specific
      test: content_check
      expected: "Types reference notes-domain structures (framework_document, toc_structure, rubric_metrics, knowledge_requests, completed_draft)"

  could:
    - id: AC-C11
      category: content
      criterion: Templates adapted from old skill
      test: content_check
      expected: "general-template.md and overview-template.md reflect constructor output format"

    - id: AC-C12
      category: content
      criterion: Constraints per operation are actionable
      test: content_check
      expected: Each constraint is testable (not vague guidance)

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

  artifacts:
    - path: "x-ipe-docs/skill-meta/x-ipe-knowledge-constructor-notes/candidate/templates/general-template.md"
      description: "Notes framework template — structural blueprint for provide_framework"

    - path: "x-ipe-docs/skill-meta/x-ipe-knowledge-constructor-notes/candidate/templates/overview-template.md"
      description: "Overview generation template — used by fill_structure for overview.md assembly"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "provide_framework success"
      given: "request_context with topic='React Hooks', scope='comprehensive', source_paths=[]"
      when: "execute provide_framework"
      then: "success=true, framework_document written to .working/framework/"

    - name: "design_rubric success"
      given: "framework from provide_framework, overview='React Hooks patterns', user_request='focus on advanced patterns'"
      when: "execute design_rubric"
      then: "success=true, rubric_metrics[] written to .working/rubric/"

    - name: "request_knowledge success"
      given: "framework, current_state with empty sections, rubric"
      when: "execute request_knowledge"
      then: "success=true, knowledge_requests[] written to .working/plan/"

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

    - name: "No gaps remain"
      given: "current_state with all sections filled"
      when: "execute request_knowledge"
      then: "success=true, knowledge_requests=[] (empty)"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All 4 operation outputs match contract types"
    - "Results written to declared .working/ paths only"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
    - "Templates loaded from templates/ folder correctly"
