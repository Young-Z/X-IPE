# ═══════════════════════════════════════════════════════════
# SKILL META - Knowledge Skill (x-ipe-knowledge)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-knowledge-mimic-web-behavior-tracker
skill_type: x-ipe-knowledge
version: "1.0.0"
status: candidate
created: 2026-04-16
updated: 2026-04-16

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Observes and records user behavior on websites via Chrome DevTools MCP, producing structured observation summaries with flow narratives, key paths, pain points, and AI annotations.

triggers:
  - "start tracking user behavior on a website"
  - "stop tracking and collect behavior observations"
  - "retrieve behavior observations for a tracking session"

not_for:
  - "UX analytics dashboards — this produces AI training data, not business metrics"
  - "Automated testing — use testing frameworks instead"
  - "Orchestration decisions — belong to assistant skills"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "Which operation to perform: start_tracking | stop_tracking | get_observations"
      validation: "Must match one of the defined operations"

    - name: context
      type: object
      description: "Full context passed by the assistant orchestrator"
      validation: "All required context fields for the specified operation must be present"

  optional:
    - name: filter
      type: object
      default: null
      description: "Filter criteria for get_observations (event_type, time_range, element_selector)"

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
      expected: file contains at least 1 example per operation

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 600 lines
      test: line_count
      expected: < 600

    # CONTENT — Operations structure
    - id: AC-C01
      category: content
      criterion: All required sections present in order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, About, When to Use,
         Input Parameters, Input Initialization, Definition of Ready,
         Operations, Output Result, Definition of Done, Error Handling,
         Examples]

    - id: AC-C02
      category: content
      criterion: Three operations defined with typed contracts (start_tracking, stop_tracking, get_observations)
      test: content_check
      expected: "Operation blocks with Input, Output, Writes To, Constraints fields"

    - id: AC-C03
      category: content
      criterion: Each operation contains phase backbone (博学之→笃行之)
      test: content_check
      expected: "All 5 phases present inside each operation: 博学之, 审问之, 慎思之, 明辨之, 笃行之"

    - id: AC-C04
      category: content
      criterion: Each operation declares writes_to path
      test: content_check
      expected: "writes_to field present in every operation contract"

    - id: AC-C05
      category: content
      criterion: Stateless service note in Important Notes
      test: content_check
      expected: "Contains 'Operations are stateless services' or equivalent"

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
      expected: returns operation_output object with success, operation, result, errors

    - id: AC-B02
      category: behavior
      criterion: Mimic writes only to x-ipe-docs/.mimicked/ (not .working/ or persistent memory)
      test: content_check
      expected: all writes_to paths under x-ipe-docs/.mimicked/

    - id: AC-B03
      category: behavior
      criterion: PII masking defaults to mask-everything; passwords NEVER revealed
      test: content_check
      expected: SKILL.md documents PII masking policy

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
      expected: "IIFE Guard, Circular Buffer, PII Masking, Post-Processing"

    - id: AC-C09
      category: content
      criterion: Input Initialization subsection present under Input Parameters
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

    - id: AC-C10
      category: content
      criterion: Operation contract types are specific (not generic string/object)
      test: content_check
      expected: Input and Output types use domain-specific type names

  could:
    - id: AC-C11
      category: content
      criterion: get_observations supports filtering by event_type, time_range, element_selector
      test: content_check
      expected: filter contract documented with specific sub-fields

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
    - path: "references/tracker-toolbar.mini.js"
      description: "Minified IIFE for browser injection — must exist before start_tracking"

    - path: "scripts/post_processor.py"
      description: "Post-processor for generating observation summary from raw events"

  runtime:
    - name: Chrome DevTools MCP
      description: "navigate_page and evaluate_script tools required for start_tracking and stop_tracking"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "start_tracking success"
      given: "valid target_app URL and session_config with purpose"
      when: "execute start_tracking"
      then: "success=true, tracking_session_id returned, session dir created under x-ipe-docs/.mimicked/"

    - name: "stop_tracking success"
      given: "active tracking session with events in circular buffer"
      when: "execute stop_tracking"
      then: "success=true, observation_summary with flow_narrative + key_paths + pain_points returned, files written to x-ipe-docs/.mimicked/{session_id}/"

    - name: "get_observations success"
      given: "completed tracking session with stored observations"
      when: "execute get_observations with filter"
      then: "success=true, filtered observations[] returned, no files written"

  error_cases:
    - name: "Invalid operation name"
      given: "operation='nonexistent'"
      when: "execute operation"
      then: "success=false, errors contains INVALID_OPERATION"

    - name: "Missing required context"
      given: "start_tracking without target_app"
      when: "execute start_tracking"
      then: "success=false, errors contains INPUT_VALIDATION_FAILED"

    - name: "Session not found on stop"
      given: "stop_tracking with non-existent session_id"
      when: "execute stop_tracking"
      then: "success=false, errors contains SESSION_NOT_FOUND"

    - name: "Double injection"
      given: "start_tracking on page where IIFE guard is already set"
      when: "execute start_tracking"
      then: "success=true, existing session ID returned (no error)"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All operation outputs match contract types"
    - "Results written to declared writes_to paths (x-ipe-docs/.mimicked/ only)"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
    - "PII masking active with passwords never exposed"
