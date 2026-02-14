# Technical Design: UIUX Reference Toolbar v2.0

> Feature ID: FEATURE-030-B (shell), FEATURE-030-B-THEME, FEATURE-030-B-MOCKUP
> Version: v2.0
> Status: Designed
> Last Updated: 02-14-2026

## Version History

| Version | Date | Description | Specification |
|---------|------|-------------|---------------|
| v2.0 | 02-14-2026 | Complete redesign — two-mode wizard shell, staged injection, offscreen canvas, smart-snap, agent rubric analysis | [specification.md](specification.md), [THEME/specification.md](../FEATURE-030-B-THEME/specification.md), [MOCKUP/specification.md](../FEATURE-030-B-MOCKUP/specification.md) |
| v1.1 | 02-14-2026 | ~~CR-001 enhancements~~ (deprecated by v2.0) | - |
| v1.0 | 02-13-2026 | ~~Initial design~~ (deprecated by v2.0) | - |

---

## Part 1 — Agent-Facing Summary

### Architecture Overview

The v2.0 system consists of three deliverables:

```
┌─────────────────────────────────────────────────────┐
│ Agent Skill (.github/skills/x-ipe-tool-uiux-reference/)   │
│  ├── SKILL.md (procedure)                                 │
│  └── references/                                          │
│       ├── toolbar-core.min.js     (shell IIFE — Stage 1)  │
│       ├── toolbar-theme.min.js    (theme mode — Stage 2)  │
│       └── toolbar-mockup.min.js   (mockup mode — Stage 2) │
├─────────────────────────────────────────────────────┤
│ Source Code (src/x_ipe/static/js/injected/)               │
│  ├── xipe-toolbar-core.js    (shell + infrastructure)     │
│  ├── xipe-toolbar-theme.js   (theme mode logic)           │
│  └── xipe-toolbar-mockup.js  (mockup mode logic)          │
├─────────────────────────────────────────────────────┤
│ Build Script (src/x_ipe/static/js/injected/build.py)      │
│  └── Minifies → references/*.min.js                       │
└─────────────────────────────────────────────────────┘
```

### Staged Injection Strategy

**Problem:** v1.1 injects 867 lines (~30KB) in a single `evaluate_script` call, causing perceptible delay (~300-500ms). v2.0 has even more code (two modes + magnifier + smart-snap).

**Solution: Two-stage injection**

| Stage | What | Size Target | When |
|-------|------|-------------|------|
| Stage 1 (Core) | Shell: hamburger, panel, mode tabs, toast, data store, comms, CSS | <8KB minified | Immediately after page load |
| Stage 2 (Mode) | Active mode logic injected on first mode activation | <5KB each | On demand (user expands panel) |

**Flow:**

```
Agent                          Browser
  │                              │
  ├─ evaluate_script(core.min) ──►│ ← Stage 1: shell visible in <500ms
  │                              │
  │◄── __xipeRefReady(init) ─────┤ ← Signals core ready
  │                              │
  │  (user hovers, panel expands)│
  │                              │
  ├─ evaluate_script(theme.min) ─►│ ← Stage 2: inject active mode
  │                              │
  │  ... user interacts ...      │
  │                              │
  │◄── __xipeRefReady(data) ─────┤ ← User clicks "Create Theme"
  │                              │
  ├─ save_uiux_reference(data) ──►│ ← Agent saves via MCP
```

**Agent injects BOTH mode scripts after core is ready** (not waiting for user to pick a mode), because:
- Eliminates latency when user switches modes
- Mode scripts are small (<5KB each)
- Total injection: 3 sequential evaluate_script calls, each fast

### Component Table

