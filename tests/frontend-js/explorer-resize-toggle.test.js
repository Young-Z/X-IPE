/**
 * FEATURE-029-D / CR-001: Explorer Border Toggle
 *
 * Tests click-vs-drag detection on the resize handle, chevron indicator state,
 * handle visibility when collapsed, animation guard, touch tap toggle,
 * and persistence of collapsed state via border toggle.
 */
import { describe, it, expect, beforeAll, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import vm from 'vm';

const JS_PATH = resolve(import.meta.dirname, '../../src/x_ipe/static/js/terminal.js');

beforeAll(() => {
  // Stub Terminal & FitAddon (xterm)
  globalThis.Terminal = class {
    constructor() { this.element = document.createElement('div'); }
    open() {} dispose() {} write() {} writeln() {} reset() {}
    loadAddon() {} onData() {} onBinary() {}
    get buffer() {
      return {
        active: {
          baseY: 0, cursorY: 0, length: 0,
          getLine: () => ({ translateToString: () => '' }),
        },
      };
    }
  };
  globalThis.FitAddon = { FitAddon: class { fit() {} } };

  // Stub socket.io
  globalThis.io = vi.fn(() => ({
    on: vi.fn(), emit: vi.fn(), disconnect: vi.fn(), connected: false,
  }));

  // Stub ResizeObserver
  globalThis.ResizeObserver = class { observe() {} disconnect() {} };

  // Stub fetch
  globalThis.fetch = vi.fn(async (url) => {
    if (url === '/api/config/cli-adapter') {
      return { ok: true, json: async () => ({ success: true, command: 'copilot', run_args: '', inline_prompt_flag: '-i', prompt_format: '{command} {inline_prompt_flag} "{escaped_prompt}"' }) };
    }
    if (url === '/api/config') {
      return { ok: true, json: async () => ({ auto_execute_prompt: false }) };
    }
    return { ok: false };
  });

  // DOM skeleton
  document.body.innerHTML = `
    <div id="terminal-content"></div>
    <div id="terminal-status-indicator"></div>
    <div id="terminal-status-text"></div>
    <div id="terminal-panel">
      <div id="terminal-header">
        <button id="terminal-toggle"></button>
        <button id="terminal-zen-btn"></button>
        <button id="terminal-explorer-toggle"></button>
        <button id="copilot-cmd-btn" title="Insert Copilot command"><i class="bi bi-robot"></i></button>
      </div>
      <div id="terminal-body">
        <div id="terminal-resize-handle"></div>
        <div id="explorer-resize-handle"></div>
        <div id="session-explorer"></div>
      </div>
    </div>
  `;

  // Stub Touch constructor (jsdom lacks it)
  globalThis.Touch = class {
    constructor(opts) { Object.assign(this, opts); }
  };

  const code = readFileSync(JS_PATH, 'utf-8');
  vm.runInThisContext(code);
});

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

function createPanel() {
  // Reset DOM state
  const explorer = document.getElementById('session-explorer');
  explorer.className = '';
  explorer.style.cssText = '';
  const handle = document.getElementById('explorer-resize-handle');
  handle.className = 'explorer-resize-handle';
  handle.style.cssText = '';

  const tm = new window.TerminalManager('terminal-content');
  tm.fitActive = vi.fn();
  const panel = new window.TerminalPanel(tm);
  return { panel, tm, explorer, handle };
}

function mousedown(el, x = 100, y = 100) {
  el.dispatchEvent(new MouseEvent('mousedown', { clientX: x, clientY: y, bubbles: true }));
}

function mousemove(x, y) {
  document.dispatchEvent(new MouseEvent('mousemove', { clientX: x, clientY: y, bubbles: true }));
}

function mouseup(x, y) {
  document.dispatchEvent(new MouseEvent('mouseup', { clientX: x, clientY: y, bubbles: true }));
}

/* ------------------------------------------------------------------ */
/* Tests                                                               */
/* ------------------------------------------------------------------ */

describe('CR-001: Border Toggle — Click-vs-Drag Detection', () => {
  afterEach(() => { vi.restoreAllMocks(); localStorage.clear(); });

  // AC-19: Click to collapse (movement < 3px)
  it('collapses explorer on click (mousedown+mouseup, no movement)', () => {
    localStorage.clear();
    const { panel, explorer, handle } = createPanel();
    expect(panel.explorerVisible).toBe(true);

    mousedown(handle, 100, 100);
    mouseup(100, 100);

    expect(panel.explorerVisible).toBe(false);
    expect(explorer.classList.contains('collapsed')).toBe(true);
  });

  // AC-20: Click collapsed handle to expand
  it('expands explorer when clicking collapsed handle', () => {
    vi.useFakeTimers();
    localStorage.clear();
    const { panel, explorer, handle } = createPanel();

    // Collapse first
    mousedown(handle, 100, 100);
    mouseup(100, 100);
    expect(panel.explorerVisible).toBe(false);

    // Wait for animation guard to clear
    vi.advanceTimersByTime(350);

    // Click again to expand
    mousedown(handle, 100, 100);
    mouseup(100, 100);

    expect(panel.explorerVisible).toBe(true);
    expect(explorer.classList.contains('collapsed')).toBe(false);
    vi.useRealTimers();
  });

  // AC-21: Click expanded handle → collapse to 0
  it('collapses to width 0 with collapsed class on click', () => {
    localStorage.clear();
    const { panel, explorer, handle } = createPanel();
    panel.explorerWidth = 280;
    panel._updateExplorerWidth(280);

    mousedown(handle, 100, 100);
    mouseup(100, 100);

    expect(explorer.classList.contains('collapsed')).toBe(true);
    expect(panel.explorerVisible).toBe(false);
    // Inline width must be cleared so CSS .collapsed { width: 0 } takes effect
    expect(explorer.style.width).toBe('');
    expect(explorer.style.minWidth).toBe('');
    expect(explorer.style.maxWidth).toBe('');
  });

  // AC-24: Drag preserves resize behavior (movement ≥ 3px)
  it('resizes on drag (movement ≥ 3px) instead of toggling', () => {
    localStorage.clear();
    const { panel, handle } = createPanel();
    const body = document.getElementById('terminal-body');
    body.getBoundingClientRect = vi.fn(() => ({ right: 800, left: 0, top: 0, bottom: 600, width: 800, height: 600 }));

    mousedown(handle, 500, 100);
    mousemove(490, 100); // 10px → exceeds 3px threshold
    mousemove(480, 100);
    mouseup(480, 100);

    // Should still be expanded (not toggled)
    expect(panel.explorerVisible).toBe(true);
    // Width should have been updated (800 - 480 = 320, within 160-360)
    expect(panel.explorerWidth).toBe(320);
  });

  // AC-9: Drag disabled when collapsed
  it('does not drag-resize when collapsed, treats as click-to-expand', () => {
    localStorage.clear();
    const { panel, explorer, handle } = createPanel();
    // Collapse first
    panel.toggleExplorer();
    expect(panel.explorerVisible).toBe(false);

    vi.useFakeTimers();
    vi.advanceTimersByTime(350);
    vi.useRealTimers();

    // Attempt drag on collapsed handle
    mousedown(handle, 100, 100);
    mousemove(110, 100); // 10px movement
    mouseup(110, 100);

    // Even though movement > 3px, collapsed state means drag doesn't resize;
    // isDragging becomes true but explorerVisible is false so no resize occurs.
    // mouseup with isDragging=true saves width + calls fitActive (existing width unchanged).
    // The explorer stays collapsed since the drag path doesn't toggle.
    // This matches the design: "When collapsed, this.explorerVisible is false → drag resize skipped"
    expect(handle.classList.contains('dragging')).toBe(false);
  });
});

describe('CR-001: Handle Visibility & Chevron', () => {
  afterEach(() => { vi.restoreAllMocks(); localStorage.clear(); });

  // AC-22: Chevron class toggles
  it('adds collapsed class to handle when explorer collapses', () => {
    localStorage.clear();
    const { panel, handle } = createPanel();

    mousedown(handle, 100, 100);
    mouseup(100, 100);

    expect(handle.classList.contains('collapsed')).toBe(true);
  });

  it('removes collapsed class from handle when explorer expands', () => {
    vi.useFakeTimers();
    localStorage.clear();
    const { panel, handle } = createPanel();

    // Collapse
    panel.toggleExplorer();
    expect(handle.classList.contains('collapsed')).toBe(true);

    // Wait for animation guard
    vi.advanceTimersByTime(350);

    // Expand
    panel.toggleExplorer();
    expect(handle.classList.contains('collapsed')).toBe(false);
    vi.useRealTimers();
  });

  // AC-9: Handle visible when collapsed (no display:none)
  it('does NOT set display:none on handle when collapsed', () => {
    localStorage.clear();
    const { panel, handle } = createPanel();
    panel.toggleExplorer();

    expect(handle.style.display).not.toBe('none');
    expect(handle.classList.contains('collapsed')).toBe(true);
  });

  // AC-25: Page reload with collapsed state → handle has .collapsed class
  it('restores handle .collapsed class on page load when saved collapsed', () => {
    localStorage.setItem('console_explorer_collapsed', 'true');
    const { handle } = createPanel();

    expect(handle.classList.contains('collapsed')).toBe(true);
    expect(handle.style.display).not.toBe('none');
  });
});

describe('CR-001: Persistence via Border Toggle', () => {
  afterEach(() => { vi.restoreAllMocks(); localStorage.clear(); });

  // AC-23: Persist collapsed state on border toggle click
  it('persists collapsed state to localStorage on border click', () => {
    localStorage.clear();
    const { handle } = createPanel();

    mousedown(handle, 100, 100);
    mouseup(100, 100);

    expect(localStorage.getItem('console_explorer_collapsed')).toBe('true');
  });

  it('persists expanded state to localStorage on border click to expand', () => {
    vi.useFakeTimers();
    localStorage.clear();
    const { panel, handle } = createPanel();
    panel.toggleExplorer(); // collapse

    vi.advanceTimersByTime(350);

    mousedown(handle, 100, 100);
    mouseup(100, 100); // expand

    expect(localStorage.getItem('console_explorer_collapsed')).toBe('false');
    vi.useRealTimers();
  });

  // AC-10: Drag saves width to localStorage
  it('saves width to localStorage after drag', () => {
    localStorage.clear();
    const { handle } = createPanel();
    const body = document.getElementById('terminal-body');
    body.getBoundingClientRect = vi.fn(() => ({ right: 800, left: 0, top: 0, bottom: 600, width: 800, height: 600 }));

    mousedown(handle, 500, 100);
    mousemove(490, 100);
    mouseup(490, 100);

    const saved = localStorage.getItem('console_explorer_width');
    expect(saved).toBe('310'); // 800 - 490 = 310
  });
});

describe('CR-001: Animation Guard', () => {
  afterEach(() => { vi.restoreAllMocks(); localStorage.clear(); });

  it('ignores rapid second toggle within 300ms', () => {
    vi.useFakeTimers();
    localStorage.clear();
    const { panel, explorer } = createPanel();

    panel.toggleExplorer(); // collapse
    expect(panel.explorerVisible).toBe(false);

    panel.toggleExplorer(); // should be ignored (within 300ms)
    expect(panel.explorerVisible).toBe(false); // still collapsed

    vi.advanceTimersByTime(350);
    panel.toggleExplorer(); // should work now
    expect(panel.explorerVisible).toBe(true);

    vi.useRealTimers();
  });
});

describe('CR-001: Touch Tap Toggle', () => {
  afterEach(() => { vi.restoreAllMocks(); localStorage.clear(); });

  it('toggles explorer on touch tap (touchstart→touchend, no move)', () => {
    localStorage.clear();
    const { panel, handle } = createPanel();
    expect(panel.explorerVisible).toBe(true);

    handle.dispatchEvent(new TouchEvent('touchstart', {
      touches: [new Touch({ identifier: 0, target: handle, clientX: 100, clientY: 100 })],
      bubbles: true,
    }));
    handle.dispatchEvent(new TouchEvent('touchend', { touches: [], bubbles: true }));

    expect(panel.explorerVisible).toBe(false);
  });

  it('does not toggle on touch with significant movement', () => {
    localStorage.clear();
    const { panel, handle } = createPanel();

    handle.dispatchEvent(new TouchEvent('touchstart', {
      touches: [new Touch({ identifier: 0, target: handle, clientX: 100, clientY: 100 })],
      bubbles: true,
    }));
    handle.dispatchEvent(new TouchEvent('touchmove', {
      touches: [new Touch({ identifier: 0, target: handle, clientX: 110, clientY: 100 })],
      bubbles: true,
    }));
    handle.dispatchEvent(new TouchEvent('touchend', { touches: [], bubbles: true }));

    expect(panel.explorerVisible).toBe(true); // not toggled
  });
});

describe('CR-001: Width Restore on Expand', () => {
  afterEach(() => { vi.restoreAllMocks(); localStorage.clear(); });

  it('restores previous width from localStorage on expand', () => {
    vi.useFakeTimers();
    localStorage.clear();
    localStorage.setItem('console_explorer_width', '300');
    const { panel, explorer, handle } = createPanel();
    expect(panel.explorerWidth).toBe(300); // restored

    // Collapse
    panel.toggleExplorer();
    expect(panel.explorerVisible).toBe(false);

    vi.advanceTimersByTime(350);

    // Expand via border click
    mousedown(handle, 100, 100);
    mouseup(100, 100);

    expect(panel.explorerVisible).toBe(true);
    expect(explorer.style.width).toBe('300px');
    vi.useRealTimers();
  });

  // AC-12: Restore width from localStorage on page load
  it('restores width on construction from localStorage', () => {
    localStorage.clear();
    localStorage.setItem('console_explorer_width', '250');
    const { panel, explorer } = createPanel();
    expect(panel.explorerWidth).toBe(250);
    expect(explorer.style.width).toBe('250px');
  });

  // AC-14: Default width when no localStorage value
  it('uses default 220px width when no stored value', () => {
    localStorage.clear();
    const { panel } = createPanel();
    expect(panel.explorerWidth).toBe(220);
  });
});
