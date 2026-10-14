# TASK-6749 — shared lifecycle candidate plan

## Scope and authority

Resume TASK-6749 (Quill, Code Refactor) using installed task_ensure.py with
the original description/role/task_type. Result: created=false; unchanged
in_progress record. This is one slice of the larger task, not task completion.
Permitted writes: this workflow candidate and metadata, tests/test_skill_lifecycle.py.
No promotion, live board updates, memory writes, Git mutations, app/source changes,
child skill migration, or creator changes. Independent reviewer is next.

## Loaded foundations and provenance

Loaded promoted creator, general guidelines, workflow orchestration scaffold,
task-based metadata scaffold, live workflow, board manager and actual CLI,
representative contract, workflow template, tools config and app interactor.
Production workflow and existing tracked candidate are clean relative to Git.
Production has three resources; candidate had four and stale Markdown-board
instructions. Preserve intentional behavior, replace stale examples and record
template, retain candidate-only templates/task-board.md as a non-authoritative
compatibility tombstone (not a live board or deletion).
No relevant workflow lesson files found; zero lessons selected or modified.

## Plan

1. Orient: one approved root/owner, dynamic skill/category discovery, exact
   mode policy, dirty baseline, validated source artifacts and action identity.
2. Plan: ensure/resume the supplied task; never allocate speculative chains;
   explicit smallest justified deliverables and revision-sensitive verification.
3. Execute: domain-only child work; direct child entry calls lifecycle first;
   no recursive workflow/domain invocation or second routing/board/Git owner.
4. Verify: domain gates, required action done with keyed real deliverables,
   fresh source/implementation/test evidence, proportionate independent review.
5. Record: persist verified lifecycle status only, approved paths only for Git,
   one mode-aware boundary and newly authorized task registration on routing.

## Compatibility evidence

- Live workflow Step 5/6: hybrid stops for human completion review; representative
  recommendation may be displayed, but human confirms next task.
- Representative returns operation_output.result.instruction_units and
  execution_plan, not legacy type:routing / completed_skill_output inputs.
  approval is guidance, not human permission; bounded scope cannot expand intent.
- UI emits --interaction@MODE; CR001 JS tests preserve exact hybrid enum and
  identify it as DAO inner-skill only. Legacy --proceed flags remain adapters.
- workflow-stage.js ACTION_MAP is authoritative action-to-skill identity;
  workflow-template.json defines stage type, context and extract tags.
  implementation action differs from tools.json implement.code_implementation.
- Existing action writer accepts skipped and missing deliverables; therefore
  lifecycle must verify done + complete artifacts, not merely non-pending.
  No app skips or gate relaxations are introduced.

## Small-path contract

Clear low-risk work may combine planning/specification/design notes and tests in
one linked artifact with explicit sections. This does not auto-complete an app
action, skip a mandatory stage, waive TDD, or claim release/promotion. Child
migration and runtime combined-deliverable integration need separately tested work.

## Tests and evidence

Content tests parse five phases, common output/status contracts, modes, ownership,
Git safety, mapping sources, links and freshness requirements. Behavior tests use
installed board CLI subprocesses in tmp_path only (ensure/retry/context/owner/
terminal states), installed validator hashes and publisher stale-hash refusal,
and actual workflow writer against temporary state. Text contracts are not a
runtime proof of autonomous agent decisions; no shadow lifecycle emulator added.
Record final candidate fingerprint + test digest + consumer fingerprints;
any changed tested input invalidates affected evidence. Independent review blocks
promotion, not candidate drafting. Do not update published version history.

## Follow-up (not performed)

Creator-owned workflow template currently defaults to generic workflow_output,
while this compatibility workflow retains its existing output aggregate. Submit
a separate creator candidate revision for shared lifecycle adoption guidance;
do not edit concurrent creator candidates or rename existing output schemas.
Later child candidates must load the common lifecycle contract explicitly and
remove their duplicate registration/routing, validated one at a time.
