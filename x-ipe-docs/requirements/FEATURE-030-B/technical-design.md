# Technical Design: UIUX Reference Agent Skill & Toolbar

> Feature ID: FEATURE-030-B | Version: v1.0 | Last Updated: 02-13-2026

---

## Part 1: Agent-Facing Summary

> **Purpose:** Quick reference for AI agents navigating large projects.
> **📌 AI Coders:** Focus on this section for implementation context.

### Key Components Implemented

| Component | Responsibility | Scope/Impact | Tags |
|-----------|----------------|--------------|------|
| `.github/skills/x-ipe-tool-uiux-reference/SKILL.md` | Agent skill definition — step-by-step procedure for the `uiux-reference` workflow | New skill file: agent reads and follows this procedure | #skill #agent #uiux-reference #chrome-devtools #cdp |
| `src/x_ipe/static/js/injected/xipe-toolbar.js` | Self-contained IIFE injected into target page via `evaluate_script` — toolbar UI, color picker, element highlighter, callback | New file: injected into external pages at runtime | #frontend #injection #toolbar #cdp #color-picker #highlighter |
| `.github/skills/x-ipe-tool-uiux-reference/references/toolbar-template.md` | Reference doc containing the toolbar IIFE source for the agent to inject | New file: agent reads this to get the injection payload | #skill #reference #toolbar #template |

### Scope & Boundaries

**In Scope:**
- Agent skill procedure: parse prompt → navigate → optional auth → inject toolbar → register callback → await "Send References" → receive data → save via MCP
- Toolbar IIFE (HTML + CSS + JS in a single `evaluate_script` call): hamburger toggle, panel with Color Picker + Element Highlighter tools, collected data summary, "Send References" button
- CDP callback registration (`Runtime.addBinding`) with `evaluate_script` polling fallback
- Screenshot capture via Chrome DevTools MCP `take_screenshot`
- Data persistence via FEATURE-033 `save_uiux_reference` MCP tool

**Out of Scope:**
- Tab UI / console integration (FEATURE-030-A — already complete)
- MCP server / Flask endpoint (FEATURE-033 — already complete)
- Phase 2 tools: Element Commenter, Asset Extractor (FEATURE-031)
- Design system generation (FEATURE-032)

### Dependencies

| Dependency | Source | Design Link | Usage Description |
|------------|--------|-------------|-------------------|
| Chrome DevTools MCP | External | — | `navigate_page`, `evaluate_script`, `take_screenshot`, `take_snapshot` tools for browser automation |
| `save_uiux_reference` MCP tool | FEATURE-033 | [technical-design.md](../FEATURE-033/technical-design.md) | Persist reference data to idea folder via `POST /api/ideas/uiux-reference` |
| UIUX Reference Tab | FEATURE-030-A | [technical-design.md](../FEATURE-030-A/technical-design.md) | Provides entry point — auto-types `uiux-reference` prompt into console |
| `copilot-prompt.json` | FEATURE-030-A | — | Prompt template with `--url`, `--auth-url`, `--extra` parameters |

### Major Flow

1. **Parse Prompt:** Agent receives `copilot execute uiux-reference --url {url} [--auth-url {auth_url}] [--extra "{instructions}"]` → extracts parameters
2. **Navigate:** If `--auth-url` provided → `navigate_page(url: auth_url)` → poll for URL change → `navigate_page(url: target_url)`. Otherwise → `navigate_page(url: target_url)` directly.
3. **Inject Toolbar:** Call `evaluate_script` with the toolbar IIFE from `toolbar-template.md` → toolbar appears at top-right of page
4. **Await Callback:** Poll `evaluate_script(() => window.__xipeRefReady ? window.__xipeRefData : null)` every 3 seconds until data is returned (user clicks "Send References")
5. **Process Data:** Take screenshots for each captured element → construct Reference Data JSON (v1.0 schema) → call `save_uiux_reference` MCP tool
6. **Report:** Output summary to user: "{N} colors, {M} elements captured from {url}"

### Usage Example

```
# Agent receives this prompt from FEATURE-030-A console integration:
copilot execute uiux-reference --url https://stripe.com/pricing --extra "Focus on the pricing card colors and CTA buttons"

# Agent skill execution (pseudocode):
1. navigate_page(url: "https://stripe.com/pricing")
2. evaluate_script(TOOLBAR_IIFE)  # injects toolbar
3. # User interacts with Color Picker and Element Highlighter
4. # User clicks "Send References"
5. ref_data = evaluate_script(() => window.__xipeRefReady ? window.__xipeRefData : null)
6. # Agent takes screenshots for each element
7. save_uiux_reference({
     version: "1.0",
     source_url: "https://stripe.com/pricing",
     idea_folder: "018. Feature-UIUX Reference",
     timestamp: "2026-02-13T13:00:00Z",
     colors: [...],
     elements: [...]
   })
8. # Output: "Reference data saved — 4 colors, 2 elements captured"
```

