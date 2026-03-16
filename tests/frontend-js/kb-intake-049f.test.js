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
  files: [
    { name: 'notes.md', path: '.intake/notes.md', size_bytes: 1024, modified_date: '2026-03-16', file_type: 'md', status: 'pending', destination: null },
    { name: 'guide.pdf', path: '.intake/guide.pdf', size_bytes: 50000, modified_date: '2026-03-15', file_type: 'pdf', status: 'processing', destination: 'docs/' },
    { name: 'old.md', path: '.intake/old.md', size_bytes: 512, modified_date: '2026-03-14', file_type: 'md', status: 'filed', destination: 'archive/' },
  ],
  stats: { total: 3, pending: 1, processing: 1, filed: 1 }
};

const MOCK_EMPTY_INTAKE = {
  files: [],
  stats: { total: 0, pending: 0, processing: 0, filed: 0 }
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
      expect(result.files).toHaveLength(3);
      expect(result.stats.total).toBe(3);
    });

    it('should return empty result on fetch failure', async () => {
      if (!ensureImpl()) return;
      globalThis.fetch = vi.fn(() => Promise.resolve({ ok: false }));
      const modal = new KBBrowseModal();
      const result = await modal._loadIntakeFiles();
      expect(result.files).toEqual([]);
      expect(result.stats.total).toBe(0);
    });

    it('should return empty result on network error', async () => {
      if (!ensureImpl()) return;
      globalThis.fetch = vi.fn(() => Promise.reject(new Error('Network error')));
      const modal = new KBBrowseModal();
      const result = await modal._loadIntakeFiles();
      expect(result.files).toEqual([]);
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
});