| Component | File | Tag | Description | Usage |
|-----------|------|-----|-------------|-------|
| ToolbarCore | xipe-toolbar-core.js | CORE | Shell: hamburger, panel, mode tabs, toast, data store, comms | Injected first. Creates DOM containers for modes. |
| ThemeMode | xipe-toolbar-theme.js | THEME | 3-step wizard: offscreen canvas color picker, magnifier, role annotation | Registers with core via `window.__xipeRegisterMode('theme', ThemeModeInit)` |
| MockupMode | xipe-toolbar-mockup.js | MOCKUP | 4-step wizard: smart-snap, instructions, analysis, generation | Registers with core via `window.__xipeRegisterMode('mockup', MockupModeInit)` |
| BuildScript | build.py | BUILD | Minifies source → references/*.min.js | Run during development. Agent reads .min.js files. |

### Usage Example (Agent Flow)

```
Step 1: Navigate to target URL
  → evaluate_script: check window.location.href (auth flow if needed)

Step 2: Inject Core
  → Read references/toolbar-core.min.js
  → evaluate_script(core_code)
  → Poll: window.__xipeToolbarReady === true (every 1s, 10s timeout)

Step 3: Inject Modes
  → Read references/toolbar-theme.min.js
  → evaluate_script(theme_code)
  → Read references/toolbar-mockup.min.js
  → evaluate_script(mockup_code)

Step 4: Wait for User Data
  → Poll: window.__xipeRefReady === true (every 3s, 30 min timeout)
  → On ready: read window.__xipeRefData

Step 5: Process Based on Mode
  IF mode === "theme":
    → Invoke brand-theme-creator skill with colors
  IF mode === "mockup":
    → Evaluate rubric (5 dimensions)
    → If missing data: write __xipeRefCommand { action: "deep_capture", target }
    → Wait for enriched data
    → Save via save_uiux_reference MCP
    → Generate mockup
    → Screenshot comparison (max 3 iterations)

Step 6: Cleanup
  → Report results to user
```

### Data Schema (v2.0)

```javascript
window.__xipeRefData = {
  mode: "theme" | "mockup",
  colors: [
    {
      id: "color-001",
      hex: "#be123c",
      rgb: "190, 18, 60",
      hsl: "347, 85%, 41%",
      source_selector: "body > div.pricing > button.cta",
      role: "primary",          // NEW: semantic role
      context: ""
    }
  ],
  components: [                  // NEW: replaces elements[]
    {
      id: "comp-001",
      selector: "body > section.hero",
      tag: "section",
      bounding_box: { x: 0, y: 0, width: 1200, height: 600 },
      screenshot_dataurl: "data:image/png;base64,...",
      html_css: {
        level: "minimal" | "deep",
        computed_styles: { ... },
        outer_html: null | "<section>..."    // only on deep capture
      },
      instruction: "Sticky header with parallax",
      agent_analysis: null | {
        confidence: {
          layout: "confident",
          typography: "uncertain",
          color_palette: "confident",
          spacing: "missing",
          visual_effects: "confident"
        },
        additional_captures: []
      }
    }
  ],
  design_tokens: null
};
```

### Communication Protocol

| Signal | Direction | Mechanism | Interval |
|--------|-----------|-----------|----------|
| `__xipeToolbarReady` | Toolbar → Agent | Set true when core DOM rendered | Agent polls 1s |
| `__xipeRefReady` | Toolbar → Agent | Set true when user sends data | Agent polls 3s |
| `__xipeRefData` | Toolbar → Agent | Read when __xipeRefReady | On demand |
| `__xipeRefCommand` | Agent → Toolbar | Agent writes, toolbar polls | Toolbar polls 1s |
| `__xipeRegisterMode` | Mode → Core | Function call during mode init | On inject |

---

## Part 2 — Implementation Guide

### 2.1 File Structure

```
src/x_ipe/static/js/injected/
├── xipe-toolbar-core.js         # Shell IIFE (FEATURE-030-B)
├── xipe-toolbar-theme.js        # Theme mode IIFE (FEATURE-030-B-THEME)
├── xipe-toolbar-mockup.js       # Mockup mode IIFE (FEATURE-030-B-MOCKUP)
└── build.py                     # Minification script

.github/skills/x-ipe-tool-uiux-reference/
├── SKILL.md                     # Updated agent procedure
└── references/
    ├── toolbar-template.md      # DEPRECATED — replaced by staged files
    ├── toolbar-core.min.js      # Minified shell (agent reads this)
    ├── toolbar-theme.min.js     # Minified theme mode
    └── toolbar-mockup.min.js    # Minified mockup mode
```

### 2.2 Core Shell (xipe-toolbar-core.js)

#### Module Structure

```javascript
(() => {
  // Guard
  if (window.__xipeToolbarInjected) return;
  window.__xipeToolbarInjected = true;

  // ===== Data Store =====
  // FR-12: shared data store
  window.__xipeRefData = { mode: 'theme', colors: [], components: [], design_tokens: null };
  window.__xipeRefReady = false;
  window.__xipeRefCommand = null;

  // ===== Mode Registry =====
  // FR-16: extension point for theme/mockup modes
  const modeRegistry = {};
  window.__xipeRegisterMode = (name, initFn) => {
    modeRegistry[name] = initFn;
    if (name === activeMode) activateMode(name);
  };

  // ===== Toast API =====
  // FR-11: toast(message, type, duration)
  window.__xipeToast = (msg, type = 'info', dur = 4000) => { ... };

  // ===== CSS Injection =====
  // FR-15: all .xipe-* scoped, FR-4: minified
  injectStyles();

  // ===== DOM Construction =====
  // FR-5: hamburger, FR-6: panel, FR-9: mode tabs
  buildToolbarDOM();

  // ===== Auto-Collapse =====
  // FR-7: 2s timer on mouseleave
  setupAutoCollapse();

  // ===== Drag =====
  // FR-8: drag hamburger
  setupDrag();

  // ===== Command Polling =====
  // FR-14: poll __xipeRefCommand every 1s
  setInterval(pollCommands, 1000);

  // ===== Signal Ready =====
  window.__xipeToolbarReady = true;
})();
```

#### CSS Strategy

All styles injected as a single `<style>` element with `.xipe-*` prefix:

```css
/* Critical path — hamburger visible immediately */
.xipe-toolbar { position: fixed; z-index: 2147483647; }
.xipe-hamburger { /* 52x52, gradient, transitions */ }

