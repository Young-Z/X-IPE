# Feature Specification: KB AI Librarian & Intake

> Feature ID: FEATURE-049-F  
> Version: v1.5  
> Status: Refined  
> Last Updated: 03-18-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 03-16-2026 | Initial specification |
| v1.1 | 03-16-2026 | CR-001: Added x-ipe-tool-kb-librarian skill to scope (was out-of-scope) |
| v1.2 | 03-17-2026 | CR-002: Replace frontmatter-embedded metadata with `.kb-index.json` registry — hidden file, locally-scoped, folder metadata, description attribute |
| v1.3 | 03-17-2026 | CR-004: Add rich file preview to KB browse — markdown+DSL, images, docx/msg conversion, PDF, HTML iframe, syntax-highlighted code |
| v1.4 | 03-18-2026 | CR-005: Folder support in intake — fix count logic for top-level items (folders + files), add folder tree display with expand/collapse in intake file list view |
| v1.5 | 03-18-2026 | CR-005 Refinement: Folder status derived from children, pre-loaded tree (no lazy loading), folder-specific actions (assign/remove/undo), filter propagation, deep-count badge, AI Librarian processes files individually |

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

7. **As a** KB user, **I want to** see uploaded folders as expandable tree items in the intake view, **so that** I can browse folder contents and manage them at both folder and file level. *(CR-005)*

8. **As a** KB user, **I want to** assign or remove entire folders at once, **so that** I can efficiently manage batches of related files without acting on each file individually. *(CR-005)*

## Acceptance Criteria

### AC-049-F-01: Upload Mode Toggle

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-01a | GIVEN user is on KB browse modal upload view AND AI Librarian is enabled in config WHEN user clicks "📚 AI Librarian" toggle button THEN upload mode switches to AI Librarian AND drop zone shows intake-specific description AND subsequent uploads go to `.intake/` folder | UI |
| AC-049-F-01b | GIVEN upload mode is AI Librarian WHEN user clicks "Normal" toggle button THEN upload mode switches back to Normal AND subsequent uploads go to the selected destination folder | UI |
| AC-049-F-01c | GIVEN `ai_librarian.enabled` is `false` in kb-config.json WHEN KB browse modal loads THEN upload mode toggle is hidden AND only Normal upload mode is available | UI |
| AC-049-F-01d | GIVEN upload mode is AI Librarian WHEN user drops files onto the intake drop zone THEN files are uploaded to `.intake/` folder AND intake file list refreshes to show new files with "Pending" status | UI |

### AC-049-F-02: Intake Item Listing (CR-005: updated from "File Listing")

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-02a | GIVEN items (files or folders) exist in `.intake/` folder WHEN intake view loads THEN all top-level intake items are displayed in a table with columns: Name, Size/Items, Uploaded, Status, Destination, Actions (per mockup Scene 4). Folders show a folder icon and item count; files show a file icon and byte size | UI |
| AC-049-F-02b | GIVEN `.intake/` folder is empty WHEN intake view loads THEN empty state message is shown with drop zone prompt ("Drop more files into Intake, or browse") | UI |
| AC-049-F-02c | GIVEN intake items exist with mixed statuses WHEN user clicks "Pending" filter pill THEN only items with Pending status are shown AND folders are shown if ANY descendant file has Pending status | UI |
| AC-049-F-02d | GIVEN intake items exist with mixed statuses WHEN user clicks "Processing" filter pill THEN only items with Processing status are shown AND folders are shown if ANY descendant file has Processing status | UI |
| AC-049-F-02e | GIVEN intake items exist with mixed statuses WHEN user clicks "Filed" filter pill THEN only items with Filed status are shown AND folders are shown if ANY descendant file has Filed status | UI |
| AC-049-F-02f | GIVEN any filter is active WHEN user clicks "All" filter pill THEN all items regardless of status are shown | UI |
| AC-049-F-02g | GIVEN a folder exists in intake AND all children are pre-loaded in the API response WHEN user clicks the folder row expand toggle THEN the folder's immediate children (files and sub-folders) are revealed as indented rows below the folder row (client-side show/hide, no additional API call) | UI |
| AC-049-F-02h | GIVEN a folder row is expanded WHEN user clicks the collapse toggle THEN child rows are hidden and the toggle returns to collapsed state | UI |
| AC-049-F-02i | GIVEN a sub-folder exists inside an expanded folder WHEN user clicks the sub-folder expand toggle THEN sub-folder's children are revealed with further indentation (recursive, all pre-loaded) | UI |
| AC-049-F-02j | GIVEN a folder row is rendered in the intake table WHEN the row displays THEN it shows: a chevron toggle (▶ collapsed / ▼ expanded), a folder icon (`bi-folder`/`bi-folder2-open`), the folder name, item count (e.g., "3 items") in the Size column, and no file-size value | UI |
| AC-049-F-02k | GIVEN nested items are displayed in expanded folders WHEN child rows render THEN each nesting level adds 20px left padding relative to its parent row for visual hierarchy | UI |

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
| AC-049-F-05g | GIVEN a folder has derived "Pending" status (≥1 child is pending) WHEN intake view renders the folder row THEN available actions are: Assign (folder-symlink icon) and Remove (red X icon). Preview action is NOT shown for folders | UI |
| AC-049-F-05h | GIVEN a folder with derived "Pending" status WHEN user clicks "Assign folder" action on the folder THEN a folder picker is shown AND upon selection, the destination is saved for ALL children of the folder (recursively) in `.intake-status.json` | UI |
| AC-049-F-05i | GIVEN a folder exists in intake WHEN user clicks Remove action on the folder THEN confirmation is requested AND upon confirm the folder and ALL its contents are deleted from `.intake/` AND intake view refreshes | UI |
| AC-049-F-05j | GIVEN a folder has derived "Filed" status (all children filed) WHEN intake view renders the folder row THEN available action is: Undo (orange refresh icon). Undo reverts ALL children to "pending" status | UI |

