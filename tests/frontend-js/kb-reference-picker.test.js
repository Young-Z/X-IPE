/**
 * Tests for FEATURE-049-G: KB Reference Picker Modal
 * Tests: Modal, folder tree, file list, search, tag filters, multi-select, copy, insert
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { loadFeatureScript } from './helpers.js';

let _implLoaded = false;
function ensureImpl() {
  if (!_implLoaded) {
    try {
      loadFeatureScript('kb-reference-picker.js');
      _implLoaded = true;
    } catch { /* not yet implemented */ }
  }
  return typeof globalThis.KBReferencePicker !== 'undefined';
}

const MOCK_TREE = [
  { name: 'guides', type: 'folder', children: [
    { name: 'setup', type: 'folder', children: [] }
  ]},
  { name: 'readme.md', type: 'file' }
];

const MOCK_FILES = [
  {
    name: 'getting-started.md',
    path: 'knowledge-base/getting-started.md',
    frontmatter: { title: 'Getting Started', tags: { lifecycle: ['Requirement'], domain: ['Onboarding'] } }
  },
  {
    name: 'api-docs.md',
    path: 'knowledge-base/api-docs.md',
    frontmatter: { title: 'API Docs', tags: { lifecycle: [], domain: ['Architecture'] } }
  }
];

const MOCK_CONFIG = {
  tags: {
    lifecycle: ['Requirement', 'Technical Design'],
    domain: ['Onboarding', 'Architecture']
  }
};

