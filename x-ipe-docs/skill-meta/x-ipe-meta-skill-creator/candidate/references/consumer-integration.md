# Creator consumer integration — explicit calls, not automatic learning

Load the installed [lesson contract](.github/skills/x-ipe-meta-lesson-learned/references/lifecycle.md).
Apply these tool-skill procedures in the same agent loop; this integration does
not require a sub-agent, reviewer round, or new task registration.
The helper exists and supplies `load`, `select`, `settle`. Do not use invented
`get_lessons`, `mark_applied`, `adopt`, task fields or statuses. Resolve the
configured Python interpreter. APIs accept explicit roots; no CWD inference.
Load the installed helper using importlib.util.spec_from_file_location with
`project_root/.github/skills/x-ipe-meta-lesson-learned/scripts/lesson_ops.py`.
Do not import an unrelated globally installed module with the same name.

The following calls are executable with `ops` bound to that installed module,
`root` the approved Path, and explicit caller values. They are tested in disposable
projects; snippets are not a claim that an agent automatically follows this policy.

## Select (read-only)

```python
selection = ops.select(root, owner_skills, relevant_to=skill_name, now=now)
```

Use the target and explicitly related primary owners only; applicability is not
directory proximity. Preserve all four result keys: summaries, critical_overflow,
protected, notices. Surface critical overflow/protected legacy/review notices;
do not treat them as fresh actionable summaries. An empty selection is valid.
Do not capture every issue, refresh TTL on selection or scan all historical prose.

## Plan (only when queue writes are authorized)

Keep each `(primary skill, LL-NNN)` identity plus exact change/test mapping in
existing creator metadata. Load the corresponding owner snapshot, not the
consumer's unrelated queue. The owner mapping uses existing task schema:
`owner={path: x-ipe-docs/planning/tasks/tasks-YYYY-MM-DD.json, task_id, owner}`.
The last owner value is the task's actual role. Allowed open statuses are pending,
in_progress, blocked, deferred. The helper only reads that task; no registration.
Do not steal another task's plan or adopt an expired/protected record.
Cross-owner applicability does not authorize editing that primary skill. If the
current change only targets a consumer and the primary candidate is out of scope,
retain the summary as guidance and report adoption unsupported/pending; never
invent a consumer-candidate path the helper does not accept.

```python
snapshot = ops.load(root, primary_skill)
planned = ops.settle(root, primary_skill, lesson_id, {
    "status": "planned", "owner": owner,
    "candidate": f"x-ipe-docs/skill-meta/{primary_skill}/candidate",
    "change": change, "test": verification,
}, expected_revision=snapshot["revision"], now=now)
```

## Settle after publication and actual production verification

```python
snapshot = ops.load(root, primary_skill)
applied = ops.settle(root, primary_skill, lesson_id, {
    "status": "applied", "task": task_id,
    "production_revision": production_revision,
    "publication_receipt": publication_receipt,
    "test_receipt": test_receipt,
}, expected_revision=snapshot["revision"], now=now)
```

The production revision is the sorted-compact complete manifest fingerprint,
not Git HEAD. Actual publisher JSON requires ok=true, operation=publish,
state=published, byte_parity=true, name, files, candidate_hash. Test JSON requires
ok=true, tests_passed=true, skill_name, production_revision, candidate_hash,
lesson_ids containing the scoped ID and verification exactly matching planned test.
The agent must establish test provenance and relevance; JSON alone is not proof.
Editor-promotion, YAML, historical partial manifests, unowned caches or mismatched
bytes are **not** compatible receipts. Do not forge/normalize them to bypass gates.
Report a blocked settlement and retain planned state. Identical owned replay is
unchanged without resetting clocks; reading/drafting never applies a lesson.

## Failed or unapproved publication

Retain planned, or explicitly release the same task's valid plan with a reason:

```python
snapshot = ops.load(root, primary_skill)
released = ops.settle(root, primary_skill, lesson_id, {
    "status": "active", "task": task_id, "reason": reason,
}, expected_revision=snapshot["revision"], now=now)
```

Conflict means reread/review, not blindly replace expected_revision and retry.
Expired releases block. No pruning, historical conversion, board/Git/memory
writes or approval fabrication in creator integration. If user excludes lesson
writes, select only and report pending settlement; do not create a parallel queue.

## Task template adoption

New/changed task skills load [common lifecycle](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md)
and [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md).
Map source/parent → goal/subgoal → stable story/leaf GWT AC/type → planned then
actual revision-bound checks in existing artifacts. All-required branches need
coverage; selected alternatives are bounded means, not mandatory backlog.
Legacy inference requires explicit so-that source. Missing intent blocks the
pertinent claim, not unrelated delivery. Observed outcome requires real evidence;
fixture/artifact checks and representative guidance leave outcome not measured.

The lifecycle owner performs registration, persistence and successor boundaries.
No child automatic next execution or type:routing calls. Exact three enums retain
the established external contract: interact-with-human asks the human within skill
and requires human completion/route confirmation; dao-represent-human-to-interact
uses bounded representative guidance within skill and selects only authorized
routes; dao-represent-human-to-interact-for-questions-in-skill uses bounded
representative guidance within skill and requires human completion/route
confirmation. Explicit domain human approval binds in every mode. Earlier
installed inverted clauses require candidate correction and reviewed promotion,
not inversion of the existing UI/config or a historical payload migration.