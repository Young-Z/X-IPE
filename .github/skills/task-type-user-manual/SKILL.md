---
name: task-type-user-manual
description: Create or update the user manual (README.md) with instructions on how to install, configure, and run the application. Use when minimum features are implemented or when specifically asked to document how to run the project.
---

# Task Type: User Manual

## Purpose

Execute **User Manual** tasks by:
1. Identifying the correct run commands for the application.
2. Verifying the commands by executing them.
3. Updating the project's `README.md` with a clear "How to Run" section.

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.
- Understand the project's tech stack (e.g., Python/uv, Node.js/npm).

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | User Manual |
| Category | Standalone |
| Next Task Type | N/A |
| Require Human Review | Yes |

---

## Skill Output

This skill MUST return these attributes to the Task Data Model:

```yaml
Output:
  status: completed | blocked
  next_task_type: null
  require_human_review: Yes
  task_output_links: [README.md]
  
  # Dynamic attributes
  run_command: {verified command}
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Application code is implemented and runnable | Yes |
| 2 | Development environment is set up | Yes |

---

## Execution Flow

Execute User Manual by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Identify Commands | Analyze config files to find run/test commands | Commands identified |
| 2 | Verify Commands | Execute commands to confirm they work | Commands verified |
| 3 | Update README | Add/update "How to Run" section in README.md | README updated |
| 4 | Complete | Inform human with verified commands | Human review |

**⛔ BLOCKING RULES:**
- Step 2 → 3: BLOCKED until run command executes successfully
- Step 4: Human MUST confirm README is clear

---

## Execution Procedure

### Step 1: Identify Run Instructions

**Action:** Determine how to start the application based on configuration files (e.g., `pyproject.toml`, `package.json`).

*   **Python (uv):** Look for usage of `uv run` or specific entry points (e.g., `src/app.py`).
*   **Node.js:** Check `scripts` in `package.json` (e.g., `npm start`, `npm run dev`).

### Step 2: Verify Run Command

**Action:** Execute the identified command in the terminal to ensure it works.

1.  Run the command (e.g., `uv run python src/app.py` or `npm start`).
2.  Check for successful startup (e.g., "Running on http://...", "Server started").
3.  If it fails, debug the issue (e.g., missing dependencies, wrong path) before documenting.
4.  **Note:** For background services, verify start and then stop/kill the process if needed.

### Step 3: Update README.md

**Action:** Add or update the "How to Run" section in `README.md`.

**Content to include:**
1.  **Prerequisites:** Dependencies needing installation (e.g., "Install `uv`").
2.  **Installation:** Commands to setup (e.g., `uv sync`).
3.  **Running:** The verified command to start the app.
4.  **Testing:** Command to run tests (e.g., `uv run pytest`).

**Example Markdown:**

```markdown
## How to Run

1.  **Install Dependencies:**
    \`\`\`bash
    uv sync
    \`\`\`

2.  **Run the Application:**
    \`\`\`bash
    uv run python src/app.py
    \`\`\`

3.  **Run Tests:**
    \`\`\`bash
    uv run pytest
    \`\`\`
```

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Run command identified and verified (executed successfully) | Yes |
| 2 | `README.md` updated with clear run instructions | Yes |
| 3 | `README.md` includes test execution instructions | Yes |

---

## Human Communication

When completed, inform the human:

```
User Manual updated in README.md.

Verified Run Command: `{command}`
Verified Test Command: `{test_command}`

Please check the README and confirm it is clear.
```
