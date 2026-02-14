# Requirement Details - Part 8

> Continuation of requirement documentation.
> See [requirement-details-index.md](requirement-details-index.md) for full index.

---

## Feature List

| Feature ID | Feature Title | Version | Brief Description | Feature Dependency |
|------------|---------------|---------|-------------------|-------------------|
| FEATURE-030-A | UIUX Reference Tab & Console Integration | v1.0 | Frontend tab (URL input, auth toggle, instructions) + console-first flow (find/create session, auto-type prompt) | None |
| FEATURE-030-B | UIUX Reference Agent Skill & Toolbar | v1.0 | Agent skill using CDP to open URL, handle auth, inject interactive toolbar (Color Picker, Element Highlighter), callback mechanism, save reference data | FEATURE-030-A, FEATURE-033 |
| FEATURE-031 | UIUX Reference Advanced Tools (Phase 2) | v1.0 | ❌ Cancelled — absorbed into IDEA-019 "Copy Design as Mockup" mode | FEATURE-030-B |
| FEATURE-032 | UIUX Reference Design System (Phase 3) | v1.0 | ❌ Cancelled — absorbed into IDEA-019 "Catch Design Theme" mode | FEATURE-031 |
| FEATURE-033 | App-Agent Interaction MCP | v1.0 | New reusable MCP server + Flask endpoint for browser→agent communication; Phase 1: save_uiux_reference tool | None |

---

## Linked Mockups

| Mockup Function Name | Feature | Mockup Link |
|---------------------|---------|-------------|
| UIUX Reference Tab (light) | FEATURE-030-A | [uiux-reference-tab-v2.html](FEATURE-030-A/mockups/uiux-reference-tab-v2.html) |
| UIUX Reference Tab (dark alt) | FEATURE-030-A | [uiux-reference-tab-v1.html](FEATURE-030-A/mockups/uiux-reference-tab-v1.html) |
| Injected Reference Toolbar (light) | FEATURE-030-B | [injected-toolbar-v2.html](FEATURE-030-B/mockups/injected-toolbar-v2.html) |
| Injected Reference Toolbar (dark alt) | FEATURE-030-B | [injected-toolbar-v1.html](FEATURE-030-B/mockups/injected-toolbar-v1.html) |
| Injected Toolbar with Phase 2 tools | FEATURE-031 | [injected-toolbar-v2.html](FEATURE-031/mockups/injected-toolbar-v2.html) |

---

## Feature Details

---

### FEATURE-030-A: UIUX Reference Tab & Console Integration

**Version:** v1.0
**Brief Description:** Frontend tab in Workplace idea creation panel with URL input, auth prerequisite toggle, extra instructions, and "Go to Reference" button that triggers console-first flow.

> Source: IDEA-018 (Feature-UIUX Reference)
> Status: Proposed
> Priority: High (MVP — entry point for the entire UIUX Reference workflow)
> Mockup: [uiux-reference-tab-v2.html](FEATURE-030-A/mockups/uiux-reference-tab-v2.html)
> Phase: 1 of 3

**Acceptance Criteria:**
- [ ] "UIUX Reference" tab visible as third tab in Workplace idea creation panel (alongside Compose and Upload)
- [ ] URL input field accepts target web page URL
- [ ] Optional auth prerequisite URL input (collapsible section, hidden by default)
- [ ] Extra instructions text area visible for guiding the agent
- [ ] "Go to Reference" button triggers console-first flow: finds idle terminal session (or creates new one), auto-types prompt from `copilot-prompt.json` (key: `uiux-reference`)
- [ ] Prompt format: `copilot execute uiux-reference --url {url} --auth-url {auth_url} --extra "{instructions}"`

**Dependencies:**
- Existing Workplace idea creation UI (FEATURE-008) — for tab placement
- Existing console session management (FEATURE-005 / FEATURE-029) — for session finding/creation

**Technical Considerations:**
- Tab UI follows existing Compose/Upload tab pattern in Workplace
- `copilot-prompt.json` must have a `uiux-reference` key for the prompt template
- Console integration reuses existing session management API

---

### FEATURE-030-B: UIUX Reference Agent Skill & Toolbar

**Version:** v1.0
**Brief Description:** Agent skill using Chrome DevTools MCP to open target URL, handle authentication, inject interactive toolbar (Color Picker, Element Highlighter), collect reference data via CDP callback, and save to idea folder.

