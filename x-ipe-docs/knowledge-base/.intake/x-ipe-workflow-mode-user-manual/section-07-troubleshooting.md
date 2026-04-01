# 7. Troubleshooting

## Common Issues and Solutions

### 1. Server Won't Start

**Symptom:** `x-ipe serve` fails or the browser shows "connection refused"

**Solutions:**
- **Port already in use:** Check if port 5858 is occupied:
  ```bash
  lsof -i :5858
  ```
  If so, either kill the existing process or use a different port:
  ```bash
  x-ipe serve --port 5859
  ```

- **Python version too old:** X-IPE requires Python 3.12+. Check:
  ```bash
  python --version
  ```

- **Missing dependencies:** Reinstall:
  ```bash
  uv tool install x-ipe --force
  # or
  pip install x-ipe --upgrade
  ```

---

### 2. Console Shows "Disconnected"

**Symptom:** Bottom status bar shows "Console: Disconnected" (red). Workflow actions don't execute.

**Solutions:**
- Ensure your AI CLI tool (Copilot, Claude, or OpenCode) is running in a terminal
- The CLI tool must be launched in the same project directory as X-IPE
- Try refreshing the browser page (Ctrl+R / Cmd+R)
- Check that WebSocket connections are not blocked by firewall or proxy

---

### 3. Workflow Actions Don't Execute

**Symptom:** Clicking a workflow action shows no response in the terminal.

**Solutions:**
- **Check console connection:** Must show "Connected" (green)
- **Check action status:** If the action shows ⏳, it may still be processing
- **Check terminal output:** Look at the terminal for error messages
- **Retry:** Click the action again. Some actions may time out on first attempt

---

### 4. "Cannot Re-open" Error

**Symptom:** Clicking a completed action shows: "Cannot re-open: {action} in {stage} stage is already started"

**Explanation:** Once a later stage has begun, previous actions are locked to maintain workflow consistency.

**Solution:** This is expected behavior. If you need to revise earlier work, edit the deliverable files directly in FREE mode.

---

### 5. Workflow Won't Save / Missing Deliverables

**Symptom:** Workflow changes don't persist, or deliverable files are missing.

**Solutions:**
- **Check directory exists:** Ensure `x-ipe-docs/engineering-workflow/` directory exists:
  ```bash
  ls -la x-ipe-docs/engineering-workflow/
  ```
- **Check permissions:** Verify write permissions on the project directory
- **Check config:** Verify `.x-ipe.yaml` has correct `project_root` setting
- **Inspect workflow file:** Open `x-ipe-docs/engineering-workflow/workflow-{name}.json` to check for corruption

---

### 6. Feature Breakdown Creates No Features

**Symptom:** After Feature Breakdown completes, no feature lanes appear.

**Solutions:**
- **Verify action status:** Ensure Feature Breakdown shows ✓ (done), not ⏳ (in progress)
- **Check terminal output:** Look for errors during the breakdown execution
- **Check the workflow file:** Open the JSON file and verify `features[]` array is populated
- **Retry:** Delete the workflow and recreate if the state is corrupted

---

### 7. Stage Won't Unlock

**Symptom:** The next stage stays "locked" even after completing all actions.

**Solutions:**
- **Check mandatory actions:** All mandatory actions in the current stage must be `done`
- **Optional actions don't block:** Only mandatory actions gate stage progression
- **Refresh the page:** Sometimes the UI needs a refresh to show updated state
- **Check JSON:** Inspect the workflow file to verify action statuses

---

### 8. Invalid Workflow Name

**Symptom:** Creating a workflow fails with "INVALID_NAME"

**Solution:** Use only:
- Letters (a-z, A-Z)
- Numbers (0-9)
- Hyphens (`-`)
- Underscores (`_`)

**Invalid examples:** "my project" (spaces), "feature@v2" (special chars), "test/flow" (slashes)

---

## Debug Mode

Enable verbose logging for troubleshooting:

