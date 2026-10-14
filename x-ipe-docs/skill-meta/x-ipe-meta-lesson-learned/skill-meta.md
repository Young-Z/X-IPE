---
skill_name: x-ipe-meta-lesson-learned
skill_type: x-ipe-meta
version: 2.0.0
last_updated: 2026-10-13
implementation_path: .github/skills/x-ipe-meta-lesson-learned/
candidate_path: x-ipe-docs/skill-meta/x-ipe-meta-lesson-learned/candidate/
task_id: TASK-6749
publication_state: published
purpose: Maintain selective time-bounded skill-improvement queues, not incident diaries.
target_skill_types:
  - x-ipe-task-based
  - x-ipe-tool
  - x-ipe-workflow-orchestration
  - x-ipe-task-category
  - x-ipe-meta
  - x-ipe-knowledge
  - x-ipe-assistant
inputs:
  - name: operation
    type: enum
    required: true
    validation: capture | select | settle | prune
  - name: project_root
    type: path
    required: true
    validation: Explicit approved absolute root; temporary projects supported.
  - name: skill_name
    type: string
    required: true
    validation: Existing skill; scoped identity; no traversal or linked nodes.
  - name: proposal
    type: mapping
    required: false
    validation: Agent-provided qualitative admission, bounded evidence, verified truth.
  - name: expected_revision
    type: string
    required: false
    validation: Required SHA256 snapshot for every write.
  - name: decision
    type: mapping
    required: false
    validation: Actual task ownership, candidate mapping or publication/test evidence.
outputs:
  - name: skill_package
    type: skill_package
    path: x-ipe-docs/skill-meta/x-ipe-meta-lesson-learned/candidate/
    description: Complete validated package; byte-identical to promoted production.
  - name: skill_meta
    type: file
    path: x-ipe-docs/skill-meta/x-ipe-meta-lesson-learned/skill-meta.md
    description: Template-derived acceptance and review metadata.
  - name: operation_result
    type: mapping
    description: Bounded disposition, revision, protected records and actions.
acceptance_criteria:
  must:
    - id: AC-M01
      description: Valid frontmatter, meta sections, canonical resource links and complete candidate.
      test_method: promoted_creator_validator
      expected: Five resources, no missing production resources, no validation errors/warnings.
    - id: AC-M02
      description: Compact template-derived body within 1000 logical lines.
      test_method: promoted_creator_validator
      expected: 221 body lines; four DoR and six DoD checkpoints.
    - id: AC-M03
      description: Admission needs critical/high-value reason and verified reusable correction.
      test_method: temporary_project_pytest
      expected: Major label alone blocks; unknown truth incident handoff; ordinary/no-retention skips.
    - id: AC-M04
      description: Finite override, two evidence links, dedup and eight pending capacity.
      test_method: temporary_project_pytest
      expected: Explicit request/purpose/1-180 day TTL; distinct recurrence evidence; no silent eviction.
    - id: AC-M05
      description: Selection is read-only, relevant, time-filtered and bounded.
      test_method: temporary_project_pytest
      expected: At most five summaries across primary owners; relevant critical overflow notice.
    - id: AC-M06
      description: Lifecycle has honest owned adoption and verified application.
      test_method: temporary_project_pytest
      expected: Existing task/candidate and mappings; publication bytes plus scoped passing test; replay unchanged.
    - id: AC-M07
      description: Exact UTC expiry and terminal grace with safe physical cleanup.
      test_method: temporary_project_pytest
      expected: 90/180 TTL, 90 critical review, 30 terminal grace; dry-run, explicit apply/preservation and critical handoff.
    - id: AC-M08
      description: Protect unknown legacy, prohibited paths and concurrent edits.
      test_method: temporary_project_pytest
      expected: Legacy filename accepted, undated/status protected; monotonic IDs; atomic lock/revision conflict.
  should:
    - id: AC-S01
      description: Runtime helper installs without external template files.
      test_method: temporary_project_pytest
      expected: Bundled template and explicit-root API/CLI tests pass.
    - id: AC-S02
      description: Review notices do not automatically steal planned ownership or refresh time.
      test_method: temporary_project_pytest
      expected: 14-day ownership and 90-day critical review notices only.
  could:
    - id: AC-C01
      description: Independent executable/safety-policy review before promotion.
      test_method: independent_review
      expected: Sequential independent reviewer passed; fixes evidenced before promotion.
  wont:
    - id: AC-W01
      description: Mirrors, historical migration, board/memory/Git writes.
      reason: Step3 permits reviewed edit-tool-only package promotion; other exclusions remain.
    - id: AC-W02
      description: Automatic severity scoring, database, external issue verification, abandoned-owner takeover.
      reason: Small helper; qualitative decisions remain agent responsibilities; conservative blocking is allowed.
