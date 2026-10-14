# TASK-6749 — step 3: task-board manager

> Historical candidate plan below. The 2026-10-13 user-authorized fresh independent
> review and file-scoped promotion supersede its candidate-only blockers; see
> independent-review.md, publication-journal.json and publication-receipt.json.
> No cache deletion, directory replacement or fabricated prior ownership occurred.

## Scope and readiness

- Existing lifecycle task: TASK-6749; no duplicate task, nickname registration,
  board/memory/git writes, unrelated edits, or wrapper removal authorized.
- Loaded installed board skill first, then current installed skill creator,
  general guidelines, x-ipe-tool and skill-meta-x-ipe-tool templates.
- Risk: high (shared persistent state, ownership, concurrent allocation).
- Independent runSubagent capability unavailable in this session. Draft and
  validate only; no promotion, production version-history change, or publication
  receipt. Self-review is not independent review.
- Source package baseline captured before drafting in baseline.json. No trusted
  managed inventory was supplied or established; managed.json is empty, not a
  fabricated claim to current source ownership. This independently blocks release.

## Evidence and smallest delta

1. LL-001 raw record independently checked against parsers, TASK_SCHEMA_V1,
   TaskBoardService, feature consumers, and CRUD tests. Selected mapping:
   executable JSON examples; --range all plus complete pagination for ownership;
   exact role comparison rather than substring search; completed canonical status.
   The record is not migrated, settled, or marked applied without publication.
2. No generator or ensure helper exists. Add optional omitted-ID allocation to
   task_create and supplied-ID task_ensure; retain explicit IDs such as T1.
   Ensure validates the same creation payload and exact role/task_type/description,
   returns current task without changing status, outputs, routing, or timestamps.
   Foreign/unassigned ownership is never silently claimed. Missing ID in ensure
   is an error, not a new allocation on every retry.
3. Add shared task-store helpers, not a new task schema or arbitrary assignee.
   Allocate max numeric TASK suffix + 1 under index lock after today's daily lock.
   Reserve all index IDs and IDs in all dated live/archived files, including
   unindexed records. Corrupt state fails closed instead of being overwritten.
4. Preserve daily → index order; do not acquire another daily lock under index.
   Fix migration's reverse lock order and write current dictionary index entries;
   preserve parsing, summaries, feature operations, and migration CLI.
5. Validate create/update statuses after type validation; reject invalid pagination
   before list division. Query remains read-only, with existing default 1w and no
   --assignee. Document snapshots are not linearizable multi-file transactions.
6. Existing API tests verify historical list daily files; candidate writers must
  preserve those bytes/format as well as CRUD object envelopes. Query/update/archive
  therefore accept both daily forms and historical string index entries. Ownership
  query fails closed on malformed daily files. Update rechecks the index before
  committing; archive validates it before rename and rechecks archive existence
  under daily lock to avoid concurrent overwrite. Schemas and API/UI untouched.

## Complete candidate inventory

- Preserve the nine existing Python sources (unchanged resources byte-exact).
- Replace SKILL.md using tool template; add references/examples.md.
- Add scripts/_task_store.py and scripts/task_ensure.py; no resource deletions.
- Production has ten __pycache__ bytecode files. Baseline includes every one.
  They are unmanaged generated runtime artifacts, not source resources. Candidate
  intentionally omits them; this is an explicit proposed omission, NOT approved
  deletion. Do not publish or delete them without ownership/review disposition.
- Existing legacy wrappers and external lesson record remain untouched.
- Tests and receipts live outside candidate. Existing production scripts remain
  unchanged; run candidate CRUD via preloaded modules, with assertions on origins.

## Scenarios and verification plan

- Bootstrap, explicit IDs, omitted IDs, archived/unindexed numeric high-water IDs,
  foreign/context mismatch, read-only completed resume, supplied missing ID create,
  concurrent same-ID ensure/create and distinct automatic creates on multiple dates.
- All-date paginated ownership: older in-progress record beyond first page;
  exact role comparison excludes description-only nickname matches.
- Fault between daily and index write: no reallocation/reuse; inconsistent resume
  fails without repair. Malformed files/index preserve bytes; no silent reset.
- Mixed create/update/archive/migrate overlap: no inverse acquisition or deadlock,
  index and dated file consistency. Locks are cooperative; external writers are
  not covered. Atomic per-file replace is not a two-file transaction.
- Existing board library, task/feature CRUD, migration, APIs, page tests; add
  candidate-output API interoperability assertions. Verified first run exposed
  existing API get ignoring object envelopes even on fallback scan. List supports
  both formats. Record strict expected failure; do not change application code or
  claim full task-get compatibility without separately authorized service fix.
- Installed creator validator receipt with candidate fingerprint. Compare full
  baseline again and report source parity, missing bytecode, warnings, and gaps.

## Publication boundary

Candidate-ready is allowed only with passing checks and explicit gaps. Independent
review, trusted managed ownership and generated-file disposition are prerequisites
to any future release. User requires apply_patch-only promotion after review;
do not run publisher --apply or replace production directories in this session.
