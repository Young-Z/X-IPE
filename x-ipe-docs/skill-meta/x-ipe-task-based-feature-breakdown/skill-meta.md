# ═══════════════════════════════════════════════════════════
# SKILL META - Task-Based: Feature Breakdown (v2)
# ═══════════════════════════════════════════════════════════

skill_name: x-ipe-task-based-feature-breakdown
skill_type: x-ipe-task-based
version: "2.0.0"
status: candidate
created: 2026-02-11
updated: 2026-02-11

summary: |
  Breaks requirements into features, tracks them on feature board, and verifies no parent-child duplication after splitting.

triggers:
  - "break down features"
  - "split into features"
  - "create feature list"

not_for:
  - "x-ipe-task-based-feature-refinement: Use for detailing individual feature specs"
  - "x-ipe-task-based-requirement-gathering: Use for gathering requirements before breakdown"

changes:
  - type: added
    description: "Step 8 'Parent Feature Deduplication' — after breakdown, checks if parent feature is fully covered by sub-features and removes it to avoid duplicate tracking"
  - type: modified
    description: "Step 8 (Complete) renumbered to Step 9"
  - type: added
    description: "New DoD checkpoint for parent deduplication verification"

workflow:
  category: requirement-stage
  phase: "Requirements"
  next_task_based_skill: "Feature Refinement"
  human_review: true

acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
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
      expected: Purpose, Important Notes, Input Parameters, DoR, Execution Flow, Execution Procedure, Output Result, DoD, Patterns, Examples

    - id: AC-C02
      category: content
      criterion: Execution Flow table has 9 steps (Analyze through Complete)
      test: table_parse
      expected: 9 rows including new Dedup step

    - id: AC-C03
      category: content
      criterion: Step 8 (Dedup) checks if parent feature is fully covered by sub-features
      test: content_check
      expected: step_8 action compares parent FRs/ACs against union of sub-feature FRs/ACs

    - id: AC-C04
      category: content
      criterion: Step 8 removes parent from feature board and requirement-details if fully covered
      test: content_check
      expected: step_8 action includes removing parent feature via feature-board-management

    - id: AC-C05
      category: content
      criterion: Step 8 keeps parent if sub-features don't fully cover it
      test: content_check
      expected: step_8 has conditional logic for partial coverage (keep parent, flag gap)

    - id: AC-C06
      category: content
      criterion: DoD has checkpoint for parent deduplication
      test: table_parse
      expected: DoD includes dedup_verified checkpoint

    - id: AC-B01
      category: behavior
      criterion: When no splitting occurred, dedup step is skipped
      test: execution
      expected: step_8 has "IF no parent was split" skip condition

  should:
    - id: AC-C07
      category: content
      criterion: Dedup step produces coverage comparison table
      test: content_check
      expected: structured comparison showing parent FRs vs sub-feature coverage

    - id: AC-C08
      category: content
      criterion: Anti-patterns include "keeping duplicate parent feature"
      test: table_parse
      expected: anti-pattern table includes parent-duplication row

    - id: AC-C09
      category: content
      criterion: Examples include dedup scenario
      test: content_check
      expected: examples.md has at least 1 dedup example

test_scenarios:
  happy_path:
    - name: "Feature split with full coverage — parent removed"
      given: "FEATURE-001 split into FEATURE-001-A, B, C covering all FRs"
      when: "Dedup step compares coverage"
      then: "Parent FEATURE-001 removed from board and requirement-details"

    - name: "No splitting occurred — dedup skipped"
      given: "All features identified as single features (no sub-features)"
      when: "Dedup step runs"
      then: "Step skipped entirely"

  edge_cases:
    - name: "Partial coverage — parent kept"
      given: "FEATURE-001 split into A and B, but 2 FRs not covered"
      when: "Dedup step compares"
      then: "Parent kept with note about uncovered FRs, gap flagged"

  blocking:
    - name: "Must use feature-board-management for removal"
      given: "Parent needs removal"
      when: "Agent attempts to edit features.md directly"
      then: "BLOCKED — must use feature-board-management skill"

evaluation:
  self_check:
    - "SKILL.md < 500 lines"
    - "9 steps in execution flow"
    - "Step 8 has coverage comparison logic"
    - "DoD includes dedup checkpoint"
