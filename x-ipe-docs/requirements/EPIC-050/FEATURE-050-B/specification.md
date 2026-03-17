# Feature Specification: Source Extraction Engine

> Feature ID: FEATURE-050-B
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

FEATURE-050-B implements Phase 2 (审问之 — Inquire Thoroughly) of the application knowledge extractor skill. Building on the input detection and tool skill loading foundation established by FEATURE-050-A, this feature adds the actual content extraction engine — reading files, browsing web pages, inspecting running applications, and performing optional web search to gather knowledge. All extraction is guided by the collection template provided by the loaded tool skill.

The extraction engine operates section-by-section following the collection template's structure. For each section, it determines which source materials are relevant, reads them using the appropriate extraction capability (file reading, web browsing, or app inspection), synthesizes the knowledge into a coherent content file, and writes it to the checkpoint directory. This produces one `section-{N}-{slug}.md` file per collection template section — synthesized knowledge, not raw file copies.

This feature is the workhorse of EPIC-050. Without it, the extractor can detect inputs and load tool skills (FEATURE-050-A) but cannot actually gather knowledge. Downstream features depend on this output: FEATURE-050-C validates the extracted content, FEATURE-050-D handles resume/recovery, and FEATURE-050-E produces the final KB output.

## User Stories

1. As an **AI agent**, I want the extractor to **read local source files following collection template section prompts**, so that **each section of the knowledge base receives targeted, synthesized content rather than raw file dumps**.

2. As an **AI agent**, I want the extractor to **browse public web pages and extract structured content via Chrome DevTools MCP**, so that **documentation hosted online can be ingested without manual copy-paste**.

3. As an **AI agent**, I want the extractor to **navigate a running web application's UI flows and capture state**, so that **the extracted knowledge reflects actual application behavior, not just source code**.

4. As an **AI agent**, I want the extractor to **perform purpose-driven web searches when enabled**, so that **domain-specific context (e.g., framework conventions, API docs) enriches the extracted knowledge**.

5. As an **AI agent**, I want the extractor to **handle user-provided screenshots as priority visual evidence and fall back to Chrome DevTools auto-capture when available**, so that **visual content is included where relevant and gracefully skipped for non-UI inputs**.

6. As an **AI agent**, I want the extractor to **skip unreadable files with inline warnings rather than halting**, so that **one inaccessible file does not block the entire extraction session**.

## Acceptance Criteria

### AC-050B-01: Collection Template-Guided Extraction

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050B-01a | GIVEN a loaded tool skill with a collection template containing N sections WHEN the extractor begins Phase 2 THEN it reads the collection template and iterates through each section in order | Unit |
| AC-050B-01b | GIVEN a collection template section with extraction prompts WHEN the extractor processes that section THEN it identifies relevant source materials based on the section's guidance and input_type | Unit |
| AC-050B-01c | GIVEN relevant source materials are identified for a section WHEN the extractor extracts content THEN it synthesizes knowledge into a single `content/section-{N}-{slug}.md` file, NOT a raw copy of source files | Unit |
| AC-050B-01d | GIVEN a collection template section that has no relevant source materials WHEN the extractor processes that section THEN it writes a content file with a note: `<!-- EXTRACTION_NOTE: No relevant sources found for this section -->` and continues to the next section | Unit |

### AC-050B-02: Local File Reading

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050B-02a | GIVEN input_type is "source_code_repo" WHEN the extractor reads files for a section THEN it reads source code, configuration, and documentation files relevant to the section's extraction prompt | Unit |
| AC-050B-02b | GIVEN input_type is "documentation_folder" WHEN the extractor reads files for a section THEN it reads markdown, text, and structured documentation files relevant to the section | Unit |
| AC-050B-02c | GIVEN input_type is "single_file" WHEN the extractor reads the file THEN it extracts content from that single file and maps it to the most relevant collection template section(s) | Unit |
| AC-050B-02d | GIVEN a file in the source is a binary file (images, compiled artifacts, archives) WHEN the extractor encounters it during reading THEN it skips the file and inserts `<!-- EXTRACTION_WARNING: Skipped {path} — binary file -->` in the content | Unit |
| AC-050B-02e | GIVEN a file path falls within `node_modules/`, `.git/`, `__pycache__/`, or `.venv/` directories WHEN the extractor encounters it during reading THEN it skips the entire directory without warning (expected exclusion) | Unit |
| AC-050B-02f | GIVEN a source file exceeds 1MB in size WHEN the extractor encounters it during reading THEN it skips the file and inserts `<!-- EXTRACTION_WARNING: Skipped {path} — file exceeds 1MB limit -->` | Unit |

