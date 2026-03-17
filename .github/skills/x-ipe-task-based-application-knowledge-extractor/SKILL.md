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

> **Version:** 1.4.0

## Purpose

1. **Extract knowledge** from diverse application sources (source code repos, documentation folders, public URLs, running web apps, single files)
2. **Auto-detect input type** (source_code_repo, documentation_folder, public_url, running_web_app, single_file), format (markdown, python, html, mixed), and app type (web, cli, mobile, unknown)
3. **Load tool skills** dynamically based on extraction category (e.g., `x-ipe-tool-knowledge-extraction-user-manual`) to obtain playbooks, collection templates, and acceptance criteria
4. **Package extracted knowledge** into KB intake format via `.intake/` pipeline following tool skill guidance

---

## Important Notes

### ⚠️ BLOCKING Rules

1. **v1 Scope:** Only "user-manual" extraction category is supported. Requests for other categories (API-reference, architecture, runbook, configuration) will halt with error listing v1-supported categories.
2. **Tool Skill Required:** Extraction cannot proceed without a matching tool skill (e.g., `x-ipe-tool-knowledge-extraction-user-manual`). If no tool skill is found, the skill halts with error.
3. **File-Based Handoff:** All knowledge exchange between extractor and tool skills MUST use `.checkpoint/` folder. Inline text exchange is prohibited.
4. **Checkpoint Location:** `.checkpoint/` is created in CWD (project root), NEVER inside target directory. For URL-only targets, CWD is used.
5. **One Category Per Run:** No parallel multi-category extraction. One extraction session processes one category.

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

<definition_of_ready>
  <checkpoint required="true">
    <name>Task Exists</name>
    <verification>Task exists on task-board.md with status pending or in_progress</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Input Validated</name>
    <verification>Target exists/reachable, purpose is v1-supported category</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Working Directory Writable</name>
    <verification>.checkpoint/ can be created in CWD</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Tool Skill Discoverable</name>
    <verification>.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md path accessible</verification>
  </checkpoint>
</definition_of_ready>

---

## Execution Flow

| Phase | Step | Name | Action | Gate |
|-------|------|------|--------|------|
| 1. 博学之 | 1.1 | Analyze Input | Classify input type, detect format/app-type | input classified |
| 1. 博学之 | 1.2 | Select Category | Validate purpose against v1 categories | category selected |
| 1. 博学之 | 1.3 | Load Tool Skill | Find and load matching tool skill | tool skill loaded |
| 1. 博学之 | 1.4 | Initialize Handoff | Create .checkpoint/ and session manifest | handoff ready |
| 2. 审问之 | 2.1 | Extract Source Content | Per-section template-guided extraction | content files written |
| 3. 慎思之 | 3.1 | Validate & Coverage Loop | Validate against criteria, iterate for gaps | coverage met or max iterations |
| 4. 明辨之 | 4.1 | Resume, Checkpoint & Error Handling | Detect prior sessions, save checkpoints, classify errors | errors handled |
| 5. 笃行之 | 5.1 | Quality Scoring | Compute 4-dimension quality scores | scores computed |
| 5. 笃行之 | 5.2 | Package KB Articles & Report | Generate .kb-intake/ output files | output packaged |
| 6. 继续执行 | 6.1 | Finalize & Clean Up | Update manifest, cleanup temp files | manifest finalized |
| 6. 继续执行 | 6.2 | Route Next Action | DAO-assisted routing to KB librarian | next action decided |

---

## Phase Definitions (5-Phase Learning Method — 博学之，审问之，慎思之，明辨之，笃行之)

| Phase | Chinese | English | SE Purpose | Typical Activities |
|-------|---------|---------|------------|-------------------|
| 1 | 博学之 (Bóxué) | Study Broadly | Gather comprehensive context | Analyze input, select category, load tool skill, init handoff |
| 2 | 审问之 (Shěnwèn) | Inquire Thoroughly | Extract source content | Template-guided per-section source content extraction |
| 3 | 慎思之 (Shènsī) | Think Carefully | Validate & iterate | Validate content against criteria, iterate for coverage gaps |
| 4 | 明辨之 (Míngbiàn) | Discern Clearly | Handle errors & checkpoints | Resume detection, checkpoint saves, error classification |
| 5 | 笃行之 (Dǔxíng) | Practice Earnestly | Package output | Quality scoring, KB article packaging, extraction report |
| 6 | 继续执行 | Route and Execute | Finalize & route next action | Cleanup temp files, route to KB librarian |

