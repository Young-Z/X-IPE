# Bug Fix — current candidate metadata, TASK-6749

Reviewed and published bug slice after completed inherited CR review/promotion.
Loaded installed creator/guidelines/task and metadata templates, shared lifecycle
and goal contract; reviewed original bug entry/examples/metadata, preexisting
candidate lifecycle deletions, actual UI/template/config and Python fix interface.
Both original resources retained and updated; integration and bug scaffold added,
no deletion. Original metadata is preserved verbatim below. No finite verified
lesson selected, lesson/memory state unchanged. Current user authorized bug publication.

Legacy examples' unsupported expiry semantics/full-suite counts corrected; no
application auth bug or real approval claimed. Existing candidate removed board
steps but kept duplicate routing; same-task owner and no implicit Git/next work
now cover all resources. Dynamic fields and complete legacy optional outputs pass
through without inventing mandatory keys. Current bug tool key has no app mapping.

Fresh blank-handoff recovery verification: 550 passed / four identical inherited
closing and lifecycle failures in 32.82s; all 51 dedicated change-quality checks
passed separately in 1.18s, no skips/deselections. Current installed validator:
four files, 258 body lines, zero
errors/warnings; receipt exactly recomputed. Live bug two-file baseline unchanged;
no publication receipt. Original metadata SHA256 preserved exactly inside text
fence after repairing editor-added fence indentation. See test-cases.yaml for
commands/results, candidate/test/consumer fingerprints and fixture-only limits.
The preceding runs were drafting self-check; the current inherited-candidate
independent review is recorded in review-findings-TASK-6749.md.

Reinspection found the inherited four-file candidate already complete; no candidate
content change was needed. Strengthened only the dedicated test: frozen original
output keys/order/nested values and actual original fixture action before/after
fix with source hashes and unchanged-test hashes. Original action returns True
before the strict-boundary fix and False after; behavioral pytest red remains
1 failed/2 preserved checks passed, then green 3 passed. This is disposable fixture
evidence, not an application fix, routed skill execution or stakeholder observation.
CR six-file live/candidate/publication byte parity, candidate and baseline manifest
fingerprints and both saved validator receipts recomputed successfully read-only.
These are historical recovery observations, superseded by the current review and
edit-tool promotion receipt. No broader-task closure or protected writes.

## Current review and publication

Independent inherited-candidate review passed without candidate content changes.
Root metadata type label null is now quoted as a string. The reviewed dry-run
changed two resources, added two and removed none. Explicit user-requested edit
promotion initially merged old content; parity checks caught it before recording
success, bounded edits removed it, and all four production hashes now exactly
match candidate. No publisher apply/journal/atomicity claimed. Original history
bytes are untouched; version 2.0.0 records verified publication only.

