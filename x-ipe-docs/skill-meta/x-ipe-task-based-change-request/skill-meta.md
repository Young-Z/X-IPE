# ═══════════════════════════════════════════════════════════
# SKILL META - Task-Based: Change Request
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-task-based-change-request
skill_type: x-ipe-task-based
version: "1.1.0"
status: candidate
created: 2026-02-15
updated: 2026-03-04

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Process change requests by analyzing impact on existing requirements and features,
  detecting conflicts with existing specs/designs/code before human approval, and
  routing to the appropriate workflow (Feature Refinement or Requirement Update + Feature Breakdown).

triggers:
  - "change request"
  - "CR"
  - "modify feature"
  - "update requirement"

not_for:
  - "x-ipe-task-based-bug-fix: When the request is about broken existing functionality"
  - "x-ipe-task-based-feature-refinement: When the feature is already identified and needs specification"

# ─────────────────────────────────────────────────────────────
# WORKFLOW POSITION
# ─────────────────────────────────────────────────────────────
workflow:
  category: standalone
  phase: null
  next_task_based_skill: "x-ipe-task-based-feature-refinement | x-ipe-task-based-feature-breakdown"
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

    - name: change_request_description
      type: string
      description: "Description of the requested change"

    - name: business_justification
      type: string
      description: "Why this change is needed"

  optional:
    - name: requestor
      type: string
      default: null
      description: "Name/role of person requesting the change"

    - name: priority
      type: string
      default: "medium"
      description: "Priority level: high, medium, low"

outputs:
  state:
    - name: category
      value: standalone
    - name: status
      value: completed | blocked
    - name: next_task_based_skill
      value: "x-ipe-task-based-feature-refinement | x-ipe-task-based-feature-breakdown"
    - name: require_human_review
      value: yes
    - name: auto_proceed
      value: "${inputs.auto_proceed}"

  artifacts:
    - name: cr_document
      type: file
      path: "x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md"
      description: "Change request document"

  data:
    - name: cr_classification
      type: string
      description: "modification | new_feature"
    - name: conflicts_found
      type: array
      description: "List of conflicts identified during conflict analysis"

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
      criterion: references/examples.md exists
      test: file_exists
      expected: file contains at least 1 example

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    - id: AC-C01
      category: content
      criterion: All required sections present in order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, Input Parameters,
         Input Initialization, Definition of Ready, Execution Flow,
         Execution Procedure, Output Result, Definition of Done,
         Patterns & Anti-Patterns, Examples]

    - id: AC-C02
      category: content
      criterion: Conflict Analysis step exists between Classify and Human Approval
      test: section_parse
      expected: step_4 named "Conflict Analysis" with sub-agent conflict detection

    - id: AC-C03
      category: content
      criterion: Conflict Analysis uses sub-agent pattern from bug-fix skill
      test: content_check
      expected: Conflict Detector sub-agent analyzes specs, designs, dependencies

    - id: AC-C04
      category: content
      criterion: Human Approval step includes conflict analysis results
      test: content_check
      expected: step_5 presents conflicts alongside classification

    - id: AC-B01
      category: behavior
      criterion: Skill produces expected outputs including conflicts_found
      test: execution
      expected: all outputs.artifacts exist, conflicts_found in output YAML

    - id: AC-B02
      category: behavior
      criterion: Output YAML has correct structure with conflicts_found
      test: yaml_validate
      expected: category is first field, conflicts_found field present

  should:
    - id: AC-C05
      category: content
      criterion: CR template includes Conflict Analysis section
      test: content_check
      expected: templates/change-request.md has Conflict Analysis section

    - id: AC-C06
      category: content
      criterion: DoD includes conflict analysis checkpoint
      test: section_parse
      expected: DoD has "Conflict analysis completed" checkpoint

    - id: AC-C07
      category: content
      criterion: Anti-patterns include "Skip conflict analysis"
      test: table_parse
      expected: Anti-pattern table has row for skipping conflict analysis

    - id: AC-B03
      category: behavior
      criterion: BLOCKING gate prevents proceeding past Step 4 with unresolved conflicts
      test: execution
      expected: skill blocks when unexpected conflicts unresolved

  could:
    - id: AC-C08
      category: content
      criterion: Examples include conflict analysis scenario
      test: content_check
      expected: At least one example shows conflict detection

  wont:
    - id: AC-W01
      criterion: Board status updates
      reason: Handled by category skill, not task-based skill

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-workflow-task-execution
      relationship: prerequisite
      description: Must be learned before executing this skill

  artifacts:
    - path: "x-ipe-docs/requirements/requirement-details.md"
      description: "Must exist with current project requirements"
    - path: "x-ipe-docs/planning/features.md"
      description: "Must exist with current feature list"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "CR with no conflicts"
      given: "CR modifies feature with no dependencies"
      when: "Conflict analysis runs"
      then: "Empty conflicts list, proceed to human approval"

    - name: "CR with expected conflicts"
      given: "CR modifies feature used by another feature"
      when: "Conflict analysis detects spec overlap"
      then: "Conflicts classified as expected, included in human approval"

  edge_cases:
    - name: "CR with unexpected conflicts"
      given: "CR modifies shared data model"
      when: "Conflict analysis finds breaking changes"
      then: "Unexpected conflicts documented, mitigation strategies suggested"

  error_cases:
    - name: "Related specs missing"
      given: "Feature referenced but no specification exists"
      when: "Conflict analysis attempts to read specs"
      then: "Note missing specs, warn in approval presentation"

  blocking:
    - name: "Unresolved unexpected conflicts"
      given: "Unexpected conflicts found"
      when: "Attempt to proceed past Step 4"
      then: "BLOCKED - must resolve or document before human approval"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "Conflict Analysis step exists as Step 4"
    - "BLOCKING gate on Step 4 before Step 5"
    - "Output YAML includes conflicts_found field"
    - "DoD includes conflict analysis checkpoint"

  judge_agent:
    - criterion: "Conflict analysis is thorough and catches specification/design/dependency conflicts"
      rubric: |
        5: Excellent - catches all conflict types, clear mitigations
        4: Good - catches most conflicts, minor gaps
        3: Acceptable - catches obvious conflicts
        2: Poor - misses important conflict categories
        1: Fail - no meaningful conflict detection