### AC-049-F-06: Statistics & Badges (CR-005: updated counts to include folders)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-06a | GIVEN intake items (files and/or folders) exist WHEN intake view loads THEN statistics bar shows: total top-level item count (purple badge), pending count (orange), processing count (blue), filed count (green) — per mockup Scene 4. Counts reflect top-level items only (not deep file count within folders) | UI |
| AC-049-F-06b | GIVEN items are uploaded or status changes WHEN intake view refreshes THEN statistics bar counts update accordingly | UI |
| AC-049-F-06c | GIVEN intake has pending files (including files inside folders) WHEN KB sidebar renders THEN "📥 Intake" entry shows a pending count badge with deep-count of individual pending FILES across all folders (not just top-level items) | UI |
| AC-049-F-06d | GIVEN a folder in `.intake/` contains children with mixed statuses WHEN folder status is determined THEN status is derived: "pending" if ≥1 child is pending, "processing" if any child is processing AND none are pending, "filed" if ALL children are filed | Unit |

### AC-049-F-07: Configuration

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-07a | GIVEN kb-config.json has `ai_librarian.enabled = true` WHEN KB browse modal loads THEN intake features (upload toggle, intake view, Run AI Librarian button) are available | Unit |
| AC-049-F-07b | GIVEN kb-config.json has `ai_librarian.enabled = false` WHEN KB browse modal loads THEN all intake features are hidden AND normal upload is the only option | Unit |
| AC-049-F-07c | GIVEN `ai_librarian` config exists WHEN `GET /api/kb/config` is called THEN response includes `ai_librarian` object with `enabled`, `intake_folder`, and `skill` fields | API |
| AC-049-F-07d | GIVEN default kb-config.json is created WHEN KB initializes for the first time THEN `ai_librarian` defaults to `{ enabled: false, intake_folder: ".intake", skill: "x-ipe-tool-kb-librarian" }` | Unit |

### AC-049-F-08: Intake Status Backend (CR-005: updated for folder support)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-08a | GIVEN `.intake/` folder exists with files and/or subdirectories AND `.intake-status.json` exists WHEN `kb_service` reads intake items THEN it returns a nested tree structure: item metadata from filesystem (type file or folder, size or item_count) + status/destination from JSON for files, derived status for folders | Unit |
| AC-049-F-08b | GIVEN `.intake-status.json` is corrupted (invalid JSON) WHEN intake status is read THEN all items default to "pending" status AND error is logged | Unit |
| AC-049-F-08c | GIVEN a new file is uploaded to `.intake/` WHEN upload completes THEN file appears in intake listing with "Pending" status (no status.json update needed) | Integration |
| AC-049-F-08d | GIVEN user assigns a destination to a pending item (file or folder) WHEN assignment is saved THEN `.intake-status.json` is updated with destination path for that item (folder assign updates all children recursively) | Unit |
| AC-049-F-08e | GIVEN a folder exists in `.intake/` WHEN `kb_service` reads intake items THEN the folder appears as a top-level item with `type: "folder"`, `item_count` (number of immediate children), `children` array (pre-loaded nested items), and `status` derived from children (not stored in `.intake-status.json`) | Unit |
| AC-049-F-08f | GIVEN `GET /api/kb/intake` is called WHEN the `.intake/` folder contains subdirectories THEN response contains a nested tree with ALL items pre-loaded (folders include `children` arrays with their files and sub-folders recursively) — no separate endpoint for folder children | API |
| AC-049-F-08g | GIVEN a folder contains children with statuses [pending, filed] WHEN `kb_service` derives folder status THEN status is "pending" (any pending child → folder is pending). GIVEN all children are "filed" THEN folder status is "filed". GIVEN any child is "processing" with no pending children THEN folder status is "processing" | Unit |

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

