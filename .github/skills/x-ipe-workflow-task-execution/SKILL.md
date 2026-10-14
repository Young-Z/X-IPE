---
name: x-ipe-workflow-task-execution
description: Orchestrates the shared Orient, Plan, Execute, Verify, Record task lifecycle with one owner, safe resume, mode-aware decisions and evidence-backed routing. Use when implementing features, fixing bugs, refactoring code, designing architecture, setting up projects, or entering a task skill directly. Triggers on requests like "implement feature", "fix bug", "refactor code", "set up project".
---

# Shared Task Execution Lifecycle

## Purpose

Coordinate one authorized task at a time through Orient → Plan → Execute →
Verify → Record. Domain skills produce work and evidence; this workflow owns
registration, lifecycle persistence, boundary decisions and authorized routing.

## Important Notes

BLOCKING: Load the [common lifecycle contract](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md)
before invoking a child. Child skills entering directly must load this workflow
and call its Orient/Plan ensure/resume entry before domain work.

Use the [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md)
when an adopting child's domain gate requires it. Keep goal/evidence mappings in
existing artifacts; no board/output schema changes or implicit child migration.

CRITICAL: One task owner. Never recursively execute the workflow or a domain
skill already on the invocation stack. A child returns domain output to its
caller; it does not independently register, close, commit, or execute the next task.
An unmigrated child with conflicting lifecycle instructions requires a bounded
adapter agreeing ownership before invocation; unresolved conflict blocks execution.
Publication does not silently rewrite or declare all live children migrated.

BLOCKING: No upfront speculative chain. A next-task suggestion is not permission.
Only ensure/register the current approved task; register a successor after the
current evidence and interaction boundary authorize it.

CRITICAL: No automatic commit, implicit push, dirty branch switch, stash, reset,
or broad staging. Preserve configured Git strategy without moving dirty work.
No application workflow skips or mandatory-gate relaxations are introduced.

## About

- **Owner:** current authorized caller with exact persisted role and task context.
- **Domain entry:** child skill selected dynamically, executed once after readiness.
- **Evidence revision:** hashes of source artifacts, implementation, tests and
  configuration relevant to a claim; timestamps alone cannot prove freshness.
- **Small path:** one explicit combined deliverable can cover multiple planning
  sections for bounded work; it cannot fake completed actions or replace domain gates.

## Input Parameters

Retain the existing Task Data Model; this is not the persisted board schema.

```yaml
input:
  task:
    task_id: "supplied ID or null for genuinely new work"
    task_based_skill: "discovered canonical skill"
    task_description: "approved scope; reuse original board description on resume"
    category: "derived from child Output Result"
    role_assigned: "authorized owner"
    status: "current board status"
    last_updated: "board-generated timestamp"
  execution_mode: free-mode | workflow-mode
  workflow:
    name: "N/A or exact workflow identity"
    action: "authoritative action identity or null"
    extra_context_reference: {}  # path | N/A | auto-detect, child keys preserved
  execution:
    next_task_based_skill: null
    process_preference:
      interaction_mode: interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill
    task_output_links: []
    dynamic_attributes: {}
  git:
    strategy: main-branch-only | dev-session-based
    main_branch: "configured or locally detected"
  closing:
    category_level_change_summary: null
```

### Input Initialization

