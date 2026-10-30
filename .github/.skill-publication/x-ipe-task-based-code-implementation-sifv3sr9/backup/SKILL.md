---
name: x-ipe-task-based-code-implementation
description: Implement one designed feature with goal-to-AC-to-test traceability, sequential enabled semantic tool routing and revision-bound validation. Delegates skill packages to x-ipe-meta-skill-creator and MCP servers to mcp-builder before normal scenario generation and routing. Use when implementing a feature. Triggers on requests like "implement feature", "write code", "develop feature".
---

# Task-Based Skill: Code Implementation

## Purpose

Deliver one approved feature capability, not an activity count:
1. Follow authoritative outcome/parent/story/AC and both parts of its design.
2. Select justified implementation means within approved contracts and constraints.
3. Delegate special domains first, otherwise generate AAA tests and route enabled tools sequentially.
4. Verify every scoped AC and original Assert clauses with relevant regression/lint evidence, reused by later acceptance.
5. Return original outputs and actual artifacts to the same lifecycle owner.

## Important Notes

Load the [single-loop delivery policy](.github/skills/x-ipe-workflow-task-execution/references/agent-loop.md)
once in the current context. Execute this skill in the same agent loop; another
skill is expertise, not a new agent. Use proportional checks and reuse current
evidence; independent review is conditional on concrete risk, not the skill name.

BLOCKING: Load `x-ipe-workflow-task-execution` and the
[common lifecycle contract](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md).
Direct entry calls Orient/Plan with supplied task ID/original context without
recursively dispatching this skill. Reuse readiness; one owner handles task
registration/status, feature/workflow persistence, Git and the next boundary.
Delegated skills receive that same task/readiness; agree a bounded ownership
adapter for unmigrated children or block, never duplicate create/close/route/Git.

BLOCKING: Adopt the [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md)
at implementation coverage/verification. Exactly ONE feature; outcomes → stable
ACs → tests/assertions → selected means → current evidence. Components and tools
are means, not stakeholder goals. Qualitative source-derived scenarios suffice;
no invented KPIs, targets, scope or observed benefit; no chasing activity counts.
Keep mappings/evidence in existing design/testing artifacts, no new output/board
schema, goal database, mandatory graph, action tag or approval ritual.

Special skill-creator/MCP skill loading happens in the current loop before scenario generation and semantic routing; it does not spawn another agent.
They retain their own tests/DoD and full scoped AC coverage; they never bypass
verification or later feature acceptance testing. Candidate readiness is not
production promotion, implementation release or permission to alter live skills.

Read [implementation guidelines](.github/skills/x-ipe-task-based-code-implementation/references/implementation-guidelines.md)
for AAA/TDD/tool I/O, standards, retry, batching and evidence. Read
[integration contract](.github/skills/x-ipe-task-based-code-implementation/references/integration.md)
for config/action/path/status/deliverables semantics. Generated Markdown links
are project-root-relative; reject escaping/symlinked artifacts. Preserve unrelated
dirty source/docs and assertions; never weaken tests to manufacture a pass.

## Input Parameters

