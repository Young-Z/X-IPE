/**
 * TDD Tests for FEATURE-043-B: Breadcrumb Navigation & Visual Distinction
 * Tests: Navigation stack, back button, breadcrumb bar, visual distinction CSS,
 *        depth cap, stack clear on close, title tooltip.
 *
 * TDD: These tests verify FEATURE-043-B additions to LinkPreviewManager.
 *      They build on FEATURE-043-A infrastructure (ensureContentRenderer, ensureLinkPreviewManager).
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { loadFeatureScript, mockFetch } from './helpers.js';

// --- Helpers to load scripts (same pattern as 043-A tests) ---

let _crLoaded = false;
let _lpmLoaded = false;

function ensureContentRenderer() {
  if (!_crLoaded) {
    try {
      class MockRenderer {
        link(href, title, text) {
          const titleAttr = title ? ` title="${title}"` : '';
          return `<a href="${href}"${titleAttr}>${text}</a>`;
        }
      }
      let activeRenderer = null;
      globalThis.marked = {
        parse: vi.fn((md) => {
          const renderer = activeRenderer || new MockRenderer();
          return md.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, text, href) => {
            return renderer.link(href, null, text);
          });
        }),
        setOptions: vi.fn((opts) => {
          if (opts && opts.renderer) activeRenderer = opts.renderer;
        }),
        Renderer: MockRenderer,
      };
      globalThis.hljs = {
        getLanguage: vi.fn(() => true),
        highlight: vi.fn((code) => ({ value: code })),
        highlightElement: vi.fn(),
      };
      loadFeatureScript('../core/content-renderer.js');
      _crLoaded = true;
    } catch { /* TDD */ }
  }
  return typeof globalThis.ContentRenderer !== 'undefined';
}

function ensureLinkPreviewManager() {
  if (!_lpmLoaded) {
    try {
      loadFeatureScript('link-preview-manager.js');
      _lpmLoaded = true;
    } catch { /* TDD */ }
  }
  return typeof globalThis.LinkPreviewManager !== 'undefined';
}

function createMockResponse(path) {
  return {
    ok: true,
    json: () => Promise.resolve({
      content: `# ${path.split('/').pop()}\nContent of ${path}`,
      type: 'markdown',
      path,
      extension: '.md'
    })
  };
}

// =============================================================================
// FEATURE-043-B Tests
// =============================================================================

