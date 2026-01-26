---
name: task-type-human-playground
description: Create interactive examples for human validation. Use when code is implemented and ready for human testing. Provides procedures for creating demos, documentation, and test scenarios.
---

# Task Type: Human Playground

## Purpose

Execute **Human Playground** tasks by:
1. Creating runnable examples
2. Documenting usage instructions
3. Setting up test scenarios
4. Enabling human interaction

---

## Important Notes

### Skill Prerequisite
- If you HAVE NOT learned `task-execution-guideline` skill, please learn it first before executing this skill.

**Important:** If Agent DO NOT have skill capability, can directly go to `.github/skills/` folder to learn skills. And SKILL.md file is the entry point to understand each skill.

---

## Task Type Default Attributes

| Attribute | Value |
|-----------|-------|
| Task Type | Human Playground |
| Category | Standalone |
| Next Task Type | - |
| Require Human Review | Yes |
| Feature Phase | Human Playground |

---

## Task Type Required Input Attributes

| Attribute | Default Value |
|-----------|---------------|
| Auto Proceed | False |

---

## Skill/Task Completion Output

This skill MUST return these attributes to the Task Data Model upon task completion:

```yaml
Output:
  category: standalone
  status: completed | blocked
  next_task_type: null
  require_human_review: Yes
  auto_proceed: {from input Auto Proceed}
  task_output_links: [x-ipe-docs/playground/]
  feature_id: FEATURE-XXX
  feature_title: {title}
  feature_version: {version}
  feature_phase: Human Playground
```

---

## Definition of Ready (DoR)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Code implementation complete | Yes |
| 2 | Feature status is "Done Code Implementation" | Yes |
| 3 | All tests passing | Yes |

---

## Execution Flow

Execute Human Playground by following these steps in order:

| Step | Name | Action | Gate to Next |
|------|------|--------|--------------|
| 1 | Create Examples | Build runnable playground files in `playground/` | Playground file created |
| 2 | Document Usage | Add entry to `playground/README.md` | README updated |
| 3 | Create Tests | Write human simulation tests in `playground/tests/` | Test files created |
| 4 | Validate | Run playground command and verify it works | Exit code 0 |
| 5 | Run Tests | Execute human simulation tests | All tests pass |
| 6 | Complete | Verify DoD, output summary, request human review | Human review |

**⛔ BLOCKING RULES:**
- Step 4: BLOCKED until playground command runs without error
- Step 5: BLOCKED until human simulation tests pass
- Step 6 → Human Review: Human MUST validate playground before Feature Closing

---

## Execution Procedure

### Step 1: Create Runnable Examples

**Action:** Build interactive demonstrations

```
1. Create a `playground/` directory if it doesn't exist
2. Place playground files directly in `playground/` (no subfolders per feature)
3. Name playground files as `playground_{feature_name}.py` (e.g., `playground_task_operations.py`)
4. Identify key functionality to demonstrate
5. Create minimal runnable examples
6. Include both happy path and edge cases
7. Ensure examples are self-contained
```

**Example Types:**

| Type | Purpose | When to Use |
|------|---------|-------------|
| CLI Script | Quick command-line testing | APIs, utilities |
| Web UI | Visual interaction | Frontend features |
| Test Suite | Automated scenarios | Complex logic |
| Notebook | Step-by-step exploration | Data processing |

### Step 2: Document Usage

**Action:** Write clear instructions

