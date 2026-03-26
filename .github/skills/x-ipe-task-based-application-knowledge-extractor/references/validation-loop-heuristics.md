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
    - section_id: "1-overview"
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

---

## Walkthrough Testing (Phase 3.5)

> Reference for Phase 3.5 (实践验证 — Validate by Practice) walkthrough-based validation.
> This phase validates that extracted content is literally followable by testing it against the running application.

### Applicability

```
ONLY for input types with Chrome DevTools access:
  - running_web_app → LIVE walkthrough via Chrome DevTools
  - public_url → LIVE walkthrough via Chrome DevTools
  - source_code_repo → SKIP (use tool skill test_walkthrough in offline mode)
  - documentation_folder → SKIP
  - single_file → SKIP
```

### Walkthrough Gap Classification

```
For each step that fails during walkthrough, classify the gap:

MISSING_ACTION:
  The step does not specify what physical action to take.
  Examples:
    - "Run the command" (missing: type it and press Enter)
    - "Execute the build" (missing: which button, which terminal, which command)
  Fix: Add explicit action verb + target (e.g., "Press Enter in the terminal to execute")

MISSING_ELEMENT:
  The step references a UI element vaguely or incorrectly.
  Examples:
    - "Click the button" (which button?)
    - "Enter text in the field" (which field?)
  Fix: Name the element exactly as shown in UI (e.g., "Click the 'Create Project' button")

MISSING_OUTCOME:
  The step does not describe what should happen after the action.
  Examples:
    - "Click Submit" (then what?)
    - "Run the test" (what does success look like?)
  Fix: Add expected outcome (e.g., "You should see 'Project created successfully'")

WRONG_STATE:
  The described UI state does not match reality.
  Examples:
    - Step says "Click 'Settings' in the sidebar" but sidebar has no Settings link
    - Step references a form field that no longer exists
  Fix: Re-extract with current UI state via Chrome DevTools

IMPLICIT_KNOWLEDGE:
  The step assumes knowledge that isn't documented elsewhere in the manual.
  Examples:
    - "Open a terminal" (user may not know how)
    - "SSH into the server" (assumes SSH knowledge)
    - "Press Enter" not mentioned after a CLI command is pasted
  Fix: Either document the prerequisite or add inline explanation
```

### Followability Score Computation

```
followability_score = steps_passed / total_steps

Where:
  steps_passed = steps where the walkthrough agent successfully:
    1. Identified what action to take from the text alone
    2. Found the named UI element
    3. Performed the action
    4. Observed the described outcome
  total_steps = all steps in the scenario

Threshold: 0.7 (70% of steps must be followable)
```

### Walkthrough Feedback File Format

```markdown
# Walkthrough Feedback: {Scenario Title}

<!-- Iteration: {M} | Input Type: {input_type} | Date: {ISO 8601} -->

## Results

| Step | Description | Result | Gap Type | Section |
|------|------------|--------|----------|---------|
| 1 | Open the application | pass | — | 03-getting-started |
| 2 | Click 'New Project' | pass | — | 05-workflows |
| 3 | Enter project name | fail | MISSING_ELEMENT | 05-workflows |
| 4 | Run build command | fail | MISSING_ACTION | 05-workflows |

## Summary

- Steps passed: 2/4 (50%)
- Followability score: 0.50
- Gaps by type: MISSING_ELEMENT (1), MISSING_ACTION (1)

## Gap Details

- **Step 3 (MISSING_ELEMENT):** Text says "enter the project name" but doesn't
  specify which field. The form has 3 text inputs. Needs: "In the 'Project Name'
  field (the first text input), type your project name."
- **Step 4 (MISSING_ACTION):** Text says "Run the build command" but doesn't
  mention pressing Enter. The UI pastes a command into the terminal. Needs:
  "Press Enter in the terminal to execute the build command. Wait for
  'Build successful' to appear (about 30 seconds)."
```

Location: `{checkpoint_path}/feedback/walkthrough-{scenario_slug}-iter-{M}.md`

### Manifest Updates (Phase 3.5)

```yaml
# Phase 3.5 additions to manifest.yaml
phase_3_5:
  status: "validated | skipped"
  skip_reason: "offline_input_type | no_scenario_available"  # only if skipped
  started_at: "ISO 8601"
  completed_at: "ISO 8601"
  scenario_used: "section-05-workflows | section-03-getting-started"
  iteration_count: int  # 1 or 2
  followability_score: float  # 0.0 - 1.0
  gaps_found: int
  gaps_fixed: int
  gap_details:
    - step: int
      gap_type: "MISSING_ACTION | MISSING_ELEMENT | MISSING_OUTCOME | WRONG_STATE | IMPLICIT_KNOWLEDGE"
      section_id: "string"
      fixed: bool
  feedback_files: ["feedback/walkthrough-{slug}-iter-1.md"]
```
