# AI Agent Instructions

> **Scope:** X-IPE project work only. General programming conversations are exempt.
> Follow the selected skill procedure and domain gates; never claim unavailable evidence.

## Before You Start

For the first workflow task in a session, choose a nickname from Nova, Echo, Flux,
Bolt, Sage, Pixel, Cipher, Spark, Drift, Pulse, Vex, Atom, Onyx, Rune, Zephyr,
Quill, Ember, Frost, Haze, Ink and introduce it. Where board access is authorized,
use `x-ipe-tool-task-board-manager` queries across dates/pages to check ownership.
Nickname alone does not establish session ownership. Resume supplied identity and
context; never take another session's task. Explicit exclusions (including no
board, memory or Git operations) remain binding; return evidence to the owner.

## Skill-First — One Lifecycle Owner

Do NOT jump straight into coding or making changes. Before edit/create:
1. Classify from discovered task-based/assistant descriptions.
2. Load `x-ipe-workflow-task-execution`, its common lifecycle and the selected skill.
3. Reuse supplied task/readiness; direct entry calls Orient/Plan once and returns
   to the same child, without recursion or duplicate registration.
4. Reach the selected implementation step, retaining domain DoR/DoD, design,
   failing-before/fixed-after bug tests and acceptance gates.

The lifecycle owner alone ensures/resumes, persists verified status and resolves
one completion/successor boundary. Supplied IDs use `task_ensure.py --task` with
original ID/type/description/role only where board access is authorized. Genuine
new work allocates once; retries ensure that ID. Children return full original
outputs/evidence, without automatic board/Git/successor execution. No upfront task
chain, duplicate per-unit task, terminal replay or false completion of a partial
slice. Another owner/context or conflicting child lifecycle policy blocks without
mutation; agree a bounded compatibility adapter before invoking that child.
`manage_todo_list` is not a JSON board substitute. Completion writes require all
domain, action/category, fresh evidence and required review gates to pass.

## Task-Based Skills Auto-Discovery

BLOCKING: Do NOT maintain a hardcoded registry. Use attached descriptions or scan
`.github/skills/x-ipe-task-based-*/SKILL.md` and
`.github/skills/x-ipe-assistant-*/SKILL.md` frontmatter. Match triggers and load
actual procedures/outputs. `x-ipe-knowledge-*` is coordinated by
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

Hybrid is DAO inner-skill only with human completion/route confirmation, matching
current FEATURE-044-E specification, app UI/config and transport tests. Earlier
lifecycle review claimed an unauthorized inversion. Conflicting installed wording
is a blocking compatibility finding, not authority to invert UI or silently
migrate children. Clear within-skill inputs need neither ceremonial questions nor forced DAO.
At DAO-routed questions use `x-ipe-assistant-user-representative-Engineer` with
existing `message_context`, preserving `operation_output` and caller mode.
Suggestions/approval-like guidance cannot supply explicit user authority for
scope/acceptance changes, publication, release, destructive actions, commit, push
or PR. Explicit human approval and independent review bind in every mode;
`require_human_review` is never a blanket safety-gate bypass.

## Goals, Evidence and Selective Learning

At an adopting domain gate read
`.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md`.
Use existing artifacts: source/parent → stakeholder goal/subgoal → stable story,
Given/When/Then AC/type/assertion → planned and actual revision-bound checks.
Cover all-required branches; alternatives are selected bounded means, not an
automatic backlog. Label legacy inference with its source. Missing intent blocks
only the pertinent claim. No new board/output/action fields or goal database.
Delivery checks are not observed stakeholder outcome; unobserved is not measured.
No fake ground truth, receipt, approval or KPI.

Use `x-ipe-meta-lesson-learned` for a verified consequential reusable gap or
explicit finite-retention request: selective admission, not capture-everything.
Select bounded applicable summaries read-only; protected legacy/expired records
are not fresh lessons. Planning/settlement needs authorized owned queue writes.
reading is not application: applied requires actual publication and relevant
passing production verification at the same revision. Do not normalize editor-only
or partial receipts into publisher receipts. No historical migration, TTL refresh,
pruning, memory/board writes or invented ground truth without separate authority.

## Development and Record Safety

Follow SOLID, DRY, YAGNI and KISS. One writer handles app action/category updates;
writer success alone is not domain completion. Mandatory workflow gates remain.
Preserve preexisting files/staging/mirrors; no implicit switch/stash/reset/commit
or network operations. Git needs explicit authority and exact owned paths, never
broad staging. Rehash relevant sources/tests/config before evidence claims.

## Knowledge Search

When lookup is authorized use `x-ipe-knowledge-extractor-memory` first for
graph-aware search; `x-ipe-tool-ontology` Operation C is deprecated. Lookup does
not authorize memory writes or override task exclusions.

## Skill Management

Creating/updating/validating X-IPE skills MUST use `x-ipe-meta-skill-creator`.
Load guidelines/subtype templates and preserve contracts/resources. Edit complete
`x-ipe-docs/skill-meta/{skill-name}/candidate/` packages first, never directly edit
`.github/skills/{skill-name}/`. Validate and independently review meaningful
workflow/executable/safety changes at the exact hash before authorized promotion.
Version history advances only after exact production parity. Candidate readiness
is not publication or larger-task completion. Do not sync AGENTS/CLAUDE/.claude/
codex mirrors without explicit separate authority.
