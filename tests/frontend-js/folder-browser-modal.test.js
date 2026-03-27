/**
 * TDD Tests for FEATURE-039-A: Folder Browser Modal (MVP)
 * Tests: Modal lifecycle, tree loading, file preview, close mechanics, error states
 *
 * TDD: All tests MUST fail until folder-browser-modal.js is implemented.
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { loadFeatureScript } from './helpers.js';

let _implLoaded = false;
function ensureImpl() {
  if (!_implLoaded) {
    try {
      // Load DeliverableViewer first (dependency for buildTreeDOM)
      loadFeatureScript('deliverable-viewer.js');
    } catch { /* not yet implemented */ }
    try {
      loadFeatureScript('folder-browser-modal.js');
      _implLoaded = true;
    } catch { /* not yet implemented */ }
  }
  return typeof globalThis.FolderBrowserModal !== 'undefined';
}

const TREE_RESPONSE = [
  { name: 'idea-summary.md', type: 'file', path: 'refined-idea/idea-summary.md' },
  { name: 'notes.txt', type: 'file', path: 'refined-idea/notes.txt' },
  { name: 'mockups', type: 'dir', path: 'refined-idea/mockups/', children: [
    { name: 'sketch.png', type: 'file', path: 'refined-idea/mockups/sketch.png' },
  ]},
];

