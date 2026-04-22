# End-User Human Representative Examples

## Example 1: Direct answer (single unit)

**Input**
```yaml
message_context:
  source: human
  task_id: "TASK-770"
  workflow_name: "EPIC-047"
  downstream_context: "EPIC-047 is intended to stand alone"
  messages:
    - content: "Should we keep the new feature standalone instead of folding it into EPIC-044?"
human_shadow: false
```

**Expected Output**
```yaml
operation_output:
  success: true
  result:
    instruction_units:
      - disposition: answer
        content: "Keep it standalone. EPIC-047 defines a new capability rather than refining EPIC-044."
        rationale_summary: "The requirement history already established this as a separate epic."
        depends_on: []
        suggested_skills: []
    execution_plan:
      strategy: "sequential"
      groups: [[0]]
      rationale: "Single unit — no parallelism needed."
    confidence: 0.88
    fallback_required: false
  errors: []
```

## Example 2: Clarification (single unit)

**Input**
```yaml
message_context:
  source: human
  task_id: "TASK-771"
  workflow_name: "EPIC-047"
  downstream_context: "No concrete scope supplied"
  messages:
    - content: "Make it smarter."
human_shadow: false
```

**Expected Output**
```yaml
operation_output:
  success: true
  result:
    instruction_units:
      - disposition: clarification
        content: "What kind of improvement do you want: better disposition selection, human-shadow fallback, or memory beyond v1 scope?"
        rationale_summary: "The request is too broad to change implementation safely."
        depends_on: []
        suggested_skills: []
    execution_plan:
      strategy: "sequential"
      groups: [[0]]
      rationale: "Single unit — no parallelism needed."
    confidence: 0.74
    fallback_required: false
  errors: []
```

## Example 3: Pass through (single unit)

**Input**
```yaml
message_context:
  source: human
  task_id: "TASK-772"
  workflow_name: "EPIC-047"
  downstream_context: "The worker agent owns the live execution status"
  messages:
    - content: "Where are we in the current implementation task?"
human_shadow: false
```

**Expected Output**
```yaml
operation_output:
  success: true
  result:
    instruction_units:
      - disposition: pass_through
        content: "I should let the downstream implementation agent answer that status question directly."
        rationale_summary: "The downstream agent has the freshest execution context."
        depends_on: []
        suggested_skills: []
    execution_plan:
      strategy: "sequential"
      groups: [[0]]
      rationale: "Single unit — no parallelism needed."
    confidence: 0.86
    fallback_required: false
  errors: []
```

## Example 4: Multiple independent units — parallel execution

**Input**
```yaml
message_context:
  source: human
  task_id: "TASK-850"
  workflow_name: "EPIC-049"
  downstream_context: "KB project with multiple features"
  messages:
    - content: "Update the DAO skill to add parallelism, and also fix the sidebar CSS that's broken on mobile"
human_shadow: false
```

**Expected Output**
```yaml
operation_output:
  success: true
  result:
    instruction_units:
      - disposition: instruction
        content: "Update DAO skill to add parallelism-awareness for multi-unit execution plans."
        rationale_summary: "Skill update targets x-ipe-assistant-user-representative-Engineer — isolated from UI code."
        depends_on: []
        suggested_skills:
          - skill_name: "x-ipe-meta-skill-creator"
            match_strength: "strong"
            reason: "Updating an existing skill"
            execution_steps:
              - phase: "1. Validate"
                step: "1.1 Load existing skill"
      - disposition: instruction
        content: "Fix sidebar CSS for mobile responsiveness."
        rationale_summary: "Bug fix targets frontend CSS — no overlap with skill files."
        depends_on: []
        suggested_skills:
          - skill_name: "x-ipe-task-based-bug-fix"
            match_strength: "strong"
            reason: "CSS bug on mobile viewport"
            execution_steps:
              - phase: "1. Diagnose"
                step: "1.1 Reproduce and identify root cause"
    execution_plan:
      strategy: "parallel"
      groups: [[0, 1]]
      rationale: "Units target different domains (skill files vs frontend CSS) with no shared files or data dependencies. Safe to run concurrently."
    confidence: 0.82
    fallback_required: false
  errors: []
```

