# Examples: UIUX Reference Tool

## Example 1: Basic URL Reference

**Trigger:** `copilot execute uiux-reference --url https://stripe.com/pricing`

**Agent Flow:**
1. Navigate to `https://stripe.com/pricing`
2. Inject toolbar → panel appears at top-right
3. User picks 4 colors from pricing cards, highlights 2 CTA buttons
4. User clicks "Send References"
5. Agent receives data: 4 colors, 2 elements
6. Agent takes screenshots for each element
7. Agent calls `save_uiux_reference` → session saved
8. Output: "Reference data saved — 4 colors, 2 elements from https://stripe.com/pricing. Session: ref-session-001.json"

## Example 2: With Authentication

**Trigger:** `copilot execute uiux-reference --url https://app.figma.com/file/xyz --auth-url https://www.figma.com/login`

**Agent Flow:**
1. Navigate to `https://www.figma.com/login`
2. Inform user: "Please log in. I'll detect when authentication completes."
3. User logs in → URL changes to `https://www.figma.com/`
4. Agent detects URL change → navigates to `https://app.figma.com/file/xyz`
5. Inject toolbar → user collects references
6. Save via MCP

## Example 3: With Extra Instructions

**Trigger:** `copilot execute uiux-reference --url https://linear.app --extra "Focus on the sidebar navigation colors and the issue card layout"`

**Agent Flow:**
1. Navigate to `https://linear.app`
2. Inject toolbar
3. Inform user: "Toolbar injected. Focus on the sidebar navigation colors and the issue card layout."
4. User collects references following the guidance
5. Save via MCP
