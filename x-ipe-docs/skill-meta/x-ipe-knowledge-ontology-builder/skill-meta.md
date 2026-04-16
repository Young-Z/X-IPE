# ═══════════════════════════════════════════════════════════
# SKILL META - Knowledge Skill (x-ipe-knowledge)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-knowledge-ontology-builder
skill_type: x-ipe-knowledge
version: "1.0.0"
status: candidate
created: 2026-04-16
updated: 2026-04-16

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Discovers classes, properties, and instances from constructed knowledge and registers them in `.ontology/` with lifecycle flags, delegating JSONL I/O to scripts/ontology_ops.py.

triggers:
  - "Discover classes/concepts from memory content and register in ontology schema"
  - "Discover properties for a class via web search and source analysis"
  - "Create entity instances from source content with lifecycle flags"
  - "Validate ontology entries against vocabulary for consistency"
  - "Register new vocabulary terms with broader/narrower hierarchy"

not_for:
  - "Orchestration decisions (belong to x-ipe-assistant-knowledge-librarian-DAO)"
  - "Relationship/edge creation between entities (use ontology-synthesizer in 059-D)"
  - "Reading/searching ontology (use x-ipe-knowledge-extractor-memory or x-ipe-tool-ontology search)"
  - "Writing memory content files (use x-ipe-knowledge-keeper-memory)"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "Which operation to perform: discover_nodes | discover_properties | create_instances | critique_validate | register_vocabulary"
      validation: "Must match one of the 5 defined operations"

    - name: context
      type: object
      description: "Full context passed by the assistant orchestrator (source paths, parameters, schemas)"
      validation: "All required context fields for the specified operation must be present"

  optional:
    - name: depth_limit
      type: int
      default: 3
      description: "Max hierarchy depth for discover_nodes"

    - name: web_search_template
      type: string
      default: "What are common attributes of a {class_label}?"
      description: "Template for web search in discover_properties"

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
         Operations (5), Output Result, Definition of Done, Error Handling,
         Examples]

    - id: AC-C02
      category: content
      criterion: All 5 operations defined with typed contracts
      test: content_check
      expected: "discover_nodes, discover_properties, create_instances, critique_validate, register_vocabulary — each with Input, Output, Writes To, Constraints"

    - id: AC-C03
      category: content
      criterion: Each operation contains phase backbone (博学之→笃行之)
      test: content_check
      expected: "All 5 phases present inside each operation"

    - id: AC-C04
      category: content
      criterion: Each operation declares writes_to path
      test: content_check
      expected: "writes_to field present in every operation contract"

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

    - id: AC-B02
      category: behavior
      criterion: ontology_ops.py has all 5 CLI commands
      test: script_check
      expected: "register_class, add_properties, create_instance, add_vocabulary, validate_terms"

    - id: AC-B03
      category: behavior
      criterion: Lifecycle determination works correctly
      test: unit
      expected: ".working/ paths → Ephemeral; persistent paths → Persistent"

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
      criterion: Input Initialization subsection present
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

    - id: AC-C10
      category: content
      criterion: Operation contract types are specific
      test: content_check
      expected: "Uses domain-specific types (node_tree, proposed_properties, critique_report)"

  could:
    - id: AC-C11
      category: content
      criterion: Chunk rotation documented in create_instances
      test: content_check
      expected: "5000 line limit and next-chunk logic described"

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

  artifacts:
    - path: "x-ipe-docs/memory/.ontology/"
      description: "Ontology root directory (schema/, instances/, vocabulary/)"

    - path: "scripts/ontology_ops.py"
      description: "Python JSONL write utility script"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "discover_nodes success"
      given: "source_content paths to semantic memory files"
      when: "execute discover_nodes"
      then: "success=true, node_tree returned, classes written to .ontology/schema/"

    - name: "discover_properties success"
      given: "class_meta for WebFramework, source_content, web_search_template"
      when: "execute discover_properties"
      then: "success=true, proposed_properties[] returned with kind/range/cardinality"

    - name: "create_instances success"
      given: "class_registry, source_content, property_schema"
      when: "execute create_instances"
      then: "success=true, instances[] with lifecycle flags written to .ontology/instances/"

    - name: "critique_validate success"
      given: "class_registry, instances, vocabulary_index"
      when: "execute critique_validate"
      then: "success=true, critique_report with scores and suggestions returned"

    - name: "register_vocabulary success"
      given: "new_terms with broader/narrower, target_scheme"
      when: "execute register_vocabulary"
      then: "success=true, terms added to .ontology/vocabulary/{scheme}.json"

  error_cases:
    - name: "Invalid operation name"
      given: "operation='nonexistent'"
      when: "execute operation"
      then: "success=false, errors contains INVALID_OPERATION"

    - name: "Missing required context"
      given: "context missing source_content"
      when: "execute discover_nodes"
      then: "success=false, errors contains INPUT_VALIDATION_FAILED"

    - name: "Ephemeral lifecycle for .working/ source"
      given: "source_files includes .working/ path"
      when: "execute create_instances"
      then: "instance lifecycle is 'Ephemeral'"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All 5 operation outputs match contract types"
    - "Results written to declared writes_to paths"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
    - "ontology_ops.py executes without error for all commands"
    - "Lifecycle determination logic correct for .working/ vs persistent paths"
