# X-IPE Ideation API Routes & Data Model - Complete Analysis

## Overview
X-IPE implements a **file-system-based idea management system** (FEATURE-008: Workplace) rather than a traditional database. All ideas are stored in `x-ipe-docs/ideas/` directory. The ideation system integrates with the workflow manager and supports knowledge base references.

---

## 1. IDEATION API ROUTES

### **File: `/src/x_ipe/routes/ideas_routes.py` (780 lines)**

#### **1.1 Tree & Browse Operations**

| Endpoint | Method | Parameters | Returns | Purpose |
|----------|--------|-----------|---------|---------|
| `/api/ideas/tree` | GET | None | `{success, tree[]}` | Get complete tree structure of ideas directory (folders & files) |
| `/api/ideas/folder-contents` | GET | `path` (optional) | `{success, items[], folder_path}` | Get contents of specific folder (lazy load support) |
| `/api/ideas/search` | GET | `q` (search query) | `{success, tree[]}` | Filter/search ideas tree by query string |
| `/api/ideas/delete-info` | GET | `path` (required) | `{success, name, type, item_count}` | Get item info for delete confirmation dialog |
| `/api/ideas/file` | GET | `path` (required) | File content (text/binary/HTML) | Serve file content with auto-conversion (DOCX→HTML, MSG→HTML) |

#### **1.2 Upload & Creation**

| Endpoint | Method | Parameters | Returns | Purpose |
|----------|--------|-----------|---------|---------|
| `/api/ideas/upload` | POST | `files` (multipart), `target_folder` (opt), `kb_references` (opt) | `{success, folder_name, folder_path, files_uploaded[]}` | Upload files to new or existing idea folder (CR-002, CR-004) |
| `/api/ideas/create-folder` | POST | `folder_name`, `parent_folder` (opt) | `{success, folder_name, folder_path}` | Create empty folder in ideas directory |

#### **1.3 Rename & Edit**

| Endpoint | Method | Parameters | Returns | Purpose |
|----------|--------|-----------|---------|---------|
| `/api/ideas/rename` | POST | `old_name`, `new_name` | `{success, old_name, new_name, new_path}` | Rename top-level idea folder |
| `/api/ideas/rename-file` | POST | `path`, `new_name` | `{success, old_path, new_path, new_name}` | Rename file within ideas directory |

#### **1.4 Delete Operations**

| Endpoint | Method | Parameters | Returns | Purpose |
|----------|--------|-----------|---------|---------|
| `/api/ideas/delete` | POST | `path` (required) | `{success, path, type}` | Delete file or folder (recursive for folders) |

#### **1.5 Drag-Drop & Tree UX (CR-006)**

| Endpoint | Method | Parameters | Returns | Purpose |
|----------|--------|-----------|---------|---------|
| `/api/ideas/move` | POST | `source_path`, `target_folder` | `{success, new_path}` | Move file or folder to new location |
| `/api/ideas/duplicate` | POST | `path` | `{success, new_path}` | Duplicate file/folder with `-copy` suffix |
| `/api/ideas/validate-drop` | POST | `source_path`, `target_folder` | `{valid: bool}` | Validate drag-drop target (prevents moving to self/children) |
| `/api/ideas/download` | GET | `path` | Binary file download | Download file with correct MIME type |

#### **1.6 Toolbox Configuration**

| Endpoint | Method | Parameters | Returns | Purpose |
|----------|--------|-----------|---------|---------|
| `/api/ideas/toolbox` | GET | None | Toolbox config JSON | Get ideation toolbox settings (mermaid, infographic-syntax, mockups) |
| `/api/ideas/toolbox` | POST | Toolbox config object | `{success}` | Save toolbox configuration to `.ideation-tools.json` |

#### **1.7 Knowledge Base References (CR-004)**

