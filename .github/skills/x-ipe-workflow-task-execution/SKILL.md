---
name: x-ipe-workflow-task-execution
description: Orchestrates development task lifecycle through 6-step workflow. Coordinates skills for planning, execution, closing, and routing. Use when "implement feature", "fix bug", "create PR", "design architecture", "set up project". Triggers on requests like "implement feature", "fix bug", "refactor code", "set up project".
---

# Task Execution Guideline

## Purpose

Orchestrate a multi-skill workflow for development tasks by:

1. **Plan** - Match requests to task-based skills and create tasks on board
2. **Verify** - Check prerequisites via Global DoR gate
3. **Execute** - Load and run task-based skills for core work
4. **Close** - Update boards via category-based skill loading
5. **Validate** - Confirm completion via Global DoD checks
6. **Route** - Chain to next task if auto-proceed enabled

---

## Important Notes

BLOCKING: Tasks MUST be created on task-board.md BEFORE any work begins. Step 2 will reject tasks not found on the board.

CRITICAL: This skill does NOT implement task logic itself — it coordinates task-based skills and category skills.

MANDATORY: NEVER use `manage_todo_list` (VS Code internal) as substitute for task-board.md (project tracking).

**Note:** If Agent does not have skill capability, go to `.github/skills/` folder to learn skills. SKILL.md is the entry point for each skill.

---

## Input Parameters

```yaml
input:
  # Task Data Model - Core fields (set during planning)
  task:
    task_id: "TASK-XXX"
    task_based_skill: "{task_based_skill}"
    task_description: "{description, max 50 words}"
    category: "{derived from task-based skill} | Standalone"
    role_assigned: "{agent_nickname}"
    status: "pending | in_progress | blocked | deferred | completed | cancelled"
    last_updated: "{MM-DD-YYYY HH:MM:SS}"

  # Execution fields (set by task-based skill)
  execution:
    next_task_based_skill: "{task_based_skill} | null"
    require_human_review: true | false
    auto_proceed: true | false
    task_output_links: ["{links}"] | null
    dynamic_attributes: {}  # Fully dynamic per task-based skill

  # Git strategy (read from .x-ipe.yaml at workflow start)
  git:
    strategy: "main-branch-only | dev-session-based"  # from .x-ipe.yaml git.strategy (default: dev-session-based)
    main_branch: "{auto-detected}"                     # auto-detected from git, overridable via .x-ipe.yaml git.main-branch

  # Closing fields (set by category skill)
  closing:
    category_level_change_summary: "{summary, max 100 words} | null"
```

### Git Strategy

BLOCKING: At the start of every workflow execution, read `.x-ipe.yaml` from project root to determine `git.strategy` and `git.main-branch`. If `.x-ipe.yaml` does not exist or `git.strategy` is not specified, default to `dev-session-based`. If `git.main-branch` is not specified, auto-detect the main branch from git (see Step 2 procedure). Pass these values to all task-based skills that interact with git.

| Strategy | Branch Model | PR Required? | Description |
|----------|-------------|--------------|-------------|
| `main-branch-only` | Work directly on main branch | No | All commits go to main. No feature branches created. |
| `dev-session-based` | `dev/{nickname}` branch per developer | Yes, on feature close | Each developer works on their own persistent branch. PR to main when a feature is closed. |

**Rules by strategy:**

**`main-branch-only`:**
- Do NOT create any branches
- All commits go directly to the main branch
- No PRs needed — code lands on main immediately
- `git push` pushes to main

**`dev-session-based`:**
- On first task execution, check if `dev/{nickname}` branch exists
  - If not → create it from main: `git checkout -b dev/{nickname}`
  - If exists → switch to it: `git checkout dev/{nickname}`
- All work happens on this branch
- On feature close → push branch, create PR targeting main
- Branch persists across features (not deleted after PR)

### Category Derivation

BLOCKING: Category is read from the skill's own Output Result section (`category` field). Do NOT hardcode category mappings.

**Auto-discovery rule:** Load `.github/skills/x-ipe-task-based-{name}/SKILL.md` → read `category` from Output Result YAML block.

