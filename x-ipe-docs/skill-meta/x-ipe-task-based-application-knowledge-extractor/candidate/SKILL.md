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

> **Version:** 2.0.0

## Purpose

1. **Extract knowledge** from diverse application sources (source code repos, documentation folders, public URLs, running web apps, single files)
2. **Auto-detect input type** plus open-ended source format and application-context labels, preserving both summary labels and multi-value detections without hardcoded format/app-type enumerations
3. **Load tool skills** dynamically based on extraction category (e.g., `x-ipe-tool-knowledge-extraction-user-manual`) to obtain playbooks, collection templates, and acceptance criteria
4. **Package extracted knowledge** into KB intake format via `.intake/` pipeline following tool skill guidance

---

## Important Notes

### ⚠️ BLOCKING Rules

1. **v1 Scope:** Only "user-manual", "application-reverse-engineering", and "notes" extraction categories are supported. Requests for other categories (API-reference, runbook, configuration) will halt with error listing supported categories.
2. **Tool Skill Required:** Extraction cannot proceed without a matching tool skill (e.g., `x-ipe-tool-knowledge-extraction-user-manual`). If no tool skill is found, the skill halts with error.
3. **File-Based Handoff:** All knowledge exchange between extractor and tool skills MUST use `.x-ipe-checkpoint/` folder. Inline text exchange is prohibited.
4. **Checkpoint Location:** `.x-ipe-checkpoint/` is created in CWD (project root), NEVER inside target directory. For URL-only targets, CWD is used.
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
  purpose: "user-manual | application-reverse-engineering | notes"  # supported categories
  
  # Optional
  config_overrides:
    max_retries: 3
    web_search_enabled: true
    timeout_seconds: 15
    max_files_per_section: 20  # default matches tool skill default; override to increase

  # Behavior Context (optional — provided by x-ipe-knowledge-mimic-web-behavior-tracker)
  behavior_context:
    learning_folder: ""  # path to learning folder with track/track-list.json and imgs/
                         # When provided, use tracked behavior data as SUPPLEMENTARY guidance
                         # to prioritize features and understand user workflows.
                         # The extractor MUST still explore the target independently via Chrome DevTools.

  # Deep Research Mode (optional)
  deep_research:
    rounds: 1           # default: 1 (single pass), max: 10, or "smart"
                         # "smart": auto-exit when 100% of functions/UI covered

  # Instruction Temperature (optional — applies to user-manual category)
  instruction_temperature: "balanced"  # strict | balanced | creative
    # Controls instructional content tone in user manual extraction.
    # Passed to tool skill operations (get_collection_template, pack_section, score_quality).
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="auto-generated" />
  <field name="execution_mode" source="workflow or free-mode" />
  <field name="target" source="user-provided (path or URL)" />
  <field name="purpose" source="user-provided: 'user-manual', 'application-reverse-engineering', or 'notes'" />
  <field name="config_overrides" source="optional, defaults: max_retries=3, web_search_enabled=true, timeout_seconds=15, max_files_per_section=20, max_validation_iterations=3, coverage_target=0.8. Config values are passed through to tool skill operations." />
  <field name="behavior_context.learning_folder" source="optional, from behavior tracker skill. Path to learning folder containing tracked events and screenshots." />
  <field name="deep_research.rounds" source="ask-user, default: 1, values: 1-10 or 'smart'" />
  <field name="instruction_temperature" source="ask-user, default: balanced, values: strict|balanced|creative. Only for purpose=user-manual." />
