# Feature Specification: KB Intake Output & Quality Scoring

> Feature ID: FEATURE-050-E
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

FEATURE-050-E implements Phase 5 (笃行之 — Practice Earnestly) and Phase 6 (继续执行 — Continue Execution) of the application knowledge extractor skill. This is the **final feature** of EPIC-050, completing the extractor's full lifecycle: from raw extraction through validation to polished KB output.

Phase 5 adds two capabilities: (1) **quality scoring** — computing per-section and overall quality scores across four dimensions (completeness, accuracy, structure, freshness) to provide a deterministic, quantitative assessment of extraction quality; and (2) **KB article packaging** — transforming validated content into the `.kb-intake/` output format with `.kb-index.json` metadata, per-section article files, and provenance tracking.

Phase 6 adds **completion and handoff**: generating an `extraction_report.md` summarizing the full run, finalizing the manifest status to "complete", populating the Output Result YAML with all fields, and cleaning up temporary working files.

Together these phases bridge the gap between validated extraction content (FEATURE-050-C output) and the EPIC-049 KB intake pipeline, ensuring every extraction run produces structured, quality-scored, pipeline-ready knowledge articles.

## User Stories

1. As an **AI agent**, I want the extractor to **compute a quality score for each extracted section**, so that **I can identify weak sections that may need re-extraction or manual review**.

2. As an **AI agent**, I want the extractor to **produce an overall quality score** for the entire extraction run, so that **downstream consumers (librarian, humans) can quickly assess output reliability**.

3. As an **AI agent**, I want validated content to be **packaged into `.kb-intake/` format with a `.kb-index.json` manifest**, so that **the KB librarian pipeline can process it without transformation**.

4. As an **AI agent**, I want every output article to include **provenance metadata** (source files, timestamps, tool skill used), so that **knowledge lineage is traceable end-to-end**.

5. As a **human user**, I want an **extraction report summarizing the entire run** (sections extracted, quality scores, errors), so that **I can review extraction outcomes at a glance**.

6. As an **AI agent**, I want the extractor to **finalize the manifest and clean up temp files**, so that **completed extractions leave a clean workspace for the next run**.

## Acceptance Criteria

### Group 1: Quality Scoring

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------|-----------|
| AC-050E-01 | GIVEN extraction and validation are complete for a section WHEN quality scoring runs THEN a per-section quality score is computed across four dimensions: completeness (weight 0.40), accuracy (weight 0.30), structure (weight 0.20), freshness (weight 0.10), each producing a value between 0.0 and 1.0 | Structured-Review |
| AC-050E-02 | GIVEN the completeness dimension WHEN computing its score THEN it equals the `coverage_ratio` value from Phase 3 validation for that section (ratio of acceptance criteria met to total ACs) | Structured-Review |
| AC-050E-03 | GIVEN the accuracy dimension WHEN computing its score THEN it equals the tool skill's validation acceptance rate for that section: `accepted_iterations / total_iterations` (capped at 1.0; a section accepted on first pass scores 1.0) | Structured-Review |
| AC-050E-04 | GIVEN the structure dimension WHEN computing its score THEN it equals the ratio of template-prescribed sub-sections present in the final content to total prescribed sub-sections (e.g., 4 of 5 prompts addressed = 0.8) | Structured-Review |
| AC-050E-05 | GIVEN the freshness dimension WHEN computing its score THEN if source file modification dates are available, score = 1.0 for files modified within 90 days, linearly decaying to 0.0 at 365 days; if modification dates are unavailable, default to 0.5 | Structured-Review |
| AC-050E-06 | GIVEN per-section dimension scores are computed WHEN calculating the section's quality score THEN `section_quality_score = (completeness × 0.40) + (accuracy × 0.30) + (structure × 0.20) + (freshness × 0.10)` and the result is rounded to 2 decimal places | Structured-Review |
| AC-050E-07 | GIVEN all section quality scores are computed WHEN calculating the overall quality score THEN `overall_quality_score = arithmetic mean of all section_quality_scores` rounded to 2 decimal places | Structured-Review |
| AC-050E-08 | GIVEN the same extraction inputs and validation results WHEN quality scoring runs multiple times THEN it produces identical scores (deterministic computation — no randomness or LLM calls in scoring) | Structured-Review |

