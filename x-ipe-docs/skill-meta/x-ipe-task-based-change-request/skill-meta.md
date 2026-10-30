# Task-Based Skill Metadata — Change Request

TASK-6749 CR slice: inherited candidate independently reviewed, validated and
exactly promoted with current user authority. No board/memory/Git/app/config/other
source writes. Original
metadata below is retained verbatim as historical context, not current readiness.
Version 2.0.0 follows verified six-file byte parity; original history is retained.

Loaded installed creator, general guidelines, both task subtype templates,
shared lifecycle and goal contract; inspected all five old resources and existing
candidate differences, authoritative specification scaffold and actual consumers.
Prework candidate entry/examples were distinct; preserve their single-owner intent
while correcting old aliases, independent routing and preapproval mutation order.
All five original resource paths retained and updated; integration reference added;
no resource deletion. Initial worker had no trusted managed publication manifest.
Current reviewer verified clean tracked HEAD inventory equals original baseline;
baseline alone was not used to assert ownership. Current user authorized promotion.
No verified finite lesson selected; historical lessons and memory unchanged.

Prior worker six-suite run: 536 passed / same four prework stale closing/lifecycle
assertions failed in 32.23s; all 37 new dedicated CR tests passed, zero skips or
deselections. Current six-file receipt exactly recomputed; zero errors/warnings,
241 body lines. Worker's 2866 protected-file check preceded authorized promotion;
the six-file CR live inventory now matches the candidate, not the old baseline.
Sequential main review of inherited worker package passed; fresh focused run 37
passed. Installed publisher dry-run verified tracked-HEAD ownership, exact original
baseline and five replacements/one addition/no deletion. Exact edit promotion is
not transactional publication; see publication receipt for method/recovery limits.
No larger-task completion claimed. Earlier candidate-only statements below are
historical, superseded by this authorized review/promotion record.

