# Technical Design: KB AI Librarian & Intake

> Feature ID: FEATURE-049-F | Version: v1.1 | Last Updated: 03-16-2026

---

## Part 1: Agent-Facing Summary

> **Purpose:** Quick reference for AI agents navigating large projects.
> **📌 AI Coders:** Focus on this section for implementation context.

### Key Components Implemented

| Component | Responsibility | Scope/Impact | Tags |
|-----------|----------------|--------------|------|
| `KBService.get_intake_files()` | List .intake/ files merged with status from .intake-status.json | Intake file listing with status | #kb #intake #service #backend |
| `KBService.update_intake_status()` | Update a single file's status/destination in .intake-status.json | Status persistence | #kb #intake #status #backend |
| `KBConfig.ai_librarian` extension | Add `skill` field to ai_librarian config | Config schema | #kb #config #backend |
| `GET /api/kb/intake` | Route returning intake files with merged status | Intake API | #kb #intake #api #route |
| `PUT /api/kb/intake/status` | Route to update a file's intake status | Status update API | #kb #intake #api #route |
| `.github/skills/x-ipe-tool-kb-librarian/SKILL.md` | Tool skill: AI-powered intake file organizer — analyzes content, assigns tags, generates frontmatter, moves files | Skill file | #kb #librarian #skill #tool |
| `KBBrowseModal._renderIntakeScene()` | Full intake view: table, status badges, filters, statistics, per-file actions | Intake UI (mockup Scene 4) | #kb #intake #frontend #ui |
| `KBBrowseModal._runAILibrarian()` fix | Remove --workflow-mode, use plain NL command | Command fix | #kb #intake #frontend |

### Dependencies

| Dependency | Source | Design Link | Usage Description |
|------------|--------|-------------|-------------------|
| `KBService` | FEATURE-049-A | [x-ipe-docs/requirements/EPIC-049/FEATURE-049-A/technical-design.md](x-ipe-docs/requirements/EPIC-049/FEATURE-049-A/technical-design.md) | Base service for file/folder CRUD, config, tree, path safety |
| `kb_routes` | FEATURE-049-A | [x-ipe-docs/requirements/EPIC-049/FEATURE-049-A/technical-design.md](x-ipe-docs/requirements/EPIC-049/FEATURE-049-A/technical-design.md) | REST API blueprint, error handling pattern |
| `KBBrowseModal` | FEATURE-049-C | N/A | Browse modal class with scene switching, upload modes, intake scaffolding |
| `POST /api/kb/upload` | FEATURE-049-E | N/A | File upload with folder parameter (used for .intake uploads) |
| `PUT /api/kb/files/move` | FEATURE-049-A | N/A | Move files between folders (used for undo-filed) |

### Major Flow

1. User toggles to "AI Librarian" upload mode → files upload to `.intake/` via existing `POST /api/kb/upload` with `folder=.intake`
2. Intake view calls `GET /api/kb/intake` → service reads `.intake/` files + `.intake-status.json` → returns merged list
3. User clicks "✨ Run AI Librarian" → plain NL command sent to Copilot CLI → AI skill (future) processes files, updates `.intake-status.json`, moves files
4. Intake view refreshes → shows updated statuses (Pending → Processing → Filed)
5. User can: Preview files, Assign destination manually, Remove files, View filed files in KB, Undo filed files

### Usage Example

```python
# Backend: get intake files with status
svc = app.config['KB_SERVICE']
files = svc.get_intake_files()
# Returns: [
#   {"name": "notes.md", "size_bytes": 1024, "status": "pending", "destination": None, ...},
#   {"name": "doc.pdf", "size_bytes": 34000, "status": "filed", "destination": "guides/", ...}
# ]

# Backend: update status
svc.update_intake_status("notes.md", status="processing", destination="api-guidelines/")
```

```javascript
// Frontend: trigger AI Librarian
_runAILibrarian() {
    const command = 'organize knowledge base intake files with AI Librarian';
    window.terminalManager.sendCopilotPromptCommand(command);
}
```