```bash
x-ipe serve --debug
```

Debug mode provides:
- Detailed Flask request/response logging
- Stack traces for errors
- WebSocket connection events

---

## Application Tracing

X-IPE includes built-in tracing for diagnosing issues:

- **View traces:** Navigate to `/tracing/traces` in the browser
- **Traced operations:** Functions decorated with `@x_ipe_tracing()` are automatically captured
- **Sensitive data:** Automatically redacted in trace output

---

## Error Code Reference

| Error Code | Meaning | Common Cause |
|------------|---------|--------------|
| `INVALID_NAME` | Workflow name has invalid characters | Spaces or special chars in name |
| `ALREADY_EXISTS` | Workflow name already taken | Duplicate workflow name |
| `NOT_FOUND` | Workflow doesn't exist (404) | Deleted or mistyped workflow name |
| `CORRUPTED_STATE` | Workflow JSON file is corrupted | Manual file editing or disk error |
| `STAGE_LOCKED` | Cannot perform action in locked stage | Previous stage not completed |
| `ACTION_NOT_FOUND` | Action doesn't exist in stage | Invalid action reference |
| `FEATURE_NOT_FOUND` | Feature ID not found | Feature deleted or wrong ID |
| `INVALID_STATUS` | Invalid status value | Must be: pending, in_progress, done, skipped, failed |
| `INVALID_VALUE` | Invalid configuration value | Wrong type or out of range |
| `PATH_NOT_FOUND` | File/folder path doesn't exist | Missing deliverable file |
| `INVALID_DELIVERABLES` | Deliverable tags don't match template | Template/instance mismatch |
| `INTERNAL_ERROR` | Unhandled server error (500) | Bug — check debug logs |

---

## Workflow Mode Specific Issues (Round 2)

### 9. "Cannot re-open" Error When Clicking Completed Action

**Symptom:** Toast message: "Cannot re-open: {action} in {stage} is already started"

**Cause:** You clicked a completed action, but a later stage has already progressed beyond that point.

**Solutions:**
- **Use context menu:** Right-click the action → "Reset to Pending" to force reopen
- **Caveat:** Only works if dependent actions haven't started; resetting may break the workflow chain
- **Alternative:** Create a new workflow if you need to restart from an earlier stage

### 10. Action Stuck in "in_progress"

**Symptom:** Action shows ⏳ spinner but never completes.

**Solutions:**
- **Right-click** the action → **"Mark as Done"** (if the AI actually completed the work)
- **Right-click** the action → **"Reset to Pending"** (to retry from scratch)
- Check the terminal — the AI CLI tool may be waiting for input

### 11. Workflow View Not Updating

**Symptom:** Action statuses seem stale; changes from the terminal aren't reflected.

**Solutions:**
- **Collapse and re-expand** the workflow card (restarts the 7-second polling interval)
- **Refresh the page** (F5) for a full state reload
- Check that the console shows **"Connected"** (WebSocket must be active)

### 12. Skills Modal Empty

**Symptom:** Clicking "Skills" button shows an empty modal.

**Solutions:**
- Ensure `.github/skills/` directory contains `SKILL.md` files
- Check that `/api/skills` endpoint returns data (open browser console → Network tab)
- Verify the Flask backend is running without errors

### 13. WebSocket Keeps Disconnecting

**Symptom:** Console shows "Disconnected" repeatedly.

**Solutions:**
- Check that Flask backend is running on port 5858: `lsof -i :5858`
- Check for firewall or proxy interference
- Auto-reconnect triggers when page regains focus; try clicking the page
- If persistent, restart the backend: `x-ipe serve`

---

## Getting Help

- **Project repository:** Check the GitHub repository for issues and discussions
- **README:** Contains latest setup and configuration documentation
- **Debug logs:** Run with `--debug` flag and check terminal output
- **Workflow files:** Inspect `.x-ipe/engineering-workflow/workflow-{name}.json` directly
