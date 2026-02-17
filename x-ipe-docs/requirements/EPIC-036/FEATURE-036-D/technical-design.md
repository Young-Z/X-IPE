# FEATURE-036-D: Technical Design — Feature Lanes & Dependencies

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 02-17-2026 | Spark | Initial design |

## References

- [Specification](specification.md)
- [FEATURE-036-C Technical Design](../FEATURE-036-C/technical-design.md)
- [Mockup](../mockups/workflow-view-v1.html) (lines ~640–800)

---

## 1. Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ workflow.js (_renderPanelBody)                                  │
│   ├── workflowStage.render() → stage ribbon + actions area      │
│   │     ├── _renderRibbon()           (existing, FEATURE-036-C) │
│   │     ├── _renderActionsArea()      (existing, global actions)│
│   │     ├── _renderFeatureSelector()  ★ NEW                     │
│   │     └── _renderFeatureLanes()     ★ NEW                     │
│   │           ├── _renderLane()       ★ NEW (per feature)       │
│   │           ├── _renderDepBadge()   ★ NEW                     │
│   │           └── _drawDepArrows()    ★ NEW (SVG overlay)       │
│   └── metadata section                (existing)                │
└─────────────────────────────────────────────────────────────────┘

API Endpoints Used (all existing):
  GET  /api/workflow/{name}                    → full state with features
  GET  /api/workflow/{name}/next-action        → next suggested action
  GET  /api/workflow/{name}/dependencies/{id}  → dependency check
```

## 2. Data Models

### 2.1 Feature Data (from workflow state JSON)

```javascript
// stages.implement.features (also validation, feedback)
{
  "FEATURE-040": {
    "name": "Login Page",
    "depends_on": [],          // empty = independent
    "actions": {
      "feature_refinement": { "status": "done", "deliverables": [] },
      "technical_design":   { "status": "in_progress", "deliverables": [] },
      "implementation":     { "status": "pending", "deliverables": [] }
    }
  },
  "FEATURE-041": {
    "name": "Dashboard",
    "depends_on": ["FEATURE-040"],  // blocked until 040 implement done
    "actions": { ... }
  }
}
```

### 2.2 Dependency Check Response

```javascript
// GET /api/workflow/{name}/dependencies/{feature_id}
{
  "blocked": true,
  "blockers": [
    { "feature_id": "FEATURE-040", "current_stage": "implement", "required_stage": "implement" }
  ]
}
```

### 2.3 Feature Lane Actions (per-feature stages in implement)

```javascript
// FEATURE_LANE_ACTIONS — per-feature actions within implement stage
const FEATURE_LANE_ACTIONS = [
  { key: 'feature_refinement', label: 'Refinement',  icon: '📐' },
  { key: 'technical_design',   label: 'Tech Design', icon: '⚙' },
  { key: 'implementation',     label: 'Implement',   icon: '💻' },
  // validation stage:
  { key: 'acceptance_testing', label: 'Testing',     icon: '✅' },
  { key: 'quality_evaluation', label: 'Quality',     icon: '📊' },
  // feedback stage:
  { key: 'change_request',     label: 'CR',          icon: '🔄' },
];
```

## 3. Rendering Flow

### 3.1 Modified `workflowStage.render()`

```
render(container, workflowState, nextAction, workflowName)
  1. _renderRibbon(stages)                        [existing]
  2. hasFeatures = _hasFeatures(stages)
  3. IF hasFeatures:
       _renderFeatureSelector(container, stages, nextAction, workflowName)
       _renderFeatureLanes(container, stages, nextAction, workflowName)
     ELSE:
       _renderActionsArea(stages, nextAction, workflowName)  [existing]
```

**Key decision:** When features exist, the global `_renderActionsArea` (which renders actions for the whole stage) is replaced by per-feature lanes. The stage ribbon still renders above.

### 3.2 Feature Selector Dropdown

```
_renderFeatureSelector(container, stages, nextAction, wfName)
  1. Create wrapper div.feature-selector-wrap
  2. Create toggle button.feature-selector-btn "Select Feature to Work On ▼"
  3. Create dropdown div.feature-selector-dropdown
  4. Collect all features across implement/validation/feedback stages
  5. For each feature:
     - Determine icon: ✅ (all done), 🔄 (in_progress), ⏳ (pending)
     - Get current stage label
     - Get next action from nextAction (if matches feature_id)
     - Create div.feature-selector-item
  6. Click handler: highlight lane, close dropdown
  7. Outside click: close dropdown
  8. Append dependencies toggle button
