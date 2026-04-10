/**
 * TASK-4873: Source file modal must be a full two-panel browser
 * matching FolderBrowserModal (tree view + file preview).
 *
 * Validates: DOM structure, tree building from flat paths, file selection,
 * search/filter, breadcrumb, preview panel, keyboard a11y, close handlers.
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import vm from 'vm';

const JS_FEATURES = resolve(import.meta.dirname, '..', '..', 'src/x_ipe/static/js/features');

function loadScript(filename) {
  const code = readFileSync(resolve(JS_FEATURES, filename), 'utf-8');
  vm.runInThisContext(code);
}

describe('TASK-4873: Source file modal two-panel browser', () => {
  let restoreFetch;

  beforeEach(() => {
    document.body.innerHTML = '';

    // Load only once per suite (class declarations are global)
    if (!globalThis._ogvSourceModalLoaded) {
      // Mock cytoscape before loading scripts that reference it
      globalThis.cytoscape = vi.fn(() => ({
        on: vi.fn(), style: vi.fn().mockReturnThis(), layout: vi.fn().mockReturnValue({ run: vi.fn() }),
        nodes: vi.fn().mockReturnValue({ length: 0, on: vi.fn(), forEach: vi.fn() }),
        edges: vi.fn().mockReturnValue({ length: 0, on: vi.fn(), forEach: vi.fn() }),
        fit: vi.fn(), zoom: vi.fn(), pan: vi.fn(), resize: vi.fn(), png: vi.fn(() => ''),
        destroy: vi.fn(), container: vi.fn(), getElementById: vi.fn(),
      }));
      loadScript('folder-browser-modal.js');
      loadScript('ontology-graph-canvas.js');
      loadScript('ontology-graph-viewer.js');
      globalThis._ogvSourceModalLoaded = true;
    }

    // Mock fetch for file preview
    const origFetch = globalThis.fetch;
    globalThis.fetch = vi.fn(async () => ({
      ok: true, text: async () => '# Hello', json: async () => ({}),
    }));
    restoreFetch = () => { globalThis.fetch = origFetch; };
  });

  afterEach(() => {
    if (restoreFetch) restoreFetch();
    document.body.innerHTML = '';
  });

  function callShowSourceFilesModal(files, nodeData) {
    const container = document.createElement('div');
    document.body.appendChild(container);
    const viewer = new OntologyGraphViewer(container);
    viewer._showSourceFilesModal(files, nodeData || { id: 'test', label: 'TestNode' });
  }

  it('creates a folder-browser-backdrop element (reuses FolderBrowserModal CSS)', () => {
    callShowSourceFilesModal(['docs/auth.md', 'src/api/login.py']);
    const backdrop = document.body.querySelector('.folder-browser-backdrop');
    expect(backdrop).toBeTruthy();
  });

  it('has two-panel layout: tree panel and preview panel', () => {
    callShowSourceFilesModal(['docs/auth.md']);
    const tree = document.body.querySelector('.folder-browser-tree');
    const preview = document.body.querySelector('.folder-browser-preview');
    expect(tree).toBeTruthy();
    expect(preview).toBeTruthy();
  });

  it('builds a tree structure from flat file paths', () => {
    callShowSourceFilesModal([
      'docs/auth.md',
      'docs/api.md',
      'src/login.py',
    ]);
    const treeItems = document.body.querySelectorAll('.tree-item');
    expect(treeItems.length).toBeGreaterThanOrEqual(3);
  });

  it('groups files into directory folders in the tree', () => {
    callShowSourceFilesModal([
      'docs/auth.md',
      'docs/api.md',
      'src/login.py',
    ]);
    const dirItems = document.body.querySelectorAll('.dir-item');
    expect(dirItems.length).toBeGreaterThanOrEqual(2); // docs/ and src/
  });

  it('has a search/filter input in the tree panel', () => {
    callShowSourceFilesModal(['docs/auth.md']);
    const searchInput = document.body.querySelector('.folder-browser-search-input');
    expect(searchInput).toBeTruthy();
    expect(searchInput.placeholder).toContain('Filter');
  });

  it('has a breadcrumb showing the node label', () => {
    callShowSourceFilesModal(['docs/auth.md'], { id: 'n1', label: 'Authentication' });
    const breadcrumb = document.body.querySelector('.folder-browser-breadcrumb');
    expect(breadcrumb).toBeTruthy();
    expect(breadcrumb.textContent).toContain('Authentication');
  });

  it('shows "Select a file to preview" in preview panel initially', () => {
    callShowSourceFilesModal(['docs/auth.md']);
    const preview = document.body.querySelector('.folder-browser-preview');
    expect(preview.textContent).toContain('Select a file to preview');
  });

  it('has a close button', () => {
    callShowSourceFilesModal(['docs/auth.md']);
    const closeBtn = document.body.querySelector('.folder-browser-close');
    expect(closeBtn).toBeTruthy();
  });

  it('closes on close button click', () => {
    callShowSourceFilesModal(['docs/auth.md']);
    const closeBtn = document.body.querySelector('.folder-browser-close');
    closeBtn.click();
    // Backdrop should have .active removed immediately
    const backdrop = document.body.querySelector('.folder-browser-backdrop');
    if (backdrop) {
      expect(backdrop.classList.contains('active')).toBe(false);
    }
  });

  it('closes on Escape key', () => {
    callShowSourceFilesModal(['docs/auth.md']);
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    const backdrop = document.body.querySelector('.folder-browser-backdrop');
    if (backdrop) {
      expect(backdrop.classList.contains('active')).toBe(false);
    }
  });

  it('file items have data-path attributes for preview fetch', () => {
    callShowSourceFilesModal(['docs/auth.md', 'src/login.py']);
    const fileItems = document.body.querySelectorAll('.file-item[data-path]');
    expect(fileItems.length).toBeGreaterThanOrEqual(2);
    const paths = Array.from(fileItems).map(el => el.dataset.path);
    expect(paths).toContain('docs/auth.md');
    expect(paths).toContain('src/login.py');
  });

  it('has a modal dialog with proper ARIA attributes', () => {
    callShowSourceFilesModal(['docs/auth.md']);
    const modal = document.body.querySelector('.folder-browser-modal');
    expect(modal).toBeTruthy();
    expect(modal.getAttribute('role')).toBe('dialog');
    expect(modal.getAttribute('aria-modal')).toBe('true');
  });

  it('header title includes node label and source files icon', () => {
    callShowSourceFilesModal(['docs/auth.md'], { id: 'n1', label: 'Auth Module' });
    const title = document.body.querySelector('.folder-browser-title');
    expect(title).toBeTruthy();
    expect(title.textContent).toContain('Auth Module');
  });

  it('handles empty file list gracefully', () => {
    callShowSourceFilesModal([], { id: 'n1', label: 'Empty' });
    const treeContent = document.body.querySelector('.folder-browser-tree-content');
    expect(treeContent).toBeTruthy();
    expect(treeContent.textContent).toMatch(/no.*files|empty/i);
  });

  it('removes previous modal when opening a new one', () => {
    callShowSourceFilesModal(['docs/a.md']);
    callShowSourceFilesModal(['docs/b.md']);
    const backdrops = document.body.querySelectorAll('.folder-browser-backdrop');
    expect(backdrops.length).toBe(1);
  });
});
