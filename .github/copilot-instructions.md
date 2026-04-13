# AI Agent Instructions

> **⚠️ CRITICAL RULE FOR AI AGENTS EXECUTING SUGGESTED SKILLS:**
> Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.
> Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.
> Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.

> **Scope:** These rules apply only when working on the X-IPE project codebase. General programming questions, explanations, or conversations that don't modify X-IPE files are exempt from the skill/task-board workflow.

## Before You Start

**When:** Starting first x-ipe workflow task in a new session
**Then:**
1. **Generate a random nickname** from this pool:
   - Nova, Echo, Flux, Bolt, Sage, Pixel, Cipher, Spark, Drift, Pulse, Vex, Atom, Onyx, Rune, Zephyr, Quill, Ember, Frost, Haze, Ink
2. **Validate nickname against task board:**
   - Query active tasks via `x-ipe-tool-task-board-manager` (task_query.py --status in_progress)
   - If another session has `🔄 in_progress` tasks with the same nickname → pick a different name from the pool
   - If the in_progress task was started by your current session (same context) → keep the name
   - Repeat until you find an unused name
3. Introduce yourself: "Hi, I'm [nickname]"
4. This nickname is your assignee identifier
5. Check for open tasks assigned to you
6. Only work on tasks assigned to you or unassigned

---

## ⚠️ CRITICAL: Skill-First, Not Code-First

**Do NOT jump straight into coding or making changes.**

### 🚫 HARD GATE: No `edit` / `create` Tool Calls Without a Loaded Skill

Before calling **any** file-editing tool (`edit`, `create`, or writing code via `bash`), you MUST have:
1. ✅ Classified the request into a task-based skill (from auto-discovery)
2. ✅ Created a task on the task board (via `x-ipe-tool-task-board-manager`)
3. ✅ Loaded the corresponding skill (via `skill` tool or by reading its `SKILL.md`)
4. ✅ Reached the skill's implementation step that permits code changes

If ANY of these are missing → **STOP. Do not touch code.**


### ⛔ Real-World Lesson:

```
❌ What happened:
   User: "CLI adapter returns copilot instead of opencode"
   Agent: *immediately found _read_active_cli(), added isinstance check,
           wrote test AFTER the fix, no task board entry*

✅ What should have happened:
   Agent: *classifies as bug fix → loads x-ipe-task-based-bug-fix →
           Phase 0: creates TASK-681 on board via x-ipe-tool-task-board-manager →
           diagnoses root cause → writes FAILING test first →
           implements fix → verifies test passes →
           final step: updates board (task done) via x-ipe-tool-task-board-manager*
```

---

## ⚠️ CRITICAL: Task Board is THE Source of Truth

**The task board (JSON-based, managed by `x-ipe-tool-task-board-manager`) is MANDATORY for ALL work.**

### Before ANY Work:
1. **Create task** using `x-ipe-tool-task-board-manager` skill (each task-based skill does this in its Phase 0)
2. **Verify task exists** on board before proceeding
3. **Only then** proceed to actual work

### After Completing Work:
1. **Update task status** — set to completed via `x-ipe-tool-task-board-manager`

### ⛔ NEVER:
- Use `manage_todo_list` as a substitute for the JSON task board (that's VS Code internal only)
- Start work without a task ID on the board
- Complete work without updating the board

---

## ⚠️ STRICT: Task Matching & Skill Enforcement

### Mandatory Workflow

All work follows the Pre-Flight Checklist below. Use `x-ipe-tool-task-board-manager` to create/update tasks.

### Task-Based Skill Identification

## Task-Based Skills Auto-Discovery

BLOCKING: Do NOT maintain a hardcoded registry. Skills are auto-discovered.

**Discovery rule:**
1. If the skills attachment is available in context, use it for matching (no filesystem scan needed)
2. Otherwise, scan `.github/skills/x-ipe-task-based-*/SKILL.md`
3. Each skill's `description` contains trigger keywords for request matching

**Request matching:** Match user request against trigger keywords in each skill's description (e.g., "fix bug" → `x-ipe-task-based-bug-fix`, "implement feature" → `x-ipe-task-based-code-implementation`).

> **Note:** When **Interaction Mode is DAO-based** (global or task-level), `require_human_review` is **skipped** regardless of the skill's default. The `process_preference.interaction_mode` enum (`interact-with-human | dao-represent-human-to-interact | dao-represent-human-to-interact-for-questions-in-skill`) controls this behavior.

> **Note:** The `interaction_mode` controls whether *within-skill* decision points go through the `x-ipe-dao-end-user-representative` skill (acting as a human representative) or ask the human directly. This is a within-skill concern — skills call DAO at their own decision points when `interaction_mode == "dao-represent-human-to-interact"`.

### 🛑 STOP AND THINK: Pre-Flight Checklist

**Before touching ANY code or making ANY changes, ask yourself:**

```
1. What task-based skill is this? → Scan `.github/skills/x-ipe-task-based-*/` descriptions
2. Did I create a task on the task board? → If NO, STOP and create it
3. Did I load the corresponding skill? → If NO, STOP and load it
4. Am I following the skill's procedure? → If NO, STOP and read it
5. Has the skill reached the step that permits code changes? → If NO, STOP
```

**If you catch yourself about to call `edit`, `create`, or write code via `bash` without completing steps 1–5 above — STOP IMMEDIATELY. Go back and follow the process.**

**Common Mistakes to Avoid:**
- User says "refactor this" → You must use `x-ipe-task-based-code-refactor` skill, NOT just start coding
- User says "fix this" → You must use `x-ipe-task-based-bug-fix` skill, NOT just fix it
- User says "add this feature" → You must identify the right task-based skill first

---

## Development Principles

Always follow:
1. **SOLID** - Design principles
2. **DRY** - Don't Repeat Yourself
3. **YAGNI** - You Aren't Gonna Need It
4. **KISS** - Keep It Simple

---

## Knowledge Search

**When:** Agent needs to search the knowledge base or knowledge graph
**Then:** Always use the **ontology search** (`x-ipe-tool-ontology` Operation C) as the first choice before any other search approach. The ontology search provides structured, graph-aware results with entity relationships and subgraph context.

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
