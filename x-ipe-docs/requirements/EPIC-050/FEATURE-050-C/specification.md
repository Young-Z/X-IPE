# Feature Specification: Extract-Validate Loop & Coverage Control

> Feature ID: FEATURE-050-C
> Epic ID: EPIC-050
> Version: v1.0
> Status: Refined
> Last Updated: 03-17-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-17-2026 | Initial specification |

## Linked Mockups

N/A — this feature has no UI component. It is a pure skill-layer feature.

## Overview

FEATURE-050-C implements Phase 3 (慎思之 — Think Carefully) of the application knowledge extractor skill. Building on the content extraction performed by Phase 2 (FEATURE-050-B), this feature adds the iterative validation loop — sending extracted content to the tool skill for validation against acceptance criteria, assessing coverage gaps, deciding depth vs. breadth adjustments, and re-extracting targeted sections until quality thresholds are met.

This is the quality control phase of EPIC-050. Phase 2 produces raw extracted content (one `section-{N}-{slug}.md` file per collection template section in `.checkpoint/content/`). Phase 3 takes that content, submits each section to the tool skill for validation, computes a coverage ratio (criteria met / total criteria), and iterates with targeted re-extraction when sections fail. The loop exits when all criteria are met, max iterations are reached, or no improvement is detected between iterations.

The feature operates as a closed-loop controller: tool skill feedback drives re-extraction decisions. If a section fails on depth (content too shallow for its acceptance criteria), Phase 3 re-invokes extraction with more detailed prompts. If a section fails on breadth (content misses required topics), Phase 3 re-invokes extraction with wider source scope. All feedback and validation results are persisted to `.checkpoint/feedback/` for traceability.

Target users are AI agents within X-IPE that orchestrate knowledge extraction workflows. This feature ensures extracted knowledge meets tool skill quality standards before downstream processing (FEATURE-050-E: KB Intake Output).

## User Stories

1. As an **AI agent**, I want the extractor to **validate each extracted section against the tool skill's acceptance criteria**, so that **only content meeting quality standards proceeds to output**.

2. As an **AI agent**, I want the extractor to **compute a coverage ratio across all sections and criteria**, so that **I have a quantitative measure of extraction completeness**.

3. As an **AI agent**, I want the extractor to **automatically re-extract sections that fail validation with targeted improvements based on feedback**, so that **quality improves iteratively without manual intervention**.

4. As an **AI agent**, I want the extractor to **distinguish depth failures from breadth failures and adjust extraction strategy accordingly**, so that **re-extraction is efficient — addressing the specific gap type rather than re-doing everything**.

5. As an **AI agent**, I want the extractor to **stop iterating when criteria are met, max iterations are reached, or no improvement is detected**, so that **the loop terminates predictably and doesn't waste resources**.

6. As an **AI agent**, I want the extractor to **persist all validation feedback to checkpoint files**, so that **the validation history is traceable and can inform future iterations or debugging**.

## Acceptance Criteria

### AC-050C-01: Validation Against Criteria

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050C-01a | GIVEN Phase 2 has completed with content files in `.checkpoint/session-{ts}/content/` WHEN Phase 3 begins THEN it reads the tool skill's `acceptance_criteria` artifact and parses per-section criteria into a structured checklist | Unit |
| AC-050C-01b | GIVEN a section content file exists at `content/section-{N}-{slug}.md` AND per-section acceptance criteria are loaded WHEN the extractor validates that section THEN it sends the content file path (not inline text) to the tool skill for validation via the file-based handoff protocol | Integration |
| AC-050C-01c | GIVEN the tool skill validates a section WHEN all acceptance criteria for that section are met THEN it returns `validation_status: "accepted"` with a `quality_score` object containing `ac_pass_rate` and `clarity_score` | Integration |
| AC-050C-01d | GIVEN the tool skill validates a section WHEN one or more acceptance criteria are NOT met THEN it returns `validation_status: "needs-more-info"` with structured feedback specifying which criteria failed and what content is missing or insufficient | Integration |

