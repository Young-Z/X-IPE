# Feature Specification: UIUX Reference Agent Skill & Toolbar

> Feature ID: FEATURE-030-B
> Version: v2.0
> Status: Refined
> Last Updated: 02-14-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v2.0 | 02-14-2026 | Complete toolbar redesign — two-mode wizard shell with auto-collapse, mode switcher, toast system, new data schema, bi-directional comms, optimized injection. All v1.x user stories and ACs deprecated. | [CR-002](./CR-002.md) |
| v1.1 | 02-13-2026 | ~~Eyedropper cursor, expandable lists, hover-highlight, screenshot accuracy, post-send reset~~ (deprecated by v2.0) | [CR-001](./CR-001.md) |
| v1.0 | 02-13-2026 | ~~Initial specification~~ (deprecated by v2.0) | - |

## Linked Mockups

| Mockup | Type | Path | Description | Status |
|--------|------|------|-------------|--------|
| Toolbar v2.0 (IDEA-019) | HTML | [mockups/toolbar-v2-v1.html](mockups/toolbar-v2-v1.html) | Two-mode wizard toolbar: hamburger auto-collapse, mode switcher tabs, toast notifications. Demo controls for Theme/Mockup/Magnifier/SmartSnap/Toast states. | current |
| Toolbar v1.1 (CR-001) | HTML | [mockups/injected-toolbar-v3.html](mockups/injected-toolbar-v3.html) | v1.1 toolbar with eyedropper, expandable lists | outdated |
| Toolbar v1.0 (light) | HTML | [mockups/injected-toolbar-v2.html](mockups/injected-toolbar-v2.html) | Frosted-glass toolbar panel | outdated |
| Toolbar v1.0 (dark) | HTML | [mockups/injected-toolbar-v1.html](mockups/injected-toolbar-v1.html) | Dark glassmorphism alternative | outdated |

> **Note:** UI/UX requirements and ACs are derived from the v2.0 mockup (toolbar-v2-v1.html).

## Overview

FEATURE-030-B v2.0 is the **toolbar shell and infrastructure** for the redesigned UIUX Reference system. It replaces the v1.x standalone Color Picker and Element Highlighter with a two-mode wizard framework accessed through a hamburger menu.

This feature provides the shared foundation that both modes depend on: the injectable panel with auto-collapse behavior, mode switching UI, toast notification system, new data schema, bi-directional agent communication channel, and optimized injection. The actual mode-specific logic lives in FEATURE-030-B-THEME (Catch Design Theme) and FEATURE-030-B-MOCKUP (Copy Design as Mockup).

**Target users:** CLI agents executing the `uiux-reference` skill, and users interacting with the injected toolbar on external web pages.

## User Stories

| ID | Story | Priority |
|----|-------|----------|
| US-1 | As an agent, I want to open a target URL in Chrome via Chrome DevTools MCP, so that the user can interact with the reference page. | P0 |
| US-2 | As an agent, I want to handle an authentication prerequisite URL flow, so that users can reference pages that require login. | P1 |
| US-3 | As an agent, I want to inject an optimized toolbar IIFE that loads perceptibly faster than v1.1, so that the user can start working sooner. | P0 |
| US-4 | As a user, I want the toolbar to appear as a small hamburger icon that does not obstruct the page, so that I have maximum screen space. | P0 |
| US-5 | As a user, I want the panel to expand on hover and auto-collapse 2 seconds after I move away, so that it stays out of my way during active tool use. | P0 |
| US-6 | As a user, I want to drag the hamburger icon to reposition the toolbar, so that it does not cover content I need to inspect. | P1 |
| US-7 | As a user, I want to switch between "Catch Theme" and "Copy Mockup" modes via tabs, so that I can use the right workflow. | P0 |
| US-8 | As a user, I want toast notifications showing progress, success, and error states, so that I know what is happening during async operations. | P0 |
| US-9 | As a user, I want data collected in one mode to persist when I switch to the other mode, so that I do not lose my work. | P1 |
| US-10 | As an agent, I want to send commands to the toolbar via __xipeRefCommand and receive data via __xipeRefReady, so that I can request deeper captures during analysis. | P0 |

## Acceptance Criteria

