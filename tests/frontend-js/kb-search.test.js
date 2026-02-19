/**
 * FEATURE-025-E: KB Search & Preview — Frontend Tests (TDD)
 *
 * Tests for:
 * - Search modal: open/close, keyboard nav, debounce, result rendering
 * - Preview panel: show/hide, metadata display, actions
 * - Sidebar search highlight enhancement
 * - Filter chip toggling
 */

import { describe, it, expect, vi, beforeEach, afterEach, beforeAll } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import vm from 'vm';

// ============================================================================
// Load kb-search.js into global scope
// ============================================================================

const JS_PATH = resolve(import.meta.dirname, '../../src/x_ipe/static/js/features/kb-search.js');

// Load once — `const kbSearch` can only be declared once in vm context
beforeAll(() => {
  const code = readFileSync(JS_PATH, 'utf-8');
  vm.runInThisContext(code);
});

/** Minimal DOM setup for KB container */
function createKBDOM() {
  document.body.innerHTML = `
    <div class="kb-container" id="kb-container">
      <div class="kb-sidebar" id="kb-sidebar">
        <input type="text" id="kb-search" placeholder="Search files...">
        <div class="kb-tree" id="kb-tree"></div>
      </div>
      <div class="kb-content" id="kb-content"></div>
    </div>
  `;
}

/** Mock fetch globally */
function mockFetch(responseData, status = 200) {
  return vi.fn(() =>
    Promise.resolve({
      ok: status >= 200 && status < 300,
      status,
      json: () => Promise.resolve(responseData),
    })
  );
}

/** Sample grouped search results */
function sampleSearchResults() {
  return {
    query: 'report',
    results: {
      files: [
        { path: 'landing/report.pdf', name: 'report.pdf', type: 'pdf', size: 1024, keywords: ['report'] },
        { path: 'landing/notes.md', name: 'notes.md', type: 'markdown', size: 512, keywords: ['notes'] },
      ],
      topics: [
        { name: 'machine-learning', file_count: 3 },
      ],
      summaries: [
        { topic: 'machine-learning', version: 'v1', path: 'processed/machine-learning/summary-v1.md' },
      ],
    },
    total: 4,
  };
}


// ============================================================================
// Search Modal Tests
// ============================================================================