---

## Part 2: Implementation Guide

> **Purpose:** Human-readable details for developers.
> **📌 Emphasis on visual diagrams for comprehension.**

### Architecture Overview

This feature consists of two deliverables that work together:

```
┌──────────────────────────────────────────────────────────────────────┐
│  Agent Skill (.github/skills/x-ipe-tool-uiux-reference/SKILL.md)   │
│  ────────────────────────────────────────────────────────────────    │
│  Step-by-step procedure the agent follows:                          │
│  1. Parse prompt args                                               │
│  2. Navigate to URL (with optional auth)                            │
│  3. Inject toolbar IIFE via evaluate_script                         │
│  4. Poll for user data via evaluate_script                          │
│  5. Take screenshots via take_screenshot                            │
│  6. Save data via save_uiux_reference MCP tool                     │
└───────────────────────┬──────────────────────────────────────────────┘
                        │ reads toolbar source from
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Toolbar IIFE (references/toolbar-template.md)                      │
│  ────────────────────────────────────────────────────────────────    │
│  Self-contained JS injected into target page:                       │
│  - Hamburger button (52×52px, draggable, top-right)                 │
│  - Panel (272px): Color Picker, Element Highlighter tools           │
│  - Collected References summary                                     │
│  - "Send References" button → sets window.__xipeRefReady = true     │
│  - All data stored in window.__xipeRefData                          │
└──────────────────────────────────────────────────────────────────────┘
```

### End-to-End Workflow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant Console as Terminal Console
    participant Agent as CLI Agent
    participant Skill as uiux-reference Skill
    participant CDP as Chrome DevTools MCP
    participant Browser as Chrome Browser
    participant MCP as save_uiux_reference MCP

    U->>Console: Press Enter (prompt auto-typed by 030-A)
    Console->>Agent: Execute prompt
    Agent->>Skill: Load skill, parse --url, --auth-url, --extra

    alt Auth URL provided
        Skill->>CDP: navigate_page(url: auth_url)
        CDP->>Browser: Open auth page
        U->>Browser: Complete login
        loop Poll URL change (3s interval, 5min timeout)
            Skill->>CDP: evaluate_script(() => location.href)
            CDP-->>Skill: current URL
        end
        Skill->>CDP: navigate_page(url: target_url)
    else No auth
        Skill->>CDP: navigate_page(url: target_url)
    end

    CDP->>Browser: Page loaded
    Skill->>CDP: evaluate_script(TOOLBAR_IIFE)
    CDP->>Browser: Toolbar injected (hamburger top-right)

    loop User picks colors & elements
        U->>Browser: Click elements with tools
        Note over Browser: Data stored in window.__xipeRefData
    end

    U->>Browser: Click "Send References"
    Note over Browser: Sets window.__xipeRefReady = true

    loop Poll for data (3s interval)
        Skill->>CDP: evaluate_script(() => __xipeRefReady ? __xipeRefData : null)
    end
    CDP-->>Skill: Reference data JSON

    loop For each captured element
        Skill->>CDP: take_screenshot(fullPage: true)
        CDP-->>Skill: Full-page PNG (base64)
        Skill->>CDP: take_snapshot()
        Note over Skill: Find element UID by selector
        Skill->>CDP: take_screenshot(uid: element_uid)
        CDP-->>Skill: Element crop PNG (base64)
    end

    Skill->>MCP: save_uiux_reference(data + screenshots)
    MCP-->>Skill: {success, session_file}
    Skill->>Agent: "Saved — N colors, M elements"
    Agent->>U: Display summary
