# Feature Specification: Browser Simulator & Proxy

> Feature ID: FEATURE-022-A  
> Version: v1.0  
> Status: Refined  
> Last Updated: 01-28-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 01-28-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description |
|--------|------|------|-------------|
| Browser Simulator | HTML | [browser-simulator.html](mockups/browser-simulator.html) | Full mockup showing browser simulator with URL bar, toolbar, and viewport |
| Original (Ideas) | HTML | [uiux-feedback-v1.html](../../ideas/005.%20Feature-UIUX%20Feedback/mockups/uiux-feedback-v1.html) | Source mockup in ideas folder |

> **Note:** UI/UX requirements below are derived from this mockup. This is the MVP feature - browser simulator and proxy only. Element inspector and feedback panel are separate features (FEATURE-022-B, C, D).

---

## Overview

The Browser Simulator & Proxy feature provides a localhost web page viewer within X-IPE Workplace. Users can enter a localhost URL, and the system proxies the request through the backend to fetch HTML content, which is then displayed in an embedded viewport. This enables viewing locally running web applications (dev servers) without leaving the X-IPE interface.

**This is the MVP (Minimum Viable Product)** for the UI/UX Feedback System. It provides the foundational infrastructure - the ability to load and view localhost pages. Subsequent features (Element Inspector, Feedback Capture, Storage) build upon this capability.

**Key Value Proposition:**
- View localhost dev server output directly in X-IPE
- No CORS issues - backend proxy handles cross-origin requests
- Foundation for element inspection and feedback capture (FEATURE-022-B, C, D)

---

## User Stories

- As a **developer**, I want to **view my localhost dev server within X-IPE**, so that **I can see my application without switching to an external browser**.

- As a **developer**, I want to **enter any localhost port in the URL bar**, so that **I can view applications running on different ports (3000, 5173, 8080, etc.)**.

- As a **developer**, I want to **see clear error messages when my dev server isn't running**, so that **I know to start my server before viewing**.

- As a **developer**, I want to **refresh the page view**, so that **I can see updated content after making changes**.

- As a **developer**, I want to **be prevented from loading external URLs**, so that **I understand this tool is for localhost development only**.

---

## Acceptance Criteria

### Navigation & Layout

- [ ] AC-1: UI/UX Feedback view is accessible from Workplace submenu in sidebar
- [ ] AC-2: View uses 3-column layout: sidebar (260px), browser simulator (flex-1), feedback panel (380px, empty/placeholder)
- [ ] AC-3: Browser simulator panel has browser chrome styling (dots, URL bar)

### URL Bar & Navigation

- [ ] AC-4: URL bar displays text input with placeholder "http://localhost:3000"
- [ ] AC-5: "Go" button next to URL input triggers page load
- [ ] AC-6: Pressing Enter in URL input triggers page load
- [ ] AC-7: URL bar accepts any localhost port (e.g., localhost:3000, localhost:5173, 127.0.0.1:8080)
- [ ] AC-8: URL bar auto-prepends "http://" if protocol missing

### Toolbar

- [ ] AC-9: Toolbar appears below URL bar with light background
- [ ] AC-10: Refresh button in toolbar reloads current URL
- [ ] AC-11: Toolbar shows placeholder for future "Inspect" toggle (disabled/hidden in MVP)

### Browser Viewport

- [ ] AC-12: Viewport displays proxied HTML content in an iframe
- [ ] AC-13: Viewport is responsive to panel size changes
- [ ] AC-14: Viewport has white background with border-radius and shadow
- [ ] AC-15: Loading indicator shows while page is being fetched

### Backend Proxy

- [ ] AC-16: Backend provides `GET /api/proxy?url=<encoded-url>` endpoint
- [ ] AC-17: Proxy only accepts URLs with host `localhost` or `127.0.0.1`
- [ ] AC-18: Proxy returns 400 error for non-localhost URLs with message "Only localhost URLs are supported"
- [ ] AC-19: Proxy fetches target URL and returns HTML content
- [ ] AC-20: Proxy rewrites relative asset paths to absolute paths through proxy
- [ ] AC-21: Proxy strips or modifies CSP headers that would block inline scripts
- [ ] AC-22: Proxy handles CSS `url()` references and rewrites them
- [ ] AC-23: Proxy handles `<script src>`, `<link href>`, `<img src>` relative paths

