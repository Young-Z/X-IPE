# DAO Decisions — Feature Refinement

## Entry: FEATURE-055-B Specification Review Questions

- **Date:** 04-03-2026
- **Task:** TASK-1064
- **Feature:** FEATURE-055-B (Task CRUD Scripts)
- **Calling Skill:** x-ipe-task-based-feature-refinement (Phase 2.1)
- **Disposition:** answer
- **Confidence:** 0.92

### Context
Agent is refining FEATURE-055-B specification. 8 design questions identified during spec review. All questions relate to CLI script behavior and can be resolved from existing patterns + KISS/YAGNI principles.

### Decisions

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Task ID: caller-provided or auto-generated? | **Caller provides** task_id in JSON | Task-board-management skill already generates sequential IDs (TASK-{N+1}). CRUD scripts are low-level tools, not ID generators. Separation of concerns. |
| 2 | Reject duplicate task_id on create? | **Yes** — check index, fail with EXIT_VALIDATION_ERROR | Fail-fast prevents silent data corruption. O(1) lookup via index. |
| 3 | Which fields are auto-populated? | **created_at** and **last_updated** set by create script (ISO 8601 UTC). **last_updated** auto-updated by update script. Caller cannot override. | Prevents clock-skew issues, ensures consistency. Standard CRUD pattern. |
| 4 | Update: partial merge or full replace? | **Partial merge** — only update provided fields | More ergonomic. Callers don't need to send full object. Matches common REST PATCH semantics. |
| 5 | Archived tasks queryable? | **No** — `task_query.py` skips `*.archived.json`. Direct `--task-id` also checks index (archived entries removed from index). | Clean separation. Archived = out of active view. Unarchive to restore. |
| 6 | Support custom date ranges (--from/--to)? | **No** — keep 1w/1m/all only | KISS. Three presets cover all realistic use cases. Custom ranges add parsing complexity with no clear need. Can add later if needed (YAGNI). |
| 7 | Auto-create directories and index? | **Yes** — scripts create `tasks/` dir and `tasks-index.json` (with INDEX_SCHEMA_V1 structure) if missing | Fail-safe bootstrapping. First `task_create.py` call sets up everything. No manual setup step. |
| 8 | Add --dry-run flag? | **No** | YAGNI. validate_schema is available programmatically. Dry-run adds flag-handling complexity for no current use case. |

### Summary
All 8 decisions align with KISS/YAGNI/DRY principles and existing project patterns. No high-risk choices — all are reversible if future needs change.

---

## DAO-110: FEATURE-056-A Design Decisions

- **Timestamp:** 2026-04-03T15:06:00+0800
- **Task ID:** TASK-1073
- **Feature ID:** FEATURE-056-A
- **Workflow:** feature-pipeline
- **Calling Skill:** x-ipe-task-based-feature-refinement
- **Source:** ai
- **Disposition:** answer
- **Confidence:** 0.92

### Message
> 7 design questions for FEATURE-056-A (Feature CRUD Scripts) covering: status enum values, epic summary computation, feature_id auto-generation, immutable fields, query pagination, dependency validation, and script count.

