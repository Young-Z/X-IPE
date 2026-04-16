# Skill Meta: x-ipe-knowledge-extractor-memory

```yaml
# ═══════════════════════════════════════════════════════════
# SKILL META - Knowledge Skill (x-ipe-knowledge)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-knowledge-extractor-memory
skill_type: x-ipe-knowledge
version: "1.0.0"
status: candidate
created: 2026-04-16
updated: 2026-04-16

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Searches and retrieves existing knowledge from persistent memory tiers and ontology — provides overview scanning (extract_overview) and detailed content retrieval (extract_details) as read-only operations.

triggers:
  - "Search memory for knowledge about a topic"
  - "Retrieve detailed content from a memory entry"
  - "Scan knowledge base for relevant entries"

not_for:
  - "Writing or modifying memory (use keeper-memory)"
  - "Extracting from web sources (use extractor-web)"
  - "Orchestration decisions (belong to assistant-knowledge-librarian-DAO)"
  - "Building or modifying ontology (deferred to ontology-builder/synthesizer)"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "Which operation to perform"
      validation: "Must be one of: extract_overview, extract_details"

    - name: context
      type: object
      description: "Full context passed by the assistant orchestrator (target, depth, scope, etc.)"
      validation: "All required context fields for the specified operation must be present"

  optional:
    - name: context.knowledge_type
      type: string
      default: null
      description: "Filter search to a specific memory tier (episodic, semantic, procedural)"

    - name: context.format_hints
      type: string
      default: null
      description: "Output format preference for extract_details"

outputs:
  state:
    - name: status
      value: success | failure

  data:
    - name: operation_output
      type: object
      description: "Structured result with success, operation name, result data (writes_to always null), and errors"

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
      criterion: At least 2 operations defined with typed contracts
      test: content_check
      expected: "extract_overview and extract_details blocks with Input, Output, Writes To, Constraints fields"

    - id: AC-C03
      category: content
      criterion: Each operation contains phase backbone (博学之→笃行之)
      test: content_check
      expected: "All 5 phases present inside each operation: 博学之, 审问之, 慎思之, 明辨之, 笃行之"

    - id: AC-C04
      category: content
      criterion: Each operation declares writes_to as null (read-only)
      test: content_check
      expected: "writes_to field is null in every operation contract"

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

    # BEHAVIOR — Bundled scripts
    - id: AC-B01
      category: behavior
      criterion: scripts/search.py exists and is functional
      test: file_exists + execution
      expected: "search.py runs with --query and --memory-dir; outputs JSON"

    - id: AC-B02
      category: behavior
      criterion: search.py loads entities from instances/*.jsonl standalone (no ontology.py dependency)
      test: content_check + execution
      expected: "No 'from ontology import' in search.py; _load_entities reads JSONL directly"

    - id: AC-B03
      category: behavior
      criterion: search.py supports --memory-dir, --query, --depth, --page-size, --page, --class-filter
      test: execution
      expected: "All CLI flags accepted; --class-filter filters entities by type"

    - id: AC-B04
      category: behavior
      criterion: extract_overview shallow uses glob/grep only; medium adds ontology search
      test: content_check
      expected: "SKILL.md Phase 3 of extract_overview distinguishes shallow (glob/grep) from medium (+search.py)"

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
      expected: "Operation Contract, Stateless Service, writes_to Discipline, Dual Search Strategy, Ontology Absorption"

    - id: AC-C09
      category: content
      criterion: Input Initialization subsection present under Input Parameters
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

    - id: AC-C10
      category: content
      criterion: Operation contract types are specific (not generic string/object)
      test: content_check
      expected: "Input/Output use domain types like overview_content, source_map, extracted_content, metadata"

  could:
    - id: AC-C11
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
    - path: "x-ipe-docs/memory/"
      description: "Memory folder structure with episodic/, semantic/, procedural/ tiers"

    - path: "x-ipe-docs/memory/.ontology/"
      description: "Ontology data for medium-depth search (instances/*.jsonl, _relations.*.jsonl)"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "extract_overview success"
      given: "query 'flask', memory tiers populated"
      when: "execute extract_overview with depth=shallow"
      then: "success=true, overview_content lists matching entries, source_map is non-empty array"

    - name: "extract_details success"
      given: "target path 'semantic/flask-jinja2-templating.md' exists"
      when: "execute extract_details with scope=full"
      then: "success=true, extracted_content contains file content, metadata has title and tags"

  error_cases:
    - name: "Empty results"
      given: "query 'nonexistent-topic-xyz'"
      when: "execute extract_overview"
      then: "success=true, overview_content='No entries found for ...', source_map is empty array (not error)"

    - name: "Invalid operation"
      given: "operation='invalid'"
      when: "execute operation"
      then: "success=false, errors contains INVALID_OPERATION"

    - name: "File not found"
      given: "target='semantic/doesnt-exist.md'"
      when: "execute extract_details"
      then: "success=false, errors contains PATH_NOT_FOUND"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All operation outputs match contract types"
    - "writes_to is null for every operation (read-only verified)"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
    - "scripts/search.py executes without ontology.py dependency"
```
