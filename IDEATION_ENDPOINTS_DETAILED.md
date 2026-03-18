# X-IPE Ideation API - Complete Endpoint Reference

## All 21 API Endpoints with Full Details

### GROUP 1: TREE & BROWSE OPERATIONS (5 endpoints)

#### 1. GET /api/ideas/tree
**Purpose:** Get complete tree structure of ideas directory
**Parameters:** None
**Query Params:** None
**Request Body:** None
**Response:**
```json
{
    "success": true,
    "tree": [
        {
            "name": "Draft Idea - 01012024 120000",
            "type": "folder",
            "path": "x-ipe-docs/ideas/Draft Idea - 01012024 120000",
            "children": [
                {
                    "name": "document.md",
                    "type": "file",
                    "path": "x-ipe-docs/ideas/Draft Idea - 01012024 120000/document.md"
                }
            ]
        }
    ]
}
```
**Status Codes:** 200, 500
**Feature:** FEATURE-008
**Security:** N/A (read-only)

---

#### 2. GET /api/ideas/folder-contents
**Purpose:** Get contents of specific folder (lazy loading support)
**Parameters:** 
- `path` (optional, query param): Folder path relative to project root or ideas root
**Response:**
```json
{
    "success": true,
    "items": [
        {"name": "file.md", "type": "file", "path": "x-ipe-docs/ideas/MyFolder/file.md"},
        {"name": "subfolder", "type": "folder", "path": "x-ipe-docs/ideas/MyFolder/subfolder", "children": []}
    ],
    "folder_path": "x-ipe-docs/ideas/MyFolder"
}
```
**Status Codes:** 200, 400
**Feature:** FEATURE-008 + CR-006
**Special:** Lazy loads folders (children: [])

---

#### 3. GET /api/ideas/search
**Purpose:** Search/filter ideas tree by query
**Parameters:**
- `q` (query param): Search query string
**Response:**
```json
{
    "success": true,
    "tree": [
        {
            "name": "MyIdea",
            "type": "folder",
            "path": "x-ipe-docs/ideas/MyIdea",
            "_matches": true
        },
        {
            "name": "important-file.md",
            "type": "file",
            "path": "x-ipe-docs/ideas/MyIdea/important-file.md",
            "_matches": true
        }
    ]
}
```
**Status Codes:** 200, 500
**Feature:** FEATURE-008 + CR-006
**Algorithm:** Case-insensitive substring matching

---

#### 4. GET /api/ideas/delete-info
**Purpose:** Get item info for delete confirmation dialog
**Parameters:**
- `path` (query param, required): Path of item to delete
**Response:**
```json
{
    "success": true,
    "path": "x-ipe-docs/ideas/MyFolder",
    "name": "MyFolder",
    "type": "folder",
    "item_count": 5
}
```
**Status Codes:** 200, 400
**Feature:** FEATURE-008
**Special:** item_count = recursive count for folders

---

#### 5. GET /api/ideas/file
**Purpose:** Serve file content with automatic format conversion
**Parameters:**
- `path` (query param, required): Relative path from project root
**Response Types:**
- Text files: Plain text with Content-Type: text/plain
- Binary (images, PDFs): Native binary with correct MIME type
- DOCX: HTML via mammoth + sanitization
- MSG: HTML via extract_msg + table layout + sanitization
**Status Codes:** 200, 400, 403, 404, 413, 415
**Feature:** FEATURE-008 + CR-001 (File Conversion)
**Special Requirements:**
- DOCX/MSG max 10MB
- BeautifulSoup sanitization removes: scripts, iframes, object, embed, event handlers
- Path security: must be within project root

---

### GROUP 2: CREATE OPERATIONS (2 endpoints)