### Page Navigation & Auth

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-1 | Agent receives uiux-reference prompt with --url | Agent executes skill | Target URL opened in Chrome via navigate_page. Page loads completely (wait for load event or 30s timeout). |
| AC-2 | Prompt includes --auth-url | Agent executes skill | Auth URL opened first. Agent polls URL every 3s. When URL changes away from auth domain, navigates to target URL. |
| AC-3 | User on auth page | 5 minutes elapse without URL change | Agent prompts: "Authentication timeout." |
| AC-4 | Target URL fails to load | Agent detects error | Agent reports error, skill terminates gracefully. |

### Toolbar Injection & Performance

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-5 | Target page loaded | Agent injects toolbar IIFE | Toolbar hamburger icon appears within 500ms. IIFE payload is minified (no uncompressed whitespace or comments). |
| AC-6 | Toolbar injected | Performance check | Injection completes faster than v1.1 despite larger feature set. Non-critical resources (fonts, icons) load lazily after initial render. |
| AC-7 | Toolbar injected | Page content check | Toolbar does NOT break page layout, styling, or JavaScript. All styles scoped with .xipe-* prefix. |
| AC-8 | Toolbar injected on page with high z-index elements | z-index check | Toolbar uses z-index: 2147483647 and remains on top. |
| AC-9 | Toolbar injected | Page scrolled or resized | Toolbar remains fixed (position: fixed). |

### Hamburger Menu & Auto-Collapse

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-10 | Toolbar first injected | Initial state | Only hamburger icon visible (collapsed). Circular button at right side of viewport. |
| AC-11 | Toolbar collapsed | User hovers over hamburger icon | Panel expands showing: header (X-IPE Reference + status), mode switcher tabs, active mode content area, toast area. Animation <=350ms. |
| AC-12 | Panel expanded | User moves mouse away from panel | After 2 seconds, panel auto-collapses to hamburger. Animation <=350ms. |
| AC-13 | Panel expanded | User moves mouse back within 2s delay | Auto-collapse timer resets. Panel stays expanded. |
| AC-14 | Panel expanded, tool active on page | User moves mouse to page to use tool | Panel auto-collapses after 2s, leaving space for active tool interaction. |
| AC-15 | Toolbar collapsed | User drags hamburger icon | Position updates in real-time. New position persists until page reload. |

### Mode Switcher

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-16 | Panel expanded | User views mode tabs | Two tabs visible: "Catch Theme" (palette icon) and "Copy Mockup" (layers icon). Active tab visually distinguished. |
| AC-17 | Catch Theme active | User clicks Copy Mockup tab | Mode switches. Content area updates. All Theme mode data preserved in shared store. |
| AC-18 | Copy Mockup active with components | User switches to Catch Theme | Theme mode UI shown. Components remain in __xipeRefData.components[]. |
| AC-19 | Fresh injection | Panel first expands | Default mode is "Catch Theme" (first tab). |

### Toast Notification System

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-20 | Panel visible | Toast triggered via JS API | Toast appears at bottom of panel with icon: info, progress (spinner), success, error. |
| AC-21 | Toast visible | 4 seconds elapse (non-error) | Toast auto-dismisses with fade-out. Error toasts persist until manual dismiss. |
| AC-22 | Multiple toasts triggered | Sequential display | Toasts stack (newest bottom). Max 3 visible; oldest dismissed. |
| AC-23 | Agent sends command | Toolbar processes it | Appropriate toast shown (e.g., "Analyzing..." with spinner). |

### Data Schema

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-24 | Toolbar injected | Data store initialized | window.__xipeRefData created: { mode, colors: [], components: [], design_tokens: null }. |
| AC-25 | Color added by Theme mode | Data stored | Entry: id, hex, rgb, hsl, source_selector, role (default empty), context. |
| AC-26 | Component added by Mockup mode | Data stored | Entry: id, selector, tag, bounding_box, screenshot_dataurl, html_css: { level, computed_styles, outer_html }, instruction, agent_analysis: { confidence: {}, additional_captures: [] }. |
| AC-27 | Data store has entries | Mode field | mode reflects currently active mode (theme or mockup). |

