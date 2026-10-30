---
name: x-ipe-task-based-technical-design
description: Create a two-part technical design for one refined feature, explaining implementation means against authoritative goals, acceptance and constraints. Use when designing a feature or updating its design. Triggers on requests like "design feature", "technical design", "architecture planning".
---

# Task-Based Skill: Technical Design

## Purpose

Translate one specification into an implementable, two-part design:
1. Read authoritative source/parent goals, subgoals, stories and acceptance.
2. Inspect reusable architecture and consult matching enabled tool capabilities.
3. Justify components, interfaces, data, algorithms and planned checks as means.
4. Verify coverage and return unchanged domain outputs to the lifecycle owner.

## Important Notes

Load the [single-loop delivery policy](.github/skills/x-ipe-workflow-task-execution/references/agent-loop.md)
once in the current context. Execute this skill in the same agent loop; another
skill is expertise, not a new agent. Use proportional checks and reuse current
evidence; independent review is conditional on concrete risk, not the skill name.

BLOCKING: Load `x-ipe-workflow-task-execution` and the
[common lifecycle contract](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md).
Direct entry calls Orient/Plan with the supplied task ID and original context,
without recursively dispatching this skill. Reuse existing readiness context;
one owner handles registration, board/status/Git and the next-task boundary.

BLOCKING: Adopt the [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md)
at the design coverage gate. Reuse existing artifacts and identifiers; no new
board/output schema, goal database, mandatory graph, action tag or approval ritual.
Exactly ONE feature. A component is an implementation means, not an independent
stakeholder goal. Planned checks/review are not observed stakeholder evidence.

Use [design principles](.github/skills/x-ipe-task-based-technical-design/references/design-principles.md)
and the full [design scaffold](.github/skills/x-ipe-task-based-technical-design/references/design-templates.md).
Keep one `technical-design.md` in the resolved owning feature folder with Version
History and Design Change Log; never versioned filenames. Support EPIC/FEATURE
and legacy FEATURE layouts. Reusable cross-feature designs belong in
`x-ipe-docs/architecture/technical-designs/{component}.md`, not a substitute for
the feature document. Generated Markdown links are project-root-relative, not
`../`, `./` or absolute machine paths. Reject escaping/symlinked source paths.

Apply KISS/YAGNI/DRY and the 800-line module threshold. Preserve unrelated dirty
documents/source; no code execution through consulted tools, task CRUD, Git or
child routing. See [integration contract](.github/skills/x-ipe-task-based-technical-design/references/integration.md)
for actual action/status/config semantics and safe completion handoff.

## Input Parameters

```yaml
input:
  task_id: "{TASK-XXX}"
  task_based_skill: "x-ipe-task-based-technical-design"
  execution_mode: "free-mode | workflow-mode"
  workflow:
    name: "N/A"
    action: "technical_design"
    extra_context_reference:
      specification: "path | N/A | auto-detect"
  category: "feature-stage"
  next_task_based_skill:
    - skill: "x-ipe-task-based-code-implementation"
      condition: "Implement the designed feature"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  feature_phase: "Technical Design"
  mockup_list: "N/A"
  feature_id: "{FEATURE-XXX}"
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="existing lifecycle task/readiness; no duplicate registration" />
  <field name="task_based_skill" source="this canonical skill; caller match" />
  <field name="execution_mode" source="lifecycle; free-mode default" />
  <field name="workflow.name" source="exact caller workflow or N/A in free-mode" />
  <field name="workflow.action"><steps>Resolve authoritative ACTION_MAP and template: technical_design. Reject conflicting explicit action; do not derive from spelling.</steps></field>
  <field name="category" source="Output Result: feature-stage" />
  <field name="next_task_based_skill" source="original conditional Code Implementation suggestion, not execution permission" />
  <field name="feature_phase" source="Technical Design" />
  <field name="process_preference.interaction_mode"><steps>Use lifecycle-resolved exact enum/source: interact-with-human, dao-represent-human-to-interact, dao-represent-human-to-interact-for-questions-in-skill. Human asks the human within skill and waits; full DAO and hybrid use bounded representative guidance. Human and hybrid require human completion/route confirmation; full DAO selects only authorized successors. Explicit human approval binds in every mode. Clear inputs need neither.</steps></field>
  <field name="feature_id"><steps>Previous refinement output, explicit authorized identity, then current task context. Query feature board read-only; material ambiguity uses actual decision policy.</steps></field>
  <field name="workflow.extra_context_reference"><steps>Explicit selected specification first, board specification_link next, unique owning EPIC/FEATURE or legacy FEATURE folder last for absent/N/A/auto-detect. A broken explicit link blocks, never falls back. Workflow-mode requires specification context even for N/A.</steps></field>
  <field name="mockup_list"><steps>Previous refinement mockup_list/linked_mockups or Idea Mockup task_output_links, then explicit human path, specification Linked Mockups, idea Mockups and Prototypes, then N/A. Validate current scope/content and identity; dates are not precedence. Open every current frontend/fullstack mockup.</steps></field>
</input_init>
```

