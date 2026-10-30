# Code implementation integration contract

## Exact live consumers

ACTION_MAP maps this skill to app action `implementation`, mandatory per-feature
under `implement`. Tools use `stages.implement.code_implementation`, never
the app-action key or informational technical_design config.
Read actual workflow template and declarations; no guessed action/stack registry.
Required selected contexts are `specification` and `tech-design`. Completion tags
are exactly `impl-files` and `impl-folder`; no new goal/evidence/action fields.

## Enabled semantic matching

Discover implementation tool descriptions, When to Use, Operations and actual
type/stack/responsibility. Metadata `_order`, `_extra_instruction` and other
underscore keys do not activate opt-in. Missing/empty/metadata-only means all
discovered tools eligible. If explicit tool booleans exist, only true is enabled;
false and undeclared are disabled with diagnostics. No force-enable general,
even when no specialized tool matches. Malformed nonboolean values
are unresolved configuration, never truthy enablement.

Match enabled declarations semantically (e.g. Python/Flask, vanilla HTML/CSS/JS,
TypeScript/React, Java/Spring), not filename suffixes or a fixed registry. General
is no-specific-match safety net, not mandatory extra work; insufficient fallback
blocks affected scope. `_extra_instruction` is supplementary context, not authority
to bypass tests/config/approval. Use the shared
[capability routing](.github/skills/x-ipe-workflow-task-execution/references/capability-routing.md)
resolver and refresh changed config/catalog revisions. Dependent work/shared
writes run sequentially, backend before dependent frontend; independent read/test
calls may be batched with isolated data/environment/cleanup. Skill-creator and mcp-builder precede normal scenario/routing
and have their own domain checks; separate ordinary code still obeys this config.

## Sources and paths

Selected contexts first in either mode, declared/previous output or supported
board specification_link next, unique owning EPIC/FEATURE or legacy FEATURE folder
last for absent/N/A/auto-detect. The board has no technical_design_link field;
design links are task outputs/action deliverables. Broken explicit sources block
rather than fall back. Verify source content, feature/workflow identity, hashes,
file/directory kind, canonical containment and no traversal/symlink escape.
Current mockups require content/scope analysis, not date comparison. Preserve
singular mockup_link and original program_type/tech_stack inputs; collect all
scoped mockups through current design/specification without output schema change.

## File-array versus directory adaptation

Original task_output_links are directory-oriented: src/ and tests/ are directories
and examples, not mandatory physical layout or workflow file values. Adapt to
actual source/test or delegated candidate directories without new output keys.
The owner collects actual owned implementation/test/delegation files separately
from tool outputs/revision evidence. `impl-files` is a nonempty file array even
for one file; `impl-folder` is one scalar directory for browsing, never an array.
Files may be outside the browsing directory (source and test files often span
different roots); every file must still be real, safe and scoped. Do not force a
common ancestor or claim the folder enumerates every file. Do not relabel a design
file or directory as implementation. For skill-only work use real scoped package
artifacts; candidate-only delegation cannot falsely claim published implementation.

Installed writer accepts nonempty string file values for legacy callers and file
arrays, marking schema_version 4.0 when arrays appear, without downgrading newer
versions. It rejects extra tags, arrays for folder tags, and blank/nonstring array
elements. It can accept missing tags, empty arrays, nonexistent paths, directories
as file strings, pending design and absent context: writer success alone is insufficient.
These helper gaps are characterized in temporary projects; source helpers are not
changed or claimed to enforce domain completion. The owner separately rejects
those semantic defects before and after any write.

## Same-owner lifecycle and completion

One current task/readiness/owner, no child registration/status/Git/next execution.
Unmigrated delegates need a bounded explicit ownership adapter before invocation;
unresolved duplicate lifecycle conflict blocks. Human asks human within
skill; full DAO and hybrid use actual message_context/instruction_units/execution_plan.
Guidance is not intent confirmation or release permission. The owner re-reads
mode at completion: human and hybrid require human completion/route confirmation;
full DAO selects only authorized successors. Explicit domain human approval
still binds in every mode. Acceptance is a suggestion,
not permission to register/invoke another task.

New implementation requires actual Designed feature. Advanced authorized
CR/resume retains Implemented/Tested/Completed and immutable identity/dependencies;
Retired or missing design evidence blocks. Owner sets Implemented only for an
authorized new Designed transition; no advanced status regression or no-op replay.

Workflow-mode owner verifies matching technical_design action `done`, its real
tech-design and feature-docs-folder, preceding applicable mandatory actions `done`
(not skipped), and required implementation specification/tech-design contexts.
Perform at most one installed workflow_update_action.py call with `--workflow`,
`--action implementation`, `--feature-id`, `--status done`, `--deliverables` keyed
JSON and `--format json`. Verify success plus workflow_get_state.py readback of
matching features[].implement.actions.implementation done, both exact tags and
all real artifacts/contexts. Prior fresh verified write means read-only resume,
not replay. workflow_action_updated is true only for verified actual/prior write;
false for free-mode or unavailable verification. Free-mode mutates no app workflow.

Owner verifies required feature/task/category persistence after domain evidence.
Do not auto-complete or skip prerequisites to unlock a stage. Legacy acceptance
initialization maps impl-files to technical_design_link incorrectly; hand off a
bounded explicit real implementation-file mapping or block that downstream claim.
No downstream consumer rewrite or blanket compatibility claim in this candidate.