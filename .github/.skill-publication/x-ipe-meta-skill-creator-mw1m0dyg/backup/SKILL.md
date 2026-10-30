---
name: x-ipe-meta-skill-creator
description: Create or update X-IPE skills from subtype templates using candidate staging, deterministic validation, risk-based review, and manifest-safe publication. Triggers on requests like "create skill", "new skill", "add task-based skill", "update skill".
---

# X-IPE Skill Creator

## Purpose

Create and maintain concise, complete skill packages by:
1. Resolving scope, subtype, risk, and the smallest justified delta.
2. Drafting metadata and all resources in a complete candidate bundle.
3. Validating contracts and behavior with proportionate independent review.
4. Publishing only a reviewed, concurrency-checked manifest with recovery.

## About

Skills supply domain contracts and reusable procedures, not generic agent advice.
This meta skill operates on skill packages and their validation metadata.
It does not implement unrelated application features, migrate historical lessons,
modify another session's work, or authorize releases on the user's behalf.

### Key Concepts

- **Candidate:** complete proposed package, including unchanged resources.
- **Baseline:** full current production file/hash inventory captured before work.
- **Managed manifest:** trusted last-published inventory, not an invented ownership claim.
- **Delta:** additions, content changes, and explicitly reviewed resource removals.
- **Evidence:** validation receipt, scenario results, review, and byte parity.

### Skill Types

Retain every subtype template, including legacy DAO compatibility. New human
representatives use assistant skills; knowledge skills retain Operations + Steps.

| Type | SKILL template | Metadata template |
|------|----------------|-------------------|
| x-ipe-task-based | x-ipe-task-based.md | skill-meta-x-ipe-task-based.md |
| x-ipe-tool | x-ipe-tool.md | skill-meta-x-ipe-tool.md |
| x-ipe-workflow-orchestration | x-ipe-workflow-orchestration.md | skill-meta-x-ipe-task-based.md |
| x-ipe-task-category | x-ipe-workflow-orchestration.md | skill-meta-x-ipe-task-category.md |
| x-ipe-meta | x-ipe-meta.md | skill-meta-x-ipe-meta.md |
| x-ipe-knowledge | x-ipe-knowledge.md | skill-meta-x-ipe-knowledge.md |
| x-ipe-assistant | x-ipe-assistant.md | skill-meta-x-ipe-assistant.md |
| x-ipe-dao (legacy) | x-ipe-dao.md | skill-meta-x-ipe-dao.md |

The existing category identity `x-ipe+feature+quality-board-management` retains
its reporting Operations + `<operation>` and `operation_output` contract. Select
`x-ipe-task-category`, not `x-ipe-tool`; use its existing package as the update
scaffold. Only this exact legacy category has that validator contract exception.
Other categories retain the workflow scaffold; no rename or workflow_output
conversion is implied. See the validation reference for the compatibility rule.

## Important Notes

BLOCKING: Load [general guidelines](.github/skills/x-ipe-meta-skill-creator/references/skill-general-guidelines-v2.md)
and the selected templates before drafting. Preserve subtype-specific contracts.

Load [consumer integration](.github/skills/x-ipe-meta-skill-creator/references/consumer-integration.md)
for actual installed lesson select/settle calls and task-template goal adoption.
Selection is read-only; queue writes require explicit scope, current revisions
and owned evidence. If excluded, report settlement pending, never implied applied.

BLOCKING: Edit only `x-ipe-docs/skill-meta/{skill_name}/candidate/` and approved
metadata. Never create missing resources directly in production, including after
publication. Include them in the candidate and revalidate instead.

CRITICAL: Every X-IPE SKILL.md BODY has a maximum of **1,000 lines**, excluding
YAML frontmatter. Exactly 1,000 passes; 1,001 fails. This is a ceiling, not a target.
Count logical lines, including blanks, after the closing frontmatter delimiter;
CRLF and LF are equivalent; a trailing newline adds no phantom line.
DoR has at most five checkpoints; DoD has at most ten.

BLOCKING: Publication requires permission, fresh validation/review evidence,
trusted ownership, baseline and candidate fingerprints, and approved deletions.
Do not overwrite preexisting edits or use recursive copying/deletion to merge.

CRITICAL: Changed creator instructions take effect only after verified promotion.
Drafting alone does not authorize promotion or claim validation success. Keep
task-specific bootstrap and review records in metadata outside the publishable bundle.

## Input Parameters

```yaml
input:
  task_id: "{existing task supplied by lifecycle}"
  skill_name: "{canonical folder name}"
  skill_type: "{one subtype from the table}"
  user_request: "{intent, acceptance criteria, exclusions}"
  examples: []
  project_root: "{absolute project root}"
  candidate: "x-ipe-docs/skill-meta/{skill_name}/candidate"
  baseline: "{full pre-work production manifest; empty for a new skill}"
  managed: "{trusted previous published manifest; empty for a new skill}"
  process_preference:
    interaction_mode: "interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill"
```

