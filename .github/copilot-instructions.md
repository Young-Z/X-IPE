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

## ⚠️ CRITICAL: Skill-First, Not Code-First

**When a user asks you to do something, do NOT jump straight into coding or making changes.**

### 🚫 HARD GATE: No `edit` / `create` Tool Calls Without a Loaded Skill

Before calling **any** file-editing tool (`edit`, `create`, or writing code via `bash`), you MUST have:
1. ✅ Classified the request into a task-based skill
2. ✅ Created a task on `task-board.md`
3. ✅ Loaded the corresponding skill (via `skill` tool or by reading its `SKILL.md`)
4. ✅ Reached the skill's implementation step that permits code changes

If ANY of these are missing → **STOP. Do not touch code.**

### Analyze the Request First

1. **Read and understand** the user's message carefully
2. **Classify the intent** — is this a bug fix? A feature? A refactor? A config change?
3. **Match to an x-ipe skill** — scan `.github/skills/x-ipe-task-based-*/SKILL.md` descriptions to find the right skill
4. **Load and follow that skill** — the skill defines the proper procedure, prerequisites, and Definition of Done

### Why This Matters

Even if a fix seems simple (e.g., "change the default port"), the correct approach is:
- User says "fix this bug" → use `x-ipe-task-based-bug-fix` (write failing test first, then fix)
- User says "this config is wrong" → still a bug fix → use `x-ipe-task-based-bug-fix`
- User says "add a new endpoint" → use `x-ipe-task-based-code-implementation`
- User says "refactor this module" → use `x-ipe-task-based-code-refactor`

**The skill ensures quality** — it enforces test coverage, proper documentation, and review steps that ad-hoc coding skips.

### ⛔ Anti-Pattern: Direct Fix Without Skill

```
❌ User: "the default port is wrong, fix it"
   Agent: *immediately edits config.py and updates 3 files*

✅ User: "the default port is wrong, fix it"
   Agent: *identifies this as a bug fix → loads x-ipe-task-based-bug-fix →
           creates task on board → writes failing test → fixes code →
           verifies tests pass → updates board*
```

### ⛔ Real-World Lesson: TASK-681

```
❌ What happened:
   User: "CLI adapter returns copilot instead of opencode"
   Agent: *immediately found _read_active_cli(), added isinstance check,
           wrote test AFTER the fix, no task board entry*

✅ What should have happened:
   Agent: *classifies as bug fix → loads x-ipe-task-based-bug-fix →
           creates TASK-681 on board → diagnoses root cause →
           runs conflict analysis → writes FAILING test first →
           implements fix → verifies test passes → updates board*
```

The skill caught things the direct fix missed: conflict analysis (checking all callers), TDD verification (proving the test fails without the fix), and task tracking.

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
5. Has the skill reached the step that permits code changes? → If NO, STOP
```

**If you catch yourself about to call `edit`, `create`, or write code via `bash` without completing steps 1–4 above — STOP IMMEDIATELY. Go back and follow the process.**

**Common Mistakes to Avoid:**
- User says "refactor this" → You must use `x-ipe-task-based-code-refactor` skill, NOT just start coding
- User says "fix this" → You must use `x-ipe-task-based-bug-fix` skill, NOT just fix it
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

## Next Step Suggestions (OpenCode & Claude CLI)

> **Note for CLI-based agents (OpenCode, Claude CLI):** When completing a task that is part of the X-IPE task workflow, your "next step" suggestion at the end of your response **MUST** be based on the `next_task_based_skill` field from the completed skill's Output Result YAML — not a generic suggestion. Read the skill's `task_completion_output` section to determine the recommended next action and present it to the user.
>
> For example, if the completed skill declares `next_task_based_skill: "Feature Acceptance Test"`, suggest: *"Next step: Run feature acceptance tests (x-ipe-task-based-feature-acceptance-test)"* rather than a generic "What would you like to do next?".
>
> If `next_task_based_skill` is empty or the task is standalone, you may suggest general next actions.

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
**Then:** MANDATORY: Always use the `x-ipe-meta-skill-creator` skill

CRITICAL: Any modification to a skill of a defined type (x-ipe-task-based, x-ipe-tool, x-ipe-workflow-orchestration, x-ipe-task-category, x-ipe-meta) MUST go through `x-ipe-meta-skill-creator`. Do NOT directly edit SKILL.md files without loading and following the skill creator process.

⛔ **NEVER directly edit files in `.github/skills/{skill-name}/`.** All changes MUST be made in the candidate folder (`x-ipe-docs/skill-meta/{skill-name}/candidate/`) first, validated, then merged to production. Direct edits to live skills bypass validation and risk breaking production behavior.

```
1. Load skill: `x-ipe-meta-skill-creator`
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