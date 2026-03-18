# X-IPE Ideation Architecture - Visual Diagrams

## 1. User Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INITIATES WORKFLOW                          │
│                  (creates new engineering workflow)                       │
└──────────────────────────────────────┬──────────────────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │  Workflow State Created             │
                    │  workflow-{name}.json               │
                    │  - Stage: ideation (mandatory)      │
                    │  - Actions: compose_idea, refine_id │
                    └──────────────────┬──────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────────────────┐
                    │  USER SEES WORKPLACE / IDEATION PAGE                │
                    │  - Sidebar with ideas tree                          │
                    │  - "Create Idea" button (top bar)                   │
                    │  - Stage Toolbox (optional)                         │
                    └──────────────────┬──────────────────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────────────────┐
                    │  USER CLICKS "CREATE IDEA" BUTTON                   │
                    └──────────────────┬──────────────────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────────┐
        │                              │                                  │
        ▼                              ▼                                  ▼
   ┌─────────────┐              ┌────────────────┐              ┌──────────────┐
   │ CREATE MODE │              │  EDIT MODE     │              │ LINK EXISTING│
   │ (Primary)   │              │ (FEATURE-037-B)│              │   (TBD)      │
   └────┬────────┘              └────┬───────────┘              └──────────────┘
        │                            │
        │                            │
        ▼                            ▼
   ComposeIdeaModal          ComposeIdeaModal
   (Create Form)             (Edit Form)
        │                            │
        ├─ Name Input                ├─ Folder name (read-only)
        │  (1-10 words max)          │
        │                            │
        ├─ Compose OR Upload Tab     ├─ Edit existing files
        │  ├─ Markdown Editor        │
        │  │  (EasyMDE)              │
        │  └─ Drag-drop files        │
        │                            │
        ├─ KB References (optional)  ├─ Add/remove KB refs
        │                            │
        └─ Submit Button             └─ Update Button
                                           │
                                           ▼
                                    Overwrites in place
                                    POST /api/ideas/upload
                                    (target_folder = existing)


        │
        ▼
   User Input Validation
   ├─ Name: 1-10 words
   ├─ Name sanitization: "Feature File Link" → "feature-file-link"
   ├─ Auto folder name: wf-NNN-{sanitized-name}
   │  └─ Fetch /api/ideas/tree to find max wf-NNN
   │  └─ Generate wf-001 or wf-008, etc.
   └─ Content: compose (text) OR upload (files)


        │
        ▼
   ┌─────────────────────────────────────────────┐
   │ USER SUBMITS IDEA                           │
   │ POST /api/ideas/upload                      │
   │ ├─ FormData:                                │
   │ │  ├─ files: [new idea.md, ...uploaded...] │
   │ │  ├─ target_folder: wf-001-feature-name   │
   │ │  └─ kb_references: ["kb/path1", "path2"] │
   └─────────────┬───────────────────────────────┘
                 │
                 ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │ BACKEND PROCESSING (IdeasService.upload)                        │
   │ 1. Create folder: x-ipe-docs/ideas/wf-001-feature-name/        │
   │ 2. Save files directly into folder                              │
   │ 3. Write .knowledge-reference.yaml (if provided)                │
   │ 4. Return: {folder_path, files_uploaded[]}                      │
   └─────────────┬───────────────────────────────────────────────────┘
                 │
                 ▼
   ┌────────────────────────────────────────────┐
   │ FOLDER CREATED IN FILESYSTEM               │
   │ x-ipe-docs/ideas/wf-001-feature-name/      │
   │ ├─ new idea.md (or user-provided content)  │
   │ ├─ uploaded_file1.pdf                      │
   │ ├─ uploaded_file2.docx                     │
   │ └─ .knowledge-reference.yaml               │
   │    └─ knowledge-reference:                 │
   │       - "path/to/kb/doc1"                  │
   │       - "path/to/kb/doc2"                  │
   └─────────────┬────────────────────────────────┘
                 │
                 ▼
   ┌──────────────────────────────────────────────────────────────┐
   │ AUTO-COMPLETE compose_idea ACTION                            │
   │ POST /api/workflow/{workflow-name}/action                    │
   │ {                                                            │
   │   action: "compose_idea",                                    │
   │   status: "done",                                            │
   │   deliverables: {                                            │
   │     "raw-ideas": "x-ipe-docs/ideas/wf-001-feature-name/...", │
   │     "ideas-folder": "x-ipe-docs/ideas/wf-001-feature-name",  │
   │     "kb-references": "x-ipe-docs/ideas/wf-001-feature-.../   │
   │     .knowledge-reference.yaml"                               │
   │   }                                                          │
   │ }                                                            │
   └─────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
   ┌────────────────────────────────────────────────────────┐
   │ WORKFLOW STATE UPDATED                                 │
   │ workflow-{name}.json                                   │
   │ ├─ stage: ideation                                     │
   │ ├─ actions.compose_idea.status = "done"               │
   │ ├─ actions.compose_idea.deliverables = {...}          │
   │ ├─ idea_folder = "x-ipe-docs/ideas/wf-001-..."        │
   │ └─ last_activity = "2025-03-17T15:45:30Z"             │
   └─────────────┬────────────────────────────────────────────┘
                 │
                 ▼
   ┌──────────────────────────────────────────┐
   │ MODAL CLOSES                             │
   │ User sees next action suggestion:        │
   │ "refine_idea" (mandatory in ideation)    │
   │ "reference_uiux" (optional)              │
   │ "design_mockup" (optional)               │
   └──────────────────────────────────────────┘