```yaml
input:
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-code-implementation"
  execution_mode: "free-mode | workflow-mode"
  workflow:
    name: "N/A"
    action: "implementation"
    extra_context_reference:
      tech-design: "path | N/A | auto-detect"
      specification: "path | N/A | auto-detect"
  category: "feature-stage"
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-acceptance-test"
      condition: "Verify implementation with acceptance tests"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  feature_phase: "Code Implementation"
  feature_id: "{FEATURE-XXX}"
  git_strategy: "main-branch-only | dev-session-based"
  git_main_branch: "{auto-detected}"
  specification_link: "x-ipe-docs/requirements/FEATURE-XXX/specification.md"
  mockup_link: "{path | N/A}"
  technical_design_link: "x-ipe-docs/requirements/FEATURE-XXX/technical-design.md"
  program_type: "frontend | backend | fullstack | cli | library | skills | mcp | ..."
  tech_stack: []
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="existing lifecycle task/readiness; no new ID" />
  <field name="task_based_skill" source="this canonical skill and caller match" />
  <field name="execution_mode" source="lifecycle; free-mode default" />
  <field name="workflow.name" source="exact lifecycle workflow or N/A" />
  <field name="workflow.action"><steps>Resolve ACTION_MAP/template implementation; reject explicit conflict. This app action is not tools.json code_implementation.</steps></field>
  <field name="workflow.extra_context_reference"><steps>Selected specification and tech-design paths take precedence in either mode. Required workflow contexts cannot be waived by N/A; preserve exact tag names.</steps></field>
  <field name="category" source="Output Result: feature-stage" />
  <field name="next_task_based_skill" source="original conditional Acceptance Test suggestion; not execution permission" />
  <field name="feature_phase" source="Code Implementation" />
  <field name="process_preference.interaction_mode"><steps>Use lifecycle-resolved exact enum/source: interact-with-human, dao-represent-human-to-interact, dao-represent-human-to-interact-for-questions-in-skill. Within skill human asks the human and waits; full DAO and hybrid use bounded message_context/instruction_units/execution_plan. Human and hybrid require human completion/route confirmation; full DAO selects only authorized successors. Explicit human approval binds in every mode. Clear inputs need neither.</steps></field>
  <field name="feature_id"><steps>Previous Technical Design output, explicit approved identity, current task context; feature board read-only verifies exactly one record.</steps></field>
  <field name="specification_link"><steps>Selected specification context first; declared input/previous design or feature specification_link next; unique owning EPIC/FEATURE or legacy FEATURE folder last for absent/N/A/auto-detect. Broken explicit path blocks, never fallback. Validate content, feature, file kind and approved roots.</steps></field>
  <field name="technical_design_link"><steps>Selected tech-design context first; actual previous design task output/declared input next; unique owning feature technical-design.md last for absent/N/A/auto-detect. No technical_design_link board field exists. Reject broken/wrong-feature/ambiguous/escaping sources.</steps></field>
  <field name="mockup_link"><steps>Previous design mockup_list/linked_mockups, explicit scoped path, specification Linked Mockups, then N/A. Preserve singular legacy field while collecting/opening every current scoped mockup. Validate content/scope, not latest date; conflict uses actual decision policy.</steps></field>
  <field name="git_strategy" source="validated lifecycle .x-ipe.yaml context; owner alone handles Git" />
  <field name="git_main_branch" source="validated lifecycle context; no child branch/network mutation" />
  <field name="program_type"><steps>Previous Technical Design output verified against both design parts and actual source; known types are extensible lowercase, not a forced enum.</steps></field>
  <field name="tech_stack"><steps>Approved design technologies/test frameworks verified against actual project artifacts, not every available tool.</steps></field>
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Identity and owner</name><verification>One feature/task/readiness, authorized source/test paths and single lifecycle owner; protected baseline captured.</verification></checkpoint>
  <checkpoint required="true"><name>Design readiness</name><verification>New implementation requires actual Designed status and complete specification/two-part design. Authorized CR/resume may preserve Implemented/Tested/Completed with fresh design evidence; Planned/Refined/Retired or missing design blocks.</verification></checkpoint>
  <checkpoint required="true"><name>Authoritative acceptance</name><verification>Sources/parent/story/AC/test types, constraints/non-goals, architecture/dependencies and current mockups resolve safely; material gaps block pertinent claims.</verification></checkpoint>
  <checkpoint required="true"><name>Verification and means</name><verification>Delta/relevant inputs, config, actual source/test paths, special delegations, regression/lint/coverage and independent review planned; tracing only where existing infrastructure is applicable.</verification></checkpoint>
</definition_of_ready>
```

## Execution Flow

| Phase | Step | Action | Gate |
| --- | --- | --- | --- |
| 1. 博学之 — Study Broadly | 1.1 | Read board/spec/design/architecture/goals/mockups | Approved outcome and bounded design |
| 2. 审问之 — Inquire Thoroughly | 2.1, 2.2 | Special delegation first; otherwise AAA/TDD coverage | Every scoped AC has valid assertions |
| 3. 慎思之 — Think Carefully | 3.1 | Match enabled capabilities and implement sequentially | Justified means within approved contracts |
| 4. 明辨之 — Discern Clearly | 4.1 | Validate, regression, applicable tracing and review | Fresh supported delivery, outcome separate |
| 5. 笃行之 — Practice Earnestly | 5.1 | Return original output and artifact handoff | Same owner, no child route |

## Execution Procedure

