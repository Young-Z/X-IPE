# Skill Meta: x-ipe-knowledge-present-to-knowledge-graph

# ═══════════════════════════════════════════════════════════
# SKILL META - Knowledge Skill (x-ipe-knowledge)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-knowledge-present-to-knowledge-graph
skill_type: x-ipe-knowledge
version: "1.0.0"
status: candidate
created: 2026-04-16
updated: 2026-04-16

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Graph connector that pushes ontology data to the X-IPE knowledge graph server
  via HTTP callback, with automatic port resolution and auth token discovery.

triggers:
  - "connector — push ontology to knowledge graph"
  - "present knowledge to graph"
  - "send ontology callback"

not_for:
  - "Orchestration decisions — belong to x-ipe-assistant-knowledge-librarian-DAO"
  - "Human-readable output — that is x-ipe-knowledge-present-to-user"
  - "Building or synthesizing ontology — those are separate knowledge skills"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "Which operation to perform: connector"
      validation: "Must be 'connector'"

    - name: context
      type: object
      description: "Full context passed by the assistant orchestrator (graph_json, port, token, query, scope)"
      validation: "graph_json must be present"

  optional:
    - name: port
      type: integer
      default: "auto-resolved"
      description: "Server port — resolved via CLI → .x-ipe.yaml → defaults → 5858"
    - name: token
      type: string
      default: "auto-resolved"
      description: "Auth token — resolved via CLI → env var → instance/.internal_token"
    - name: query
      type: string
      description: "Original query that triggered the knowledge pipeline"
    - name: scope
      type: string
      description: "Scope hint for the graph callback"

outputs:
  state:
    - name: status
      value: success | failure

  data:
    - name: operation_output
      type: object
      description: "Structured result with callback_status, server response, and errors"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter (name starts with 'x-ipe-knowledge-')
      test: file_exists + yaml_parse
      expected: name == 'x-ipe-knowledge-present-to-knowledge-graph'

    - id: AC-S02
      category: structure
      criterion: scripts/graph_connector.py exists with connect subcommand
      test: file_exists + content_check
      expected: argparse with connect command

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
         Operations (1: connector), Output Result, Definition of Done,
         Error Handling, Examples]

    - id: AC-C02
      category: content
      criterion: connector operation defined with typed contract
      test: content_check
      expected: "Input, Output, Writes To, Constraints fields"

    - id: AC-C03
      category: content
      criterion: connector operation contains phase backbone (博学之→笃行之)
      test: content_check
      expected: "All 5 phases present"

    - id: AC-C04
      category: content
      criterion: Stateless service documented
      test: content_check
      expected: "Contains stateless service note"

    - id: AC-B01
      category: behavior
      criterion: graph_connector.py resolves port from CLI flag
      test: execution
      expected: uses CLI --port value

    - id: AC-B02
      category: behavior
      criterion: graph_connector.py resolves port from .x-ipe.yaml when no CLI flag
      test: execution
      expected: reads server.port from .x-ipe.yaml

    - id: AC-B03
      category: behavior
      criterion: graph_connector.py falls back to port 5858
      test: execution
      expected: uses 5858 when no other source found

    - id: AC-B04
      category: behavior
      criterion: graph_connector.py resolves auth token from env var
      test: execution
      expected: reads $X_IPE_INTERNAL_TOKEN

    - id: AC-B05
      category: behavior
      criterion: graph_connector.py handles missing graph JSON
      test: execution
      expected: GRAPH_JSON_NOT_FOUND error

    - id: AC-B06
      category: behavior
      criterion: graph_connector.py handles connection refused
      test: execution
      expected: CONNECTION_FAILED error after retries

  should:
    - id: AC-C05
      category: content
      criterion: Port resolution chain documented
      test: content_check
      expected: "CLI → .x-ipe.yaml → defaults → 5858"

    - id: AC-C06
      category: content
      criterion: Auth resolution chain documented
      test: content_check
      expected: "CLI → env var → instance/.internal_token"

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
      description: "Feature specification (AC-059D-09)"
    - path: "x-ipe-docs/requirements/EPIC-059/FEATURE-059-D/technical-design.md"
      description: "Technical design (D3 section)"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "port resolution from CLI"
      given: "--port 9000 flag"
      when: "execute connect"
      then: "Uses port 9000"

    - name: "port resolution fallback"
      given: "No CLI port, no .x-ipe.yaml"
      when: "execute connect"
      then: "Uses port 5858"

  error_cases:
    - name: "missing graph JSON"
      given: "graph_json path does not exist"
      when: "execute connect"
      then: "GRAPH_JSON_NOT_FOUND error"

    - name: "auth token not found"
      given: "No CLI token, no env var, no .internal_token file"
      when: "execute connect"
      then: "AUTH_TOKEN_NOT_FOUND error"

    - name: "connection refused"
      given: "Server not running"
      when: "execute connect"
      then: "CONNECTION_FAILED error after 2 retries"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "Port resolution chain works correctly (CLI → yaml → defaults → 5858)"
    - "Auth token resolution chain works correctly"
    - "HTTP POST uses correct URL, headers, and payload format"
    - "Retry logic executes max 2 attempts with 1-second delay"
    - "Error handling produces structured JSON errors"