```

---

## 2. System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            X-IPE IDEATION SYSTEM                             │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ FRONTEND LAYER                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────┐  ┌──────────────────────────┐                 │
│  │  Workplace.html          │  │  Base.html               │                 │
│  │  ├─ Sidebar (tree view)  │  │  ├─ CSS/JS imports       │                 │
│  │  ├─ Create Idea button   │  │  ├─ compose-idea-modal.js│                 │
│  │  ├─ Content area         │  │  └─ compose-idea-modal.css│                 │
│  │  └─ Terminal panel       │  │                          │                 │
│  └──────────────────────────┘  └──────────────────────────┘                 │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │  compose-idea-modal.js (700 lines)                          │           │
│  │  ┌────────────────────────────────────────────────────────┐ │           │
│  │  │ IdeaNameValidator                                      │ │           │
│  │  │ - validate() → {valid, wordCount, sanitized}         │ │           │
│  │  │ - sanitize() → "Feature Name" → "feature-name"       │ │           │
│  │  │ - getWordCount() → checks 1-10 word limit            │ │           │
│  │  │ - bindLiveValidation() → real-time feedback          │ │           │
│  │  └────────────────────────────────────────────────────────┘ │           │
│  │  ┌────────────────────────────────────────────────────────┐ │           │
│  │  │ AutoFolderNamer                                        │ │           │
│  │  │ - generate() → "wf-001-feature-name"                  │ │           │
│  │  │ - fetchTree() → GET /api/ideas/tree                   │ │           │
│  │  │ - findHighestWfNumber() → increments NNN              │ │           │
│  │  └────────────────────────────────────────────────────────┘ │           │
│  │  ┌────────────────────────────────────────────────────────┐ │           │
│  │  │ ComposeIdeaModal                                       │ │           │
│  │  │ ├─ open/close/cleanup                                │ │           │
│  │  │ ├─ switchMode (create/link)                          │ │           │
│  │  │ ├─ switchTab (compose/upload)                        │ │           │
│  │  │ ├─ handleSubmit()                                    │ │           │
│  │  │ ├─ initEasyMDE() (Markdown editor)                   │ │           │
│  │  │ ├─ addFiles/removeFile (upload zone)                 │ │           │
│  │  │ └─ KB References integration                         │ │           │
│  │  └────────────────────────────────────────────────────────┘ │           │
│  └──────────────────────────────────────────────────────────────┘           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    HTTP Requests (JSON / FormData)
                    │
                    ├─ GET /api/ideas/tree
                    ├─ POST /api/ideas/upload (FormData)
                    ├─ POST /api/workflow/{name}/action (JSON)
                    ├─ GET /api/skills
                    └─ ... (21 endpoints total)
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ API LAYER (FLASK BLUEPRINTS)                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────┐  ┌─────────────────────────────┐ │
│  │  ideas_routes.py (780 lines)         │  │  workflow_routes.py         │ │
│  │  ├─ GET /api/ideas/tree              │  │  ├─ POST .../link-idea      │ │
│  │  ├─ POST /api/ideas/upload           │  │  ├─ POST .../action         │ │
│  │  ├─ POST /api/ideas/create-folder    │  │  └─ GET .../deliverables   │ │
│  │  ├─ POST /api/ideas/rename           │  └─────────────────────────────┘ │
│  │  ├─ POST /api/ideas/delete           │                                 │
│  │  ├─ POST /api/ideas/move             │  ┌─────────────────────────────┐ │
│  │  ├─ POST /api/ideas/duplicate        │  │  uiux_reference_routes.py   │ │
│  │  ├─ GET /api/ideas/kb-references     │  │  POST /api/ideas/uiux-ref.. │ │
│  │  ├─ POST /api/ideas/toolbox          │  └─────────────────────────────┘ │
│  │  └─ GET /api/skills                  │                                 │
│  └──────────────────────────────────────┘                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    Delegate to services
                    │
                    ├─ IdeasService (ideas_service.py)
                    ├─ WorkflowManagerService (workflow_manager_service.py)
                    ├─ SkillsService (skills_service.py)
                    ├─ ConversionUtils (conversion_utils.py)
                    └─ KBService
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ SERVICE LAYER                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ IdeasService (1101 lines)                                           │   │
│  ├─ Tree Ops: get_tree(), filter_tree(), _scan_directory()           │   │
│  ├─ Upload: upload(), create_folder(), _generate_unique_name()        │   │
│  ├─ Rename: rename_folder(), rename_file()                            │   │
│  ├─ Delete: delete_item(), get_delete_info()                          │   │
│  ├─ Move: move_item(), duplicate_item(), is_valid_drop_target()       │   │
│  ├─ Versioning: get_next_version_number(), create_versioned_summary() │   │
│  ├─ KB Refs: get_kb_references(), save_kb_references()                │   │
│  ├─ Config: get_toolbox(), save_toolbox()                             │   │
│  └─ Utils: _validate_folder_name(), _resolve_folder_path()           │   │
│  └─ ALL methods decorated with @x_ipe_tracing()                       │   │
│  └─ Security: Path traversal prevention, filename validation          │   │
│  └─ Storage: File-based (no database)                                 │   │
│  └─ Collision handling: (2), (3), -copy, -copy-2                     │   │
│                                                                        │   │
│  ┌──────────────────────────────────────────────────────────┐        │   │
│  │ WorkflowManagerService                                   │        │   │
│  ├─ create_workflow()                                       │        │   │
│  ├─ update_action_status()                                  │        │   │
│  ├─ link_idea_folder()                                      │        │   │
│  └─ resolve_deliverables()                                  │        │   │
│                                                             │        │   │
│  ┌──────────────────────────────────────────────────────────┐        │   │
│  │ ConversionUtils                                          │        │   │
│  ├─ convert_docx() → mammoth → HTML                         │        │   │
│  ├─ convert_msg() → extract_msg → HTML                      │        │   │
│  └─ sanitize_converted_html() → BeautifulSoup remove badtags│        │   │
│                                                             │        │   │
│  ┌──────────────────────────────────────────────────────────┐        │   │
│  │ SkillsService (95 lines)                                 │        │   │
│  ├─ get_all() → reads .github/skills/*/SKILL.md            │        │   │
│  ├─ _parse_skill_md() → YAML frontmatter extraction         │        │   │
│  └─ Returns: {name, description}[]                         │        │   │
│  └─ Storage: File-based YAML frontmatter                    │        │   │
│                                                             │        │   │
│  └─ All use PROJECT_ROOT for path resolution               │        │   │
│  └─ All wrapped with @x_ipe_tracing() for telemetry        │        │   │
│                                                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    Read/Write filesystem
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ FILESYSTEM STORAGE                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  project_root/                                                              │
│  ├─ x-ipe-docs/                                                             │
│  │  ├─ ideas/                                (← IDEAS ROOT)                 │
│  │  │  ├─ .ideation-tools.json              (Toolbox config)               │
│  │  │  │                                                                    │
│  │  │  ├─ wf-001-feature-name/              (Workflow-linked idea)          │
│  │  │  │  ├─ new idea.md                    (Content)                       │
│  │  │  │  ├─ document.docx                  (Uploaded file)                 │
│  │  │  │  ├─ reference.pdf                  (Uploaded file)                 │
│  │  │  │  ├─ .knowledge-reference.yaml      (KB refs)                       │
│  │  │  │  └─ idea-summary-v1.md             (Versioned summary)             │
│  │  │  │                                                                    │
│  │  │  ├─ Draft Idea - 03142026 151855/     (Timestamped idea)              │
│  │  │  │  ├─ file1.md                                                       │
│  │  │  │  └─ file2.pdf                                                      │
│  │  │  │                                                                    │
│  │  │  └─ Sample/                           (User-created folder)           │
│  │  │     ├─ research.md                                                    │
│  │  │     └─ notes.txt                                                      │
│  │  │                                                                        │
│  │  ├─ config/                                                              │
│  │  │  ├─ workflow-template.json            (Workflow stages & actions)     │
│  │  │  ├─ tools.json                        (Tool config)                   │
│  │  │  └─ cli-adapters.yaml                 (CLI adapters)                  │
│  │  │                                                                        │
│  │  └─ engineering-workflow/                                                │
│  │     ├─ workflow-feature-file-link.json   (Workflow state)               │
│  │     ├─ workflow-kb-impl.json                                             │
│  │     └─ ... (more workflows)                                              │
│  │                                                                           │
│  └─ .github/                                                                │
│     └─ skills/                                                              │
│        ├─ skill-1/SKILL.md                  (Skill definition)              │
│        │  ---                                                               │
│        │  name: "Skill Name"                                                │
│        │  description: "..."                                                │
│        │  ---                                                               │
│        │  Markdown content...                                               │
│        │                                                                    │
│        └─ skill-2/SKILL.md                                                  │
│           ...                                                               │
│                                                                              │
│  .x-ipe-checkpoint/ (auto-generated)                                         │
│  └─ screenshots/                                                             │
│     ├─ 01-ideation-list.png                                                 │
│     └─ 02-ideation-page.png                                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow Diagram (Compose Idea)

```
User Actions                    Frontend Processing              Backend Processing

