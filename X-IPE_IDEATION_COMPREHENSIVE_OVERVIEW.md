# X-IPE Ideation Feature - Comprehensive Overview

## Executive Summary

X-IPE implements a **file-system-based ideation system** (FEATURE-008: Workplace) integrated with the engineering workflow engine. Instead of using a database, all ideas are stored in the `x-ipe-docs/ideas/` directory. Users can create, edit, refine, and organize ideas through a web UI, with automatic workflow integration for the ideation stage.

**Key Stats:**
- **21 API Endpoints** for idea CRUD operations
- **30+ Service Methods** in IdeasService
- **2 Main Workflows:** Compose Idea → Refine Idea (mandatory in ideation stage)
- **File-Based Storage:** Git-friendly, no database dependency
- **Integrated with Workflow Manager:** Workflow state automatically updated when ideas are composed/refined

---

## 1. ROUTES & ENDPOINTS (21 Total)

### 1.1 Tree & Browse Operations (5 endpoints)

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|-----------|
| `/api/ideas/tree` | GET | Get complete tree structure | None |
| `/api/ideas/folder-contents` | GET | Get folder contents (lazy load) | `path` (optional) |
| `/api/ideas/search` | GET | Search ideas by query | `q` (search string) |
| `/api/ideas/delete-info` | GET | Get item info for delete dialog | `path` (required) |
| `/api/ideas/file` | GET | Serve file content (auto-converts DOCX/MSG) | `path` (required) |

**Key Feature:** Auto-conversion of DOCX → HTML and MSG → HTML (CR-001)

### 1.2 Create Operations (2 endpoints)

| Endpoint | Method | Purpose | Key Parameters |
|----------|--------|---------|-----------------|
| `/api/ideas/upload` | POST | Upload files to new/existing folder | `files`, `target_folder` (opt), `kb_references` (opt) |
| `/api/ideas/create-folder` | POST | Create empty folder | `folder_name`, `parent_folder` (opt) |

**Feature CR-002:** Support uploading to existing target folder  
**Feature CR-004:** Attach KB references when uploading

### 1.3 Rename/Edit Operations (2 endpoints)

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|-----------|
| `/api/ideas/rename` | POST | Rename top-level folder | `old_name`, `new_name` |
| `/api/ideas/rename-file` | POST | Rename file within ideas | `path`, `new_name` |

### 1.4 Delete Operations (1 endpoint)

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|-----------|
| `/api/ideas/delete` | POST | Delete file/folder recursively | `path` |

### 1.5 Move & Transform Operations (4 endpoints)

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|-----------|
| `/api/ideas/move` | POST | Move item to new folder | `source_path`, `target_folder` |
| `/api/ideas/duplicate` | POST | Duplicate item with `-copy` suffix | `path` |
| `/api/ideas/validate-drop` | POST | Validate drag-drop target | `source_path`, `target_folder` |
| `/api/ideas/download` | GET | Download file | `path` |

**Feature CR-006:** Tree UX enhancements (drag-drop, duplicate, move)

### 1.6 Configuration Operations (2 endpoints)

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|-----------|
| `/api/ideas/toolbox` | GET | Get ideation toolbox config | None |
| `/api/ideas/toolbox` | POST | Save toolbox config | `{ideation, mockup, sharing}` |

**Toolbox Config Structure:**
```json
{
    "version": "1.0",
    "ideation": {
        "x-ipe-tool-infographic-syntax": false,
        "mermaid": true
    },
    "mockup": {
        "frontend-design": true
    },
    "sharing": {}
}
```

### 1.7 Knowledge Base Integration (3 endpoints) - CR-004

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|-----------|
| `/api/ideas/kb-references` | GET | Read KB references from folder | `folder_path` |
| `/api/ideas/kb-references` | POST | Save KB references to folder | `folder_path`, `kb_references[]` |
| `/api/ideas/kb-references` | DELETE | Delete KB references file | `folder_path` |

**Persistence:** Stored in `.knowledge-reference.yaml` inside each idea folder

### 1.8 Skills API (1 endpoint)

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|-----------|
| `/api/skills` | GET | Get all skills with descriptions | None |

**Source:** Reads from `.github/skills/*/SKILL.md` (YAML frontmatter format)

---

## 2. TEMPLATES & UI