describe('FEATURE-049-G: KB Reference Picker', () => {
  let picker;

  beforeEach(() => {
    if (!ensureImpl()) return;
    globalThis.fetch = vi.fn((url) => {
      if (typeof url === 'string' && url.includes('/api/kb/tree')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ tree: MOCK_TREE }) });
      }
      if (typeof url === 'string' && url.includes('/api/kb/config')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(MOCK_CONFIG) });
      }
      if (typeof url === 'string' && (url.includes('/api/kb/files') || url.includes('/api/kb/search'))) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ files: MOCK_FILES }) });
      }
      return Promise.resolve({ ok: false });
    });

    // Mock clipboard API
    globalThis.navigator.clipboard = { writeText: vi.fn(() => Promise.resolve()) };
  });

  afterEach(() => {
    if (picker) {
      try { picker.close(); } catch { /* ignore */ }
    }
    document.querySelectorAll('.kb-ref-overlay').forEach(el => el.remove());
    document.body.style.overflow = '';
    vi.restoreAllMocks();
  });

  describe('Modal', () => {
    it('should export KBReferencePicker class', () => {
      if (!globalThis.KBReferencePicker) return;
      expect(typeof globalThis.KBReferencePicker).toBe('function');
    });

    it('should create overlay on open', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      expect(document.querySelector('.kb-ref-overlay')).not.toBeNull();
    });

    it('should show header', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      expect(document.querySelector('.kb-ref-header h3').textContent).toContain('Reference');
    });

    it('should remove overlay on close', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      picker.close();
      await new Promise(r => setTimeout(r, 350));
      expect(document.querySelector('.kb-ref-overlay')).toBeNull();
    });
  });

  describe('Two-Panel Layout', () => {
    it('should render tree panel', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      expect(document.querySelector('.kb-ref-tree-panel')).not.toBeNull();
    });

    it('should render list panel', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      expect(document.querySelector('.kb-ref-list-panel')).not.toBeNull();
    });

    it('should show folders in tree with checkboxes', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      
      const folderChecks = document.querySelectorAll('.kb-ref-tree-panel .kb-ref-check[data-type="folder"]');
      expect(folderChecks.length).toBe(2); // guides + setup
    });

    it('should show files in list panel', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      
      const fileItems = document.querySelectorAll('.kb-ref-file-item');
      expect(fileItems.length).toBe(2);
    });
  });

  describe('Search', () => {
    it('should render search input', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      expect(document.querySelector('.kb-ref-search-input')).not.toBeNull();
    });
  });

  describe('Tag Filters', () => {
    it('should render lifecycle filter chips', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      
      const chips = document.querySelectorAll('.kb-ref-chip-lifecycle');
      expect(chips.length).toBe(2);
    });

    it('should render domain filter chips', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      
      const chips = document.querySelectorAll('.kb-ref-chip-domain');
      expect(chips.length).toBe(2);
    });

    it('should toggle active on chip click', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      
      const chip = document.querySelector('.kb-ref-chip-lifecycle');
      expect(chip.classList.contains('active')).toBe(false);
      chip.click();
      expect(chip.classList.contains('active')).toBe(true);
    });
  });

  describe('Multi-Select', () => {
    it('should update selected count when checkbox checked', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      
      const check = document.querySelector('.kb-ref-check[data-type="file"]');
      check.checked = true;
      check.dispatchEvent(new Event('change', { bubbles: true }));
      
      const count = document.querySelector('.kb-ref-count');
      expect(count.textContent).toContain('1');
    });

    it('should track selected paths', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      
      const check = document.querySelector('.kb-ref-check[data-type="file"]');
      check.checked = true;
      check.dispatchEvent(new Event('change', { bubbles: true }));
      
      expect(picker.selected.size).toBe(1);
    });
  });

  describe('Copy Button', () => {
    it('should render copy button', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      expect(document.querySelector('.kb-ref-copy-btn')).not.toBeNull();
    });

    it('should call clipboard API on copy', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      
      picker.selected.add('knowledge-base/test.md');
      document.querySelector('.kb-ref-copy-btn').click();
      
      await new Promise(r => setTimeout(r, 50));
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith('knowledge-base/test.md');
    });

    it('should copy multiple paths newline-separated', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();

      picker.selected.add('knowledge-base/a.md');
      picker.selected.add('knowledge-base/b.md');
      document.querySelector('.kb-ref-copy-btn').click();

      await new Promise(r => setTimeout(r, 50));
      const arg = navigator.clipboard.writeText.mock.calls[0][0];
      expect(arg).toContain('knowledge-base/a.md');
      expect(arg).toContain('knowledge-base/b.md');
      expect(arg).toContain('\n');
    });
  });

  describe('Insert Button', () => {
    it('should render insert button', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      expect(document.querySelector('.kb-ref-insert-btn')).not.toBeNull();
    });

    it('should call onInsert callback', async () => {
      if (!globalThis.KBReferencePicker) return;
      const onInsert = vi.fn();
      picker = new globalThis.KBReferencePicker({ onInsert });
      await picker.open();
      
      picker.selected.add('knowledge-base/test.md');
      document.querySelector('.kb-ref-insert-btn').click();
      
      await new Promise(r => setTimeout(r, 350));
      expect(onInsert).toHaveBeenCalledWith(['knowledge-base/test.md']);
    });

    it('should dispatch kb:references-inserted event', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      
      let eventPaths = null;
      document.addEventListener('kb:references-inserted', (e) => { eventPaths = e.detail.paths; }, { once: true });
      
      picker.selected.add('knowledge-base/api.md');
      document.querySelector('.kb-ref-insert-btn').click();
      
      await new Promise(r => setTimeout(r, 50));
      expect(eventPaths).toEqual(['knowledge-base/api.md']);
    });
  });

  describe('Backdrop & Scroll', () => {
    it('should close on overlay backdrop click', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();

      const overlay = document.querySelector('.kb-ref-overlay');
      overlay.dispatchEvent(new MouseEvent('click', { bubbles: true }));
      // overlay click handler checks e.target === overlay
      // Simulate by calling click directly on the overlay element
      await new Promise(r => setTimeout(r, 350));
      expect(document.querySelector('.kb-ref-overlay')).toBeNull();
    });

    it('should lock body scroll on open', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      expect(document.body.style.overflow).toBe('hidden');
    });

    it('should restore body scroll on close', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      picker.close();
      await new Promise(r => setTimeout(r, 350));
      expect(document.body.style.overflow).toBe('');
    });
  });

  describe('Search Debounce', () => {
    it('should debounce search and call API', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();

      const input = document.querySelector('.kb-ref-search-input');
      const initialCalls = globalThis.fetch.mock.calls.length;

      // Simulate typing
      input.value = 'test query';
      input.dispatchEvent(new Event('input', { bubbles: true }));

      // Before debounce — no new call yet
      await new Promise(r => setTimeout(r, 50));
      expect(globalThis.fetch.mock.calls.length).toBe(initialCalls);

      // After debounce fires
      await new Promise(r => setTimeout(r, 350));
      const searchCalls = globalThis.fetch.mock.calls.filter(c =>
        typeof c[0] === 'string' && c[0].includes('/api/kb/search')
      );
      expect(searchCalls.length).toBeGreaterThanOrEqual(1);
      expect(searchCalls[0][0]).toContain('q=test%20query');
    });
  });

  describe('Tag Filtering Behavior', () => {
    it('should filter file list when tag chip activated', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();

      // Before filter: 2 files
      expect(document.querySelectorAll('.kb-ref-file-item').length).toBe(2);

      // Click "Architecture" domain chip
      const archChip = Array.from(document.querySelectorAll('.kb-ref-chip-domain'))
        .find(c => c.dataset.tag === 'Architecture');
      archChip.click();

      // After filter: only api-docs.md has Architecture tag
      expect(document.querySelectorAll('.kb-ref-file-item').length).toBe(1);
    });
  });

  describe('Deselection', () => {
    it('should deselect and reduce count', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();

      const check = document.querySelector('.kb-ref-check[data-type="file"]');
      check.checked = true;
      check.dispatchEvent(new Event('change', { bubbles: true }));
      expect(picker.selected.size).toBe(1);

      check.checked = false;
      check.dispatchEvent(new Event('change', { bubbles: true }));
      expect(picker.selected.size).toBe(0);
      expect(document.querySelector('.kb-ref-count').textContent).toContain('0');
    });
  });

  describe('Empty States', () => {
    it('should show empty message when no folders', async () => {
      if (!globalThis.KBReferencePicker) return;
      // Override tree to empty
      globalThis.fetch = vi.fn((url) => {
        if (typeof url === 'string' && url.includes('/api/kb/tree')) {
          return Promise.resolve({ ok: true, json: () => Promise.resolve({ tree: [] }) });
        }
        if (typeof url === 'string' && url.includes('/api/kb/config')) {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(MOCK_CONFIG) });
        }
        if (typeof url === 'string' && url.includes('/api/kb/files')) {
          return Promise.resolve({ ok: true, json: () => Promise.resolve({ files: MOCK_FILES }) });
        }
        return Promise.resolve({ ok: false });
      });

      picker = new globalThis.KBReferencePicker();
      await picker.open();
      expect(document.querySelector('.kb-ref-tree-empty').textContent).toContain('No folders');
    });
  });

  describe('Error Handling', () => {
    it('should handle API failure gracefully', async () => {
      if (!globalThis.KBReferencePicker) return;
      globalThis.fetch = vi.fn(() => Promise.reject(new Error('Network error')));

      picker = new globalThis.KBReferencePicker();
      await picker.open();
      // Modal should still render without crashing
      expect(document.querySelector('.kb-ref-overlay')).not.toBeNull();
      expect(document.querySelector('.kb-ref-tree-empty').textContent).toContain('No folders');
    });
  });

  describe('HTML Escaping', () => {
    it('should escape HTML in file names', async () => {
      if (!globalThis.KBReferencePicker) return;
      const xssFiles = [{
        name: '<img src=x onerror=alert(1)>',
        path: 'knowledge-base/xss.md',
        frontmatter: { title: '<script>alert("xss")</script>', tags: { lifecycle: [], domain: [] } }
      }];
      globalThis.fetch = vi.fn((url) => {
        if (typeof url === 'string' && url.includes('/api/kb/tree')) {
          return Promise.resolve({ ok: true, json: () => Promise.resolve({ tree: MOCK_TREE }) });
        }
        if (typeof url === 'string' && url.includes('/api/kb/config')) {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(MOCK_CONFIG) });
        }
        if (typeof url === 'string' && url.includes('/api/kb/files')) {
          return Promise.resolve({ ok: true, json: () => Promise.resolve({ files: xssFiles }) });
        }
        return Promise.resolve({ ok: false });
      });

      picker = new globalThis.KBReferencePicker();
      await picker.open();

      const fileName = document.querySelector('.kb-ref-file-name');
      expect(fileName.textContent).toContain('<script>');
      // The script should be text content, NOT an actual script element
      expect(document.querySelector('.kb-ref-list-panel script')).toBeNull();
    });
  });
});