┌──────────────────┐
│ Click            │
│ "Create Idea"    │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────┐
│ ComposeIdeaModal.open()          │
│ - createDOM()                    │
│ - bindEvents()                   │
│ - initEasyMDE()                  │
└────────┬────────────────────────┘
         │
         ├─ Render modal form
         │  ├─ Name input (0 / 10 words)
         │  ├─ Compose tab (EasyMDE)
         │  ├─ Upload tab (drag-drop)
         │  ├─ KB Reference button
         │  └─ Submit button (disabled)
         │
         ▼
┌─────────────────────────────────┐
│ User enters idea name            │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ IdeaNameValidator                │
│ - validate()                     │
│ - getWordCount()                 │
│ - sanitize()                     │
│ Output: {                        │
│   valid: true,                   │
│   wordCount: 3,                  │
│   sanitized: "feature-file-link" │
│ }                                │
└────────┬────────────────────────┘
         │
         ├─ Update UI:
         │  ├─ Word counter: "3 / 10"
         │  ├─ Folder preview: "wf-???-feature-file-link"
         │  └─ Enable submit if has content
         │
         ▼
┌─────────────────────────────────┐
│ User adds content                │
│ (compose OR upload)              │
└────────┬────────────────────────┘
         │
         ├─ Option A: Type in editor
         │  └─ EasyMDE.value() → markdown
         │
         └─ Option B: Upload files
            ├─ Drag-drop or click
            ├─ addFiles()
            └─ pendingFiles[]
                                        
                                        
         ▼
