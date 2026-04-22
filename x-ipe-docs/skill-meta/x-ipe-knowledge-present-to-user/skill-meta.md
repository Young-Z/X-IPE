# Skill Meta: x-ipe-knowledge-present-to-user

# ═══════════════════════════════════════════════════════════
# SKILL META - Knowledge Skill (x-ipe-knowledge)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-knowledge-present-to-user
skill_type: x-ipe-knowledge
version: "1.0.0"
status: candidate
created: 2026-04-16
updated: 2026-04-16

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Knowledge output formatter that renders constructed knowledge as a structured summary for human consumption, with completeness tracking and incomplete-section warnings.

triggers:
  - "render — format knowledge content for human consumption"
  - "present knowledge to user"
  - "generate structured summary"

not_for:
  - "Orchestration decisions — belong to x-ipe-assistant-knowledge-librarian-DAO"
  - "Graph visualization — that is x-ipe-knowledge-present-to-knowledge-graph"
  - "Building or synthesizing ontology — those are separate knowledge skills"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "Which operation to perform: render"
      validation: "Must be 'render'"

    - name: context
      type: object
      description: "Full context passed by the assistant orchestrator (content_path, format)"
      validation: "content_path must be present"

  optional:
    - name: format
      type: string
      default: "structured"
      description: "Output format: 'structured' (JSON) or 'markdown'"

outputs:
  state:
    - name: status
      value: success | failure

  data:
    - name: operation_output
      type: object
      description: "Structured result with success, operation name, rendered content, and errors"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter (name starts with 'x-ipe-knowledge-')
      test: file_exists + yaml_parse
      expected: name == 'x-ipe-knowledge-present-to-user'

    - id: AC-S02
      category: structure
      criterion: scripts/render.py exists with render subcommand
      test: file_exists + content_check
      expected: argparse with render command

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    - id: AC-C01
      category: content
      criterion: All required sections present in order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, About, When to Use,
         Input Parameters, Input Initialization, Definition of Ready,
         Operations (1: render), Output Result, Definition of Done,
         Error Handling, Examples]

    - id: AC-C02
      category: content
      criterion: render operation defined with typed contract
      test: content_check
      expected: "Input, Output, Writes To, Constraints fields"

    - id: AC-C03
      category: content
      criterion: render operation contains phase backbone (博学之→笃行之)
      test: content_check
      expected: "All 5 phases present"

    - id: AC-C04
      category: content
      criterion: Stateless service documented
      test: content_check
      expected: "Contains stateless service note"

    - id: AC-B01
      category: behavior
      criterion: render.py with structured format returns JSON with title, summary, sections[], metadata
      test: execution
      expected: valid JSON output with all fields

    - id: AC-B02
      category: behavior
      criterion: render.py with markdown format returns Markdown output
      test: execution
      expected: Markdown-formatted text

    - id: AC-B03
      category: behavior
      criterion: render.py flags [INCOMPLETE: ...] markers with warnings
      test: execution
      expected: sections with incomplete markers have warnings[]

    - id: AC-B04
      category: behavior
      criterion: render.py handles missing file with CONTENT_NOT_FOUND error
      test: execution
      expected: JSON error to stderr + exit 1

  should:
    - id: AC-C05
      category: content
      criterion: Edge cases documented (empty file, non-UTF-8, no headers)
      test: content_check
      expected: Error handling table covers these cases

    - id: AC-C06
      category: content
      criterion: Input Initialization subsection present
      test: section_parse
      expected: "<input_init> XML block"

  could:
    - id: AC-C07
      category: content
      criterion: references/examples.md with usage scenarios
      test: file_exists
      expected: at least 2 examples

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-meta-skill-creator
      relationship: creator
    - name: x-ipe-assistant-knowledge-librarian-DAO
      relationship: orchestrator

  artifacts:
    - path: "x-ipe-docs/requirements/EPIC-059/FEATURE-059-D/specification.md"
      description: "Feature specification (AC-059D-08)"
    - path: "x-ipe-docs/requirements/EPIC-059/FEATURE-059-D/technical-design.md"
      description: "Technical design (D2 section)"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "render structured summary"
      given: "A multi-section knowledge Markdown file"
      when: "execute render with format=structured"
      then: "JSON output with title, summary, sections[], metadata"

    - name: "render markdown format"
      given: "A multi-section knowledge Markdown file"
      when: "execute render with format=markdown"
      then: "Markdown-formatted output"

  error_cases:
    - name: "content not found"
      given: "content_path does not exist"
      when: "execute render"
      then: "CONTENT_NOT_FOUND error"

    - name: "empty file"
      given: "content_path points to empty file"
      when: "execute render"
      then: "JSON with title='Empty', sections=[], completeness=0"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "render operation output matches contract types"
    - "Completeness percentage calculated correctly"
    - "INCOMPLETE markers flagged in warnings"
    - "Both structured and markdown formats produce valid output"
