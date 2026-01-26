# Dev Environment - Examples

> Reference from SKILL.md: `See [references/examples.md](references/examples.md)`

---

## Example 1: Python Project Setup

**Context:** User runs Dev Environment after Project Initialization

### Execution Flow

```
1. Execute Task Flow from task-execution-guideline skill

2. Detect Project Type:
   - Found: pyproject.toml → Python project
   - Found: Flask in dependencies → Web framework
   - Found: pytest in dev dependencies → Test framework

3. Check Existing Setup:
   - x-ipe-docs/environment/setup.md: EXISTS
   - .vscode/: NOT EXISTS

4. Read Setup Guide:
   - Python version: 3.11+
   - Dependencies: Flask, pytest, python-dotenv
   - Dev server: flask run

5. Create VS Code Configuration:

   .vscode/settings.json:
   ```json
   {
     "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
     "python.testing.pytestEnabled": true,
     "python.testing.pytestArgs": ["tests"],
     "editor.formatOnSave": true,
     "python.formatting.provider": "black"
   }
   ```

   .vscode/launch.json:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Flask: Development",
         "type": "debugpy",
         "request": "launch",
         "module": "flask",
         "args": ["run", "--debug"],
         "env": {"FLASK_APP": "src/app.py"}
       },
       {
         "name": "pytest: All Tests",
         "type": "debugpy",
         "request": "launch",
         "module": "pytest",
         "args": ["tests/", "-v"]
       }
     ]
   }
   ```

   .vscode/tasks.json:
   ```json
   {
     "version": "2.0.0",
     "tasks": [
       {
         "label": "Install Dependencies",
         "type": "shell",
         "command": "pip install -e '.[dev]'"
       },
       {
         "label": "Run Tests",
         "type": "shell",
         "command": "pytest tests/ -v",
         "group": "test"
       }
     ]
   }
   ```

6. Verify Configuration:
   - Open Flask debug config → Valid ✓
   - Run pytest task → Works ✓

7. Resume Task Flow from task-execution-guideline skill
```

### Output

```yaml
category: Standalone
next_task_type: null
require_human_review: No

environment_summary: |
  Configured VS Code for Python Flask project:
  - Debug: Flask dev server, pytest
  - Tasks: Install deps, run tests
  - Settings: Black formatting, pytest enabled

task_output_links:
  - .vscode/settings.json
  - .vscode/launch.json
  - .vscode/tasks.json
```

---

## Example 2: Node.js/TypeScript Project

**Context:** TypeScript project with multiple services

```
1. Detect Project Type:
   - Found: package.json → Node.js
   - Found: tsconfig.json → TypeScript
   - Found: jest.config.js → Jest testing
   - Found: src/server.ts → Backend service

2. Read Setup Guide:
   - Node version: 18+
   - Package manager: pnpm
   - Build: tsc
   - Dev server: tsx watch

3. Create VS Code Configuration:

   .vscode/settings.json:
   ```json
   {
     "typescript.tsdk": "node_modules/typescript/lib",
     "editor.defaultFormatter": "esbenp.prettier-vscode",
     "editor.formatOnSave": true,
     "jest.autoRun": "off"
   }
   ```

   .vscode/launch.json:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Debug Server",
         "type": "node",
         "request": "launch",
         "runtimeExecutable": "pnpm",
         "runtimeArgs": ["tsx", "src/server.ts"],
         "console": "integratedTerminal"
       },
       {
         "name": "Jest: Current File",
         "type": "node",
         "request": "launch",
         "runtimeExecutable": "pnpm",
         "runtimeArgs": ["jest", "${relativeFile}"],
         "console": "integratedTerminal"
       }
     ]
   }
   ```

4. Verify:
   - TypeScript intellisense working ✓
   - Debug config launches server ✓

5. Output:
   configured_for: Node.js TypeScript
   debug_configs: [server, jest]
```

---

## Example 3: Missing Setup Guide (Blocked)

**Scenario:** No x-ipe-docs/environment/setup.md exists

```
1. Check Project Files:
   - pyproject.toml: EXISTS
   - x-ipe-docs/environment/setup.md: NOT FOUND

2. BLOCKED:
   "Setup guide not found at x-ipe-docs/environment/setup.md
    
    This file should have been created during Project Initialization.
    Cannot configure environment without knowing:
    - Required runtime versions
    - Dependency installation steps
    - How to run the application"

3. Options:
   A) Run Project Initialization to create setup.md
   B) Create minimal setup.md based on project files

4. Wait for human decision
```

---

## Example 4: Existing VS Code Config (Merge)

**Scenario:** .vscode folder already exists with partial config

```
1. Check Existing Config:
   - .vscode/settings.json: EXISTS (partial)
   - .vscode/launch.json: NOT EXISTS
   - .vscode/tasks.json: EXISTS (partial)

2. Strategy: Merge (don't overwrite)

3. Update settings.json:
   - Keep existing user settings
   - Add missing testing configuration
   - Add missing formatting settings

4. Create launch.json:
   - New file with debug configurations

5. Update tasks.json:
   - Keep existing tasks
   - Add missing test/build tasks

6. Output:
   action: merged
   files_created: [launch.json]
   files_updated: [settings.json, tasks.json]
   files_preserved: user customizations
```
