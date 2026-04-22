# ═══════════════════════════════════════════════════════════
# SKILL META - Assistant Skill (x-ipe-assistant)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-assistant-user-representative-Engineer
skill_type: x-ipe-assistant
version: "1.0.0"
status: candidate
created: 2026-04-20
updated: 2026-04-20

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Represent human intent at end-user-facing touchpoints as an autonomous human representative (工程師 persona). Migrated from x-ipe-assistant-user-representative-Engineer to x-ipe-assistant namespace with identical functionality.

triggers:
  - "represent human intent"
  - "human representative guidance"
  - "approval-like guidance"
  - "guidance on behalf of the human"

not_for:
  - "long-term memory retrieval or persistence"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: message_context
      type: object
      description: "Message source, calling context, and messages array"
      validation: "Must have source (human|ai) and non-empty messages array"

    - name: message_context.messages
      type: array
      description: "Array of messages with content and optional preferred_dispositions"

  optional:
    - name: human_shadow
      type: boolean
      default: false
      description: "Whether the skill may escalate to a real human when confidence is low"

outputs:
  state:
    - name: status
      value: success | failure

  data:
    - name: operation_output
      type: object
      description: "Structured output with instruction_units[], execution_plan, confidence, and fallback_required"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
      test: file_exists + yaml_parse
      expected: name = 'x-ipe-assistant-user-representative-Engineer'

    - id: AC-S02
      category: structure
      criterion: references/ folder contains all 5 reference files from old skill
      test: file_exists
      expected: dao-disposition-guidelines.md, dao-log-format.md, dao-phases-and-output-format.md, engineering-workflow.md, examples.md

    - id: AC-S03
      category: structure
      criterion: templates/ folder contains dao-log-template.md
      test: file_exists
      expected: templates/dao-log-template.md exists

    - id: AC-S04
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: "< 500"

    - id: AC-C01
      category: content
      criterion: Output contract preserves instruction_units[], execution_plan, confidence, fallback_required
      test: content_check
      expected: All fields from old skill present in Output Result

    - id: AC-C02
      category: content
      criterion: All 7 disposition types preserved
      test: content_check
      expected: "answer, clarification, reframe, critique, instruction, approval, pass_through"

    - id: AC-C03
      category: content
      criterion: SKILL.md conforms to x-ipe-assistant template section order
      test: content_check
      expected: "CONTEXT → DECISION → ACTION → VERIFY → REFERENCE section flow"

    - id: AC-C04
      category: content
      criterion: About section present with 格物致知 backbone and Key Concepts
      test: content_check
      expected: About section with CORE Backbone explanation

    - id: AC-C05
      category: content
      criterion: 工程師 (Engineer) persona in description
      test: content_check
      expected: description frontmatter mentions 工程師

    - id: AC-B01
      category: behavior
      criterion: Functionally identical output to old skill
      test: execution
      expected: Same dispositions, same instruction_units format, same fallback behavior

  should:
    - id: AC-C06
      category: content
      criterion: Best-Model Requirement documented
      test: content_check
      expected: Premium LLM requirement in Important Notes

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-meta-skill-creator
      relationship: creator
    - name: x-ipe-assistant-user-representative-Engineer
      relationship: migration_source

  artifacts:
    - path: "references/dao-disposition-guidelines.md"
      description: "Disposition selection guidance (copied from source)"
    - path: "references/dao-log-format.md"
      description: "Semantic log format (copied from source)"
    - path: "references/dao-phases-and-output-format.md"
      description: "Phase definitions and CLI output (copied from source)"
    - path: "references/engineering-workflow.md"
      description: "Engineering workflow DAG (copied from source)"
    - path: "references/examples.md"
      description: "Usage examples (copied from source, name refs updated)"
    - path: "templates/dao-log-template.md"
      description: "Log template (copied from source)"