```

### 3.3 Feature Lanes Container

```
_renderFeatureLanes(container, stages, nextAction, wfName)
  1. Create div.lanes-container (position: relative)
  2. Collect features from implement stage (primary source)
  3. For each feature: _renderLane(feature, stages, nextAction, wfName)
  4. Create SVG overlay: svg.dep-svg-overlay
  5. Append all lanes + SVG to container
  6. Call _drawDepArrows() after render (setTimeout 100ms)
  7. Add window.resize handler (debounced) for arrow redraw
```

### 3.4 Individual Lane Rendering

```
_renderLane(featureId, featureData, stages, nextAction, wfName)
  1. Create div.feature-lane[data-feature="{id}"][data-depends-on="{deps}"]
  2. Lane label (div.lane-label, 180px):
     - Feature ID (monospace, accent color)
     - Feature name (bold)
     - Dependency badge: ⛓ needs {id} OR ⇉ Parallel
  3. Lane stages (div.lane-stages):
     - For each FEATURE_LANE_ACTION:
       - Check action status from featureData.actions
       - Render stage dot: ✓ done (green), ● active (accent), ○ pending (gray)
       - Stage label text
       - Arrow separator ›
  4. Click handler on lane: highlight this lane, set selected in selector
  5. Action button per active stage: _renderFeatureActionBtn()
