# FEATURE-036-E: Technical Design — Deliverables, Polling & Lifecycle

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 02-17-2026 | Spark | Initial design |

## References

- [Specification](x-ipe-docs/requirements/EPIC-036/FEATURE-036-E/specification.md)
- [Mockup](x-ipe-docs/requirements/EPIC-036/mockups/workflow-view-v1.html) (deliverables: lines ~856–964, 1537–1605)

---

## 1. Component Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│ Backend                                                          │
│  workflow_manager_service.py                                     │
│    ├── resolve_deliverables(name)       ★ NEW                    │
│    ├── archive_stale_workflows()        ★ NEW                    │
│    └── list_workflows()                 MOD (exclude archived)   │
│                                                                  │
│  workflow_routes.py                                              │
│    └── GET /api/workflow/<name>/deliverables   ★ NEW             │
├──────────────────────────────────────────────────────────────────┤
│ Frontend                                                         │
│  workflow-stage.js (extended)                                    │
│    ├── _renderDeliverables()            ★ NEW                    │
│    ├── _renderDeliverableCard()         ★ NEW                    │
│    └── _renderContextMenu()            ★ NEW (manual override)   │
│                                                                  │
│  workflow.js (extended)                                          │
│    ├── _startPolling()                  ★ NEW                    │
│    ├── _stopPolling()                   ★ NEW                    │
│    └── _renderPanelBody()              MOD (+ deliverables)      │
│                                                                  │
│  workflow.css (extended)                                         │
│    └── deliverables + context menu CSS  ★ NEW                    │
└──────────────────────────────────────────────────────────────────┘
```

## 2. Data Models

### 2.1 Deliverables API Response

```javascript
// GET /api/workflow/{name}/deliverables
{
  "success": true,
  "data": {
    "deliverables": [
      { "name": "idea-summary-v2.md", "path": "ideas/021/idea-summary-v2.md", "category": "ideas", "exists": true },
      { "name": "specification.md", "path": "requirements/FEATURE-040/specification.md", "category": "requirements", "exists": true },
      { "name": "missing-file.py", "path": "src/missing.py", "category": "implementations", "exists": false }
    ],
    "count": 3
  }
}
```

### 2.2 Deliverable Categories

```python
DELIVERABLE_CATEGORIES = {
    "compose_idea":         "ideas",
    "refine_idea":          "ideas",
    "reference_uiux":       "mockups",
    "design_mockup":        "mockups",
    "requirement_gathering": "requirements",
    "feature_breakdown":    "requirements",
    "feature_refinement":   "requirements",
    "technical_design":     "requirements",
    "implementation":       "implementations",
    "acceptance_testing":   "quality",
    "quality_evaluation":   "quality",
    "change_request":       "requirements",
}
```

### 2.3 Category UI Config

```javascript
const DELIVERABLE_ICONS = {
    ideas:           { icon: '💡', label: 'Ideas' },
    mockups:         { icon: '🎨', label: 'Mockups' },
    requirements:    { icon: '📋', label: 'Requirements' },
    implementations: { icon: '💻', label: 'Implementations' },
    quality:         { icon: '📊', label: 'Quality' },
};
```

## 3. Implementation Steps

### Step 1: Backend — Deliverables Resolver

**File:** `src/x_ipe/services/workflow_manager_service.py`

Add method `resolve_deliverables(workflow_name)`:
```
1. Read workflow state
2. Iterate all stages and all actions (shared + per-feature)
3. For each action with non-empty deliverables array:
   - Determine category from DELIVERABLE_CATEGORIES map
   - For each deliverable path:
     - Extract filename (basename)
     - Check file existence: (project_root / path).exists()
     - Add to result list
4. Return { deliverables: [...], count: N }
```

### Step 2: Backend — Auto-Archive

**File:** `src/x_ipe/services/workflow_manager_service.py`

Add method `archive_stale_workflows(days=30)`:
```
1. Create archive directory if not exists
2. For each workflow JSON in workflow_dir:
   - Parse last_activity timestamp
   - If now - last_activity > days: move file to archive/
3. Return count of archived workflows
```

Modify `list_workflows()`:
- Already only reads from `workflow_dir` (not archive), so no change needed.

### Step 3: Backend — New API Route

**File:** `src/x_ipe/routes/workflow_routes.py`

Add route:
```python
@workflow_bp.route('/api/workflow/<name>/deliverables', methods=['GET'])
def get_deliverables(name):
    result = _get_service().resolve_deliverables(name)
    return jsonify({'success': True, 'data': result})