┌─────────────────────────────────┐
│ User adds KB References         │
│ (Optional)                       │
└────────┬────────────────────────┘
         │
         ├─ KBReferencePicker.open()
         ├─ Select KB documents
         └─ kbReferences: string[]
         │
         ▼
┌─────────────────────────────────────────┐
│ User clicks "Submit Idea"               │
└────────┬────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────┐
│ ComposeIdeaModal.handleSubmit()                      │
│                                                      │
│ 1. Validate name: IdeaNameValidator.validate()      │
│    → Returns {valid, wordCount, sanitized}          │
│                                                      │
│ 2. Generate folder name:                            │
│    AutoFolderNamer.generate("feature-file-link")    │
│    - fetch /api/ideas/tree                          │
│    - find max wf-NNN from tree                       │
│    → Returns "wf-001-feature-file-link"             │
│                                                      │
│ 3. Build FormData:                                  │
│    - files: [new idea.md, uploaded_files...]        │
│    - target_folder: "wf-001-feature-file-link"      │
│    - kb_references: ["kb/path1", "kb/path2"]        │
│                                                      │
│ 4. POST /api/ideas/upload                           │
│    └─ Multipart/form-data                           │
└────────┬─────────────────────────────────────────────┘
         │
         │                           ┌──────────────────────────────────────┐
         ├──────────────────────────>│ ideas_routes.py::upload_ideas()      │
         │                           │ - Extract form fields                │
         │                           │ - Validate files                     │
         │                           │ - Call IdeasService.upload()         │
         │                           └───────┬──────────────────────────────┘
         │                                   │
         │                           ┌───────▼──────────────────────────────┐
         │                           │ IdeasService.upload()                │
         │                           │                                      │
         │                           │ 1. Parse target_folder path          │
         │                           │ 2. Create folder if missing          │
         │                           │    x-ipe-docs/ideas/wf-001-.../     │
         │                           │ 3. Save uploaded files               │
         │                           │ 4. Save kb_references.yaml           │
         │                           │ 5. Return {                          │
         │                           │    folder_path,                      │
         │                           │    files_uploaded[]                  │
         │                           │ }                                    │
         │                           └───────┬──────────────────────────────┘
         │                                   │
         │                           ┌───────▼──────────────────────────────┐
         │                           │ FILESYSTEM WRITE                     │
         │                           │ x-ipe-docs/ideas/wf-001-.../        │
         │                           │ ├─ new idea.md                       │
         │                           │ ├─ document.docx                     │
         │                           │ └─ .knowledge-reference.yaml         │
         │                           └───────┬──────────────────────────────┘
         │                                   │
         │<──────────────────────────────────┤
         │ {folder_path, files_uploaded[]}   │
         │                                   
         ▼
