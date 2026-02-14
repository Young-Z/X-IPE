(() => {
  // Guard: prevent double injection
  if (window.__xipeToolbarInjected) return;
  window.__xipeToolbarInjected = true;

  // ===== Data Store (FR-12) =====
  window.__xipeRefData = { mode: 'theme', colors: [], components: [], design_tokens: null };
  window.__xipeRefReady = false;
  window.__xipeRefCommand = null;

  // ===== Mode Registry (FR-16) =====
  const modeRegistry = {};
  const modeContainers = {};
  let activeMode = 'theme';

  window.__xipeRegisterMode = (name, initFn) => {
    modeRegistry[name] = initFn;
    const container = modeContainers[name];
    if (container && name === activeMode) {
      initFn(container);
    }
  };

  // ===== Toast API (FR-11) =====
  let toastContainer;
  window.__xipeToast = (msg, type = 'info', dur = 4000) => {
    if (!toastContainer) return;
    const toast = document.createElement('div');
    toast.className = `xipe-toast xipe-toast-${type}`;
    const icons = { info: 'ℹ', progress: '⏳', success: '✓', error: '✗' };
    toast.innerHTML = `<span class="xipe-toast-icon">${icons[type] || 'ℹ'}</span><span class="xipe-toast-msg">${msg}</span>`;
    toastContainer.appendChild(toast);
    // Max 3 visible
    while (toastContainer.children.length > 3) {
      toastContainer.removeChild(toastContainer.firstChild);
    }
    if (type !== 'error') {
      setTimeout(() => { if (toast.parentNode) toast.remove(); }, dur);
    } else {
      const dismiss = document.createElement('button');
      dismiss.className = 'xipe-toast-dismiss';
      dismiss.textContent = '×';
      dismiss.onclick = () => toast.remove();
      toast.appendChild(dismiss);
    }
  };

  // ===== CSS Injection (FR-15, FR-4) =====
  const style = document.createElement('style');
  style.textContent = `
    .xipe-toolbar { position: fixed; top: 50%; right: 20px; z-index: 2147483647; font-family: 'Outfit', system-ui, sans-serif; user-select: none; transform: translateY(-50%); }
    .xipe-hamburger { width: 52px; height: 52px; background: linear-gradient(135deg, #3730a3, #4f46e5); border: 2px solid rgba(255,255,255,0.25); border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: grab; color: white; font-size: 9px; font-weight: 700; letter-spacing: 0.08em; box-shadow: 0 4px 16px rgba(55,48,163,0.35); transition: all 0.4s cubic-bezier(0.22,1,0.36,1); }
    .xipe-hamburger:hover { background: linear-gradient(135deg, #4f46e5, #7c3aed, #a855f7); transform: scale(1.1); }
    .xipe-panel { position: absolute; right: 62px; top: 50%; transform: translateY(-50%); width: 280px; max-height: 80vh; background: #0f172a; border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; overflow: hidden; transition: width 350ms cubic-bezier(0.22,1,0.36,1), opacity 350ms; box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
    .xipe-panel.xipe-collapsed { width: 0; opacity: 0; pointer-events: none; overflow: hidden; border: none; }
    .xipe-panel-header { padding: 14px 16px 10px; border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; align-items: center; gap: 8px; }
    .xipe-panel-title { color: #e2e8f0; font-size: 13px; font-weight: 600; }
    .xipe-status-dot { width: 6px; height: 6px; border-radius: 50%; background: #10b981; }
    .xipe-mode-tabs { display: flex; gap: 4px; padding: 8px 12px; }
    .xipe-mode-tab { flex: 1; padding: 6px 8px; background: transparent; border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; color: #94a3b8; font-size: 11px; font-weight: 500; cursor: pointer; text-align: center; transition: all 0.2s; font-family: inherit; }
    .xipe-mode-tab.xipe-active { background: #10b981; color: white; border-color: #10b981; }
    .xipe-mode-content { padding: 12px; overflow-y: auto; max-height: calc(80vh - 120px); min-height: 100px; }
    .xipe-toast-area { padding: 8px 12px; }
    .xipe-toast { display: flex; align-items: center; gap: 6px; padding: 8px 12px; border-radius: 8px; font-size: 11px; color: #e2e8f0; margin-bottom: 4px; animation: xipe-slide-in 0.3s ease; }
    .xipe-toast-info { background: rgba(59,130,246,0.15); border: 1px solid rgba(59,130,246,0.3); }
    .xipe-toast-progress { background: rgba(168,85,247,0.15); border: 1px solid rgba(168,85,247,0.3); }
    .xipe-toast-success { background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.3); }
    .xipe-toast-error { background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3); }
    .xipe-toast-icon { font-size: 14px; }
    .xipe-toast-msg { flex: 1; }
    .xipe-toast-dismiss { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 14px; padding: 0 4px; font-family: inherit; }
    @keyframes xipe-slide-in { from { transform: translateX(20px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
  `;
  document.head.appendChild(style);

  // ===== DOM Construction =====
  const toolbar = document.createElement('div');
  toolbar.className = 'xipe-toolbar';

  const hamburger = document.createElement('div');
  hamburger.className = 'xipe-hamburger';
  hamburger.textContent = 'X-IPE';
  toolbar.appendChild(hamburger);

  const panel = document.createElement('div');
  panel.className = 'xipe-panel xipe-collapsed';

  // Header
  const header = document.createElement('div');
  header.className = 'xipe-panel-header';
  header.innerHTML = '<span class="xipe-status-dot"></span><span class="xipe-panel-title">X-IPE Reference</span>';
  panel.appendChild(header);

  // Mode tabs (FR-9)
  const tabsDiv = document.createElement('div');
  tabsDiv.className = 'xipe-mode-tabs';
  const modes = [
    { id: 'theme', label: '🎨 Catch Theme' },
    { id: 'mockup', label: '📐 Copy Mockup' }
  ];
  const tabEls = modes.map(m => {
    const btn = document.createElement('button');
    btn.className = `xipe-mode-tab${m.id === activeMode ? ' xipe-active' : ''}`;
    btn.dataset.mode = m.id;
    btn.textContent = m.label;
    btn.onclick = () => switchMode(m.id);
    tabsDiv.appendChild(btn);
    return btn;
  });
  panel.appendChild(tabsDiv);

  // Mode content containers (FR-16)
  const contentArea = document.createElement('div');
  contentArea.className = 'xipe-mode-content';
  modes.forEach(m => {
    const container = document.createElement('div');
    container.className = `xipe-mode-${m.id}`;
    container.style.display = m.id === activeMode ? 'block' : 'none';
    modeContainers[m.id] = container;
    contentArea.appendChild(container);
  });
  panel.appendChild(contentArea);

  // Toast area
  toastContainer = document.createElement('div');
  toastContainer.className = 'xipe-toast-area';
  panel.appendChild(toastContainer);

  toolbar.appendChild(panel);
  document.body.appendChild(toolbar);

  // ===== Mode Switching (FR-9, FR-10) =====
  function switchMode(mode) {
    activeMode = mode;
    window.__xipeRefData.mode = mode;
    tabEls.forEach(t => t.classList.toggle('xipe-active', t.dataset.mode === mode));
    Object.entries(modeContainers).forEach(([name, el]) => {
      el.style.display = name === mode ? 'block' : 'none';
    });
    if (modeRegistry[mode] && !modeContainers[mode].dataset.initialized) {
      modeRegistry[mode](modeContainers[mode]);
      modeContainers[mode].dataset.initialized = 'true';
    }
  }

  // ===== Auto-Collapse (FR-7) =====
  let collapseTimer = null;
  function expandPanel() { panel.classList.remove('xipe-collapsed'); }
  function collapsePanel() { panel.classList.add('xipe-collapsed'); }

  hamburger.addEventListener('mouseenter', () => {
    clearTimeout(collapseTimer);
    expandPanel();
  });
  panel.addEventListener('mouseenter', () => {
    clearTimeout(collapseTimer);
  });
  panel.addEventListener('mouseleave', () => {
    collapseTimer = setTimeout(collapsePanel, 2000);
  });
  hamburger.addEventListener('mouseleave', () => {
    collapseTimer = setTimeout(collapsePanel, 2000);
  });

  // ===== Drag (FR-8) =====
  let isDragging = false;
  let dragOffsetX = 0, dragOffsetY = 0;
  hamburger.addEventListener('mousedown', (e) => {
    isDragging = true;
    dragOffsetX = e.clientX - toolbar.getBoundingClientRect().left;
    dragOffsetY = e.clientY - toolbar.getBoundingClientRect().top;
    hamburger.style.cursor = 'grabbing';
    e.preventDefault();
  });
  document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    let x = e.clientX - dragOffsetX;
    let y = e.clientY - dragOffsetY;
    x = Math.max(10, Math.min(window.innerWidth - 62, x));
    y = Math.max(10, Math.min(window.innerHeight - 62, y));
    toolbar.style.left = x + 'px';
    toolbar.style.top = y + 'px';
    toolbar.style.right = 'auto';
    toolbar.style.transform = 'none';
  });
  document.addEventListener('mouseup', () => {
    if (isDragging) {
      isDragging = false;
      hamburger.style.cursor = 'grab';
    }
  });

  // ===== CSS Selector Generator =====
  window.__xipeGenerateSelector = function(el) {
    if (!el || el === document.body || el === document.documentElement) return 'body';
    if (el.id) return '#' + CSS.escape(el.id);
    const parts = [];
    let current = el;
    while (current && current !== document.body && current !== document.documentElement) {
      let part = current.tagName.toLowerCase();
      const stableClasses = [...current.classList]
        .filter(c => !/[0-9a-f]{6,}|__|--[a-z0-9]{4,}/i.test(c))
        .filter(c => !c.startsWith('xipe-'))
        .slice(0, 2);
      if (stableClasses.length) {
        part += '.' + stableClasses.map(CSS.escape).join('.');
      } else {
        const siblings = [...(current.parentElement?.children || [])].filter(c => c.tagName === current.tagName);
        const idx = siblings.indexOf(current);
        if (siblings.length > 1) part += `:nth-of-type(${idx + 1})`;
      }
      parts.unshift(part);
      current = current.parentElement;
    }
    return 'body > ' + parts.join(' > ');
  };

  // ===== Command Polling (FR-14) =====
  function handleDeepCapture(targetId) {
    const comp = window.__xipeRefData.components.find(c => c.id === targetId);
    if (!comp) { window.__xipeToast(`Component ${targetId} not found`, 'error'); return; }
    const el = document.querySelector(comp.selector);
    if (!el) { window.__xipeToast(`Element not found for ${targetId}`, 'error'); return; }
    const styles = window.getComputedStyle(el);
    const allStyles = {};
    for (let i = 0; i < styles.length; i++) {
      allStyles[styles[i]] = styles.getPropertyValue(styles[i]);
    }
    comp.html_css = { level: 'deep', computed_styles: allStyles, outer_html: el.outerHTML };
    window.__xipeToast(`Deep capture complete: ${targetId}`, 'success');
    window.__xipeRefReady = true;
  }

  function pollCommands() {
    const cmd = window.__xipeRefCommand;
    if (!cmd) return;
    window.__xipeRefCommand = null;
    try {
      switch (cmd.action) {
        case 'deep_capture': handleDeepCapture(cmd.target); break;
        case 'reset':
          window.__xipeRefData = { mode: activeMode, colors: [], components: [], design_tokens: null };
          window.__xipeToast('Data reset', 'info');
          break;
        default: window.__xipeToast(`Unknown command: ${cmd.action}`, 'error');
      }
    } catch (e) {
      window.__xipeToast(`Command error: ${e.message}`, 'error');
    }
  }
  setInterval(pollCommands, 1000);

  // ===== Font Loading (NFR-5) =====
  (window.requestIdleCallback || setTimeout)(() => {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=Space+Mono&family=DM+Sans:wght@400;500&display=swap';
    document.head.appendChild(link);
  });

  // ===== Signal Ready =====
  window.__xipeToolbarReady = true;
})();
