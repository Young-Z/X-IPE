# Skill Meta Template: Tool Skill

Use this template to create skill-meta.md for tool skills. The skill-meta defines **acceptance criteria** for automated testing.

---

## Template

```yaml
# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-{name}
skill_type: x-ipe-tool
version: "1.0.0"
status: draft | candidate | production
created: YYYY-MM-DD
updated: YYYY-MM-DD

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  {One sentence: What this tool does and its key value.}

triggers:
  - "{trigger phrase 1}"
  - "{trigger phrase 2}"

not_for:
  - "{alternative tool}: {when to use instead}"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "The operation to perform"
      validation: "Must match one of the defined operations"

    - name: {input_name}
      type: string | number | boolean | array | object
      default: {value}
      description: "{what this controls}"

  optional:
    - name: {input_name}
      type: string
      default: null
      description: "{what this controls}"

outputs:
  state:
    - name: status
      value: success | failure

  artifacts:
    - name: {artifact_name}
      type: file
      path: "{path}"
      description: "{what this contains}"

  data:
    - name: operation_output
      type: object
      description: "Structure containing result, success status, and errors"

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
      expected: name starts with 'x-ipe-tool-'

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists
      test: file_exists
      expected: file contains at least 1 example

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    # CONTENT
    - id: AC-C01
      category: content
      criterion: All 12 required sections present in order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, About, When to Use, 
         Input Parameters, Definition of Ready, Operations, 
         Output Result, Definition of Done, Error Handling, 
         Templates, Examples]

    - id: AC-C02
      category: content
      criterion: Operations use XML structure
      test: regex_match
      expected: "<operation name=.*>"

    - id: AC-C03
      category: content
      criterion: Error Handling table present
      test: table_parse
      expected: columns [Error, Cause, Resolution]

    # BEHAVIOR
    - id: AC-B01
      category: behavior
      criterion: Tool produces structured output
      test: execution
      expected: returns operation_output object

  should:
    - id: AC-C04
      category: content
      criterion: When to Use includes explicit triggers
      test: yaml_parse
      expected: triggers list is not empty

    - id: AC-C05
      category: content
      criterion: Key Concepts section in About
      test: content_check
      expected: "**Key Concepts:**"

  could:
    - id: AC-C06
      category: content
      criterion: Templates provided for outputs
      test: file_exists
      expected: templates directory is not empty

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: task-execution-guideline
      relationship: prerequisite

  artifacts:
    - path: "{required artifact path}"
      description: "{what must exist before skill can run}"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "{operation name} success"
      given: "{valid inputs}"
      when: "execute {operation}"
      then: "success=true and result contains {value}"

  error_cases:
    - name: "Invalid input handling"
      given: "{invalid input}"
      when: "execute {operation}"
      then: "success=false and errors contains {error_code}"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All outputs match schema"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
```

---

## Field Reference

| Section | Field | Required | Description |
|---------|-------|----------|-------------|
| Identity | skill_name | Yes | `x-ipe-tool-{name}` format |
| Interface | inputs.required | Yes | `operation` is standard |
| Acceptance | must | Yes | All must pass for merge |
| Testing | happy_path | Yes | At least 1 scenario per operation |

---

## Usage

1. Copy template YAML block
2. Fill all required fields
3. Define specific acceptance criteria for tool operations
4. Add test scenarios
5. Save as `x-ipe-docs/skill-meta/{skill-name}/skill-meta.md`