### 2.1 Main Template Files

**File:** `/src/x_ipe/templates/workplace.html`
- Main ideation UI container
- Features: Sidebar tree view, content area, terminal panel
- Contains "Create Idea" button (top bar)
- Stage Toolbox modal (FEATURE-011)

**Key UI Elements:**
```html
<!-- Top Bar -->
<button class="btn btn-sm btn-primary" id="btn-create-idea" title="Create new idea">
    <i class="bi bi-plus-lg"></i> Create Idea
</button>

<!-- Stage Toolbox -->
<button class="btn btn-sm btn-outline-secondary" id="btn-stage-toolbox" title="Stage Toolbox">
    <i class="bi bi-tools"></i>
</button>
```

### 2.2 CSS Styling

**File:** `/src/x_ipe/static/css/features/compose-idea-modal.css`
- Modal styling and animations
- Dragover effects, upload zone styling
- KB reference popup styling

---

## 3. JAVASCRIPT FRONTEND

### 3.1 Compose Idea Modal - FEATURE-037-A/B

**File:** `/src/x_ipe/static/js/features/compose-idea-modal.js` (~700 lines)

#### Three Main Classes:

**1. IdeaNameValidator**
```javascript
class IdeaNameValidator {
    validate(text)           // Returns {valid, wordCount, sanitized}
    sanitize(text)           // Converts to lowercase, replaces spaces with hyphens
    getWordCount(text)       // Returns word count (max 10 words)
    bindLiveValidation()     // Real-time validation feedback
}
```

**Input Requirements:**
- 1-10 words max
- Auto-sanitized: spaces → hyphens, special chars removed
- Example: "Feature File Link Preview" → `wf-001-feature-file-link-preview`

---

**2. AutoFolderNamer**
```javascript
class AutoFolderNamer {
    async generate(sanitizedName)    // Returns wf-NNN-{name}
    async fetchTree()                 // Fetches /api/ideas/tree
    findHighestWfNumber(tree)         // Finds max wf-NNN and increments
}
```

**Naming Pattern:** `wf-NNN-sanitized-name` where NNN = zero-padded sequence number

---

**3. ComposeIdeaModal**
```javascript
class ComposeIdeaModal {
    constructor({workflowName, onComplete, mode, filePath, folderPath})
    
    // Lifecycle
    open()                   // Create DOM, bind events, show modal
    close()                  // Cleanup, hide modal
    
    // Modes
    switchMode(mode)         // "create" vs "link" (link mode TBD)
    switchTab(tab)           // "compose" vs "upload" tab
    
    // Content
    addFiles(fileList)       // Add files to pending list
    removeFile(index)        // Remove file from pending
    renderFileList()         // Display file list
    
    // Submission
    handleSubmit()           // Main submit handler
    handleUpdate()           // Edit mode - update existing
}
```

#### User Workflow (Create Mode):

1. **User clicks "Create Idea" button**
   - Modal opens, "Compose" tab active
   - Name input ready for input

2. **User enters idea name**
   - Real-time validation: `IdeaNameValidator.validate(text)`
   - Word counter displays: "3 / 10 words"
   - Folder preview shows: `Folder: x-ipe-docs/ideas/wf-001-feature-name`

3. **User adds content** (2 options):
   - **Compose Tab:** Write in Markdown editor (EasyMDE)
   - **Upload Tab:** Drag-drop files (md, docx, pdf, png, jpg, py, js)

4. **User adds KB References (optional)**
   - Click "📚 KB Reference" button
   - `KBReferencePicker` opens
   - Select knowledge base documents
   - Display count badge

5. **User submits**
   - Auto-generates folder name: `wf-NNN-sanitized-name`
   - Calls `POST /api/ideas/upload` with FormData:
     - `target_folder`: wf-001-feature-name
     - `files`: Content blob + uploaded files
     - `kb_references`: JSON array of KB paths
   
   - **Response includes:** folder_path, files_uploaded[]
   
   - **Auto-completes compose_idea action:**
     ```javascript
     POST /api/workflow/{workflowName}/action
     {
         action: 'compose_idea',
         status: 'done',
         deliverables: {
             'raw-ideas': [file1, file2],
             'ideas-folder': 'x-ipe-docs/ideas/wf-001-...',
             'kb-references': '.../.knowledge-reference.yaml'
         }
     }
     ```

