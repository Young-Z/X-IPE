# Acceptance testing — integration and evidence boundaries

## Actual consumers, not guessed names

ACTION_MAP associates this skill with per-feature app action `acceptance_testing`
under validation. Toolbox key is `stages.validation.acceptance_test`, not the app
action or implementation enablement. Current template requires specification and
impl-files contexts; exact completion tags are test-report and test-folder.
Test-report is actual report file, test-folder one real scalar browsing directory.
Folder need not enumerate all tests/evidence. Original output has one report link,
both conditional successors, original result fields and repaired interaction_mode;
do not add goal/evidence fields to app/board/task output.

Selected impl-files resolves actual implementation_files, never technical_design_link.
Normalize legacy scalar file to nonempty file array; verify actual package/source/
test files, content and scope. Do not substitute src/ or tests/ directory task links,
design or invented code paths. Required contexts cannot be waived by N/A.
Design resolves from actual design output/declared link/unique owning folder, not
an unsupported board field. Explicit broken/wrong-feature sources block; absent/
auto inputs may use unique owning EPIC/FEATURE or legacy folder. Same precedence
in free-mode; standalone uses explicitly approved source/design/acceptance scope.
Validate canonical containment, file kind, content/identity and no symlink/traversal.

## Testing enablement and test-only operations

Only literal true permits the corresponding executable testing capability. False,
absent and nonboolean entries remain disabled; missing/empty/metadata-only config
cannot opt in. No force-enable general and no fallback to code_implementation
config. Missing/unparseable config is explicit blocker for affected executable
groups. Structured reading is still possible without browser/external tooling;
executable helper/validator scenarios use an applicable enabled test capability.
_extra_instruction supplements context, cannot override original assertions,
source scope, permissions or gates. Semantic match actual enabled declarations,
runtime and responsibilities; do not infer eligibility from a suffix.

Installed implementation tool skills expose implement/fix/refactor, not test.
Do not invent a test operation or call implement during acceptance and permit
production code changes. Agree an explicit same-task test-generation/execution-only
adapter for supported tooling, or use an authorized existing runner within an
enabled matching capability. Preserve source bytes and original assertions. If
the operation cannot be restricted, block that group rather than execute ad hoc.
TDD RED/GREEN/baseline remains implementation responsibility; acceptance neither
waives it nor forces existing passing behavior red. Failure proposes bounded
fix/CR work through owner, never edits code or routes another task itself.

Frontend UI needs configured enabled Chrome DevTools MCP and actual isolated/
dedicated browser profile; enabled UI skill delegates execute_ui_tests only when
available, otherwise enabled direct MCP. Generic browser/Playwright availability
does not itself satisfy chrome-devtools-mcp authorization. Navigate, trigger
actual path, inspect console/load/runtime errors and every original assertion.
Source/jsdom/keyword assertions are not browser evidence. If no authorized browser
can run, mark UI Blocked while independent backend/CLI/library/review checks proceed.
No universal URL/browser/manual test-data collection requirement for non-UI scopes.

## Explicit revision-bound reuse

Keep goal/AC/evidence tables and one acceptance_evidence YAML block inside the
existing acceptance report; this is document-local evidence, not a new task output
or board schema. Every original assertion has current type-appropriate evidence.
Record feature/scope identity, precise test/review, actual expected/actual result,
environment/config boundary and hashed artifacts. Claim-specific dependencies
include source intent/parent, specification, code/package files, test configuration
and tests, plus applicable both design parts/interfaces/mockup/environment and
captured logs/screenshots/review evidence. Missing roles or relevant files cannot
be omitted simply because a reported pass came from a smaller manifest.

