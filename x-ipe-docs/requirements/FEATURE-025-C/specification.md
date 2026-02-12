# Feature Specification: KB Manager Skill

> Feature ID: FEATURE-025-C  
> Version: v1.0  
> Status: Refined  
> Last Updated: 02-12-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-12-2026 | Initial specification |

## Linked Mockups

N/A — This is a backend/skill feature. UI integration (processing indicator) is defined in FEATURE-025-B.

## Overview

**What:** The KB Manager Skill is an AI-powered Copilot skill that processes files in the Knowledge Base landing folder. It classifies files into topics, generates markdown summaries, reorganizes topic structures, and searches the knowledge base index. It bridges the gap between raw file uploads (FEATURE-025-B) and organized, AI-summarized knowledge topics (FEATURE-025-D).

**Why:** Without automated processing, users must manually organize uploaded files into topics and write summaries themselves. The KB Manager Skill leverages AI to analyze file content, suggest topic classifications, and generate concise markdown summaries — turning a collection of raw files into structured, searchable knowledge.

**Who:**
- End users who upload files to the Knowledge Base and want them organized
- AI agents (Copilot) that invoke the skill via trigger phrases
- Developers building downstream features (025-D Topics & Summaries, 025-E Search & Preview)

## User Stories

### US-1: Classify Landing Files
As a user, I want to classify files in the landing folder into topics, so that my knowledge base is organized by subject area.

### US-2: Generate Summaries
As a user, I want AI-generated markdown summaries of my topic files, so that I can quickly understand the content without reading every document.

### US-3: Process via Copilot
As a user, I want to trigger KB processing through Copilot trigger phrases, so that I can manage my knowledge base conversationally.

### US-4: Process via UI
As a user, I want to click "Process Selected" in the KB landing view to process specific files, so that I can selectively organize my knowledge.

### US-5: Search Knowledge
As a user, I want to search across my knowledge base index, so that I can find relevant files and summaries quickly.

### US-6: Reorganize Topics
As a user, I want to reorganize my knowledge base topics, so that I can restructure knowledge as my understanding evolves.

## Acceptance Criteria

### 1. Classification

| # | Acceptance Criteria | Verification |
|---|---------------------|--------------|
| AC-1.1 | Processing MUST be triggered manually by user (click "Process" or Copilot command) | Trigger processing → skill starts, no auto-processing |
| AC-1.2 | Skill MUST analyze content type and text of selected landing items | Select files → process → skill reads file content |
| AC-1.3 | Skill MUST suggest topic classification for each file (AI suggestion) | Process files → topic suggestions returned (e.g., "machine-learning", "api-design") |
| AC-1.4 | User MUST be able to confirm or modify suggested topic before classification | Suggestion shown → user confirms "Yes" or types new topic → classification proceeds |
| AC-1.5 | On confirmation, skill MUST move files from `landing/` to `topics/{topic}/raw/` | Confirm topic → file moved from `landing/test.pdf` to `topics/machine-learning/raw/test.pdf` |
| AC-1.6 | Skill MUST create topic folder structure if it doesn't exist (`topics/{topic}/raw/`) | New topic → folder created automatically |
| AC-1.7 | Skill MUST update `topics/{topic}/metadata.json` after classification | File moved → metadata.json updated with new file count, last_updated |
| AC-1.8 | Skill MUST update `index/file-index.json` with new file paths and topic assignments | After move → index reflects new path and `"topic": "{topic-name}"` |

### 2. Summary Generation

