# Actual feature board and workflow integration

## Ownership and approved root

Lifecycle readiness carries the existing TASK ID. Feature CRUD below is domain
registration, not a new task. Never call task_create/ensure/update, commit or
execute refinement from this child. Run installed scripts with configured Python
from the approved project root. Do not edit status stores manually.

Load [board manager](.github/skills/x-ipe-tool-task-board-manager/SKILL.md) and
[app interactor](.github/skills/x-ipe-tool-x-ipe-app-interactor/SKILL.md).
Use [action map](src/x_ipe/static/js/features/workflow-stage.js),
[workflow template](x-ipe-docs/config/workflow-template.json) and
[prompts](x-ipe-docs/config/copilot-prompt.json), not guessed schemas/action names.

## Board feature registration and CR

Feature store is x-ipe-docs/planning/features/features.json. First read/validate
existing JSON envelope/features records and inventory; absent store is a genuine
new-board condition, not a parse-error fallback. Corrupt/unreadable/ambiguous
store blocks: current query can return empty on parse errors and create can reset
an unreadable store, so absence cannot be inferred from query success alone.
Consume all feature_query pages/statuses (including Retired) for reservations.

Actual new-feature object (no priority/AC/task/assignee fields):

```json
{"feature_id":"FEATURE-061-A","epic_id":"EPIC-061","title":"Status Badge","version":"v1.0","status":"Planned","description":"Read-only operator status badge","dependencies":[]}
```

Required: feature_id, epic_id, title, version, status, dependencies. Optional:
description, specification_link (do not link an uncreated spec). Timestamps are
system-managed. Enforce domain ID patterns, dependency existence/DAG and matching
Epic in prechecks; CLI only checks types/status, not these semantics.

```text
{python} .github/skills/x-ipe-tool-task-board-manager/scripts/feature_query.py --feature-id FEATURE-061-A
{python} .github/skills/x-ipe-tool-task-board-manager/scripts/feature_create.py --feature '{feature object JSON}'
{python} .github/skills/x-ipe-tool-task-board-manager/scripts/feature_query.py --feature-id FEATURE-061-A
{python} .github/skills/x-ipe-tool-task-board-manager/scripts/feature_update.py --feature-id FEATURE-028-B --updates '{approved mutable delta JSON}'
```

CLI success: success/data.feature_id or data.feature; list pagination is flat
inside data. Failures use stderr JSON/nonzero exits. DUPLICATE_ERROR means query
and match existing identity/context, never automatic allocation of replacement.
No batch create_or_update_features, feature_archive or feature_delete operation.
Query unchanged resume is read-only and preserves timestamps/status/spec links.
CR may update title/version/description/dependencies as approved; feature_id,
epic_id and created_at are immutable. Never blanket-set Planned on existing IDs.
Full approved split retirement uses --updates '{"status":"Retired"}', retaining
history. Active document removal with redirects must also be verified before
parent_features_removed is populated. Partial coverage keeps parent and gaps.

HTTP read consumer: GET /api/features/list uses nested data.pagination;
GET /api/features/get/{id} wraps the record in data.feature, like single CLI query.
Do not transfer the task HTTP get envelope (direct data record) to feature reads.
These routes are read-only, not invented POST/DELETE feature CRUD endpoints.
Use actual CLI mutation contract; do not change app consumers to mimic CLI shape.

## Mandatory workflow artifacts and feature shape

feature_breakdown is shared/mandatory; required requirement-doc context comes from
requirement_gathering. Preserve EN/ZH prompt tags. Verify gathering actually done
with populated artifacts and required context, not skipped/pending. Writer does
not enforce every in-stage prerequisite or filesystem semantic gate.

- features-list: actual populated Feature List file (selected requirement part
  is valid, with all scoped detail sections); not board JSON or an empty file.
- breakdown-folder: scalar existing directory containing the breakdown document/
  Epic context (requirements root is valid); never an array or invented folder.
- Both tags required even though writer tolerates missing tags/nonexistent paths.
- Validate root containment, source/Epic identity, language, links and hashes.

Workflow --features uses a DISTINCT schema:

```json
[{"id":"FEATURE-061-A","name":"Status Badge","depends_on":[]}]
```

```text
{python} .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/workflow_get_state.py --workflow {name} --format json
{python} .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/workflow_update_action.py --workflow {name} --action feature_breakdown --status done --deliverables '{"features-list":"x-ipe-docs/requirements/{selected-file}","breakdown-folder":"x-ipe-docs/requirements"}' --features '{absent new id/name/depends_on entries JSON}' --format json
{python} .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/workflow_get_state.py --workflow {name} --format json
```

Agree action owner once: child writes unless lifecycle already performed the
verified write. Readback shared.requirement.actions.feature_breakdown must be
done with exact both tags/files; state.features must have unique intended IDs,
names/direct depends_on and preserved existing per-feature stages/actions.
Initial action requires nonempty --features. Extra tags/folder arrays fail;
missing tags/files can succeed, so writer exit alone never supports completion.

## Append-only helper and incremental/resume safety

The installed workflow helper blindly APPENDS supplied entries with fresh locked
stages. It neither deduplicates nor updates existing graph entries; same-ID replay
creates duplicates. features_created is overwritten with the latest supplied
delta, not a cumulative list. Preserve full state.features as identity source,
and report both existing and new entries; do not claim features_created is total.

1. Query current state and validate uniqueness/matching existing identity/graph.
2. Done unchanged resume: verify artifacts and prior write evidence, no replay.
3. New delta: pass ONLY absent new entries; prove existing entries/stages unchanged
   and new dependencies refer to existing/new nonretired IDs without cycles.
4. Existing-only CR on an already-done action: verify current valid artifacts and
   graph without write. Retain true only with evidence of actual prior write and
   current exact readback, not intention. Documents/board are separate evidence.
5. Pending/failed initial action with only preexisting entries: --features [] is
   MISSING_FEATURES, resending duplicates is unsafe. Block required completion.
6. Changes to existing workflow dependencies/names, retirement of referenced IDs,
   or split references cannot be reconciled safely by this append helper. Require
   a separately supported authorized reconciler; otherwise blocked partial result.
   No silent workflow JSON edits, reset, duplicate or skipped/done prerequisite.
7. Free-mode has no workflow mutation and false workflow_action_updated.

On failed write/readback retain actual partial artifacts/state and honest flags;
do not silently rollback unrelated state. Rerun affected checks after revision
changes. Domain conflicts/dependencies/authoring decisions are not proven by
contract assertions or helper exits. Temporary helper tests characterize actual
mechanics and gaps; separate independent review is required before promotion.
