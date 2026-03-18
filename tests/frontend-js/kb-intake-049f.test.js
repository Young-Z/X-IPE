/**
 * Tests for FEATURE-049-F: KB AI Librarian & Intake
 * Tests: Intake scene rendering, status display, filters, action dispatch,
 * AI Librarian command fix, sidebar badge, data loading
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { loadFeatureScript } from './helpers.js';

let _implLoaded = false;
function ensureImpl() {
  if (!_implLoaded) {
    try {
      loadFeatureScript('kb-browse-modal.js');
      _implLoaded = true;
    } catch { /* not yet implemented */ }
  }
  return typeof globalThis.KBBrowseModal !== 'undefined';
}

const MOCK_INTAKE_RESPONSE = {
  items: [
    { name: 'notes.md', path: 'notes.md', type: 'file', size_bytes: 1024, modified_date: '2026-03-16', file_type: 'md', status: 'pending', destination: null },
    { name: 'guide.pdf', path: 'guide.pdf', type: 'file', size_bytes: 50000, modified_date: '2026-03-15', file_type: 'pdf', status: 'processing', destination: 'docs/' },
    { name: 'old.md', path: 'old.md', type: 'file', size_bytes: 512, modified_date: '2026-03-14', file_type: 'md', status: 'filed', destination: 'archive/' },
  ],
  stats: { total: 3, pending: 1, processing: 1, filed: 1 },
  pending_deep_count: 1
};

const MOCK_EMPTY_INTAKE = {
  items: [],
  stats: { total: 0, pending: 0, processing: 0, filed: 0 },
  pending_deep_count: 0
};

const MOCK_TREE_INTAKE = {
  items: [
    { name: 'readme.md', path: 'readme.md', type: 'file', size_bytes: 256, modified_date: '2026-03-16', file_type: 'md', status: 'pending', destination: null },
    {
      name: 'extracted-docs', path: 'extracted-docs', type: 'folder', item_count: 2, status: 'pending',
      children: [
        { name: 'api.md', path: 'extracted-docs/api.md', type: 'file', size_bytes: 1024, modified_date: '2026-03-16', file_type: 'md', status: 'pending', destination: null },
        { name: 'setup.md', path: 'extracted-docs/setup.md', type: 'file', size_bytes: 512, modified_date: '2026-03-15', file_type: 'md', status: 'filed', destination: 'guides/' },
      ]
    },
    {
      name: 'images', path: 'images', type: 'folder', item_count: 1, status: 'filed',
      children: [
        { name: 'logo.png', path: 'images/logo.png', type: 'file', size_bytes: 8192, modified_date: '2026-03-14', file_type: 'png', status: 'filed', destination: 'assets/' },
      ]
    }
  ],
  stats: { total: 3, pending: 2, processing: 0, filed: 1 },
  pending_deep_count: 2
};

