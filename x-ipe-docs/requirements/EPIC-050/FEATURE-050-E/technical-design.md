# Technical Design: KB Intake Output & Quality Scoring

> Feature ID: FEATURE-050-E | Version: v1.0 | Last Updated: 2026-03-17
> Program Type: skills | Tech Stack: SKILL.md/Prompt Engineering

---

## Part 1: AC-to-Deliverable Mapping

> **Purpose:** Trace every acceptance criterion to a concrete deliverable location.
> **Convention:** `SKILL.md` = procedure step changes; `REF` = `references/output-quality-heuristics.md`.

### Group 1: Quality Scoring (AC-050E-01 through AC-050E-08)

| AC ID | Summary | Deliverable | Location |
|-------|---------|-------------|----------|
| AC-050E-01 | Per-section score across 4 weighted dimensions | SKILL.md Step 5.1 CONTEXT + ACTION; REF §1 | Step 5.1 reads dimensions + weights; REF §1 provides formulas |
| AC-050E-02 | Completeness = coverage_ratio from Phase 3 | SKILL.md Step 5.1 CONTEXT; REF §1.1 | Step 5.1 reads `phase_3.per_section[].criteria_met / criteria_total`; REF documents mapping |
| AC-050E-03 | Accuracy = accepted_iterations / total_iterations | SKILL.md Step 5.1 CONTEXT; REF §1.2 | Step 5.1 reads iteration data from manifest; REF documents formula |
| AC-050E-04 | Structure = present sub-sections / prescribed sub-sections | SKILL.md Step 5.1 ACTION; REF §1.3 | Step 5.1 counts sub-sections against template; REF documents matching algorithm |
| AC-050E-05 | Freshness = linear decay 90d→365d, default 0.5 | SKILL.md Step 5.1 ACTION; REF §1.4 | Step 5.1 checks source mtime; REF documents decay curve |
| AC-050E-06 | Weighted formula: 0.40C + 0.30A + 0.20S + 0.10F, round 2dp | SKILL.md Step 5.1 ACTION; REF §1.5 | Step 5.1 computes weighted sum; REF documents normalization |
| AC-050E-07 | Overall = arithmetic mean of section scores, round 2dp | SKILL.md Step 5.1 ACTION; REF §2 | Step 5.1 aggregates; REF documents exclusion rules |
| AC-050E-08 | Deterministic (no LLM, no randomness) | SKILL.md Step 5.1 CONTEXT (explicit note); REF §1 header | Both locations reinforce: purely algorithmic |

### Group 2: Quality Thresholds (AC-050E-09 through AC-050E-12)

| AC ID | Summary | Deliverable | Location |
|-------|---------|-------------|----------|
| AC-050E-09 | Score ≥ 0.80 → "high", no warnings | SKILL.md Step 5.1 DECISION; REF §3 | Step 5.1 classifies threshold; REF documents classification table |
| AC-050E-10 | Score 0.50–0.79 → "acceptable", log warning | SKILL.md Step 5.1 DECISION; REF §3 | Step 5.1 logs warning with lowest sections; REF documents template |
| AC-050E-11 | Score < 0.50 → "low", log warning, still package | SKILL.md Step 5.1 DECISION; REF §3 | Step 5.1 logs warning, proceeds to packaging; REF documents non-blocking rule |
| AC-050E-12 | Per-section flag `quality_flag: "low"` if < 0.50 | SKILL.md Step 5.1 ACTION; REF §3 | Step 5.1 sets per-section flags; REF documents flag schema |

### Group 3: KB Article Packaging (AC-050E-13 through AC-050E-17)