| Endpoint | Method | Parameters | Returns | Purpose |
|----------|--------|-----------|---------|---------|
| `/api/ideas/kb-references` | GET | `folder_path` | `{success, kb_references[]}` | Read `.knowledge-reference.yaml` from idea folder |
| `/api/ideas/kb-references` | POST | `folder_path`, `kb_references[]` | `{success, path}` | Write `.knowledge-reference.yaml` with immediate persistence |
| `/api/ideas/kb-references` | DELETE | `folder_path` | `{success, deleted: bool}` | Remove `.knowledge-reference.yaml` file |

#### **1.8 Skills API**

| Endpoint | Method | Parameters | Returns | Purpose |
|----------|--------|-----------|---------|---------|
| `/api/skills` | GET | None | `{success, skills[]}` | Get all skills from `.github/skills/` (name, description) |

---

## 2. IDEATION SERVICE METHODS

### **File: `/src/x_ipe/services/ideas_service.py` (1101 lines)**

#### **Class: `IdeasService`**

**Initialization:**
```python
def __init__(self, project_root: str)
```
- Stores `project_root` (Path object)
- Sets `ideas_root = project_root / 'x-ipe-docs/ideas'`

**Core Constants:**
- `IDEAS_PATH = 'x-ipe-docs/ideas'`
- `MAX_NAME_LENGTH = 255`
- `INVALID_CHARS = r'[/\\:*?"<>|]'` (filesystem invalid chars)
- `TOOLBOX_FILE = '.ideation-tools.json'`
- `DEFAULT_TOOLBOX = {...}` (stores tool settings)

#### **2.1 Tree Operations**

| Method | Parameters | Returns | Purpose |
|--------|-----------|---------|---------|
| `get_tree()` | None | `List[Dict]` | Scan `x-ipe-docs/ideas/` recursively, return tree structure |
| `_scan_directory(directory: Path)` | directory path | `List[Dict]` | Recursively scan and build tree (skips hidden files) |
| `filter_tree(query: str)` | search query | `List[Dict]` | Filter tree by search query (flat results with parents) |
| `_collect_matches(items[], query, results[], include_all)` | items, query, results | `bool` | Recursively collect matching items and parent context |

#### **2.2 Upload & Creation**

| Method | Parameters | Returns | Purpose |
|--------|-----------|---------|---------|
| `upload(files[], date=None, target_folder=None, kb_references=None)` | files (filename, content) tuples | `{success, folder_name, folder_path, files_uploaded[]}` | Upload files to new timestamped folder or existing target folder (CR-002) |
| `create_folder(folder_name, parent_folder=None)` | folder name, optional parent path | `{success, folder_name, folder_path}` | Create empty folder with unique name collision handling |
| `_generate_unique_name(base_name, base_path=None)` | base name, base path | `str` | Generate unique name by appending (2), (3), etc. |

#### **2.3 Rename Operations**

| Method | Parameters | Returns | Purpose |
|--------|-----------|---------|---------|
| `rename_folder(old_name, new_name)` | old folder name, new folder name | `{success, old_name, new_name, new_path}` | Rename top-level folder with validation |
| `rename_file(file_path, new_name)` | file path, new name | `{success, old_path, new_path, new_name}` | Rename file with security checks (path must be in ideas/) |
| `_validate_folder_name(name)` | folder name | `(bool, error_msg)` | Validate name length and invalid characters |

#### **2.4 Delete Operations**

| Method | Parameters | Returns | Purpose |
|--------|-----------|---------|---------|
| `delete_item(path)` | relative path | `{success, path, type}` | Delete file or folder recursively with security validation |
| `get_delete_info(path)` | relative path | `{success, path, name, type, item_count}` | Get item info (counts recursive items for folders) |

#### **2.5 Move & Duplicate (CR-006)**

| Method | Parameters | Returns | Purpose |
|--------|-----------|---------|---------|
| `move_item(source_path, target_folder)` | source path, target folder | `{success, new_path}` | Move file/folder with collision handling and drop validation |
| `duplicate_item(path)` | source path | `{success, new_path}` | Duplicate with `-copy` or `-copy-N` suffix, handles collisions |
| `is_valid_drop_target(source_path, target_folder)` | source, target | `bool` | Validate target (prevents moving to self/children) |