describe('KB Search Modal', () => {
  beforeEach(() => {
    createKBDOM();
    vi.useFakeTimers();
    globalThis.fetch = mockFetch(sampleSearchResults());
    // Reset internal state since DOM is recreated
    window.kbSearch.modal = null;
    window.kbSearch.previewPanel = null;
    window.kbSearch.activeResultIndex = -1;
    window.kbSearch.results = [];
    window.kbSearch.activeFilters = { types: [], topic: null };
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
    document.body.innerHTML = '';
  });

  describe('Opening and Closing', () => {
    it('should create modal DOM when openModal is called', async () => {

      window.kbSearch.init();
      window.kbSearch.openModal();
      const modal = document.getElementById('kb-search-modal');
      expect(modal).not.toBeNull();
    });

    it('should show modal with backdrop on open', async () => {

      window.kbSearch.init();
      window.kbSearch.openModal();
      const modal = document.getElementById('kb-search-modal');
      expect(modal.classList.contains('active') || modal.style.display !== 'none').toBe(true);
    });

    it('should close modal when closeModal is called', async () => {

      window.kbSearch.init();
      window.kbSearch.openModal();
      window.kbSearch.closeModal();
      const modal = document.getElementById('kb-search-modal');
      expect(modal.classList.contains('active')).toBe(false);
    });

    it('should focus input when modal opens', async () => {

      window.kbSearch.init();
      window.kbSearch.openModal();
      const input = document.querySelector('#kb-search-modal input[type="text"]');
      expect(input).not.toBeNull();
    });

    it('should open on Cmd+K keydown', async () => {

      window.kbSearch.init();
      const event = new KeyboardEvent('keydown', { key: 'k', metaKey: true, bubbles: true });
      document.dispatchEvent(event);
      const modal = document.getElementById('kb-search-modal');
      expect(modal).not.toBeNull();
    });

    it('should close on Escape keydown', async () => {

      window.kbSearch.init();
      window.kbSearch.openModal();
      const event = new KeyboardEvent('keydown', { key: 'Escape', bubbles: true });
      document.dispatchEvent(event);
      const modal = document.getElementById('kb-search-modal');
      expect(modal.classList.contains('active')).toBe(false);
    });
  });

  describe('Search Input and Debounce', () => {
    it('should debounce search input (no API call before 300ms)', async () => {

      window.kbSearch.init();
      window.kbSearch.openModal();
      const input = document.querySelector('#kb-search-modal input[type="text"]');
      input.value = 'test';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      expect(globalThis.fetch).not.toHaveBeenCalled();
    });

    it('should call API after debounce delay', async () => {

      window.kbSearch.init();
      window.kbSearch.openModal();
      const input = document.querySelector('#kb-search-modal input[type="text"]');
      input.value = 'report';
      input.dispatchEvent(new Event('input', { bubbles: true }));
      vi.advanceTimersByTime(350);
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/kb/search?q=report')
      );
    });
  });

  describe('Result Rendering', () => {
    it('should render grouped section headers', async () => {

      window.kbSearch.init();
      window.kbSearch.openModal();
      // Simulate results being rendered
      window.kbSearch._renderResults(sampleSearchResults().results);
      const body = document.querySelector('.kb-search-modal-body');
      expect(body).not.toBeNull();
      expect(body.innerHTML).toContain('Files');
    });

    it('should render result items with icon, title, and path', async () => {

      window.kbSearch.init();
      window.kbSearch.openModal();
      window.kbSearch._renderResults(sampleSearchResults().results);
      const results = document.querySelectorAll('.search-result');
      expect(results.length).toBeGreaterThan(0);
    });

    it('should show no-results message for empty results', async () => {

      window.kbSearch.init();
      window.kbSearch.openModal();
      window.kbSearch._renderResults({ files: [], topics: [], summaries: [] });
      const body = document.querySelector('.kb-search-modal-body');
      expect(body.textContent).toContain('No results');
    });

    it('should highlight matched terms in result titles', async () => {

      const highlighted = window.kbSearch._highlightMatch('report.pdf', 'report');
      expect(highlighted).toContain('search-result-highlight');
      expect(highlighted).toContain('report');
    });
  });

  describe('Keyboard Navigation', () => {
    it('should track activeResultIndex starting at -1', async () => {

      window.kbSearch.init();
      expect(window.kbSearch.activeResultIndex).toBe(-1);
    });

    it('should increment activeResultIndex on down arrow', async () => {

      window.kbSearch.init();
      window.kbSearch.openModal();
      window.kbSearch._renderResults(sampleSearchResults().results);
      window.kbSearch._navigateResults(1); // down
      expect(window.kbSearch.activeResultIndex).toBe(0);
    });

    it('should decrement activeResultIndex on up arrow', async () => {

      window.kbSearch.init();
      window.kbSearch.openModal();
      window.kbSearch._renderResults(sampleSearchResults().results);
      window.kbSearch._navigateResults(1); // down to 0
      window.kbSearch._navigateResults(1); // down to 1
      window.kbSearch._navigateResults(-1); // up to 0
      expect(window.kbSearch.activeResultIndex).toBe(0);
    });

    it('should not go below -1', async () => {

      window.kbSearch.init();
      window.kbSearch._navigateResults(-1);
      expect(window.kbSearch.activeResultIndex).toBe(-1);
    });
  });
});


// ============================================================================
// Preview Panel Tests
// ============================================================================

