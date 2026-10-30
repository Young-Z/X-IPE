# X-IPE Skill Creator - Examples

Concrete subtype examples for the creator's scope → candidate → verify/review →
dry-run/authorized publication → record process, all in the same agent loop by
default. Skill/tool invocation is not an agent handoff. Test results are hypothetical expected outcomes,
not execution evidence; record actual receipts outside the candidate.

---

## Example 1: Create Task-Based Skill

**Request:** "Create a skill for bug fixing"

### Step 1: Identify Skill Type

```yaml
input:
  user_request: "bug fixing"
  analysis: "Development lifecycle workflow"
  
output:
  skill_type: x-ipe-task-based
  template: templates/x-ipe-task-based.md
```

### Step 2: Gather Examples

```yaml
user_examples:
  - "Fix the login button that's not working"
  - "Debug the null pointer exception in UserService"
  - "This test is failing, can you fix it?"

trigger_patterns:
  - "fix bug"
  - "debug"
  - "failing test"
  - "not working"
```

### Step 3: Plan Resources

```yaml
resources_plan:
  templates: null
  references:
    - examples.md  # REQUIRED for x-ipe-task-based
  scripts: null
```

### Draft Metadata and Candidate in the Same Loop

**Metadata output: skill-meta.md**

```yaml
skill_name: x-ipe-task-based-bug-fix
skill_type: x-ipe-task-based
acceptance_criteria:
  must:
    - id: AC-M01
      description: Failing test written before fix
    - id: AC-M02
      description: Root cause identified
    - id: AC-M03
      description: All tests pass after fix
```