### Bi-Directional Communication

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-28 | Toolbar has data, user triggers send | __xipeRefReady signal | __xipeRefReady set to true. Agent polls and detects within 3s. Agent reads __xipeRefData. |
| AC-29 | Agent needs deeper capture | Agent writes __xipeRefCommand | Toolbar polls every 1s. On command: execute action (e.g., deep_capture for comp-001), clear command, set __xipeRefReady when done. |
| AC-30 | Agent writes malformed command | Toolbar reads it | Warning toast shown, command cleared. No crash. |
| AC-31 | Agent saves data via MCP | save_uiux_reference call | Data saved using new schema. Old v1.x schema not accepted. |

### CSS Scoping & Isolation

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-32 | Toolbar injected on any page | CSS inspection | All toolbar CSS rules use .xipe-* prefix. No global styles applied. |
| AC-33 | Page has CSP restrictions | Toolbar injection | Toolbar degrades gracefully. Toast: "Some styling may be limited due to page security policy." |

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Open target URL via Chrome DevTools MCP navigate_page. Wait for load event (30s timeout). | P0 |
| FR-2 | If --auth-url provided: open auth URL first, poll URL change every 3s, redirect to target on domain change. 5-minute timeout with user prompt. | P1 |
| FR-3 | Inject toolbar as self-executing IIFE via CDP evaluate_script. Guard double-injection with window.__xipeToolbarInjected flag. | P0 |
| FR-4 | Toolbar IIFE must be minified before injection (strip comments, collapse whitespace). Non-critical resources (fonts, icons) loaded lazily after initial render. | P0 |
| FR-5 | Render hamburger icon as circular button (52x52px) at right side of viewport (20px from right edge, vertically centered). Show X-IPE branding. | P0 |
| FR-6 | On hover over hamburger: expand panel (280px wide) with slide animation (<=350ms). Show header, mode tabs, content area, toast area. | P0 |
| FR-7 | On mouseleave from panel: start 2-second timer. On timeout: collapse to hamburger (<=350ms). Cancel timer if mouse re-enters. | P0 |
| FR-8 | Hamburger icon is draggable via mousedown/mousemove/mouseup. Constrain to viewport bounds. | P1 |
| FR-9 | Mode switcher: two tab buttons (Catch Theme with palette icon, Copy Mockup with layers icon). Clicking switches content area. Active tab highlighted. | P0 |
| FR-10 | Default mode on first expand: Catch Theme. | P0 |
| FR-11 | Toast API: window.__xipeToast(message, type, duration). Types: info, progress, success, error. Default 4s. Errors require manual dismiss. Max 3 visible. | P0 |
| FR-12 | Initialize window.__xipeRefData with schema: { mode: "theme", colors: [], components: [], design_tokens: null }. Shared across both modes. | P0 |
| FR-13 | __xipeRefReady flag: set true on send action. Agent polls every 3s. After read, toolbar resets to false. | P0 |
| FR-14 | __xipeRefCommand queue: agent writes { action, target, params }. Toolbar polls every 1s. On match: execute, clear, set __xipeRefReady when done. Supported: deep_capture, reset. | P0 |
| FR-15 | All CSS scoped with .xipe-* prefix. position: fixed, z-index: 2147483647. No page interference. | P0 |
| FR-16 | Mode content area provides extension points (DOM containers) for FEATURE-030-B-THEME and FEATURE-030-B-MOCKUP to render their wizard UI. | P0 |
| FR-17 | Agent saves via FEATURE-033 MCP save_uiux_reference. New schema only. | P0 |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | Hamburger icon visible within 500ms of injection. Full panel interactive within 1s. | P0 |
| NFR-2 | Injected IIFE smaller than v1.1 unminified (~30KB). Target: <15KB minified. | P0 |
| NFR-3 | All CSS scoped with .xipe-* prefix. No global style leakage. | P0 |
| NFR-4 | Expand/collapse animations at 60fps (<=16ms per frame). | P1 |
| NFR-5 | Fonts loaded lazily. Toolbar functional with system fonts before web fonts arrive. | P1 |
| NFR-6 | Auto-collapse timer accurate to +/-200ms of 2-second target. | P1 |
| NFR-7 | __xipeRefCommand polling: 1s interval. __xipeRefReady polling: 3s max detection latency. | P0 |
| NFR-8 | CDP resilience: 3 reconnection retries on drop. Save partial data on failure. | P1 |
| NFR-9 | No memory leaks from event listeners. Cleanup on toolbar removal. | P1 |

