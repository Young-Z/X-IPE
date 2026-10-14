# TASK-6749 — final reviewer findings and authored corrections

2026-10-14. GitHub Copilot reviewing the prior builder's implementation report,
creator/representative bundles and current app consumers. No newly spawned
reviewer is claimed. Supplied TASK-6749 reused; **no real project-board, memory
or Git operations** and no unrelated knowledge/history edits. Tests exercise
board/lesson helpers only in disposable fixtures, as requested. Corrections use editor
operations only. No skill package published; no version history advanced.

## Verdict and source authority

**Reject full integration/publication certification at this revision.** The prior
review's claim that the user requested hybrid inversion is unsupported. Current
user explicitly requires preserving the established external contract, not
silently changing UI or requiring an unrequested mode redesign.

Authoritative current source:
- [FEATURE-044-E AC-044-E.4](x-ipe-docs/requirements/EPIC-044/FEATURE-044-E/specification.md):
  DAO represents human for inner-skill questions only.
- [CR-002 enum/UI contract](x-ipe-docs/requirements/EPIC-044/FEATURE-044-E/CR-002.md),
  [existing UI](src/x_ipe/static/js/features/workflow.js) and
  [existing modal transport tests](tests/frontend-js/action-execution-modal-cr001.test.js).
- [Current workflow config](x-ipe-docs/config/workflow-template.json) and
  [bundled config](src/x_ipe/resources/config/workflow-template.json) preserve
  the enum/default; [service](src/x_ipe/services/workflow_manager_service.py)
  accepts these exact enums. None of these app/config/spec files was edited.

Current policy: human questions + human boundary; full DAO bounded questions +
authorized DAO routing; hybrid bounded DAO questions + human completion/route
confirmation. Explicit product scope/acceptance/publication/release/Git/destructive
authority and domain-required human approvals remain binding in all modes.

There is a real baseline conflict: earlier stop_for_question requirements and
older instruction/skill clauses describe human questions with automatic routing;
the more recent named-enum spec/UI describe the opposite. This is recorded, not
hidden by renaming enums or rewriting historical requirements. Prior review and
publication receipts remain historical evidence; they cannot authorize inversion.

## Prior authored deltas independently inspected

| Scope | Findings | Disposition |
| --- | --- | --- |
| Creator select/plan/settle guidance | Actual installed APIs, explicit roots/revisions, canonical owned candidate/task mapping, four selection result keys, bounded protected/expired handling | No safety blocker found in this original delta; read-only selection is not applied status |
| Receipt safety | Actual publication manifest + matching relevant verification required; JSON alone cannot authenticate test provenance; editor-only receipts and compiled-cache partial manifests cannot be laundered | No invented settlement/provenance/migration; real queues untouched |
| Validator identity | Exact existing capital Engineer assistant only; name/subtype/frontmatter/path/line/resource/checkpoint gates retained; wrong subtype, suffix/lookalike and arbitrary uppercase reject | Proposed executable exception reviewed/tested; unchanged installed validator still rejects legacy identity |
| Task template | Goal/source/AC/type/evidence and one owner are appropriate; original input/output blocks unchanged; child successor/type:routing removed | Original question branch inverted hybrid; corrected in candidate, needs later independent review |
| Representative | Existing message_context/operation_output, seven dispositions, 1–3 units, dependency plan, phase order, append-only log and human_shadow fallback preserved | Bounded original candidate inspected; no caller-mode override, successor execution or new goal input/schema |

Representative scenarios are authored plans, not executed decision pilots. Passing
content/schema tests do not prove autonomous judgment, logging execution, actual
human approvals or stakeholder benefit. A fixture admission ground_truth string
is synthetic test input, not a real project admission or stakeholder observation.

## Reviewer-authored corrections — pending independent review

1. Workflow candidate entry/common/examples restore current spec/UI hybrid
   policy and require an explicit adapter or block conflicting child invocation.
   Refresh repaired acceptance/closing mismatch descriptions, retaining CR's
   eval-report baseline conflict and actual action/tag/file-array boundaries.
2. Creator task-template candidate routes only actual questions through both
   DAO modes; human mode waits, hybrid boundary waits for human. Existing task
   inputs and full output declaration remain byte-identical to installed template.
3. [Canonical English instructions](.github/copilot-instructions.md), EN/ZH
   resources and both CLI templates use single owner ensure/resume, document-local
   goal/evidence and selective lesson admission. Remove duplicated hardcoded
   child phase registration/completion and blanket review bypass. Actual DAO
   interception remains only in DAO variants; no-DAO variants have no gateway or
   unit-plan loop. Clear within-skill inputs require no ceremonial DAO call.
4. EN no-DAO resource and CLI template exactly equal canonical local bytes;
   EN DAO and DAO CLI bytes are equal and removing only the gateway reproduces
   canonical. The same gateway-only distinction holds for localized ZH variants.
   Existing ScaffoldManager and SkillTranslator generate those exact resources
   in temporary projects; forced upgrade tested across EN/ZH and both settings.
   Existing non-forced merge semantics are unchanged, not certified idempotent.
5. Tests now bind candidate semantics to the current source instead of the prior
   unsupported review assertion. Publication census checks all installed bytes
   against historical receipts; the changed workflow candidate is explicitly
   non-parity/pending rather than falsely reported as installed or skipped.

