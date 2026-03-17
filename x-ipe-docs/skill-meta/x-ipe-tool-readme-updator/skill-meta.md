# ═══════════════════════════════════════════════════════════
# SKILL META - Tool Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-tool-readme-updator
skill_type: x-ipe-tool
version: "1.0.0"
status: candidate
created: 2026-03-17
updated: 2026-03-17

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Update project-related instructional documentation (README.md) by identifying, verifying, and documenting run/test commands from project configuration files.

triggers:
  - "update README"
  - "generate README run section"
  - "document how to run"
  - "update project docs"
  - "update README with run instructions"

not_for:
  - "x-ipe-task-based-user-manual: standalone lifecycle task with task board management"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: operation
      type: string
      description: "The operation to perform"
      validation: "Must be 'update_readme'"

  optional:
    - name: feature_context
      type: object
      default: null
      description: "Context about the feature being documented (feature_id, feature_title) — used when invoked from feature-closing to scope documentation"

    - name: readme_path
      type: string
      default: "README.md"
      description: "Path to the README file to update"

outputs:
  state:
    - name: status
      value: success | failure

  artifacts:
    - name: readme
      type: file
      path: "README.md"
      description: "Updated README with How to Run section"

  data:
    - name: operation_output
      type: object
      description: "Contains success status, verified run_command, test_command, and errors"

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
      criterion: All required sections present in correct order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, About, When to Use,
         Input Parameters, Input Initialization, Definition of Ready,
         Operations, Output Result, Definition of Done, Error Handling,
         Examples]

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
      criterion: Tool identifies run commands from pyproject.toml or package.json
      test: execution
      expected: returns run_command string

    - id: AC-B02
      category: behavior
      criterion: Tool verifies commands execute successfully
      test: execution
      expected: commands run without error

    - id: AC-B03
      category: behavior
      criterion: Tool updates README with Prerequisites, Installation, Running, Testing sections
      test: content_check
      expected: All 4 subsections present in README after execution

  should:
    - id: AC-C04
      category: content
      criterion: When to Use includes explicit triggers and not_for
      test: yaml_parse
      expected: triggers list is not empty

    - id: AC-C05
      category: content
      criterion: Key Concepts section in About
      test: content_check
      expected: "**Key Concepts:**"

    - id: AC-C06
      category: content
      criterion: Input Initialization subsection present under Input Parameters
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

  could:
    - id: AC-C07
      category: content
      criterion: feature_context used to scope README documentation
      test: content_check
      expected: when feature_context provided, README section mentions the feature

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-task-based-feature-closing
      relationship: "optional caller — invokes this tool in Phase 3"

  artifacts:
    - path: "pyproject.toml OR package.json"
      description: "Project config file to detect run/test commands"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Python project README update"
      given: "pyproject.toml exists with entry point"
      when: "execute update_readme"
      then: "success=true, README contains uv-based instructions"

    - name: "Node.js project README update"
      given: "package.json exists with scripts"
      when: "execute update_readme"
      then: "success=true, README contains npm-based instructions"

  error_cases:
    - name: "No config file found"
      given: "neither pyproject.toml nor package.json exists"
      when: "execute update_readme"
      then: "success=false, errors contains MANUAL_NO_CONFIG"

    - name: "Command verification fails"
      given: "config file exists but run command fails"
      when: "execute update_readme"
      then: "success=false, errors contains MANUAL_CMD_FAILED"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All outputs match schema"
    - "DoD checkpoints all verified"
    - "Error scenarios handled gracefully"