#### 6. POST /api/ideas/upload
**Purpose:** Upload files to new timestamped folder or existing target folder (CR-002)
**Content-Type:** multipart/form-data
**Parameters:**
- `files` (form field, required): Multiple files to upload
- `target_folder` (form field, optional): Existing folder path to upload into
- `kb_references` (form field, optional, JSON): Knowledge base references for KB integration (CR-004)
**Request Example:**
```
POST /api/ideas/upload
Content-Type: multipart/form-data

files: [file1.md, file2.docx]
target_folder: "x-ipe-docs/ideas/MyExistingFolder"
kb_references: ["path/to/kb/doc1", "path/to/kb/doc2"]
```
**Response:**
```json
{
    "success": true,
    "folder_name": "Draft Idea - 01012024 120000",
    "folder_path": "x-ipe-docs/ideas/Draft Idea - 01012024 120000",
    "files_uploaded": ["file1.md", "file2.docx"]
}
```
**Status Codes:** 200, 400
**Feature:** FEATURE-008 + CR-002 (Target Folder) + CR-004 (KB Refs)
**Side Effects:**
- Creates x-ipe-docs/ideas/ if missing
- Creates target_folder if missing (FEATURE-037-A)
- Writes .knowledge-reference.yaml if kb_references provided

---

#### 7. POST /api/ideas/create-folder
**Purpose:** Create empty folder with unique name collision handling
**Content-Type:** application/json
**Parameters:**
```json
{
    "folder_name": "My New Idea",
    "parent_folder": "x-ipe-docs/ideas/ParentFolder" (optional)
}
```
**Response:**
```json
{
    "success": true,
    "folder_name": "My New Idea",
    "folder_path": "x-ipe-docs/ideas/My New Idea"
}
```
**Status Codes:** 200, 400
**Feature:** FEATURE-008 + CR-006
**Collision Handling:** "My New Idea (2)", "My New Idea (3)", etc.

---

### GROUP 3: RENAME OPERATIONS (2 endpoints)