Determine `program_type` and `tech_stack` from specification, actual project
artifacts and justified choices during study/design, not guessed input. Known
types: frontend, backend, fullstack, cli, library, skills, mcp; extend with
descriptive lowercase types when warranted. Stack/test frameworks reflect the
approved solution, not every consulted tool.

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>One owner and feature</name><verification>Lifecycle readiness/task context and exactly one existing feature record match scope and protected paths.</verification></checkpoint>
  <checkpoint required="true"><name>Refinement gate</name><verification>New design requires actual Refined status and complete specification. Authorized CR/resume may retain Designed/Implemented/Tested/Completed without regression; Retired or missing refinement evidence blocks.</verification></checkpoint>
  <checkpoint required="true"><name>Authoritative sources</name><verification>Specification and required workflow context match feature and approved roots; goals/story/AC/constraints understood, legacy inference labeled, material gaps surfaced.</verification></checkpoint>
  <checkpoint required="true"><name>Delta and verification</name><verification>Existing design/history/mockups/config/source hashes inspected; affected scope and independent review agreed without replacing foreign edits.</verification></checkpoint>
</definition_of_ready>
```

## Execution Flow

| Phase | Step | Action | Gate |
| --- | --- | --- | --- |
| 1. 博学之 — Study Broadly | 1.1 | Read feature/specification/goals/design/architecture | Authoritative bounded scope |
| 2. 审问之 — Inquire Thoroughly | 2.1 | Consult enabled matches and mockups; resolve questions | Constraints and options understood |
| 3. 慎思之 — Think Carefully | 3.1 | Write/update two-part design and coverage | Justified means and planned evidence |
| 4. 明辨之 — Discern Clearly | 4.1 | Critique/review at current revision | Domain DoD supported |
| 5. 笃行之 — Practice Earnestly | 5.1 | Return completion handoff to same owner | No child routing |

## Execution Procedure

```xml
<procedure name="technical-design">
  <execute_dor_checks_before_starting/>
  <phase_1 name="博学之 — Study Broadly">
    <step_1_1>
      <name>Read Authoritative Feature Context</name>
      <action>
        1. Query feature board read-only via x-ipe-tool-task-board-manager; retain feature_id, title, version, status, specification_link and dependencies.
        2. Read resolved specification, referenced source/parent goals/subgoals, stories, stable leaf AC/test types, FR/NFR, business rules, dependencies, edge cases, constraints and non-goals. Follow parent intent, not component names as goals.
        3. For legacy scope reuse explicit story so-that intent only, label inferred with exact source/story anchor. Missing/ambiguous intent blocks the pertinent outcome/coverage claim, not unrelated established delivery; do not retrofit every historical AC.
        4. Read existing design and architecture/source patterns. Classify actual type/stack; reuse compatible components. Record source/config hashes, actual source/test paths, module sizes and ownership.
        5. Compare authorized delta with existing design/dependencies: affected goals/AC/components/interfaces/data/tests/mockups only. Preserve unaffected IDs, bytes, history and evidence; no baseline means complete new design, not fabricated delta.
      </action>
      <output>Resolved feature model, goal-to-AC scope, reuse/delta plan and gaps</output>
    </step_1_1>
  </phase_1>
  <phase_2 name="审问之 — Inquire Thoroughly">
    <step_2_1>
      <name>Consult Capabilities and Resolve Options</name>
      <action>
        1. Discover actual x-ipe-tool-implementation-* descriptions/When to Use, Built-In Practices and Operations. Read tools.json stages.implement.technical_design and _extra_instruction, never code_implementation.
        2. Exclude metadata keys before activation: missing/empty/metadata-only configuration enables discovered tools; explicit tool booleans activate opt-in filtering and force-enable general. Match enabled tools semantically to actual program_type/tech_stack/responsibility, not filename suffix alone. General is available fallback, not mandatory execution or automatic winner. Multiple relevant matches may be consulted (MCP protocol plus Python runtime); unrelated enabled tools need not be loaded.
        3. Read matched capabilities INFORMATIONAL ONLY; do not invoke implement/fix/refactor or run tool procedures. Record enabled/matched/excluded tools and applicability in Tool Capability Summary. Disabled specific tool means report gap and consult eligible fallback, not bypass config.
        4. Research official documentation and existing project/library patterns as needed; check runtime/version/license compatibility. Options are selected/rejected/deferred means bounded by authoritative outcome/AC/constraints, not extra goals or backlog mandates.
        5. For frontend/fullstack open and analyze all current provided/linked mockups: hierarchy/layout, spacing/colors, states/events, accessibility/responsiveness. Map mockup elements to components and acceptance in Part 2. Mockup is visual source of truth within approved scope; conflicts require bounded question, not scope expansion.
        6. Ask only consequential unresolved questions: human asks human and waits; full DAO and hybrid use common message_context and consume instruction_units/execution_plan. Guidance cannot invent KPIs, confirm stakeholder intent, authorize CR scope or replace required human approval. Clear inputs skip questions.
      </action>
      <output>Evidence-backed options, capability summary and mockup constraints</output>
    </step_2_1>
  </phase_2>
  <phase_3 name="慎思之 — Think Carefully">
    <step_3_1>
      <name>Create or Update Two-Part Design</name>
      <action>
        1. Use design-templates.md at owning feature folder/technical-design.md. Preserve language/structure on updates, one file/version/history and project-root links.
        2. Part 1: scope/non-goals, authoritative goal/subgoal frame, component table with Tags, dependency table/design links, major flow, usage example, actual program_type/tech_stack and Tool Capability Summary. Explain enabling contribution and all-required children versus alternative means.
        3. Part 2: implementation-type-specific workflows/diagrams, interfaces/signatures/API or CLI contracts, data/storage, algorithms/state transitions, ordered implementation steps/source/test paths, edge/error/security handling, planned unit/integration/UI/API tests and mockup-to-component mapping. Part 2 remains complete and independent of tool availability.
        4. Coverage table links source/parent goal, story/subgoal and every scoped AC to justified component/flow, interface/data/algorithm contract and concrete planned validation. Add qualitative outcome scenario with observable conditions/result, source and evidence gap; no invented numerical targets or scope.
        5. Goals and constraints control tradeoffs; justify every selected component or required support concern. Rejected alternatives are not work items. Separate planned delivery checks from observed stakeholder outcome/not measured. A design/test plan is not a passing implementation test.
        6. Authorized intent/parent/means delta invalidates only affected design/test/outcome evidence and dependent claims. Preserve unrelated mappings/history; identify downstream reruns in the same design. Scope/acceptance changes require authorized CR/human-intent boundary, not autonomous rewrite.
        7. Design tracing/observability where applicable: existing infrastructure, INFO/DEBUG boundary, sensitive parameter/log redaction, errors without secrets, opt-in/config behavior and tests; document N/A rationale otherwise. Do not instrument or execute code in design.
        8. Apply KISS/YAGNI/DRY and 800-line module threshold; increment authorized version and append Design Change Log only for actual changes, not no-op resume.
      </action>
      <output>One revision-bound technical-design.md with coverage/planned checks</output>
    </step_3_1>
  </phase_3>
  <phase_4 name="明辨之 — Discern Clearly">
    <step_4_1>
      <name>Critique and Verify</name>
      <action>
        1. Check each scoped source/parent goal/story/AC has a contribution chain, justified means and planned validation; outcome scenario respects source/constraints and labels unavailable observations. No orphan AC, invented KPI, false delivery or implicit outcome achievement.
        2. Check compatible technologies/patterns, complete interfaces/data/algorithms/tests and mockup fidelity; no speculative feature/dependency contradiction. Verify domain DoD and paths.
        3. Resolve only specific conflicts per actual mode; revise affected sections. Never ask broad is-this-correct questions or add approval loops when clear.
        4. Self-check the design against scoped ACs and actual interfaces. Apply the shared risk policy before requesting independent review; a changed design alone is not a review trigger. Bind applicable evidence to relevant revisions and rerun only affected checks.
      </action>
      <output>Current verification with explicit unresolved gaps/review limits</output>
    </step_4_1>
  </phase_4>
  <phase_5 name="笃行之 — Practice Earnestly">
    <step_5_1>
      <name>Return Completion Handoff</name>
      <action>
        1. Verify DoD; return original task_completion_output fields and actual links/feature/version/type/stack/mockups. Block unsupported claims.
        2. Same lifecycle owner performs or verifies workflow-mode action technical_design with exact tech-design file and feature-docs-folder scalar directory tags after required specification/refinement checks. Success plus state/artifact readback required; free-mode writes no app workflow. workflow_action_updated true only for verified actual/prior write, otherwise false.
        3. Owner performs required feature handoff to actual Designed for new Refined design; preserve advanced CR/resume status unless explicitly authorized to change it. Keep design links in existing task_output_links/action deliverables; technical_design_link is not a board field. Task/category persistence and fresh-mode boundary remain owner's responsibility; this child does not route/register another task.
      </action>
      <output>Unchanged domain output and same-owner handoff, no recursive task/Git/routing</output>
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
    - skill: "x-ipe-task-based-code-implementation"
      condition: "Implement the designed feature"
  process_preference:
    interaction_mode: "{from input process_preference.interaction_mode}"
  execution_mode: "{from input}"
  workflow:
    name: "{from input}"
  workflow_action: "{workflow.action}"
  workflow_action_updated: true | false
  task_output_links:
    - "x-ipe-docs/requirements/FEATURE-XXX/technical-design.md"
  mockup_list: {from input mockup_list, pass to next task if applicable}
  feature_id: "FEATURE-XXX"
  feature_title: "{title}"
  feature_version: "{version}"
  feature_phase: "Technical Design"
  program_type: "frontend | backend | fullstack | cli | library | skills | mcp | ..."
  tech_stack: ["Python/Flask", "JavaScript/Vanilla", "HTML/CSS"]