```yaml
skill_name: x-ipe-task-based-bug-fix
skill_type: x-ipe-task-based
version: "2.0.0"
planned_version: "2.0.0"
status: production
created: 2026-02-24
updated: 2026-10-13
task_id: TASK-6749
publication_state: published
independent_review: passed_inherited_candidate_review
candidate_hash: 72e377126dbd984e21186d513de7358941b7a69ec3aea3f2841995c909990b6c
summary: Restore documented intended behavior under existing goals/subgoals/constraints with actual reproduction, root-cause boundaries, behavioral red/green and regression evidence; one lifecycle owner.
triggers: [fix bug, something is broken, not working]
not_for:
  - "x-ipe-task-based-change-request: intentional goal/scope/acceptance/constraint change"
  - "x-ipe-task-based-code-refactor: restructuring without reported behavior deviation"
workflow:
  category: standalone
  phase: null
  next_task_based_skill: null
  human_review: true
  current_app_action: null
  unsupported_workflow_mode: blocked; owner may obtain authorized free-mode disposition
inputs:
  required:
    - {name: task_id, type: string, description: same existing lifecycle task/readiness}
    - {name: task_based_skill, type: string, description: exact canonical discovered name}
    - {name: process_preference.interaction_mode, type: string, default: interact-with-human, description: exact three-mode policy/source not boolean}
    - {name: bug_description, type: string, description: original report and scope}
    - {name: expected_behavior, type: string, description: reconcile report and approved source/story/GWT AC/constraints}
    - {name: actual_behavior, type: string, description: symptoms then actual reproduction evidence}
  optional:
    - {name: execution_mode, type: string, default: free-mode}
    - {name: workflow, type: object, description: exact caller name/action/context; no invented bug_fix association}
    - {name: reproduction_steps, type: string, default: N/A, description: known original steps or bounded hypothesis}
    - {name: environment_info, type: string, default: N/A, description: relevant actual runtime/browser/config/data}
    - {name: program_type, type: string, description: actual behavior/project context not extension alone}
    - {name: tech_stack, type: array, default: [], description: verified project/runtime and affected layers}
    - {name: category, type: string, default: standalone}
    - {name: next_task_based_skill, type: "null", description: no successor authorization}
outputs:
  state:
    - {name: category, value: standalone}
    - {name: status, value: completed | blocked}
    - {name: next_task_based_skill, value: null}
    - {name: process_preference.interaction_mode, value: original nested caller enum}
  artifacts:
    - {name: fixed_source_file, type: file, path: actual approved fixed source, description: bounded restoration only}
    - {name: test_file, type: file, path: actual regression test, description: unchanged behavioral assertions red then green}
    - {name: bug_evidence, type: file, path: existing bug artifact or approved report path, description: original context plus goal/root-cause/conflict/before-after evidence; no mandatory new output key}
  data:
    - {name: execution_mode, type: string, description: original mode; unsupported workflow blocked}
    - {name: workflow.name, type: string, description: original identity or free-mode N/A}
    - {name: task_output_links, type: array, description: actual source/test or blocked partial links}
    - {name: bug_severity, type: string, description: Critical | High | Medium | Low}
    - {name: root_cause, type: string, description: actual cause and boundaries not symptom-only claim}
    - {name: conflicts_found, type: array, description: original conflict records and actual report evidence}
    - {name: supplied legacy/dynamic fields, type: passthrough, description: retain existing optional require_human_review/full child fields; not mandatory invention}
acceptance_criteria:
  must:
    - {id: AC-S01, category: structure, criterion: valid complete four-file task subtype with ordered sections body/checkpoint limits, test: installed validator and XML parse}
    - {id: AC-S02, category: preservation, criterion: original resources/use cases and original output keys/order/values plus legacy optional passthrough preserved; production untouched, test: original schema equality and baseline fingerprints}
    - {id: AC-G01, category: goal, criterion: existing intended behavior/source/parent/stakeholder/contribution/constraints/story/GWT AC/type and all-required branches with qualitative success; no arbitrary metrics/new goal/AC weakening, test: authored restoration row/scaffold and negative constraints}
    - {id: AC-G02, category: evidence, criterion: inferred explicit legacy so-that or pertinent blocker; delivery separate from unmeasured/observed outcome, test: contract/example and false observation negative}
    - {id: AC-B01, category: behavior, criterion: actual reproduction behavioral failure not setup error precedes fix; unchanged test green and regression boundaries, test: real disposable miniature Python fixture red 1 failed 2 passed then green 3 passed}
    - {id: AC-B02, category: regression, criterion: original steps full suite/smoke/lint and side effects checked; new regressions block; pre-existing failures explicit and no all-green claim, test: entry/scaffold separate textual gate not autonomous execution}
    - {id: AC-C01, category: cause, criterion: actual root cause design flaw versus implementation error and callers/dependent interface/data/workflow boundaries, test: procedure/example/scaffold contract}
    - {id: AC-C02, category: conflict, criterion: Detector/Validator compare actual code to ORIGINAL report before test/fix; expected proceeds unexpected authority/narrowing and unresolved blocked, test: eight-step contract and guest boundary example}
    - {id: AC-A01, category: authority, criterion: human/hybrid human decisions full DAO bounded guidance; actual human changed-contract CR authority all modes; no repeated confirmation, test: three-mode contract}
    - {id: AC-D01, category: design, criterion: minimal restoration and approved key interface/data/workflow design/Change Log before implementation, test: entry/example/scaffold gates}
    - {id: AC-I01, category: workflow, criterion: actual absent bug-fix UI/template mapping not invented; authorized free-mode or requested workflow blocked; no fake tags, test: actual consumers and installed helper rejected write preserves temp state}
    - {id: AC-I02, category: tools, criterion: actual enabled semantic routing operation fix mini AAA one assertion per clause sequential grouping and exact operation_output retained; synthetic tool context not feature allocation, test: actual config/Python operation interface plus integration contract}
    - {id: AC-I03, category: optional, criterion: browser UI/config/availability gate actual evidence or disabled/unavailable gap; no tracing forced when disabled/absent, test: actual config and reference/scaffold not browser execution}
    - {id: AC-L01, category: lifecycle, criterion: one same-task owner no duplicate registration/board/Git/app/next/automatic commit and complete dynamic/legacy output handoff, test: obsolete block absence and original contract}
    - {id: AC-E01, category: freshness, criterion: current source/design/test/config/review hashes plus bounded affected invalidation unaffected retention; reviewed authorized exact-byte publication, test: validator and publication receipts plus independent review handoff}
  should:
    - {id: AC-C03, criterion: examples preserve original token and guest cases while removing unsupported semantic/security/pass-count claims}
    - {id: AC-C04, criterion: intermittent failure uses controlled schedule/seed not arbitrary success target}
  could:
    - {id: AC-B03, criterion: separately authorized autonomous skill/tool/browser pilot on actual reported application bug}
  wont:
    - {id: AC-W01, criterion: publish unrelated refactor candidate, reason: current user requires its later independent reviewer}
    - {id: AC-W02, criterion: board/memory/Git/app/config/other source writes, reason: excluded scope}
dependencies:
  skills:
    - {name: x-ipe-workflow-task-execution, relationship: prerequisite, description: common lifecycle/goal contract and owner}
    - {name: x-ipe-task-based-change-request, relationship: boundary, description: changed acceptance/intent not automatic execution}
    - {name: enabled implementation tool skills, relationship: routing, description: load actual fix operation no fabricated invocation}
    - {name: x-ipe-tool-ui-testing-via-chrome-mcp, relationship: conditional, description: UI/config/available browser only}
  artifacts:
    - {path: x-ipe-docs/config/tools.json, description: enabled bug tool route and tracing false}
    - {path: x-ipe-docs/config/workflow-template.json, description: no bug_fix action}
    - {path: src/x_ipe/static/js/features/workflow-stage.js, description: authoritative no skill association}
test_scenarios:
  happy_path:
    - {name: Fixture restoration, given: strict expiry contract and broken inclusive predicate, when: same test red then minimal fixture fix, then: 3 fixture checks green unchanged tests; not application fix}
  edge_cases:
    - {name: Shared guest boundary, given: regular validation caller change affects guest, when: original request conflict review, then: narrowing or actual authority before fix; authored only}
    - {name: Legacy unavailable visual evidence, given: inferred goal or disabled/unavailable browser, when: claimed outcome/visual restoration, then: pertinent gap/blocker not fake evidence}
  error_cases:
    - {name: Unknown app action, given: current installed template/state, when: helper action bug_fix in temp project, then: rejected nonzero state bytes unchanged}
  blocking:
    - {name: Changed contract or unresolved conflict, given: unapproved scope delta, when: testing/fix requested, then: blocked; no forced tracing}
evaluation:
  self_check:
    - Deterministic complete package and original schema/baseline checks.
    - Textual contract versus actual disposable behavioral/helper execution explicitly separated.
    - Existing historical metadata retained exactly; production limited to reviewed bug package; no lifecycle writes.
  judge_agent:
    - {criterion: Independent candidate review, rubric: passed inherited-candidate review in current session; not a spawned subagent or autonomous runtime execution}
version_history:
  - version: "2.0.0"
    date: 2026-10-13
    task_id: TASK-6749
    evidence: publication-receipt-goal-TASK-6749.json
    changes: Goal restoration and root-cause safety; exact reviewed four-file edit-tool promotion.
```

