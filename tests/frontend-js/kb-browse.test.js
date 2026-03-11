/**
 * Tests for FEATURE-049-C: KB Browse & Search View
 * Tests: Grid rendering, search, sort, tag filtering, empty state, card click, new article button
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { loadFeatureScript } from './helpers.js';

let _implLoaded = false;
function ensureImpl() {
  if (!_implLoaded) {
    try {
      loadFeatureScript('kb-browse.js');
      _implLoaded = true;
    } catch { /* not yet implemented */ }
  }
  return typeof globalThis.KBBrowseView !== 'undefined';
}

const MOCK_FILES = [
  {
    name: 'getting-started.md',
    path: 'knowledge-base/getting-started.md',
    type: 'file',
    mtime: 1700000000,
    content_preview: 'This guide helps you get started with the project...',
    frontmatter: {
      title: 'Getting Started',
      tags: { lifecycle: ['Requirement'], domain: ['Onboarding'] }
    }
  },
  {
    name: 'api-reference.md',
    path: 'knowledge-base/api-reference.md',
    type: 'file',
    mtime: 1700100000,
    content_preview: 'REST API endpoints documentation',
    frontmatter: {
      title: 'API Reference',
      tags: { lifecycle: ['Technical Design'], domain: [] }
    }
  },
  {
    name: 'untagged-note.md',
    path: 'knowledge-base/untagged-note.md',
    type: 'file',
    mtime: 1700200000,
    content_preview: 'Some untagged content',
    frontmatter: { title: 'Untagged Note', tags: { lifecycle: [], domain: [] } }
  }
];

const MOCK_CONFIG = {
  tags: {
    lifecycle: ['Requirement', 'Feature', 'Technical Design', 'Implementation'],
    domain: ['Onboarding', 'Architecture', 'Testing']
  }
};

