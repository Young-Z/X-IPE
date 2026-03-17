---
name: x-ipe-task-based-application-knowledge-extractor
description: Extract knowledge from applications (source code repos, docs, URLs, running apps, files) and package into KB intake format. Use when extracting documentation, user manuals, or knowledge from application sources. Triggers on requests like "extract knowledge", "knowledge extraction", "extract user manual", "analyze application".
category: standalone
triggers:
  - "extract knowledge"
  - "knowledge extraction"
  - "extract user manual"
  - "analyze application"
  - "extract documentation"
  - "build knowledge base from app"
---

# Application Knowledge Extractor

> **Version:** 1.1.0 | **Status:** Candidate | **Feature:** FEATURE-050-B

## Purpose

1. **Extract knowledge** from diverse application sources (source code repos, documentation folders, public URLs, running web apps, single files)
2. **Auto-detect input type** (source_code_repo, documentation_folder, public_url, running_web_app, single_file), format (markdown, python, html, mixed), and app type (web, cli, mobile, unknown)
3. **Load tool skills** dynamically based on extraction category (e.g., \`x-ipe-tool-knowledge-extraction-user-manual\`) to obtain playbooks, collection templates, and acceptance criteria
4. **Package extracted knowledge** into KB intake format via \`.intake/\` pipeline (FEATURE-050-E) following tool skill guidance

---

## Important Notes

### ⚠️ BLOCKING Rules

1. **v1 Scope:** Only "user-manual" extraction category is supported. Requests for other categories (API-reference, architecture, runbook, configuration) will halt with error listing v1-supported categories.
2. **Tool Skill Required:** Extraction cannot proceed without a matching tool skill (e.g., \`x-ipe-tool-knowledge-extraction-user-manual\`). If no tool skill is found, the skill halts with error.
3. **File-Based Handoff:** All knowledge exchange between extractor and tool skills MUST use \`.checkpoint/\` folder. Inline text exchange is prohibited.
4. **Checkpoint Location:** \`.checkpoint/\` is created in CWD (project root), NEVER inside target directory. For URL-only targets, CWD is used.
5. **One Category Per Run:** No parallel multi-category extraction. One extraction session processes one category.

### 🎯 Implemented Phases

This version implements **Phase 1 (Foundation)** and **Phase 2 (Extraction)**:
- ✅ Input analysis (detect type, format, app-type)
- ✅ Category selection (v1: hardcoded filter)
- ✅ Tool skill loading (glob discover, load, get artifacts)
- ✅ Handoff protocol initialization (.checkpoint/ setup)
- ✅ Source content extraction (template-guided, per-section)

**NOT Yet Implemented (future features):**
- ❌ Validation & coverage loop (FEATURE-050-C)
- ❌ Checkpoint persistence & resume (FEATURE-050-D)
- ❌ KB intake output generation (FEATURE-050-E)

---

## Input Parameters

```yaml
input:
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-application-knowledge-extractor"
  execution_mode: "free-mode | workflow-mode"
  workflow:
    name: "N/A"
  category: "standalone"
  next_task_based_skill:
    - skill: "x-ipe-tool-kb-librarian"
      condition: "Organize extracted KB files into knowledge base"
  process_preference:
    interaction_mode: "interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill"
  
  # Required inputs
  target: "{path or URL to application/documentation}"
  purpose: "user-manual"  # v1: only user-manual supported
  
  # Optional
  config_overrides:
    max_retries: 3
    web_search_enabled: true
    timeout_seconds: 15
```

### Input Initialization

```xml
<input_init>
  <!-- Standard fields (auto-populated by workflow) -->
  <field name="task_id" source="x-ipe+all+task-board-management (auto-generated)" />
  <field name="execution_mode" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="workflow.name" source="x-ipe-workflow-task-execution (from --workflow-mode@{name})" />
  <field name="category" derive="Read from this skill's Output Result `category` field → 'standalone'" />
  <field name="process_preference.interaction_mode" source="from caller (x-ipe-workflow-task-execution) or default 'interact-with-human'" />

  <!-- Skill-specific fields -->
  <field name="target" source="user-provided (path or URL to application/documentation)" />
  <field name="purpose" source="user-provided, must be v1-supported category ('user-manual')" />
  <field name="config_overrides" source="optional user-provided overrides, defaults: max_retries=3, web_search_enabled=true, timeout_seconds=15" />
</input_init>
```

**CONTEXT — Validate Prerequisites:**
- ✅ \`target\` parameter is provided (path or URL)
- ✅ \`purpose\` parameter matches a v1-supported category ("user-manual")
- ✅ Target path exists (if local) OR URL is reachable (if remote)
- ✅ Working directory is writable (for .checkpoint/ creation)

**DECISION — Validation Gates:**
- IF \`target\` is missing → halt with error: "Parameter 'target' is required"
- IF \`purpose\` is not "user-manual" → halt with error: "Category '{purpose}' is not supported in v1. Supported: user-manual"
- IF target path does not exist → halt with error: "Target path '{target}' does not exist"
- IF target URL returns non-200 status → halt with error: "URL not reachable (HTTP {status})"
- IF working directory is not writable → halt with error: "Working directory is not writable. Cannot create .checkpoint/ folder"

**ACTION — Initialize:**
- Set default \`config_overrides\` if not provided: \`max_retries=3, web_search_enabled=true, timeout_seconds=15\`
- Resolve symlinks in target path (if local)
- Log input parameters for debugging

---

## Definition of Ready (DoR)

- [ ] **Task exists on task-board.md** with status "pending" or "in_progress"
- [ ] **Input validation passed:** target exists/reachable, purpose is v1-supported
- [ ] **Working directory writable:** .checkpoint/ can be created
- [ ] **Tool skill discoverable:** \`.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md\` path is accessible

---

## Execution Flow

| Phase | Name | Steps | Feature |
|-------|------|-------|---------|
| 1 | 博学之 — Study Broadly | 1.1 Analyze Input, 1.2 Select Category, 1.3 Load Tool Skill, 1.4 Initialize Handoff | FEATURE-050-A ✅ |
| 2 | 审问之 — Inquire Thoroughly | 2.1 Extract Source Content | FEATURE-050-B 🔜 |
| 3 | 慎思之 — Think Carefully | 3.1 Validate & Coverage Loop | FEATURE-050-C 🔜 |
| 4 | 明辨之 — Discern Clearly | 4.1 Handle Errors & Checkpoints | FEATURE-050-D 🔜 |
| 5 | 笃行之 — Practice Earnestly | 5.1 Generate KB Intake Output, 5.2 Complete | FEATURE-050-E 🔜 + Completion |
| 6 | 继续执行 — Continue Execution | 6.1 Decide Next Action, 6.2 Execute Next Action | Standard |

---

## Phase Definitions

### Phase 1: 博学之 — Study Broadly (Foundation)

**Purpose:** Analyze input source, detect type/format/app-type, select extraction category, load tool skill, initialize handoff protocol.

**Steps:**
1. **Step 1.1 — Analyze Input:** Classify target as input_type (source_code_repo, documentation_folder, public_url, running_web_app, single_file), detect format (markdown, python, html, mixed), detect app_type (web, cli, mobile, unknown)
2. **Step 1.2 — Select Category:** Validate purpose against v1-supported categories ("user-manual" only in v1)
3. **Step 1.3 — Load Tool Skill:** Glob \`.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md\`, filter by category, load SKILL.md, extract artifact paths (playbook, collection template, acceptance criteria)
4. **Step 1.4 — Initialize Handoff:** Create \`.checkpoint/session-{timestamp}/\` folder in CWD, write session manifest YAML

**Deliverables:**
- \`InputAnalysis\` object (input_type, format, app_type, source_metadata)
- Selected category: "user-manual"
- Loaded tool skill: "x-ipe-tool-knowledge-extraction-user-manual"
- Checkpoint path: ".checkpoint/session-{timestamp}/"
- Session manifest: ".checkpoint/session-{timestamp}/manifest.yaml"

### Phase 2: 审问之 — Inquire Thoroughly (Source Extraction)

**Status:** ✅ FEATURE-050-B — IMPLEMENTED

**Steps:**
1. **Step 2.1 — Extract Source Content:** Read collection template, iterate sections, extract knowledge per input_type (file reading / web browsing / app inspection), write section content files, update manifest

**Deliverables:**
- Content files: `.checkpoint/session-{timestamp}/content/section-{NN}-{slug}.md`
- Updated manifest with per-section status, timestamps, warnings

### Phase 3: 慎思之 — Think Carefully (Validation Loop)

**Status:** 🔜 FEATURE-050-C — NOT IMPLEMENTED

**Planned Steps:**
1. **Step 3.1 — Validate & Coverage Loop:** Send content to tool skill for validation, assess coverage gaps, decide depth/breadth adjustments, iterate until acceptance criteria met

**Deliverables:** Validated content with coverage assessment

### Phase 4: 明辨之 — Discern Clearly (Error Handling)

**Status:** 🔜 FEATURE-050-D — NOT IMPLEMENTED

**Planned Steps:**
1. **Step 4.1 — Handle Errors & Checkpoints:** Retry logic for inaccessible sources, pause/resume capability, checkpoint management, error recovery

**Deliverables:** Robust extraction with checkpoint recovery

### Phase 5: 笃行之 — Practice Earnestly (KB Output & Completion)

**Status:** 🔜 FEATURE-050-E — NOT IMPLEMENTED + Standard Completion

**Planned Steps:**
1. **Step 5.1 — Generate KB Intake Output:** Quality scoring, generate \`.intake/\` pipeline files
2. **Step 5.2 — Complete:** Verify DoD, update task status, archive \`.checkpoint/\`

**Deliverables:** KB intake output ready for librarian

### Phase 6: 继续执行 — Continue Execution (Standard)

**Purpose:** Decide and execute next action based on task completion status.

---

## Execution Procedure

### Phase 1: 博学之 — Study Broadly (Foundation)

#### Step 1.1 — Analyze Input

**CONTEXT:** Read target parameter (path or URL). Determine if local path or remote URL.

**DECISION — Classify Input Type:**
- IF target is local directory AND empty → halt with error
- IF directory with package.json/pyproject.toml/Cargo.toml → input_type = "source_code_repo"
- IF directory with only .md/.rst/.txt files → input_type = "documentation_folder"
- IF `localhost:*` or `127.0.0.1:*` → input_type = "running_web_app"
- IF `https?://*` (not localhost) → input_type = "public_url"
- IF single file → input_type = "single_file"
- ELSE → halt with error

**ACTION — Detect Format & App Type:**
- Call input detection heuristics (see `references/input-detection-heuristics.md`)
- Detect format: analyze file extensions (.md → markdown, .py → python, mixed → mixed)
- Detect app_type: framework markers (Flask/Django → web, argparse/click → cli, React Native → mobile, none → unknown)
- Collect source_metadata: primary_language, framework, file_count, total_size_bytes, entry_points, has_docs

**VERIFY:** ✅ InputAnalysis created with input_type, format, app_type, source_metadata

**REFERENCE:** `references/input-detection-heuristics.md`, `templates/input-analysis-output.md`

---

#### Step 1.2 — Select Category

**CONTEXT:** Read purpose parameter, check against v1-supported categories.

**DECISION — Category Selection (v1):**
- IF purpose == "user-manual" → selected_category = "user-manual"
- IF purpose in ["API-reference", "architecture", "runbook", "configuration"] → halt: "Not supported in v1"
- ELSE → halt: "Unknown category"

**VERIFY:** ✅ selected_category is "user-manual"

**REFERENCE:** `references/category-taxonomy.md`

---

#### Step 1.3 — Load Tool Skill

**CONTEXT:** Glob `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md`, filter by category.

**DECISION:** 0 matches → halt (install tool skill); 1 match → load; multiple → filter by frontmatter category.

**ACTION — Load Tool Skill:**
- Read SKILL.md, parse frontmatter (name, categories)
- Extract artifact paths: playbook_template, collection_template, acceptance_criteria
- Read app-type mixin paths (web, cli, mobile overrides)
- Verify artifact paths exist

**VERIFY:** ✅ loaded_tool_skill set, artifact paths exist, supports "user-manual"

**REFERENCE:** `x-ipe-docs/requirements/EPIC-050/FEATURE-050-A/technical-design.md` (Tool Skill Interface Contract)

---

#### Step 1.4 — Initialize Handoff

**CONTEXT:** Determine checkpoint path `.checkpoint/session-{timestamp}/` in CWD.

**DECISION:** If path exists → create new timestamped subfolder; else → create it.

**ACTION — Create Session Manifest:**
- Create directory structure: `manifest.yaml`, `content/`, `feedback/`
- Write manifest using template (`templates/checkpoint-manifest.md`)
- Fields: schema_version, session_id, created_at, target, purpose, input_analysis, selected_category, loaded_tool_skill, status ("initialized")

**VERIFY:** ✅ Checkpoint dir exists, manifest.yaml written with status "initialized"

**REFERENCE:** `references/handoff-protocol.md`, `templates/checkpoint-manifest.md`

---

### Phase 2: 审问之 — Inquire Thoroughly (Source Extraction)

#### Step 2.1 — Extract Source Content

**CONTEXT — Read Collection Template:**
- Read `tool_skill_artifacts.collection_template` file from Phase 1 output
- Parse sections: each H2 heading = one section with extraction prompts in HTML comments
- Create `{checkpoint_path}/content/` directory; update manifest status → "extracting"
- Load `config_overrides`: web_search_enabled (default true), max_files_per_section (default 50)

**DECISION — Extraction Capability per input_type:**
- `source_code_repo` / `documentation_folder` → **local file reading** (enumerate, skip, filter, read)
- `single_file` → **direct file read** (one file, map relevant portions per section)
- `public_url` → **Chrome DevTools browsing** (navigate_page, take_snapshot; follow up to 5 links/section)
- `running_web_app` → **Chrome DevTools navigation + interaction** (navigate, click, take_snapshot, take_screenshot)

**ACTION — Per-Section Extraction Loop:**
For EACH section in collection template order:
1. Identify relevant source materials matching section extraction prompts
2. Apply skip rules (see `references/extraction-engine-heuristics.md` for evaluation order)
3. Read/browse/inspect using the capability from DECISION above
4. **Synthesize** knowledge into coherent content — do NOT raw-dump files
5. Screenshots: user-provided first → Chrome DevTools auto-capture → graceful skip
6. IF `config_overrides.web_search_enabled`: augment with purpose-driven search (supplementary only)
7. Write to `{checkpoint_path}/content/section-{NN}-{slug}.md` (see reference for format)
8. Update `manifest.yaml` with section result (status, content_file, files_read, warnings, timestamps)

**VERIFY:**
- ✅ All template sections processed (each has status: extracted | skipped | empty | error | partial)
- ✅ Content files exist in `{checkpoint_path}/content/` for each extracted section
- ✅ Manifest updated per-section with status, content_file, files_read, warnings, timestamps
- ✅ Phase 2 overall status in manifest is "phase_2_complete"
- ✅ All content via file paths in checkpoint — no inline content

**REFERENCE:**
- Extraction heuristics: `.github/skills/x-ipe-task-based-application-knowledge-extractor/references/extraction-engine-heuristics.md`
- Handoff protocol: `.github/skills/x-ipe-task-based-application-knowledge-extractor/references/handoff-protocol.md`

---

### Phase 3-4: Future Implementation Stubs

**Phase 3 (慎思之):** Validation & coverage loop — See FEATURE-050-C specification

**Phase 4 (明辨之):** Error handling & checkpoints — See FEATURE-050-D specification

---

### Phase 5: 笃行之 — Practice Earnestly (Completion)

#### Step 5.1 — Generate KB Intake Output (FEATURE-050-E Stub)

**Status:** 🔜 NOT IMPLEMENTED — Placeholder for FEATURE-050-E

**Planned Actions:**
- Quality scoring of extracted knowledge
- Generate \`.intake/\` pipeline files
- Prepare for librarian handoff

---

#### Step 5.2 — Complete

**CONTEXT — Verify Phases Complete:**
- Check Phase 1 + Phase 2 completed:
  - ✅ Input analysis complete (InputAnalysis object exists)
  - ✅ Category selected ("user-manual")
  - ✅ Tool skill loaded (artifact paths obtained)
  - ✅ Handoff initialized (.checkpoint/ created with manifest)
  - ✅ Source extraction complete (content files written, manifest phase_2_complete)

**DECISION — Determine Completion Status:**
- IF Phase 1 + Phase 2 complete → status = "extraction_complete" (awaiting FEATURE-050-C validation)
- IF only Phase 1 complete → status = "ready_for_extraction"
- IF any step failed → status = "blocked"

**ACTION — Update Task Board & Review Gate:**
1. Update task-board.md: move task to Completed section
2. Set task output_links: [".checkpoint/session-{timestamp}/"]
3. Log completion summary
4. Mode-aware review gate:
   - IF process_preference.interaction_mode == "dao-represent-human-to-interact":
     Skip human review. If any open questions remain, invoke
     x-ipe-dao-end-user-representative to resolve them autonomously.
   - ELIF process_preference.interaction_mode == "dao-represent-human-to-interact-for-questions-in-skill" OR "interact-with-human":
     Present results to human and wait for approval.

**VERIFY:**
- ✅ Task status on task-board.md is "completed"
- ✅ Output result YAML populated
- ✅ DoD checklist satisfied

---

### Phase 6: 继续执行 — Continue Execution

#### Step 6.1 — Decide Next Action

**CONTEXT:** Collect task_completion_output. Route based on status:
- "extraction_complete" → invoke x-ipe-tool-kb-librarian (future: after FEATURE-050-C validation)
- "ready_for_extraction" → wait for Phase 2 extraction
- "blocked" → report error

**DECISION — Mode-Aware Routing:**
- IF interaction_mode == "dao-represent-human-to-interact": invoke DAO for routing
- ELSE: present suggestion to human

---

#### Step 6.2 — Execute Next Action

**ACTION:** Log completion status. Future: invoke x-ipe-tool-kb-librarian with extracted KB files.

---

## Output Result

```yaml
task_completion_output:
  category: "standalone"
  status: "extraction_complete | ready_for_extraction | blocked"
  next_task_based_skill:
    - skill: "x-ipe-tool-kb-librarian"
      condition: "Organize extracted KB files into knowledge base"
  process_preference:
    interaction_mode: "{from input}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "{.checkpoint/session-{timestamp}/}"
  
  # Dynamic outputs
  input_analysis:
    input_type: "source_code_repo | documentation_folder | running_web_app | public_url | single_file"
    format: "mixed | markdown | python | javascript | html | yaml | json | go | rust | java | ruby | restructuredtext | text | unknown"
    app_type: "web | cli | mobile | unknown"
    source_metadata:
      primary_language: "string | null"
      framework: "string | null"
      secondary_app_types: []  # Lower-priority app types detected (e.g., both web + cli)
      file_count: int
      total_size_bytes: int
      entry_points: ["string"]
      has_docs: bool
  
  selected_category: "user-manual"
  deferred_categories: []  # v1: none
  loaded_tool_skill: "x-ipe-tool-knowledge-extraction-user-manual | null"
  tool_skill_artifacts:
    playbook_template: "path | null"
    collection_template: "path | null"
    acceptance_criteria: "path | null"
    app_type_mixins:
      web: "path | null"
      cli: "path | null"
      mobile: "path | null"
  checkpoint_path: ".checkpoint/session-{timestamp}/"
  
  # Phase 2 outputs (FEATURE-050-B)
  extraction_summary:
    sections_extracted: int
    sections_skipped: int
    sections_error: int
    total_warnings: int
    content_files: ["content/section-{NN}-{slug}.md"]
  
  # Future fields (FEATURE-050-E)
  extraction_status: "foundation_only | complete | partial | failed"
  quality_score: null  # 0.0-1.0 in FEATURE-050-E
```

---

## Definition of Done (DoD)

- [ ] **Phase 1 Complete:** All steps in Phase 1 executed successfully
- [ ] **InputAnalysis Created:** input_type, format, app_type, source_metadata populated
- [ ] **Category Selected:** "user-manual" selected and validated
- [ ] **Tool Skill Loaded:** \`x-ipe-tool-knowledge-extraction-user-manual\` loaded with artifact paths
- [ ] **Checkpoint Initialized:** \`.checkpoint/session-{timestamp}/\` created with manifest.yaml
- [ ] **Phase 2 Complete:** All template sections extracted, content files written
- [ ] **Manifest Updated:** Per-section status, content_file, files_read, warnings in manifest.yaml
- [ ] **Output Result Populated:** All dynamic fields in output YAML set
- [ ] **Task Board Updated:** Task moved to Completed section
- [ ] **Verification:** All VERIFY checkpoints in Phase 1 + Phase 2 steps passed

---

## Patterns & Anti-Patterns

### ✅ Patterns (Do This)

1. **Auto-Detect First:** Always run input analysis before category selection or tool skill loading
2. **File-Based Handoff:** Use \`.checkpoint/\` folder for all knowledge exchange; never inline content in YAML
3. **Fail Fast:** Halt immediately when tool skill not found or target not accessible
4. **Synthesize, Don't Dump:** Extract and organize knowledge — never raw-copy files into content
5. **Section-by-Section:** Follow collection template order; one content file per section
6. **Reference Documentation:** Link to references/ for details; keep SKILL.md under 500 lines

### ❌ Anti-Patterns (Don't Do This)

1. **Inline Content Exchange:** Passing extracted content directly in YAML instead of file paths
2. **Raw File Dumps:** Copying file contents verbatim into section files without synthesis
3. **Skip Validation:** Proceeding without validating target exists/reachable
4. **Checkpoint Inside Target:** Creating \`.checkpoint/\` inside target directory instead of CWD
5. **Multi-Category Parallel:** Attempting multiple extraction categories in one session

---

## Examples

For detailed execution examples, see: \`.github/skills/x-ipe-task-based-application-knowledge-extractor/references/examples.md\`
