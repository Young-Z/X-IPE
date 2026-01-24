# Copilot Instructions

## Before You Start
**When:** Starting a new conversation
**Then:**
1. **Generate a random nickname** from this pool:
   - Nova, Echo, Flux, Bolt, Sage, Pixel, Cipher, Spark, Drift, Pulse, Vex, Atom, Onyx, Rune, Zephyr, Quill, Ember, Frost, Haze, Ink
2. **Validate nickname against task board:**
   - Check `docs/planning/task-board.md` Active Tasks section
   - If another session has `🔄 in_progress` tasks with the same nickname → pick a different name from the pool
   - If the in_progress task was started by your current session (same context) → keep the name
   - Repeat until you find an unused name
3. Introduce yourself: "Hi, I'm [nickname]"
4. This nickname is your assignee identifier
5. Check for open tasks assigned to you
6. Only work on tasks assigned to you or unassigned

**When:** Before starting any thinking
**Then:**

1. Check if Agent Model have capability to use Anthropic skills protocol.
2. If yes, load skill: `task-execution-guideline`.
2. If no, do following things:
   - read files under `.github/skills/task-execution-guideline/` folder to understand task execution guideline.
   - **Important:** each type of task mentioned in the guideline must have a corresponding skill file under `.github/skills/` folder. And SKILL.md file is the entry point to understand each skill.

---

## ⚠️ CRITICAL: Task Board is THE Source of Truth

**The task board (`docs/planning/task-board.md`) is MANDATORY for ALL work.**

### Before ANY Work:
1. **Create task on task-board.md** using `task-board-management` skill
2. **Verify task exists** on board (Step 2 of task-execution-guideline)
3. **Only then** proceed to actual work

### After Completing Work:
1. **Update task-board.md** - move task to Completed section
2. **Update Quick Stats** - increment completed count

### ⛔ NEVER:
- Use `manage_todo_list` as a substitute for task-board.md (that's VS Code internal only)
- Start work without a task ID on the board
- Complete work without updating the board

---

## ⚠️ STRICT: Task Matching & Skill Enforcement

### Mandatory Task Classification

**Before doing ANY work**, the agent MUST:

1. **Classify the work** into a Task Type from the table below
2. **Create task on task-board.md** via `task-board-management` skill ← **BLOCKING**
3. **Load the corresponding skill** from `.github/skills/` folder
4. **Follow the skill's execution procedure** step-by-step
5. **Complete the skill's Definition of Done (DoD)** before marking complete
6. **Update task-board.md** with completion status ← **MANDATORY**

### Task Type Identification

## Task Types Registry

| Task Type | Skill | Category | Next Task | Human Review |
|-----------|-------|----------|-----------|--------------|
| Ideation | `task-type-ideation` | ideation-stage | Idea Mockup | No |
| Idea Mockup | `task-type-idea-mockup` | ideation-stage | Requirement Gathering | No |
| Share Idea | `task-type-share-idea` | Standalone | - | Yes |
| Requirement Gathering | `task-type-requirement-gathering` | requirement-stage | Feature Breakdown | Yes |
| Feature Breakdown | `task-type-feature-breakdown` | requirement-stage | Feature Refinement | Yes |
| Feature Refinement | `task-type-feature-refinement` | feature-stage | Technical Design | Yes |
| Technical Design | `task-type-technical-design` | feature-stage | Test Generation | Yes |
| Test Generation | `task-type-test-generation` | feature-stage | Code Implementation | No |
| Code Implementation | `task-type-code-implementation` | feature-stage | Feature Closing | No |
| Human Playground | `task-type-human-playground` | Standalone | - | Yes |
| Feature Closing | `task-type-feature-closing` | feature-stage | User Manual | No |
| Bug Fix | `task-type-bug-fix` | Standalone | - | Yes |
| Code Refactor | `task-type-code-refactor` | Standalone | - | Yes |
| Change Request | `task-type-change-request` | Standalone | Feature Refinement OR Feature Breakdown | Yes |
| Project Initialization | `task-type-project-init` | Standalone | Dev Environment | No |
| Dev Environment | `task-type-dev-environment` | Standalone | - | No |
| User Manual | `task-type-user-manual` | Standalone | - | Yes |

### 🛑 STOP AND THINK: Pre-Flight Checklist

**Before touching ANY code or making ANY changes, ask yourself:**

```
1. What task type is this? → Check registry table above
2. Did I create a task on task-board.md? → If NO, STOP and create it
3. Did I load the corresponding skill? → If NO, STOP and load it
4. Am I following the skill's procedure? → If NO, STOP and read it
```

**Common Mistakes to Avoid:**
- User says "refactor this" → You must use `task-type-code-refactor` skill, NOT just start coding
- User says "fix this bug" → You must use `task-type-bug-fix` skill, NOT just fix it
- User says "add this feature" → You must identify the right task type first

### ⚠️ DO NOT Skip Skills

**Forbidden Actions:**
- ❌ Starting work without creating task on task-board.md first
- ❌ Using `manage_todo_list` as a substitute for task-board.md
- ❌ Completing work without updating task-board.md
- ❌ Jumping straight to code without checking for existing tests
- ❌ Fixing bugs without writing a failing test first
- ❌ Implementing features without reading technical design
- ❌ Making changes without following the skill's execution procedure
- ❌ Refactoring code without using `task-type-code-refactor` skill

**Required Actions:**
- ✅ Always create task on task-board.md BEFORE starting work
- ✅ Always identify task type first
- ✅ Always load and follow the corresponding skill
- ✅ Always check prerequisites (DoR) before starting
- ✅ Always complete Definition of Done (DoD) before finishing
- ✅ Always update task-board.md AFTER completing work

---

## Human Interaction

### Approval Recognition

- Do NOT assume approval unless human explicitly says: `approve`, `confirmed`, `lgtm`, `looks good`, `go ahead`, `proceed`
- If human gives feedback without approval → keep task in current state
- When in doubt, ask: "Do you approve this to proceed?"

---

## Development Principles

Always follow:
1. **SOLID** - Design principles
3. **YAGNI** - You Aren't Gonna Need It
4. **KISS** - Keep It Simple

---

## Skill Management

### Creating, Updating, or Validating X-IPE Skills

**When:** Creating a new skill, updating an existing skill, or validating skill structure
**Then:** Always use the `x-ipe-skill-creator` skill

```
1. Load skill: `x-ipe-skill-creator`
2. Follow the skill creation process defined in the skill
3. Use appropriate template based on skill type:
   - Task Type → templates/task-type-skill.md
   - Skill Category → templates/skill-category-skill.md
   - Tool Skill → TBD
4. Validate against skill-creator checklist before completing
```

