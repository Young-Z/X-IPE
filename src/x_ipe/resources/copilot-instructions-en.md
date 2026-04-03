# Copilot Instructions

> **⚠️ CRITICAL RULE FOR AI AGENTS EXECUTING SUGGESTED SKILLS:**
> Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.
> Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.
> Follow the steps EXACTLY in the skill to execute! Do NOT skip, reorder, or improvise.

> **Scope:** These rules apply only when working on the X-IPE project codebase. General programming questions, explanations, or conversations that don't modify X-IPE files are exempt from the skill/task-board workflow.

## Before You Start

## ⚠️ CRITICAL: DAO-First — Every Message Through Human Representative

**When:** Receiving ANY user message (command, question, feedback, approval)
**Then:**
1. **EVERY user message MUST be processed through `x-ipe-dao-end-user-representative` before any other action.**
   - This is the universal gateway. No matter what the user says — a command, a question, feedback, approval — the message flows through the human representative skill first. The DAO interprets the message, selects a disposition, and the agent acts on that structured output.
2. Model Requirement
   - When `x-ipe-dao-end-user-representative` is delegated to a sub-agent (e.g., via the `task` tool), **use the most capable (premium) LLM model available** (e.g., `model: "claude-opus-4.6"`). The 7-step backbone requires nuanced reasoning — weighing three perspectives, analyzing gains/losses, scenario planning — that fast/cheap models cannot reliably handle. If running inline (not as a sub-agent), the main agent's model is used automatically.
3. Why DAO-First Matters
   - **Consistent interpretation** — Every message gets structured analysis, not ad-hoc pattern matching
   - **Context-aware routing** — DAO considers the current task, feature, and workflow state when interpreting
   - **Disposition-driven branching** — The agent's next action is determined by a clear, bounded signal, not raw text parsing
   - **Bounded scope** — DAO interprets intent only. It does NOT execute tasks, write code, or absorb skill responsibilities

> **Note:** Session initialization (nickname selection below) runs once at session start and is exempt from DAO-first.

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

**When DAO returns any instruction unit with disposition `instruction` (user is commanding action), do NOT jump straight into coding or making changes.**

### 🚫 HARD GATE: No `edit` / `create` Tool Calls Without a Loaded Skill

DAO now returns `instruction_units[]` — an array of 1–3 instruction units with an `execution_plan`. The agent MUST respect the execution plan:

```
for each group in execution_plan.groups (sequentially):
    for each unit_index in group (in PARALLEL if group has multiple units):
        unit = instruction_units[unit_index]
        1. ✅ Check unit disposition (if `instruction` → continue below; if `answer`/other → handle accordingly)
        2. ✅ Classified the unit into a task-based skill (from unit's suggested_skills)
        3. ✅ Created a task via `x-ipe-tool-task-board-manager` for this unit
        4. ✅ Loaded the corresponding skill (via `skill` tool or by reading its `SKILL.md`)
        5. ✅ Reached the skill's implementation step that permits code changes
        6. Execute the unit
    wait for all units in this group to complete before starting next group
```

If ANY of steps 1–5 are missing for the CURRENT unit → **STOP. Do not touch code.**


### ⛔ Real-World Lesson:

```
❌ What happened:
   User: "CLI adapter returns copilot instead of opencode"
   Agent: *immediately found _read_active_cli(), added isinstance check,
           wrote test AFTER the fix, no task board entry*

✅ What should have happened:
   Agent: *DAO interprets → instruction_units[0].disposition: instruction →
           classifies as bug fix → loads x-ipe-workflow-task-execution → loads x-ipe-task-based-bug-fix →
           creates TASK-681 on board → diagnoses root cause →
           runs conflict analysis → writes FAILING test first →
           implements fix → verifies test passes → updates board*
```

---

## ⚠️ CRITICAL: Task Board is THE Source of Truth

**The task board (JSON-based, managed by `x-ipe-tool-task-board-manager`) is MANDATORY for ALL work.**

### Before ANY Work:
1. **Create task** using `x-ipe-tool-task-board-manager` skill
2. **Verify task exists** on board (Step 2 of x-ipe-workflow-task-execution)
3. **Only then** proceed to actual work

### After Completing Work:
1. **Update task status** — set to completed via `x-ipe-tool-task-board-manager`
2. 
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

> **Note:** DAO-First is universal — it applies in ALL modes (`auto`, `manual`, `stop_for_question`). The mode affects whether *within-skill* decision points also go through DAO (auto) or ask the human (manual/stop_for_question). But the initial message always goes through DAO.

### 🛑 STOP AND THINK: Pre-Flight Checklist

**Before touching ANY code or making ANY changes, ask yourself:**

```
0. Did I process this message through DAO? → If NO, STOP and call x-ipe-dao-end-user-representative
1. What task-based skill is this? → Scan `.github/skills/x-ipe-task-based-*/` descriptions
2. Did I create a task on the task board? → If NO, STOP and create it
3. Did I load the corresponding skill? → If NO, STOP and load it
4. Am I following the skill's procedure? → If NO, STOP and read it
5. Has the skill reached the step that permits code changes? → If NO, STOP
```

**If you catch yourself about to call `edit`, `create`, or write code via `bash` without completing steps 0–5 above — STOP IMMEDIATELY. Go back and follow the process.**

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