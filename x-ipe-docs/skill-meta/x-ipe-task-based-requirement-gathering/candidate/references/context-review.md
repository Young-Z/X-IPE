# Requirement context, conflict coverage and application evidence

## Delta-first context

| Path | Minimum domain context | Expand when |
| --- | --- | --- |
| Small compatible | Fresh idea/CR intent, affected scope/acceptance, existing coverage map | Unknown boundary, changed dependency, uncovered part or material risk |
| Standard new | What/who/why, acceptance, in/out scope, domain facts, full conflict coverage | New integration, unfamiliar domain or cross-feature coupling |
| CR intake | Existing feature IDs/FRs/ACs, authorized delta, related dependencies and impact decisions | Contradiction, public contract/security/data change or structural redesign |

These are authoring paths, not permission to skip app actions or automatically
launch another skill. A high-risk change uses broader affected-context analysis,
mitigation and independent review. A small change can still be high risk.
Existing approved research/clarifications are reused; only material gaps justify
new research or bounded questions. Preserve original language/links and facts.

## Complete conflict coverage without repeated full reanalysis

1. Inventory every requirement-details part and index, including unindexed parts;
   reconcile indexed targets with files. Missing indexed part, duplicate/ambiguous
   active file or context mismatch blocks the coverage claim until resolved.
2. Preserve both legacy FEATURE-{nnn} and EPIC-{nnn}/FEATURE-{nnn}-{X} contexts.
   Do not infer feature identity from the newest filename alone.
3. A reusable review must cover all existing parts, with per-part SHA256 hashes,
   scope/feature/FR/dependency summaries, actual decisions, source request/idea
   revision and the compared delta. A bare timestamp or "reviewed" flag is invalid.
4. Reuse unchanged summaries; compare the current delta against ALL summarized
   scopes. Read changed/new parts and affected feature/dependency sections. If
   source intent changed, compare the new delta and invalidate affected decisions.
5. Removed parts/index targets, newly introduced dependencies, config changes or
   incomplete summaries invalidate relevant coverage. Expand to a full semantic
   baseline only when safe affected scope cannot be bounded or no baseline exists.
   Hashing bytes/inventory is not a repeated semantic analysis of every document.
6. Record exactly which coverage was reused/refreshed, current inventory/hash
   map, inspected sections, delta, conflict table and decisions. Zero conflicts
   is a reviewed conclusion, not a reason to omit coverage. An empty first-project
   inventory is valid and is recorded explicitly.

Suggested embedded evidence (not a new app/board schema):

```yaml
requirement_review:
  sources: [{path: "{idea or request evidence}", sha256: "{content hash}"}]
  parts: [{path: "{part}", sha256: "{hash}", scopes: [], dependencies: []}]
  index_sha256: "{hash or absent}"
  config_sha256: "{workflow/tools revision where relevant}"
  delta: "{what changed and what did not}"
  reused_sections: []
  refreshed_sections: []
  invalidation_reasons: []
  conflicts: [{feature_id: "{FEATURE ID}", affected_frs: [], decision: "CR | new", rationale: "{why}"}]
  unresolved_material_questions: []
  checks: [{command: "{actual check}", exit: 0, result: "{observed only}"}]
```

## Impacts and bounded questions

- Read the [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md).
   New/changed requirement coverage uses source/parent IDs and outcome/evidence
   gaps in the existing requirement section. Legacy goals may be inferred only
   from explicit story so-that intent with source; ambiguity blocks that claim.
   CR delta invalidates affected goal/AC evidence, not all historical findings.
- Choose CR versus new work using responsibility/cohesion/independence/coupling,
  with paths, affected FRs/ACs, alternatives and rationale for each conflict.
- Questions, including an unresolved scope confirmation, use the common lifecycle
  policy and at most 3-5 per batch. Already approved input is not a new decision.
- Do not silently assume material behavior; document nonblocking design assumptions
  separately. If required human authority or a response is unavailable, return
  blocked with partial artifacts. DAO guidance is not human release approval.
- Append CR markers idempotently by task/ref + affected feature, then edit only
  authorized conflict sections. A useful marker contains date, change, FRs/ACs,
  follow-up, new Epic and actual root-relative document link.
- Major conflict retains history under `[RETIRED by EPIC-{nnn}]`, with reason,
  date and linked replacement; minor conflict updates inline. Independent work
  receives Related Features dependency notes instead of a false impact marker.

## Workflow consumer compatibility and actual completion

Read authoritative [ACTION_MAP](src/x_ipe/static/js/features/workflow-stage.js),
[workflow template](x-ipe-docs/config/workflow-template.json) and
[prompt consumers](x-ipe-docs/config/copilot-prompt.json). Requirement gathering
is shared, mandatory and uses `requirement_gathering`. Refined idea is required;
mockup context is optional. EN/ZH prompts consume the same tags without translation.
Feature Breakdown and Feature Refinement consume the actual `requirement-doc`.

Read [tools config](x-ipe-docs/config/tools.json): `stages.requirement.gathering`
is the tool configuration location, NOT the app action name. Current metadata-only
section does not enable a web implementation tool; missing/disabled/undeclared
tools do not become enabled by guessing or copying another stage's settings.
Unavailable optional research is reported; a blocking knowledge gap remains blocked.

Before completion validate populated file, scalar directory, approved root and
matching requirement/idea context. Read installed workflow state and check required
prerequisites are truly done with valid artifacts; `skipped` is not completion
evidence even though the current helper permits it for stage unlocking.
The child performs the write once unless the agreed lifecycle owner already did:

```text
{python} .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/workflow_update_action.py --workflow {name} --action requirement_gathering --status done --deliverables '{"requirement-doc":"x-ipe-docs/requirements/{active-file}","requirements-folder":"x-ipe-docs/requirements"}' --format json
{python} .github/skills/x-ipe-tool-x-ipe-app-interactor/scripts/workflow_get_state.py --workflow {name} --format json
```

Run from the approved project root with the configured interpreter. Verify update
exit 0 and readback at `shared.requirement.actions.requirement_gathering`, status
`done`, exact keyed deliverables, files and required context. Only then return
`workflow_action_updated: true`. Do not replay a successful write on resume merely
to make a receipt; verify recorded current state and revision instead.

The installed writer does not reject all missing tags/files or enforce every
semantic prerequisite. Its exit alone does not prove this domain's DoD. Do not
use it to mark skipped/done prerequisites or fabricate missing output. Free-mode
performs no app write and returns false. If write succeeded but verification
failed, retain partial state and blocked output; report the actual result rather
than silently rollback or falsely claim success.

## Evidence limits

Contract tests prove text/schema/resource compatibility; temporary helper tests
prove installed CLI write/readback and negative inputs. Neither simulates an
agent's questions, conflict judgment, research, authoring, split or routing.
Independent review and representative domain pilots must be reported separately;
candidate readiness is not promotion or end-to-end workflow certification.