## Historical metadata (verbatim prework snapshot)

```text
# ═══════════════════════════════════════════════════════════
# SKILL META - Task-Based: Bug Fix
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-task-based-bug-fix
skill_type: x-ipe-task-based
version: "1.1.0"
status: candidate
created: 2026-02-24
updated: 2026-02-24

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Systematically diagnose, fix, and verify bug resolutions with conflict pre-check
  to ensure fixes don't introduce unexpected behavioral changes.

triggers:
  - "fix bug"
  - "something is broken"
  - "not working"

not_for:
  - "x-ipe-task-based-code-refactor: When restructuring code without fixing a bug"
  - "x-ipe-task-based-change-request: When modifying behavior intentionally"

# ─────────────────────────────────────────────────────────────
# CHANGE DESCRIPTION (v1.0.0 → v1.1.0)
# ─────────────────────────────────────────────────────────────
change_description: |
  Add "Conflict Analysis" step between Design Fix (Step 4) and Write Test (new Step 6).
  New Step 5 uses two sub-agents:
    1. Conflict Detector: Analyzes proposed fix against existing codebase logic, lists conflicts
    2. Conflict Validator: Checks if each conflict is expected from user's original request
  If unexpected conflicts exist, asks user to confirm or clarify before proceeding.
  This prevents fixes from silently breaking existing behavior.

# ─────────────────────────────────────────────────────────────
# WORKFLOW POSITION
# ─────────────────────────────────────────────────────────────
workflow:
  category: standalone
  phase: null
  next_task_based_skill: null
  human_review: true

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: interaction_mode
      type: boolean
      default: false
      description: Whether to auto-proceed to next task

    - name: bug_description
      type: string
      description: Description of the bug

    - name: expected_behavior
      type: string
      description: What should happen

    - name: actual_behavior
      type: string
      description: What actually happens

  optional:
    - name: reproduction_steps
      type: string
      default: null
      description: Steps to reproduce the bug

    - name: environment_info
      type: string
      default: null
      description: Environment details if relevant

    - name: program_type
      type: string
      default: null
      description: "frontend | backend | fullstack | cli | library | skills | mcp"

    - name: tech_stack
      type: array
      default: []
      description: e.g. ["Python/Flask", "JavaScript/Vanilla"]

outputs:
  state:
    - name: category
      value: standalone
    - name: status
      value: completed | blocked
    - name: next_task_based_skill
      value: null
    - name: require_human_review
      value: yes

  artifacts:
    - name: fixed_source_file
      type: file
      path: "{path to fixed source file}"
      description: The source file with the bug fix applied

    - name: test_file
      type: file
      path: "{path to test file}"
      description: Test file with bug-reproducing test case

  data:
    - name: bug_severity
      type: string
      description: "Critical | High | Medium | Low"
    - name: root_cause
      type: string
      description: Brief description of root cause
    - name: conflicts_found
      type: array
      description: List of conflicts identified during analysis (empty if none)

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
      test: file_exists + yaml_parse
      expected: name and description fields present

    - id: AC-S02
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    - id: AC-C01
      category: content
      criterion: Execution Flow table has 8 steps (was 7)
      test: table_parse
      expected: 8 rows in Execution Flow table

    - id: AC-C02
      category: content
      criterion: Step 5 is named "Conflict Analysis"
      test: content_check
      expected: step_5 contains "Conflict Analysis"

    - id: AC-C03
      category: content
      criterion: Conflict Analysis step uses two sub-agents
      test: content_check
      expected: References "Conflict Detector" and "Conflict Validator" sub-agents

    - id: AC-C04
      category: content
      criterion: Unexpected conflicts trigger user confirmation
      test: content_check
      expected: Contains "ask user" or "check with user" for unexpected conflicts

    - id: AC-C05
      category: content
      criterion: BLOCKING rule prevents skipping unresolved conflicts
      test: content_check
      expected: BLOCKING constraint on Step 5 about unresolved conflicts

    - id: AC-C06
      category: content
      criterion: Steps after Conflict Analysis correctly renumbered
      test: content_check
      expected: Write Test=Step 6, Implement=Step 7, Verify=Step 8

    - id: AC-C07
      category: content
      criterion: DoD includes conflict analysis checkpoint
      test: content_check
      expected: DoD has checkpoint for conflicts resolved

    - id: AC-B01
      category: behavior
      criterion: No-conflict path proceeds directly to Write Test
      test: execution
      expected: When no conflicts, flow goes Step 4 → Step 5 (no conflicts) → Step 6

    - id: AC-B02
      category: behavior
      criterion: Expected-conflict path proceeds without user prompt
      test: execution
      expected: When all conflicts expected, flow continues without asking user

    - id: AC-B03
      category: behavior
      criterion: Unexpected-conflict path asks user
      test: execution
      expected: When unexpected conflicts found, user is asked to confirm or clarify

  should:
    - id: AC-S03
      category: structure
      criterion: Conflict analysis pattern documented in Patterns section
      test: content_check
      expected: Pattern for conflict analysis exists

    - id: AC-C08
      category: content
      criterion: Anti-pattern for skipping conflict check
      test: table_parse
      expected: Anti-pattern entry about fixing without checking conflicts

    - id: AC-C09
      category: content
      criterion: Example updated to show conflict analysis step
      test: content_check
      expected: Example includes Step 5 conflict analysis

  could:
    - id: AC-C10
      category: content
      criterion: Conflict severity classification guidance
      test: content_check
      expected: Guidance on classifying conflict severity

  wont:
    - id: AC-W01
      criterion: Automated conflict detection tooling
      reason: Agent uses code analysis, not specialized tools

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: Bug fix with no conflicts
      given: Simple off-by-one bug in isolated function
      when: Conflict Detector analyzes fix
      then: No conflicts found, proceeds to Write Test

    - name: Bug fix with expected conflicts
      given: Bug fix changes comparison operator, user explicitly requested this change
      when: Conflict Validator checks against user request
      then: All conflicts classified as "expected", proceeds without user prompt

  edge_cases:
    - name: Bug fix with mix of expected and unexpected conflicts
      given: Fix changes multiple behaviors, some requested, some not
      when: Conflict Validator classifies each
      then: Only unexpected ones presented to user for confirmation

  error_cases:
    - name: User rejects unexpected conflict
      given: Fix would break guest login, user didn't intend this
      when: User says "no, guest login should still work"
      then: Returns to Design Fix step with updated understanding

  blocking:
    - name: Cannot skip conflict analysis
      given: Fix designed but conflicts not checked
      when: Attempt to proceed to Write Test
      then: BLOCKED — must complete conflict analysis first

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "Step 5 exists as Conflict Analysis"
    - "Two sub-agent roles defined: Conflict Detector, Conflict Validator"
    - "BLOCKING constraint prevents skipping"
    - "User prompt on unexpected conflicts"
    - "DoD checkpoint for conflict resolution"

  judge_agent:
    - criterion: "Conflict Analysis step is clear and actionable"
      rubric: |
        5: Excellent - clear sub-agent roles, all paths handled
        4: Good - minor clarity improvements needed
        3: Acceptable - some gaps in conflict handling
        2: Poor - significant logic gaps
        1: Fail - step is unclear or missing key paths
```



