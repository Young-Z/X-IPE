# Feature Specification: KB Core Infrastructure

> Feature ID: FEATURE-025-A  
> Version: v1.0  
> Status: Refined  
> Last Updated: 02-05-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.0 | 02-05-2026 | Initial specification | - |

## Linked Mockups

| Mockup Name | Description | Path |
|-------------|-------------|------|
| kb-landing-view | Landing view showing sidebar integration and folder structure | [knowledge-base-v1.html](mockups/knowledge-base-v1.html) |
| kb-processed-view | Processed/Topics view showing content organization | [knowledge-base-processed-v1.html](mockups/knowledge-base-processed-v1.html) |

## Overview

**What:** FEATURE-025-A establishes the foundational infrastructure for the Knowledge Base system, including folder structure, file index, metadata management, and sidebar integration into the X-IPE Workplace interface.

**Why:** Without core infrastructure, subsequent Knowledge Base features (Landing Zone, Search, Topics) cannot function. This feature creates the essential scaffolding that all other KB sub-features depend on.

**Who:** 
- End users who want to organize project knowledge
- AI agents that need to access indexed knowledge for RAG
- Developers building KB-dependent features (025-B through 025-F)

## User Stories

| ID | User Story | Priority |
|----|------------|----------|
| US-1 | As a **user**, I want to **see a Knowledge Base menu item under Workplace**, so that **I can access my organized knowledge from the sidebar** | Must |
| US-2 | As a **user**, I want to **have a dedicated folder structure for knowledge**, so that **raw uploads, topics, and summaries are organized separately** | Must |
| US-3 | As a **user**, I want to **see an index of all knowledge items**, so that **I can quickly find content without browsing folders** | Must |
| US-4 | As a **user**, I want to **refresh the knowledge index**, so that **manually added files are recognized by the system** | Must |
| US-5 | As a **developer**, I want to **have a standardized metadata format per topic**, so that **I can build features that rely on consistent data structures** | Must |

## Acceptance Criteria

### 1. Sidebar Integration

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-1.1 | "Knowledge Base" submenu MUST appear under Workplace section in sidebar | Navigate to app → Workplace section shows "Knowledge Base" submenu item |
| AC-1.2 | Submenu MUST use icon `bi-archive` or `bi-database` | Inspect sidebar → KB item has Bootstrap Icons class `bi-archive` or `bi-database` |
| AC-1.3 | Submenu MUST always be visible (even when knowledge base is empty) | Delete all KB content → Submenu still visible |
| AC-1.4 | Clicking submenu MUST switch content area to Knowledge Base view | Click "Knowledge Base" → Content area shows KB view component |

### 2. Folder Structure

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-2.1 | Knowledge Base files MUST be stored in `x-ipe-docs/knowledge-base/` folder | Check file system → folder exists at specified path |
| AC-2.2 | `landing/` subfolder MUST exist for raw uploaded files | Check `x-ipe-docs/knowledge-base/landing/` exists |
| AC-2.3 | `topics/` subfolder MUST exist for organized knowledge | Check `x-ipe-docs/knowledge-base/topics/` exists |
| AC-2.4 | `processed/` subfolder MUST exist for AI-generated summaries | Check `x-ipe-docs/knowledge-base/processed/` exists |
| AC-2.5 | `index/` subfolder MUST contain `file-index.json` | Check `x-ipe-docs/knowledge-base/index/file-index.json` exists |
| AC-2.6 | Each topic folder MUST have `raw/` subfolder and `metadata.json` | Create topic "test" → `topics/test/raw/` and `topics/test/metadata.json` exist |

### 3. Index Schema

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-3.1 | `file-index.json` MUST contain file entries with: path, name, type, size, topic, created_date, keywords | Read index → Each entry has all required fields |
| AC-3.2 | Index MUST be valid JSON parseable by standard libraries | `JSON.parse(file-index.json)` succeeds without error |
| AC-3.3 | Index entries MUST have unique identifiers (file path serves as ID) | Read index → No duplicate paths |
| AC-3.4 | Index MUST include files from all KB subfolders (landing, topics, processed) | Add files to each folder → All appear in index |

### 4. Topic Metadata Schema

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-4.1 | `metadata.json` per topic MUST contain: name, description, file_count, last_updated, tags | Read metadata → All required fields present |
| AC-4.2 | `file_count` MUST accurately reflect number of files in topic's `raw/` folder | Add 3 files → file_count = 3 |
| AC-4.3 | `last_updated` MUST be ISO 8601 timestamp | Read metadata → last_updated matches YYYY-MM-DDTHH:MM:SS format |
| AC-4.4 | `tags` MUST be an array of strings | Read metadata → tags is array, items are strings |

