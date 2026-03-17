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

> **Version:** 1.4.0 | **Status:** Candidate | **Feature:** FEATURE-050-E

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

- ✅ Phase 1 (Foundation): Input analysis, category selection, tool skill loading, handoff init
- ✅ Phase 2 (Extraction): Template-guided, per-section source content extraction
- ✅ Phase 3 (Validation): Extract-validate loop with coverage tracking and gap classification
- ✅ Phase 4 (Checkpoint): Resume detection, section-level checkpoint, 2-tier error handling
- ✅ Phase 5 (KB Output): Quality scoring, KB article packaging, extraction report generation

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
  <field name="task_id" source="auto-generated" />
  <field name="execution_mode" source="workflow or free-mode" />
  <field name="target" source="user-provided (path or URL)" />
  <field name="purpose" source="user-provided, v1: 'user-manual' only" />
  <field name="config_overrides" source="optional, defaults: max_retries=3, web_search_enabled=true, timeout_seconds=15, max_files_per_section=50, max_validation_iterations=3, coverage_target=0.8" />
</input_init>
```

**Validation Gates:**
- IF `target` missing → halt; IF `purpose` not "user-manual" → halt
- IF target path missing or URL unreachable → halt
- IF CWD not writable → halt
- Set defaults for unspecified config_overrides

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
| 2 | 审问之 — Inquire Thoroughly | 2.1 Extract Source Content | FEATURE-050-B ✅ |
| 3 | 慎思之 — Think Carefully | 3.1 Validate & Coverage Loop | FEATURE-050-C ✅ |
| 4 | 明辨之 — Discern Clearly | 4.1 Resume, Checkpoint & Error Handling | FEATURE-050-D ✅ |
| 5 | 笃行之 — Practice Earnestly | 5.1 Quality Scoring, 5.2 Package KB Articles & Report | FEATURE-050-E ✅ |
| 6 | 继续执行 — Continue Execution | 6.1 Finalize & Clean Up, 6.2 Route Next Action | FEATURE-050-E ✅ |

---

## Phase Definitions

### Phase 1: 博学之 — Study Broadly (Foundation)

**Status:** ✅ FEATURE-050-A — Input analysis, category selection, tool skill loading, handoff initialization

### Phase 2: 审问之 — Inquire Thoroughly (Source Extraction)

**Status:** ✅ FEATURE-050-B — Template-guided per-section source content extraction with manifest tracking

### Phase 3: 慎思之 — Think Carefully (Validation Loop)

**Status:** ✅ FEATURE-050-C — Validate content against tool skill criteria, iterate extraction for coverage gaps

### Phase 4: 明辨之 — Discern Clearly (Error Handling)

**Status:** ✅ FEATURE-050-D — Resume detection, section-level checkpoint, 2-tier error handling, state machine

### Phase 5: 笃行之 — Practice Earnestly (KB Output & Quality Scoring)

**Status:** ✅ FEATURE-050-E — Quality scoring (4 dimensions), KB article packaging, extraction report

### Phase 6: 继续执行 — Continue Execution

**Status:** ✅ FEATURE-050-E — Manifest finalization, cleanup, next action routing

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

### Phase 3: 慎思之 — Think Carefully (Validation Loop)

#### Step 3.1 — Validate & Iterate

**CONTEXT:** Read `tool_skill_artifacts.acceptance_criteria` from Phase 1. Load Phase 2 content from manifest. Config: `max_validation_iterations` (default 3), `coverage_target` (default 0.8). Update manifest: phase_3.status → "in_progress".

**DECISION — Exit Conditions (checked per iteration):**
- All sections accepted → exit "all_criteria_met"
- iterations ≥ max → exit "max_iterations_reached"
- coverage_ratio not improving (iteration > 1) → exit "plateau_detected"
- No content from Phase 2 → skip Phase 3 entirely

**ACTION — Iteration Loop (up to max_validation_iterations):**
1. Validate each non-accepted section against acceptance criteria (per-criterion pass/fail)
2. Write feedback to `{checkpoint_path}/feedback/section-{NN}-{slug}-iter-{M}.md`
3. Lock accepted sections — not re-validated in later iterations
4. Compute `coverage_ratio = criteria_met / total_criteria`; check exit conditions
5. Classify gaps as "depth" (shallow) or "breadth" (missing topics) — see reference
6. Re-extract failing sections via Phase 2 Step 2.1 with adjusted prompts

**VERIFY:**
- ✅ All sections have final validation_status (accepted | needs-more-info | error)
- ✅ Feedback files in `{checkpoint_path}/feedback/`, manifest updated with phase_3 results
- ✅ phase_3.final_coverage_ratio, exit_reason, coverage_history recorded

**REFERENCE:** `references/validation-loop-heuristics.md`, `references/handoff-protocol.md`

---

### Phase 4: 明辨之 — Discern Clearly (Checkpoint & Error Handling)

#### Step 4.1 — Resume, Checkpoint & Error Handling

**CONTEXT — Cross-Cutting Behavior:** Phase 4 wraps Phases 1–3 (not sequential). On invocation: scan `.checkpoint/session-*/manifest.yaml` sorted by timestamp desc; select most recent with status "paused"|"extracting". If valid → resume (skip accepted sections). If corrupted (YAML parse fail or schema_version ≠ "1.0") → log warning, start fresh. Config: `max_retries` (default 3 total attempts).

**DECISION — Error Classification & Recovery:**
- Transient error (timeout, rate limit, temp lock) → immediate retry, max 2 retries (3 total)
- Permanent error (not found, permission denied, unsupported) → no retry, mark section "error"
- Exhausted retries → mark "error", log to error_log[], continue next section (fail-open)
- Recovery: DAO mode → autonomous skip/adjust/halt; manual mode → surface options to human

**ACTION — Checkpoint & State Machine:**
1. After each section extraction/validation: persist manifest (status, updated_at, content_file)
2. On pause: status → "paused"; on resume: add event_log entry, refresh updated_at
3. Valid transitions: initialized→extracting, extracting→validating|paused, validating→paused, paused→extracting|validating, any→error|complete. Reject invalid with warning.
4. Append to error_log[]: {section_id, error_type, message, retry_count, timestamp}

**VERIFY:**
- ✅ Manifest status reflects valid state machine transition at every step
- ✅ error_log[] entries have required fields; resumed sessions skip accepted sections
- ✅ Corrupted checkpoints → fresh start with warning logged

**REFERENCE:** `references/checkpoint-error-heuristics.md`, `references/handoff-protocol.md`

---

### Phase 5: 笃行之 — Practice Earnestly (KB Output & Quality Scoring)

#### Step 5.1 — Quality Scoring

**CONTEXT — Gather Scoring Inputs (Deterministic Only — No LLM):**
- Read manifest `phase_3.per_section[]`: for each section, extract `criteria_met`, `criteria_total`, `iterations_validated`, `validation_status`
- Read collection template: count prescribed sub-sections (H3 headings / extraction prompts) per section
- Read packed content files: count present sub-sections (H2/H3 headings matching template) per section
- Read source file modification dates from `source_metadata` (if local); for URLs default freshness to 0.5

**DECISION — Classify Quality Threshold:**
- Compute per-section `section_quality_score` (see reference for 4-dimension formula)
- Compute `overall_quality_score` = arithmetic mean of section scores (exclude error/skipped from mean; count as 0.0 per BR-2)
- Classify: ≥ 0.80 → "high"; 0.50–0.79 → "acceptable"; < 0.50 → "low"
- IF "acceptable" → log warning with lowest-scoring sections; IF "low" → log warning with sections below 0.50
- Per-section: IF section score < 0.50 → set `quality_flag: "low"` in manifest

**ACTION:** Compute all scores per reference formulas. Write quality results to manifest: `phase_5.quality_scores[]`, `phase_5.overall_quality_score`, `phase_5.quality_label`. Scoring is non-blocking — always proceed to Step 5.2.

**VERIFY:** ✅ Every section has `section_quality_score` (0.0–1.0, 2dp); overall score and label set; identical inputs → identical scores

**REFERENCE:** `references/output-quality-heuristics.md` §1–§3

---

#### Step 5.2 — Package KB Articles & Report

**CONTEXT:** Read all packed content files from `.checkpoint/session-{timestamp}/packed/`. Read quality scores from Step 5.1. Read manifest for provenance data (target, loaded_tool_skill, timestamps). Derive `extraction_id` from session folder name.

**DECISION — Determine Output Path & Status:**
- Output folder: `x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/`
- IF zero accepted sections → extraction_status = "failed" (still generate report)
- IF all accepted → extraction_status = "complete"
- IF some accepted, some error/skipped → extraction_status = "partial"

**ACTION — Write Output Files:**
1. Create output folder (and `.kb-intake/` parent if needed)
2. Generate `.kb-index.json` per reference schema: title, category, extraction_id, quality_score, quality_label, sections[], excluded_sections[], source_summary, created_at, schema_version "1.0"
3. For each accepted section: write article `.md` with YAML frontmatter (section_id, title, quality_score, quality_dimensions, provenance) + validated content from packed files
4. For error/skipped sections: add to `excluded_sections[]` in index with status and reason; no article file
5. Generate `extraction_report.md`: Summary, Per-Section Scores (sorted quality ascending), Validation Statistics, Error Log, Provenance
6. All files UTF-8, no BOM

**VERIFY:**
- ✅ `.kb-index.json` exists with all required fields; article count matches accepted sections
- ✅ `extraction_report.md` exists with 5 sections; per-section table sorted ascending
- ✅ Excluded sections in index but no article files

**REFERENCE:** `references/output-quality-heuristics.md` §4–§7

---

### Phase 6: 继续执行 — Continue Execution

#### Step 6.1 — Finalize & Clean Up

**ACTION:** 1) Update manifest: `status` → "complete", `completed_at` → ISO 8601. 2) Populate Output Result: `extraction_status`, `quality_score`, `quality_label`, `kb_output_path`. 3) Set `task_output_links[]`: .kb-index.json, extraction_report.md, manifest paths. 4) Update task-board.md → completed. 5) Remove `{checkpoint_path}/content/` and `feedback/` dirs. 6) Preserve: `manifest.yaml`, `packed/`, `collection-template.md`.

**VERIFY:** ✅ Manifest "complete"; Output Result populated; temp dirs removed; packed/ + manifest preserved

#### Step 6.2 — Route Next Action

**DECISION:** DAO mode → log completion, future: invoke `x-ipe-tool-kb-librarian`; manual → present to human.

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
  
  # Phase 3 outputs (FEATURE-050-C)
  validation_summary:
    final_coverage_ratio: float  # 0.0-1.0
    exit_reason: "all_criteria_met | max_iterations_reached | plateau_detected | skipped"
    iterations_completed: int
    coverage_history: [float]  # per-iteration coverage ratios
    sections_accepted: int
    sections_needs_more_info: int
    sections_error: int
  
  # Phase 4 outputs (FEATURE-050-D)
  error_summary:
    total_errors: int
    transient_retried: int
    permanent_halted: int
    sections_skipped: int
    resumed_from: "session path | null"
  
  # Phase 5 outputs (FEATURE-050-E)
  extraction_status: "complete | partial | failed"
  quality_score: 0.0       # 0.0–1.0, overall quality (2 decimal places)
  quality_label: "high | acceptable | low"
  kb_output_path: "x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/"
  task_output_links:
    - "x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/.kb-index.json"
    - "x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/extraction_report.md"
    - ".checkpoint/session-{timestamp}/manifest.yaml"
```

