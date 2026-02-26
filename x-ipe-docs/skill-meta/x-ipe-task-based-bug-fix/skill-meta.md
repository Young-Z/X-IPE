# ═══════════════════════════════════════════════════════════
# SKILL META - Task-Based: Bug Fix
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-task-based-bug-fix
skill_type: x-ipe-task-based
version: "1.1.0"
status: candidate
created: 2026-02-24
updated: 2026-02-24

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Systematically diagnose, fix, and verify bug resolutions with conflict pre-check
  to ensure fixes don't introduce unexpected behavioral changes.

triggers:
  - "fix bug"
  - "something is broken"
  - "not working"

not_for:
  - "x-ipe-task-based-code-refactor: When restructuring code without fixing a bug"
  - "x-ipe-task-based-change-request: When modifying behavior intentionally"

# ─────────────────────────────────────────────────────────────
# CHANGE DESCRIPTION (v1.0.0 → v1.1.0)
# ─────────────────────────────────────────────────────────────
change_description: |
  Add "Conflict Analysis" step between Design Fix (Step 4) and Write Test (new Step 6).
  New Step 5 uses two sub-agents:
    1. Conflict Detector: Analyzes proposed fix against existing codebase logic, lists conflicts
    2. Conflict Validator: Checks if each conflict is expected from user's original request
  If unexpected conflicts exist, asks user to confirm or clarify before proceeding.
  This prevents fixes from silently breaking existing behavior.

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
    - name: auto_proceed
      type: boolean
      default: false
      description: Whether to auto-proceed to next task

    - name: bug_description
      type: string
      description: Description of the bug

    - name: expected_behavior
      type: string
      description: What should happen

    - name: actual_behavior
      type: string
      description: What actually happens

  optional:
    - name: reproduction_steps
      type: string
      default: null
      description: Steps to reproduce the bug

    - name: environment_info
      type: string
      default: null
      description: Environment details if relevant

    - name: program_type
      type: string
      default: null
      description: "frontend | backend | fullstack | cli | library | skills | mcp"

    - name: tech_stack
      type: array
      default: []
      description: e.g. ["Python/Flask", "JavaScript/Vanilla"]

outputs:
  state:
    - name: category
      value: standalone
    - name: status
      value: completed | blocked
    - name: next_task_based_skill
      value: null
    - name: require_human_review
      value: yes

  artifacts:
    - name: fixed_source_file
      type: file
      path: "{path to fixed source file}"
      description: The source file with the bug fix applied

    - name: test_file
      type: file
      path: "{path to test file}"
      description: Test file with bug-reproducing test case

  data:
    - name: bug_severity
      type: string
      description: "Critical | High | Medium | Low"
    - name: root_cause
      type: string
      description: Brief description of root cause
    - name: conflicts_found
      type: array
      description: List of conflicts identified during analysis (empty if none)

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
      test: file_exists + yaml_parse
      expected: name and description fields present

    - id: AC-S02
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    - id: AC-C01
      category: content
      criterion: Execution Flow table has 8 steps (was 7)
      test: table_parse
      expected: 8 rows in Execution Flow table

    - id: AC-C02
      category: content
      criterion: Step 5 is named "Conflict Analysis"
      test: content_check
      expected: step_5 contains "Conflict Analysis"

    - id: AC-C03
      category: content
      criterion: Conflict Analysis step uses two sub-agents
      test: content_check
      expected: References "Conflict Detector" and "Conflict Validator" sub-agents

    - id: AC-C04
      category: content
      criterion: Unexpected conflicts trigger user confirmation
      test: content_check
      expected: Contains "ask user" or "check with user" for unexpected conflicts

    - id: AC-C05
      category: content
      criterion: BLOCKING rule prevents skipping unresolved conflicts
      test: content_check
      expected: BLOCKING constraint on Step 5 about unresolved conflicts

    - id: AC-C06
      category: content
      criterion: Steps after Conflict Analysis correctly renumbered
      test: content_check
      expected: Write Test=Step 6, Implement=Step 7, Verify=Step 8

    - id: AC-C07
      category: content
      criterion: DoD includes conflict analysis checkpoint
      test: content_check
      expected: DoD has checkpoint for conflicts resolved

    - id: AC-B01
      category: behavior
      criterion: No-conflict path proceeds directly to Write Test
      test: execution
      expected: When no conflicts, flow goes Step 4 → Step 5 (no conflicts) → Step 6

    - id: AC-B02
      category: behavior
      criterion: Expected-conflict path proceeds without user prompt
      test: execution
      expected: When all conflicts expected, flow continues without asking user

    - id: AC-B03
      category: behavior
      criterion: Unexpected-conflict path asks user
      test: execution
      expected: When unexpected conflicts found, user is asked to confirm or clarify

  should:
    - id: AC-S03
      category: structure
      criterion: Conflict analysis pattern documented in Patterns section
      test: content_check
      expected: Pattern for conflict analysis exists

    - id: AC-C08
      category: content
      criterion: Anti-pattern for skipping conflict check
      test: table_parse
      expected: Anti-pattern entry about fixing without checking conflicts

    - id: AC-C09
      category: content
      criterion: Example updated to show conflict analysis step
      test: content_check
      expected: Example includes Step 5 conflict analysis

  could:
    - id: AC-C10
      category: content
      criterion: Conflict severity classification guidance
      test: content_check
      expected: Guidance on classifying conflict severity

  wont:
    - id: AC-W01
      criterion: Automated conflict detection tooling
      reason: Agent uses code analysis, not specialized tools

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: Bug fix with no conflicts
      given: Simple off-by-one bug in isolated function
      when: Conflict Detector analyzes fix
      then: No conflicts found, proceeds to Write Test

    - name: Bug fix with expected conflicts
      given: Bug fix changes comparison operator, user explicitly requested this change
      when: Conflict Validator checks against user request
      then: All conflicts classified as "expected", proceeds without user prompt

  edge_cases:
    - name: Bug fix with mix of expected and unexpected conflicts
      given: Fix changes multiple behaviors, some requested, some not
      when: Conflict Validator classifies each
      then: Only unexpected ones presented to user for confirmation

  error_cases:
    - name: User rejects unexpected conflict
      given: Fix would break guest login, user didn't intend this
      when: User says "no, guest login should still work"
      then: Returns to Design Fix step with updated understanding

  blocking:
    - name: Cannot skip conflict analysis
      given: Fix designed but conflicts not checked
      when: Attempt to proceed to Write Test
      then: BLOCKED — must complete conflict analysis first

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "Step 5 exists as Conflict Analysis"
    - "Two sub-agent roles defined: Conflict Detector, Conflict Validator"
    - "BLOCKING constraint prevents skipping"
    - "User prompt on unexpected conflicts"
    - "DoD checkpoint for conflict resolution"

  judge_agent:
    - criterion: "Conflict Analysis step is clear and actionable"
      rubric: |
        5: Excellent - clear sub-agent roles, all paths handled
        4: Good - minor clarity improvements needed
        3: Acceptable - some gaps in conflict handling
        2: Poor - significant logic gaps
        1: Fail - step is unclear or missing key paths
