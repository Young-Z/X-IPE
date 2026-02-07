# Human Playground - Examples

## Example 1: Auth Feature Playground

**Feature:** FEATURE-002 Email/Password Login

```
1. Execute Task Flow from x-ipe-workflow-task-execution skill

2. DoR Check:
   - Code complete: verified
   - Feature status: Done Code Implementation: verified
   - Tests passing: verified

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
   category: standalone
   next_task_based_skill: null
   require_human_review: yes
   task_output_links:
     - playground/playground_auth.py
     - playground/tests/test_playground_auth.py

8. Resume Task Flow from x-ipe-workflow-task-execution skill
```

---

## Example 2: Human Communication Template

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

---

## Example 3: Scenario Template

| # | Scenario | Steps | Expected Result |
|---|----------|-------|-----------------|
| 1 | Happy path | [Steps] | [Expected] |
| 2 | Invalid input | [Steps] | [Error handling] |
| 3 | Edge case | [Steps] | [Expected] |

---

## Example 4: API Playground README

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

---

## Example 5: Interactive Script Pattern

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

## Playground Example Types

| Type | Purpose | When to Use |
|------|---------|-------------|
| CLI Script | Quick command-line testing | APIs, utilities |
| Web UI | Visual interaction | Frontend features |
| Test Suite | Automated scenarios | Complex logic |
| Notebook | Step-by-step exploration | Data processing |

---

## Playground README Template

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
