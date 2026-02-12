# ═══════════════════════════════════════════════════════════
# SKILL META - Task-Based: Requirement Gathering (v2)
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-task-based-requirement-gathering
skill_type: x-ipe-task-based
version: "2.0.0"
status: candidate
created: 2026-02-11
updated: 2026-02-11

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Gathers requirements from user requests, checks for conflicts/overlaps with existing features, updates impacted features, and creates requirement detail documents.

triggers:
  - "new feature"
  - "add feature"
  - "I want to build"
  - "create requirement"
  - "gather requirements"

not_for:
  - "x-ipe-task-based-feature-breakdown: Use for splitting requirements into features"
  - "x-ipe-task-based-change-request: Use when modifying an already-specified feature"

# ─────────────────────────────────────────────────────────────
# CHANGE LOG (v1 → v2)
# ─────────────────────────────────────────────────────────────
changes:
  - type: added
    description: "Step 3 'Conflict & Overlap Review' — scans existing requirement-details for conflicting/overlapping features before documenting new requirements"
  - type: added
    description: "Step 4 'Update Impacted Features' — marks impacted features in requirement-details with CR notes and flags for specification refactoring"
  - type: modified
    description: "Steps 3-5 renumbered to 5-7 to accommodate new steps"
  - type: added
    description: "New DoD checkpoints for conflict review and impact update verification"

# ─────────────────────────────────────────────────────────────
# WORKFLOW POSITION
# ─────────────────────────────────────────────────────────────
workflow:
  category: requirement-stage
  phase: "Requirements"
  next_task_based_skill: "Feature Breakdown"
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

    - name: mockup_list
      type: array
      default: null
      description: "List of mockups from ideation, each with mockup_name and mockup_link"

  optional:
    - name: idea_summary_path
      type: string
      default: null
      description: "Path to idea summary from ideation stage"