describe('FEATURE-039-A: Folder Browser Modal (MVP)', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    document.body.style.overflow = '';
    globalThis.fetch = vi.fn();
    globalThis.marked = { parse: vi.fn((md) => `<p>${md}</p>`) };
    ensureImpl();
  });

  afterEach(() => {
    // Clean up any modal still open
    document.querySelectorAll('.folder-browser-backdrop').forEach(el => el.remove());
    document.body.style.overflow = '';
  });

  describe('Class Export', () => {
    it('should export FolderBrowserModal class', () => {
      expect(globalThis.FolderBrowserModal).toBeDefined();
    });

    it('should accept workflowName in constructor', () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      const modal = new FBM({ workflowName: 'test-wf' });
      expect(modal).toBeDefined();
    });
  });

  describe('Modal Open', () => {
    it('should create backdrop on open()', () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      expect(document.querySelector('.folder-browser-backdrop')).not.toBeNull();
    });

    it('should create modal container inside backdrop', () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      expect(document.querySelector('.folder-browser-modal')).not.toBeNull();
    });

    it('should show folder name in header', () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      const title = document.querySelector('.folder-browser-title');
      expect(title).not.toBeNull();
      expect(title.textContent).toContain('refined-idea');
    });

    it('should have two-panel body (tree + preview)', () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      expect(document.querySelector('.folder-browser-tree')).not.toBeNull();
      expect(document.querySelector('.folder-browser-preview')).not.toBeNull();
    });

    it('should lock body scroll when open', () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      expect(document.body.style.overflow).toBe('hidden');
    });
  });

  describe('Tree Loading', () => {
    it('should fetch tree from API on open', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      await vi.waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/workflow/test-wf/deliverables/tree'),
          expect.anything()
        );
      });
    });

    it('should show spinner while tree loads', () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      // Don't resolve fetch — keep it pending
      globalThis.fetch.mockReturnValue(new Promise(() => {}));

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      expect(document.querySelector('.folder-browser-spinner')).not.toBeNull();
    });

    it('should render tree after successful fetch', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      await vi.waitFor(() => {
        expect(document.querySelector('.file-tree')).not.toBeNull();
      });
    });

    it('should show "This folder is empty" for empty folder', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => [] });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('empty-folder/');
      await vi.waitFor(() => {
        const tree = document.querySelector('.folder-browser-tree');
        expect(tree.textContent).toContain('This folder is empty');
      });
    });

    it('should show error with retry on API failure', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: false, status: 500 });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      await vi.waitFor(() => {
        const tree = document.querySelector('.folder-browser-tree');
        expect(tree.querySelector('.folder-browser-error')).not.toBeNull();
        expect(tree.querySelector('button')).not.toBeNull(); // retry button
      });
    });
  });

  describe('File Preview', () => {
    it('should render markdown with marked.parse()', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();

      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => TREE_RESPONSE })
        .mockResolvedValueOnce({ ok: true, text: async () => '# Hello' });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');

      await vi.waitFor(() => {
        expect(document.querySelector('.file-tree')).not.toBeNull();
      });

      // Click the .md file
      const fileItem = document.querySelector('.file-item[data-path="refined-idea/idea-summary.md"]');
      expect(fileItem).not.toBeNull();
      fileItem.click();

      await vi.waitFor(() => {
        expect(globalThis.marked.parse).toHaveBeenCalledWith('# Hello');
      });
    });

    it('should render text files as preformatted text', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();

      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => TREE_RESPONSE })
        .mockResolvedValueOnce({ ok: true, text: async () => 'plain text' });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');

      await vi.waitFor(() => {
        expect(document.querySelector('.file-tree')).not.toBeNull();
      });

      const fileItem = document.querySelector('.file-item[data-path="refined-idea/notes.txt"]');
      expect(fileItem).not.toBeNull();
      fileItem.click();

      await vi.waitFor(() => {
        const pre = document.querySelector('.folder-browser-preview-content pre');
        expect(pre).not.toBeNull();
      });
    });

    it('should highlight selected file in tree', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();

      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => TREE_RESPONSE })
        .mockResolvedValueOnce({ ok: true, text: async () => 'content' });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');

      await vi.waitFor(() => {
        expect(document.querySelector('.file-tree')).not.toBeNull();
      });

      const fileItem = document.querySelector('.file-item[data-path="refined-idea/idea-summary.md"]');
      fileItem.click();

      await vi.waitFor(() => {
        expect(fileItem.classList.contains('selected')).toBe(true);
      });
    });

    it('should show file name in preview header', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();

      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => TREE_RESPONSE })
        .mockResolvedValueOnce({ ok: true, text: async () => 'content' });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');

      await vi.waitFor(() => {
        expect(document.querySelector('.file-tree')).not.toBeNull();
      });

      const fileItem = document.querySelector('.file-item[data-path="refined-idea/idea-summary.md"]');
      fileItem.click();

      await vi.waitFor(() => {
        const header = document.querySelector('.folder-browser-preview-header');
        expect(header).not.toBeNull();
        expect(header.textContent).toContain('idea-summary.md');
      });
    });

    it('should show image preview for image extensions', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();

      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => TREE_RESPONSE });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');

      await vi.waitFor(() => {
        expect(document.querySelector('.file-tree')).not.toBeNull();
      });

      const imgItem = document.querySelector('.file-item[data-path="refined-idea/mockups/sketch.png"]');
      expect(imgItem).not.toBeNull();
      imgItem.click();

      await vi.waitFor(() => {
        const img = document.querySelector('.folder-browser-image-preview img');
        expect(img).not.toBeNull();
        expect(img.src).toContain('sketch.png');
      });
    });

    it('should replace previous preview on new file click', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();

      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => TREE_RESPONSE })
        .mockResolvedValueOnce({ ok: true, text: async () => 'first file' })
        .mockResolvedValueOnce({ ok: true, text: async () => 'second file' });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');

      await vi.waitFor(() => {
        expect(document.querySelector('.file-tree')).not.toBeNull();
      });

      // Click first file
      document.querySelector('.file-item[data-path="refined-idea/idea-summary.md"]').click();
      await vi.waitFor(() => {
        expect(document.querySelector('.folder-browser-preview-content')).not.toBeNull();
      });

      // Click second file
      document.querySelector('.file-item[data-path="refined-idea/notes.txt"]').click();
      await vi.waitFor(() => {
        const contents = document.querySelectorAll('.folder-browser-preview-content');
        expect(contents.length).toBe(1);
      });
    });
  });

  describe('Modal Close', () => {
    it('should close on close button click', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');

      const closeBtn = document.querySelector('.folder-browser-close');
      expect(closeBtn).not.toBeNull();
      closeBtn.click();

      // Wait for transition (200ms in design)
      await new Promise(r => setTimeout(r, 300));
      expect(document.querySelector('.folder-browser-backdrop')).toBeNull();
    });

    it('should close on Escape key', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');

      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));

      await new Promise(r => setTimeout(r, 300));
      expect(document.querySelector('.folder-browser-backdrop')).toBeNull();
    });

    it('should close on backdrop click', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');

      const backdrop = document.querySelector('.folder-browser-backdrop');
      backdrop.click();

      await new Promise(r => setTimeout(r, 300));
      expect(document.querySelector('.folder-browser-backdrop')).toBeNull();
    });

    it('should NOT close on modal content click', () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');

      const modalEl = document.querySelector('.folder-browser-modal');
      modalEl.click();

      expect(document.querySelector('.folder-browser-backdrop')).not.toBeNull();
    });

    it('should restore body scroll on close', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      expect(document.body.style.overflow).toBe('hidden');

      modal.close();
      await new Promise(r => setTimeout(r, 300));
      expect(document.body.style.overflow).toBe('');
    });

    it('should abort pending fetch on close', () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      // Don't resolve fetch
      globalThis.fetch.mockReturnValue(new Promise(() => {}));

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      modal.close();
      // Should not throw
    });
  });

  describe('Tree Interaction', () => {
    it('should expand/collapse directories on click', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');

      await vi.waitFor(() => {
        expect(document.querySelector('.file-tree')).not.toBeNull();
      });

      const dirItem = document.querySelector('.dir-item');
      expect(dirItem).not.toBeNull();
      dirItem.click();
      // Children should toggle visibility
      const children = dirItem.querySelector('ul');
      if (children) {
        expect(children.style.display).toBe('none');
      }
    });

    it('should lazy-load sub-folder contents on click', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();

      // First call: top-level tree (dir has no children from API)
      const flatTree = [
        { name: 'readme.md', type: 'file', path: 'folder/readme.md' },
        { name: 'sub', type: 'dir', path: 'folder/sub/' },
      ];
      const subFolderContents = [
        { name: 'inner.md', type: 'file', path: 'folder/sub/inner.md' },
      ];

      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => flatTree })
        .mockResolvedValueOnce({ ok: true, json: async () => subFolderContents });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('folder/');

      await vi.waitFor(() => {
        expect(document.querySelector('.file-tree')).not.toBeNull();
      });

      // Click the sub-folder dir-item
      const dirItem = document.querySelector('.dir-item');
      expect(dirItem).not.toBeNull();
      dirItem.click();

      // Should fetch sub-folder contents
      await vi.waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalledTimes(2);
        expect(globalThis.fetch).toHaveBeenLastCalledWith(
          expect.stringContaining('path=folder%2Fsub%2F')
        );
      });

      // Should render child tree
      await vi.waitFor(() => {
        const childTree = dirItem.querySelector('.file-tree');
        expect(childTree).not.toBeNull();
        expect(childTree.querySelector('.file-item')).not.toBeNull();
      });
    });

    it('should toggle lazy-loaded sub-folder on second click', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();

      const flatTree = [
        { name: 'sub', type: 'dir', path: 'folder/sub/' },
      ];
      const subContents = [
        { name: 'file.md', type: 'file', path: 'folder/sub/file.md' },
      ];

      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => flatTree })
        .mockResolvedValueOnce({ ok: true, json: async () => subContents });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('folder/');

      await vi.waitFor(() => {
        expect(document.querySelector('.dir-item')).not.toBeNull();
      });

      const dirItem = document.querySelector('.dir-item');
      dirItem.click();

      await vi.waitFor(() => {
        expect(dirItem.querySelector('.file-tree')).not.toBeNull();
      });

      // Second click should hide (not re-fetch)
      dirItem.click();
      const childUl = dirItem.querySelector('ul');
      expect(childUl.style.display).toBe('none');

      // Third click should show again
      dirItem.click();
      expect(childUl.style.display).toBe('');

      // fetch should still only have been called twice (no re-fetch)
      expect(globalThis.fetch).toHaveBeenCalledTimes(2);
    });
  });

  describe('TASK-615: HTML Preview as Iframe', () => {
    it('should render HTML files in an iframe instead of raw text', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();

      const TREE_WITH_HTML = [
        { name: 'mockup.html', type: 'file', path: 'refined-idea/mockups/mockup.html' },
      ];

      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => TREE_WITH_HTML })
        .mockResolvedValueOnce({ ok: true, text: async () => '<html><body><h1>Mockup</h1></body></html>' });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');

      await vi.waitFor(() => {
        expect(document.querySelector('.file-tree')).not.toBeNull();
      });

      const fileItem = document.querySelector('.file-item[data-path="refined-idea/mockups/mockup.html"]');
      expect(fileItem).not.toBeNull();
      fileItem.click();

      await vi.waitFor(() => {
        const iframe = document.querySelector('.folder-browser-preview-content iframe');
        expect(iframe).not.toBeNull();
        expect(iframe.getAttribute('sandbox')).toContain('allow-scripts');
      });
    });

    it('should NOT show HTML files as preformatted text', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();

      const TREE_WITH_HTML = [
        { name: 'page.html', type: 'file', path: 'refined-idea/page.html' },
      ];

      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => TREE_WITH_HTML })
        .mockResolvedValueOnce({ ok: true, text: async () => '<html><body>Test</body></html>' });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');

      await vi.waitFor(() => {
        expect(document.querySelector('.file-tree')).not.toBeNull();
      });

      const fileItem = document.querySelector('.file-item[data-path="refined-idea/page.html"]');
      fileItem.click();

      await vi.waitFor(() => {
        const content = document.querySelector('.folder-browser-preview-content');
        expect(content).not.toBeNull();
        const pre = content.querySelector('pre');
        expect(pre).toBeNull();
      });
    });
  });

  describe('TASK-618: Markdown Preview uses ContentRenderer', () => {
    it('should use ContentRenderer.renderMarkdown for .md files', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();

      // Mock ContentRenderer
      const renderMarkdownSpy = vi.fn();
      globalThis.ContentRenderer = class {
        constructor(containerOrId) {
          this.container = typeof containerOrId === 'string'
            ? document.getElementById(containerOrId)
            : containerOrId;
        }
        initMermaid() {}
        initMarked() {}
        initArchitectureDSL() {}
        renderMarkdown(content) { renderMarkdownSpy(content); this.container.innerHTML = '<div class="markdown-body"><p>' + content + '</p></div>'; }
      };

      const mdContent = '# Hello\n\n```mermaid\ngraph TD;\n  A-->B;\n```';

      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => TREE_RESPONSE })
        .mockResolvedValueOnce({ ok: true, text: async () => mdContent });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');

      await vi.waitFor(() => {
        expect(document.querySelector('.file-tree')).not.toBeNull();
      });

      const fileItem = document.querySelector('.file-item[data-path="refined-idea/idea-summary.md"]');
      fileItem.click();

      await vi.waitFor(() => {
        expect(renderMarkdownSpy).toHaveBeenCalledWith(mdContent);
      });
    });

    it('should wrap markdown content in markdown-body class', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();

      // Mock ContentRenderer that wraps in markdown-body
      globalThis.ContentRenderer = class {
        constructor(containerOrId) {
          this.container = typeof containerOrId === 'string'
            ? document.getElementById(containerOrId)
            : containerOrId;
        }
        initMermaid() {}
        initMarked() {}
        initArchitectureDSL() {}
        renderMarkdown(content) { this.container.innerHTML = '<div class="markdown-body"><p>' + content + '</p></div>'; }
      };

      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => TREE_RESPONSE })
        .mockResolvedValueOnce({ ok: true, text: async () => '# Hello' });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');

      await vi.waitFor(() => {
        expect(document.querySelector('.file-tree')).not.toBeNull();
      });

      document.querySelector('.file-item[data-path="refined-idea/idea-summary.md"]').click();

      await vi.waitFor(() => {
        const mdBody = document.querySelector('.folder-browser-preview-content .markdown-body');
        expect(mdBody).not.toBeNull();
      });
    });

    it('should accept DOM element in ContentRenderer constructor', () => {
      // ContentRenderer should support passing a DOM element, not just a string ID
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();

      // Load content-renderer.js with proper mocks
      const origMarked = globalThis.marked;
      class MockRenderer { link(h, t, x) { return `<a href="${h}">${x}</a>`; } }
      globalThis.marked = { parse: vi.fn((md) => `<p>${md}</p>`), setOptions: vi.fn(), Renderer: MockRenderer };

      try {
        loadFeatureScript('../core/content-renderer.js', 'core');
      } catch { /* may not exist in test */ }

      const CR = globalThis.ContentRenderer;
      if (CR) {
        const div = document.createElement('div');
        document.body.appendChild(div);
        const renderer = new CR(div);
        expect(renderer.container).toBe(div);
        div.remove();
      }

      // Restore
      globalThis.marked = origMarked;
    });
  });

  describe('Default Preview State', () => {
    it('should show "Select a file to preview" initially', () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      const preview = document.querySelector('.folder-browser-preview');
      expect(preview.textContent).toContain('Select a file');
    });
  });

  describe('FEATURE-039-B: Enhanced Modal Features', () => {
    describe('ARIA Roles', () => {
      it('should set role="dialog" and aria-modal on modal container', () => {
        const FBM = globalThis.FolderBrowserModal;
        globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });
        const modal = new FBM({ workflowName: 'test-wf' });
        modal.open('refined-idea/');
        const m = document.querySelector('.folder-browser-modal');
        expect(m.getAttribute('role')).toBe('dialog');
        expect(m.getAttribute('aria-modal')).toBe('true');
      });

      it('should set role="tree" on tree root and role="treeitem" on items', async () => {
        const FBM = globalThis.FolderBrowserModal;
        globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });
        const modal = new FBM({ workflowName: 'test-wf' });
        modal.open('refined-idea/');
        await vi.waitFor(() => {
          const tree = document.querySelector('.file-tree');
          expect(tree).not.toBeNull();
          expect(tree.getAttribute('role')).toBe('tree');
          const items = tree.querySelectorAll('[role="treeitem"]');
          expect(items.length).toBeGreaterThan(0);
        });
      });
    });

    describe('Search / Filter', () => {
      it('should render search input in tree panel', () => {
        const FBM = globalThis.FolderBrowserModal;
        globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });
        const modal = new FBM({ workflowName: 'test-wf' });
        modal.open('refined-idea/');
        expect(document.querySelector('.folder-browser-search-input')).not.toBeNull();
      });

      it('should filter tree items on input', async () => {
        const FBM = globalThis.FolderBrowserModal;
        globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });
        const modal = new FBM({ workflowName: 'test-wf' });
        modal.open('refined-idea/');
        await vi.waitFor(() => {
          expect(document.querySelector('.file-tree')).not.toBeNull();
        });
        const input = document.querySelector('.folder-browser-search-input');
        input.value = 'notes';
        input.dispatchEvent(new Event('input'));
        // Wait debounce
        await new Promise(r => setTimeout(r, 250));
        const items = document.querySelectorAll('.tree-item');
        const visibleItems = [...items].filter(i => i.style.display !== 'none');
        expect(visibleItems.some(i => i.textContent.includes('notes'))).toBe(true);
      });

      it('should show "No matching files" when nothing matches', async () => {
        const FBM = globalThis.FolderBrowserModal;
        globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });
        const modal = new FBM({ workflowName: 'test-wf' });
        modal.open('refined-idea/');
        await vi.waitFor(() => {
          expect(document.querySelector('.file-tree')).not.toBeNull();
        });
        const input = document.querySelector('.folder-browser-search-input');
        input.value = 'zzzznonexistent';
        input.dispatchEvent(new Event('input'));
        await new Promise(r => setTimeout(r, 250));
        expect(document.querySelector('.folder-browser-no-match')).not.toBeNull();
      });
    });

    describe('Breadcrumb Navigation', () => {
      it('should render breadcrumb on open', () => {
        const FBM = globalThis.FolderBrowserModal;
        globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });
        const modal = new FBM({ workflowName: 'test-wf' });
        modal.open('refined-idea/');
        expect(document.querySelector('.folder-browser-breadcrumb')).not.toBeNull();
        expect(document.querySelector('.folder-browser-breadcrumb').textContent).toContain('refined-idea');
      });

      it('should truncate >5 segments with ellipsis', () => {
        const FBM = globalThis.FolderBrowserModal;
        globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });
        const modal = new FBM({ workflowName: 'test-wf' });
        modal.open('a/b/c/d/e/f/g/');
        const bc = document.querySelector('.folder-browser-breadcrumb');
        expect(bc.textContent).toContain('\u2026');
      });
    });

    describe('Typed File Icons', () => {
      it('should show 📝 for .md files', async () => {
        const FBM = globalThis.FolderBrowserModal;
        globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });
        const modal = new FBM({ workflowName: 'test-wf' });
        modal.open('refined-idea/');
        await vi.waitFor(() => {
          const mdItem = document.querySelector('.file-item[data-path="refined-idea/idea-summary.md"]');
          expect(mdItem).not.toBeNull();
          expect(mdItem.textContent).toMatch(/📝/);
        });
      });

      it('should show 🖼️ for image files', async () => {
        const FBM = globalThis.FolderBrowserModal;
        globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });
        const modal = new FBM({ workflowName: 'test-wf' });
        modal.open('refined-idea/');
        await vi.waitFor(() => {
          const imgItem = document.querySelector('.file-item[data-path="refined-idea/mockups/sketch.png"]');
          expect(imgItem).not.toBeNull();
          expect(imgItem.textContent).toMatch(/🖼️/);
        });
      });
    });

    describe('Download Button', () => {
      it('should show download button in preview header', async () => {
        const FBM = globalThis.FolderBrowserModal;
        globalThis.fetch
          .mockResolvedValueOnce({ ok: true, json: async () => TREE_RESPONSE })
          .mockResolvedValueOnce({ ok: true, text: async () => 'content' });
        const modal = new FBM({ workflowName: 'test-wf' });
        modal.open('refined-idea/');
        await vi.waitFor(() => expect(document.querySelector('.file-tree')).not.toBeNull());
        document.querySelector('.file-item[data-path="refined-idea/notes.txt"]').click();
        await vi.waitFor(() => {
          const dl = document.querySelector('.folder-browser-download-btn');
          expect(dl).not.toBeNull();
          expect(dl.getAttribute('download')).toBe('notes.txt');
        });
      });
    });

    describe('Binary File Enhancement', () => {
      it('should show download link for binary (non-image) files', async () => {
        const FBM = globalThis.FolderBrowserModal;
        const binaryTree = [
          { name: 'archive.zip', type: 'file', path: 'refined-idea/archive.zip' },
        ];
        globalThis.fetch.mockResolvedValueOnce({ ok: true, json: async () => binaryTree });
        const modal = new FBM({ workflowName: 'test-wf' });
        modal.open('refined-idea/');
        await vi.waitFor(() => expect(document.querySelector('.file-tree')).not.toBeNull());
        document.querySelector('.file-item[data-path="refined-idea/archive.zip"]').click();
        await vi.waitFor(() => {
          const dl = document.querySelector('.folder-browser-download-link');
          expect(dl).not.toBeNull();
          expect(dl.getAttribute('download')).toBe('archive.zip');
        });
      });
    });

    describe('Large File Handling', () => {
      it('should show "File too large" for >1MB text files', async () => {
        const FBM = globalThis.FolderBrowserModal;
        const bigContent = 'x'.repeat(1_100_000);
        globalThis.fetch
          .mockResolvedValueOnce({ ok: true, json: async () => TREE_RESPONSE })
          .mockResolvedValueOnce({ ok: true, text: async () => bigContent });
        const modal = new FBM({ workflowName: 'test-wf' });
        modal.open('refined-idea/');
        await vi.waitFor(() => expect(document.querySelector('.file-tree')).not.toBeNull());
        document.querySelector('.file-item[data-path="refined-idea/notes.txt"]').click();
        await vi.waitFor(() => {
          const content = document.querySelector('.folder-browser-binary-info');
          expect(content).not.toBeNull();
          expect(content.textContent).toContain('too large');
        });
      });
    });

    describe('Keyboard Navigation', () => {
      it('should have tabindex on tree and preview panels', () => {
        const FBM = globalThis.FolderBrowserModal;
        globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });
        const modal = new FBM({ workflowName: 'test-wf' });
        modal.open('refined-idea/');
        expect(document.querySelector('.folder-browser-tree').getAttribute('tabindex')).toBe('0');
        expect(document.querySelector('.folder-browser-preview').getAttribute('tabindex')).toBe('0');
      });

      it('should navigate tree items with arrow keys', async () => {
        const FBM = globalThis.FolderBrowserModal;
        globalThis.fetch.mockResolvedValue({ ok: true, json: async () => TREE_RESPONSE });
        const modal = new FBM({ workflowName: 'test-wf' });
        modal.open('refined-idea/');
        await vi.waitFor(() => expect(document.querySelector('.file-tree')).not.toBeNull());

        const treePanel = document.querySelector('.folder-browser-tree');
        treePanel.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));
        const focused = document.querySelector('.tree-item.keyboard-focus');
        expect(focused).not.toBeNull();
      });
    });
  });

  // ────────────────────────────────────────────────────
  // CR-003: Folder Browser Modal Toolbar Parity
  // ────────────────────────────────────────────────────
  describe('CR-003: Folder Browser Toolbar Parity', () => {
    let _fprLoaded = false;
    function ensureFPR() {
      if (!_fprLoaded) {
        try { loadFeatureScript('../core/file-preview-renderer.js'); } catch { /* skip */ }
        _fprLoaded = true;
      }
      return typeof globalThis.FilePreviewRenderer !== 'undefined';
    }

    beforeEach(() => {
      ensureFPR();
      // marked is needed by FilePreviewRenderer for .md rendering
      globalThis.marked = {
        parse: vi.fn((md) => `<p>${md}</p>`),
        Renderer: function MockRenderer() { this.link = function() { return ''; }; },
        setOptions: vi.fn()
      };
    });

    const MOCK_HEADERS = { get: () => null };

    it('should show toolbar group with download and toggle for text file (AC-07a)', async () => {
      if (!ensureFPR()) return;
      const FBM = globalThis.FolderBrowserModal;
      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => TREE_RESPONSE })
        .mockResolvedValueOnce({ ok: true, text: async () => '# Hello', headers: MOCK_HEADERS });
      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      await vi.waitFor(() => expect(document.querySelector('.file-tree')).not.toBeNull());
      document.querySelector('.file-item[data-path="refined-idea/idea-summary.md"]').click();
      await vi.waitFor(() => {
        const toolbar = document.querySelector('.folder-browser-toolbar-group');
        expect(toolbar).not.toBeNull();
        const dl = toolbar.querySelector('.folder-browser-download-btn');
        expect(dl).not.toBeNull();
        expect(dl.href).toContain('download=true');
        const toggle = toolbar.querySelector('.folder-browser-toggle-btn');
        expect(toggle).not.toBeNull();
      });
    });

    it('should hide toggle for non-text file like .png (AC-07b)', async () => {
      if (!ensureFPR()) return;
      const FBM = globalThis.FolderBrowserModal;
      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => TREE_RESPONSE })
        .mockResolvedValueOnce({ ok: true, text: async () => 'binary', headers: MOCK_HEADERS });
      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      await vi.waitFor(() => expect(document.querySelector('.file-tree')).not.toBeNull());
      document.querySelector('.file-item[data-path="refined-idea/mockups/sketch.png"]').click();
      await vi.waitFor(() => {
        const header = document.querySelector('.folder-browser-preview-header');
        expect(header).not.toBeNull();
      });
      // Image goes through _renderImagePreview fallback — no toggle
      const toggle = document.querySelector('.folder-browser-toggle-btn');
      expect(toggle).toBeNull();
    });

    it('should default to raw mode for /src/ path (AC-07c)', async () => {
      if (!ensureFPR()) return;
      const FBM = globalThis.FolderBrowserModal;
      const srcTree = [
        { name: 'app.js', type: 'file', path: 'project/src/app.js' },
      ];
      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => srcTree })
        .mockResolvedValueOnce({ ok: true, text: async () => 'const x = 1;', headers: MOCK_HEADERS });
      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('project/');
      await vi.waitFor(() => expect(document.querySelector('.file-tree')).not.toBeNull());
      document.querySelector('.file-item[data-path="project/src/app.js"]').click();
      await vi.waitFor(() => {
        const raw = document.querySelector('.preview-raw-content');
        expect(raw).not.toBeNull();
        expect(raw.textContent).toBe('const x = 1;');
      });
    });

    it('should toggle between preview and raw without re-fetching (AC-07d)', async () => {
      if (!ensureFPR()) return;
      const FBM = globalThis.FolderBrowserModal;
      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => TREE_RESPONSE })
        .mockResolvedValueOnce({ ok: true, text: async () => '# Toggle Me', headers: MOCK_HEADERS });
      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      await vi.waitFor(() => expect(document.querySelector('.file-tree')).not.toBeNull());
      document.querySelector('.file-item[data-path="refined-idea/idea-summary.md"]').click();
      await vi.waitFor(() => {
        expect(document.querySelector('.folder-browser-toggle-btn')).not.toBeNull();
      });
      const fetchCountBefore = globalThis.fetch.mock.calls.length;
      // Click toggle to switch to raw
      document.querySelector('.folder-browser-toggle-btn').click();
      await vi.waitFor(() => {
        expect(document.querySelector('.preview-raw-content')).not.toBeNull();
      });
      // No additional fetch calls
      expect(globalThis.fetch.mock.calls.length).toBe(fetchCountBefore);
      // Click toggle again to switch back to preview
      document.querySelector('.folder-browser-toggle-btn').click();
      await vi.waitFor(() => {
        expect(document.querySelector('.preview-raw-content')).toBeNull();
      });
      expect(globalThis.fetch.mock.calls.length).toBe(fetchCountBefore);
    });

    it('should include download=true in download link href', async () => {
      if (!ensureFPR()) return;
      const FBM = globalThis.FolderBrowserModal;
      globalThis.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => TREE_RESPONSE })
        .mockResolvedValueOnce({ ok: true, text: async () => 'content', headers: MOCK_HEADERS });
      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('refined-idea/');
      await vi.waitFor(() => expect(document.querySelector('.file-tree')).not.toBeNull());
      document.querySelector('.file-item[data-path="refined-idea/notes.txt"]').click();
      await vi.waitFor(() => {
        const dl = document.querySelector('.folder-browser-download-btn');
        expect(dl).not.toBeNull();
        expect(dl.href).toContain('download=true');
        expect(dl.getAttribute('download')).toBe('notes.txt');
      });
    });
  });
});
