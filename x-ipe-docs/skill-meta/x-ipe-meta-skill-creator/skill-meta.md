# Skill Metadata: x-ipe-meta-skill-creator

```yaml
# ═══════════════════════════════════════════════════════════
# SKILL META - x-ipe-meta-skill-creator
# ═══════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# IDENTITY
# ─────────────────────────────────────────────────────────────
skill_name: x-ipe-meta-skill-creator
skill_type: x-ipe-meta
version: "1.3.0"
status: published
created: 2026-02-05
updated: 2026-10-14
implementation_path: .github/skills/x-ipe-meta-skill-creator/
created_from: .github/skills/x-ipe-meta-skill-creator/templates/skill-meta-x-ipe-meta.md
draft_task: TASK-6749
draft_round: 1
draft_role: Meta & Draft Creator
bootstrap_procedure: "OLD creator: four rounds; this delivery is Round 1 only"
validation_state: "Current R2 installed API/CLI, full manifest and test evidence validated in publication-receipt-TASK-6749-R2.json; older evaluation/drafting fields below are historical provenance, not current evidence"
publication_state: "Published exact independently reviewed R2 creator candidate via authorized per-file apply_patch; 33 distributables match, two unmanaged caches preserved; see publication-receipt-TASK-6749-R2.json. Prior receipts retained unchanged; real lesson settlement excluded/pending."
cleanup_policy: "Creator-only metadata root excludes exactly review-findings.md and test-cases.yaml after persistent editing-tool deletion failure; authoritative copies remain outside candidate"
compatibility_scope: "Actual creator bundle templates and existing nested caller contract; no application workflow modernization or blanket runtime compatibility"
version_history_policy: "Advanced to 1.3.0 only after verified R2 production parity and saved-receipt validation; prior history entries retained unchanged"

# ─────────────────────────────────────────────────────────────
# PURPOSE
# ─────────────────────────────────────────────────────────────
purpose: |
  Create/update complete template-derived candidates with deterministic validation,
  risk-based independent review, bounded lesson adoption, and manifest-safe publication.

target_skill_types:
  - x-ipe-task-based
  - x-ipe-tool
  - x-ipe-workflow-orchestration
  - x-ipe-meta
  - x-ipe-task-category
  - x-ipe-dao
  - x-ipe-knowledge
  - x-ipe-assistant

triggers:
  - "create a new skill"
  - "build a skill for {task}"
  - "generate skill template"

not_for:
  - "x-ipe-meta-lesson-learned: for capturing feedback on existing skills"
  - "x-ipe-workflow-task-execution: for executing tasks, not creating skills"

# ─────────────────────────────────────────────────────────────
# VERSION HISTORY
# ─────────────────────────────────────────────────────────────
upgraded_from: x-ipe-meta-skill-creator-v2

improvements_over_v2:
  - area: Templates
    v2_issue: "4 mentioned, only 2 exist"
    v3_fix: "All 6 templates exist and validated (added task-category and dao)"
  - area: Examples
    v2_issue: ">= 2 examples"
    v3_fix: ">= 3 concrete usage examples required"
  - area: Keywords
    v2_issue: "Mentioned but not enforced"
    v3_fix: "BLOCKING/CRITICAL/MANDATORY validation (no emoji)"
  - area: Sub-agent workflow
    v2_issue: "Basic"
    v3_fix: "Full DAG with model hints (haiku/sonnet)"

# ─────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────
inputs:
  required:
    - name: skill_name
      type: string
      description: Name of skill to create/manage
      validation: "Canonical subtype prefix, lowercase hyphens; legacy category x-ipe+ names and exact existing Engineer assistant identity allowed; 1-64 chars"
    - name: skill_type
      type: string
      description: Type of skill
      validation: "x-ipe-task-based | x-ipe-tool | x-ipe-workflow-orchestration | x-ipe-meta | x-ipe-task-category | x-ipe-dao | x-ipe-knowledge | x-ipe-assistant"
    - name: user_request
      type: string
      description: Description of what the skill should do

  optional:
    - name: examples
      type: array
      default: null
      description: Concrete usage examples provided by user

outputs:
  artifacts:
    - name: skill_package
      type: directory
      path: ".github/skills/{skill_name}/"
      description: Complete published package only after permission and verified promotion; Round 1 output is candidate/
      created_from: ".github/skills/x-ipe-meta-skill-creator/templates/{mapped_template} (reviewed creator candidate override only during bootstrap)"
    - name: skill_meta
      type: file
      path: "x-ipe-docs/skill-meta/{skill_name}/skill-meta.md"
      description: Skill specification with acceptance criteria
      created_from: ".github/skills/x-ipe-meta-skill-creator/templates/{mapped_meta_template} (reviewed creator candidate override only during bootstrap)"

  state:
    - name: status
      value: completed | blocked
    - name: templates_validated
      value: true | false

# ─────────────────────────────────────────────────────────────
# ACCEPTANCE CRITERIA (MoSCoW)
# ─────────────────────────────────────────────────────────────
acceptance_criteria:
  must:
    # STRUCTURE - File organization
    - id: AC-M01
      category: structure
      criterion: All eight subtype mappings retain complete SKILL and metadata templates
      test: file_exists
      expected: |
        x-ipe-task-based.md, x-ipe-tool.md, x-ipe-workflow-orchestration.md,
        x-ipe-meta.md, x-ipe-dao.md, x-ipe-knowledge.md, x-ipe-assistant.md,
        all seven skill-meta subtype templates (workflow shares task-based)
    
    - id: AC-M02
      category: structure
      criterion: Each template follows skill-general-guidelines-v2.md section order
      test: structure_validation
      expected: Section order matches cognitive flow per skill type

    - id: AC-M03
      category: structure
      criterion: All X-IPE SKILL.md bodies ≤ 1000 logical lines, frontmatter excluded (ceiling, not target)
      test: line_count
      expected: "1000 passes; 1001 fails; blank lines included; LF/CRLF and trailing-newline behavior equivalent"

    # CONTENT - Required sections and quality
    - id: AC-M04
      category: content
      criterion: At least 3 concrete usage examples in references/examples.md
      test: content_check
      expected: ">= 3 examples with ## Example headers"

    - id: AC-M05
      category: content
      criterion: Importance signals use keywords (BLOCKING, CRITICAL, MANDATORY)
      test: content_check
      expected: "No emoji importance signals (⛔, ⚠️, 🔴, 🟢)"

    - id: AC-M06
      category: content
      criterion: YAML frontmatter has name (1-64 chars) and description (includes triggers)
      test: yaml_parse
      expected: "name and description fields present with trigger phrases"

    - id: AC-M07
      category: content
      criterion: BLOCKING reference to skill-general-guidelines-v2.md in Important Notes
      test: content_check
      expected: "BLOCKING.*skill-general-guidelines pattern found"

    # BEHAVIOR - Execution produces correct results
    - id: AC-M08
      category: behavior
      criterion: Risk-based independent review for meaningful workflow, executable, or safety-policy changes
      test: structure_validation
      expected: "One independent reviewer where required; cosmetic exception documented; no fixed four-agent requirement after promotion"

    - id: AC-M09
      category: behavior
      criterion: Final deliverables and safety gates are covered by bounded DoR/DoD checkpoints
      test: content_comparison
      expected: "DoR ≤ 5; DoD ≤ 10; grouped checks cover complete resources, validation, review, publication, records"

    - id: AC-M10
      category: behavior
      criterion: Validator preserves subtype contracts and resolves candidate-self versus project-external resources
      test: content_comparison
      expected: "Required subtype sections; tool/knowledge operation outputs not forced into task_completion_output; broken local links block"

    - id: AC-M11
      category: safety
      criterion: Baseline and reviewed candidate fingerprints reject concurrent modification
      test: temporary_project_transaction
      expected: "Nonzero JSON failure without discarding target edits"
    - id: AC-M12
      category: safety
      criterion: Managed manifest protects preexisting dirty, deleted, and unmanaged resources
      test: temporary_project_transaction
      expected: "Only identical protected bytes retained; no ownership inferred from current baseline"
    - id: AC-M13
      category: safety
      criterion: Complete add/change/remove manifest and exact reviewed deletion list
      test: temporary_project_transaction
      expected: "Resource deletion requires trusted managed hash plus explicit review; no blind recursive deletion"
    - id: AC-M14
      category: safety
      criterion: Same-name canonical paths, symlink/traversal/special-node protection, dry-run default
      test: temporary_project_transaction
      expected: "Invalid roots blocked; dry-run changes no files; explicit --apply required"
    - id: AC-M15
      category: safety
      criterion: Staged byte comparison, journaled swap, retained backup, and recoverable interrupted publication
      test: temporary_project_fault_injection
      expected: "Rollback restores baseline or explicitly blocks on unexpected edits; production never recursively deleted"
    - id: AC-M16
      category: behavior
      criterion: Lesson application requires publication plus verification evidence
      test: independent_review
      expected: "LL-001 mapping planned in metadata; historical raw status unchanged in Round 1"

  should:
    - id: AC-S01
      category: content
      criterion: Section order follows cognitive flow (CONTEXT → DECISION → ACTION → VERIFY → REFERENCE)
      test: section_parse
      expected: "Sections in correct order"

    - id: AC-S02
      category: structure
      criterion: Complex details delegated to references/ folder
      test: content_check
      expected: "Progressive disclosure applied"

    - id: AC-S03
      category: content
      criterion: DoR/DoD use XML checkpoint format
      test: structure_validation
      expected: "<definition_of_ready> and <definition_of_done> tags"

    - id: AC-S04
      category: content
      criterion: Uses {variable_name} pattern throughout procedures
      test: content_check
      expected: "Consistent variable syntax"

    - id: AC-S05
      category: content
      criterion: Input Initialization subsection present under Input Parameters
      test: section_parse
      expected: "### Input Initialization with <input_init> XML block"

  could:
    - id: AC-C01
      category: content
      criterion: Cross-reference validation for x-ipe-task-based skills
      test: custom
      expected: "Bidirectional references validated"

    - id: AC-C02
      category: behavior
      criterion: Skill update workflow checks x-ipe-meta-lesson-learned.md
      test: content_check
      expected: "Lesson integration documented"

    - id: AC-C03
      category: behavior
      criterion: Proportional reviewer/decomposition choices avoid unnecessary handoffs
      test: content_check
      expected: "Review by semantics and risk, not line count, step count, or hardcoded model"

  wont:
    - id: AC-W01
      criterion: Application feature generation or historical lesson migration in this creator update
      reason: "Candidate helper scripts are in scope; unrelated runtime and lesson maintenance are not"

# ─────────────────────────────────────────────────────────────
# DEPENDENCIES
# ─────────────────────────────────────────────────────────────
dependencies:
  skills:
    - name: x-ipe-meta-lesson-learned
      relationship: integration
      description: Bounded relevant selection; settle after publication only; no compulsory incident-history loading

  artifacts:
    - path: ".github/skills/x-ipe-meta-skill-creator/references/skill-general-guidelines-v2.md"
      description: "Candidate-local self-reference before promotion"

  # ═══════════════════════════════════════════════════════════
  # TEMPLATE MAPPING
  # ═══════════════════════════════════════════════════════════
  # CRITICAL: Use these templates instead of creating from scratch
  # Location: x-ipe-docs/skill-meta/x-ipe-meta-skill-creator/candidate/templates/
  # ═══════════════════════════════════════════════════════════
  
  skill_templates:
    description: "SKILL.md templates - use to create skill implementation"
    mapping:
      x-ipe-task-based: x-ipe-task-based.md
      x-ipe-tool: x-ipe-tool.md
      x-ipe-workflow-orchestration: x-ipe-workflow-orchestration.md
      x-ipe-meta: x-ipe-meta.md
      x-ipe-task-category: x-ipe-workflow-orchestration.md  # Same structure
      x-ipe-dao: x-ipe-dao.md
      x-ipe-knowledge: x-ipe-knowledge.md
      x-ipe-assistant: x-ipe-assistant.md

  skill_meta_templates:
    description: "skill-meta.md templates - use to create acceptance criteria"
    mapping:
      x-ipe-task-based: skill-meta-x-ipe-task-based.md
      x-ipe-tool: skill-meta-x-ipe-tool.md
      x-ipe-task-category: skill-meta-x-ipe-task-category.md
      x-ipe-meta: skill-meta-x-ipe-meta.md
      x-ipe-workflow-orchestration: skill-meta-x-ipe-task-based.md  # Same structure
      x-ipe-dao: skill-meta-x-ipe-dao.md
      x-ipe-knowledge: skill-meta-x-ipe-knowledge.md
      x-ipe-assistant: skill-meta-x-ipe-assistant.md

# ─────────────────────────────────────────────────────────────
# TEMPLATE USAGE PROCEDURE
# ─────────────────────────────────────────────────────────────
template_usage:
  step_1:
    action: "Identify skill_type from user request"
    output: "skill_type value"
  
  step_2:
    action: "Load SKILL.md template"
    source: ".github/skills/x-ipe-meta-skill-creator/templates/{skill_templates.mapping[skill_type]} (creator candidate override during authorized bootstrap only)"
    output: "SKILL.md scaffold"
  
  step_3:
    action: "Load skill-meta.md template"  
    source: ".github/skills/x-ipe-meta-skill-creator/templates/{skill_meta_templates.mapping[skill_type]} (creator candidate override during authorized bootstrap only)"
    output: "skill-meta.md scaffold"
  
  step_4:
    action: "Fill templates with skill-specific content"
    inputs: [user_request, skill_name, examples]
    output: "Complete SKILL.md and skill-meta.md"
  
  step_5:
    action: "Validate against guideline-v2"
    reference: "candidate/references/skill-general-guidelines-v2.md"
    output: "Validation result"

# ─────────────────────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────────────────────
test_scenarios:
  happy_path:
    - name: "Create task-based skill from template"
      given: "User request for task-based skill"
      when: "Load x-ipe-task-based.md and skill-meta-x-ipe-task-based.md templates"
      then: "Valid SKILL.md and skill-meta.md produced from templates"

    - name: "Create tool skill from template"
      given: "User request for utility tool"
      when: "Load x-ipe-tool.md and skill-meta-x-ipe-tool.md templates"
      then: "Valid SKILL.md and skill-meta.md produced from templates"

    - name: "Create meta skill from template"
      given: "User request for meta skill"
      when: "Load x-ipe-meta.md and skill-meta-x-ipe-meta.md templates"
      then: "Valid SKILL.md and skill-meta.md produced from templates"

    - name: "Validate template structure"
      given: "Draft skill created from template"
      when: "Run validation against guideline-v2"
      then: "Section order matches template structure"

  edge_cases:
    - name: "Meaningful safety change requires independent review"
      given: "Executable publisher or workflow-contract change"
      when: "Execute skill creator"
      then: "Independent review required before publication; no fixed agent count"

  error_cases:
    - name: "Invalid skill type"
      given: "Unknown skill_type parameter"
      when: "Execute skill creator"
      then: "Error: unsupported skill type"

  blocking:
    - name: "Missing guideline reference"
      given: "SKILL.md without BLOCKING guideline reference"
      when: "Run validation"
      then: "BLOCKED: AC-M07 failed"

# ─────────────────────────────────────────────────────────────
# EVALUATION
# ─────────────────────────────────────────────────────────────
evaluation:
  self_check:
    - "All template files exist"
    - "Logical body line count ≤ 1000; 1000 pass / 1001 fail, newline variants"
    - "Section order validated"
    - "Keyword vs emoji check passed"
    - "Bounded checkpoints cover final deliverables and safety gates"
    - "Candidate resource hashes, baseline/managed manifests, deletion review, path safety, and exact byte parity"

  judge_agent:
    - criterion: "Quality of execution procedure clarity"
      rubric: |
        5: Crystal clear, unambiguous steps
        4: Clear with minor ambiguities
        3: Acceptable, some gaps
        2: Confusing, significant issues
        1: Unusable

    - criterion: "Acceptance criteria completeness"
      rubric: |
        5: All behaviors covered with tests
        4: Most behaviors covered
        3: Core behaviors covered
        2: Major gaps
        1: Insufficient

# ─────────────────────────────────────────────────────────────
# PASS CRITERIA
# ─────────────────────────────────────────────────────────────
pass_criteria:
  must_pass_rate: 100%   # All 16 MUST criteria pass; not yet executed
  should_pass_rate: 80%  # At least 4 of 5 SHOULD criteria pass
  could_pass_rate: 0%    # Optional, no minimum
  
  overall_pass:
    condition: "must_pass_rate == 100% AND should_pass_rate >= 80%"
    then: "Review fresh dry-run manifest and permission before explicit publication; Round 1 cannot promote"
    else: "Iterate (max 3 attempts) or escalate"

# ─────────────────────────────────────────────────────────────
# VALIDATION MATRIX
# ─────────────────────────────────────────────────────────────
validation_matrix:
  - { criterion: AC-M01, test_type: file_existence, automated: true, human_review: false }
  - { criterion: AC-M02, test_type: structure_validation, automated: true, human_review: false }
  - { criterion: AC-M03, test_type: line_count, automated: true, human_review: false }
  - { criterion: AC-M04, test_type: content_check, automated: true, human_review: false }
  - { criterion: AC-M05, test_type: pattern_match, automated: true, human_review: false }
  - { criterion: AC-M06, test_type: yaml_parse, automated: true, human_review: false }
  - { criterion: AC-M07, test_type: pattern_match, automated: true, human_review: false }
  - { criterion: AC-M08, test_type: structure_validation, automated: true, human_review: true }
  - { criterion: AC-M09, test_type: content_comparison, automated: true, human_review: false }
  - { criterion: AC-M10, test_type: content_comparison, automated: true, human_review: false }
  - { criterion: AC-M11-M15, test_type: temporary_project_safety, automated: true, human_review: true }
  - { criterion: AC-M16, test_type: evidence_review, automated: partial, human_review: true }
  - { criterion: AC-S01-S04, test_type: content_analysis, automated: partial, human_review: true }
  - { criterion: AC-C01-C03, test_type: manual_review, automated: false, human_review: true }
```