---

## Execution Procedure

<procedure>
<phase_1 name="博学之 — Study Broadly">
  <step_1_1>
    <name>Analyze Input</name>
    <action>
      1. Read target parameter, classify input_type (source_code_repo, documentation_folder, public_url, running_web_app, single_file)
      2. Detect format (markdown, python, html, mixed) and app_type (web, cli, mobile, unknown)
      3. Build InputAnalysis object with source_metadata
    </action>
    <constraints>
      - BLOCKING: Empty directory or unreachable URL → halt with error
    </constraints>
    <output>InputAnalysis {input_type, format, app_type, source_metadata}</output>
  </step_1_1>

  <step_1_2>
    <name>Select Category</name>
    <action>
      1. Read purpose parameter from input
      2. Validate against v1-supported categories (user-manual only)
      3. Halt with error if unsupported or unknown category
    </action>
    <constraints>
      - BLOCKING: purpose not "user-manual" → halt listing v1-supported categories
    </constraints>
    <output>selected_category = "user-manual"</output>
  </step_1_2>

  <step_1_3>
    <name>Load Tool Skill</name>
    <action>
      1. Glob .github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md, filter by category
      2. Parse frontmatter, extract artifact paths (playbook, collection template, acceptance criteria)
      3. Read app-type mixin paths, verify all artifact paths exist
    </action>
    <constraints>
      - BLOCKING: 0 matching tool skills → halt with install instructions
    </constraints>
    <output>loaded_tool_skill, tool_skill_artifacts {playbook_template, collection_template, acceptance_criteria, app_type_mixins}</output>
  </step_1_3>

  <step_1_4>
    <name>Initialize Handoff</name>
    <action>
      1. Create .checkpoint/session-{timestamp}/ in CWD with content/ and feedback/ subdirs
      2. Write manifest.yaml using templates/checkpoint-manifest.md
      3. Set manifest status to "initialized"
    </action>
    <constraints>
      - BLOCKING: CWD not writable → halt
    </constraints>
    <output>.checkpoint/session-{timestamp}/manifest.yaml with status "initialized"</output>
  </step_1_4>
</phase_1>

<phase_2 name="审问之 — Inquire Thoroughly">
  <step_2_1>
    <name>Extract Source Content</name>
    <action>
      1. Read collection template from Phase 1 artifacts, parse H2 sections with extraction prompts
      2. For each section: identify relevant sources, apply skip rules, extract/browse content
      3. Synthesize knowledge into coherent content (never raw-dump files)
      4. Write to checkpoint/content/section-{NN}-{slug}.md, update manifest per-section
    </action>
    <constraints>
      - BLOCKING: All content must go through file paths in checkpoint — no inline content
      - Extraction capability varies by input_type (local read vs Chrome DevTools)
    </constraints>
    <output>Content files in checkpoint/content/, manifest sections[] updated with status per section</output>
  </step_2_1>
</phase_2>

<phase_3 name="慎思之 — Think Carefully">
  <step_3_1>
    <name>Validate & Coverage Loop</name>
    <action>
      1. Load acceptance criteria from tool skill, validate each section (per-criterion pass/fail)
      2. Write feedback to checkpoint/feedback/, lock accepted sections
      3. Compute coverage_ratio, check exit conditions (all met / max iterations / plateau)
      4. Re-extract failing sections with adjusted prompts if iterations remain
    </action>
    <constraints>
      - Max iterations capped by config_overrides.max_validation_iterations (default 3)
    </constraints>
    <output>Per-section validation_status, final_coverage_ratio, exit_reason, coverage_history</output>
  </step_3_1>
</phase_3>

<phase_4 name="明辨之 — Discern Clearly">
  <step_4_1>
    <name>Resume, Checkpoint & Error Handling</name>
    <action>
      1. Cross-cutting: scan .checkpoint/ for resumable sessions (paused/extracting)
      2. Classify errors as transient (retry up to 3) or permanent (mark error, continue)
      3. Persist manifest after every section, enforce valid state machine transitions
      4. Append to error_log[] with section_id, error_type, message, retry_count, timestamp
    </action>
    <constraints>
      - BLOCKING: Invalid state transitions rejected with warning
      - Corrupted checkpoints (YAML parse fail) → fresh start with warning
    </constraints>
    <output>Manifest with valid state transitions, error_log[], resume capability</output>
  </step_4_1>
</phase_4>