| AC ID | Summary | Deliverable | Location |
|-------|---------|-------------|----------|
| AC-050E-13 | Create `.kb-intake/{extraction_id}/` with index + articles | SKILL.md Step 5.2 ACTION; REF §4, §5 | Step 5.2 creates folder; REF defines schema + format |
| AC-050E-14 | `.kb-index.json` schema (title, category, sections[], etc.) | SKILL.md Step 5.2 ACTION; REF §4 | Step 5.2 writes JSON; REF §4 defines full schema |
| AC-050E-15 | Article frontmatter (section_id, quality, provenance) + content | SKILL.md Step 5.2 ACTION; REF §5 | Step 5.2 enriches articles; REF §5 defines frontmatter schema |
| AC-050E-16 | All output files UTF-8 encoded, no BOM | SKILL.md Step 5.2 VERIFY; REF §5 note | Step 5.2 verify checkpoint; REF documents encoding rule |
| AC-050E-17 | Excluded sections (error/skipped) in `excluded_sections[]` | SKILL.md Step 5.2 ACTION; REF §4 `excluded_sections` field | Step 5.2 filters by status; REF defines exclusion schema |

### Group 4: Extraction Report (AC-050E-18 through AC-050E-20)

| AC ID | Summary | Deliverable | Location |
|-------|---------|-------------|----------|
| AC-050E-18 | `extraction_report.md` in intake folder | SKILL.md Step 5.2 ACTION; REF §6 | Step 5.2 generates report; REF §6 defines template |
| AC-050E-19 | Report sections: Summary, Per-Section, Validation Stats, Errors, Provenance | SKILL.md Step 5.2 ACTION; REF §6 | Step 5.2 assembles sections; REF §6 defines each section |
| AC-050E-20 | Per-section table sorted by quality ascending (lowest first) | REF §6 template | REF §6 specifies sort order |

### Group 5: Completion & Handoff (AC-050E-21 through AC-050E-24)

| AC ID | Summary | Deliverable | Location |
|-------|---------|-------------|----------|
| AC-050E-21 | Manifest status → "complete", `completed_at` set | SKILL.md Phase 6 ACTION | Phase 6 finalizes manifest |
| AC-050E-22 | Output Result: extraction_status + quality_score populated | SKILL.md Phase 6 ACTION; Output Result section | Phase 6 populates; Output Result defines field schema |
| AC-050E-23 | Output Result: `output_links` with paths to index, report, manifest | SKILL.md Phase 6 ACTION; Output Result section | Phase 6 sets links; Output Result defines structure |
| AC-050E-24 | Cleanup: remove extracted/ + feedback/, preserve manifest + packed/ | SKILL.md Phase 6 ACTION | Phase 6 performs cleanup |

### Deliverable Coverage Summary

| Deliverable | ACs Covered | Count |
|-------------|-------------|-------|
| SKILL.md Step 5.1 (Quality Scoring) | 01–12 | 12 |
| SKILL.md Step 5.2 (Packaging + Report) | 13–20 | 8 |
| SKILL.md Phase 6 (Completion) | 21–24 | 4 |
| REF `output-quality-heuristics.md` | 01–20 (supporting detail) | 20 |
| SKILL.md Output Result section | 22, 23 | 2 |

**All 24 ACs are mapped.** No AC is left without a deliverable. The REF file provides implementation detail; SKILL.md provides the agent-executable procedure.

---

## Part 2: Implementation Guide

> **Purpose:** Detailed guide for implementing Phase 5 + Phase 6 in SKILL.md + reference file.
> **📌 Emphasis on SKILL.md prompt engineering, not runtime code.**

### A. SKILL.md Changes

#### Step 5.1 — Quality Scoring (Replace Stub)

**Current state (lines 358–360):** 3-line stub ("NOT IMPLEMENTED").

**Proposed replacement (~14 lines):**

