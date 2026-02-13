# Requirement Details - Part 8

> Continuation of requirement documentation.
> See [requirement-details-index.md](requirement-details-index.md) for full index.

---

## FEATURE-030: UIUX Reference — Core Tab & Agent Skill (Phase 1)

> Source: IDEA-018 (Feature-UIUX Reference)
> Status: Proposed
> Priority: High
> Mockup: [uiux-reference-tab-v2.html](../ideas/018.%20Feature-UIUX%20Reference/mockups/uiux-reference-tab-v2.html)
> Phase: 1 of 3

### Overview

Add a **UIUX Reference** tab as the third idea creation method in the Workplace (alongside Compose and Upload). The tab provides URL input, optional authentication prerequisite, extra instructions, and a "Go to Reference" button. Clicking the button triggers a console-first flow: the app finds an idle terminal session (or creates a new one), auto-types a `uiux-reference` prompt, and the user presses Enter. The CLI agent then opens the target URL in Chrome via Chrome DevTools MCP, handles authentication if needed, and injects an interactive toolbar with Color Picker and Element Highlighter tools. Collected reference data is sent back to the agent via CDP `Runtime.addBinding` callback and saved to the idea folder.

### User Request

The user wants to:
1. Reference external web pages for design inspiration during ideation
2. Pick colors and highlight elements directly on live web pages
3. Have reference data automatically saved to the idea folder in structured JSON format
4. Support authentication flows for gated pages (login → redirect → target)

### Clarifications

| Question | Answer |
|----------|--------|
| Relationship to FEATURE-022 (Browser Simulator)? | **Independent** — FEATURE-022 uses iframe for localhost only; UIUX Reference uses Chrome DevTools MCP for real external web pages. If UIUX Reference approach works well, its technique may be backported to FEATURE-022 later. |
| Relationship to FEATURE-008 (Workplace)? | **Independent** — UIUX Reference has its own data flow to the idea folder; does not modify Workplace file management. Uses existing folder structure. |
| Relationship to FEATURE-012 (Design Themes)? | **Complementary** — UIUX Reference extracts design tokens from web pages; FEATURE-012 stores/applies themes. Phase 3 can promote extracted tokens to FEATURE-012's theme folder. |
| Browser infrastructure? | Independent CDP connection — UIUX Reference manages its own Chrome browser tab via Chrome DevTools MCP, not dependent on FEATURE-022 infrastructure. |
| Frontend tab placement? | Third tab in the Workplace idea creation UI, alongside Compose and Upload. Tab contains URL input, console handles agent execution. |
| Phase scope? | 3 phases as separate features: Phase 1 (FEATURE-030), Phase 2 (FEATURE-031), Phase 3 (FEATURE-032). |
| MCP endpoint scope? | Phase 1 only: `POST /api/ideas/uiux-reference` (save reference data). Extend later as needed. |

### High-Level Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-030.1 | "UIUX Reference" tab in Workplace idea creation panel (third tab alongside Compose and Upload) | P0 |
| FR-030.2 | URL input field for target web page URL | P0 |
| FR-030.3 | Optional prerequisite URL input for authentication flows (collapsible section, hidden by default) | P1 |
| FR-030.4 | Extra instructions text area for guiding the agent | P1 |
| FR-030.5 | "Go to Reference" button triggers console-first flow | P0 |
| FR-030.6 | Console integration: find idle terminal session or create new one; auto-type prompt from `copilot-prompt.json` (key: `uiux-reference`) | P0 |
| FR-030.7 | Agent opens target URL via Chrome DevTools MCP | P0 |
| FR-030.8 | Authentication prerequisite flow: open auth URL → user completes login → URL-change-based detection (current URL leaves auth domain or matches target) → redirect to target URL | P1 |
| FR-030.9 | Auth timeout: 5-minute timer on auth page; prompt user if exceeded | P2 |
| FR-030.10 | Inject interactive toolbar into target page as draggable element (initial position: top-right corner) | P0 |
| FR-030.11 | Toolbar collapses to hamburger menu icon; expands on hover/click to show tool panel | P0 |
| FR-030.12 | Toolbar uses `z-index: 2147483647` to remain on top of all page content | P0 |
| FR-030.13 | **Color Picker tool** — click any element to capture hex, RGB, HSL values + CSS selector of source element | P0 |
| FR-030.14 | **Element Highlighter tool** — hover to highlight any element with bounding box overlay; click to capture CSS selector path, bounding box coordinates, full-page screenshot, and cropped element screenshot | P0 |
| FR-030.15 | Collected data displayed in toolbar panel as running summary (color count, element count) | P1 |
| FR-030.16 | "Send References" button in toolbar triggers callback to agent | P0 |
| FR-030.17 | Primary callback: `Runtime.addBinding("__xipeCallback")` — injected JS calls `window.__xipeCallback(JSON.stringify(data))`, CDP fires `Runtime.bindingCalled` event, agent receives payload directly | P0 |
| FR-030.18 | Fallback callback: if `Runtime.addBinding` unavailable, set `window.__xipeRefReady = true` and agent polls via `evaluate_script` | P1 |
| FR-030.19 | Reference data saved as JSON in `uiux-references/sessions/ref-session-{NNN}.json` within the idea folder | P0 |
| FR-030.20 | Top-level `uiux-references/reference-data.json` created/updated as merged view of all sessions | P1 |
| FR-030.21 | Screenshots saved to `uiux-references/screenshots/` (full-page: `full-page-{NNN}.png`, element crops: `elem-{NNN}-crop.png`) | P0 |

#### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-030.1 | Toolbar injection must not break target page layout or functionality | P0 |
| NFR-030.2 | Toolbar must remain functional after page scroll, resize, and dynamic content changes | P0 |
| NFR-030.3 | Reference JSON must conform to the schema defined in idea-summary-v2.md | P0 |
| NFR-030.4 | CDP connection resilience: 3 reconnection retries on drop; save partial data on failure | P1 |
| NFR-030.5 | CORS-blocked assets logged as warnings, skipped without breaking flow | P1 |
| NFR-030.6 | Top-level DOM only (v1); Shadow DOM and cross-origin iframes out of scope | P0 |

### Acceptance Criteria

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-030.1 | User is in Workplace idea creation panel | User clicks "UIUX Reference" tab | Tab displays URL input, optional auth URL (collapsed), extra instructions, and "Go to Reference" button |
| AC-030.2 | User has entered a target URL and clicks "Go to Reference" | Console-first flow triggers | App finds idle session (or creates new one), auto-types `copilot execute uiux-reference --url {url}` prompt |
| AC-030.3 | Agent receives uiux-reference prompt with auth URL | Agent processes authentication flow | Auth page opens, user logs in, URL-change detection redirects to target URL |
| AC-030.4 | Target page loaded in Chrome | Agent injects toolbar | Draggable toolbar appears top-right with hamburger icon; expands to show Color Picker and Element Highlighter tools |
| AC-030.5 | Color Picker tool active | User clicks an element | Hex, RGB, HSL values captured along with source element's CSS selector; counter increments in toolbar |
| AC-030.6 | Element Highlighter tool active | User hovers over an element | Element highlighted with bounding box overlay and CSS selector label (e.g., `body > main > .cards > .card:nth-child(2)`) |
| AC-030.7 | Element Highlighter tool active | User clicks a highlighted element | CSS selector path, bounding box, full-page screenshot, and cropped element screenshot captured |
| AC-030.8 | User has collected references | User clicks "Send References" | Callback fires via `Runtime.addBinding`; agent receives JSON payload with all collected data |
| AC-030.9 | Agent receives reference data | Agent saves to idea folder | JSON saved to `uiux-references/sessions/ref-session-{NNN}.json`; screenshots saved to `uiux-references/screenshots/` |
| AC-030.10 | Multiple reference sessions completed | Agent merges sessions | `uiux-references/reference-data.json` contains merged view of all sessions |

### Constraints

- Chrome DevTools MCP must be configured and running
- Only one UIUX Reference session per browser tab at a time
- `copilot-prompt.json` must have a `uiux-reference` key for the prompt template
- Top-level DOM only (no Shadow DOM, no cross-origin iframes)

### Dependencies

- Chrome DevTools MCP server (external, must be pre-configured)
- FEATURE-033 (x-ipe-app-and-agent-interaction MCP) — for saving reference data back to the app
- Existing Workplace idea creation UI (FEATURE-008) — for tab placement
- Existing console session management (FEATURE-005 / FEATURE-029) — for session finding/creation

---

## FEATURE-031: UIUX Reference — Advanced Tools (Phase 2)

> Source: IDEA-018 (Feature-UIUX Reference)
> Status: Proposed
> Priority: Medium
> Mockup: [injected-toolbar-v2.html](../ideas/018.%20Feature-UIUX%20Reference/mockups/injected-toolbar-v2.html)
> Phase: 2 of 3
> Depends on: FEATURE-030

### Overview

Extend the UIUX Reference toolbar (from FEATURE-030) with two advanced tools: **Element Commenter** (attach text comments to highlighted elements) and **Asset Extractor** (capture computed CSS, relevant CSS rules, fonts, icons, and images for 1:1 reproduction). Binary assets (fonts, images) are downloaded and stored locally.

