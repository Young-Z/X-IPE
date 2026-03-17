# Feature Specification: KB AI Librarian & Intake

> Feature ID: FEATURE-049-F  
> Version: v1.2  
> Status: Refined  
> Last Updated: 03-17-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-16-2026 | Initial specification |
| v1.1 | 03-16-2026 | CR-001: Added x-ipe-tool-kb-librarian skill to scope (was out-of-scope) |
| v1.2 | 03-17-2026 | CR-002: Replace frontmatter-embedded metadata with `.kb-index.json` registry — hidden file, locally-scoped, folder metadata, description attribute |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| KB Interface v1 — Scene 4 | HTML | [x-ipe-docs/requirements/EPIC-049/FEATURE-049-F/mockups/kb-interface-v1.html](x-ipe-docs/requirements/EPIC-049/FEATURE-049-F/mockups/kb-interface-v1.html) | Intake — AI Librarian file management UI (Scene 4) | current | 03-16-2026 |

> **Path Convention:** Use full project-root-relative paths for mockup links.
>
> **Note:** UI/UX requirements and acceptance criteria below are derived from mockups marked as "current".
> Mockups marked as "outdated" are directional references only — do not use for AC comparison.

## Overview

FEATURE-049-F adds an AI Librarian intake staging workflow to the Knowledge Base. Instead of uploading files directly into KB folders (the "Normal" mode from FEATURE-049-E), users can choose "AI Librarian" mode, which stages files in a hidden `.intake/` folder. An intake view displays staged files with their processing status (Pending, Processing, Filed), and a "✨ Run AI Librarian" button triggers a Copilot CLI tool skill that classifies, moves, and tags the files automatically.

This feature builds on the foundation laid by FEATURE-049-A (`.intake/` folder constant, `KBConfig.ai_librarian` field, tree exclusion) and FEATURE-049-E (file upload infrastructure). The actual AI classification logic lives in the `x-ipe-tool-kb-librarian` tool skill, which is out of scope for this feature — FEATURE-049-F provides the staging infrastructure and UI that the skill plugs into.

The intake workflow separates the "upload" action from the "organize" action, letting users batch-upload files and defer organization to AI. Status tracking via `.intake-status.json` ensures persistence across restarts.

## User Stories

1. **As a** KB user, **I want to** upload files to an intake staging area, **so that** AI can organize them into the right folders and tag them automatically.

2. **As a** KB user, **I want to** see all intake files with their processing status (Pending, Processing, Filed), **so that** I know which files have been organized and which are waiting.

3. **As a** KB user, **I want to** trigger the AI Librarian with one click, **so that** pending intake files are classified, moved, and tagged without manual effort.

4. **As a** KB user, **I want to** manually assign folders to pending intake files, **so that** I can override or pre-set destinations before running the AI Librarian.

5. **As a** KB user, **I want to** remove files from intake, **so that** I can clean up unwanted or duplicate uploads.

6. **As a** KB user, **I want to** undo a "Filed" result, **so that** I can re-process a file if the AI placed it incorrectly.

## Acceptance Criteria

### AC-049-F-01: Upload Mode Toggle

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-01a | GIVEN user is on KB browse modal upload view AND AI Librarian is enabled in config WHEN user clicks "📚 AI Librarian" toggle button THEN upload mode switches to AI Librarian AND drop zone shows intake-specific description AND subsequent uploads go to `.intake/` folder | UI |
| AC-049-F-01b | GIVEN upload mode is AI Librarian WHEN user clicks "Normal" toggle button THEN upload mode switches back to Normal AND subsequent uploads go to the selected destination folder | UI |
| AC-049-F-01c | GIVEN `ai_librarian.enabled` is `false` in kb-config.json WHEN KB browse modal loads THEN upload mode toggle is hidden AND only Normal upload mode is available | UI |
| AC-049-F-01d | GIVEN upload mode is AI Librarian WHEN user drops files onto the intake drop zone THEN files are uploaded to `.intake/` folder AND intake file list refreshes to show new files with "Pending" status | UI |