/* Panel — shown on hover */
.xipe-panel { width: 280px; max-height: 80vh; overflow-y: auto; }
.xipe-panel.xipe-collapsed { width: 0; opacity: 0; pointer-events: none; }

/* Transitions: CSS-only, GPU-accelerated */
.xipe-panel { transition: width 350ms cubic-bezier(0.22,1,0.36,1), opacity 350ms; }
```

**Font loading (NFR-5):**

```javascript
// Load fonts AFTER initial render
requestIdleCallback(() => {
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=Space+Mono&family=DM+Sans:wght@400;500&display=swap';
  document.head.appendChild(link);
});
```

#### Auto-Collapse Logic (FR-7)

```javascript
let collapseTimer = null;
const COLLAPSE_DELAY = 2000;

panel.addEventListener('mouseenter', () => {
  clearTimeout(collapseTimer);
  expandPanel();
});

panel.addEventListener('mouseleave', () => {
  collapseTimer = setTimeout(collapsePanel, COLLAPSE_DELAY);
});

hamburger.addEventListener('mouseenter', () => {
  clearTimeout(collapseTimer);
  expandPanel();
});
```

#### Mode Switching (FR-9, FR-10)

```javascript
let activeMode = 'theme'; // FR-10: default

function switchMode(mode) {
  activeMode = mode;
  window.__xipeRefData.mode = mode;
  // Update tab UI
  tabs.forEach(t => t.classList.toggle('xipe-active', t.dataset.mode === mode));
  // Show/hide content containers
  Object.entries(modeContainers).forEach(([name, el]) => {
    el.style.display = name === mode ? 'block' : 'none';
  });
  // Activate registered mode
  if (modeRegistry[mode]) activateMode(mode);
}
```

#### Command Polling (FR-14)

```javascript
function pollCommands() {
  const cmd = window.__xipeRefCommand;
  if (!cmd) return;
  window.__xipeRefCommand = null;

  try {
    switch (cmd.action) {
      case 'deep_capture':
        handleDeepCapture(cmd.target);
        break;
      case 'reset':
        handleReset();
        break;
      default:
        window.__xipeToast(`Unknown command: ${cmd.action}`, 'error');
    }
  } catch (e) {
    window.__xipeToast(`Command error: ${e.message}`, 'error');
  }
}

