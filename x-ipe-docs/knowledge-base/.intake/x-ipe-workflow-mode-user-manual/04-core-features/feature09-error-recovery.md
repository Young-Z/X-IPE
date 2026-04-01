---
title: "Error Recovery"
section: "04-core-features"
extraction_round: 2
source_files:
  - src/x_ipe/static/js/features/workflow-stage.js
  - src/x_ipe/static/js/terminal-v2.js
---

# Error Recovery

## Overview

This section documents how to handle and recover from errors in workflow mode, including action failures, network issues, and state corruption.

## Action Failures

| Scenario | Symptom | Recovery |
|----------|---------|----------|
| Action stuck in "in_progress" | Spinner never completes | Right-click → **Mark as Done** or **Reset to Pending** |
| Action errored | ✗ status icon shown | Right-click → **Reset to Pending**, then retry |
| AI didn't update status | Action appears pending but work is done | Right-click → **Mark as Done** |
| Wrong action triggered | Unintended action started | Right-click → **Reset to Pending** |

## Network Errors

### WebSocket Disconnection
- **Symptom:** Console status shows "Disconnected" (red)
- **Auto-recovery:** WebSocket auto-reconnects when page regains focus
- **Manual recovery:** Refresh the page (F5)
- **Persistent issue:** Check that Flask backend is running on port 5858

### API Call Failures
- **Symptom:** Toast messages like "Failed to update action status"
- **Recovery:** Wait a moment and retry the action
- **Persistent issue:** Check browser console for HTTP error codes

## State Corruption

The workflow state file uses **atomic writes** (temp file + `os.replace()`) to prevent corruption:
- On normal operation: state is always consistent
- On server crash during write: temp file is cleaned up, last good state preserved
- Auto-migration handles version upgrades (v1→v2→v3→v4)

## Stage Gate Issues

| Error Message | Cause | Resolution |
|---------------|-------|------------|
| "Cannot re-open: {action} in {stage} is already started" | Trying to re-trigger a completed action when a later stage has progressed | Use context menu to reset if needed, but be aware this may affect dependent actions |
| Stage won't unlock | Mandatory actions in previous stage not completed | Check stage's mandatory actions (✓ vs ○) and complete missing ones |

![Cannot Re-open Error](screenshots/action-reopen-error.png)

## Terminal Recovery

- If terminal becomes unresponsive: Click the terminal toggle button to hide/show
- If command is hung: Use Ctrl+C in the terminal to interrupt
- Multiple terminals supported (max 2) — switch tabs if one is stuck
