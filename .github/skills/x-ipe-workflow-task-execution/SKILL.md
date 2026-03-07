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

IMPORTANT: When `process_preference.auto_proceed == "auto"`, NEVER stop to ask the human. Instead, call `x-ipe-dao-end-user-representative` to get the answer. The DAO skill acts as the human representative and will provide the guidance needed to continue. When `manual` or `stop_for_question`, always wait for human feedback before proceeding to the next task.

---

## Input Parameters

```yaml
input:
  task:
    task_id: "TASK-XXX"
    task_based_skill: "{task_based_skill}"
    task_description: "{description, max 50 words}"
    category: "{derived from task-based skill} | Standalone"
    role_assigned: "{agent_nickname}"
    status: "pending | in_progress | blocked | deferred | completed | cancelled"
    last_updated: "{MM-DD-YYYY HH:MM:SS}"

  execution_mode: "free-mode | workflow-mode"
  workflow:
    name: "N/A"

  execution:
    next_task_based_skill: "{task_based_skill} | null"
    process_preference:
      auto_proceed: "manual | auto | stop_for_question"  # default: manual
    task_output_links: ["{links}"] | null
    dynamic_attributes: {}

  git:
    strategy: "main-branch-only | dev-session-based"
    main_branch: "{auto-detected}"

  closing:
    category_level_change_summary: "{summary, max 100 words} | null"
```

### Input Initialization

```xml
<input_init>
  <!-- Task fields (resolved during Step 1 Planning) -->
  <field name="task.task_id" source="x-ipe+all+task-board-management (auto-generated on create)" />
  <field name="task.task_based_skill" source="Auto-discovery: match request against .github/skills/x-ipe-task-based-*/SKILL.md descriptions" />
  <field name="task.task_description" source="Summarize from human request (max 50 words)" />
  <field name="task.category" source="Read from matched skill's Output Result `category` field" />
  <field name="task.role_assigned" source="Current agent nickname" />
  <field name="task.status" source="Set to 'pending' on creation" />
  <field name="task.last_updated" source="Current timestamp on each status change" />

  <!-- Execution mode (resolved at start of Step 1) -->
  <field name="execution_mode">
    <steps>
      1. IF instruction starts with `--workflow-mode@{name}` → "workflow-mode"
      2. IF instruction starts with `--workflow-mode` (no @) → "workflow-mode"
      3. ELSE → "free-mode"
    </steps>
  </field>
  <field name="workflow.name">
    <steps>
      1. IF instruction has `--workflow-mode@{name}` → extract {name}
      2. ELSE → "N/A"
    </steps>
  </field>

  <!-- Execution fields (populated after Step 3) -->
  <field name="execution.next_task_based_skill" source="From task-based skill output" />
  <field name="execution.process_preference.auto_proceed" source="Resolved from: (a) workflow-{name}.json global.process_preference in workflow-mode, (b) CLI flag --proceed@auto or --proceed@stop-for-question in free-mode, (c) Semantic understanding from user message, (d) default: manual" />
  <field name="execution.task_output_links" source="From task-based skill output" />

  <!-- Git strategy (resolved during Step 2 DoR) -->
  <field name="git.strategy">
    <steps>
      1. Read .x-ipe.yaml from project root
      2. IF file exists AND git.strategy specified → use value
      3. ELSE → "main-branch-only"
    </steps>
  </field>
  <field name="git.main_branch">
    <steps>
      1. IF .x-ipe.yaml specifies git.main-branch → use value
      2. ELSE → auto-detect from `git remote show origin` or fallback to main/master
    </steps>
  </field>

  <!-- Closing fields (populated after Step 4) -->
  <field name="closing.category_level_change_summary" source="From category skill output (or null if skipped)" />
</input_init>
```

### Git Strategy

BLOCKING: At the start of every workflow execution, read `.x-ipe.yaml` from project root to determine `git.strategy` and `git.main-branch`. If `.x-ipe.yaml` does not exist or `git.strategy` is not specified, default to `main-branch-only`. If `git.main-branch` is not specified, auto-detect the main branch from git (see Step 2 procedure). Pass these values to all task-based skills that interact with git.