```markdown
#### Step 5.1 — Quality Scoring

**CONTEXT — Gather Scoring Inputs (Deterministic Only — No LLM):**
- Read manifest `phase_3.per_section[]`: for each section, extract `criteria_met`, `criteria_total`, `iterations_validated`, `validation_status`
- Read collection template: count prescribed sub-sections (H3 headings / extraction prompts) per section
- Read packed content files: count present sub-sections (H2/H3 headings matching template) per section
- Read source file modification dates from `source_metadata` (if local); for URLs default freshness to 0.5

**DECISION — Classify Quality Threshold:**
- Compute per-section `section_quality_score` (see reference for 4-dimension formula)
- Compute `overall_quality_score` = arithmetic mean of section scores (exclude error/skipped sections from mean; count them as 0.0 only if doing so per BR-2)
- Classify: ≥ 0.80 → "high"; 0.50–0.79 → "acceptable"; < 0.50 → "low"
- IF "acceptable" → log warning with lowest-scoring sections; IF "low" → log warning with sections below 0.50
- Per-section: IF section score < 0.50 → set `quality_flag: "low"` in manifest

**ACTION:** Compute all scores per reference formulas. Write quality results to manifest: `phase_5.quality_scores[]`, `phase_5.overall_quality_score`, `phase_5.quality_label`. Scoring is non-blocking — always proceed to Step 5.2.

**VERIFY:** ✅ Every section has `section_quality_score` (0.0–1.0, 2dp); overall score and label set; identical inputs → identical scores

**REFERENCE:** `references/output-quality-heuristics.md` §1–§3
```

**Line count:** 14 lines (excluding fenced code markers — this is inline content).

---

#### Step 5.2 — Package KB Article Output (Replace Stub)

**Current state (lines 364–372):** 9-line stub (compressed completion logic that should actually be the packaging step).

**Proposed replacement (~16 lines):**

```markdown
#### Step 5.2 — Package KB Articles & Report

**CONTEXT:** Read all packed content files from `.checkpoint/session-{timestamp}/packed/`. Read quality scores from Step 5.1. Read manifest for provenance data (target, loaded_tool_skill, timestamps). Derive `extraction_id` from session folder name (e.g., `session-20260317-143022`).

**DECISION — Determine Output Path & Status:**
- Output folder: `x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/`
- IF zero accepted sections → extraction_status = "failed" (still generate report with error details)
- IF all sections accepted → extraction_status = "complete"
- IF some accepted, some error/skipped → extraction_status = "partial"

**ACTION — Write Output Files:**
1. Create output folder (and `x-ipe-docs/knowledge-base/.kb-intake/` if needed)
2. Generate `.kb-index.json` per reference schema: title, category, extraction_id, quality_score, quality_label, sections[], excluded_sections[], source_summary, created_at, schema_version "1.0"
3. For each accepted section: write article `.md` with YAML frontmatter (section_id, title, quality_score, quality_dimensions, provenance) + validated content from packed files
4. For error/skipped sections: add to `excluded_sections[]` in index with status and reason; no article file
5. Generate `extraction_report.md` per reference template: Summary, Per-Section Scores (sorted quality ascending), Validation Statistics, Error Log, Provenance
6. All files UTF-8, no BOM

**VERIFY:**
- ✅ `.kb-index.json` exists with all required fields; article files match accepted section count
- ✅ `extraction_report.md` exists with all 5 sections; per-section table sorted ascending
- ✅ Excluded sections listed in index but have no article files

**REFERENCE:** `references/output-quality-heuristics.md` §4–§7
```

**Line count:** 16 lines.

---

#### Phase 6 — Completion & Handoff (Replace Stub)

**Current state (lines 376–386):** 11-line stub with Step 6.1 + Step 6.2 placeholders.

**Proposed replacement (~12 lines):**

```markdown
### Phase 6: 继续执行 — Continue Execution

#### Step 6.1 — Finalize & Clean Up

**ACTION — Manifest & Output Result:**
1. Update manifest: `status` → "complete", `completed_at` → ISO 8601 timestamp
2. Populate Output Result: `extraction_status` (from Step 5.2), `quality_score` (overall), `quality_label`, `kb_output_path` (intake folder path)
3. Set `task_output_links[]`: path to `.kb-index.json`, `extraction_report.md`, manifest path
4. Update task-board.md: set task status to completed

**ACTION — Cleanup Temporary Files:**
5. Remove `{checkpoint_path}/extracted/` and `{checkpoint_path}/feedback/` directories
6. Preserve: `manifest.yaml`, `packed/` content files, `collection-template.md`

**VERIFY:** ✅ Manifest status is "complete"; Output Result fields populated; temp dirs removed; packed/ and manifest preserved

#### Step 6.2 — Route Next Action

**DECISION:** DAO mode → log completion, future: invoke `x-ipe-tool-kb-librarian`; manual mode → present results to human.
```