### AC-049-F-02: Intake File Listing

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-02a | GIVEN files exist in `.intake/` folder WHEN intake view loads THEN all intake files are displayed in a table with columns: File, Size, Uploaded, Status, Destination, Actions (per mockup Scene 4) | UI |
| AC-049-F-02b | GIVEN `.intake/` folder is empty WHEN intake view loads THEN empty state message is shown with drop zone prompt ("Drop more files into Intake, or browse") | UI |
| AC-049-F-02c | GIVEN intake files exist with mixed statuses WHEN user clicks "Pending" filter pill THEN only files with Pending status are shown | UI |
| AC-049-F-02d | GIVEN intake files exist with mixed statuses WHEN user clicks "Processing" filter pill THEN only files with Processing status are shown | UI |
| AC-049-F-02e | GIVEN intake files exist with mixed statuses WHEN user clicks "Filed" filter pill THEN only files with Filed status are shown | UI |
| AC-049-F-02f | GIVEN any filter is active WHEN user clicks "All" filter pill THEN all files regardless of status are shown | UI |

### AC-049-F-03: Status Tracking

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-03a | GIVEN a file exists in `.intake/` AND has no entry in `.intake-status.json` WHEN intake status is read THEN its status defaults to "pending" | Unit |
| AC-049-F-03b | GIVEN `.intake-status.json` has an entry with `"status": "processing"` for a file WHEN intake view loads THEN that file shows "Processing…" status badge with blue highlight (per mockup) | UI |
| AC-049-F-03c | GIVEN `.intake-status.json` has an entry with `"status": "filed"` and a destination path for a file WHEN intake view loads THEN that file shows "Filed ✓" status badge AND its row is dimmed (opacity 0.7) AND destination column shows the target folder | UI |
| AC-049-F-03d | GIVEN `.intake-status.json` does not exist WHEN intake status is read THEN all files in `.intake/` default to "pending" status | Unit |
| AC-049-F-03e | GIVEN `.intake-status.json` has an entry for a file that no longer exists in `.intake/` WHEN intake status is read THEN the stale entry is ignored (not shown in listing) | Unit |

### AC-049-F-04: AI Librarian Trigger

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-04a | GIVEN intake files exist with Pending status WHEN user clicks "✨ Run AI Librarian" button THEN a natural language command is sent to Copilot CLI (no `--workflow-mode` flag) AND modal closes AND terminal panel expands | UI |
| AC-049-F-04b | GIVEN no intake files exist WHEN intake view loads THEN "✨ Run AI Librarian" button is disabled | UI |
| AC-049-F-04c | GIVEN terminal manager is not available WHEN user clicks "✨ Run AI Librarian" THEN command is copied to clipboard AND toast notification "Command copied — paste into Copilot CLI" is shown | UI |
| AC-049-F-04d | GIVEN `ai_librarian.skill` field exists in config WHEN command is generated THEN command text is `'organize knowledge base intake files with AI Librarian'` (plain natural language, no flags) | Unit |

### AC-049-F-05: Per-File Actions

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-05a | GIVEN a file has "Pending" status WHEN user clicks Preview (eye icon) action THEN file content preview is displayed (reusing existing preview infrastructure) | UI |
| AC-049-F-05b | GIVEN a file has "Pending" status WHEN user clicks "Assign folder" (folder-symlink icon) action THEN a folder picker is shown AND user can select a destination folder AND selection is saved to `.intake-status.json` | UI |
| AC-049-F-05c | GIVEN a file has "Pending" status WHEN user clicks Remove (red X icon) action THEN confirmation is requested AND upon confirm the file is deleted from `.intake/` AND intake view refreshes | UI |
| AC-049-F-05d | GIVEN a file has "Filed" status WHEN user clicks "View in KB" (arrow icon) action THEN KB browse modal navigates to the file's destination folder | UI |
| AC-049-F-05e | GIVEN a file has "Filed" status WHEN user clicks "Undo" (orange refresh icon) action THEN file is moved back to `.intake/` from its destination AND `.intake-status.json` entry reverts to `"pending"` AND destination is cleared | UI |
| AC-049-F-05f | GIVEN a file has "Processing" status WHEN intake view renders that row THEN action buttons are disabled (no actions during processing) | UI |

