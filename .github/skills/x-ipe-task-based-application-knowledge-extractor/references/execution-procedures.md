# Execution Procedures — Detailed Step Reference

> This file contains the detailed CONTEXT/DECISION/ACTION/VERIFY blocks for each step.
> The main SKILL.md contains condensed action summaries; refer here for full execution detail.

---

## Phase 1: 博学之 — Study Broadly

### Step 1.1 — Analyze Input

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
- Detect one or more source format labels from file extensions, MIME hints, or content signatures; store a concise summary in `format` and preserve the full set in `source_metadata.detected_formats`
- Detect one or more application-context labels from framework markers, runtime clues, and entry points; store a concise summary in `app_type` and preserve the full set in `source_metadata.detected_app_types`
- Collect source_metadata: primary_language, framework, file_count, total_size_bytes, entry_points, has_docs

**ACTION — Plan Extraction Techniques:**
- Based on input_type, plan which tools are available:
  - `source_code_repo` / `documentation_folder` → grep, glob, file reading, code analysis
  - `public_url` / `running_web_app` → Chrome DevTools MCP (navigate_page, take_snapshot, take_screenshot)
  - `single_file` → direct file read
- IF input_type involves UI → plan screenshot capture points (login screens, dashboards, key workflows)
- IF images can aid knowledge explanation → mark sections for screenshot capture in manifest
- Store planned techniques in `source_metadata.extraction_techniques[]`

**VERIFY:** ✅ InputAnalysis created with input_type, format, app_type, source_metadata

**REFERENCE:** `references/input-detection-heuristics.md`, `templates/input-analysis-output.md`

---

### Step 1.2 — Select Category

**CONTEXT:** Read purpose parameter, check against v1-supported categories.

**DECISION — Category Selection (v1):**
- IF purpose == "user-manual" → selected_category = "user-manual"
- IF purpose in ["API-reference", "architecture", "runbook", "configuration"] → halt: "Not supported in v1"
- ELSE → halt: "Unknown category"

**VERIFY:** ✅ selected_category is "user-manual"

**REFERENCE:** `references/category-taxonomy.md`

---

### Step 1.3 — Load Tool Skill

**CONTEXT:** Glob `.github/skills/x-ipe-tool-knowledge-extraction-*/SKILL.md`, filter by category.

**DECISION:** 0 matches → halt (install tool skill); 1 match → load; multiple → filter by frontmatter category.

**ACTION — Load Tool Skill:**
- Read SKILL.md, parse frontmatter (name, categories)
- Extract artifact paths: playbook_template, collection_template, acceptance_criteria
- Read app-type mixin paths as a label-keyed map of optional overrides
- Resolve applicable mixins by exact `app_type`, then `source_metadata.detected_app_types` order, and fall back to the base template when no key matches
- Verify artifact paths exist

**VERIFY:** ✅ loaded_tool_skill set, artifact paths exist, supports "user-manual"

**REFERENCE:** `references/handoff-protocol.md`

---

### Step 1.4 — Initialize Handoff

**CONTEXT:** Determine checkpoint path `.x-ipe-checkpoint/session-{timestamp}/` in CWD.

**DECISION:** If path exists → create new timestamped subfolder; else → create it.

**ACTION — Create Session Manifest:**
- Create directory structure: `manifest.yaml`, `content/`, `feedback/`
- Write manifest using template (`templates/checkpoint-manifest.md`)
- Fields: schema_version, session_id, created_at, target, purpose, input_analysis, selected_category, loaded_tool_skill, status ("initialized")

**VERIFY:** ✅ Checkpoint dir exists, manifest.yaml written with status "initialized"

**REFERENCE:** `references/handoff-protocol.md`, `templates/checkpoint-manifest.md`

---

## Phase 2: 审问之 — Inquire Thoroughly