**Agent Consumption:**
```
# execution_plan.strategy = "parallel", groups = [[0, 1]]
# → Launch BOTH units concurrently as background sub-agents:
#   Agent A: TASK-851 (skill update via x-ipe-meta-skill-creator)
#   Agent B: TASK-852 (bug fix via x-ipe-task-based-bug-fix)
# → Wait for both to complete
```

## Example 5: Multiple dependent units — sequential execution

**Input**
```yaml
message_context:
  source: human
  task_id: "TASK-860"
  workflow_name: "EPIC-049"
  downstream_context: "Need new API endpoint then UI to consume it"
  messages:
    - content: "Add a KB export API endpoint, then build a UI export button that calls it"
human_shadow: false
```

**Expected Output**
```yaml
operation_output:
  success: true
  result:
    instruction_units:
      - disposition: instruction
        content: "Implement KB export API endpoint (backend route + service logic)."
        rationale_summary: "Backend endpoint must exist before UI can call it."
        depends_on: []
        suggested_skills:
          - skill_name: "x-ipe-task-based-code-implementation"
            match_strength: "strong"
            reason: "New backend feature implementation"
            execution_steps:
              - phase: "1. Implement"
                step: "1.1 Write tests then code"
      - disposition: instruction
        content: "Build UI export button that calls the new KB export endpoint."
        rationale_summary: "UI depends on the API endpoint from unit 0."
        depends_on: [0]
        suggested_skills:
          - skill_name: "x-ipe-task-based-code-implementation"
            match_strength: "strong"
            reason: "Frontend feature consuming new API"
            execution_steps:
              - phase: "1. Implement"
                step: "1.1 Write tests then code"
    execution_plan:
      strategy: "sequential"
      groups: [[0], [1]]
      rationale: "Unit 1 (UI button) calls the API endpoint created by unit 0. Must complete backend first."
    confidence: 0.80
    fallback_required: false
  errors: []
```

## Example 6: Mixed execution — some parallel, some sequential

**Input**
```yaml
message_context:
  source: human
  task_id: "TASK-870"
  workflow_name: "EPIC-049"
  messages:
    - content: "Fix the sidebar drag-drop bug, update the README, and then run full acceptance tests"
human_shadow: false
```

**Expected Output**
```yaml
operation_output:
  success: true
  result:
    instruction_units:
      - disposition: instruction
        content: "Fix sidebar drag-drop bug."
        rationale_summary: "Bug fix in sidebar.js — independent of documentation."
        depends_on: []
        suggested_skills:
          - skill_name: "x-ipe-task-based-bug-fix"
            match_strength: "strong"
            reason: "Sidebar drag-drop broken"
      - disposition: instruction
        content: "Update README with latest KB feature documentation."
        rationale_summary: "Documentation update — independent of sidebar code."
        depends_on: []
        suggested_skills:
          - skill_name: "x-ipe-tool-readme-updator"
            match_strength: "strong"
            reason: "README update (tool skill, invoked via feature-closing)"
      - disposition: instruction
        content: "Run full acceptance tests after bug fix and docs are complete."
        rationale_summary: "Tests should verify the final state after all changes."
        depends_on: [0, 1]
        suggested_skills:
          - skill_name: "x-ipe-task-based-feature-acceptance-test"
            match_strength: "strong"
            reason: "Full test suite execution"
    execution_plan:
      strategy: "mixed"
      groups: [[0, 1], [2]]
      rationale: "Bug fix (unit 0) and README (unit 1) are independent — run in parallel. Acceptance tests (unit 2) depend on both completing first."
    confidence: 0.85
    fallback_required: false
  errors: []
```

**Agent Consumption:**
```
# execution_plan.strategy = "mixed", groups = [[0, 1], [2]]
# → Group 1: Launch unit 0 and unit 1 in parallel (background sub-agents)
# → Wait for both to complete
# → Group 2: Run unit 2 (acceptance tests)
```