### AC-049-F-06: Statistics & Badges

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-06a | GIVEN intake files exist WHEN intake view loads THEN statistics bar shows: total file count (purple badge), pending count (orange), processing count (blue), filed count (green) — per mockup Scene 4 | UI |
| AC-049-F-06b | GIVEN files are uploaded or status changes WHEN intake view refreshes THEN statistics bar counts update accordingly | UI |
| AC-049-F-06c | GIVEN intake has pending files WHEN KB sidebar renders THEN "📥 Intake" entry shows a pending count badge | UI |

### AC-049-F-07: Configuration

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-07a | GIVEN kb-config.json has `ai_librarian.enabled = true` WHEN KB browse modal loads THEN intake features (upload toggle, intake view, Run AI Librarian button) are available | Unit |
| AC-049-F-07b | GIVEN kb-config.json has `ai_librarian.enabled = false` WHEN KB browse modal loads THEN all intake features are hidden AND normal upload is the only option | Unit |
| AC-049-F-07c | GIVEN `ai_librarian` config exists WHEN `GET /api/kb/config` is called THEN response includes `ai_librarian` object with `enabled`, `intake_folder`, and `skill` fields | API |
| AC-049-F-07d | GIVEN default kb-config.json is created WHEN KB initializes for the first time THEN `ai_librarian` defaults to `{ enabled: false, intake_folder: ".intake", skill: "x-ipe-tool-kb-librarian" }` | Unit |

### AC-049-F-08: Intake Status Backend

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-08a | GIVEN `.intake/` folder exists with files AND `.intake-status.json` exists WHEN `kb_service` reads intake files THEN it returns merged data: file metadata from filesystem + status/destination from JSON | Unit |
| AC-049-F-08b | GIVEN `.intake-status.json` is corrupted (invalid JSON) WHEN intake status is read THEN all files default to "pending" status AND error is logged | Unit |
| AC-049-F-08c | GIVEN a new file is uploaded to `.intake/` WHEN upload completes THEN file appears in intake listing with "Pending" status (no status.json update needed) | Integration |
| AC-049-F-08d | GIVEN user assigns a folder to a pending file WHEN assignment is saved THEN `.intake-status.json` is updated with destination path for that file | Unit |

### AC-049-F-09: Edge Cases

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-09a | GIVEN user uploads a .zip archive in AI Librarian mode WHEN upload completes THEN archive is extracted into `.intake/` with folder structure preserved (same behavior as normal upload) | Integration |
| AC-049-F-09b | GIVEN `.intake/` folder does not exist WHEN AI Librarian mode is activated THEN `.intake/` folder is created automatically | Unit |
| AC-049-F-09c | GIVEN a filed file's destination folder no longer exists WHEN user clicks "View in KB" THEN an error toast is shown ("Destination folder not found") | UI |
| AC-049-F-09d | GIVEN user uploads a file with the same name as an existing intake file WHEN upload completes THEN a numeric suffix is added to avoid overwriting (e.g., `file (1).md`) | Unit |

### AC-049-F-10: Skill — Batch Processing

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-10a | GIVEN pending files exist in `.intake/` WHEN `x-ipe-tool-kb-librarian` skill is invoked via Copilot CLI THEN the skill reads all pending intake files AND updates each file's status to "processing" before starting analysis | Unit |
| AC-049-F-10b | GIVEN some files have pre-assigned destinations (via UI "Assign folder") AND others have no destination WHEN the skill processes the batch THEN pre-assigned files are moved to their assigned destination AND unassigned files are analyzed by AI to determine the best destination folder | Unit |
| AC-049-F-10c | GIVEN the `.intake/` folder has no pending files (all are "processing" or "filed") WHEN the skill is invoked THEN it prints "No pending intake files to process" and exits without error | Unit |
| AC-049-F-10d | GIVEN the `.intake/` folder does not exist WHEN the skill is invoked THEN it prints "Intake folder not found — nothing to process" and exits without error | Unit |

