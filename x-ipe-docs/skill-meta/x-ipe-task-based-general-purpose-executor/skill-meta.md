# ═══════════════════════════════════════════════════════════
# SKILL META - Task-Based
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-task-based-general-purpose-executor
skill_type: x-ipe-task-based
version: "1.0.0"
status: candidate
created: 2026-04-07
updated: 2026-04-07

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  A general-purpose task executor that follows execution instructions to accomplish a goal,
  using knowledge base references (user manuals) for guidance via x-ipe-tool-user-manual-referencer.
  Asks human for feedback when instructions are unclear.

triggers:
  - "execute task"
  - "follow instructions"
  - "run instructions"
  - "general purpose executor"

not_for:
  - "x-ipe-task-based-code-implementation: When specifically implementing code features"
  - "x-ipe-task-based-bug-fix: When fixing bugs"

# ─────────────────────────────────────────────────────────────
# WORKFLOW POSITION
# ─────────────────────────────────────────────────────────────
workflow:
  category: standalone
  phase: null
  next_task_based_skill: null
  human_review: true

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: interaction_mode
      type: string
      default: "interact-with-human"
      description: "Interaction mode"

    - name: goal
      type: string
      description: "What the executor should accomplish"

    - name: execution_instructions
      type: string
      description: "Step-by-step or high-level instructions to follow"

    - name: kb_reference
      type: object
      description: "Knowledge base reference with path and manual_name"

  optional:
    - name: kb_reference.manual_name
      type: string
      default: null
      description: "Name of the user manual to reference"

outputs:
  state:
    - name: status
      value: completed | blocked

  data:
    - name: step_results
      type: array
      description: "Per-step execution results with status"

    - name: manual_references_used
      type: array
      description: "List of manual sections consulted during execution"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
      test: file_exists + yaml_parse
      expected: "name starts with 'x-ipe-task-based-'"

    - id: AC-S02
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: "< 500"

    - id: AC-B01
      category: behavior
      criterion: Executor calls user-manual-referencer when step references manual
      test: execution
      expected: "referencer invoked with lookup_instruction or get_step_by_step"

    - id: AC-B02
      category: behavior
      criterion: Executor asks human when instructions are unclear (clarity_score < 0.6)
      test: execution
      expected: "Human prompted for feedback when needs_human_feedback=true"

    - id: AC-B03
      category: behavior
      criterion: Executor logs results for each step
      test: execution
      expected: "step_results array contains entry per instruction step"

  should:
    - id: AC-B04
      category: behavior
      criterion: Executor uses troubleshoot operation when step outcome doesn't match
      test: execution
      expected: "troubleshoot called on mismatch"

    - id: AC-B05
      category: behavior
      criterion: Executor resolves kb_reference.path from manual_name
      test: execution
      expected: "Path resolved to x-ipe-docs/knowledge-base/{manual_name}/"

  could:
    - id: AC-B06
      category: behavior
      criterion: Executor uses screenshots from manual as visual reference
      test: execution
      expected: "Screenshot paths extracted and used for UI verification"

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-tool-user-manual-referencer
      relationship: "calls (executor invokes referencer for manual lookups)"
    - name: x-ipe-workflow-task-execution
      relationship: "loaded-by (task execution workflow loads this skill)"

  artifacts:
    - path: "x-ipe-docs/knowledge-base/"
      description: "Knowledge base folder containing user manuals"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Execute with clear manual instructions"
      given: "Goal, instructions, and kb_reference provided. Manual has clear step-by-step."
      when: "Executor runs"
      then: "All steps completed, referencer called for manual lookups, step_results logged"

    - name: "Execute with unclear manual instructions"
      given: "Instructions reference a feature, but manual is vague"
      when: "Executor calls referencer, gets needs_human_feedback=true"
      then: "Executor asks human for feedback before proceeding"

  error_cases:
    - name: "KB path not found"
      given: "kb_reference.path points to non-existent folder"
      when: "Executor tries to load KB"
      then: "Halts with error, asks user for correct path"

    - name: "No matching manual section"
      given: "Instruction references feature not in manual"
      when: "Referencer returns no matches"
      then: "Executor asks human for guidance"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All instruction steps attempted with results logged"
    - "Referencer called for manual-dependent steps"
    - "Human feedback requested when clarity_score < 0.6"
    - "DoD checkpoints verified"