6. **Modal closes**, workflow auto-progresses to refine_idea action

#### Edit Mode (FEATURE-037-B):

- Opens with folder name pre-filled and read-only
- User can update file content or add more files
- Calls `POST /api/ideas/upload` to target existing folder

#### Link Existing Mode (FEATURE-037-B, partially implemented):

- Currently shows placeholder ("Available in next update")
- Will allow linking existing idea folders to workflow

---

## 4. DATA MODELS & STORAGE

### 4.1 Directory Structure

```
project_root/
├── x-ipe-docs/
│   ├── ideas/                              # Root ideas directory
│   │   ├── .ideation-tools.json            # Toolbox config
│   │   ├── wf-001-feature-name/            # Workflow-linked idea
│   │   │   ├── new idea.md                 # Content
│   │   │   ├── document.docx               # Uploaded file
│   │   │   ├── .knowledge-reference.yaml   # KB references
│   │   │   └── idea-summary-v1.md          # Versioned summary
│   │   ├── Draft Idea - 03142026 151855/   # Timestamped idea
│   │   │   ├── file1.md
│   │   │   └── file2.pdf
│   │   └── Sample/                          # User-created folder
│   │       ├── research.md
│   │       └── notes.txt
│   └── config/
│       ├── workflow-template.json
│       └── cli-adapters.yaml
└── .github/
    └── skills/
        ├── skill-1/SKILL.md
        └── skill-2/SKILL.md
```

### 4.2 Tree Node Format (JSON)

```json
{
    "name": "wf-001-feature-name",
    "type": "folder",
    "path": "x-ipe-docs/ideas/wf-001-feature-name",
    "children": [
        {
            "name": "new idea.md",
            "type": "file",
            "path": "x-ipe-docs/ideas/wf-001-feature-name/new idea.md"
        },
        {
            "name": ".knowledge-reference.yaml",
            "type": "file",
            "path": "x-ipe-docs/ideas/wf-001-feature-name/.knowledge-reference.yaml"
        }
    ]
}
```

### 4.3 Configuration Files

**`.ideation-tools.json`** (Toolbox configuration):
```json
{
    "version": "1.0",
    "ideation": {
        "x-ipe-tool-infographic-syntax": false,
        "mermaid": true
    },
    "mockup": {
        "frontend-design": true
    },
    "sharing": {}
}
```

**`.knowledge-reference.yaml`** (KB References):
```yaml
knowledge-reference:
  - "path/to/kb/document1.md"
  - "path/to/kb/document2.md"
```

**`SKILL.md`** (Skill Definition Format):
```yaml
---
name: "Skill Name"
description: "Short description"
---
Markdown content...
```

---

## 5. WORKFLOW INTEGRATION

### 5.1 Ideation Stage Definition

**From `workflow-template.json`:**

```json
{
  "ideation": {
    "type": "shared",
    "next_stage": "requirement",
    "actions": {
      "compose_idea": {
        "optional": false,
        "deliverables": [
          "$output:raw-ideas",
          "$output-folder:ideas-folder"
        ],
        "next_actions_suggested": [
          "refine_idea",
          "reference_uiux"
        ]
      },
      "refine_idea": {
        "optional": false,
        "action_context": {
          "raw-ideas": {
            "required": true,
            "candidates": "ideas-folder"
          }
        },
        "deliverables": [
          "$output:refined-idea",
          "$output-folder:refined-ideas-folder"
        ],
        "next_actions_suggested": [
          "design_mockup",
          "requirement_gathering"
        ]
      },
      "reference_uiux": {
        "optional": true,
        "deliverables": ["$output:uiux-reference"],
        "next_actions_suggested": ["design_mockup", "refine_idea"]
      },
      "design_mockup": {
        "optional": true,
        "action_context": {
          "refined-idea": {"required": true, "candidates": "refined-ideas-folder"},
          "uiux-reference": {"required": false}
        },
        "deliverables": ["$output:mockup-html", "$output-folder:mockups-folder"],
        "next_actions_suggested": ["requirement_gathering"]
      }
    }
  }
}
```

### 5.2 Mandatory vs Optional Actions

