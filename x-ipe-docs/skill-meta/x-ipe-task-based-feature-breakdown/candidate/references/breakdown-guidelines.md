# Feature breakdown domain guidelines

## Context reuse and delta

Reuse Requirement Gathering's source/parts/index SHA256 coverage, scope decisions,
conflict resolutions, acceptance, risks, language and mockup findings. Compare
current inventory and revisions, including board/workflow changes and impacted
legacy/new feature edges. Refresh only changed/affected facts; missing coverage
requires establishing a baseline. A timestamp or prior completed flag is not
fresh semantic evidence. Scope/priority uncertainty is a real question, not a
mandatory repeated interview. Human asks the human; full DAO and hybrid use the
common representative contract with bounded authority. Human and hybrid require
human completion/route confirmation. Explicit human approval binds in every mode.
No child routing.

| Path | Required work | What stays stable |
| --- | --- | --- |
| Single clear feature | One runnable unit, ACs, direct dependencies, actual registration and artifacts | No artificial split or repeated research |
| Standard new | Domain clusters, grouping rationale, coverage, MVP and enhancements | Approved requirement findings |
| Incremental CR | Affected rows/FRs/ACs/dependencies and supported integration changes only | Existing IDs, Epic, status, specs and unrelated documents |

## Epic grouping decision matrix

Assess feature count, domain diversity, dependency clusters and team boundaries
before assigning new features. Reuse the intake Epic for a single grouping.
Additional Epic allocation is a scoped grouping decision, not mandatory at every
task. Allocate highest reserved Epic number + 1 across folders/headers/board;
recheck collisions and never overwrite another grouping or renumber history.

| Scope signals | Recommendation | Rationale |
| --- | --- | --- |
| 1 domain, <=7 features | Single Epic | Cohesive responsibility and manageable delivery |
| 2-3 domains, 8-15 features | 2-3 Epics | Separate natural responsibilities/dependency clusters |
| 4+ domains or >15 features | Multiple Epics | Keep each grouping coherent and <=7 features |
| Borderline, e.g. 2 domains/7 features | Document cohesion/coupling/team trade-off | No blind count-based regrouping |

Use 5-7 as the maximum planning range, never a minimum requiring padding.
Do not truncate a large requirement to seven features: record all covered or
explicitly deferred scope, regroup when necessary. New allocated Epics link back
to the intake. Existing CR features retain original Epic membership.

## Sizing and separation

Apply the [goal contract](.github/skills/x-ipe-workflow-task-execution/references/goal-contract.md).
Each new/changed feature deliverable contributes a subgoal with stable parent
requirement/source, stakeholder, outcome scenario, constraints and GWT AC links.
Internal enabling work needs a credible contribution chain. Legacy explicit
story so-that goals remain inferred/source-labeled; ambiguity blocks the relevant
claim, not rewrites of history. No fixed minimum or three-goal cap.

| AC count per proposed feature | Action |
| --- | --- |
| Under 10 | Likely one feature, if one coherent deliverable |
| 10-20 | Evaluate distinct capabilities, outcome contributions and testable value |
| More than 20 | MUST split along natural boundaries |

Assess 3+ technical layers, 5+ estimated files, distinct user capabilities,
AC groups and foundation/consumer depth as signals, not automatic split mandates.
Single Responsibility, Independence, Deliverable Value and Reasonable Size apply.
Aim for 3-7 concise ACs without inventing criteria or discarding required cases.
Descriptions <=50 words; technical/security/performance hints belong in details.

Natural boundaries: runnable foundation + consumers, processing stages with useful
outcomes, variants, or read vs write capabilities. Do not split into buttons,
validation messages or bare controller layers. First new feature per Epic is
Minimum Runnable Feature (MVP): a testable vertical minimum user/core outcome.
A bare interface with no runnable use is not an MVP. Enhancements add separable
value; necessary error/security paths remain in the MVP. CR does not replace a
stable existing MVP. Existing shared prerequisites may be cross-Epic/legacy.

## IDs, versions, names and folders