### Category to Closing Skill Mapping

| Category | Closing Skill | Required? |
|----------|--------------|-----------|
| feature-stage | x-ipe+feature+feature-board-management | Yes |
| ideation-stage | (none) | N/A |
| requirement-stage | (none) | N/A |
| code-refactoring-stage | x-ipe+feature+quality-board-management | No (optional) |
| Standalone | (none) | N/A |

### Task States

| State | Terminal? | Description |
|-------|-----------|-------------|
| `pending` | No | Created, waiting to start |
| `in_progress` | No | Currently being worked on |
| `blocked` | No | Waiting for dependency |
| `deferred` | No | Human paused |
| `completed` | Yes | Successfully done |
| `cancelled` | Yes | Stopped |

### Valid State Transitions

```
pending → in_progress
in_progress → completed | blocked | deferred | cancelled
blocked → in_progress
deferred → in_progress
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>Task Exists on Board</name>
    <verification>Task {task_id} found in Active Tasks section of x-ipe-docs/planning/task-board.md</verification>
    <on_failure>STOP, return to Step 1 to create task on board</on_failure>
  </checkpoint>
  <checkpoint required="true">
    <name>Valid Starting Status</name>
    <verification>Task status is pending or blocked</verification>
    <on_failure>STOP, log "Task {task_id} has invalid status: {status}"</on_failure>
  </checkpoint>
  <checkpoint required="true">
    <name>Git Repository Initialized</name>
    <verification>Project root is a git repository (invoke x-ipe-tool-git-version-control skill if needed)</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Git Strategy Resolved</name>
    <verification>Read .x-ipe.yaml git.strategy; agent is on correct branch per strategy rules</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Execution Flow Summary

| Step | Name | Action | Mandatory Output | Next Step |
|------|------|--------|------------------|-----------|
| 1 | Planning | Match request, create task(s) on board | Tasks visible on task-board.md | → Step 2 |
| 2 | Global DoR | Verify prerequisites | All checks pass | → Step 3 (pass) or STOP (fail) |
| 3 | Execute | Load task-based skill, do work | Skill output collected | → Step 4 |
| 4 | Closing | Load category skills, update boards | Boards updated | → Step 5 |
| 5 | Global DoD | Validate, output summary | Summary displayed | → Step 6 (pass) or STOP (review) |
| 6 | Routing | Check auto_proceed, next task or STOP | Next action decided | → Step 2 (next) or END |

BLOCKING: Step 1 → Step 2: task must be created on task-board.md.
BLOCKING: Step 3 → Step 4: x-ipe+all+task-board-management skill must be loaded.
BLOCKING: Step 4 → Step 5: task-board.md must be updated.

---

## Execution Procedure

```xml
<procedure name="x-ipe-workflow-task-execution">
  <execute_dor_checks_before_starting/>
  <schedule_dod_checks_with_sub_agent_before_starting/>

  <step_1>
    <name>Task Planning</name>
    <trigger>Receive work request from human or system</trigger>
    <actions>
      1. Match request to task-based skill using auto-discovery (scan `.github/skills/x-ipe-task-based-*/SKILL.md` descriptions)
         See references/examples.md for request matching patterns.
      2. Derive category from skill's Output Result `category` field
      3. Check task:
         - IF task not exists → Create with status: pending
         - ELSE IF exists AND assigned to you → Continue
         - ELSE → STOP
      4. MANDATORY: Load x-ipe+all+task-board-management skill to create/update tasks on board
         → This step CANNOT be skipped
         → Tasks MUST appear on board BEFORE proceeding to Step 2
      5. IF task-based skill defines next_task_based_skill → Create ALL chained tasks upfront
      6. VERIFICATION: Confirm all tasks are visible on task board before proceeding
    </actions>
    <output>Task Data Model with core fields populated AND tasks created on board</output>
    <gate>All tasks visible on task-board.md</gate>
  </step_1>

  <step_2>
    <name>Check Global DoR</name>
    <actions>
      GATE CHECK: This step validates that Step 1 was completed correctly.

      1. Read task board at x-ipe-docs/planning/task-board.md
      2. Search for {task_id} in Active Tasks section
      3. IF task NOT found:
         → STOP execution
         → Log: "Task {task_id} not found on board. Returning to Step 1."
         → Return to Step 1 and create task on board
      4. IF task found but status is not pending/blocked:
         → STOP execution
         → Log: "Task {task_id} has invalid status for starting: {status}"
      5. Verify git repository:
         IF not a git repository:
           CALL x-ipe-tool-git-version-control skill: operation=init
           CALL x-ipe-tool-git-version-control skill: operation=create_gitignore

      6. Read git strategy from .x-ipe.yaml:
         → Read .x-ipe.yaml from project root (if file exists)
         → Set git.strategy = git.strategy (default: "dev-session-based" if not specified or file missing)
         → Set git.main_branch:
           IF .x-ipe.yaml specifies git.main-branch → use that value
           ELSE → auto-detect: run `git remote show origin` to find HEAD branch,
                  or fallback to `git symbolic-ref refs/remotes/origin/HEAD` → parse branch name,
                  or fallback to checking if `main` or `master` branch exists locally

      7. Apply git strategy:
         IF git.strategy == "main-branch-only":
           → Ensure on main branch: git checkout {main_branch}
           → Do NOT create any other branches
         ELSE IF git.strategy == "dev-session-based":
           → Check if branch dev/{nickname} exists
           → IF not exists: git checkout -b dev/{nickname} (from main)
           → IF exists: git checkout dev/{nickname}
           → Pull latest: git pull origin dev/{nickname} (ignore if remote doesn't exist yet)
    </actions>
    <on_failure>STOP and report missing prerequisites</on_failure>
    <on_success>Transition task status: pending → in_progress</on_success>
    <gate>All DoR checkpoints pass</gate>
  </step_2>

  <step_3>
    <name>Task Work Execution</name>
    <actions>
      1. Load task-based skill: x-ipe-task-based-{task_based_skill}
      2. Pass Task Data Model to skill
      3. Check task-based skill DoR (defined in skill)
      4. Execute core work (defined in skill)
      5. Check task-based skill DoD (defined in skill)
      6. Collect skill output into Task Data Model
    </actions>
    <skill_output_contract>
      Each task-based skill MUST return:
        status: {new_status}
        next_task_based_skill: {task_based_skill} | null
        require_human_review: true | false
        task_output_links: [{links}] | null
        {dynamic_attributes}: per skill definition
    </skill_output_contract>
    <output>Task Data Model updated with execution results</output>
    <gate>Skill output collected</gate>
  </step_3>

  <step_4>
    <name>Category Closing</name>
    <actions>
      1. MANDATORY: Load skill x-ipe+all+task-board-management
         → Update task status on board
         → Pass Task Data Model

      2. IF category != "Standalone":
         TRY:
           → Load skill @{category}+{category-skill-name}
           → Pass Task Data Model
           → Collect category_level_change_summary
         CATCH SkillNotFound:
           → Log: "No category-level skill found for {category}, skipping"
           → Continue without error (category_level_change_summary = null)
    </actions>
    <category_skill_mapping>
      Refer to "Category to Closing Skill Mapping" in the Category Derivation section above.
    </category_skill_mapping>
    <note>If category skill not found, execution continues without error. Category-level change summary will be null if skipped.</note>
    <output>category_level_change_summary added to Task Data Model (or null)</output>
    <gate>task-board.md updated</gate>
  </step_4>

  <step_5>
    <name>Check Global DoD</name>
    <actions>
      1. Validate:
         - Task status updated on task board
         - Category-level changes committed (if applicable)
         - All task-based skill DoD met
         - Changes committed to git (if files were created/modified)

      2. Git Commit Check:
         IF task_output_links is NOT empty AND files were created/modified:
           CALL x-ipe-tool-git-version-control skill: operation=add, files=null (stage all)
           CALL x-ipe-tool-git-version-control skill: operation=commit, task_data={task_id, task_description, feature_id}
         OPTIONAL: IF auto_push = true:
           CALL x-ipe-tool-git-version-control skill: operation=push

      3. Human Review Check:
         IF require_human_review = true AND auto_proceed = false AND global_auto_proceed = false:
           → Output summary and STOP for human review
         ELSE:
           → Skip human review (auto-proceed overrides)
    </actions>
    <output_template>
      > Task ID: {task_id}
      > Task-Based Skill: {task_based_skill}
      > Description: {task_description}
      > Category: {category}
      > Assignee: {role_assigned}
      > Status: {status}
      > Category Changes: {category_level_change_summary}
      > Require Human Review: {require_human_review}
      > Task Output Links: {task_output_links}
      > Auto Proceed: {auto_proceed}
      > --- Dynamic Attributes ---
      > {attr_1}: {value}
    </output_template>
    <gate>All DoD checkpoints pass</gate>
  </step_5>

  <step_6>
    <name>Task Routing</name>
    <actions>
      1. Read Global Auto-Proceed setting from task-board.md (Global Settings section)
         → Default to false if not found
      2. Set effective_auto_proceed = auto_proceed OR global_auto_proceed

      IF effective_auto_proceed = true AND next_task_based_skill EXISTS:
        → Find next task on board (already created in Step 1)
        → Start execution from Step 2
      ELSE:
        → STOP (wait for human)
    </actions>
    <gate>Routing decision made</gate>
  </step_6>
</procedure>
```

---

## Output Result

```yaml
output:
  task_id: "{task_id}"
  task_based_skill: "{task_based_skill}"
  task_description: "{task_description}"
  category: "{category}"
  role_assigned: "{role_assigned}"
  status: "completed | blocked | deferred"
  category_level_change_summary: "{summary} | null"
  require_human_review: true | false
  task_output_links: ["{links}"] | null
  auto_proceed: true | false
  next_task_based_skill: "{task_based_skill} | null"
  dynamic_attributes: {}  # Per task-based skill
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Task Board Updated</name>
    <verification>Task status updated on task-board.md</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Category Changes Committed</name>
    <verification>Category-level changes committed if applicable</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Task-Based Skill DoD Met</name>
    <verification>All task-based skill Definition of Done criteria satisfied</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Git Changes Committed</name>
    <verification>All created/modified files committed to git</verification>
  </checkpoint>
</definition_of_done>
```

---

## Task-Based Skills Auto-Discovery

BLOCKING: Do NOT maintain a hardcoded registry. Skills are auto-discovered.

**Discovery rule:**
1. Scan `.github/skills/x-ipe-task-based-*/SKILL.md`
2. Each skill's Output Result YAML declares: `category`, `next_task_based_skill`, `require_human_review`
3. Each skill's `description` in frontmatter contains trigger keywords for request matching

**Request matching:**
1. Read the `description` field from each `x-ipe-task-based-*/SKILL.md` frontmatter
2. Match user request against trigger keywords (e.g., "fix bug" matches `x-ipe-task-based-bug-fix`)
3. See [references/examples.md](references/examples.md) for common request-to-skill patterns

> **Note:** When Auto-Proceed is enabled (global or task-level), `require_human_review` is skipped regardless of the skill's default.

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| `TASK_NOT_ON_BOARD` | Task not found on task-board.md | Return to Step 1, create task on board |
| `INVALID_STATUS` | Task status not valid for starting | STOP, log invalid status |
| `SKILL_NOT_FOUND` | Task-based or category skill missing | Fail for task-based skills; skip for optional category skills |
| `GIT_NOT_INITIALIZED` | No git repository | Invoke x-ipe-tool-git-version-control skill to init |
| `DOR_FAILED` | Prerequisites not met | STOP, report missing prerequisites |

---

## Templates

- `templates/task-record.yaml` - Task data template
- `templates/task-board.md` - Task tracking board

---

## Examples

See [references/examples.md](references/examples.md) for full workflow examples and request matching patterns.