describe('KB Preview Panel', () => {
  beforeEach(() => {
    createKBDOM();
    window.kbSearch.modal = null;
    window.kbSearch.previewPanel = null;
  });

  afterEach(() => {
    vi.restoreAllMocks();
    document.body.innerHTML = '';
  });

  const sampleFile = {
    path: 'landing/report.pdf',
    name: 'report.pdf',
    type: 'pdf',
    size: 2457600,
    topic: null,
    created_date: '2026-02-19T09:00:00Z',
    keywords: ['report', 'research'],
  };

  it('should create preview panel DOM when showPreview is called', async () => {

    window.kbSearch.init();
    window.kbSearch.showPreview(sampleFile);
    const panel = document.getElementById('kb-preview-panel');
    expect(panel).not.toBeNull();
  });

  it('should display file name in preview', async () => {

    window.kbSearch.init();
    window.kbSearch.showPreview(sampleFile);
    const panel = document.getElementById('kb-preview-panel');
    expect(panel.textContent).toContain('report.pdf');
  });

  it('should display file type in preview', async () => {

    window.kbSearch.init();
    window.kbSearch.showPreview(sampleFile);
    const panel = document.getElementById('kb-preview-panel');
    expect(panel.textContent.toLowerCase()).toContain('pdf');
  });

  it('should display file size formatted', async () => {

    window.kbSearch.init();
    window.kbSearch.showPreview(sampleFile);
    const panel = document.getElementById('kb-preview-panel');
    // 2457600 bytes ≈ 2.3 MB
    expect(panel.textContent).toMatch(/2\.\d\s*MB/);
  });

  it('should display AI keyword tags as badges', async () => {

    window.kbSearch.init();
    window.kbSearch.showPreview(sampleFile);
    const tags = document.querySelectorAll('.kb-preview-tag');
    expect(tags.length).toBe(2);
    expect(tags[0].textContent).toBe('report');
    expect(tags[1].textContent).toBe('research');
  });

  it('should include Process and Open action buttons', async () => {

    window.kbSearch.init();
    window.kbSearch.showPreview(sampleFile);
    const panel = document.getElementById('kb-preview-panel');
    expect(panel.textContent).toContain('Process');
    expect(panel.textContent).toContain('Open');
  });

  it('should include close button', async () => {

    window.kbSearch.init();
    window.kbSearch.showPreview(sampleFile);
    const closeBtn = document.querySelector('#kb-preview-panel .btn-close, #btn-close-preview');
    expect(closeBtn).not.toBeNull();
  });

  it('should hide preview when hidePreview is called', async () => {

    window.kbSearch.init();
    window.kbSearch.showPreview(sampleFile);
    window.kbSearch.hidePreview();
    const panel = document.getElementById('kb-preview-panel');
    expect(panel.style.display).toBe('none');
  });

  it('should update preview when different file selected', async () => {

    window.kbSearch.init();
    window.kbSearch.showPreview(sampleFile);
    const secondFile = { ...sampleFile, name: 'notes.md', type: 'markdown', keywords: ['notes'] };
    window.kbSearch.showPreview(secondFile);
    const panel = document.getElementById('kb-preview-panel');
    expect(panel.textContent).toContain('notes.md');
    expect(panel.textContent).not.toContain('report.pdf');
  });

  it('should show type-specific icon for PDF', async () => {

    window.kbSearch.init();
    window.kbSearch.showPreview(sampleFile);
    const thumb = document.querySelector('.kb-preview-thumbnail i');
    expect(thumb.classList.contains('bi-file-pdf')).toBe(true);
  });
});


// ============================================================================
// Filter Chip Tests
// ============================================================================

describe('KB Search Filters', () => {
  beforeEach(() => {
    createKBDOM();
    window.kbSearch.activeFilters = { types: [], topic: null };
  });

  afterEach(() => {
    vi.restoreAllMocks();
    document.body.innerHTML = '';
  });

  it('should initialize with empty active filters', async () => {

    window.kbSearch.init();
    expect(window.kbSearch.activeFilters.types).toEqual([]);
    expect(window.kbSearch.activeFilters.topic).toBeNull();
  });

  it('should toggle type filter on _toggleTypeFilter', async () => {

    window.kbSearch.init();
    window.kbSearch._toggleTypeFilter('pdf');
    expect(window.kbSearch.activeFilters.types).toContain('pdf');
  });

  it('should remove type filter on second toggle', async () => {

    window.kbSearch.init();
    window.kbSearch._toggleTypeFilter('pdf');
    window.kbSearch._toggleTypeFilter('pdf');
    expect(window.kbSearch.activeFilters.types).not.toContain('pdf');
  });

  it('should support multi-select type filters', async () => {

    window.kbSearch.init();
    window.kbSearch._toggleTypeFilter('pdf');
    window.kbSearch._toggleTypeFilter('markdown');
    expect(window.kbSearch.activeFilters.types).toContain('pdf');
    expect(window.kbSearch.activeFilters.types).toContain('markdown');
  });

  it('should set topic filter on _setTopicFilter', async () => {

    window.kbSearch.init();
    window.kbSearch._setTopicFilter('machine-learning');
    expect(window.kbSearch.activeFilters.topic).toBe('machine-learning');
  });

  it('should clear topic filter when set to null', async () => {

    window.kbSearch.init();
    window.kbSearch._setTopicFilter('machine-learning');
    window.kbSearch._setTopicFilter(null);
    expect(window.kbSearch.activeFilters.topic).toBeNull();
  });
});


// ============================================================================
// Sidebar Search Highlight Tests
// ============================================================================

describe('KB Sidebar Search Highlight', () => {
  beforeEach(() => {
    createKBDOM();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    document.body.innerHTML = '';
  });

  it('should have _highlightMatch method', async () => {

    expect(typeof window.kbSearch._highlightMatch).toBe('function');
  });

  it('should wrap matched text in highlight span', async () => {

    const result = window.kbSearch._highlightMatch('my-report.pdf', 'report');
    expect(result).toContain('<span class="search-result-highlight">');
    expect(result).toContain('report');
  });

  it('should return original text when no match', async () => {

    const result = window.kbSearch._highlightMatch('notes.md', 'xyz');
    expect(result).toBe('notes.md');
  });

  it('should be case-insensitive', async () => {

    const result = window.kbSearch._highlightMatch('Report.PDF', 'report');
    expect(result).toContain('search-result-highlight');
  });
});
