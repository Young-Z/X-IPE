# X-IPE Knowledge-Base-Implementation Workflow: Skills & State

**Generated:** 2026-03-11

---

## 1. DAO SKILL FILE
**Location:** `.github/skills/x-ipe-dao-end-user-representative/SKILL.md`

### Purpose
Represent human intent at end-user-facing touchpoints as an autonomous human representative. Acts as a fallback when an agent needs human-like guidance (clarification, critique, instruction, approval-like, or pass-through).

### Key Concepts
- **7 Dispositions:** `answer | clarification | reframe | critique | instruction | approval | pass_through`
- **Core Backbone:** 格物致知 (investigate → reach understanding) — internal two-phase cognitive framework
- **Instruction Units:** Returns 1–3 independent units per message
- **Autonomous by Default:** Can answer, clarify, reframe, critique, instruct, or approve WITHOUT waiting for human

### Execution Flow (5 Phases)

| Phase | Step | Name | Action | Gate |
|-------|------|------|--------|------|
| 0 | 0.1 | 礼 — Greet | Announce identity as '道' | Greeting delivered |
| 1 | 1.1–1.3 | 格物 — Investigate | Restate need, decompose compound, three perspectives, assess environment | Context gathered + units identified |
| 2 | 2.1–2.4 | 致知 — Reach Understanding | Per unit: scan skills, weigh dispositions, validate, commit | One disposition per unit committed |
| 3 | 3.1 | 录 — Record | Write semantic log entry (all units) | Log written |
| 4 | 4.1 | 示 — Present | Format CLI output (all units) | Output delivered |

### Input Parameters
```yaml
input:
  message_context:
    source: "human | ai"                     # Required
    calling_skill: "{skill name}"            # Optional
    task_id: "{TASK-XXX}"                    # Required
    feature_id: "{FEATURE-XXX | N/A}"        # Optional, default: N/A
    workflow_name: "{name | N/A}"            # Required
    downstream_context: "target agent/task context or N/A"
    messages:
      - content: "raw user-facing message"
        preferred_dispositions: [...]         # Optional
  human_shadow: false                         # Standalone, default: false
```

### Output Structure
```yaml
operation_output:
  success: true | false
  result:
    instruction_units:
      - disposition: "answer | clarification | reframe | critique | instruction | approval | pass_through"
        content: "bounded response for this instruction unit"
        rationale_summary: "brief explanation of why this disposition was chosen"
        suggested_skills:
          - skill_name: "x-ipe-task-based-{name}"
            match_strength: "strong | partial"
            reason: "why this skill matches this unit"
            execution_steps: [...]
    confidence: 0.0                # minimum confidence across all units
    fallback_required: false
    execution_strategy:
      interaction_mode: "dao-represent-human-to-interact | interact-with-human | dao-represent-human-to-interact-for-questions-in-skill"
  errors: []
```

### Critical Rules
- **BLOCKING:** All 5 phases in order 0→1→2→3→4. No skipping.
- **One disposition PER unit** — max 3 units per message
- **Bounded responses** — do NOT expose full inner reasoning
- **Fallback only if needed** — `fallback_required: true` ONLY if `human_shadow: true` AND confidence < threshold
- **Best-Model Requirement:** Delegation MUST use premium LLM (e.g., `claude-opus-4.6`)

### When to Use
- Triggers: `"represent human intent"`, `"human representative guidance"`, `"approval-like guidance"`
- NOT for: long-term memory retrieval or persistence

### Error Handling
| Error | Cause | Resolution |
|-------|-------|------------|
| `DAO_INPUT_INVALID` | Missing message content, missing source, or invalid source value | Provide message_context with source and at least one message with content |
| `DAO_DISPOSITION_UNCLEAR` | Competing dispositions remain equally plausible | Prefer `clarification` or `pass_through`, or enable human-shadow fallback |
| `DAO_HUMAN_SHADOW_REQUIRED` | Internal confidence below threshold while human-shadow enabled | Route touchpoint to real human before irreversible action |

