# Output & Quality Heuristics

## §1. Quality Scoring Algorithm

### §1.1 Completeness Dimension (Weight: 0.40)
  - Formula: completeness = section.criteria_met / section.criteria_total
  - Source: Phase 3 manifest per_section[].criteria_met, criteria_total
  - If section has no criteria (implicitly accepted): completeness = 1.0
  - Range: 0.0 – 1.0

### §1.2 Accuracy Dimension (Weight: 0.30)
  - Formula: accuracy = 1 / section.iterations_validated
    (accepted on pass 1 = 1.0; pass 2 = 0.5; pass 3 = 0.33)
  - Capped at 1.0 (minimum 1 iteration)
  - If section status is "error": accuracy = 0.0
  - Range: 0.0 – 1.0

### §1.3 Structure Dimension (Weight: 0.20)
  - Formula: structure = present_sub_sections / prescribed_sub_sections
  - Prescribed: count extraction prompts / H3 sub-headings in collection template for this section
  - Present: count matching H2/H3 headings in packed content file
  - If prescribed = 0 (no sub-sections defined): structure = 1.0
  - Range: 0.0 – 1.0

### §1.4 Freshness Dimension (Weight: 0.10)
  - For LOCAL files (source_code_repo, documentation_folder, single_file):
    - Read source file mtime from filesystem
    - If multiple source files: use MEDIAN mtime
    - Score: 1.0 if mtime ≤ 90 days ago
             Linear decay from 1.0 to 0.0 between 90 and 365 days
             0.0 if mtime > 365 days ago
    - Formula (90–365 range): freshness = (365 - days_old) / 275
  - For URLs (public_url, running_web_app):
    - If Last-Modified header available: use same formula as local
    - If unavailable: default to 0.5
  - Range: 0.0 – 1.0

### §1.5 Per-Section Weighted Score
  - Formula: section_score = (completeness × 0.40) + (accuracy × 0.30)
                            + (structure × 0.20) + (freshness × 0.10)
  - Round to 2 decimal places
  - Range: 0.0 – 1.0

## §2. Overall Quality Score & Aggregation

  - Include only sections with validation_status "accepted"
  - Sections with status "error" or "skipped": count as 0.0 per BR-2
  - Formula: overall_score = sum(all section_scores including 0.0 for excluded)
                           / total_section_count
  - Round to 2 decimal places
  - Edge case: zero accepted sections → overall_score = 0.0,
    extraction_status = "failed"
  - Edge case: single section → overall_score = that section's score

## §3. Threshold Classification & Warnings

  | Overall Score | Label | Warning | Action |
  |---------------|-------|---------|--------|
  | ≥ 0.80 | "high" | None | Proceed to packaging |
  | 0.50 – 0.79 | "acceptable" | "Quality score {score} is acceptable but below high threshold (0.80). Consider re-extraction for sections: {lowest}" | Proceed to packaging |
  | < 0.50 | "low" | "Quality score {score} is below acceptable threshold. Low-quality sections: {sections below 0.50}" | Proceed to packaging (non-blocking) |

  Per-section flag:
  - If section_quality_score < 0.50 → set quality_flag: "low" in manifest per_section entry

## §4. Intake Folder Convention

  The extractor deposits raw output into `.intake/{extraction_id}/`. No index file is generated — downstream skills (e.g., KB librarian) own indexing and cataloguing.

  Folder contents:
  - `section-{NN}-{slug}.md` — one article per accepted section
  - `extraction_report.md` — summary with scores, validation stats, error log, provenance

## §5. Article File Format

  File name: `section-{NN}-{slug}.md` (matches checkpoint content naming)
  Location: `.intake/{extraction_id}/section-{NN}-{slug}.md`

  ```markdown
  ---
  section_id: 1
  title: "Overview"
  quality_score: 0.92
  quality_dimensions:
    completeness: 1.0
    accuracy: 1.0
    structure: 0.8
    freshness: 0.7
  provenance:
    source_files:
      - "src/main.py"
      - "README.md"
    extraction_timestamp: "2026-03-17T14:30:22Z"
    tool_skill: "x-ipe-tool-knowledge-extraction-user-manual"
    iteration_count: 2
  ---

  {validated markdown content from packed/ file — copied verbatim}
  ```

  Encoding: UTF-8, no BOM. All article files.

## §6. extraction_report.md Template

  Location: `.intake/{extraction_id}/extraction_report.md`

  ```markdown
  # Extraction Report

  ## Summary

  | Field | Value |
  |-------|-------|
  | Target | {target path or URL} |
  | Category | {selected_category} |
  | Overall Quality Score | {overall_score} ({quality_label}) |
  | Total Sections | {total} ({accepted} accepted, {excluded} excluded) |
  | Duration | {started_at} → {completed_at} |

  ## Per-Section Scores

  <!-- Sorted by quality_score ASCENDING (lowest first) -->

  | # | Section | Score | Label | Completeness | Accuracy | Structure | Freshness |
  |---|---------|-------|-------|-------------|----------|-----------|-----------|
  | 4 | Troubleshooting | 0.00 | excluded | — | — | — | — |
  | 2 | Installation | 0.65 | acceptable | 0.80 | 0.50 | 0.60 | 0.70 |
  | 1 | Overview | 0.92 | high | 1.00 | 1.00 | 0.80 | 0.70 |

  ## Validation Statistics

  | Metric | Value |
  |--------|-------|
  | Iterations Completed | {iteration_count} |
  | Final Coverage Ratio | {final_coverage_ratio} |
  | Exit Reason | {exit_reason} |
  | Coverage History | {coverage_history[]} |

  ## Error Log

  <!-- From manifest error_log[]; empty if no errors -->

  | Section | Error Type | Message | Retries | Timestamp |
  |---------|-----------|---------|---------|-----------|
  | Troubleshooting | permanent | Source file not found | 0 | 2026-03-17T15:02:30Z |

  ## Provenance

  | Field | Value |
  |-------|-------|
  | Source Paths | {source files / URLs} |
  | Tool Skill | {loaded_tool_skill} |
  | Extraction Timestamp | {created_at} |
  | Agent | {agent nickname} |
  ```

  Notes:
  - Per-Section table: excluded sections shown with score 0.00 and label "excluded"
  - Error Log: pulled from manifest `error_log[]`; show "No errors" if empty
  - Provenance agent field: agent nickname from session context

## §7. Edge Cases

  | Scenario | Behavior |
  |----------|----------|
  | All sections accepted, high quality | Package all, label "high", no warnings |
  | Some sections error/skipped | Package accepted only; excluded_sections[] populated; 0.0 in mean |
  | Zero accepted sections | extraction_status = "failed"; empty articles; report generated with errors |
  | Single section | overall_score = that section's score |
  | Source files have no mtime (URLs) | Freshness defaults to 0.5 |
  | Section has 0 ACs (implicitly accepted) | Completeness = 1.0 |
  | Section accepted on first pass | Accuracy = 1.0 (1/1) |
  | Coverage ratio = 0.0 | Completeness = 0.0; section still packaged if "accepted" |
  | Re-running Phase 5 | Idempotent: overwrite .intake/{extraction_id}/ |
  | .intake/ folder missing | Create x-ipe-docs/knowledge-base/.intake/ automatically |
  | Packed content file missing | Mark section "error", skip article generation |