### AC-049-F-11: Skill — AI Content Analysis

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-11a | GIVEN a pending markdown file in `.intake/` with no pre-assigned destination WHEN the skill analyzes it THEN the skill reads the file content AND examines the existing KB folder structure AND selects the best-matching destination folder | Unit |
| AC-049-F-11b | GIVEN a pending file WHEN the skill analyzes its content THEN the skill assigns lifecycle tags (from: Ideation, Requirement, Design, Implementation, Testing, Deployment, Maintenance) AND domain tags (from: API, Authentication, UI-UX, Database, Infrastructure, Security, Performance, Integration, Documentation, Analytics) based on content relevance | Unit |
| AC-049-F-11c | GIVEN the AI determines a file should go to a folder that does not yet exist WHEN the skill processes the file THEN the skill creates the destination folder automatically before moving the file | Unit |

### AC-049-F-12: Skill — Metadata Index Generation (CR-002: replaces Frontmatter Generation)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-12a | GIVEN a pending file (any type) in `.intake/` WHEN the skill processes it THEN a metadata entry is written to the destination folder's `.kb-index.json` with fields: `title`, `description` (< 100 words), `tags` (lifecycle + domain), `author`, `created`, `type` (markdown/image/video/pdf/document/other), and `auto_generated: true` | Unit |
| AC-049-F-12b | GIVEN a pending non-markdown file (PDF, image, video, ZIP) in `.intake/` WHEN the skill processes it THEN the file is moved to the destination AND receives a full metadata entry in `.kb-index.json` (same fields as markdown files) — the file content is NOT modified | Unit |
| AC-049-F-12c | GIVEN a file already has an entry in the destination `.kb-index.json` WHEN the skill processes a new version of that file THEN existing metadata fields are preserved AND only missing fields are auto-populated (no overwriting) | Unit |

### AC-049-F-13: Skill — File Movement & Status Updates

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-13a | GIVEN a file is being processed WHEN the skill moves it to the destination folder THEN the file is moved from `.intake/{filename}` to `{destination}/{filename}` via the KB service move API AND `.intake-status.json` is updated with status "filed" and the destination path | Unit |
| AC-049-F-13b | GIVEN a file move fails (e.g., permission error, disk full) WHEN the skill encounters the error THEN the file remains in `.intake/` AND status stays "processing" AND the error is logged AND the skill continues processing remaining files | Unit |
| AC-049-F-13c | GIVEN all files in the batch have been processed WHEN processing completes THEN the skill prints a terminal summary: count of files processed, list of destinations used (e.g., "3 files processed → docs/guides/, docs/references/") | Unit |

### AC-049-F-14: Skill File & Configuration

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-14a | GIVEN the X-IPE project WHEN `.github/skills/x-ipe-tool-kb-librarian/` is inspected THEN a valid SKILL.md exists following the x-ipe tool skill template with: Purpose, Input Parameters, Operations, Output Result, Definition of Done | Unit |
| AC-049-F-14b | GIVEN the skill SKILL.md WHEN the trigger patterns are inspected THEN it matches on: "organize knowledge base intake files with AI Librarian", "run AI Librarian", "organize intake" | Unit |
| AC-049-F-14c | GIVEN the KB config has `ai_librarian.skill = "x-ipe-tool-kb-librarian"` WHEN the skill reads config THEN it uses the tag taxonomy from `kb-config.json` tags section for classification | Unit |

