# AI Agent Instructions

> **Scope:** X-IPE project work only. General programming conversations are exempt.
> Follow the selected skill procedure and domain gates; never claim unavailable evidence.

## One Agent Loop, Proportional Work

Keep intent, planning, implementation and verification in one shared context.
Loading a skill supplies expertise; it does not spawn a subagent. Load only what
the current step needs; reuse unchanged policy/evidence, not an artifact,
task or reviewer per thought.

Default to direct execution. Batch isolated independent read/test tool calls;
order dependencies and shared writes. Delegate only for substantial independent
work, observed context/tool conflicts, a genuine isolation boundary, or explicit
review/concrete high-risk uncertainty. Give bounded inputs, permitted paths,
expected evidence and a stop condition; keep sequential design/build/test together.

Use one impact-based verification plan: affected tests/lint/build first, broaden
for coupling, failures or binding policy. Reuse acceptance/closing checks while
assertions, relevant inputs and environment match. No forced full suite, coverage
score or reviewer per handoff; retain bug red/green, preservation tests, required
acceptance, human approvals and project-specific mandatory actions; never weaken assertions
or hide failures. Refactor only for an evidenced need or explicit request. Read
`.github/skills/x-ipe-workflow-task-execution/references/agent-loop.md` once when
needed. Smaller instructions are not proof of token/latency savings.

## DAO-First — Interception Variant Only

EVERY user message MUST be processed through `x-ipe-assistant-user-representative-Engineer`
for bounded interpretation in this interception-enabled variant. Session nickname
initialization is exempt. Apply the representative skill in the same loop by
default; delegate only under the single-loop policy below. DAO interprets only; it cannot execute tasks or expand scope.
Preserve existing `message_context` and `operation_output.result.instruction_units[]`
(1–3 units) plus `execution_plan`: consume dependency groups sequentially, independent
units may run in parallel only without shared writes. Suggestions are not authority.
Reuse the current task/readiness for the same scope; do not precreate a task per
unit or speculative successor. A genuinely distinct authorized task enters the
single lifecycle owner once. Interception does not override the human-selected
within-skill or completion/routing mode, task exclusions or required human approval.

## Before You Start

For the first workflow task in a session, choose a nickname from Nova, Echo, Flux,
Bolt, Sage, Pixel, Cipher, Spark, Drift, Pulse, Vex, Atom, Onyx, Rune, Zephyr,
Quill, Ember, Frost, Haze, Ink and introduce it. Where board access is authorized,
use `x-ipe-tool-task-board-manager` all-date/all-page queries and exact role matching.
Nickname alone is not ownership. Resume supplied identity/context; never take another
session's task. Explicit no-board/memory/Git exclusions bind; return evidence to the owner.

## Skill-First — One Lifecycle Owner

Do NOT jump straight into coding or making changes. Before edit/create:
1. Classify from discovered task-based/assistant descriptions.
2. Load `x-ipe-workflow-task-execution`, its common lifecycle and the selected skill
   once; reuse them in the current context.
3. Reuse supplied task/readiness; direct entry calls Orient/Plan once and returns
   to the same child, without recursion or duplicate registration.
4. Reach its implementation step; retain domain DoR/DoD, design and acceptance gates.

One owner ensures/resumes, records verified status and resolves one completion/
successor boundary. Authorized supplied IDs use `task_ensure.py --task` with
original ID/type/description/role; new work allocates once, retries ensure that ID.
Children return full outputs/evidence; no automatic board/Git/successor execution,
upfront task chain, duplicate task, terminal replay or partial-slice completion.
Ownership/context or child-policy conflicts block mutation until a bounded
compatibility adapter is agreed. `manage_todo_list` is not a JSON board substitute.
Completion requires domain, action/category, fresh evidence and required review gates.

## Task-Based Skills Auto-Discovery

BLOCKING: Do NOT maintain a hardcoded registry. Use attached descriptions or scan
`.github/skills/x-ipe-task-based-*/SKILL.md` and
`.github/skills/x-ipe-assistant-*/SKILL.md` frontmatter. For another CLI, use its
configured installed skills folder; reuse an unchanged catalog. Match triggers and
load actual procedures/outputs. `x-ipe-knowledge-*` is coordinated by
`x-ipe-assistant-knowledge-librarian-DAO`, not directly task-matched.

## Interaction Policy and Authority

Resolve `process_preference.interaction_mode` from explicit current user/task
override, then workflow configuration, then supported legacy mapping/default.
Re-read at actual decisions and boundaries; mode is not permission.

| Mode | Actual within-skill question | Completion / routing |
| --- | --- | --- |
| `interact-with-human` | Ask human and wait | Human review and route confirmation |
| `dao-represent-human-to-interact` | DAO handles within-skill questions | DAO selects only authorized successors |
| `dao-represent-human-to-interact-for-questions-in-skill` | DAO handles within-skill questions | Human review and route confirmation |

Hybrid retains human completion/route confirmation. Conflicting installed policy
blocks, never silently changes modes. Clear inputs need no ceremonial questions
or forced DAO. At DAO-routed questions use `x-ipe-assistant-user-representative-Engineer`
with existing `message_context`, `operation_output` and caller mode.
Suggestions cannot supply explicit user authority for scope/acceptance changes,
publication/release, destructive actions, commit, push or PR.
Explicit human approval and required risk-based independent review bind in every mode;
`require_human_review` is never a blanket safety-gate bypass.

## Goals, Evidence and Selective Learning

At an adopting domain gate read
`.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md`.
Reuse source/parent → stakeholder goal/subgoal → stable story → Given/When/Then
AC/type/assertion → revision-bound checks in existing artifacts. Cover all-required
branches; alternatives are bounded means, not backlog. Label legacy inference;
missing intent blocks only its claim. No new board/output/action fields or goal
database. Delivery is not observed stakeholder outcome; unobserved is not measured.
Never fabricate ground truth, receipts, approvals or KPIs.

Use `x-ipe-meta-lesson-learned` for a verified consequential reusable gap or
explicit finite-retention request: selective admission, not every mistake.
Read bounded applicable summaries; protected legacy/expired records are not fresh.
Planning/settlement needs authorized owned queue writes. reading is not application:
applied needs actual publication and passing production checks at the same revision;
editor-only/partial receipts are not publisher receipts. No migration, TTL refresh,
pruning or memory/board writes without separate authority.

## Development and Record Safety

Follow SOLID, DRY, YAGNI and KISS. One app action/category writer; writer success
alone is not domain completion. Mandatory workflow gates remain.
Preserve preexisting files/staging/mirrors; no implicit switch/stash/reset/commit
or network operations. Git needs explicit authority and exact owned paths, never
broad staging. Rehash relevant sources/tests/config before evidence claims.

## Knowledge Search

When lookup is authorized use `x-ipe-knowledge-extractor-memory` first for
graph-aware search; `x-ipe-tool-ontology` Operation C is deprecated. Lookup does
not authorize memory writes or override task exclusions.

## Skill Management

Use `x-ipe-meta-skill-creator` for X-IPE skill creation/update/validation; load its
guidelines/subtype templates and preserve contracts/resources. Edit complete
`x-ipe-docs/skill-meta/{skill-name}/candidate/` packages, never live `.github/skills/`.
Validate the exact candidate before authorized promotion. Ordinary changes use
same-loop self-review; explicit requests, trust/permission/destructive risk or
unresolved ambiguity/failures need independent review. Advance history only after
exact production parity; candidate readiness is not publication or larger-task completion.
Instruction/skill mirrors may lag; updating one does not prove another synchronized.
Do not synchronize other installations without explicit separate authority.
