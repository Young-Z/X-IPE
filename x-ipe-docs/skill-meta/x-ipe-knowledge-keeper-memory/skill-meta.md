# Skill Meta — x-ipe-knowledge-keeper-memory

```yaml
# ═══════════════════════════════════════════════════════════
# SKILL META - Knowledge Skill (x-ipe-knowledge)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-knowledge-keeper-memory
skill_type: x-ipe-knowledge
version: "1.0.0"
status: candidate
created: 2026-04-16
updated: 2026-04-16

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Unified write gatekeeper for persistent memory — stores new knowledge entries
  and promotes working drafts to persistent memory tiers (episodic, semantic, procedural).

triggers:
  - "Store knowledge content to persistent memory"
  - "Promote working draft to a memory tier"
  - "Bootstrap memory folder structure"

not_for:
  - "Orchestration decisions (belong to assistant-knowledge-librarian-DAO)"
  - "Ontology entity registration (deferred to ontology-builder in FEATURE-059-C)"
  - "Reading/searching memory (use extractor-memory)"
  - "Web content extraction (use extractor-web)"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "Which operation to perform"
      validation: "Must be one of: store, promote"

    - name: context
      type: object
      description: "Full context passed by assistant orchestrator — varies per operation"
      validation: "All required context fields for the specified operation must be present"

  optional:
    - name: context.tags
      type: string[]
      default: "[]"
      description: "Searchable tags for the memory entry (store operation)"

    - name: context.metadata
      type: dict
      default: "{}"
      description: "Additional metadata (source, extracted_by, date, etc.)"

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
      expected: file contains at least 1 example per operation (store, promote)

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
      criterion: At least 2 operations defined (store, promote) with typed contracts
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
      criterion: Scripts exist (init_memory.py, memory_ops.py) in scripts/
      test: file_exists
      expected: "candidate/scripts/init_memory.py and candidate/scripts/memory_ops.py both exist"

    - id: AC-B02
      category: behavior
      criterion: store operation delegates to scripts/memory_ops.py create
      test: content_check
      expected: "store operation references 'scripts/memory_ops.py create'"

    - id: AC-B03
      category: behavior
      criterion: promote operation delegates to scripts/memory_ops.py promote
      test: content_check
      expected: "promote operation references 'scripts/memory_ops.py promote'"

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
      expected: "Operation Contract, Stateless Service, writes_to Discipline, Meaningful Slugs"

    - id: AC-C09
      category: content
      criterion: Input Initialization subsection present
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
      criterion: Multiple operations defined
      test: content_check
      expected: "≥2 operation blocks (store, promote)"

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
    - path: "x-ipe-docs/memory/"
      description: "Memory folder root — auto-bootstrapped by init_memory.py if missing"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "store success"
      given: "valid content + memory_type=semantic + title='Flask Jinja2 Templating'"
      when: "execute store"
      then: "file written to x-ipe-docs/memory/semantic/flask-jinja2-templating.md with frontmatter"

    - name: "promote success"
      given: "file in .working/overview/oauth2-patterns.md + memory_type=procedural"
      when: "execute promote"
      then: "file moved to x-ipe-docs/memory/procedural/oauth2-token-refresh-workflow.md"

  error_cases:
    - name: "Invalid memory_type"
      given: "memory_type='invalid'"
      when: "execute store"
      then: "success=false, errors contains INVALID_MEMORY_TYPE"

    - name: "Missing content"
      given: "no content provided"
      when: "execute store"
      then: "success=false, errors contains INPUT_VALIDATION_FAILED"

    - name: "Working path not found"
      given: "working_path doesn't exist"
      when: "execute promote"
      then: "success=false, errors contains PATH_NOT_FOUND"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All operation outputs match contract types"
    - "Results written to declared writes_to paths"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
    - "Scripts execute without import errors"
```
