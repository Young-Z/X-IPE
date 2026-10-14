# CR source, workflow and evidence boundaries

## Source lookup (read before domain work)

Use the common lifecycle resolver, preserving specification and closing-report
context names. Explicit selected path first, then declared artifact / feature
board specification_link, then unique owning EPIC/FEATURE or legacy
requirements/FEATURE lookup. Strip supported Markdown anchors for file lookup,
but retain the source anchor in CR evidence. Check file/directory kind, feature
identity, approved-root containment and symlink escape. An explicit broken link
blocks; do not silently fall back, choose newest, or translate old paths blindly.
Multiple matches block. Legacy requirement parts/index must resolve linked parts;
read all affected parts rather than assume the default summary is authoritative.
Current board is planning/features/features.json; historical markdown is not CRUD.

Missing design/code/pending CR sources are documented unavailable or justified
not applicable, never zero conflicts. Required specification/content ambiguity
blocks the pertinent classification/completion claim. Outcome ambiguity alone
does not erase unrelated established delivery evidence.

## Actual feedback action and tool configuration

ACTION_MAP associates x-ipe-task-based-change-request with change_request.
Current workflow-template feedback stage is per_feature; this action is optional.
Its specification context is required; closing-report is optional. No closing
report production/extraction is required, and no eval-report alias is invented.
Explicit optional selections must still validate; absence is not a defect.
stages.feedback.change_request in tools.json is an empty routing configuration:
domain document analysis is valid; do not force-enable web search or implementation
tools. If configured later, discover enabled semantic capabilities, respect their
declared operations and consultation boundaries. Research when a consequential
standard/compliance uncertainty warrants it; unavailable evidence is a gap.

The single lifecycle owner reads named workflow state through the installed
workflow_get_state.py, matches features[].feature_id.feedback.actions.change_request,
checks required context and all mandatory predecessor actions are actually done.
Skipped/failed/in_progress is not done. A helper's already-open stage cannot waive
application prerequisites, document authority, domain checks or human approval.
No child app writes and no automatic reopening/unlocking of other actions.

After approved delta documents and domain verification, owner calls installed
workflow_update_action.py with --workflow NAME --action change_request --status done
--feature-id ACTUAL-ID --deliverables JSON --format json. The exact keyed JSON is:

```yaml
deliverables:
  cr-doc: "actual owning feature CR document file"
  cr-folder: "actual owning feature directory, scalar string"
```

Both tags must be nonempty real correct-feature paths; no goal-delta tag,
closing-report output or invented folder. Writer success alone is insufficient:
the installed writer tolerates missing tags, nonexistent files and missing source
context; the owner independently validates these before write and on readback.
Folder arrays, unknown tags, wrong feature and locked predecessors are rejected
by real helper tests. Verify exact done/status, keyed deliverables and unchanged
contexts; read-only resume verifies existing evidence without replaying writes.
Free-mode never writes app workflow state.

## New-feature intake without circular execution

If a related owning feature exists, co-locate CR there even when new_feature is
chosen; update its impacted specification and history without relabeling that
feature as the new one. new_feature_ids stays [] until independently authorized
breakdown actually allocates IDs. Never fabricate an ID, status or folder.

If no related feature exists in free-mode, approve a requirements intake CR path
under an existing requirements folder; link the requirement source and explicitly
record specification update as not applicable until breakdown/refinement creates
the new feature. This is not an unconditional claim that both specifications
were updated. Return existing output keys with feature_id N/A and actual links.
In workflow-mode, no related feature means the required per-feature specification
and feature identity cannot be satisfied: return blocked with the intake artifact,
not done, and let the owner request an authorized free-mode/breakdown disposition.
Do not recursively run breakdown to create a folder in order to finish this CR.

## Revision and authority

Record relevant requirement/index/parts, board read, specification, design, code,
tests, pending CR, mockup, configuration and approval SHA256 revisions in the CR.
Read actual artifact clauses and callers/dependencies; assertions in an authored
example are not verified feature behavior. Dependency omission is an evidence gap.
Approval names approver/source, bounded decision, revision, changed sections and
allowed writes; guidance is not human approval. A changed proposal invalidates
affected approval/checks, not a reason to repeat identical confirmations.

Before implementation, approved deltas update affected requirement/specification/
design context, GWT AC/type mappings and histories. Invalidate affected design,
test, review and outcome evidence; retain unaffected IDs and evidence bytes.
Keep delivery and outcome separate: CR preparation is verified document delivery
only when actually checked; stakeholder outcome remains not measured unless an
actual cited observation supports it. Approval, DAO, fixture and plan are not
observations. Meaningful workflow/safety/public-contract changes need independent
review; unavailable required review blocks promotion, not candidate drafting.
