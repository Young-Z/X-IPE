# Feature Specification: Trace Viewer & DAG Visualization

> Feature ID: FEATURE-023-C  
> Version: v1.1  
> Status: Implemented  
> Last Updated: 02-02-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.1 | 02-02-2026 | Updated AC status - DAG visualization implemented |
| v1.0 | 02-01-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description |
|--------|------|------|-------------|
| Tracing Dashboard v4 | HTML | [mockups/tracing-dashboard-v4.html](mockups/tracing-dashboard-v4.html) | Full dashboard with DAG visualization, click-to-open modal, zoom/pan controls |
| Error Trace Detail | HTML | [mockups/error-trace-detail-v1.html](mockups/error-trace-detail-v1.html) | Error visualization with stack traces and skipped function display |

> **Note:** UI/UX requirements below are derived from these mockups.

---

## Overview

**Trace Viewer & DAG Visualization** extends the Tracing Dashboard UI (FEATURE-023-B) with an interactive call graph visualization. When a user selects a trace from the sidebar, this feature renders a Directed Acyclic Graph (DAG) showing the function call hierarchy, execution times, and parameters in the detail panel.

The visualization uses G6 by AntV for canvas-based rendering with:
- Dagre layout algorithm for left-to-right call flow
- Custom trace nodes showing function name, status indicator, level badge, and timing
- Click-to-open modal with full input/output JSON and error details
- Zoom/pan controls for navigating large traces
- Color-coded status indicators (green=success, red=error)

This feature transforms raw trace log files into intuitive visual call graphs, enabling developers to quickly understand execution flow and identify bottlenecks or errors.

---

## User Stories

| ID | As a... | I want to... | So that... |
|----|---------|--------------|------------|
| US-1 | Developer | see a visual graph of function calls | I can understand execution flow at a glance |
| US-2 | Developer | click on a function node to see its details | I can inspect parameters and return values |
| US-3 | Developer | see timing on each node | I can identify performance bottlenecks |
| US-4 | Developer | distinguish errors from successful calls | I can quickly locate failed functions |
| US-5 | Developer | zoom and pan the graph | I can navigate large traces with many nodes |
| US-6 | QA Engineer | see the call hierarchy | I can verify expected execution paths |
| US-7 | Developer | see DEBUG vs INFO level functions | I can focus on important calls or see full detail |
| US-8 | Developer | see error stack traces | I can debug failures with full context |

---

## Acceptance Criteria

### 1. Trace Selection & Loading

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-1.1 | Clicking a trace in sidebar MUST load its data into the detail panel | Must |
| AC-1.2 | Detail panel header MUST show trace ID (truncated) | Must |
| AC-1.3 | Detail panel header MUST show status badge (SUCCESS/ERROR) | Must |
| AC-1.4 | Detail panel header MUST show summary stats (API, total time, function count) | Must |
| AC-1.5 | Loading state MUST be shown while trace data is being fetched | Should |
| AC-1.6 | Error state MUST be shown if trace data fails to load | Must |

### 2. DAG Graph Rendering

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-2.1 | Graph MUST render using G6 by AntV library | Must |
| AC-2.2 | Graph MUST use dagre layout with left-to-right direction (rankdir: 'LR') | Must |
| AC-2.3 | Graph MUST fit within the detail panel container | Must |
| AC-2.4 | Graph MUST auto-fit to view on initial load | Must |
| AC-2.5 | Graph MUST animate node positions during layout | Should |
| AC-2.6 | Empty state MUST show "Select a trace to view" message | Must |

### 3. Trace Node Design

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-3.1 | Each node MUST display function name (centered) | Must |
| AC-3.2 | Each node MUST display status indicator dot (green=success, red=error) | Must |
| AC-3.3 | Each node MUST display level badge (API/INFO/DEBUG) | Must |
| AC-3.4 | Each node MUST display execution time | Must |
| AC-3.5 | Node border MUST be colored by status (green=success, red=error) | Must |
| AC-3.6 | Node MUST have white background with subtle shadow | Must |
| AC-3.7 | Node dimensions MUST be 140x56 pixels | Should |
| AC-3.8 | Node MUST use JetBrains Mono font for function name and timing | Should |

