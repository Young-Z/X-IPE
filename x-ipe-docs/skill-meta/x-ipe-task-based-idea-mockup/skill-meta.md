# ═══════════════════════════════════════════════════════════
# SKILL META - Task-Based
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-task-based-idea-mockup
skill_type: x-ipe-task-based
version: "1.1.0"
status: candidate
created: 2026-02-20
updated: 2026-02-20

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Create visual mockups and prototypes for refined ideas, updating the existing idea-summary in-place with mockup links.

triggers:
  - "create mockup"
  - "visualize idea"
  - "prototype UI"
  - "design mockup"

not_for:
  - "x-ipe-task-based-ideation-v2: Use for refining ideas through brainstorming"
  - "x-ipe-task-based-requirement-gathering: Use for gathering requirements"

# ─────────────────────────────────────────────────────────────
# CHANGE LOG (v1.1.0)
# ─────────────────────────────────────────────────────────────
# - Step 9: Changed from "create new version idea-summary-v{N+1}.md"
#   to "update existing idea-summary-vN.md in-place"
# - Removed constraint "Do NOT modify existing idea-summary files"
# - Added constraint "Update the existing idea-summary file in-place"
# - Updated DoD checkpoint "Summary Updated" to verify in-place update
# - Updated Output Result: idea_summary_version from "v{N+1}" to "vN"
# - Updated references/examples.md to reflect in-place update
# - Updated references/mockup-guidelines.md summary update template

# ─────────────────────────────────────────────────────────────
# WORKFLOW POSITION
# ─────────────────────────────────────────────────────────────
workflow:
  category: ideation-stage
  phase: "mockup"
  next_task_based_skill: "Requirement Gathering"
  human_review: true

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (focused on v1.1.0 change)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-B01
      category: behavior
      criterion: Step 9 instructs to update existing idea-summary in-place
      test: content_check
      expected: SKILL.md Step 9 contains "Update the existing" and "in-place"

    - id: AC-B02
      category: behavior
      criterion: No references to creating new version v{N+1} remain
      test: content_check
      expected: No occurrence of "v{N+1}" in SKILL.md, examples.md, mockup-guidelines.md

    - id: AC-B03
      category: behavior
      criterion: DoD checkpoint reflects in-place update
      test: content_check
      expected: "Summary Updated" checkpoint says "in-place" not "created"

    - id: AC-S01
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

  should:
    - id: AC-C01
      category: content
      criterion: Examples reflect in-place update pattern
      test: content_check
      expected: examples.md shows updating existing file, not creating v2

    - id: AC-C05
      category: content
      criterion: Input Initialization subsection present under Input Parameters
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"