### AC-049-F-15: Metadata Index Structure (CR-002)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-15a | GIVEN a KB folder WHEN `.kb-index.json` is inspected THEN it is a hidden file (dot-prefixed) containing `version` (string) and `entries` (object keyed by filename or foldername with trailing `/`) | Unit |
| AC-049-F-15b | GIVEN a `.kb-index.json` file WHEN an entry has a `description` field THEN the description is plain text with fewer than 100 words | Unit |
| AC-049-F-15c | GIVEN a KB folder with subfolders WHEN `.kb-index.json` is read THEN subfolder entries (keys ending with `/`) can have metadata: `title`, `description`, and `tags` — enabling folder-level classification | Unit |
| AC-049-F-15d | GIVEN a `.kb-index.json` WHEN it is read THEN it indexes ONLY the files and immediate subfolders in its own directory — it does NOT index files in nested subdirectories (each subfolder has its own `.kb-index.json`) | Unit |
| AC-049-F-15e | GIVEN the KBService builds the file tree WHEN files are listed for a folder THEN metadata is read from that folder's `.kb-index.json` instead of parsing YAML frontmatter from file content | Unit |
| AC-049-F-15f | GIVEN a file exists in a folder but has no entry in `.kb-index.json` WHEN the file is listed THEN default metadata is used (title from filename, no tags, author "unknown", type from extension) | Unit |
| AC-049-F-15g | GIVEN a new file is created or moved into a folder WHEN the operation completes THEN an entry is auto-populated in that folder's `.kb-index.json` with default metadata | Unit |

## Functional Requirements

| ID | Requirement | Input | Process | Output |
|----|-------------|-------|---------|--------|
| FR-049-F.1 | Upload Mode Toggle | User click on mode toggle | Switch between Normal and AI Librarian upload modes; AI Librarian routes uploads to `.intake/` | Mode state updated, UI reflects active mode |
| FR-049-F.2 | Intake File Storage | Files dropped/browsed in AI Librarian mode | Store files in `x-ipe-docs/knowledge-base/.intake/` folder | Files persisted in intake staging area |
| FR-049-F.3 | Status Tracking | `.intake-status.json` + filesystem listing | Merge file metadata with status entries; default to "pending" for files without entries | Unified intake file list with statuses |
| FR-049-F.4 | Intake View | Intake file data | Render table with File, Size, Uploaded, Status, Destination, Actions columns; apply filter pills | Intake management UI per mockup Scene 4 |
| FR-049-F.5 | AI Librarian Trigger | User clicks "✨ Run AI Librarian" button | Send plain natural language command to Copilot CLI via terminal manager | CLI session receives prompt; modal closes |
| FR-049-F.6 | Per-File Actions | User clicks action button per file row | Execute action: Preview (show content), Assign (set destination), Remove (delete), View in KB (navigate), Undo (revert filed) | Action executed, intake view refreshed |
| FR-049-F.7 | Statistics Bar | Intake file data | Calculate counts by status (total, pending, processing, filed) | Statistics badges displayed in header |
| FR-049-F.8 | Config Extension | `kb-config.json` ai_librarian section | Read config; gate all intake features behind `enabled` flag | Features shown/hidden based on config |
| FR-049-F.9 | AI Content Analysis | Pending intake file content + KB folder structure | Analyze content to determine best destination folder; assign lifecycle + domain tags based on relevance | Destination path + tag assignments per file |
| FR-049-F.10 | Metadata Index Management | File/folder metadata + `.kb-index.json` | Read/write `.kb-index.json` per folder; auto-populate entries for new files; preserve existing entries on update | Metadata entries in hidden `.kb-index.json` per folder |
| FR-049-F.11 | Batch File Processing | All pending intake files | Process each: set status → processing, analyze content, generate index entry (all file types), move to destination, set status → filed | All pending files moved and metadata indexed |
| FR-049-F.12 | Skill File | x-ipe tool skill template | Create `.github/skills/x-ipe-tool-kb-librarian/SKILL.md` with trigger patterns, input/output contract, operations | Valid tool skill file |
| FR-049-F.13 | Folder Metadata | KB folder structure | Subfolders can have metadata entries (title, description, tags) in parent's `.kb-index.json` — key ends with `/` | Folder-level classification and description |
| FR-049-F.14 | Description Attribute | File/folder metadata | Each index entry supports a `description` field (< 100 words, plain text) for AI-generated or human-provided summaries | Description available for search and display |

## Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-049-F.1 | `.intake/` folder is excluded from regular KB browsing, tree, and search | Already implemented in FEATURE-049-A |
| NFR-049-F.2 | Graceful degradation: corrupted `.intake-status.json` treated as all-pending | Error logged, no crash |
| NFR-049-F.3 | Intake view loads within 500ms for up to 100 files | Performance |
| NFR-049-F.4 | No new API routes — intake uses existing KB endpoints + filesystem | Simplicity (YAGNI) |
| NFR-049-F.5 | Skill processes files non-destructively — original content is preserved, only frontmatter is added/merged | Data safety |

## UI/UX Requirements

Derived from mockup Scene 4:

1. **Upload Mode Toggle:** Two side-by-side buttons ("Normal" / "📚 AI Librarian") in the upload view. Active mode is visually highlighted. Purple accent (`#8b5cf6`) for AI Librarian mode elements.

2. **Intake View Layout:**
   - Header: "📥 Intake — AI Librarian" title with purple icon
   - "✨ Run AI Librarian" gradient purple button (top-right)
   - Statistics bar: total (purple), pending (orange), processing (blue), filed (green) badges with separator dividers
   - Filter pills: All | Pending | Processing | Filed (right-aligned)

3. **Intake Table:**
   - Columns: File (icon + name), Size, Uploaded, Status (badge), Destination (folder path or "—"), Actions (icon buttons)
   - Pending rows: normal styling, 3 action buttons (Preview, Assign, Remove)
   - Processing rows: subtle blue background highlight (`rgba(59,130,246,0.04)`), disabled actions
   - Filed rows: dimmed (opacity 0.7), green "Filed ✓" badge, breadcrumb tags, 2 action buttons (View in KB, Undo)

4. **Drop Zone (Bottom):** Dashed purple border (`rgba(139,92,246,0.3)`), cloud-upload icon, "Drop more files into Intake, or browse" text.

5. **Sidebar Badge:** "📥 Intake" entry in KB sidebar with pending count badge.

## Dependencies

### Internal

| Dependency | Feature | Status | Integration Point |
|------------|---------|--------|-------------------|
| KB Backend & Storage Foundation | FEATURE-049-A | ✅ Done | `.intake/` constant, `KBConfig.ai_librarian` field, tree exclusion, config API |
| KB File Upload | FEATURE-049-E | ✅ Done | Upload infrastructure, archive extraction, `POST /api/kb/upload` |
| KB Sidebar & Navigation | FEATURE-049-B | ✅ Done | Sidebar "📥 Intake" entry placeholder |

### External

| Dependency | Description | Status |
|------------|-------------|--------|
| `x-ipe-tool-kb-librarian` skill | AI classification, file moving, and tagging logic | 🔄 In scope (CR-001) |
| `x-ipe-meta-skill-creator` skill | Required for creating the tool skill following X-IPE standards | ✅ Available |

## Business Rules

