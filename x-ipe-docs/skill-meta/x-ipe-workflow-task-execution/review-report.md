# TASK-6749 — independent candidate review and publication

Reviewed 2026-10-13 as the reviewer of the previous builder's supplied candidate.
Authority: current user explicitly requested review, narrow candidate/tests fixes
and complete-file promotion via apply_patch only. No child/board/memory/Git work.
This is review of a prior builder bundle, not a claim of a newly spawned second
review agent. Narrow reviewer corrections were self-checked and rerun below.

## Findings and disposition

1. **Fixed — inverted hybrid policy.** User's exact contract: human interaction
   within skill, DAO only routing among already authorized successors. Human mode
   waits for human routing; full DAO handles bounded questions and routing. Hybrid
   alone adds no human routing confirmation. All explicit domain approval/release
   gates remain human; DAO guidance cannot expand scope or approve Git/release.
   Corrected entry, common reference, examples and regression assertions.
2. **Fixed — undeclared output flag.** require_human_review is optional, retained
   only when declared. Live implementation/change-request/closing omit it. Preserve
   task_completion_output, operation_output and workflow output, nullable links,
   conditional successors and full dynamic fields; no invented CRUD fields.
3. **Confirmed — actual ensure CLI.** Installed task_ensure.py --task creation
   JSON uses original ID/type/description/nonempty role. Real subprocess tests in
   temporary projects cover retry, owner/context conflicts, duplicate records,
   timestamps/outputs, terminal states and complete query pagination. No live
   board call. Owner is authorized session context, not nickname alone.
4. **Confirmed — one owner/safe operations.** Direct child Orient/Plan returns
   readiness without recursion; no second register/close/route/commit, no upfront
   chain, terminal resume never replays routing. Dirty/index safety is an instruction
   contract, not a real Git test: no Git commands run. Default uncommitted completion,
   exact approved paths only and separate push/PR permission remain explicit.
5. **Confirmed — mapping and states.** ACTION_MAP selects app implementation;
   tools.json implement.code_implementation selects enabled tools. Actual helpers
   read shared and feature-nested state. done plus required keyed artifacts is
   stronger than writer success; empty done outputs are accepted by writer and
   explicitly rejected by lifecycle policy. Task completed, action done and skill
   published are distinct; larger TASK-6749 board status was not changed.

## Known mismatches retained, not hidden or waived

- UI mode tests still describe hybrid as DAO inner-skill only. Enum transport
  tests pass but do not prove the corrected semantics; no UI/child edits made.
- feature-closing writes closing-report while its template action has no extract
  tags. Do not invent a supported tag or infer a report from writer success.
- change-request consumes closing-report; legacy test expects eval-report.
- acceptance-test initializes technical_design_link from impl-files, although
  those are implementation paths, not design.
- implementation task_output_links are src/ and tests/ directories; impl-files
  requires actual files, and impl-folder is a scalar folder. Collect changed files
  explicitly; no automatic directory-to-file conversion.
- Shared creator template uses workflow_output; this workflow keeps historical
  output. Separate creator/child adoption remains deferred, not performed here.
- Combined deliverable integration and autonomous instruction-following are not
  tested. Mandatory app/domain gates are not relaxed. Conflicting unmigrated
  children need a bounded explicit ownership/mapping adapter or execution blocks.

## Evidence at the published revision

Candidate: 90b220f8d92463eae43e18f7f2157c1cfd6ecb90a6f7fce0531173233186ed25.
Test: 092df266074e10ea6426f4ccce7f64c6118f2a0a8c1acb1abd3ded5c82f18c6b.
Consumer hashes: evidence-files.json; validation: validation-receipt.json.

- Focused lifecycle + creator foundation: 172 passed, including 27 lifecycle cases.
- Wider lifecycle/foundation/041g/workflow-stage/settings: 259 passed, 2 failed.
  Failures retained: change-request eval-report and historical 19-vs-22 skill count.
- Existing UI action-modal and workflow-panel mode tests: 34 passed. Transport
  evidence only; legacy hybrid wording is not semantic compatibility evidence.
- Installed validator: ok, 244 body lines, zero errors/warnings. Validator refuses
  live roots by design; production assurance is candidate validity + exact bytes,
  not a fabricated successful production-root validation.
- Read-only installed publisher dry-run: 3 changes, 2 additions, zero removals,
  zero protected conflicts. Apply mode deliberately not invoked: user requires
  patches and no destructive tree swaps. No automatic transactional recovery or
  new publisher lock claimed; patch receipt records this bounded exception.
- Five package files have exact candidate/production bytes. Protected 1,361-file
  digest (including existing caches, excluding workflow target/new lifecycle test)
  remains 5ddb9d2ca6d321425c9dac50c3763d41b88e6fab61cca6df73f49f59a8facc5e.

## Child refactor entry contract

Load production workflow and references/lifecycle.md, then adopt one validated
child candidate at a time. Direct entry ensures current original task once and
receives readiness; retain domain DoR/DoD/TDD, config-gated tool selection, exact
mode and input tags. Delegate board/Git/boundary to one owner. Return domain output
and real links unchanged; suggestions never execute a successor. Verify revisions
and action artifacts before completion; record mismatches rather than fake done.
