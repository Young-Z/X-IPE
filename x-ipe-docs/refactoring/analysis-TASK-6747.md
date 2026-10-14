# Project Cleanup and Lightweight Development Workflow — Study & Plan

Date: 2026-10-13 | Task: TASK-6747 | Assignee: Quill

**Status: study complete; implementation awaits user approval.**

## 1. Recommendation

Keep X-IPE's durable context and traceability, but replace repeated ceremony with a small shared lifecycle and risk-proportional specialist steps. Better agent capability should remove repeated analysis, bookkeeping, and forced handoffs—not acceptance criteria, evidence, or approval boundaries.

Adopt a **1,000-line maximum for the SKILL.md body across X-IPE skill types**, not a target length. Keep progressive disclosure and prefer concise skills. First improve creator safety and contract consistency, then simplify the development workflow, then clean packaging and proven redundant resources. Defer large application refactors to separately scoped work.

### Scope and boundaries

- Studied instructions, creator/templates/references, requirement-to-closing skills, CR/bug/refactor skills, boards, workflow/config consumers, CLI translation/scaffolding, packaging, and test baselines.
- This task authorizes analysis and planning artifacts only. No production/candidate skill edits, source changes, deletions, branch switching, commits, pushes, or PRs.
- Existing dirty/untracked knowledge skills, candidates, documents, agent mirrors, and security-scan work are preserved.
- The full code-refactor skill's sync/execute/validate phases are **not performed**: this is not a completed application refactor. Documentation sync and blanket coverage expansion would exceed the requested study scope.
- Inventory and test results below are direct local observations. Proposed benefits are hypotheses to measure, not delivery-time guarantees.

## 2. Verified Current State

