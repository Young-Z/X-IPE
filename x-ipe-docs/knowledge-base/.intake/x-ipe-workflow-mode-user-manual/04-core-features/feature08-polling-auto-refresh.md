---
title: "Polling & Auto-Refresh"
section: "04-core-features"
extraction_round: 2
source_files:
  - src/x_ipe/static/js/features/workflow.js
---

# Polling & Auto-Refresh

## Overview

Workflow panels automatically refresh every 7 seconds when expanded, keeping the UI in sync with backend state changes triggered by AI actions.

## How It Works

1. **Start:** When you expand a workflow card, a polling interval starts for that workflow
2. **Interval:** Every **7 seconds**, the UI fetches the latest workflow state
3. **Compare:** The `last_activity` timestamp is compared with the previous value
4. **Update:** If changed → the panel body re-renders with new data (action statuses, deliverables, stage progression)
5. **Stop:** When you collapse the card or switch to FREE mode, polling stops

## Technical Details

| Setting | Value |
|---------|-------|
| Poll interval | 7 seconds |
| API call | `GET /api/workflow/{workflowName}` |
| Change detection | `last_activity` timestamp comparison |
| Storage | `_pollingIntervals[wfName]` (setInterval ID) |
| Error behavior | Silently skips failed polls (no user notification) |

## When Polling Is Active

- ✅ Workflow card is **expanded**
- ✅ Mode is **WORKFLOW** (not FREE)
- ✅ Page is in foreground

## When Polling Stops

- ❌ Workflow card **collapsed**
- ❌ Mode switched to **FREE**
- ❌ Page navigated away

## Troubleshooting

If the workflow view seems stale:
1. **Collapse and re-expand** the workflow card to restart polling
2. **Refresh the page** (F5) for a full state reload
3. Check the console for "Connected" status (WebSocket must be active)