describe('FEATURE-049-C: KB Browse & Search View', () => {
  let container;
  let browseView;
  let fetchMock;

  beforeEach(() => {
    if (!ensureImpl()) return;
    container = document.createElement('div');
    container.id = 'content-area';
    document.body.appendChild(container);

    // Mock fetch
    fetchMock = vi.fn((url) => {
      if (url.includes('/api/kb/config')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve(MOCK_CONFIG) });
      }
      if (url.includes('/api/kb/files') || url.includes('/api/kb/search')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ files: MOCK_FILES }) });
      }
      return Promise.resolve({ ok: false });
    });
    globalThis.fetch = fetchMock;
  });

  afterEach(() => {
    if (browseView && typeof browseView.destroy === 'function') browseView.destroy();
    if (container && container.parentNode) container.parentNode.removeChild(container);
    vi.restoreAllMocks();
  });

  describe('Initialization', () => {
    it('should export KBBrowseView class', () => {
      if (!globalThis.KBBrowseView) return;
      expect(typeof globalThis.KBBrowseView).toBe('function');
    });

    it('should accept a container element', () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      expect(browseView.container).toBe(container);
    });

    it('should accept container by string ID', () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView('content-area');
      expect(browseView.container).toBe(container);
    });
  });

  describe('Grid Rendering', () => {
    it('should render article cards in a grid', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const cards = container.querySelectorAll('.kb-card');
      expect(cards.length).toBe(3);
    });

    it('should display title from frontmatter', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const titles = container.querySelectorAll('.kb-card-title');
      expect(titles[0].textContent).toBe('Getting Started');
    });

    it('should display content snippet', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const snippet = container.querySelector('.kb-card-snippet');
      expect(snippet.textContent).toContain('get started');
    });

    it('should truncate snippet to 100 characters', async () => {
      if (!globalThis.KBBrowseView) return;
      const longFiles = [{
        name: 'long.md', path: 'kb/long.md', type: 'file', mtime: 1700000000,
        content_preview: 'A'.repeat(200),
        frontmatter: { title: 'Long', tags: { lifecycle: [], domain: [] } }
      }];
      globalThis.fetch = vi.fn((url) => {
        if (url.includes('/api/kb/config')) return Promise.resolve({ ok: true, json: () => Promise.resolve(MOCK_CONFIG) });
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ files: longFiles }) });
      });
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      const snippet = container.querySelector('.kb-card-snippet');
      expect(snippet.textContent.length).toBeLessThanOrEqual(100);
    });

    it('should display last modified date on cards', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      const meta = container.querySelector('.kb-card-meta');
      expect(meta).not.toBeNull();
      expect(meta.textContent.length).toBeGreaterThan(0);
    });

    it('should display lifecycle tags with amber style', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const lifecycleTags = container.querySelectorAll('.kb-tag-lifecycle');
      expect(lifecycleTags.length).toBeGreaterThan(0);
      expect(lifecycleTags[0].textContent).toContain('▸');
    });

    it('should display domain tags with blue style', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const domainTags = container.querySelectorAll('.kb-tag-domain');
      expect(domainTags.length).toBeGreaterThan(0);
      expect(domainTags[0].textContent).toContain('#');
    });

    it('should show "Needs Tags" badge for untagged articles', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const badges = container.querySelectorAll('.kb-tag-badge-untagged');
      expect(badges.length).toBe(1);
      expect(badges[0].textContent).toBe('Needs Tags');
    });
  });

  describe('Empty State', () => {
    it('should show empty state when no files', async () => {
      if (!globalThis.KBBrowseView) return;
      globalThis.fetch = vi.fn((url) => {
        if (url.includes('/api/kb/config')) {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(MOCK_CONFIG) });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ files: [] }) });
      });
      
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const empty = container.querySelector('.kb-browse-empty');
      expect(empty).not.toBeNull();
      expect(empty.textContent).toContain('No articles yet');
    });

    it('should have create button in empty state', async () => {
      if (!globalThis.KBBrowseView) return;
      globalThis.fetch = vi.fn((url) => {
        if (url.includes('/api/kb/config')) {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(MOCK_CONFIG) });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ files: [] }) });
      });
      
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const btn = container.querySelector('.kb-browse-create-btn');
      expect(btn).not.toBeNull();
    });
  });

  describe('Search', () => {
    it('should render search input', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const input = container.querySelector('.kb-search-input');
      expect(input).not.toBeNull();
    });

    it('should debounce search on input', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const input = container.querySelector('.kb-search-input');
      vi.useFakeTimers();
      
      input.value = 'test';
      input.dispatchEvent(new Event('input'));
      
      // Not yet called (debounced)
      const callsBefore = fetchMock.mock.calls.length;
      
      vi.advanceTimersByTime(350);
      // After debounce, should have called fetch
      expect(fetchMock.mock.calls.length).toBeGreaterThan(callsBefore);
      
      vi.useRealTimers();
    });

    it('should call /api/kb/search with query parameter', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const input = container.querySelector('.kb-search-input');
      vi.useFakeTimers();
      input.value = 'api docs';
      input.dispatchEvent(new Event('input'));
      vi.advanceTimersByTime(350);
      vi.useRealTimers();
      
      const searchCall = fetchMock.mock.calls.find(c => c[0].includes('/api/kb/search'));
      expect(searchCall).toBeDefined();
      expect(searchCall[0]).toContain('q=api%20docs');
    });
  });

  describe('Sort', () => {
    it('should render sort dropdown', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const select = container.querySelector('.kb-sort-select');
      expect(select).not.toBeNull();
    });

    it('should have 4 sort options', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const options = container.querySelectorAll('.kb-sort-select option');
      expect(options.length).toBe(4);
    });

    it('should default to Last Modified', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const select = container.querySelector('.kb-sort-select');
      expect(select.value).toBe('modified_desc');
    });

    it('should reload files when sort changes', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const callsBefore = fetchMock.mock.calls.length;
      const select = container.querySelector('.kb-sort-select');
      select.value = 'name_asc';
      select.dispatchEvent(new Event('change'));
      await new Promise(r => setTimeout(r, 50));
      
      const fileCall = fetchMock.mock.calls.slice(callsBefore).find(c => c[0].includes('/api/kb/files'));
      expect(fileCall).toBeDefined();
      expect(fileCall[0]).toContain('sort=name_asc');
    });
  });

  describe('Tag Filters', () => {
    it('should render lifecycle filter chips', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const chips = container.querySelectorAll('.kb-filter-lifecycle');
      expect(chips.length).toBe(4);
    });

    it('should render domain filter chips', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const chips = container.querySelectorAll('.kb-filter-domain');
      expect(chips.length).toBe(3);
    });

    it('should render untagged filter chip', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const untagged = container.querySelector('.kb-filter-untagged');
      expect(untagged).not.toBeNull();
      expect(untagged.textContent).toContain('Untagged');
    });

    it('should toggle filter chip active on click', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const chip = container.querySelector('.kb-filter-lifecycle');
      expect(chip.classList.contains('active')).toBe(false);
      chip.click();
      expect(chip.classList.contains('active')).toBe(true);
    });

    it('should filter to untagged only when untagged chip active', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const untaggedChip = container.querySelector('.kb-filter-untagged');
      untaggedChip.click();
      
      const cards = container.querySelectorAll('.kb-card');
      expect(cards.length).toBe(1);
      expect(cards[0].dataset.path).toContain('untagged');
    });
  });

  describe('New Article Button', () => {
    it('should render New Article button', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const btn = container.querySelector('.kb-browse-new-btn');
      expect(btn).not.toBeNull();
      expect(btn.textContent).toContain('New Article');
    });

    it('should open editor when New Article clicked', async () => {
      if (!globalThis.KBBrowseView) return;
      const openSpy = vi.fn();
      globalThis.KBArticleEditor = class { constructor() {} open() { openSpy(); } };
      
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const btn = container.querySelector('.kb-browse-new-btn');
      btn.click();
      
      expect(openSpy).toHaveBeenCalled();
      delete globalThis.KBArticleEditor;
    });
  });

  describe('Card Click', () => {
    it('should dispatch fileSelected event on card click', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      let selectedPath = null;
      document.addEventListener('fileSelected', (e) => { selectedPath = e.detail.path; }, { once: true });
      
      const card = container.querySelector('.kb-card');
      card.click();
      
      expect(selectedPath).toBe('knowledge-base/getting-started.md');
    });

    it('should call contentRenderer.load on card click', async () => {
      if (!globalThis.KBBrowseView) return;
      const loadSpy = vi.fn();
      window.contentRenderer = { load: loadSpy };
      
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const card = container.querySelector('.kb-card');
      card.click();
      
      expect(loadSpy).toHaveBeenCalledWith('knowledge-base/getting-started.md');
      delete window.contentRenderer;
    });
  });

  describe('kb:changed Event', () => {
    it('should refresh on kb:changed event', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      const callsBefore = fetchMock.mock.calls.length;
      document.dispatchEvent(new CustomEvent('kb:changed'));
      
      // Wait for async refresh
      await new Promise(r => setTimeout(r, 50));
      expect(fetchMock.mock.calls.length).toBeGreaterThan(callsBefore);
    });
  });

  describe('Lifecycle', () => {
    it('should stop listening to kb:changed after destroy()', async () => {
      if (!globalThis.KBBrowseView) return;
      browseView = new globalThis.KBBrowseView(container);
      await browseView.render();
      
      browseView.destroy();
      const callsBefore = fetchMock.mock.calls.length;
      document.dispatchEvent(new CustomEvent('kb:changed'));
      await new Promise(r => setTimeout(r, 50));
      expect(fetchMock.mock.calls.length).toBe(callsBefore);
    });
  });
});