### 4. Edge Design

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-4.1 | Edges MUST connect parent to child nodes | Must |
| AC-4.2 | Edges MUST use polyline type with rounded corners (radius: 8) | Must |
| AC-4.3 | Edges MUST have arrow at target end | Must |
| AC-4.4 | Edge color MUST be subtle gray (#cbd5e1) | Must |
| AC-4.5 | Edge lineWidth MUST be 2 pixels | Should |

### 5. Node Interactions

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-5.1 | Clicking a node MUST open the detail modal | Must |
| AC-5.2 | Hovering a node MUST show enhanced shadow/highlight | Must |
| AC-5.3 | Cursor MUST change to pointer when hovering nodes | Must |
| AC-5.4 | Cursor MUST change to grab when hovering canvas | Should |

### 6. Detail Modal

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-6.1 | Modal MUST display function name in header | Must |
| AC-6.2 | Modal MUST display execution time in header | Must |
| AC-6.3 | Modal MUST display status dot (green/red) in header | Must |
| AC-6.4 | Modal MUST have close button (X) | Must |
| AC-6.5 | Modal MUST have "Input Parameters" section with JSON code block | Must |
| AC-6.6 | Modal MUST have "Output / Return Value" section with JSON code block | Must |
| AC-6.7 | Modal MUST have "Errors" section | Must |
| AC-6.8 | If no errors, show "No errors occurred" message with checkmark icon | Must |
| AC-6.9 | If errors exist, show error type, message, and stack trace | Must |
| AC-6.10 | JSON in code blocks MUST be syntax highlighted (keys, strings, numbers, booleans) | Should |
| AC-6.11 | Modal MUST close when clicking X, clicking overlay, or pressing ESC | Must |
| AC-6.12 | Modal MUST animate in with scale+fade transition | Should |

### 7. Zoom & Pan Controls

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-7.1 | Zoom In button MUST increase zoom by 1.2x | Must |
| AC-7.2 | Zoom Out button MUST decrease zoom by 1.2x | Must |
| AC-7.3 | Fit to View button MUST fit entire graph in viewport | Must |
| AC-7.4 | Mouse scroll MUST zoom in/out | Must |
| AC-7.5 | Mouse drag MUST pan the graph | Must |
| AC-7.6 | Zoom controls MUST be positioned at bottom-right of graph panel | Should |
| AC-7.7 | Help text "Scroll to zoom • Drag to pan • Click node to see details" MUST be visible | Should |

### 8. Error Visualization

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-8.1 | Error nodes MUST have red border | Must |
| AC-8.2 | Error nodes MUST have red status dot | Must |
| AC-8.3 | Trace with errors MUST show ERROR status badge in header | Must |
| AC-8.4 | Error modal section MUST show exception type prominently | Must |
| AC-8.5 | Error modal section MUST show exception message | Must |
| AC-8.6 | Error modal section MUST show stack trace with file:line info | Must |
| AC-8.7 | Stack trace MUST show function name, file path, and line number | Should |

### 9. API Integration

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-9.1 | MUST call `GET /api/tracing/logs/{trace_id}` to fetch trace data | Must |
| AC-9.2 | Response MUST include nodes array with: id, label, timing, status, level, input, output | Must |
| AC-9.3 | Response MUST include edges array with: source, target | Must |
| AC-9.4 | Response MUST include error details if applicable | Must |
| AC-9.5 | API error MUST display user-friendly error message | Must |

### 10. Responsive Behavior

| # | Acceptance Criteria | Priority |
|---|---------------------|----------|
| AC-10.1 | Graph MUST resize when window is resized | Must |
| AC-10.2 | Graph MUST re-fit to view after resize | Should |
| AC-10.3 | Detail panel MUST maintain minimum width of 400px | Should |

---

## Functional Requirements

### FR-1: Trace Data Fetching

**Description:** Fetch parsed trace data for visualization when a trace is selected.

**Input:** User clicks a trace entry in sidebar

**Process:**
1. Get trace_id from selected entry
2. Call `GET /api/tracing/logs/{trace_id}`
3. Parse response into graph data model
4. Pass to G6 graph for rendering

**Output:** Graph rendered with trace data

### FR-2: DAG Graph Initialization

**Description:** Initialize G6 graph with proper configuration.

**Input:** Graph container element ready

**Process:**
1. Get container dimensions
2. Create G6.Graph with dagre layout
3. Register custom 'trace-node' node type
4. Configure default edge style
5. Enable drag-canvas and zoom-canvas modes
6. Attach event handlers (click, hover)

**Output:** Graph instance ready for data

### FR-3: Custom Trace Node Rendering

**Description:** Render nodes with X-IPE trace styling.

**Input:** Node model with: id, label, timing, status, level, input, output, error

**Process:**
1. Create 140x56 rounded rectangle with shadow
2. Add status dot (colored by status)
3. Add level badge (API/INFO/DEBUG)
4. Add function name text (centered)
5. Add timing text below name
6. Set border color by status

**Output:** Styled node shape group

### FR-4: Modal Data Display

**Description:** Show detailed function information in modal.

**Input:** User clicks a node

**Process:**
1. Extract node model data
2. Populate modal header (name, timing, status)
3. Format and syntax-highlight input JSON
4. Format and syntax-highlight output JSON
5. If error exists, show error section with stack trace
6. Animate modal open

**Output:** Modal displayed with function details

### FR-5: Graph Navigation

**Description:** Provide zoom and pan controls for graph exploration.

**Input:** User interacts with zoom buttons or mouse

**Process:**
1. Zoom In: `graph.zoomTo(currentZoom * 1.2, center)`
2. Zoom Out: `graph.zoomTo(currentZoom / 1.2, center)`
3. Fit: `graph.fitView(padding)`
4. Scroll: Native G6 zoom-canvas behavior
5. Drag: Native G6 drag-canvas behavior

**Output:** Graph viewport updated

### FR-6: Responsive Resize

**Description:** Handle window resize events for proper graph sizing.

**Input:** Window resize event

**Process:**
1. Get new container dimensions
2. Call `graph.changeSize(width, height)`
3. Call `graph.fitView(padding)`

**Output:** Graph resized and re-fitted

---

## Non-Functional Requirements

### NFR-1: Performance

| Metric | Target |
|--------|--------|
| Trace data fetch | < 500ms for 100 nodes |
| Graph render time | < 200ms for 50 nodes |
| Zoom/pan responsiveness | < 16ms (60fps) |
| Modal open animation | 200ms |
| Graph resize handling | < 100ms |

### NFR-2: Browser Compatibility

| Browser | Minimum Version |
|---------|----------------|
| Chrome | 90+ |
| Firefox | 88+ |
| Safari | 14+ |
| Edge | 90+ |

### NFR-3: Scalability

| Metric | Target |
|--------|--------|
| Max nodes displayed | 200 without degradation |
| Large traces (200+ nodes) | Warning message, enable virtual rendering |

### NFR-4: Accessibility

| Requirement | Implementation |
|-------------|----------------|
| Keyboard navigation | Tab through controls, Enter to activate |
| Screen reader | ARIA labels on buttons and modal |
| Color contrast | WCAG AA for all text |
| Focus indicators | Visible focus rings on controls |

---

## Dependencies

### Internal Dependencies

| Feature | Dependency Type | What It Provides |
|---------|-----------------|------------------|
| FEATURE-023-A | Required | Trace log files and parsing API |
| FEATURE-023-B | Required | Dashboard layout, sidebar, trace list |
| FEATURE-008 | Required | Workplace framework |

### External Dependencies

| Library | Purpose | Version | CDN |
|---------|---------|---------|-----|
| G6 by AntV | Graph visualization | 4.8.24 | unpkg.com/@antv/g6@4.8.24/dist/g6.min.js |
| JetBrains Mono | Monospace font | - | Google Fonts |
| Inter | UI font | - | Google Fonts |

---

## UI/UX Requirements

### Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│ DETAIL PANEL HEADER                                                     │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ Trace ID: 550e8400-e29b-41d4  [SUCCESS]                             │ │
│ │ Entry: POST /api/orders  │  Total: 287ms  │  Functions: 5           │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│ GRAPH CANVAS                                                            │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │                                                                     │ │
│ │  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      │ │
│ │  │ 🟢 API       │      │ 🟢 INFO      │      │ 🟢 INFO      │      │ │
│ │  │ POST /api/.. │ ──▶  │validate_order│ ──▶  │process_paymt │      │ │
│ │  │    287ms     │      │    45ms      │      │    230ms     │      │ │
│ │  └──────────────┘      └──────┬───────┘      └──────┬───────┘      │ │
│ │                               │                     │              │ │
│ │                               ▼                     ▼              │ │
│ │                        ┌──────────────┐      ┌──────────────┐      │ │
│ │                        │ 🟢 DEBUG     │      │ 🟢 INFO      │      │ │
│ │                        │check_invntry │      │send_notif    │      │ │
│ │                        │    12ms      │      │    12ms      │      │ │
│ │                        └──────────────┘      └──────────────┘      │ │
│ │                                                                     │ │
│ │  [Scroll to zoom • Drag to pan • Click node to see details]        │ │
│ │                                                    [+] [-] [⤢]     │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### Modal Layout

```
┌──────────────────────────────────────────────────────────────┐
│ MODAL HEADER                                                 │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │  🟢 validate_order                            45ms   [X] │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 📥 Input Parameters                                       │ │
│ │ ┌──────────────────────────────────────────────────────┐ │ │
│ │ │ {                                                    │ │ │
│ │ │   "order_data": {...}                                │ │ │
│ │ │ }                                                    │ │ │
│ │ └──────────────────────────────────────────────────────┘ │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 📤 Output / Return Value                                  │ │
│ │ ┌──────────────────────────────────────────────────────┐ │ │
│ │ │ {                                                    │ │ │
│ │ │   "valid": true                                      │ │ │
│ │ │ }                                                    │ │ │
│ │ └──────────────────────────────────────────────────────┘ │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ ⚠️ Errors                                                 │ │
│ │   ✓ No errors occurred                                   │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Color Scheme

| Element | Color | Hex |
|---------|-------|-----|
| Success status | Green | #10b981 |
| Success bg | Light green | #d1fae5 |
| Error status | Red | #ef4444 |
| Error bg | Light red | #fee2e2 |
| Processing | Blue | #3b82f6 |
| DEBUG level | Gray | #94a3b8 |
| INFO level | Blue | #3b82f6 |
| API level | Purple | #6366f1 |
| Node background | White | #ffffff |
| Node shadow | Gray | rgba(0,0,0,0.08) |
| Edge | Subtle gray | #cbd5e1 |

### Empty States

| State | Display |
|-------|---------|
| No trace selected | "Select a trace to view" with icon |
| Trace loading | Skeleton loader or spinner |
| Trace load error | Error message with retry button |

---

## Business Rules

### BR-1: One Trace at a Time

**Rule:** Only one trace can be visualized at a time. Selecting a new trace replaces the current visualization.

### BR-2: Node Click Priority

**Rule:** Clicking a node opens the modal. It does not select the node for multi-select.

### BR-3: Error Propagation

**Rule:** Error status is determined per-node based on trace log error markers. Parent nodes do NOT inherit child error status (unlike some APM tools).

### BR-4: Level Filtering (Future)

**Rule:** DEBUG-level nodes are shown by default. Filtering to hide DEBUG nodes is out of scope for v1.

---

## Edge Cases & Constraints

### EC-1: Empty Trace

**Scenario:** Trace file exists but has no function calls (only API entry/exit).
**Expected:** Show single API node with "No nested function calls" message.

### EC-2: Very Large Trace (100+ nodes)

**Scenario:** Trace has 100+ nodes from complex operation.
**Expected:** Graph renders with warning. Performance may degrade. Consider pagination in v2.

### EC-3: Malformed Trace Data

**Scenario:** API returns trace data with missing fields.
**Expected:** Show error state with "Failed to parse trace data" message.

### EC-4: Trace Deleted While Viewing

**Scenario:** User is viewing trace, another process deletes the log file.
**Expected:** Show "Trace no longer available" message.

### EC-5: Circular Reference (Shouldn't Happen)

**Scenario:** Trace data contains circular edge (A → B → A).
**Expected:** G6 dagre layout handles gracefully. No infinite loops.

### EC-6: Long Function Names

**Scenario:** Function name exceeds node width (e.g., `validate_complex_order_with_multiple_items`).
**Expected:** Truncate with ellipsis, show full name in modal and tooltip.

### EC-7: Deep Nesting

**Scenario:** Trace has 10+ levels of nesting.
**Expected:** Dagre layout handles automatically. User can pan/zoom to navigate.

---

## Out of Scope

- **Real-time trace streaming** (deferred to v2)
- **Trace comparison** (view two traces side-by-side)
- **Trace export** (download as PNG/SVG/JSON)
- **Node filtering** (hide DEBUG nodes)
- **Search within trace** (find specific function)
- **Flame graph view** (alternative visualization)
- **Timing waterfall** (horizontal timeline view)
- **Node collapsing** (collapse subtrees)

---

## Technical Considerations

### Frontend Implementation

- Extend existing `tracing-dashboard.js` with graph rendering
- Use G6 by AntV library (already in mockup)
- Custom `trace-node` node type with G6.registerNode
- Modal can be shared HTML/CSS from mockup

### G6 Configuration

```javascript
const graph = new G6.Graph({
    container: 'traceGraph',
    width, height,
    fitView: true,
    fitViewPadding: 60,
    animate: true,
    modes: { default: ['drag-canvas', 'zoom-canvas'] },
    layout: { 
        type: 'dagre', 
        rankdir: 'LR', 
        nodesep: 40, 
        ranksep: 80 
    },
    defaultNode: { type: 'trace-node' },
    defaultEdge: {
        type: 'polyline',
        style: {
            stroke: '#cbd5e1', 
            lineWidth: 2,
            endArrow: { path: G6.Arrow.triangle(8, 10, 0), fill: '#cbd5e1' },
            radius: 8
        }
    }
});
```

### API Response Format

```javascript
// GET /api/tracing/logs/{trace_id}
{
    "trace_id": "550e8400-e29b-41d4-a716-446655440000",
    "api": "POST /api/orders",
    "timestamp": "2026-02-01T04:15:30Z",
    "total_time_ms": 287,
    "status": "success",  // or "error"
    "nodes": [
        {
            "id": "api",
            "label": "POST /api/orders",
            "timing": "287ms",
            "status": "success",
            "level": "API",
            "input": "{...}",
            "output": "{...}",
            "error": null
        },
        {
            "id": "validate",
            "label": "validate_order",
            "timing": "45ms",
            "status": "success",
            "level": "INFO",
            "input": "{...}",
            "output": "{...}",
            "error": null
        }
    ],
    "edges": [
        { "source": "api", "target": "validate" },
        { "source": "validate", "target": "inventory" }
    ]
}
```

### Error Response Format

```javascript
{
    "id": "payment",
    "label": "process_payment",
    "timing": "230ms",
    "status": "error",
    "level": "INFO",
    "input": "{...}",
    "output": null,
    "error": {
        "type": "PaymentError",
        "message": "Card declined",
        "stack": [
            { "func": "process_payment", "file": "payment.py", "line": 42 },
            { "func": "handle_order", "file": "orders.py", "line": 15 }
        ]
    }
}
```

---

## Open Questions

- [x] Should we support filtering DEBUG nodes? → Defer to v2
- [x] Should hovering show tooltip? → Yes, but use modal for details (per mockup)
- [ ] Maximum zoom level? (Suggest 4x)
- [ ] Minimum zoom level? (Suggest 0.25x)
- [ ] Should timing show in ms or formatted (e.g., "1.2s")? → Use ms for < 1s, formatted for >= 1s

---