**Line count:** 12 lines.

---

#### Output Result Section Updates

**Current state (lines 459–462):** Future-field placeholder comment.

**Proposed replacement:**

```yaml
  # Phase 5 outputs (FEATURE-050-E)
  extraction_status: "complete | partial | failed"
  quality_score: 0.0       # 0.0–1.0, overall quality (2 decimal places)
  quality_label: "high | acceptable | low"
  kb_output_path: "x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/"
  task_output_links:
    - "x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/.kb-index.json"
    - "x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/extraction_report.md"
    - ".checkpoint/session-{timestamp}/manifest.yaml"
```

**Net change:** Replaces 3 lines (comment + 2 placeholder fields) with 8 lines → net +5 lines.

---

#### DoD Section Updates

**Current state (lines 466–475):** 7 checklist items through Phase 4.

**Proposed updates:**
- Update `Phase 4 Active` → `Phase 4 Complete` (wording change, net 0)
- Add Phase 5 + Phase 6 items (+2 lines)
- Remove "Active" qualifier from Phase 4 (already done via FEATURE-050-D)

```markdown
- [ ] **Phase 5 Complete:** Quality scores computed (4 dimensions), articles packaged in .kb-intake/, extraction report generated
- [ ] **Phase 6 Complete:** Manifest finalized, Output Result populated, temp files cleaned up
```

**Net change:** +2 lines.

---

#### Additional Metadata Updates

| Section | Current | Update | Net Lines |
|---------|---------|--------|-----------|
| Frontmatter line 16 | `Version: 1.3.0 \| Feature: FEATURE-050-D` | `Version: 1.4.0 \| Feature: FEATURE-050-E` | 0 |
| 🎯 Implemented Phases (line 44) | `NOT Yet Implemented: Phase 5` | Remove line (all phases implemented) | −1 |
| Execution Flow table (line 112) | `FEATURE-050-E 🔜` | `FEATURE-050-E ✅` | 0 |
| Phase 3 Definition (lines 147–154) | `🔜 NOT IMPLEMENTED` (8 lines) | Implemented status (2 lines) | −6 |
| Phase 4 Definition (lines 156–163) | `🔜 NOT IMPLEMENTED` (8 lines) | Implemented status (2 lines) | −6 |
| Phase 5 Definition (lines 165–173) | `🔜 NOT IMPLEMENTED` (9 lines) | Implemented status (2 lines) | −7 |

**Total reclaim from Phase Definitions:** −19 lines.

---

### B. Line Budget Analysis

```
Current SKILL.md:                                  497 lines

REMOVALS (lines reclaimed):
  Phase 5 Step 5.1 stub (lines 358–360):           −3 lines
  Phase 5 Step 5.2 + old complete (lines 364–372):  −9 lines
  Phase 6 stub (lines 376–386):                    −11 lines
  Phase 3 Definition compression:                   −6 lines
  Phase 4 Definition compression:                   −6 lines
  Phase 5 Definition compression:                   −7 lines
  "NOT Yet Implemented" line:                       −1 line
  Future-field placeholder (Output Result):          −3 lines
                                          Subtotal: −46 lines

ADDITIONS:
  Step 5.1 (Quality Scoring):                      +14 lines
  Step 5.2 (Packaging + Report):                   +16 lines
  Phase 6 (Completion + Cleanup):                  +12 lines
  Output Result Phase 5 fields:                     +8 lines
  DoD Phase 5 + Phase 6 items:                      +2 lines
                                          Subtotal: +52 lines

NET CHANGE:         +52 − 46 = +6 lines
PROJECTED TOTAL:    497 + 6 = 503 lines

WITHIN BUDGET:      503 ≤ 500 + 5 tolerance = ✅ (acceptable)
```