> Source: IDEA-018 (Feature-UIUX Reference)
> Status: Proposed
> Priority: High
> Mockup: [injected-toolbar-v2.html](FEATURE-030-B/mockups/injected-toolbar-v2.html)
> Phase: 1 of 3

**Acceptance Criteria:**
- [ ] Agent opens target URL in Chrome via Chrome DevTools MCP
- [ ] Authentication prerequisite flow: open auth URL → user logs in → URL-change detection → redirect to target URL; 5-minute timeout
- [ ] Draggable toolbar injected top-right with hamburger icon; expands on hover/click to show tool panel
- [ ] Toolbar uses `z-index: 2147483647`; remains functional after scroll/resize/dynamic content changes
- [ ] Color Picker tool: click element → capture hex, RGB, HSL + CSS selector; counter increments
- [ ] Element Highlighter tool: hover → bounding box overlay + CSS selector label; click → capture selector path, bounding box, full-page + cropped screenshots
- [ ] "Send References" callback via `Runtime.addBinding("__xipeCallback")`; fallback: `evaluate_script` polling
- [ ] Reference data saved as JSON in `uiux-references/sessions/ref-session-{NNN}.json`
- [ ] Screenshots saved to `uiux-references/screenshots/` (full-page + element crops)
- [ ] Top-level `uiux-references/reference-data.json` created/updated as merged view of all sessions

**Dependencies:**
- FEATURE-030-A (UIUX Reference Tab) — provides the entry point and prompt
- FEATURE-033 (App-Agent Interaction MCP) — for saving reference data back to the app
- Chrome DevTools MCP server (external, must be pre-configured)

**Technical Considerations:**
- Toolbar injection must not break target page layout or functionality
- CDP connection resilience: 3 reconnection retries on drop; save partial data on failure
- Top-level DOM only (no Shadow DOM, no cross-origin iframes in v1)
- Reference JSON must conform to schema defined in idea-summary-v2.md
- CORS-blocked assets logged as warnings, skipped without breaking flow

**Clarifications (inherited from FEATURE-030):**

| Question | Answer |
|----------|--------|
| Relationship to FEATURE-022? | **Independent** — FEATURE-022 uses iframe for localhost; UIUX Reference uses CDP for real external pages. May backport technique later. |
| Browser infrastructure? | Independent CDP connection — not dependent on FEATURE-022 infrastructure. |
| Phase scope? | ~~3 phases: Phase 1 (030-A/B), Phase 2 (031), Phase 3 (032).~~ Revised: Phase 2 (031) and Phase 3 (032) cancelled — absorbed into CR-002 on FEATURE-030-B v2.0. |

> **⚠️ CR Impact Note** (added 02-14-2026, ref: IDEA-019 / CR-002)
> - **Change:** Complete toolbar redesign — v1.1 standalone tools replaced by two-mode wizard (Catch Design Theme + Copy Design as Mockup)
> - **Affected FRs:** All existing FRs (FR-1 through FR-37) — v1.x user stories and FRs to be deprecated and replaced
> - **Action Required:** Feature specification refactoring to v2.0 needed before implementation
> - **Source:** IDEA-019 (CR-UIUX Reference) — see [idea-summary-v3.md](../ideas/019.%20CR-UIUX%20Reference/idea-summary-v3.md)

---

## FEATURE-031: UIUX Reference — Advanced Tools (Phase 2)

> Source: IDEA-018 (Feature-UIUX Reference)
> Status: ❌ Cancelled
> Cancelled: 02-14-2026
> Reason: Absorbed into IDEA-019 (CR-UIUX Reference). Element Commenter → "Copy Design as Mockup" Step 2 (per-component instructions). Asset Extractor → agent analysis loop (rubric-driven deep capture on demand).
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

- FEATURE-030-B (UIUX Reference Agent Skill & Toolbar) — toolbar infrastructure, callback mechanism
- FEATURE-033 (x-ipe-app-and-agent-interaction MCP) — for saving extended reference data

---

## FEATURE-032: UIUX Reference — Design System Integration (Phase 3)

> Source: IDEA-018 (Feature-UIUX Reference)
> Status: ❌ Cancelled
> Cancelled: 02-14-2026
> Reason: Absorbed into IDEA-019 (CR-UIUX Reference). "Catch Design Theme" mode captures colors with role annotations and calls brand-theme-creator to generate design-system.md — the full scope of FEATURE-032.
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
| Toolbar v2.0 — Two-mode wizard (IDEA-019) | [toolbar-v2-v1.html](../ideas/019.%20CR-UIUX%20Reference/mockups/toolbar-v2-v1.html) |