function handleDeepCapture(targetId) {
  const comp = window.__xipeRefData.components.find(c => c.id === targetId);
  if (!comp) {
    window.__xipeToast(`Component ${targetId} not found`, 'error');
    return;
  }
  const el = document.querySelector(comp.selector);
  if (!el) {
    window.__xipeToast(`Element not found for ${targetId}`, 'error');
    return;
  }
  // Capture all computed styles
  const styles = window.getComputedStyle(el);
  const allStyles = {};
  for (let i = 0; i < styles.length; i++) {
    allStyles[styles[i]] = styles.getPropertyValue(styles[i]);
  }
  comp.html_css = {
    level: 'deep',
    computed_styles: allStyles,
    outer_html: el.outerHTML
  };
  window.__xipeToast(`Deep capture complete: ${targetId}`, 'success');
  window.__xipeRefReady = true;
}
```

#### CSS Selector Generation

```javascript
function generateSelector(el) {
  if (el.id) return `#${CSS.escape(el.id)}`;
  const parts = [];
  let current = el;
  while (current && current !== document.body && current !== document.documentElement) {
    let part = current.tagName.toLowerCase();
    // Use stable classes (exclude dynamic: random chars, hashes)
    const stableClasses = [...current.classList]
      .filter(c => !/[0-9a-f]{6,}|__|--[a-z0-9]{4,}/i.test(c))
      .slice(0, 2);
    if (stableClasses.length) {
      part += '.' + stableClasses.map(CSS.escape).join('.');
    } else {
      const idx = [...current.parentElement.children]
        .filter(c => c.tagName === current.tagName)
        .indexOf(current);
      if (idx > 0) part += `:nth-of-type(${idx + 1})`;
    }
    parts.unshift(part);
    current = current.parentElement;
  }
  return 'body > ' + parts.join(' > ');
}
```

### 2.3 Theme Mode (xipe-toolbar-theme.js)

#### Module Structure

```javascript
(() => {
  // Wait for core
  if (!window.__xipeRegisterMode) {
    console.warn('[X-IPE Theme] Core not loaded');
    return;
  }

  window.__xipeRegisterMode('theme', function ThemeModeInit(container) {
    // container = DOM element provided by core for this mode's UI

    let colorCounter = 0;
    let magnifierActive = false;
    let offscreenCanvas = null;
    let offscreenCtx = null;
    let currentStep = 1; // 1: Pick, 2: Annotate, 3: Create

    // ===== Step Navigation =====
    buildStepUI(container);

    // ===== Offscreen Canvas =====
    renderOffscreenCanvas();

    // ===== Magnifier =====
    setupMagnifier();

    // ===== Color List =====
    buildColorList(container);

    // ===== Role Annotation =====
    buildRoleUI(container);

    // ===== Create Theme =====
    buildCreateButton(container);
  });
})();
```

#### Offscreen Canvas Rendering (FR-T1)

```javascript
function renderOffscreenCanvas() {
  // Use html2canvas-lite approach: render DOM to canvas
  // NOTE: Full html2canvas is too heavy (400KB). Use lightweight approach.
  offscreenCanvas = document.createElement('canvas');
  offscreenCanvas.width = window.innerWidth;
  offscreenCanvas.height = window.innerHeight;
  offscreenCtx = offscreenCanvas.getContext('2d', { willReadFrequently: true });

  // Strategy: capture visible viewport as image via CDP screenshot
  // Agent provides screenshot_dataurl after core injection
  // Toolbar loads it into canvas for pixel sampling
  //
  // Alternative: Use drawImage with DOM range rendering
  // This avoids CORS but is limited to rendered pixel data

  // Debounced re-render on scroll/resize
  let renderTimer;
  const debouncedRender = () => {
    clearTimeout(renderTimer);
    renderTimer = setTimeout(() => {
      // Request agent to take fresh screenshot via command
      window.__xipeRefCommand = null;
      window.__xipeToast('Updating viewport capture...', 'info', 2000);
      // Agent detects need via polling and provides fresh screenshot
    }, 200);
  };
  window.addEventListener('scroll', debouncedRender, { passive: true });
  window.addEventListener('resize', debouncedRender, { passive: true });
}
```

**Canvas Population Strategy:**

The offscreen canvas is populated in two ways:
1. **Agent-provided screenshot**: After core injection, agent takes `take_screenshot()` and injects the dataURL via `evaluate_script(() => { window.__xipeViewportScreenshot = "data:..." })`. Toolbar loads this into the canvas.
2. **Inline element sampling (fallback)**: For elements without CORS issues, use `getComputedStyle(el).backgroundColor` at click point via `document.elementsFromPoint(x, y)`.

This hybrid approach provides:
- Accurate pixel data for images, gradients, and complex backgrounds (via screenshot)
- Fast color sampling without re-rendering (canvas getImageData)
- CORS safety (screenshot provided by agent, not by page resources)

#### Magnifier (FR-T2)

```javascript
function setupMagnifier() {
  const magnifier = document.createElement('div');
  magnifier.className = 'xipe-magnifier';
  // 120px circle, positioned near cursor
  document.body.appendChild(magnifier);

  const magnifierCanvas = document.createElement('canvas');
  magnifierCanvas.width = 120;
  magnifierCanvas.height = 120;
  const magCtx = magnifierCanvas.getContext('2d');
  magnifier.appendChild(magnifierCanvas);

  const hexLabel = document.createElement('div');
  hexLabel.className = 'xipe-magnifier-hex';
  magnifier.appendChild(hexLabel);

  let rafId = null;

  function updateMagnifier(e) {
    if (!magnifierActive || !offscreenCtx) return;

    // Position: offset top-right of cursor (20px gap)
    magnifier.style.left = (e.clientX + 20) + 'px';
    magnifier.style.top = (e.clientY - 140) + 'px';

    // Sample 11x11 pixel area from offscreen canvas at cursor position
    const GRID = 11;
    const ZOOM = 10;
    const halfGrid = Math.floor(GRID / 2);

    try {
      const imageData = offscreenCtx.getImageData(
        e.clientX - halfGrid, e.clientY - halfGrid,
        GRID, GRID
      );

      // Draw zoomed grid
      magCtx.clearRect(0, 0, 120, 120);
      const cellSize = 120 / GRID;
      for (let y = 0; y < GRID; y++) {
        for (let x = 0; x < GRID; x++) {
          const idx = (y * GRID + x) * 4;
          const r = imageData.data[idx];
          const g = imageData.data[idx + 1];
          const b = imageData.data[idx + 2];
          magCtx.fillStyle = `rgb(${r},${g},${b})`;
          magCtx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
          // Grid lines
          magCtx.strokeStyle = 'rgba(255,255,255,0.15)';
          magCtx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
        }
      }

      // Crosshair at center
      const center = halfGrid * cellSize + cellSize / 2;
      magCtx.strokeStyle = '#10b981';
      magCtx.lineWidth = 2;
      magCtx.beginPath();
      magCtx.moveTo(center, 0); magCtx.lineTo(center, 120);
      magCtx.moveTo(0, center); magCtx.lineTo(120, center);
      magCtx.stroke();

      // Center pixel hex
      const ci = (halfGrid * GRID + halfGrid) * 4;
      const hex = rgbToHex(imageData.data[ci], imageData.data[ci+1], imageData.data[ci+2]);
      hexLabel.textContent = hex;
    } catch (e) {
      // CORS tainted canvas — show checkerboard
      magCtx.fillStyle = '#666';
      magCtx.fillRect(0, 0, 120, 120);
      hexLabel.textContent = 'CORS';
    }
  }

  document.addEventListener('mousemove', (e) => {
    if (!magnifierActive) return;
    cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(() => updateMagnifier(e));
  }, true);
}
```

#### Color Sampling (FR-T3, FR-T4, FR-T5)

```javascript
function handleColorClick(e) {
  if (!magnifierActive) return;
  e.preventDefault();
  e.stopPropagation();

  try {
    const imageData = offscreenCtx.getImageData(e.clientX, e.clientY, 1, 1);
    const [r, g, b] = imageData.data;
    const hex = rgbToHex(r, g, b);
    const hsl = rgbToHsl(r, g, b);

    colorCounter++;
    const id = `color-${String(colorCounter).padStart(3, '0')}`;

    // Element at click for selector
    const el = document.elementFromPoint(e.clientX, e.clientY);
    const selector = el ? generateSelector(el) : 'unknown';

    const colorEntry = { id, hex, rgb: `${r}, ${g}, ${b}`, hsl, source_selector: selector, role: '', context: '' };
    window.__xipeRefData.colors.push(colorEntry);

    // Visual feedback: swatch pill near click
    showSwatchPill(e.clientX, e.clientY, hex);

    // Update color list in panel
    renderColorList();

    window.__xipeToast(`Picked ${hex}`, 'info', 2000);
  } catch (err) {
    window.__xipeToast('Cross-origin content cannot be color-sampled.', 'error');
  }
}