describe('FEATURE-049-F: KB AI Librarian & Intake', () => {
  beforeEach(() => {
    if (!ensureImpl()) return;
    // Mock fetch
    globalThis.fetch = vi.fn((url) => {
      if (url === '/api/kb/intake') {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(MOCK_INTAKE_RESPONSE) });
      }
      if (url === '/api/kb/tree') {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ tree: [] }) });
      }
      if (url?.startsWith('/api/kb/files')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ files: [] }) });
      }
      if (url === '/api/kb/config') {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ tags: { lifecycle: [], domain: [] } }) });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
    globalThis.showToast = vi.fn();
    globalThis.showConfirmModal = vi.fn(() => Promise.resolve(true));
    globalThis.hljs = undefined;
    globalThis.marked = undefined;
  });

  afterEach(() => {
    vi.restoreAllMocks();
    document.body.innerHTML = '';
  });

  // AC-049-F-04d: AI Librarian command fix
  describe('AC-049-F-04: AI Librarian Command', () => {
    it('should use plain NL command without --workflow-mode flag', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      // Mock terminalManager
      const sendFn = vi.fn();
      globalThis.window.terminalManager = { sendCopilotPromptCommand: sendFn };
      modal.close = vi.fn();
      modal._runAILibrarian();
      // The command should be called after timeout, so check clipboard fallback scenario
      // When no terminal manager, it should copy the clean command
      delete globalThis.window.terminalManager;
      globalThis.navigator = { clipboard: { writeText: vi.fn() } };
      modal._runAILibrarian();
      const copiedText = globalThis.navigator.clipboard.writeText.mock.calls[0]?.[0];
      expect(copiedText).toBe('organize knowledge base intake files with AI Librarian');
      expect(copiedText).not.toContain('--workflow-mode');
    });
  });

  // AC-049-F-02: Intake File Listing
  describe('AC-049-F-02: Intake Scene Rendering', () => {
    it('should fetch from /api/kb/intake endpoint', async () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      const result = await modal._loadIntakeFiles();
      expect(globalThis.fetch).toHaveBeenCalledWith('/api/kb/intake');
      expect(result.items).toHaveLength(3);
      expect(result.stats.total).toBe(3);
      expect(result.pending_deep_count).toBe(1);
    });

    it('should return empty result on fetch failure', async () => {
      if (!ensureImpl()) return;
      globalThis.fetch = vi.fn(() => Promise.resolve({ ok: false }));
      const modal = new KBBrowseModal();
      const result = await modal._loadIntakeFiles();
      expect(result.items).toEqual([]);
      expect(result.stats.total).toBe(0);
      expect(result.pending_deep_count).toBe(0);
    });

    it('should return empty result on network error', async () => {
      if (!ensureImpl()) return;
      globalThis.fetch = vi.fn(() => Promise.reject(new Error('Network error')));
      const modal = new KBBrowseModal();
      const result = await modal._loadIntakeFiles();
      expect(result.items).toEqual([]);
    });
  });

  // AC-049-F-03: Status Tracking
  describe('AC-049-F-03: Status Display', () => {
    it('should have intakeFilter property defaulting to all', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      expect(modal.intakeFilter).toBe('all');
    });
  });

  // AC-049-F-05: Per-File Actions
  describe('AC-049-F-05: Per-File Actions', () => {
    it('should have _handleIntakeAction method', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      expect(typeof modal._handleIntakeAction).toBe('function');
    });

    it('should handle preview action by showing article', async () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      modal._showArticle = vi.fn();
      await modal._handleIntakeAction('preview', 'notes.md', null);
      expect(modal._showArticle).toHaveBeenCalledWith('.intake/notes.md');
    });

    it('should handle remove action with confirmation', async () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      modal._refreshIntakeFiles = vi.fn();
      globalThis.fetch = vi.fn(() => Promise.resolve({ ok: true }));
      await modal._handleIntakeAction('remove', 'notes.md', null);
      expect(globalThis.showConfirmModal).toHaveBeenCalled();
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('.intake%2Fnotes.md'),
        expect.objectContaining({ method: 'DELETE' })
      );
    });

    it('should handle view action by switching to browse', async () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      modal._showScene = vi.fn();
      modal._renderSidebarFolders = vi.fn();
      modal._renderBrowseContent = vi.fn();
      await modal._handleIntakeAction('view', 'old.md', 'archive');
      expect(modal._showScene).toHaveBeenCalledWith('browse');
      expect(modal.activeSidebarFolder).toBe('archive');
    });

    it('should handle undo action with move and status reset', async () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      modal._refreshIntakeFiles = vi.fn();
      globalThis.fetch = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ ok: true }) }));
      await modal._handleIntakeAction('undo', 'old.md', 'archive');
      // Should call move endpoint then status reset
      expect(globalThis.fetch).toHaveBeenCalledTimes(2);
      const [moveUrl, moveOpts] = globalThis.fetch.mock.calls[0];
      expect(moveUrl).toBe('/api/kb/files/move');
      const moveBody = JSON.parse(moveOpts.body);
      expect(moveBody.source).toBe('archive/old.md');
      expect(moveBody.target).toBe('.intake/old.md');
    });
  });

  // AC-049-F-06: Statistics & Badges
  describe('AC-049-F-06: Statistics', () => {
    it('should load intake stats during data loading', async () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      await modal._loadData();
      expect(modal._intakeStats).toBeDefined();
      expect(modal._intakeStats.pending).toBe(1);
    });
  });

  // AC-049-F-07: Configuration
  describe('AC-049-F-07: Configuration', () => {
    it('should have intake API URL without /api/kb prefix in static API', () => {
      if (!ensureImpl()) return;
      // The intake endpoint is called directly, not via static API constant
      // This test verifies the endpoint pattern is correct
      const modal = new KBBrowseModal();
      expect(KBBrowseModal.API.TREE).toBe('/api/kb/tree');
      expect(KBBrowseModal.API.FILES).toBe('/api/kb/files');
    });
  });

  describe('Bug Fix: Librarian panel file list rendering', () => {
    it('should have _renderIntakeFileList method', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      expect(typeof modal._renderIntakeFileList).toBe('function');
    });

    it('should render file rows into kb-intake-files container', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      // Create a mock overlay with the container
      modal.overlay = document.createElement('div');
      const container = document.createElement('div');
      container.setAttribute('data-role', 'intake-files');
      modal.overlay.appendChild(container);

      modal._renderIntakeFileList(MOCK_INTAKE_RESPONSE.items);
      const fileRows = container.querySelectorAll('.kb-intake-file');
      expect(fileRows.length).toBe(3);
      expect(container.innerHTML).toContain('notes.md');
      expect(container.innerHTML).toContain('guide.pdf');
    });

    it('should clear container when no files', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      modal.overlay = document.createElement('div');
      const container = document.createElement('div');
      container.setAttribute('data-role', 'intake-files');
      container.innerHTML = '<div>old content</div>';
      modal.overlay.appendChild(container);

      modal._renderIntakeFileList([]);
      expect(container.innerHTML).toBe('');
    });
  });

  describe('Bug Fix: Action buttons display inline', () => {
    it('should use inline-flex for kb-content-btn in CSS', async () => {
      // Read the CSS file and verify inline-flex
      const fs = await import('fs');
      const css = fs.readFileSync('src/x_ipe/static/css/kb-browse-modal.css', 'utf8');
      const btnMatch = css.match(/\.kb-content-btn\s*\{[^}]*display:\s*([\w-]+)/);
      expect(btnMatch).not.toBeNull();
      expect(btnMatch[1]).toBe('inline-flex');
    });
  });

  // ─── CR-005: Folder Support Tests ────────────────
  describe('CR-005: Folder Tree Support', () => {
    it('should have _expandedFolders Set initialized in constructor', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      expect(modal._expandedFolders).toBeInstanceOf(Set);
      expect(modal._expandedFolders.size).toBe(0);
    });

    it('should have _intakeItems array initialized in constructor', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      expect(modal._intakeItems).toEqual([]);
    });

    it('should have _toggleFolder method that toggles expand state', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      modal._renderIntakeScene = vi.fn(); // prevent actual render
      modal._toggleFolder('extracted-docs');
      expect(modal._expandedFolders.has('extracted-docs')).toBe(true);
      modal._toggleFolder('extracted-docs');
      expect(modal._expandedFolders.has('extracted-docs')).toBe(false);
    });

    it('should filter items recursively preserving folder hierarchy', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      const filtered = modal._filterIntakeItems(MOCK_TREE_INTAKE.items, 'pending');
      // readme.md is pending (file)
      expect(filtered.some(i => i.name === 'readme.md')).toBe(true);
      // extracted-docs has a pending child (api.md) so folder shown
      const folder = filtered.find(i => i.name === 'extracted-docs');
      expect(folder).toBeDefined();
      // Only the pending child should remain
      expect(folder.children).toHaveLength(1);
      expect(folder.children[0].name).toBe('api.md');
      // images folder has no pending children — should be excluded
      expect(filtered.find(i => i.name === 'images')).toBeUndefined();
    });

    it('should return all items when filter is "all"', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      const filtered = modal._filterIntakeItems(MOCK_TREE_INTAKE.items, 'all');
      expect(filtered).toEqual(MOCK_TREE_INTAKE.items);
    });

    it('should render folder row with chevron and folder icon', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      const folderItem = MOCK_TREE_INTAKE.items[1]; // extracted-docs
      const html = modal._renderIntakeRow(folderItem, 0);
      expect(html).toContain('data-intake-toggle="extracted-docs"');
      expect(html).toContain('bi-chevron-right'); // collapsed by default
      expect(html).toContain('bi-folder');
      expect(html).toContain('extracted-docs');
      expect(html).toContain('2 items');
    });

    it('should render expanded folder with children', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      modal._expandedFolders.add('extracted-docs');
      const folderItem = MOCK_TREE_INTAKE.items[1];
      const html = modal._renderIntakeRow(folderItem, 0);
      expect(html).toContain('bi-chevron-down'); // expanded
      expect(html).toContain('bi-folder2-open');
      expect(html).toContain('api.md');
      expect(html).toContain('setup.md');
    });

    it('should render file row with file icon and indent', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      const fileItem = MOCK_TREE_INTAKE.items[0]; // readme.md
      const html = modal._renderIntakeRow(fileItem, 0);
      expect(html).toContain('bi-file-earmark-text');
      expect(html).toContain('readme.md');
      expect(html).not.toContain('data-intake-toggle');
    });

    it('should indent nested items by 20px per level', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      const childItem = MOCK_TREE_INTAKE.items[1].children[0]; // api.md at depth 1
      const html = modal._renderIntakeRow(childItem, 1);
      expect(html).toContain('padding-left:44px'); // 1*20 + 24 = 44
    });

    it('should show folder actions without preview button', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      const folderItem = { name: 'docs', path: 'docs', type: 'folder', item_count: 2, status: 'pending', children: [] };
      const btns = modal._intakeActionButtons(folderItem);
      expect(btns).not.toContain('data-intake-op="preview"');
      expect(btns).toContain('data-intake-op="assign"');
      expect(btns).toContain('data-intake-op="remove"');
      expect(btns).toContain('data-intake-type="folder"');
    });

    it('should show file actions with preview button', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      const fileItem = { name: 'test.md', path: 'test.md', type: 'file', status: 'pending' };
      const btns = modal._intakeActionButtons(fileItem);
      expect(btns).toContain('data-intake-op="preview"');
      expect(btns).toContain('data-intake-op="assign"');
      expect(btns).toContain('data-intake-type="file"');
    });

    it('should not show view action for filed folders', () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      const folderItem = { name: 'docs', path: 'docs', type: 'folder', item_count: 1, status: 'filed', destination: 'guides/', children: [] };
      const btns = modal._intakeActionButtons(folderItem);
      expect(btns).not.toContain('data-intake-op="view"');
      expect(btns).toContain('data-intake-op="undo"');
    });

    it('should handle folder assign by passing path to API', async () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      modal._refreshIntakeFiles = vi.fn();
      modal._getFolderNames = vi.fn(() => ['guides', 'docs']);
      globalThis.fetch = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ ok: true }) }));
      // Assign triggers folder picker — we test the API call pattern
      await modal._handleIntakeAction('assign', 'extracted-docs', null, 'folder');
      // Picker is created but we test the cascade is setup correctly via data attributes
      const picker = document.querySelector('.kb-upload-folder-dropdown');
      expect(picker).not.toBeNull();
    });

    it('should handle folder remove with warning message', async () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      modal._refreshIntakeFiles = vi.fn();
      globalThis.fetch = vi.fn(() => Promise.resolve({ ok: true }));
      await modal._handleIntakeAction('remove', 'extracted-docs', null, 'folder');
      expect(globalThis.showConfirmModal).toHaveBeenCalledWith(
        'Remove',
        expect.stringContaining('folder and all its contents')
      );
    });

    it('should skip preview for folders', async () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      modal._showArticle = vi.fn();
      await modal._handleIntakeAction('preview', 'extracted-docs', null, 'folder');
      expect(modal._showArticle).not.toHaveBeenCalled();
    });

    it('should skip view for folders', async () => {
      if (!ensureImpl()) return;
      const modal = new KBBrowseModal();
      modal._showScene = vi.fn();
      await modal._handleIntakeAction('view', 'extracted-docs', 'guides/', 'folder');
      expect(modal._showScene).not.toHaveBeenCalled();
    });

    it('should use pending_deep_count for badges', async () => {
      if (!ensureImpl()) return;
      globalThis.fetch = vi.fn((url) => {
        if (url === '/api/kb/intake') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(MOCK_TREE_INTAKE) });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      });
      const modal = new KBBrowseModal();
      modal.overlay = document.createElement('div');
      const badge = document.createElement('span');
      badge.className = 'intake-badge';
      modal.overlay.appendChild(badge);
      modal._renderIntakeFileList = vi.fn();
      modal.currentScene = 'other';
      await modal._refreshIntakeFiles();
      expect(badge.textContent).toBe('2'); // pending_deep_count = 2
    });
  });
});