### AC-050C-02: Coverage Assessment

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050C-02a | GIVEN all sections have been validated in the current iteration WHEN the extractor computes coverage THEN `coverage_ratio` = (number of criteria met across all sections) / (total criteria across all sections) | Unit |
| AC-050C-02b | GIVEN `coverage_ratio` >= `config_overrides.coverage_target` (default 0.8) WHEN the coverage check runs THEN Phase 3 marks overall coverage as "sufficient" and proceeds to exit evaluation | Unit |
| AC-050C-02c | GIVEN `coverage_ratio` < `config_overrides.coverage_target` WHEN the coverage check runs THEN Phase 3 identifies the specific sections and criteria that are failing and classifies each gap as "depth" or "breadth" | Unit |
| AC-050C-02d | GIVEN a section's content exists but fails criteria related to insufficient detail or shallow treatment WHEN the extractor classifies the gap THEN it labels the section as needing "depth" re-extraction (extract more detail from the same sources) | Unit |
| AC-050C-02e | GIVEN a section's content is missing required topics or has no relevant source materials found WHEN the extractor classifies the gap THEN it labels the section as needing "breadth" re-extraction (discover wider file/page scope) | Unit |

### AC-050C-03: Re-extraction Loop

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050C-03a | GIVEN sections are marked for "depth" re-extraction WHEN the extractor re-invokes extraction THEN it calls Phase 2 extraction for only those specific sections with augmented prompts requesting more detailed content from the same source scope | Integration |
| AC-050C-03b | GIVEN sections are marked for "breadth" re-extraction WHEN the extractor re-invokes extraction THEN it calls Phase 2 extraction for those sections with expanded source scope (additional files, sub-pages, or broader directory scanning) | Integration |
| AC-050C-03c | GIVEN a re-extraction iteration completes for targeted sections WHEN the extractor resubmits to the tool skill THEN it sends only the updated section content files for re-validation (sections that passed in previous iterations are NOT re-validated) | Integration |
| AC-050C-03d | GIVEN the current iteration count is N AND N < `config_overrides.max_validation_iterations` (default 3) AND coverage is not "sufficient" WHEN the exit conditions are checked THEN the loop proceeds to iteration N+1 with the classified re-extraction targets | Unit |

### AC-050C-04: Feedback Integration

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050C-04a | GIVEN the tool skill returns feedback for a section in iteration M WHEN feedback is received THEN the extractor writes it to `.checkpoint/session-{ts}/feedback/section-{N}-{slug}-iter-{M}.md` | Unit |
| AC-050C-04b | GIVEN feedback from iteration M-1 exists for a section WHEN the extractor re-extracts that section in iteration M THEN it reads the previous feedback file to guide targeted improvements (e.g., focusing on specific missing topics) | Unit |
| AC-050C-04c | GIVEN tool skill feedback specifies "missing topics" or "insufficient depth on {topic}" WHEN re-extracting THEN the extractor incorporates those specific directives into the extraction prompts for the targeted section | Unit |
| AC-050C-04d | GIVEN multiple iterations of feedback exist for the same section WHEN the extractor reads feedback THEN it reads only the most recent iteration's feedback (not cumulative) to avoid conflicting guidance | Unit |

### AC-050C-05: Exit Conditions

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050C-05a | GIVEN all sections have `validation_status: "accepted"` from the tool skill WHEN exit conditions are evaluated THEN Phase 3 exits with `phase_3_status: "validated"` and `exit_reason: "all_criteria_met"` | Unit |
| AC-050C-05b | GIVEN the current iteration count equals `config_overrides.max_validation_iterations` (default 3) AND coverage_target is not yet met WHEN exit conditions are evaluated THEN Phase 3 exits with `phase_3_status: "partial"` and `exit_reason: "max_iterations_reached"` AND logs the remaining coverage gaps | Unit |
| AC-050C-05c | GIVEN `coverage_ratio` did not improve (delta ≤ 0) between iteration N-1 and iteration N WHEN exit conditions are evaluated THEN Phase 3 exits with `phase_3_status: "partial"` and `exit_reason: "plateau_detected"` AND logs "no improvement between iterations {N-1} and {N}" | Unit |
| AC-050C-05d | GIVEN Phase 3 exits for any reason WHEN the exit is recorded THEN the output includes: `exit_reason`, final `coverage_ratio`, `iterations_completed`, per-section final `validation_status`, and a list of `unresolved_gaps` (if any) | Unit |

