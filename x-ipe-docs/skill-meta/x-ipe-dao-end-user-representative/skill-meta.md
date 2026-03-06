# ═══════════════════════════════════════════════════════════
# SKILL META - DAO Skill
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-dao-end-user-representative
skill_type: x-ipe-dao
version: "1.0.0"
status: candidate
created: 2026-03-06
updated: 2026-03-06
implementation_path: .github/skills/x-ipe-dao-end-user-representative/

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Represent human intent at end-user-facing touchpoints by returning a bounded disposition,
  a user-safe response, and optional human-shadow fallback guidance.

triggers:
  - "represent human intent"
  - "human representative guidance"
  - "human representative"
  - "guidance on behalf of the human"

not_for:
  - "semantic DAO logging rollout: handled by FEATURE-047-B"
  - "instruction-resource interception rollout: handled by FEATURE-047-C"
  - "persistent memory or experience replay: out of scope for v1"

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

    - name: message_context.calling_skill
      type: string
      description: "Name of the skill invoking this human representative"

outputs:
  state:
    - name: status
      value: success | failure

  data:
    - name: operation_output
      type: object
      description: "Structured output with disposition, content, rationale_summary, confidence, and fallback_required"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
      test: file_exists + yaml_parse
      expected: name is 'x-ipe-dao-end-user-representative'

    - id: AC-S02
      category: structure
      criterion: references/examples.md and references/dao-disposition-guidelines.md exist
      test: file_exists
      expected: both files present

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    - id: AC-C01
      category: content
      criterion: DAO documents seven supported dispositions
      test: content_check
      expected: answer, clarification, reframe, critique, instruction, approval, pass_through

    - id: AC-C02
      category: content
      criterion: Output contract is bounded and excludes full inner reasoning
      test: content_check
      expected: explicit bounded-output language plus rationale_summary field

    - id: AC-C03
      category: content
      criterion: Human-shadow fallback logic uses AND semantics
      test: content_check
      expected: fallback_required only when human-shadow is enabled and confidence is below threshold

    - id: AC-B01
      category: behavior
      criterion: DAO can directly answer or pass through depending on context
      test: execution
      expected: examples cover both answer and pass_through outcomes

  should:
    - id: AC-C04
      category: content
      criterion: Seven-step backbone documented
      test: content_check
      expected: 静虑, 兼听, 审势, 权衡, 谋后而定, 试错, 断 all present

    - id: AC-C05
      category: content
      criterion: Input Initialization subsection present under Input Parameters
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-meta-skill-creator
      relationship: creator
      description: Creator skill used to generate DAO-specific structure and templates

  artifacts:
    - path: ".github/skills/x-ipe-meta-skill-creator/templates/x-ipe-dao.md"
      description: "DAO skill template used to define the runtime skill"
    - path: ".github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-dao.md"
      description: "DAO skill-meta template used to define acceptance criteria"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Direct answer disposition"
      given: "A user-facing question the skill can answer directly"
      when: "execute represent_human_intent"
      then: "success=true, disposition=answer, fallback_required=false"

    - name: "Pass through to downstream agent"
      given: "A user asks workflow-status detail best answered by downstream task context"
      when: "execute represent_human_intent"
      then: "success=true, disposition=pass_through, content reframes or forwards the question"

  error_cases:
    - name: "Missing message content"
      given: "message_context.messages is empty"
      when: "execute represent_human_intent"
      then: "success=false with DAO_INPUT_INVALID"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "Output contract remains bounded and chain-of-thought-safe"
    - "Fallback logic uses human_shadow AND internal confidence threshold"
    - "Examples show both direct-answer and pass-through guidance"