### Error Handling

- [ ] AC-24: Invalid URL format shows error message in viewport area
- [ ] AC-25: Non-localhost URL shows "Only localhost URLs supported" message
- [ ] AC-26: Connection refused (server not running) shows "Cannot connect to [url]. Is your dev server running?"
- [ ] AC-27: Timeout (>10 seconds) shows "Request timed out" message
- [ ] AC-28: Error states have retry button to attempt reload

### Feedback Panel Placeholder

- [ ] AC-29: Right panel shows placeholder UI with "Feedback panel coming soon" message
- [ ] AC-30: Panel maintains 380px width consistent with mockup

---

## Functional Requirements

### FR-1: Workplace Submenu Integration

**Description:** Add UI/UX Feedback as a submenu item under Workplace in the sidebar navigation.

**Details:**
- Input: Sidebar navigation structure (from FEATURE-008 v1.4)
- Process: Add new route `/uiux-feedback` as second submenu item under Workplace
- Output: Navigable submenu item with appropriate icon

### FR-2: 3-Column Layout Rendering

**Description:** Render the UI/UX Feedback view with three distinct columns.

**Details:**
- Input: Route activation `/uiux-feedback`
- Process: Render CSS Grid layout with fixed sidebar, flexible center, fixed right panel
- Output: `grid-template-columns: 260px 1fr 380px`

### FR-3: URL Input Processing

**Description:** Process and validate URL input from the URL bar.

**Details:**
- Input: User-entered URL string
- Process:
  1. Trim whitespace
  2. If no protocol, prepend "http://"
  3. Parse URL and validate host is localhost or 127.0.0.1
  4. Encode URL for proxy request
- Output: Valid encoded URL or validation error

### FR-4: Localhost Proxy Endpoint

**Description:** Backend endpoint that proxies requests to localhost URLs.

**Details:**
- Input: `GET /api/proxy?url=http%3A%2F%2Flocalhost%3A3000%2F`
- Process:
  1. Decode URL parameter
  2. Validate host is localhost or 127.0.0.1
  3. Fetch HTML from target URL
  4. Rewrite relative asset paths to proxy URLs
  5. Strip restrictive CSP headers
  6. Return modified HTML
- Output: HTML content with rewritten asset paths

### FR-5: Asset Path Rewriting

**Description:** Rewrite relative asset paths in proxied HTML to route through proxy.

**Details:**
- Input: HTML content with relative paths like `<script src="/app.js">`
- Process: Transform to `<script src="/api/proxy?url=http://localhost:3000/app.js">`
- Output: HTML with all assets routed through proxy

**Asset Types to Rewrite:**
- `<script src="...">`
- `<link href="...">`
- `<img src="...">`
- `<a href="...">` (for navigation within simulator)
- CSS `url(...)` references
- `@import` statements

### FR-6: Viewport Rendering

**Description:** Display proxied HTML content in an iframe.

**Details:**
- Input: HTML string from proxy response
- Process: Set iframe `srcdoc` attribute with HTML content
- Output: Rendered page in viewport

### FR-7: Page Refresh

**Description:** Reload the current URL when refresh button is clicked.

**Details:**
- Input: Refresh button click
- Process: Re-fetch current URL through proxy
- Output: Updated viewport content

### FR-8: Error Display

**Description:** Show user-friendly error messages for various failure conditions.

**Details:**
- Input: Error type (invalid URL, connection refused, timeout, etc.)
- Process: Map error type to user-friendly message
- Output: Error displayed in viewport area with retry option

---

## Non-Functional Requirements

### NFR-1: Performance

- **Page load time:** < 3 seconds for typical localhost page (excluding external resources)
- **Proxy response time:** < 500ms for HTML fetch (excluding slow dev servers)
- **URL validation:** < 50ms