### High-Level Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-031.1 | **Element Commenter tool** — attach text comments to any highlighted element via CSS tree selector (e.g., `body > header > nav.main-nav`) | P0 |
| FR-031.2 | Comment displayed as tooltip/bubble attached to the element; stored with CSS selector reference | P0 |
| FR-031.3 | **Asset Extractor tool** — extract full computed CSS for a selected element | P0 |
| FR-031.4 | Extract relevant CSS rules (matching rules from stylesheets, not just computed values) | P0 |
| FR-031.5 | Download referenced font files (woff2, woff, ttf) and store in `uiux-references/assets/fonts/` | P1 |
| FR-031.6 | Download referenced icon files (SVG, icon fonts) and store in `uiux-references/assets/icons/` | P1 |
| FR-031.7 | Download referenced image assets (backgrounds, content images) and store in `uiux-references/assets/elem-{NNN}/` | P1 |
| FR-031.8 | Computed styles saved as JSON in `uiux-references/assets/elem-{NNN}/computed-styles.json` | P0 |
| FR-031.9 | Relevant CSS rules saved in `uiux-references/assets/elem-{NNN}/rules.css` | P0 |
| FR-031.10 | Phase 2 tools appear in a separate section in the toolbar (below Phase 1 tools, with separator) | P1 |

#### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-031.1 | Font/image downloads must handle CORS restrictions gracefully (skip with warning) | P0 |
| NFR-031.2 | Binary asset size should be monitored; warn if total exceeds 50MB | P1 |
| NFR-031.3 | Font licensing disclaimer included in reference data JSON (`licensing: "reference_only"`) | P0 |

### Acceptance Criteria

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-031.1 | Element Commenter tool active | User clicks an element and types a comment | Comment text stored with CSS tree selector; tooltip bubble visible on element |
| AC-031.2 | Asset Extractor tool active | User clicks an element | Computed CSS extracted as JSON; relevant CSS rules extracted; referenced fonts/icons/images downloaded |
| AC-031.3 | User sends references with Phase 2 data | Agent receives callback | JSON payload includes `elements[].comment` and `elements[].extracted_assets` sections |
| AC-031.4 | Asset download encounters CORS block | Agent attempts download | Warning logged; blocked asset skipped; remaining assets continue downloading |

### Dependencies

- FEATURE-030 (UIUX Reference Phase 1) — toolbar infrastructure, callback mechanism
- FEATURE-033 (x-ipe-app-and-agent-interaction MCP) — for saving extended reference data

---

## FEATURE-032: UIUX Reference — Design System Integration (Phase 3)

> Source: IDEA-018 (Feature-UIUX Reference)
> Status: Proposed
> Priority: Low
> Phase: 3 of 3
> Depends on: FEATURE-031
> Related: FEATURE-012 (Design Themes), FEATURE-013 (Default Theme Content)

### Overview

Auto-generate a local `design-system.md` from extracted design tokens (colors and typography only). The generated file lives in the idea's `uiux-references/` folder and can optionally be **promoted** to FEATURE-012's global theme folder via the brand-theme-creator tool.

### High-Level Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-032.1 | Auto-generate `uiux-references/design-system.md` from extracted design tokens after reference session completes | P0 |
| FR-032.2 | Design tokens include: color palette (primary, secondary, background, text), typography (heading font, body font, base size) | P0 |
| FR-032.3 | Only directly extractable values captured — spacing grids and component hierarchies NOT auto-inferred | P0 |
| FR-032.4 | Promotion path: user can promote local design-system.md to global theme folder via brand-theme-creator | P1 |
| FR-032.5 | Multiple sessions' tokens merged into single design-system.md (append, not overwrite) | P1 |

#### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-032.1 | Generated design-system.md must be compatible with FEATURE-014 (Theme-Aware Frontend Design Skill) format | P0 |
| NFR-032.2 | Promotion to global theme must not overwrite existing theme data without confirmation | P0 |

### Acceptance Criteria

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-032.1 | Reference session completed with color and typography data | Agent generates design system | `uiux-references/design-system.md` created with color palette and typography sections |
| AC-032.2 | Multiple reference sessions exist | Agent generates design system | Tokens from all sessions merged into single design-system.md |
| AC-032.3 | User wants to promote to global theme | User triggers brand-theme-creator promotion | Local design-system.md contents are available as input to brand-theme-creator |

### Dependencies

- FEATURE-031 (UIUX Reference Phase 2) — asset extraction provides computed styles data
- FEATURE-012 (Design Themes) — target for promotion path
- FEATURE-014 (Theme-Aware Frontend Design Skill) — format compatibility

---

## FEATURE-033: x-ipe-app-and-agent-interaction MCP

> Source: IDEA-018 (Feature-UIUX Reference)
> Status: Proposed
> Priority: High

### Overview

