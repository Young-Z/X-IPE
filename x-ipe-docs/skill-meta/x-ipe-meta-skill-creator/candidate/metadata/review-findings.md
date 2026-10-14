# TASK-6749 — Round 2 Independent Reflection

Date: 2026-10-13. Role: Reflector & Test Generator. Bootstrap authority: the
current production creator's OLD step 6 (reflection/test generation), not the
candidate's proposed simplified process. Round 3 execution and Round 4 evaluation
are still required. **No tests have been run; no pass rate is claimed.**

## Scope and Evidence

Read the candidate entry, validator, publisher, validation/publication reference,
creator metadata/criteria, selected LL-001, retained template/reference contracts,
and current production creator. Compared against the TASK-6747 P1 foundation and
validation matrix and TASK-6748 creator evidence/lesson boundaries. The existing
TASK-6749 board entry was read, not modified; no duplicate task was created.

Direct interface inspection used importlib with bytecode disabled. The actual
`publish(project_root, candidate, name, skill_type, baseline, managed,
expected_candidate_hash, reviewed_deletions=(), apply=False, hook=None)` and
`recover(project_root, name, transaction, apply=False)` signatures match the API
reference. The validator dependency was explicitly registered in `sys.modules`
before loading the publisher, as its sibling import requires. This verified
loading/signatures only, not runtime safety or a publication result.

Executable scenarios are in tests/test_skill_creator_foundation.py. Test cases
are recorded beside this review in test-cases.yaml. These metadata sources stay
inside the permitted candidate boundary; the publisher currently inventories
them as ordinary candidate resources. They are not validation/publication receipts.

## Concrete Findings and Narrow Fixes

### R2-F01 — Contract-tag prefix lookalikes accepted (correctness)

Evidence: validator block checks previously used substring membership, so
`<input_init_fake>` and `<operation_fake>` satisfied checks for `<input_init` and
`<operation`. This contradicts the declared corresponding-block contract.

Candidate fix: require the actual opening name to be followed by whitespace,
`/`, or `>`. Regression: test_contract_prefix_lookalike_rejected. This is a bounded
tag-name check, **not** XML parsing or proof of balanced executable procedures.
Fix is authored; runtime verification is deferred to Round 3.

### R2-F02 — Unexpected new-skill recovery backup could enter production (high)

Evidence: in an intermediate recovery journal with `target_existed: false`,
backup hashes were not checked; the later unconditional `if backup.exists()`
branch renamed that backup into production. Parity was checked only afterward.
An unexpected backup could therefore mutate production before recovery failed.

Candidate fix: reject a new-skill intermediate journal with nonempty baseline or
any existing backup before recovery mutations. Regression:
test_new_recovery_rejects_impossible_backup_or_baseline snapshots the full tree
and expects rejection with unchanged bytes/directories. Runtime verification pending.

### R2-F03 — Durable published state mislabeled as rolled back (correctness)

Evidence: the publication exception path called recovery but discarded its
receipt, then unconditionally raised “rolled back.” Recovery explicitly returns
`published` for an already journaled terminal publication, without restoring the
baseline. A late journal/fsync/cleanup exception can reach this path.

Candidate fix: if recovery confirms terminal `published`, return the published
receipt with transaction/parity rather than a false rollback report. Regression:
test_durable_published_journal_failure_not_reported_as_rollback injects an error
after the real terminal journal write. Persistent recovery/lock failures still
retain evidence and return recovery-required errors. Runtime verification pending.

## Test Design and Plan Alignment

- **145 statically expanded cases in 44 test functions.** This count comes from
  AST parameter-list lengths, not pytest collection or execution. Interface
  inspection and AST syntax inspection do not establish that these tests pass.
- Boundary matrix covers 999/1000/1001 BODY lines, blanks, substantial excluded
  frontmatter, LF/CRLF, and optional final newline. Invalid/missing/mismatched
  frontmatter and invalid identities fail without filesystem changes.
- Eight synthetic subtype contracts separate operations from procedures and task
  routing. Real template presence and copied creator bundle are checked separately.
  Minimal fixtures do not pretend to prove actual domain-schema compatibility.