### NFR-2: Security

- **Localhost-only:** Proxy MUST reject any non-localhost URL
- **No credential forwarding:** Proxy MUST NOT forward cookies or auth headers to target
- **CSP handling:** Strip headers that would block functionality, but maintain XSS protections

### NFR-3: Reliability

- **Timeout handling:** 10-second timeout for proxy requests
- **Graceful degradation:** Show error UI, never crash or hang

### NFR-4: Compatibility

- **Browser support:** Chrome, Firefox, Edge (latest versions)
- **Device support:** Desktop only (mouse required for future inspector feature)

---

## UI/UX Requirements

### Layout Structure (from Mockup)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              X-IPE                                      │
├──────────┬─────────────────────────────────────────────────┬────────────┤
│ Sidebar  │ Browser Chrome (dots + URL bar + Go)            │ Feedback   │
│ 260px    │─────────────────────────────────────────────────│ Panel      │
│          │ Toolbar (Refresh | Inspect placeholder)         │ 380px      │
│ Workplace│─────────────────────────────────────────────────│            │
│  └─Idea  │                                                  │ "Coming    │
│  └─UIUX ◄│         Browser Viewport                        │  Soon"     │
│          │         (iframe with proxied content)            │            │
│ Files    │                                                  │            │
│ Settings │                                                  │            │
└──────────┴─────────────────────────────────────────────────┴────────────┘
```

### Color Scheme (from theme-default)

| Element | Color Variable | Value |
|---------|---------------|-------|
| Browser chrome background | `--slate-800` | #1e293b |
| URL bar background | `--slate-700` | #334155 |
| URL input text | white | #ffffff |
| Go button | `--color-accent` | #10b981 |
| Toolbar background | `--slate-100` | #f1f5f9 |
| Viewport background | white | #ffffff |
| Viewport shadow | `--shadow-lg` | Complex shadow |

### UI Elements (from Mockup)

**Browser Chrome:**
- Traffic light dots (red #ff5f57, yellow #febc2e, green #28c840)
- URL input with monospace font (JetBrains Mono)
- "Go" button with accent color

**Toolbar:**
- Refresh button with icon
- Inspect toggle (disabled/placeholder for MVP)
- Divider line
- Info text area (right side)

**Viewport:**
- Border radius: 12px (`--radius-lg`)
- Shadow: `--shadow-lg`
- Margin: 16px from edges
- Overflow: hidden (scroll within iframe)

### Error States

**Connection Refused:**
```
┌─────────────────────────────────────┐
│           ⚠️ Connection Failed      │
│                                     │
│  Cannot connect to localhost:3000   │
│  Is your dev server running?        │
│                                     │
│  [Try Again] [Help]                 │
└─────────────────────────────────────┘
```

**Invalid URL:**
```
┌─────────────────────────────────────┐
│           ❌ Invalid URL            │
│                                     │
│  Only localhost URLs are supported  │
│  Example: http://localhost:3000     │
│                                     │
└─────────────────────────────────────┘
```

---

## Dependencies

### Internal Dependencies

- **FEATURE-008 (Workplace):** Provides sidebar submenu structure. UI/UX Feedback appears as second item under Workplace submenu.

### External Dependencies

- **None for MVP** - No external libraries required for basic proxy and iframe rendering.

---

## Business Rules

### BR-1: Localhost URL Only

**Rule:** The proxy endpoint MUST only accept URLs where the host is `localhost` or `127.0.0.1`.

**Examples:**
- ✅ `http://localhost:3000/` - Allowed
- ✅ `http://127.0.0.1:8080/dashboard` - Allowed
- ✅ `http://localhost:5173/app/page` - Allowed
- ❌ `http://example.com/` - Rejected
- ❌ `http://192.168.1.100:3000/` - Rejected (internal network, not localhost)
- ❌ `https://google.com/` - Rejected

### BR-2: Any Port Allowed

**Rule:** Any port number is allowed for localhost URLs.