```

### State Diagram — Skill Execution

```mermaid
stateDiagram-v2
    [*] --> ParsePrompt
    ParsePrompt --> AuthFlow : --auth-url provided
    ParsePrompt --> NavigateTarget : no auth
    
    AuthFlow --> PollAuthURL : navigate to auth URL
    PollAuthURL --> NavigateTarget : URL changed (auth complete)
    PollAuthURL --> AuthTimeout : 5 min elapsed
    AuthTimeout --> NavigateTarget : user types "skip"
    AuthTimeout --> [*] : user aborts
    
    NavigateTarget --> InjectToolbar : page loaded
    NavigateTarget --> Error : page load failed
    
    InjectToolbar --> WaitForData : toolbar visible
    
    WaitForData --> ProcessData : __xipeRefReady = true
    WaitForData --> WaitForData : poll every 3s
    
    ProcessData --> TakeScreenshots : elements found
    ProcessData --> SaveData : no elements (colors only)
    
    TakeScreenshots --> SaveData : all screenshots captured
    
    SaveData --> [*] : success
    SaveData --> Error : save failed
    
    Error --> [*] : report error to user
```

### Component 1: Agent Skill (SKILL.md)

**File:** `.github/skills/x-ipe-tool-uiux-reference/SKILL.md`

This is a **tool skill** (not task-based) — it defines a procedure the agent follows when the user triggers the `uiux-reference` command.

#### Skill Metadata

```yaml
---
name: x-ipe-tool-uiux-reference
description: Execute UIUX reference workflow — open target URL via Chrome DevTools MCP, inject interactive toolbar, collect colors and elements, take screenshots, save reference data via save_uiux_reference MCP tool. Triggers on "uiux-reference", "execute uiux-reference".
---
```

#### Skill Procedure (Pseudocode)

```
PROCEDURE uiux-reference:

  INPUT:
    url: string (required)       # from --url flag
    auth_url: string (optional)  # from --auth-url flag
    extra: string (optional)     # from --extra flag
    idea_folder: string          # derived from prompt context or asked from user

  STEP 1 — Parse Prompt:
    Extract --url, --auth-url, --extra from prompt arguments.
    IF --url is missing → report error, STOP.
    IF idea_folder is unknown → ask user: "Which idea folder should I save to?"

  STEP 2 — Authentication (if --auth-url provided):
    CALL navigate_page(url: auth_url)
    WAIT for page load
    INFORM user: "Please log in. I'll detect when authentication completes."
    SET auth_start = now()
    LOOP every 3 seconds:
      current_url = evaluate_script(() => window.location.href)
      IF current_url domain != auth_url domain OR current_url path != auth_url path:
        AUTH COMPLETE → break
      IF elapsed > 5 minutes:
        ASK user: "Authentication timeout. Type 'skip' to proceed or 'retry'."
        IF skip → break
        IF retry → reset timer
    END LOOP

  STEP 3 — Navigate to Target:
    CALL navigate_page(url: target_url)
    WAIT for page load (30s timeout)
    IF load fails → report error, STOP

  STEP 4 — Inject Toolbar:
    READ toolbar IIFE source from references/toolbar-template.md
    CALL evaluate_script(function: TOOLBAR_IIFE)
    INFORM user: "Toolbar injected. Use Color Picker or Element Highlighter, then click 'Send References' when done."

  STEP 5 — Await User Data:
    LOOP every 3 seconds (max 30 minutes):
      result = evaluate_script(() => window.__xipeRefReady ? window.__xipeRefData : null)
      IF result is not null → DATA RECEIVED, break
    END LOOP
    IF timeout → INFORM user, STOP

  STEP 6 — Take Screenshots:
    FOR each element in result.elements:
      full_page_screenshot = take_screenshot(fullPage: true)
      snapshot = take_snapshot()
      element_uid = find UID matching element.selector in snapshot
      IF element_uid found:
        element_screenshot = take_screenshot(uid: element_uid)
      Encode screenshots as base64 with "base64:" prefix
      Attach to element.screenshots.full_page and element.screenshots.element_crop

  STEP 7 — Save via MCP:
    CONSTRUCT reference data JSON:
      version: "1.0"
      source_url: target_url
      auth_url: auth_url (if provided)
      timestamp: ISO 8601 now
      idea_folder: idea_folder
      colors: result.colors
      elements: result.elements (with screenshot data)
      design_tokens: result.design_tokens (if present)
    CALL save_uiux_reference(data)
    IF success:
      INFORM user: "Reference data saved — {N} colors, {M} elements from {url}. Session: {session_file}"
    ELSE:
      REPORT error from MCP response