---

## Part 2: Implementation Guide

> **Purpose:** Human-readable details for developers.
> **📌 Emphasis on visual diagrams for comprehension.**

### Workflow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant UI as KBBrowseModal
    participant API as kb_routes
    participant SVC as KBService
    participant FS as Filesystem (.intake/)
    participant CLI as Copilot CLI

    Note over U, CLI: Upload Phase
    U->>UI: Drop files (AI Librarian mode)
    UI->>API: POST /api/kb/upload (folder=.intake)
    API->>SVC: create_file/create_binary_file
    SVC->>FS: Write to .intake/

    Note over U, CLI: View Phase
    UI->>API: GET /api/kb/intake
    API->>SVC: get_intake_files()
    SVC->>FS: List .intake/ + read .intake-status.json
    SVC-->>API: Merged file list with statuses
    API-->>UI: JSON response
    UI-->>U: Render intake table

    Note over U, CLI: AI Librarian Phase
    U->>UI: Click "Run AI Librarian"
    UI->>CLI: Send NL command (no flags)
    Note over CLI: Future: x-ipe-tool-kb-librarian skill processes files
    CLI->>FS: Read .intake/, classify, move, update status.json

    Note over U, CLI: Manual Actions
    U->>UI: Assign folder / Remove / Undo
    UI->>API: PUT /api/kb/intake/status or DELETE/MOVE
    API->>SVC: update_intake_status() or existing methods
    SVC->>FS: Update .intake-status.json or move files
```

### State Diagram: Intake File Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Pending: File uploaded to .intake/
    Pending --> Processing: AI Librarian starts
    Pending --> Pending: User assigns destination (manual)
    Pending --> [*]: User removes file
    Processing --> Filed: AI moves file to destination
    Processing --> Pending: AI encounters error
    Filed --> Pending: User clicks Undo
    Filed --> [*]: File stays in KB folder
```

### Class Diagram

```mermaid
classDiagram
    class KBService {
        -kb_root: Path
        -config_path: Path
        +get_intake_files() List~Dict~
        +update_intake_status(filename, status, destination) Dict
        -_read_intake_status() Dict
        -_write_intake_status(data) None
        +get_tree() List~KBNode~
        +list_files(folder, sort, recursive) List~KBNode~
        +get_config() Dict
    }

    class KBConfig {
        +tags: Dict
        +agent_write_allowlist: List
        +allowed_extensions: List
        +ai_librarian: Dict
        +to_dict() Dict
    }

    class KBBrowseModal {
        -uploadMode: string
        -intakeFiles: Array
        -intakeStatus: Object
        -intakeFilter: string
        +_renderIntakeScene() void
        +_runAILibrarian() void
        +_loadIntakeFiles() Array
        +_filterIntakeByStatus(status) Array
        +_handleIntakeAction(action, file) void
    }

    KBService --> KBConfig: reads config
    KBBrowseModal --> KBService: via REST API
```

### Data Models

#### `.intake-status.json` Schema

```json
{
  "sprint-retro-notes-q1.md": {
    "status": "pending",
    "destination": null,
    "updated_at": "2026-03-16T10:30:00Z"
  },
  "architecture-decisions-adr.md": {
    "status": "processing",
    "destination": "api-guidelines/",
    "updated_at": "2026-03-16T10:35:00Z"
  },
  "logo-variants-2026.svg": {
    "status": "filed",
    "destination": "brand-assets/",
    "updated_at": "2026-03-16T10:40:00Z"
  }
}
```

**Rules:**
- File in `.intake/` with NO status.json entry → status = `"pending"`, destination = `null`
- Status.json entry for file NOT in `.intake/` → silently ignored (stale)
- Corrupted/missing status.json → all files = `"pending"`

#### KBConfig.ai_librarian Extension

```python
ai_librarian: Dict[str, Any] = field(default_factory=lambda: {
    'enabled': False,
    'intake_folder': '.intake',
    'skill': 'x-ipe-tool-kb-librarian',
})
```