#### **2.6 Folder Content Operations**

| Method | Parameters | Returns | Purpose |
|--------|-----------|---------|---------|
| `get_folder_contents(folder_path)` | folder path (optional) | `{success, items[], folder_path}` | Get specific folder contents for folder view panel (lazy load) |
| `_resolve_folder_path(folder_path)` | folder path | `Path` | Resolve path (relative to project root or ideas root) to absolute Path |

#### **2.7 File Content Operations**

| Method | Parameters | Returns | Purpose |
|--------|-----------|---------|---------|
| `get_download_info(path)` | relative path | `{success, content, filename, mime_type}` | Get file content for download with MIME type detection |

#### **2.8 Versioned Summary Files**

| Method | Parameters | Returns | Purpose |
|--------|-----------|---------|---------|
| `get_next_version_number(folder_path, base_name='idea-summary')` | folder path, base name | `int` | Get next version number for versioned file (pattern: `idea-summary-v1.md`) |
| `create_versioned_summary(folder_path, content, base_name='idea-summary')` | folder path, content, base name | `{success, file_path, version, filename}` | Create versioned markdown summary file |

#### **2.9 Toolbox Configuration**

| Method | Parameters | Returns | Purpose |
|--------|-----------|---------|---------|
| `get_toolbox()` | None | `Dict` | Read `.ideation-tools.json`, return defaults if missing |
| `save_toolbox(config)` | config dict | `{success}` | Save toolbox config to `.ideation-tools.json` |

#### **2.10 Knowledge Base References (CR-004)**

| Method | Parameters | Returns | Purpose |
|--------|-----------|---------|---------|
| `get_kb_references(folder_path)` | folder path | `{success, kb_references[]}` | Read `.knowledge-reference.yaml` from folder |
| `save_kb_references(folder_path, kb_references)` | folder path, references list | `{success, path}` | Write `.knowledge-reference.yaml` with immediate persistence |
| `delete_kb_references(folder_path)` | folder path | `{success, deleted: bool}` | Delete `.knowledge-reference.yaml` file |
| `_write_kb_references(folder_path, kb_references)` | folder path, references | None | Internal: write YAML file |

#### **2.11 Utility Methods**

| Method | Parameters | Returns | Purpose |
|--------|-----------|---------|---------|
| `_get_unique_path(path: Path)` | path object | `Path` | Generate unique path by appending `-2`, `-3`, etc. |

---

## 3. DATA MODEL & SCHEMAS

### **3.1 Directory Structure**
```
project_root/
├── x-ipe-docs/
│   ├── ideas/                          # Root ideas directory
│   │   ├── .ideation-tools.json        # Toolbox config
│   │   ├── Draft Idea - 01012024 .../ # Timestamped idea folders
│   │   │   ├── file1.md
│   │   │   ├── .knowledge-reference.yaml  # KB references (CR-004)
│   │   └── Custom Folder/              # User-created folders
│   └── config/
├── .github/
│   └── skills/
│       ├── skill1/
│       │   └── SKILL.md               # Skill definition
│       └── skill2/
│           └── SKILL.md
```

### **3.2 File Objects (JSON)**

**Tree Node Structure:**
```python
{
    'name': str,                    # File/folder name
    'type': 'file' | 'folder',     # Item type
    'path': str,                   # Relative path from project root
    'children': List[Node]         # For folders only (recursive)
}
```

**Folder Contents Item:**
```python
{
    'name': str,
    'type': 'file' | 'folder',
    'path': str,                   # Relative to project root
    'children': [] | None          # For folders (lazy load marker)
}
```

### **3.3 Configuration Files**

**`.ideation-tools.json`** (Toolbox Config)
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