END PROCEDURE
```

### Component 2: Toolbar IIFE (Injected JavaScript)

**File:** `src/x_ipe/static/js/injected/xipe-toolbar.js`
**Reference:** `.github/skills/x-ipe-tool-uiux-reference/references/toolbar-template.md`

The toolbar is a single self-contained IIFE that injects all HTML, CSS, and JS into the target page. The agent reads this code and passes it to `evaluate_script`.

#### Class Diagram

```mermaid
classDiagram
    class XipeToolbar {
        -HTMLElement root
        -String activeTool
        -Object refData
        -Boolean isDragging
        -Number startX
        -Number startY
        +init() void
        +injectStyles() void
        +injectHTML() void
        +bindEvents() void
        +togglePanel() void
        +selectTool(toolName) void
        +updateBadges() void
        +sendReferences() void
    }

    class ColorPicker {
        +activate() void
        +deactivate() void
        -handleClick(event) void
        -extractColor(element) Object
        -rgbToHex(r, g, b) String
        -rgbToHsl(r, g, b) String
        -generateSelector(element) String
        -showSwatch(element, hex) void
    }

    class ElementHighlighter {
        +activate() void
        +deactivate() void
        -handleMouseMove(event) void
        -handleClick(event) void
        -showOverlay(element) void
        -hideOverlay() void
        -generateSelector(element) String
        -captureElement(element) Object
    }

    class SelectorGenerator {
        +generate(element) String
        -getTagWithClasses(element) String
        -getNthChild(element) String
        -isUnique(selector) Boolean
    }

    XipeToolbar --> ColorPicker : manages
    XipeToolbar --> ElementHighlighter : manages
    ColorPicker --> SelectorGenerator : uses
    ElementHighlighter --> SelectorGenerator : uses