### 5. Index Operations

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-5.1 | "Refresh" button MUST appear in top bar when KB view is active | Navigate to KB view → "Refresh" button visible in top bar |
| AC-5.2 | Clicking "Refresh" MUST rebuild index from file system | Add file manually → Click Refresh → File appears in index |
| AC-5.3 | Index rebuild MUST complete without blocking UI | Click Refresh → UI remains responsive during rebuild |
| AC-5.4 | Index rebuild MUST show progress indicator for large collections | Add 100+ files → Refresh shows loading indicator |

### 6. Initialization

| # | Acceptance Criteria | Testable Condition |
|---|---------------------|-------------------|
| AC-6.1 | First visit to KB view MUST auto-create folder structure if missing | Delete KB folder → Navigate to KB → Folders auto-created |
| AC-6.2 | Auto-created index MUST be empty but valid JSON | Auto-create → index contains `{"files": [], "last_updated": "..."}` |
| AC-6.3 | Folder creation MUST NOT overwrite existing content | Have existing files → Navigate to KB → Files preserved |

## Functional Requirements

### FR-1: Sidebar Menu Registration

**Input:** Application startup
**Process:**
1. Register "Knowledge Base" as submenu item under "Workplace" section
2. Use icon class `bi-archive`
3. Set route to `/workplace/knowledge-base`
4. Set display order after existing Workplace items (Ideation)

**Output:** Sidebar renders KB menu item on every page load

### FR-2: Folder Structure Initialization

**Input:** User navigates to Knowledge Base view (first time or after folder deletion)
**Process:**
1. Check if `x-ipe-docs/knowledge-base/` exists
2. If not exists, create folder structure:
   ```
   knowledge-base/
   ├── landing/
   ├── topics/
   ├── processed/
   └── index/
       └── file-index.json (empty: {"files": [], "last_updated": "..."})
   ```
3. If exists, do not modify

**Output:** Folder structure guaranteed to exist before any KB operations

### FR-3: File Index Management

**Input:** File added, moved, or deleted in KB folders
**Process:**
1. Detect file system change (via watcher or explicit refresh)
2. Scan all KB subfolders recursively
3. For each file, extract: path, name, extension→type, size, parent→topic, mtime→created_date
4. Generate keywords from filename (split on `-`, `_`, spaces)
5. Write updated entries to `file-index.json`
6. Update `last_updated` timestamp

**Output:** Index reflects current file system state

### FR-4: Topic Metadata Management

**Input:** Topic folder created or modified
**Process:**
1. When topic folder created, generate `metadata.json`:
   ```json
   {
     "name": "{folder-name}",
     "description": "",
     "file_count": 0,
     "last_updated": "2026-02-05T15:00:00Z",
     "tags": []
   }
   ```
2. When files added/removed from topic, update `file_count` and `last_updated`
3. Description and tags are editable via UI (future feature)

**Output:** Each topic has accurate metadata

### FR-5: Index Refresh Operation

**Input:** User clicks "Refresh" button in KB view top bar
**Process:**
1. Show loading indicator
2. Perform full index rebuild (FR-3)
3. Update all topic metadata (FR-4)
4. Hide loading indicator
5. Refresh UI to show updated content

**Output:** Index and metadata synchronized with file system

## Non-Functional Requirements

| # | Requirement | Metric | Priority |
|---|-------------|--------|----------|
| NFR-1 | Folder initialization MUST complete within 1 second | < 1000ms for empty KB | Must |
| NFR-2 | Index refresh MUST complete within 5 seconds for 1000 files | < 5000ms for 1000 files | Should |
| NFR-3 | Index file MUST NOT exceed 5MB for 1000 files | < 5MB at 1000 files | Should |
| NFR-4 | Sidebar menu MUST render within 100ms of page load | < 100ms sidebar render | Must |
| NFR-5 | Index JSON MUST be human-readable (pretty-printed) | 2-space indentation | Should |

## UI/UX Requirements

### UI-1: Sidebar Integration

**Based on mockup:** [knowledge-base-v1.html](mockups/knowledge-base-v1.html)

| Element | Specification |
|---------|--------------|
| Menu Position | Under "Workplace" section, after "Ideation" |
| Icon | `bi-archive` (Bootstrap Icons) |
| Label | "Knowledge Base" |
| Indent | Same level as "Ideation" (nested under Workplace) |
| Active State | Highlight when KB view is active |

### UI-2: KB View Layout

| Element | Specification |
|---------|--------------|
| Content Area | Full width of main content panel |
| Top Bar | Contains: View title, Refresh button, (future: Upload, Search) |
| Refresh Button | Icon: `bi-arrow-clockwise`, tooltip: "Refresh Index" |
| Loading State | Spinner overlay during refresh operation |

### UI-3: Empty State

When knowledge base is empty (no files):
- Show centered message: "Your Knowledge Base is empty"
- Show subtext: "Upload files to get started"
- Show upload icon/button placeholder (actual upload in FEATURE-025-B)

## Dependencies

### Internal Dependencies

