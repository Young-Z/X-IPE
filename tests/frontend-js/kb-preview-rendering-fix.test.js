/**
 * TASK-989: KB Preview Rendering Fixes
 *
 * Bug 1: Preview window height not fully utilizing available space
 *   - .kb-article-main needs flex column layout
 *   - .kb-article-content needs flex: 1 to fill remaining space
 *
 * Bug 2: Docx icons (avatars) render at oversized native dimensions
 *   - _renderConvertedHtml should inject a base stylesheet constraining
 *     inline images to text-relative sizes
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import { loadFeatureScript } from './helpers.js';

/* ───────────────────────────
   Part A: CSS Layout Tests
   ─────────────────────────── */

const CSS_PATH = resolve(
  __dirname,
  '../../src/x_ipe/static/css/kb-browse-modal.css'
);
const cssContent = readFileSync(CSS_PATH, 'utf-8');

function getCssBlock(css, selector) {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp(`${escaped}\\s*\\{([^}]+)\\}`, 'g');
  const matches = [];
  let m;
  while ((m = re.exec(css)) !== null) {
    matches.push(m[1]);
  }
  return matches.join('\n');
}

describe('TASK-989 Bug 1: Preview height utilization', () => {
  it('.kb-article-main should be a flex column container', () => {
    const block = getCssBlock(cssContent, '.kb-article-main');
    expect(block).toContain('display: flex');
    expect(block).toContain('flex-direction: column');
  });

  it('.kb-article-content should flex-grow to fill remaining space', () => {
    const block = getCssBlock(cssContent, '.kb-article-content');
    expect(block).toContain('flex: 1');
    expect(block).toContain('min-height: 0');
  });
});

/* ───────────────────────────
   Part B: Converted HTML Stylesheet Injection Tests
   ─────────────────────────── */

let _loaded = false;
function ensureLoaded() {
  if (!_loaded) {
    loadFeatureScript('../core/content-renderer.js');
    loadFeatureScript('../core/file-preview-renderer.js');
    _loaded = true;
  }
  return typeof globalThis.FilePreviewRenderer !== 'undefined';
}

describe('TASK-989 Bug 2: Docx icon rendering', () => {
  let container;
  let capturedBlobContent;

  beforeEach(() => {
    ensureLoaded();
    document.body.innerHTML = '<div id="preview"></div>';
    container = document.getElementById('preview');

    // Capture blob content passed to createObjectURL
    capturedBlobContent = null;
    globalThis.URL.createObjectURL = vi.fn((blob) => {
      // Read the blob content synchronously via the Blob polyfill
      if (blob && typeof blob.text === 'function') {
        blob.text().then(t => { capturedBlobContent = t; });
      }
      return 'blob:mock-url';
    });
    globalThis.URL.revokeObjectURL = vi.fn();
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('should inject a base stylesheet into converted HTML', async () => {
    const docxHtml = '<p><img src="data:image/png;base64,abc123"><strong>Person Name</strong></p>';
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      text: async () => docxHtml,
      headers: { get: (h) => h === 'X-Converted' ? 'true' : null }
    });

    const renderer = new FilePreviewRenderer({
      apiEndpoint: '/api/kb/files/{path}/raw',
      endpointStyle: 'path'
    });
    await renderer.renderPreview('doc.docx', container);

    // Wait for blob.text() promise
    await new Promise(r => setTimeout(r, 10));

    expect(capturedBlobContent).not.toBeNull();
    expect(capturedBlobContent).toContain('<style');
    expect(capturedBlobContent).toContain(docxHtml);
  });

  it('should constrain inline images with max-height in injected styles', async () => {
    const docxHtml = '<p><img src="data:image/png;base64,abc"><strong>Name</strong></p>';
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      text: async () => docxHtml,
      headers: { get: (h) => h === 'X-Converted' ? 'true' : null }
    });

    const renderer = new FilePreviewRenderer({
      apiEndpoint: '/api/kb/files/{path}/raw',
      endpointStyle: 'path'
    });
    await renderer.renderPreview('doc.docx', container);

    await new Promise(r => setTimeout(r, 10));

    expect(capturedBlobContent).toContain('max-height');
    expect(capturedBlobContent).toContain('vertical-align');
  });

  it('should allow standalone images to display at larger sizes', async () => {
    const docxHtml = '<p><img src="data:image/png;base64,diagram123"></p>';
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      text: async () => docxHtml,
      headers: { get: (h) => h === 'X-Converted' ? 'true' : null }
    });

    const renderer = new FilePreviewRenderer({
      apiEndpoint: '/api/kb/files/{path}/raw',
      endpointStyle: 'path'
    });
    await renderer.renderPreview('doc.docx', container);

    await new Promise(r => setTimeout(r, 10));

    // Standalone images (:only-child) should not be constrained to text-height
    expect(capturedBlobContent).toContain('only-child');
    expect(capturedBlobContent).toContain('max-width');
  });

  it('should hide br tags after inline images to preserve inline flow', async () => {
    const docxHtml = '<p><img src="data:image/png;base64,abc"><strong><br>Warren WANG </strong>已开始听录</p>';
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      text: async () => docxHtml,
      headers: { get: (h) => h === 'X-Converted' ? 'true' : null }
    });

    const renderer = new FilePreviewRenderer({
      apiEndpoint: '/api/kb/files/{path}/raw',
      endpointStyle: 'path'
    });
    await renderer.renderPreview('doc.docx', container);

    await new Promise(r => setTimeout(r, 10));

    // CSS rules to hide br tags that break inline image+text flow
    expect(capturedBlobContent).toContain('img + br { display: none');
    expect(capturedBlobContent).toContain('img + * > br:first-child { display: none');
  });

  it('should NOT inject stylesheet for regular HTML files', async () => {
    const htmlContent = '<html><body><img src="photo.jpg"></body></html>';
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      text: async () => htmlContent,
      headers: { get: () => null }
    });

    const renderer = new FilePreviewRenderer({
      apiEndpoint: '/api/kb/files/{path}/raw',
      endpointStyle: 'path'
    });
    await renderer.renderPreview('page.html', container);

    await new Promise(r => setTimeout(r, 10));

    // Regular HTML should be rendered as-is without injected styles
    if (capturedBlobContent) {
      expect(capturedBlobContent).not.toContain('docx-preview-base');
    }
  });
});
