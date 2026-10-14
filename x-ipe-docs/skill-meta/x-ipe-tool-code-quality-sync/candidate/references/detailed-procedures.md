# Quality sync — domain reconciliation and evidence

## Source authority before edits

Read actual analysis and selected intent sources, their dates/anchors/content/hash,
approved requirements/story/GWT AC/type/design and caller scope/exclusions.
Source-authoritative user goals outrank accidental implementation. Conflicting
approved sources need a bounded owner decision, not automatic precedence by date.
Explicit broken/ambiguous selected link blocks; validate root containment and
symlink escape, not merely existence. Reuse actual identities and unaffected
history. No new goal database, board fields or artifact mandatory infrastructure.

Map each affected goal/subgoal to parent/source/stakeholder, direct or indirect
contribution, baseline and intended observable success, constraints/non-goals,
all-required children or selected alternatives, existing story/AC/test type and
actual evidence. Alternatives are bounded means, not a backlog of all options.
Legacy so-that can be labeled inferred with anchor; missing intent blocks only
the pertinent goal-coverage/outcome claim. Numeric improvement requires comparable
observations; a concrete qualitative scenario can suffice when appropriate.

## Classification and authorized actions

| Finding | Authority comparison | Action in authorized local/broad sync |
| --- | --- | --- |
| Descriptive doc drift | Approved behavior and current checks agree; docs stale | Correct affected descriptions/links, retain IDs/ACs, date/hash the update |
| Undocumented implementation | Approval not evidenced | Labeled observed-current-state note; no new requirement/AC or approved status |
| Unimplemented requirement | Approved intent not delivered | Retain requirement and gap; no deletion, scope amendment or source repair |
| Deviated behavior | Code violates approved behavior | Bug finding plus failing evidence; do not skip/xfail/delete to mask failure |
| Intentional change | User requests different goal/acceptance/constraint | CR boundary; actual human authority required, tool returns to owner |
| Conflicting intent | Relevant approved sources disagree | Record exact sources and unresolved question; no unilateral resolution |
| Missing source/doc | Not found or inaccessible | Record not_found/unavailable; authorized observational draft is not approved intent |

Study performs these comparisons without edits, except an authorized report.
Do not append bug paths to passed-through authorized refactor scope, reinterpret
DAO guidance as approval or run another task inside this tool.

## Requirements, features and technical design

Requirements retain gap vocabulary undocumented/unimplemented/deviated and
related_docs; verify desired outcome, constraints and implementation contribution.
Document actual discovered behavior only as observation until approval is cited.
No timing/token/security guarantees inferred from code examples or invented tests.

Feature/specification retains missing/extra/deviated gaps, spec_docs, feature IDs,
US/AC IDs, GWT criteria and original test types. Map each affected leaf AC to its
goal and test; a passing implementation test of the wrong behavior is divergence.
Use separate feature_alignment when supplied; specification summary does not
collapse independent missing technical evidence into aligned.

Technical design retains structure/interface/data_model/pattern gaps and real
component/directory/API/schema/pattern links. Describe observed architecture and
approved design separately when they diverge. Correct an approved functional API
description without inventing APIs/types. Record actual date, changed paths and
source/doc/config fingerprints in Design Change Log. Absent design may become
an explicitly observational draft only in approved paths, not automatic approval.

Tracing is preserved, not installed: inspect actual tracing_enabled and existing
infrastructure/redaction/decorators where implicated. Disabled/absent tracing or
skills/documents requires no newinfra. Existing security/redaction losses remain
critical findings. Retain tracing_coverage and all analysis extensions unchanged
unless current scoped evidence supports an explicit field-level update.

## Mode and risk matrix

| Mode | Docs | Tests and measurements | Readiness |
| --- | --- | --- | --- |
| study-only | Read-only gap assessment; authorized report only | Inspect existing results or run authorized read-only checks; propose missing characterization | Always false for mutation; complete assessment may succeed |
| local | Only affected authorized descriptive docs and preservation tests | Critical changed paths, implicated callers, applicable test/build/lint; no blanket coverage/full-suite gate | Required current preservation/intent evidence and approved baseline failure disposition |
| broad | All relevant affected docs within approved scope | Planned relevant integration/full suite; comparable scoped coverage when applicable | Same critical gates; applicable authoritative thresholds only |

