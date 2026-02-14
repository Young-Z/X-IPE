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
      width: 288px;
      max-height: calc(100vh - 120px);
      background: rgba(255, 255, 255, 0.94);
      backdrop-filter: blur(24px);
      border: 1px solid rgba(55, 48, 163, 0.15);
      border-radius: 14px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.1), 0 0 0 1px rgba(55, 48, 163, 0.04);
      overflow-y: auto;
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
      position: sticky;
      top: 0;
      z-index: 1;
      background: rgba(255, 255, 255, 0.97);
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
    .xipe-cursor-eyedropper, .xipe-cursor-eyedropper * { cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><path d="M27.3 4.7a3.8 3.8 0 00-5.4 0l-3.2 3.2-1.4-1.4a1 1 0 00-1.4 0l-1.4 1.4a1 1 0 000 1.4l.7.7L5.7 19.5a2 2 0 00-.5.9l-1.1 4.4a1 1 0 001.2 1.2l4.4-1.1a2 2 0 00.9-.5L20 14.9l.7.7a1 1 0 001.4 0l1.4-1.4a1 1 0 000-1.4l-1.4-1.4 3.2-3.2a3.8 3.8 0 000-5.4z" fill="%233730a3"/></svg>') 2 30, crosshair !important; }
    .xipe-cursor-crosshair, .xipe-cursor-crosshair * { cursor: crosshair !important; }
    .xipe-color-list, .xipe-elem-list { padding: 0 4px; }
    .xipe-color-entry, .xipe-elem-entry {
      display: flex; align-items: center; gap: 6px;
      padding: 4px 6px; border-radius: 6px;
      font-family: 'Outfit', sans-serif; font-size: 10px;
      transition: background 0.15s;
    }
    .xipe-color-entry:hover { background: rgba(190, 18, 60, 0.04); }
    .xipe-elem-entry:hover { background: rgba(55, 48, 163, 0.04); }
    .xipe-color-hex { font-family: 'Space Mono', monospace; font-size: 10px; color: #4a4a5c; }
    .xipe-color-selector, .xipe-elem-selector {
      font-size: 9px; color: #8e8e9f; overflow: hidden;
      text-overflow: ellipsis; white-space: nowrap; max-width: 120px;
    }
    .xipe-tag-pill {
      font-family: 'Space Mono', monospace; font-size: 9px;
      background: rgba(55, 48, 163, 0.08); color: #3730a3;
      padding: 2px 6px; border-radius: 3px; flex-shrink: 0;
    }
    .xipe-elem-dims { font-size: 9px; color: #8e8e9f; white-space: nowrap; }
    .xipe-remove-btn {
      margin-left: auto; width: 16px; height: 16px;
      display: flex; align-items: center; justify-content: center;
      background: none; border: none; cursor: pointer;
      font-size: 12px; color: #8e8e9f; opacity: 0;
      border-radius: 50%; transition: all 0.15s; flex-shrink: 0;
    }
    .xipe-color-entry:hover .xipe-remove-btn { opacity: 1; color: #be123c; }
    .xipe-elem-entry:hover .xipe-remove-btn { opacity: 1; color: #3730a3; }
    .xipe-remove-btn:hover { background: rgba(0,0,0,0.06); }
    .xipe-hover-highlight-rose { box-shadow: 0 0 0 2px #be123c !important; transition: box-shadow 0.15s; }
    .xipe-hover-highlight-accent { box-shadow: 0 0 0 2px #3730a3 !important; transition: box-shadow 0.15s; }
    .xipe-collected-header {
      display: flex; align-items: center; justify-content: space-between;
      cursor: pointer; margin-bottom: 8px;
    }
    .xipe-collected-chevron {
      font-size: 10px; color: #8e8e9f;
      transition: transform 0.2s ease;
    }
    .xipe-collected-chevron.collapsed { transform: rotate(180deg); }
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
        <div class="xipe-collected-header" id="xipe-collected-toggle">
          <div class="xipe-collected-title" style="margin-bottom:0;">Collected References</div>
          <i class="bi bi-chevron-up xipe-collected-chevron" id="xipe-chevron"></i>
        </div>
        <div class="xipe-collected-items" id="xipe-collected" style="margin-top:8px;">
          <span class="xipe-collected-tag colors"><i class="bi bi-circle-fill"></i> <span id="xipe-color-count">0</span> colors</span>
          <span class="xipe-collected-tag elements"><i class="bi bi-circle-fill"></i> <span id="xipe-elem-count">0</span> elements</span>
        </div>
        <div class="xipe-color-list" id="xipe-color-list"></div>
        <div class="xipe-elem-list" id="xipe-elem-list"></div>
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
    const sourceSelector = generateSelector(el);
    window.__xipeRefData.colors.push({
      id: colorId,
      hex: hex,
      rgb: r + ', ' + g + ', ' + b,
      hsl: hsl,
      source_selector: sourceSelector,
      context: ''
    });
    updateBadges();
    addColorEntry(colorId, hex, sourceSelector);
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

  // ===== Color List Management (CR-001) =====
  function addColorEntry(id, hex, selector) {
    const list = document.getElementById('xipe-color-list');
    const entry = document.createElement('div');
    entry.className = 'xipe-color-entry';
    entry.dataset.colorId = id;
    entry.dataset.selector = selector;
    entry.innerHTML =
      '<span class="xipe-swatch-dot" style="background:' + hex + ';width:16px;height:16px;border-radius:50%;flex-shrink:0;"></span>' +
      '<span class="xipe-color-hex">' + hex + '</span>' +
      '<span class="xipe-color-selector">' + selector + '</span>' +
      '<button class="xipe-remove-btn" title="Remove">\u00d7</button>';
    entry.addEventListener('mouseenter', function() { highlightPageElement(selector, 'rose'); });
    entry.addEventListener('mouseleave', function() { removePageHighlight(); });
    entry.querySelector('.xipe-remove-btn').addEventListener('click', function(e) {
      e.stopPropagation();
      window.__xipeRefData.colors = window.__xipeRefData.colors.filter(function(c) { return c.id !== id; });
      entry.remove();
      updateBadges();
    });
    list.appendChild(entry);
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
    const elemSelector = generateSelector(el);
    window.__xipeRefData.elements.push({
      id: elemId,
      selector: elemSelector,
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
    addElementEntry(elemId, el.tagName.toLowerCase(), elemSelector, rect);
  }

  // ===== Element List Management (CR-001) =====
  function addElementEntry(id, tag, selector, rect) {
    const list = document.getElementById('xipe-elem-list');
    const entry = document.createElement('div');
    entry.className = 'xipe-elem-entry';
    entry.dataset.elemId = id;
    entry.dataset.selector = selector;
    entry.innerHTML =
      '<span class="xipe-tag-pill">' + tag + '</span>' +
      '<span class="xipe-elem-selector">' + selector + '</span>' +
      '<span class="xipe-elem-dims">' + Math.round(rect.width) + '\u00d7' + Math.round(rect.height) + '</span>' +
      '<button class="xipe-remove-btn" title="Remove">\u00d7</button>';
    entry.addEventListener('mouseenter', function() { highlightPageElement(selector, 'accent'); });
    entry.addEventListener('mouseleave', function() { removePageHighlight(); });
    entry.querySelector('.xipe-remove-btn').addEventListener('click', function(e) {
      e.stopPropagation();
      window.__xipeRefData.elements = window.__xipeRefData.elements.filter(function(el) { return el.id !== id; });
      entry.remove();
      updateBadges();
    });
    list.appendChild(entry);
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

  // ===== Hover Highlight for List Entries (CR-001) =====
  let hoverHighlightEl = null;
  let hoverLabelEl = null;

  function highlightPageElement(selector, colorType) {
    removePageHighlight();
    try {
      const el = document.querySelector(selector);
      if (!el) return;
      const className = colorType === 'rose' ? 'xipe-hover-highlight-rose' : 'xipe-hover-highlight-accent';
      el.classList.add(className);
      hoverHighlightEl = { element: el, className: className };
      if (colorType === 'accent') {
        const rect = el.getBoundingClientRect();
        hoverLabelEl = document.createElement('div');
        hoverLabelEl.className = 'xipe-selector-label';
        hoverLabelEl.textContent = selector;
        hoverLabelEl.style.cssText = 'position:fixed;top:' + (rect.top - 24) + 'px;left:' + rect.left + 'px;z-index:2147483646;pointer-events:none;';
        document.body.appendChild(hoverLabelEl);
      }
    } catch (e) { /* invalid selector */ }
  }

  function removePageHighlight() {
    if (hoverHighlightEl) {
      hoverHighlightEl.element.classList.remove(hoverHighlightEl.className);
      hoverHighlightEl = null;
    }
    if (hoverLabelEl) { hoverLabelEl.remove(); hoverLabelEl = null; }
  }

  // ===== Cursor Management (CR-001) =====
  function updateCursor() {
    document.body.classList.remove('xipe-cursor-eyedropper', 'xipe-cursor-crosshair');
    if (panel.classList.contains('visible')) {
      if (colorPickerActive) document.body.classList.add('xipe-cursor-eyedropper');
      else if (highlighterActive) document.body.classList.add('xipe-cursor-crosshair');
    }
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
      updateCursor();
    });
  });

  // ===== Panel Toggle =====
  const hamburger = document.getElementById('xipe-hamburger');
  const panel = document.getElementById('xipe-panel');
  hamburger.addEventListener('click', (e) => {
    if (e.detail === 0) return;
    hamburger.style.display = 'none';
    panel.classList.add('visible');
    updateCursor();
  });
  document.getElementById('xipe-close').addEventListener('click', () => {
    panel.classList.remove('visible');
    hamburger.style.display = 'flex';
    updateCursor();
  });
  // Start expanded
  hamburger.style.display = 'none';
  panel.classList.add('visible');
  updateCursor();

  // ===== Collected References Toggle (CR-001) =====
  let listsExpanded = true;
  document.getElementById('xipe-collected-toggle').addEventListener('click', () => {
    listsExpanded = !listsExpanded;
    const chevron = document.getElementById('xipe-chevron');
    const colorList = document.getElementById('xipe-color-list');
    const elemList = document.getElementById('xipe-elem-list');
    chevron.classList.toggle('collapsed', !listsExpanded);
    colorList.style.display = listsExpanded ? '' : 'none';
    elemList.style.display = listsExpanded ? '' : 'none';
  });

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
    }, 1200);
  });

  // ===== Page Event Listeners (capture phase) =====
  document.addEventListener('click', handleColorClick, true);
  document.addEventListener('mousemove', handleHighlightMove, true);
  document.addEventListener('click', handleHighlightClick, true);
})();
