# Feature Specification: UIUX Reference Script

> Feature ID: FEATURE-052-C  
> Version: v1.0  
> Status: Refined  
> Last Updated: 03-30-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-30-2026 | Initial specification |

## Linked Mockups

N/A — CLI script, no UI mockups.

## Overview

FEATURE-052-C implements `uiux_save_reference.py`, a standalone Python script that replaces the `save_uiux_reference` MCP tool. The script validates UIUX reference input data (colors, elements, screenshots, design tokens), decodes base64 screenshots to PNG files, merges element data into `referenced-elements.json`, generates per-element HTML/CSS resource files, and produces `summarized-uiux-reference.md` and `mimic-strategy.md` documentation.

This is the most complex script in EPIC-052 due to the multi-file generation pipeline: input validation → screenshot decoding → element merge → HTML/CSS generation → markdown generation. The script uses `_lib.py` for atomic writes, path resolution, and structured output, while keeping all UIUX-specific logic self-contained.

## User Stories

1. As an **AI agent executing the uiux-reference skill**, I want to persist UIUX reference data by running a Python script, so that I no longer depend on the MCP server and Flask backend.
2. As a **skill author**, I want the script's CLI and output structure to match the existing MCP tool, so that skill migration is a drop-in replacement.
3. As a **developer**, I want incremental element merging, so that multiple collection passes accumulate data without overwriting previous results.

## Acceptance Criteria

### AC-052C-01: Input Validation & CLI Interface

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052C-01a | GIVEN a valid JSON file path WHEN `--data-file /tmp/data.json` is passed THEN the script reads and parses the JSON from that file | Unit |
| AC-052C-01b | GIVEN a valid JSON string WHEN `--data '{"version":"3.0",...}'` is passed THEN the script parses the inline JSON | Unit |
| AC-052C-01c | GIVEN neither `--data-file` nor `--data` is provided WHEN the script runs THEN it exits with code 1 and error message "No input data provided" | Unit |
| AC-052C-01d | GIVEN both `--data-file` and `--data` are provided WHEN the script runs THEN `--data-file` takes precedence | Unit |
| AC-052C-01e | GIVEN input with a missing required field (version, source_url, timestamp, idea_folder) WHEN validated THEN the script exits with code 1 and lists missing fields | Unit |
| AC-052C-01f | GIVEN input with all required fields but no data sections (colors, elements, design_tokens all empty/missing) WHEN validated THEN the script exits with code 1 and error "At least one data section must be non-empty" | Unit |
| AC-052C-01g | GIVEN `--data-file` points to a nonexistent file WHEN the script runs THEN it exits with code 2 and error "Data file not found" | Unit |
| AC-052C-01h | GIVEN `--data-file` contains malformed JSON WHEN the script runs THEN it exits with code 1 and error "Invalid JSON" | Unit |

### AC-052C-02: Idea Folder Resolution

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052C-02a | GIVEN `idea_folder` = "036. My Idea" WHEN the script runs THEN it resolves to `{project_root}/x-ipe-docs/ideas/036. My Idea/` | Unit |
| AC-052C-02b | GIVEN `idea_folder` references a nonexistent folder WHEN the script runs THEN it exits with code 2 and error "Idea folder not found: {folder}" | Unit |
| AC-052C-02c | GIVEN a valid `idea_folder` WHEN the script runs THEN it creates `uiux-references/`, `uiux-references/screenshots/`, and `uiux-references/page-element-references/resources/` subdirectories if they don't exist | Unit |

### AC-052C-03: Base64 Screenshot Decoding

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052C-03a | GIVEN an element with `screenshots.full_page = "base64:iVBOR..."` WHEN processing THEN the script decodes the base64 data, writes `{element_id}-full_page.png` to `screenshots/`, and replaces the value with `"screenshots/{element_id}-full_page.png"` | Unit |
| AC-052C-03b | GIVEN an element with multiple screenshot keys (full_page, element_crop) WHEN processing THEN each key is decoded to a separate PNG file | Unit |
| AC-052C-03c | GIVEN an element with a non-base64 screenshot value (already a path) WHEN processing THEN the value is left unchanged | Unit |
| AC-052C-03d | GIVEN a screenshot with invalid base64 data WHEN decoding fails THEN the value is set to null and processing continues (no crash) | Unit |
| AC-052C-03e | GIVEN input with no elements or no screenshots WHEN processing THEN no screenshot files are created and no errors occur | Unit |