**`.knowledge-reference.yaml`** (KB References - CR-004)
```yaml
knowledge-reference:
  - "path/to/kb/file1.md"
  - "path/to/kb/file2.md"
```

**`SKILL.md`** (Skill Definition Format)
```yaml
---
name: "Skill Name"
description: "Skill description"
---
Markdown content...
```

### **3.4 API Response Objects**

**Success Response (Generic):**
```python
{
    'success': True,
    'data': {...}  # Varies by endpoint
}
```

**Error Response:**
```python
{
    'success': False,
    'error': 'error_message' | 'error_code'
}
```

---

## 4. SKILLS SERVICE

### **File: `/src/x_ipe/services/skills_service.py`**

#### **Class: `SkillsService`**

**Initialization:**
```python
def __init__(self, project_root: str)
```

**Methods:**

| Method | Parameters | Returns | Purpose |
|--------|-----------|---------|---------|
| `get_all()` | None | `List[Dict]` | Get all skills from `.github/skills/` with name and description |
| `_parse_skill_md(skill_md_path)` | path to SKILL.md | `Dict \| None` | Parse YAML frontmatter to extract skill metadata |

**Skill Object:**
```python
{
    'name': str,
    'description': str
}
```

---

## 5. WORKFLOW INTEGRATION

### **File: `/src/x_ipe/routes/workflow_routes.py`**

#### **Ideation Workflow Endpoints**

| Endpoint | Method | Purpose | Related Ideas |
|----------|--------|---------|---------------|
| `/api/workflow/<name>/link-idea` | POST | Link idea folder to workflow | `idea_folder_path` parameter |
| `/api/workflow/<name>/action` | POST | Update action status (including compose_idea, refine_idea) | `feature_id`, `deliverables`, `context` |
| `/api/workflow/<name>/deliverables` | GET | Get deliverables (ideas category) | Maps to `x-ipe-docs/ideas/` |

#### **Workflow Manager Mappings**

From `WorkflowManagerService`:
```python
action_to_category = {
    "compose_idea": "ideas",       # Create/compose new idea
    "refine_idea": "ideas",        # Refine existing idea
    # ... other actions
}

deliverable_categories = {
    "compose_idea": "ideas",
    "refine_idea": "ideas",
    # ... other actions
}

# Workflow stages
stages = {
    "ideation": {
        "type": "shared",
        "mandatory_actions": ["compose_idea", "refine_idea"],
        "optional_actions": ["reference_uiux", "design_mockup"],
        "next_stage": "requirement",
    },
    # ... other stages
}
```

---

## 6. FLASK APP SETUP

### **File: `/src/x_ipe/app.py`**

**Blueprint Registration** (line 186-210):
```python
from x_ipe.routes import main_bp, settings_bp, project_bp, ideas_bp, tools_bp, proxy_bp, config_bp
from x_ipe.routes.workflow_routes import workflow_bp
from x_ipe.routes.kb_routes import kb_bp

def _register_blueprints(app):
    app.register_blueprint(ideas_bp)        # Ideation routes
    app.register_blueprint(workflow_bp)     # Workflow routes (with ideas integration)
    # ... other blueprints
```

**Ideas Blueprint** (FEATURE-008):
- Module: `x_ipe.routes.ideas_routes`
- URL prefix: `/api/ideas/` and `/api/skills`
- Features: Workplace (idea management)

---

## 7. SECURITY & VALIDATION

### **Path Traversal Protection**
- All operations resolve paths and validate they're within `x-ipe-docs/ideas/`
- Uses `Path.resolve()` to prevent `..` attacks
- Path prefixes checked: must start with `ideas_resolved`

### **Filename Validation**
- Invalid characters: `[/\\:*?"<>|]`
- Max length: 255 characters
- Empty names rejected

### **File Conversion (CR-001)**
- DOCX → HTML (via mammoth)
- MSG → HTML (via extract_msg)
- Max file size: 10MB
- Sanitization removes scripts, iframes, event handlers