---

## 2. FEATURE-CLOSING SKILL FILE
**Location:** `.github/skills/x-ipe-task-based-feature-closing/SKILL.md`

### Purpose
Close a completed feature and ship it by:
1. Verifying all acceptance criteria are met
2. Reviewing code to sync documentation artifacts (specification, technical design, tests)
3. Updating project files (e.g., README) if needed
4. Running refactoring analysis scoped to the feature
5. Creating a pull request with proper description
6. Outputting completion summary with refactoring recommendations

### Important Notes
- **BLOCKING:** Single Feature Only. Do NOT batch multiple features.
- **Learn First:** Must understand `x-ipe-workflow-task-execution` before executing this skill.
- **Interaction Mode:** When `process_preference.interaction_mode == "dao-represent-human-to-interact"`, NEVER stop to ask human. Instead, call `x-ipe-dao-end-user-representative`.

### Input Parameters
```yaml
input:
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-feature-closing"
  execution_mode: "free-mode | workflow-mode"
  workflow:
    name: "N/A"
    extra_context_reference:
      specification: "path | N/A | auto-detect"
      refactor-report: "path | N/A | auto-detect"
  category: "feature-stage"
  process_preference:
    interaction_mode: "{from input}"
  feature_phase: "Feature Closing"
  feature_id: "{FEATURE-XXX}"
  feature_title: "{title}"
  feature_version: "{version}"
  git_strategy: "main-branch-only | dev-session-based"
  git_main_branch: "{auto-detected}"
  git_dev_branch: "dev/{git_user_name}"
  specification_path: "x-ipe-docs/features/{FEATURE-XXX}/specification.md"
  test_results: "all passing"
```

### Execution Flow (6 Phases)

| Phase | Steps | Action | Gate |
|-------|-------|--------|------|
| 1. 博学之 — Study Broadly | 1.1 | Verify all acceptance criteria are met | All criteria met |
| 2. 审问之 — Inquire Thoroughly | 2.1 | Subagent reviews code against spec, design, tests | Review complete |
| 3. 慎思之 — Think Carefully | 3.1, 3.2 | Update project files, run refactoring analysis | Files updated, analysis complete |
| 4. 明辨之 — Discern Clearly | 4.1 | Push to main or create PR based on git strategy | Shipped |
| 5. 笃行之 — Practice Earnestly | 5.1 | Output completion summary with refactoring recommendations | Summary delivered |
| 6. 继续执行 — Continue Execute | 6.1, 6.2 | Decide next action and execute | Next action started |

### Key Steps

**Step 1.1: Verify Acceptance Criteria**
- Read acceptance criteria from feature specification
- Check each criterion against implementation
- If Technical Scope includes [Frontend]/[Full Stack]: verify UI against mockups
- Document verification results in table format
- FLAG any unmet criteria (BLOCKING)

**Step 2.1: Code-to-Docs Review**
- Launch sub-agent to perform constructive critique
- Compare code against specification, technical design, test cases
- Identify behavioral differences, missing coverage, stale references
- Apply necessary updates to sync docs with code
- NOTE: Do NOT change implementation code in this step

**Step 3.1: Update Project Files**
- Update README if feature is user-facing
- Update API docs if endpoints added/changed
- Ensure complex logic has code comments
- Verify all feature doc artifacts present in `x-ipe-docs/features/{FEATURE-XXX}/`

**Step 3.2: Refactoring Analysis**
- Launch sub-agent to execute `x-ipe-tool-refactoring-analysis` with feature scope
- Collect overall_quality_score, refactoring_suggestion, key gaps
- Store analysis result for inclusion in summary
- NOTE: Analysis only — do NOT execute any refactoring

**Step 4.1: Create Pull Request (conditional)**

*IF git_strategy == "main-branch-only":*
- Do NOT create branches
- Ensure on {git_main_branch}
- Stage and commit remaining changes
- Push to main
- Skip PR creation — no PR needed
- Log: "Strategy is main-branch-only — pushed directly to main"

