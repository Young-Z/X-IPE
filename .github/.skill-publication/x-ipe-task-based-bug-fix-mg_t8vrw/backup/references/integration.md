# Bug integration — tool routing is not an app action

## Source and lifecycle

Read the common lifecycle and goal contract. Same current task/readiness, one
owner, original bug description/expected behavior and protected baseline. The
child does not create/update a task, close it, commit, mutate app state or run
a successor. Owner preserves original task_completion_output and dynamic fields;
optional existing legacy require_human_review is retained only when supplied.
Null next_task_based_skill is not authority for speculative routing.

Source precedence: explicit selected source, declared source/board specification
link, unique EPIC/FEATURE ownership, then validated legacy requirements/FEATURE.
Retain anchors while resolving file, validate content/identity/kind/approved-root
containment, reject traversal and symlink escape. Explicit broken or ambiguous
links block instead of falling back. Requirements parts/index must resolve all
affected parts. Missing source/design/dependency is a named gap, not no conflict.

## Actual app association

Current UI ACTION_MAP has no x-ipe-task-based-bug-fix association and the workflow
template has no bug_fix action in any stage. tools.stages.feedback.bug_fix is an
enabled semantic tool routing key, not an app action, status or deliverable tag.
Do not manufacture workflow.action bug_fix, impl-files, bug-report or goal tags,
or write another action such as implementation/change_request as a proxy.

Default free-mode remains supported without app workflow writes. Requested
workflow-mode returns blocked when the exact skill/action/template association is
absent; owner can request authorized free-mode disposition. Do not silently change
the selected mode/name or claim workflow done. Contextual workflow source can be
read without inventing action completion. If a real association is added later,
resolve actual state, mandatory predecessor done, required contexts/output tags
and owner write/readback from current consumers; no assumed future schema.

The actual installed workflow_update_action.py rejects an unknown bug_fix action
in disposable-project tests without mutating state. That rejection is characterized
consumer behavior, not a production app bug fixed by this skill update.

## Enabled semantic implementation tools

Read x-ipe-docs/config/tools.json stages.feedback.bug_fix and its `_extra_instruction`.
Discover enabled matching implementation tools by actual language/framework/domain,
load their SKILL.md and fix operation contracts; do not hardcode file suffix as
program type or force-enable disabled tools. Group cross-stack scenarios and route
sequentially, preserving one same-task context and shared-boundary checks.

Current routing enables Python, TypeScript, HTML5, Java, MCP and general fallback
plus UI testing. Tool input is operation fix, aaa_scenarios list of scenario_text,
source_code_path, test_code_path and optional actual feature_context. Use mini AAA
with source/AC/constraint context and one assertion per Assert clause. Tool returns
operation_output.success, result implementation_files/test_files/test_results/
lint_status/lint_details/stack_identified and errors; preserve actual result fields
and failures. Never invent a routed invocation or coerce it into task output.

Python fix operation explicitly permits absent feature_context and synthetic
BUG-task context; this operation-specific exception governs its generic feature
DoR. Synthetic context stays tool-local, technical_design_link N/A, no feature
allocation, board/workflow ID or fabricated design file. If another tool actually
requires unavailable context, report blocker instead of fabricating it. Read each
selected tool's real fix contract; do not assume all operations share exceptions.

Tool fix owns learn/write-test/behavioral-red/minimal-fix/green/full-regression/lint
in that order. Its red must be the correct behavioral assertion, not setup error.
Record source and unchanged test hashes before/after and each original reproduction
result. Do not independently execute a second fix or redo registration/routing.
Generic tool automated lint cleanup must stay within the approved fix boundary;
unauthorized widening is blocked, never accepted as incidental cleanup.

## Browser and tracing

For UI bugs inspect configured x-ipe-tool-ui-testing-via-chrome-mcp and available
actual browser capabilities. Load that tool contract, use actual equivalent enabled
browser operations, and record which capability executed navigation, interaction,
snapshot/screenshot and console/surrounding regression checks. Browser absence is
unavailable, not executed; snapshots from authored fixtures are not browser evidence.

Disabled optional browser means actual-domain tests plus explicit visual evidence
gap. Enabled/required but unavailable browser blocks the browser completion claim;
never force configuration, fake results or conflate jsdom with rendered visual proof.
Required checks cannot be waived by a tool availability label or passing unit test.

Consult actual tracing_enabled, ignored APIs and existing infrastructure only if
diagnostic relevance warrants it. Current tracing_enabled is false. Disabled or
absent infrastructure requires no forced tracing setup/decorator/installation;
use normal tests, logs or debugger evidence with privacy/redaction as applicable.
Mandatory diagnostic data unavailable means named gap/blocker, not invented trace.

## Evidence and boundaries

Existing bug artifact stores original report, intended source/parent/subgoal/
story/GWT AC/type, qualitative success, constraints/non-goals, all-required branches
or selected alternative, reproduction, root cause/callers, conflicts/authority,
design impact and actual red/green/full-suite/browser/review evidence. No new output
keys, board fields or goals database. Restore behavior, not a new product outcome.

Real source/design/tests/config/review hashes and commands/exits bind claims;
edits invalidate affected evidence, unaffected IDs/history/evidence remain intact.
Unresolved unexpected conflict blocks testing/fix; actual human CR authority is
required for changed acceptance/constraints in every mode. Meaningful independent
review missing blocks pertinent completion/publication, not candidate drafting.

Separate verified engineering delivery from not measured stakeholder outcome;
actual observations need cited stakeholder/context evidence. The test suite's
miniature expiry reproduction is a real executed fixture only, not this repo's
authentication implementation, autonomous tool routing or actual stakeholder gain.