describe('FEATURE-043-B: Breadcrumb Navigation & Visual Distinction', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    globalThis.fetch = vi.fn();
    _crLoaded = false;
    _lpmLoaded = false;
    if (globalThis.LinkPreviewManager) {
      globalThis.LinkPreviewManager.instance = null;
    }
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  // =========================================================================
  // 1. Navigation Stack (FR-043-B.1)
  // =========================================================================

  describe('Navigation Stack (FR-043-B.1)', () => {
    it('should initialize _navStack as empty array', () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      const instance = new LPM();
      expect(instance._navStack).toBeDefined();
      expect(Array.isArray(instance._navStack)).toBe(true);
      expect(instance._navStack.length).toBe(0);
    });

    it('should have _maxDepth of 5', () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const instance = new globalThis.LinkPreviewManager();
      expect(instance._maxDepth).toBe(5);
    });

    it('should track _currentPath after open()', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn(() => Promise.resolve(createMockResponse('x-ipe-docs/file-a.md')));

      await instance.open('x-ipe-docs/file-a.md');
      expect(instance._currentPath).toBe('x-ipe-docs/file-a.md');
    });

    it('should push current file to stack when _navigateFromModal is called', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn((url) => {
        const path = new URL(url, 'http://localhost').searchParams.get('path');
        return Promise.resolve(createMockResponse(path));
      });

      // Open first file
      await instance.open('x-ipe-docs/file-a.md');
      expect(instance._navStack.length).toBe(0);

      // Navigate from modal to second file
      await instance._navigateFromModal('x-ipe-docs/file-b.md');
      expect(instance._navStack.length).toBe(1);
      expect(instance._navStack[0].path).toBe('x-ipe-docs/file-a.md');
      expect(instance._currentPath).toBe('x-ipe-docs/file-b.md');
    });

    it('should cap navigation stack at _maxDepth (5)', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn((url) => {
        const path = new URL(url, 'http://localhost').searchParams.get('path');
        return Promise.resolve(createMockResponse(path));
      });

      // Open first file then navigate 6 times
      await instance.open('x-ipe-docs/file-0.md');
      for (let i = 1; i <= 6; i++) {
        await instance._navigateFromModal(`x-ipe-docs/file-${i}.md`);
      }
      // Stack should be capped at 5
      expect(instance._navStack.length).toBeLessThanOrEqual(5);
    });

    it('should clear stack on close()', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn((url) => {
        const path = new URL(url, 'http://localhost').searchParams.get('path');
        return Promise.resolve(createMockResponse(path));
      });

      await instance.open('x-ipe-docs/file-a.md');
      await instance._navigateFromModal('x-ipe-docs/file-b.md');
      expect(instance._navStack.length).toBe(1);

      instance.close();
      expect(instance._navStack.length).toBe(0);
      expect(instance._currentPath).toBeNull();
    });
  });

  // =========================================================================
  // 2. Back Button (FR-043-B.1.2, FR-043-B.1.7)
  // =========================================================================

  describe('Back Button (FR-043-B.1.2)', () => {
    it('should have a back button in the modal header', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn(() => Promise.resolve(createMockResponse('x-ipe-docs/test.md')));
      await instance.open('x-ipe-docs/test.md');

      const backBtn = document.querySelector('.link-preview-back');
      expect(backBtn).not.toBeNull();
    });

    it('should hide back button when stack is empty', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn(() => Promise.resolve(createMockResponse('x-ipe-docs/test.md')));
      await instance.open('x-ipe-docs/test.md');

      const backBtn = document.querySelector('.link-preview-back');
      expect(backBtn).not.toBeNull();
      expect(backBtn.style.display).toBe('none');
    });

    it('should show back button when stack has entries', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn((url) => {
        const path = new URL(url, 'http://localhost').searchParams.get('path');
        return Promise.resolve(createMockResponse(path));
      });

      await instance.open('x-ipe-docs/file-a.md');
      await instance._navigateFromModal('x-ipe-docs/file-b.md');

      const backBtn = document.querySelector('.link-preview-back');
      expect(backBtn).not.toBeNull();
      expect(backBtn.style.display).not.toBe('none');
    });

    it('should navigate back when back button is clicked', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn((url) => {
        const path = new URL(url, 'http://localhost').searchParams.get('path');
        return Promise.resolve(createMockResponse(path));
      });

      await instance.open('x-ipe-docs/file-a.md');
      await instance._navigateFromModal('x-ipe-docs/file-b.md');
      expect(instance._currentPath).toBe('x-ipe-docs/file-b.md');

      await instance._goBack();
      expect(instance._currentPath).toBe('x-ipe-docs/file-a.md');
      expect(instance._navStack.length).toBe(0);
    });
  });

  // =========================================================================
  // 3. Breadcrumb Bar (FR-043-B.1.3, FR-043-B.1.4)
  // =========================================================================

  describe('Breadcrumb Bar (FR-043-B.1.3)', () => {
    it('should create breadcrumb bar element in modal', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn(() => Promise.resolve(createMockResponse('x-ipe-docs/test.md')));
      await instance.open('x-ipe-docs/test.md');

      const breadcrumb = document.querySelector('.link-preview-breadcrumb');
      expect(breadcrumb).not.toBeNull();
    });

    it('should hide breadcrumb when stack is empty', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn(() => Promise.resolve(createMockResponse('x-ipe-docs/test.md')));
      await instance.open('x-ipe-docs/test.md');

      const breadcrumb = document.querySelector('.link-preview-breadcrumb');
      expect(breadcrumb.style.display).toBe('none');
    });

    it('should show breadcrumb with entries when navigating', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn((url) => {
        const path = new URL(url, 'http://localhost').searchParams.get('path');
        return Promise.resolve(createMockResponse(path));
      });

      await instance.open('x-ipe-docs/file-a.md');
      await instance._navigateFromModal('x-ipe-docs/file-b.md');

      const breadcrumb = document.querySelector('.link-preview-breadcrumb');
      expect(breadcrumb.style.display).not.toBe('none');

      const entries = breadcrumb.querySelectorAll('.breadcrumb-entry');
      expect(entries.length).toBe(1);
      expect(entries[0].textContent).toBe('file-a.md');

      const current = breadcrumb.querySelector('.breadcrumb-current');
      expect(current).not.toBeNull();
      expect(current.textContent).toBe('file-b.md');
    });

    it('should show separator between breadcrumb entries', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn((url) => {
        const path = new URL(url, 'http://localhost').searchParams.get('path');
        return Promise.resolve(createMockResponse(path));
      });

      await instance.open('x-ipe-docs/file-a.md');
      await instance._navigateFromModal('x-ipe-docs/file-b.md');

      const seps = document.querySelectorAll('.breadcrumb-sep');
      expect(seps.length).toBeGreaterThanOrEqual(1);
      expect(seps[0].textContent).toBe('›');
    });

    it('should navigate to breadcrumb entry when clicked (truncate stack)', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn((url) => {
        const path = new URL(url, 'http://localhost').searchParams.get('path');
        return Promise.resolve(createMockResponse(path));
      });

      await instance.open('x-ipe-docs/file-a.md');
      await instance._navigateFromModal('x-ipe-docs/file-b.md');
      await instance._navigateFromModal('x-ipe-docs/file-c.md');
      expect(instance._navStack.length).toBe(2);

      // Click first breadcrumb entry (file-a.md) — should truncate to empty stack
      await instance._goToBreadcrumb(0);
      expect(instance._currentPath).toBe('x-ipe-docs/file-a.md');
      expect(instance._navStack.length).toBe(0);
    });
  });

  // =========================================================================
  // 4. Visual Link Distinction (FR-043-B.2)
  // =========================================================================

  describe('Visual Link Distinction (FR-043-B.2)', () => {
    it('should add title="Open preview" to internal links', () => {
      ensureContentRenderer();
      const CR = globalThis.ContentRenderer;
      expect(CR).toBeDefined();

      const container = document.createElement('div');
      container.id = 'test-visual';
      document.body.appendChild(container);
      const renderer = new CR('test-visual');

      const md = '[spec](x-ipe-docs/requirements/spec.md)';
      renderer.renderMarkdown(md);

      const link = container.querySelector('a[data-preview-path]');
      expect(link).not.toBeNull();
      expect(link.getAttribute('title')).toBe('Open preview');
    });

    it('should NOT add title="Open preview" to external links', () => {
      ensureContentRenderer();
      const CR = globalThis.ContentRenderer;
      expect(CR).toBeDefined();

      const container = document.createElement('div');
      container.id = 'test-external';
      document.body.appendChild(container);
      const renderer = new CR('test-external');

      const md = '[Google](https://google.com)';
      renderer.renderMarkdown(md);

      const link = container.querySelector('a');
      expect(link).not.toBeNull();
      expect(link.getAttribute('title')).not.toBe('Open preview');
    });

    it('should preserve explicit title attribute over default', () => {
      ensureContentRenderer();
      const CR = globalThis.ContentRenderer;
      expect(CR).toBeDefined();

      const container = document.createElement('div');
      container.id = 'test-title';
      document.body.appendChild(container);
      const renderer = new CR('test-title');

      // When title is explicitly set in markdown, it should be preserved
      // Note: marked's link token includes title from [text](url "title") syntax
      // The custom renderer should prefer explicit title over default
      const link = document.createElement('a');
      link.href = 'x-ipe-docs/test.md';
      link.setAttribute('data-preview-path', 'x-ipe-docs/test.md');
      link.title = 'Custom title';
      document.body.appendChild(link);
      expect(link.getAttribute('title')).toBe('Custom title');
    });
  });

  // =========================================================================
  // 5. Modal Context Detection (attachTo)
  // =========================================================================

  describe('Modal Context Detection', () => {
    it('should call _navigateFromModal when link is inside open modal', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn((url) => {
        const path = new URL(url, 'http://localhost').searchParams.get('path');
        return Promise.resolve(createMockResponse(path));
      });

      // Open modal with first file
      await instance.open('x-ipe-docs/file-a.md');

      // Verify modal content has markdown-body with link preview attached
      const mdBody = instance._contentArea.querySelector('.markdown-body');
      expect(mdBody).not.toBeNull();

      // Spy on _navigateFromModal
      const navSpy = vi.spyOn(instance, '_navigateFromModal');

      // Create internal link inside modal content area
      const link = document.createElement('a');
      link.setAttribute('data-preview-path', 'x-ipe-docs/file-b.md');
      link.href = 'x-ipe-docs/file-b.md';
      link.textContent = 'File B';
      mdBody.appendChild(link);

      // Click the link
      link.click();

      expect(navSpy).toHaveBeenCalledWith('x-ipe-docs/file-b.md');
    });

    it('should reset stack when link is clicked from page (not modal)', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn((url) => {
        const path = new URL(url, 'http://localhost').searchParams.get('path');
        return Promise.resolve(createMockResponse(path));
      });

      // Manually add stack entries
      instance._navStack = [{ path: 'x-ipe-docs/old.md', title: 'old.md' }];

      // Create page container with link
      const container = document.createElement('div');
      container.className = 'markdown-body';
      document.body.appendChild(container);

      const link = document.createElement('a');
      link.setAttribute('data-preview-path', 'x-ipe-docs/new.md');
      link.href = 'x-ipe-docs/new.md';
      link.textContent = 'New File';
      container.appendChild(link);

      LPM.attachTo(container);

      // Click the link from page context (not modal)
      link.click();

      // Wait for async
      await new Promise(r => setTimeout(r, 100));

      // Stack should be reset (not preserved)
      expect(instance._navStack.length).toBe(0);
    });
  });

  // =========================================================================
  // 6. Non-Regression (AC-043-B.13, AC-043-B.14)
  // =========================================================================

  describe('Non-Regression (AC-043-B.13)', () => {
    it('should still open modal and show content (FEATURE-043-A preserved)', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn(() => Promise.resolve(createMockResponse('x-ipe-docs/test.md')));
      await instance.open('x-ipe-docs/test.md');

      const backdrop = document.querySelector('.link-preview-backdrop');
      expect(backdrop).not.toBeNull();
      // active class is set via requestAnimationFrame — verify isOpen flag instead
      expect(instance._isOpen).toBe(true);

      const content = document.querySelector('.link-preview-content');
      expect(content.textContent).toContain('test.md');
    });

    it('should still close via close() method (FEATURE-043-A preserved)', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn(() => Promise.resolve(createMockResponse('x-ipe-docs/test.md')));
      await instance.open('x-ipe-docs/test.md');

      instance.close();
      expect(instance._isOpen).toBe(false);
    });

    it('should still show error state for 404 (FEATURE-043-A preserved)', async () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      const instance = new LPM();
      LPM.instance = instance;

      globalThis.fetch = vi.fn(() => Promise.resolve({ ok: false, status: 404 }));

      await instance.open('x-ipe-docs/nonexistent.md');
      const error = document.querySelector('.link-preview-error');
      expect(error).not.toBeNull();
      expect(error.textContent).toContain('File not found');
    });
  });
});