### Group 2: Quality Thresholds

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------|-----------|
| AC-050E-09 | GIVEN an overall quality score ≥ 0.80 WHEN classifying quality THEN it is labeled "high" and extraction proceeds to packaging without warnings | Structured-Review |
| AC-050E-10 | GIVEN an overall quality score between 0.50 and 0.79 inclusive WHEN classifying quality THEN it is labeled "acceptable" and a warning is logged: "Quality score {score} is acceptable but below high threshold (0.80). Consider re-extraction for sections: {lowest-scoring-sections}" | Structured-Review |
| AC-050E-11 | GIVEN an overall quality score below 0.50 WHEN classifying quality THEN it is labeled "low" and a warning is logged: "Quality score {score} is below acceptable threshold. Low-quality sections: {sections-below-0.50}" AND extraction still proceeds to packaging (does not block output) | Structured-Review |
| AC-050E-12 | GIVEN any section has a quality score below 0.50 WHEN generating section-level warnings THEN each such section is flagged individually in the manifest with `quality_flag: "low"` | Structured-Review |

### Group 3: KB Article Packaging

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------|-----------|
| AC-050E-13 | GIVEN validated content exists for all accepted sections WHEN packaging runs THEN a `.kb-intake/{extraction_id}/` folder is created under `x-ipe-docs/knowledge-base/` containing `.kb-index.json` and per-section article markdown files | Structured-Review |
| AC-050E-14 | GIVEN the `.kb-index.json` is generated WHEN reading its contents THEN it contains: `title` (from extraction purpose + target name), `category` ("user-manual"), `extraction_id`, `quality_score` (overall), `quality_label` ("high"/"acceptable"/"low"), `sections[]` (array of {id, title, file, quality_score}), `source_summary` ({input_type, target, file_count, primary_language}), `created_at` (ISO 8601 timestamp), `schema_version` ("1.0") | Structured-Review |
| AC-050E-15 | GIVEN per-section articles are generated WHEN reading any article file THEN it contains: YAML frontmatter with `section_id`, `title`, `quality_score`, `quality_dimensions` ({completeness, accuracy, structure, freshness}), and `provenance` ({source_files[], extraction_timestamp, tool_skill, iteration_count}); followed by the validated markdown content from Phase 3 | Structured-Review |
| AC-050E-16 | GIVEN articles are written WHEN checking file encoding THEN all output files (`.kb-index.json` and article `.md` files) are UTF-8 encoded with no BOM | Structured-Review |
| AC-050E-17 | GIVEN sections with status "error" or "skipped" exist WHEN packaging runs THEN those sections are excluded from article files but listed in `.kb-index.json` under `excluded_sections[]` with their status and reason | Structured-Review |

### Group 4: Extraction Report

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------|-----------|
| AC-050E-18 | GIVEN extraction is complete WHEN the report is generated THEN an `extraction_report.md` file is created in the `.kb-intake/{extraction_id}/` folder alongside the articles | Structured-Review |
| AC-050E-19 | GIVEN the extraction report is generated WHEN reading its contents THEN it contains these sections: **Summary** (target, category, overall quality score and label, total sections, duration), **Per-Section Scores** (table with section name, quality score, label, dimension breakdown), **Validation Statistics** (iterations completed, coverage history, exit reason), **Error Log** (errors from Phase 4, if any), **Provenance** (source paths, tool skill used, extraction timestamp, agent nickname) | Structured-Review |
| AC-050E-20 | GIVEN the extraction report WHEN reviewing the per-section scores table THEN sections are sorted by quality score ascending (lowest first) to highlight weak areas | Structured-Review |

### Group 5: Completion & Handoff

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|------|-----------|
| AC-050E-21 | GIVEN all articles are packaged and report generated WHEN completing extraction THEN manifest.yaml status transitions to "complete" and `completed_at` timestamp is set | Structured-Review |
| AC-050E-22 | GIVEN extraction is complete WHEN populating the Output Result YAML THEN `extraction_status` is set to "complete" (or "partial" if any sections were skipped/errored, or "failed" if zero sections were accepted), and `quality_score` is set to the computed overall score | Structured-Review |
| AC-050E-23 | GIVEN extraction completes successfully WHEN the Output Result is logged THEN `output_links` contains paths to: `.kb-intake/{extraction_id}/.kb-index.json`, `.kb-intake/{extraction_id}/extraction_report.md`, and the checkpoint manifest path | Structured-Review |
| AC-050E-24 | GIVEN extraction is complete WHEN cleanup runs THEN temporary working files in `.checkpoint/session-{timestamp}/extracted/` and `.checkpoint/session-{timestamp}/feedback/` are removed, but `manifest.yaml`, `packed/` content files, and `collection-template.md` are preserved | Structured-Review |