```

#### IIFE Structure

```javascript
// xipe-toolbar.js — Self-contained IIFE for injection via evaluate_script
(() => {
  // Guard: prevent double injection
  if (window.__xipeToolbarInjected) return;
  window.__xipeToolbarInjected = true;

  // ===== Data Store =====
  window.__xipeRefData = { colors: [], elements: [], design_tokens: null };
  window.__xipeRefReady = false;

  // ===== CSS Injection =====
  const style = document.createElement('style');
  style.textContent = `
    /* All styles from mockup injected-toolbar-v2.html */
    /* Prefixed with .xipe- to avoid conflicts */
    .xipe-toolbar { position: fixed; top: 20px; right: 20px; z-index: 2147483647; ... }
    .xipe-hamburger { width: 52px; height: 52px; ... }
    .xipe-panel { width: 272px; ... backdrop-filter: blur(24px); ... }
    /* ... (full CSS from mockup) ... */
  `;
  document.head.appendChild(style);

  // ===== Font Loading =====
  const fontLink = document.createElement('link');
  fontLink.rel = 'stylesheet';
  fontLink.href = 'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap';
  document.head.appendChild(fontLink);

  const iconLink = document.createElement('link');
  iconLink.rel = 'stylesheet';
  iconLink.href = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css';
  document.head.appendChild(iconLink);

  // ===== HTML Injection =====
  const toolbar = document.createElement('div');
  toolbar.className = 'xipe-toolbar';
  toolbar.id = 'xipe-toolbar';
  toolbar.innerHTML = `
    <div class="xipe-hamburger" id="xipe-hamburger">
      <span class="xipe-logo">X-IPE</span>
      <span class="badge-count" id="xipe-badge">0</span>
    </div>
    <div class="xipe-panel" id="xipe-panel">
      <div class="xipe-panel-header">
        <div class="xipe-panel-title">
          <span class="logo-dot"></span> X-IPE Reference
        </div>
        <button class="xipe-panel-close" id="xipe-close">
          <i class="bi bi-x"></i>
        </button>
      </div>
      <div class="xipe-phase-sep">Phase 1 — Core</div>
      <div class="xipe-tools">
        <button class="xipe-tool-btn active" data-tool="color">
          <span class="xipe-tool-icon color-picker"><i class="bi bi-eyedropper"></i></span>
          <span class="xipe-tool-info">
            <span class="xipe-tool-name">Color Picker</span>
            <span class="xipe-tool-desc">Pick colors from page</span>
          </span>
          <span class="xipe-tool-badge" id="xipe-color-badge">0</span>
        </button>
        <button class="xipe-tool-btn" data-tool="highlight">
          <span class="xipe-tool-icon highlighter"><i class="bi bi-cursor-text"></i></span>
          <span class="xipe-tool-info">
            <span class="xipe-tool-name">Element Highlighter</span>
            <span class="xipe-tool-desc">Inspect & screenshot</span>
          </span>
          <span class="xipe-tool-badge" id="xipe-elem-badge">0</span>
        </button>
      </div>
      <div class="xipe-divider"></div>
      <div class="xipe-phase-sep">Phase 2 — Advanced</div>
      <div class="xipe-tools">
        <button class="xipe-tool-btn xipe-disabled" data-tool="comment" disabled>
          <span class="xipe-tool-icon commenter"><i class="bi bi-chat-left-text"></i></span>
          <span class="xipe-tool-info">
            <span class="xipe-tool-name">Element Commenter</span>
            <span class="xipe-tool-desc">Attach notes to elements</span>
          </span>
          <span class="xipe-tool-badge">—</span>
        </button>
        <button class="xipe-tool-btn xipe-disabled" data-tool="extract" disabled>
          <span class="xipe-tool-icon extractor"><i class="bi bi-box-arrow-down"></i></span>
          <span class="xipe-tool-info">
            <span class="xipe-tool-name">Asset Extractor</span>
            <span class="xipe-tool-desc">CSS, fonts, images</span>
          </span>
          <span class="xipe-tool-badge">—</span>
        </button>
      </div>
      <div class="xipe-collected">
        <div class="xipe-collected-title">Collected References</div>
        <div class="xipe-collected-items" id="xipe-collected">
          <span class="xipe-collected-tag colors"><i class="bi bi-circle-fill"></i> <span id="xipe-color-count">0</span> colors</span>
          <span class="xipe-collected-tag elements"><i class="bi bi-circle-fill"></i> <span id="xipe-elem-count">0</span> elements</span>
        </div>
      </div>
      <button class="xipe-send-btn" id="xipe-send">
        <i class="bi bi-send-fill"></i> Send References
      </button>
    </div>
  `;
  document.body.appendChild(toolbar);

  // ===== Drag Hint =====
  const hint = document.createElement('div');
  hint.className = 'xipe-drag-hint';
  hint.innerHTML = '<i class="bi bi-arrows-move"></i> Drag to move toolbar';
  document.body.appendChild(hint);
  setTimeout(() => hint.remove(), 3500);

  // ===== Selector Generator =====
  function generateSelector(el) {
    if (el === document.body) return 'body';
    const parts = [];
    let current = el;
    while (current && current !== document.body) {
      let selector = current.tagName.toLowerCase();
      // Add meaningful classes (skip dynamic/generated ones)
      const classes = Array.from(current.classList)
        .filter(c => !c.match(/^(js-|_|ng-|css-|sc-|chakra-)/))
        .slice(0, 2);
      if (classes.length) selector += '.' + classes.join('.');
      // Add nth-child if selector is not unique among siblings
      const parent = current.parentElement;
      if (parent) {
        const siblings = Array.from(parent.children).filter(
          s => s.tagName === current.tagName
        );
        if (siblings.length > 1) {
          const idx = siblings.indexOf(current) + 1;
          selector += `:nth-child(${idx})`;
        }
      }
      parts.unshift(selector);
      current = current.parentElement;
    }
    parts.unshift('body');
    return parts.join(' > ');
  }

  // ===== Color Picker =====
  let colorPickerActive = true;
  let highlighterActive = false;
  let overlayEl = null;
  let labelEl = null;

  function handleColorClick(e) {
    if (!colorPickerActive) return;
    // Ignore clicks on toolbar itself
    if (e.target.closest('.xipe-toolbar')) return;
    e.preventDefault();
    e.stopPropagation();

    const el = e.target;
    const computed = window.getComputedStyle(el);
    const bgColor = computed.backgroundColor;
    const textColor = computed.color;
    // Prefer background color if not transparent, else use text color
    const colorStr = (bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent')
      ? bgColor : textColor;

    // Parse RGB
    const match = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
    if (!match) return;
    const [, r, g, b] = match.map(Number);
    const hex = '#' + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('');

    // Convert to HSL
    const rN = r/255, gN = g/255, bN = b/255;
    const max = Math.max(rN, gN, bN), min = Math.min(rN, gN, bN);
    const l = (max + min) / 2;
    let h = 0, s = 0;
    if (max !== min) {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      if (max === rN) h = ((gN - bN) / d + (gN < bN ? 6 : 0)) / 6;
      else if (max === gN) h = ((bN - rN) / d + 2) / 6;
      else h = ((rN - gN) / d + 4) / 6;
    }
    const hsl = `${Math.round(h*360)}, ${Math.round(s*100)}%, ${Math.round(l*100)}%`;

    const colorId = `color-${String(window.__xipeRefData.colors.length + 1).padStart(3, '0')}`;
    window.__xipeRefData.colors.push({
      id: colorId,
      hex: hex,
      rgb: `${r}, ${g}, ${b}`,
      hsl: hsl,
      source_selector: generateSelector(el),
      context: ''
    });
    updateBadges();
    showSwatch(el, hex);
  }

  function showSwatch(el, hex) {
    const swatch = document.createElement('div');
    swatch.className = 'xipe-picked-swatch';
    swatch.innerHTML = `<span class="xipe-swatch-dot" style="background:${hex};"></span>${hex}`;
    swatch.style.cssText = `position:absolute;z-index:2147483646;`;
    const rect = el.getBoundingClientRect();
    swatch.style.top = (rect.bottom + window.scrollY + 4) + 'px';
    swatch.style.left = (rect.left + window.scrollX) + 'px';
    document.body.appendChild(swatch);
    setTimeout(() => swatch.remove(), 5000);
  }

  // ===== Element Highlighter =====
  function handleHighlightMove(e) {
    if (!highlighterActive) return;
    if (e.target.closest('.xipe-toolbar')) return;
    showOverlay(e.target);
  }

  function handleHighlightClick(e) {
    if (!highlighterActive) return;
    if (e.target.closest('.xipe-toolbar')) return;
    e.preventDefault();
    e.stopPropagation();

    const el = e.target;
    const rect = el.getBoundingClientRect();
    const elemId = `elem-${String(window.__xipeRefData.elements.length + 1).padStart(3, '0')}`;
    window.__xipeRefData.elements.push({
      id: elemId,
      selector: generateSelector(el),
      tag: el.tagName.toLowerCase(),
      bounding_box: {
        x: Math.round(rect.x),
        y: Math.round(rect.y),
        width: Math.round(rect.width),
        height: Math.round(rect.height)
      },
      screenshots: { full_page: null, element_crop: null },
      comment: null,
      extracted_assets: null
    });
    updateBadges();
  }

  function showOverlay(el) {
    hideOverlay();
    const rect = el.getBoundingClientRect();
    overlayEl = document.createElement('div');
    overlayEl.className = 'xipe-highlight-overlay';
    overlayEl.style.cssText = `
      position: fixed; top: ${rect.top}px; left: ${rect.left}px;
      width: ${rect.width}px; height: ${rect.height}px;
      pointer-events: none; z-index: 2147483646;
    `;
    labelEl = document.createElement('div');
    labelEl.className = 'xipe-selector-label';
    labelEl.textContent = generateSelector(el);
    labelEl.style.cssText = `
      position: fixed; top: ${rect.top - 24}px; left: ${rect.left}px;
      z-index: 2147483646; pointer-events: none;
    `;
    document.body.appendChild(overlayEl);
    document.body.appendChild(labelEl);
  }

  function hideOverlay() {
    if (overlayEl) { overlayEl.remove(); overlayEl = null; }
    if (labelEl) { labelEl.remove(); labelEl = null; }
  }

  // ===== Badge Updates =====
  function updateBadges() {
    const cc = window.__xipeRefData.colors.length;
    const ec = window.__xipeRefData.elements.length;
    document.getElementById('xipe-color-badge').textContent = cc;
    document.getElementById('xipe-elem-badge').textContent = ec;
    document.getElementById('xipe-color-count').textContent = cc;
    document.getElementById('xipe-elem-count').textContent = ec;
    document.getElementById('xipe-badge').textContent = cc + ec;
    // Update badge styling
    const cb = document.getElementById('xipe-color-badge');
    const eb = document.getElementById('xipe-elem-badge');
    cb.className = 'xipe-tool-badge' + (cc > 0 ? ' has-items' : '');
    eb.className = 'xipe-tool-badge' + (ec > 0 ? ' has-items' : '');
  }

  // ===== Tool Selection =====
  document.querySelectorAll('.xipe-tool-btn:not(.xipe-disabled)').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.xipe-tool-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const tool = btn.dataset.tool;
      colorPickerActive = tool === 'color';
      highlighterActive = tool === 'highlight';
      if (!highlighterActive) hideOverlay();
    });
  });

  // ===== Panel Toggle =====
  const hamburger = document.getElementById('xipe-hamburger');
  const panel = document.getElementById('xipe-panel');
  hamburger.addEventListener('click', (e) => {
    if (e.detail === 0) return; // ignore non-click
    hamburger.style.display = 'none';
    panel.classList.add('visible');
  });
  document.getElementById('xipe-close').addEventListener('click', () => {
    panel.classList.remove('visible');
    hamburger.style.display = 'flex';
  });
  // Start expanded
  hamburger.style.display = 'none';
  panel.classList.add('visible');

  // ===== Drag =====
  let isDragging = false, dragStartX, dragStartY, toolbarStartTop, toolbarStartRight;
  hamburger.addEventListener('mousedown', (e) => {
    if (panel.classList.contains('visible')) return;
    isDragging = true;
    dragStartX = e.clientX; dragStartY = e.clientY;
    const rect = toolbar.getBoundingClientRect();
    toolbarStartTop = rect.top;
    toolbarStartRight = window.innerWidth - rect.right;
    hamburger.style.cursor = 'grabbing';
    e.preventDefault();
  });
  document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    toolbar.style.top = (toolbarStartTop + e.clientY - dragStartY) + 'px';
    toolbar.style.right = (toolbarStartRight - (e.clientX - dragStartX)) + 'px';
  });
  document.addEventListener('mouseup', () => {
    if (isDragging) { isDragging = false; hamburger.style.cursor = 'grab'; }
  });

  // ===== Send References =====
  const sendBtn = document.getElementById('xipe-send');
  sendBtn.addEventListener('click', () => {
    const total = window.__xipeRefData.colors.length + window.__xipeRefData.elements.length;
    if (total === 0) {
      sendBtn.innerHTML = '<i class="bi bi-exclamation-circle"></i> No data collected';
      setTimeout(() => { sendBtn.innerHTML = '<i class="bi bi-send-fill"></i> Send References'; }, 2000);
      return;
    }
    sendBtn.innerHTML = '<i class="bi bi-arrow-repeat xipe-spin"></i> Sending...';
    sendBtn.disabled = true;
    setTimeout(() => {
      window.__xipeRefReady = true;
      sendBtn.innerHTML = '<i class="bi bi-check-circle-fill"></i> Sent to X-IPE!';
      sendBtn.style.background = '#059669';
      setTimeout(() => {
        sendBtn.innerHTML = '<i class="bi bi-send-fill"></i> Send References';
        sendBtn.style.background = '';
        sendBtn.disabled = false;
      }, 2300);
    }, 1200);
  });

  // ===== Page Event Listeners =====
  document.addEventListener('click', handleColorClick, true);
  document.addEventListener('mousemove', handleHighlightMove, true);
  document.addEventListener('click', handleHighlightClick, true);
})();
```

**Key design decisions:**

| Decision | Rationale |
|----------|-----------|
| Single IIFE, no external dependencies (except CDN fonts/icons) | Must work on any website; no build step; injected via `evaluate_script` |
| `window.__xipeRefData` + `window.__xipeRefReady` globals | Simple communication contract between injected toolbar and agent polling |
| Polling via `evaluate_script` (not `Runtime.addBinding`) | Chrome DevTools MCP may not expose raw CDP `Runtime.addBinding`. Polling is reliable and works with all MCP implementations. If `addBinding` support is available, it can be used as an optimization. |
| CSS class prefix `.xipe-` | Prevents style conflicts with any target page |
| Capture-phase event listeners (`true` 3rd arg) | Ensures toolbar intercepts clicks before page handlers |
| Phase 2 tools rendered but disabled | Shows the roadmap to users; no functional code needed yet |
| Guard `if (window.__xipeToolbarInjected)` | Prevents double injection if agent re-runs `evaluate_script` |

#### Toolbar CSS (Key Styles from Mockup)

The full CSS is derived from `injected-toolbar-v2.html`. Key visual specifications:

| Element | Property | Value |
|---------|----------|-------|
| Hamburger | Size | 52×52px circle |
| Hamburger | Background | `linear-gradient(135deg, #3730a3 0%, #4f46e5 100%)` |
| Hamburger | Shadow | `0 4px 16px rgba(55,48,163,0.35)` |
| Panel | Width | 272px |
| Panel | Background | `rgba(255,255,255,0.94)` + `backdrop-filter: blur(24px)` |
| Panel | Border-radius | 14px |
| Tool button | Padding | 9px 10px |
| Tool icon | Size | 30×30px, 8px radius |
| Active tool | Background | `rgba(55,48,163,0.08)` |
| Send button | Background | `#047857` (emerald) |
| Highlight overlay | Border | `2px solid #3730a3`, pulsing glow |
| Selector label | Background | `#3730a3`, white text, Space Mono 10px |
| Swatch pill | Background | white, 1px border, Space Mono 10px hex |

### Component 3: Screenshot Capture Strategy

Screenshots are taken by the **agent** (server-side via Chrome DevTools MCP), not by the in-page JavaScript. The flow:

```mermaid
flowchart TD
    A[Agent receives __xipeRefData] --> B{elements array empty?}
    B -->|Yes| F[Skip screenshots]
    B -->|No| C[For each element]
    C --> D1[take_screenshot fullPage: true]
    D1 --> D2[take_snapshot]
    D2 --> D3{Find element UID by selector?}
    D3 -->|Found| D4[take_screenshot uid: element_uid]
    D3 -->|Not found| D5[Log warning, skip element crop]
    D4 --> D6[Encode both as base64: prefix]
    D5 --> D6
    D6 --> D7{More elements?}
    D7 -->|Yes| C
    D7 -->|No| F
    F --> G[Call save_uiux_reference MCP tool]
```

**Finding element UID from CSS selector:**
1. Agent calls `take_snapshot()` to get the page's accessibility tree with UIDs
2. Agent calls `evaluate_script((sel) => { const el = document.querySelector(sel); return el ? el.getAttribute('data-xipe-uid') : null; }, args: [{uid: ...}])` — but this won't work since UIDs are snapshot-internal
3. **Better approach:** Agent calls `evaluate_script` to mark the element with a temporary attribute: `document.querySelector(selector).setAttribute('data-xipe-target', 'true')` → then `take_snapshot` → find element with `data-xipe-target` attribute in the snapshot tree → use that UID for `take_screenshot` → remove attribute

### File Summary

| File | Action | Description |
|------|--------|-------------|
| `.github/skills/x-ipe-tool-uiux-reference/SKILL.md` | Create | Agent skill definition with step-by-step procedure |
| `.github/skills/x-ipe-tool-uiux-reference/references/toolbar-template.md` | Create | Contains the toolbar IIFE source for agent to inject |
| `src/x_ipe/static/js/injected/xipe-toolbar.js` | Create | Source file for the toolbar IIFE (also referenced in toolbar-template.md) |

### Implementation Steps

1. **Create skill folder:** `.github/skills/x-ipe-tool-uiux-reference/`
2. **Write SKILL.md:** Agent skill procedure (parse → navigate → auth → inject → poll → screenshot → save)
3. **Write toolbar IIFE:** `src/x_ipe/static/js/injected/xipe-toolbar.js` — all HTML/CSS/JS in a single file
4. **Create toolbar-template.md:** Reference document containing the IIFE wrapped in a code block for the agent to read and inject
5. **Test manually:** Run `copilot execute uiux-reference --url https://example.com` and verify the full workflow

### Edge Cases & Error Handling

| Scenario | Component | Expected Behavior |
|----------|-----------|-------------------|
| Target page has CSP blocking inline styles | Toolbar IIFE | `evaluate_script` runs in isolated world, bypasses CSP. Toolbar injection works. |
| Target page navigates (SPA route change) | Toolbar IIFE | Toolbar stays (it's in DOM). `position: fixed` keeps it visible. If full reload, agent detects and re-injects. |
| User clicks "Send" with 0 items | Toolbar IIFE | Show "No data collected" message for 2s, reset. Agent never receives data. |
| CDP connection drops | Agent skill | 3 retries with exponential backoff (2s, 4s, 8s). On failure, save any partial data already received. |
| Element selector not found in snapshot | Agent skill | Log warning, skip screenshot for that element. Continue with remaining elements. |
| Very large page (slow screenshots) | Agent skill | Extend screenshot timeout to 15s per capture. |
| Auth URL same domain as target | Agent skill | Monitor path change instead of domain change. |
| Polling timeout (30 min, no data sent) | Agent skill | Inform user: "Session timed out. Please click Send References or re-run the command." |
| Double injection (agent re-runs evaluate_script) | Toolbar IIFE | Guard: `if (window.__xipeToolbarInjected) return;` prevents duplicate toolbars. |
| CDN fonts/icons fail to load | Toolbar IIFE | Toolbar degrades gracefully — system fonts used, icons show as empty squares. Functionality unaffected. |

---

## Design Change Log

| Date | Phase | Change Summary |
|------|-------|----------------|
| 02-13-2026 | Initial Design | Initial technical design: Agent skill procedure (SKILL.md) + Toolbar IIFE (xipe-toolbar.js) + screenshot capture strategy. Polling-based callback (evaluate_script) as primary mechanism for reliability across all MCP implementations. |