```

### 3.5 SVG Dependency Arrows

```
_drawDepArrows(container)
  1. Get SVG element
  2. Clear innerHTML
  3. Get container bounding rect
  4. For each lane with data-depends-on:
     - Find source lane
     - Calculate srcRect, tgtRect relative to container
     - Draw cubic Bézier path: M x1,y1 C x1,midY x2,midY x2,y2-4
     - Draw arrowhead polygon at (x2, y2)
  5. Style: dashed stroke (#3b82f6), opacity 0.7
```

## 4. CSS Specifications (Dark Theme Adapted)

```css
/* Feature Selector */
.feature-selector-wrap    { position: relative; margin: 12px 0; display: flex; gap: 8px; align-items: center; }
.feature-selector-btn     { bg: var(--card-bg); border: 1px solid var(--border-color); color: var(--text-primary); }
.feature-selector-dropdown { position: absolute; top: calc(100% + 6px); width: 340px; z-index: 10; opacity: 0; visibility: hidden; }
.feature-selector-dropdown.open { opacity: 1; visibility: visible; }
.feature-selector-item    { display: flex; align-items: center; gap: 10px; padding: 10px 14px; cursor: pointer; }
.feature-selector-item.selected { background: rgba(16,185,129,0.1); }

/* Feature Lanes */
.lanes-container          { display: flex; flex-direction: column; gap: 8px; position: relative; }
.feature-lane             { display: flex; align-items: stretch; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer; transition: all 0.25s; }
.feature-lane:hover       { border-color: var(--accent); box-shadow: 0 2px 8px rgba(16,185,129,0.08); }
.feature-lane.highlighted { border-color: var(--accent); box-shadow: 0 0 0 2px rgba(16,185,129,0.15); background: var(--bg-color); }
.lane-label               { width: 180px; padding: 12px 16px; border-right: 1px solid var(--border-color); display: flex; flex-direction: column; gap: 4px; }
.lane-feature-id          { font-family: monospace; font-size: 10px; color: var(--accent); }
.lane-feature-name        { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.lane-stages              { display: flex; align-items: center; padding: 10px 12px; gap: 4px; flex: 1; flex-wrap: wrap; }
.lane-stage               { display: flex; gap: 5px; align-items: center; padding: 5px 10px; border-radius: 4px; font-size: 11px; white-space: nowrap; }
.lane-stage.done          { background: rgba(16,185,129,0.1); color: #10b981; }
.lane-stage.active        { background: rgba(16,185,129,0.15); color: var(--accent); font-weight: 600; }
.lane-stage.pending       { color: var(--text-muted); }
.lane-arrow               { color: var(--text-muted); font-size: 14px; }

/* Dependency Badges */
.dep-tag                  { display: inline-flex; gap: 3px; padding: 2px 7px; font-size: 9px; font-weight: 600; border-radius: 4px; margin-top: 4px; }
.dep-tag.depends          { background: #fefce8; color: #a16207; border: 1px solid #fde68a; }
.dep-tag.parallel         { background: #eff6ff; color: #1d4ed8; border: 1px solid #93c5fd; }

/* Dependencies Toggle */
.dep-toggle               { padding: 2px 8px; font-size: 11px; cursor: pointer; border-radius: 4px; background: #eff6ff; color: #3b82f6; border: 1px solid #3b82f6; }
.dep-toggle.active        { background: #3b82f6; color: #fff; }
.lanes-container.deps-hidden .dep-svg-overlay,
.lanes-container.deps-hidden .dep-tag { opacity: 0; pointer-events: none; }

/* SVG Arrows */
.dep-svg-overlay          { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 2; overflow: visible; }
.dep-arrow-line           { fill: none; stroke: #3b82f6; stroke-width: 1.8; stroke-dasharray: 5 3; opacity: 0.7; }
.dep-arrow-head           { fill: #3b82f6; opacity: 0.7; }
```

## 5. Implementation Steps

### Step 1: Extend `workflow-stage.js`

1. Add `FEATURE_LANE_ACTIONS` constant
2. Add `_hasFeatures(stages)` — check if any stage has non-empty `features` object
3. Modify `render()` — branch between global actions and feature lanes
4. Add `_renderFeatureSelector()` — dropdown with feature list
5. Add `_renderFeatureLanes()` — container + per-feature lanes
6. Add `_renderLane()` — individual feature lane with label + stage dots
7. Add `_renderDepBadge()` — ⛓ needs or ⇉ Parallel badge
8. Add `_drawDepArrows()` — SVG Bézier arrow rendering
9. Add `_toggleDeps()` — show/hide dependencies
10. Add dependency-aware action dispatch — calls `GET /api/workflow/{name}/dependencies/{feature_id}` before dispatch, shows confirm modal if blocked

### Step 2: Append CSS to `workflow.css`

Append feature lane CSS (from Section 4) after existing FEATURE-036-C styles.

### Step 3: Update tests

Add test cases for:
- Feature lane rendering with features in stage
- Dependency badge logic (parallel vs depends)
- SVG overlay presence
- Feature selector dropdown
- Dependency-aware dispatch flow
- No lanes when no features (fallback to global actions)

## 6. Integration Points

| Component | Change | Impact |
|-----------|--------|--------|
| `workflowStage.render()` | Add feature lanes branch | Low — additive |
| `workflowStage._renderActionsArea()` | Still used when no features | None |
| `workflow.js` | No changes needed | None |
| `workflow.css` | Append new CSS rules | None (additive) |
| `base.html` | No changes needed | None |
| Backend API | No changes needed | None |

## 7. Sequence Diagram

```
User clicks panel expand
  │
  ├─ workflow.js._renderPanelBody()
  │   ├── GET /api/workflow/{name}          → stateData
  │   └── GET /api/workflow/{name}/next-action → nextAction
  │
  ├─ workflowStage.render(body, stateData, nextAction, name)
  │   ├── _renderRibbon()
  │   ├── _hasFeatures()? → YES
  │   ├── _renderFeatureSelector()
  │   │     └── user clicks feature → lane.highlighted
  │   └── _renderFeatureLanes()
  │         ├── _renderLane() × N features
  │         │     ├── lane-label (ID, name, dep badge)
  │         │     └── lane-stages (done/active/pending dots)
  │         ├── SVG overlay
  │         └── _drawDepArrows()
  │
  └─ User clicks action on feature lane
      ├── GET /api/workflow/{name}/dependencies/{feature_id}
      ├── IF blocked → show confirm modal (blockers list)
      │     ├── "Proceed Anyway" → dispatch action
      │     └── "Cancel" → abort
      └── IF not blocked → dispatch action immediately
```

## 8. Edge Cases

| Case | Handling |
|------|----------|
| No features | `_hasFeatures()` returns false → use existing `_renderActionsArea()` |
| Single feature, no deps | One lane, ⇉ Parallel badge, no SVG arrows |
| Window resize | Debounced `_drawDepArrows()` re-render (200ms) |
| Circular deps | Both features show ⛓ tags; both trigger confirm modal |
| Feature in multiple stages | Feature appears in whichever stage has it — typically implement only |
| Dropdown outside click | `document.addEventListener('click', close)` pattern |