### Step 2.1 — Extract Source Content

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
5. Screenshots: user-provided first → Chrome DevTools auto-capture → graceful skip. Save all screenshots to `{checkpoint_path}/screenshots/` (session-scoped, not flat).
6. IF `config_overrides.web_search_enabled`: augment with purpose-driven search (supplementary only)
7. Write to `{checkpoint_path}/content/section-{NN}-{slug}.md` (see reference for format)
8. Update `manifest.yaml` with section result (status, content_file, files_read, warnings, timestamps)
9. **Tool Skill Early Feedback:** After writing each section, call loaded tool skill's `validate_section` operation:
   - Pass section_id and content_file_path
   - Read feedback: if criteria failures indicate missing content → adjust prompts and re-extract BEFORE moving to next section
   - Check for `incomplete` criteria and `missing_info[]`. If present, adjust extraction prompts to specifically target the missing content described in `missing_info` entries.
   - Write early feedback to `{checkpoint_path}/feedback/section-{NN}-{slug}-early.md`
   - This reduces Phase 3 iteration count by catching gaps early

**VERIFY:**
- ✅ All template sections processed (each has status: extracted | skipped | empty | error | partial)
- ✅ Content files exist in `{checkpoint_path}/content/` for each extracted section
- ✅ Manifest updated per-section with status, content_file, files_read, warnings, timestamps
- ✅ Phase 2 overall status in manifest is "phase_2_complete"
- ✅ All content via file paths in checkpoint — no inline content

**REFERENCE:**
- Extraction heuristics: `references/extraction-engine-heuristics.md`
- Handoff protocol: `references/handoff-protocol.md`

---

## Phase 3: 慎思之 — Think Carefully

### Step 3.1 — Validate & Iterate

**CONTEXT:** Read `tool_skill_artifacts.acceptance_criteria` from Phase 1. Load Phase 2 content from manifest. Config: `max_validation_iterations` (default 3), `coverage_target` (default 0.8). Update manifest: phase_3.status → "in_progress".

**DECISION — Exit Conditions (checked per iteration):**
- All sections accepted → exit "all_criteria_met"
- iterations ≥ max → exit "max_iterations_reached"
- coverage_ratio not improving (iteration > 1) → exit "plateau_detected"
- No content from Phase 2 → skip Phase 3 entirely
- IF any criteria has status `incomplete` with `missing_info[]` → treat as extractable gap (not content failure). Feed `missing_info` descriptions back to Phase 2 as targeted extraction prompts.

**ACTION — Iteration Loop (up to max_validation_iterations):**
1. Call tool skill's validate_section operation for each non-accepted section — tool skill evaluates per-criterion pass/fail; extractor does NOT self-validate against criteria
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

## Phase 3.5: 实践验证 — Validate by Practice

### Step 3.5.1 — Walkthrough Testing

**CONTEXT:** After Phase 3 validates content against acceptance criteria (structural completeness), Phase 3.5 validates that the content is actually *followable* by walking through the running application step-by-step. This phase only applies to `running_web_app` and `public_url` input types where Chrome DevTools is available.

**DECISION — Applicability Gate:**
- IF input_type == "running_web_app" OR input_type == "public_url" → proceed with live walkthrough
- IF input_type == "source_code_repo" OR "documentation_folder" OR "single_file" → SKIP this phase entirely (use tool skill `test_walkthrough` in `offline` mode within Phase 3 instead)

**DECISION — Scenario Selection:**
- IF Section 5 (Common Workflow Scenarios) exists and has content → select the scenario most likely to be a user's first experience (e.g., "Building a New Application")
- IF no Section 5 → fall back to Section 3 (Quick Start / Getting Started)
- IF neither exists → SKIP phase with warning: "No walkthrough scenario available"

**ACTION — Walkthrough Test Loop (max 2 iterations):**
1. Read the selected scenario content file from `{checkpoint_path}/content/`
2. Call tool skill `test_walkthrough` operation:
   - `content_path`: path to the scenario content file
   - `app_url`: the running app URL (from `input.target`)
   - `mode`: "live" (Chrome DevTools-based)
3. Process `gap_report` from tool skill response. For each failed step, classify:
   - **MISSING_ACTION:** Step doesn't specify what to do (e.g., "press Enter to execute", "click Submit")
   - **MISSING_ELEMENT:** Step doesn't name the UI element (e.g., "the button" instead of "the 'Create Project' button")
   - **MISSING_OUTCOME:** Step doesn't say what happens after (e.g., no "you should see..." confirmation)
   - **WRONG_STATE:** Actual UI doesn't match described state (e.g., element not found, different layout)
   - **IMPLICIT_KNOWLEDGE:** Step assumes knowledge not documented (e.g., terminal conventions, keyboard shortcuts)
