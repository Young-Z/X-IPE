# DAO Decisions — General

| Entry ID | Timestamp | Task ID | Calling Skill | Disposition | Confidence | Summary |
|----------|-----------|---------|---------------|-------------|------------|---------|
| DAO-001 | 2026-03-18T07:38:52.343Z | TASK-TBD | N/A | answer | 0.97 | Confirm repository uses watchdog for file monitoring |

## DAO-001
- **Timestamp:** 2026-03-18T07:38:52.343Z
- **Task ID:** TASK-TBD
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A
- **Source:** human
- **Disposition:** answer
- **Confidence:** 0.97

### Message
> we did x-ipe used watchdog

### Guidance Returned
> Yes — X-IPE uses `watchdog` for file monitoring and real-time file change handling.

### Rationale
> The message reads as a corrective reminder or context note rather than a new implementation request. Repository evidence confirms `watchdog` is both declared as a dependency and imported by the file watcher service, so the smallest useful response is to acknowledge and confirm the fact.

### Suggested Skills
> suggested_skills:
>   - none

### Follow-up
> None

| DAO-003 | 2026-03-18T07:43:51.916Z | TASK-TBD | N/A | answer | 0.95 | Recommend realistic replacements for watchdog in this repo |

## DAO-003
- **Timestamp:** 2026-03-18T07:43:51.916Z
- **Task ID:** TASK-TBD
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A
- **Source:** human
- **Disposition:** answer
- **Confidence:** 0.95

### Message
> any replacement solution for watchdog?

### Guidance Returned
> Yes. For this repo, the main alternatives are: `watchfiles` (best modern replacement), a custom polling loop using file mtimes (simplest dependency-free fallback), or platform-specific filesystem APIs (most work, least portable). Given the current `FileWatcher.start()/stop()` shape, `watchfiles` is the best practical replacement if you want to swap libraries.

### Rationale
> The user asked for solution options rather than requesting an implementation. The current code only needs recursive watching, start/stop lifecycle, and file event callbacks, so the most useful response is to rank replacements by fit and migration cost.

### Suggested Skills
> suggested_skills:
>   - none

### Follow-up
> None

| DAO-002 | 2026-03-18T07:42:37.115Z | TASK-TBD | N/A | answer | 0.98 | Identify which functions/classes use watchdog |

## DAO-002
- **Timestamp:** 2026-03-18T07:42:37.115Z
- **Task ID:** TASK-TBD
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A
- **Source:** human
- **Disposition:** answer
- **Confidence:** 0.98

### Message
> which function uses it?

### Guidance Returned
> `watchdog` is used in `src/x_ipe/services/file_service.py` by the `FileWatcher` and `FileWatcherHandler` classes. The concrete call site is `FileWatcher.start()`, which instantiates `Observer()`, schedules the handler, and starts the observer.

### Rationale
> This is a direct code-location question about an already confirmed dependency. The smallest useful response is a concrete pointer to the class and method where `watchdog` is actually instantiated and where its event callbacks are handled.

### Suggested Skills
> suggested_skills:
>   - none

### Follow-up
> None

## DAO-088
- **Timestamp:** 2026-03-18T17:39:44Z
- **Task ID:** TASK-NEW
- **Feature ID:** N/A
- **Workflow:** N/A
- **Calling Skill:** N/A (initial user message)
- **Source:** human
- **Disposition:** instruction (x3 units)
- **Confidence:** 0.88

### Message
> Get uiux feedback, please visit feedback folder x-ipe-docs/uiux-feedback/Feedback-20260318-173426 to get details. Three feedback items: (1) Workflow mode zh instructions should display in Chinese, (2) Claude code command should not use -p flag, (3) x-ipe upgrade should support language switch.

### Guidance Returned
> 3 instruction units: Unit 0 → Change Request (workflow i18n), Unit 1 → Bug Fix (claude -p flag), Unit 2 → Change Request (upgrade lang switch). All independent — parallel execution.

### Rationale
> Three distinct feedback items targeting different subsystems. Feedback #1 and #3 are feature gaps (change requests), #2 is a command format bug. All independent — no shared files or output dependencies.

### Suggested Skills
> suggested_skills:
>   - Unit 0: x-ipe-task-based-change-request (strong) — workflow mode i18n gap
>   - Unit 1: x-ipe-task-based-bug-fix (strong) — incorrect -p flag in command
>   - Unit 2: x-ipe-task-based-change-request (strong) — upgrade missing lang support

### Follow-up
> None
