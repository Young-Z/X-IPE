# Skill Meta Template: Knowledge Skill (x-ipe-knowledge)

Use this template to create skill-meta.md for knowledge skills (type: `x-ipe-knowledge`). These skills are stateless pipeline services called by assistant orchestrators. Each skill defines named **Operations** with typed contracts; inside each operation, the phase backbone (博学之→笃行之) provides internal cognitive flow.

---

## Template

```yaml
# ═══════════════════════════════════════════════════════════
# SKILL META - Knowledge Skill (x-ipe-knowledge)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-knowledge-{sub-category}-{name}
skill_type: x-ipe-knowledge
version: "1.0.0"
status: draft | candidate | production
created: YYYY-MM-DD
updated: YYYY-MM-DD

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  {One sentence: what knowledge pipeline service(s) this skill provides and for which domain.}

triggers:
  - "{operation trigger 1 — what the orchestrator requests}"
  - "{operation trigger 2}"

not_for:
  - "{out-of-scope — e.g., orchestration decisions belong to assistant skills}"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "Which operation to perform"
      validation: "Must match one of the defined operations"

    - name: context
      type: object
      description: "Full context passed by the assistant orchestrator (source_path, output_path, params)"
      validation: "All required context fields for the specified operation must be present"

  optional:
    - name: {param_name}
      type: string
      default: null
      description: "{operation-specific optional parameter}"

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
      criterion: At least one Operation defined with typed contract
      test: content_check
      expected: "Operation block with Input, Output, Writes To, Constraints fields"

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
      criterion: Multiple operations defined
      test: content_check
      expected: ≥2 operation blocks

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
    - path: "{required artifact path}"
      description: "{what must exist before skill can run}"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "{operation name} success"
      given: "{valid context with source_path and output_path}"
      when: "execute {operation}"
      then: "success=true, result written to writes_to path"

  error_cases:
    - name: "Invalid operation name"
      given: "operation='nonexistent'"
      when: "execute operation"
      then: "success=false, errors contains INVALID_OPERATION"

    - name: "Missing required context"
      given: "context missing source_path"
      when: "execute {operation}"
      then: "success=false, errors contains INPUT_VALIDATION_FAILED"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All operation outputs match contract types"
    - "Results written to declared writes_to paths"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
```

---

## Field Reference

| Section | Field | Required | Description |
|---------|-------|----------|-------------|
| Identity | skill_name | Yes | `x-ipe-knowledge-{sub-category}-{name}` format |
| Identity | version | Yes | Semver format |
| Identity | status | Yes | draft → candidate → production |
| Purpose | summary | Yes | Single sentence: what pipeline service |
| Purpose | triggers | Yes | Operation-level triggers from orchestrator |
| Purpose | not_for | Yes | Explicit out-of-scope (e.g., orchestration) |
| Interface | inputs.required | Yes | `operation` and `context` are standard |
| Interface | outputs.data | Yes | `operation_output` is standard |
| Acceptance | must (AC-C02) | Yes | Typed operation contract required |
| Acceptance | must (AC-C03) | Yes | Phase backbone inside operations |
| Acceptance | must (AC-C04) | Yes | writes_to in every operation |
| Acceptance | must (AC-C05) | Yes | Stateless service documented |
| Testing | happy_path | Yes | At least 1 scenario per operation |
| Testing | error_cases | Yes | Invalid operation + missing context |

---

## Knowledge-Specific Criteria (vs. Other Types)

| Criterion | Knowledge | Tool | Task-Based | Assistant |
|-----------|-----------|------|------------|-----------|
| Primary structure | Operations | Operations | Phases | 格物致知 backbone |
| Phase backbone | Inside each operation | Not used | Top-level | Top-level |
| State model | Stateless (orchestrator passes context) | Stateless | Internal | Manages workflow state |
| writes_to required | Yes (per operation) | No | No | No |
| Caller | Assistant orchestrator | Any skill/agent | Human/workflow | General AI/workflow |
| Task-matched | No (coordinated by assistant) | No | Yes | Yes |

---

## Usage

1. Copy template YAML block
2. Fill all required fields
3. Define knowledge-specific acceptance criteria (operations, writes_to, statelessness)
4. Add test scenarios for each operation
5. Save as `x-ipe-docs/skill-meta/{skill-name}/skill-meta.md`
