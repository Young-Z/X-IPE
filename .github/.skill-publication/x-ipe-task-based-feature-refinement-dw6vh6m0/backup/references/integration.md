# Refinement artifact, board and workflow integration

## One owner and actual feature query

Load [board manager](.github/skills/x-ipe-tool-task-board-manager/SKILL.md) and
[app interactor](.github/skills/x-ipe-tool-x-ipe-app-interactor/SKILL.md).
Lifecycle readiness carries task identity, mode and approved scope. Child writes
the specification and one agreed action, returning its full output. Lifecycle
owns task status, category/feature status/link persistence, Git and routing.
No child task CRUD, manual JSON mutation, commit or next-skill execution.

From approved root with configured Python:

```text
{python} .github/skills/x-ipe-tool-task-board-manager/scripts/feature_query.py --feature-id {feature_id}
```

CLI success is success/data.feature, including feature_id, epic_id, title,
version, status, description, dependencies and optional specification_link.
Validate readable existing inventory first: corrupt input may look like empty
query results. Missing/wrong identity blocks; refinement never creates a feature.
New path requires Planned; advanced CR/resume requires explicit scope/readiness
and matching existing spec, never a status reset or implicit gate waiver.

## Source, specification and folder resolution

Required contexts: explicit requirement-doc/features-list first, upstream output
links second, actual owning requirement part/Feature List fallback last. Reconcile
parts/index by feature identity, not simply highest/latest part. Workflow-mode
requires both; a populated owning part may satisfy both. Free-mode retains valid
legacy fallback, not omission of required domain source coverage.

Specification target order:

1. Explicit authorized specification artifact path.
2. Board specification_link, including supported Markdown anchors for lookup.
3. Unique matching x-ipe-docs/requirements/EPIC-{nnn}/FEATURE-{nnn}-{X}/.
4. Matching legacy x-ipe-docs/requirements/FEATURE-{nnn}/ (or existing suffix folder).

Explicit broken/wrong-feature/escaping/ambiguous link blocks, never fallback.
Validate content identity, approved canonical containment, file/directory kind,
symlink escape and collisions. Preserve existing owning folder; do not migrate
legacy data or create a second spec. For absent new suffix feature use new
EPIC/FEATURE folder; new legacy ID uses legacy folder. Existing folder lookup
uses actual immutable board epic_id, not assumption from a CR intake Epic.

Mockups: explicit/upstream links then scoped existing feature copies, linked
idea-summary/idea mockups, matching Epic shared mockups. Every candidate including
existing copies is filtered/analyzed. Shared root-relative links stay shared;
copy missing authorized files only if needed, no overwrite. HTTP/HTTPS links need
actual content/reachability evidence when required; SHA256 binds local revisions.
Status current/outdated and Linked Date provenance are distinct from authority.

## Exact application action and output artifacts

Inspect [action map](src/x_ipe/static/js/features/workflow-stage.js) and
[workflow template](x-ipe-docs/config/workflow-template.json).
feature_refinement is mandatory, implement stage, per_feature. Both contexts
requirement-doc and features-list are required. The two deliverable keys are:

- specification: actual populated specification file for exactly this feature.
- feature-docs-folder: scalar existing owning directory containing that file.

No spec-path, specification-folder or renamed tags; folder is not an array.
All links are project-root-relative; reject traversal, wrong-feature artifact or
placeholder/unpopulated content before write. Writer exit alone cannot prove this.

```text
{python} .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/workflow_get_state.py --workflow {name} --format json
{python} .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/workflow_update_action.py --workflow {name} --action feature_refinement --status done --feature-id {feature_id} --deliverables '{"specification":"{actual spec}","feature-docs-folder":"{actual folder}"}' --format json
{python} .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/workflow_get_state.py --workflow {name} --format json
```

Preserve already selected context. If authorized required context population is
needed, supply actual selected values via supported --context JSON, merging
existing unrelated keys rather than erasing them. No --features: this action
must not append another feature. Agree writer once with lifecycle, verify rather
than replay a completed unchanged action. Free-mode has no app write and false
workflow_action_updated. Prior-write true requires actual evidence/current readback.

Precheck shared.requirement.actions.feature_breakdown done with valid artifacts,
unique matching workflow feature and both populated source contexts. Readback
features[].implement.actions.feature_refinement matched by feature_id must be
done with both exact artifact tags/context. Prove unrelated features/prerequisites
and advanced stages unchanged. Do not equate skipped/pending/failed with done or
reset gates to bypass helper errors. Missing tags/files/contexts and some
prerequisite gaps may be accepted by helper; domain validation still blocks.

## Lifecycle board handoff and evidence invalidation

Return actual specification path, owning directory and original feature output
fields unchanged. Lifecycle/category integration verifies supported
feature_update.py --feature-id ID --updates JSON for specification_link and
authorized Refined status on new refinement. Advanced CR retains status; only
approved fields/version change. Query readback verifies immutable IDs/Epic,
created_at, dependencies, stable history and actual link. No child status update.

Source/AC/spec/mockup changes invalidate affected downstream design, test and
acceptance evidence. Report affected revisions to lifecycle; do not automatically
reset workflow/board statuses or call old evidence current. Required category
handoff or invalidation not supported/verified means blocked partial output.
On failure preserve artifacts and state; no destructive rollback of foreign work.

Temporary helper tests characterize mechanics, not agent authoring, question,
language, scope or semantic freshness reasoning. Independent reviewer must assess
this candidate before any separate authorized promotion; receipts alone cannot
grant permission or make unavailable checks pass.