- Resource cases distinguish candidate-self from actual external sources; a
  live-only resource cannot mask a candidate omission. Hidden files, encoded
  links, image/reference targets, symlinks, traversal, hard links, and FIFO are covered.
- New/update dry-runs compare the whole temporary tree, including directories and
  modes. Applied new/update scenarios compare all bytes, hidden/resources,
  retained baseline backups, terminal journals, and cooperative lock cleanup.
- Ownership cases cover dirty/unmanaged retention versus change/removal,
  preexisting managed deletions, exact reviewed removal lists, and immutable
  supplied ownership maps. Concurrent baseline/candidate edits invalidate review;
  staged target edits and later target/backup edits must remain protected.
- Faults at staged/backed_up/installed, unequal stage inventory, failed installation,
  failed rollback restoration, explicit recovery, terminal replay, wrong roots,
  mismatched locks/journals, missing/corrupt backups, and conflicting failed trees
  are covered without touching real skills. Interrupted-process tests model
  persisted journals; they do not execute process kills or power failures.
- LL-001 maps to missing-self-resource, complete new/update byte parity, and
  protected-file tests. Historical `raw` remains unchanged. Neither this review
  nor a future isolated test pass authorizes applied lesson status or promotion.

## Remaining Review Limits / Decisions Before Promotion

1. **Filesystem race/durability boundary:** path checks and inventories use
   pathname operations rather than anchored directory descriptors. Cooperative
   locks plus rechecks do not exclude a hostile noncooperating writer between
   a check and use. Stage directory entries are not explicitly fsynced throughout
   the tree. The reference already disclaims seamless exchange/power-loss safety.
   No hostile-writer or power-loss certification is made; decide the supported
   threat/durability model before release, and harden if a stronger guarantee is required.
2. **Pre-journal crash:** a hard termination after acquiring/writing the lock but
   before the first complete journal can leave a transaction with no recoverable
   journal. Production has not yet been swapped, but automated recovery cannot
   authenticate that transaction. Stop the old publisher and review manually;
   never steal the lock blindly. The suite models journaled interruptions only.
3. **Manifest limits and provenance:** manifests cover file bytes, not empty
   directory ownership, modes, or source-control provenance. Meaningful unmanaged
   state must not reside only in empty directories. Trusted managed hashes and
   release permission are caller/reviewer responsibilities, not facts inferred
   from a matching baseline or successful receipt.
4. **Structural checks are bounded:** Markdown scanning is not CommonMark; tag
   checks are not XML/schema validation; nonempty descriptions do not prove trigger
   quality. Operation-specific output schemas, actual workflow/config consumers,
   full template section-order rubric, and bidirectional references need semantic
   review. Preserve the existing subtype/domain contracts rather than forcing
   task routing or inventing a generic schema. No global compatibility claim.
5. **Retained reference drift:** examples still show a historical recursive-copy
   merge and legacy subtype/template names; the candidate entry explicitly says
   legacy examples are illustrative, not mandatory. The type-comparison reference
   still describes task-based skills as owning board entries and full phase
   backbones, whereas the revised task-based template allows flat steps and the
   creator takes an existing lifecycle task. Reconcile these instructional
   contradictions before final evaluation; this review did not rewrite retained
   domain resources or silently resolve P2 lifecycle migration decisions.
6. **Round state:** metadata still records Round 1/`not_executed`, honestly.
   Round 2 sources supplement it rather than rewriting historical status/history.
   Tests and fixes require Round 3 execution and Round 4 must/should evaluation.
   Review alone is not permission to publish or declare acceptance complete.

## Handoff

Expected Round 3 command (not executed):

`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -p no:cacheprovider tests/test_skill_creator_foundation.py -q`

No promotion, board/memory/git writes, historical lesson changes, or version-history
changes were performed. Only candidate scripts, candidate Round 2 metadata, and
the scoped new pytest file were edited with apply_patch. Return failures honestly;
do not weaken assertions to obtain green or run tests against live production.