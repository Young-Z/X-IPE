# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-reference-ontology
skill_type: x-ipe-tool
version: "1.0.0"
status: candidate
created: 2026-07-17
updated: 2026-07-17

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Search and query the knowledge base ontology — entity lookup, graph traversal, and semantic search across ontology graphs.

triggers:
  - "search ontology"
  - "query ontology"
  - "find related entities"
  - "ontology search"
  - "knowledge graph search"
  - "find path between entities"

not_for:
  - "Creating/updating entities — use x-ipe-tool-ontology"
  - "Building graphs — use x-ipe-tool-ontology"
  - "Dimension registry operations — use x-ipe-tool-ontology"
  - "Retag operations — use x-ipe-tool-ontology"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "The read/search operation to perform"
      validation: "Must be one of: search, query, related, find_path, load"

  optional:
    - name: query
      type: string
      default: null
      description: "Search text (required for search operation)"

    - name: scope
      type: string
      default: "all"
      description: "Search scope: 'all' or comma-separated .jsonl filenames"

    - name: ontology_dir
      type: string
      default: "x-ipe-docs/knowledge-base/.ontology/"
      description: "Path to .ontology/ directory"

    - name: graph_path
      type: string
      default: null
      description: "Path to specific graph .jsonl file (for query, related, find_path, load)"

    - name: entity_type
      type: string
      default: "KnowledgeNode"
      description: "Entity type filter (for query operation)"

    - name: where
      type: object
      default: null
      description: "JSON property filter (for query operation)"

    - name: entity_id
      type: string
      default: null
      description: "Entity ID (for related operation)"

    - name: from_id
      type: string
      default: null
      description: "Source entity ID (for find_path operation)"

    - name: to_id
      type: string
      default: null
      description: "Target entity ID (for find_path operation)"

    - name: relation_type
      type: string
      default: null
      description: "Filter by relation type (for related operation)"

    - name: direction
      type: string
      default: null
      description: "Relation direction: outgoing or incoming (for related operation)"

    - name: depth
      type: integer
      default: 3
      description: "BFS traversal depth (for search operation)"

    - name: page_size
      type: integer
      default: 20
      description: "Results per page (for search operation)"

    - name: page
      type: integer
      default: 1
      description: "1-based page number (for search operation)"

outputs:
  state:
    - name: status
      value: success | failure

  data:
    - name: operation_output
      type: object
      description: "JSON result from the executed operation (entities, matches, paths, or graph state)"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
      test: file_exists + yaml_parse
      expected: name is 'x-ipe-tool-reference-ontology'

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists
      test: file_exists
      expected: file contains at least 4 examples (one per read operation)

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 600 lines
      test: line_count
      expected: < 600

    - id: AC-C01
      category: content
      criterion: All required tool-skill sections present in order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, About, When to Use,
         Input Parameters, Input Initialization, Definition of Ready,
         Operations, Output Result, Definition of Done, Error Handling,
         Templates, Examples]

    - id: AC-C02
      category: content
      criterion: Only read/search operations included — no CRUD, no graph build, no retag
      test: content_check
      expected: operations limited to search, query, related, find_path, load

    - id: AC-C03
      category: content
      criterion: Scripts referenced at original path (.github/skills/x-ipe-tool-ontology/scripts/)
      test: content_check
      expected: no script copies — all commands use original ontology skill script paths

    - id: AC-B01
      category: behavior
      criterion: Search operation executes both search.py and ui-callback.py steps
      test: execution
      expected: two-step search+callback documented as BLOCKING

  should:
    - id: AC-C04
      category: content
      criterion: Input Initialization subsection present under Input Parameters
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

    - id: AC-C05
      category: content
      criterion: Entity model reference included (KnowledgeNode properties, relation types, ID format)
      test: content_check
      expected: About section documents entity model from x-ipe-tool-ontology

    - id: AC-B02
      category: behavior
      criterion: All five operations return JSON to stdout
      test: execution
      expected: consistent JSON output format across operations

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-tool-ontology
      reason: "Scripts (search.py, ontology.py, ui-callback.py) live in this skill's scripts/ directory"

  artifacts:
    - path: ".github/skills/x-ipe-tool-ontology/scripts/search.py"
      description: "Full ontology search engine"
    - path: ".github/skills/x-ipe-tool-ontology/scripts/ontology.py"
      description: "Entity operations (query, related, find-path, load)"
    - path: ".github/skills/x-ipe-tool-ontology/scripts/ui-callback.py"
      description: "Push search results to KB Graph Viewer UI"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Search ontology for a keyword"
      given: "ontology with entities containing 'authentication'"
      when: "execute search with query='authentication' scope='all'"
      then: "success=true with matches, subgraph, and UI callback triggered"

    - name: "Query entities by property filter"
      given: "ontology with concept-type entities"
      when: "execute query with entity_type='KnowledgeNode' where={'node_type':'concept'}"
      then: "success=true with filtered entity list"

    - name: "Find related entities"
      given: "entity with known relations"
      when: "execute related with entity_id='know_a1b2c3d4'"
      then: "success=true with list of related entities and relation types"

    - name: "Find path between two entities"
      given: "two entities connected via intermediate nodes"
      when: "execute find_path with from_id and to_id"
      then: "success=true with BFS shortest path"

  error_cases:
    - name: "Search with missing ontology directory"
      given: "non-existent ontology-dir path"
      when: "execute search"
      then: "success=false with descriptive error"

    - name: "Related with unknown entity ID"
      given: "entity_id that does not exist in graph"
      when: "execute related"
      then: "success=false or empty result set"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "Only read/search operations are exposed — no mutation operations"
    - "All script paths point to x-ipe-tool-ontology/scripts/ (no copies)"
    - "Search operation documents the mandatory two-step search+callback flow"
    - "Entity model reference matches x-ipe-tool-ontology documentation"