### Input Initialization

```xml
<input_init>
  <field name="task_id" source="existing lifecycle task; do not create a duplicate" />
  <field name="skill_name">
    <steps>Resolve the exact canonical name; use lowercase hyphens (legacy category plus names allowed); reject naming conflicts.</steps>
  </field>
  <field name="skill_type">
    <steps>Select by responsibility, then load both mapped templates; do not infer tool task outputs.</steps>
  </field>
  <field name="project_root">
    <steps>Resolve the approved project; reject symlinked or escaping candidate/production paths.</steps>
  </field>
  <field name="baseline">
    <steps>Inventory production before work; compare to trusted managed hashes and identify dirty/unmanaged files. Record rather than assume ownership.</steps>
  </field>
  <field name="examples">
    <steps>Reuse clear examples already supplied; ask only bounded unresolved questions. Record at least two representative scenarios.</steps>
  </field>
  <field name="process_preference" source="lifecycle policy; retain all three existing interaction modes" />
</input_init>
```

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Scope authorized</name>
    <verification>Existing task, intent, exclusions, and permitted paths are known.</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Subtype resolved</name>
    <verification>Canonical name and both subtype templates are selected and loaded.</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Baseline protected</name>
    <verification>Full inventory and trusted managed manifest distinguish preexisting edits and unmanaged resources.</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Scenarios and risk understood</name>
    <verification>Examples, dependencies, dangerous operations, and review needs are explicit.</verification>
  </checkpoint>
</definition_of_ready>
```

## Execution Flow

| Step | Action | Gate |
|------|--------|------|
| 1 | Scope and delta plan | Ambiguities resolved; risk documented |
| 2 | Complete candidate + metadata | Resources preserved; removals explicit |
| 3 | Deterministic checks + scenarios + review | Fresh evidence; no blocking findings |
| 4 | Dry-run then authorized publication | Fingerprints, ownership, recovery, parity |
| 5 | Record completion or blocked state | Honest evidence and lesson disposition |

## Execution Procedure

```xml
<procedure name="skill-creation">
  <execute_dor_checks_before_starting/>
  <step_1>
    <name>Scope and Plan</name>
    <action>
      1. Compare requested behavior with current package; plan the smallest delta.
      2. Invoke installed lesson_ops.select with explicit project_root, owner skills and relevant_to target per consumer integration; retain summaries, critical_overflow, protected and notices. Select up to five relevant valid summaries within approximately 120 lines; zero is valid. No filesystem-wide raw lesson concatenation.
      3. Legacy undated/raw records require verification, not automatic freshness or expiry. Record selected lesson-to-change/scenario mapping in metadata. When queue writes are authorized, load its revision and invoke settle(status=planned) only for an actual existing open owned task and canonical candidate; otherwise record pending. Do not migrate historical status.
      4. IF cosmetic/document-only and no semantics change, use lightweight checks; ELSE require independent review for workflow, executable, or safety-policy changes.
      5. Route genuine questions through the resolved interaction policy; DAO cannot invent release permission.
    </action>
    <output>delta plan, selected lesson mappings, scenarios, risk/review plan</output>
  </step_1>
  <step_2>
    <name>Draft Complete Candidate</name>
    <action>
      1. For a new skill, fill both templates. For an existing skill, preserve metadata and unchanged resources, including tracked candidate differences; do not overwrite them blindly from production.
      2. Compare complete production and candidate trees; explain every missing/extra path and content difference.
      3. Draft all scripts, references, templates, and entry instructions inside candidate. Resource removals require a named rationale and reviewed deletion list.
      4. Preserve domain contracts, configuration gating, discovery triggers, and input/output schemas. Task-based outputs retain category, next_task_based_skill, and process_preference.interaction_mode; tools retain their operation result contract.
      5. Keep project-root links canonical; validator maps self production references to candidate. Detailed examples and recovery instructions belong in references.
      6. New/changed task skills use the shared document-local goal contract: source/parent/stakeholder, contribution, all-required versus selected alternatives, stable story/GWT AC/type and planned/actual checks. Reuse existing artifacts; distinguish engineering delivery from unobserved outcome, not measured. No new board/output fields or historical retrofit.
    </action>
    <output>complete candidate package, template-derived skill-meta.md</output>
  </step_2>
  <step_3>
    <name>Verify and Review</name>
    <action>
      1. Run .github/skills/x-ipe-meta-skill-creator/scripts/validate_skill.py with project root, target name, subtype, and target candidate; capture its JSON receipt outside the bundle. Tooling belongs to the installed creator, not the target skill's candidate/scripts. During an authorized creator bootstrap only, use the reviewed creator candidate helper and record that override in external metadata.
      2. Execute applicable scenarios against temporary projects, never production; record commands, results, fingerprints, and known failures.
      3. Obtain independent review when required by risk; unavailable review blocks promotion, not drafting. Cosmetic work can use deterministic and self-review evidence.
      4. Correct blocking findings and rerun affected checks; changed content invalidates receipts. Escalate after three failed iterations rather than claiming completion.
      5. Verify external workflow/config consumers separately; structural validation does not prove runtime compatibility or semantic correctness.
    </action>
    <output>validation receipt, scenario evidence, independent review or justified lightweight disposition</output>
  </step_3>
  <step_4>
    <name>Publish Safely</name>
    <action>
      1. Run .github/skills/x-ipe-meta-skill-creator/scripts/publish_skill.py in default dry-run mode with baseline, managed manifest, validated candidate hash, and exact reviewed deletion paths; use the same creator-tooling resolution as Step 3.
      2. Review full additions/changes/deletions and protected paths. Resolve preexisting dirty/unmanaged changes explicitly; never relabel them as managed to bypass protection.
      3. IF candidate-only scope or missing permission/evidence, stop with candidate_ready or blocked; ELSE invoke the same reviewed plan with --apply.
      4. Publication stages bytes outside production, locks cooperating publishers, rechecks fingerprints, journals the swap, preserves backup, and verifies exact bytes.
      5. IF interruption/failure, inspect retained transaction and use --recover; never blindly remove production/backup. Concurrent noncooperating changes block destructive rollback.
    </action>
    <output>dry-run plan or publication/recovery receipt and byte parity</output>
  </step_4>
  <step_5>
    <name>Record Outcome</name>
    <action>
      1. Return exact owned paths, evidence, unresolved issues, and next action to lifecycle owner; do not duplicate board or git work.
      2. Update version history only after verified publication; retain prior history unchanged during candidate work.
      3. Invoke installed lesson_ops.settle for selected owned mappings only: applied requires actual production fingerprint, complete compatible publisher JSON receipt and relevant passing production test receipt per consumer integration, not reading/drafting. An editor-promotion receipt is not compatible publisher evidence; report blocked instead of translating it into fictitious publish success.
      4. Failed publication preserves planned ownership or explicitly releases via settle(status=active, task, reason) while valid. Replay identical owned receipts is unchanged, never renewed. Excluded queue writes remain pending. Do not prune/migrate historical lessons without separately approved maintenance.
    </action>
    <output>honest completion record and bounded lesson dispositions</output>
  </step_5>