Broad line80 default: 80% line coverage is a guideline for scoped executable code,
not a universal DoD gate or proof of preserved goals. Below-guideline coverage can
coexist with justified critical-path preservation. Above-guideline coverage cannot
excuse a missing critical error/security path. A project's applicable authoritative
policy can require a threshold; cite its source and denominator. Never silently
lower that policy, or impose it on unrelated code/skills/docs without applicability.
Do not execute unbounded coverage loops. Report remaining risk and planned work.

## Critical base-to-target characterization

Identify changed approved doc/test/implementation paths from actual base/target
bytes or supplied revision diff. Inspection of callers/shared state/imports/config
is not additional write authority. Preserve public imports/exports/results/errors,
data/side effects and implicated async/concurrency/security/external boundaries.
Cover happy/error/edge scenarios with unchanged acceptance assertions. Run existing
and authorized added preservation assertions against base and target, keep their
hashes and actual results. Refactor characterization tests need not fail first.

Do not assert preservation from target-only green, coverage alone, stale output,
changed expected results or a current implementation characterization that conflicts
with approval. An exposed approved-behavior bug is a bug finding, not accepted
characterization. Preserve the failure; no automatic skip/xfail or incidental fix.
Record base failures separately, classify goal/path impact and any exact approved
safe disposition. Unresolved required critical failures/new regressions block
readiness. Unrelated suite failures remain visible but do not force global repair.

Use domain evidence: actual configured browser for UI claims, API/CLI/library
checks for those contracts, existing skill validator/schema/resource checks plus
disposable scenarios for skills/docs. An authored fixture verifies that fixture,
not autonomous agent execution or production behavior. No forced new tracing,
coverage framework, integration service or compile infrastructure.

## Freshness, states and counts

Each evidence record: actual date, source/anchor, goal/AC/type, base/target hashes,
test/doc/config hashes, command, cwd, exit, observed result, applicability and
limitations. Missing command/check has exit=null, not a failure exit or fabricated
pass. Attempted failure has its actual exit/result. Missing docs remain not_found;
not applicable needs a reason. Alignment_state aligned/divergent/unavailable is
separate from measurement/test statuses. divergent requires contradictory evidence;
unavailable never means aligned or measured zero.

After any edit invalidate affected evidence and rerun its checks; preserve unrelated
history. Fingerprints bind the actual source/test/docs/config and review, not just
a timestamp. Historical metrics may be retained with provenance, never relabeled
as current. Scores number|null require a comparable actual authoritative rubric;
no invented weights or smell-count aggregate. Percentage line_coverage string|null;
legacy current_percentage number passes through with provenance and conflicts,
not silently overwritten by a differently scoped line value.

Count actual distinct docs created/updated and tests added/updated; report paths
and counting basis. A report is not an invented requirement/feature doc or test.
Requirements/spec/design gaps clear only when evidence resolves them, not because
a file was edited. code_alignment remains exact input, new bugs appear in report.
Pass-through scope, target_structure, goals, suggestions and principles remain exact.

## Operation versus readiness and consumer limits

success=true means all authorized sync/assessment activities and report delivered
with honest dispositions, even if a completed assessment exposes a preservation
gap. ready_for_refactoring=false for study, unresolved critical intent/preservation
failure or required unavailable evidence. Required operation/check execution errors,
unauthorized writes or incomplete deliverable return success=false and actual
partial result/errors. Neither success nor readiness proves stakeholder outcome;
delivery may be evidenced while stakeholder outcome remains not measured.

Re-read installed caller and strict consumer contracts. The refactor caller's old
integration snapshot still describes the legacy sync; do not edit that dependency
in this task or claim migration. This candidate's modes/status/nullability are not
installed until reviewed promotion. Consumers rejecting null/new states are a
disclosed handoff blocker; never stringify null, force zero or claim compatibility.
