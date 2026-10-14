---
name: x-ipe-tool-task-board-manager
description: Manage tasks and features on JSON project boards with schema-compatible CLI operations, collision-safe task IDs, and supplied-ID idempotent registration/resume. Use for creating, updating, querying, archiving tasks and managing features. Triggers on requests like "create task", "ensure task", "resume task", "update task status", "query tasks", "create feature", "update feature", "query features".
---

# Task & Feature Board Manager

## Purpose

Provide task/feature CRUD, all-date ownership checks, and safe task registration
without duplicating an existing lifecycle task or changing application schemas.

## Important Notes

BLOCKING: Operate only on the caller's approved project and task. A supplied task
ID means query/ensure that ID, not allocate a replacement. Reuse only matching
ownership/context; do not take another session's work or silently claim a blank role.

BLOCKING: Ownership/nickname checks use `--range all`, consume every page, and
compare `role` exactly in returned JSON. There is NO `--assignee` option.
`--search` is case-insensitive substring search across multiple fields, not ownership.

CRITICAL: Scripts resolve project root by walking up from CWD to `x-ipe-docs/`.
Run from the approved root; relative script paths below are project-root relative.
Write calls in agent workflows are sequential. Locks protect cooperating writers,
not manual JSON edits. Never delete lock files to bypass contention.

## About

**Key Concepts:**
- **Task store:** dated UTC files in `x-ipe-docs/planning/tasks/`, plus
  `tasks-index.json` with entries containing `file`, `status`, `last_updated`.
- **Feature store:** `x-ipe-docs/planning/features/features.json`.
- **Owner:** existing `role` string; no new `assignee`, `title`, or session field.
- **Resume:** ensure a supplied ID with nonempty caller `role` and exact
  `role`, `task_type`, `description`;
  return current record unchanged, even if completed. Never reopen automatically.
- **Auto allocation:** only an omitted `task_id` in create allocates `TASK-NNN`,
  numeric maximum + 1 across index and dated live/archive records under index lock.
  Explicit string IDs remain supported; automatic create is NOT retry-idempotent.

## When to Use

```yaml
triggers: [create task, ensure task, resume task, update task status, query tasks, archive tasks, create feature, update feature, query features]
not_for: [development lifecycle orchestration, skill publication, deleting tracking history]
```

## Input Parameters

```yaml
input:
  operation: task_create | task_ensure | task_query | task_update | task_archive | feature_create | feature_query | feature_update | migrate
  project_root: approved absolute project root
  task:                         # --task JSON; task_create/task_ensure
    task_id: optional for create, REQUIRED for ensure
    task_type: string
    description: string
    role: string
    status: pending | in_progress | completed | blocked | cancelled | skipped | deferred
    output_links: []             # required list
    next_task: ""               # required string
  feature:                      # --feature JSON; feature_create
    feature_id: string
    epic_id: string
    title: string
    version: string
    status: Planned | Refined | Designed | Implemented | Tested | Completed | Retired
    dependencies: []             # required list
    description: optional string
    specification_link: optional string
  updates: object               # --updates JSON for task/feature updates
  query: object                 # flags from the table below
  date: YYYY-MM-DD               # task_archive archives an entire day, not an ID
  lock_timeout: 10               # seconds on writer CLIs
```

### Input Initialization

```xml
<input_init>
  <field name="operation" source="Caller selects one operation; never create a lifecycle task inside this tool just to use the tool." />
  <field name="project_root"><steps>Resolve caller-approved root and CWD. Confirm x-ipe-docs marker; use scripts belonging to this skill.</steps></field>
  <field name="task"><steps>Use actual task schema. If lifecycle supplies task_id, retain it and exact original role/task_type/description for ensure. If new, omit task_id only on create; retain returned ID immediately for future retries. Do not invent assignee/title fields.</steps></field>
  <field name="feature"><steps>Supply all required feature fields; optional description/specification_link can be absent. Preserve existing ID/epic ID when updating.</steps></field>
  <field name="updates"><steps>Use only known mutable fields. Tasks cannot change task_id/created_at; features also cannot change epic_id. created_at and last_updated are generated on create; last_updated is auto-set on update.</steps></field>
  <field name="query"><steps>Use all-date complete pagination for ownership/resume discovery; default 1w is only for browsing. Match role exactly after parsing JSON.</steps></field>
  <field name="date"><steps>Confirm archival authorization and inspect every task for the target UTC day. Do not archive active work accidentally.</steps></field>
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Approved root and operation</name><verification>Caller intent, target project and permitted mutations are known.</verification></checkpoint>
  <checkpoint required="true"><name>Existing identity respected</name><verification>Supplied task/feature IDs and ownership/context checked; no duplicate lifecycle registration.</verification></checkpoint>
  <checkpoint required="true"><name>Contract inputs</name><verification>JSON fields, status case and documented CLI flags match operation; archive scope explicitly authorized.</verification></checkpoint>
</definition_of_ready>
```