| Dependency | Type | Description | Status |
|------------|------|-------------|--------|
| FEATURE-008 | Feature | Workplace framework provides sidebar and content area infrastructure | Implemented |

### External Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| File System | System | Read/write access to `x-ipe-docs/knowledge-base/` |
| Flask Backend | System | API endpoints for index operations |
| Bootstrap Icons | Library | Icon font for sidebar and buttons |

## Business Rules

| # | Rule | Rationale |
|---|------|-----------|
| BR-1 | KB folder MUST be inside `x-ipe-docs/` | Keeps knowledge with project documentation |
| BR-2 | Index MUST be JSON format | Ensures compatibility with web frontend and AI agents |
| BR-3 | Topic names MUST be valid folder names | Filesystem compatibility (no special chars) |
| BR-4 | Empty KB folders MUST NOT be deleted automatically | Preserves user-created structure |
| BR-5 | Index refresh MUST NOT delete orphaned entries immediately | Gives users time to restore accidentally deleted files |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| KB folder deleted while app running | Re-create on next navigation to KB view |
| Invalid JSON in file-index.json | Log error, recreate empty index |
| Permission denied on folder creation | Show error toast, suggest checking permissions |
| Topic folder with no metadata.json | Auto-generate metadata on index refresh |
| File with no extension | Type = "unknown", still indexed |
| Very long filename (>255 chars) | Truncate in display, preserve in index |
| Concurrent index updates | Last-write-wins (simple approach for MVP) |
| Unicode filenames | Fully supported, UTF-8 encoding |

## Out of Scope

- File upload functionality (FEATURE-025-B)
- Search functionality (FEATURE-025-E)
- AI processing/summarization (FEATURE-025-C)
- Topic view and management UI (FEATURE-025-D)
- Navigation tabs (Landing/Topics) (FEATURE-025-F)
- Vector embeddings or semantic search (Phase 2)
- Real-time file watching (manual refresh for MVP)

## Technical Considerations

### Backend API Endpoints

```
GET  /api/kb/index          - Get current file index
POST /api/kb/index/refresh  - Trigger index rebuild
GET  /api/kb/topics         - List all topics with metadata
GET  /api/kb/topics/{name}  - Get specific topic metadata
```

### Index Schema (file-index.json)

```json
{
  "version": "1.0",
  "last_updated": "2026-02-05T15:00:00Z",
  "files": [
    {
      "path": "landing/document.pdf",
      "name": "document.pdf",
      "type": "pdf",
      "size": 1024567,
      "topic": null,
      "created_date": "2026-02-05T14:30:00Z",
      "keywords": ["document"]
    },
    {
      "path": "topics/ai-research/raw/paper.pdf",
      "name": "paper.pdf",
      "type": "pdf",
      "size": 2048000,
      "topic": "ai-research",
      "created_date": "2026-02-04T10:00:00Z",
      "keywords": ["paper"]
    }
  ]
}
```

### Topic Metadata Schema (metadata.json)

```json
{
  "name": "ai-research",
  "description": "Research papers and notes on AI topics",
  "file_count": 5,
  "last_updated": "2026-02-05T15:00:00Z",
  "tags": ["ai", "machine-learning", "research"]
}
```

### File Type Mapping

| Extension(s) | Type |
|--------------|------|
| .pdf | pdf |
| .md, .markdown | markdown |
| .txt | text |
| .docx | docx |
| .xlsx | xlsx |
| .py | python |
| .js, .ts | javascript |
| .java | java |
| .png, .jpg, .jpeg, .gif | image |
| (none) | unknown |

## Open Questions

| # | Question | Status | Resolution |
|---|----------|--------|------------|
| OQ-1 | Should index include file content hash for duplicate detection? | Open | Defer to FEATURE-025-B (upload handles duplicates) |
| OQ-2 | Should we support nested topics (topics within topics)? | Resolved | No - flat topic structure for MVP |
| OQ-3 | How to handle symlinks in KB folder? | Resolved | Ignore symlinks for MVP |

---

## Appendix: Folder Structure Diagram

```
x-ipe-docs/
└── knowledge-base/
    ├── landing/                    # Raw uploads awaiting processing
    │   ├── document1.pdf
    │   └── notes.md
    │
    ├── topics/                     # Organized by topic
    │   ├── ai-research/
    │   │   ├── raw/               # Original files for this topic
    │   │   │   ├── paper1.pdf
    │   │   │   └── paper2.pdf
    │   │   └── metadata.json      # Topic metadata
    │   │
    │   └── project-ideas/
    │       ├── raw/
    │       │   └── brainstorm.md
    │       └── metadata.json
    │
    ├── processed/                  # AI-generated summaries
    │   ├── ai-research/
    │   │   ├── summary-v1.md
    │   │   └── summary-v2.md
    │   └── project-ideas/
    │       └── summary-v1.md
    │
    └── index/
        └── file-index.json        # Search index
```