**Contingency if over 500:** Compress Phase 6 Step 6.2 to a single line (saves 1–2 lines), or inline the "Route Next Action" decision into Step 6.1 VERIFY block. Phase Definition compression provides the primary savings.

---

### C. New Reference File: `references/output-quality-heuristics.md`

**Location:**
```
.github/skills/x-ipe-task-based-application-knowledge-extractor/
├── references/
│   ├── input-detection-heuristics.md         # FEATURE-050-A
│   ├── handoff-protocol.md                   # FEATURE-050-A
│   ├── category-taxonomy.md                  # FEATURE-050-A
│   ├── examples.md                           # FEATURE-050-A
│   ├── extraction-engine-heuristics.md       # FEATURE-050-B
│   ├── validation-loop-heuristics.md         # FEATURE-050-C
│   ├── checkpoint-error-heuristics.md        # FEATURE-050-D
│   └── output-quality-heuristics.md          # NEW (FEATURE-050-E)
└── templates/
    ├── checkpoint-manifest.md                # FEATURE-050-A
    └── input-analysis-output.md              # FEATURE-050-A
```

**Structure (no line limit — reference files are unconstrained):**

```
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

## §4. .kb-index.json Schema

  ```json
  {
    "schema_version": "1.0",
    "title": "{purpose} — {target_name}",
    "category": "user-manual",
    "extraction_id": "session-{timestamp}",
    "quality_score": 0.85,
    "quality_label": "high",
    "created_at": "2026-03-17T15:00:00Z",
    "source_summary": {
      "input_type": "source_code_repo",
      "target": "./my-app/",
      "file_count": 42,
      "primary_language": "Python"
    },
    "sections": [
      {
        "id": 1,
        "title": "Overview",
        "file": "section-01-overview.md",
        "quality_score": 0.92,
        "quality_flag": null
      }
    ],
    "excluded_sections": [
      {
        "id": 4,
        "title": "Troubleshooting",
        "status": "error",
        "reason": "Source file not found: docs/TROUBLESHOOT.md"
      }
    ]
  }
  ```

  Field requirements:
  - title: "{purpose} — {target basename or URL host}"
  - category: always "user-manual" in v1
  - extraction_id: matches session folder name
  - quality_score: overall from §2 (float, 2dp)
  - quality_label: from §3 classification
  - sections[]: one entry per accepted section, ordered by section_id
  - excluded_sections[]: one entry per error/skipped section
  - source_summary: subset of input_analysis from Phase 1
  - created_at: ISO 8601 timestamp at packaging time
  - schema_version: "1.0" (matches manifest convention)

## §5. Article File Format

  File name: `section-{NN}-{slug}.md` (matches checkpoint content naming)
  Location: `.kb-intake/{extraction_id}/section-{NN}-{slug}.md`

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

  Encoding: UTF-8, no BOM. All article files and .kb-index.json.

## §6. extraction_report.md Template

  Location: `.kb-intake/{extraction_id}/extraction_report.md`

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
  | Re-running Phase 5 | Idempotent: overwrite .kb-intake/{extraction_id}/ |
  | .kb-intake/ folder missing | Create x-ipe-docs/knowledge-base/.kb-intake/ automatically |
  | Packed content file missing | Mark section "error" in index, add to excluded_sections |
```

---

### D. Output Result Field Schema

The Output Result section in SKILL.md gains these fields (replacing the future-field placeholder):

```yaml
# Phase 5 outputs (FEATURE-050-E)
extraction_status: "complete | partial | failed"
  # complete = all sections accepted and packaged
  # partial  = some sections accepted, some error/skipped
  # failed   = zero sections accepted
quality_score: 0.0           # 0.0–1.0, overall quality score (2 decimal places)
quality_label: "high | acceptable | low"
kb_output_path: "x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/"
task_output_links:
  - "x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/.kb-index.json"
  - "x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/extraction_report.md"
  - ".checkpoint/session-{timestamp}/manifest.yaml"
```

