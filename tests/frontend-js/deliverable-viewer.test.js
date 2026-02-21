/**
 * TDD Tests for FEATURE-038-C: Enhanced Deliverable Viewer (Frontend)
 * Tests: Folder detection, file-tree rendering, inline preview
 *
 * TDD: All tests MUST fail until deliverable-viewer.js is implemented.
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { loadFeatureScript } from './helpers.js';

/**
 * Guard: loads the feature script once.
 */
let _implLoaded = false;
function ensureImpl() {
  if (!_implLoaded) {
    try {
      loadFeatureScript('deliverable-viewer.js');
      _implLoaded = true;
    } catch {
      // File not yet implemented — TDD
    }
  }
  return typeof globalThis.DeliverableViewer !== 'undefined';
}

describe('FEATURE-038-C: Enhanced Deliverable Viewer', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    globalThis.fetch = vi.fn();
    globalThis.marked = { parse: vi.fn((md) => `<p>${md}</p>`) };
    ensureImpl();
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  describe('Folder Detection', () => {
    it('should export DeliverableViewer class', () => {
      expect(globalThis.DeliverableViewer).toBeDefined();
    });

    it('should identify paths ending with / as folder-type', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      expect(DV.isFolderType('x-ipe-docs/ideas/025/refined-idea/')).toBe(true);
    });

    it('should identify paths without extension as folder-type', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      expect(DV.isFolderType('x-ipe-docs/ideas/wf-001-test-the-workflow')).toBe(true);
    });

    it('should identify paths with extension as file-type', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      expect(DV.isFolderType('x-ipe-docs/ideas/025/idea-summary.md')).toBe(false);
    });
  });

  describe('File-Tree Rendering', () => {
    it('should render expand toggle for folder deliverables', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      const card = viewer.renderFolderDeliverable({ path: 'refined-idea/', name: 'refined-idea' });
      expect(card.querySelector('.toggle-icon')).not.toBeNull();
    });

    it('should fetch folder contents on expand click', async () => {
      globalThis.fetch.mockResolvedValue({
        ok: true,
        json: async () => [
          { name: 'idea-summary.md', type: 'file', path: 'refined-idea/idea-summary.md' },
          { name: 'mockups', type: 'dir', path: 'refined-idea/mockups/' },
        ],
      });

      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      const card = viewer.renderFolderDeliverable({ path: 'refined-idea/', name: 'refined-idea' });
      document.body.appendChild(card);
      card.querySelector('.toggle-icon').click();
      await vi.waitFor(() => {
        expect(globalThis.fetch).toHaveBeenCalledWith(expect.stringContaining('/deliverables/tree'));
      });
    });

    it('should render nested ul/li structure for tree', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const entries = [
        { name: 'file.md', type: 'file', path: 'folder/file.md' },
        { name: 'sub', type: 'dir', path: 'folder/sub/', children: [] },
      ];
      const tree = DV.buildTreeDOM(entries);
      expect(tree.tagName).toBe('UL');
      expect(tree.children.length).toBe(2);
    });

    it('should show folder icons for directories', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const entries = [{ name: 'sub', type: 'dir', path: 'folder/sub/', children: [] }];
      const tree = DV.buildTreeDOM(entries);
      expect(tree.querySelector('.dir-icon')).not.toBeNull();
    });

    it('should show file icons for files', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const entries = [{ name: 'readme.md', type: 'file', path: 'folder/readme.md' }];
      const tree = DV.buildTreeDOM(entries);
      expect(tree.querySelector('.file-icon')).not.toBeNull();
    });

    it('should make subdirectories collapsible', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const entries = [
        { name: 'sub', type: 'dir', path: 'folder/sub/', children: [
          { name: 'inner.md', type: 'file', path: 'folder/sub/inner.md' }
        ]},
      ];
      const tree = DV.buildTreeDOM(entries);
      const dirItem = tree.querySelector('.dir-item');
      expect(dirItem).not.toBeNull();
      dirItem.click();
      expect(dirItem.querySelector('ul').style.display).toBe('none');
    });

    it('should show "No files" for empty folders', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const tree = DV.buildTreeDOM([]);
      expect(tree.textContent).toContain('No files');
    });
  });

  describe('Inline Preview', () => {
    it('should open preview pane when file clicked', async () => {
      globalThis.fetch.mockResolvedValue({
        ok: true,
        text: async () => '# Test Heading\n\nSome content',
      });

      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      await viewer.showPreview('refined-idea/readme.md');
      expect(document.querySelector('.deliverable-preview')).not.toBeNull();
    });

    it('should render markdown files with marked.parse()', async () => {
      globalThis.fetch.mockResolvedValue({
        ok: true,
        text: async () => '# Heading',
      });

      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      await viewer.showPreview('refined-idea/readme.md');
      expect(globalThis.marked.parse).toHaveBeenCalledWith('# Heading');
    });

    it('should render text files as preformatted text', async () => {
      globalThis.fetch.mockResolvedValue({
        ok: true,
        text: async () => 'plain text content',
      });

      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      await viewer.showPreview('refined-idea/data.txt');
      expect(document.querySelector('.deliverable-preview pre')).not.toBeNull();
    });

    it('should show file name in preview header', async () => {
      globalThis.fetch.mockResolvedValue({
        ok: true,
        text: async () => 'content',
      });

      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      await viewer.showPreview('refined-idea/readme.md');
      expect(document.querySelector('.preview-header').textContent).toContain('readme.md');
    });

    it('should replace previous preview when new file clicked', async () => {
      globalThis.fetch.mockResolvedValue({
        ok: true,
        text: async () => 'content',
      });

      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      await viewer.showPreview('file1.md');
      await viewer.showPreview('file2.md');
      const previews = document.querySelectorAll('.deliverable-preview');
      expect(previews.length).toBe(1);
    });

    it('should show message for binary files (415 response)', async () => {
      globalThis.fetch.mockResolvedValue({
        ok: false,
        status: 415,
      });

      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      await viewer.showPreview('image.png');
      expect(document.querySelector('.deliverable-preview').textContent).toContain('Binary');
    });
  });

  describe('Security', () => {
    it('should not allow path traversal in file requests', async () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      await expect(viewer.showPreview('../../etc/passwd')).rejects.toThrow();
    });
  });
});