```

### Step 4: Frontend — Deliverables Section

**File:** `src/x_ipe/static/js/features/workflow-stage.js`

Add methods:
- `_renderDeliverables(container, wfName)` — fetch deliverables API, render collapsible section
- `_renderDeliverableCard(item)` — individual card with icon, name, path, existence status

Modify `render()`:
```
render(container, workflowState, nextAction, workflowName) {
    // ... existing ribbon + lanes/actions ...
    this._renderDeliverables(container, workflowName);
}
```

### Step 5: Frontend — Polling

**File:** `src/x_ipe/static/js/features/workflow.js`

Add polling logic:
- `_startPolling(wfName, body, wf)` — setInterval(7000) that:
  1. Fetches `GET /api/workflow/{name}`
  2. Compares `last_activity` with stored value
  3. If changed: clear body, re-render via `_renderPanelBody()`
- `_stopPolling(wfName)` — clearInterval
- Store intervals in `this._pollingIntervals = {}`

Modify `_renderPanelBody()`:
- After rendering, call `_startPolling()` for this panel

Modify panel collapse:
- Call `_stopPolling(wf.name)` on collapse

### Step 6: Frontend — Context Menu (Manual Override)

**File:** `src/x_ipe/static/js/features/workflow-stage.js`

Add `_renderContextMenu(actionKey, wfName, featureId)`:
- Create positioned div with "Mark as Done" / "Reset to Pending" options
- On click: call `POST /api/workflow/{name}/action` with status
- Close on outside click

Add context menu trigger:
- On `_renderActionButton()` and feature lane stage dots: `btn.oncontextmenu = (e) => ...`

### Step 7: CSS

**File:** `src/x_ipe/static/css/workflow.css`

Append CSS for:
- `.deliverables-area`, `.deliverables-header`, `.deliverables-grid`
- `.deliverable-card`, `.deliverable-icon.{category}`, `.deliverable-name`, `.deliverable-path`
- `.deliverable-missing` (⚠️ indicator)
- `.deliverables-count` badge
- `.deliverables-toggle` chevron
- `.context-menu`, `.context-menu-item`

## 4. CSS Specifications

```css
/* Deliverables */
.deliverables-area          { padding: 16px 0; border-top: 1px solid var(--border-color); margin-top: 12px; }
.deliverables-header        { display: flex; justify-content: space-between; align-items: center; cursor: pointer; padding: 4px 0; }
.deliverables-title         { font-size: 13px; font-weight: 600; color: var(--text-primary); display: flex; align-items: center; gap: 8px; }
.deliverables-count         { font-size: 11px; padding: 1px 8px; background: rgba(59,130,246,0.15); color: #3b82f6; border-radius: 10px; }
.deliverables-toggle        { font-size: 14px; color: var(--text-muted); transition: transform 0.2s; }
.deliverables-grid          { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 8px; margin-top: 10px; }
.deliverables-empty         { color: var(--text-muted); font-size: 12px; padding: 12px 0; }
.deliverable-card           { display: flex; align-items: center; gap: 10px; padding: 10px 12px; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 6px; transition: all 0.2s; cursor: default; }
.deliverable-card:hover     { border-color: var(--accent); }
.deliverable-card.missing   { opacity: 0.6; }
.deliverable-icon           { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border-radius: 6px; font-size: 16px; flex-shrink: 0; }
.deliverable-icon.ideas           { background: rgba(168,85,247,0.15); }
.deliverable-icon.mockups         { background: rgba(236,72,153,0.15); }
.deliverable-icon.requirements    { background: rgba(59,130,246,0.15); }
.deliverable-icon.implementations { background: rgba(245,158,11,0.15); }
.deliverable-icon.quality         { background: rgba(16,185,129,0.15); }
.deliverable-info           { flex: 1; min-width: 0; }
.deliverable-name           { font-size: 12px; font-weight: 500; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.deliverable-path           { font-size: 10px; font-family: monospace; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.deliverable-missing-badge  { font-size: 10px; color: #ef4444; white-space: nowrap; }

/* Context Menu */
.wf-context-menu            { position: fixed; z-index: 100; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 6px; box-shadow: 0 4px 16px rgba(0,0,0,0.3); min-width: 160px; padding: 4px 0; }
.wf-context-menu-item       { display: block; width: 100%; padding: 8px 14px; font-size: 12px; color: var(--text-primary); background: none; border: none; cursor: pointer; text-align: left; }
.wf-context-menu-item:hover { background: rgba(255,255,255,0.08); }
```

## 5. Sequence Diagrams

### 5.1 Deliverables Load

```
User expands panel
  │
  ├── workflow.js._renderPanelBody()
  │     ├── workflowStage.render()  (ribbon + lanes/actions)
  │     └── workflowStage._renderDeliverables(container, wfName)
  │           ├── GET /api/workflow/{name}/deliverables
  │           ├── Render collapsible section with grid
  │           └── Each card: icon + name + path + exists check
  │
  └── Deliverables section visible in panel body
```

### 5.2 Polling Flow

```
Panel expanded → _startPolling(wfName)
  │
  ├── setInterval(7000)
  │     ├── GET /api/workflow/{name}
  │     ├── Compare last_activity
  │     ├── IF changed:
  │     │     ├── Clear body
  │     │     └── _renderPanelBody() (full re-render)
  │     └── IF same: no-op
  │
  └── Panel collapsed → _stopPolling(wfName)
       └── clearInterval
```

### 5.3 Manual Override

```
User right-clicks action button
  │
  ├── preventDefault() (suppress native menu)
  ├── _renderContextMenu(actionKey, wfName, featureId)
  │     ├── "Mark as Done" → POST /api/workflow/{name}/action { status: "done" }
  │     └── "Reset to Pending" → POST /api/workflow/{name}/action { status: "pending" }
  │
  └── UI refreshes via polling or immediate re-render
```

## 6. Integration Points

| Component | Change | Impact |
|-----------|--------|--------|
| `workflow_manager_service.py` | Add resolve_deliverables(), archive_stale_workflows() | Low — additive |
| `workflow_routes.py` | Add GET /deliverables endpoint | Low — additive |
| `workflow-stage.js` render() | Add deliverables call after ribbon+lanes | Low |
| `workflow-stage.js` action buttons | Add oncontextmenu handler | Low |
| `workflow.js` _renderPanelBody() | Add polling start | Low |
| `workflow.js` panel collapse | Add polling stop | Low |
| `workflow.css` | Append deliverables + context menu CSS | None (additive) |

## 7. Edge Cases

| Case | Handling |
|------|----------|
| No deliverables | Show "No deliverables yet" message |
| API error on deliverables fetch | Show error state in section |
| Poll returns same state | No re-render (timestamp comparison) |
| Multiple panels expanded | Each has independent polling interval |
| Navigate away from Workflow | Stop all polling intervals |
| Right-click on locked action | Context menu still shows (override allowed) |
| Archive directory doesn't exist | Create it on first archive |