**Mapping to ACs:**
- `extraction_status` → AC-050E-22 (complete/partial/failed logic)
- `quality_score` + `quality_label` → AC-050E-22 (overall quality in output)
- `task_output_links[]` → AC-050E-23 (paths to index, report, manifest)
- `kb_output_path` → AC-050E-13 (intake folder location)

---

### E. Manifest Updates (Phase 5 additions)

Phase 5 adds these fields to `manifest.yaml` (written by Step 5.1):

```yaml
phase_5:
  status: "scored | packaged | complete"
  started_at: "ISO 8601"
  completed_at: "ISO 8601"
  overall_quality_score: float    # 0.0–1.0, 2dp
  quality_label: "high | acceptable | low"
  kb_output_path: "x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/"
  per_section_quality:
    - section_id: int
      slug: "string"
      quality_score: float        # 0.0–1.0, 2dp
      quality_flag: "low | null"
      dimensions:
        completeness: float
        accuracy: float
        structure: float
        freshness: float
```

---

### F. Implementation Sequence

Step-by-step order of edits to implement FEATURE-050-E:

```
Step 1: Create reference file
  → .github/skills/.../references/output-quality-heuristics.md
  → Contains: scoring algorithm (§1), aggregation (§2), thresholds (§3),
    .kb-index.json schema (§4), article format (§5), report template (§6),
    edge cases (§7)
  → No line limit (reference files unconstrained)

Step 2: Replace Phase 5 Step 5.1 stub in SKILL.md (lines 358–360)
  → Delete: "Status: 🔜 NOT IMPLEMENTED" stub
  → Insert: Step 5.1 Quality Scoring (~14 lines)

Step 3: Replace Phase 5 Step 5.2 + old completion stub (lines 364–372)
  → Delete: old Step 5.2 Complete block
  → Insert: Step 5.2 Package KB Articles & Report (~16 lines)

Step 4: Replace Phase 6 stub (lines 376–386)
  → Delete: old Step 6.1 + 6.2 placeholders
  → Insert: Phase 6 Completion & Cleanup (~12 lines)

Step 5: Compress Phase Definitions section
  → Phase 3 definition: 8 lines → 2 lines (implemented)
  → Phase 4 definition: 8 lines → 2 lines (implemented)
  → Phase 5 definition: 9 lines → 2 lines (implemented)
  → Reclaim ~19 lines

Step 6: Update Output Result section
  → Replace future-field placeholder with Phase 5 output fields
  → Net +5 lines

Step 7: Update DoD section
  → Add Phase 5 + Phase 6 DoD items
  → Net +2 lines

Step 8: Update metadata
  → Frontmatter: Version 1.3.0 → 1.4.0, Feature → FEATURE-050-E
  → 🎯 Implemented Phases: remove "NOT Yet Implemented" line
  → Execution Flow table: Phase 5 status → ✅

Step 9: Verify line count
  → Target: ≤ 503 lines (within tolerance)
  → Run: wc -l SKILL.md

Step 10: Validate coherence
  → Phase 5 steps reference output-quality-heuristics.md correctly
  → Quality formula matches AC-050E-06
  → .kb-index.json schema matches AC-050E-14
  → Report template matches AC-050E-19
  → All 24 ACs traceable to deliverables (cross-check Part 1 table)
```

---

### G. Design Decisions (DAO — Autonomous)

> The following decisions were made under `dao-represent-human-to-interact` mode.

**DD-1: Accuracy Formula — Inverse Iteration Count**
The spec says `accepted_iterations / total_iterations` (AC-050E-03). For a section accepted on iteration 2 out of 3 max, this means `1/2 = 0.5` (it took 2 tries). For first-pass acceptance: `1/1 = 1.0`. This naturally penalizes sections that required more validation rounds while rewarding clean first-pass results. We use `1 / iterations_validated` (where iterations_validated is the count of times the section went through validation, minimum 1).

**DD-2: Freshness Linear Decay Window — 90 to 365 Days**
The spec (AC-050E-05) says "1.0 for files modified within 90 days, linearly decaying to 0.0 at 365 days." This is a simpler model than the original tiered approach (0–30, 31–90, 91–180 bands). The linear decay is cleaner: `freshness = max(0, (365 - days_old) / 275)` for days > 90, clamped to 1.0 for days ≤ 90. This matches the spec exactly and is deterministic.