## Round 1 Design Application and Handoff

Derived from the existing meta metadata template's identity, interface, acceptance,
dependencies, scenario, and evaluation sections; historical version fields and
the separate version-history file remain unchanged. Current criteria above
supersede earlier DAG/model-hint requirements, not historical claims.

### Baseline Resource Review

- Initial production/candidate path inventories match: 29 files, including all
  14 subtype/metadata templates and 14 reference files. No resource removals proposed.
- Preexisting tracked content differences in the entry and seven templates are
  preserved except explicitly scoped policy/delta edits. Candidate is not blindly
  refreshed from production. All unrelated dirty knowledge packages remain untouched.
- New resources: validator, publisher, and validation/publication reference.
- Future publication must capture/review baseline hashes and trusted managed hashes.
  This Round 1 records design, not a fabricated validation/publication receipt.

### Selected Lesson Mapping

- Scoped lesson: x-ipe-meta-skill-creator / LL-001.
- Observed gap: resource created directly in production after merge bypassed candidate.
- Candidate safeguards: complete manifest; candidate-self links; managed/removal guards;
  post-swap byte parity; no post-merge resource writes.
- Planned verification: missing self resource rejected; complete resource publication;
  unmanaged protection; byte parity.
- Disposition: selected for this candidate; historical `raw` remains unchanged.
  Not applied or verified.

