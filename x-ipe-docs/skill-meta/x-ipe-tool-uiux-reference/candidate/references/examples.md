# Examples: UIUX Reference Tool v3.0

## Example 1: Catch Design Theme

**Trigger:** `copilot execute uiux-reference --url https://stripe.com/pricing`

**Agent Flow:**
1. Navigate to `https://stripe.com/pricing`
2. Read `toolbar.compressed.json`, inject via 2 `evaluate_script` calls
3. User selects "Catch Design Theme" mode
4. User picks 4 colors with magnifier, assigns roles (primary, secondary, accent, neutral)
5. User clicks "Create Theme" → `__xipeRefReady` becomes true
6. Agent reads `result.mode === "theme"`, extracts annotated colors
7. Agent calls `save_uiux_reference` with colors and roles
8. Agent invokes `x-ipe-tool-brand-theme-creator` with annotated colors
9. Output: "Theme created — 4 colors extracted from https://stripe.com/pricing"

## Example 2: Copy Design as Mockup (Analyze + Generate)

**Trigger:** `copilot execute uiux-reference --url https://linear.app --extra "Focus on the sidebar navigation"`

**Agent Flow:**
1. Navigate to `https://linear.app`, inject toolbar via 2-call compressed injection
2. User selects "Copy Design as Mockup" mode, selects 2 areas via smart-snap
3. User clicks "Analyze" → `result.action === "analyze"`
4. Agent takes viewport screenshot, crops each area by bounding_box
5. Agent discovers all elements in each bounding_box via `evaluate_script`
6. Agent enriches: element_name, purpose, relationships, mimic_tips
7. Agent downloads resources (fonts, images) via page-context fetch
8. Agent evaluates 6-dimension rubric, persists as `referenced-elements.json`
9. Agent re-enables buttons, resumes polling
10. User clicks "Generate Mockup" → `result.action === "generate"`
11. Agent generates `mockup-v1.html` from referenced-elements.json, validates at 99% target
12. Output: "Mockup mockup-v1.html generated — 2 areas from https://linear.app"

## Example 3: With Authentication

**Trigger:** `copilot execute uiux-reference --url https://app.figma.com/file/xyz --auth-url https://www.figma.com/login`

**Agent Flow:**
1. Navigate to `https://www.figma.com/login`
2. Inform user: "Please log in. I'll detect when authentication completes."
3. User logs in → URL changes away from auth_url
4. Agent detects URL change → navigates to `https://app.figma.com/file/xyz`
5. Inject toolbar via 2-call compressed injection
6. User collects references (theme or mockup mode)
7. Save via `save_uiux_reference` MCP tool

## Example 4: ARIA Workaround for Screenshots (LL-001)

**Scenario:** User selects a generic `<div>` without ARIA role in mockup mode.

**Agent Flow:**
1. Agent needs element screenshot but `<div>` has no UID in a11y snapshot
2. Agent adds temporary `role="region"` + `aria-label="xipe-target-element"` via `evaluate_script`
3. Agent calls `take_snapshot()` to refresh a11y tree
4. Agent finds node with `aria-label="xipe-target-element"` → gets UID
5. Agent calls `take_screenshot(uid: found_uid)` for element-level capture
6. Agent removes temporary ARIA attributes via `evaluate_script`