### AC-050B-03: Web Browsing & Page Extraction

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050B-03a | GIVEN input_type is "public_url" WHEN the extractor processes a section THEN it browses the target URL via Chrome DevTools MCP and extracts page content relevant to the section prompt | Unit |
| AC-050B-03b | GIVEN input_type is "running_web_app" WHEN the extractor processes a section THEN it navigates to the application URL, interacts with UI flows as needed, and captures page state relevant to the section | Unit |
| AC-050B-03c | GIVEN a web page contains navigation links to sub-pages WHEN the section prompt requires deeper content THEN the extractor follows relevant links within the same domain to gather comprehensive content | Unit |
| AC-050B-03d | GIVEN a web page is unresponsive or returns an error WHEN the extractor attempts to browse it THEN it inserts `<!-- EXTRACTION_WARNING: Skipped {url} — {error_reason} -->` and continues extraction | Unit |

### AC-050B-04: Screenshot Handling

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050B-04a | GIVEN user-provided screenshots exist in the input WHEN the extractor processes a section that benefits from visual content THEN it prioritizes user screenshots over auto-capture and references them in the section content file | Unit |
| AC-050B-04b | GIVEN input_type is "running_web_app" or "public_url" AND no user screenshots are provided WHEN the extractor processes a UI-relevant section THEN it captures screenshots via Chrome DevTools MCP as fallback evidence | Unit |
| AC-050B-04c | GIVEN input_type is "source_code_repo" or "documentation_folder" AND no user screenshots are provided WHEN the extractor processes a section THEN it gracefully skips screenshot capture without warning (expected for non-UI inputs) | Unit |

### AC-050B-05: Web Search Integration

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050B-05a | GIVEN `config_overrides.web_search_enabled` is true WHEN the extractor processes a section that would benefit from external context THEN it performs purpose-driven web searches informed by the tool skill's collection template prompts | Unit |
| AC-050B-05b | GIVEN `config_overrides.web_search_enabled` is false or not set WHEN the extractor processes any section THEN it does NOT perform web searches regardless of potential benefit | Unit |
| AC-050B-05c | GIVEN web search is enabled AND a search is performed WHEN the extractor incorporates search results THEN it synthesizes findings into the section content (not raw search dumps) and attributes the source | Unit |
| AC-050B-05d | GIVEN web search is enabled WHEN the extractor constructs search queries THEN queries are purpose-driven based on the current section's extraction prompt and detected framework/language context from Phase 1 | Unit |

### AC-050B-06: Checkpoint & Manifest Updates

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050B-06a | GIVEN an extraction session with checkpoint path from Phase 1 WHEN the extractor completes a section THEN it writes the content file to `{checkpoint_path}/content/section-{N}-{slug}.md` | Unit |
| AC-050B-06b | GIVEN a section content file is written WHEN the extractor updates the manifest THEN it updates `manifest.yaml` with the section's status ("extracted"), file path, and timestamp | Unit |
| AC-050B-06c | GIVEN all collection template sections have been processed WHEN the extractor finishes Phase 2 THEN the manifest.yaml shows status for every section (either "extracted" or "skipped") and an overall Phase 2 status of "complete" | Unit |
| AC-050B-06d | GIVEN the extractor writes content to a section file WHEN passing results to the tool skill THEN it passes the file path (e.g., `content/section-01-overview.md`) and NEVER inline text content | Unit |

### AC-050B-07: Error Handling & Skip Rules

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050B-07a | GIVEN a file cannot be read due to permission denied WHEN the extractor encounters it THEN it inserts `<!-- EXTRACTION_WARNING: Skipped {path} — permission denied -->` and continues | Unit |
| AC-050B-07b | GIVEN a section has more files matching than `config_overrides.max_files_per_section` (default 50) WHEN the extractor processes the section THEN it processes only the first 50 files (sorted by relevance), inserts `<!-- EXTRACTION_WARNING: Section truncated — {total} files matched, limit is {max} -->`, and continues | Unit |
| AC-050B-07c | GIVEN multiple files are skipped during a section's extraction WHEN the content file is written THEN all skip warnings are collected at the end of the content file in a warnings block | Unit |
| AC-050B-07d | GIVEN an unexpected error occurs during extraction of a single section WHEN the error is non-fatal THEN the extractor logs the error in the manifest, marks the section as "error", and continues to the next section | Unit |