| Action | Required | Deliverables |
|--------|----------|--------------|
| `compose_idea` | **YES** | raw-ideas, ideas-folder |
| `refine_idea` | **YES** | refined-idea, refined-ideas-folder |
| `reference_uiux` | Optional | uiux-reference |
| `design_mockup` | Optional | mockup-html, mockups-folder |

### 5.3 Workflow Linking (EPIC-036)

**Endpoint:** `POST /api/workflow/{name}/link-idea`

**Request:**
```json
{
    "idea_folder_path": "x-ipe-docs/ideas/wf-001-feature-name"
}
```

**Backend Processing:**
```python
def link_idea_folder(self, workflow_name: str, idea_folder_path: str):
    state = self._read_state(workflow_name)
    state["idea_folder"] = idea_folder_path
    state["last_activity"] = _now_iso()
    self._write_state(workflow_name, state)
    return {"success": True, "data": {"idea_folder": idea_folder_path}}
```

### 5.4 Action Status Updates

**Endpoint:** `POST /api/workflow/{name}/action`

**When compose_idea completes:**
```json
{
    "action": "compose_idea",
    "status": "done",
    "deliverables": {
        "raw-ideas": "x-ipe-docs/ideas/wf-001-feature-name/new idea.md",
        "ideas-folder": "x-ipe-docs/ideas/wf-001-feature-name",
        "kb-references": "x-ipe-docs/ideas/wf-001-feature-name/.knowledge-reference.yaml"
    }
}
```

**When refine_idea completes:**
```json
{
    "action": "refine_idea",
    "status": "done",
    "deliverables": {
        "refined-idea": "x-ipe-docs/ideas/wf-001-feature-name/idea-summary-v1.md",
        "refined-ideas-folder": "x-ipe-docs/ideas/wf-001-feature-name"
    }
}
```

---

## 6. SERVICE LAYER (IdeasService)

**File:** `/src/x_ipe/services/ideas_service.py` (1101 lines)

### 6.1 Core Service Methods

#### Tree Operations:
```python
def get_tree() -> List[Dict]
    # Recursively scan x-ipe-docs/ideas/ and return tree
    
def filter_tree(query: str) -> List[Dict]
    # Case-insensitive search across tree
```

#### Upload & Creation:
```python
def upload(files: List[tuple], date=None, target_folder=None, 
           kb_references=None) -> Dict
    # Upload to new timestamped folder OR existing target_folder
    # Auto-creates target if needed (FEATURE-037-A)
    # Saves KB references if provided
    
def create_folder(folder_name, parent_folder=None) -> Dict
    # Create empty folder with collision handling
```

#### Rename:
```python
def rename_folder(old_name, new_name) -> Dict
    # Rename top-level idea folder
    
def rename_file(file_path, new_name) -> Dict
    # Rename file within ideas directory
```

#### Delete:
```python
def delete_item(path) -> Dict
    # Delete file or folder recursively
    
def get_delete_info(path) -> Dict
    # Get item info (recursive count for folders)
```

#### Move & Duplicate:
```python
def move_item(source_path, target_folder) -> Dict
    # Move with collision handling
    
def duplicate_item(path) -> Dict
    # Duplicate with -copy suffix
    
def is_valid_drop_target(source_path, target_folder) -> bool
    # Validate drag-drop (prevent moving into self/children)
```

#### Versioning:
```python
def get_next_version_number(folder_path, base_name='idea-summary') -> int
    # Get next version number (searches for idea-summary-vN.md)
    
def create_versioned_summary(folder_path, content, 
                             base_name='idea-summary') -> Dict
    # Create idea-summary-v1.md, v2.md, etc.
```

#### KB References:
```python
def get_kb_references(folder_path) -> Dict
    # Read .knowledge-reference.yaml
    
def save_kb_references(folder_path, kb_references) -> Dict
    # Write .knowledge-reference.yaml
    
def delete_kb_references(folder_path) -> Dict
    # Delete .knowledge-reference.yaml
```

#### Configuration:
```python
def get_toolbox() -> Dict
    # Read .ideation-tools.json (or return defaults)
    
def save_toolbox(config) -> Dict
    # Write .ideation-tools.json
```

### 6.2 Security & Validation

- **Path Traversal Prevention:** All operations validate paths are within `x-ipe-docs/ideas/`
- **Filename Validation:** 
  - Invalid chars: `/\:*?"<>|`
  - Max length: 255 characters
