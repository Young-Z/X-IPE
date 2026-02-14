(() => {
  // Wait for core
  if (!window.__xipeRegisterMode) {
    console.warn('[X-IPE Mockup] Core not loaded');
    return;
  }

  window.__xipeRegisterMode('mockup', function MockupModeInit(container) {
    let compCounter = 0;
    let snapActive = false;
    let currentStep = 1;
    const MAX_COMPONENTS = 20;

    const SEMANTIC_TAGS = new Set(['SECTION', 'NAV', 'ARTICLE', 'ASIDE', 'HEADER', 'FOOTER', 'MAIN', 'FIGURE']);

    const CAPTURE_PROPS = [
      'display', 'position', 'flex-direction', 'justify-content', 'align-items',
      'grid-template-columns', 'grid-template-rows',
      'width', 'height', 'min-width', 'max-width', 'min-height', 'max-height',
      'margin', 'padding', 'border', 'border-radius',
      'background', 'background-color', 'background-image',
      'color', 'font-family', 'font-size', 'font-weight', 'line-height',
      'box-shadow', 'opacity', 'overflow', 'z-index'
    ];

    // ===== Mockup Styles =====
    const mockupStyle = document.createElement('style');
    mockupStyle.textContent = `
      .xipe-snap-overlay { position: fixed; border: 2px dashed #10b981; pointer-events: none; z-index: 2147483646; }
      .xipe-tag-badge { position: absolute; top: -22px; left: 0; background: #10b981; color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-family: 'Space Mono', monospace; pointer-events: none; }
      .xipe-drag-handle { position: absolute; width: 8px; height: 8px; background: #10b981; pointer-events: auto; border-radius: 1px; }
      .xipe-comp-row { display: flex; align-items: center; gap: 6px; padding: 6px 0; font-size: 11px; color: #e2e8f0; border-bottom: 1px solid rgba(255,255,255,0.06); }
      .xipe-comp-tag { background: rgba(16,185,129,0.15); color: #10b981; padding: 1px 5px; border-radius: 4px; font-size: 9px; font-family: 'Space Mono', monospace; }
      .xipe-comp-selector { color: #64748b; font-size: 9px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 120px; }
      .xipe-comp-dims { color: #94a3b8; font-size: 9px; }
      .xipe-comp-remove { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 12px; margin-left: auto; opacity: 0; transition: opacity 0.2s; font-family: inherit; }
      .xipe-comp-row:hover .xipe-comp-remove { opacity: 1; }
      .xipe-instruction-input { width: 100%; padding: 4px 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15); background: rgba(255,255,255,0.05); color: #e2e8f0; font-size: 10px; margin-top: 4px; font-family: inherit; }
      .xipe-step-indicator { display: flex; gap: 4px; padding: 8px 0; margin-bottom: 8px; }
      .xipe-step-dot { flex: 1; height: 3px; border-radius: 2px; background: rgba(255,255,255,0.1); }
      .xipe-step-dot.xipe-active { background: #10b981; }
      .xipe-step-label { font-size: 11px; color: #94a3b8; margin-bottom: 8px; }
      .xipe-btn { display: block; width: 100%; padding: 8px; border: none; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; text-align: center; transition: all 0.2s; margin-top: 8px; font-family: inherit; }
      .xipe-btn-primary { background: #10b981; color: white; }
      .xipe-btn-primary:hover { background: #059669; }
      .xipe-btn-primary:disabled { background: #374151; color: #6b7280; cursor: not-allowed; }
      .xipe-btn-secondary { background: rgba(255,255,255,0.08); color: #e2e8f0; }
      .xipe-nav-buttons { display: flex; gap: 6px; margin-top: 10px; }
      .xipe-nav-buttons .xipe-btn { flex: 1; }
    `;
    document.head.appendChild(mockupStyle);

    const overlays = [];

    // ===== Smart-Snap =====
    function findSemanticContainer(el) {
      let current = el;
      let depth = 0;
      while (current && current !== document.body && depth < 5) {
        if (SEMANTIC_TAGS.has(current.tagName) || current.getAttribute('role')) return current;
        current = current.parentElement;
        depth++;
      }
      // Fallback: div with dimensions > 50x50
      current = el;
      depth = 0;
      while (current && current !== document.body && depth < 5) {
        if (current.tagName === 'DIV' && current.offsetWidth > 50 && current.offsetHeight > 50) return current;
        current = current.parentElement;
        depth++;
      }
      return null;
    }

    function handleSnapClick(e) {
      if (!snapActive) return;
      if (e.target.closest('.xipe-toolbar') || e.target.closest('.xipe-snap-overlay')) return;
      e.preventDefault();
      e.stopPropagation();

      const target = findSemanticContainer(e.target);
      if (!target || target === document.body || target === document.documentElement) {
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

    // ===== Component Capture =====
    function captureComponent(el) {
      compCounter++;
      const id = `comp-${String(compCounter).padStart(3, '0')}`;
      const rect = el.getBoundingClientRect();
      const selector = window.__xipeGenerateSelector(el);
      const tag = el.tagName.toLowerCase();

      const styles = window.getComputedStyle(el);
      const computedStyles = {};
      CAPTURE_PROPS.forEach(p => { computedStyles[p] = styles.getPropertyValue(p); });

      // Screenshot crop from viewport canvas
      let screenshotDataurl = null;
      if (window.__xipeViewportScreenshot) {
        try {
          const crop = document.createElement('canvas');
          crop.width = Math.max(1, rect.width);
          crop.height = Math.max(1, rect.height);
          const ctx = crop.getContext('2d');
          const img = new Image();
          img.src = window.__xipeViewportScreenshot;
          ctx.drawImage(img, rect.x, rect.y, rect.width, rect.height, 0, 0, rect.width, rect.height);
          screenshotDataurl = crop.toDataURL('image/png');
        } catch (err) { /* ignore crop errors */ }
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
      showSnapOverlay(rect, tag, selector);
      renderComponentList();
      window.__xipeToast(`Selected: <${tag}>`, 'info', 2000);
    }

    // ===== Snap Overlay with Drag Handles =====
    function showSnapOverlay(rect, tag, selector) {
      const overlay = document.createElement('div');
      overlay.className = 'xipe-snap-overlay';
      overlay.style.cssText = `left:${rect.x}px;top:${rect.y}px;width:${rect.width}px;height:${rect.height}px;`;

      const badge = document.createElement('span');
      badge.className = 'xipe-tag-badge';
      badge.textContent = tag;
      overlay.appendChild(badge);

      const positions = [
        { x: 0, y: 0, cursor: 'nw-resize' },
        { x: 0.5, y: 0, cursor: 'n-resize' },
        { x: 1, y: 0, cursor: 'ne-resize' },
        { x: 1, y: 0.5, cursor: 'e-resize' },
        { x: 1, y: 1, cursor: 'se-resize' },
        { x: 0.5, y: 1, cursor: 's-resize' },
        { x: 0, y: 1, cursor: 'sw-resize' },
        { x: 0, y: 0.5, cursor: 'w-resize' }
      ];
      positions.forEach(pos => {
        const handle = document.createElement('div');
        handle.className = 'xipe-drag-handle';
        handle.style.cssText = `left:${pos.x * 100}%;top:${pos.y * 100}%;margin:-4px;cursor:${pos.cursor};`;
        overlay.appendChild(handle);
      });

      document.body.appendChild(overlay);
      overlays.push(overlay);
    }

    // ===== Step UI =====
    const steps = ['Select Components', 'Add Instructions', 'Analyze', 'Generate'];
    const stepContainers = [];

    function buildStepUI() {
      container.innerHTML = '';
      const indicator = document.createElement('div');
      indicator.className = 'xipe-step-indicator';
      steps.forEach((_, i) => {
        const dot = document.createElement('div');
        dot.className = `xipe-step-dot${i < currentStep ? ' xipe-active' : ''}`;
        indicator.appendChild(dot);
      });
      container.appendChild(indicator);

      const label = document.createElement('div');
      label.className = 'xipe-step-label';
      label.textContent = `Step ${currentStep}/4: ${steps[currentStep - 1]}`;
      container.appendChild(label);

      steps.forEach((_, i) => {
        const sc = document.createElement('div');
        sc.className = `xipe-step-${i + 1}`;
        sc.style.display = (i + 1) === currentStep ? 'block' : 'none';
        stepContainers[i] = sc;
        container.appendChild(sc);
      });

      // Nav buttons
      const nav = document.createElement('div');
      nav.className = 'xipe-nav-buttons';
      if (currentStep > 1) {
        const back = document.createElement('button');
        back.className = 'xipe-btn xipe-btn-secondary';
        back.textContent = 'Back';
        back.onclick = () => { currentStep--; buildStepUI(); renderStep(); };
        nav.appendChild(back);
      }
      if (currentStep < 4) {
        const next = document.createElement('button');
        next.className = 'xipe-btn xipe-btn-primary';
        next.textContent = 'Next';
        next.onclick = () => { currentStep++; snapActive = (currentStep === 1); buildStepUI(); renderStep(); };
        nav.appendChild(next);
      }
      container.appendChild(nav);
      renderStep();
    }

    function renderStep() {
      if (currentStep === 1) {
        snapActive = true;
        renderComponentList();
      } else if (currentStep === 2) {
        snapActive = false;
        renderInstructions();
      } else if (currentStep === 3) {
        snapActive = false;
        renderAnalyze();
      } else if (currentStep === 4) {
        snapActive = false;
        renderGenerate();
      }
    }

    // ===== Component List (Step 1) =====
    function renderComponentList() {
      const sc = stepContainers[0];
      if (!sc) return;
      sc.innerHTML = '';
      window.__xipeRefData.components.forEach((comp, i) => {
        const row = document.createElement('div');
        row.className = 'xipe-comp-row';
        row.innerHTML = `<span class="xipe-comp-tag">${comp.tag}</span><span class="xipe-comp-selector">${comp.selector}</span><span class="xipe-comp-dims">${Math.round(comp.bounding_box.width)}×${Math.round(comp.bounding_box.height)}</span>`;
        const rmBtn = document.createElement('button');
        rmBtn.className = 'xipe-comp-remove';
        rmBtn.textContent = '×';
        rmBtn.onclick = () => {
          window.__xipeRefData.components.splice(i, 1);
          if (overlays[i]) { overlays[i].remove(); overlays.splice(i, 1); }
          renderComponentList();
        };
        row.appendChild(rmBtn);
        // Hover highlight
        row.addEventListener('mouseenter', () => {
          if (overlays[i]) overlays[i].style.borderColor = '#f59e0b';
        });
        row.addEventListener('mouseleave', () => {
          if (overlays[i]) overlays[i].style.borderColor = '#10b981';
        });
        sc.appendChild(row);
      });
      if (window.__xipeRefData.components.length === 0) {
        sc.innerHTML = '<div style="color:#64748b;font-size:11px;text-align:center;padding:20px">Click elements on the page to select components</div>';
      }
    }

    // ===== Instructions (Step 2) =====
    function renderInstructions() {
      const sc = stepContainers[1];
      if (!sc) return;
      sc.innerHTML = '';
      window.__xipeRefData.components.forEach((comp) => {
        const wrapper = document.createElement('div');
        wrapper.style.marginBottom = '8px';
        wrapper.innerHTML = `<div class="xipe-comp-row"><span class="xipe-comp-tag">${comp.tag}</span><span class="xipe-comp-selector">${comp.selector}</span></div>`;
        const input = document.createElement('input');
        input.className = 'xipe-instruction-input';
        input.placeholder = 'Add notes (e.g., sticky header, animated)';
        input.value = comp.instruction;
        input.addEventListener('input', (e) => { comp.instruction = e.target.value; });
        wrapper.appendChild(input);
        sc.appendChild(wrapper);
      });
      if (window.__xipeRefData.components.length === 0) {
        sc.innerHTML = '<div style="color:#64748b;font-size:11px;text-align:center;padding:20px">No components selected. Go back to Step 1.</div>';
      }
    }

    // ===== Analyze (Step 3) =====
    function renderAnalyze() {
      const sc = stepContainers[2];
      if (!sc) return;
      sc.innerHTML = '';
      const summary = document.createElement('div');
      summary.style.cssText = 'color:#e2e8f0;font-size:11px;margin-bottom:12px';
      summary.textContent = `${window.__xipeRefData.components.length} components ready for analysis`;
      sc.appendChild(summary);

      const btn = document.createElement('button');
      btn.className = 'xipe-btn xipe-btn-primary';
      btn.textContent = 'Analyze';
      btn.disabled = window.__xipeRefData.components.length === 0;
      btn.onclick = () => {
        window.__xipeRefData.mode = 'mockup';
        window.__xipeRefReady = true;
        window.__xipeToast('Analyzing components...', 'progress');
      };
      sc.appendChild(btn);
    }

    // ===== Generate (Step 4) =====
    function renderGenerate() {
      const sc = stepContainers[3];
      if (!sc) return;
      sc.innerHTML = '';
      const summary = document.createElement('div');
      summary.style.cssText = 'color:#e2e8f0;font-size:11px;margin-bottom:12px';
      summary.textContent = `Ready to generate mockup from ${window.__xipeRefData.components.length} components`;
      sc.appendChild(summary);

      const btn = document.createElement('button');
      btn.className = 'xipe-btn xipe-btn-primary';
      btn.textContent = 'Generate Mockup';
      btn.disabled = window.__xipeRefData.components.length === 0;
      if (btn.disabled) btn.title = 'Select at least one component first.';
      btn.onclick = () => {
        window.__xipeRefData.mode = 'mockup';
        window.__xipeRefReady = true;
        window.__xipeToast('Saving reference data...', 'progress');
      };
      sc.appendChild(btn);
    }

    buildStepUI();
  });
})();