#### 8. POST /api/ideas/rename
**Purpose:** Rename top-level idea folder
**Content-Type:** application/json
**Parameters:**
```json
{
    "old_name": "Draft Idea - 01012024 120000",
    "new_name": "My Amazing Product Idea"
}
```
**Response:**
```json
{
    "success": true,
    "old_name": "Draft Idea - 01012024 120000",
    "new_name": "My Amazing Product Idea",
    "new_path": "x-ipe-docs/ideas/My Amazing Product Idea"
}
```
**Status Codes:** 200, 400
**Feature:** FEATURE-008
**Validation:** No invalid chars (/\:*?"<>|), max 255 chars

---

#### 9. POST /api/ideas/rename-file
**Purpose:** Rename file within ideas directory
**Content-Type:** application/json
**Parameters:**
```json
{
    "path": "x-ipe-docs/ideas/MyFolder/old_name.md",
    "new_name": "new_name.md"
}
```
**Response:**
```json
{
    "success": true,
    "old_path": "x-ipe-docs/ideas/MyFolder/old_name.md",
    "new_path": "x-ipe-docs/ideas/MyFolder/new_name.md",
    "new_name": "new_name.md"
}
```
**Status Codes:** 200, 400
**Feature:** FEATURE-008
**Security:** Path must be within ideas_root (resolved check)
**Validation:** 255 char limit, no invalid chars

---

### GROUP 4: DELETE OPERATIONS (1 endpoint)

#### 10. POST /api/ideas/delete
**Purpose:** Delete file or folder (recursive deletion for folders)
**Content-Type:** application/json
**Parameters:**
```json
{
    "path": "x-ipe-docs/ideas/MyFolder"
}
```
**Response:**
```json
{
    "success": true,
    "path": "x-ipe-docs/ideas/MyFolder",
    "type": "folder"
}
```
**Status Codes:** 200, 400
**Feature:** FEATURE-008
**Security:** Path must be within ideas_root (resolved check)
**Behavior:** Uses shutil.rmtree() for folders, unlink() for files

---

### GROUP 5: MOVE & TRANSFORM OPERATIONS (4 endpoints)

#### 11. POST /api/ideas/move
**Purpose:** Move file or folder to new location with collision handling
**Content-Type:** application/json
**Parameters:**
```json
{
    "source_path": "x-ipe-docs/ideas/SourceFolder/item",
    "target_folder": "x-ipe-docs/ideas/DestinationFolder"
}
```
**Response:**
```json
{
    "success": true,
    "new_path": "item"
}
```
**Status Codes:** 200, 400
**Feature:** FEATURE-008 + CR-006
**Validation:** Cannot move folder into itself or children
**Collision Handling:** Appends -2, -3, etc. if destination exists

---

#### 12. POST /api/ideas/duplicate
**Purpose:** Duplicate file or folder with -copy suffix
**Content-Type:** application/json
**Parameters:**
```json
{
    "path": "x-ipe-docs/ideas/MyFolder/file.md"
}
```
**Response:**
```json
{
    "success": true,
    "new_path": "file-copy.md"
}
```
**Status Codes:** 200, 400
**Feature:** FEATURE-008 + CR-006
**Naming:**
- Files: `filename-copy.ext`, then `filename-copy-2.ext`, etc.
- Folders: `foldername-copy/`, then `foldername-copy-2/`, etc.
**Operation:** Uses shutil.copy2() for files, shutil.copytree() for folders

---

#### 13. POST /api/ideas/validate-drop
**Purpose:** Validate drag-drop target for tree operations
**Content-Type:** application/json
**Parameters:**
```json
{
    "source_path": "MyFolder",
    "target_folder": "MyFolder/SubFolder"
}
```
**Response:**
```json
{
    "valid": false
}
```
**Status Codes:** 200, 400
**Feature:** FEATURE-008 + CR-006
**Logic:** Prevents dropping folder into itself or its children

---

#### 14. GET /api/ideas/download
**Purpose:** Download file with correct MIME type
**Parameters:**
- `path` (query param, required): Relative path
**Response:** Binary file with Content-Type and Content-Disposition headers
**MIME Types Handled:**
- .md → text/markdown
- .txt → text/plain
- .json → application/json
- .html → text/html
- .pdf → application/pdf
- .png → image/png
- .jpg/.jpeg → image/jpeg
- .gif → image/gif
- default → application/octet-stream
**Status Codes:** 200, 400, 404
**Feature:** FEATURE-008 + CR-006

---

### GROUP 6: CONFIGURATION OPERATIONS (2 endpoints)

#### 15. GET /api/ideas/toolbox
**Purpose:** Get ideation toolbox configuration
**Parameters:** None
**Response:**
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
**Status Codes:** 200
**Feature:** FEATURE-008 + FEATURE-011
**File:** .ideation-tools.json
**Fallback:** Returns DEFAULT_TOOLBOX if file missing/invalid

---

#### 16. POST /api/ideas/toolbox
**Purpose:** Save ideation toolbox configuration
**Content-Type:** application/json
**Parameters:**
```json
{
    "version": "1.0",
    "ideation": {
        "x-ipe-tool-infographic-syntax": true,
        "mermaid": true
    },
    "mockup": {
        "frontend-design": false
    },
    "sharing": {}
}
```
**Response:**
```json
{
    "success": true
}
```
**Status Codes:** 200, 400
**Feature:** FEATURE-008 + FEATURE-011
**File:** Writes to .ideation-tools.json (JSON format with indent=2)

---

### GROUP 7: KNOWLEDGE BASE INTEGRATION (3 endpoints - CR-004)

#### 17. GET /api/ideas/kb-references
**Purpose:** Read knowledge base references from idea folder
**Parameters:**
- `folder_path` (query param, required): Idea folder path
**Response:**
```json
{
    "success": true,
    "kb_references": [
        "path/to/kb/document1.md",
        "path/to/kb/document2.md"
    ]
}
```
**Status Codes:** 200, 400
**Feature:** FEATURE-008 + CR-004 + FEATURE-049-A (KB Service)
**File:** .knowledge-reference.yaml
**Default:** Returns empty array if file missing

---

#### 18. POST /api/ideas/kb-references
**Purpose:** Write knowledge base references with immediate persistence
**Content-Type:** application/json
**Parameters:**
```json
{
    "folder_path": "x-ipe-docs/ideas/MyIdea",
    "kb_references": [
        "path/to/kb/doc1.md",
        "path/to/kb/doc2.md"
    ]
}
```
**Response:**
```json
{
    "success": true,
    "path": "/full/path/to/.knowledge-reference.yaml"
}
```
**Status Codes:** 200, 400
**Feature:** FEATURE-008 + CR-004
**File:** Writes YAML format (safe_dump, no flow style)
**Side Effect:** Creates folder if missing

---

#### 19. DELETE /api/ideas/kb-references
**Purpose:** Remove knowledge base references file
**Content-Type:** application/json
**Parameters:**
```json
{
    "folder_path": "x-ipe-docs/ideas/MyIdea"
}
```
**Response:**
```json
{
    "success": true,
    "deleted": true
}
```
**Status Codes:** 200, 400
**Feature:** FEATURE-008 + CR-004
**Behavior:** Returns success even if file doesn't exist

---

### GROUP 8: SKILLS API (1 endpoint)

#### 20. GET /api/skills
**Purpose:** Get all skills defined in .github/skills/
**Parameters:** None
**Response:**
```json
{
    "success": true,
    "skills": [
        {
            "name": "FastAPI Development",
            "description": "Build high-performance APIs with FastAPI"
        },
        {
            "name": "React Frontend",
            "description": "Modern React with hooks and TypeScript"
        }
    ]
}
```
**Status Codes:** 200, 500
**Feature:** FEATURE-008 (Workplace, Skills list)
**Service:** SkillsService
**Source:** .github/skills/ directory
**Parsing:** YAML frontmatter from SKILL.md files

---

### GROUP 9: WORKFLOW INTEGRATION ENDPOINTS

#### 21. POST /api/workflow/<name>/link-idea
**Purpose:** Link idea folder to workflow (separate blueprint)
**Content-Type:** application/json
**Parameters:**
```json
{
    "idea_folder_path": "x-ipe-docs/ideas/MyIdea"
}
```
**Status Codes:** 200, 400, 404
**Feature:** EPIC-036 (Workflow Manager) + FEATURE-008
**Blueprint:** workflow_bp (workflow_routes.py)
**Related:** compose_idea, refine_idea actions map to ideas category

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Endpoints | 21 |
| GET Endpoints | 8 |
| POST Endpoints | 12 |
| DELETE Endpoints | 1 |
| PATCH Endpoints | 0 |
| HTTP Status Codes | 200, 201, 400, 403, 404, 409, 413, 415, 500 |
| Content Types | application/json, multipart/form-data, text/plain, text/html, binary/* |
| Feature Coverage | FEATURE-008, CR-001, CR-002, CR-004, CR-006, EPIC-036 |

---

## Request/Response Patterns

### Success Pattern
```json
{
    "success": true,
    "data": {...}
}
```

### Error Pattern
```json
{
    "success": false,
    "error": "Error code or message"
}
```

### Multipart Upload Pattern
```
POST /api/ideas/upload
Content-Type: multipart/form-data

----boundary
Content-Disposition: form-data; name="files"; filename="file.md"
[file content bytes]
----boundary
Content-Disposition: form-data; name="target_folder"
x-ipe-docs/ideas/MyFolder
----boundary--
```

---

## Path Normalization Logic

All endpoints accept paths in multiple formats:
1. **Full path:** `x-ipe-docs/ideas/MyFolder/file.md`
2. **Ideas root relative:** `MyFolder/file.md`
3. **Combination:** Service auto-normalizes by:
   - Stripping `x-ipe-docs/ideas/` prefix if present
   - Resolving to absolute path
   - Validating within ideas_root