document.addEventListener('click', handleColorClick, true);
```

#### Role Annotation (FR-T6)

```javascript
function buildRoleUI(container) {
  // Step 2: For each color, show role chips
  // Renders inside step-2 container
  const roles = ['primary', 'secondary', 'accent'];

  function renderRoleAnnotation() {
    const step2 = container.querySelector('.xipe-step-2');
    step2.innerHTML = '';
    window.__xipeRefData.colors.forEach((color, i) => {
      const row = document.createElement('div');
      row.className = 'xipe-role-row';
      row.innerHTML = `
        <span class="xipe-swatch" style="background:${color.hex}"></span>
        <span class="xipe-hex">${color.hex}</span>
        <div class="xipe-role-chips">
          ${roles.map(r => `<button class="xipe-chip ${color.role === r ? 'xipe-active' : ''}" data-role="${r}">${r}</button>`).join('')}
          <input class="xipe-custom-role" placeholder="custom" value="${!roles.includes(color.role) ? color.role : ''}" />
        </div>
      `;
      // Chip click
      row.querySelectorAll('.xipe-chip').forEach(chip => {
        chip.addEventListener('click', () => {
          color.role = chip.dataset.role;
          renderRoleAnnotation();
        });
      });
      // Custom input
      row.querySelector('.xipe-custom-role').addEventListener('input', (e) => {
        color.role = e.target.value;
      });
      step2.appendChild(row);
    });
  }
  return renderRoleAnnotation;
}
```

### 2.4 Mockup Mode (xipe-toolbar-mockup.js)

#### Module Structure

```javascript
(() => {
  if (!window.__xipeRegisterMode) {
    console.warn('[X-IPE Mockup] Core not loaded');
    return;
  }

  window.__xipeRegisterMode('mockup', function MockupModeInit(container) {
    let compCounter = 0;
    let snapActive = false;
    let currentStep = 1; // 1: Select, 2: Instructions, 3: Analyze, 4: Generate
    const MAX_COMPONENTS = 20;

    // ===== Step Navigation =====
    buildStepUI(container, 4);

    // ===== Smart-Snap =====
    setupSmartSnap();

    // ===== Component List =====
    buildComponentList(container);

    // ===== Instructions =====
    buildInstructionUI(container);

    // ===== Analyze Button =====
    buildAnalyzeButton(container);

    // ===== Generate Button =====
    buildGenerateButton(container);
  });
})();
```

#### Smart-Snap Detection (FR-M1, FR-M2)

```javascript
const SEMANTIC_TAGS = new Set([
  'SECTION', 'NAV', 'ARTICLE', 'ASIDE', 'HEADER', 'FOOTER', 'MAIN', 'FIGURE'
]);