### AC-050C-06: Manifest Updates

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050C-06a | GIVEN Phase 3 begins WHEN the manifest is first updated THEN `manifest.yaml` shows `phase_3.status: "in_progress"`, `phase_3.iteration_count: 1`, and `phase_3.started_at` timestamp | Unit |
| AC-050C-06b | GIVEN a section is validated in iteration M WHEN the manifest is updated THEN the section entry includes: `validation_status` ("accepted" or "needs-more-info"), `quality_score`, `validated_in_iteration: M`, and `feedback_file` path (if rejected) | Unit |
| AC-050C-06c | GIVEN a re-extraction iteration completes WHEN the manifest is updated THEN `phase_3.iteration_count` increments, per-section validation results are updated, and `phase_3.coverage_ratio` reflects the latest computation | Unit |
| AC-050C-06d | GIVEN Phase 3 exits WHEN the manifest is finalized THEN `manifest.yaml` shows `phase_3.status` with the exit status ("validated" or "partial"), `phase_3.exit_reason`, `phase_3.final_coverage_ratio`, `phase_3.iterations_completed`, and `phase_3.completed_at` timestamp | Unit |

## Functional Requirements

### FR-050C-01: Acceptance Criteria Loading

**Description:** Phase 3 loads and parses the tool skill's acceptance criteria into a structured per-section checklist.

**Details:**
- Input: `tool_skill_artifacts.acceptance_criteria` file path from Phase 1 output
- Process: Parse acceptance criteria into a map of section_id → list of criteria. Each criterion has an ID, description, and type (depth or breadth indicator).
- Output: Structured criteria checklist used for validation and gap classification

### FR-050C-02: Section Validation Dispatch

**Description:** Phase 3 sends each section's content to the tool skill for validation via file-based handoff.

**Details:**
- Input: Section content file path (`content/section-{N}-{slug}.md`), section's acceptance criteria
- Process: Construct `validate_request` with section ID, content file path, and media attachments (if any). Send to tool skill. Receive `validate_response` with status, feedback, and quality score.
- Output: Per-section validation result (accepted/needs-more-info) with structured feedback

### FR-050C-03: Coverage Ratio Computation

**Description:** Phase 3 computes an aggregate coverage metric across all sections and criteria.

**Details:**
- Input: Per-section validation results from FR-050C-02
- Process: Count total criteria across all sections; count criteria marked as "met" (from accepted sections + passing criteria in partially-accepted sections). Compute ratio.
- Output: `coverage_ratio` (float 0.0–1.0), per-section pass/fail breakdown

### FR-050C-04: Gap Classification Engine

**Description:** Phase 3 classifies each failing criterion as a depth or breadth gap to drive targeted re-extraction.

**Details:**
- Input: Failing criteria from validation, tool skill feedback
- Process: Analyze feedback text — "insufficient detail", "too shallow", "needs examples" → depth gap. "Missing topic", "not covered", "no sources found" → breadth gap. Default to depth if ambiguous.
- Output: Per-section gap classification: `{section_id: {gap_type: "depth"|"breadth", failing_criteria: [...], feedback_summary: "..."}}`

### FR-050C-05: Targeted Re-extraction Coordinator

**Description:** Phase 3 coordinates re-extraction by invoking Phase 2 for specific sections with adjusted parameters.

**Details:**
- Input: Gap classification from FR-050C-04, previous feedback files
- Process: For depth gaps — augment section extraction prompts with "provide more detail on {topic}", narrow source scope. For breadth gaps — expand source scope (additional directories, sub-pages), add search queries for missing topics.
- Output: Updated content files for targeted sections only