1. Create a single `README.md` inside the `playground/` folder (if it doesn't exist).
2. Add an entry for the new playground with the command to run it.
3. Keep documentation minimal - just explain how to run each playground.

**Documentation Structure:**

```markdown
# Playground

Interactive playgrounds for human testing.

## How to Run

| Playground | Command |
|------------|--------|
| Task Operations | `uv run python playground/playground_task_operations.py` |
| Persistence | `uv run python playground/playground_persistence.py` |

## Human Simulation Tests

| Test | Command |
|------|--------|
| Task Operations | `uv run python playground/tests/test_playground_task_operations.py` |
| Persistence | `uv run python playground/tests/test_playground_persistence.py` |
```

### Step 3: Validate and Setup Test Scenarios

**Action:** Agent runs the playground command to ensure it works, then defines what human should verify.

**Validation:**
1. Execute the playground command (e.g., `uv run python playground/playground_feature.py`).
2. Verify it runs without error (exit code 0).
3. If it fails, fix the playground script or surrounding code.

**Human Simulation Tests:**
1. Create `playground/tests/` directory for test scripts
2. Name test files as `test_playground_{feature_name}.py`
3. These are NOT unittests - they simulate human interaction scenarios
4. Tests should validate expected behavior from a human perspective
5. Run tests to verify playground works correctly

**Scenario Template:**

| # | Scenario | Steps | Expected Result |
|---|----------|-------|-----------------|
| 1 | Happy path | [Steps] | [Expected] |
| 2 | Invalid input | [Steps] | [Error handling] |
| 3 | Edge case | [Steps] | [Expected] |

### Step 4: Enable Interaction

**Action:** Make it easy for human to test

```
1. Provide start/stop commands
2. Include sample data
3. Add reset capability
4. Log outputs for debugging
```

---

## Definition of Done (DoD)

| # | Checkpoint | Required |
|---|------------|----------|
| 1 | Runnable examples created as `playground/playground_{feature_name}.py` | Yes |
| 2 | Entry added to `playground/README.md` with run command | Yes |
| 3 | Human simulation tests created in `playground/tests/test_playground_{feature_name}.py` | Yes |
| 4 | Agent has verified the playground command runs successfully | Yes |
| 5 | Agent has verified the human simulation tests pass | Yes |
| 6 | Human can interact with feature | Yes |

**Important:** After completing this skill, always return to `task-execution-guideline` skill to continue the task execution flow and validate the DoD defined there.

---

## Output Artifacts

| Artifact | Location | Description |
|----------|----------|-------------|
| Playground Files | `playground/playground_{feature_name}.py` | Runnable interactive examples |
| Usage Doc | `playground/README.md` | How to run playgrounds |
| Human Simulation Tests | `playground/tests/test_playground_{feature_name}.py` | Automated human scenario validation |

---

## Patterns

### Pattern: Standard Playground Structure

**Structure:**
```
playground/
├── README.md                      # How to run all playgrounds
├── playground_{feature1}.py       # Interactive playground for feature 1
├── playground_{feature2}.py       # Interactive playground for feature 2
└── tests/
    ├── test_playground_{feature1}.py  # Human simulation tests
    └── test_playground_{feature2}.py  # Human simulation tests
```

### Pattern: API Playground

**Structure:**
```
playground/
├── README.md              # How to run all playgrounds
├── playground_api.py      # Interactive API testing script
├── sample-data.json       # Test data (optional)
└── tests/
    └── test_playground_api.py  # Human simulation tests
```

**Example README:**
```markdown
# Auth API Playground

## Start Server
\`\`\`bash
npm run dev
\`\`\`

## Test Login
\`\`\`bash
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
\`\`\`

Expected response:
\`\`\`json
{
  "token": "eyJhbG...",
  "expiresIn": 3600
}
\`\`\`
```

### Pattern: CLI Playground

**Structure:**
```
playground/
├── README.md                  # How to run all playgrounds
├── playground_cli.py          # Interactive CLI playground
└── tests/
    └── test_playground_cli.py # Human simulation tests
```

### Pattern: Interactive Script

```javascript
// playground/interactive.js
const readline = require('readline');
const { AuthService } = require('../src/services/auth');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('=== Auth Playground ===');
console.log('Commands: register, login, logout, exit\n');

rl.on('line', async (input) => {
  const [cmd, ...args] = input.split(' ');
  
  switch(cmd) {
    case 'register':
      // Handle register
      break;
    case 'login':
      // Handle login
      break;
    // ...
  }
});
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Instead |
|--------------|---------|---------|
| No instructions | Human can't start | Write clear README |
| Hard-coded config | Doesn't work elsewhere | Use environment variables |
| No sample data | Nothing to test with | Provide seed data |
| Complex setup | Human gives up | Keep setup to 1-2 commands |
| No expected outputs | Human doesn't know if it works | Document what to expect |

---

## Example

**Feature:** FEATURE-002 Email/Password Login

```
1. Execute Task Flow from task-execution-guideline skill

2. DoR Check:
   - Code complete ✓
   - Feature status: Done Code Implementation ✓
   - Tests passing ✓

3. Step 1 - Create Examples:
   Created:
   - playground/playground_auth.py
   - playground/tests/test_playground_auth.py
   - Updated playground/README.md with run command

4. Step 2 - Document:
   README includes:
   - How to start server
   - How to register user
   - How to login
   - Expected responses

5. Step 3 - Scenarios:
   Defined:
   - Scenario 1: Successful login
   - Scenario 2: Invalid password
   - Scenario 3: Non-existent user
   - Scenario 4: Rate limiting

6. Step 4 - Enable Interaction:
   - npm run playground starts everything
   - Sample users pre-seeded
   - Clear console output

7. Return Task Completion Output:
   feature_id: FEATURE-002
   feature_status: Done Human Playground
   category: Standalone
   next_task_type: null
   require_human_review: Yes
   task_output_links:
     - playground/playground_auth.py
     - playground/tests/test_playground_auth.py

8. Resume Task Flow from task-execution-guideline skill
```

---

## Human Communication

When playground is ready, inform human:

```
Playground ready for [Feature Name]!

To start:
  [command]

Test scenarios:
1. [Scenario 1] - [brief description]
2. [Scenario 2] - [brief description]

Please verify and let me know when ready to proceed.
```