outputs:
  state:
    - name: category
      value: requirement-stage
    - name: status
      value: completed | blocked
    - name: next_task_based_skill
      value: Feature Breakdown
    - name: require_human_review
      value: true
    - name: auto_proceed
      value: "${inputs.auto_proceed}"

  artifacts:
    - name: requirement_details
      type: file
      path: "x-ipe-docs/requirements/requirement-details-part-{N}.md"
      description: "Requirement details document with new feature requirements"

    - name: impacted_features_log
      type: embedded
      path: "within requirement-details files"
      description: "CR markers added to impacted features in existing requirement-details files"

  data:
    - name: conflict_review_result
      type: object
      description: "Summary of conflicts/overlaps found and human decisions (CR vs new feature)"
    - name: impacted_features
      type: array
      description: "List of feature IDs that were marked as impacted"
    - name: requirement_details_part
      type: number
      description: "Current active part number"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter (name + description with triggers)
      test: file_exists + yaml_parse
      expected: name and description fields present

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists with at least 1 example
      test: file_exists
      expected: file contains at least 1 example

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    - id: AC-C01
      category: content
      criterion: All required sections present in cognitive flow order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, Input Parameters, 
         Definition of Ready, Execution Flow, Execution Procedure, 
         Output Result, Definition of Done, Patterns & Anti-Patterns, Examples]

    - id: AC-C02
      category: content
      criterion: Execution Flow table has 7 steps (Understand, Clarify, Conflict Review, Update Impacted, Check File, Document, Complete)
      test: table_parse
      expected: 7 rows in execution flow table

    - id: AC-C03
      category: content
      criterion: Step 3 (Conflict Review) scans ALL existing requirement-details files for overlapping features
      test: content_check
      expected: step_3 action includes scanning requirement-details files and comparing with new requirements

    - id: AC-C04
      category: content
      criterion: Step 3 asks human to confirm CR vs new feature with recommendation
      test: content_check
      expected: step_3 action includes asking human with recommendation based on principles

    - id: AC-C05
      category: content
      criterion: Step 4 (Update Impacted Features) marks changes in affected requirement-details files
      test: content_check
      expected: step_4 action includes adding CR markers and notes for spec refactoring

    - id: AC-C06
      category: content
      criterion: DoD has checkpoints for conflict review and impact update
      test: table_parse
      expected: DoD includes conflict_review_completed and impacted_features_updated checkpoints

    - id: AC-B01
      category: behavior
      criterion: When conflicts found, skill blocks until human decides CR vs new feature
      test: execution
      expected: BLOCKING constraint in step_3 prevents proceeding without human decision

    - id: AC-B02
      category: behavior
      criterion: When no conflicts found, steps 3-4 complete quickly without blocking
      test: execution
      expected: step_3 outputs "no conflicts" and step_4 is skipped

  should:
    - id: AC-C07
      category: content
      criterion: Conflict review provides principle-based recommendation (single responsibility, cohesion, minimal coupling)
      test: content_check
      expected: recommendation guidelines reference feature management principles

    - id: AC-C08
      category: content
      criterion: Impact markers use consistent format (e.g., `<!-- CR-IMPACT: ... -->` or similar)
      test: content_check
      expected: defined marker format for impacted features

    - id: AC-C09
      category: content
      criterion: Anti-patterns include "skipping conflict review" scenario
      test: table_parse
      expected: anti-pattern table includes conflict-skipping row

  could:
    - id: AC-C10
      category: content
      criterion: Conflict review generates a summary table of all overlaps found
      test: content_check
      expected: structured output format for conflict findings

  wont:
    - id: AC-W01
      criterion: Automatic conflict resolution without human input
      reason: Human judgment required for CR vs new feature decisions

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-workflow-task-execution
      relationship: prerequisite
      description: Must be learned before executing this skill

  artifacts:
    - path: "x-ipe-docs/requirements/requirement-details*.md"
      description: "Existing requirement details files to scan for conflicts"
    - path: "x-ipe-docs/requirements/requirement-details-index.md"
      description: "Index of all requirement parts"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "New feature with no conflicts"
      given: "User requests new feature, no overlaps with existing features"
      when: "Skill scans existing requirements"
      then: "Step 3 reports no conflicts, Step 4 skipped, proceeds to document"

    - name: "New feature with overlapping feature found"
      given: "User requests feature that overlaps FEATURE-005 (Console)"
      when: "Skill scans and finds overlap"
      then: "Presents overlap to human with CR recommendation, human decides, impacted features marked"

  edge_cases:
    - name: "Multiple overlapping features"
      given: "New requirement overlaps 3 existing features"
      when: "Skill scans"
      then: "All 3 presented to human, each decided independently"

    - name: "Partial overlap - some FRs conflict, some don't"
      given: "New feature has 5 FRs, 2 overlap with existing"
      when: "Skill identifies partial overlap"
      then: "Only overlapping FRs flagged, recommendation distinguishes partial vs full overlap"

  error_cases:
    - name: "No existing requirement files"
      given: "First-time requirement gathering, no existing files"
      when: "Skill attempts scan"
      then: "Reports no existing requirements, skips conflict review"

  blocking:
    - name: "Human must decide on conflict"
      given: "Overlap found with existing feature"
      when: "Agent tries to proceed without human decision"
      then: "BLOCKED until human confirms CR or new feature"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "SKILL.md < 500 lines"
    - "All 7 steps present in execution flow"
    - "Step 3 has BLOCKING constraint for human decision"
    - "Step 4 has clear marker format"
    - "DoD includes conflict and impact checkpoints"

  judge_agent:
    - criterion: "Conflict review step is clear, actionable, and principle-based"
      rubric: |
        5: Excellent - clear scan procedure, principle-based recommendation, structured output
        4: Good - scan and recommendation present but could be clearer
        3: Acceptable - basic conflict check present
        2: Poor - vague conflict handling
        1: Fail - no conflict review
