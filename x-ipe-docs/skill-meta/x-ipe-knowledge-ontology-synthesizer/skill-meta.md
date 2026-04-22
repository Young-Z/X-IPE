# Skill Meta: x-ipe-knowledge-ontology-synthesizer

# ═══════════════════════════════════════════════════════════
# SKILL META - Knowledge Skill (x-ipe-knowledge)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-knowledge-ontology-synthesizer
skill_type: x-ipe-knowledge
version: "1.0.0"
status: candidate
created: 2026-04-16
updated: 2026-04-16

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Cross-graph integration engine that discovers related ontology graphs, normalizes vocabulary into canonical terms, and links nodes across domains at class-level and instance-level tiers.

triggers:
  - "discover_related — find overlapping ontology graphs"
  - "wash_terms — normalize vocabulary across graphs"
  - "link_nodes — create cross-domain relationships"

not_for:
  - "Orchestration decisions — belong to x-ipe-assistant-knowledge-librarian-DAO"
  - "Building ontology from source content — that is x-ipe-knowledge-ontology-builder"
  - "Rendering knowledge for users — that is x-ipe-knowledge-present-to-user"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "Which operation to perform: discover_related | wash_terms | link_nodes"
      validation: "Must match one of the three defined operations"

    - name: context
      type: object
      description: "Full context passed by the assistant orchestrator (ontology_dir, graphs, params)"
      validation: "All required context fields for the specified operation must be present"

  optional:
    - name: search_scope
      type: string
      default: "all"
      description: "For discover_related: which graphs to search ('all' or comma-separated paths)"

    - name: tier
      type: string
      default: "class"
      description: "For link_nodes: linking tier ('class' or 'instance')"

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
      criterion: SKILL.md exists with valid frontmatter (name starts with 'x-ipe-knowledge-')
      test: file_exists + yaml_parse
      expected: name == 'x-ipe-knowledge-ontology-synthesizer'

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists with at least 1 example per operation
      test: file_exists + content_check
      expected: examples for discover_related, wash_terms, link_nodes

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    - id: AC-S04
      category: structure
      criterion: scripts/synthesis_ops.py exists with 4 commands (discover, wash, link, init_relations)
      test: file_exists + content_check
      expected: argparse subcommands for all 4 commands

    # CONTENT — Operations structure
    - id: AC-C01
      category: content
      criterion: All required sections present in order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, About, When to Use,
         Input Parameters, Input Initialization, Definition of Ready,
         Operations (3), Output Result, Definition of Done, Error Handling,
         Patterns & Anti-Patterns, Examples]

    - id: AC-C02
      category: content
      criterion: Three operations defined with typed contracts (discover_related, wash_terms, link_nodes)
      test: content_check
      expected: "Each operation has Input, Output, Writes To, Delegates To, Constraints"

    - id: AC-C03
      category: content
      criterion: Each operation contains phase backbone (博学之→笃行之)
      test: content_check
      expected: "All 5 phases present inside each of the 3 operations"

    - id: AC-C04
      category: content
      criterion: Each operation declares writes_to path
      test: content_check
      expected: "discover_related: stdout; wash_terms: stdout; link_nodes: .ontology/relations/"

    - id: AC-C05
      category: content
      criterion: Stateless service note in Important Notes
      test: content_check
      expected: "Contains 'stateless service' or equivalent"

    - id: AC-C06
      category: content
      criterion: Error Handling table present with columns [Error, Cause, Resolution]
      test: table_parse
      expected: at least 5 error entries

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: synthesis_ops.py discover command outputs JSON with related_graphs[] and overlap_candidates[]
      test: execution
      expected: JSON to stdout with correct fields

    - id: AC-B02
      category: behavior
      criterion: synthesis_ops.py wash command outputs JSON with canonical_vocabulary and normalization_map
      test: execution
      expected: JSON to stdout with correct fields

    - id: AC-B03
      category: behavior
      criterion: synthesis_ops.py link command writes to _relations.NNN.jsonl with event-sourcing envelope
      test: execution
      expected: JSONL records with {op, type, id, ts, props}

    - id: AC-B04
      category: behavior
      criterion: Chunk rotation at CHUNK_LINE_LIMIT=5000 works correctly
      test: execution
      expected: new chunk created when limit exceeded

    - id: AC-B05
      category: behavior
      criterion: Hierarchical linking enforced (BR-1) — no instance links without class links
      test: execution
      expected: instance tier returns empty when no class relations exist

  should:
    - id: AC-C07
      category: content
      criterion: When to Use includes explicit triggers for all 3 operations
      test: yaml_parse
      expected: triggers list has 3+ entries

    - id: AC-C08
      category: content
      criterion: Key Concepts in About section covers all domain concepts
      test: content_check
      expected: "Cross-Graph Discovery, Vocabulary Normalization, Hierarchical Linking, Confidence Scoring, Chunk Rotation"

    - id: AC-C09
      category: content
      criterion: Input Initialization subsection present under Input Parameters
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

    - id: AC-C10
      category: content
      criterion: Operation contract types are specific (not generic string/object)
      test: content_check
      expected: types like overlap_candidates[], normalization_map, cross_references[]

  could:
    - id: AC-C11
      category: content
      criterion: Confidence scoring documented with thresholds (1.0, 0.8, 0.6)
      test: content_check
      expected: confidence levels explained per match type

    - id: AC-C12
      category: content
      criterion: Constraints per operation are actionable and testable
      test: content_check
      expected: Each constraint maps to a verifiable condition

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

    - name: x-ipe-knowledge-ontology-builder
      relationship: upstream
      description: "Creates entities and vocabulary that the synthesizer integrates across domains"

  artifacts:
    - path: "x-ipe-docs/memory/.ontology/"
      description: "Ontology directory with schema/, instances/, vocabulary/ created by builder"

    - path: "x-ipe-docs/requirements/EPIC-059/FEATURE-059-D/specification.md"
      description: "Feature specification with ACs, FRs, BRs"

    - path: "x-ipe-docs/requirements/EPIC-059/FEATURE-059-D/technical-design.md"
      description: "Technical design with D1 synthesizer architecture"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "discover_related finds overlapping graphs"
      given: "Two ontology graphs with shared class label 'WebFramework'"
      when: "execute discover_related with source_graph pointing to graph 1"
      then: "success=true, related_graphs contains graph 2, overlap_candidates contains the shared class pair"

    - name: "wash_terms normalizes synonyms"
      given: "overlap_candidates with terms 'JS', 'JavaScript', 'javascript'"
      when: "execute wash_terms"
      then: "success=true, normalization_map maps all 3 to canonical 'JavaScript'"

    - name: "link_nodes creates class-level relations"
      given: "Two graphs with normalized matching class labels"
      when: "execute link_nodes with tier=class"
      then: "success=true, cross_references contains related_to relation, written to _relations.NNN.jsonl"

    - name: "link_nodes creates instance-level relations"
      given: "Class-level relations exist, instances belong to linked classes"
      when: "execute link_nodes with tier=instance"
      then: "success=true, instance relations created, synthesize_id/synthesize_message updated on entities"

    - name: "init_relations bootstraps empty file"
      given: ".ontology/ exists but no _relations.*.jsonl files"
      when: "execute init_relations"
      then: "_relations.001.jsonl created as empty file"

  error_cases:
    - name: "Invalid operation name"
      given: "operation='nonexistent'"
      when: "execute operation"
      then: "success=false, errors contains INVALID_OPERATION"

    - name: "Missing ontology directory"
      given: "ontology_dir path does not exist"
      when: "execute discover_related"
      then: "success=false, errors contains ONTOLOGY_DIR_ERROR"

    - name: "No overlapping graphs"
      given: "Two completely independent ontology graphs"
      when: "execute discover_related"
      then: "success=true, related_graphs=[], overlap_candidates=[]"

    - name: "Instance linking without class relations"
      given: "No class-level relations exist between target domains"
      when: "execute link_nodes with tier=instance"
      then: "success=true, cross_references=[], log warning"

    - name: "Duplicate relation detected"
      given: "Relation with same from_id+to_id+relation_type already exists"
      when: "execute link_nodes"
      then: "Duplicate skipped, logged, not written"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All 3 operation outputs match contract types"
    - "Relations written to declared writes_to paths (.ontology/relations/)"
    - "Entity synthesis updates written with correct envelope format"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully (no unhandled exceptions)"
    - "Chunk rotation triggers at 5000 records"
    - "Hierarchical linking constraint (BR-1) enforced"