## Functional Requirements

### FR-050B-01: Collection Template Parsing

**Description:** The extractor reads and parses the collection template loaded by Phase 1 to determine the extraction plan.

**Details:**
- Input: `tool_skill_artifacts.collection_template` file path from Phase 1 output
- Process: Parse template into ordered list of sections, each with extraction prompts, scope guidance, and expected content type
- Output: Ordered section list driving the extraction loop

### FR-050B-02: Section-by-Section Extraction Loop

**Description:** The extractor iterates through collection template sections, extracting content for each one.

**Details:**
- Input: Ordered section list from FR-050B-01, input_analysis from Phase 1
- Process: For each section — identify relevant sources, read/browse/inspect as appropriate, synthesize knowledge, write content file
- Output: One `content/section-{N}-{slug}.md` file per section in checkpoint directory

### FR-050B-03: Local File Reading Engine

**Description:** The extractor reads local files for source_code_repo, documentation_folder, and single_file input types.

**Details:**
- Input: File paths from source, section extraction prompts
- Process: Filter files by skip rules (binary, node_modules, .git, __pycache__, .venv, >1MB), read relevant files, synthesize content following section prompt
- Output: Synthesized knowledge for the section, with skip warnings for excluded files

### FR-050B-04: Web Browsing Engine

**Description:** The extractor browses web pages for public_url and running_web_app input types.

**Details:**
- Input: Target URL, section extraction prompts
- Process: Navigate to URL via Chrome DevTools MCP, extract page content, follow relevant links within domain, capture screenshots when applicable
- Output: Synthesized knowledge from web content for the section

### FR-050B-05: Web Search Engine

**Description:** The extractor performs purpose-driven web searches when enabled.

**Details:**
- Input: Section extraction prompts, detected framework/language context, `config_overrides.web_search_enabled` flag
- Process: Construct targeted search queries based on section needs and input context, execute search, synthesize findings
- Output: Supplementary knowledge integrated into section content with source attribution

### FR-050B-06: Screenshot Handling Engine

**Description:** The extractor manages visual evidence through user-provided screenshots and auto-capture.

**Details:**
- Input: User-provided screenshots (if any), input_type, section relevance
- Process: Prioritize user screenshots; fall back to Chrome DevTools capture for web inputs; skip for non-UI inputs
- Output: Screenshot references embedded in section content files where applicable

### FR-050B-07: Manifest & Progress Tracking

**Description:** The extractor maintains extraction progress in the session manifest.

**Details:**
- Input: Section extraction results
- Process: After each section completes, update manifest.yaml with section status, file path, timestamp, and any warnings
- Output: Updated manifest.yaml reflecting current extraction state

## Non-Functional Requirements

### NFR-050B-01: Performance

- Section extraction should complete within a reasonable time proportional to source size (no fixed timeout per section — collection template sections are natural scope boundaries)
- File skip rules must execute before file read to avoid wasting I/O on excluded files
- The `max_files_per_section` circuit breaker (default 50) prevents runaway extraction on very large repositories

### NFR-050B-02: Robustness

- No single file failure should halt the extraction session — skip and continue is the default behavior
- No single section failure should halt the extraction session — log error, mark section as "error", continue
- Network failures during web browsing should produce warning comments, not session-ending errors
- The extractor must handle empty results gracefully (empty sections produce note comments, not errors)

### NFR-050B-03: Context Efficiency

- Content files contain synthesized knowledge, not raw file dumps — the extractor summarizes and organizes
- Skip rules prevent wasting context tokens on irrelevant content (binary files, vendor directories, oversized files)
- Web search queries are targeted and section-specific, not broad exploratory searches

## UI/UX Requirements

N/A — this is a pure skill-layer feature with no user interface.

## Dependencies

### Internal Dependencies

- **FEATURE-050-A (Extractor Skill Foundation & Input Detection):** Provides Phase 1 output consumed by Phase 2 — input_analysis, selected_category, loaded_tool_skill, tool_skill_artifacts, checkpoint_path. This is a hard dependency; Phase 2 cannot execute without Phase 1 output.

### External Dependencies

- **`x-ipe-tool-knowledge-extraction-user-manual`:** Required tool skill that provides collection template, playbook template, and acceptance criteria guiding extraction. Without this tool skill, Phase 2 has no extraction guidance.
- **Chrome DevTools MCP:** Required for web browsing and running app inspection capabilities (public_url, running_web_app input types). Available as a built-in MCP tool in the agent environment.
- **Web Search Tool:** Required for web search capability when `config_overrides.web_search_enabled` is true. Available as a built-in tool in the agent environment.