### AC-049-F-16: Rich File Preview (CR-004)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-049-F-16a | GIVEN a markdown file in KB WHEN user clicks the file card THEN content is rendered with DSL-enhanced markdown (Mermaid diagrams, Architecture DSL, Infographic DSL rendered inline) via ContentRenderer | UI |
| AC-049-F-16b | GIVEN an image file (PNG, JPG, GIF, SVG, WebP) in KB WHEN user clicks the file card THEN the image is displayed inline in the article scene with proper scaling (max-width: 100%) | UI |
| AC-049-F-16c | GIVEN a .docx file in KB WHEN user clicks the file card THEN the backend converts it to HTML via mammoth AND the converted HTML is displayed in a sandboxed iframe in the article scene | UI |
| AC-049-F-16d | GIVEN a PDF file in KB WHEN user clicks the file card THEN the PDF is displayed in an iframe viewer in the article scene | UI |
| AC-049-F-16e | GIVEN an HTML file in KB WHEN user clicks the file card THEN the HTML is rendered in a sandboxed iframe in the article scene | UI |
| AC-049-F-16f | GIVEN a code/text file (.py, .js, .json, .yaml, etc.) in KB WHEN user clicks the file card THEN the content is displayed with syntax highlighting | UI |
| AC-049-F-16g | GIVEN a binary file that cannot be previewed WHEN user clicks the file card THEN a "Cannot preview this file type" message is shown with file metadata (name, size, type) and a download link | UI |
| AC-049-F-16h | GIVEN `GET /api/kb/files/{path}/preview` endpoint WHEN called with a .docx file path THEN response is converted HTML with `X-Converted: true` header AND `Content-Type: text/html` | API |
| AC-049-F-16i | GIVEN `GET /api/kb/files/{path}/preview` endpoint WHEN called with an image file path THEN response is the raw binary with correct MIME type (e.g., `image/png`) | API |

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
| FR-049-F.15 | Rich File Preview | File card click in KB browse | Detect file type; render markdown+DSL via ContentRenderer, convert docx/msg to HTML, serve images/PDF natively, syntax-highlight code | Rich preview in article scene matching ideation capabilities |
| FR-049-F.16 | Folder Tree Display (CR-005) | Intake API response with nested items | Render top-level items; folders show expand/collapse chevron and folder icon; expanding reveals pre-loaded children with indentation (20px per level); recursive sub-folder support | Hierarchical intake view with expand/collapse |
| FR-049-F.17 | Folder Status Derivation (CR-005) | Children statuses from `.intake-status.json` | Derive folder status: "pending" if ≥1 child pending, "processing" if any processing with no pending, "filed" if all children filed. Applied recursively for nested folders | Computed status per folder, no stored folder status |
| FR-049-F.18 | Folder Actions (CR-005) | User clicks action on folder row | Folder-specific actions: Assign (bulk-set destination for all children), Remove (delete folder + all contents), Undo (revert all filed children to pending). No Preview action for folders | Folder-level batch operations |
| FR-049-F.19 | Pre-loaded Intake Tree (CR-005) | `GET /api/kb/intake` | Return full nested tree in single API call; folders include `children` arrays with files and sub-folders recursively; no lazy-loading endpoint | Complete tree in one response |

## Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-049-F.1 | `.intake/` folder is excluded from regular KB browsing, tree, and search | Already implemented in FEATURE-049-A |
| NFR-049-F.2 | Graceful degradation: corrupted `.intake-status.json` treated as all-pending | Error logged, no crash |
| NFR-049-F.3 | Intake view loads within 500ms for up to 100 files | Performance |
| NFR-049-F.4 | Minimal new API routes — intake uses existing KB endpoints + filesystem; preview route is the exception for binary file serving | Simplicity (YAGNI) |
| NFR-049-F.5 | Skill processes files non-destructively — original content is preserved, only frontmatter is added/merged | Data safety |
| NFR-049-F.6 | Pre-loaded intake tree handles up to 500 total items (files + folders combined) without performance degradation | Performance (CR-005) |

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