*IF git_strategy == "dev-session-based":*
- Resolve dev branch: `dev/{sanitized_git_user_name}`
- Stage all feature changes
- Push dev branch to remote
- Create PR from dev branch → main
- Use PR template
- Title format: `feat: [Feature Name] - [Brief Description]`
- Link feature ID and design doc
- Include testing checklist status

### Output Result
```yaml
task_completion_output:
  category: "feature-stage"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-user-manual"
      condition: "Document the completed feature"
    - skill: "x-ipe-task-based-feature-refinement"
      condition: "Start next feature from backlog"
  process_preference:
    interaction_mode: "{from input}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  task_output_links:
    - "{PR link (dev-session-based) or 'pushed to main' (main-branch-only)}"
    - "x-ipe-docs/features/{FEATURE-XXX}/"
    - "x-ipe-docs/refactoring/analysis-{task_id}.md"
  feature_id: "{FEATURE-XXX}"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Feature Closing"
  refactoring_analysis:
    overall_quality_score: "{1-10}"
    refactoring_recommended: "true | false"
    top_suggestions: ["{summary of key suggestions}"]
```

### Definition of Done (Sub-Agent Validated)
1. ✅ Acceptance criteria verified with evidence
2. ✅ Code-to-docs review completed by sub-agent
3. ✅ Project files updated
4. ✅ Refactoring analysis completed
5. ✅ PR created or code pushed to main (per git_strategy)
6. ✅ Summary with refactoring recommendation presented

### Critical Constraints
- **BLOCKING (dev-session-based):** PR description must not be empty
- **CRITICAL:** PR scoped to single feature only
- **CRITICAL (dev-session-based):** Branch name MUST use git user identity, NOT agent nickname
- **BLOCKING (main-branch-only):** Do NOT create branches or PRs

---

## 3. DECISIONS MADE — ACCEPTANCE TEST
**Location:** `x-ipe-docs/dao/26-03-11/decisions_made_acceptance_test.md`

### DAO-039: Revert skip & re-execute acceptance testing for FEATURE-049-A

| Field | Value |
|-------|-------|
| **Decision ID** | DAO-039 |
| **Timestamp** | 2026-03-11T11:15:00Z |
| **Source** | human |
| **Calling Skill** | x-ipe-task-based-feature-acceptance-test |
| **Task ID** | TASK-838 |
| **Feature ID** | FEATURE-049-A |
| **Workflow** | Knowledge-Base-Implementation |
| **Disposition** | `instruction` |
| **Confidence** | 0.95 |

### Context
The human updated `.github/skills/x-ipe-task-based-feature-acceptance-test/SKILL.md` to support ALL feature types (`frontend-ui`, `backend-api`, `unit`, `integration`), replacing old logic that skipped backend-only features. Agent had set FEATURE-049-A `acceptance_testing → skipped` under old rule. Human directed: *"I have updated ac test scope, now you shall continue."*

### Decision
1. **Revert** workflow action `acceptance_testing` for FEATURE-049-A from `skipped` → `pending`
2. **Instruct** downstream agent to invoke `x-ipe-task-based-feature-acceptance-test` for FEATURE-049-A using updated skill definition
3. Updated skill will classify all 11 AC groups (40+ individual ACs) by test type and route to appropriate testing tools per `tools.json` config

### Rationale
- Human gave explicit directive — no ambiguity
- FEATURE-049-A is foundation feature (12 REST endpoints, 11 AC groups); skipping acceptance testing leaves all downstream features (B–G) on unvalidated base
- Updated skill now correctly handles backend-api testing via classification and tool routing
- Workflow integrity requires correcting stale state when governing rules change

### Perspectives Considered
| Perspective | Position | Weight |
|-------------|----------|--------|
| QA advocate (supporting) | Backend foundation must be tested; 40+ ACs unvalidated | High |
| Velocity advocate (opposing) | Adds testing cycle; but human explicitly directed it | Low (overruled) |
| Process expert (neutral) | `skipped → pending` is valid transition; rules changed | Neutral-positive |

