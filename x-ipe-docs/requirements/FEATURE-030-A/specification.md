# Feature Specification: UIUX Reference Tab & Console Integration

> Feature ID: FEATURE-030-A
> Version: v1.0
> Status: Refined
> Last Updated: 02-13-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 02-13-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| UIUX Reference Tab (light) | HTML | [mockups/uiux-reference-tab-v2.html](mockups/uiux-reference-tab-v2.html) | Light editorial theme — tab UI with URL input, auth toggle, instructions, Go to Reference button | current |
| UIUX Reference Tab (dark) | HTML | [mockups/uiux-reference-tab-v1.html](mockups/uiux-reference-tab-v1.html) | Dark glassmorphism alternative | outdated — use as directional reference only |

> **Note:** UI/UX requirements and acceptance criteria below are derived from the mockup marked as "current" (v2 light theme).
> The v1 dark mockup is outdated; use as directional reference only.

## Overview

FEATURE-030-A adds a **UIUX Reference** tab as the third idea creation method in the Workplace panel, alongside Compose and Upload. The tab provides a form for entering a target web page URL, an optional authentication prerequisite URL (collapsible), extra instructions for the agent, and a "Go to Reference" button.

When the user clicks "Go to Reference," the app triggers a **console-first flow**: it finds an idle terminal session (or creates a new one), auto-types a `uiux-reference` prompt using the template from `copilot-prompt.json`, and the user presses Enter to start the agent. This feature is the **entry point** for the entire UIUX Reference workflow — the agent skill and toolbar injection (FEATURE-030-B) handles everything after the prompt is submitted.

**Target users:** X-IPE users who want to reference external web pages for design inspiration during ideation.

## User Stories

| ID | Story | Priority |
|----|-------|----------|
| US-1 | As a user, I want to see a "UIUX Reference" tab in the Workplace idea panel, so that I can start a new idea by referencing an external web page. | P0 |
| US-2 | As a user, I want to enter a target URL and click "Go to Reference," so that the agent opens the page and lets me pick design elements. | P0 |
| US-3 | As a user, I want to optionally specify an authentication URL, so that I can reference pages that require login. | P1 |
| US-4 | As a user, I want to provide extra instructions for the agent, so that it knows what aspects of the page to focus on. | P1 |
| US-5 | As a user, I want to see a flow preview explaining what happens next, so that I understand the console-first workflow. | P2 |

## Acceptance Criteria

### Tab Navigation

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-1 | User is in Workplace idea creation panel | User sees the tab bar | Three tabs visible: Compose, Upload, UIUX Reference. UIUX Reference tab shows a "NEW" badge (pulsing animation). |
| AC-2 | User is on any tab | User clicks "UIUX Reference" tab | Tab becomes active (underline indicator animates in). UIUX Reference pane fades in (0.35s fadeSlideIn). Previous pane hides. |
| AC-3 | User is on UIUX Reference tab | User clicks another tab (Compose/Upload) | UIUX Reference pane hides. Other tab's pane appears. Form state is preserved (not cleared). |
| AC-4 | UI layout is rendered | Visual comparison | UI layout MUST match the approved mockup (uiux-reference-tab-v2.html) for the tab bar and reference pane. |