evaluation:
  self_check:
    - Promoted creator validator; complete resource hashes and no removals.
    - 100 temporary-project API/CLI lifecycle tests; same 100 against installed helper/template.
    - Five production resources verified byte-identical to complete validated candidate.
  judge_agent:
    - Sequential independent safety/executable review passed; user authorized promotion.
workflow:
  sub_agent_dag: risk_based
  test_driven: false
  supports_iteration: true
dependencies:
  skills:
    - x-ipe-meta-skill-creator
  artifacts:
    - path: x-ipe-docs/planning/tasks/
      description: Existing-schema owned task files, read-only verification.
  templates:
    - .github/skills/x-ipe-meta-skill-creator/templates/x-ipe-meta.md
    - .github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-meta.md
    - .github/skills/x-ipe-meta-lesson-learned/templates/lesson-learned.md
---

# TASK-6749 — Published 2.0.0

Sequential review completed 2026-10-13. Original 85 tests passed; 15 additional
cases exposed 13 failures, repaired in candidate before promotion. Final and
installed suites each pass 100. Promoted validator: 221 body lines, five resources,
no errors/warnings. Reviewed clean tracked HEAD inventory matched original
baseline; working/index diffs were empty before changes. Complete promotion used
edit tools only as requested, followed by exact byte parity. No transactional
publisher --apply or atomic-swap guarantee is claimed. See review-findings.md,
promotion-receipt.json and skill-version-history.md for evidence and boundaries.

## Prior Step 2 Record (Historical Candidate-Only Context)

User supplied the existing task and approved full plan/lesson redesign. No
duplicate board/task or lifecycle operations were performed. This metadata
adapts the meta scaffold's interface/acceptance/evaluation/dependency fields;
runtime helper generation is explicitly in scope (not the generic template's
runtime-code exclusion). At Step 2, version 2.0.0 was proposed, not released.

## Scope, Baseline and Delta

Loaded promoted creator, general guidelines, both meta templates, approved
TASK-6748 plan, existing lesson entry/examples and actual legacy template.
The old documented template path is absent; bundled canonical template fixes
clean installation without editing the old global template.

Production has two files; both are represented in the candidate. Their content
is intentionally replaced with bounded lifecycle instructions/examples. Three
resources are added: helper, API reference and canonical empty queue. No removals.
No preexisting target candidate/meta folder was present to overwrite.
Hashes were inventoried after candidate staging; production remained unchanged.
This baseline is concurrency evidence, NOT a trusted managed ownership claim.
No Git lookup was authorized; managed provenance remains unresolved for reviewer.

## Lesson-to-Change Mapping

Approved redesign is represented by TASK-6748 plan, not a new persistent lesson.
No historical lessons were read into routine context, dated, migrated, marked
applied or pruned. The previously read example/template is structural source
material, not verified ground truth for an admitted lesson.

## Scenarios and Risk

Primary scenarios: consequential authorization failure → verified correction;
blocking contract recurrence → bounded consolidation; owned candidate → verified
publication/test application → replay; expiry → owned risk handoff → preservation.
Negative scenarios: harmless/covered/no-retention, unknown truth, fake major label,
candidate-only receipt, wrong owner/test, stale revisions, undated legacy and WIP.

Meaningful workflow/executable/safety changes require independent review. This
session supplies deterministic evidence only. Candidate-ready means ready for
that reviewer, NOT approved for release. No publication/dry-run merge was invoked.

## Remaining Gaps (Still Applicable After Promotion)

- External consumer/instruction variants and existing lessons are untouched;
  their compatibility/integration/migration need separate approved work.
- Helper verifies existing tasks, not arbitrary remote issue providers.
- Physical purge always requires revision-bound explicit user approval because
  no Git tracked/history state is inspected. Critical resolved/rejected content
  conservatively requires task handoff unless verified applied.
- Semantic dedup/admission, trustworthy evidence provenance and explicit user
  permission remain agent gates. Self-authored JSON is not cryptographic proof.
- Evidence-only revalidation without a new occurrence, retired re-admission and
  automatic abandoned-plan release block rather than infer unsupported facts.
- POSIX cooperative locks/atomic writes tested; Windows, remote filesystems,
  power-loss directory durability and hostile noncooperating writer races unproven.
- Pending exceptions can prevent strict disk bounds; optional ownership/receipt
  fields can exceed the aspirational 20 physical lines per entry.
- No test-before-implementation claim: tests were staged with implementation,
  then executed and refined. One initial test assertion misidentified the
  intentionally persistent lock as leaked temporary storage; corrected honestly.