- **File Conversion Sanitization:**
  - Removes: `<script>`, `<iframe>`, `<object>`, event handlers
  - Max file size: 10MB for DOCX/MSG conversion

---

## 7. FEATURE FLOW - User Perspective

### 7.1 Complete Workflow: Create Idea → Refine Idea

```
User initiates workflow
         ↓
[1] Workflow created (e.g., wf-001-feature-name)
         ↓
[2] User clicks "Create Idea" button on workplace
         ↓
[3] ComposeIdeaModal opens
    - Name input (validated: 1-10 words)
    - Compose or Upload tab
    - KB References picker
         ↓
[4] User enters idea name → Auto-generates folder name
    - Example: "Feature File Link Preview" 
    - Generated: wf-001-feature-file-link-preview
         ↓
[5] User creates content (2 options):
    a) Type in Markdown editor (EasyMDE)
    b) Upload files (drag-drop or browse)
         ↓
[6] User adds KB references (optional)
         ↓
[7] User clicks "Submit Idea"
         ↓
[8] POST /api/ideas/upload
    - Creates: x-ipe-docs/ideas/wf-001-feature-file-link-preview/
    - Uploads: new idea.md + any additional files
    - Saves: .knowledge-reference.yaml (if provided)
         ↓
[9] Auto-complete compose_idea action
    POST /api/workflow/{workflow}/action
    - status: "done"
    - deliverables:
        * raw-ideas: file path
        * ideas-folder: folder path
        * kb-references: .yaml file path
         ↓
[10] Modal closes, workflow progresses
    - suggest_next_action: refine_idea
         ↓
[11] User refines idea (TBD - likely similar modal)
    - Edits existing files
    - Adds additional analysis/refinement
         ↓
[12] Auto-complete refine_idea action
    POST /api/workflow/{workflow}/action
    - status: "done"
    - deliverables:
        * refined-idea: summary file
        * refined-ideas-folder: folder path
         ↓
[13] Workflow progresses to next stage (requirement)
```

### 7.2 Alternative: Link Existing Idea

```
User has idea folder already created
         ↓
Click "Create Idea" → Switch to "Link Existing" tab
         ↓
Browse ideas tree → Select folder
         ↓
Click "Confirm Link"
         ↓
POST /api/workflow/{workflow}/action
    - action: compose_idea
    - status: done
    - deliverables: selected folder + primary file
         ↓
Workflow progresses to refine_idea
```

---

## 8. KEY CONFIGURATION FILES

### 8.1 Workflow Template Structure

**File:** `x-ipe-docs/config/workflow-template.json`

Contains:
- **stages:** ideation, requirement, design, implementation, testing, deployment
- **Each stage includes:**
  - Type (shared/exclusive)
  - Mandatory actions
  - Optional actions
  - Action context (dependencies)
  - Deliverables (output specifications)
  - Next action suggestions

### 8.2 Skills Configuration

**Location:** `.github/skills/*/SKILL.md`

**Format:**
```markdown
---
name: "Skill Name"
description: "One-line description"
---

# Content

Markdown formatted skill content...
```

**Loaded by:** `/src/x_ipe/services/skills_service.py`

---

## 9. SPECIAL FEATURES

### 9.1 File Conversion (CR-001)

**Supported Conversions:**
- **DOCX → HTML:** Using `mammoth` library
- **MSG → HTML:** Using `extract_msg` library
- **Size Limit:** 10MB max

**Sanitization Removes:**
- `<script>` tags
- `<iframe>` tags
- `<object>` and `<embed>` tags
- Event handlers (onclick, onload, etc.)

**Endpoint:** `GET /api/ideas/file?path=...`

### 9.2 Lazy Loading

- Tree endpoints return folders with empty `children: []`
- Frontend loads specific folder via `GET /api/ideas/folder-contents?path=...`
- Optimizes performance for large idea trees

### 9.3 Unique Naming

- **Timestamped:** `Draft Idea - 03142026 151855`
- **Workflow-linked:** `wf-NNN-sanitized-name`
- **Collision handling:** Appends (2), (3), etc.
- **Copy suffix:** `original-copy`, `original-copy-2`

### 9.4 Versioned Summaries

- Automatically versioned: `idea-summary-v1.md`, `v2.md`, etc.
- Each version is separate file (immutable history)
- Used for workflow result storage (FEATURE-038-B)