## Business Rules

- **BR-050B-01:** Extraction follows collection template section order — sections are processed sequentially, not in parallel
- **BR-050B-02:** One content file per collection template section — the extractor produces `section-{N}-{slug}.md`, never multiple files per section
- **BR-050B-03:** Content files contain synthesized knowledge — the extractor summarizes, organizes, and contextualizes; it does NOT dump raw file contents
- **BR-050B-04:** File-based handoff is mandatory — content is written to checkpoint files; inline text is never passed between extractor and tool skill
- **BR-050B-05:** Web search happens AFTER tool skill is loaded and only within section context — never as a standalone pre-extraction step
- **BR-050B-06:** Skip rules are hardcoded (not configurable): binary files, `node_modules/`, `.git/`, `__pycache__/`, `.venv/`, files >1MB
- **BR-050B-07:** The `max_files_per_section` circuit breaker defaults to 50 and is configurable via `config_overrides.max_files_per_section`
- **BR-050B-08:** User-provided screenshots always take priority over auto-captured screenshots for the same content area

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Empty repository (no readable files after skip rules applied) | Write note comments in all section files: `<!-- EXTRACTION_NOTE: No readable source files found after applying skip rules -->`. Mark sections as "empty" in manifest. |
| Public URL behind authentication or paywall | Insert warning: `<!-- EXTRACTION_WARNING: Skipped {url} — authentication required -->`. Continue with other available sources. |
| Running web app becomes unresponsive mid-extraction | Insert warning for the current section. Mark section as "partial" in manifest. Continue to next section. |
| Collection template has zero sections | Mark Phase 2 as "complete" with zero content files. Log warning in manifest. |
| Single file input mapped to multiple sections | Extract relevant portions of the file for each applicable section. Same file content may inform multiple section files. |
| Mixed input: source_code_repo with embedded docs AND a public URL | Use file reading for local files AND web browsing for the URL. Input_type from Phase 1 determines primary capability; supplementary sources discovered during extraction use appropriate capability. |
| All files in a section exceed 1MB | Write warning-only content file for that section. Mark as "skipped" in manifest. |
| Web search returns no useful results | Omit web search content from section. No warning needed — web search is supplementary. |
| Source code repo with >1000 files | Apply `max_files_per_section` circuit breaker (default 50). Process most relevant files per section, warn about truncation. |
| Collection template section slug contains special characters | Sanitize slug to lowercase alphanumeric with hyphens only for filename safety |

## Out of Scope

- **Validation loop with tool skills (FEATURE-050-C):** Phase 2 extracts content but does not validate it against acceptance criteria — that is Phase 3
- **Checkpoint resume and recovery (FEATURE-050-D):** Phase 2 writes checkpoints but does not implement resume-from-failure logic
- **KB intake output and quality scoring (FEATURE-050-E):** Phase 2 produces section content files but does not assemble or score the final knowledge base
- **Tool skill creation:** The extractor consumes tool skills; creating new tool skill categories is outside EPIC-050 scope
- **Multi-category extraction:** v1 supports one category per run; parallel multi-category extraction is deferred
- **Remote Git repository cloning:** The extractor reads local paths only; remote repository support is deferred

## Technical Considerations

- The collection template format defines sections with extraction prompts, scope guidance, and expected content types — the extractor must parse this structure reliably
- Content file naming follows `section-{N}-{slug}.md` where N is the zero-padded section index and slug is derived from the section title (sanitized to lowercase alphanumeric with hyphens)
- The manifest.yaml schema should track per-section: status (pending, in_progress, extracted, skipped, error, empty, partial), file_path, started_at, completed_at, warnings[]
- DECISION branches within the extraction step are determined by `input_analysis.input_type`: source_code_repo and documentation_folder use file reading, public_url uses web browsing, running_web_app uses web browsing + app inspection, single_file uses file reading
- Web search is a supplementary action available within any DECISION branch, not a separate step — it augments section content when enabled
- The app_type_mixins from Phase 1 output may influence extraction prompts (e.g., web app mixin adds UI flow extraction guidance)
- Skip rule evaluation order: directory exclusions first (node_modules, .git, __pycache__, .venv), then binary detection, then size check — this minimizes I/O

## Open Questions

None — all design ambiguities were resolved in DAO-109 (step structure, web search gating, chunking strategy, error handling, depth limits).