| Strategy | Branch Model | PR Required? | Description |
|----------|-------------|--------------|-------------|
| `main-branch-only` | Work directly on main branch | No | All commits go to main. No feature branches created. |
| `dev-session-based` | `dev/{git_user_name}` branch per developer | Yes, on feature close | Each developer works on their own persistent branch. PR to main when a feature is closed. |

See [references/examples.md](.github/skills/x-ipe-workflow-task-execution/references/examples.md) for detailed strategy rules and git identity validation.

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
  <checkpoint required="true">
    <name>Git Identity Valid</name>
    <verification>For dev-session-based strategy: git config user.name is NOT a placeholder ("Your Name", empty). If invalid, STOP and ask user.</verification>
    <on_failure>STOP, ask user to provide actual git user.name</on_failure>
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
| 5 | Global DoD | Validate, output summary | Summary displayed | → Step 6 (pass) or STOP (manual) |
| 6 | Routing | Resolve process_preference mode, route next | Next action decided | → Step 2 (auto) or WAIT for human (manual/stop_for_question) or END (no next task) |

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
      1. Resolve execution_mode and workflow.name from instruction prefix (see Input Initialization)
      2. Match request to task-based skill using auto-discovery (scan `.github/skills/x-ipe-task-based-*/SKILL.md` descriptions)
         See references/examples.md for request matching patterns.
      3. Derive category from skill's Output Result `category` field
      4. Check task:
         - IF task not exists → Create with status: pending
         - ELSE IF exists AND assigned to you → Continue
         - ELSE → STOP
      5. MANDATORY: Load x-ipe+all+task-board-management skill to create/update tasks on board
         → This step CANNOT be skipped
         → Tasks MUST appear on board BEFORE proceeding to Step 2
      6. IF task-based skill defines next_task_based_skill → Create ALL chained tasks upfront
      7. VERIFICATION: Confirm all tasks are visible on task board before proceeding
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

      6. Resolve git.strategy and git.main_branch (see Input Initialization)

      7. Apply git strategy:
         IF git.strategy == "main-branch-only":
           → Ensure on main branch: git checkout {main_branch}
           → Do NOT create any other branches
         ELSE IF git.strategy == "dev-session-based":
           → BLOCKING: Validate git identity first:
             Run: git config user.name AND git config user.email
             KNOWN_PLACEHOLDERS = ["Your Name", "your name", "you@example.com", ""]
             IF user.name IN KNOWN_PLACEHOLDERS OR user.email IN KNOWN_PLACEHOLDERS OR user.name is empty:
               → STOP: Ask user "Your git user.name is '{user.name}' which appears to be a placeholder. Please provide your actual name for the dev branch."
               → Do NOT proceed until user provides valid identity
               → After user provides name: run git config user.name "{provided_name}" (and git config user.email if needed)
           → Resolve dev branch name from git identity:
             Run: git config user.name (or git config user.email if empty)
             Sanitize: lowercase, spaces→hyphens, remove special chars
             Branch name: dev/{sanitized_git_user_name}
           → Check if branch dev/{git_user_name} exists
           → IF not exists: git checkout -b dev/{git_user_name} (from main)
           → IF exists: git checkout dev/{git_user_name}
           → Pull latest: git pull origin dev/{git_user_name} (ignore if remote doesn't exist yet)
    </actions>
    <on_failure>STOP and report missing prerequisites</on_failure>
    <on_success>Transition task status: pending → in_progress</on_success>
    <gate>All DoR checkpoints pass</gate>
  </step_2>

  <step_3>
    <name>Task Work Execution</name>
    <actions>
      1. Load task-based skill: x-ipe-task-based-{task_based_skill}
      2. Pass Task Data Model to skill, including execution_mode and workflow.name
      3. Check task-based skill DoR (defined in skill)
      4. Execute core work (defined in skill)
      5. Check task-based skill DoD (defined in skill)
      6. Collect skill output into Task Data Model
    </actions>
    <skill_output_contract>
      Each task-based skill MUST return:
        status: {new_status}
        next_task_based_skill: {task_based_skill} | null
        process_preference:
          auto_proceed: "{from input process_preference.auto_proceed}"
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

      3. Workflow Status Verification:
         IF execution_mode == "workflow-mode" AND completed skill's task_completion_output contains workflow_action field:
           a. Extract workflow_name and workflow_action from output
           b. READ instance/workflows/wf-{nnn}-{workflow_name}.json
           c. CHECK that actions.{workflow_action}.status is NOT "pending"
           d. IF status is "pending" → FLAG task as incomplete: "Workflow action '{workflow_action}' status not updated. Call the `update_workflow_action` tool of `x-ipe-app-and-agent-interaction` MCP server before completing."
           e. CHECK that actions.{workflow_action}.deliverables is a keyed dict (not a list). Keys must match extract tags from workflow-template.json for this action.
           f. IF workflow JSON file not found → WARN and skip (non-blocking)
         ELSE IF execution_mode == "free-mode":
           → Skip workflow status verification

      4. Human Review Check (mode-aware):
         IF process_preference.auto_proceed == "auto":
           → Skip human review, proceed directly
         ELIF process_preference.auto_proceed == "stop_for_question" OR "manual":
           → Output summary and STOP for human review
    </actions>
    <output_template>
      > Task ID: {task_id}
      > Task-Based Skill: {task_based_skill}
      > Description: {task_description}
      > Category: {category}
      > Assignee: {role_assigned}
      > Status: {status}
      > Execution Mode: {execution_mode}
      > Workflow: {workflow.name}
      > Category Changes: {category_level_change_summary}
      > Process Preference: {process_preference.auto_proceed}
      > Task Output Links: {task_output_links}
      > --- Dynamic Attributes ---
      > {attr_1}: {value}
    </output_template>
    <gate>All DoD checkpoints pass</gate>
  </step_5>

  <step_6>
    <name>Task Routing</name>
    <actions>
      1. Check with task to execute next task, can reference next_task_based_skill from Step 3 output.
      2. Wait for response based on auto_proceed condition before proceeding.
      3. Route to next task (Another iteration of task execution)

      IF process_preference.auto_proceed == "auto":
        → invoke x-ipe-dao-end-user-representative learn the context to define best next task
      ELSE (manual/stop_for_question):
        → Present next task suggestion to human and wait for instruction
    </actions>
    <constraints>
      - BLOCKING (manual/stop_for_question): Human MUST confirm or redirect before routing to next task
      - BLOCKING (auto): Proceed automatically; resolve routing ambiguity via x-ipe-dao-end-user-representative
    </constraints>
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
  execution_mode: "{execution_mode}"
  workflow:
    name: "{workflow.name}"
  category_level_change_summary: "{summary} | null"
  process_preference:
    auto_proceed: "manual | auto | stop_for_question"
  task_output_links: ["{links}"] | null
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
2. Each skill's Output Result YAML declares: `category`, `next_task_based_skill`, `process_preference.auto_proceed`
3. Each skill's `description` in frontmatter contains trigger keywords for request matching

**Request matching:**
1. Read the `description` field from each `x-ipe-task-based-*/SKILL.md` frontmatter
2. Match user request against trigger keywords (e.g., "fix bug" matches `x-ipe-task-based-bug-fix`)
3. See [references/examples.md](.github/skills/x-ipe-workflow-task-execution/references/examples.md) for common request-to-skill patterns

> **Note:** When `process_preference.auto_proceed` is `auto` or `stop_for_question`, human review at skill completion is handled by the mode-aware gate in Step 5. In `auto` mode, review is skipped entirely. In `stop_for_question` mode, review still stops for human approval.

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

## Templates & Examples

- `templates/task-record.yaml` - Task data template
- `templates/task-board.md` - Task tracking board
- [references/examples.md](.github/skills/x-ipe-workflow-task-execution/references/examples.md) - Full workflow examples, request matching patterns, and git strategy rules
