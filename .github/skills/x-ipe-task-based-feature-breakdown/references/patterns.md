# Feature Breakdown: Patterns & Anti-Patterns

## Pattern: Fresh clear requirements / one feature

**When:** Approved source findings still match current revisions.
**Then:** Reuse scope and acceptance; record grouping, one runnable MVP, coverage
and real direct dependencies. Populate the selected Feature List and details;
register/query a real Planned feature and verify both workflow artifacts when
applicable. No artificial split, second intake Epic or duplicate lifecycle task.

## Pattern: Material ambiguity

**When:** Scope, MVP value, overlap or delivery priority is genuinely unresolved.
**Then:** Ask the human in human mode; use bounded representative guidance
in full DAO and hybrid per the common lifecycle. Record the answer and its revisions.
Human and hybrid require human completion/route confirmation. Explicit human
approval binds in every mode.
Do not convert an assumption into approval. Confirm the final list is complete
before refinement under the retained domain gate; no successor execution here.

## Pattern: Large multi-domain scope

**When:** Approved requirements need more than seven features or multiple clusters.
**Then:** Group by domains/dependencies/team boundaries before assigning IDs.
Reuse intake Epic and justify additional collision-checked groups, with a
vertical runnable MVP per new Epic and <=7 features per Epic. Cover EVERY source
FR/AC or explicitly approved deferral; never truncate the overall list to seven.

## Pattern: Incremental CR / unchanged resume

**When:** Existing legacy/new features are affected by an approved narrow delta.
**Then:** Update only owning rows/details and authorized board fields. Preserve
IDs/Epic/status/specifications/unrelated parts and feature-stage history. Matching
resume reads rather than creates/appends. Existing workflow graph changes need
supported authorized reconciliation or a blocked partial result.

## Pattern: Genuine split with parent dedup

**When:** A parent needs splitting along independently deliverable boundaries.
**Then:** Map every parent FR/AC to child ACs. Partial coverage keeps the parent
active and reports dedup_gaps. Full coverage PLUS explicit retirement authority
permits Retired via feature_update.py and removal from the active breakdown with
history/redirects retained. Verify both before parent_features_removed; do not
delete a board record. Reconcile incoming dependencies before retirement.

## Anti-Patterns

| Anti-Pattern | Consequence | Correction |
| --- | --- | --- |
| Duplicate lifecycle/routing | Multiple tasks or unapproved successors | Return once to common lifecycle owner |
| Interface-only MVP | No runnable user/core outcome | Vertical minimum, then enhancements |
| Truncate large scope | Lost requirements | Regroup and record coverage/approved deferrals |
| Renumber legacy features | Broken references/history | Reserve new suffixes; preserve existing identity |
| Transitive/self/circular edges | Misleading or impossible order | Direct reasons and validated combined DAG |
| Reset existing features to Planned | Lost progress | Only new records Planned; approved mutable CR delta |
| Remove parent automatically | Lost coverage/history | Full coverage, authority, Retired readback and redirects |
| Replay workflow feature payload | Duplicate IDs and reset stages | Query first; absent new entries only |
| Writer success treated as completion | False done despite missing artifacts/gates | Exact artifact and prerequisite readback |

See [integration](.github/skills/x-ipe-task-based-feature-breakdown/references/integration.md)
for installed CLI shapes, corrupt-store guards and append-only limitations.