┌──────────────────────────────────────────────────────────┐
│ Parse upload response:                                   │
│ - folder_path = "x-ipe-docs/ideas/wf-001-..."           │
│ - files_uploaded = ["new idea.md", "document.docx"]     │
│ - Build deliverables:                                   │
│   * raw-ideas: [file1, file2]                           │
│   * ideas-folder: folder_path                           │
│   * kb-references: folder_path/.knowledge-reference.yaml│
└────────┬─────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Auto-complete compose_idea action:                       │
│ POST /api/workflow/{workflowName}/action                │
│ {                                                        │
│   action: "compose_idea",                                │
│   status: "done",                                        │
│   deliverables: {...}                                    │
│ }                                                        │
└────────┬─────────────────────────────────────────────────┘
         │
         ├────────────────────────────────────────────────>│ workflow_routes.py::update_action()
         │                                                  │
         │                          ┌──────────────────────▼──────────────────┐
         │                          │ WorkflowManagerService.                │
         │                          │ update_action_status()                 │
         │                          │                                        │
         │                          │ 1. Read workflow-{name}.json           │
         │                          │ 2. Update action.compose_idea:         │
         │                          │    - status: "done"                    │
         │                          │    - deliverables: {...}               │
         │                          │ 3. Set workflow.idea_folder            │
         │                          │ 4. Write workflow-{name}.json          │
         │                          │ 5. Return success                      │
         │                          └──────────────────┬───────────────────┘
         │                                            │
         │                          ┌──────────────────▼───────────────────┐
         │                          │ FILESYSTEM WRITE                     │
         │                          │ workflow-{name}.json:                │
         │                          │ {                                    │
         │                          │   "stage": "ideation",               │
         │                          │   "actions": {                       │
         │                          │     "compose_idea": {                │
         │                          │       "status": "done",              │
         │                          │       "deliverables": {...}          │
         │                          │     },                               │
         │                          │     "refine_idea": {                 │
         │                          │       "status": "pending"            │
         │                          │     }                                │
         │                          │   },                                 │
         │                          │   "idea_folder": "x-ipe-docs/...",   │
         │                          │   "last_activity": "2025-03-17T..."  │
         │                          │ }                                    │
         │                          └──────────────────┬───────────────────┘
         │                                            │
         │<─────────────────────────────────────────────┤
         │ {success: true}                              │
         │                                              
         ▼
┌────────────────────────────────┐
│ Modal closes                   │
│ - Cleanup                      │
│ - Call onComplete callback     │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Workflow progresses            │
│ - Suggest next action:         │
│   * refine_idea (mandatory)    │
│   * reference_uiux (optional)  │
│   * design_mockup (optional)   │
└────────────────────────────────┘
```

---

## 4. File Organization Hierarchy

```
Ideas Tree Structure