```xml
<procedure name="code-implementation">
  <execute_dor_checks_before_starting/>
  <phase_1 name="博学之 — Study Broadly">
    <step_1_1>
      <name>Study Approved Outcome and Design</name>
      <action>
        1. Query feature board read-only for actual identity/title/version/status/specification/dependencies. Resolve both source documents via initialization; no invented board design-link field.
        2. Read authoritative source/parent/subgoal/story/AC/test types, constraints/non-goals and both design parts, Version History/Design Change Log, referenced architecture and reuse patterns. Legacy explicit so-that may be labeled inferred with exact anchor; missing intent blocks its pertinent outcome/coverage claim only.
        3. Follow goal-to-AC-to-planned-check chain. Explain enabling contributions and all-required cases versus alternative means. Rejected options are not backlog mandates. Choose flexible means within approved design/contracts; changes outside it require authorized affected design/change-log update before coding, scope/AC changes need CR/human-intent authority.
        4. Inspect actual source/test paths/module sizes and project standards; retain KISS/YAGNI/DRY and 800-line module threshold. Open current frontend/fullstack mockups and map layout/spacing/colors/states/events/accessibility/responsiveness within scope.
        5. Capture relevant input hashes and baseline tests; identify affected goals/AC/contracts/dependencies, preserve unaffected IDs/bytes/assertions/history/evidence. No-op resume is read-only verification, not mandatory rewrite or replay.
      </action>
      <output>Approved contribution chain, delta/test plan and source revision evidence</output>
    </step_1_1>
  </phase_1>
  <phase_2 name="审问之 — Inquire Thoroughly">
    <step_2_1>
      <name>Special Delegation Gate</name>
      <action>
        1. Before normal AAA generation or semantic routing, if program_type is skills or any approved skill files are involved, delegate that package scope to x-ipe-meta-skill-creator with same task/readiness, complete candidate/metadata, validation/review and explicit publication boundary. Do not edit live skills directly. If MCP server scope exists, load mcp-builder and delegate its protocol/build scope first; it may consult runtime capabilities, not bypass configured routing for separate ordinary layers.
        2. Collect actual delegated artifacts/tests/receipts and DoD, map every scoped AC to structured or executable checks and original expectations. A delegation does not jump past validation/tracing/handoff or assert outcome achievement; later feature-acceptance-test still applies.
        3. For exclusively delegated scope use its suitable structured/executable tests instead of forcing code AAA; for uncovered ordinary code continue step_2_2 and step_3_1 without double implementation. Missing delegation checks/review/promotion authority block pertinent completion, preserve candidate output honestly.
      </action>
      <output>Bounded special-domain outputs or explicit ordinary path</output>
    </step_2_1>
    <step_2_2>
      <name>Generate AAA Scenarios</name>
      <action>
        1. For ordinary scope translate every scoped AC into Arrange/Act/Assert with stable source/story/AC links and original test type. Use @backend, @frontend, @integration for layer responsibility; UI/API/CLI/structured acceptance types remain intact, not converted to mocked integration only.
        2. Map selected design interfaces/data/algorithms/state/error branches to concrete happy/error/edge checks and affected regression. Include relevant no-mutation/security/mockup requirements, not speculative endpoints or activity quotas. Validate all ACs and all original Assert clauses are retained, including multiple clauses per AC.
        3. For large context retain a complete cross-layer coverage map first, then per-layer batches (backend first); no untested AC disappears between batches. If AAA generation fails, use x-ipe-tool-test-generation safety net with same authorized design/ACs; unresolved vague acceptance still blocks, never invent expectations.
        4. TDD: new/changed expected behavior must fail before implementation for the relevant reason, then pass after; existing satisfied criteria keep passing baseline and regression evidence. Orchestrator supplies/runs relevant RED tests before invoking an implement operation; live tools do not uniformly enforce RED. Preserve assertions/test types/all ACs; do not delete, weaken, xfail or skip a failing check to get green. Delegated structured checks retain their domain readiness rather than fabricate executable RED.
        5. Ask only consequential unresolved questions per actual mode; DAO cannot invent targets, confirm stakeholder intent, authorize scope/release or replace explicit required human approval.
      </action>
      <output>Full acceptance/assertion map, tagged scenarios and genuine relevant RED/baseline evidence</output>
    </step_2_2>
  </phase_2>
  <phase_3 name="慎思之 — Think Carefully">
    <step_3_1>
      <name>Route and Implement Sequentially</name>
      <action>
        1. Discover x-ipe-tool-implementation-* descriptions/When to Use/operations. Read tools.json stages.implement.code_implementation and _extra_instruction, not app action implementation or technical_design consultation config.
        2. Exclude metadata keys: missing/empty/metadata-only enables discovered tools. Explicit tool booleans activate opt-in: true enabled, false disabled, undeclared disabled; log disabled/undeclared rationale. Malformed values block the relevant config decision, not truthy enablement. Always force-enable general with warning if disabled/undeclared.
        3. Match actual type/stack/responsibility semantically to enabled tools only, not suffix or hardcoded registry. General is fallback when no eligible specific match; if insufficient report new-tool gap and block affected implementation, do not continue ad hoc. Preserve _extra_instruction as supplementary context, never authority to weaken gates or disable assertions.
        4. Invoke distinct matched skills sequentially, backend first then dependent frontend, never parallel. Pass standard operation implement, original layer aaa_scenarios, actual source_code_path/test_code_path, feature_context with source/design links and current frontend mockup_link. Tool calls carry agreed same-owner adapter; no child task CRUD/Git/routing.
        5. Collect implementation_files, test_files, test_results for each original assertion and lint_status/details. Deduplicate actual paths, preserve passing outputs. Retry a failed tool once with original scenarios plus error context; persistent failure blocks affected delivery. Adapt suitable means within approved design; design-contract changes require affected authorized update/reruns, not silent drift.
      </action>
      <output>Actual sequential tool outputs and revision-bound implementation/test inventory</output>
    </step_3_1>
  </phase_3>
  <phase_4 name="明辨之 — Discern Clearly">
    <step_4_1>
      <name>Verify Delivery and Relevant Evidence</name>
      <action>
        1. Inspect actual skill/tool outputs and run the smallest checks covering all original scoped Assert clauses and affected regression. Record suitable unit/integration/UI/API/CLI/structured evidence for later acceptance reuse, not a second full test pipeline. Mocked integration alone cannot prove UI/API acceptance or stakeholder observation. Verify actual paths/content/design/mockup fidelity and relevant lint. Coverage thresholds apply only when the project or approved AC explicitly requires one; do not impose a universal 80% gate.
        2. With existing tracing infrastructure and applicable modified runtime functions, use x-ipe-tool-tracing-instrumentation for supported files: INFO public boundaries, DEBUG helpers, sensitive parameter/log redaction and opt-in behavior. Skip with rationale when absent/inapplicable or only tests/config/skills; no mandatory setup every task. Rerun affected tests after instrumentation; do not introduce tracing infrastructure implicitly.
        3. Record actual commands/exits/assertion results, relevant source/spec/design/mockup/config/implementation/test hashes, review and unavailable checks in existing artifacts. Engineering delivery may be verified while stakeholder outcome is not measured. Qualitative outcome scenario follows source intent; only actual cited observation supports observed stakeholder outcome.
        4. Rehash relevant inputs before claiming completion; changed intent/parent/means invalidates affected design/test/outcome evidence and dependent claims. Rerun affected checks/review; preserve unrelated evidence only when dependencies establish it is still valid. Timestamps alone or historical pass counts are insufficient.
        5. Self-check DoD in the current loop. Obtain independent review only for an explicit request or concrete high-risk uncertainty under the shared policy; reuse suitable existing review. Missing required checks or unresolved failures block affected completion, not candidate drafting; preserve partial artifacts and passing evidence.
      </action>
      <output>Fresh delivery/AC evidence with honest outcome state and review limits</output>
    </step_4_1>
  </phase_4>
  <phase_5 name="笃行之 — Practice Earnestly">
    <step_5_1>
      <name>Return Same-Owner Handoff</name>
      <action>
        1. Verify domain DoD and return original task_completion_output/conditional successor and resolved actual links/feature fields. src/ and tests/ are legacy directory output examples, not impl-files. Preserve directory-oriented output semantics adapted to actual source/test/delegated folders, no schema additions.
        2. Same lifecycle owner in workflow-mode verifies specification and tech-design contexts, actual technical_design done and design artifacts, then performs or verifies one implementation action write/readback. Deliverables are exact impl-files nonempty file array from actual owned implementation/test/delegation files and impl-folder scalar directory for browsing. Files may span source/tests outside that browsing directory; every path still must exist safely and match scope. Neither directories nor a design document mislabeled as code substitute for impl-files.
        3. Owner verifies matching features[].implement.actions.implementation done, exact tags/artifacts/contexts and actual Implemented feature handoff for new Designed scope. Authorized advanced CR/resume preserves Tested/Completed status unless explicit transition approved. Writer success alone is insufficient; workflow_action_updated true only for verified actual/prior write, read-only resume otherwise. Free-mode writes no app workflow.
        4. Task/category persistence, Git and fresh-mode next boundary belong only to current owner. Suggest Acceptance Test without invoking/registering it. Unmigrated acceptance impl-files-to-design-link mismatch needs bounded mapping or blocks its claim, never fake a tag. Return to already-active caller, no recursive lifecycle or duplicate boundary.
      </action>
      <output>Original domain result and real file/directory adaptation for current owner</output>
    </step_5_1>
  </phase_5>
</procedure>
```