**DD-3: BR-2 — Excluded Sections as 0.0 in Overall Mean**
The spec's BR-2 states excluded sections count as 0.0. This means `overall_score = sum(accepted_scores + zeros_for_excluded) / total_section_count`. This penalizes extractions with many failures, accurately reflecting knowledge coverage gaps.

**DD-4: Report Sort — Quality Ascending**
AC-050E-20 requires ascending sort (lowest first). This follows the "worst first" pattern from the spec's DN-6, matching the FEATURE-050-D design precedent for error-first reporting.

**DD-5: Extraction ID = Session Folder Name**
Per BR-3, `extraction_id` matches the session ID (e.g., `session-20260317-143022`). This ensures 1:1 mapping between checkpoint sessions and output folders, simplifying audit trails.

**DD-6: Cleanup Scope — extracted/ + feedback/ Only**
AC-050E-24 specifies removing "extracted/" and "feedback/" while preserving manifest, packed/, and collection-template.md. Note: the checkpoint folder uses `content/` not `extracted/` for Phase 2 output. The cleanup targets `content/` (raw extraction) and `feedback/` (validation iterations), since `packed/` contains the final validated versions used by articles.

---

### H. Edge Cases & Error Handling

| Edge Case | Expected Behavior | AC Reference |
|-----------|-------------------|--------------|
| All sections accepted, high quality | Package all, "high" label, no warnings | AC-050E-09 |
| Some sections error/skipped | Package accepted; excluded in index; 0.0 in mean | AC-050E-17, BR-2 |
| Zero accepted sections | extraction_status "failed"; report with errors only | AC-050E-22 |
| Single section extraction | overall_score = section score | AC-050E-07 |
| No source modification dates (URLs) | Freshness = 0.5 | AC-050E-05 |
| Section with 0 ACs (implicitly accepted) | Completeness = 1.0 | AC-050E-02 (Phase 3 convention) |
| Section accepted on first pass | Accuracy = 1.0 (1/1 iterations) | AC-050E-03 |
| Re-running Phase 5 on same content | Idempotent: overwrite .kb-intake folder | NFR-4 |
| .kb-intake/ folder doesn't exist | Create automatically | AC-050E-13 |
| Packed content file missing unexpectedly | Treat as "error" section, add to excluded | Defensive handling |
| Manifest missing phase_3 data | Score completeness/accuracy as 0.0, warn | Defensive handling |

---

### I. Proposed SKILL.md Content (Combined View)

Below shows the exact flow of Phase 5 + Phase 6 as they will appear in the final SKILL.md, in context:

