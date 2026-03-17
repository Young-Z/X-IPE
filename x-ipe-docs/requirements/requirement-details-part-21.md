## EPIC-050: Application Knowledge Extraction

> Version: 1.0
> Source Idea: [IDEA-008 — Knowledge Extraction](x-ipe-docs/ideas/wf-008-knowledge-extraction/refined-idea/idea-summary-v1.md)
> Depends On: EPIC-049 (Knowledge Base infrastructure — `.intake/` pipeline, AI Librarian)
> External Dependency: `x-ipe-tool-knowledge-extraction-user-manual` tool skill (separate EPIC, must be built first)

### Project Overview

Build an AI-powered **extractor skill** (`x-ipe-task-based-application-knowledge-extractor`) that accepts any application source — local file paths, URLs, or running applications — auto-detects the input type and format, and progressively extracts structured knowledge. The extractor is the hands-on worker: it reads files, browses web pages, inspects running apps, and sends extracted knowledge to tool skills for validation and packaging. Output feeds into the EPIC-049 KB `.intake/` pipeline for librarian processing.

This EPIC covers the **extractor orchestrator only**. The user-manual tool skill (`x-ipe-tool-knowledge-extraction-user-manual`) that provides playbook templates, validates extracted knowledge, and packs approved content is a separate deliverable.

### User Request

Create a two-tier AI skill system for structured knowledge extraction from applications. The extractor skill does the hands-on work of reading sources and extracting knowledge. It collaborates with tool skills (built separately) that act as source-agnostic instructors, validators, and packers. The extractor feeds results into the X-IPE knowledge base via the `.intake/` folder.

### Clarifications

| Question | Answer |
|----------|--------|
| Concurrency: one purpose at a time or parallel? | One purpose at a time (v1). Sequential processing only. |
| Error handling for inaccessible sources? | Retry automatically first, then pause and ask user how to proceed. |
| Output format? | KB `.intake/` pipeline only. No standalone file export. |
| Which tool skills for v1? | User-manual tool skill only. API-reference, architecture, runbook deferred to future EPICs. |
| Scope of this EPIC? | Extractor skill only. User-manual tool skill is a separate EPIC (external dependency). |

### High-Level Requirements

1. **Input Auto-Detection:** Accept local file paths (files or directories), URLs (web pages, documentation sites), and references to running applications. Auto-detect input type (source code repo, documentation folder, running web app, public URL) and format (markdown, code, HTML, etc.).

2. **Tool Skill Loading & Collaboration:** After input detection, load available `x-ipe-tool-knowledge-extraction-*` tool skills. Tool skills provide: (a) playbook templates defining extraction structure, (b) knowledge collection templates with per-section prompts guiding what to extract, (c) acceptance criteria for validation. The extractor NEVER generates output structure — it follows what tool skills prescribe.

3. **Hands-On Extraction:** The extractor directly reads source files, browses web pages (via Chrome DevTools MCP or similar), and inspects running applications. It performs the actual data gathering work based on guidance from loaded tool skills.

4. **File-Based Knowledge Handoff:** All knowledge exchange between extractor and tool skills uses temporary files in a `.checkpoint/` folder with file links (not inline text). This supports large extractions without context overflow. Tool skills receive file paths, validate content, and return feedback or packed output as files.