<phase_5 name="笃行之 — Practice Earnestly">
  <step_5_1>
    <name>Quality Scoring</name>
    <action>
      1. Gather deterministic scoring inputs (criteria met, sub-section counts, freshness) — no LLM
      2. Compute per-section section_quality_score using 4-dimension formula
      3. Compute overall_quality_score (arithmetic mean), classify as high/acceptable/low
    </action>
    <constraints>
      - Scoring is deterministic: identical inputs → identical scores
      - Non-blocking: always proceed to Step 5.2 regardless of score
    </constraints>
    <output>phase_5.quality_scores[], overall_quality_score, quality_label</output>
  </step_5_1>

  <step_5_2>
    <name>Package KB Articles & Report</name>
    <action>
      1. Create x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/
      2. Generate .kb-index.json with sections, quality scores, provenance
      3. Write article .md files for accepted sections with YAML frontmatter
      4. Generate extraction_report.md (summary, scores, validation stats, error log, provenance)
    </action>
    <constraints>
      - All files UTF-8, no BOM
      - Error/skipped sections go to excluded_sections[] in index — no article files
    </constraints>
    <output>.kb-intake/ folder with .kb-index.json, article files, extraction_report.md</output>
  </step_5_2>
</phase_5>

<phase_6 name="继续执行 — Route and Execute">
  <step_6_1>
    <name>Finalize & Clean Up</name>
    <action>
      1. Update manifest: status → "complete", completed_at → ISO 8601
      2. Populate Output Result with extraction_status, quality_score, quality_label, kb_output_path
      3. Remove checkpoint content/ and feedback/ dirs; preserve manifest.yaml and packed/
      4. Update task-board.md → completed
    </action>
    <constraints>
      - Must preserve manifest.yaml and packed/ for audit trail
    </constraints>
    <output>Finalized manifest, populated Output Result, cleaned temp dirs</output>
  </step_6_1>

  <step_6_2>
    <name>Route Next Action</name>
    <action>
      1. DAO mode → log completion, route to x-ipe-tool-kb-librarian
      2. Manual mode → present completion summary to human
    </action>
    <constraints>
      - Routing decision follows process_preference.interaction_mode
    </constraints>
    <output>Next action routed or human notified</output>
  </step_6_2>
</phase_6>
</procedure>

REFERENCE: See `references/execution-procedures.md` for detailed CONTEXT/DECISION/ACTION/VERIFY blocks per step.

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
      secondary_app_types: []
      file_count: int
      total_size_bytes: int
      entry_points: ["string"]
      has_docs: bool
  
  selected_category: "user-manual"
  deferred_categories: []
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
  
  extraction_summary:
    sections_extracted: int
    sections_skipped: int
    sections_error: int
    total_warnings: int
    content_files: ["content/section-{NN}-{slug}.md"]
  
  validation_summary:
    final_coverage_ratio: float
    exit_reason: "all_criteria_met | max_iterations_reached | plateau_detected | skipped"
    iterations_completed: int
    coverage_history: [float]
    sections_accepted: int
    sections_needs_more_info: int
    sections_error: int
  
  error_summary:
    total_errors: int
    transient_retried: int
    permanent_halted: int
    sections_skipped: int
    resumed_from: "session path | null"
  
  extraction_status: "complete | partial | failed"
  quality_score: 0.0
  quality_label: "high | acceptable | low"
  kb_output_path: "x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/"
  task_output_links:
    - "x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/.kb-index.json"
    - "x-ipe-docs/knowledge-base/.kb-intake/{extraction_id}/extraction_report.md"
    - ".checkpoint/session-{timestamp}/manifest.yaml"
```

---

## Definition of Done (DoD)

<definition_of_done>
  <checkpoint required="true">
    <name>Phases 1-4 Complete</name>
    <verification>Input analyzed, content extracted, validation loop run, checkpoints saved</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Phase 5 Complete</name>
    <verification>Quality scores computed (4 dimensions), articles packaged in .kb-intake/, extraction report generated</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Phase 6 Complete</name>
    <verification>Manifest finalized, Output Result populated, temp files cleaned up</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Output Result Populated</name>
    <verification>All dynamic fields set: input_analysis, extraction/validation/error/quality summaries</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Verification Passed</name>
    <verification>All VERIFY checkpoints in Phase 1-6 steps passed</verification>
  </checkpoint>
</definition_of_done>

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

For detailed execution examples, see: `references/examples.md`