#### GET /api/kb/intake Response

```json
{
  "files": [
    {
      "name": "sprint-retro-notes-q1.md",
      "path": ".intake/sprint-retro-notes-q1.md",
      "size_bytes": 24576,
      "modified_date": "2026-03-11T00:00:00",
      "file_type": "md",
      "status": "pending",
      "destination": null
    }
  ],
  "stats": {
    "total": 5,
    "pending": 3,
    "processing": 1,
    "filed": 1
  }
}
```

#### PUT /api/kb/intake/status Request/Response

```json
// Request
{ "filename": "notes.md", "status": "pending", "destination": "api-guidelines/" }

// Response (200)
{ "ok": true, "filename": "notes.md", "status": "pending", "destination": "api-guidelines/" }

// Error (404)
{ "error": "FILE_NOT_FOUND", "message": "File not in .intake/" }
```

### Implementation Steps

#### 1. Backend: KBConfig Extension (~5 lines)

In `kb_service.py`, update `KBConfig.ai_librarian` default to include `skill` field:

```python
ai_librarian: Dict[str, Any] = field(default_factory=lambda: {
    'enabled': False,
    'intake_folder': '.intake',
    'skill': 'x-ipe-tool-kb-librarian',
})
```

#### 2. Backend: Intake Service Methods (~80 lines in kb_service.py)

Add to `KBService`:

**`_read_intake_status()`** — Private helper. Reads `.intake-status.json` from `.intake/` folder. Returns empty dict on missing/corrupt file (logs warning).

**`_write_intake_status(data)`** — Private helper. Writes status dict to `.intake-status.json` using the existing `_write_json()` method (atomic temp+rename pattern, same as config writes).

**`get_intake_files()`** — Public method:
1. List all files in `.intake/` using `os.scandir()` (skip `.intake-status.json` itself and directories)
2. Read status via `_read_intake_status()`
3. For each file: merge filesystem metadata (name, size, modified) with status entry (default: `pending`, destination: `null`)
4. Calculate stats: total, pending, processing, filed counts
5. Return `{"files": [...], "stats": {...}}`

**`update_intake_status(filename, status, destination=None)`** — Public method:
1. Verify file exists in `.intake/` (raise ValueError if not)
2. Read current status dict
3. Update/add entry for filename
4. Write back atomically
5. Invalidate cache

#### 3. Backend: Intake Routes (~40 lines in kb_routes.py)

**`GET /api/kb/intake`:**
```python
@kb_bp.route('/api/kb/intake')
def get_intake():
    svc = _get_kb_service_or_abort()
    return jsonify(svc.get_intake_files())
```

**`PUT /api/kb/intake/status`:**
```python
@kb_bp.route('/api/kb/intake/status', methods=['PUT'])
def update_intake_status():
    svc = _get_kb_service_or_abort()
    data = request.get_json(force=True)
    filename = data.get('filename', '').strip()
    status = data.get('status', '').strip()
    destination = data.get('destination')
    # Validate
    if not filename or status not in ('pending', 'processing', 'filed'):
        return _error('INVALID_INPUT', 'filename and valid status required', 400)
    try:
        result = svc.update_intake_status(filename, status, destination)
        return jsonify(result)
    except ValueError as e:
        return _error('FILE_NOT_FOUND', str(e), 404)
```

#### 4. Frontend: Fix _runAILibrarian() (~3 lines in kb-browse-modal.js)

```javascript
_runAILibrarian() {
    const command = 'organize knowledge base intake files with AI Librarian';
    // ... rest unchanged
}
```

#### 5. Frontend: Enhanced Intake Scene (~200 lines in kb-browse-modal.js)

Update `_renderIntakeScene()` to match mockup Scene 4:

**Header:** Title + "✨ Run AI Librarian" gradient purple button
**Statistics bar:** Total (purple), Pending (orange), Processing (blue), Filed (green) badges
**Filter pills:** All | Pending | Processing | Filed — toggles `this.intakeFilter`
**Intake table:** File | Size | Uploaded | Status | Destination | Actions columns
**Empty state:** When `files.length === 0`, show drop zone with "Drop more files into Intake, or browse" message instead of table
**Row styling:** Pending = normal, Processing = blue bg, Filed = dimmed (opacity 0.7)
**Actions per status:**
- Pending: Preview (eye), Assign (folder), Remove (X)
- Processing: all disabled
- Filed: View in KB (arrow), Undo (refresh)
**Drop zone:** Purple dashed border at bottom

#### 6. Frontend: Intake Data Loading (~30 lines)

Update `_loadIntakeFiles()` to use `GET /api/kb/intake`:
```javascript
async _loadIntakeFiles() {
    try {
        const res = await fetch('/api/kb/intake');
        if (!res.ok) return { files: [], stats: { total: 0, pending: 0, processing: 0, filed: 0 } };
        return await res.json();
    } catch { return { files: [], stats: { total: 0, pending: 0, processing: 0, filed: 0 } }; }
}
```

#### 7. Frontend: Per-File Action Handlers (~60 lines)

Implement a single dispatcher method `_handleIntakeAction(action, file)` that routes to action-specific logic:

**Preview:** Reuse existing article preview (call `_showScene('article')` with file data)
**Assign folder:** Show folder picker (reuse existing `_showFolderPicker()` from browse modal — the picker already lists KB folders excluding `.intake/`), then `PUT /api/kb/intake/status` with destination
**Remove:** Confirm → `DELETE /api/kb/files/.intake/{filename}` → refresh
**View in KB:** Navigate browse view to destination folder
**Undo:** `PUT /api/kb/files/move` (source: destination path, target: `.intake/{filename}`) → `PUT /api/kb/intake/status` (status: pending, destination: null) → refresh

#### 8. Frontend: Sidebar Intake Badge (~10 lines)

In `_renderSidebarFolders()`, update the "📥 Intake" entry to show pending count badge fetched from `GET /api/kb/intake` stats.

### Edge Cases & Error Handling

| Scenario | Expected Behavior | Component |
|----------|-------------------|-----------|
| `.intake-status.json` corrupted | `_read_intake_status()` returns `{}`, logs warning | KBService |
| `.intake-status.json` missing | Returns `{}` (all files = pending) | KBService |
| File in status.json but deleted from .intake | Ignored in merge (stale entry) | KBService.get_intake_files() |
| `.intake/` folder doesn't exist | `get_intake_files()` returns empty, `_uploadIntakeFiles()` creates it | KBService / frontend |
| Concurrent status writes | `_write_intake_status()` uses atomic write (temp+rename) | KBService |
| Undo filed: destination folder gone | Move fails → show error toast | Frontend |
| Duplicate filename upload | Handled by existing upload route (numeric suffix) | kb_routes upload |
| ai_librarian.enabled = false | Frontend hides all intake UI | KBBrowseModal |

### Step 9: Create `x-ipe-tool-kb-librarian` Skill (CR-001)

**Files:** `.github/skills/x-ipe-tool-kb-librarian/SKILL.md`
**program_type:** skills
**Created via:** `x-ipe-meta-skill-creator`

#### Skill Architecture

```mermaid
sequenceDiagram
    participant User
    participant CLI as Copilot CLI
    participant Agent as Agent (executing skill)
    participant KB as KB Service API
    participant FS as Filesystem

    User->>CLI: "✨ Run AI Librarian"
    CLI->>Agent: NL command: "organize knowledge base intake files with AI Librarian"
    Agent->>Agent: Load x-ipe-tool-kb-librarian SKILL.md
    Agent->>KB: GET /api/kb/config (read tag taxonomy)
    Agent->>KB: GET /api/kb/intake (get pending files)

    loop For each pending file
        Agent->>KB: PUT /api/kb/intake/status (status → "processing")
        Agent->>FS: Read file content
        Agent->>Agent: AI: analyze content → determine folder + tags
        alt Markdown file
            Agent->>Agent: Generate/merge YAML frontmatter
            Agent->>KB: PUT /api/kb/files/{path} (write updated content)
        end
        Agent->>KB: POST /api/kb/files/move (move to destination)
        Agent->>KB: PUT /api/kb/intake/status (status → "filed", destination)
    end

    Agent->>CLI: Print summary: "N files processed → folder1/, folder2/"
```