### Guidance Returned

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Status values: enum or free-form? | **Validated enum** — `Planned`, `Refined`, `Designed`, `Implemented`, `Tested`, `Completed`, `Retired` | 7 statuses mirror the engineering workflow pipeline (refine→design→implement→test→close + retired for soft-delete). Enum validation catches typos. Unlike tasks (open string), features have a well-defined lifecycle. Board rendering can alias display names. |
| 2 | Epic summary computation | **Count-based (option c)** — return `{"total": N, "Planned": X, "Completed": Y, ...}` per-status counts | Most informative, KISS. Callers derive rollup status from counts if needed. Avoids opinionated "lowest-progress" logic. Example output: `{"epic_id": "EPIC-056", "total": 3, "Planned": 1, "Implemented": 1, "Completed": 1}`. |
| 3 | Auto-generate feature_id? | **No** — caller always provides feature_id | Mirrors FEATURE-055-B precedent (task_create.py requires caller-provided task_id). Features board pre-assigns IDs. CRUD scripts are low-level tools, not ID generators. Separation of concerns. |
| 4 | Immutable fields on update | **`feature_id`, `epic_id`, `created_at`** — all three immutable | feature_id = identity key. epic_id = organizational grouping (features don't migrate between epics). created_at = audit trail. Extends task pattern (task_id + created_at) with epic_id. |
| 5 | Query pagination defaults | **Same as tasks: `page=1`, `page_size=50`** | Consistency with task_query.py. Even though features are fewer (<50 typical), a higher default is harmless. One less thing to remember. Code symmetry aids maintenance. |
| 6 | Dependencies validation | **Store as strings, no existence validation** | YAGNI. Dependency IDs are informational metadata. Validating existence creates coupling and blocks creation order. Query tool can optionally flag broken links later. Same pattern as tasks' `next_task` field (stored as string, not validated). |
| 7 | Script count: 3 scripts, no archive? | **Confirmed: 3 scripts** — `feature_create.py`, `feature_update.py`, `feature_query.py`. No `feature_archive.py`. | Single `features.json` file (not daily files) eliminates archive need. Status lifecycle (`Retired`) serves as soft-delete. Matches the stated design: "no archive/delete — status lifecycle only." |

### Rationale
> All 7 decisions follow KISS/YAGNI/DRY principles and maintain consistency with FEATURE-055-B (Task CRUD) implementation patterns. Key theme: mirror tasks where possible, diverge only where feature semantics require it (validated status enum, epic_id immutability, no archive). All decisions are reversible.

### Suggested Skills
> - skill_name: "x-ipe-task-based-feature-refinement"
>   match_strength: "strong"
>   reason: "These are specification-level design decisions for FEATURE-056-A refinement"
>   execution_steps:
>     - phase: "2. Write Specification"
>       step: "2.1 Create specification document incorporating DAO decisions"

### Follow-up
> None. All questions answered. Proceed to specification writing with these decisions as constraints.

---

## FEATURE-057-A: Task Board Web Page — Refinement Decisions

**Task:** TASK-1075  
**Feature:** FEATURE-057-A  
**Timestamp:** 2026-04-03T08:12:00Z  
**Disposition:** instruction  
**Confidence:** 0.92

### Decisions

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Page URL | `/task-board`, add to sidebar nav | Consistent with `/settings`, `/workplace` pattern |
| 2 | Time range toggle | Map 1W→`range=1w`, 1M→`range=1m`, All→`range=all`. No custom picker | API already supports. YAGNI on date picker |
| 3 | Sidebar | Extend `base.html`, ignore mockup's custom sidebar | Consistency with app chrome |
| 4 | Stat cards | Client-side computation from API response | No new endpoint needed. YAGNI |
| 5 | Task detail view | Expandable inline row (accordion) | KISS, keeps context |
| 6 | Output links | Open in new tab (`target="_blank"`) | Simple, no DeliverableViewer dependency |
| 7 | Empty/error states | Inline messages only, no toasts | Consistent, harder to miss |
| 8 | Auto-refresh | No auto-refresh, manual only | YAGNI, infrequent data changes |
| 9 | Status filter | Single select dropdown | KISS, mockup shows `<select>` |
| 10 | Sort order | `last_updated` descending | Most useful default |


---

## FEATURE-057-B: Feature Board Web Page — Refinement Decisions

**Task:** TASK-1075  
**Feature:** FEATURE-057-B  
**Timestamp:** 2026-04-03T08:25:00Z  
**Disposition:** instruction  
**Confidence:** 0.93

### Decisions

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Page URL | `/feature-board`, add to nav bar | Consistent with `/task-board` |
| 2 | Epic accordion default | All collapsed | Overview first, expand on demand |
| 3 | Progress bar | Per-epic only in header | YAGNI on global bar |
| 4 | Retired color | `#64748b` (Slate 500) | Distinct from Planned gray |
| 5 | Epic summary data | Use `/api/features/epic-summary` endpoint | Server-computed, avoid fetching all features |
| 6 | Feature detail | Inline expand (same as task board) | KISS, consistency |
| 7 | Search scope | feature_id, title, epic_id | API already supports |
| 8 | Sort order | Status priority → feature_id asc | Active work first |
| 9 | Shared CSS | Extract board-common.css for shared styles | DRY |
| 10 | Nav label | "Features" with bi-kanban icon | Short, matches "Tasks" |


---

## FEATURE-057-C: Data Migration — Decisions

**Task:** TASK-1075  
**Feature:** FEATURE-057-C  
**Timestamp:** 2026-04-03T08:35:00Z  
**Disposition:** instruction  
**Confidence:** 0.95

### Decisions

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Migration approach | Python script, reusable/testable | Deterministic, rerunnable |
| 2 | Import strategy | Use _board_lib directly (not CRUD scripts) | CRUD scripts call sys.exit, not importable |
| 3 | Markdown parsing | str.split('|') | Well-structured tables, KISS |
| 4 | Dry-run | Yes, --dry-run flag | Low effort, high safety |
| 5 | Script location | .github/skills/.../scripts/migrate.py | Colocate with CRUD scripts |
| 6 | Active vs Completed | Parse both identically, plus Cancelled | Same parser, different column counts |
| 7 | Emoji status | Strip emoji, normalize | ✅ done → done, 🔄 in_progress → in_progress |
| 8 | Post-migration | Keep originals as .bak | Cleanup in 057-E |


---

## DAO-111: FEATURE-057-D Skill Updates for JSON Board Migration — Refinement Decisions

- **Timestamp:** 2026-04-03T16:30:00+0800
- **Task ID:** TASK-1075
- **Feature ID:** FEATURE-057-D
- **Workflow:** feature-pipeline
- **Calling Skill:** x-ipe-task-based-feature-refinement
- **Source:** ai
- **Disposition:** instruction
- **Confidence:** 0.93

### Message
> 5 refinement questions for FEATURE-057-D (Skill Updates for JSON Board Migration) covering: scope/batching strategy for ~34 skill updates, update pattern abstraction level, testing strategy, backward compatibility, and old skill name handling.

### Decisions

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Scope: batch all, logical groups, or critical-only? | **(a) Update ALL ~34 skills in one batch commit** | These are documentation-only changes (SKILL.md text). Agents read skills fresh each invocation — no cached versions. Grouping adds process overhead for what is essentially find-and-replace. The "blast radius" is text in instructions, not runtime code. A post-update grep verification (Q3) catches any misses. One atomic commit is easier to revert than scattered partial updates. |
| 2 | Update pattern: explicit script paths, abstract language, or cross-skill reference? | **Hybrid (b)+(c): Abstract language that names the target skill** — e.g. "Use `x-ipe-tool-task-board-manager` to create the task" or "Use `x-ipe-tool-feature-board-manager` to update feature status" | Pure script paths (option a) are fragile — args/paths change, all 34 skills break. Pure cross-references (option c) force agents to load a second skill mid-step, adding latency. The hybrid names the skill (discoverable, agents can invoke it) while keeping language abstract (no hardcoded `python .github/skills/.../scripts/task_create.py --title`). DRY — board manager skill owns the procedure details. |
| 3 | Testing: grep, CI lint, or nothing? | **(a) Grep verification** — after all updates, run grep for `task-board.md`, `features.md`, `x-ipe+all+task-board-management`, and `x-ipe+feature+feature-board-management` across all SKILL.md files | Quick, effective, one-time. YAGNI on CI lint infrastructure for a migration that runs once. Option (c) is too cavalier for 34 files — one missed reference creates confusion. The grep also serves as the acceptance criterion for the feature. |
| 4 | Backward compatibility: all-at-once or deprecation notices first? | **(a) Update all at once** — agents pick up new instructions on next invocation | Skills have no caching layer — each agent loads SKILL.md fresh. Deprecation notices add a whole extra pass (write notices → wait → write real updates) for zero benefit. There is no "breaking change" risk since the old markdown files will still exist as .bak (per 057-C decision). |
| 5 | Old skill names (`x-ipe+all+task-board-management`, `x-ipe+feature+feature-board-management`): update refs, remove old, or create wrappers? | **(a) Update all references to new skill names, keep old skills for cleanup in 057-E** | Follows the established 057 pattern: 057-C keeps originals as .bak, 057-E handles cleanup. FEATURE-057-D's scope is "update references" — deleting or wrapping old skills is a separate concern. Clean separation of feature scope. One thing at a time. |

### Rationale
> All 5 decisions follow KISS/YAGNI/DRY principles and maintain consistency with the 057-series migration pattern (057-C: migrate data + keep originals, 057-E: cleanup). Key theme: minimize ceremony for documentation-only changes while ensuring completeness via grep verification. Confidence is high because the migration pattern is well-established and all changes are easily reversible (git revert of single commit).

### Suggested Skills
> - skill_name: "x-ipe-task-based-feature-refinement"
>   match_strength: "strong"
>   reason: "These are specification-level refinement decisions for FEATURE-057-D"
>   execution_steps:
>     - phase: "2. Write Specification"
>       step: "2.1 Create specification document incorporating DAO decisions"

### Follow-up
> None. All questions answered. Proceed to specification writing with these decisions as constraints. The grep patterns in Q3 should be documented in the spec's acceptance criteria section.