---

## Definition of Done (DoD)

- [ ] **Phase 1 Complete:** Input analysis, category selection, tool skill loading, checkpoint init all passed
- [ ] **Phase 2 Complete:** All template sections extracted, content files written, manifest updated
- [ ] **Phase 3 Complete:** Validation loop executed, coverage_ratio computed, feedback files written
- [ ] **Phase 4 Complete:** Checkpoint saves after each section, errors classified and logged, resume detection works
- [ ] **Phase 5 Complete:** Quality scores computed (4 dimensions), articles packaged in .kb-intake/, extraction report generated
- [ ] **Phase 6 Complete:** Manifest finalized, Output Result populated, temp files cleaned up
- [ ] **Output Result Populated:** All dynamic fields (input_analysis, extraction/validation/error/quality summaries) set
- [ ] **Task Board Updated:** Task moved to Completed section
- [ ] **Verification:** All VERIFY checkpoints in Phase 1–6 steps passed

---

## Patterns & Anti-Patterns

### ✅ Do This
1. **Auto-Detect First:** Run input analysis before category selection or tool skill loading
2. **File-Based Handoff:** Use `.checkpoint/` for all knowledge exchange; never inline content
3. **Fail Fast:** Halt when tool skill not found or target not accessible
4. **Synthesize, Don't Dump:** Extract and organize — never raw-copy files into content
5. **Section-by-Section:** Follow collection template order; one content file per section

### ❌ Don't Do This
1. **Inline Content Exchange:** Passing content directly in YAML instead of file paths
2. **Raw File Dumps:** Copying file contents verbatim without synthesis
3. **Checkpoint Inside Target:** Creating `.checkpoint/` inside target directory instead of CWD
4. **Multi-Category Parallel:** Attempting multiple extraction categories in one session

---

## Examples

For detailed execution examples, see: \`.github/skills/x-ipe-task-based-application-knowledge-extractor/references/examples.md\`