function findSemanticContainer(el) {
  let current = el;
  let depth = 0;
  const MAX_DEPTH = 5;

  while (current && current !== document.body && depth < MAX_DEPTH) {
    if (SEMANTIC_TAGS.has(current.tagName) || current.getAttribute('role')) {
      return current;
    }
    current = current.parentElement;
    depth++;
  }

  // Fallback: nearest div with dimensions > 50x50
  current = el;
  depth = 0;
  while (current && current !== document.body && depth < MAX_DEPTH) {
    if (current.tagName === 'DIV' && current.offsetWidth > 50 && current.offsetHeight > 50) {
      return current;
    }
    current = current.parentElement;
    depth++;
  }

  return null; // No suitable container
}

function handleSnapClick(e) {
  if (!snapActive) return;

  // Ignore clicks on toolbar
  if (e.target.closest('.xipe-toolbar')) return;

  e.preventDefault();
  e.stopPropagation();

  const target = findSemanticContainer(e.target);
  if (!target) {
    window.__xipeToast('Please click a more specific element.', 'error');
    return;
  }

  if (target === document.body || target === document.documentElement) {
    window.__xipeToast('Please click a more specific element.', 'error');
    return;
  }

  if (window.__xipeRefData.components.length >= MAX_COMPONENTS) {
    window.__xipeToast('Maximum 20 components per session.', 'error');
    return;
  }

  captureComponent(target);
}