## Functional Requirements

**FR-1: Per-Section Quality Score Computation**
- Input: Section's validation results (coverage_ratio, iterations, acceptance status), content file, collection template
- Process: Compute four dimension scores (completeness, accuracy, structure, freshness), apply weights (0.40/0.30/0.20/0.10), sum to section score
- Output: `section_quality_score` (float 0.0–1.0, 2 decimal places) with dimension breakdown

**FR-2: Overall Quality Score Computation**
- Input: All section quality scores
- Process: Arithmetic mean of section scores, rounded to 2 decimal places
- Output: `overall_quality_score` (float 0.0–1.0) with quality label (high/acceptable/low)

**FR-3: Quality Threshold Classification**
- Input: Overall quality score
- Process: Classify into high (≥0.80), acceptable (0.50–0.79), low (<0.50); generate warnings for acceptable/low
- Output: Quality label, optional warning message

**FR-4: KB Article Packaging**
- Input: Validated and packed content files from `.checkpoint/session-{timestamp}/packed/`
- Process: Create `.kb-intake/{extraction_id}/` folder, generate `.kb-index.json`, copy and enrich article files with frontmatter, handle excluded sections
- Output: Pipeline-ready KB intake folder

**FR-5: Extraction Report Generation**
- Input: All Phase 1–5 data (manifest, quality scores, validation stats, error log)
- Process: Generate structured markdown report with summary, per-section table, statistics, errors, provenance
- Output: `extraction_report.md` in the intake folder

**FR-6: Manifest Finalization & Cleanup**
- Input: Completed packaging and report
- Process: Set manifest status → "complete", populate Output Result YAML, remove temp files (extracted/, feedback/), preserve manifest and packed/
- Output: Clean workspace, fully populated Output Result

## Non-Functional Requirements

**NFR-1: Deterministic Scoring** — Quality score computation must be purely algorithmic (no LLM calls, no randomness). Given identical inputs, scores must be bit-identical across runs.

**NFR-2: UTF-8 Encoding** — All output files must be UTF-8 encoded without BOM. No binary content in article files.

**NFR-3: KB Pipeline Compatibility** — Output folder structure and `.kb-index.json` schema must be compatible with `x-ipe-docs/knowledge-base/.intake/` pipeline conventions (EPIC-049).

**NFR-4: Idempotent Packaging** — Running Phase 5 twice on the same validated content produces identical output (safe to re-run).

**NFR-5: Minimal Disk Footprint** — Cleanup removes temporary extracted/ and feedback/ files. Only manifest, packed content, and final intake output persist.

## Dependencies

### Internal
- **FEATURE-050-A** (✅ Implemented) — Foundation, `.checkpoint/` folder structure, manifest template
- **FEATURE-050-B** (✅ Implemented) — Phase 2 extraction (produces content files)
- **FEATURE-050-C** (✅ Implemented) — Phase 3 validation (produces coverage_ratio, acceptance results, packed content)
- **FEATURE-050-D** (✅ Implemented) — Phase 4 checkpoint & error handling (provides error_log, manifest state machine)
- **EPIC-049** (External) — KB intake pipeline conventions; `.intake/` folder and librarian processing

### External
- None

## Business Rules

**BR-1:** Quality scores never block output. Even "low" quality extractions are packaged — the score is informational, not a gate. Rationale: blocking on quality would require re-extraction loops that belong in Phase 3, not Phase 5.

**BR-2:** Excluded sections (error/skipped) are tracked in `.kb-index.json` but do not receive article files. They are counted as 0.0 when computing overall quality score.

**BR-3:** The `extraction_id` used in `.kb-intake/{extraction_id}/` matches the session ID from the checkpoint folder (`session-{timestamp}`).

**BR-4:** Cleanup preserves the manifest and packed content as an audit trail. Only intermediate working files are deleted.