5. **Sidebar Badge:** "📥 Intake" entry in KB sidebar with deep-count pending files badge (counts all individual pending files across all folders).

6. **Folder Tree Display (CR-005):**
   - Folder rows: chevron toggle (▶/▼) + `bi-folder`/`bi-folder2-open` icon + folder name + item count badge (e.g., "3 items")
   - Expand/collapse is instant (pre-loaded data, no loading spinners)
   - Indentation: 20px per nesting level applied via `padding-left`
   - Expanded folder icon changes from `bi-folder` to `bi-folder2-open`
   - Folder actions: Assign + Remove (for pending), Undo (for filed) — no Preview button
   - Folder status badge same as files (Pending orange, Processing blue, Filed green) but derived from children
   - Nested rows share the same table structure (no separate sub-table)

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
| BR-049-F-07 | Per-item actions vary by status and type: Files — Pending → Preview/Assign/Remove; Processing → disabled; Filed → View in KB/Undo. Folders — Pending → Assign/Remove; Processing → disabled; Filed → Undo |
| BR-049-F-08 | Folder status is derived from children: "pending" if ≥1 child pending, "processing" if any processing (none pending), "filed" if all children filed. Folders have NO explicit status in `.intake-status.json` (CR-005) |
| BR-049-F-09 | Folder Assign/Remove/Undo actions apply recursively to ALL children (CR-005) |
| BR-049-F-10 | AI Librarian processes individual files, not folders as units. Files within one folder may be assigned to different KB destinations (CR-005) |
| BR-049-F-11 | Sidebar badge shows deep-count of individual pending FILES (not top-level items). Stats bar shows top-level item counts (CR-005) |

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
| Empty folder in `.intake/` (CR-005) | Show folder row with "0 items" count; expanding shows empty state within the folder |
| Deeply nested folder structure (5+ levels) (CR-005) | Support recursive expand/collapse with cumulative indentation; no depth limit |
| Folder with mixed-status children (CR-005) | Folder visible in all relevant filter views (e.g., visible in both "Pending" and "Filed" filters if it has children with both statuses) |
| Folder removal with some filed children (CR-005) | Confirmation dialog warns: "This folder contains filed items. Remove anyway?" |
| Very large nested tree (500+ items) (CR-005) | Pre-loading handles up to 500 items; beyond that, consider pagination (NFR-049-F.6) |

## Out of Scope

- **`agent_write_allowlist` enforcement** — implemented when skill writes via API
- **`kb-articles` workflow action context key** — workflow integration for the skill
- **Batch operations** (select multiple files, bulk assign/remove) — future enhancement
- **Drag-and-drop reordering** within intake table — not in mockup
- **Lazy loading of folder children** — pre-loaded for simplicity per YAGNI; add if performance requires it (CR-005)
- **Sidecar `.meta.json` for non-markdown files** — replaced by `.kb-index.json` registry (CR-002)
- **YAML frontmatter for metadata** — replaced by `.kb-index.json` registry (CR-002); existing frontmatter in markdown files is NOT removed but no longer the source of truth

## Technical Considerations

- `.intake-status.json` schema: `{ "filename.ext": { "status": "pending|processing|filed", "destination": "folder/path/", "updated_at": "ISO8601" } }` — keys are relative file paths (e.g., `subfolder/file.md` for nested files); folder entries are NOT stored (status derived from children)
- `GET /api/kb/intake` response schema (CR-005): `{ "items": [ { "name": "file.md", "type": "file", "size": 1234, "uploaded": "ISO8601", "status": "pending", "destination": null, "path": "file.md" }, { "name": "folder/", "type": "folder", "item_count": 3, "status": "pending", "path": "folder", "children": [ ... ] } ], "stats": { "total": N, "pending": N, "processing": N, "filed": N }, "pending_deep_count": N }`
- Folder status derivation priority: pending > processing > filed (any pending child makes folder pending)
- Expand/collapse state is client-side only — not persisted across page reloads
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

None — all questions resolved via DAO (see `x-ipe-docs/dao/26-03-16/decisions_made_feature_refinement.md`, `x-ipe-docs/dao/26-03-18/decisions_made_change_request.md`). CR-005 folder support decisions: derived folder status, pre-loaded tree, folder-specific actions, filter propagation, deep-count badge, per-file AI Librarian processing.
CR-001 questions resolved: batch processing, destination priority (UI-assigned > AI), non-markdown handling, terminal summary, auto-create folders.
CR-002 questions resolved: metadata storage (`.kb-index.json` registry), locally-scoped indexes, folder metadata, description attribute (< 100 words).