## Operations

All scripts below are under `.github/skills/x-ipe-tool-task-board-manager/scripts/`.
Invoke with the project's configured Python (for example `uv run python`).

| Operation/script | Actual flags | Success `data` |
|---|---|---|
| task_create.py | `--task JSON`, `--lock-timeout SECONDS` | `task_id`, `file` |
| task_ensure.py | `--task JSON` including ID, `--lock-timeout SECONDS` | `task_id`, `file`, `created`, `task` |
| task_query.py | `--task-id ID` OR `--range 1w\|1m\|all`, `--status`, `--search`, `--page`, `--page-size` | `task` OR `tasks`, `total`, `page`, `page_size`, `total_pages` |
| task_update.py | `--task-id ID`, `--updates JSON`, `--lock-timeout SECONDS` | `task_id`, `updated_fields` |
| task_archive.py | `--date YYYY-MM-DD`, `--lock-timeout SECONDS` | `archived_file`, `tasks_removed`, `task_ids` |
| feature_create.py | `--feature JSON`, `--lock-timeout SECONDS` | `feature_id` |
| feature_update.py | `--feature-id ID`, `--updates JSON`, `--lock-timeout SECONDS` | `feature_id`, `updated_fields` |
| feature_query.py | `--feature-id ID` OR list `--epic-id`, `--status`, `--search`, `--page`, `--page-size`; `--epic-summary` optionally with epic filter; `--lock-timeout` accepted | `feature` OR paginated `features` OR `summaries` |
| migrate.py | exactly one of `--tasks`, `--features`, `--all`; optional `--dry-run` | final JSON `results` after progress text |

### Operation: Register or Resume Task

```xml
<operation name="task_register_resume">
  <action>
    1. Supplied ID: query by ID, then ensure with original context; if genuinely absent, ensure creates exactly that ID atomically. Errors other than not-found are blocking.
    2. No supplied ID: complete all-date queries to check existing owned tasks and nickname collisions. Reuse only a task identified by caller/session context; same nickname alone does not establish session identity. Resolve ambiguity, do not guess.
    3. For genuinely new work, task_create may omit ID. Save returned ID; subsequent retries use task_ensure with this ID, never a second automatic create.
    4. Ensure reports created=false for one indexed live record with matching role/task_type/description and does not overwrite timestamps, status, outputs or next_task. Return completed work as-is to lifecycle owner.
  </action>
  <constraints>Do not generate IDs by an unlocked scan. Blank/different existing role is a conflict, not authorization to claim. Archives, multiple records and index mismatches cannot be resumed automatically.</constraints>
  <output>Existing or created task ID and current record; ownership/context conflicts reported without mutation.</output>
</operation>
```

### Operation: Query and Update

```xml
<operation name="query_update">
  <action>
    1. Query task/feature by ID or list using supported filters. Task list defaults to 1w, page 1, size 50; archives are excluded. Ownership checks consume all pages of all-date results.
    2. Before a task mutation, verify current role and caller authority; generic update does not enforce ownership itself. Use --updates JSON for mutable fields only.
    3. Write canonical statuses: completed for tasks; Completed for features. Task done/complete aliases normalize to completed. Feature statuses are case-sensitive, without aliases.
    4. Query after writes to verify ID, intended fields, outputs and routing. Query is read-only; repeated reads of unchanged state do not change timestamps or create files.
  </action>
  <output>Structured CLI success data or error; no fabricated application schema.</output>
</operation>
```

### Operation: Archive or Migrate