x-ipe-docs/ideas/
├── Timestamped Ideas (Legacy)
│   ├── Draft Idea - 03142026 151855/
│   │   ├── file1.md
│   │   ├── file2.pdf
│   │   └── .knowledge-reference.yaml (optional)
│   │
│   └── Draft Idea - 01012024 120000/
│       ├── document.md
│       ├── image.png
│       └── reference.pdf
│
├── Workflow-Linked Ideas (New Pattern)
│   ├── wf-001-feature-name/
│   │   ├── new idea.md (generated)
│   │   ├── uploaded_doc.docx (converted to HTML)
│   │   ├── analysis.pdf
│   │   ├── .knowledge-reference.yaml
│   │   │   knowledge-reference:
│   │   │     - "kb/ai-models"
│   │   │     - "kb/design-patterns"
│   │   │
│   │   └── idea-summary-v1.md (versioned)
│   │
│   ├── wf-002-api-integration/
│   │   ├── new idea.md
│   │   ├── api-spec.docx
│   │   ├── diagram.png
│   │   ├── .knowledge-reference.yaml
│   │   └── idea-summary-v1.md
│   │
│   └── wf-008-knowledge-extraction/
│       ├── new idea.md
│       ├── research.pdf
│       ├── .knowledge-reference.yaml
│       └── idea-summary-v1.md
│
├── User-Created Folders (Nested)
│   ├── Sample/
│   │   ├── research.md
│   │   ├── notes.txt
│   │   └── subfolder/
│   │       ├── detail1.md
│   │       └── detail2.md
│   │
│   └── Sample - Replishment system/
│       ├── requirements.md
│       ├── implementation_plan.md
│       └── .knowledge-reference.yaml
│
├── Archived/Research Ideas
│   ├── 001. Feature-Console Voice Input - 01242026 000728/
│   ├── 100. Research-AI-Integrated Enterprise Knowledge Base/
│   ├── 101. Research-X-IPE Module Architecture/
│   └── 200. Playground-Checklist - 01232026 225812/
│
└── Configuration Files
    ├── .ideation-tools.json
    │   {
    │       "version": "1.0",
    │       "ideation": {
    │           "x-ipe-tool-infographic-syntax": false,
    │           "mermaid": true
    │       },
    │       "mockup": {
    │           "frontend-design": true
    │       },
    │       "sharing": {}
    │   }
    │
    └── (Hidden files omitted)

Key Patterns:
1. Workflow-linked: wf-NNN-{sanitized-name}
   - NNN = zero-padded sequence (001, 002, 003...)
   - Automatically generated by AutoFolderNamer
   
2. Timestamped: Draft Idea - MMDDYYYY HHMMSS
   - Legacy pattern, still supported
   
3. User-created: Any custom name
   - Can be nested in subfolders
   - Can have duplicates with (2), (3) suffix
```

---

## 5. API Endpoint Dependency Graph

```
┌──────────────────────────────────────────────────────┐
│ PRIMARY WORKFLOWS                                    │
└──────────────────────────────────────────────────────┘

Workflow 1: Create & Upload Idea
────────────────────────────────
1. GET /api/ideas/tree
   └─ Fetch full tree to find max wf-NNN
   
2. POST /api/ideas/upload
   ├─ Creates folder: x-ipe-docs/ideas/wf-NNN-name/
   ├─ Saves files
   └─ Returns folder_path, files_uploaded[]
   
3. (Auto) POST /api/workflow/{name}/action
   ├─ Updates action.compose_idea
   ├─ Sets idea_folder
   └─ Progresses workflow

4. (Next Action) POST /api/ideas/kb-references
   └─ (Optional) Save KB references


Workflow 2: Refine Idea
──────────────────────
1. GET /api/ideas/tree (or specific folder)
   └─ Show ideas for refinement

2. GET /api/ideas/file
   └─ Display file content (auto-converts DOCX→HTML)

3. POST /api/ideas/upload
   ├─ target_folder = existing folder (edit mode)
   ├─ Overwrites/adds files
   └─ Returns updated folder info

4. POST /api/workflow/{name}/action
   ├─ Updates action.refine_idea
   ├─ Sets deliverables.refined-idea
   └─ Progresses workflow