```yaml
skill_name: x-ipe-task-based-change-request
skill_type: x-ipe-task-based
version: "2.0.0"
planned_version: "2.0.0"
status: production
created: 2026-02-15
updated: 2026-10-13
task_id: TASK-6749
publication_state: published
independent_review: passed_inherited_candidate_review
candidate_hash: 7e7604fbaa558da5e881ad82e1efc49bef4a27a832afc2480fa263e1423eb5c2
summary: Critically evaluate the complete affected goal/subgoal pipeline and actual conflict evidence, classify modification versus new_feature, and apply only approved document deltas before implementation under one lifecycle owner.
triggers: [change request, CR, modify feature, update requirement]
not_for:
  - "x-ipe-task-based-bug-fix: restore broken documented behavior"
  - "x-ipe-task-based-feature-refinement: detailed specification after approved classification"
  - "x-ipe-task-based-evaluate-change-request-efforts: vendor estimation reports, not this CR domain"
workflow:
  category: standalone
  phase: null
  next_task_based_skill:
    - {skill: x-ipe-task-based-feature-refinement, condition: When CR modifies an existing feature}
    - {skill: x-ipe-task-based-feature-breakdown, condition: When CR requires a new feature}
  human_review: true
inputs:
  required:
    - {name: task_id, type: string, description: same supplied lifecycle task/readiness}
    - {name: task_based_skill, type: string, description: exact canonical discovered name}
    - name: process_preference.interaction_mode
      type: string
      default: interact-with-human
      description: exact caller policy and source; not legacy boolean
      validation: interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill
    - {name: change_request_description, type: string, description: source change intent and affected scope}
    - {name: business_justification, type: string, description: source rationale and observable stakeholder need}
    - {name: requirement_details_path, type: string, default: x-ipe-docs/requirements/requirement-details.md, description: selected source or validated parts/index; no blind default}
    - {name: features_path, type: string, default: x-ipe-docs/planning/features/features.json, description: current board read only by owner/helper}
  optional:
    - {name: execution_mode, type: string, default: free-mode}
    - {name: workflow, type: object, description: exact name/action and selected required specification/optional closing-report}
    - {name: requestor, type: string, default: null, description: actual name/role or unknown; not implied approver}
    - {name: priority, type: string, default: medium, description: urgency does not waive authority}
    - {name: category, type: string, default: standalone}
    - {name: next_task_based_skill, type: array, description: original conditional suggestions only}
outputs:
  state:
    - {name: category, value: standalone}
    - {name: status, value: completed | blocked}
    - {name: next_task_based_skill, value: original conditional skill/condition list}
    - {name: process_preference.interaction_mode, value: original exact nested caller enum}
  artifacts:
    - {name: cr_document, type: file, path: actual owning EPIC/FEATURE or legacy CR file; approved free-mode intake exception, description: complete original scaffold plus goal delta and revision evidence}
    - {name: approved_delta_documents, type: files, path: actual affected requirements/spec/design-context/mockup links only, description: only approved sections; histories retained}
  data:
    - {name: execution_mode, type: string, description: original caller mode}
    - {name: workflow.name, type: string, description: original workflow identity or N/A}
    - {name: task_output_links, type: array, description: actual artifacts only; no nonexistent pending folders}
    - {name: feature_id, type: string, description: immutable primary owner or N/A for no-feature free-mode}
    - {name: cr_id, type: string, description: stable reserved actual CR ID}
    - {name: cr_classification, type: string, description: modification | new_feature; no third enum}
    - {name: affected_features, type: array, description: actual impacted existing IDs}
    - {name: new_feature_ids, type: array, description: empty until real later authorized allocation}
    - {name: requirement_updated, type: boolean, description: actual approved requirement source delta}
    - {name: mockup_updated, type: boolean, description: actual new mockup version only}
    - {name: updated_mockup_paths, type: array, description: actual new paths; original preserved}
    - {name: conflicts_found, type: array, description: original conflict records plus actual evidence in CR}
    - {name: conflicts_resolution, type: string, description: none | all_expected | mitigated; actual disposition}
    - {name: conflicting_docs_updated, type: array, description: actual minor inline approved sections}
    - {name: conflicting_docs_retired, type: array, description: major retained sections and replacement provenance}
acceptance_criteria:
  must:
    - {id: AC-S01, category: structure, criterion: valid canonical frontmatter and complete six-file candidate preserving original paths, test: root validator/inventory}
    - {id: AC-S02, category: structure, criterion: all original example use cases retained with corrected enums/owner/source evidence limits, test: authored example cases}
    - {id: AC-S03, category: structure, criterion: body at most 1000 logical lines; DoR at most 5 and DoD at most 10, test: root validator}
    - {id: AC-C01, category: content, criterion: ordered subtype sections/input initialization and five domain actions, test: XML/heading parse}
    - {id: AC-C02, category: content, criterion: actual conflict analysis before classification and approval; no missing sources treated as no conflicts, test: entry/reference and authored conflict table}
    - {id: AC-C03, category: review, criterion: meaningful workflow/executable/safety/public-contract risk independent review required; unavailable pending not completed, test: scoped contract and pending handoff}
    - {id: AC-C04, category: authority, criterion: one consolidated exact-revision classification/conflicts/goal/approach approval before all target edits; actual human large-scope or changed-contract permission in every mode, test: three-mode contracts and false authority negative}
    - {id: AC-B01, category: behavior, criterion: complete CR template and applicable both-path approved document/history/mockup updates before implementation; no phantom specification in no-feature intake, test: rendered scaffold and six use cases}
    - {id: AC-B02, category: contract, criterion: all original output fields nested values key order and conditional list stable; no new goal/status/tag schema, test: parsed live/candidate output equality}
    - {id: AC-G01, category: goal, criterion: changed goal/source/parent/stakeholder/before-proposed outcome/contribution/success/constraint/story/GWT AC/type/evidence links complete with full affected pipeline evaluated, test: delta/AC/matrix tables and negatives}
    - {id: AC-G02, category: classification, criterion: goal-aligned means and enabling subgoals can modification; independent outcome may new_feature after boundary/conflict facts not automatic screen/API/size rules, test: means/new-outcome/enabling/chain cases}
    - {id: AC-G03, category: evidence, criterion: delivery distinct from observed outcome/not measured; legacy explicit so-that labeled inferred and pertinent gaps blocked, test: false observation/source negatives and legacy case}
    - {id: AC-E01, category: freshness, criterion: affected design/test/review/outcome evidence invalidated with relevant hashes; unrelated IDs/bytes/evidence retained, test: changed/unchanged authored rows and negatives}
    - {id: AC-D01, category: preservation, criterion: major sections retired with reason/date/CR/replacement and histories/reserved ID mappings retained; minor approved inline changes; originals mockups never overwritten, test: major case/scaffold/version rules and protected fingerprint}
    - {id: AC-L01, category: lifecycle, criterion: same task/readiness and one owner no child board/Git/successor/app writes or recursive registration/routing, test: obsolete-block absence and disposable helper scope}
    - {id: AC-I01, category: integration, criterion: actual change_request action required specification optional closing-report exact cr-doc/scalar cr-folder and predecessor done/readback; no bogus tag, test: installed temporary helper success/failures/permissiveness}
    - {id: AC-I02, category: source, criterion: selected/board/unique EPIC or legacy source precedence anchors containment and wrong/broken/ambiguous link blocking; no-feature workflow blocked, test: integration contract and two-layout fixtures}
    - {id: AC-I03, category: configuration, criterion: actual empty CR config does not force-enable research/implementation tools; consequential research only within authorized capability, test: actual tools config and reference}
  should:
    - {id: AC-C05, criterion: CR template contains complete actual Conflict Analysis}
    - {id: AC-C06, criterion: DoD verifies conflict evidence and authorized dispositions}
    - {id: AC-C07, criterion: Skip conflict analysis anti-pattern retained with remedy}
    - {id: AC-B03, criterion: unresolved unexpected conflict blocks application/completion not just warning}
  could:
    - {id: AC-C08, criterion: separately authorized real autonomous CR pilot and stakeholder observation}
  wont:
    - {id: AC-W01, criterion: board status updates, reason: single lifecycle owner; explicitly excluded here}
    - {id: AC-W02, criterion: promotion before independent review, reason: user prohibited}
    - {id: AC-W03, criterion: other source/dirty docs/memory/Git/application gate migration, reason: excluded}
dependencies:
  skills:
    - {name: x-ipe-workflow-task-execution, relationship: prerequisite, description: common lifecycle/goal contract and one owner}
    - {name: x-ipe-task-based-feature-refinement, relationship: downstream, description: authoritative full specification scaffold and suggested successor}
    - {name: x-ipe-task-based-feature-breakdown, relationship: downstream, description: real later approved new-feature allocation}
    - {name: x-ipe-tool-x-ipe-app-interactor, relationship: consumer, description: actual workflow writer/readback; no child mutation}
    - {name: x-ipe-assistant-user-representative-Engineer, relationship: bounded guidance, description: real questions only under full DAO; not human authority}
  artifacts:
    - {path: x-ipe-docs/config/workflow-template.json, description: current action contexts tags and mandatory gates}
    - {path: x-ipe-docs/config/tools.json, description: current empty CR route}
    - {path: src/x_ipe/static/js/features/workflow-stage.js, description: authoritative ACTION_MAP}
test_scenarios:
  happy_path:
    - {name: Same-goal auto-save, given: original preferences outcome/constraints, when: authored delta rendered, then: means-only modification and all AC clauses/types preserved with planned checks}
    - {name: Actual workflow tags, given: disposable real template/state and actual CR/spec/folder, when: installed helper writes and reads, then: exact done/tag/context and optional report absent; no real board tasks}
  edge_cases:
    - {name: Bulk import boundary, given: existing single-product versus independent supplier outcome, when: critical matrix/conflict review, then: no automatic classification by new endpoint or subgoal}
    - {name: Legacy/no-feature, given: explicit so-that or absent related owner, when: authorized intake, then: inference/gaps honest; free-mode N/A or workflow blocker}
  error_cases:
    - {name: Authored false claim, given: changed parent/outcome/authority/AC/type/invalidation/matrix/source, when: consistency checker, then: reject not fake agent execution}
    - {name: Helper rejects wrong tags/feature/locked stage, given: temporary state, when: installed helper, then: nonzero and exact unchanged state bytes}
  blocking:
    - {name: Missing authority or unresolved unexpected conflict, given: unanalyzed/unapproved major solution, when: target edit requested, then: blocked before mutation}
    - {name: Required review unavailable, given: semantic safety/workflow change, when: promotion requested, then: pending review blocks promotion; drafting allowed}
evaluation:
  self_check:
    - Exact original schema, complete candidate and installed root validator with fresh receipt.
    - Separate dedicated tests; authored scenarios are not autonomous classification or stakeholder observations.
    - Actual installed helpers only in disposable projects; permissiveness documented, not semantic gate proof.
    - Existing unowned suites unchanged; only authorized CR promotion and dedicated tests/metadata; no TASK-6749 closure.
  judge_agent:
    - criterion: Independent main review
      rubric: Passed sequential review of inherited worker candidate; complete six-file package, consumers/authority/new-feature exceptions inspected before promotion; receipt records exact scope and limits.
version_history:
  - version: "2.0.0"
    date: 2026-10-13
    task_id: TASK-6749
    change: Goal delta and single-owner contracts; exact six-file promotion after inherited-candidate review and fresh verification
    evidence: publication-receipt-goal-TASK-6749.json
```