```xml
<input_init>
  <field name="task"><steps>Use supplied ID and original role/task_type/description when resuming. Adapt role_assigned to role, task_description to description, selected task type to task_type; never send the whole Task Data Model to CRUD. Query current board state; board owns timestamps.</steps></field>
  <field name="task.task_based_skill"><steps>Match attached discovered descriptions or scan task-based and assistant SKILL.md frontmatter; exact explicit skill wins if authorized. Ambiguity uses the decision policy. Read its declared category and outputs, never infer category from its name.</steps></field>
  <field name="execution_mode"><steps>--workflow-mode@name or --workflow-mode selects workflow-mode; otherwise free-mode. Named workflow must resolve uniquely through the app interactor; missing or ambiguous identity blocks workflow claims.</steps></field>
  <field name="workflow"><steps>Preserve name/action/extra_context_reference. Resolve action from the authoritative ACTION_MAP and verify against the current workflow template and requested skill. Resolve required artifacts by the common contract; free-mode retains validated legacy fallback.</steps></field>
  <field name="execution.process_preference"><steps>Explicit current --interaction@MODE or user task override, then named workflow global.process_preference, then legacy --proceed flags/user intent, then interact-with-human. Normalize --proceed@auto to full DAO and --proceed@stop-for-question to hybrid; manual to human. Reject unknown enums; record source and re-read at every decision/boundary.</steps></field>
  <field name="execution"><steps>Capture full child output unchanged; adapt next-task forms only for selection, preserve dynamic fields and links. Validate the common output contract before lifecycle persistence.</steps></field>
  <field name="git"><steps>Read approved root .x-ipe.yaml; strategy defaults main-branch-only. Use git.main-branch or local refs/remotes/origin/HEAD, then existing main/master; ambiguity blocks Git mutation. dev-session-based uses validated real Git identity, not nickname. Capture branch, staged and unstaged/untracked paths before work; pass git_strategy/git_main_branch to existing child inputs.</steps></field>
  <field name="closing"><steps>Derive required category/feature updates from child contract or discovered category skill. Missing mandatory category work blocks completion; optional unavailable integrations are reported, never invented.</steps></field>
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true"><name>Identity and scope</name><verification>Approved root, current task ID/context/owner and write paths known; ownership exact and session authority established.</verification></checkpoint>
  <checkpoint required="true"><name>Domain and policy</name><verification>Selected child and common contract loaded; mode source and single lifecycle owner agreed; no invocation cycle.</verification></checkpoint>
  <checkpoint required="true"><name>Inputs and workflow</name><verification>Required artifacts exist, resolve within approved roots, match feature/context and action; domain DoR and application gates remain enforced.</verification></checkpoint>
  <checkpoint required="true"><name>Preservation and verification</name><verification>Dirty baseline protected; Git strategy resolved; required tests/review and revision evidence planned.</verification></checkpoint>
</definition_of_ready>
```

## Execution Flow

| Phase | Coordination | Gate |
| --- | --- | --- |
| Orient | Resolve request, domain, policy, source links and protected paths | Authorized scope and inputs |
| Plan | Ensure/resume one task and choose proportional deliverables/tests | Matching board identity + domain readiness |
| Execute | Invoke child domain once | Full child result and artifacts |
| Verify | Verify output, evidence freshness, action/category gates and review | No unsupported completion claim |
| Record | Persist verified state; report; resolve one next boundary | Authorized next task or stop |

## Execution Procedure

