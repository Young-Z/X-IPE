# Skill Meta Template: Assistant (x-ipe-assistant)

Use this template to create skill-meta.md for assistant skills (type: `x-ipe-assistant`). These skills act as assistant orchestrators with bounded, auditable outputs. The 格物致知 backbone serves as the CORE internal reasoning methodology.

---

## Template

```yaml
# ═══════════════════════════════════════════════════════════
# SKILL META - Assistant Skill (x-ipe-assistant)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-assistant-{name}
skill_type: x-ipe-assistant
version: "1.0.0"
status: draft | candidate | production
created: YYYY-MM-DD
updated: YYYY-MM-DD

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  {One sentence: what human-required touchpoint this skill mediates and why — use universally understood language, avoid "DAO" in the summary.}

triggers:
  - "{trigger phrase 1}"
  - "{trigger phrase 2}"

not_for:
  - "{out-of-scope use case}"

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
      description: "Structured DAO output with disposition, content, rationale_summary, confidence, and fallback_required"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
      test: file_exists + yaml_parse
      expected: name starts with 'x-ipe-assistant-'

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists
      test: file_exists
      expected: file contains at least 2 examples

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    - id: AC-C01
      category: content
      criterion: Output contract includes disposition, content, rationale_summary, confidence, fallback_required
      test: content_check
      expected: all 5 fields present in Output Result

    - id: AC-C02
      category: content
      criterion: Assistant documents bounded-output behavior
      test: content_check
      expected: explicit prohibition on exposing full inner reasoning

    - id: AC-B01
      category: behavior
      criterion: Assistant can choose among supported dispositions
      test: execution
      expected: supported dispositions documented and examples cover direct answer and pass-through

  should:
    - id: AC-C03
      category: content
      criterion: Human-shadow fallback logic documented
      test: content_check
      expected: fallback_required only when human-shadow is enabled and confidence is below threshold

    - id: AC-C04
      category: content
      criterion: Seven-step backbone documented
      test: content_check
      expected: 静虑, 兼听, 审势, 权衡, 谋后而定, 试错, 断 all present

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-meta-skill-creator
      relationship: creator

  artifacts:
    - path: "references/dao-disposition-guidelines.md"
      description: "Reference for choosing DAO dispositions consistently"
```

---

## Usage

1. Copy template YAML block
2. Fill all required fields
3. Define Assistant-specific acceptance criteria
4. Save as `x-ipe-docs/skill-meta/{skill-name}/skill-meta.md`