---

## 8. DEPLOYMENT FILES

**Location:** `/src/x_ipe/routes/ideas_routes.py` (exported in `__init__.py`)

```python
ideas_bp = Blueprint('ideas', __name__)
```

---

## 9. KEY DESIGN PATTERNS

### **No Database**
- File-system based (ideas stored in folders)
- Config stored in JSON/YAML files
- Designed for git version control

### **Lazy Loading**
- Folders return empty `children: []` for lazy expansion
- `get_folder_contents()` loads specific folder on demand

### **Immutable Versioning**
- Idea summaries versioned: `idea-summary-v1.md`, `idea-summary-v2.md`, etc.
- Each version is separate file
- Supports FEATURE-038-B (Workflow Result Viewer)

### **Knowledge Base Integration**
- `.knowledge-reference.yaml` links ideas to KB entries
- Immediate persistence (CR-004)
- Supports multi-reference per idea folder

### **Workflow Binding**
- Workflows link to idea folders via `link_idea_folder()`
- Two mandatory actions: `compose_idea`, `refine_idea`
- Ideas category maps to deliverables

---

## 10. TESTING & DEBUGGING

**Test Files:**
- `/tests/test_ideas.py` - Ideas service tests
- `/tests/test_compose_idea_modal.py` - Compose modal tests
- `/tests/test_feature_037b.py` - Feature 037-B tests (file conversion)

**Tracing:**
- All service methods wrapped with `@x_ipe_tracing()` decorator
- Endpoints support DEBUG level tracing for file conversions
- Enables performance monitoring and debugging

---

## 11. COMPLETE ENDPOINT SUMMARY TABLE

| Group | Endpoint | Method | Key Params | Returns |
|-------|----------|--------|-----------|---------|
| **Tree** | `/api/ideas/tree` | GET | - | Tree structure |
| **Tree** | `/api/ideas/folder-contents` | GET | path | Items + folder_path |
| **Tree** | `/api/ideas/search` | GET | q | Filtered tree |
| **Tree** | `/api/ideas/delete-info` | GET | path | Item info |
| **Tree** | `/api/ideas/file` | GET | path | File content |
| **Upload** | `/api/ideas/upload` | POST | files, target_folder, kb_refs | Folder info |
| **Upload** | `/api/ideas/create-folder` | POST | folder_name, parent | Folder info |
| **Edit** | `/api/ideas/rename` | POST | old_name, new_name | Rename result |
| **Edit** | `/api/ideas/rename-file` | POST | path, new_name | Rename result |
| **Delete** | `/api/ideas/delete` | POST | path | Delete result |
| **Move** | `/api/ideas/move` | POST | source, target | New path |
| **Move** | `/api/ideas/duplicate` | POST | path | New path |
| **Move** | `/api/ideas/validate-drop` | POST | source, target | Valid bool |
| **Move** | `/api/ideas/download` | GET | path | Binary file |
| **Config** | `/api/ideas/toolbox` | GET | - | Toolbox JSON |
| **Config** | `/api/ideas/toolbox` | POST | config | Success |
| **KB Refs** | `/api/ideas/kb-references` | GET | folder_path | References list |
| **KB Refs** | `/api/ideas/kb-references` | POST | folder_path, kb_refs | Save result |
| **KB Refs** | `/api/ideas/kb-references` | DELETE | folder_path | Delete result |
| **Skills** | `/api/skills` | GET | - | Skills list |

---

## Summary Statistics

- **Total API Endpoints:** 21
- **Total Service Methods:** 30+
- **HTTP Methods Used:** GET, POST, DELETE, PATCH
- **Configuration Files:** 2 types (.json, .yaml)
- **Integration Points:** Workflow Manager, Knowledge Base, Skills
- **Security Features:** Path traversal prevention, filename validation, file sanitization
- **File Conversion:** DOCX, MSG (with size limits)

