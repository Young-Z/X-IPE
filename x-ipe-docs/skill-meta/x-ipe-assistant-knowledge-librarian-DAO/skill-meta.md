# ═══════════════════════════════════════════════════════════
# SKILL META - Assistant Skill (x-ipe-assistant)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-assistant-knowledge-librarian-DAO
skill_type: x-ipe-assistant
version: "1.0.0"
status: candidate
created: 2026-04-20
updated: 2026-04-20

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Central orchestrator for the knowledge pipeline — discovers available knowledge skills at runtime, classifies incoming requests, routes to the appropriate constructor/extractor/ontology skill, and drives the full 格物致知 workflow (plan → execute → critique → store → present).

triggers:
  - "Build a user manual for an application"
  - "Extract knowledge from a website"
  - "Discover and link ontology graphs"
  - "Construct notes from source material"
  - "Run the knowledge pipeline"

not_for:
  - "Direct skill invocation (knowledge skills can be called directly as fallback)"
  - "Task board management (belongs to x-ipe-tool-task-board-manager)"
  - "Feature workflow orchestration (belongs to x-ipe-workflow-task-execution)"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: request
      type: string
      description: "The knowledge task description (e.g., 'build a user manual for app X')"
      validation: "Must be non-empty string"

  optional:
    - name: request_type_override
      type: string
      description: "Skip classification: construction | extraction | ontology_only | presentation | storage"
      default: null

    - name: target_constructor
      type: string
      description: "Skip routing: specific constructor skill name"
      default: null

    - name: max_iterations
      type: integer
      default: 3
      description: "Maximum critique loop iterations before accepting partial quality"

    - name: output_format
      type: string
      default: "markdown"
      description: "Output format: structured | markdown | graph"

    - name: session_context
      type: object
      description: "Optional caller context (task_id, feature_id, etc.)"
      default: null

outputs:
  state:
    - name: pipeline_status
      value: "success | partial | failed"

  data:
    - name: pipeline_summary
      type: string
      description: "Human-readable summary of pipeline execution"
    - name: stored_path
      type: string
      description: "Path to stored knowledge artifact (if applicable)"
    - name: ontology_result
      type: object
      description: "Ontology builder + synthesizer results (if applicable)"
    - name: presented_output
      type: object
      description: "Formatted output from present-to-user (if applicable)"
    - name: completed_steps
      type: array
      description: "List of pipeline steps and their status"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter (name starts with 'x-ipe-assistant-')
      test: file_exists + yaml_parse
      expected: name = 'x-ipe-assistant-knowledge-librarian-DAO'

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists with at least 2 examples
      test: file_exists + content_check
      expected: file contains construction + ontology_only examples

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: "< 500"

    - id: AC-C01
      category: content
      criterion: Skill discovery via glob pattern documented
      test: content_check
      expected: ".github/skills/x-ipe-knowledge-*/SKILL.md glob pattern present"

    - id: AC-C02
      category: content
      criterion: Request classification covers 5 types
      test: content_check
      expected: "construction, extraction, ontology_only, presentation, storage types documented"

    - id: AC-C03
      category: content
      criterion: 格物致知 workflow phases documented with step markers
      test: content_check
      expected: "格物.1 through 格物.4 and 致知.1 through 致知.6 step markers present"

    - id: AC-C04
      category: content
      criterion: Critique loop with max_iterations guard
      test: content_check
      expected: "iteration_count check and partial_quality fallback documented"

    - id: AC-C05
      category: content
      criterion: Pipeline state tracker with step-level status
      test: content_check
      expected: "pipeline_state structure with per-step status tracking"

    - id: AC-C06
      category: content
      criterion: Output contract includes pipeline_summary, pipeline_status, completed_steps, stored_path, ontology_result, presented_output
      test: content_check
      expected: "All 6 fields present in Output Result"

    - id: AC-B01
      category: behavior
      criterion: Input parameters document request, request_type_override, target_constructor, max_iterations, output_format
      test: content_check
      expected: "All 5 parameters in Input Parameters section"

  should:
    - id: AC-C07
      category: content
      criterion: Error handling table documents graceful degradation
      test: content_check
      expected: "Partial pipeline handling, individual step failure behavior"

    - id: AC-C08
      category: content
      criterion: Session isolation via .working/ subfolders
      test: content_check
      expected: "librarian-{timestamp} subfolder pattern documented"

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-meta-skill-creator
      relationship: creator
    - name: x-ipe-knowledge-constructor-user-manual
      relationship: downstream
    - name: x-ipe-knowledge-constructor-notes
      relationship: downstream
    - name: x-ipe-knowledge-constructor-app-reverse-engineering
      relationship: downstream
    - name: x-ipe-knowledge-extractor-web
      relationship: downstream
    - name: x-ipe-knowledge-extractor-memory
      relationship: downstream
    - name: x-ipe-knowledge-keeper-memory
      relationship: downstream
    - name: x-ipe-knowledge-ontology-builder
      relationship: downstream
    - name: x-ipe-knowledge-ontology-synthesizer
      relationship: downstream
    - name: x-ipe-knowledge-present-to-user
      relationship: downstream
    - name: x-ipe-knowledge-present-to-knowledge-graph
      relationship: downstream

  artifacts:
    - path: "references/examples.md"
      description: "Worked examples for construction, extraction, and ontology_only pipelines"
    - path: "references/pipeline-state-format.md"
      description: "Pipeline state tracker schema documentation"