4. For each gap: trace back to the specific section and location in the content file
5. Feed gaps back to Phase 2 for targeted re-extraction of affected sections:
   - Build gap-specific prompts (e.g., "CLI_DISPATCH interaction at step 4 missing: user must press Enter to execute the command. Document what the terminal shows and how to confirm completion.")
   - Re-extract only the affected sections, preserving accepted content
6. Check followability_score from gap_report:
   - IF `followability_score >= 0.7` → proceed to Phase 4
   - IF `followability_score < 0.7` AND iteration < 2 → re-extract and retest
   - IF `followability_score < 0.7` AND iteration == 2 → proceed with warning

**VERIFY:**
- ✅ Walkthrough test executed against running application (or skipped for offline input types)
- ✅ All gaps classified and traced to specific sections
- ✅ Affected sections re-extracted with gap-specific prompts (if gaps found)
- ✅ `walkthrough_results` recorded: followability_score, gaps_found, gaps_fixed, iterations_used

**REFERENCE:** `references/validation-loop-heuristics.md` (Walkthrough Testing section)

---

## Phase 4: 明辨之 — Discern Clearly

### Step 4.1 — Resume, Checkpoint & Error Handling

**CONTEXT — Cross-Cutting Behavior:** Phase 4 wraps Phases 1–3.5 (not sequential). On invocation: scan `.x-ipe-checkpoint/session-*/manifest.yaml` sorted by timestamp desc; select most recent with status "paused"|"extracting". If valid → resume (skip accepted sections). If corrupted (YAML parse fail or schema_version ≠ "1.0") → log warning, start fresh. Config: `max_retries` (default 3 total attempts).

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

## Phase 5: 笃行之 — Practice Earnestly

### Step 5.1 — Quality Scoring (Tool Skill Delegated)

**CONTEXT:** Quality assessment is delegated to the tool skill because it has domain expertise on what constitutes good content for the extraction category.

**DECISION — Score Source:**
- IF tool skill has `score_quality` operation → call it for each section
- IF tool skill lacks `score_quality` → fall back to validate_section pass-rate as proxy score (criteria_met / criteria_total)

**ACTION — Delegate Quality Scoring:**
1. For each accepted section: call tool skill `score_quality` operation with section content path and section_id
2. Collect per-section scores from tool skill response — tool skill now returns 5 dimensions: completeness, structure, clarity, followability, freshness
3. Log `is_key_section` in per-section manifest entry. When deciding which sections to re-extract, prioritize `is_key_section: true` sections. Pass `improvement_hints[]` as context to Phase 2 for targeted improvement.
4. Compute `overall_quality_score` = arithmetic mean of section scores (exclude error/skipped; count as 0.0)
4. Classify: ≥ 0.80 → "high"; 0.50–0.79 → "acceptable"; < 0.50 → "low"
5. IF quality_label is "low" AND quality_loop not already triggered:
   - Set quality_loop_triggered = true
   - Identify lowest-scoring sections (below 0.50)
   - Loop back to Phase 2 Step 2.1 for targeted re-extraction of those sections
   - After re-extraction, re-run Phase 3 validation, then return here for re-scoring
6. Write quality results to manifest: phase_5.quality_scores[], overall_quality_score, quality_label

**VERIFY:** ✅ Every section has quality score from tool skill (or proxy); overall score and label set; quality loop triggered if "low"

**REFERENCE:** Tool skill's `score_quality` operation documentation

---

### Step 5.2 — Package KB Articles & Report

**CONTEXT:** Read all packed content files from `.x-ipe-checkpoint/session-{timestamp}/packed/`. Read quality scores from Step 5.1. Read manifest for provenance data (target, loaded_tool_skill, timestamps). Derive `extraction_id` from `source_metadata.app_name` + `selected_category`: format as `{app_name}-{category}` (e.g., `x-ipe-user-manual`). If user provided a scope/focus, include it: `{app_name}-{scope}-{category}` (e.g., `x-ipe-workflow-mode-user-manual`). If folder already exists, append `-{N}` suffix.

**DECISION — Determine Output Path & Status:**
- Output folder: `x-ipe-docs/knowledge-base/.intake/{extraction_id}/` (e.g., `.intake/x-ipe-user-manual/`)
- IF zero accepted sections → extraction_status = "failed" (still generate report)
- IF all accepted → extraction_status = "complete"
- IF some accepted, some error/skipped → extraction_status = "partial"