#### Skill State Machine

```mermaid
stateDiagram-v2
    [*] --> ReadConfig: Skill invoked
    ReadConfig --> GetIntakeFiles: Config loaded
    GetIntakeFiles --> CheckPending: Files retrieved
    CheckPending --> Exit_NoPending: No pending files
    CheckPending --> ProcessFile: Has pending files

    state ProcessFile {
        [*] --> SetProcessing
        SetProcessing --> AnalyzeContent: Status updated
        AnalyzeContent --> DetermineDestination: Content analyzed
        DetermineDestination --> AssignTags: Folder selected
        AssignTags --> GenerateFrontmatter: Tags assigned
        GenerateFrontmatter --> MoveFile: Frontmatter ready (md) or skipped (non-md)
        MoveFile --> SetFiled: File moved
        SetFiled --> [*]: Status → filed
    }

    ProcessFile --> NextFile: File done
    NextFile --> ProcessFile: More files
    NextFile --> PrintSummary: All done
    PrintSummary --> [*]
    Exit_NoPending --> [*]
```

#### Skill SKILL.md Structure

The skill follows the x-ipe tool skill template:

```yaml
# SKILL.md structure
name: x-ipe-tool-kb-librarian
description: "Organize knowledge base intake files — analyze content, assign tags, generate frontmatter, move to destination folders."
triggers:
  - "organize knowledge base intake files with AI Librarian"
  - "run AI Librarian"
  - "organize intake"

input:
  kb_root: "auto-detect from project"  # x-ipe-docs/knowledge-base/
  intake_folder: ".intake"              # from kb-config.json

operations:
  - organize_intake:
      1. Read KB config (tag taxonomy, folder structure)
      2. Get all intake files via GET /api/kb/intake
      3. Filter to status == "pending"
      4. For each file:
         a. Update status → "processing"
         b. Read file content
         c. AI: analyze → determine destination folder + lifecycle/domain tags
         d. If destination pre-assigned in status.json → use it (skip AI folder selection)
         e. If markdown: generate/merge frontmatter (title, tags, author, created, auto_generated=true)
         f. If destination folder doesn't exist → create it
         g. Move file from .intake/ to destination
         h. Update status → "filed" with destination path
      5. Print terminal summary

output:
  files_processed: int
  destinations: list[str]
  errors: list[str]  # files that failed (continued processing others)
```

#### Key Design Decisions (from DAO)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Processing mode | Batch all pending | KISS — user clicked button = intent to process all |
| Folder determination | UI-assigned > AI fallback | Respect explicit user choices, AI fills gaps |
| Non-markdown files | Move + status track, skip frontmatter | Can't inject YAML into PDFs/images |
| Summary output | Terminal print | Simple, visible, no file overhead |
| Folder creation | Auto-create if needed | Cheap, reversible, preserves AI accuracy |
| Existing frontmatter | Preserve + merge (no overwrite) | Non-destructive, respect original metadata |

#### AI Classification Approach

The agent executing this skill uses its LLM capabilities to:
1. **Read file content** — extract key topics, domain terminology, structure
2. **Scan KB folder structure** — understand existing organization (via tree API)
3. **Match content to folder** — semantic matching of content topics to folder names/purposes
4. **Assign tags** — select from the config-defined taxonomy:
   - Lifecycle: Ideation, Requirement, Design, Implementation, Testing, Deployment, Maintenance
   - Domain: API, Authentication, UI-UX, Database, Infrastructure, Security, Performance, Integration, Documentation, Analytics
5. **Generate title** — derive from filename or first heading

No external AI API calls needed — the executing agent IS the LLM.