```xml
<procedure name="x-ipe-workflow-task-execution">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>
  <phase_1>
    <name>Orient</name>
    <action>
      1. Load common contract and dynamically selected skill; resolve inputs as above.
      2. Establish one lifecycle owner; direct child entry calls this entry once and resumes domain work only after it returns readiness context. Do not dispatch the same child back to itself.
      3. Capture protected dirty paths and source revisions; identify real decisions and route through exact mode policy. Clear inputs do not require a ceremonial question or DAO call.
      4. Verify artifact links and action identity; loading a tool capability for design is not authorization to execute code.
      5. For adopting children, locate stakeholder goal/subgoal, source/parent and evidence gaps in the existing artifact per goal contract; legacy inference is labeled, ambiguity blocks only the pertinent claim.
    </action>
    <gate>Authorized scope, policy and caller identity resolved</gate>
  </phase_1>
  <phase_2>
    <name>Plan</name>
    <action>
      1. Load board manager. Supplied ID: query then task_ensure.py --task JSON with original context; genuine not-found permits ensure of exactly that ID. Never allocate a replacement on conflict or corruption.
      2. No supplied ID: all-date ownership queries, consume all pages and exact role matches; identify same-session context, not nickname alone. For genuinely new work call task_create.py once, retain returned ID; retries use ensure.
      3. Matching in_progress resumes without re-registering or resetting outputs. pending starts after readiness; blocked/deferred resume only when dependency/permission is resolved. completed/cancelled/skipped returns existing result without reopening or routing again. Another owner/context blocks without mutation.
      4. Choose explicit deliverables, tests, review and next decision. A small clear path may combine scope, acceptance and design sections in one linked artifact; name every covered requirement and retained gate. Do not precreate downstream tasks.
      5. Preserve main-branch-only or dev-session-based strategy. If wrong branch and dirty, block branch-sensitive mutation and request a safe authorized disposition; no switch, stash or pull. Clean branch preparation still requires authority; no network or identity changes by default. Recheck domain DoR, then owner updates current task to in_progress and queries it.
    </action>
    <gate>One matching task and domain readiness; no speculative chain</gate>
  </phase_2>
  <phase_3>
    <name>Execute</name>
    <action>
      1. Pass task ID, resolved mode, execution_mode, workflow.name/action/context, Git strategy and child-specific fields. Invoke the child domain procedure once, or return readiness to an already-entered direct child.
      2. Child reads common lifecycle contract, performs its domain steps and actual decision policy, preserves domain gates and returns task_completion_output (or its declared operation result when an assistant/tool is coordinated). Do not force task output fields onto tools.
      3. Route actual within-skill questions per mode: human asks the human and waits; full DAO and hybrid use the representative for bounded guidance. DAO calls use message_context and consume operation_output.result.instruction_units plus execution_plan; do not use legacy type:routing input. Guidance cannot authorize new scope or protected operations. Conflicting child mode wording needs a bounded compatibility adapter or blocks invocation; preserve current FEATURE-044-E/UI semantics, not earlier unauthorized review claims.
      4. Child next-task execution/board/Git blocks are delegated to this owner, not recursively invoked. Collect all output fields, domain DoD evidence and exact changed paths. On failure preserve artifacts and return blocked/deferred as appropriate, not completed.
    </action>
    <gate>Domain result collected; no recursive execution</gate>
  </phase_3>
  <phase_4>
    <name>Verify</name>
    <action>
      1. Validate common output fields and declared category; preserve dynamic attributes. Confirm domain DoD and tests, failed assertions and required review honestly. Independent review required for meaningful workflow/executable/safety/public-contract changes; unavailable review blocks publication, not candidate drafting.
      2. Rehash relevant source/implementation/tests/config and compare evidence revision. Any edit invalidates affected tests, review and acceptance; rerun or report blocked. A passing receipt or timestamp alone is insufficient.
      2a. Where the child adopts the goal contract, verify source/goal/story/AC/validation coverage and authorized delta invalidation. Separate verified engineering delivery from observed stakeholder outcome or not measured; do not invent metrics, observations or confirmation.
      3. In workflow-mode, resolve state via workflow_get_state.py and inspect shared.stage.actions.action or the matching features[].stage.actions.action. Required completed action must be done, not merely non-pending. Verify keyed deliverables against extract tags, all required links/files and feature context; missing state/action or failed/skipped/in_progress is blocking, never warn-and-pass.
      4. Domain completion writes use existing workflow_update_action.py flags and real tag-to-path values only, once by the agreed owner; if child already wrote, verify instead of replaying. No skipped writes, fake done or automatic prerequisite completion. Free-mode does not mutate app workflows.
      5. Derive category work from the selected contract and verify required updates. Do not mark board completed before these checks. Re-read mode source before the boundary; a mode change cannot retroactively authorize unapproved work.
    </action>
    <gate>Claims supported at current revision; required gates satisfied</gate>
  </phase_4>
  <phase_5>
    <name>Record</name>
    <action>
      1. Persist only verified lifecycle status, output_links and next_task through board manager with ownership query before and after. Map task_output_links to output_links and null next_task_based_skill to empty next_task. Retain broader-task in_progress when only one slice is candidate_ready; record slice evidence outside board if board writes are excluded.
      2. Git changes may remain uncommitted by default. Commit only with explicit user approval for exact owned paths, reviewing staged and unstaged diffs against protected baseline. Never git add -A, git add . or files=null. Preexisting staged changes block committing until separately approved isolated disposition; never silently unstage them. Push/PR/network actions require separate explicit authority, even in full DAO.
      3. Return existing output aggregate and full child result without renamed schemas. State candidate readiness separately from promotion/release and list unresolved issues.
      4. Apply one boundary: human asks actual decisions and waits for human completion/route confirmation; full DAO answers within skill and chooses only authorized routes; hybrid uses DAO within skill, then waits for human completion/route confirmation. Explicit domain-required human approval still blocks until obtained in every mode. Representative approval is guidance, not human permission. No successor or no authorized route means stop, not invent work.
      5. After authorization, dynamically select the next skill from current result/context; ensure a newly approved task through Orient/Plan. Never execute child routing twice. Record already-handled boundary on resume in existing task evidence/dynamic context, not a new board field.
    </action>
    <gate>Verified record and one mode-aware boundary; successor authorized or stopped</gate>
  </phase_5>
</procedure>
```

