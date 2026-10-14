# Board CLI examples

Run from the approved project root using its configured Python. All paths below
refer to installed scripts after publication; tests use candidate scripts instead.
Do not run these examples on a real board merely to validate documentation.

## New task, explicit registration and resume

```sh
uv run python .github/skills/x-ipe-tool-task-board-manager/scripts/task_create.py --task '{"task_type":"Skill Update","description":"Review board contracts","role":"Drift","status":"in_progress","output_links":[],"next_task":""}'
```

Save the returned `data.task_id` immediately. Suppose it is `TASK-001` in an empty
temporary project. The same JSON with supplied ID is the retry contract:

```sh
uv run python .github/skills/x-ipe-tool-task-board-manager/scripts/task_ensure.py --task '{"task_id":"TASK-001","task_type":"Skill Update","description":"Review board contracts","role":"Drift","status":"in_progress","output_links":[],"next_task":""}'
uv run python .github/skills/x-ipe-tool-task-board-manager/scripts/task_query.py --task-id TASK-001
uv run python .github/skills/x-ipe-tool-task-board-manager/scripts/task_update.py --task-id TASK-001 --updates '{"status":"completed","output_links":[],"next_task":""}'
```

Ensure returns `created:false` with the current record on repeat; a completed task
stays completed even if ensure input requests `in_progress`. Exact `role`,
`task_type`, `description` must match. It does not claim unassigned tasks. For an
authorized new explicit ID use create `--task` including ID, or ensure with that
ID: concurrent ensure calls create at most one record. Creation duplicates fail.
No supplied ID in ensure fails validation. Explicit IDs such as `T1` still work.

## All-date ownership and nickname collision checks

```sh
uv run python .github/skills/x-ipe-tool-task-board-manager/scripts/task_query.py --range all --status in_progress --page 1 --page-size 50
```

Consume `data.total_pages`, request pages 2 through the last, and compare each
task's `role` to the nickname exactly. Query pending/blocked/deferred when checking
other open work; do not infer no owned tasks from only in_progress. No `--assignee`
flag exists. A search hit on a description mentioning Drift is not Drift ownership.
An older task can be on a later page; the default 1w query cannot authorize a name.
Concurrent list reads are snapshots of individual files, not one serializable
global snapshot. Rerun when allocation/resume encounters conflicting state.
Matching nicknames across sessions require caller task/context confirmation.

## Features

```sh
uv run python .github/skills/x-ipe-tool-task-board-manager/scripts/feature_create.py --feature '{"feature_id":"FEATURE-001-A","epic_id":"EPIC-001","title":"Board contracts","version":"1.0","status":"Planned","description":"","dependencies":[],"specification_link":""}'
uv run python .github/skills/x-ipe-tool-task-board-manager/scripts/feature_update.py --feature-id FEATURE-001-A --updates '{"status":"Completed"}'
uv run python .github/skills/x-ipe-tool-task-board-manager/scripts/feature_query.py --feature-id FEATURE-001-A
uv run python .github/skills/x-ipe-tool-task-board-manager/scripts/feature_query.py --epic-summary --epic-id EPIC-001
```

## Archive and migration

```sh
uv run python .github/skills/x-ipe-tool-task-board-manager/scripts/task_archive.py --date 2026-01-01
uv run python .github/skills/x-ipe-tool-task-board-manager/scripts/migrate.py --all --dry-run
```

Archive is day-wide; inspect tasks and obtain maintenance authorization first.
Migration progress text precedes final JSON. Its task writer is per-date, not one
transaction across the entire migration. Archived IDs remain reserved even though
archive removes them from the active index.

## Interrupted registration

If daily write succeeds but index write fails, do not auto-create again as a retry.
Ensure with the saved ID fails `INCONSISTENT_BOARD` until authorized index repair.
Automatic allocation reserves unindexed live/archive IDs, so the next genuinely
new task will not collide with the interrupted record. Corrupt inventory blocks
allocation rather than assuming an empty store. This is collision safety, not
crash recovery or transactional repair. No deletion/repair helper is introduced.
