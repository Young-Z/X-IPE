# Acceptance Test Cases: Copy Design as Mockup Mode

> Feature ID: FEATURE-030-B-MOCKUP
> Version: v2.0
> Test Date: 02-14-2026
> Tester: Spark (automated via Chrome DevTools MCP)
> Target: https://github.com (injected toolbar)

---

## Execution Results

| Metric | Value |
|--------|-------|
| Total Test Cases | 6 |
| Passed | 6 |
| Failed | 0 |
| Blocked | 0 |
| Pass Rate | 100% |

---

## Test Cases

### TC-M1: Mode Switch to Copy Mockup

| Field | Value |
|-------|-------|
| Maps to | AC-M1 |
| Priority | P0 |
| Status | ✅ Pass |

**Verification:**
- Clicked "📐 Copy Mockup" tab → active tab switched
- `__xipeRefData.mode` = "mockup"
- Panel shows "Step 1/4: Select Components"
- Empty state message: "Click elements on the page to select components"
- 4-step wizard indicator visible

---

### TC-M2: Smart-Snap Component Capture

| Field | Value |
|-------|-------|
| Maps to | AC-M1, AC-M2, AC-M5 |
| Priority | P0 |
| Status | ✅ Pass |

**Verification:**
- Captured `<nav>` element (semantic tag in SEMANTIC_TAGS set) ✅
- Captured `<main>` element (semantic tag) ✅
- Component data structure correct — all 8 fields present:
  - id, selector, tag, bounding_box, screenshot_dataurl, html_css, instruction, agent_analysis
- Bounding boxes have valid width/height > 0
- `html_css.level` = "minimal" on initial capture
- Selector generator produces valid CSS selector that resolves to element

---

### TC-M3: Component Data Schema

| Field | Value |
|-------|-------|
| Maps to | AC-M5, AC-M6 |
| Priority | P0 |
| Status | ✅ Pass |

**Verification:**
- Component ID format: `comp-001`, `comp-002` (auto-increment) ✅
- Selector resolves back to element: `document.querySelector(selector)` returns element ✅
- Bounding box: `{ x, y, width, height }` from `getBoundingClientRect()`
- Lightweight capture includes CAPTURE_PROPS list (~25 CSS properties)
- Max 20 components enforced via `MAX_COMPONENTS` constant

---

### TC-M4: Instructions (Step 2)

| Field | Value |
|-------|-------|
| Maps to | AC-M8, AC-M9, AC-M10 |
| Priority | P0 |
| Status | ✅ Pass |

**Verification:**
- Instructions stored in `components[n].instruction`:
  - comp-001: "Navigation bar - sticky header"
  - comp-002: "Main content area with hero section"
- Both instructions stored correctly ✅
- Empty instruction is valid (not required) ✅

---

### TC-M5: Analyze & Deep Capture (Step 3)

| Field | Value |
|-------|-------|
| Maps to | AC-M11, AC-M13, AC-M14 |
| Priority | P0 |
| Status | ✅ Pass |

**Verification:**
- "Analyze" click sets `mode = "mockup"`, `__xipeRefReady = true` ✅
- Agent receives: mode, colors_count=3, components_count=2, has_instructions=true
- Deep capture command flow:
  - Set `__xipeRefCommand = { action: "deep_capture", target: "comp-001" }` ✅
  - Deep capture upgrades `html_css.level` from "minimal" to "deep"
  - Full computed styles captured: **2,297 CSS properties** ✅
  - `outer_html` captured ✅
- Command polling via `setInterval(pollCommands, 1000)` active

---

### TC-M6: Generate Mockup (Step 4)

| Field | Value |
|-------|-------|
| Maps to | AC-M17, AC-M18, AC-M23 |
| Priority | P0 |
| Status | ✅ Pass |

**Verification:**
- "Generate Mockup" button disabled when no components (tooltip: "Select at least one component first.")
- When components present: button enabled
- On click: `mode = "mockup"`, `__xipeRefReady = true`
- Toast: "Saving reference data..." (progress type)
- Agent data complete for generation: 2 components with instructions + 3 colors ✅

---

## Notes

- Smart-snap was verified by programmatic element capture (the click handler requires real user mouse events targeting page elements, which are intercepted by the capturing listener)
- Deep capture successfully retrieved 2,297 computed styles from a GitHub nav element
- The 4-step wizard UI renders correctly with proper step labels and navigation
- Overlay elements (.xipe-snap-overlay) are not created during programmatic capture since the renderComponentList() was not triggered via UI; the overlay creation code was verified via source inspection
- Cross-mode data persistence verified: colors from theme mode remain available in mockup mode
