# Validation Loop Heuristics

> Reference for Phase 3 (慎思之 — Think Carefully) validation and re-extraction logic.

---

## Acceptance Criteria Loading

```
Input: tool_skill_artifacts.acceptance_criteria (file path from Phase 1)

Expected format (markdown with structured sections):
  ## Section: Overview
  - [AC-UM-01] Describes what the application does and its purpose
  - [AC-UM-02] Identifies target users and use cases

  ## Section: Installation
  - [AC-UM-04] Lists all prerequisites and system requirements
  - [AC-UM-05] Provides step-by-step installation instructions

Parsing rules:
  - Each H2 heading maps to a collection template section (by slug match)
  - Each list item = one criterion with ID prefix [AC-XXX]
  - Criteria without section mapping → apply to all sections (global)
  - No criteria for a section → implicitly "accepted" (warn in manifest)
```

---

## Section Validation Dispatch

```
For each non-accepted section:
  1. Read content file: {checkpoint_path}/content/section-{NN}-{slug}.md
  2. Read relevant criteria from acceptance_criteria (matched by section slug)
  3. Evaluate each criterion against content:
     - Does content address the criterion's requirement?
     - Is the depth sufficient (detailed explanation vs surface mention)?
     - Is the breadth adequate (all sub-topics covered)?
  4. Return per-criterion: pass | fail
  5. Compute section_status:
     - All criteria pass → "accepted"
     - Any criteria fail → "needs-more-info"
     - Content file missing/empty → "error"
```

---

## Gap Classification

```
For each failing criterion, classify the gap:

DEPTH gap (content exists but too shallow):
  Keywords in feedback: "too brief", "lacks detail", "surface-level",
    "needs more explanation", "missing examples", "vague"
  Action: Re-extract with detail-augmented prompts
    → Prepend to extraction prompt: "Provide detailed, step-by-step information.
       Include specific examples, configuration values, and edge cases."

BREADTH gap (content misses required topics):
  Keywords in feedback: "missing", "not covered", "absent",
    "no mention of", "lacks coverage", "topic not found"
  Action: Re-extract with scope-expanded prompts
    → Prepend to extraction prompt: "Expand scope to cover: {missing_topics}.
       Look in additional files, pages, or documentation sources."

DEFAULT: If classification is ambiguous → treat as depth gap.
```

---

## Feedback File Format

```markdown
# Validation Feedback: {Section Title}

<!-- Iteration: {M} | Section: {N} | Date: {ISO 8601} -->

## Criteria Results

| Criterion ID | Description | Result | Gap Type |
|-------------|-------------|--------|----------|
| AC-UM-01 | Describes app purpose | pass | — |
| AC-UM-02 | Target users identified | fail | breadth |
| AC-UM-03 | Version info included | fail | depth |

## Coverage

- Criteria met: 1/3 (33.3%)
- Section status: needs-more-info

## Suggested Improvements

- **AC-UM-02 (breadth):** Content does not mention target users.
  Look for: about page, README intro, marketing materials.
- **AC-UM-03 (depth):** Version mentioned but no compatibility info.
  Add: supported platforms, minimum requirements, dependency versions.
```

Location: `{checkpoint_path}/feedback/section-{NN}-{slug}-iter-{M}.md`

---

## Re-extraction Strategy

```
After gap classification:
  1. Collect all failing sections with their gap classifications
  2. For each failing section:
     a. Read original extraction prompt from collection template
     b. Augment prompt based on gap type (see Gap Classification above)
     c. Re-invoke Phase 2 Step 2.1 extraction for THIS SECTION ONLY
     d. Overwrite the content file: content/section-{NN}-{slug}.md
     e. Update manifest section entry with new timestamps
  3. Proceed to next validation iteration
```

---

## Exit Conditions (Evaluation Order)

```
After each iteration, evaluate in order:

1. ALL_CRITERIA_MET:
   Every section has validation_status == "accepted"
   → phase_3.status = "validated", exit_reason = "all_criteria_met"

2. MAX_ITERATIONS_REACHED:
   iteration_count >= config_overrides.max_validation_iterations
   → phase_3.status = "validated" (partial), exit_reason = "max_iterations_reached"

3. PLATEAU_DETECTED:
   coverage_ratio[current] <= coverage_ratio[previous] AND iteration > 1
   → phase_3.status = "validated" (partial), exit_reason = "plateau_detected"

4. NO_CONTENT:
   Zero content files from Phase 2
   → phase_3.status = "skipped", exit_reason = "no_content_to_validate"
```

---

## Coverage Computation

```
coverage_ratio = criteria_met / total_criteria

Where:
  criteria_met = sum of passed criteria across ALL sections
  total_criteria = sum of ALL applicable criteria across ALL sections

Per-section coverage:
  section_coverage = section_criteria_met / section_total_criteria

Coverage history:
  coverage_history = [0.45, 0.72, 0.85]  # one entry per iteration
```

---

## Manifest Updates (Phase 3)

```yaml
# Phase 3 additions to manifest.yaml
phase_3:
  status: "validated | skipped"  # from "in_progress" → "validated"
  started_at: "ISO 8601"
  completed_at: "ISO 8601"
  exit_reason: "all_criteria_met | max_iterations_reached | plateau_detected | no_content_to_validate"
  iteration_count: int
  final_coverage_ratio: float  # 0.0 - 1.0
  coverage_target: float  # from config_overrides
  coverage_history: [float]  # one per iteration
  sections_accepted: int
  sections_needs_more_info: int
  sections_error: int
  per_section:
    - section_id: 1
      slug: "overview"
      validation_status: "accepted | needs-more-info | error"
      criteria_met: 3
      criteria_total: 3
      iterations_validated: 2  # how many times this section was validated
      feedback_files: ["feedback/section-01-overview-iter-1.md"]
```

---

## Edge Cases

| Edge Case | Behavior |
|-----------|----------|
| Tool skill has no acceptance criteria | Skip Phase 3, mark "skipped", warn |
| Section has no matching criteria | Implicitly "accepted", warn in manifest |
| Phase 2 produced zero sections | Skip Phase 3, exit "no_content_to_validate" |
| All sections accepted on iteration 1 | Exit immediately, 1 iteration only |
| Coverage worsens after re-extraction | Plateau detected → exit early |
| Re-extraction produces empty content | Mark section "error", continue others |
| Iteration config = 0 | Clamp to 1 (minimum 1 iteration) |
| Coverage target = 0 | All sections accepted on first iteration |