5. **Iterative Extract→Validate Loop:** Extractor sends extracted knowledge to tool skill → tool skill validates against acceptance criteria → tool skill either accepts (packs into output format) or rejects (returns feedback specifying what's missing) → extractor refines and re-extracts. Loop continues until tool skill approves.

6. **Coverage Metrics & Depth/Breadth Control:** The extractor auto-controls extraction depth vs. breadth based on coverage metrics. When coverage gaps exist in a section → go deeper (extract more detail). When entire sections are missing → go wider (discover new scope). No manual user intervention needed for switching.

7. **Checkpoint & Resume:** Support pause/resume with a checkpoint file in `.checkpoint/` folder. Checkpoint captures: current extraction state, sections completed, sections in progress, coverage metrics, and tool skill feedback history. Include `schema_version: "1.0"` from day one.

8. **Purpose-Driven Web Search:** After tool skills are loaded (not before), optionally invoke web search to research domain best practices informed by both the extraction purpose and the loaded tool skills' requirements. Web search is gated by `tools.json` configuration.

9. **KB Intake Output:** Final validated and packed output goes to `x-ipe-docs/knowledge-base/.intake/` folder for EPIC-049 AI Librarian processing. Output follows KB intake format conventions.

10. **Error Handling:** On inaccessible sources (broken URLs, permission denied, app not running): retry automatically (configurable max retries, default 3), then pause and present the issue to the user for guidance (skip source, provide alternative, abort).

11. **Quality Dual-Metric:** Each tool skill runs its own per-section critique sub-agent to validate individual sections against acceptance criteria. Additionally, maintain an overall quality score tracking coverage percentage, clarity, and completeness across all sections.

12. **Dynamic Category Selection:** Use a fixed taxonomy of extraction categories (user-manual, API-reference, architecture, runbook, configuration) but the AI selects which categories apply based on input analysis. V1 only processes user-manual category (other categories require their respective tool skills).

### Constraints

- **Single-purpose execution:** V1 processes one extraction category per run. No parallel multi-purpose extraction.
- **Tool skill dependency:** The extractor cannot produce output without at least one tool skill loaded. If no matching tool skill is found, the extractor must report the gap and halt gracefully.
- **KB pipeline only:** Output goes exclusively through `.intake/` — no standalone file export mode.
- **Skill architecture compliance:** Must follow X-IPE skill conventions: SKILL.md entry point, `.github/skills/x-ipe-task-based-application-knowledge-extractor/` folder structure, input/output YAML contracts.
- **File-based handoff:** Knowledge exchange between extractor and tool skills MUST use file links, not inline text, to prevent context overflow on large codebases.
- **App-type mixins:** When tool skills provide playbook templates, they use a base template + app-type-specific mixins (web, CLI, mobile). The extractor must detect app type to request the correct mixin.
- **Screenshot support:** For visual extraction, prioritize user-provided images. Fall back to Chrome DevTools auto-capture only when user images are unavailable.

### Open Questions

- What is the maximum codebase size (in files/LOC) the extractor should handle in v1?
- Should the extractor support incremental re-extraction (only re-process changed files since last run)?
- What is the expected quality threshold for the overall quality score before output is accepted?

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| N/A — no UI component | N/A |

---

## Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-050-A | EPIC-050 | Extractor Skill Foundation & Input Detection | v1.0 | SKILL.md skeleton, input auto-detection, tool skill loading, file-based handoff protocol | None |
| FEATURE-050-B | EPIC-050 | Source Extraction Engine | v1.0 | Hands-on extraction from files, URLs, and running apps; web search integration | FEATURE-050-A |
| FEATURE-050-C | EPIC-050 | Extract-Validate Loop & Coverage Control | v1.0 | Iterative extract→validate cycle with tool skills; depth/breadth coverage metrics | FEATURE-050-A, FEATURE-050-B |
| FEATURE-050-D | EPIC-050 | Checkpoint, Resume & Error Handling | v1.0 | Checkpoint file with schema versioning; pause/resume; retry + user-prompt error handling | FEATURE-050-A |
| FEATURE-050-E | EPIC-050 | KB Intake Output & Quality Scoring | v1.0 | Final output to .intake/ folder; per-section critique; overall quality score | FEATURE-050-C |

---

## Feature Details

### FEATURE-050-A: Extractor Skill Foundation & Input Detection

**Version:** v1.0
**Brief Description:** Create the extractor skill skeleton following X-IPE conventions and implement input auto-detection and tool skill loading — the minimum runnable foundation.

**Acceptance Criteria:**
- [ ] SKILL.md exists at `.github/skills/x-ipe-task-based-application-knowledge-extractor/` with input/output YAML contracts
- [ ] Accepts input sources: local file paths (single file or directory), URLs, running app references
- [ ] Auto-detects input type (source code repo, documentation folder, running web app, public URL) and format (markdown, code, HTML)
- [ ] Detects app type (web, CLI, mobile) for mixin selection
- [ ] Loads available `x-ipe-tool-knowledge-extraction-*` tool skills after input detection
- [ ] Receives playbook template, knowledge collection template, and acceptance criteria from loaded tool skill
- [ ] Halts gracefully with clear error message if no matching tool skill is found
- [ ] Implements file-based handoff protocol: all knowledge exchange uses `.checkpoint/` folder with file links
- [ ] Dynamic category selection: fixed taxonomy (user-manual, API-reference, architecture, runbook, configuration), AI selects applicable categories, v1 processes user-manual only

**Dependencies:**
- None (MVP foundation)

**Technical Considerations:**
- Must follow X-IPE skill conventions (SKILL.md, references/, templates/ folders)
- Input detection should use file extension analysis, directory structure heuristics, and URL pattern matching
- Tool skill loading uses glob pattern `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md`

---

### FEATURE-050-B: Source Extraction Engine

**Version:** v1.0
**Brief Description:** The hands-on extraction capability — reading files, browsing web pages, inspecting running apps, and optional web search for domain research.

**Acceptance Criteria:**
- [ ] Reads local source files (code, markdown, config, etc.) and extracts structured knowledge per collection template prompts
- [ ] Browses web pages via Chrome DevTools MCP (or similar) and extracts page content
- [ ] Inspects running applications by navigating UI flows and capturing state
- [ ] Supports user-provided screenshots; falls back to Chrome DevTools auto-capture when unavailable
- [ ] Purpose-driven web search (after tool skills loaded, gated by tools.json) researches domain best practices
- [ ] Writes extracted knowledge to temp files in `.checkpoint/` and passes file links to tool skill
- [ ] Extraction guided by tool skill's knowledge collection template (per-section prompts)

**Dependencies:**
- FEATURE-050-A: Needs skill skeleton, input detection, and tool skill loading

**Technical Considerations:**
- Web browsing requires Chrome DevTools MCP availability
- Large codebases need chunked reading strategy to avoid context overflow
- Web search gated by `x-ipe-docs/config/tools.json` configuration

---

### FEATURE-050-C: Extract-Validate Loop & Coverage Control

**Version:** v1.0
**Brief Description:** The iterative extract→validate cycle with tool skills and automatic depth/breadth switching based on coverage metrics.

**Acceptance Criteria:**
- [ ] Sends extracted knowledge (as file links) to tool skill for validation against acceptance criteria
- [ ] Tool skill returns accept (packs into output format) or reject (feedback specifying what's missing)
- [ ] On rejection: extractor refines and re-extracts based on tool skill feedback, then resubmits
- [ ] Loop continues until tool skill approves all sections
- [ ] Maintains coverage metrics: percentage of sections completed, per-section completeness score
- [ ] Auto-switches depth vs. breadth: coverage gap in section → go deeper; missing sections → go wider
- [ ] Per-section critique: tool skill runs its own critique sub-agent per section

**Dependencies:**
- FEATURE-050-A: Skill foundation and file-based handoff protocol
- FEATURE-050-B: Extraction engine provides the knowledge to validate

**Technical Considerations:**
- Coverage metric thresholds should be configurable
- Depth/breadth switching is automatic — no user intervention needed
- Must handle edge case: tool skill keeps rejecting same section (max retry limit)

---

### FEATURE-050-D: Checkpoint, Resume & Error Handling

**Version:** v1.0
**Brief Description:** Pause/resume support via checkpoint files and robust error handling with retry + user-prompt fallback.

**Acceptance Criteria:**
- [ ] Creates checkpoint file in `.checkpoint/` capturing: extraction state, sections completed, sections in progress, coverage metrics, tool skill feedback history
- [ ] Checkpoint file includes `schema_version: "1.0"` from day one
- [ ] Supports resume from checkpoint: detects existing checkpoint, restores state, continues extraction
- [ ] On inaccessible source: retries automatically (configurable max retries, default 3)
- [ ] After max retries exhausted: pauses and presents issue to user with options (skip source, provide alternative, abort)
- [ ] Checkpoint updated after each successful section extraction (incremental save)

**Dependencies:**
- FEATURE-050-A: Skill skeleton and `.checkpoint/` folder structure

**Technical Considerations:**
- Checkpoint format should be JSON/YAML for easy parsing
- Resume must handle partial section state (mid-extraction)
- Error handling must distinguish between transient (network timeout) and permanent (file not found) errors

---

### FEATURE-050-E: KB Intake Output & Quality Scoring

**Version:** v1.0
**Brief Description:** Final delivery to KB `.intake/` pipeline and holistic quality assessment across all extracted sections.

**Acceptance Criteria:**
- [ ] Validated and packed output from tool skill goes to `x-ipe-docs/knowledge-base/.intake/` folder
- [ ] Output follows EPIC-049 KB intake format conventions
- [ ] Maintains overall quality score tracking: coverage percentage, clarity, and completeness
- [ ] Quality score computed across all sections after tool skill validation
- [ ] Extraction marked complete only when all sections pass tool skill validation AND overall quality threshold met
- [ ] Single-purpose execution enforced: one extraction category per run

**Dependencies:**
- FEATURE-050-C: Needs validated output from the extract-validate loop

**Technical Considerations:**
- KB intake format must align with EPIC-049 FEATURE-049-F (AI Librarian) expectations
- Quality threshold should be configurable (default TBD in open questions)
- Output metadata should include extraction source, timestamp, category, quality score

---

## EPIC-051: User Manual Knowledge Extraction Tool Skill

> Version: 1.0
> Source: EPIC-050 external dependency — the extractor skill requires this tool skill for "user-manual" category extraction
> Depends On: EPIC-050 (Application Knowledge Extractor — consumes this skill's artifacts)
> Scope: Single feature — one tool skill, one deliverable

### Project Overview

Build a **tool skill** (`x-ipe-tool-knowledge-extraction-user-manual`) that provides domain expertise for extracting user manual knowledge from applications. This skill is NOT an extractor — it is the "instructor" that tells the extractor WHAT to look for, HOW to validate it, and HOW to structure the output.

The tool skill provides four categories of artifacts:
1. **Playbook template** — defines the section layout of a user manual (7 sections)
2. **Collection template** — extraction prompts per section (tells the extractor what to search for in source)
3. **Acceptance criteria** — per-section validation rules (pass/fail criteria for extracted content)
4. **App-type mixins** — web/cli/mobile-specific section overlays that augment the base template

### User Request

Create the tool skill referenced as an external dependency by EPIC-050. The Application Knowledge Extractor (SKILL.md) globs `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md`, matches by category, and loads artifact paths. This skill provides the "user-manual" category expertise.

### Clarifications

| Question | Answer (DAO-resolved) |
|----------|----------------------|
| What sections should a user manual cover? | 7 sections: Overview, Installation & Setup, Getting Started, Core Features, Configuration, Troubleshooting, FAQ & Reference |
| How does the extractor discover this skill? | Glob `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md`, filter by `categories: ["user-manual"]` in frontmatter |
| What operations does the extractor call? | get_artifacts (Phase 1), get_collection_template (Phase 2), validate_section (Phase 3), get_mixin (Phase 1), pack_section (Phase 5) |
| What app-type mixins are needed? | web (UI/auth/navigation), cli (commands/flags/subcommands), mobile (gestures/permissions/stores) |
| Does this skill execute extraction itself? | No — it is source-agnostic. It provides templates and validates content. The extractor does the hands-on work. |
| How are acceptance criteria structured? | Per-section checklist. Each section has 3-5 required criteria (e.g., "Installation must have copy-pasteable commands") |
| Config overrides? | web_search_enabled (default false), max_files_per_section (default 20), max_iterations (default 3) |

### High-Level Requirements

1. **Artifact Discovery Interface:** SKILL.md frontmatter declares `categories: ["user-manual"]` and artifact paths (playbook_template, collection_template, acceptance_criteria, app_type_mixins). The extractor reads these paths programmatically.

2. **Playbook Template (7-Section Base Layout):** Define the canonical structure of a user manual: Overview, Installation & Setup, Getting Started, Core Features, Configuration, Troubleshooting, FAQ & Reference. Each section has a heading and description of what content belongs there.

3. **Collection Template (Extraction Prompts):** For each of the 7 sections, provide specific extraction prompts as HTML comments telling the extractor what to search for in the source (e.g., "look for README install section, Makefile, scripts/setup.*" for Installation).

4. **Acceptance Criteria (Per-Section Validation):** For each section, define 3-5 pass/fail criteria that the extractor's validation loop checks against (e.g., "Installation must list system prerequisites with version requirements"). These drive the Phase 3 extract-validate loop.

5. **App-Type Mixins (Web/CLI/Mobile):** Three overlay templates that add app-type-specific extraction prompts and acceptance criteria to the base template: web (UI flows, auth, screenshots), CLI (commands, flags, shell completion), mobile (gestures, permissions, app stores).

6. **Operations API:** Expose 5 operations callable by the extractor: get_artifacts, get_collection_template, validate_section, get_mixin, pack_section. Each operation is documented in SKILL.md with inputs, actions, and outputs.

7. **Content Packing Guidance:** For the pack_section operation, provide formatting rules for how validated content should be structured in the final user manual output (heading hierarchy, code block formatting, cross-references).

### Constraints

- **Source-agnostic:** This skill NEVER accesses source files, URLs, or running apps directly. It only provides templates and validates content.
- **File-based handoff:** All communication with the extractor uses `.checkpoint/` file paths, not inline text.
- **500-line SKILL.md limit:** Keep SKILL.md concise; move detailed templates, prompts, and criteria to `templates/` and `references/` folders.
- **Single feature:** This is a small, focused tool skill. One feature covers all requirements — no multi-feature breakdown needed.
- **v1 scope:** User manual category only. No API-reference, architecture, or runbook templates.
- **Skill conventions:** Must follow X-IPE skill conventions (SKILL.md, references/, templates/ folders, tool skill template format).

### Open Questions

- None — scope is well-defined by EPIC-050 interface contract.

### Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| N/A — no UI component | N/A |

---

## Feature List

| Feature ID | Epic ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------|---------------|---------|-------------------|-------------------|
| FEATURE-051-A | EPIC-051 | User Manual Tool Skill | v1.0 | Complete tool skill with playbook, collection template, acceptance criteria, app-type mixins, and 5 operations | None |