**Package output: candidate/**

```
candidate/
├── SKILL.md (x-ipe-task-based-bug-fix skill)
└── references/
    └── examples.md (bug fix examples)
```

### Review and Prepare Affected Checks in the Same Loop

**Self-review**

```yaml
gaps_found:
  - section: Definition of Ready
    issue: "Missing reproduction steps prerequisite"
    fix: "Added checkpoint: Reproduction steps documented"
```

**Prepare tests**

```yaml
test_cases:
  - id: TC-001
    source_ac: AC-M01
    scenario: Fix login button bug
    expected: Failing test exists before fix applied
```

### Steps 8-9: Run and Evaluate

```yaml
evaluation_result:
  affected_checks: passed
  independent_review: "No concrete trigger; same-loop self-review"
  unmet_recommendations: []
  overall_pass: true
```

### Publication Gate

Run the installed creator's `scripts/publish_skill.py` with the reviewed baseline,
trusted managed manifest, fresh candidate hash, and exact deletion list. Default
dry-run must be reviewed. Candidate-only scope stops at `candidate_ready`; use
`--apply` only with explicit permission and fresh evidence. Never recursively copy
a candidate into production. Verify byte parity and retain recovery evidence.

### Step 11: Cross-References

```yaml
cross_reference_checks:
  auto_discovery_fields: declared
  task_execution_guideline: verified
  status: valid
```

---

## Example 2: Create Tool Skill

**Request:** "Create a skill for generating PDF documents"

### Step 1: Identify Skill Type

```yaml
input:
  user_request: "PDF documents"
  analysis: "Utility function"
  
output:
  skill_type: x-ipe-tool
  template: templates/x-ipe-tool.md
```

### Step 2: Gather Examples

```yaml
user_examples:
  - "Convert this markdown to PDF"
  - "Extract text from PDF"
  - "Merge these PDFs together"

trigger_patterns:
  - "create PDF"
  - "extract from PDF"
  - "merge PDF"
```

### Step 3: Plan Resources

```yaml
resources_plan:
  templates:
    - pdf-template.md
  references:
    - pdf-library-docs.md
  scripts:
    - pdf-generator.py
    - pdf-extractor.py
```

### Execution Summary

```yaml
workflow_execution:
  draft: "Created skill-meta.md + candidate/ in the same loop"
  verify: "Ran affected tests (PDF generation, extraction, merge)"
  review: "Same-loop self-review; no concrete independent-review trigger"
  
publication_target: ".github/skills/x-ipe-tool-pdf/"  # Only after authorized publication
```

---

## Example 3: Create Workflow Orchestration Skill

**Request:** "Create a workflow that handles the full feature development pipeline from refinement to closing"

### Step 1: Identify Skill Type

```yaml
input:
  user_request: "full feature development pipeline"
  analysis: "Orchestrates multiple skills"
  
output:
  skill_type: x-ipe-workflow-orchestration
  template: templates/x-ipe-workflow-orchestration.md
```

### Step 2: Gather Examples

```yaml
user_examples:
  - "Run the complete feature workflow for FEAT-001"
  - "Execute the full pipeline from refinement to PR"
  - "Automate the feature development process"

trigger_patterns:
  - "full pipeline"
  - "complete workflow"
  - "feature development flow"
```

### Step 3: Plan Resources

```yaml
resources_plan:
  templates: null
  references:
    - examples.md
    - skill-registry.md  # Documents orchestrated skills
  scripts: null

orchestrated_skills:
  - x-ipe-task-based-feature-refinement
  - x-ipe-task-based-technical-design
  - x-ipe-tool-test-generation
  - x-ipe-task-based-code-implementation
  - x-ipe-task-based-feature-acceptance-test
  - x-ipe-task-based-feature-closing
```

### Draft Metadata and Candidate in the Same Loop

**Metadata output: skill-meta.md**

```yaml
skill_name: x-ipe-workflow-full-pipeline
skill_type: x-ipe-workflow-orchestration
acceptance_criteria:
  must:
    - id: AC-M01
      description: All 6 skills execute in correct order
    - id: AC-M02
      description: Data flows correctly between skills
    - id: AC-M03
      description: Failure in any skill triggers appropriate handling
  should:
    - id: AC-S01
      description: Parallel execution only for substantial independent work with a documented benefit
    - id: AC-S02
      description: Human review gates respected
```

**Package output: candidate/**

```
candidate/
├── SKILL.md (x-ipe-workflow-full-pipeline orchestration)
└── references/
    ├── examples.md
    └── skill-registry.md
```

### Skill Registry in SKILL.md

```yaml
skill_registry:
  - skill: x-ipe-task-based-feature-refinement
    phase: 1
    input: feature_id
    output: specification_path
    
  - skill: x-ipe-task-based-technical-design
    phase: 2
    input: specification_path
    output: design_path
    
  - skill: x-ipe-tool-test-generation
    phase: 3
    input: design_path
    output: test_files[]
    
  - skill: x-ipe-task-based-code-implementation
    phase: 4
    input: design_path, test_files[]
    output: implementation_files[]
    
  - skill: x-ipe-task-based-feature-acceptance-test
    phase: 5
    input: implementation_files[]
    output: acceptance_report
    
  - skill: x-ipe-task-based-feature-closing
    phase: 6
    input: acceptance_report
    output: pr_url
```

### Execution Summary

```yaml
workflow_execution:
  draft: "Created skill-meta.md + candidate/ in the same loop"
  verify: "Checked happy path, failures, data flow and preserved transitions"
  review: "Same-loop self-review; workflow artifact type alone does not trigger a reviewer"
  
publication_target: ".github/skills/x-ipe-workflow-full-pipeline/"  # Only after authorized publication
```

---

## Example 4: Update Skill from Lessons

**Scenario:** Lesson-learned captured that x-ipe-task-based-bug-fix skill misses edge case

### Pre-Step: Check Lessons

```yaml
file: x-ipe-docs/skill-meta/x-ipe-task-based-bug-fix/x-ipe-meta-lesson-learned.md

lessons:
  - id: LL-001
    status: raw
    issue: "Skill doesn't handle flaky test scenarios"
    suggestion: "Add pattern for flaky test isolation"
```

### Step 1: Read Lessons

```yaml
lesson_analysis:
  lesson_id: LL-001
  issue: "Flaky test handling missing"
  action: "Convert to acceptance criterion"
```

### Step 2: Update skill-meta.md

```yaml
acceptance_criteria:
  should:
    - id: AC-S04  # NEW
      description: Handles flaky test scenarios
      test_method: content_check
      expected: "Pattern for flaky test isolation exists"
```

### Steps 3-11: Normal Workflow

```yaml
workflow_execution:
  - "Updated candidate/ with flaky test pattern"
  - "Generated test for AC-S04"
  - "Ran tests - all passed"
  - "Merged update"
  - "Only after publication revision and relevant passing verification: settle selected lesson as applied"

Candidate-only work keeps the selected lesson mapping planned in external metadata;
it does not change historical raw records or version history. Mere reading,
drafting, or a hypothetical test result is not lesson application.
```

---

## Example 5: Skill Creation Failure and Iteration

**Request:** "Create a skill for database migrations"

### Initial Draft

Created candidate skill for database migrations in the same loop. Destructive
database writes are a concrete independent-review trigger; obtain bounded review
of backup/rollback/permission boundaries before promotion, not a reviewer per step.

### First Verification

```yaml
evaluation_result:
  overall_pass: false
  failed_tests:
    - id: TC-003
      issue: "DoR missing database connection prerequisite"
```

### Iteration 1: Fix and Re-run

```yaml
fix_applied:
  section: Definition of Ready
  change: "Added checkpoint: Database connection available"
  
action: "Rerun checks affected by the prerequisite change"
```

### Second Verification

```yaml
evaluation_result:
  overall_pass: false
  failed_tests:
    - id: TC-007
      issue: "Rollback procedure not documented"
```

### Iteration 2: Fix and Re-run

```yaml
fix_applied:
  section: Execution Procedure
  change: "Added rollback procedure steps"
  
action: "Rerun affected rollback scenarios and refresh required review evidence"
```

### Final Evaluation

```yaml
evaluation_result:
  affected_checks: passed
  independent_review: "Destructive-operation findings resolved"
  overall_pass: true

merge_target: ".github/skills/x-ipe-task-based-database-migration/"
```

---

## Summary of Examples

| Example | Skill Type | Key Learning |
|---------|------------|--------------|
| 1 | x-ipe-task-based | Candidate, review and permission boundary |
| 2 | x-ipe-tool | Tool skill with scripts and templates |
| 3 | x-ipe-workflow-orchestration | Multi-skill coordination with registry |
| 4 | Update flow | Incorporating lessons into existing skill |
| 5 | Failure iteration | How to handle test failures and iterate |
