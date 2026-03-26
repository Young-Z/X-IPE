# Extraction Engine Heuristics

> Reference for Phase 2 (审问之 — Inquire Thoroughly) extraction logic.

---

## Skip Rule Evaluation Order

Evaluated top-to-bottom to minimize I/O:

### 1. Directory Exclusion (Silent Skip — No Warning)

Skip entire directory trees:
- `node_modules/`, `.git/`, `__pycache__/`, `.venv/`, `dist/`, `build/`, `.tox/`, `.mypy_cache/`, `.pytest_cache/`, `.eggs/`, `*.egg-info/`

### 2. Binary File Detection (Skip with Warning)

Extensions to skip:
- **Compiled:** `.pyc`, `.pyo`, `.whl`, `.egg`, `.exe`, `.dll`, `.so`, `.dylib`, `.a`, `.o`, `.class`
- **Images:** `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.ico`, `.svg`, `.webp`
- **Fonts:** `.woff`, `.woff2`, `.ttf`, `.eot`, `.otf`
- **Archives:** `.zip`, `.tar`, `.gz`, `.bz2`, `.7z`, `.rar`
- **Documents:** `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`
- **Media:** `.mp3`, `.mp4`, `.avi`, `.mov`, `.wav`
- **Data:** `.db`, `.sqlite`, `.lock`

Warning: `<!-- EXTRACTION_WARNING: Skipped {path} — binary file -->`

### 3. Size Check (Skip with Warning)

Threshold: **1MB** (1,048,576 bytes)

Warning: `<!-- EXTRACTION_WARNING: Skipped {path} — file exceeds 1MB limit -->`

### 4. Permission Check (Skip with Warning)

Trigger: OS returns permission denied on read attempt.

Warning: `<!-- EXTRACTION_WARNING: Skipped {path} — permission denied -->`

### 5. Circuit Breaker (Truncate with Warning)

Trigger: Matched files per section exceeds `config_overrides.max_files_per_section` (default 50).
Action: Keep top 50 by relevance, discard rest.

Warning: `<!-- EXTRACTION_WARNING: Section truncated — {total} files matched, limit is {max} -->`

---

## Extraction Strategy per Input Type

### source_code_repo / documentation_folder

```
1. ENUMERATE: List all files recursively
2. EXCLUDE: Apply skip rules (directory → binary → size → permission)
3. FILTER: Match file paths/names against section extraction prompts
   - Use source_metadata (framework, language) to prioritize
   - Example: "Installation" section → setup.py, requirements.txt, Dockerfile, docs/install*
4. CIRCUIT BREAKER: If matches > max_files_per_section → take top 50
5. READ: Read file contents
6. SYNTHESIZE: Produce coherent knowledge — NOT raw file dumps
```

### public_url

```
1. NAVIGATE: Chrome DevTools navigate_page to URL
2. SNAPSHOT: take_snapshot for page content (a11y tree / text)
3. EXTRACT: Parse content matching section extraction prompts
4. FOLLOW LINKS: Navigate relevant sub-pages (max 5/section for v1, same domain only)
5. SCREENSHOT: If section is UI-relevant, take_screenshot
6. SYNTHESIZE: Combine content into section knowledge
7. ERROR: If page unresponsive → warning comment, continue
```

### running_web_app

```
1. NAVIGATE: Chrome DevTools navigate_page to app URL
2. INTERACT: Click navigation, fill forms to demonstrate functionality
3. DETECT INTERACTION PATTERNS: Classify each interactive element:
   - FORM: User fills fields → submits → sees result
   - MODAL: Click opens popup → user interacts → popup closes
   - CLI_DISPATCH: Click sends command to terminal → user must press Enter to execute
   - NAVIGATION: Click moves to different page
   - TOGGLE: Click changes state in-place
4. CAPTURE: take_snapshot after each interaction, take_screenshot for visual evidence
5. EXTRACT: Combine snapshots, screenshots, observed behavior
6. SYNTHESIZE: Describe application behavior in section context
7. ERROR: If app unresponsive → warning, mark section "partial"
```

#### CLI_DISPATCH Pattern (CRITICAL)

When a UI element dispatches a command to a terminal or system process:
```
MUST document ALL of the following:
  1. What terminal/system receives the command (e.g., "integrated terminal", "system shell")
  2. That the user MUST press Enter to execute the command
  3. What the expected terminal output looks like (exact text or pattern)
  4. How to know when execution completes (e.g., "prompt returns", "success message appears")
  5. What to do if the command fails (error messages, troubleshooting)

Example — GOOD:
  "Click 'Run Build'. This copies a build command to the integrated terminal.
   Press Enter to execute. You should see 'Build completed successfully' after
   10-30 seconds. If you see 'Error:', check that all dependencies are installed."

Example — BAD:
  "Click 'Run Build' to build the project."
  (Missing: terminal, Enter, expected output, completion signal)
```

### single_file

```
1. READ: Read the single file content
2. MAP: For each collection template section, identify relevant portions
3. SYNTHESIZE: Extract section-relevant knowledge
4. NOTE: Same file content may inform multiple section files
```

---

## Collection Template Parsing

```
Input: tool_skill_artifacts.collection_template (file path from Phase 1)

Expected structure (markdown):
  ## Section 1: Overview
  <!-- extraction_prompt: What does the application do? -->
  <!-- scope: README, main entry point, about page -->

  ## Section 2: Installation
  <!-- extraction_prompt: How to install? Dependencies? -->
  <!-- scope: setup files, requirements, Dockerfiles -->

Parsing rules:
  - Each H2 (##) heading = one section
  - Section index (N) = sequential from 1, zero-padded to 2 digits
  - Slug = heading text → lowercase, alphanumeric + hyphens only
  - Extraction prompts in HTML comments guide what to look for
  - Scope hints in HTML comments suggest relevant files/pages
```