```

Legacy path/stack examples above are placeholders, not forced layout/technology.
Use resolved artifacts; preserve keys/order/conditional successor. No goal or
coverage fields added to board/output. Return to already-active caller, never
invoke the lifecycle recursively.

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Complete two-part artifact</name><verification>One design has Part 1 tags/dependencies/flow/usage and Part 2 type-specific interfaces/data/algorithms/steps/tests/errors/paths, Version History and Design Change Log.</verification></checkpoint>
  <checkpoint required="true"><name>Goal coverage</name><verification>Every scoped source/parent goal/story/AC maps to means/planned checks; outcome scenario and gaps distinguish delivery from not measured/actual observation.</verification></checkpoint>
  <checkpoint required="true"><name>Bounded design</name><verification>Goals/constraints control options; KISS/YAGNI/DRY and 800-line rule; unaffected IDs/bytes/evidence retained, affected claims invalidated.</verification></checkpoint>
  <checkpoint required="true"><name>Consultation</name><verification>Actual type/stack and enabled semantic matches recorded; technical_design config/extra instruction respected; no tool execution; Part 2 independent of availability.</verification></checkpoint>
  <checkpoint required="if_applicable"><name>Mockups and diagrams</name><verification>Current frontend/fullstack mockups mapped; workflow diagrams for complex flows and class diagram where useful; N/A otherwise.</verification></checkpoint>
  <checkpoint required="true"><name>Safety and revision</name><verification>Safe links/paths, security/tracing redaction or N/A, source/config/design hashes and proportionate independent review; missing evidence explicit.</verification></checkpoint>
  <checkpoint required="true"><name>Verified owner handoff</name><verification>Owner verifies workflow done/both tags/artifacts and Designed where authorized; design links use existing outputs, no new board fields, task duplication, status regression, Git or child routing.</verification></checkpoint>
</definition_of_done>
```

## Patterns & Anti-Patterns

| Pattern | When | Then |
| --- | --- | --- |
| API/service | Backend/API | Auth/request/response/data/error contracts and complex sequence flows |
| UI-heavy | Frontend/fullstack | Current mockup elements/states mapped to components/acceptance/UI checks |
| Delta-first | Authorized CR/resume | Affected contracts only; preserve advanced status/history/unrelated evidence |

| Anti-Pattern | Consequence | Correction |
| --- | --- | --- |
| Components promoted to goals | Scope inflation | Justify means against authoritative outcomes/constraints |
| All enabled tools executed | Boundary violation | Consult relevant enabled capabilities only |
| Writer success alone | False completion | Verify done, contexts, tags, feature and actual artifacts |
| Plan equals outcome | False stakeholder claim | Separate planned delivery, verified delivery and observation |
| No-op rewrite/recursive handoff | History/ownership corruption | Keep bytes/same owner; return suggestion only |

## Examples

See [authored artifacts/scenarios](.github/skills/x-ipe-task-based-technical-design/references/examples.md)
and [integration contract](.github/skills/x-ipe-task-based-technical-design/references/integration.md).
