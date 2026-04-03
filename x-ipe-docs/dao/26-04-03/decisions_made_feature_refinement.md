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