document.addEventListener('click', handleSnapClick, true);
```

#### Component Capture (FR-M5, FR-M6)

```javascript
function captureComponent(el) {
  compCounter++;
  const id = `comp-${String(compCounter).padStart(3, '0')}`;
  const rect = el.getBoundingClientRect();
  const selector = generateSelector(el);
  const tag = el.tagName.toLowerCase();

  // Lightweight computed styles (limited property set)
  const CAPTURE_PROPS = [
    'display', 'position', 'flex-direction', 'justify-content', 'align-items',
    'grid-template-columns', 'grid-template-rows',
    'width', 'height', 'min-width', 'max-width', 'min-height', 'max-height',
    'margin', 'padding', 'border', 'border-radius',
    'background', 'background-color', 'background-image',
    'color', 'font-family', 'font-size', 'font-weight', 'line-height',
    'box-shadow', 'opacity', 'overflow', 'z-index'
  ];
  const styles = window.getComputedStyle(el);
  const computedStyles = {};
  CAPTURE_PROPS.forEach(p => { computedStyles[p] = styles.getPropertyValue(p); });

  // Screenshot: crop from viewport canvas (if available)
  let screenshotDataurl = null;
  if (window.__xipeViewportScreenshot) {
    screenshotDataurl = cropScreenshot(rect);
  }

  const component = {
    id, selector, tag,
    bounding_box: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
    screenshot_dataurl: screenshotDataurl,
    html_css: { level: 'minimal', computed_styles: computedStyles, outer_html: null },
    instruction: '',
    agent_analysis: null
  };

  window.__xipeRefData.components.push(component);

  // Show overlay
  showSnapOverlay(rect, tag, selector);

  // Update component list
  renderComponentList();

  window.__xipeToast(`Selected: <${tag}>`, 'info', 2000);
}
```

#### Snap Overlay with Drag Handles (FR-M3, FR-M4)

```javascript
function showSnapOverlay(rect, tag, selector) {
  const overlay = document.createElement('div');
  overlay.className = 'xipe-snap-overlay';
  overlay.style.cssText = `
    position: fixed;
    left: ${rect.x}px; top: ${rect.y}px;
    width: ${rect.width}px; height: ${rect.height}px;
    border: 2px dashed #10b981;
    pointer-events: none;
    z-index: 2147483646;
  `;

  // Tag badge
  const badge = document.createElement('span');
  badge.className = 'xipe-tag-badge';
  badge.textContent = tag;
  badge.style.cssText = `
    position: absolute; top: -22px; left: 0;
    background: #10b981; color: white;
    font-size: 10px; padding: 2px 6px; border-radius: 4px;
    font-family: 'Space Mono', monospace;
    pointer-events: none;
  `;
  overlay.appendChild(badge);

  // 8 drag handles (corners + midpoints)
  const positions = [
    { x: 0, y: 0, cursor: 'nw-resize' },
    { x: 0.5, y: 0, cursor: 'n-resize' },
    { x: 1, y: 0, cursor: 'ne-resize' },
    { x: 1, y: 0.5, cursor: 'e-resize' },
    { x: 1, y: 1, cursor: 'se-resize' },
    { x: 0.5, y: 1, cursor: 's-resize' },
    { x: 0, y: 1, cursor: 'sw-resize' },
    { x: 0, y: 0.5, cursor: 'w-resize' },
  ];
  positions.forEach(pos => {
    const handle = document.createElement('div');
    handle.className = 'xipe-drag-handle';
    handle.style.cssText = `
      position: absolute;
      left: ${pos.x * 100}%; top: ${pos.y * 100}%;
      width: 8px; height: 8px; margin: -4px;
      background: #10b981; cursor: ${pos.cursor};
      pointer-events: auto;
    `;
    handle.addEventListener('mousedown', (e) => startResize(e, overlay, pos, compCounter));
    overlay.appendChild(handle);
  });

  document.body.appendChild(overlay);
}
```

### 2.5 Build Script (build.py)

```python
"""Minify toolbar source files for injection."""
import re
from pathlib import Path

SRC_DIR = Path('src/x_ipe/static/js/injected')
OUT_DIR = Path('.github/skills/x-ipe-tool-uiux-reference/references')

FILES = {
    'xipe-toolbar-core.js': 'toolbar-core.min.js',
    'xipe-toolbar-theme.js': 'toolbar-theme.min.js',
    'xipe-toolbar-mockup.js': 'toolbar-mockup.min.js',
}

def minify(source: str) -> str:
    """Basic JS minification: strip comments, collapse whitespace."""
    # Remove single-line comments (but not URLs with //)
    result = re.sub(r'(?<!:)//(?!/).*?$', '', source, flags=re.MULTILINE)
    # Remove multi-line comments
    result = re.sub(r'/\*.*?\*/', '', result, flags=re.DOTALL)
    # Collapse whitespace
    result = re.sub(r'\s+', ' ', result)
    # Remove space around operators
    result = re.sub(r'\s*([={}();,:<>+\-*/&|!?])\s*', r'\1', result)
    return result.strip()

def build():
    for src_name, out_name in FILES.items():
        src = SRC_DIR / src_name
        out = OUT_DIR / out_name
        if not src.exists():
            print(f'SKIP {src_name} (not found)')
            continue
        source = src.read_text()
        minified = minify(source)
        out.write_text(minified)
        ratio = len(minified) / len(source) * 100
        print(f'{src_name} → {out_name}: {len(source)} → {len(minified)} bytes ({ratio:.0f}%)')

if __name__ == '__main__':
    build()
```

### 2.6 Injection Performance Analysis

| Metric | v1.1 | v2.0 Target | Strategy |
|--------|------|-------------|----------|
| IIFE size (unminified) | 867 lines (~30KB) | Core: ~300 lines, Modes: ~200 each | Split into 3 files |
| IIFE size (minified) | N/A (not minified) | Core: <8KB, Modes: <5KB each | Basic minification |
| Time to hamburger visible | ~500ms | <300ms | Stage 1 only: smaller payload |
| Total injection time | ~500ms (one call) | ~200ms × 3 = ~600ms total | But first paint at 200ms |
| Font loading | Synchronous (blocks render) | Lazy via requestIdleCallback | NFR-5 |
| Panel interactive | ~500ms | <500ms (core only) | Modes load after core |

**Key insight:** Time-to-first-paint (hamburger visible) drops from ~500ms to ~200ms because Stage 1 is 1/3 the size. Total injection is slightly longer but perceived performance is much better.

### 2.7 Agent Skill Updates

The SKILL.md procedure must be updated:

```markdown
## Injection (Updated for v2.0)

