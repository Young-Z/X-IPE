import { beforeAll, beforeEach, afterEach, describe, expect, it, vi } from 'vitest';
import { loadFeatureScript } from './helpers.js';

beforeAll(() => {
  loadFeatureScript('../core/content-renderer.js');
  loadFeatureScript('../core/file-preview-renderer.js');
  loadFeatureScript('workplace.js');
});

beforeEach(() => {
  document.body.innerHTML = '<div id="preview"></div>';
  URL.createObjectURL = vi.fn(() => 'blob:in-memory');
  URL.revokeObjectURL = vi.fn();
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true, text: async () => '<div id="app"></div>', headers: { get: () => null },
  }));
});

afterEach(() => vi.unstubAllGlobals());

describe('saved HTML directory context', () => {
  const path = 'mockups/space # & \u6d4b\u8bd5/index.html';
  const url = '/api/file/preview/' + path.split('/').map(encodeURIComponent).join('/');

  it('retains the metadata path when rendered without load()', () => {
    const renderer = new ContentRenderer('preview');
    renderer.render({ type: 'html', path, content: '<div id="app"></div>' });
    expect(document.querySelector('iframe').getAttribute('src')).toBe(url);
    expect(renderer.currentPath).toBe(path);
    expect(URL.createObjectURL).not.toHaveBeenCalled();
    expect(document.querySelector('iframe').getAttribute('sandbox')).toBe('allow-scripts allow-same-origin');
  });

  it('uses the saved Workplace path and revokes an earlier blob', () => {
    const manager = Object.create(WorkplaceManager.prototype);
    manager.currentPath = path;
    manager._htmlBlobUrl = 'blob:previous';
    document.getElementById('preview').innerHTML = manager._renderHtmlPreview('<div></div>');
    expect(document.querySelector('iframe').getAttribute('src')).toBe(url);
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:previous');
    expect(manager._htmlBlobUrl).toBeNull();
  });

  it.each([
    ['/api/file/raw?path={path}', path, url],
    ['/api/ideas/file?path={path}', path, url],
    ['/api/kb/files/{path}/raw', path, url.replace('/preview/', '/preview/x-ipe-docs/memory/')],
  ])('renders saved files from %s', async (apiEndpoint, filePath, expected) => {
    const renderer = new FilePreviewRenderer({ apiEndpoint });
    await renderer.renderPreview(filePath, document.getElementById('preview'));
    expect(document.querySelector('iframe').getAttribute('src')).toBe(expected);
    expect(URL.createObjectURL).not.toHaveBeenCalled();
    expect(document.querySelector('iframe').getAttribute('sandbox')).toBe('allow-scripts allow-same-origin');
  });

  it('preserves in-memory HTML without retaining a previous metadata path', () => {
    const renderer = new ContentRenderer('preview');
    renderer.render({ type: 'html', path, content: 'saved' });
    renderer.render({ type: 'html', content: '<h1>In memory</h1>' });
    expect(document.querySelector('iframe').getAttribute('src')).toBe('blob:in-memory');
    expect(URL.createObjectURL).toHaveBeenCalled();
    renderer.render({ type: 'html', path, content: 'saved' });
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:in-memory');
  });

  it('preserves shared renderer no-path HTML and converted documents as blobs', () => {
    const renderer = new FilePreviewRenderer();
    const container = document.getElementById('preview');
    renderer._renderHtml(container, '<h1>In memory</h1>');
    expect(container.querySelector('iframe').getAttribute('src')).toBe('blob:in-memory');
    renderer._renderContent(container, '<h1>Converted</h1>', 'example.docx', true);
    expect(container.querySelector('iframe').getAttribute('src')).toBe('blob:in-memory');
    expect(container.querySelector('iframe').getAttribute('sandbox')).toBe('allow-same-origin');
  });

  it('keeps source mode inert and toggles back to saved preview', async () => {
    const renderer = new FilePreviewRenderer({ renderMode: 'raw' });
    const container = document.getElementById('preview');
    await renderer.renderPreview(path, container);
    expect(container.querySelector('iframe')).toBeNull();
    expect(container.querySelector('pre').textContent).toBe('<div id="app"></div>');
    renderer.setRenderMode('auto', container);
    expect(container.querySelector('iframe').getAttribute('src')).toBe(url);
  });
});
