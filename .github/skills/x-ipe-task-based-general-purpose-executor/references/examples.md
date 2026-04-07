# Examples: General Purpose Executor

## Example 1: Create a Workflow via User Manual Guidance

**Input:**
```yaml
goal: "Create a new workflow in X-IPE"
execution_instructions: "Use the workflow mode to create a project workflow"
kb_reference:
  path: "x-ipe-docs/knowledge-base/x-ipe-workflow-mode-user-manual/"
  manual_name: "x-ipe-workflow-mode-user-manual"
```

**Execution Trace:**

1. **Phase 1 — Parse:** Breaks instruction into one step: "Create a project workflow using workflow mode." Classified as `manual-guided`.

2. **Phase 1 — Load KB:** Reads `x-ipe-docs/knowledge-base/x-ipe-workflow-mode-user-manual/`, indexes sections like "Getting Started", "Create Workflow", "Workflow Templates".

3. **Phase 2 — Clarify:** Calls `x-ipe-tool-user-manual-referencer` with `lookup_instruction`:
   - query: "create a project workflow using workflow mode"
   - Returns: step-by-step instructions with `clarity_score: 0.85`
   - Result: Step resolved — no human intervention needed.

4. **Phase 5 — Execute:** Calls referencer with `get_step_by_step` to get detailed walkthrough:
   - Step A: Navigate to X-IPE workflow page
   - Step B: Click "New Workflow" button
   - Step C: Select workflow template
   - Step D: Configure workflow name and settings
   - Step E: Save workflow
   - Executor follows each sub-step via Chrome DevTools, verifying each action succeeds.

5. **Phase 5 — Complete:**
   ```yaml
   status: completed
   steps_total: 1
   steps_completed: 1
   steps_failed: 0
   step_results:
     - step: "Create a project workflow using workflow mode"
       status: success
       manual_ref: "x-ipe-workflow-mode-user-manual/create-workflow"
   manual_references_used:
     - "x-ipe-workflow-mode-user-manual/create-workflow"
   ```

---

## Example 2: Unclear Manual Instruction — Escalate to Human

**Input:**
```yaml
goal: "Configure X-IPE for production deployment"
execution_instructions: |
  1. Set up the database connection
  2. Configure the settings
  3. Run the deployment script
kb_reference:
  path: "x-ipe-docs/knowledge-base/x-ipe-deployment-manual/"
  manual_name: "x-ipe-deployment-manual"
```

**Execution Trace:**

1. **Phase 1 — Parse:** Three steps identified. Steps 1 and 3 classified as `manual-guided`. Step 2 also classified as `manual-guided` (ambiguous: "configure the settings" — which settings?).

2. **Phase 2 — Clarify:**
   - Step 1 ("Set up the database connection"): referencer returns `clarity_score: 0.8` → resolved.
   - Step 2 ("Configure the settings"): referencer returns `clarity_score: 0.4` → **below threshold**.
     - Executor asks human: *"The manual says 'configure settings' but doesn't specify which settings. Which settings should I configure?"*
     - Human responds: *"Configure the environment variables in .env: DATABASE_URL, SECRET_KEY, and DEBUG=false"*
     - Step 2 updated with human clarification.
   - Step 3 ("Run the deployment script"): referencer returns `clarity_score: 0.9` → resolved.

3. **Phase 5 — Execute:** All three steps executed successfully with the clarified instructions.

4. **Phase 5 — Complete:**
   ```yaml
   status: completed
   steps_total: 3
   steps_completed: 3
   steps_failed: 0
   step_results:
     - step: "Set up the database connection"
       status: success
       manual_ref: "x-ipe-deployment-manual/database-setup"
     - step: "Configure the settings"
       status: success
       manual_ref: null  # resolved via human clarification
     - step: "Run the deployment script"
       status: success
       manual_ref: "x-ipe-deployment-manual/deployment"
   manual_references_used:
     - "x-ipe-deployment-manual/database-setup"
     - "x-ipe-deployment-manual/deployment"
   ```