**ACTION — Write Output Files:**
1. Create output folder (and `.intake/` parent if needed)
2. For each accepted section: write article `.md` with YAML frontmatter (section_id, title, quality_score, quality_dimensions, provenance) + validated content from packed files
3. For error/skipped sections: no article file generated
4. Generate `extraction_report.md`: Summary, Per-Section Scores (sorted quality ascending), Validation Statistics, Error Log, Provenance
5. All files UTF-8, no BOM

**VERIFY:**
- ✅ Article count matches accepted sections
- ✅ `extraction_report.md` exists with 5 sections; per-section table sorted ascending

**REFERENCE:** `references/output-quality-heuristics.md` §4–§7

---

### Step 5.3 — Deep Research Iteration

**CONTEXT:** Read `deep_research.rounds` from input parameters and `current_round` from manifest (defaults to 1 if not set). Read all accepted section content from `.intake/{extraction_id}/` as the baseline knowledge.

**DECISION — Continue or Exit:**
- IF `rounds == 1` → **SKIP** this step entirely (single-pass mode, backward-compatible)
- IF `rounds` is numeric AND `current_round >= rounds` → **EXIT** loop, proceed to Phase 6
- IF `rounds == "smart"` AND `coverage_pct >= 100%` → **EXIT** loop (full coverage achieved)
- IF `rounds == "smart"` AND `coverage_pct == previous_round_coverage_pct` → **EXIT** loop (plateau, no progress)
- OTHERWISE → **CONTINUE** to next round

**ACTION — Build Coverage Inventory:**
1. Parse all extracted content to enumerate documented items:
   - Features/functions documented (from Section 4 files)
   - Workflows/scenarios covered (from Section 5 files)
   - UI elements/pages visited (from screenshots + Section 3)
   - API endpoints/settings documented (from Sections 6, 8)
2. Discover total available items from the target application:
   - For web apps: crawl navigation, list all menu items, count unique routes/pages
   - For source repos: grep for exported functions, CLI commands, config options
   - For documentation: count TOC entries, linked pages
3. Compute `coverage_pct = (documented_items / total_discoverable_items) × 100`
4. Generate gap analysis: list specific undocumented areas with exploration hints

**ACTION — Prepare Next Round:**
1. Create targeted extraction prompts focusing ONLY on gaps (avoid re-extracting covered content)
2. Mark sections needing expansion (e.g., "Section 4 has 5/9 features")
3. Update manifest: increment `current_round`, store `coverage_pct`, append `gap_analysis`
4. **Loop back to Phase 2 (Step 2.1)** with:
   - Existing content as READ-ONLY context
   - Gap-targeted extraction prompts
   - Clear instruction: "Explore ONLY these undocumented areas: [list]"
5. Phases 2→3→3.5→4→5.1→5.2 run on new content; new findings are **merged** into existing `.intake/` articles
6. Return to Step 5.3 for next iteration check

**VERIFY:**
- ✅ Each round adds measurable new content (stagnant rounds → forced exit)
- ✅ `current_round` never exceeds 10 (safety cap)
- ✅ Coverage inventory is reproducible between rounds
- ✅ Manifest tracks per-round: `{ round_number, coverage_pct, items_added, gap_summary }`

---

## Phase 6: 继续执行 — Continue Execution

### Step 6.1 — Finalize & Clean Up

**ACTION:**
1. Update manifest: `status` → "complete", `completed_at` → ISO 8601
2. Populate Output Result: `extraction_status`, `quality_score`, `quality_label`, `kb_output_path`
3. Set `task_output_links[]`: extraction_report.md, manifest paths
4. Update task-board.md → completed
5. IF extraction_status == "complete" or "partial":
   - Remove ENTIRE session folder `{checkpoint_path}` (manifest, content, feedback, screenshots, packed — all)
   - Rationale: all useful output is already in `.intake/{extraction_id}/`; checkpoint was temporary
6. IF extraction_status == "failed":
   - Preserve session folder for debugging (do NOT remove)
   - Log: "Session preserved for debugging at {checkpoint_path}"

**VERIFY:** ✅ Manifest "complete"; Output Result populated; session folder removed on success OR preserved on failure

---

### Step 6.2 — Route Next Action

**DECISION:** DAO mode → log completion, future: invoke `x-ipe-tool-kb-librarian`; manual → present to human.