## UI/UX Requirements

### Layout

- **Collapsed state**: Circular hamburger button (52x52px), right side, vertically centered. X-IPE branding.
- **Expanded state**: 280px wide, max-height 80vh with scroll. Dark chrome (#0f172a), emerald accent (#10b981).
- **Header**: "X-IPE Reference" + status dot.
- **Mode tabs**: Two equal-width buttons. Active: accent background. Inactive: subtle border.
- **Content area**: Scrollable, rendered by active mode sub-feature.
- **Toast area**: Fixed bottom of panel. Slide-in animation.

### Interactions

- Hover expand: panel expands on mouseenter of hamburger.
- Auto-collapse: 2s after mouseleave. Timer resets on re-entry.
- Drag: click-and-drag hamburger. Constrained to viewport.
- Mode switch: click tab. Instant swap.

### Visual Reference

UI must match approved mockup (toolbar-v2-v1.html):
- Dark panel with emerald accents
- Font stack: Outfit (headings), Space Mono (code), DM Sans (body) loaded lazily
- Toast styles: rounded pill with icon + message + auto-dismiss progress

## Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-030-A | Internal | Tab & Console Integration (entry point) |
| FEATURE-033 | Internal | App-Agent Interaction MCP (save_uiux_reference) |
| Chrome DevTools MCP | External | CDP for navigation, injection, screenshots |
| FEATURE-030-B-THEME | Consumer | Renders Catch Theme wizard into content area |
| FEATURE-030-B-MOCKUP | Consumer | Renders Copy Mockup wizard into content area |

## Business Rules

| ID | Rule |
|----|------|
| BR-1 | One mode active at a time. Mode switch preserves all collected data. |
| BR-2 | Auto-collapse applies regardless of active mode. Active tools continue working when collapsed. |
| BR-3 | Each mode has its own send action (Create Theme / Generate Mockup). No unified Send. |
| BR-4 | New schema only. No v1.x backward compatibility. |
| BR-5 | Auth flow unchanged from v1.1. |

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|------------------|
| Hover hamburger while page loading | Toolbar expands normally. Page load unaffected. |
| Drag near viewport edge | Position constrained (min 10px from any edge). |
| Auto-collapse timer + mouse re-entry | Timer cancelled, panel stays expanded. |
| Mode switch during active tool | Tool deactivated. Collected data preserved. Resume on switch back. |
| CSP blocks inline styles | Warning toast. Degrade gracefully with system fonts, no animations. |
| Page reloads | Toolbar lost. Agent must re-inject. __xipeRefData lost (session-based). |
| __xipeRefCommand while collapsed | Toolbar still polls. Executes command. Shows toast on next expand. |
| Unknown __xipeRefCommand action | Warning toast, clear command. No crash. |
| Rapid mode switches | Instant. Last switch wins. No queuing. |

## Out of Scope

- Color picking logic (FEATURE-030-B-THEME)
- Component selection logic (FEATURE-030-B-MOCKUP)
- Brand theme generation (brand-theme-creator skill)
- Mockup generation (downstream skill)
- Agent analysis rubric (FEATURE-030-B-MOCKUP)
- Screenshot comparison / iterative validation (FEATURE-030-B-MOCKUP)
- Keyboard shortcuts (mouse-only per clarification)
- Cross-origin iframe content

## Technical Considerations

- Toolbar IIFE structured with extension points (DOM containers + registration functions) for sub-features.
- Minification: strip comments, collapse whitespace, shorten internals. Consider build-time step or template-time compression.
- Fonts: use font-display: swap to avoid FOIT. Load after initial render.
- __xipeRefCommand handles one command at a time. Agent waits for __xipeRefReady before next command.
- CSS selector generation handles edge cases: no classes, dynamic class names (exclude), deep nesting.
- 2-second auto-collapse uses setTimeout. Clear on mouseenter to prevent race conditions.
- Only __xipe* globals exposed (xipeRefData, xipeRefReady, xipeRefCommand, xipeToolbarInjected, xipeToast).

## Open Questions

None — all clarifications resolved during CR-002 requirement gathering.