| # | Acceptance Criteria | Verification |
|---|---------------------|--------------|
| AC-2.1 | Skill MUST generate a markdown summary for each topic after classification | Process files into topic → `processed/{topic}/summary-v1.md` created |
| AC-2.2 | Summaries MUST be versioned (v1, v2, v3...) — never overwrite previous versions | Process again → `summary-v2.md` created, `summary-v1.md` preserved |
| AC-2.3 | Summary MUST include: title, topic name, file list, key concepts extracted from files, generation date | Read summary → all sections present |
| AC-2.4 | Summary MUST be generated using AI (LLM) by reading file contents | Summary contains accurate concepts from file content, not just filenames |
| AC-2.5 | For non-text files (images, binary), summary MUST note "Binary file — content not analyzed" | Upload image → summary lists it as binary, no hallucinated content |
| AC-2.6 | Summary generation MUST be idempotent for the same set of files (re-processing creates new version, doesn't corrupt existing) | Process same topic twice → v1 and v2 both valid |

### 3. Copilot Skill Interface

| # | Acceptance Criteria | Verification |
|---|---------------------|--------------|
| AC-3.1 | Skill MUST be registered as an X-IPE skill (`.github/skills/` folder with SKILL.md) | Skill folder exists with valid SKILL.md frontmatter |
| AC-3.2 | Skill MUST support `classify` command — moves landing items to suggested topics | Copilot: "classify landing items" → files classified |
| AC-3.3 | Skill MUST support `process` command — generates summaries for specified topic | Copilot: "process topic machine-learning" → summary generated |
| AC-3.4 | Skill MUST support `search` command — queries index and returns results | Copilot: "search knowledge for API design" → relevant files listed |
| AC-3.5 | Skill MUST support `reorganize` command — restructures topics with summary | Copilot: "reorganize knowledge base" → topics restructured |
| AC-3.6 | Skill trigger phrases MUST be documented in SKILL.md description | SKILL.md contains trigger phrases |

### 4. REST API Endpoints

| # | Acceptance Criteria | Verification |
|---|---------------------|--------------|
| AC-4.1 | `POST /api/kb/process` MUST accept list of file paths and trigger classification | POST with `{"paths": ["landing/test.md"]}` → processing starts |
| AC-4.2 | `POST /api/kb/process` MUST return classification suggestions before moving files | Response includes `{"suggestions": [{"file": "test.md", "topic": "api-design"}]}` |
| AC-4.3 | `POST /api/kb/process/confirm` MUST accept confirmed classifications and execute moves | POST with confirmed mappings → files moved, summaries generated |
| AC-4.4 | `POST /api/kb/process/cancel` MUST cancel an in-progress operation | POST cancel → processing stops, remaining files stay in landing |
| AC-4.5 | `GET /api/kb/search?q={query}` MUST return matching files from index | GET with query → list of matching file entries |
| AC-4.6 | `POST /api/kb/reorganize` MUST trigger topic reorganization | POST → topics restructured with summary of changes |
| AC-4.7 | All endpoints MUST return proper error responses (400, 404, 500) with descriptive messages | Invalid input → 400 with message; server error → 500 |

### 5. Processing Indicator Integration

| # | Acceptance Criteria | Verification |
|---|---------------------|--------------|
| AC-5.1 | Processing MUST trigger the processing indicator bar in KB landing view (AC-7.1 from 025-B) | Start processing → indicator bar appears with spinner |
| AC-5.2 | Processing indicator MUST show descriptive text ("Processing N files...") | During processing → text shows file count |
| AC-5.3 | Cancel button in indicator MUST call `POST /api/kb/process/cancel` | Click Cancel → processing stops |
| AC-5.4 | After processing completes, indicator MUST hide and file grid MUST refresh | Processing done → indicator gone, grid shows updated state |

### 6. Error Handling

| # | Acceptance Criteria | Verification |
|---|---------------------|--------------|
| AC-6.1 | If AI classification fails, skill MUST fall back to "uncategorized" topic | AI unavailable → files moved to `topics/uncategorized/raw/` |
| AC-6.2 | If file move fails (permission, disk full), skill MUST report error and leave file in landing | Move fails → error message, file stays in landing |
| AC-6.3 | If summary generation fails, skill MUST still complete classification (partial success) | Summary fails → files moved to topic, error noted, no summary |
| AC-6.4 | Processing MUST be atomic per file — failure on one file MUST NOT affect others | File 3 of 5 fails → files 1,2,4,5 processed, file 3 error reported |

## Functional Requirements

### FR-1: Classification Engine
- **Input:** List of file paths in landing folder
- **Process:** Read file content (text extraction for supported types), send to AI for topic suggestion, collect suggestions
- **Output:** List of `{file, suggested_topic, confidence}` tuples

### FR-2: File Movement
- **Input:** Confirmed `{file, topic}` mappings
- **Process:** Create topic folder if needed, move file from `landing/` to `topics/{topic}/raw/`, update metadata.json, update file-index.json
- **Output:** List of moved files with new paths

### FR-3: Summary Generation
- **Input:** Topic name with files in `topics/{topic}/raw/`
- **Process:** Read all raw files, extract key content, send to AI for summarization, write `processed/{topic}/summary-vN.md`
- **Output:** Summary file path and version number

### FR-4: Search
- **Input:** Search query string
- **Process:** Search file-index.json entries by name, path, keywords, and topic
- **Output:** List of matching file entries with relevance ranking

### FR-5: Reorganization
- **Input:** Reorganize command (optionally with specific topics)
- **Process:** Analyze all topics, suggest merges/splits/renames, execute on confirmation
- **Output:** Change summary listing what was reorganized

## Non-Functional Requirements

| # | Requirement | Target |
|---|-------------|--------|
| NFR-1 | Classification response time | < 10 seconds for up to 10 files |
| NFR-2 | Summary generation time | < 30 seconds per topic |
| NFR-3 | Search response time | < 500ms for index queries |
| NFR-4 | Maximum file content read size | 1MB per file (truncate larger files for AI analysis) |
| NFR-5 | AI token budget | Configurable, default 4000 tokens per classification request |
| NFR-6 | Tracing | All service methods MUST use `@x_ipe_tracing()` decorator |

## UI/UX Requirements

This feature is primarily backend/skill. UI integration is limited to:

1. **Processing Indicator** (defined in FEATURE-025-B, AC-7.x): The KB landing view already has a processing indicator component (`#kb-processing-indicator`). This feature provides the backend that triggers and updates it.

2. **"Process Selected" Button**: The KB landing toolbar should include a "Process" button (disabled when no files selected). This button triggers `POST /api/kb/process` with selected file paths.

3. **Classification Confirmation**: After AI suggests topics, a lightweight confirmation UI (toast or inline) should show suggestions and let users confirm/modify. Exact UI design is left to FEATURE-025-D or can be a simple browser `prompt()` for MVP.

## Dependencies

### Internal Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| FEATURE-025-A | Required | KBService, folder structure, index management |
| FEATURE-025-B | Required | Landing zone, file upload, processing indicator UI |

### External Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| AI/LLM API | Required | For topic classification and summary generation (uses existing project AI integration) |
| werkzeug | Existing | secure_filename for file operations |

## Business Rules

| # | Rule |
|---|------|
| BR-1 | Files MUST only be moved out of landing via explicit user action (never auto-processed) |
| BR-2 | Original files in `topics/{topic}/raw/` MUST be preserved (never modified or deleted by processing) |
| BR-3 | Summaries are append-only — new versions created, old versions never deleted |
| BR-4 | Topic names MUST be kebab-case (lowercase, hyphens, no spaces) |
| BR-5 | Empty topics (0 files) MAY exist after reorganization but SHOULD be cleaned up |
| BR-6 | Search MUST be case-insensitive |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Empty landing folder | Process command returns "No files to process" message |
| File with no text content (image, binary) | Classify based on filename/extension, mark as "binary" in summary |
| AI service unavailable | Fall back to "uncategorized" topic, skip summary generation |
| Duplicate filename in target topic | Append numeric suffix: `test.md` → `test-1.md` |
| Very large file (>1MB) | Truncate content to 1MB for AI analysis, note truncation in summary |
| Topic name collision | Merge into existing topic (add files, regenerate summary) |
| Processing cancelled mid-way | Files already moved stay in topics; remaining files stay in landing |
| Concurrent processing requests | Reject second request with 409 Conflict while processing is active |
| File deleted between selection and processing | Skip with warning, process remaining files |
| Non-UTF8 file content | Detect encoding, fall back to binary classification |

## Out of Scope

- **Automatic/scheduled processing** — all processing is user-triggered (BR-1)
- **File content editing** — this feature only moves and summarizes, never modifies original files
- **Topic UI view** — handled by FEATURE-025-D
- **Advanced search UI** — handled by FEATURE-025-E
- **File preview** — handled by FEATURE-025-E
- **Multi-project KB** — out of scope for v1.0
- **Streaming/real-time progress updates via WebSocket** — use polling or simple indicator for MVP

## Technical Considerations

- The KB Manager Skill is both a **backend service** (REST API endpoints) and a **Copilot skill** (`.github/skills/` folder with SKILL.md)
- Existing `KBService` should be extended with new methods (classify, process, search, reorganize) rather than creating a separate service class
- AI integration should use the project's existing LLM configuration (check for existing AI service patterns in the codebase)
- File content reading should support: plain text (.md, .txt, .py, .js, etc.), PDF text extraction (if library available), and binary detection
- The `POST /api/kb/process` → `POST /api/kb/process/confirm` two-step flow allows user review before file operations
- Index updates should call existing `refresh_index()` after file moves
- Processing state (in-progress, cancelled) needs to be tracked to prevent concurrent operations

## Open Questions

| # | Question | Status | Resolution |
|---|----------|--------|------------|
| OQ-1 | Should we use WebSocket for real-time progress updates during processing? | Resolved | No — use simple polling or processing indicator for MVP. WebSocket can be added later. |
| OQ-2 | How should the "Process Selected" button interact with the existing toolbar? | Resolved | Add as new button in action toolbar, next to Delete button. Visible when files are selected. |
| OQ-3 | What AI model/service should be used for classification and summarization? | Open | Use existing project AI integration. Check `config_service.py` for LLM configuration. |
| OQ-4 | Should reorganization require confirmation for each change or bulk confirm? | Resolved | Bulk confirmation with summary of proposed changes. |
| OQ-5 | Maximum number of files to process in one batch? | Resolved | 50 files per batch (practical limit for AI analysis). |
