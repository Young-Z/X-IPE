# Copilot Instructions

## Before You Start
**When:** Starting a new conversation
**Then:**
1. **Generate a random nickname** from this pool:
   - Nova, Echo, Flux, Bolt, Sage, Pixel, Cipher, Spark, Drift, Pulse, Vex, Atom, Onyx, Rune, Zephyr, Quill, Ember, Frost, Haze, Ink
2. **Validate nickname against task board:**
   - Check `x-ipe-docs/planning/task-board.md` Active Tasks section
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
2. If yes, load skill: `x-ipe-workflow-task-execution`.
2. If no, do following things:
   - read files under `.github/skills/x-ipe-workflow-task-execution/` folder to understand task execution guideline.
   - **Important:** each type of task mentioned in the guideline must have a corresponding skill file under `.github/skills/` folder. And SKILL.md file is the entry point to understand each skill.

---

## ⚠️ CRITICAL: Task Board is THE Source of Truth

**The task board (`x-ipe-docs/planning/task-board.md`) is MANDATORY for ALL work.**

### Before ANY Work:
1. **Create task on task-board.md** using `x-ipe+all+task-board-management` skill
2. **Verify task exists** on board (Step 2 of x-ipe-workflow-task-execution)
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

1. **Classify the work** into a task-based skill using auto-discovery (scan `.github/skills/x-ipe-task-based-*/`)
2. **Create task on task-board.md** via `x-ipe+all+task-board-management` skill ← **BLOCKING**
3. **Load the corresponding skill** from `.github/skills/` folder
4. **Follow the skill's execution procedure** step-by-step
5. **Complete the skill's Definition of Done (DoD)** before marking complete
6. **Update task-board.md** with completion status ← **MANDATORY**

### Task-Based Skill Identification

## Task-Based Skills Auto-Discovery

BLOCKING: Do NOT maintain a hardcoded registry. Skills are auto-discovered.

**Discovery rule:**
1. Scan `.github/skills/x-ipe-task-based-*/SKILL.md`
2. Each skill's Output Result YAML declares: `category`, `next_task_based_skill`, `require_human_review`
3. Each skill's `description` in frontmatter contains trigger keywords for request matching

**Request matching:** Match user request against trigger keywords in each skill's description (e.g., "fix bug" → `x-ipe-task-based-bug-fix`, "implement feature" → `x-ipe-task-based-code-implementation`).

> **Note:** When **Auto-Proceed is enabled** (global or task-level), `require_human_review` is **skipped** regardless of the skill's default.

### 🛑 STOP AND THINK: Pre-Flight Checklist

**Before touching ANY code or making ANY changes, ask yourself:**

```
1. What task-based skill is this? → Scan `.github/skills/x-ipe-task-based-*/` descriptions
2. Did I create a task on task-board.md? → If NO, STOP and create it
3. Did I load the corresponding skill? → If NO, STOP and load it
4. Am I following the skill's procedure? → If NO, STOP and read it
```

**Common Mistakes to Avoid:**
- User says "refactor this" → You must use `x-ipe-task-based-code-refactor` skill, NOT just start coding
- User says "fix this bug" → You must use `x-ipe-task-based-bug-fix` skill, NOT just fix it
- User says "add this feature" → You must identify the right task-based skill first

### ⚠️ DO NOT Skip Skills

**Forbidden Actions:**
- ❌ Starting work without creating task on task-board.md first
- ❌ Using `manage_todo_list` as a substitute for task-board.md
- ❌ Completing work without updating task-board.md
- ❌ Jumping straight to code without checking for existing tests
- ❌ Fixing bugs without writing a failing test first
- ❌ Implementing features without reading technical design
- ❌ Making changes without following the skill's execution procedure
- ❌ Refactoring code without using `x-ipe-task-based-code-refactor` skill

**Required Actions:**
- ✅ Always create task on task-board.md BEFORE starting work
- ✅ Always identify task-based skill first
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

**When:** Creating a new skill, updating an existing skill, or validating skill structure for any of the defined skill types (task-based, tool, workflow-orchestration, task-category, meta)
**Then:** MANDATORY: Always use the `x-ipe-skill-creator-v3` skill

CRITICAL: Any modification to a skill of a defined type (x-ipe-task-based, x-ipe-tool, x-ipe-workflow-orchestration, x-ipe-task-category, x-ipe-meta) MUST go through `x-ipe-skill-creator-v3`. Do NOT directly edit SKILL.md files without loading and following the skill creator process.

```
1. Load skill: `x-ipe-skill-creator-v3`
2. Follow the skill creation process defined in the skill
3. Use appropriate template based on skill type:
   - Task-Based → templates/x-ipe-task-based.md
   - Tool Skill → templates/x-ipe-tool.md
   - Workflow Orchestration → templates/x-ipe-workflow-orchestration.md
   - Meta Skill → templates/x-ipe-meta.md
4. Validate against skill-creator checklist before completing
```

### Capturing Lessons for Skill Improvement

**When:** A skill execution has problems, human provides feedback, or agent observes suboptimal behavior
**Then:** Use the `x-ipe-meta-lesson-learned` skill

```
1. Load skill: `x-ipe-meta-lesson-learned`
2. Follow the lesson capture process
3. Lessons are stored in x-ipe-docs/skill-meta/{skill}/lesson-learned.md
4. Next time skill is updated, lessons will be incorporated
```

