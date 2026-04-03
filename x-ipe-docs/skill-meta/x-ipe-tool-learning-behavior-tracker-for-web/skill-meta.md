# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-learning-behavior-tracker-for-web
skill_type: x-ipe-tool
version: "1.0.0"
status: candidate
created: 2026-04-03
updated: 2026-04-03

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Record and analyze user behavior on any website for AI agent training data via Chrome DevTools injection.

triggers:
  - "track behavior"
  - "record user behavior"
  - "learn from website"
  - "behavior tracking"

not_for:
  - "x-ipe-tool-frontend-design: for creating UI mockups, not tracking behavior"
  - "UX analytics: this is AI agent training data, not business analytics"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "The operation to perform: inject | collect | stop | post_process"
      validation: "Must be one of: inject, collect, stop, post_process"

    - name: url
      type: string
      description: "Target website URL (https:// or http://)"
      validation: "Must be a valid URL with protocol"

    - name: purpose
      type: string
      description: "Tracking purpose description (required, max 200 words)"
      validation: "Non-empty, ≤200 words"

  optional:
    - name: pii_whitelist
      type: array
      default: []
      description: "CSS selectors to reveal (override default PII masking)"

    - name: buffer_capacity
      type: number
      default: 10000
      description: "Maximum events in circular buffer before pruning oldest"

outputs:
  state:
    - name: status
      value: success | failure

  artifacts:
    - name: behavior_recording
      type: file
      path: "behavior-recording-{sessionId}.json"
      description: "Structured JSON with session, pages, statistics, events, and analysis"

  data:
    - name: operation_output
      type: object
      description: "Contains result (session_id, file_path), success status, and errors"

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
      expected: name equals 'x-ipe-tool-learning-behavior-tracker-for-web'

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists with usage scenarios
      test: file_exists
      expected: file contains at least 2 examples

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    - id: AC-S04
      category: structure
      criterion: tracker-toolbar.js and tracker-toolbar.mini.js both exist
      test: file_exists
      expected: both files present in references/

    # CONTENT
    - id: AC-C01
      category: content
      criterion: All required sections present in order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, About, When to Use,
         Input Parameters, Input Initialization, Definition of Ready,
         Operations, Output Result, Definition of Done, Error Handling,
         References, Examples]

    - id: AC-C02
      category: content
      criterion: Operations use XML structure with action blocks
      test: regex_match
      expected: "<operation name=.*>"

    - id: AC-C03
      category: content
      criterion: Error Handling table has 3 columns
      test: table_parse
      expected: columns [Error, Cause, Resolution]

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: inject operation produces session_id
      test: execution
      expected: returns session_id in operation_output

    - id: AC-B02
      category: behavior
      criterion: post_process produces structured analysis
      test: execution
      expected: analysis contains flow_narrative, key_paths, key_path_summary, pain_points, ai_annotations

  should:
    - id: AC-C04
      category: content
      criterion: When to Use includes trigger and not_for lists
      test: yaml_parse
      expected: triggers and not_for lists not empty

    - id: AC-C05
      category: content
      criterion: Key Concepts in About section
      test: content_check
      expected: "**Key Concepts:**"

    - id: AC-C06
      category: content
      criterion: Input Initialization subsection present
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

  could:
    - id: AC-C07
      category: content
      criterion: scripts/ contain Python orchestration and post-processing
      test: file_exists
      expected: track_behavior.py and post_processor.py exist

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-workflow-task-execution
      relationship: prerequisite

  artifacts:
    - path: "Chrome DevTools MCP connection"
      description: "Must have active Chrome DevTools MCP for injection"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "inject success"
      given: "Valid URL and active Chrome DevTools"
      when: "execute inject operation"
      then: "success=true, session_id returned, IIFE injected into page"

    - name: "collect + post_process success"
      given: "Active recording session with events"
      when: "execute stop then post_process"
      then: "behavior-recording-{sessionId}.json written with full analysis"

  error_cases:
    - name: "inject without Chrome DevTools"
      given: "No Chrome DevTools MCP connection"
      when: "execute inject"
      then: "success=false, errors contains INJECTION_FAILED"

    - name: "invalid URL"
      given: "URL without protocol"
      when: "execute inject"
      then: "success=false, errors contains INVALID_URL"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All outputs match schema"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
    - "Both tracker-toolbar.js and tracker-toolbar.mini.js present"