## Output Result

```yaml
task_completion_output:
  category: "feature-stage"
  status: completed | blocked
  next_task_based_skill:
    - skill: "x-ipe-task-based-feature-acceptance-test"
      condition: "Verify implementation with acceptance tests"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"
  workflow_action_updated: true | false
  task_output_links:
    - "src/"
    - "tests/"
  feature_id: "{FEATURE-XXX}"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Code Implementation"
```

Preserve original keys/order/value types; directory examples are not forced
layout. Collect actual file inventory in existing evidence/tool outputs for
workflow tags separately. No goal/coverage/implementation_files board fields.

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Authoritative context</name><verification>One designed feature, both design parts/spec/architecture/source goals/ACs/current mockups and actual path/config contracts inspected.</verification></checkpoint>
  <checkpoint required="true"><name>Full acceptance preserved</name><verification>Every scoped AC/original assertion/test type maps to selected means and suitable tests; TDD RED/GREEN and baseline/affected regression are real, no weakened/skipped checks.</verification></checkpoint>
  <checkpoint required="true"><name>Correct delegation/routing</name><verification>Skill-creator/MCP first with own tests/DoD; ordinary tools enabled semantic matches sequentially with general fallback; actual outputs verified, gaps block.</verification></checkpoint>
  <checkpoint required="true"><name>Approved means</name><verification>Implementation stays within approved outcome/acceptance/design/constraints, KISS/YAGNI/DRY/800-line rule; authorized affected design log and reruns where contracts changed.</verification></checkpoint>
  <checkpoint required="if_applicable"><name>Mockup fidelity</name><verification>Actual frontend visuals/states/accessibility/responsiveness match current scoped mockups and acceptance; unavailable visual verification explicit.</verification></checkpoint>
  <checkpoint required="true"><name>Delivery verification</name><verification>Actual assertions/integration/regression/lint pass; new executable code coverage at least 80% where applicable, structured delegation checks otherwise; no activity-count surrogate.</verification></checkpoint>
  <checkpoint required="if_applicable"><name>Existing tracing only</name><verification>Applicable existing runtime infrastructure instrumented/redacted/opt-in and tests rerun; absent infrastructure or only test/config/skill changes have explicit skip, no mandatory setup.</verification></checkpoint>
  <checkpoint required="true"><name>Fresh honest evidence</name><verification>Relevant input/implementation/test/config hashes match checks/review; affected deltas invalidated; delivery separate from not measured/cited actual outcome, independent risk review satisfied or blocked.</verification></checkpoint>
  <checkpoint required="true"><name>Verified owner handoff</name><verification>Workflow-mode owner verifies required prior design/context and done/both tags/nonempty actual file array/scalar folder/readback plus Implemented where authorized; original output preserved, no duplicate task/Git/route or status regression.</verification></checkpoint>
</definition_of_done>
```

## Patterns & Anti-Patterns

| Pattern | When | Then |
| --- | --- | --- |
| Ordinary code | Approved designed feature | Outcome/AC map → AAA/TDD → enabled sequential tools → actual validation |
| Special package/protocol | Skill files or MCP server | Delegate first with same readiness; collect own scoped checks, still verify/accept |
| Authorized CR/resume | Affected parent/means delta | Preserve IDs/assertions/advanced status, invalidate dependent evidence only |

| Anti-Pattern | Consequence | Correction |
| --- | --- | --- |
| Component/tool counts as success | Activity over outcome | Full approved acceptance and fresh actual evidence |
| Green by deleting assertions | False delivery | Preserve original expectations and fix behavior |
| General gap ignored | Unsupported implementation | Block affected scope with bounded decision |
| Output directories copied to impl-files | Invalid workflow handoff | Collect real files separately and one browsing directory |
| Mandatory tracing creation or recursive route | Scope/ownership violation | Existing applicable infrastructure only; same owner boundary |

## Examples

See [authored mappings and scenarios](.github/skills/x-ipe-task-based-code-implementation/references/examples.md)
and [integration contract](.github/skills/x-ipe-task-based-code-implementation/references/integration.md).