</input_init>
```

**Validation Gates:**
- IF `target` missing → halt; IF `purpose` not in ["user-manual", "application-reverse-engineering", "notes"] → halt
- IF target path missing or URL unreachable → halt
- IF CWD not writable → halt
- Set defaults for unspecified config_overrides
- IF `deep_research.rounds` not provided → prompt user:
  - "How many deep research rounds? (default: 1, max: 10, or 'smart' for auto-detect)"
  - IF numeric → clamp to 1–10; IF "smart" → set rounds = "smart"
- IF `purpose` == "user-manual" AND `instruction_temperature` not provided → prompt user:
  - "What instruction tone? Strict (exact/verbatim), Balanced (default, accuracy + flow), or Creative (exploratory)?"
  - IF not in [strict, balanced, creative] → default to "balanced"

---

## Definition of Ready (DoR)

<definition_of_ready>
  <checkpoint required="true">
    <name>Task Exists</name>
    <verification>Task exists on task-board.md with status pending or in_progress</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Input Validated</name>
    <verification>Target exists/reachable, purpose is a supported category</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Working Directory Writable</name>
    <verification>.x-ipe-checkpoint/ can be created in CWD</verification>
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
| 1. 博学之 | 1.1 | Analyze Input | Classify input type, detect source format and app-context profiles | input classified |
| 1. 博学之 | 1.2 | Select Category | Validate purpose against v1 categories | category selected |
| 1. 博学之 | 1.3 | Load Tool Skill | Find and load matching tool skill | tool skill loaded |
| 1. 博学之 | 1.4 | Initialize Handoff | Create .x-ipe-checkpoint/ and session manifest | handoff ready |
| 2. 审问之 | 2.1 | Extract Source Content | Per-section template-guided extraction | content files written |
| 3. 慎思之 | 3.1 | Validate & Coverage Loop | Validate against criteria, iterate for gaps | coverage met or max iterations |
| 3.5 实践验证 | 3.5.1 | Walkthrough Testing | Follow manual through running app, test each step literally | followability ≥ 0.7 or max iterations |
| 4. 明辨之 | 4.1 | Resume, Checkpoint & Error Handling | Detect prior sessions, save checkpoints, classify errors | errors handled |
| 5. 笃行之 | 5.1 | Quality Scoring | Delegate to tool skill score_quality, loop if low | scores computed |
| 5. 笃行之 | 5.2 | Package KB Articles & Report | Generate .intake/ output files | output packaged |
| 5. 笃行之 | 5.3 | Deep Research Iteration | Analyze gaps, loop to Phase 2 if rounds remain | rounds exhausted or coverage 100% |
| 6. 继续执行 | 6.1 | Finalize & Clean Up | Update manifest, cleanup temp files | manifest finalized |
| 6. 继续执行 | 6.2 | Route Next Action | DAO-assisted routing to KB librarian | next action decided |

---

## Phase Definitions (5-Phase Learning Method — 博学之，审问之，慎思之，明辨之，笃行之)

| Phase | Chinese | English | SE Purpose | Typical Activities |
|-------|---------|---------|------------|-------------------|
| 1 | 博学之 (Bóxué) | Study Broadly | Gather comprehensive context | Analyze input, select category, load tool skill, init handoff |
| 2 | 审问之 (Shěnwèn) | Inquire Thoroughly | Extract source content | Template-guided per-section source content extraction |
| 3 | 慎思之 (Shènsī) | Think Carefully | Validate & iterate | Validate content against criteria, iterate for coverage gaps |
| 3.5 | 实践验证 (Shíjiàn Yànzhèng) | Validate by Practice | Test manual against running app | Walk through scenarios literally, record gaps, feed back for re-extraction |
| 4 | 明辨之 (Míngbiàn) | Discern Clearly | Handle errors & checkpoints | Resume detection, checkpoint saves, error classification |
| 5 | 笃行之 (Dǔxíng) | Practice Earnestly | Package output | Tool-skill-delegated quality scoring, KB article packaging, extraction report |
| 6 | 继续执行 | Route and Execute | Finalize & route next action | Cleanup temp files, route to KB librarian |

---

## Execution Procedure

<procedure>
<phase_1 name="博学之 — Study Broadly">
  <step_1_1>
    <name>Analyze Input</name>
    <action>
      1. Read target parameter, classify input_type (source_code_repo, documentation_folder, public_url, running_web_app, single_file)
      2. Detect source format label(s) and application-context label(s); store summary labels in `format` / `app_type` and preserve all detections in `source_metadata.detected_formats` / `source_metadata.detected_app_types`
      3. Detect `app_name` for extraction_id derivation:
         - running_web_app / public_url → page title (first heading or `<title>` tag), slugified
         - source_code_repo → package name from package.json `name` or pyproject.toml `[project] name`
         - documentation_folder → directory name
         - single_file → file name without extension
         - Slugify: lowercase, replace spaces/special chars with hyphens, strip leading/trailing hyphens
         - Store as `source_metadata.app_name` (e.g., "x-ipe", "my-cool-app")
      4. Build InputAnalysis object with source_metadata (including app_name)
      5. Determine extraction techniques based on input_type:
         - source_code_repo / documentation_folder → file reading, code analysis
         - public_url / running_web_app → Chrome DevTools (navigate, take_snapshot, take_screenshot for UI knowledge)
         - IF visual content would aid knowledge explanation → plan screenshot capture points
      5. NOTE: Chrome DevTools MCP is available for URL/web app targets — use take_screenshot to capture UI states that help explain features
      6. IF behavior_context.learning_folder is provided:
         - Read track/track-list.json from the learning folder to understand tracked user workflows
         - Use tracked events as SUPPLEMENTARY guidance to prioritize features and understand navigation paths
         - Review imgs/ screenshots from tracking for additional context
         - CRITICAL: Do NOT rely solely on tracked behavior — independently explore the target app
           to discover and document features the user did not interact with during tracking
    </action>
    <constraints>
      - BLOCKING: Empty directory or unreachable URL → halt with error
    </constraints>
    <output>InputAnalysis {input_type, format, app_type, app_name, source_metadata, has_behavior_context}</output>
  </step_1_1>

  <step_1_2>
    <name>Select Category</name>
    <action>
      1. Read purpose parameter from input
      2. Validate against supported categories: "user-manual", "application-reverse-engineering", "notes"
      3. Halt with error if unsupported or unknown category
    </action>
    <constraints>
      - BLOCKING: purpose not in ["user-manual", "application-reverse-engineering", "notes"] → halt listing supported categories
    </constraints>
    <output>selected_category = "{purpose}"</output>
  </step_1_2>

  <step_1_3>
    <name>Load Tool Skill</name>
    <action>
      1. Glob .github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md, filter by category
      2. Parse frontmatter, extract artifact paths (playbook, collection template, acceptance criteria)
      3. Read any available app-type mixin paths as a label-keyed map, resolve mixins by exact `app_type` then ordered `source_metadata.detected_app_types`, proceed without a mixin if no label matches, and verify all artifact paths exist
      4. Resolve detected app_type (from Step 1.1 InputAnalysis.app_type) to a mixin by calling tool skill `get_mixin` operation:
         - Pass `app_type` from InputAnalysis (e.g., "web", "cli", "mobile" for user-manual; repo-type/language-type for reverse-engineering)
         - Store returned mixin content in tool_skill_artifacts.resolved_mixin
         - IF app_type is null or unrecognized → proceed without mixin (log warning)
      5. Build tool_skill_config by merging extractor config_overrides into tool skill defaults:
         - max_files_per_section: use config_overrides value (default: 20)
         - web_search_enabled: use config_overrides value (default: true for extractor, false for tool skill — extractor value wins)
         - max_iterations: use config_overrides.max_validation_iterations (default: 3)
         - CRITICAL: tool_skill_config is passed to ALL subsequent tool skill operation calls
    </action>
    <constraints>
      - BLOCKING: 0 matching tool skills → halt with install instructions
      - CRITICAL: config_overrides MUST be resolved and passed through — tool skill defaults are overridden by extractor config
    </constraints>
    <output>loaded_tool_skill, tool_skill_artifacts {playbook_template, collection_template, acceptance_criteria, app_type_mixins, resolved_mixin}, tool_skill_config</output>
  </step_1_3>

  <step_1_4>
    <name>Initialize Handoff</name>
    <action>
      1. Determine checkpoint path: .x-ipe-checkpoint/session-{timestamp}/ in CWD
      2. Create session manifest using template (templates/checkpoint-manifest.md)
      3. Create content/, feedback/, and screenshots/ subdirectories
      4. Write initial manifest
    </action>
    <constraints>
      - BLOCKING: CWD not writable → halt
    </constraints>
    <output>.x-ipe-checkpoint/session-{timestamp}/manifest.yaml with status "initialized"</output>
  </step_1_4>
</phase_1>

<phase_2 name="审问之 — Inquire Thoroughly">
  <step_2_1>
    <name>Extract Source Content</name>
    <action>
      **Category: user-manual** (purpose == "user-manual"):
      1. Read collection template from Phase 1 artifacts, parse H2 sections with extraction prompts
      2. IF behavior_context.learning_folder is available from input:
         a. Read track/track-list.json to extract user workflow patterns and navigation sequences
         b. Use tracked events to prioritize which features/sections to explore first
         c. Reference behavior screenshots (imgs/) for understanding UI states observed during tracking
         d. CRITICAL: This is SUPPLEMENTARY guidance only — the extractor MUST still independently
            explore the target app via Chrome DevTools to discover features beyond what was tracked
      3. For each section: identify relevant sources, apply skip rules, extract/browse content
      4. Synthesize knowledge into coherent content (never raw-dump files)
      5. FOR running_web_app / public_url targets: Detect interaction patterns per element:
         - FORM, MODAL, CLI_DISPATCH, NAVIGATION, TOGGLE
         - For CLI_DISPATCH: MUST document terminal target, Enter-to-execute requirement, expected output, and completion signal
         - Record patterns in content file alongside feature descriptions
      6. Screenshot strategy for running_web_app / public_url:
         a. Section 4 (Core Features): screenshot of each feature's primary UI state
         b. Section 5 (Workflows): screenshot at EACH STEP (before-action + after-action)
         c. Section 3 (Getting Started): screenshot at key quick start steps
         d. Name: screenshots/{section_nn}-{step_nn}-{description}.png
         e. Reference in content: ![Step N: Description](screenshots/{filename})
      7. Write to checkpoint/content/section-{NN}-{slug}.md, update manifest per-section
         - CRITICAL: Content path contract — tool skill operations receive content_path as:
           `.x-ipe-checkpoint/session-{timestamp}/content/section-{NN}-{slug}.md`
           This exact path format is passed to validate_section, pack_section, and score_quality.
      8. Call tool skill validate_section operation with:
         - section_id, content_path (full path from step 7), instruction_temperature, config from tool_skill_config
         - IF behavior_context.learning_folder is available → pass as additional context for coverage-aware validation
      9. IF validation result contains criteria with status `incomplete` AND `missing_info[]` is non-empty → use `missing_info` entries to form targeted re-extraction prompts for the specific content gaps
      10. IF tool skill feedback indicates gaps → adjust extraction prompts and re-extract before moving to next section

      **Category: application-reverse-engineering** (purpose == "application-reverse-engineering"):
      1. Call loaded tool skill (x-ipe-tool-knowledge-extraction-application-reverse-engineering) `orchestrate_phases` operation with:
         - repo_path: input.target (must be a local directory)
         - output_path: `.x-ipe-checkpoint/session-{timestamp}/content/` (extractor-managed checkpoint dir)
         - config: tool_skill_config (merged from extractor config_overrides)
      2. The orchestrator handles its own 3-phase execution (Scan → Tests → Deep) via sub-skills
      3. Monitor orchestration progress; update extractor manifest as each phase completes
      4. On orchestrator completion, collect all section outputs from output_path subdirectories
      5. Map orchestrator section paths to extractor checkpoint structure:
         - orchestrator writes: `{output_path}/section-{NN}-{slug}/`
         - extractor references: `.x-ipe-checkpoint/session-{timestamp}/content/section-{NN}-{slug}/index.md`
      6. Proceed to Phase 3 validation using orchestrator's per-section quality scores as initial baseline

      **Category: notes** (purpose == "notes"):
      1. Call loaded tool skill (x-ipe-tool-knowledge-extraction-notes) `init_knowledge_folder` operation with:
         - knowledge_name: derived from input.target (sanitized slug)
         - output_dir: `.x-ipe-checkpoint/session-{timestamp}/content/`
         - template_type: inferred from source content or default "general"
      2. Call `get_template` to retrieve section layout for the chosen template_type
      3. For each template section: call `extract_section` with:
         - source_content from input.target (file, URL, or text)
         - section_id matching template numbering
         - knowledge_name and output_dir from step 1
      4. For any images/screenshots captured during extraction: call `embed_image` with:
         - image_path, section_id, image_description
      5. After all sections extracted: call `generate_overview` to produce linked table of contents
      6. Call `validate_structure` to verify folder integrity, fix any broken links
      7. Map notes folder to extractor checkpoint structure:
         - tool skill writes: `{output_dir}/{knowledge_name}/`
         - extractor references: `.x-ipe-checkpoint/session-{timestamp}/content/{knowledge_name}/overview.md`
    </action>
    <constraints>
      - BLOCKING: All content must go through file paths in checkpoint — no inline content
      - Extraction capability varies by input_type (local read vs Chrome DevTools)
      - CRITICAL: Tool skill operations MUST receive tool_skill_config (from Phase 1.3) — not tool skill defaults
    </constraints>
    <output>Content files in checkpoint/content/, manifest sections[] updated with status per section</output>
  </step_2_1>
</phase_2>

<phase_3 name="慎思之 — Think Carefully">
  <step_3_1>
    <name>Validate & Coverage Loop</name>
    <action>
      1. Call tool skill validate_section operation for each section with:
         - section_id, content_path, instruction_temperature, config from tool_skill_config
         - CRITICAL: Pass instruction_temperature so validation thresholds match extraction tone
      2. Write feedback to checkpoint/feedback/, lock accepted sections
      3. Compute coverage_ratio, check exit conditions (all met / max iterations / plateau)
      4. IF any criteria has status `incomplete` with `missing_info[]` → treat as extractable gap (not content failure). Feed `missing_info` descriptions back to Phase 2 as targeted extraction prompts
      5. Re-extract failing sections with adjusted prompts if iterations remain
    </action>
    <constraints>
      - Max iterations capped by config_overrides.max_validation_iterations (default 3)
    </constraints>
    <output>Per-section validation_status, final_coverage_ratio, exit_reason, coverage_history</output>
  </step_3_1>
</phase_3>

<phase_3_5 name="实践验证 — Validate by Practice">
  <step_3_5_1>
    <name>Walkthrough Testing</name>
    <action>
      1. APPLICABILITY: Only for input_type running_web_app or public_url (Chrome DevTools available).
         For source_code_repo / documentation_folder / single_file → SKIP this phase (use tool skill test_walkthrough in offline mode instead)
      2. Select the primary workflow scenario from Section 5 (Common Workflow Scenarios)
         - Pick the scenario most likely to be a user's first experience
         - IF no Section 5 scenario exists yet → use Section 3 Quick Start
      3. Call tool skill `test_walkthrough` operation with:
         - content_path: path to the scenario content file
         - app_url: the running app URL (from input.target)
         - mode: "live" (Chrome DevTools-based)
         - instruction_temperature: from input (affects strictness of walkthrough evaluation)
      4. Process gap_report from test_walkthrough — for each failed step, classify:
         - MISSING_ACTION: step doesn't specify what to do (e.g., "press Enter")
         - MISSING_ELEMENT: step doesn't name the UI element
         - MISSING_OUTCOME: step doesn't say what happens after
         - WRONG_STATE: actual UI doesn't match described state
         - IMPLICIT_KNOWLEDGE: step assumes knowledge not documented
      5. Feed each gap back to Phase 2 for targeted re-extraction of that section
      6. IF followability_score < 0.7 → re-extract affected sections with gap-specific prompts
      7. IF followability_score >= 0.7 → proceed to Phase 4
      8. Max 2 walkthrough iterations (test → fix → retest)
    </action>
    <constraints>
      - BLOCKING: Only runs for running_web_app / public_url input types
      - CRITICAL: Follow steps LITERALLY — do not infer or improvise
      - CRITICAL: Each gap must be traced back to a specific section for targeted re-extraction
    </constraints>
    <output>walkthrough_results: {followability_score, gaps_found, gaps_fixed, iterations_used}</output>
  </step_3_5_1>
</phase_3_5>

<phase_4 name="明辨之 — Discern Clearly">
  <step_4_1>
    <name>Resume, Checkpoint & Error Handling</name>
    <action>
      1. Cross-cutting: scan .x-ipe-checkpoint/ for resumable sessions (paused/extracting)
      2. Classify errors using tool skill error code mapping:
         **Transient errors** (retry up to config_overrides.max_retries):
         - CONTENT_NOT_FOUND → checkpoint file not yet written; retry after re-extraction
         - SCORING_FAILED → content unreadable; retry after re-write
         - SUB_SKILL_EXTRACT_FAILED → sub-skill temporary failure; retry dispatch
         **Permanent errors** (mark error, continue with remaining sections):
         - INVALID_OPERATION → wrong operation name; fix and retry once
         - MISSING_SECTION_ID → programming error in extractor; log and skip section
         - MISSING_CONTENT_PATH → section was never extracted; mark as skipped
         - INVALID_APP_TYPE → app_type detection failed; proceed without mixin
         - TEMPLATE_NOT_FOUND → tool skill installation incomplete; halt extraction
         - NO_SUB_SKILLS_FOUND → reverse-engineering sub-skills missing; halt
         - BELOW_COMPLEXITY_GATE → codebase too small for reverse-engineering; skip with note
      3. Persist manifest after every section, enforce valid state machine transitions
      4. Append to error_log[] with section_id, error_code, error_type (transient/permanent), message, retry_count, timestamp
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
    <name>Quality Scoring (Tool Skill Delegated)</name>
    <action>
      1. For each accepted section: call tool skill score_quality operation with:
         - section_id, content_path, instruction_temperature, config from tool_skill_config
         - CRITICAL: All parameters must be passed — tool skill uses instruction_temperature for threshold adjustment
      2. Tool skill returns 5 dimensions: completeness, structure, clarity, followability, freshness
      3. Aggregate per-section scores into overall_quality_score (arithmetic mean)
      4. Record `is_key_section` flag in manifest. When quality_label is 'low', prioritize re-extraction of sections where `is_key_section` is true. Use `improvement_hints[]` as re-extraction guidance.
      5. Classify: ≥ 0.80 → "high"; 0.50–0.79 → "acceptable"; < 0.50 → "low"
      6. IF quality_label is "low" → loop back to Phase 2 for re-extraction of lowest-scoring sections (max 1 quality loop)
    </action>
    <constraints>
      - BLOCKING: Quality scoring MUST be delegated to tool skill — extractor does NOT self-score
      - If tool skill lacks score_quality operation → fall back to validate_section pass-rate as proxy
    </constraints>
    <output>phase_5.quality_scores[], overall_quality_score, quality_label, quality_loop_triggered</output>
  </step_5_1>

  <step_5_2>
    <name>Package KB Articles & Report</name>
    <action>
      1. Derive `extraction_id` from InputAnalysis: `{app_name}-{selected_category}` (e.g., `x-ipe-user-manual`)
         - Use `source_metadata.app_name` (slugified in Phase 1.1) + selected_category
         - IF user provided a scope/focus in their request → include it: `{app_name}-{scope}-{category}` (e.g., `x-ipe-workflow-mode-user-manual`)
         - IF folder already exists → append `-{N}` suffix (e.g., `x-ipe-user-manual-2`)
      2. Create x-ipe-docs/knowledge-base/.intake/{extraction_id}/
      3. Write article .md files for accepted sections with YAML frontmatter
      4. Generate extraction_report.md (summary, scores, validation stats, error log, provenance)
    </action>
    <constraints>
      - All files UTF-8, no BOM
      - No index file generated — downstream skills (e.g., KB librarian) own indexing
    </constraints>
    <output>.intake/ folder with article files and extraction_report.md</output>
  </step_5_2>

  <step_5_3>
    <name>Deep Research Iteration</name>
    <action>
      1. Read `deep_research.rounds` from input and `current_round` from manifest (default: 1)
      2. IF rounds == 1 → skip (single-pass, backward-compatible); proceed to Phase 6
      3. Build **coverage inventory**: list documented features/UI/APIs vs total discoverable items
         - Compute `coverage_pct` = (documented / total) × 100
      4. **Exit conditions** (any triggers exit → proceed to Phase 6):
         - Numeric mode: `current_round >= rounds`
         - Smart mode: `coverage_pct >= 100%` OR `coverage_pct == previous_round` (plateau)
      5. **Prepare next round** (if continuing):
         a. Generate gap analysis targeting only undocumented areas
         b. Update manifest: increment current_round, store coverage_pct
         c. **Loop back to Phase 2** with gap-targeted prompts; Phases 2→3→3.5→4→5.1→5.2 run on new content
         d. New findings merge additively into existing .intake/ articles
         e. Return to Step 5.3 for next iteration
    </action>
    <constraints>
      - BLOCKING: Each round MUST add new content; stagnant rounds → forced exit
      - Max 10 rounds regardless of mode (safety cap)
      - Prior round content is READ-ONLY during gap analysis
    </constraints>
    <output>deep_research_summary { total_rounds_executed, final_coverage_pct, gap_analysis_per_round[] }</output>
  </step_5_3>
</phase_5>

<phase_6 name="继续执行 — Route and Execute">
  <step_6_1>
    <name>Finalize & Clean Up</name>
    <action>
      1. Update manifest: status → "complete", completed_at → ISO 8601
      2. Populate Output Result with extraction_status, quality_score, quality_label, kb_output_path
      3. Clean up session: IF success/partial → remove entire session folder (all output already in .intake/); IF failed → preserve for debugging
      4. Update task-board.md → completed
    </action>
    <constraints>
      - On success: remove entire .x-ipe-checkpoint/session-{timestamp}/ (output is in .intake/)
      - On failure: preserve session folder for debugging
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
    - ".x-ipe-checkpoint/session-{timestamp}/"
    - "x-ipe-docs/knowledge-base/.intake/{extraction_id}/"

  # Dynamic outputs — schemas and examples in references/output-schemas.md
  input_analysis: { input_type, format, app_type, app_name, source_metadata }
  selected_category: "user-manual"
  loaded_tool_skill: "x-ipe-tool-knowledge-extraction-{category} | null"
  checkpoint_path: ".x-ipe-checkpoint/session-{timestamp}/"
  extraction_id: "{app_name}-{category}"  # e.g., "x-ipe-user-manual", "x-ipe-workflow-mode-user-manual"
  extraction_summary: { sections_extracted, sections_skipped, sections_error }
  validation_summary: { final_coverage_ratio, exit_reason, sections_accepted }
  error_summary: { total_errors, transient_retried, permanent_halted }
  deep_research_summary: { total_rounds_executed, final_coverage_pct, gap_analysis_per_round[] }
  extraction_status: "complete | partial | failed"
  quality_score: 0.0  # 0.0–1.0
  quality_label: "high | acceptable | low"
  kb_output_path: "x-ipe-docs/knowledge-base/.intake/{extraction_id}/"
```