| ID | Rule |
|----|------|
| BR-049-F-01 | `.intake/` folder is excluded from KB tree, browse, and search results |
| BR-049-F-02 | Default status for a file in `.intake/` with no `.intake-status.json` entry is "Pending" |
| BR-049-F-03 | All intake features are gated behind `ai_librarian.enabled` config flag |
| BR-049-F-04 | Archive extraction in AI Librarian mode follows the same rules as normal upload (FEATURE-049-E) |
| BR-049-F-05 | The AI Librarian command is plain natural language — no `--workflow-mode` or other flags |
| BR-049-F-06 | Stale entries in `.intake-status.json` (files that no longer exist) are silently ignored |
| BR-049-F-07 | Per-file actions vary by status: Pending → Preview/Assign/Remove; Processing → disabled; Filed → View in KB/Undo |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| `.intake-status.json` is corrupted | Treat all files as "Pending", log error |
| `.intake/` folder doesn't exist when AI Librarian mode is activated | Create `.intake/` folder automatically |
| Upload file with duplicate name in `.intake/` | Add numeric suffix (e.g., `file (1).md`) |
| Filed file's destination folder deleted | "View in KB" shows error toast |
| Very large `.intake/` (100+ files) | Pagination or virtual scrolling if needed (NFR-049-F.3) |
| User uploads non-markdown file (PDF, ZIP, image) | Full metadata entry in `.kb-index.json` — same fields as markdown files; file content not modified |
| AI Librarian skill not yet installed | Button still works (sends command to CLI); skill absence is the CLI agent's concern |
| Skill encounters a file it cannot classify | Move to a default "unsorted" folder, log warning, continue batch |
| Skill processes a very large file (>10MB) | Same behavior — file is moved, metadata entry added to `.kb-index.json` |

## Out of Scope

- **`agent_write_allowlist` enforcement** — implemented when skill writes via API
- **`kb-articles` workflow action context key** — workflow integration for the skill
- **Batch operations** (select multiple files, bulk assign/remove) — future enhancement
- **Drag-and-drop reordering** within intake table — not in mockup
- **Sidecar `.meta.json` for non-markdown files** — replaced by `.kb-index.json` registry (CR-002)
- **YAML frontmatter for metadata** — replaced by `.kb-index.json` registry (CR-002); existing frontmatter in markdown files is NOT removed but no longer the source of truth

## Technical Considerations

- `.intake-status.json` schema: `{ "filename.ext": { "status": "pending|processing|filed", "destination": "folder/path/", "updated_at": "ISO8601" } }`
- The `_runAILibrarian()` method should use plain command: `'organize knowledge base intake files with AI Librarian'`
- Existing `POST /api/kb/upload` with `folder=.intake` handles intake uploads — no new route needed
- Existing `GET /api/kb/files?folder=.intake` or tree API can list intake files — extend if needed for status merging
- Config `KBConfig.ai_librarian` needs `skill` field added (default: `"x-ipe-tool-kb-librarian"`)
- Frontend polls or refreshes intake view after AI Librarian runs to pick up status changes
- `.kb-index.json` schema (CR-002): `{ "version": "1.0", "entries": { "filename.ext": { "title": "...", "description": "< 100 words", "tags": { "domain": [...], "lifecycle": [...] }, "author": "...", "created": "YYYY-MM-DD", "type": "markdown|image|video|pdf|document|other", "auto_generated": true }, "subfolder/": { "title": "...", "description": "...", "tags": {...} } } }`
- Each `.kb-index.json` is locally-scoped — indexes only files and immediate subfolders in its directory
- Metadata is read from `.kb-index.json` instead of parsing YAML frontmatter from file content
- Skill uses KB service methods: `get_intake_files()`, `update_intake_status()`, `move_file()`, `_read_kb_index()`, `_write_kb_index()`
- Skill reads tag taxonomy from kb-config.json (`tags.lifecycle`, `tags.domain`) for AI classification
- Non-markdown files: moved, metadata indexed in `.kb-index.json`, same fields as markdown
- Skill is a tool skill created via `x-ipe-meta-skill-creator` — file at `.github/skills/x-ipe-tool-kb-librarian/SKILL.md`

## Open Questions

None — all questions resolved via DAO (see `x-ipe-docs/dao/26-03-16/decisions_made_feature_refinement.md`).
CR-001 questions resolved: batch processing, destination priority (UI-assigned > AI), non-markdown handling, terminal summary, auto-create folders.
CR-002 questions resolved: metadata storage (`.kb-index.json` registry), locally-scoped indexes, folder metadata, description attribute (< 100 words).