The workflow correction was staged/validated before instruction integration.
It is **not independently approved or published**: new authoring in this reviewer
session cannot be its own independent review. Instruction edits are in tracked
working files as requested, not a certified release. Installed lifecycle/ten
adopting children still invert hybrid; their tests characterize those installed
clauses and do not establish compatibility. Further changes must stage each child
through creator, preserve original domain approvals and refresh review/evidence.
No unsafe live invocation is endorsed while the conflict remains.

## Exact package revisions and real validation

| Bundle | Candidate fingerprint | Unchanged installed fingerprint | State |
| --- | --- | --- | --- |
| Workflow | b79761fd9d6c36700b1312dc98b7e6b69c7099e14e05d8a10ded9f6ef21dcc00 | 89ddfa5a1abd55dca9a5e16177340c806fa194e575e5c3cd58396fa8e40d4764 | 6 files, 250 body lines; corrected candidate pending review |
| Creator | 934eb129a59b92f9947c04f7fcb03cdbbcacd9679cc179757e2d6735dbda9752 | 72caec919101f8333dbaacc6ec504756c31b9facc607d9d764d314ca29b92cfd | 33 distributables, 259 body lines; complete candidate pending review |
| Representative | 37b3921d4486ecce4c0fb49a0ca2b6c374c6d2dadeef2740fed8246c3022e8e8 | 9ec07b8bb2a7c5e99dced66bdc9950e1befa5e78be6d091203fce8cdae27962f | 8 files, 339 body lines; reviewed original delta, not promoted |

Creator's installed physical fingerprint includes two unchanged unmanaged compiled
caches; distributable fingerprint remains 762d5ef4818aba6ca16ad1dfb75b646b74eddcc2f46f3ef90252829c5d5ea271.
All three actual candidate validator APIs equal actual CLI JSON, zero warnings or
errors. Explicit creator-candidate helper bootstrap is disclosed, not substituted
as installed-tool success. Installed creator validation still accepts creator and
workflow; installed representative identity failure remains in regression tests.
See [workflow receipt](x-ipe-docs/skill-meta/x-ipe-workflow-task-execution/review-evidence-TASK-6749.json)
and [current integration evaluation](x-ipe-docs/skill-meta/x-ipe-meta-skill-creator/integration-evaluation-TASK-6749.json).
The [root validation record](x-ipe-docs/skill-meta/x-ipe-meta-skill-creator/review-validation-TASK-6749.json)
contains actual complete creator/representative receipts and current instruction,
changed-test and source hashes, not a forged root publication receipt.

No root publication receipt, lock, transaction, parity or version increment was
fabricated. No publisher apply was invoked. Later publication must validate/review
current hashes, recheck allowed live baselines, apply exact reviewed editor delta,
verify complete distributables plus preserved caches, then record actual parity,
root publication receipt and version history. Editor receipts stay incompatible
with lesson settlement; do not claim applied lessons from them.

## Verification and remaining failures

- Independent baseline: new integration 22 passed; full focused 1,041 passed.
- New source-grounded review regressions before correction: 10 failed / 1 passed.
- Final full focused: **1,058 passed**, 19 files, 32.20s, exit 0.
- Final broad: **1,457 passed / 8 failed**, 30 files, 33.73s, exit 1.
- Entire npm frontend: **51 files / 1,016 passed**, 4.92s, exit 0.
- No skip, xfail or deselection. Python 3.12.9 configured venv, -B,
  PYTHONDONTWRITEBYTECODE=1, PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, -p no:cacheprovider,
  --noconftest, -q --tb=short. Focused matrix is the implementation report's 18
  named focused files plus [review tests](tests/test_review_6749.py); broad is its
  29 named files plus the same new file. npm test -- --reporter=dot.
- The eight unchanged failure identities are original three CLI destination,
  two workflow tag and three representative entry-only logging assertions.
  Canonical instruction sync is now repaired; no logging/domain assertions were
  removed to conceal baseline failures. Existing transport/quality suites retained.
- Editor diagnostics: no errors in five changed Python test files or workflow
  receipt. No lint-clean-all, browser, wheel/release or autonomous pilot claim.
- During authoring, the patch engine mishandled same-path delete/add replacement;
  the full instruction text was corrected via editor fallback, then byte-tested.
  Two EN DAO terminal-newline differences were repaired before the final runs.

## Protected mirrors and return state

AGENTS and CLAUDE each retain 44623afbbab53bad175960ca54c942e644aeca0768c133af86685bcb62dfb1a7.
Complete .claude tree: 1,492 files, 67508b3224a9d493ad4be37fb99a2af2e41648ba57671243cc022a06cbe8bfda.
Complete codex tree: 1,711 files, 6b3dca304a7bd22d87b3cad247aad6cb8f0655e55d682d5f571c8f36a9b68cca.
These are read-only content fingerprints, not Git/index/dirty-state assertions.
They were rechecked unchanged; mirrors intentionally **unsynced** with instructions.

Return: **no new promoted skill; corrected candidates and edited instructions
pending later independent review, installed child compatibility still blocked.**
No main-task completion, task status write, history migration or Git action.