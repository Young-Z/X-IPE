# Feature Specification: Extractor Skill Foundation & Input Detection

> Feature ID: FEATURE-050-A
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

FEATURE-050-A establishes the foundational extractor skill (`x-ipe-task-based-application-knowledge-extractor`) following X-IPE skill conventions. It provides the minimum runnable foundation: accepting user-provided input sources, auto-detecting their type and format, loading appropriate tool skills for guidance, and defining the file-based handoff protocol for knowledge exchange.

This is the MVP feature for EPIC-050. Without it, no extraction can occur — all other features (extraction engine, validation loop, checkpoint, KB output) depend on this foundation. The feature creates the skill skeleton, implements the input analysis pipeline, and establishes the collaboration contract between the extractor and tool skills.

Target users are AI agents within X-IPE that orchestrate knowledge extraction workflows. The skill is invoked by users or other skills providing a target path/URL and extraction purpose.

## User Stories

1. As an **AI agent**, I want to **provide a file path or URL and have the extractor auto-detect what kind of source it is**, so that **I don't need to manually classify input types**.

2. As an **AI agent**, I want the extractor to **automatically load the correct tool skill based on the extraction category**, so that **the extraction process follows the right playbook and acceptance criteria**.

3. As an **AI agent**, I want the extractor to **halt gracefully when no matching tool skill exists**, so that **I get a clear error message instead of undefined behavior**.

4. As an **AI agent**, I want the extractor to **detect the application type (web, CLI, mobile)**, so that **the correct app-type mixin is requested from the tool skill**.

5. As a **developer**, I want the extractor skill to **follow X-IPE skill conventions (SKILL.md, input/output YAML)**, so that **it integrates seamlessly with the existing skill ecosystem**.

## Acceptance Criteria

### AC-050A-01: Skill Skeleton & Convention Compliance

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050A-01a | GIVEN the extractor skill is created WHEN inspecting `.github/skills/x-ipe-task-based-application-knowledge-extractor/` THEN SKILL.md exists with valid input/output YAML contracts | Unit |
| AC-050A-01b | GIVEN the SKILL.md exists WHEN parsing the input parameters section THEN it declares: target (path or URL), purpose (extraction category), and optional config overrides | Unit |
| AC-050A-01c | GIVEN the SKILL.md exists WHEN parsing the output result section THEN it declares: extraction_status, loaded_tool_skills, detected_input_type, detected_app_type, checkpoint_path | Unit |