Workflow 3: Organize Ideas (Move/Duplicate)
──────────────────────────────────────────
1. GET /api/ideas/tree (or folder-contents)
   └─ Display tree for selection

2. POST /api/ideas/validate-drop
   └─ Validate target before dropping

3. POST /api/ideas/move or POST /api/ideas/duplicate
   └─ Move/duplicate folder with collision handling

4. POST /api/ideas/rename
   └─ Rename top-level folder


┌──────────────────────────────────────────────────────┐
│ SECONDARY ENDPOINTS (CONFIG & UTILITIES)            │
└──────────────────────────────────────────────────────┘

Configuration:
──────────────
GET /api/ideas/toolbox        ← Read toolbox config
POST /api/ideas/toolbox       ← Save toolbox config

Knowledge Base:
───────────────
GET /api/ideas/kb-references       ← Read KB refs for folder
POST /api/ideas/kb-references      ← Save KB refs
DELETE /api/ideas/kb-references    ← Delete KB refs

Skills:
───────
GET /api/skills               ← List all skills with descriptions

Management:
───────────
GET /api/ideas/folder-contents  ← Lazy load specific folder
GET /api/ideas/search           ← Search tree by query
GET /api/ideas/delete-info      ← Get item info before delete
GET /api/ideas/download         ← Download file
POST /api/ideas/create-folder   ← Create empty folder
POST /api/ideas/rename-file     ← Rename file

File Operations:
────────────────
GET /api/ideas/file           ← Serve file (auto-converts DOCX/MSG)
POST /api/ideas/delete        ← Delete file or folder
```

---

## 6. Action Dependency Chain

```
IDEATION STAGE ACTIONS

┌─────────────────────┐
│ compose_idea        │ (MANDATORY)
│                     │
│ Status: pending     │
│ (User opens modal)  │
└────────┬────────────┘
         │
         ├─ Prerequisites: None
         ├─ User Action: Create & upload idea
         ├─ Deliverables:
         │  ├─ raw-ideas: file paths[]
         │  └─ ideas-folder: folder path
         │
         ├─ Status Update:
         │  └─ POST /api/workflow/.../action
         │     {action: "compose_idea", status: "done"}
         │
         └─ Next Actions Suggested:
            ├─ refine_idea (mandatory)
            ├─ reference_uiux (optional)
            └─ design_mockup (optional)

         │
         ▼

┌─────────────────────────────────────┐
│ refine_idea                         │ (MANDATORY)
│                                     │
│ Status: pending → in_progress → done│
│ (User refines existing idea)        │
└────────┬────────────────────────────┘
         │
         ├─ Prerequisites:
         │  └─ compose_idea must be "done"
         │  └─ raw-ideas must exist
         │
         ├─ User Action: Edit & refine
         ├─ Deliverables:
         │  ├─ refined-idea: summary file
         │  └─ refined-ideas-folder: folder path
         │
         ├─ Status Update:
         │  └─ POST /api/workflow/.../action
         │     {action: "refine_idea", status: "done"}
         │
         └─ Next Actions Suggested:
            ├─ design_mockup (optional)
            └─ requirement_gathering (move to next stage)


┌─────────────────────────────────────┐
│ reference_uiux                      │ (OPTIONAL)
│                                     │
│ Status: pending → in_progress → done│
└────────┬────────────────────────────┘
         │
         ├─ Prerequisites: None
         ├─ User Action: Select UIUX references
         ├─ Deliverables:
         │  └─ uiux-reference: reference paths
         │
         └─ Next Actions Suggested:
            ├─ design_mockup
            └─ refine_idea


┌─────────────────────────────────────┐
│ design_mockup                       │ (OPTIONAL)
│                                     │
│ Status: pending → in_progress → done│
└────────┬────────────────────────────┘
         │
         ├─ Prerequisites:
         │  └─ refined-idea must exist (from refine_idea)
         │  └─ optional: uiux-reference
         │
         ├─ User Action: Create mockup
         ├─ Deliverables:
         │  ├─ mockup-html: mockup file
         │  └─ mockups-folder: folder path
         │
         └─ Next Actions Suggested:
            └─ requirement_gathering (move to next stage)


All actions → Stage completion
   │
   ▼

NEXT STAGE: requirement
├─ requirement_gathering (mandatory)
├─ competitive_analysis (optional)
└─ ...more actions
```