### FR-050C-06: Iteration Controller

**Description:** Phase 3 manages the validation loop lifecycle — iteration count, exit condition evaluation, and termination.

**Details:**
- Input: Current iteration count, coverage_ratio history, max_validation_iterations config
- Process: After each iteration — check exit conditions in order: (1) all criteria met → exit "validated", (2) max iterations reached → exit "max_iterations_reached", (3) coverage plateau → exit "plateau_detected", (4) else → continue loop.
- Output: Loop continuation or termination signal with exit metadata

### FR-050C-07: Feedback Persistence

**Description:** Phase 3 persists all validation feedback to checkpoint files for traceability.

**Details:**
- Input: Tool skill validation responses containing feedback
- Process: Write feedback to `.checkpoint/session-{ts}/feedback/section-{N}-{slug}-iter-{M}.md` with iteration number, failing criteria, and tool skill comments.
- Output: Feedback files on disk, referenced in manifest

## Non-Functional Requirements

### NFR-050C-01: Performance

- Validation of a single section should complete within the time the tool skill requires for critique (no artificial timeout — tool skill critique is the bottleneck)
- Coverage computation must be O(sections × criteria) — no expensive recomputation
- Re-extraction should only process failing sections, not re-run the entire Phase 2

### NFR-050C-02: Configurability

- `max_validation_iterations` is configurable via `config_overrides.max_validation_iterations` (default: 3, min: 1, max: 10)
- `coverage_target` is configurable via `config_overrides.coverage_target` (default: 0.8, range: 0.0–1.0)
- Both defaults are defined in the skill's input parameters section; overrides are optional

### NFR-050C-03: Traceability

- Every validation result, feedback file, and coverage computation is persisted to `.checkpoint/`
- Manifest tracks per-section validation history across iterations
- Exit reason and final metrics are always recorded regardless of exit path

### NFR-050C-04: Robustness

- If the tool skill returns an unexpected response format during validation, Phase 3 logs a warning, marks the section as "error", and continues validating remaining sections
- If re-extraction produces identical content to the previous iteration for a section, Phase 3 detects the plateau for that section and excludes it from further iterations

## UI/UX Requirements

N/A — this is a pure skill-layer feature with no user interface.

## Dependencies

### Internal Dependencies

- **FEATURE-050-A (Extractor Skill Foundation & Input Detection):** Provides tool skill artifacts (acceptance_criteria, collection_template), checkpoint path, and file-based handoff protocol. Hard dependency.
- **FEATURE-050-B (Source Extraction Engine):** Provides Phase 2 content files in `.checkpoint/session-{ts}/content/`. Phase 3 validates these files. Hard dependency. Phase 3 also re-invokes Phase 2 extraction logic for targeted re-extraction of failing sections.

### External Dependencies

- **`x-ipe-tool-knowledge-extraction-user-manual`:** Required tool skill that performs validation against its acceptance criteria and returns structured feedback. Phase 3 calls the tool skill's "Operation 2: Validate & Pack" interface.
- **No additional external dependencies:** Phase 3 does not directly access file systems, URLs, or web search — it delegates re-extraction to Phase 2 logic.

## Business Rules

