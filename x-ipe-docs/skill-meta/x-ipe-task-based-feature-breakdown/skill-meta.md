# ═══════════════════════════════════════════════════════════
# SKILL META - Task-Based: Feature Breakdown (v3)
# ═══════════════════════════════════════════════════════════

skill_name: x-ipe-task-based-feature-breakdown
skill_type: x-ipe-task-based
version: "3.0.0"
status: candidate
created: 2026-02-11
updated: 2026-03-05

summary: |
  Breaks requirements into Epics and features. Assesses scope to determine Epic grouping, then breaks each Epic into features with MVP-first criteria. Tracks on feature board and verifies no parent-child duplication after splitting.

triggers:
  - "break down features"
  - "split into features"
  - "create feature list"
  - "organize epics"

not_for:
  - "x-ipe-task-based-feature-refinement: Use for detailing individual feature specs"
  - "x-ipe-task-based-requirement-gathering: Use for gathering requirements before breakdown"

changes:
  - type: added
    description: "Step 2 'Assess Epic Granularity' — evaluates scope signals (feature count, domain diversity, dependency clusters, team boundaries) to determine single vs multi-Epic grouping"
  - type: added
    description: "Epic grouping decision matrix in references/breakdown-guidelines.md"
  - type: modified
    description: "Steps 2-9 renumbered to 3-10 to accommodate new Step 2"
  - type: modified
    description: "Steps 3-4 (Evaluate Complexity, Identify Features) now operate per-Epic"
  - type: added
    description: "Output Result includes epic_ids and epic_count"
  - type: added
    description: "DoD checkpoint for Epic structure assessment"
  - type: added
    description: "Anti-patterns: 'Skipping Epic assessment', 'All features in one Epic'"
  - type: modified
    description: "Patterns moved to references/patterns.md to stay under 500 lines"

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
      expected: Purpose, Important Notes, Input Parameters, Input Initialization, DoR, Execution Flow, Execution Procedure, Output Result, DoD, Patterns, Examples

    - id: AC-C02
      category: content
      criterion: Execution Flow table has 10 steps (Analyze through Complete)
      test: table_parse
      expected: 10 rows including new Epic Assessment step

    - id: AC-C03
      category: content
      criterion: Step 2 assesses Epic granularity with scope signals
      test: content_check
      expected: step_2 evaluates feature count, domain diversity, dependency clusters, team boundaries

    - id: AC-C04
      category: content
      criterion: Step 2 applies Epic grouping decision matrix
      test: content_check
      expected: step_2 references decision matrix with thresholds (≤7 features, 2-3 domains, etc.)

    - id: AC-C05
      category: content
      criterion: Steps 3-4 operate per-Epic
      test: content_check
      expected: step_3 and step_4 contain "per Epic" or "For each Epic" language

    - id: AC-C06
      category: content
      criterion: Output Result includes epic_ids and epic_count
      test: content_check
      expected: task_completion_output YAML has epic_ids array and epic_count field

    - id: AC-C07
      category: content
      criterion: DoD has checkpoint for Epic structure assessment
      test: content_check
      expected: DoD includes Epic assessment checkpoint

    - id: AC-C08
      category: content
      criterion: Step 9 (Dedup) checks parent feature coverage
      test: content_check
      expected: step_9 compares parent FRs/ACs against sub-feature coverage

    - id: AC-B01
      category: behavior
      criterion: When scope is single domain with few features, single Epic created
      test: execution
      expected: step_2 produces single Epic when ≤7 features in 1 domain

    - id: AC-B02
      category: behavior
      criterion: When scope spans multiple domains, multiple Epics created
      test: execution
      expected: step_2 produces multiple Epics when 2+ domains with 8+ features

  should:
    - id: AC-C09
      category: content
      criterion: Anti-patterns include "Skipping Epic assessment" and "All features in one Epic"
      test: table_parse
      expected: anti-pattern table includes both rows

    - id: AC-C10
      category: content
      criterion: Examples include multi-Epic breakdown scenario
      test: content_check
      expected: examples.md has at least 1 multi-Epic example

    - id: AC-C11
      category: content
      criterion: references/breakdown-guidelines.md has Epic grouping decision matrix
      test: content_check
      expected: decision matrix table with domain/feature count thresholds

    - id: AC-C12
      category: content
      criterion: Input Initialization subsection present under Input Parameters
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

    - id: AC-C13
      category: content
      criterion: references/patterns.md has Epic Grouping pattern
      test: content_check
      expected: pattern for single vs multi-Epic decision

test_scenarios:
  happy_path:
    - name: "Multi-domain requirement → multiple Epics created"
      given: "Requirements span 3 domains with ~12 features estimated"
      when: "Step 2 assesses Epic granularity"
      then: "3 Epics created, one per domain, with Epic-level dependencies documented"

    - name: "Single-domain requirement → single Epic created"
      given: "Requirements cover 1 domain with ~5 features estimated"
      when: "Step 2 assesses Epic granularity"
      then: "1 Epic created, proceeds to per-Epic feature breakdown"

    - name: "Feature split with full coverage — parent removed"
      given: "FEATURE-001 split into FEATURE-001-A, B, C covering all FRs"
      when: "Dedup step compares coverage"
      then: "Parent FEATURE-001 removed from board and requirement-details"

  edge_cases:
    - name: "Borderline scope — 2 domains with 7 features"
      given: "Requirements have 2 domains but only 7 total features"
      when: "Step 2 assesses Epic granularity"
      then: "Single Epic chosen (≤7 features despite 2 domains)"

    - name: "Partial coverage — parent kept"
      given: "FEATURE-001 split into A and B, but 2 FRs not covered"
      when: "Dedup step compares"
      then: "Parent kept with note about uncovered FRs, gap flagged"

  blocking:
    - name: "Epic structure must precede feature identification"
      given: "Requirements analyzed"
      when: "Agent attempts to identify features before Epic assessment"
      then: "BLOCKED — Step 2 must complete before Step 4"

    - name: "Must use feature-board-management for removal"
      given: "Parent needs removal"
      when: "Agent attempts to edit features.md directly"
      then: "BLOCKED — must use feature-board-management skill"

evaluation:
  self_check:
    - "SKILL.md < 500 lines"
    - "10 steps in execution flow"
    - "Step 2 has Epic granularity assessment with decision matrix"
    - "Steps 3-4 operate per-Epic"
    - "Output Result includes epic_ids and epic_count"
    - "DoD includes Epic assessment checkpoint"
    - "Step 9 has coverage comparison logic"
    - "Anti-patterns include 'Skipping Epic assessment'"