</procedure>
```

## Output Result

```yaml
task_completion_output:
  category: standalone
  status: completed | blocked
  next_task_based_skill: null
  process_preference:
    interaction_mode: "{resolved mode}"
  require_human_review: "{risk and user boundary}"
  task_output_links: ["{candidate}", "{skill-meta}", "{evidence}"]
  skill_name: "{skill_name}"
  skill_type: "{skill_type}"
  publication_state: candidate_ready | published | blocked | recovery_required
  candidate_hash: "{validated manifest fingerprint}"
  unresolved_issues: []
```

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true"><name>Scope and resources</name><verification>Template-derived metadata, complete candidate, and explicit delta/removals match authorized scope.</verification></checkpoint>
  <checkpoint required="true"><name>Contracts valid</name><verification>Frontmatter, subtype contract, local resources, line boundary, and checkpoint limits pass deterministic validation.</verification></checkpoint>
  <checkpoint required="true"><name>Behavior evidenced</name><verification>Applicable scenarios pass; known failures and unavailable evidence are not concealed.</verification></checkpoint>
  <checkpoint required="true"><name>Review proportionate</name><verification>Independent review covers meaningful workflow/executable/safety changes; lightweight exceptions have rationale.</verification></checkpoint>
  <checkpoint required="true"><name>Publication honest</name><verification>Candidate-only outcome is explicit; published outcome requires authorized manifest, fresh baseline, recovery record, and exact byte parity.</verification></checkpoint>
  <checkpoint required="true"><name>Records accurate</name><verification>History changes only after promotion; selected lessons need publication and test evidence before applied status.</verification></checkpoint>
</definition_of_done>
```

## Templates

All subtype mappings above resolve under
[templates](.github/skills/x-ipe-meta-skill-creator/templates).
Load [meta scaffold](.github/skills/x-ipe-meta-skill-creator/templates/x-ipe-meta.md)
and [meta metadata](.github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-meta.md)
for the creator itself; do not fabricate replacements from scratch.

## Examples and References

- [Examples](.github/skills/x-ipe-meta-skill-creator/references/examples.md): current subtype drafting, verification, and candidate-only examples.
- [Validation and publication](.github/skills/x-ipe-meta-skill-creator/references/validation-publication.md): API, receipt, ownership, and recovery contract.
- [Production patterns](.github/skills/x-ipe-meta-skill-creator/references/12.%20reference-production-patterns.md): bounded lessons, explicit dependencies, configuration gating.
- [Type comparison](.github/skills/x-ipe-meta-skill-creator/references/skill-type-comparison.md): subtype responsibilities.
