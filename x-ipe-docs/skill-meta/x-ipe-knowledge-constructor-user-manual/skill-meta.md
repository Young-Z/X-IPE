# ═══════════════════════════════════════════════════════════
# SKILL META - Knowledge Skill (x-ipe-knowledge)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-knowledge-constructor-user-manual
skill_type: x-ipe-knowledge
version: "1.0.0"
status: candidate
created: 2025-07-16
updated: 2025-07-16

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Domain expert for user manual construction — provides framework, rubric, knowledge requests, and structure filling via a 4-operation interface called by the Knowledge Librarian assistant.

triggers:
  - "Provide a user manual framework for an application"
  - "Design quality rubric for a user manual"
  - "Identify knowledge gaps in a user manual draft"
  - "Fill user manual structure with gathered knowledge"

not_for:
  - "Orchestration decisions (belongs to x-ipe-assistant-knowledge-librarian-DAO)"
  - "Extracting knowledge from sources (belongs to extractor-web / extractor-memory)"
  - "Persisting drafts to memory (belongs to keeper-memory)"
  - "Ontology registration (belongs to ontology-builder)"

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
      description: "Full context passed by the assistant orchestrator — varies per operation"
      validation: "All required context fields for the specified operation must be present"

  optional:
    - name: output_format
      type: string
      default: "markdown"
      description: "Format hint for provide_framework output (markdown | split)"

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
      expected: < 600

    - id: AC-S04
      category: structure
      criterion: templates/ folder contains 6 domain templates
      test: file_exists
      expected: playbook-template.md, collection-template.md, acceptance-criteria.md, mixin-web.md, mixin-cli.md, mixin-mobile.md

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
      expected: "All 5 phases present inside each operation"

    - id: AC-C04
      category: content
      criterion: Each operation declares writes_to path under .working/
      test: content_check
      expected: "provide_framework→.working/framework/, design_rubric→.working/rubric/, request_knowledge→.working/plan/, fill_structure→.working/draft/"

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

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: Skill produces structured operation_output
      test: execution
      expected: returns operation_output with success, operation, result, errors

  should:
    - id: AC-C07
      category: content
      criterion: When to Use includes explicit triggers for all 4 operations
      test: yaml_parse
      expected: triggers list has 4 entries

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
      criterion: Operation contract types are domain-specific (not generic string/object)
      test: content_check
      expected: Uses types like request_context, framework_document, toc_structure, rubric_metrics[]

  could:
    - id: AC-C11
      category: content
      criterion: Templates adapted from old skill (not just copied)
      test: content_check
      expected: Constructor-focused instructions (producing output, not direct extraction)

    - id: AC-C12
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

    - name: x-ipe-knowledge-keeper-memory
      relationship: downstream
      description: "Handles promotion of .working/ drafts to persistent memory"

    - name: x-ipe-knowledge-extractor-web
      relationship: referenced
      description: "Referenced as suggested_extractor in request_knowledge output"

    - name: x-ipe-knowledge-extractor-memory
      relationship: referenced
      description: "Referenced as suggested_extractor in request_knowledge output"

  artifacts:
    - path: "x-ipe-docs/memory/.working/"
      description: "Working directory where all operation outputs are written"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "provide_framework success"
      given: "request_context with app_name='MyApp', app_type='web', user_goal='create user manual', source_paths=['./src']"
      when: "execute provide_framework"
      then: "success=true, framework_document contains 8 sections, toc_structure has 8 entries, written to .working/framework/"

    - name: "design_rubric success"
      given: "framework from provide_framework, overview='MyApp is a web dashboard', user_request='focus on getting started'"
      when: "execute design_rubric"
      then: "success=true, rubric_metrics[] has per-section criteria, Getting Started has highest weight"

    - name: "request_knowledge success"
      given: "framework, current_state with 3 empty sections, rubric"
      when: "execute request_knowledge"
      then: "success=true, knowledge_requests[] has 3 entries with target_section, what_needed, suggested_extractor"

    - name: "fill_structure success"
      given: "framework, gathered_knowledge[] covering all sections, rubric"
      when: "execute fill_structure"
      then: "success=true, completed_draft maps all knowledge to sections, written to .working/draft/"

  error_cases:
    - name: "Invalid operation name"
      given: "operation='nonexistent'"
      when: "execute operation"
      then: "success=false, errors contains INVALID_OPERATION"

    - name: "Missing required context"
      given: "context missing request_context for provide_framework"
      when: "execute provide_framework"
      then: "success=false, errors contains INPUT_VALIDATION_FAILED"

    - name: "No gaps in request_knowledge"
      given: "current_state with all sections filled"
      when: "execute request_knowledge"
      then: "success=true, knowledge_requests[] is empty"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All 4 operation outputs match contract types"
    - "Results written to declared writes_to paths (.working/ only)"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
    - "Templates adapted from old skill with constructor focus"
