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

    it('should identify numbered folder names with dots as folder-type', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      // Folder names like "001. Feature Name" contain dots but are not file extensions
      expect(DV.isFolderType('ideas/001. Feature-Console Voice Input - 01242026 000728')).toBe(true);
      expect(DV.isFolderType('x-ipe-docs/ideas/002. Feature-Brand Themes')).toBe(true);
      // Files should still be detected correctly
      expect(DV.isFolderType('ideas/001. Feature-Console Voice Input/new idea.md')).toBe(false);
      expect(DV.isFolderType('ideas/002. Feature-Brand Themes/mockup.html')).toBe(false);
    });
  });

  describe('File-Tree Rendering', () => {
    it('FEATURE-039-A: folder card no longer has expand toggle (modal replaces inline tree)', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      const card = viewer.renderFolderDeliverable({ path: 'refined-idea/', name: 'refined-idea' });
      expect(card.querySelector('.toggle-icon')).toBeNull();
      expect(card.classList.contains('clickable')).toBe(true);
    });

    it('FEATURE-039-A: folder card no longer has inline tree container', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      const card = viewer.renderFolderDeliverable({ path: 'refined-idea/', name: 'refined-idea' });
      expect(card.querySelector('.deliverable-tree')).toBeNull();
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

  describe('TASK-588: Deliverable Card Styling Fixes', () => {
    it('should render folder icon with deliverable-icon class and background', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      const card = viewer.renderFolderDeliverable({ path: 'ideas/wf-001-greedy-snake', name: 'wf-001-greedy-snake', category: 'ideas' });
      const icon = card.querySelector('.deliverable-icon');
      expect(icon).not.toBeNull();
      expect(icon.textContent).toBe('📁');
    });

    it('should render folder name and path on separate lines', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      const card = viewer.renderFolderDeliverable({ path: 'ideas/wf-001-greedy-snake', name: 'wf-001-greedy-snake', category: 'ideas' });
      const info = card.querySelector('.deliverable-info');
      expect(info).not.toBeNull();
      const name = info.querySelector('.deliverable-name');
      const path = info.querySelector('.deliverable-path');
      expect(name).not.toBeNull();
      expect(path).not.toBeNull();
      // name and path should be block elements (div), not inline (span)
      expect(name.tagName).toBe('DIV');
      expect(path.tagName).toBe('DIV');
    });

    it('should strip x-ipe-docs/ prefix from folder deliverable path', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      const card = viewer.renderFolderDeliverable({ path: 'x-ipe-docs/ideas/wf-001-greedy-snake', name: 'wf-001-greedy-snake', category: 'ideas' });
      const path = card.querySelector('.deliverable-path');
      expect(path.textContent).not.toContain('x-ipe-docs/');
      expect(path.textContent).toBe('ideas/wf-001-greedy-snake');
    });
  });

  describe('TASK-589: File Deliverable Click-to-Preview', () => {
    it('should have makeClickableForPreview method', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      expect(typeof viewer.makeClickableForPreview).toBe('function');
    });

    it('should set cursor pointer on card', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      const card = document.createElement('div');
      viewer.makeClickableForPreview(card, 'ideas/test/idea-summary.md');
      expect(card.style.cursor).toBe('pointer');
    });

    it('should call showPreview on click', async () => {
      globalThis.fetch.mockResolvedValue({
        ok: true,
        text: async () => '# Content',
      });

      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      vi.spyOn(viewer, 'showPreview');
      const card = document.createElement('div');
      viewer.makeClickableForPreview(card, 'ideas/test/idea-summary.md');
      document.body.appendChild(card);
      card.click();
      expect(viewer.showPreview).toHaveBeenCalledWith('ideas/test/idea-summary.md');
    });

    it('should not make missing deliverables clickable', () => {
      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      const card = document.createElement('div');
      card.classList.add('missing');
      viewer.makeClickableForPreview(card, 'ideas/test/idea-summary.md', { exists: false });
      expect(card.style.cursor).not.toBe('pointer');
    });
  });

  describe('TASK-615: HTML Preview as Iframe', () => {
    it('should render HTML files in an iframe instead of raw text', async () => {
      globalThis.fetch.mockResolvedValue({
        ok: true,
        text: async () => '<html><body><h1>Hello</h1></body></html>',
      });

      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      await viewer.showPreview('mockups/design.html');
      const iframe = document.querySelector('.preview-content iframe');
      expect(iframe).not.toBeNull();
      expect(iframe.getAttribute('sandbox')).toContain('allow-scripts');
    });

    it('should render .htm files in an iframe', async () => {
      globalThis.fetch.mockResolvedValue({
        ok: true,
        text: async () => '<html><body>Test</body></html>',
      });

      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      await viewer.showPreview('mockups/page.htm');
      const iframe = document.querySelector('.preview-content iframe');
      expect(iframe).not.toBeNull();
    });

    it('should NOT show HTML files as preformatted text', async () => {
      globalThis.fetch.mockResolvedValue({
        ok: true,
        text: async () => '<html><body><h1>Hello</h1></body></html>',
      });

      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      await viewer.showPreview('mockups/design.html');
      const pre = document.querySelector('.preview-content pre');
      expect(pre).toBeNull();
    });
  });

  describe('TASK-680: Markdown preview uses ContentRenderer (same as folder browser)', () => {
    it('should use ContentRenderer for markdown files when available', async () => {
      const renderMarkdownSpy = vi.fn();
      globalThis.ContentRenderer = class {
        constructor() {}
        renderMarkdown(text) { renderMarkdownSpy(text); }
      };

      globalThis.fetch.mockResolvedValue({
        ok: true,
        text: async () => '# Heading with mermaid',
      });

      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      await viewer.showPreview('refined-idea/readme.md');
      expect(renderMarkdownSpy).toHaveBeenCalledWith('# Heading with mermaid');

      delete globalThis.ContentRenderer;
    });

    it('should fall back to marked.parse when ContentRenderer is not available', async () => {
      delete globalThis.ContentRenderer;

      globalThis.fetch.mockResolvedValue({
        ok: true,
        text: async () => '# Fallback',
      });

      const DV = globalThis.DeliverableViewer;
      expect(DV).toBeDefined();
      const viewer = new DV({ workflowName: 'hello' });
      await viewer.showPreview('refined-idea/readme.md');
      expect(globalThis.marked.parse).toHaveBeenCalledWith('# Fallback');
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