The read-only [consistency helper](.github/skills/x-ipe-task-based-feature-acceptance-test/scripts/verify_evidence.py)
checks explicit expected inputs against report hashes and expected AC/type/assertion
coverage. It has CLI --project-root, --report, --expected; expected is a real JSON
file containing feature_id, inputs role-to-path-array and acs ID-to-types/assertions.
Required nonempty roles: source, specification, code, config, test, evidence.
Extra relevant roles (design, mockup, environment, interface) are allowed when
independently selected. Paths must be project-root-relative regular nonsymlink
files. Expected ACs and all original assertions/types come from current approved
source/spec and inspected plan, NOT copied from the report's claimed coverage.
All five types use this same document-local case schema. Each expected AC/type
pair must cover its full original assertion list; multiple cases of that SAME
type may jointly cover it, but another type cannot supply missing clauses.
For different type-specific clauses, independently partition the explicit reuse
expectations by type, preserve original AC IDs and prove complete merged report
coverage. Do not invent new ACs or alter the task output schema to fit the helper.
Semantic selection/review remains mandatory; the helper cannot discover omitted
relevant files, authenticate logs, verify current live environment from text, or
prove assertions actually executed. reusable true means hash/coverage consistency
only, never acceptance or stakeholder success. Self-reported Pass without actual
artifacts/type evidence remains unsupported even if hashes match.

Helper CLI exit 0 = reusable consistency, 1 = non-reusable/error; JSON output has
reusable/errors/limits. It writes no files, workflows, boards, memory or Git.
API verify(project_root, report, expected) supports temporary scenario checks.
Fresh report parsing requires exactly one acceptance_evidence block; duplicate
inputs/TCs, unexpected/missing files, wrong feature/AC/type, weakened assertions,
missing command/result/environment/artifact evidence, failed/partial/blocked/
not-run cases and stale/unsafe paths reject reuse. Report schema is not an
execution engine or an autonomous agent evaluation. Structured check artifacts
may be actual review records; fixtures clearly disclose not stakeholder observation.

Rehash again before handoff and recheck live environment/tool/config. Authorized
intent/parent/means deltas invalidate affected evidence/review/outcome/dependent
claims; preserve unaffected IDs/bytes/history and independent evidence only with
dependency rationale. For partial reuse, partition expected source/AC/input scope
explicitly and prove full report all-AC coverage after merging; never shrink the
feature's acceptance to satisfy the helper. Timestamp and pass count are insufficient.
Delivery may be verified while outcome is not measured; qualitative source-derived
scenario is enough, no invented latency, match_score, percentage gain or observation.

## App completion, owner and conditional routing

One owner receives the domain output and performs/verifies at most one installed
workflow_update_action.py --workflow actual-name --action acceptance_testing
--feature-id actual-id --status done --deliverables keyed-JSON --format json.
Verify matching prior implementation and preceding mandatory actions done (not
skipped), actual specification/impl-files contexts, all current acceptance checks/
required review, both real tags and workflow_get_state.py readback. The
writer success alone is insufficient: installed writer may allow pending prerequisites when stage
is already open, empty context, missing outputs/nonexistent paths or authored
unexecuted report. Tests characterize permissiveness, not application enforcement
of semantic acceptance. A genuinely locked stage with pending implementation rejects
without changing state. Extra tags/folder arrays/wrong feature fail without writes.

workflow_action_updated is true only for actual/prior verified done write; false
for free-mode/unverified. Read-only resume verifies hashes/state/artifacts, no
replayed done writes. New Implemented acceptance can transition to Tested via
owner/category only; advanced authorized Completed remains Completed. No child
create/close/feature/task/Git/next execution, no duplicate routing. Actual mode:
human asks human within skill; full DAO and hybrid use bounded guidance. Owner
requires human completion/route confirmation for human and hybrid; full DAO
selects only authorized successors. Explicit human approval/release binds in every mode.

Refactor recommendation is conditional on an evidenced quality/preservation need
or explicit request. Both default templates make code_refactor optional; acceptance
suggests feature_closing first and code_refactor second. No need means closing
directly without a new report, code churn or agent-authored skip/done record.
The service initializes optional actions as skipped; that is not evidence that
refactoring ran. Project-customized mandatory actions still bind and must be
resolved honestly. Current acceptance, specification and actual implementation
evidence remain required for closing. Reuse unchanged checks through closing.