REFERENCE: See `references/output-schemas.md` for full dynamic output schemas with field types and examples.

---

## Definition of Done (DoD)

<definition_of_done>
  <checkpoint required="true">
    <name>Phases 1-4 Complete</name>
    <verification>Input analyzed, content extracted, validation loop run, walkthrough tested (if applicable), checkpoints saved</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Phase 5 Complete</name>
    <verification>Quality scores computed (5 dimensions), articles packaged in .intake/, extraction report generated</verification>
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
2. **File-Based Handoff:** Use `.x-ipe-checkpoint/` for all knowledge exchange; never inline content
3. **Fail Fast:** Halt when tool skill not found or target not accessible
4. **Synthesize, Don't Dump:** Extract and organize — never raw-copy files into content
5. **Section-by-Section:** Follow collection template order; one content file per section
6. **Walkthrough Test:** For running apps, follow the manual literally to find gaps before packaging

### ❌ Don't Do This
1. **Inline Content Exchange:** Passing content directly in YAML instead of file paths
2. **Raw File Dumps:** Copying file contents verbatim without synthesis
3. **Checkpoint Inside Target:** Creating `.x-ipe-checkpoint/` inside target directory instead of CWD
4. **Multi-Category Parallel:** Attempting multiple extraction categories in one session
5. **Implicit Knowledge:** Assuming the reader knows to press Enter, click a specific button, etc. without documenting it
---

## Examples

For detailed execution examples, see: `references/examples.md`
