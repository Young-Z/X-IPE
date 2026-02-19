/**
 * FEATURE-037-B: LinkExistingPanel tests (Vitest + jsdom)
 * Tests rendering, tree display, search filtering, file selection.
 */
import { describe, it, expect, beforeAll, beforeEach, vi } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import vm from 'vm';

const JS_PATH = resolve(import.meta.dirname, '../../src/x_ipe/static/js/features/compose-idea-modal.js');

beforeAll(() => {
  const code = readFileSync(JS_PATH, 'utf-8');
  const assignments = `
    globalThis.IdeaNameValidator = IdeaNameValidator;
    globalThis.AutoFolderNamer = AutoFolderNamer;
    globalThis.ComposeIdeaModal = ComposeIdeaModal;
    globalThis.LinkExistingPanel = LinkExistingPanel;
  `;
  vm.runInThisContext(code + assignments);
});

describe('LinkExistingPanel', () => {
  let container;
  let onSelect;

  beforeEach(() => {
    document.body.innerHTML = '';
    container = document.createElement('div');
    document.body.appendChild(container);
    onSelect = vi.fn();

    // Mock fetch for /api/ideas/tree
    globalThis.fetch = vi.fn(async (url) => {
      if (url === '/api/ideas/tree') {
        return {
          ok: true,
          json: async () => ({
            tree: [
              {
                name: 'Idea One',
                type: 'folder',
                children: [
                  { name: 'summary.md', type: 'file', path: 'x-ipe-docs/ideas/Idea One/summary.md' },
                  { name: 'notes.txt', type: 'file', path: 'x-ipe-docs/ideas/Idea One/notes.txt' },
                ],
              },
              {
                name: 'Idea Two',
                type: 'folder',
                children: [
                  { name: 'idea.md', type: 'file', path: 'x-ipe-docs/ideas/Idea Two/idea.md' },
                ],
              },
            ],
          }),
        };
      }
      return { ok: true, text: async () => '# Hello' };
    });
  });

  describe('render', () => {
    it('creates search input', () => {
      const panel = new LinkExistingPanel(container, { onSelect });
      panel.render();
      expect(container.querySelector('.link-existing-search-input')).not.toBeNull();
    });

    it('creates two-column layout (tree + preview)', () => {
      const panel = new LinkExistingPanel(container, { onSelect });
      panel.render();
      expect(container.querySelector('.link-existing-tree')).not.toBeNull();
      expect(container.querySelector('.link-existing-preview')).not.toBeNull();
    });

    it('fetches idea tree on render', async () => {
      const panel = new LinkExistingPanel(container, { onSelect });
      panel.render();
      await vi.waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/ideas/tree');
      });
    });

    it('renders folder and file items from API', async () => {
      const panel = new LinkExistingPanel(container, { onSelect });
      panel.render();
      await vi.waitFor(() => {
        const items = container.querySelectorAll('.link-existing-item');
        // 2 folders + 3 files = 5 items
        expect(items.length).toBe(5);
      });
    });

    it('renders folder items with 📁 icon', async () => {
      const panel = new LinkExistingPanel(container, { onSelect });
      panel.render();
      await vi.waitFor(() => {
        const items = container.querySelectorAll('.link-existing-item');
        expect(items[0].textContent).toContain('📁');
        expect(items[0].textContent).toContain('Idea One');
      });
    });

    it('renders file items with 📄 icon', async () => {
      const panel = new LinkExistingPanel(container, { onSelect });
      panel.render();
      await vi.waitFor(() => {
        const items = container.querySelectorAll('.link-existing-item');
        expect(items[1].textContent).toContain('📄');
        expect(items[1].textContent).toContain('summary.md');
      });
    });

    it('shows error message when API fails', async () => {
      globalThis.fetch = vi.fn(async () => { throw new Error('network error'); });
      const panel = new LinkExistingPanel(container, { onSelect });
      panel.render();
      await vi.waitFor(() => {
        expect(container.textContent).toContain('Failed to load ideas');
      });
    });
  });

  describe('_filterTree', () => {
    it('hides items that do not match search query', async () => {
      const panel = new LinkExistingPanel(container, { onSelect });
      panel.render();
      await vi.waitFor(() => {
        expect(container.querySelectorAll('.link-existing-item').length).toBe(5);
      });

      // Type a search query
      panel.searchInput.value = 'summary';
      panel.searchInput.dispatchEvent(new Event('input'));

      const items = container.querySelectorAll('.link-existing-item');
      const visible = [...items].filter(i => i.style.display !== 'none');
      expect(visible.length).toBe(1);
      expect(visible[0].textContent).toContain('summary.md');
    });

    it('is case-insensitive', async () => {
      const panel = new LinkExistingPanel(container, { onSelect });
      panel.render();
      await vi.waitFor(() => {
        expect(container.querySelectorAll('.link-existing-item').length).toBe(5);
      });

      panel.searchInput.value = 'IDEA TWO';
      panel.searchInput.dispatchEvent(new Event('input'));

      const items = container.querySelectorAll('.link-existing-item');
      const visible = [...items].filter(i => i.style.display !== 'none');
      expect(visible.length).toBeGreaterThanOrEqual(1);
      expect(visible[0].textContent).toContain('Idea Two');
    });

    it('shows all items when search is cleared', async () => {
      const panel = new LinkExistingPanel(container, { onSelect });
      panel.render();
      await vi.waitFor(() => {
        expect(container.querySelectorAll('.link-existing-item').length).toBe(5);
      });

      // Filter, then clear
      panel.searchInput.value = 'zzzzz';
      panel.searchInput.dispatchEvent(new Event('input'));
      const hidden = [...container.querySelectorAll('.link-existing-item')].filter(i => i.style.display === 'none');
      expect(hidden.length).toBe(5);

      panel.searchInput.value = '';
      panel.searchInput.dispatchEvent(new Event('input'));
      const allVisible = [...container.querySelectorAll('.link-existing-item')].filter(i => i.style.display !== 'none');
      expect(allVisible.length).toBe(5);
    });
  });

  describe('file selection', () => {
    it('adds selected class on click', async () => {
      const panel = new LinkExistingPanel(container, { onSelect });
      panel.render();
      await vi.waitFor(() => {
        expect(container.querySelectorAll('.link-existing-item').length).toBe(5);
      });

      const fileItems = [...container.querySelectorAll('.link-existing-item[data-path]')];
      fileItems[0].click();
      expect(fileItems[0].classList.contains('selected')).toBe(true);
    });

    it('calls onSelect with file path', async () => {
      const panel = new LinkExistingPanel(container, { onSelect });
      panel.render();
      await vi.waitFor(() => {
        expect(container.querySelectorAll('.link-existing-item').length).toBe(5);
      });

      const fileItems = [...container.querySelectorAll('.link-existing-item[data-path]')];
      fileItems[0].click();
      await vi.waitFor(() => {
        expect(onSelect).toHaveBeenCalledWith('x-ipe-docs/ideas/Idea One/summary.md');
      });
    });

    it('deselects previous when new file is clicked', async () => {
      const panel = new LinkExistingPanel(container, { onSelect });
      panel.render();
      await vi.waitFor(() => {
        expect(container.querySelectorAll('.link-existing-item').length).toBe(5);
      });

      const fileItems = [...container.querySelectorAll('.link-existing-item[data-path]')];
      fileItems[0].click();
      fileItems[1].click();
      expect(fileItems[0].classList.contains('selected')).toBe(false);
      expect(fileItems[1].classList.contains('selected')).toBe(true);
    });
  });

  describe('destroy', () => {
    it('clears container content', () => {
      const panel = new LinkExistingPanel(container, { onSelect });
      panel.render();
      panel.destroy();
      expect(container.innerHTML).toBe('');
    });

    it('resets selectedPath', () => {
      const panel = new LinkExistingPanel(container, { onSelect });
      panel.render();
      panel.selectedPath = 'test/path';
      panel.destroy();
      expect(panel.selectedPath).toBeNull();
    });
  });
});
