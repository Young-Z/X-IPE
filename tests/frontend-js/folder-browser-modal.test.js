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

    it('should show "No files" for empty folder', async () => {
      const FBM = globalThis.FolderBrowserModal;
      expect(FBM).toBeDefined();
      globalThis.fetch.mockResolvedValue({ ok: true, json: async () => [] });

      const modal = new FBM({ workflowName: 'test-wf' });
      modal.open('empty-folder/');
      await vi.waitFor(() => {
        const tree = document.querySelector('.folder-browser-tree');
        expect(tree.textContent).toContain('No files');
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

    it('should show "Binary file" for binary extensions', async () => {
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
        const content = document.querySelector('.folder-browser-preview-content');
        expect(content.textContent).toContain('Binary');
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
});