### Workflow Action Taken
- `update_workflow_action(workflow=Knowledge-Base-Implementation, feature=FEATURE-049-A, action=acceptance_testing, status=pending)` — ✅ Success

---

## 4. REFACTORING-ANALYSIS TOOL SKILL FILE
**Location:** `.github/skills/x-ipe-tool-refactoring-analysis/SKILL.md`

### Purpose
Analyze refactoring scope and evaluate code quality across 5 dimensions:
1. Check existing quality baseline
2. Parse and iteratively expand scope via dependency analysis
3. Evaluate quality across 5 perspectives (requirements, features, tech spec, tests, tracing)
4. Generate actionable refactoring suggestions with applicable principles

### Important Notes
- **BLOCKING:** Tool skill — performs analysis only, NO task board interaction
- **CRITICAL:** Called by `x-ipe-task-based-code-refactor` as Step 1 of refactoring workflow

### Key Concepts
- **Scope Expansion:** Iteratively discover related files via imports, shared interfaces, coupling
- **Quality Perspectives:** 5 dimensions: requirements, features, tech spec, test coverage, tracing
- **Gap Analysis:** Categorized gaps (undocumented, unimplemented, deviated, missing, etc.)

### Input Parameters
```yaml
input:
  operation: "full_analysis"
  scope:
    scope_level: "feature | custom"
    feature_id: "{FEATURE-XXX}"             # required when scope_level=feature
    refactoring_purpose: "<why refactoring is needed>"
    files: []                                # optional when scope_level=feature (auto-resolved)
    modules: []                              # optional when scope_level=feature (auto-resolved)
    description: "<user's refactoring intent>"
  quality_baseline_path: "x-ipe-docs/planning/project-quality-evaluation.md"
```

### Operation: Full Analysis

**Phase 1 — Baseline Check:**
- Check for quality evaluation at quality_baseline_path
- If exists: READ report, EXTRACT baseline data (scores, violations, gaps)
- If not exists: SET quality_baseline.exists = false

**Phase 2 — Parse & Expand Scope:**
- IF scope_level == "feature": RESOLVE feature artifacts, POPULATE files[] and modules[]
- VALIDATE scope (files exist, modules identifiable)
- **SCOPE EXPANSION LOOP** (max 10 iterations):
  - FOR EACH file: ANALYZE imports/dependencies
  - FOR EACH module: IDENTIFY sibling/parent/child modules, assess coupling
  - REFLECT: hidden dependencies, config files, test files
  - LOG expansion (iteration, files added, reason)
  - REPEAT until no new items OR iteration > 10

**Phase 3 — Evaluate Quality (5 Perspectives):**
- **3a. Requirements:** SEARCH `x-ipe-docs/requirements/**/*.md`, compare with code, identify gaps
  - Gap types: `undocumented | unimplemented | deviated`
- **3b. Features:** READ specification.md, compare behavior, identify gaps
  - Gap types: `missing | extra | deviated`
- **3c. Tech Spec:** READ technical-design.md, compare structure/interfaces/patterns
  - Gap types: `structure | interface | data_model | pattern`
- **3d. Test Coverage:** RUN coverage tool, analyze line/branch coverage
  - Gap types: `business_logic | error_handling | edge_case`
- **3e. Tracing:** SCAN for @x_ipe_tracing decorators, check coverage and redaction
  - Gap types: `untraced | unredacted | wrong_level`
- **CRITICAL:** Evaluate ALL 5 perspectives even if docs missing (set status: not_found)

**Phase 4 — Generate Suggestions:**
- CONSULT TOOL SKILLS (config-filtered):
  - DISCOVER: Scan `.github/skills/x-ipe-tool-implementation-*/` for available tools
  - READ CONFIG: Read `x-ipe-docs/config/tools.json` → stages.feature.consultation
  - FILTER: IF config_active → only ENABLED tools participate
  - FOR detected tech_stack: read matched tool's "Built-In Practices"