LL-001 has historical evidence but no modern validity/expiry record. Selection is
based on its verified resource-bypass cause and this safety scope, not assumed
freshness. No historical migration, date reset, pruning, or applied claim occurs.

### Scenarios for Rounds 2–3 (Planned, Not Executed)

| Scenario | Expected evidence |
| --- | --- |
| New skill | Empty baseline/managed maps; valid tool contract without task routing fields; dry-run no writes, explicit publish complete bytes |
| Small existing update | Preserve unchanged resources and metadata; targeted delta; trusted manifest; cosmetic reviewer exception only when semantics unchanged |
| Missing resource | Self production link must fail against candidate even if production still has that resource; external root links checked separately |
| Body boundary | 999/1000 pass, 1001 fail, frontmatter excluded, blank lines counted, LF/CRLF and final-newline variants; malformed frontmatter/identity fail |
| Interrupted merge | Fault hook at staged/backed_up/installed; exceptions roll back; process interruption leaves journal/lock for explicit recovery; verify before/after bytes |
| Concurrent modified target | Baseline drift, between-stage mutation, noncooperating swap changes rejected; recovery refuses to overwrite new edits |
| Deletion and unmanaged protection | Exact removal review required; managed clean removal allowed; dirty/unmanaged/deleted target changes blocked; no recursive production deletion |
| Path and CLI safety | Traversal, symlink ancestors/resources, hard links, special nodes, wrong-name target rejected; JSON receipts and nonzero failure status |
| Freshness and lessons | Candidate hash mutation invalidates evidence; failed publish cannot mark lesson applied; history unchanged until successful promotion |

### Next Gate

Independent Round 2 reflection must review parser coverage, ownership provenance,
filesystem fault/recovery behavior, lifecycle/config compatibility, and all retained
template differences. Generate tests then execute only in temporary projects in
Round 3. Round 4 evaluates must/should results before any promotion decision.

## TASK-6750 single-loop delivery revision

Published after deterministic validation, bounded workflow safety review, and real manifest-safe publication; prior metadata above remains version history.

- Current revision: `21f6be920a7568c8a1b3e2a9e39bda04d0152c20de10477290c6acfb972e2dc1`
- Previous revision: `9970a327b4f64069db1ffb96fff8d89ae99af5cb198ec2bd718c5b3ba6066d32`
- Evidence: `single-loop-TASK-6750.json`, `publication-receipt-TASK-6750.json`, `validation-receipt-TASK-6750.json`.
- Same-loop delivery/default risk-based verification; unchanged resources and protected bytes retained.
- Token/latency savings not measured; no live-agent efficacy claim.
