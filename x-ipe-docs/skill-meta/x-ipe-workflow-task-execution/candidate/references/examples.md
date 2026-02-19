# Task Execution Guideline - Examples

## Example: "Implement the user login feature"

### Step 1: Planning

```
Match: "implement" → Code Implementation
Category: feature-stage
Description: "Implement user login feature with authentication"

MANDATORY: Create tasks on board BEFORE proceeding
→ Load x-ipe+all+task-board-management skill
→ Create: TASK-001 (Code Implementation) - status: pending
→ Create: TASK-002 (Feature Closing) - status: pending
→ Verify all tasks appear in Active Tasks section of task-board.md
```

### Step 2: DoR

```
[pass] Read task-board.md
[pass] Find TASK-001 in Active Tasks section
[pass] Confirm status: pending (valid for starting)
[pass] Git repository initialized
→ Update TASK-001 status: pending → in_progress
```

### Step 3: Execute

```
Load: x-ipe-task-based-code-implementation
Work: Write code, tests
Output:
  status: completed
  next_task_based_skill: Feature Closing
  require_human_review: false
  task_output_links: [src/auth/login.ts, tests/auth/login.test.ts]
  feature_id: FEATURE-001
  feature_phase: Code Implementation
```

### Step 4: Closing

```
Load: x-ipe+all+task-board-management → Update TASK-001 to completed
Load: x-ipe+feature+feature-board-management → Update feature status
Output:
  category_level_change_summary: "FEATURE-001 updated to Done Code Implementation"
```

### Step 5: DoD

```
[pass] Board updated
[pass] Feature board updated
Output standard summary
```

### Step 6: Routing

```
auto_proceed = true, next_task_based_skill = Feature Closing
→ Start TASK-002 from Step 2
```

---

## Request Matching Examples

| Request Pattern | Task-Based Skill |
|-----------------|-----------|
| "ideate", "brainstorm", "refine idea", "analyze my idea" | Ideation |
| "create mockup", "visualize idea", "prototype UI", "design mockup" | Idea Mockup |
| "create architecture", "design system", "architecture diagram", "system design" | Idea to Architecture |
| "share idea", "convert to ppt", "make presentation", "export idea" | Share Idea |
| "new feature", "add feature" | Requirement Gathering |
| "break down", "split features" | Feature Breakdown |
| "refine", "clarify requirements" | Feature Refinement |
| "design", "architecture" | Technical Design |
| "implement", "code", "build" | Code Implementation |
| "playground", "demo", "test manually" | Human Playground |
| "close feature", "create PR" | Feature Closing |
| "fix bug", "not working" | Bug Fix |
| "refactor", "restructure", "split file", "clean up code", "improve code quality" | Code Refactor |
| "change request", "CR", "modify feature", "update requirement" | Change Request |
| "set up project", "initialize" | Project Initialization |