### AC-052C-04: Referenced Elements Persistence

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052C-04a | GIVEN no existing `referenced-elements.json` WHEN elements are saved THEN a new file is created with version, source_url, timestamp, areas, and colors fields | Unit |
| AC-052C-04b | GIVEN an existing `referenced-elements.json` with area "area-1" WHEN new data contains area "area-2" THEN the merged file contains both area-1 and area-2 (incremental merge) | Unit |
| AC-052C-04c | GIVEN an existing `referenced-elements.json` with area "area-1" WHEN new data also contains area "area-1" THEN the existing area-1 is overwritten with the new data | Unit |
| AC-052C-04d | GIVEN elements with `html_css.discovered_elements` WHEN saving THEN each discovered element is converted to enriched format with `element_name`, `purpose_of_the_element`, `relationships_to_other_elements`, and `element_details` | Unit |
| AC-052C-04e | GIVEN new data has colors and the existing file also has colors WHEN merging THEN the new colors replace the existing colors | Unit |
| AC-052C-04f | GIVEN new data has no colors but existing file has colors WHEN merging THEN the existing colors are preserved | Unit |
| AC-052C-04g | GIVEN data with `static_resources` WHEN saving THEN the static_resources field is included in the output | Unit |
| AC-052C-04h | GIVEN the write operation WHEN persisting `referenced-elements.json` THEN the write is atomic (tempfile → fsync → rename) | Unit |

### AC-052C-05: Area Resource Generation (HTML/CSS)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052C-05a | GIVEN an element with `html_css.outer_html` WHEN generating resources THEN `{element_id}-structure.html` is written to `page-element-references/resources/` | Unit |
| AC-052C-05b | GIVEN an element with `html_css.computed_styles` WHEN generating resources THEN `{element_id}-styles.css` is written with a CSS selector block containing all sorted properties | Unit |
| AC-052C-05c | GIVEN an element with `html_css.computed_styles` and a `selector` field WHEN generating CSS THEN the element's selector is used as the CSS selector | Unit |
| AC-052C-05d | GIVEN an element with no `html_css` WHEN generating resources THEN no resource files are created for that element | Unit |
| AC-052C-05e | GIVEN elements with html_css data WHEN generating resources THEN the count of files saved is returned in the output | Unit |

### AC-052C-06: Summarized Reference Markdown

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052C-06a | GIVEN data with colors WHEN generating the summary THEN `summarized-uiux-reference.md` includes a Colors table with Hex, Role, and Source columns | Unit |
| AC-052C-06b | GIVEN data with no colors WHEN generating the summary THEN the Colors section shows "_No colors captured._" | Unit |
| AC-052C-06c | GIVEN elements with enriched discovered_elements WHEN generating the summary THEN each element has a section with tag, purpose, content, key styles, and resources | Unit |
| AC-052C-06d | GIVEN elements with relationships_to_other_elements WHEN generating the summary THEN an "Element Relationships" table and "Reconstruction Strategy" section are generated | Unit |
| AC-052C-06e | GIVEN elements with only computed_styles (legacy format) WHEN generating the summary THEN a Typography table is generated as fallback | Unit |
| AC-052C-06f | GIVEN data with static_resources WHEN generating the summary THEN a "Static Resources" table with Type, Source URL, Local Path, Usage columns is appended | Unit |

### AC-052C-07: Mimic Strategy Generation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052C-07a | GIVEN elements with instructions WHEN generating the strategy THEN `mimic-strategy.md` is written to `uiux-references/` with Target section listing each element's component, dimensions, and instruction | Unit |
| AC-052C-07b | GIVEN any elements WHEN generating the strategy THEN the 6-dimension validation rubric (Layout, Typography, Color Palette, Spacing, Visual Effects, Static Resources) is included with checklist items | Unit |
| AC-052C-07c | GIVEN any elements WHEN generating the strategy THEN a "Validation Criteria" section with accuracy targets (99%, 1px tolerance, 3 max iterations) is included | Unit |

