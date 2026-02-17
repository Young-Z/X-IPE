# Acceptance Test Cases: Catch Design Theme Mode

> Feature ID: FEATURE-030-B-THEME
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

### TC-T1: Core Shell — Toolbar Injection & Globals

| Field | Value |
|-------|-------|
| Maps to | AC-T1, AC-T7 |
| Priority | P0 |
| Status | ✅ Pass |

**Verification:**
- `__xipeToolbarReady` = true
- `__xipeRegisterMode` = function
- `__xipeToast` = function
- `__xipeGenerateSelector` = function
- `__xipeRefData` initialized with mode, colors[], components[]
- Toolbar element `.xipe-toolbar` exists with `position: fixed`, `z-index: 2147483647`
- Hamburger shows "X-IPE", panel has 2 mode tabs ("🎨 Catch Theme", "📐 Copy Mockup")
- Default active tab: "🎨 Catch Theme"

---

### TC-T2: Offscreen Canvas & Color Sampling

| Field | Value |
|-------|-------|
| Maps to | AC-T1, AC-T2, AC-T3, AC-T4, AC-T5 |
| Priority | P0 |
| Status | ✅ Pass |

**Verification:**
- `__xipeViewportScreenshot` loaded into offscreen canvas
- Pixel at (750, 330) reads RGB(35, 134, 54) = #238636 ✅ (matches painted test data)
- Magnifier element `.xipe-magnifier` exists in DOM
- Colors stored with correct schema: id, hex, rgb, hsl, source_selector, role, context
- Color ID format: `color-001`, `color-002`, `color-003`

---

### TC-T3: Magnifier UI Elements

| Field | Value |
|-------|-------|
| Maps to | AC-T1, AC-T7 |
| Priority | P0 |
| Status | ✅ Pass |

**Verification:**
- Magnifier element exists with 120px canvas
- Uses `requestAnimationFrame` for throttling
- Crosshair drawn with `#10b981` stroke
- Hex label displayed below magnifier circle
- CORS error handling: fallback shows "CORS" text

---

### TC-T4: Role Annotation (Step 2)

| Field | Value |
|-------|-------|
| Maps to | AC-T9, AC-T10, AC-T11, AC-T12 |
| Priority | P0 |
| Status | ✅ Pass |

**Verification:**
- 3 preset role chips: primary, secondary, accent
- Custom role text input available
- Roles stored in `__xipeRefData.colors[n].role`:
  - #238636 → "primary"
  - #f0f6fc → "secondary"
  - #161b22 → "accent"
- All colors have roles assigned ✅

---

### TC-T5: Create Theme (Step 3)

| Field | Value |
|-------|-------|
| Maps to | AC-T13, AC-T16 |
| Priority | P0 |
| Status | ✅ Pass |

**Verification:**
- "Create Theme" button enabled when ≥1 color has role
- On click: `__xipeRefData.mode` set to "theme", `__xipeRefReady` set to true
- Agent can read complete annotated color data
- Data complete check: 3 colors with roles, mode = "theme" ✅

---

### TC-T6: Toast API & Wizard Navigation

| Field | Value |
|-------|-------|
| Maps to | AC-T6, FR-T9 |
| Priority | P1 |
| Status | ✅ Pass |

**Verification:**
- Toast API functional: info, success, progress, error types render correctly
- Toast elements have correct CSS classes (`.xipe-toast-info`, `.xipe-toast-success`)
- Step indicator shows 3 dots with active highlighting
- Step labels: "Step 1/3: Pick Colors", "Step 2/3: Annotate Roles", "Step 3/3: Create Theme"
- Next/Back navigation buttons functional

---

## Notes

- Color picking was tested via programmatic canvas pixel read + data store push (the click handler requires real user mouse events which can't be fully simulated via MCP dispatch)
- Offscreen canvas correctly loaded test screenshot data and returned accurate pixel values
- The toolbar successfully injected into github.com without CSP errors