---

## 10. SECURITY FEATURES

### 10.1 Path Traversal Prevention

```python
# Validate all paths are within ideas_root
resolved_path = Path(path).resolve()
ideas_resolved = self.ideas_root.resolve()
assert str(resolved_path).startswith(str(ideas_resolved))
```

### 10.2 Filename Validation

```python
# Invalid characters for filesystem
INVALID_CHARS = r'[/\\:*?"<>|]'

# Reject if contains invalid chars or > 255 chars
if re.search(INVALID_CHARS, name) or len(name) > 255:
    return {"success": False, "error": "Invalid filename"}
```

### 10.3 Content Sanitization

```python
# For converted HTML files
def sanitize_converted_html(html_str):
    soup = BeautifulSoup(html_str, 'html.parser')
    # Remove dangerous tags
    for tag in soup.find_all(['script', 'iframe', 'object', 'embed']):
        tag.decompose()
    # Remove event handlers
    for tag in soup.find_all(True):
        for attr in list(tag.attrs.keys()):
            if attr.startswith('on'):
                del tag.attrs[attr]
    return str(soup)
```

---

## 11. FILES & LOCATIONS

### Backend Implementation:
- **Routes:** `/src/x_ipe/routes/ideas_routes.py` (780 lines)
- **Service:** `/src/x_ipe/services/ideas_service.py` (1101 lines)
- **Workflow Routes:** `/src/x_ipe/routes/workflow_routes.py` (200+ lines)
- **Workflow Service:** `/src/x_ipe/services/workflow_manager_service.py`
- **Conversion Utils:** `/src/x_ipe/services/conversion_utils.py`

### Frontend Implementation:
- **Modal JS:** `/src/x_ipe/static/js/features/compose-idea-modal.js` (~700 lines)
- **Modal CSS:** `/src/x_ipe/static/css/features/compose-idea-modal.css`
- **Templates:** `/src/x_ipe/templates/workplace.html`

### Configuration:
- **Workflow Template:** `x-ipe-docs/config/workflow-template.json`
- **Skills:** `.github/skills/*/SKILL.md`
- **Toolbox Config:** `x-ipe-docs/ideas/.ideation-tools.json`
- **KB References:** `x-ipe-docs/ideas/{folder}/.knowledge-reference.yaml`

### Testing:
- **Ideas Tests:** `/tests/test_ideas.py`
- **Modal Tests:** `/tests/test_compose_idea_modal.py`
- **Feature 037-B Tests:** `/tests/test_feature_037b.py`

---

## 12. FEATURE MATRIX

| Feature ID | Title | Implementation | Status |
|-----------|-------|-----------------|--------|
| FEATURE-008 | Workplace (Idea Management) | Ideas API + UI | ✅ Complete |
| CR-001 | File Format Conversion | DOCX/MSG → HTML | ✅ Complete |
| CR-002 | Target Folder Upload | Upload to existing folder | ✅ Complete |
| CR-004 | KB References Integration | .knowledge-reference.yaml | ✅ Complete |
| CR-006 | Folder Tree UX | Drag-drop, move, duplicate | ✅ Complete |
| FEATURE-037-A | Compose Modal - Create | Modal + EasyMDE | ✅ Complete |
| FEATURE-037-B | Compose Modal - Edit/Link | Edit mode + Link mode (partial) | 🟡 Partial |
| EPIC-036 | Workflow Integration | Link workflow to ideas | ✅ Complete |
| FEATURE-049-A | KB Service Integration | Link ideas to KB | ✅ Complete |

---

## 13. SUMMARY & KEY TAKEAWAYS

1. **No Database:** Fully file-system based, git-friendly
2. **21 Endpoints:** Comprehensive CRUD + tree operations
3. **Smart Naming:** Auto-generates `wf-NNN-{sanitized-name}` folders
4. **Workflow Integration:** Auto-completes compose_idea action
5. **Lazy Loading:** Optimized for large idea trees
6. **File Conversion:** DOCX/MSG → HTML with sanitization
7. **KB References:** Link ideas to knowledge base
8. **Versioning:** Immutable versioned summaries
9. **Security:** Path traversal prevention, filename validation, content sanitization
10. **User Flow:** Create → Compose → Refine → Progress workflow

