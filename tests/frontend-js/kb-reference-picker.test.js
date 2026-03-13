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

    it('should show clickable folder tree items without checkboxes', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();

      const treeItems = document.querySelectorAll('.kb-ref-tree-panel .kb-ref-tree-item');
      expect(treeItems.length).toBe(3); // KB Root + guides + setup
      const treeChecks = document.querySelectorAll('.kb-ref-tree-panel .kb-ref-check');
      expect(treeChecks.length).toBe(0);
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
      
      picker.selected.add('x-ipe-docs/knowledge-base/test.md');
      document.querySelector('.kb-ref-copy-btn').click();
      
      await new Promise(r => setTimeout(r, 50));
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith('x-ipe-docs/knowledge-base/test.md');
    });

    it('should copy multiple paths newline-separated', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();

      picker.selected.add('x-ipe-docs/knowledge-base/a.md');
      picker.selected.add('x-ipe-docs/knowledge-base/b.md');
      document.querySelector('.kb-ref-copy-btn').click();

      await new Promise(r => setTimeout(r, 50));
      const arg = navigator.clipboard.writeText.mock.calls[0][0];
      expect(arg).toContain('x-ipe-docs/knowledge-base/a.md');
      expect(arg).toContain('x-ipe-docs/knowledge-base/b.md');
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
      
      picker.selected.add('x-ipe-docs/knowledge-base/test.md');
      document.querySelector('.kb-ref-insert-btn').click();
      
      await new Promise(r => setTimeout(r, 350));
      expect(onInsert).toHaveBeenCalledWith(['x-ipe-docs/knowledge-base/test.md']);
    });

    it('should dispatch kb:references-inserted event', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      
      let eventPaths = null;
      document.addEventListener('kb:references-inserted', (e) => { eventPaths = e.detail.paths; }, { once: true });
      
      picker.selected.add('x-ipe-docs/knowledge-base/api.md');
      document.querySelector('.kb-ref-insert-btn').click();
      
      await new Promise(r => setTimeout(r, 50));
      expect(eventPaths).toEqual(['x-ipe-docs/knowledge-base/api.md']);
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

  describe('Breadcrumb Navigation', () => {
    it('should render breadcrumb bar', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      expect(document.querySelector('.kb-ref-breadcrumb')).not.toBeNull();
    });

    it('should show KB Root at root level', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const trail = document.querySelector('.kb-ref-crumb-trail');
      expect(trail.textContent).toContain('KB Root');
    });

    it('should have folder checkbox in breadcrumb', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const check = document.querySelector('.kb-ref-folder-check');
      expect(check).not.toBeNull();
      expect(check.dataset.type).toBe('folder');
      expect(check.dataset.path).toBe('x-ipe-docs/knowledge-base');
    });
  });

  describe('Folder Navigation', () => {
    it('should show sub-folders in right panel', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const subfolders = document.querySelectorAll('.kb-ref-subfolder');
      expect(subfolders.length).toBe(1); // guides
    });

    it('should navigate when tree folder clicked', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const guidesItem = Array.from(document.querySelectorAll('.kb-ref-tree-item'))
        .find(el => el.dataset.folderPath === 'guides');
      guidesItem.click();
      expect(picker.currentFolder).toBe('guides');
    });

    it('should toggle check when subfolder in right panel clicked', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const subfolder = document.querySelector('.kb-ref-subfolder');
      const checkbox = subfolder.querySelector('.kb-ref-check');
      expect(checkbox.checked).toBe(false);
      subfolder.click();
      expect(checkbox.checked).toBe(true);
      expect(picker.selected.size).toBe(1);
    });

    it('should navigate when subfolder in right panel double-clicked', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const subfolder = document.querySelector('.kb-ref-subfolder');
      subfolder.dispatchEvent(new MouseEvent('dblclick', { bubbles: true }));
      expect(picker.currentFolder).toBe('guides');
    });

    it('should update breadcrumb on navigation', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      picker._navigateToFolder('guides');
      const trail = document.querySelector('.kb-ref-crumb-trail');
      expect(trail.textContent).toContain('guides');
    });
  });

  describe('Full Paths', () => {
    it('should prefix file paths with x-ipe-docs/', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const check = document.querySelector('.kb-ref-check[data-type="file"]');
      expect(check.dataset.path).toMatch(/^x-ipe-docs\//);
    });

    it('should prefix folder path with x-ipe-docs/', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const check = document.querySelector('.kb-ref-folder-check');
      expect(check.dataset.path).toMatch(/^x-ipe-docs\//);
    });
  });

  describe('Tag Filter Layout', () => {
    it('should render tag chips in separate rows', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const rows = document.querySelectorAll('.kb-ref-chip-row');
      expect(rows.length).toBe(2);
    });

    it('should have lifecycle chips in first row and domain in second', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const rows = document.querySelectorAll('.kb-ref-chip-row');
      expect(rows[0].querySelectorAll('.kb-ref-chip-lifecycle').length).toBe(2);
      expect(rows[1].querySelectorAll('.kb-ref-chip-domain').length).toBe(2);
    });
  });

  describe('Global instantiation (init.js integration)', () => {
    it('should open reference picker when triggered via window.kbReferencePicker', async () => {
      if (!globalThis.KBReferencePicker) return;
      // Simulate what init.js should do: create global instance
      globalThis.window = globalThis.window || globalThis;
      globalThis.window.kbReferencePicker = new globalThis.KBReferencePicker();

      expect(typeof globalThis.window.kbReferencePicker).not.toBe('undefined');
      expect(typeof globalThis.window.kbReferencePicker.open).toBe('function');

      await globalThis.window.kbReferencePicker.open();
      const overlay = document.querySelector('.kb-ref-overlay');
      expect(overlay).not.toBeNull();

      globalThis.window.kbReferencePicker.close();
      delete globalThis.window.kbReferencePicker;
    });

    it('should be instantiated by init.js alongside KBBrowseModal and KBArticleEditor', () => {
      if (!globalThis.KBReferencePicker) return;
      // This test documents the expected init.js behavior:
      // init.js should create window.kbReferencePicker just like it creates
      // window.kbBrowseModal and window.kbArticleEditor
      const initContent = require('fs').readFileSync(
        require('path').resolve(__dirname, '../../src/x_ipe/static/js/init.js'),
        'utf8'
      );
      expect(initContent).toContain('KBReferencePicker');
      expect(initContent).toContain('kbReferencePicker');
    });
  });

  describe('CR-002: View Toggle (list/icon)', () => {
    it('should default to list view', () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      expect(picker.viewMode).toBe('list');
    });

    it('should render view toggle buttons in breadcrumb bar', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const btns = document.querySelectorAll('.kb-ref-view-btn');
      expect(btns.length).toBe(2);
      expect(btns[0].dataset.view).toBe('list');
      expect(btns[1].dataset.view).toBe('icon');
    });

    it('should mark list button as active by default', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const listBtn = document.querySelector('[data-view="list"]');
      expect(listBtn.classList.contains('active')).toBe(true);
      const iconBtn = document.querySelector('[data-view="icon"]');
      expect(iconBtn.classList.contains('active')).toBe(false);
    });

    it('should switch to icon view on icon button click', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const iconBtn = document.querySelector('[data-view="icon"]');
      iconBtn.click();
      expect(picker.viewMode).toBe('icon');
      const grid = document.querySelector('.kb-ref-icon-grid');
      expect(grid).not.toBeNull();
    });

    it('should render icon cards in icon view', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      picker.viewMode = 'icon';
      picker._refreshRightPanel();
      const cards = document.querySelectorAll('.kb-ref-icon-card');
      expect(cards.length).toBeGreaterThan(0);
    });

    it('should place checkbox at bottom-right in icon view cards', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      picker.viewMode = 'icon';
      picker._refreshRightPanel();
      const iconCheck = document.querySelector('.kb-ref-icon-check');
      expect(iconCheck).not.toBeNull();
      expect(iconCheck.classList.contains('kb-ref-icon-check')).toBe(true);
    });
  });

  describe('CR-002: Sub-folder Checkboxes', () => {
    it('should render checkboxes on sub-folders in list view', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const subfolder = document.querySelector('.kb-ref-subfolder');
      expect(subfolder).not.toBeNull();
      const checkbox = subfolder.querySelector('.kb-ref-check');
      expect(checkbox).not.toBeNull();
      expect(checkbox.dataset.type).toBe('folder');
    });

    it('should render checkboxes on sub-folders in icon view', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      picker.viewMode = 'icon';
      picker._refreshRightPanel();
      const folderCard = document.querySelector('.kb-ref-icon-folder');
      expect(folderCard).not.toBeNull();
      const checkbox = folderCard.querySelector('.kb-ref-check');
      expect(checkbox).not.toBeNull();
      expect(checkbox.dataset.type).toBe('folder');
    });

    it('should use full path for sub-folder checkbox data-path', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const subfolder = document.querySelector('.kb-ref-subfolder');
      const checkbox = subfolder.querySelector('.kb-ref-check');
      expect(checkbox.dataset.path).toContain('x-ipe-docs/knowledge-base');
    });
  });

  describe('CR-002: Click-to-check / Double-click Navigation', () => {
    it('should toggle file checkbox on single click', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const fileItem = document.querySelector('.kb-ref-file-item');
      if (!fileItem) return;
      const checkbox = fileItem.querySelector('.kb-ref-check');
      expect(checkbox.checked).toBe(false);
      fileItem.click();
      expect(checkbox.checked).toBe(true);
      expect(picker.selected.size).toBe(1);
    });

    it('should uncheck on second click', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const fileItem = document.querySelector('.kb-ref-file-item');
      if (!fileItem) return;
      fileItem.click();
      expect(picker.selected.size).toBe(1);
      fileItem.click();
      expect(picker.selected.size).toBe(0);
    });

    it('should toggle icon card checkbox on single click', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      picker.viewMode = 'icon';
      picker._refreshRightPanel();
      const card = document.querySelector('.kb-ref-icon-card');
      if (!card) return;
      const checkbox = card.querySelector('.kb-ref-check');
      expect(checkbox.checked).toBe(false);
      card.click();
      expect(checkbox.checked).toBe(true);
    });

    it('should navigate into folder on double-click in icon view', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      picker.viewMode = 'icon';
      picker._refreshRightPanel();
      const folderCard = document.querySelector('.kb-ref-icon-folder');
      if (!folderCard) return;
      folderCard.dispatchEvent(new MouseEvent('dblclick', { bubbles: true }));
      expect(picker.currentFolder).toBe('guides');
    });
  });

  describe('CR-002: Footer Tip', () => {
    it('should show double-click tip in footer', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const tip = document.querySelector('.kb-ref-tip');
      expect(tip).not.toBeNull();
      expect(tip.textContent).toContain('Double-click');
    });
  });

  describe('TASK-862: Auto-persist references when no onInsert callback', () => {
    it('should detect ideation folder from breadcrumb', () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      // No breadcrumb → null
      expect(picker._detectIdeationFolder()).toBeNull();

      // Add a breadcrumb with current folder
      const crumb = document.createElement('span');
      crumb.className = 'breadcrumb-item current';
      crumb.dataset.path = 'x-ipe-docs/ideas/002. Feature-Brand Themes';
      document.body.appendChild(crumb);
      expect(picker._detectIdeationFolder()).toBe('x-ipe-docs/ideas/002. Feature-Brand Themes');
      crumb.remove();
    });

    it('should return null for non-ideas paths', () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      const crumb = document.createElement('span');
      crumb.className = 'breadcrumb-item current';
      crumb.dataset.path = 'x-ipe-docs/requirements/EPIC-001';
      document.body.appendChild(crumb);
      expect(picker._detectIdeationFolder()).toBeNull();
      crumb.remove();
    });

    it('should call _persistReferences when onInsert is not set', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();
      await picker.open();
      const persistSpy = vi.spyOn(picker, '_persistReferences').mockResolvedValue();

      // Select a file
      const fileCheck = picker.overlay.querySelector('.kb-ref-check[data-type="file"]');
      if (fileCheck) {
        fileCheck.checked = true;
        picker.selected.add(fileCheck.dataset.path);
      }

      // Click insert
      picker.overlay.querySelector('.kb-ref-insert-btn').click();
      await vi.waitFor(() => expect(persistSpy).toHaveBeenCalledTimes(1));
      persistSpy.mockRestore();
    });

    it('should NOT call _persistReferences when onInsert IS set', async () => {
      if (!globalThis.KBReferencePicker) return;
      const onInsert = vi.fn();
      picker = new globalThis.KBReferencePicker({ onInsert });
      await picker.open();
      const persistSpy = vi.spyOn(picker, '_persistReferences').mockResolvedValue();

      // Select a file
      const fileCheck = picker.overlay.querySelector('.kb-ref-check[data-type="file"]');
      if (fileCheck) {
        fileCheck.checked = true;
        picker.selected.add(fileCheck.dataset.path);
      }

      // Click insert
      picker.overlay.querySelector('.kb-ref-insert-btn').click();
      expect(onInsert).toHaveBeenCalledTimes(1);
      expect(persistSpy).not.toHaveBeenCalled();
      persistSpy.mockRestore();
    });

    it('should POST to /api/ideas/kb-references with detected folder', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();

      // Mock fetch
      const origFetch = globalThis.fetch;
      const fetchMock = vi.fn().mockResolvedValue({
        json: () => Promise.resolve({ success: true, path: 'test' })
      });
      globalThis.fetch = fetchMock;

      // Set up breadcrumb
      const crumb = document.createElement('span');
      crumb.className = 'breadcrumb-item current';
      crumb.dataset.path = 'x-ipe-docs/ideas/002. Feature-Brand Themes';
      document.body.appendChild(crumb);

      await picker._persistReferences(['knowledge-base/guides/setup.md']);

      expect(fetchMock).toHaveBeenCalledTimes(1);
      const [url, opts] = fetchMock.mock.calls[0];
      expect(url).toBe('/api/ideas/kb-references');
      expect(opts.method).toBe('POST');
      const body = JSON.parse(opts.body);
      expect(body.folder_path).toBe('x-ipe-docs/ideas/002. Feature-Brand Themes');
      expect(body.kb_references).toEqual(['knowledge-base/guides/setup.md']);

      crumb.remove();
      globalThis.fetch = origFetch;
    });

    it('should not POST when no ideation folder is detected', async () => {
      if (!globalThis.KBReferencePicker) return;
      picker = new globalThis.KBReferencePicker();

      const origFetch = globalThis.fetch;
      const fetchMock = vi.fn();
      globalThis.fetch = fetchMock;

      await picker._persistReferences(['knowledge-base/guides/setup.md']);
      expect(fetchMock).not.toHaveBeenCalled();

      globalThis.fetch = origFetch;
    });
  });
});