- ANALYZE quality gaps → derive suggestion categories
- SCAN code for principle violations (SRP, DRY, KISS, YAGNI, SoC)
- CROSS-REFERENCE gaps against tool built-in practices
- PRIORITIZE into primary (MUST) and secondary (nice-to-have) principles
- FORMULATE specific, measurable goals with priority and rationale
- DEFINE target structure and constraints (backward compat, API stability)
- **BLOCKING:** Every suggestion must trace back to documented gap

**Phase 5 — Compile Output:**
- CALCULATE dimension scores (1-10): `score = 10 - SUM(violations × weights)`, clamped 1-10
- DERIVE status: `8-10 = aligned, 6-7 = needs_attention, 1-5 = critical`
- CALCULATE overall_quality_score (weighted avg: req 0.20, feat 0.20, tech 0.20, test 0.20, tracing 0.10, code 0.10)
- GENERATE report to `x-ipe-docs/refactoring/analysis-{context}.md`
- SELF-REVIEW: check for missing content, inconsistencies

### Output Result
```yaml
operation_output:
  success: true | false
  result:
    quality_baseline:
      exists: true | false
      overall_score: "<1-10>"
    refactoring_scope:
      scope_level: "feature | custom"
      feature_id: "{FEATURE-XXX or null}"
      refactoring_purpose: "<purpose>"
      files: [<expanded file list>]
      modules: [<expanded module list>]
      dependencies: [<identified dependencies>]
      scope_expansion_log: [<log entries>]
    code_quality_evaluated:
      requirements_alignment: { score: "<1-10>", status: "<aligned|needs_attention|critical>", gaps: [] }
      specification_alignment: { score: "<1-10>", status: "<aligned|needs_attention|critical>", gaps: [] }
      test_coverage: { score: "<1-10>", line_coverage: "<XX%>", critical_gaps: [] }
      code_alignment: { score: "<1-10>", file_size_violations: [], solid_assessment: {}, kiss_assessment: {} }
      overall_quality_score: "<1-10>"
    refactoring_suggestion:
      summary: "<high-level description>"
      goals: [{ goal: "<specific goal>", priority: "<high|medium|low>", rationale: "<why>" }]
      target_structure: "<desired end state>"
    refactoring_principle:
      primary_principles: [{ principle: "<name>", rationale: "<why>", applications: [] }]
      secondary_principles: [{ principle: "<name>", rationale: "<why>" }]
      constraints: [{ constraint: "<what>", reason: "<why>" }]
    report_path: "x-ipe-docs/refactoring/analysis-{context}.md"
  errors: []
```

### Evaluation Thresholds
- Line Coverage ≥80%
- File Size ≤800 lines
- Function Size ≤50 lines

### Definition of Done
1. ✅ Scope expansion completed (no new items or iteration cap)
2. ✅ All 5 quality perspectives evaluated
3. ✅ Suggestions generated with principles
4. ✅ Analysis report generated at `x-ipe-docs/refactoring/analysis-{context}.md`

### Error Handling
| Error | Cause | Resolution |
|-------|-------|------------|
| `SCOPE_EMPTY` | No files provided or resolved | Ask caller for file paths |
| `FEATURE_NOT_FOUND` | Feature artifacts not at expected path | Verify feature_id, check x-ipe-docs/requirements/ |
| `CIRCULAR_DEPS` | Scope expansion exceeds 10 iterations | Warn about circular dependencies, cap scope |
| `BUILD_FAILURE` | Code doesn't compile before analysis | Fix build errors before analysis |

---

## 5. WORKFLOW STATE — Knowledge-Base-Implementation
**Location:** `x-ipe-docs/engineering-workflow/workflow-Knowledge-Base-Implementation.json`