---

## Section-to-File Mapping

```
output_file = {checkpoint_path}/content/section-{NN}-{slug}.md

Examples:
  Section 1: "Overview"      → content/section-01-overview.md
  Section 2: "Installation"  → content/section-02-installation.md
  Section 3: "Usage Guide"   → content/section-03-usage-guide.md
```

---

## Content File Format

```markdown
# {Section Title}

<!-- Generated by: x-ipe-task-based-application-knowledge-extractor Phase 2 -->
<!-- Section: {N} | Source: {input_type} | Files read: {count} -->

{Synthesized knowledge content — organized, coherent, contextual}

<!-- Warnings collected at END of content file: -->
<!-- EXTRACTION_WARNING: Skipped src/vendor/large.min.js — file exceeds 1MB limit -->
```

If no relevant sources found for a section:
```markdown
# {Section Title}

<!-- Generated by: x-ipe-task-based-application-knowledge-extractor Phase 2 -->
<!-- EXTRACTION_NOTE: No relevant sources found for this section -->
```
Mark section status as "empty" in manifest.

---

## Screenshot Handling Priority Chain

```
Per section, in order:
  1. User-provided: Check for images in target directory or user-specified paths
     → Reference: ![description](relative/path/to/image.png)
  2. Auto-capture: Chrome DevTools take_screenshot (running_web_app or public_url only)
     → Save to: {checkpoint_path}/screenshots/{section_nn}-{step_nn}-{description}.png
  3. Graceful skip: For source_code_repo/documentation_folder/single_file
     → No screenshots expected — skip silently (no warning)
```

### Action-Level Screenshot Strategy (running_web_app / public_url)

```
For workflow-heavy sections, capture screenshots at EACH STEP, not just per feature:

Section 3 (Getting Started / Quick Start):
  → Screenshot at key milestone steps (e.g., after initial setup, first success)

Section 4 (Core Features):
  → Screenshot of each feature's PRIMARY UI state
  → One screenshot per feature showing the main interaction surface

Section 5 (Workflows / Scenarios):
  → Screenshot at EACH STEP of the workflow:
     - BEFORE: the UI state before the action (what the user should see)
     - AFTER: the UI state after the action (confirming the expected outcome)
  → This is CRITICAL for followability — the reader must be able to
     compare their screen to the screenshot at every step

Naming convention:
  screenshots/{section_nn}-{step_nn}-{description}.png
  Examples:
    screenshots/05-01-click-new-project-button.png
    screenshots/05-02-fill-project-name-field.png
    screenshots/05-03-project-created-confirmation.png

Reference in content:
  ![Step 1: Click New Project](screenshots/05-01-click-new-project-button.png)
```

---

## Web Search Integration

```
Gate:    config_overrides.web_search_enabled == true
Timing:  AFTER primary extraction per section (supplementary, not primary)

Query construction:
  - Base: section extraction prompt keywords
  - Context: source_metadata.framework + primary_language
  - Scope: purpose-driven (e.g., "Flask installation best practices")

Integration:
  - Synthesize INTO section content (not a separate block)
  - Attribute sources: "According to [Flask docs](url), ..."
  - Web search supplements — does NOT replace local extraction
  - No useful results → silently omit (no warning)
```

---

## Content Synthesis Guidelines

"Synthesize, not dump" means:
1. **Organize:** Group related information logically (install steps in order, config options in categories)
2. **Contextualize:** Explain WHY and WHEN, not just WHAT (e.g., "This env var controls the database connection used in production deployments")
3. **Summarize:** Don't copy entire files — extract relevant portions and explain them
4. **Cross-reference:** Connect information across files (e.g., "The routes defined in `app.py` correspond to the API endpoints documented in `docs/api.md`")
5. **Fill gaps:** If information is implicit in code, make it explicit in prose

---

## Manifest Update Schema (Phase 2)

```yaml
# Phase 2 additions to manifest.yaml
status: "phase_2_complete"  # from "initialized" → "extracting" → "phase_2_complete"
extraction_started_at: "ISO 8601"
extraction_completed_at: "ISO 8601"
sections:
  - id: 1
    title: "string"
    slug: "string"
    status: "extracted | skipped | empty | error | partial"
    content_file: "content/section-01-slug.md"
    started_at: "ISO 8601"
    completed_at: "ISO 8601"
    files_read: int
    warnings: int
    error_message: "string | null"  # populated when status == "error" or "partial"
    screenshots: []
total_sections: int
sections_extracted: int
sections_skipped: int
sections_error: int
total_warnings: int
web_search_used: bool
```

---

## Edge Cases

| Edge Case | Behavior |
|-----------|----------|
| Empty repo (no readable files) | Write note in all section files, mark sections "empty" |
| URL behind authentication | Warning, continue with other sources |
| App unresponsive mid-extraction | Warning for current section, mark "partial", continue |
| Zero sections in template | Phase 2 "complete" with zero content files |
| Single file → multiple sections | Extract relevant portions per section (expected) |
| All files in section >1MB | Warning-only content file, mark "skipped" |
| Web search returns nothing | Silently omit (supplementary) |
| >1000 files in source | Circuit breaker: top 50/section by relevance |