A new **reusable MCP server** that provides a general-purpose communication bridge between the X-IPE web app and CLI agents. The MCP server exposes tools that call new endpoints on the existing Flask backend. UIUX Reference is the first use case; the MCP is designed for future extension with additional app-agent interaction endpoints.

### User Request

The user wants:
1. A new MCP server (separate from existing ones) for app↔agent communication
2. MCP tools that call new endpoints on the existing Flask backend
3. Phase 1 scope: only `POST /api/ideas/uiux-reference` (save reference data)
4. Designed for reuse — future endpoints can be added without architectural changes

### Clarifications

| Question | Answer |
|----------|--------|
| Separate MCP or extension of existing? | New standalone MCP server with its own process; calls existing Flask backend via HTTP |
| Flask endpoint? | New endpoint added to existing Flask backend: `POST /api/ideas/uiux-reference` |
| Phase 1 scope? | Only `POST` (save). No `GET`, `DELETE`, `PATCH` in Phase 1. Extend later as needed. |
| Reuse strategy? | MCP designed with generic tool registration; UIUX Reference is first registered tool |

### High-Level Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-033.1 | New MCP server process: `x-ipe-app-and-agent-interaction` | P0 |
| FR-033.2 | MCP tool: `save_uiux_reference` — accepts reference data JSON, calls Flask backend `POST /api/ideas/uiux-reference` | P0 |
| FR-033.3 | Flask backend endpoint: `POST /api/ideas/uiux-reference` — validates and saves reference JSON to idea folder | P0 |
| FR-033.4 | Flask endpoint saves session JSON to `uiux-references/sessions/ref-session-{NNN}.json` | P0 |
| FR-033.5 | Flask endpoint creates/updates merged `uiux-references/reference-data.json` | P1 |
| FR-033.6 | Flask endpoint saves screenshots and binary assets to appropriate subfolders | P0 |
| FR-033.7 | MCP server designed with extensible tool registration for future endpoints | P1 |

#### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-033.1 | MCP server must follow X-IPE MCP conventions (FastMCP or MCP SDK) | P0 |
| NFR-033.2 | Flask endpoint must validate JSON schema before saving | P0 |
| NFR-033.3 | Error responses must include descriptive messages for agent consumption | P1 |

### Acceptance Criteria

| AC ID | Given | When | Then |
|-------|-------|------|------|
| AC-033.1 | MCP server is running | Agent calls `save_uiux_reference` with valid reference JSON | Flask backend receives POST, saves session JSON to idea folder, returns success |
| AC-033.2 | Reference data includes screenshots (base64) | Agent sends via MCP | Flask endpoint decodes and saves screenshots to `uiux-references/screenshots/` |
| AC-033.3 | Invalid JSON schema submitted | Agent sends via MCP | Flask endpoint returns 400 with descriptive error message |
| AC-033.4 | Multiple sessions saved | Agent queries merged view | `reference-data.json` contains all sessions' data |

### Dependencies

- Existing Flask backend (X-IPE web app)
- X-IPE MCP infrastructure conventions

---

## Conflict Review Summary

| Existing Feature | Overlap Type | Decision | Rationale |
|-----------------|--------------|----------|-----------|
| FEATURE-022-A/B (Browser Simulator & Element Inspector) | Functional — both open URLs and inspect elements | **New standalone feature** | Different user intent (testing vs. design inspiration); different infrastructure (iframe/localhost vs. CDP/external); UIUX Reference approach may be backported to FEATURE-022 later |
| FEATURE-008 (Workplace / Idea Management) | Scope — both manage idea folder data | **New standalone feature** | UIUX Reference adds its own subfolder (`uiux-references/`); uses existing folder structure without modification |
| FEATURE-012 (Design Themes) | Functional — both manage design tokens | **Complementary features** (cross-referenced) | UIUX Reference extracts tokens from web pages; FEATURE-012 stores/applies themes; Phase 3 promotion path connects them |

## Linked Mockups

| Mockup Function Name | Mockup Link |
|---------------------|-------------|
| UIUX Reference Tab (light editorial theme) | [uiux-reference-tab-v2.html](../ideas/018.%20Feature-UIUX%20Reference/mockups/uiux-reference-tab-v2.html) |
| Injected Reference Toolbar (light editorial theme) | [injected-toolbar-v2.html](../ideas/018.%20Feature-UIUX%20Reference/mockups/injected-toolbar-v2.html) |
| UIUX Reference Tab (dark alt) | [uiux-reference-tab-v1.html](../ideas/018.%20Feature-UIUX%20Reference/mockups/uiux-reference-tab-v1.html) |
| Injected Reference Toolbar (dark alt) | [injected-toolbar-v1.html](../ideas/018.%20Feature-UIUX%20Reference/mockups/injected-toolbar-v1.html) |