### Metadata
| Field | Value |
|-------|-------|
| **schema_version** | 3.0 |
| **name** | Knowledge-Base-Implementation |
| **created** | 2026-03-10T11:29:06.244938+00:00 |
| **last_activity** | 2026-03-11T11:45:38.193532+00:00 |
| **current_stage** | validation |
| **idea_folder** | null |

### Global Configuration
```json
{
  "global": {
    "process_preference": {
      "interaction_mode": "dao-represent-human-to-interact"
    }
  }
}
```

**NOTE:** Interaction mode is set to `"dao-represent-human-to-interact"` — agents should use DAO skill for human guidance rather than asking directly.

### Workflow Stages Overview

**Status Summary by Feature:**
- **FEATURE-049-A** (KB Backend & Storage Foundation): `validation: in_progress`
  - `acceptance_testing: done`
  - `code_refactor: pending`
  - `feature_closing: done`
- **FEATURE-049-B** (KB Sidebar & Navigation): `validation: in_progress`
  - `acceptance_testing: done`
  - `code_refactor: pending`
  - `feature_closing: done`
- **FEATURE-049-C** (KB Browse & Search): `implement: in_progress`
  - `acceptance_testing: pending`
  - `code_refactor: pending`
  - `feature_closing: pending`
- **FEATURE-049-D** (KB Article Editor): `implement: in_progress`
  - `acceptance_testing: pending`
  - `code_refactor: pending`
  - `feature_closing: pending`
- **FEATURE-049-E** (KB File Upload): `implement: in_progress`
  - `acceptance_testing: pending`
  - `code_refactor: pending`
  - `feature_closing: pending`
- **FEATURE-049-F** (KB AI Librarian & Intake): `implement: locked`
  - All actions pending (depends on FEATURE-049-A, FEATURE-049-E)
- **FEATURE-049-G** (KB Reference Picker): `implement: in_progress`
  - `acceptance_testing: pending`
  - `code_refactor: pending`
  - `feature_closing: pending`

### Feature Dependencies
```
FEATURE-049-A (Backend & Storage Foundation)
  ├── FEATURE-049-B (Sidebar & Navigation)
  │   ├── FEATURE-049-C (Browse & Search)
  │   └── FEATURE-049-E (File Upload)
  ├── FEATURE-049-D (Article Editor)
  ├── FEATURE-049-E (File Upload)
  │   └── FEATURE-049-F (AI Librarian & Intake)
  └── FEATURE-049-C (Browse & Search)
      └── FEATURE-049-G (Reference Picker)
```

### Shared Phase Status

**Ideation Phase:** ✅ COMPLETED
- `compose_idea`: done
- `refine_idea`: done
- `reference_uiux`: pending (optional)
- `design_mockup`: done

**Requirement Phase:** ✅ COMPLETED
- `requirement_gathering`: done
- `feature_breakdown`: done (7 features created)

### FEATURE-049-A Detailed State

**Implement Phase:** ✅ COMPLETED
- `feature_refinement`: done
  - Specification: `x-ipe-docs/requirements/EPIC-049/FEATURE-049-A/specification.md`
- `technical_design`: done
  - Tech Design: `x-ipe-docs/requirements/EPIC-049/FEATURE-049-A/technical-design.md`
- `implementation`: done
  - Impl Files: `src/x_ipe/services/kb_service.py, src/x_ipe/routes/kb_routes.py`

**Validation Phase:** ⏳ IN_PROGRESS
- `acceptance_testing`: done ✅
  - Test Report: `x-ipe-docs/requirements/EPIC-049/FEATURE-049-A/acceptance-test-cases.md`
  - Test Folder: `tests/test_kb_service.py`
  - Next Actions: `code_refactor`
- `code_refactor`: pending (next action after acceptance test)
- `feature_closing`: done ✅
  - Closing Report: `x-ipe-docs/requirements/EPIC-049/FEATURE-049-A/acceptance-test-cases.md`
  - Next Actions: `human_playground, change_request`

**Feedback Phase:** 🔒 LOCKED
- `human_playground`: skipped (optional)
- `change_request`: skipped (optional)