### URL Input

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-5 | UIUX Reference tab is active | User sees the form | "Target Page URL" field is visible with globe icon prefix, placeholder "https://example.com/page-to-reference". Field is required. |
| AC-6 | URL field is empty | User clicks "Go to Reference" | Button does not trigger console flow. URL field shows validation error (red border). |
| AC-7 | URL field has invalid URL | User clicks "Go to Reference" | Validation error shown. Must be a valid URL format (starts with http:// or https://). |
| AC-8 | URL field has valid URL | User focuses the field | Border changes to accent color (#3730a3) with 3px glow shadow. Background changes to white. |

### Authentication Prerequisite

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-9 | UIUX Reference tab is active | User sees the form | "Authentication Prerequisite" section is collapsed by default. Marked as "(optional)". |
| AC-10 | Auth section is collapsed | User clicks "Authentication Prerequisite" button | Section expands with slide animation (0.3s). Chevron icon rotates 90°. Auth URL input and hint message become visible. |
| AC-11 | Auth section is expanded | User clicks the button again | Section collapses. Chevron rotates back. Auth URL input hides. |
| AC-12 | Auth section is expanded | User sees auth hint | Info message displayed: explains that the agent will open the auth URL first, user logs in, then the agent redirects to the target page. |

### Extra Instructions

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-13 | UIUX Reference tab is active | User sees the form | "Extra Instructions" textarea is visible, marked "(optional)", with placeholder text guiding the user. |
| AC-14 | User types in instructions textarea | Textarea receives input | Text is preserved across tab switches. Textarea is resizable vertically (min-height: 76px). |

### Go to Reference Button & Console Integration

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-15 | Valid URL entered | User clicks "Go to Reference" | Button shows loading state: spinner icon + "Opening console..." text. Background changes to light accent. |
| AC-16 | Loading state active | Console integration executes | App finds an idle terminal session. If no idle session exists, creates a new terminal session. |
| AC-17 | Session found/created | Prompt is auto-typed | Prompt auto-typed into console: `copilot execute uiux-reference --url {url}` (+ `--auth-url {auth_url}` if provided, + `--extra "{instructions}"` if provided). Typing uses realistic simulation (30-80ms delays). |
| AC-18 | Prompt auto-typed | Button updates | Button shows success state: checkmark icon + "Console ready — press Enter" text. Background changes to emerald green (#047857). |
| AC-19 | Success state shown | After 4 seconds | Button resets to idle state: external link icon + "Go to Reference" text. |
| AC-20 | Button is idle | User hovers | Button lifts (translateY -1px), shadow enhances, background lightens slightly. |

### Flow Preview

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-21 | UIUX Reference tab is active | User sees the form bottom | Flow preview section visible below the button, showing 4 steps: "Enter URL" → "Console Opens" → "Agent Navigates" → "Pick Elements". Each step has an icon and label. Steps connected with arrow indicators. |

### Visual Consistency

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-22 | Page is rendered | Visual comparison | Visual styling (colors, spacing, typography) MUST be consistent with mockup (uiux-reference-tab-v2.html). Fraunces serif for display, Outfit sans for body. Warm cream background (#f8f6f1). Deep indigo accent (#3730a3). |
| AC-23 | Page is rendered | Interactive elements check | All interactive elements shown in mockup (uiux-reference-tab-v2.html) MUST be present and functional: tab switching, auth toggle, input focus states, button state transitions. |

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | "UIUX Reference" tab added as third tab in Workplace idea creation panel, after Compose and Upload | P0 |
| FR-2 | Tab shows "NEW" badge with pulsing animation (removable via config after launch period) | P2 |
| FR-3 | URL input field with `type="url"`, required validation, globe icon prefix | P0 |
| FR-4 | URL validation: must start with `http://` or `https://`; show red border on invalid | P0 |
| FR-5 | Collapsible "Authentication Prerequisite" section, collapsed by default, with chevron rotation animation | P1 |
| FR-6 | Auth URL input field with key icon prefix, visible only when section is expanded | P1 |
| FR-7 | Auth hint info message explaining the authentication flow (agent opens auth URL → user logs in → redirect to target) | P1 |
| FR-8 | "Extra Instructions" textarea, optional, resizable vertically, min-height 76px | P1 |
| FR-9 | "Go to Reference" button with 3-state transition: idle → loading (1.5s) → success (2.5s) → reset to idle | P0 |
| FR-10 | Console integration: find idle terminal session using existing session management API | P0 |
| FR-11 | Console integration: if no idle session, create new terminal session | P0 |
| FR-12 | Auto-type prompt from `copilot-prompt.json` (key: `uiux-reference`) with realistic typing simulation (30-80ms per character) | P0 |
| FR-13 | Prompt format: `copilot execute uiux-reference --url {url} [--auth-url {auth_url}] [--extra "{instructions}"]` | P0 |
| FR-14 | Form state preserved across tab switches (URL, auth URL, instructions not cleared) | P1 |
| FR-15 | Flow preview section showing 4-step process: Enter URL → Console Opens → Agent Navigates → Pick Elements | P2 |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Tab switch animation completes within 350ms (fadeSlideIn) | P1 |
| NFR-2 | Button state transitions smooth: idle→loading (immediate), loading→success (1.5s), success→reset (2.5s) | P1 |
| NFR-3 | Auth section expand/collapse animation: 300ms with cubic-bezier easing | P1 |
| NFR-4 | Input focus transitions: 250ms border color + shadow change | P2 |
| NFR-5 | Console session detection completes within 500ms | P1 |
| NFR-6 | Prompt auto-typing completes within 3 seconds for typical prompt length | P1 |

## UI/UX Requirements

### Component Inventory (from mockup)

| Component | Element | Details |
|-----------|---------|---------|
| Tab Bar | 3 tabs (Compose, Upload, UIUX Reference) | Flex row, equal width, 14px padding, icons + labels |
| Tab Indicator | Active underline | `::after` pseudo-element, scaleX animation, accent color |
| NEW Badge | Pill badge on UIUX Reference tab | Pulsing opacity animation (2.5s infinite) |
| URL Input | Text input with icon prefix | Globe icon, 38px left padding, `type="url"` |
| Auth Toggle | Collapsible button | Shield icon + chevron, 90° rotation on expand |
| Auth URL Input | Text input with icon prefix | Key icon, visible only when expanded |
| Auth Hint | Info message | Amber info icon, muted text |
| Instructions Textarea | Multi-line text input | Resizable vertical, min-height 76px |
| Go to Reference Button | Primary action button | 3-state: idle/loading/success, full width |
| Flow Preview | Step indicator | 4 steps with icons, arrows between, accent background |

### Color System

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-page` | #f8f6f1 | Page background (warm cream) |
| `--bg-panel` | #ffffff | Panel/card background |
| `--bg-input` | #f4f2ed | Input background |
| `--accent` | #3730a3 | Primary accent (deep indigo) |
| `--accent-light` | #4f46e5 | Accent hover/light variant |
| `--text-primary` | #1a1a2e | Primary text |
| `--text-secondary` | #4a4a5c | Secondary text |
| `--text-muted` | #8e8e9f | Muted/helper text |
| `--emerald` | #047857 | Success state |
| `--danger` | #b91c1c | Error/validation state |
| `--border` | #e0dcd4 | Default border |
| `--border-focus` | #3730a3 | Focus border |

### Typography

| Element | Font | Size | Weight | Extras |
|---------|------|------|--------|--------|
| Display | Fraunces | 30px | 600 | italic, letter-spacing -0.02em |
| Tab labels | Outfit | 13px | 500 | — |
| Input text | Outfit | 13px | 400 | — |
| Labels | Outfit | 11px | 600 | uppercase, letter-spacing 0.08em |
| Placeholder | Outfit | 13px | 400 | color: --text-placeholder |

### Spacing & Radius

| Token | Value |
|-------|-------|
| `--radius-sm` | 6px |
| `--radius-md` | 10px |
| `--radius-lg` | 14px |
| `--radius-xl` | 20px |
| Input padding | 12px 14px |
| Section gap | 20px |

### Staggered Entrance Animations

| Element | Delay | Duration |
|---------|-------|----------|
| Tab bar | 0s | 0.5s |
| First section | 0.1s | 0.5s |
| Middle sections | 0.15s | 0.5s |
| Action button | 0.3s | 0.5s |

## Dependencies

### Internal

| Dependency | Type | Description |
|------------|------|-------------|
| FEATURE-008 (Workplace) | Soft | Tab placement in existing Workplace idea creation panel. Uses existing panel layout. |
| FEATURE-005 / FEATURE-029 (Console) | Soft | Console session finding/creation API. Uses existing session management. |

### External

| Dependency | Type | Description |
|------------|------|-------------|
| `copilot-prompt.json` | Config | Must have a `uiux-reference` key with the prompt template for auto-typing. |
| Google Fonts | CDN | Fraunces and Outfit fonts loaded from Google Fonts CDN. |

## Business Rules

| ID | Rule |
|----|------|
| BR-1 | Target URL is required; the form cannot be submitted without a valid URL. |
| BR-2 | Authentication URL is optional; when omitted, the agent skips the auth prerequisite step. |
| BR-3 | Extra instructions are optional; when omitted, the `--extra` flag is not included in the prompt. |
| BR-4 | Only one "Go to Reference" flow can be active at a time per browser tab. Clicking the button while loading/success state is active has no effect. |
| BR-5 | The prompt template in `copilot-prompt.json` is the single source of truth for the auto-typed command format. |
| BR-6 | Form state is preserved across tab switches — switching away and back does not clear entered data. |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| No idle terminal session available | Create a new terminal session, then auto-type prompt. |
| Maximum terminal sessions reached (10) | Show toast notification per FEATURE-029 session limit. Do not create new session. Button resets to idle. |
| `copilot-prompt.json` missing or malformed | Fall back to hardcoded default prompt template. Log warning to console. |
| User navigates away from Workplace during loading | Console prompt still gets typed. Button state resets on return. |
| URL with special characters (query params, fragments) | URL is passed as-is in the prompt. Shell-escape quotes in `--extra` parameter. |
| Very long extra instructions (>1000 chars) | Truncate at 1000 characters with "..." suffix. Show character counter when approaching limit. |
| Auth URL same as target URL | Proceed normally — agent treats auth URL as prerequisite regardless. |
| Browser offline | Show error message: "Unable to reach console. Check your connection." Button resets. |

## Out of Scope

- Agent skill execution (FEATURE-030-B handles everything after prompt submission)
- Toolbar injection into target page (FEATURE-030-B)
- Reference data collection and storage (FEATURE-030-B)
- MCP server communication (FEATURE-033)
- Multiple simultaneous reference sessions from the same tab
- Drag-and-drop URL input
- URL history/favorites

## Technical Considerations

- Tab component should follow existing Compose/Upload tab pattern in Workplace for consistency
- Console integration reuses existing session management API (same as Copilot button in FEATURE-008)
- `copilot-prompt.json` is read via existing config API (`GET /api/config/copilot-prompt`)
- Button state machine: idle → loading → success → idle (no error state in v1; errors fall through to reset)
- Form validation uses HTML5 `type="url"` with `required` attribute, supplemented by custom validation for http/https prefix
- Auth section uses CSS `display: none/block` toggle with JS class manipulation (not `<details>` element) for animation control
- "NEW" badge can be removed via a feature flag or config setting after initial launch period

## Open Questions

None — all clarifications resolved during requirement gathering and feature breakdown.