## R2 recovered publication history

- Version 2.0.1, TASK-6749; verified 2026-10-14T04:28:27.605298+00:00.
- Current production/candidate fingerprint: e3410950f38bb6e6b987302d77176220e1e22519d61d0d589b31b7719740f2e0.
- [Recovered verification receipt](publication-receipt-TASK-6749-R2.json); prior history above remains historical, not current parity evidence.
- Hybrid inner guidance and human completion/route boundary independently reviewed at exact R2 hash; documented expected behavior and failing-before/fixed-after regression evidence retained. Prior-worker promotion time is unknown; no production replay or atomic writer journal claimed.

## TASK-6750 single-loop delivery revision

Published after deterministic validation, bounded workflow safety review, and real manifest-safe publication; prior metadata above remains version history.

- Current revision: `5b94f2e36e2f29f127333603989b410126037d2b676411a1b78ee2acde1e9d7e`
- Previous revision: `e3410950f38bb6e6b987302d77176220e1e22519d61d0d589b31b7719740f2e0`
- Evidence: `single-loop-TASK-6750.json`, `publication-receipt-TASK-6750.json`, `validation-receipt-TASK-6750.json`.
- Same-loop delivery/default risk-based verification; unchanged resources and protected bytes retained.
- Token/latency savings not measured; no live-agent efficacy claim.

## TASK-6752 proportional-delivery revision

Published through the installed manifest-safe publisher after bounded compatibility review, correction of its TypeScript test-path finding, deterministic validation and affected post-publication regressions. Prior metadata remains historical.

- Current revision: `32704aa6dde1a64091e4ce3bbc86f225de8eda089bc7ae4d5deea995f7be4af3`
- Previous revision: `5b94f2e36e2f29f127333603989b410126037d2b676411a1b78ee2acde1e9d7e`
- Evidence: `lean-delivery-TASK-6752.json`, `publication-receipt-TASK-6752.json`, `validation-receipt-TASK-6752.json`.
- Verification: 599 selected checks passed; exact installed/candidate byte parity. No resource removals, mirror synchronization or Git mutation.
- Live-agent efficacy, token/latency savings and stakeholder outcome remain unmeasured.