**Examples:**
- ✅ `localhost:80`
- ✅ `localhost:443`
- ✅ `localhost:3000`
- ✅ `localhost:5173`
- ✅ `localhost:8080`
- ✅ `localhost:65535`

### BR-3: Protocol Default

**Rule:** If no protocol is provided, default to `http://`.

**Examples:**
- `localhost:3000` → `http://localhost:3000`
- `127.0.0.1:8080` → `http://127.0.0.1:8080`

---

## Edge Cases & Constraints

### EC-1: Dev Server Not Running

**Scenario:** User enters localhost URL but dev server is not running.
**Expected Behavior:** Show "Connection refused" error with suggestion to start server. Provide retry button.

### EC-2: Slow Dev Server

**Scenario:** Dev server takes >10 seconds to respond.
**Expected Behavior:** Show timeout error after 10 seconds. Provide retry button.

### EC-3: Invalid Port

**Scenario:** User enters invalid port like `localhost:99999`.
**Expected Behavior:** Show "Invalid URL" error.

### EC-4: Empty URL

**Scenario:** User clicks Go with empty URL bar.
**Expected Behavior:** Show placeholder page or "Enter a localhost URL" message.

### EC-5: Page With Iframes

**Scenario:** Localhost page contains nested iframes.
**Expected Behavior:** Iframes may not load if they reference external resources. No special handling in MVP.

### EC-6: Page With WebSocket

**Scenario:** Localhost page uses WebSocket connections (e.g., HMR).
**Expected Behavior:** WebSocket connections may fail through proxy. Hot reload may not work. Documented limitation.

### EC-7: Large Page

**Scenario:** Localhost page is very large (>10MB HTML).
**Expected Behavior:** May be slow to load. No specific handling in MVP.

### EC-8: HTTPS Localhost

**Scenario:** User enters `https://localhost:3000`.
**Expected Behavior:** Attempt to proxy HTTPS. May fail if self-signed cert not trusted. Document limitation.

### EC-9: Redirect Response

**Scenario:** Localhost server returns 302 redirect.
**Expected Behavior:** Proxy follows redirect and returns final content. Rewrite redirect URLs if they're relative.

---

## Out of Scope

The following are explicitly NOT included in this feature:

- **Element inspection** - Covered by FEATURE-022-B
- **Feedback capture** - Covered by FEATURE-022-C
- **Feedback storage** - Covered by FEATURE-022-D
- **External URL viewing** - Only localhost supported
- **Mobile/tablet support** - Desktop only
- **WebSocket proxying** - May add in future version
- **Authentication pass-through** - Proxy doesn't forward auth
- **Cookie handling** - Proxy doesn't forward cookies
- **HTTPS with self-signed certs** - May not work reliably

---

## Technical Considerations

### Proxy Implementation

- Use Python `requests` library to fetch target URL
- Set appropriate timeout (10 seconds)
- Handle various content types (HTML, CSS, JS, images)
- For HTML: parse and rewrite asset paths using BeautifulSoup or regex
- For CSS: rewrite `url()` references
- Binary assets: return as-is with correct content-type

### Asset Path Rewriting Strategy

1. Parse HTML with BeautifulSoup
2. Find all `src`, `href`, `srcset` attributes
3. For relative paths, convert to absolute using base URL
4. Replace with proxy URL: `/api/proxy?url={encoded_absolute_url}`
5. Handle CSS `url()` in both `<style>` tags and linked stylesheets

### Iframe Rendering

- Use `srcdoc` attribute to inject HTML content
- Alternative: Create blob URL and set as `src`
- Handle sandbox attribute carefully to allow scripts

### CSP Header Handling

- Remove `Content-Security-Policy` header from proxied response
- Or modify to allow `unsafe-inline` for scripts/styles
- Be aware this reduces security for the proxied content

---

## Open Questions

- [x] Should proxy support HTTPS localhost? → Best effort, may not work with self-signed certs
- [x] Should proxy forward cookies? → No, security concern
- [x] Maximum timeout value? → 10 seconds
- [ ] Should we provide a list of recently loaded URLs? → Defer to future enhancement

---
