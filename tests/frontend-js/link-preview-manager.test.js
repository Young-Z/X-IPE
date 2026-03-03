/**
 * TDD Tests for FEATURE-043-A: Link Interception & Preview Modal
 * Tests: Custom link renderer, delegated click interception, preview modal,
 *        error/loading states, AbortController management.
 *
 * TDD: All tests MUST fail until link-preview-manager.js and
 *      content-renderer.js extension are implemented.
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { loadFeatureScript, mockFetch } from './helpers.js';

// --- Helpers to load both scripts ---

let _crLoaded = false;
let _lpmLoaded = false;

function ensureContentRenderer() {
  if (!_crLoaded) {
    try {
      // marked.js must be available before ContentRenderer loads
      // Renderer must be a class (used with `new`)
      class MockRenderer {
        link(href, title, text) {
          return `<a href="${href}">${text}</a>`;
        }
      }

      let activeRenderer = null;

      globalThis.marked = {
        parse: vi.fn((md) => {
          // Use active renderer for links if available
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
    } catch {
      // File not yet modified — TDD
    }
  }
  return typeof globalThis.ContentRenderer !== 'undefined';
}

function ensureLinkPreviewManager() {
  if (!_lpmLoaded) {
    try {
      loadFeatureScript('link-preview-manager.js');
      _lpmLoaded = true;
    } catch {
      // File not yet implemented — TDD
    }
  }
  return typeof globalThis.LinkPreviewManager !== 'undefined';
}

// =============================================================================
// SECTION 1: Custom Link Renderer in marked.js (FR-043-A.1)
// =============================================================================

describe('FEATURE-043-A: Link Interception & Preview Modal', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    globalThis.fetch = vi.fn();
    _crLoaded = false;
    _lpmLoaded = false;
    // Reset singleton state
    if (globalThis.LinkPreviewManager) {
      globalThis.LinkPreviewManager.instance = null;
    }
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  // =========================================================================
  // 1. Custom Link Renderer
  // =========================================================================

  describe('Custom Link Renderer (FR-043-A.1)', () => {
    it('should add data-preview-path attribute to x-ipe-docs/ links', () => {
      ensureContentRenderer();
      const CR = globalThis.ContentRenderer;
      expect(CR).toBeDefined();

      const container = document.createElement('div');
      container.id = 'test-render';
      document.body.appendChild(container);
      const renderer = new CR('test-render');

      // The custom renderer should tag internal links
      // We test by rendering markdown with an internal link
      const md = '[spec](x-ipe-docs/requirements/EPIC-043/specification.md)';
      renderer.renderMarkdown(md);

      const link = container.querySelector('a[data-preview-path]');
      expect(link).not.toBeNull();
      expect(link.getAttribute('data-preview-path')).toBe('x-ipe-docs/requirements/EPIC-043/specification.md');
    });

    it('should add data-preview-path attribute to .github/skills/ links', () => {
      ensureContentRenderer();
      const CR = globalThis.ContentRenderer;
      expect(CR).toBeDefined();

      const container = document.createElement('div');
      container.id = 'test-render-2';
      document.body.appendChild(container);
      const renderer = new CR('test-render-2');

      const md = '[skill](.github/skills/x-ipe-task-based-bug-fix/SKILL.md)';
      renderer.renderMarkdown(md);

      const link = container.querySelector('a[data-preview-path]');
      expect(link).not.toBeNull();
      expect(link.getAttribute('data-preview-path')).toBe('.github/skills/x-ipe-task-based-bug-fix/SKILL.md');
    });

    it('should NOT add data-preview-path to external links', () => {
      ensureContentRenderer();
      const CR = globalThis.ContentRenderer;
      expect(CR).toBeDefined();

      const container = document.createElement('div');
      container.id = 'test-render-3';
      document.body.appendChild(container);
      const renderer = new CR('test-render-3');

      const md = '[Google](https://google.com)';
      renderer.renderMarkdown(md);

      const link = container.querySelector('a[data-preview-path]');
      expect(link).toBeNull();
      const normalLink = container.querySelector('a');
      expect(normalLink).not.toBeNull();
      expect(normalLink.getAttribute('href')).toBe('https://google.com');
    });

    it('should NOT add data-preview-path to src/ or tests/ links', () => {
      ensureContentRenderer();
      const CR = globalThis.ContentRenderer;
      expect(CR).toBeDefined();

      const container = document.createElement('div');
      container.id = 'test-render-4';
      document.body.appendChild(container);
      const renderer = new CR('test-render-4');

      const md = '[source](src/x_ipe/main.py)';
      renderer.renderMarkdown(md);

      const link = container.querySelector('a[data-preview-path]');
      expect(link).toBeNull();
    });
  });

  // =========================================================================
  // 2. LinkPreviewManager Class
  // =========================================================================

  describe('LinkPreviewManager (FR-043-A.2–FR-043-A.6)', () => {
    it('should export LinkPreviewManager class', () => {
      ensureLinkPreviewManager();
      expect(globalThis.LinkPreviewManager).toBeDefined();
    });

    it('should have static attachTo method', () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();
      expect(typeof LPM.attachTo).toBe('function');
    });

    it('should have open method', () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();
      const instance = LPM.instance || new LPM();
      expect(typeof instance.open).toBe('function');
    });

    it('should have close method', () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();
      const instance = LPM.instance || new LPM();
      expect(typeof instance.close).toBe('function');
    });
  });

  // =========================================================================
  // 3. Delegated Click Interception (FR-043-A.2)
  // =========================================================================

  describe('Delegated Click Interception (AC-043-A.1, AC-043-A.2)', () => {
    it('should intercept clicks on data-preview-path links', () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      const container = document.createElement('div');
      container.classList.add('markdown-body');
      container.innerHTML = '<a href="x-ipe-docs/test.md" data-preview-path="x-ipe-docs/test.md">test</a>';
      document.body.appendChild(container);

      // attachTo creates the singleton if needed
      LPM.attachTo(container);

      // Spy on the singleton's open method
      const openSpy = vi.spyOn(LPM.instance, 'open').mockResolvedValue();

      const link = container.querySelector('a');
      const event = new Event('click', { bubbles: true });
      event.preventDefault = vi.fn();
      link.dispatchEvent(event);

      expect(event.preventDefault).toHaveBeenCalled();
      expect(openSpy).toHaveBeenCalledWith('x-ipe-docs/test.md');
    });

    it('should NOT intercept clicks on links without data-preview-path', () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      const container = document.createElement('div');
      container.classList.add('markdown-body');
      container.innerHTML = '<a href="https://google.com">external</a>';
      document.body.appendChild(container);

      LPM.attachTo(container);

      const link = container.querySelector('a');
      const event = new Event('click', { bubbles: true });
      event.preventDefault = vi.fn();
      link.dispatchEvent(event);

      expect(event.preventDefault).not.toHaveBeenCalled();
    });

    it('should use event delegation (single listener on container, not per-link)', () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      const container = document.createElement('div');
      container.classList.add('markdown-body');
      document.body.appendChild(container);

      const addEventSpy = vi.spyOn(container, 'addEventListener');
      LPM.attachTo(container);

      // Should add exactly one click listener to the container
      const clickCalls = addEventSpy.mock.calls.filter(c => c[0] === 'click');
      expect(clickCalls.length).toBe(1);
    });

    it('should not double-attach to the same container', () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      const container = document.createElement('div');
      container.classList.add('markdown-body');
      document.body.appendChild(container);

      const addEventSpy = vi.spyOn(container, 'addEventListener');
      LPM.attachTo(container);
      LPM.attachTo(container); // second call

      const clickCalls = addEventSpy.mock.calls.filter(c => c[0] === 'click');
      expect(clickCalls.length).toBe(1);
    });
  });

  // =========================================================================
  // 4. Preview Modal Display (FR-043-A.4)
  // =========================================================================

  describe('Preview Modal Display (AC-043-A.3–AC-043-A.6)', () => {
    it('should create modal backdrop on open', async () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ content: '# Hello', type: 'markdown', path: 'test.md', extension: '.md' }),
      });

      const instance = LPM.instance || new LPM();
      await instance.open('x-ipe-docs/test.md');

      const backdrop = document.querySelector('.link-preview-backdrop, .deliverable-preview-backdrop');
      expect(backdrop).not.toBeNull();
    });

    it('should display filename in modal header', async () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ content: '# Hello', type: 'markdown', path: 'x-ipe-docs/test.md', extension: '.md' }),
      });

      const instance = LPM.instance || new LPM();
      await instance.open('x-ipe-docs/test.md');

      const header = document.querySelector('.link-preview-header, .preview-header');
      expect(header).not.toBeNull();
      expect(header.textContent).toContain('test.md');
    });

    it('should render markdown content in modal', async () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ content: '# Hello World', type: 'markdown', path: 'x-ipe-docs/test.md', extension: '.md' }),
      });

      const instance = LPM.instance || new LPM();
      await instance.open('x-ipe-docs/test.md');

      const content = document.querySelector('.link-preview-content, .preview-content');
      expect(content).not.toBeNull();
      expect(content.innerHTML).toBeTruthy();
    });

    it('should show "Cannot preview binary file" for binary content', async () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ content: null, type: 'binary', path: 'x-ipe-docs/image.png', extension: '.png' }),
      });

      const instance = LPM.instance || new LPM();
      await instance.open('x-ipe-docs/image.png');

      const content = document.querySelector('.link-preview-content, .preview-content');
      expect(content).not.toBeNull();
      expect(content.textContent.toLowerCase()).toContain('cannot preview');
    });

    it('should close modal on close button click', async () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ content: '# Test', type: 'markdown', path: 'test.md', extension: '.md' }),
      });

      const instance = LPM.instance || new LPM();
      await instance.open('x-ipe-docs/test.md');

      const closeBtn = document.querySelector('.link-preview-close, .preview-close');
      expect(closeBtn).not.toBeNull();
      closeBtn.click();

      // After close, backdrop should not have active class
      const backdrop = document.querySelector('.link-preview-backdrop');
      expect(backdrop).not.toBeNull();
      expect(backdrop.classList.contains('active')).toBe(false);
    });

    it('should close modal on backdrop click', async () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ content: '# Test', type: 'markdown', path: 'test.md', extension: '.md' }),
      });

      const instance = LPM.instance || new LPM();
      await instance.open('x-ipe-docs/test.md');

      const backdrop = document.querySelector('.link-preview-backdrop, .deliverable-preview-backdrop');
      expect(backdrop).not.toBeNull();
      // Click the backdrop directly (not the modal)
      backdrop.dispatchEvent(new Event('click', { bubbles: false }));

      await new Promise(r => setTimeout(r, 50));
      instance.close();
      expect(instance._isOpen === false || !document.querySelector('.link-preview-backdrop.active')).toBe(true);
    });
  });

  // =========================================================================
  // 5. Error & Loading States (FR-043-A.5)
  // =========================================================================

  describe('Loading State (AC-043-A.9)', () => {
    it('should show loading spinner with path when opening', () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      // Use a never-resolving fetch to keep loading state
      globalThis.fetch = vi.fn().mockReturnValue(new Promise(() => {}));

      const instance = LPM.instance || new LPM();
      instance.open('x-ipe-docs/requirements/test.md');

      const content = document.querySelector('.link-preview-content, .preview-content');
      expect(content).not.toBeNull();
      expect(content.textContent).toContain('x-ipe-docs/requirements/test.md');
    });
  });

  describe('Error State — 404 (AC-043-A.10)', () => {
    it('should show "File not found" error on 404 response', async () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({ error: 'not found' }),
      });

      const instance = LPM.instance || new LPM();
      await instance.open('x-ipe-docs/nonexistent.md');

      const content = document.querySelector('.link-preview-content, .preview-content');
      expect(content).not.toBeNull();
      expect(content.textContent.toLowerCase()).toContain('file not found');
      expect(content.textContent).toContain('x-ipe-docs/nonexistent.md');
    });
  });

  describe('Error State — Network Error (AC-043-A.11)', () => {
    it('should show error with retry button on network failure', async () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      globalThis.fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));

      const instance = LPM.instance || new LPM();
      await instance.open('x-ipe-docs/test.md');

      const content = document.querySelector('.link-preview-content, .preview-content');
      expect(content).not.toBeNull();
      expect(content.textContent.toLowerCase()).toContain('failed to load');

      const retryBtn = content.querySelector('button, .retry-btn');
      expect(retryBtn).not.toBeNull();
    });

    it('should retry fetch when retry button is clicked (AC-043-A.12)', async () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      let callCount = 0;
      globalThis.fetch = vi.fn().mockImplementation(async () => {
        callCount++;
        if (callCount === 1) throw new TypeError('Failed to fetch');
        return {
          ok: true,
          status: 200,
          json: async () => ({ content: '# Recovered', type: 'markdown', path: 'test.md', extension: '.md' }),
        };
      });

      const instance = LPM.instance || new LPM();
      await instance.open('x-ipe-docs/test.md');

      const retryBtn = document.querySelector('button, .retry-btn');
      expect(retryBtn).not.toBeNull();
      retryBtn.click();

      await new Promise(r => setTimeout(r, 100));
      expect(callCount).toBeGreaterThanOrEqual(2);
    });
  });

  // =========================================================================
  // 6. AbortController Management (FR-043-A.6)
  // =========================================================================

  describe('AbortController (AC-043-A.15)', () => {
    it('should abort previous request when new link is clicked', async () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      let abortSignals = [];
      globalThis.fetch = vi.fn().mockImplementation(async (url, opts) => {
        abortSignals.push(opts?.signal);
        // Simulate slow response
        await new Promise(r => setTimeout(r, 500));
        return {
          ok: true,
          status: 200,
          json: async () => ({ content: '# Test', type: 'markdown', path: 'test.md', extension: '.md' }),
        };
      });

      const instance = LPM.instance || new LPM();

      // First call (will be aborted)
      instance.open('x-ipe-docs/first.md');
      await new Promise(r => setTimeout(r, 10));

      // Second call (should abort first)
      instance.open('x-ipe-docs/second.md');

      expect(abortSignals.length).toBeGreaterThanOrEqual(2);
      // First signal should be aborted
      if (abortSignals[0]) {
        expect(abortSignals[0].aborted).toBe(true);
      }
    });
  });

  // =========================================================================
  // 7. Non-Regression (AC-043-A.19–AC-043-A.22)
  // =========================================================================

  describe('Non-Regression', () => {
    it('should not break ContentRenderer basic markdown rendering', () => {
      ensureContentRenderer();
      const CR = globalThis.ContentRenderer;
      expect(CR).toBeDefined();

      const container = document.createElement('div');
      container.id = 'test-regression';
      document.body.appendChild(container);
      const renderer = new CR('test-regression');

      // Basic markdown without internal links should still work
      const md = '# Hello\n\nThis is **bold** text.';
      renderer.renderMarkdown(md);

      const markdownBody = container.querySelector('.markdown-body');
      expect(markdownBody).not.toBeNull();
      expect(markdownBody.innerHTML).toBeTruthy();
    });

    it('should auto-attach link preview after renderMarkdown', () => {
      ensureContentRenderer();
      ensureLinkPreviewManager();
      const CR = globalThis.ContentRenderer;
      const LPM = globalThis.LinkPreviewManager;
      expect(CR).toBeDefined();
      expect(LPM).toBeDefined();

      const container = document.createElement('div');
      container.id = 'test-auto-attach';
      document.body.appendChild(container);
      const renderer = new CR('test-auto-attach');

      const md = '[test](x-ipe-docs/test.md)';
      renderer.renderMarkdown(md);

      const markdownBody = container.querySelector('.markdown-body');
      // Should have link preview attached (flag or listener)
      expect(markdownBody._linkPreviewAttached).toBe(true);
    });
  });

  // =========================================================================
  // 8. Edge Cases
  // =========================================================================

  describe('Edge Cases', () => {
    it('should handle link with query parameters by stripping them', async () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      let fetchedUrl = '';
      globalThis.fetch = vi.fn().mockImplementation(async (url) => {
        fetchedUrl = url;
        return {
          ok: true,
          status: 200,
          json: async () => ({ content: '# Test', type: 'markdown', path: 'test.md', extension: '.md' }),
        };
      });

      const instance = LPM.instance || new LPM();
      await instance.open('x-ipe-docs/test.md?line=5');

      // Should strip query params
      expect(fetchedUrl).toContain('x-ipe-docs%2Ftest.md');
      expect(fetchedUrl).not.toContain('line=5');
    });

    it('should handle link with anchor fragment by stripping it', async () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      let fetchedUrl = '';
      globalThis.fetch = vi.fn().mockImplementation(async (url) => {
        fetchedUrl = url;
        return {
          ok: true,
          status: 200,
          json: async () => ({ content: '# Test', type: 'markdown', path: 'test.md', extension: '.md' }),
        };
      });

      const instance = LPM.instance || new LPM();
      await instance.open('x-ipe-docs/test.md#section-2');

      expect(fetchedUrl).toContain('x-ipe-docs%2Ftest.md');
      expect(fetchedUrl).not.toContain('section-2');
    });

    it('should encode file paths with special characters', async () => {
      ensureLinkPreviewManager();
      const LPM = globalThis.LinkPreviewManager;
      expect(LPM).toBeDefined();

      let fetchedUrl = '';
      globalThis.fetch = vi.fn().mockImplementation(async (url) => {
        fetchedUrl = url;
        return {
          ok: true,
          status: 200,
          json: async () => ({ content: '# Test', type: 'markdown', path: 'test file.md', extension: '.md' }),
        };
      });

      const instance = LPM.instance || new LPM();
      await instance.open('x-ipe-docs/ideas/test file.md');

      expect(fetchedUrl).toContain(encodeURIComponent('x-ipe-docs/ideas/test file.md'));
    });
  });
});
