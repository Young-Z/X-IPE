# Technical-design integration contract

## Actual consumers, not invented schemas

- ACTION_MAP maps this skill to `technical_design`; actual workflow template is
  `implement`, `per_feature`, mandatory, with required `specification` context.
- Extract tags are exactly `tech-design` (file) and `feature-docs-folder` (scalar
  directory). Do not add goal/coverage tags or use tool key `code_implementation`.
- Actual feature statuses are Planned, Refined, Designed, Implemented, Tested,
  Completed, Retired. New design reads Refined, completion hands off Designed.
  Authorized advanced CR/resume preserves status/identity/Epic/created_at/deps;
  never reset status merely to pass a gate. Retired is not a design-ready feature.
- Existing feature schema does NOT support `technical_design_link`; it rejects
  that unknown field. Keep design links in existing task_output_links and action
  deliverables; owner updates actual status/approved version only when changed.

## Source resolution and safe paths

Use selected workflow.extra_context_reference.specification first, then feature
specification_link, then unique owning EPIC/FEATURE or legacy requirements/FEATURE
folder for absent/N/A/auto-detect. Broken explicit path blocks, not fallback.
Check kind/existence/feature identity, content and canonical approved-root
containment; reject traversal/symlink escape and ambiguous matches. Workflow
required context is not waived by N/A. Strip supported anchors for lookup;
keep project-root-relative links in generated Markdown. Mockups require actual
content analysis for frontend/fullstack, not existence or newer timestamps alone.

## Consultation config and real matching

Read actual `stages.implement.technical_design` in tools.json. Ignore `_order`
and other metadata keys for activation; preserve `_extra_instruction` for
consultation. Missing/empty/metadata-only means all discovered implementation
tools eligible. Explicit tool booleans mean opt-in; no force-enable general.
Malformed values are a configuration question, not truthy enablement.
Use [capability routing](.github/skills/x-ipe-workflow-task-execution/references/capability-routing.md)
for read-only resolution and config/catalog revision checks.

Match descriptions/When to Use to actual type/stack/responsibility: Python/Flask
practices from Python, vanilla HTML/CSS/JS from HTML5, TypeScript/React from
TypeScript, Java/Spring from Java, FastMCP/MCP SDK protocol from MCP. These are
examples from installed declarations, not a hardcoded routing registry. MCP
may also need runtime-specific consultation. General is eligible fallback only
when enabled and suitable. No enabled match is a disclosed capability gap.
Record matched/excluded rationale; never run
Operations or implement/fix/refactor. Availability does not change Part 2 format.

## Same-owner completion handoff

The child returns artifacts/evidence to its current lifecycle caller. No child
task registration/closure, recursive workflow, successor execution, commit or
Git routing. Human questions are human; full DAO and hybrid use current common
message_context/instruction_units/execution_plan contract. At completion the
owner re-reads policy: human and hybrid require human completion/route confirmation;
full DAO selects only authorized successors. Explicit domain human approval
cannot be replaced by DAO. Clear inputs do not create ceremonial questions.

For workflow-mode the same owner first verifies required specification context,
matching feature_refinement action `done` and real specification artifact, plus
other applicable lifecycle prerequisites. Never skip/complete prerequisites to
unlock design. Owner performs at most one required update using installed
workflow_update_action.py with `--workflow`, `--action technical_design`,
`--feature-id`, `--status done`, `--deliverables` keyed JSON and `--format json`.
Values are the actual design file and owning directory. Verify exit success and
workflow_get_state.py readback: matching features[].implement.actions.technical_design
must be done with both exact tags and real matching artifacts/context. Prior
verified done is read-only resume, not replay. Free-mode has no app write.

Installed writer permissiveness is not domain completion: it accepts missing
tags and does not prove file existence, source identity, AC coverage or prior
refinement done. `writer success alone is insufficient`; missing evidence blocks
the completion claim. workflow_action_updated true requires a verified actual
or prior write; otherwise false. Return original output fields, no new schemas.

Owner hands new Refined feature to Designed, retaining design links in outputs;
authorized advanced CR/resume retains advanced status unless separately approved.
Required owner updates/readback precede final task completion. Candidate-only
skill maintenance runs no real workflow/feature/board writes. Tests use temporary
projects and characterize helpers, not autonomous design reasoning or outcomes.