### Step 10: `.kb-index.json` Metadata Registry (CR-002)

**Motivation:** Replace frontmatter-embedded metadata with a centralized, per-folder JSON registry. Works for ALL file types (images, videos, PDFs) and supports folder-level metadata.

#### Architecture Overview

```mermaid
graph TB
    subgraph "KB Folder: guides/"
        IDX1[".kb-index.json"]
        F1["setup.md"]
        F2["diagram.png"]
        SF1["tutorials/"]
    end

    subgraph "KB Folder: guides/tutorials/"
        IDX2[".kb-index.json"]
        F3["quickstart.md"]
        F4["demo.mp4"]
    end

    IDX1 -->|indexes| F1
    IDX1 -->|indexes| F2
    IDX1 -->|indexes| SF1
    IDX2 -->|indexes| F3
    IDX2 -->|indexes| F4

    style IDX1 fill:#f9f,stroke:#333
    style IDX2 fill:#f9f,stroke:#333
```

**Key Design Principle:** Each `.kb-index.json` is locally-scoped — it indexes ONLY the files and immediate subfolders in its own directory. Nested subdirectories have their own `.kb-index.json`.

#### `.kb-index.json` Schema

```json
{
  "version": "1.0",
  "entries": {
    "setup.md": {
      "title": "Environment Setup Guide",
      "description": "Step-by-step guide for setting up the local development environment with required tools and dependencies.",
      "tags": {
        "domain": ["infrastructure"],
        "lifecycle": ["implementation"]
      },
      "author": "yzhang",
      "created": "2026-03-16",
      "type": "markdown",
      "auto_generated": false
    },
    "diagram.png": {
      "title": "Architecture Diagram",
      "description": "High-level system architecture showing component interactions and data flow paths.",
      "tags": {
        "domain": ["infrastructure"],
        "lifecycle": ["design"]
      },
      "author": "unknown",
      "created": "2026-03-16",
      "type": "image",
      "auto_generated": false
    },
    "tutorials/": {
      "title": "Tutorial Materials",
      "description": "Collection of quickstart guides and demo videos for onboarding new team members.",
      "tags": {
        "domain": ["documentation"],
        "lifecycle": ["implementation"]
      }
    }
  }
}
```

**Schema Rules:**
- `version`: Always `"1.0"` (for future schema migrations)
- Keys: filename for files, foldername + `/` for subfolders
- `type` field (files only): `markdown`, `image`, `video`, `pdf`, `document`, `other`
- `description`: Max 100 words, plain text
- `auto_generated`: Whether metadata was AI-generated (default `false`)
- Missing entry = file has no metadata (defaults from filename/extension)
- Folder entries do NOT have `type`, `author`, `created`, or `auto_generated` fields

#### Type Detection

```python
EXTENSION_TYPE_MAP = {
    '.md': 'markdown',
    '.png': 'image', '.jpg': 'image', '.jpeg': 'image',
    '.gif': 'image', '.svg': 'image', '.webp': 'image',
    '.mp4': 'video', '.mov': 'video', '.webm': 'video', '.avi': 'video',
    '.pdf': 'pdf',
    '.doc': 'document', '.docx': 'document', '.xls': 'document',
    '.xlsx': 'document', '.ppt': 'document', '.pptx': 'document',
}
# Default: 'other'
```

#### New/Refactored Methods in `kb_service.py`

| Method | Type | Purpose |
|--------|------|---------|
| `_read_kb_index(folder_path)` | New | Read `.kb-index.json` from folder; return `{}` entries if missing |
| `_write_kb_index(folder_path, index_data)` | New | Atomic write `.kb-index.json` to folder (temp+rename) |
| `_get_index_entry(folder_path, name)` | New | Get single entry from folder's index; return `None` if missing |
| `_set_index_entry(folder_path, name, entry)` | New | Set/update single entry in folder's index |
| `_remove_index_entry(folder_path, name)` | New | Remove entry from folder's index |
| `_auto_populate_index_entry(filename)` | Refactor | Default metadata from filename/extension (was `_auto_populate_frontmatter`) |
| `_detect_file_type(filename)` | New | Map file extension to type string |
| `_migrate_frontmatter_to_index(folder_path)` | New | One-time: read YAML frontmatter from .md files, write to `.kb-index.json` |