## Output Result

Preserve the existing aggregate `output`, not generic `workflow_output` or a new
board schema. Full child result is retained in dynamic_attributes when needed.

```yaml
output:
  task_id: "current task"
  task_based_skill: "selected canonical skill"
  task_description: "original scope"
  category: "child-declared category"
  role_assigned: "owner"
  status: completed | blocked | deferred | in_progress | cancelled | skipped
  execution_mode: free-mode | workflow-mode
  workflow:
    name: "exact name or N/A"
  category_level_change_summary: null
  process_preference:
    interaction_mode: "resolved exact enum"
  task_output_links: []
  next_task_based_skill: null
  dynamic_attributes: {}  # full child output, revision evidence, bounded slice state
```

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Single ownership</name><verification>One current task registered/resumed; owner and original context preserved; no recursive or speculative execution.</verification></checkpoint>
  <checkpoint required="true"><name>Domain result</name><verification>Common output and dynamic fields retained; required domain DoD, category and action gates verified or honest noncompletion returned.</verification></checkpoint>
  <checkpoint required="true"><name>Fresh evidence</name><verification>Artifacts and test/review evidence match current relevant revisions; candidate_ready distinguished from publication and larger-task completion.</verification></checkpoint>
  <checkpoint required="true"><name>Safe records</name><verification>Authorized board write queried; dirty paths/staging preserved; commit/push absent unless separately approved.</verification></checkpoint>
  <checkpoint required="true"><name>Boundary resolved</name><verification>Fresh exact mode respected; human and hybrid retain human completion/route confirmation, hybrid DAO only within skill, DAO authority bounded, one successor authorized or stopped.</verification></checkpoint>
</definition_of_done>
```

## Skill Registry

Registry is discovery-based, not a hardcoded domain/category mapping.

| Discovered role | Input | Output |
| --- | --- | --- |
| Current task-based/assistant SKILL.md descriptions | Authorized request + context | Selected skill, declared category and output contract |
| x-ipe-tool-task-board-manager | Actual CRUD JSON and supplied ID | Existing record or safe registration; verified update |
| x-ipe-assistant-user-representative-Engineer (decision policy only) | message_context, human_shadow | operation_output.result.instruction_units + execution_plan |
| x-ipe-tool-x-ipe-app-interactor (workflow-mode only) | Exact workflow/action/feature/tags | Existing state and verified action write |
| Required category integrations from child/discovery | Full child result | Verified category changes; optional unavailable integration reported |
| x-ipe-tool-git-version-control (explicitly authorized only) | Strategy and approved exact paths | Bounded Git receipt, never automatic release |

Authoritative action identity comes from [ACTION_MAP](src/x_ipe/static/js/features/workflow-stage.js),
with gates/tags from [workflow template](x-ipe-docs/config/workflow-template.json).
Enabled tool routing comes separately from [tools configuration](x-ipe-docs/config/tools.json):
the workflow action `implementation` is NOT the tool key `code_implementation`.
See [common contract](.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md)
for exact schemas, modes, statuses, source resolution and child entry obligations.

## Error Handling

| Condition | Recovery |
| --- | --- |
| Missing task | Ensure supplied ID only after genuine not-found; never replace on error |
| Ownership/context/corrupt board conflict | Stop without mutation; request authorized resolution |
| Invalid mode, cycle or unresolved lifecycle owner | Block invocation; no guessed policy |
| Missing/ambiguous source or action | Block required claim; validated legacy fallback only for absent/auto inputs |
| Dirty wrong branch or staged foreign changes | Preserve all bytes/index; no implicit switch/stash/commit |
| Stale/failed evidence | Rerun affected checks, otherwise blocked; retain partial outputs |
| Independent review unavailable | Candidate drafting allowed; promotion blocked |

No destructive rollback by default. Preserve partial domain output and report
recovery scope; retry only bounded idempotent operations with the same identity.

## Examples

- [Direct entry, mode boundaries and combined deliverables](.github/skills/x-ipe-workflow-task-execution/references/examples.md)
- [Task Data Model and CRUD adaptation](.github/skills/x-ipe-workflow-task-execution/templates/task-record.yaml)