```xml
<operation name="archive_migrate">
  <action>
    1. Archive only an authorized whole date: rename dated file to tasks-DATE.archived.json and remove its IDs from active index. Reserved archived IDs are never reused by creation.
    2. Migration is explicit maintenance, never automatic registration fallback. Use --dry-run first; inspect output before authorized writes. It reads legacy planning markdown and retains historical timestamps.
    3. Task writers acquire daily lock then index lock; migration follows the same order per date. No additional daily lock under index. Feature writers lock features.json alone.
    4. Atomic replacement protects individual files only. On interrupted daily/index commit or corrupt state, stop and request authorized repair; do not erase data or retry allocation as if nothing happened.
  </action>
  <output>Archive receipt or migration summary; no deletion of historical task records.</output>
</operation>
```

## Output Result

Tool caller adaptation (not a change to CLI or API payloads):

```yaml
operation_output:
  success: true | false
  result: "parsed script data, or migrate results"
  errors: []                    # on failure retain error/message and exit code
```

Task/feature CRUD scripts emit `{"success":true,"data":{...}}` on stdout;
runtime failures emit `{"success":false,"error":"CODE","message":"..."}` on stderr.
Exit codes: 0 success, 1 validation, 2 missing resource, 3 lock timeout.
Argparse usage errors/help use standard argparse text (error exit 2). Migration
includes progress text and a final JSON summary, not JSON-only stdout.
CLI pagination is flat inside `data`; HTTP API pagination is nested under
`data.pagination`. Task CLI single wraps `data.task`; HTTP task get returns the
record directly inside `data`. Do not change consumers to mimic CLI envelopes.
The HTTP service accepts CRUD object-form and historical list-form daily files,
including historical string index entries and fallback when the index is stale.
Task scripts retain their existing JSON envelopes; HTTP responses stay distinct.

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Actual contract used</name><verification>Supported CLI and existing schemas only; no arbitrary assignee or invented fields.</verification></checkpoint>
  <checkpoint required="true"><name>Identity safe</name><verification>Correct supplied/allocated ID recorded; retries did not duplicate or seize foreign work.</verification></checkpoint>
  <checkpoint required="true"><name>Ownership complete</name><verification>All-date pages and exact role matching used when checking ownership; same nickname not treated as session proof.</verification></checkpoint>
  <checkpoint required="true"><name>Outcome verified</name><verification>Query verifies authorized writes; canonical status/output/routing preserved; conflicts and interruptions surfaced.</verification></checkpoint>
  <checkpoint required="true"><name>Result returned</name><verification>Parsed data/errors returned to caller; this utility does not independently complete lifecycle or git work.</verification></checkpoint>
</definition_of_done>
```

## Error Handling

| Error | Cause | Resolution |
|---|---|---|
| SCHEMA_VALIDATION_FAILED / TYPE_ERROR / UNKNOWN_FIELD | Invalid JSON schema | Use actual task/feature fields, not title/assignee for tasks |
| INVALID_STATUS / INVALID_PAGINATION | Unsupported enum or nonpositive task page values | Canonical status and positive page/page-size |
| DUPLICATE_TASK_ID | Explicit ID already reserved | Query and ensure supplied context; never allocate a replacement silently |
| OWNERSHIP_CONFLICT / CONTEXT_CONFLICT | Existing record differs | Return conflict to lifecycle owner; no claim/rewrite |
| OWNERSHIP_REQUIRED | Blank ensure caller role | Provide authorized nonempty owner; never implicitly claim blank-owned work |
| TASK_ARCHIVED / INCONSISTENT_BOARD / INVALID_BOARD / BOARD_READ_ERROR | Archived, duplicate, orphan or corrupt state | Stop; preserve bytes; separately authorized repair |
| TASK_NOT_FOUND / INDEX_NOT_FOUND | Missing query/update resource | Distinguish genuine absence from damaged state before ensure |
| LOCK_TIMEOUT | Contending writer | Retry boundedly using same supplied ID; never remove lock |
| IMMUTABLE_FIELD | Identity change attempted | Preserve immutable IDs and timestamps |

## Templates

No generated artifact templates are required. Use the JSON contracts above;
envelope `_version` belongs to stores/schema metadata, not per-task/feature input.
Schema validators reject unknown record fields, including a record `_version`.

## Examples

Executable JSON examples, ownership pagination and interrupted-write handling:
[references/examples.md](.github/skills/x-ipe-tool-task-board-manager/references/examples.md).