### AC-052C-08: Output Compatibility

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052C-08a | GIVEN a successful save WHEN the script outputs its result THEN the JSON contains `success: true`, `referenced_elements_file`, and `screenshots_saved` | Unit |
| AC-052C-08b | GIVEN resource files were generated WHEN the script outputs THEN the JSON additionally contains `resource_files_saved` with the count | Unit |
| AC-052C-08c | GIVEN `--format text` WHEN the script outputs THEN the result is in human-readable key=value format | Unit |
| AC-052C-08d | GIVEN a validation error WHEN the script outputs THEN the JSON contains `success: false`, `error`, and `message` | Unit |

### AC-052C-09: Exit Codes & Shared Utilities

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-052C-09a | GIVEN a successful execution WHEN the script exits THEN exit code is 0 | Unit |
| AC-052C-09b | GIVEN a validation error WHEN the script exits THEN exit code is 1 | Unit |
| AC-052C-09c | GIVEN a missing idea folder or data file WHEN the script exits THEN exit code is 2 | Unit |
| AC-052C-09d | GIVEN the script WHEN importing THEN it imports from `_lib.py` for `resolve_project_root`, `atomic_write_json`, `output_result`, `exit_with_error` | Unit |
| AC-052C-09e | GIVEN the script WHEN checked for dependencies THEN it uses only Python standard library modules (base64, json, os, tempfile, argparse, pathlib, copy, datetime) plus `_lib.py` | Unit |

## Functional Requirements

- **FR-052C.01**: Accept input via `--data-file` (JSON file path) or `--data` (inline JSON string), with `--data-file` taking precedence.
- **FR-052C.02**: Validate required fields (`version`, `source_url`, `timestamp`, `idea_folder`) and at least one non-empty data section (`colors`, `elements`, `design_tokens`).
- **FR-052C.03**: Decode all `base64:`-prefixed screenshot values to PNG files in `uiux-references/screenshots/`.
- **FR-052C.04**: Merge incoming elements into `referenced-elements.json` keyed by `area_id`, supporting incremental updates across multiple invocations.
- **FR-052C.05**: Generate per-element `{id}-structure.html` and `{id}-styles.css` files from `html_css` data.
- **FR-052C.06**: Generate `summarized-uiux-reference.md` with colors table, per-area element details, relationships, and reconstruction strategy.
- **FR-052C.07**: Generate `mimic-strategy.md` with 6-dimension validation rubric.
- **FR-052C.08**: Use atomic writes (tempfile → fsync → rename) for `referenced-elements.json`.

## Non-Functional Requirements

- **NFR-052C.01**: Zero external dependencies — Python stdlib + `_lib.py` only.
- **NFR-052C.02**: Output structure identical to existing MCP tool for drop-in skill migration.
- **NFR-052C.03**: Graceful error isolation — individual screenshot decode failures don't crash the pipeline.

## Dependencies

- **FEATURE-052-A**: `_lib.py` shared utility module (resolve_project_root, atomic_write_json, output_result, exit_with_error)

## Business Rules

- **BR-01**: `referenced-elements.json` is the single source of truth — all element data is merged there.
- **BR-02**: Areas are keyed by `area_id` (`element.id`); same ID overwrites, different ID appends.
- **BR-03**: Colors from new data replace existing; absent new colors preserve existing.
- **BR-04**: Screenshot decode errors set value to `None` and continue (no pipeline abort).

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Corrupted existing `referenced-elements.json` | Treat as empty, overwrite with new data |
| Element with no `html_css` | Skip resource file generation for that element |
| Empty elements list but colors present | Save colors only, no screenshots/resources |
| Idea folder with spaces in name | Handled by Path resolution, spaces preserved |
| Very large base64 screenshots | Standard library handles; no memory limit imposed |
| No `selector` field on element | Fall back to `.{element_id}` for CSS selector |

## Out of Scope

- File locking (single-writer pattern, no concurrent access for UIUX saves)
- Static resource downloading (font/image files — done by the toolbar JS, not the persistence script)
- Schema version migration (v1→v2→v3 — handled by consuming skill, not this script)
- Direct Flask/HTTP integration (this is a standalone script)

## Technical Considerations

- Estimated 350-450 lines due to multi-file generation pipeline (largest script in EPIC-052)
- Uses `base64`, `copy`, `datetime` modules beyond standard `_lib.py` dependencies
- The `_generate_summarized_reference()` and `_generate_mimic_strategy()` methods are the most complex — they generate markdown from nested element structures
- `referenced-elements.json` atomic write uses `_lib.py`'s `atomic_write_json()` to prevent corruption