| Observation | Evidence / implication |
| --- | --- |
| 89 canonical skills | Count of immediate skill folders with SKILL.md under .github/skills. Do not rewrite all of them for this initiative. |
| 5,776 lines across the orchestrator and 10 lifecycle/CR/bug/refactor skills | The seven requirement-to-closing skills alone total 3,697 lines. Shared lifecycle text is a strong simplification target; line count alone does not prove uselessness. |
| Creator is 504 total lines; policy says body under 500 / 600 for tools | [Creator policy](.github/skills/x-ipe-meta-skill-creator/SKILL.md#L57), [guidelines](.github/skills/x-ipe-meta-skill-creator/references/skill-general-guidelines-v2.md#L22), and templates contain multiple thresholds. Define body versus total-line counting explicitly. |
| Three identical local 175-line instruction files | [.github/copilot-instructions.md](.github/copilot-instructions.md), [AGENTS.md](AGENTS.md), and [CLAUDE.md](CLAUDE.md) are byte-identical. The latter two are untracked, not three independently tracked canonical sources. Installed instruction variants can still drift. |
| CLI skill translation already exists | [SkillTranslator](src/x_ipe/services/skill_translator.py#L38-L61) and [scaffolding](src/x_ipe/core/scaffold.py#L88-L136) distribute skills. Extend existing mechanisms rather than invent a second mirror system. |
| Local Claude/Codex mirrors are untracked | Claude has 88 skills and lacks the CR-effort skill; local codex/skills has 89. Compared SKILL.md contents otherwise match canonical files. This is entry-file parity, not full-tree parity. Configured Codex target is .codex/skills, not codex/skills: [adapter config](x-ipe-docs/config/cli-adapters.yaml#L39-L48). |
| Tracked presentation node_modules: 941 files / 33,626,245 bytes | Includes a Darwin arm64 shared library. [Manifest](.github/skills/pptx/scripts/package.json) and [lockfile](.github/skills/pptx/scripts/package-lock.json) exist. This is rebuildable dependency material in principle, but bootstrap/portability must be tested first. |
| CR report assets: 209 tracked files / 16,378,833 bytes | 103 source maps account for 12,862,407 bytes. Offline runtime assets are intentional; assess source maps separately, retaining required scripts, fonts, licenses, and attribution. |
| Canonical skills are force-included into the wheel | [Packaging configuration](pyproject.toml#L35-L38) makes skill cleanup a distribution concern, not just a working-directory concern. Measure actual wheel contents before/after. |
| Old active tasks survive outside the default query window | [Query default is one week](.github/skills/x-ipe-tool-task-board-manager/scripts/task_query.py#L27-L29). An all-date query found eight other active tasks. Age is not proof they are abandoned. |

### Test baseline actually executed

**Selected Python baseline: 616 passed, 9 failed in 4.72 seconds.**

The 16 suites cover board library/CRUD/APIs, CLI adapters/init, skill translation, tools config, workflow deliverables, DAO skills/instructions, and app-interactor migration/scripts:

- [test_board_lib.py](tests/test_board_lib.py), [test_task_crud.py](tests/test_task_crud.py), [test_feature_crud.py](tests/test_feature_crud.py)
- [test_task_board_api.py](tests/test_task_board_api.py), [test_feature_board_api.py](tests/test_feature_board_api.py)
- [test_cli_adapter.py](tests/test_cli_adapter.py), [test_cli_init_selection.py](tests/test_cli_init_selection.py), [test_skill_translator.py](tests/test_skill_translator.py), [test_tools_config.py](tests/test_tools_config.py)
- [test_feature_041e.py](tests/test_feature_041e.py), [test_feature_047a_dao_skill.py](tests/test_feature_047a_dao_skill.py), [test_feature_047b_dao_migration.py](tests/test_feature_047b_dao_migration.py), [test_feature_047c_dao_instructions.py](tests/test_feature_047c_dao_instructions.py)
- [test_feature_052a.py](tests/test_feature_052a.py), [test_feature_052b.py](tests/test_feature_052b.py), [test_feature_052c.py](tests/test_feature_052c.py)

| Failure group | Count | What is observed; what remains undecided |
| --- | ---: | --- |
| OpenCode instruction destination | 3 | Tests expect .opencode/instructions.md; [configured destination](x-ipe-docs/config/cli-adapters.yaml#L14-L23) is Agents.md. Determine intended adapter contract before changing tests or runtime. |
| Deliverable validation | 2 | Tests expect missing tags to return false and extra tags to be accepted; [runtime](src/x_ipe/services/workflow_manager_service.py#L588-L609) warns for missing tags and rejects unexpected tags. Check later CR/spec intent; do not assume the older tests are authoritative. |
| DAO logging wording | 3 | Tests require timestamp, append/merge, and registry text in the current representative skill. Text absence is not proof of a runtime logging failure. Review the skill's revised contract. |
| Instruction-template parity | 1 | Local instructions differ from the packaged English no-DAO variant. Decide canonical generation/variant rules. |

**Full configured frontend baseline: 51 files / 1,016 tests passed in 5.15 seconds.** Run used npm test with dot reporter. Stderr included fixture/runtime warnings (for example sidebar fixture shapes and CSS import resolution), despite zero test failures.

Not measured: full Python suite, line/branch coverage, browser acceptance, installed-wheel behavior, latency, or production dead-code reachability. No numerical quality score or global coverage claim is made.

## 3. Main Process Findings

### F1 — Lifecycle responsibilities have more than one owner (high priority)

[Workflow planning](.github/skills/x-ipe-workflow-task-execution/SKILL.md#L260-L275) creates tasks and all suggested chained tasks upfront. Individual skills such as [implementation](.github/skills/x-ipe-task-based-code-implementation/SKILL.md#L173-L188) also create a task in Phase 0. Both the orchestrator and skills close/update tasks and route to the next skill.

This is a conflicting instruction contract, not proof that every real run creates duplicates. The board rejects duplicate IDs. Fix ownership: the shared lifecycle ensures one current task; specialist skills receive/reuse its ID and return outputs/next-step suggestions. Direct invocation uses the same ensure-task entrypoint. Create subsequent tasks when actually selected, not a speculative chain.

### F2 — Some contracts differ from their executable consumers (high priority)

- [Board documentation](.github/skills/x-ipe-tool-task-board-manager/SKILL.md#L26-L30) advertises --title/--assignee and autogenerated IDs. Actual [creation](.github/skills/x-ipe-tool-task-board-manager/scripts/task_create.py#L29-L32) takes --task JSON and validates a caller-supplied ID and [schema fields](.github/skills/x-ipe-tool-task-board-manager/scripts/_board_lib.py#L46-L58). Following the documented command failed during this study; corrected invocation succeeded.
- [Implementation routing](.github/skills/x-ipe-task-based-code-implementation/SKILL.md#L275-L300) reads stages.implement.implementation, while [tools config](x-ipe-docs/config/tools.json) uses code_implementation. Its fallback can ignore opt-in restrictions. Normalize the vocabulary or define one explicit adapter mapping.
- [Closing](.github/skills/x-ipe-task-based-feature-closing/SKILL.md#L238-L293) still references x-ipe-docs/features while [analysis](.github/skills/x-ipe-tool-refactoring-analysis/SKILL.md#L151-L157) expects requirement/epic feature artifacts. Resolve artifacts from validated board links, with tested legacy-path fallback.
- [Closing output](.github/skills/x-ipe-task-based-feature-closing/SKILL.md#L347-L352) submits closing-report, but [workflow template](x-ipe-docs/config/workflow-template.json) declares no feature_closing deliverable tags. The runtime rejects unexpected tags. Reconcile this before migration.
- Terminal status vocabularies and feature-stage output fields vary across prose, schemas, and consumers. Canonicalize from actual board/workflow contracts; retain backward-compatible aliases where required.

### F3 — Verification is repeated without freshness criteria (high priority)

Acceptance testing verifies ACs, closing verifies them again, closing always commissions refactoring analysis, and the workflow template makes code_refactor non-optional although acceptance skills allow closing without it. Make refactoring conditional on a concrete gap; closing should check the existing evidence and rerun affected tests only when code/spec/config has changed since that evidence.

Evidence reuse needs a revision/diff fingerprint, relevant AC/spec version, test commands/results, and open failures. A claim that tests passed, without provenance, is not reusable evidence. Existing artifacts should carry this information; avoid a new context service solely for caching.

### F4 — Rigid shape adds more than project-specific knowledge (medium priority)

The creator requires ten steps, four sequential role handoffs, metadata/tests/logs/evaluation/history artifacts, and independent DoD checks. Templates additionally repeat fixed phase tables, completion branching, and next-task execution. [General guidelines already advise against decomposition for tightly coupled or simple tasks](.github/skills/x-ipe-meta-skill-creator/references/skill-general-guidelines-v2.md#L171-L191).

Keep the five learning principles if useful, but do not require five named procedural phases and duplicate tables for every trivial operation. Project-specific invariants, exact schemas, dangerous operations, and failure recovery deserve detail; generic instructions to study, think, and verify usually do not.

### F5 — Current git completion rules are too broad for a dirty workspace (high priority)

[Global DoD](.github/skills/x-ipe-workflow-task-execution/SKILL.md#L350-L368) can stage all files; [refactor DoD](.github/skills/x-ipe-task-based-code-refactor/SKILL.md#L489-L491) requires a clean working tree. Those rules can sweep unrelated human/agent work into commits. Track task-owned paths, compare against initial status, and stage only approved changes. A task can be validated with unrelated changes present. Never infer authorization to push/delete/rewrite history from autonomous decision mode.

## 4. Proposed Lightweight Target

### Single shared lifecycle: Orient → Plan → Execute → Verify → Record

The shared lifecycle owns task registration/resume, interaction policy, feature/workflow updates, git scope, and next-step routing. Domain skills own only their specialized work. The agent loads shared policy once per task/session and refreshes it when changed; it loads domain references only when needed.

Keep existing skill names as entrypoints during migration. Simplify behavior first; merge/remove names only once triggers, prompts, app routes, and old projects have tested compatibility.

### Risk-based paths (not thresholds based on changed lines or AC count)

| Path | Selection | Required context and verification |
| --- | --- | --- |
| Study / documentation | No behavior or lifecycle-state change | One tracked task, bounded study/diff, findings with uncertainty, human review where requested. No mandatory code coverage, tracing, or feature pipeline. |
| Small compatible change | Localized, understood, no public-contract/data/security/architecture changes | Existing feature context; short intent/AC or CR delta; brief design rationale in existing artifact; targeted tests and relevant regression checks; close once evidence is current. |
| Standard feature | New behavior within established architecture | Spec/ACs + focused technical design + implementation + acceptance evidence. Combine authoring sessions if helpful; preserve separately addressable artifacts required by UI consumers. |
| High-risk / cross-feature | Auth/security, public APIs, data migration, destructive operations, broad coupling, or unclear semantics | Explicit impact/design/rollback, independent review, broader tests, approval at material scope/release decisions. |

- **New feature:** capture intent, ACs, exclusions, and impacted context once. Breakdown is substantive when multiple features/dependencies exist; a single-feature case still produces the lightweight registration/deliverable required by workflow consumers.
- **CR:** classify against existing boundaries, update only affected requirements/spec/design sections, carry the CR delta forward, and validate affected behavior. Do not regenerate a full specification or invent a feature for every correction.
- **Bug fix:** reproduce and add an appropriate regression test before the fix; use a documented alternative when automation is genuinely infeasible. Do not run a full new-feature pipeline for a local repair.
- **Refactor:** establish current behavior and impacted dependencies; add characterization tests where needed; execute incrementally; update only misleading references. Broad docs sync and a global 80% coverage threshold must not gate study-only work or unrelated modules.
- **Closing:** review current AC evidence, unresolved deviations, changed docs, and task-owned diff; close/update once. Optional refactor recommendations go to backlog, not compulsory pre-shipping analysis.
- **Interaction:** resolve mode once in shared policy. Preserve the three existing interaction-mode values and their intended human/DAO boundaries. Centralization must not silently alter the hybrid mode or allow DAO to invent human approval.

### Minimum durable context (extend existing artifacts, not another database)

Intent + ACs + non-goals; affected features/modules/contracts; key decisions and rationale; source/spec revision; test commands/results and known failures; current state/next action; artifact links. Provide a concise resume summary using these fields.

Project files and validated board state remain authoritative. Persistent agent memory is an index/hint, never a replacement for current source, a specification, or recorded user approval.

### Preserve app contracts during simplification

Preserve task/feature IDs and canonical state models, workflow action names and keyed deliverables, action-context references, per-feature/shared stage semantics, config filtering, CLI adapters, language/DAO variants, and legacy artifact lookup. Existing saved workflows must resume.

Do not simply skip a required workflow action and mark it done. First implement/test supported optional/skipped transitions and stage gating; when work is combined, record the actual required deliverables/evidence for each affected action.

## 5. Skill-Creator Target

**Plan extension:** [Selective, time-bounded lesson management](x-ipe-docs/refactoring/lesson-management-plan-TASK-6748.md) adds admission filtering, evidence-backed application statuses, finite lifetimes, bounded retrieval, and safe forgetting. Integrate its creator/lesson changes into P1 and instruction/ownership changes into P2; historical pruning remains a separately reviewed P4 action.

1. **Classify scope/risk and derive a delta plan** from user intent and related lessons. No compulsory interview when requirements and examples are already clear.
2. **Draft in candidate staging**, including all required resources. For an existing skill, update the delta; do not recreate unchanged metadata/reference material.
3. **Run deterministic checks and applicable behavior scenarios**, then use one independent reviewer for meaningful workflow, executable, or safety-policy changes. Cosmetic/document-only changes can use a lightweight path. Four compulsory sequential agents are unnecessary.
4. **Publish a verified manifest/diff and merge safely**, verify production parity, retain a compact validation/version record. Stop on failure or unapproved risk.

### 1,000-line policy

- One ceiling: body lines **≤ 1,000** for X-IPE skills; 1,000 passes, 1,001 fails. YAML frontmatter is validated separately and excluded from body counting. Define counting consistently for blank lines, trailing newline, and CRLF.
- It is capacity, not encouragement to fill the file. No forced 750/800/900 subtype caps. Keep examples, extensive references, and executable code on demand.
- Update creator instructions, guidelines, quality standards, section-order guidance, task-based template, skill-meta templates, affected candidate metadata, and genuine line-limit tests as one coherent change.
- Apply the policy to X-IPE skills, not third-party skill documentation, generated reports, or unrelated application file-size guidance. Audit old thresholds for meaning before replacement; 800-line code limits and 5,000-token examples are separate concerns.

### Deterministic validation should replace ritual, not judgment

Validate frontmatter/discovery, selected type's input/output contract, referenced resources/dependencies, workflow action/config compatibility, line policy, candidate file manifest, executable script scenarios, and safe merge boundaries. Keep focused DoR/DoD checks without requiring a separate checkpoint for every trivial intermediate output.

Resolve self-references against the candidate and external references against their actual sources. Check contents/checksums, not just existence. Exclude declared generated caches consistently.

The current recursive copy merge can leave removed production files behind. A manifest-aware replacement must explicitly handle additions/changes/deletions, protect unmanaged files, support dry-run/rollback, and verify parity. Do not introduce blind recursive deletion.

## 6. Cleanup Register

| Candidate | Confidence / disposition | Required proof before removal |
| --- | --- | --- |
| Presentation node_modules and native binary | High-confidence dependency payload; **replace then remove** | Clean bootstrap using manifest/lock, presentation smoke test, no-network/install expectations documented, wheel and non-macOS install checks. Update creator candidate via its approved path for any changed skill resources. |
| CR report source maps | High-confidence debug payload; **conditional packaging cleanup** | Offline report smoke tests, import/network inspection, debug expectations, license/attribution preservation. Do not remove offline Mermaid/font assets as a group. |
| Two deprecated board-wrapper skills | Proven redirect-only entrypoints; **migrate then retire** | Rewrite remaining live references, update discovery/deployment tests, retain compatibility policy for existing installed projects. Historical mentions need not be erased. |
| Two manual-reference skills | Main skill bodies differ only in name/title wording; **consolidate after full-tree comparison** | Select canonical name, check resources/operation contracts, update general-purpose executor callers, test old-name redirection then retire. |
| Tracked reverse-engineering v1 backup | Likely archival; **archive/remove after reference scan** | Preserve retrievable history, confirm no automation uses it, remove from distribution only after verification. |
| Local agent mirrors and duplicate instruction entrypoints | Intentional portability / untracked local state; **retain and formalize generation** | Reuse translator/scaffold, define canonical source/variant policy, drift detection, no destructive force-overwrite of local work. |
| Old candidates, task history, decision logs | Durable context / possible WIP; **index or archive, not blanket delete** | Determine latest/pending versions and references. An old active task is not owned by this session. |
| Empty untitled workspace folder | Empty and untracked; **optional local housekeeping** | No meaningful Git/package savings; not a project refactoring deliverable. |
| Ontology/extraction tool skills and app-agent MCP | **Retain pending dedicated migration audit** | Actual callers remain (including application extractor and MCP tests). Deprecated wording does not establish full replacement. |
| Large runtime/UI modules | **Separate scoped follow-up, not proven dead code** | Use semantic references, runtime registration/template loading, characterization tests, focused responsibilities, and browser/API evidence. |

Useful follow-up size signals (not automatic violations): [workplace](src/x_ipe/static/js/features/workplace.js) 3,132 lines; [KB service](src/x_ipe/services/kb_service.py) 1,397; [workflow manager](src/x_ipe/services/workflow_manager_service.py) 1,306. Prefer testable extraction of responsibilities over mechanical line splitting.

## 7. Execution Plan After Approval

Each phase is independently reviewable and reversible. Work in candidate folders for skill changes, promote only after validation, and keep pre-existing edits outside each task-owned diff.

| Phase | Work package | Size / risk | Exit gate |
| --- | --- | --- | --- |
| P0 — Reconcile baseline/contracts | Triage the nine Python failures against latest specs/CRs; align board CLI documentation, status/field contracts, config keys, artifact resolution, closing deliverable tags; snapshot initial dirty state. | Small–medium / medium | Intent decided for each mismatch; relevant tests pass or explicit unrelated baseline failures remain documented. No tests weakened just to obtain green. |
| P1 — Creator foundation | Bootstrap creator's own candidate using current process; implement unified 1,000-body-line policy and deterministic validator; safe manifest merge/dry-run/parity; simplify creator rounds and update templates together. | Medium / medium–high | Boundary/resource/parity/rollback tests pass; one representative new-skill and existing-skill update validated; production/candidate parity recorded. |
| P2 — Shared lifecycle | Orchestrator owns ensure/resume/create/update/route; domain skills return outputs. Eliminate duplicate registration and speculative task chains; centralize interaction/git policy; generate/sync instruction variants using existing distribution paths. | Medium / high integration | Direct and orchestrated entrypoints each create one task; resumption/concurrency works; three modes/CLI variants preserve behavior; no unrelated files staged. |
| P3 — Lean requirement-to-close paths | Delta-first context, risk-based paths, concise spec/design authoring, revision-bound verification reuse, conditional refactoring/closing; migrate workflow template/stage gating before skipping actions. | Medium–large / high integration | Small feature, standard feature, existing-feature CR, bugfix, study-only task, and refactor pilots pass; old workflows resume; UI actions/deliverables remain accurate. |
| P4 — Proven cleanup/distribution | Bootstrap dependencies, filter unnecessary build/debug payload after smoke tests, retire wrappers/duplicate manual skill after caller migration, archive selected backups; formalize mirror drift checks. | Medium / medium | Package/install/offline-report/presentation smoke checks pass; removed items have no live callers; required licenses/resources remain. |
| P5 — Optional application refactors | Select one hotspot based on actual change frequency/test risk; characterize and extract responsibilities. Not necessary to deliver process simplification. | Per module / varies | Same externally visible behavior; impacted suites and browser/API checks pass; tracing retained where applicable. |

**Recommended first implementation batch: P0 + P1.** Do not combine workflow-state changes, large module refactors, and wholesale asset deletion into one patch.

### Validation matrix

- **Creator:** 999/1,000/1,001 body lines; frontmatter, newline/CRLF handling; missing resources; self/external reference resolution; malformed contracts; add/change/remove manifest; protected files; failed merge rollback; new/update scenario review.
- **Lifecycle:** direct/orchestrated invocation, supplied task ID, duplicate/concurrent creation, restart/resume, all-date active task lookup, canonical aliases, no speculative tasks, task-owned git staging.
- **Configuration:** configured enabled/disabled/undeclared tools, missing/metadata-only sections, general fallback, matching action-to-config keys.
- **Workflow:** required/optional/skipped actions, dependency/stage gating, per-feature isolation, exact deliverable tags including closing, legacy instances, all three interaction modes.
- **Evidence:** unchanged work reuses a valid report; source/spec/config/test-scope changes invalidate it; known failures remain visible; AC-to-test mapping retained; no stale report closes a changed feature.
- **Distribution:** clean CLI scaffold and upgrade for Copilot/OpenCode/Claude/Codex, EN/ZH and DAO/non-DAO instructions, user overrides protected, mirror drift checks, wheel content/size checks, offline report and presentation smoke tests.
- **Pilots:** no functional regressions and no new failures in impacted suites; inspect changed UI behavior in a browser when P3 is executed. Run the broader Python suite before declaring repository-wide success.

### Measure efficiency rather than assume it

For pilot tasks record skills/reference bytes loaded, redundant task reads/writes, subagent handoffs, generated artifacts, repeated test runs, elapsed/tool time, user interruptions, and resulting defects. Target one lifecycle owner, one current task, no repeated analysis without an invalidation reason, and fewer unnecessary artifacts/handoffs. Do not promise a percentage improvement until measured.

## 8. Analysis Completeness and Remaining Questions

Requirements/features/design alignment was assessed for the workflow/creator scope; concrete drift is listed above. Test **outcomes** were measured, not coverage. Tracing infrastructure exists in inspected services/translator; tracing coverage and redaction were not exhaustively audited. No runtime module is declared unused based solely on search results.

Open design choices to settle in their implementation phase:

1. Which later spec/CR is authoritative for the nine baseline test mismatches?
2. Should packaged presentation dependencies be installed on demand or supplied through a platform-specific distribution path?
3. What supported skipped-action semantics should old workflow instances receive?
4. Which manual-reference name becomes canonical, and how long should compatibility redirects live?

These do not block the study. The requested 1,000-line ceiling is already part of the proposed plan. Implementation, deletions, and shipping remain deferred until the user starts the work.