Step 4: Inject Toolbar Core
  → Read references/toolbar-core.min.js
  → CALL evaluate_script(function: CORE_CODE)
  → Poll: evaluate_script(() => window.__xipeToolbarReady) every 1s, 10s timeout

Step 5: Inject Mode Scripts
  → Read references/toolbar-theme.min.js
  → CALL evaluate_script(function: THEME_CODE)
  → Read references/toolbar-mockup.min.js
  → CALL evaluate_script(function: MOCKUP_CODE)

Step 6: Provide Viewport Screenshot
  → CALL take_screenshot(format: "png")
  → Convert to data URL
  → CALL evaluate_script((dataUrl) => { window.__xipeViewportScreenshot = dataUrl })

Step 7: Await User Data
  → Poll: evaluate_script(() => window.__xipeRefReady ? window.__xipeRefData : null)
  → Interval: 3s, Timeout: 30 min
```

### 2.8 Utility Functions

```javascript
function rgbToHex(r, g, b) {
  return '#' + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('');
}

function rgbToHsl(r, g, b) {
  r /= 255; g /= 255; b /= 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  let h, s, l = (max + min) / 2;
  if (max === min) { h = s = 0; }
  else {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
      case g: h = ((b - r) / d + 2) / 6; break;
      case b: h = ((r - g) / d + 4) / 6; break;
    }
  }
  return `${Math.round(h * 360)}, ${Math.round(s * 100)}%, ${Math.round(l * 100)}%`;
}

function cropScreenshot(rect) {
  // Crop from full-viewport screenshot loaded in offscreen canvas
  if (!offscreenCanvas) return null;
  const crop = document.createElement('canvas');
  crop.width = rect.width;
  crop.height = rect.height;
  const ctx = crop.getContext('2d');
  ctx.drawImage(offscreenCanvas, rect.x, rect.y, rect.width, rect.height, 0, 0, rect.width, rect.height);
  return crop.toDataURL('image/png');
}
```

### 2.9 Error Handling & Edge Cases

| Case | Handling |
|------|----------|
| Core not loaded when mode injected | Mode IIFE checks `window.__xipeRegisterMode` existence, logs warning |
| CORS tainted canvas | try/catch on getImageData, show checkerboard in magnifier, warning toast |
| Element removed after capture | Component marked with warning. Agent uses cached bounding_box and styles |
| Page reload | All state lost. Agent re-injects from Step 4 |
| CSP blocks inline styles | Toolbar degrades: system fonts, no transitions. Warning toast |
| > 20 components | Toast + block further adds |
| Deep capture target not found | Toast error, component marked, agent uses available data |
| Rapid mode switch | Last mode wins. No animation queue |

### 2.10 Testing Strategy

Tests live in `tests/test_uiux_reference_toolbar.py`. Key test areas:

1. **Core shell**: hamburger render, panel expand/collapse, mode switching, toast API
2. **Data schema**: correct initialization, mode field, color/component entries
3. **Communication**: __xipeRefReady, __xipeRefCommand polling, deep_capture
4. **Theme mode**: color sampling, role annotation, create theme trigger
5. **Mockup mode**: smart-snap detection, component capture, instruction storage
6. **Build script**: minification produces valid JS, size targets met
7. **Integration**: staged injection sequence, agent skill flow

### 2.11 KISS / YAGNI / DRY Principles

- **KISS**: Each file (core, theme, mockup) is a self-contained IIFE. No build toolchain beyond basic minification. No framework dependencies.
- **YAGNI**: No undo/redo, no keyboard shortcuts, no cross-origin iframe capture, no typography extraction. Only what's in the spec.
- **DRY**: Shared utilities (selector generation, color conversion, toast) live in core. Modes call `window.__xipeToast()` and `generateSelector()` from core scope.

### 2.12 Dependencies & Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| html2canvas library too heavy for injection | Bloats Stage 2 | Use agent-provided screenshot instead of client-side rendering |
| CORS prevents canvas pixel sampling | Theme mode degraded | Hybrid approach: agent screenshot + fallback element inspection |
| CDP evaluate_script payload limit | Injection fails | Minification + staged approach keeps each call <8KB |
| Font CDN unavailable | Visual degradation | font-display: swap + system font fallback stack |
| Page JS modifies __xipe* globals | Data corruption | Use Object.defineProperty with configurable: false for critical globals |

---

## Open Questions

None — all design decisions resolved.
