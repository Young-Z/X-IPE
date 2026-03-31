/**
 * TASK-1034: KB article preview does not render markdown images
 *
 * Bug: Markdown image syntax ![alt](relative/path.png) is not converted
 * to <img> tags with resolved API URLs in the KB article preview.
 * The image files exist, but the preview shows broken images because
 * relative paths aren't resolved to /api/kb/files/{dir}/{path}/raw endpoints.
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import vm from 'vm';
import { loadFeatureScript } from './helpers.js';

// Load real marked.js library so custom renderer.image is exercised
const PROJECT_ROOT = resolve(import.meta.dirname, '..', '..');
const markedCode = readFileSync(resolve(PROJECT_ROOT, 'src/x_ipe/static/3rdparty/js/marked.min.js'), 'utf-8');
vm.runInThisContext(
  '(function(){var exports={};var module={exports:exports};' + markedCode + ';globalThis.marked=module.exports;})();'
);

let _loaded = false;
function ensureLoaded() {
  if (!_loaded) {
    loadFeatureScript('../core/content-renderer.js');
    loadFeatureScript('../core/file-preview-renderer.js');
    _loaded = true;
  }
  return typeof globalThis.FilePreviewRenderer !== 'undefined';
}

describe('TASK-1034: KB markdown image rendering', () => {
  let container;

  beforeEach(() => {
    ensureLoaded();
    document.body.innerHTML = '<div id="preview"></div>';
    container = document.getElementById('preview');
    globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
    globalThis.URL.revokeObjectURL = vi.fn();
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  describe('Image path resolution in markdown preview', () => {
    it('should resolve relative image paths to KB API URLs', async () => {
      const mdContent = '# Create Workflow\n\n![Workflow Overview](screenshots/workflow-mode-overview.png)\n\nSome text after.';
      const filePath = '.intake/user-manual/05-workflows/workflow01.md';

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        text: async () => mdContent,
        headers: { get: () => null }
      });

      const renderer = new FilePreviewRenderer({
        apiEndpoint: '/api/kb/files/{path}/raw',
        endpointStyle: 'path'
      });
      await renderer.renderPreview(filePath, container);

      const img = container.querySelector('img');
      expect(img).not.toBeNull();
      // The image src should be resolved to the KB API endpoint
      // combining the article's directory with the relative image path
      expect(img.src).toContain('/api/kb/files/');
      expect(img.src).toContain('.intake/user-manual/05-workflows/screenshots/workflow-mode-overview.png');
      expect(img.src).toContain('/raw');
    });

    it('should resolve relative image paths without leading dot-slash', async () => {
      const mdContent = '![Diagram](images/diagram.png)';
      const filePath = 'docs/section/article.md';

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        text: async () => mdContent,
        headers: { get: () => null }
      });

      const renderer = new FilePreviewRenderer({
        apiEndpoint: '/api/kb/files/{path}/raw',
        endpointStyle: 'path'
      });
      await renderer.renderPreview(filePath, container);

      const img = container.querySelector('img');
      expect(img).not.toBeNull();
      expect(img.src).toContain('/api/kb/files/');
      expect(img.src).toContain('docs/section/images/diagram.png');
      expect(img.src).toContain('/raw');
    });

    it('should not rewrite absolute URLs (http/https)', async () => {
      const mdContent = '![External](https://example.com/image.png)';
      const filePath = 'docs/article.md';

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        text: async () => mdContent,
        headers: { get: () => null }
      });

      const renderer = new FilePreviewRenderer({
        apiEndpoint: '/api/kb/files/{path}/raw',
        endpointStyle: 'path'
      });
      await renderer.renderPreview(filePath, container);

      const img = container.querySelector('img');
      expect(img).not.toBeNull();
      expect(img.src).toBe('https://example.com/image.png');
    });

    it('should not rewrite data: URIs', async () => {
      const mdContent = '![Inline](data:image/png;base64,abc123)';
      const filePath = 'docs/article.md';

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        text: async () => mdContent,
        headers: { get: () => null }
      });

      const renderer = new FilePreviewRenderer({
        apiEndpoint: '/api/kb/files/{path}/raw',
        endpointStyle: 'path'
      });
      await renderer.renderPreview(filePath, container);

      const img = container.querySelector('img');
      expect(img).not.toBeNull();
      expect(img.src).toBe('data:image/png;base64,abc123');
    });

    it('should not rewrite root-relative paths (starting with /)', async () => {
      const mdContent = '![Root](/static/images/logo.png)';
      const filePath = 'docs/article.md';

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        text: async () => mdContent,
        headers: { get: () => null }
      });

      const renderer = new FilePreviewRenderer({
        apiEndpoint: '/api/kb/files/{path}/raw',
        endpointStyle: 'path'
      });
      await renderer.renderPreview(filePath, container);

      const img = container.querySelector('img');
      expect(img).not.toBeNull();
      expect(img.src).toContain('/static/images/logo.png');
      expect(img.src).not.toContain('/api/kb/files/');
    });

    it('should handle multiple images in one markdown file', async () => {
      const mdContent = '![A](screenshots/a.png)\n\n![B](screenshots/b.png)';
      const filePath = 'folder/article.md';

      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        text: async () => mdContent,
        headers: { get: () => null }
      });

      const renderer = new FilePreviewRenderer({
        apiEndpoint: '/api/kb/files/{path}/raw',
        endpointStyle: 'path'
      });
      await renderer.renderPreview(filePath, container);

      const imgs = container.querySelectorAll('img');
      expect(imgs.length).toBe(2);
      expect(imgs[0].src).toContain('folder/screenshots/a.png');
      expect(imgs[1].src).toContain('folder/screenshots/b.png');
    });
  });

  describe('ContentRenderer.renderMarkdown with basePath', () => {
    it('should accept optional basePath and resolve image paths', () => {
      const cr = new ContentRenderer(container);
      cr.renderMarkdown(
        '![Screenshot](screenshots/test.png)',
        'kb-folder/article.md'
      );

      const img = container.querySelector('img');
      expect(img).not.toBeNull();
      expect(img.src).toContain('/api/kb/files/');
      expect(img.src).toContain('kb-folder/screenshots/test.png');
      expect(img.src).toContain('/raw');
    });

    it('should render images normally when no basePath is provided', () => {
      const cr = new ContentRenderer(container);
      cr.renderMarkdown('![Alt](screenshots/test.png)');

      const img = container.querySelector('img');
      expect(img).not.toBeNull();
      // Without basePath, should use default behavior (no rewriting)
      expect(img.src).toContain('screenshots/test.png');
    });
  });
});