- New EPIC-{nnn} and FEATURE-{nnn}-{X}: zero-padded Epic number matches exactly;
  uppercase suffix A, B, C... within that Epic. EPIC IDs never fill Feature ID rows.
- Inventory documents, folders, board (all pages/statuses) and retired/history
  reservations before assigning. Continue after the highest reserved suffix;
  do not reuse retired/deleted IDs or fill historic gaps. Recheck at write time.
- Preserve legacy FEATURE-{nnn} identifiers and existing legacy FEATURE folders.
  New features reside at x-ipe-docs/requirements/EPIC-{nnn}/FEATURE-{nnn}-{X}/.
  Do not silently migrate legacy folders, immutable board epic_id or stable IDs.
- New version v1.0; approved additive delta v1.1/v1.2, redesign v2.0. Do not bump
  every feature during CR or reset advanced statuses to Planned.
- Names are specific, action-oriented and scoped: Cart Management rather than
  Button, User Stuff or Everything. Grouping containers are not feature units.

## Dependency rules and priority

Distinguish all-required subgoals/prerequisites from alternative means. Select and
bound a means with rationale; do not instantiate a feature for every option or
split one feature per technical layer. Board dependencies encode actual selected
prerequisites only; alternatives stay in existing details. An enabling subgoal
may be indirect but must explain how it supports its parent's scenario.

Use only direct Feature-ID dependencies with reasons. Sequential, parallel shared
foundation and multiple-predecessor patterns are valid; cross-Epic and legacy IDs
remain unchanged. Validate all references, no self edge, no circular dependencies,
and the DAG over changed plus existing impacted edges. Foundations first;
provide topological delivery order, not an invented edge for workflow sequencing.
Retired targets require an approved replacement mapping, never dangling links.
P0 = runnable MVP/core blockers; P1 = launch; P2 = convenience; P3 = future.
Document user/business value, risk and dependencies; priorities are document
fields, not unsupported feature-board JSON fields.

## Document, mockup and part rules

Feature List and all scoped detail sections live in the selected owning
requirement-details file/part, never only in index. Explicit valid affected-part
selection precedes highest numeric active-part fallback; reconcile index/all parts
and inspect older impacted features. CR does not regenerate or re-split stable
parts. Free-mode direct request must become real populated requirement artifacts.
Keep original REQ ID if supplied; Epic-only input does not invent a REQ identity.

Each detail includes title/version, <=50-word description, ACs with coverage,
direct dependencies/reasons, technical considerations and applicable mockups.
Consolidation is required; individual feature.md/specification files are not
breakdown deliverables. Retained specification template is downstream-only.
Index contains Parts Overview with actual file links, coverage and line counts;
Feature List stays in parts. Requested EN/ZH prose is preserved, not IDs or tags.

Mockup list uses mockup_name/mockup_link (not mockup_list inside each entry).
Prefer explicit/upstream links, then selected Epic/mockups, then linked idea only.
Keep shared Epic mockups and preserve extensions; verify URLs/content where
required; copy only authorized missing local files. N/A means no false mockup
claim. All generated links are project-root-relative, never ../mockups/ or ./.
Do not overwrite foreign bytes or unnecessarily create per-feature mockup copies.

## Parent split coverage and history

For an actual split compare every parent FR/AC against the union of child FR/ACs
with a coverage table and recorded rationale. Preserve stable identifiers and
inbound references; unrelated features are not split as a CR side effect.
Partial coverage: retain parent active with uncovered IDs in dedup_gaps; material
missing coverage blocks a completed split claim until resolved. Full coverage:
only with explicit approved retirement may the parent leave the active list,
retain historical text/redirects, and board status become Retired through actual
feature_update.py. No feature_archive or delete operation exists. Report
parent_features_removed as removal from active breakdown, not erasure of history,
only after both document and board changes are verified. No auto deletion.

See [actual integration](.github/skills/x-ipe-task-based-feature-breakdown/references/integration.md)
for schema, resume, append-only limitations and current helper evidence boundaries.