### FEATURE-049-B Detailed State

**Implement Phase:** ✅ COMPLETED
- `feature_refinement`: done
- `technical_design`: done
- `implementation`: done
  - Files: `src/x_ipe/static/js/features/sidebar.js`, `sidebar.css`, `file_service.py`
  - Tests: `tests/frontend-js/kb-sidebar.test.js`

**Validation Phase:** ⏳ IN_PROGRESS
- `acceptance_testing`: done ✅
- `code_refactor`: pending
- `feature_closing`: done ✅

### FEATURE-049-C Detailed State

**Implement Phase:** ⏳ IN_PROGRESS
- `feature_refinement`: done
- `technical_design`: done
- `implementation`: done
  - Files: `src/x_ipe/static/js/features/kb-browse.js`, `kb-browse.css`
  - Tests: `tests/frontend-js/kb-browse.test.js`

**Validation Phase:** 🔒 LOCKED
- `acceptance_testing`: pending (blocked until implementation confirmed)
- `code_refactor`: pending
- `feature_closing`: pending

### FEATURE-049-D Detailed State

**Implement Phase:** ⏳ IN_PROGRESS
- `feature_refinement`: done
- `technical_design`: in_progress (not yet complete)
- `implementation`: done
  - Files: `kb-article-editor.js`, `kb-article-editor.css`

### FEATURE-049-E Detailed State

**Implement Phase:** ⏳ IN_PROGRESS
- `feature_refinement`: done
- `technical_design`: done
- `implementation`: done
  - Files: `kb-file-upload.js`, `kb-file-upload.css`, `kb_routes.py`

### FEATURE-049-F Detailed State

**Implement Phase:** �� LOCKED
- `feature_refinement`: pending (waiting for dependencies)
- `technical_design`: pending
- `implementation`: pending
- **Reason:** Depends on FEATURE-049-A (done) and FEATURE-049-E (in_progress)

### FEATURE-049-G Detailed State

**Implement Phase:** ⏳ IN_PROGRESS
- `feature_refinement`: pending
- `technical_design`: done
- `implementation`: done
  - Files: `kb-reference-picker.js`, `kb-reference-picker.css`

---

## Summary & Key Insights

### DAO Skill Integration
- The Knowledge-Base-Implementation workflow uses `interaction_mode: "dao-represent-human-to-interact"`
- All agents MUST use DAO skill when human guidance is needed (NO direct human asks)
- DAO skill provides 7 dispositions; agents should leverage this for bounded, autonomous decisions

### Feature-Closing Skill Flow
- Used AFTER acceptance testing to ship completed features
- MANDATORY steps:
  1. Verify ALL acceptance criteria
  2. Review code-to-docs alignment via sub-agent
  3. Update project files
  4. Run refactoring analysis (ANALYSIS ONLY, NO EXECUTION)
  5. Create PR or push to main (per git strategy)
  6. Output summary with refactoring recommendations
- Git strategy determines final action (main-branch-only = direct push; dev-session-based = PR)

### Refactoring-Analysis Tool
- Evaluates code across 5 dimensions (requirements, features, tech spec, tests, tracing)
- Max 10 iterations for scope expansion; stops when stable
- Generates quality scores (1-10) and prioritized improvement suggestions
- CRITICAL: Analysis only — NOT an execution tool

### Current Workflow State
- **FEATURE-049-A & FEATURE-049-B**: Nearly complete (feature_closing done, code_refactor pending)
- **FEATURE-049-C, D, E, G**: Implementation in progress, validation pending
- **FEATURE-049-F**: Locked pending dependencies (A & E)
- **Next Critical Step:** Run code_refactor on FEATURE-049-A & FEATURE-049-B (already closed)

### DAO Decision (DAO-039)
- Human overrode auto-skip logic for FEATURE-049-A acceptance testing
- Skill was updated to support backend-api testing
- Feature must be re-validated with new acceptance test scope
- Confidence: 0.95 (high certainty human intent was clear)