**BR-5:** The `schema_version` field in `.kb-index.json` starts at "1.0" matching the manifest schema version convention from FEATURE-050-D.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| All sections accepted, high quality | Package all articles, quality label "high", no warnings |
| Some sections skipped/errored | Package accepted sections only; excluded_sections[] populated; overall score penalized |
| All sections failed (zero accepted) | extraction_status = "failed"; empty article folder; report still generated with error details |
| Single section extraction | Quality score = that section's score; overall = section score |
| Source files have no modification dates (URLs, runtime) | Freshness dimension defaults to 0.5 |
| Re-running Phase 5 on already-packaged output | Idempotent: overwrites existing `.kb-intake/{extraction_id}/` with identical content |
| `.kb-intake/` folder doesn't exist | Create `x-ipe-docs/knowledge-base/.intake/` directory automatically |
| Section has 0 iterations (accepted on first pass) | Accuracy score = 1.0 (1/1) |
| Coverage ratio from Phase 3 is 0.0 (no ACs met) | Completeness = 0.0; section still packaged if status is "accepted" by tool skill |

## Out of Scope

- Quality score as a gate/blocker for output (quality is informational only in v1)
- LLM-based quality assessment (scoring is purely algorithmic)
- Multi-category output (v1 processes one category — user-manual — per run)
- KB librarian invocation (Phase 6 logs completion; actual librarian call is EPIC-049 scope)
- Incremental re-packaging (re-running packages entire extraction, not delta)
- Custom quality dimension weights (weights are fixed at 0.40/0.30/0.20/0.10 in v1)
- Quality score visualization or dashboard UI

## Technical Considerations

- Phase 5 content in SKILL.md should be concise (~25 lines) with detailed scoring formulas in a reference file (`references/quality-scoring-formulas.md`)
- The `.kb-index.json` schema should be documented in a reference file for future tool skill compatibility
- Freshness scoring relies on filesystem `mtime` for local files; for URLs, `Last-Modified` header if available, else default 0.5
- The extraction report is markdown (not YAML/JSON) for human readability; machine-readable data is in `.kb-index.json`
- Cleanup must not delete files while other phases are running (only runs after Phase 5 packaging is complete)
- `extraction_status` in Output Result maps: all accepted → "complete", some accepted → "partial", zero accepted → "failed"

## Design Notes (DAO Decisions)

> The following design decisions were made autonomously under `dao-represent-human-to-interact` mode.

**DN-1: Quality Dimension Weights (0.40/0.30/0.20/0.10)**
Completeness gets the highest weight (0.40) because missing content is the most impactful quality deficiency for KB articles. Accuracy (0.30) is next — validated content must be trustworthy. Structure (0.20) matters for usability but is less critical than content quality. Freshness (0.10) gets minimal weight because extraction targets are typically current applications; stale sources are the exception.

**DN-2: Quality Thresholds (0.80 / 0.50)**
The 0.80 "high" threshold aligns with common documentation quality standards (80% coverage is generally considered comprehensive). The 0.50 "acceptable" floor means at least half the quality dimensions are reasonably satisfied. Below 0.50 indicates significant quality gaps that warrant explicit flagging.

**DN-3: Low Quality Does Not Block Output**
In v1, quality scoring is informational. Blocking on quality would create a re-extraction loop that overlaps with Phase 3's validation loop. Phase 3 handles content improvement; Phase 5 measures the final state. The librarian (EPIC-049) can use quality scores to prioritize review.

**DN-4: Excluded Sections Score as 0.0**
Errored/skipped sections represent knowledge gaps. Counting them as 0.0 in the overall average accurately reflects extraction completeness and incentivizes full coverage.

**DN-5: Arithmetic Mean for Overall Score**
Weighted per-section averages (by section importance) were considered but rejected for v1 — section importance is subjective and tool-skill-dependent. Arithmetic mean is simple, deterministic, and provides a fair baseline. Future versions could allow tool skills to specify section weights.

**DN-6: Report Sorted by Quality Ascending**
Showing lowest-quality sections first in the report follows the "worst first" principle — reviewers can quickly identify and address the weakest areas.

## Open Questions

None — all design decisions resolved autonomously via DAO reasoning (see Design Notes above).