#### Migration Strategy (Frontmatter → Index)

```
For each KB folder:
  1. Scan for .md files with YAML frontmatter
  2. Parse frontmatter (title, tags, author, created)
  3. Write entries to .kb-index.json (preserve all existing values)
  4. Do NOT remove frontmatter from .md files (non-destructive)
  5. Mark index entries with auto_generated: false (human-authored frontmatter)
```

After migration, `_ensure_file_index()` reads from `.kb-index.json` instead of parsing frontmatter.

#### API Compatibility

The API response shape is preserved — no frontend changes needed:

```
Before (frontmatter):  file.frontmatter.title → from YAML in .md file
After (index):         file.frontmatter.title → from .kb-index.json entry
```

The `frontmatter` key in API responses is kept for backwards compatibility but now sourced from the index. Future API versions may rename it to `metadata`.

#### Sequence: File Creation with Index Entry

```mermaid
sequenceDiagram
    participant Client
    participant Routes
    participant KBService
    participant FS as Filesystem

    Client->>Routes: POST /api/kb/files (content, metadata)
    Routes->>KBService: create_file(path, content, metadata)
    KBService->>FS: Write file content (no frontmatter injection)
    KBService->>KBService: _auto_populate_index_entry(filename)
    KBService->>KBService: merge provided metadata with defaults
    KBService->>KBService: _set_index_entry(folder, filename, entry)
    KBService->>FS: Atomic write .kb-index.json
    KBService-->>Routes: {name, path, metadata}
    Routes-->>Client: 201 Created
```

### File Change Summary

| File | Changes | Est. Lines |
|------|---------|------------|
| `src/x_ipe/services/kb_service.py` | Add `_read_kb_index()`, `_write_kb_index()`, `_get/set/remove_index_entry()`, `_auto_populate_index_entry()`, `_detect_file_type()`, `_migrate_frontmatter_to_index()`. Refactor tree building to read from index. Update `create_file()`, `update_file()`, `move_file()` to write index entries. Keep `_parse_frontmatter()` for migration only. | ~150 |
| `src/x_ipe/routes/kb_routes.py` | Minimal — API response shape preserved. Update `create_file`/`update_file` params for metadata (was frontmatter). | ~10 |
| `src/x_ipe/static/js/features/kb-browse-modal.js` | No changes — consumes same `file.frontmatter` JSON shape from API | 0 |
| `.github/skills/x-ipe-tool-kb-librarian/SKILL.md` | Update procedure: generate index entries instead of frontmatter. Remove markdown-only gate. All file types get metadata. | ~30 |
| `tests/test_kb_service.py` | Update frontmatter tests → index tests. Add `.kb-index.json` read/write/migrate tests. | ~80 |
| `tests/frontend-js/kb-intake-049f.test.js` | No changes — tests mock API response, not internal storage | 0 |

---

## Design Change Log

| Date | Phase | Change Summary |
|------|-------|----------------|
| 03-16-2026 | Initial Design | Initial technical design for FEATURE-049-F. Backend: intake status service + 2 routes. Frontend: full intake scene matching mockup Scene 4 with status tracking, filters, per-file actions. Command fix: remove --workflow-mode. |
| 03-16-2026 | CR-001 Skill Design | Added Step 9: x-ipe-tool-kb-librarian skill design. program_type=skills. Sequence diagram, state machine, SKILL.md structure, AI classification approach, 6 DAO-driven decisions. |
| 03-17-2026 | CR-002 Metadata Registry | Added Step 10: .kb-index.json registry design. Replaces frontmatter-embedded metadata. Per-folder hidden JSON index, folder metadata support, description field (< 100 words). Migration strategy, API compatibility, new/refactored methods. |
