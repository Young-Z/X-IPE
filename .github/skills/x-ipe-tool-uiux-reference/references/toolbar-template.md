# Toolbar Template

This file contains the toolbar IIFE source code that the agent injects into the target page via `evaluate_script`.

**Usage:** Read the JavaScript code block below and pass it as the `function` parameter to `evaluate_script`.

```javascript
(() => {
  // Guard: prevent double injection
  if (window.__xipeToolbarInjected) return;
  window.__xipeToolbarInjected = true;

  // ===== Data Store =====
  window.__xipeRefData = { colors: [], elements: [], design_tokens: null };
  window.__xipeRefReady = false;

  // ===== CSS Variables & Styles =====
  const style = document.createElement('style');
  style.textContent = `
    .xipe-toolbar {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 2147483647;
      font-family: 'Outfit', sans-serif;
      user-select: none;
    }
    .xipe-hamburger {
      width: 52px;
      height: 52px;
      background: linear-gradient(135deg, #3730a3 0%, #4f46e5 100%);
      backdrop-filter: blur(20px);
      border: 2px solid rgba(255, 255, 255, 0.25);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: grab;
      color: white;
      font-size: 20px;
      box-shadow: 0 4px 16px rgba(55, 48, 163, 0.35), 0 0 0 1px rgba(55, 48, 163, 0.08);
      transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);
      position: relative;
    }
    .xipe-hamburger:hover {
      background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%);
      border-color: rgba(255, 255, 255, 0.4);
      box-shadow: 0 6px 24px rgba(79, 70, 229, 0.45), 0 0 0 3px rgba(79, 70, 229, 0.15);
      transform: scale(1.1);
    }
    .xipe-hamburger .xipe-logo {
      font-size: 9px;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: white;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }
    .xipe-hamburger .badge-count {
      position: absolute;
      top: -5px;
      right: -5px;
      width: 18px;
      height: 18px;
      background: #047857;
      color: white;
      font-size: 10px;
      font-weight: 700;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 1px 4px rgba(4, 120, 87, 0.3);
    }
    .xipe-panel {
      position: absolute;
      top: 0;
      right: 0;
      width: 272px;
      background: rgba(255, 255, 255, 0.94);
      backdrop-filter: blur(24px);
      border: 1px solid rgba(55, 48, 163, 0.15);
      border-radius: 14px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.1), 0 0 0 1px rgba(55, 48, 163, 0.04);
      overflow: hidden;
      display: none;
      animation: xipePanelSlideIn 0.35s cubic-bezier(0.22, 1, 0.36, 1);
    }
    .xipe-panel.visible { display: block; }
    @keyframes xipePanelSlideIn {
      from { opacity: 0; transform: translateY(-8px) scale(0.96); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }
    .xipe-panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 14px;
      border-bottom: 1px solid rgba(224, 220, 212, 0.9);
    }
    .xipe-panel-title {
      display: flex;
      align-items: center;
      gap: 7px;
      font-size: 12.5px;
      font-weight: 600;
      color: #1a1a2e;
      letter-spacing: 0.01em;
    }
    .xipe-panel-title .logo-dot {
      width: 8px;
      height: 8px;
      background: #3730a3;
      border-radius: 50%;
      box-shadow: 0 0 6px rgba(55, 48, 163, 0.35);
    }
    .xipe-panel-close {
      width: 26px;
      height: 26px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: none;
      border: none;
      color: #8e8e9f;
      font-size: 16px;
      cursor: pointer;
      border-radius: 6px;
      transition: all 0.2s;
    }
    .xipe-panel-close:hover {
      background: rgba(55, 48, 163, 0.06);
      color: #1a1a2e;
    }
    .xipe-tools { padding: 6px 8px; }
    .xipe-tool-btn {
      display: flex;
      align-items: center;
      gap: 10px;
      width: 100%;
      padding: 9px 10px;
      background: none;
      border: 1px solid transparent;
      border-radius: 6px;
      color: #4a4a5c;
      font-family: 'Outfit', sans-serif;
      font-size: 12.5px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.22, 1, 0.36, 1);
      text-align: left;
    }
    .xipe-tool-btn:hover {
      background: rgba(55, 48, 163, 0.06);
      color: #1a1a2e;
      border-color: rgba(55, 48, 163, 0.06);
    }
    .xipe-tool-btn.active {
      background: rgba(55, 48, 163, 0.08);
      color: #3730a3;
      border-color: rgba(55, 48, 163, 0.12);
    }
    .xipe-tool-btn.xipe-disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    .xipe-tool-icon {
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 8px;
      font-size: 14px;
      flex-shrink: 0;
    }
    .xipe-tool-icon.color-picker { background: rgba(190, 18, 60, 0.06); color: #be123c; }
    .xipe-tool-icon.highlighter { background: rgba(55, 48, 163, 0.08); color: #3730a3; }
    .xipe-tool-icon.commenter { background: rgba(180, 83, 9, 0.06); color: #b45309; }
    .xipe-tool-icon.extractor { background: rgba(4, 120, 87, 0.06); color: #047857; }
    .xipe-tool-info {
      display: flex;
      flex-direction: column;
      gap: 1px;
    }
    .xipe-tool-name { font-size: 12.5px; font-weight: 500; }
    .xipe-tool-desc { font-size: 10px; color: #8e8e9f; }
    .xipe-tool-badge {
      margin-left: auto;
      font-size: 10px;
      font-weight: 600;
      padding: 2px 7px;
      border-radius: 100px;
      background: rgba(245, 243, 238, 0.8);
      color: #8e8e9f;
    }
    .xipe-tool-badge.has-items {
      background: rgba(4, 120, 87, 0.06);
      color: #047857;
    }
    .xipe-phase-sep {
      padding: 8px 12px 4px;
      font-size: 9.5px;
      font-weight: 600;
      color: #8e8e9f;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }
    .xipe-divider {
      height: 1px;
      background: rgba(224, 220, 212, 0.9);
      margin: 4px 8px;
    }
    .xipe-collected {
      padding: 10px 14px;
      border-top: 1px solid rgba(224, 220, 212, 0.9);
      background: rgba(4, 120, 87, 0.06);
    }
    .xipe-collected-title {
      font-size: 10px;
      font-weight: 600;
      color: #8e8e9f;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }
    .xipe-collected-items {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
    }
    .xipe-collected-tag {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px 8px;
      border-radius: 100px;
      font-size: 10px;
      font-weight: 500;
    }
    .xipe-collected-tag.colors { background: rgba(190, 18, 60, 0.06); color: #be123c; }
    .xipe-collected-tag.elements { background: rgba(55, 48, 163, 0.08); color: #3730a3; }
    .xipe-send-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      width: calc(100% - 16px);
      margin: 8px 8px 10px;
      padding: 10px;
      background: #047857;
      color: white;
      border: none;
      border-radius: 6px;
      font-family: 'Outfit', sans-serif;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
      box-shadow: 0 2px 8px rgba(4, 120, 87, 0.2);
    }
    .xipe-send-btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(4, 120, 87, 0.3);
      background: #059669;
    }
    .xipe-drag-hint {
      position: fixed;
      top: 70px;
      right: 20px;
      display: flex;
      align-items: center;
      gap: 6px;
      background: white;
      border: 1px solid #d0ccc4;
      border-radius: 100px;
      padding: 5px 12px;
      font-family: 'Outfit', sans-serif;
      font-size: 10px;
      color: #8e8e9f;
      z-index: 2147483646;
      animation: xipeHintFade 3s ease-in-out forwards;
      pointer-events: none;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    @keyframes xipeHintFade {
      0% { opacity: 0; transform: translateY(-4px); }
      15% { opacity: 1; transform: translateY(0); }
      75% { opacity: 1; }
      100% { opacity: 0; }
    }
    .xipe-highlight-overlay {
      border: 2px solid #3730a3;
      border-radius: 4px;
      animation: xipeHighlightPulse 1.5s ease-in-out infinite;
    }
    @keyframes xipeHighlightPulse {
      0%, 100% { box-shadow: 0 0 0 0 rgba(55, 48, 163, 0.2); }
      50% { box-shadow: 0 0 0 6px rgba(55, 48, 163, 0); }
    }
    .xipe-selector-label {
      background: #3730a3;
      color: white;
      font-family: 'Space Mono', monospace;
      font-size: 10px;
      padding: 3px 8px;
      border-radius: 4px;
      white-space: nowrap;
    }
    .xipe-picked-swatch {
      display: flex;
      align-items: center;
      gap: 6px;
      background: white;
      border: 1px solid #d0ccc4;
      border-radius: 100px;
      padding: 4px 10px 4px 4px;
      font-family: 'Space Mono', monospace;
      font-size: 10px;
      color: #4a4a5c;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .xipe-swatch-dot {
      width: 18px;
      height: 18px;
      border-radius: 50%;
      border: 2px solid rgba(0,0,0,0.08);
      display: inline-block;
    }
    @keyframes xipeSpin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    .xipe-spin { animation: xipeSpin 1s linear infinite; }
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
      <div class="xipe-phase-sep">Phase 1 \u2014 Core</div>
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
      <div class="xipe-phase-sep">Phase 2 \u2014 Advanced</div>
      <div class="xipe-tools">
        <button class="xipe-tool-btn xipe-disabled" data-tool="comment" disabled>
          <span class="xipe-tool-icon commenter"><i class="bi bi-chat-left-text"></i></span>
          <span class="xipe-tool-info">
            <span class="xipe-tool-name">Element Commenter</span>
            <span class="xipe-tool-desc">Attach notes to elements</span>
          </span>
          <span class="xipe-tool-badge">\u2014</span>
        </button>
        <button class="xipe-tool-btn xipe-disabled" data-tool="extract" disabled>
          <span class="xipe-tool-icon extractor"><i class="bi bi-box-arrow-down"></i></span>
          <span class="xipe-tool-info">
            <span class="xipe-tool-name">Asset Extractor</span>
            <span class="xipe-tool-desc">CSS, fonts, images</span>
          </span>
          <span class="xipe-tool-badge">\u2014</span>
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
      const classes = Array.from(current.classList)
        .filter(c => !c.match(/^(js-|_|ng-|css-|sc-|chakra-|xipe-)/))
        .slice(0, 2);
      if (classes.length) selector += '.' + classes.join('.');
      const parent = current.parentElement;
      if (parent) {
        const siblings = Array.from(parent.children).filter(
          s => s.tagName === current.tagName
        );
        if (siblings.length > 1) {
          const idx = siblings.indexOf(current) + 1;
          selector += ':nth-child(' + idx + ')';
        }
      }
      parts.unshift(selector);
      current = current.parentElement;
    }
    parts.unshift('body');
    return parts.join(' > ');
  }

  // ===== State =====
  let colorPickerActive = true;
  let highlighterActive = false;
  let overlayEl = null;
  let labelEl = null;

  // ===== Color Picker =====
  function handleColorClick(e) {
    if (!colorPickerActive) return;
    if (e.target.closest('.xipe-toolbar')) return;
    e.preventDefault();
    e.stopPropagation();

    const el = e.target;
    const computed = window.getComputedStyle(el);
    const bgColor = computed.backgroundColor;
    const textColor = computed.color;
    const colorStr = (bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent')
      ? bgColor : textColor;

    const match = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
    if (!match) return;
    const r = Number(match[1]), g = Number(match[2]), b = Number(match[3]);
    const hex = '#' + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('');

    const rN = r / 255, gN = g / 255, bN = b / 255;
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
    const hsl = Math.round(h * 360) + ', ' + Math.round(s * 100) + '%, ' + Math.round(l * 100) + '%';

    const colorId = 'color-' + String(window.__xipeRefData.colors.length + 1).padStart(3, '0');
    window.__xipeRefData.colors.push({
      id: colorId,
      hex: hex,
      rgb: r + ', ' + g + ', ' + b,
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
    swatch.innerHTML = '<span class="xipe-swatch-dot" style="background:' + hex + ';"></span>' + hex;
    swatch.style.cssText = 'position:absolute;z-index:2147483646;';
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
    const elemId = 'elem-' + String(window.__xipeRefData.elements.length + 1).padStart(3, '0');
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
    overlayEl.style.cssText =
      'position:fixed;top:' + rect.top + 'px;left:' + rect.left + 'px;' +
      'width:' + rect.width + 'px;height:' + rect.height + 'px;' +
      'pointer-events:none;z-index:2147483646;';
    labelEl = document.createElement('div');
    labelEl.className = 'xipe-selector-label';
    labelEl.textContent = generateSelector(el);
    labelEl.style.cssText =
      'position:fixed;top:' + (rect.top - 24) + 'px;left:' + rect.left + 'px;' +
      'z-index:2147483646;pointer-events:none;';
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
    if (e.detail === 0) return;
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
    dragStartX = e.clientX;
    dragStartY = e.clientY;
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

  // ===== Page Event Listeners (capture phase) =====
  document.addEventListener('click', handleColorClick, true);
  document.addEventListener('mousemove', handleHighlightMove, true);
  document.addEventListener('click', handleHighlightClick, true);
})();
```