## Historical metadata (verbatim prework snapshot; superseded fields)

```text
# ═══════════════════════════════════════════════════════════
# SKILL META - Task-Based: Change Request
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-task-based-change-request
skill_type: x-ipe-task-based
version: "1.1.0"
status: candidate
created: 2026-02-15
updated: 2026-03-30

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
summary: |
  Process change requests by analyzing impact on existing requirements and features,
  detecting conflicts with existing specs/designs/code before human approval, and
  routing to the appropriate workflow (Feature Refinement or Requirement Update + Feature Breakdown).

triggers:
  - "change request"
  - "CR"
  - "modify feature"
  - "update requirement"

not_for:
  - "x-ipe-task-based-bug-fix: When the request is about broken existing functionality"
  - "x-ipe-task-based-feature-refinement: When the feature is already identified and needs specification"

# ─────────────────────────────────────────────────────────────
# WORKFLOW POSITION
# ─────────────────────────────────────────────────────────────
workflow:
  category: standalone
  phase: null
  next_task_based_skill: "x-ipe-task-based-feature-refinement | x-ipe-task-based-feature-breakdown"
  human_review: true

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: interaction_mode
      type: boolean
      default: false
      description: Whether to auto-proceed to next task

    - name: change_request_description
      type: string
      description: "Description of the requested change"

    - name: business_justification
      type: string
      description: "Why this change is needed"

  optional:
    - name: requestor
      type: string
      default: null
      description: "Name/role of person requesting the change"

    - name: priority
      type: string
      default: "medium"
      description: "Priority level: high, medium, low"

outputs:
  state:
    - name: category
      value: standalone
    - name: status
      value: completed | blocked
    - name: next_task_based_skill
      value: "x-ipe-task-based-feature-refinement | x-ipe-task-based-feature-breakdown"
    - name: require_human_review
      value: yes
    - name: interaction_mode
      value: "${inputs.interaction_mode}"

  artifacts:
    - name: cr_document
      type: file
      path: "x-ipe-docs/requirements/FEATURE-XXX/CR-XXX.md"
      description: "Change request document"

  data:
    - name: cr_classification
      type: string
      description: "modification | new_feature"
    - name: conflicts_found
      type: array
      description: "List of conflicts identified during conflict analysis"

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    - id: AC-S01
      category: structure
      criterion: SKILL.md exists with valid frontmatter
      test: file_exists + yaml_parse
      expected: name and description fields present

    - id: AC-S02
      category: structure
      criterion: references/examples.md exists
      test: file_exists
      expected: file contains at least 1 example

    - id: AC-S03
      category: structure
      criterion: SKILL.md body < 500 lines
      test: line_count
      expected: < 500

    - id: AC-C01
      category: content
      criterion: All required sections present in order
      test: section_parse
      expected: |
        [Frontmatter, Purpose, Important Notes, Input Parameters,
         Input Initialization, Definition of Ready, Execution Flow,
         Execution Procedure, Output Result, Definition of Done,
         Patterns & Anti-Patterns, Examples]

    - id: AC-C02
      category: content
      criterion: Conflict Analysis step exists between Classify and Human Approval
      test: section_parse
      expected: step_4 named "Conflict Analysis" with sub-agent conflict detection

    - id: AC-C03
      category: content
      criterion: Conflict Analysis uses sub-agent pattern from bug-fix skill
      test: content_check
      expected: Conflict Detector sub-agent analyzes specs, designs, dependencies

    - id: AC-C04
      category: content
      criterion: Human Approval step includes conflict analysis results
      test: content_check
      expected: step_5 presents conflicts alongside classification

    - id: AC-B01
      category: behavior
      criterion: Skill produces expected outputs including conflicts_found
      test: execution
      expected: all outputs.artifacts exist, conflicts_found in output YAML

    - id: AC-B02
      category: behavior
      criterion: Output YAML has correct structure with conflicts_found
      test: yaml_validate
      expected: category is first field, conflicts_found field present

  should:
    - id: AC-C05
      category: content
      criterion: CR template includes Conflict Analysis section
      test: content_check
      expected: templates/change-request.md has Conflict Analysis section

    - id: AC-C06
      category: content
      criterion: DoD includes conflict analysis checkpoint
      test: section_parse
      expected: DoD has "Conflict analysis completed" checkpoint

    - id: AC-C07
      category: content
      criterion: Anti-patterns include "Skip conflict analysis"
      test: table_parse
      expected: Anti-pattern table has row for skipping conflict analysis

    - id: AC-B03
      category: behavior
      criterion: BLOCKING gate prevents proceeding past Step 4 with unresolved conflicts
      test: execution
      expected: skill blocks when unexpected conflicts unresolved

  could:
    - id: AC-C08
      category: content
      criterion: Examples include conflict analysis scenario
      test: content_check
      expected: At least one example shows conflict detection

  wont:
    - id: AC-W01
      criterion: Board status updates
      reason: Handled by category skill, not task-based skill

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-workflow-task-execution
      relationship: prerequisite
      description: Must be learned before executing this skill

  artifacts:
    - path: "x-ipe-docs/requirements/requirement-details.md"
      description: "Must exist with current project requirements"
    - path: "x-ipe-docs/planning/features.md"
      description: "Must exist with current feature list"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "CR with no conflicts"
      given: "CR modifies feature with no dependencies"
      when: "Conflict analysis runs"
      then: "Empty conflicts list, proceed to human approval"

    - name: "CR with expected conflicts"
      given: "CR modifies feature used by another feature"
      when: "Conflict analysis detects spec overlap"
      then: "Conflicts classified as expected, included in human approval"

  edge_cases:
    - name: "CR with unexpected conflicts"
      given: "CR modifies shared data model"
      when: "Conflict analysis finds breaking changes"
      then: "Unexpected conflicts documented, mitigation strategies suggested"

  error_cases:
    - name: "Related specs missing"
      given: "Feature referenced but no specification exists"
      when: "Conflict analysis attempts to read specs"
      then: "Note missing specs, warn in approval presentation"

  blocking:
    - name: "Unresolved unexpected conflicts"
      given: "Unexpected conflicts found"
      when: "Attempt to proceed past Step 4"
      then: "BLOCKED - must resolve or document before human approval"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "Conflict Analysis step exists as Step 4"
    - "BLOCKING gate on Step 4 before Step 5"
    - "Output YAML includes conflicts_found field"
    - "DoD includes conflict analysis checkpoint"

  judge_agent:
    - criterion: "Conflict analysis is thorough and catches specification/design/dependency conflicts"
      rubric: |
        5: Excellent - catches all conflict types, clear mitigations
        4: Good - catches most conflicts, minor gaps
        3: Acceptable - catches obvious conflicts
        2: Poor - misses important conflict categories
        1: Fail - no meaningful conflict detection
```

      ## R2 recovered publication history

      - Version 2.0.1, TASK-6749; verified 2026-10-14T04:28:27.605298+00:00.
      - Current production/candidate fingerprint: 55ad88aaac927844d8019abe350b1c2f273bd007e89b7bca0f4a47128a0bd578.
      - [Recovered verification receipt](publication-receipt-TASK-6749-R2.json); prior history above remains historical, not current parity evidence.
      - Hybrid inner guidance and human completion/route boundary independently reviewed at exact R2 hash; actual human CR authority and affected-only invalidation retained. Prior-worker promotion time is unknown; no production replay or atomic writer journal claimed.

## TASK-6750 single-loop delivery revision

Published after deterministic validation, bounded workflow safety review, and real manifest-safe publication; prior metadata above remains version history.

- Current revision: `30caca6cdb12431f48a6b0196ad30857650969e618709b068d78f7a88d455482`
- Previous revision: `55ad88aaac927844d8019abe350b1c2f273bd007e89b7bca0f4a47128a0bd578`
- Evidence: `single-loop-TASK-6750.json`, `publication-receipt-TASK-6750.json`, `validation-receipt-TASK-6750.json`.
- Same-loop delivery/default risk-based verification; unchanged resources and protected bytes retained.
- Token/latency savings not measured; no live-agent efficacy claim.