### AC-050A-02: Input Auto-Detection

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050A-02a | GIVEN a local directory path containing Python/JS source files WHEN the extractor analyzes the input THEN it detects input_type as "source_code_repo" AND identifies primary language(s) | Unit |
| AC-050A-02b | GIVEN a local directory path containing only markdown files WHEN the extractor analyzes the input THEN it detects input_type as "documentation_folder" AND format as "markdown" | Unit |
| AC-050A-02c | GIVEN a public URL (e.g., https://example.com/docs) WHEN the extractor analyzes the input THEN it detects input_type as "public_url" AND format as "html" | Unit |
| AC-050A-02d | GIVEN a reference to a running web application (e.g., localhost:3000) WHEN the extractor analyzes the input THEN it detects input_type as "running_web_app" | Unit |
| AC-050A-02e | GIVEN a single local file path (e.g., README.md) WHEN the extractor analyzes the input THEN it detects input_type as "single_file" AND format based on file extension | Unit |
| AC-050A-02f | GIVEN an input path that does not exist WHEN the extractor analyzes the input THEN it returns an error with message indicating the path is not accessible | Unit |

### AC-050A-03: App-Type Detection

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050A-03a | GIVEN a source code repo with package.json AND an HTML entry point WHEN the extractor detects app type THEN it classifies as "web" | Unit |
| AC-050A-03b | GIVEN a source code repo with a CLI entry point (argparse, click, commander) WHEN the extractor detects app type THEN it classifies as "cli" | Unit |
| AC-050A-03c | GIVEN a source code repo with mobile framework markers (React Native, Flutter, Swift) WHEN the extractor detects app type THEN it classifies as "mobile" | Unit |
| AC-050A-03d | GIVEN a documentation folder with no code markers WHEN the extractor detects app type THEN it classifies as "unknown" AND proceeds without mixin | Unit |

### AC-050A-04: Tool Skill Loading

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050A-04a | GIVEN extraction category is "user-manual" AND `x-ipe-tool-knowledge-extraction-user-manual` skill exists WHEN the extractor loads tool skills THEN it discovers and loads the skill via glob pattern `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md` | Integration |
| AC-050A-04b | GIVEN a tool skill is loaded WHEN the extractor requests guidance THEN it receives: playbook template, knowledge collection template, and acceptance criteria as file paths | Integration |
| AC-050A-04c | GIVEN extraction category is "user-manual" AND no matching tool skill exists WHEN the extractor attempts to load tool skills THEN it halts with error message: "No tool skill found for category 'user-manual'. Install x-ipe-tool-knowledge-extraction-user-manual." | Unit |
| AC-050A-04d | GIVEN multiple tool skills match the glob pattern WHEN the extractor loads tool skills THEN it selects only the one matching the current extraction category | Unit |

### AC-050A-05: Category Selection (v1: User-Provided Purpose Validation)

> **v1 Implementation Note:** In v1, category selection validates the user-provided `purpose` parameter against supported categories ("user-manual" only). AI-driven category suggestion (analyzing input to infer applicable categories) is deferred to a future version.

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050A-05a | GIVEN the fixed taxonomy defines 5 categories: user-manual, API-reference, architecture, runbook, configuration WHEN the user provides purpose="user-manual" THEN the extractor validates the purpose against supported v1 categories AND proceeds with "user-manual" | Unit |
| AC-050A-05b | GIVEN v1 only supports "user-manual" WHEN the user provides purpose="API-reference" THEN the extractor halts with: "Category 'API-reference' is not supported in v1. Supported: user-manual" AND logs the unsupported category | Unit |
| AC-050A-05c | GIVEN the user provides an unknown purpose value WHEN category validation runs THEN the extractor halts with error: "Unknown category '{purpose}'. Valid categories: user-manual, API-reference, architecture, runbook, configuration" | Unit |

### AC-050A-06: File-Based Handoff Protocol

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-050A-06a | GIVEN an extraction session starts WHEN the extractor initializes THEN it creates a `.checkpoint/` folder in the working directory | Unit |
| AC-050A-06b | GIVEN the extractor has extracted knowledge for a section WHEN it sends results to the tool skill THEN it writes content to a temp file in `.checkpoint/` AND passes the file path (not inline content) | Unit |
| AC-050A-06c | GIVEN the tool skill returns feedback WHEN the extractor reads the response THEN it reads from a file path in `.checkpoint/` (not inline content) | Unit |
| AC-050A-06d | GIVEN the `.checkpoint/` folder already exists from a previous run WHEN a new extraction starts without resume flag THEN it creates a new subfolder with timestamp to avoid conflicts | Unit |

## Functional Requirements

### FR-1: Input Source Acceptance

**Description:** The extractor accepts a target source and extraction purpose from the user.

**Details:**
- Input: `target` (string — file path, directory path, or URL), `purpose` (string — extraction category name)
- Process: Validate target exists/is reachable, classify input type and format, detect app type
- Output: `InputAnalysis` object containing: input_type, format, app_type, source_metadata

### FR-2: Tool Skill Discovery & Loading

**Description:** The extractor discovers and loads tool skills matching the extraction category.

**Details:**
- Input: Extraction category from purpose or AI selection
- Process: Glob `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md`, filter by category match, load SKILL.md
- Output: Loaded tool skill providing playbook template, collection template, and acceptance criteria

### FR-3: Handoff Protocol Initialization

**Description:** The extractor creates the file-based communication channel for knowledge exchange.

**Details:**
- Input: Working directory context
- Process: Create `.checkpoint/` folder, establish file naming conventions for knowledge chunks and feedback
- Output: Initialized checkpoint directory ready for extraction session

### FR-4: Category Selection Pipeline

**Description:** The extractor analyzes input to determine applicable extraction categories.

**Details:**
- Input: InputAnalysis from FR-1
- Process: Evaluate input against fixed taxonomy, AI ranks applicable categories, filter to v1-supported categories
- Output: Selected category (v1: user-manual only) with deferred categories logged

## Non-Functional Requirements

### NFR-1: Performance
- Input analysis should complete within 10 seconds for local paths
- URL reachability check should timeout after 15 seconds
- Tool skill loading should complete within 5 seconds

### NFR-2: Extensibility
- Adding a new extraction category requires only adding a new tool skill (no extractor code changes)
- Adding a new input type requires only extending the detection heuristics (no architectural changes)

### NFR-3: Reliability
- Input detection must handle edge cases: symlinks, empty directories, binary files, mixed-content folders
- Tool skill loading must handle: missing skills, malformed SKILL.md, permission errors

## UI/UX Requirements

N/A — this is a pure skill-layer feature with no user interface.

## Dependencies

### Internal Dependencies
- None — this is the MVP foundation feature with no internal feature dependencies

### External Dependencies
- **`x-ipe-tool-knowledge-extraction-user-manual`:** Required for v1 extraction. This tool skill is built in a separate EPIC. Without it, the extractor will detect input but cannot proceed with extraction.
- **EPIC-049 (KB infrastructure):** Required for downstream output via `.intake/` pipeline (used by FEATURE-050-E, not directly by this feature)
- **X-IPE skill framework:** Existing `.github/skills/` conventions, SKILL.md format, input/output YAML contracts

## Business Rules

- BR-1: The extractor MUST NOT generate output structure independently — it follows what tool skills prescribe
- BR-2: v1 only supports the "user-manual" extraction category; other categories are detected but logged as deferred
- BR-3: One extraction category per run — no parallel multi-category extraction
- BR-4: Tool skill loading happens AFTER input detection, not before (input type informs which tool skills to load)
- BR-5: File-based handoff is mandatory — inline text exchange between extractor and tool skills is prohibited

## Edge Cases & Constraints

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Input path is a symlink | Resolve symlink, analyze target |
| Input directory is empty | Halt with error: "Input directory is empty" |
| Input directory contains only binary files | Detect as "binary_only", log warning, attempt to find text-based files |
| URL returns 404 | Halt with error: "URL not reachable (HTTP 404)" |
| URL requires authentication | Halt with error: "URL requires authentication — provide credentials or accessible URL" |
| Mixed-content directory (code + docs + images) | Detect primary type by file count majority, list secondary types in metadata |
| Tool skill SKILL.md is malformed | Halt with error identifying the parse failure, suggest reinstalling the skill |
| Multiple extraction categories equally applicable | Select highest-priority category (user-manual > API-reference > architecture > runbook > configuration) |

## Out of Scope

- Actual file reading and content extraction (FEATURE-050-B)
- Iterative validation loop with tool skills (FEATURE-050-C)
- Checkpoint persistence and resume logic (FEATURE-050-D — this feature only creates the `.checkpoint/` folder)
- KB intake output (FEATURE-050-E)
- Web search for domain research (FEATURE-050-B)
- Error retry logic for inaccessible sources (FEATURE-050-D)
- Quality scoring (FEATURE-050-E)

## Technical Considerations

- Input detection should use file extension analysis, directory structure heuristics (presence of package.json, Cargo.toml, etc.), and URL pattern matching
- App-type detection should look for framework-specific markers (Flask/Django → web+Python, argparse/click → CLI, React Native → mobile)
- The fixed category taxonomy should be defined as a configuration constant, not hardcoded in logic, to support future extension
- The `.checkpoint/` folder naming convention should include a session identifier to support multiple concurrent extractions on different targets
- Tool skill glob pattern should be configurable but default to `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md`

## Open Questions

- Should the extractor support remote Git repositories (clone and analyze) or only local paths?
- What metadata should be captured during input analysis beyond type/format/app-type?