```markdown
### Phase 5: 笃行之 — Practice Earnestly (KB Output & Quality Scoring)

#### Step 5.1 — Quality Scoring

**CONTEXT — Gather Scoring Inputs (Deterministic Only — No LLM):**
- Read manifest `phase_3.per_section[]`: for each section, extract `criteria_met`, `criteria_total`, `iterations_validated`, `validation_status`
- Read collection template: count prescribed sub-sections (H3 headings / extraction prompts) per section
- Read packed content files: count present sub-sections (H2/H3 headings matching template) per section
- Read source file modification dates from `source_metadata` (if local); for URLs default freshness to 0.5

**DECISION — Classify Quality Threshold:**
- Compute per-section `section_quality_score` (see reference for 4-dimension formula)
- Compute `overall_quality_score` = arithmetic mean of section scores (exclude error/skipped from mean; count as 0.0 per BR-2)
- Classify: ≥ 0.80 → "high"; 0.50–0.79 → "acceptable"; < 0.50 → "low"
- IF "acceptable" → log warning with lowest-scoring sections; IF "low" → log warning with sections below 0.50
- Per-section: IF section score < 0.50 → set `quality_flag: "low"` in manifest

**ACTION:** Compute all scores per reference formulas. Write quality results to manifest: `phase_5.quality_scores[]`, `phase_5.overall_quality_score`, `phase_5.quality_label`. Scoring is non-blocking — always proceed to Step 5.2.

**VERIFY:** ✅ Every section has `section_quality_score` (0.0–1.0, 2dp); overall score and label set; identical inputs → identical scores

**REFERENCE:** `references/output-quality-heuristics.md` §1–§3

---

#### Step 5.2 — Package KB Articles & Report

**CONTEXT:** Read all packed content files from `.checkpoint/session-{timestamp}/packed/`. Read quality scores from Step 5.1. Read manifest for provenance data (target, loaded_tool_skill, timestamps). Derive `extraction_id` from session folder name.

**DECISION — Determine Output Path & Status:**
- Output folder: `x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/`
- IF zero accepted sections → extraction_status = "failed" (still generate report)
- IF all accepted → extraction_status = "complete"
- IF some accepted, some error/skipped → extraction_status = "partial"

**ACTION — Write Output Files:**
1. Create output folder (and `.kb-intake/` parent if needed)
2. Generate `.kb-index.json` per reference schema: title, category, extraction_id, quality_score, quality_label, sections[], excluded_sections[], source_summary, created_at, schema_version "1.0"
3. For each accepted section: write article `.md` with YAML frontmatter (section_id, title, quality_score, quality_dimensions, provenance) + validated content from packed files
4. For error/skipped sections: add to `excluded_sections[]` in index with status and reason; no article file
5. Generate `extraction_report.md`: Summary, Per-Section Scores (sorted quality ascending), Validation Statistics, Error Log, Provenance
6. All files UTF-8, no BOM

**VERIFY:**
- ✅ `.kb-index.json` exists with all required fields; article count matches accepted sections
- ✅ `extraction_report.md` exists with 5 sections; per-section table sorted ascending
- ✅ Excluded sections in index but no article files

**REFERENCE:** `references/output-quality-heuristics.md` §4–§7

---

### Phase 6: 继续执行 — Continue Execution

#### Step 6.1 — Finalize & Clean Up

**ACTION — Manifest & Output Result:**
1. Update manifest: `status` → "complete", `completed_at` → ISO 8601 timestamp
2. Populate Output Result: `extraction_status`, `quality_score`, `quality_label`, `kb_output_path`
3. Set `task_output_links[]`: .kb-index.json path, extraction_report.md path, manifest path
4. Update task-board.md: task status → completed

**ACTION — Cleanup Temporary Files:**
5. Remove `{checkpoint_path}/content/` and `{checkpoint_path}/feedback/` directories
6. Preserve: `manifest.yaml`, `packed/` content files, `collection-template.md`

**VERIFY:** ✅ Manifest "complete"; Output Result populated; temp dirs removed; packed/ + manifest preserved

#### Step 6.2 — Route Next Action

**DECISION:** DAO mode → log completion, future: invoke `x-ipe-tool-kb-librarian`; manual → present to human.
```

---

## Design Change Log

| Date | Phase | Change Summary |
|------|-------|----------------|
| 2026-03-17 | Initial Design | Technical design for KB Intake Output & Quality Scoring (Phase 5 + Phase 6). Defines Step 5.1 Quality Scoring (4 dimensions: completeness=0.40, accuracy=0.30, structure=0.20, freshness=0.10; threshold classification high/acceptable/low; deterministic, no LLM). Defines Step 5.2 KB Article Packaging (.kb-index.json schema, per-section article frontmatter with provenance, extraction_report.md with 5 sections sorted quality ascending, excluded_sections handling). Defines Phase 6 Completion (manifest finalize, Output Result population, temp file cleanup preserving manifest + packed). Line budget: net +6 lines (497 → ~503, within tolerance). New reference file `output-quality-heuristics.md` holds scoring formulas, schemas, templates, edge cases. All 24 ACs mapped to deliverables. Design decisions: accuracy = 1/iterations_validated, freshness linear decay 90–365 days, excluded sections as 0.0 in mean, extraction_id = session folder name, cleanup targets content/ + feedback/. |