- **BR-050C-01:** Phase 3 MUST NOT modify content files directly — it delegates all content changes to Phase 2 re-extraction
- **BR-050C-02:** Sections that pass validation in iteration N are NOT re-validated in iteration N+1 (accepted sections are locked)
- **BR-050C-03:** The tool skill is the sole authority on acceptance — the extractor does not second-guess validation results
- **BR-050C-04:** File-based handoff is mandatory — validation requests and responses use file paths, not inline content
- **BR-050C-05:** Coverage ratio uses a flat count across all criteria (no per-section weighting in v1)
- **BR-050C-06:** When gap type is ambiguous from feedback, default classification is "depth" (safer to over-detail than under-discover)
- **BR-050C-07:** Plateau detection compares coverage_ratio values — a delta ≤ 0 triggers plateau exit (even if individual sections improved, if overall ratio didn't increase, the loop stops)
- **BR-050C-08:** Max iterations config is validated on input — values outside [1, 10] are clamped to the nearest bound with a warning

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Phase 2 produced zero content files (all sections empty/skipped) | Phase 3 skips validation entirely, exits with `phase_3_status: "skipped"`, `exit_reason: "no_content_to_validate"`, `coverage_ratio: 0.0` |
| Tool skill has no acceptance criteria defined for a section | Treat the section as implicitly "accepted" (no criteria = nothing to fail). Log warning: "No acceptance criteria for section {slug}" |
| Tool skill returns validation error (unexpected format) | Log error, mark section as "error" in manifest, continue validating other sections. Section counts as "not met" in coverage ratio. |
| All sections fail in every iteration (coverage_ratio stays 0.0) | Plateau detection triggers after iteration 2 (ratio 0.0 → 0.0 = no improvement). Exit with `exit_reason: "plateau_detected"`. |
| Single section keeps failing while others improve | Re-extraction targets only the failing section. If overall coverage_ratio improves, loop continues. If the stuck section is the only remaining gap and overall ratio plateaus, plateau exit triggers. |
| Re-extraction produces identical content to previous iteration | Phase 3 detects no change for that section, excludes it from further re-extraction targets. If all failing sections are excluded, triggers plateau exit. |
| `max_validation_iterations` set to 1 | Only one validation pass occurs. No re-extraction. Phase 3 reports whatever coverage the initial content achieved. |
| `coverage_target` set to 0.0 | Any non-negative coverage ratio meets the target. Phase 3 exits with "all_criteria_met" after the first validation pass (even with failures). |
| `coverage_target` set to 1.0 | Every single criterion must pass. Strict mode — any failure triggers re-extraction loop. |
| Tool skill accepts a section but with low quality_score | Section is marked "accepted" and locked. Coverage ratio counts it as met. Quality scores are recorded but do NOT influence the validation loop (quality scoring is FEATURE-050-E scope). |

## Out of Scope

- **Content generation or modification:** Phase 3 validates content and coordinates re-extraction; it does NOT write or edit content files directly (that is Phase 2's job)
- **Quality scoring aggregation:** Per-section quality_score values are recorded but not aggregated into an overall quality score (FEATURE-050-E)
- **KB intake output:** Validated content is not yet assembled into final output format (FEATURE-050-E)
- **Checkpoint resume logic:** Phase 3 writes to the manifest but does not implement resume-from-failure (FEATURE-050-D)
- **Per-section weighting:** v1 uses flat criteria counting; weighted coverage (some criteria more important) is deferred
- **Parallel section validation:** v1 validates sections sequentially; parallel validation is deferred
- **Tool skill critique sub-agent orchestration:** The tool skill internally manages its own critique sub-agent; Phase 3 treats validation as a black box

## Technical Considerations

- Phase 3 re-invokes Phase 2 extraction logic, NOT the full Phase 2 step — it calls the section-level extraction function with modified parameters (augmented prompts or expanded scope), not the entire phase orchestration
- The gap classification engine uses keyword matching on tool skill feedback text. A future version could use semantic analysis, but v1 uses simple pattern matching ("insufficient detail" → depth, "not covered" → breadth)
- Coverage ratio history should be stored as a list in the manifest: `phase_3.coverage_history: [0.4, 0.6, 0.8]` — one entry per iteration — to enable plateau detection
- The feedback file naming convention (`section-{N}-{slug}-iter-{M}.md`) ensures no overwrites across iterations and enables easy "read latest" by finding max M for a given section
- Manifest schema additions for Phase 3 should be additive — Phase 3 adds `phase_3.*` fields to the existing manifest without modifying Phase 1 or Phase 2 fields

## Open Questions

None — all design decisions were resolved in DAO-autonomous mode (validation mechanism, iteration control, coverage assessment, feedback loop, exit conditions, depth vs breadth classification).
