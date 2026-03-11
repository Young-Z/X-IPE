/**
 * Tests for FEATURE-049-D: KB Article Editor
 * Tests: Modal lifecycle, form rendering, tag chips, frontmatter, save/edit
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { loadFeatureScript } from './helpers.js';

let _implLoaded = false;
function ensureImpl() {
  if (!_implLoaded) {
    try {
      loadFeatureScript('kb-article-editor.js');
      _implLoaded = true;
    } catch { /* not yet implemented */ }
  }
  return typeof globalThis.KBArticleEditor !== 'undefined';
}

describe('FEATURE-049-D: KB Article Editor', () => {
  let editor;

  beforeEach(() => {
    document.body.innerHTML = '';
    document.body.style.overflow = '';
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        tags: {
          lifecycle: ['Ideation', 'Design', 'Implementation'],
          domain: ['API', 'UI-UX', 'Security']
        }
      })
    });
    // Stub EasyMDE as a proper constructor
    globalThis.EasyMDE = class MockEasyMDE {
      constructor() {
        this._value = '';
        this.codemirror = { on: vi.fn() };
      }
      value(v) { if (v !== undefined) this._value = v; return this._value; }
      toTextArea() {}
    };
    ensureImpl();
  });

  afterEach(() => {
    document.querySelectorAll('.kb-editor-overlay').forEach(el => el.remove());
    document.body.style.overflow = '';
  });

  describe('Class Export', () => {
    it('should export KBArticleEditor class', () => {
      expect(globalThis.KBArticleEditor).toBeDefined();
    });

    it('should accept options in constructor', () => {
      const KBE = globalThis.KBArticleEditor;
      const ed = new KBE({ folder: 'test', editPath: null });
      expect(ed).toBeDefined();
      expect(ed.editMode).toBe(false);
    });

    it('should set editMode when editPath provided', () => {
      const KBE = globalThis.KBArticleEditor;
      const ed = new KBE({ editPath: 'docs/guide.md' });
      expect(ed.editMode).toBe(true);
    });
  });

  describe('AC-049-D-02: Modal Shell', () => {
    it('should create overlay with kb-editor-overlay class', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      const overlay = document.querySelector('.kb-editor-overlay');
      expect(overlay).not.toBeNull();
    });

    it('should add active class on open', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      // requestAnimationFrame mock - trigger manually
      await new Promise(r => setTimeout(r, 50));
      const overlay = document.querySelector('.kb-editor-overlay');
      expect(overlay.classList.contains('active')).toBe(true);
    });

    it('should show header with "New Article" for create mode', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      const header = document.querySelector('.kb-editor-header h3');
      expect(header.textContent).toContain('New Article');
    });

    it('should show header with "Edit Article" for edit mode', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ editPath: 'docs/guide.md' });
      await editor.open();
      const header = document.querySelector('.kb-editor-header h3');
      expect(header.textContent).toContain('Edit Article');
    });
  });

  describe('AC-049-D-04: Frontmatter Form', () => {
    it('should render title input', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      const titleInput = document.querySelector('.kb-editor-title');
      expect(titleInput).not.toBeNull();
    });

    it('should render lifecycle tag chips', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      const chips = document.querySelectorAll('.kb-chip-lifecycle');
      expect(chips.length).toBe(3); // Ideation, Design, Implementation
    });

    it('should render domain tag chips', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      const chips = document.querySelectorAll('.kb-chip-domain');
      expect(chips.length).toBe(3); // API, UI-UX, Security
    });

    it('should toggle tag chip active on click', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      const chip = document.querySelector('.kb-chip-lifecycle');
      expect(chip.classList.contains('active')).toBe(false);
      chip.click();
      expect(chip.classList.contains('active')).toBe(true);
      chip.click();
      expect(chip.classList.contains('active')).toBe(false);
    });
  });

  describe('AC-049-D-03: EasyMDE Editor', () => {
    it('should initialize EasyMDE', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      await new Promise(r => setTimeout(r, 50));
      expect(editor.easyMDE).not.toBeNull();
    });

    it('should clean up EasyMDE on close (NFR-049-D-04)', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      await new Promise(r => setTimeout(r, 50));
      expect(editor.easyMDE).not.toBeNull();
      editor.close(true);
      expect(editor.easyMDE).toBeNull();
    });
  });

  describe('AC-049-D-06: Save Creates File', () => {
    it('should disable save button when title is empty', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      const saveBtn = document.querySelector('.kb-editor-btn-save');
      expect(saveBtn.disabled).toBe(true);
    });

    it('should enable save button when title is provided', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      const titleInput = document.querySelector('.kb-editor-title');
      titleInput.value = 'My Article';
      titleInput.dispatchEvent(new Event('input'));
      const saveBtn = document.querySelector('.kb-editor-btn-save');
      expect(saveBtn.disabled).toBe(false);
    });

    it('should call POST /api/kb/files for new articles', async () => {
      if (!globalThis.KBArticleEditor) return;
      const mockFetch = vi.fn()
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ tags: { lifecycle: [], domain: [] } }) })
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ path: 'test/my-article.md' }) });
      globalThis.fetch = mockFetch;
      
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      
      const titleInput = document.querySelector('.kb-editor-title');
      titleInput.value = 'My Article';
      titleInput.dispatchEvent(new Event('input'));
      
      await editor._save();
      
      const saveCalls = mockFetch.mock.calls.filter(c => c[0] === '/api/kb/files');
      expect(saveCalls.length).toBe(1);
      expect(saveCalls[0][1].method).toBe('POST');
    });
  });

  describe('AC-049-D-09: kb:changed Event', () => {
    it('should dispatch kb:changed on successful save', async () => {
      if (!globalThis.KBArticleEditor) return;
      const mockFetch = vi.fn()
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ tags: { lifecycle: [], domain: [] } }) })
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({}) });
      globalThis.fetch = mockFetch;
      
      const eventSpy = vi.fn();
      document.addEventListener('kb:changed', eventSpy);
      
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      
      document.querySelector('.kb-editor-title').value = 'Test';
      document.querySelector('.kb-editor-title').dispatchEvent(new Event('input'));
      
      await editor._save();
      
      expect(eventSpy).toHaveBeenCalled();
      document.removeEventListener('kb:changed', eventSpy);
    });
  });

  describe('AC-049-D-05: Auto-Populated Fields & Frontmatter Building', () => {
    it('should build valid YAML frontmatter', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      
      document.querySelector('.kb-editor-title').value = 'Test Article';
      editor.selectedTags.lifecycle.add('Design');
      editor.selectedTags.domain.add('API');
      
      const fm = editor._buildFrontmatter();
      expect(fm).toContain('title: "Test Article"');
      expect(fm).toContain('author: user');
      expect(fm).toContain('auto_generated: false');
      expect(fm).toContain('- Design');
      expect(fm).toContain('- API');
      expect(fm.startsWith('---\n')).toBe(true);
      expect(fm.endsWith('---\n')).toBe(true);
    });

    it('should auto-populate created date with today', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      document.querySelector('.kb-editor-title').value = 'Date Test';
      const fm = editor._buildFrontmatter();
      const today = new Date().toISOString().split('T')[0];
      expect(fm).toContain(`created: "${today}"`);
    });

    it('should omit tags section when no tags selected', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      document.querySelector('.kb-editor-title').value = 'No Tags';
      const fm = editor._buildFrontmatter();
      expect(fm).not.toContain('tags:');
    });
  });

  describe('Filename Sanitization', () => {
    it('should sanitize title for filename', () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      expect(editor._sanitizeFilename('My Test Article!')).toBe('my-test-article');
      expect(editor._sanitizeFilename('Hello   World')).toBe('hello-world');
      expect(editor._sanitizeFilename('API & Auth Guide')).toBe('api-auth-guide');
    });
  });

  describe('Frontmatter Parsing', () => {
    it('should parse frontmatter from content', () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      const content = '---\ntitle: "My Guide"\nauthor: user\ntags:\n  lifecycle:\n    - Design\n  domain:\n    - API\n---\n# Hello';
      const { frontmatter, body } = editor._parseFrontmatter(content);
      expect(frontmatter.title).toBe('"My Guide"');
      expect(frontmatter.tags.lifecycle).toContain('Design');
      expect(frontmatter.tags.domain).toContain('API');
      expect(body).toBe('# Hello');
    });

    it('should handle content without frontmatter', () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      const { frontmatter, body } = editor._parseFrontmatter('# Just content');
      expect(Object.keys(frontmatter).length).toBe(0);
      expect(body).toBe('# Just content');
    });
  });

  describe('Modal Close', () => {
    it('should remove overlay on close', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      editor.close(true);
      await new Promise(r => setTimeout(r, 350));
      expect(document.querySelector('.kb-editor-overlay')).toBeNull();
    });

    it('should restore body scroll on close', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      expect(document.body.style.overflow).toBe('hidden');
      editor.close(true);
      expect(document.body.style.overflow).toBe('');
    });
  });

  describe('AC-049-D-07: Edit Existing Article', () => {
    it('should load existing article and pre-populate title', async () => {
      if (!globalThis.KBArticleEditor) return;
      const existingContent = '---\ntitle: My Guide\nauthor: user\ntags:\n  lifecycle:\n    - Design\n  domain:\n    - API\n---\n# Hello World';
      globalThis.fetch = vi.fn()
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ tags: { lifecycle: ['Ideation', 'Design'], domain: ['API', 'UI-UX'] } }) })
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ content: existingContent }) });

      editor = new globalThis.KBArticleEditor({ editPath: 'docs/guide.md' });
      await editor.open();
      await new Promise(r => setTimeout(r, 100));

      const titleInput = document.querySelector('.kb-editor-title');
      expect(titleInput.value).toBe('My Guide');
    });

    it('should pre-populate tags from existing article', async () => {
      if (!globalThis.KBArticleEditor) return;
      const existingContent = '---\ntitle: "My Guide"\ntags:\n  lifecycle:\n    - Design\n  domain:\n    - API\n---\nBody';
      globalThis.fetch = vi.fn()
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ tags: { lifecycle: ['Ideation', 'Design'], domain: ['API', 'UI-UX'] } }) })
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ content: existingContent }) });

      editor = new globalThis.KBArticleEditor({ editPath: 'docs/guide.md' });
      await editor.open();
      await new Promise(r => setTimeout(r, 100));

      expect(editor.selectedTags.lifecycle.has('Design')).toBe(true);
      expect(editor.selectedTags.domain.has('API')).toBe(true);
      const designChip = document.querySelector('.kb-chip-lifecycle[data-tag="Design"]');
      expect(designChip.classList.contains('active')).toBe(true);
    });

    it('should call PUT for edit mode save', async () => {
      if (!globalThis.KBArticleEditor) return;
      const mockFetch = vi.fn()
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ tags: { lifecycle: [], domain: [] } }) })
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({}) });
      globalThis.fetch = mockFetch;

      editor = new globalThis.KBArticleEditor({ editPath: 'docs/guide.md' });
      await editor.open();
      document.querySelector('.kb-editor-title').value = 'Updated Title';
      document.querySelector('.kb-editor-title').dispatchEvent(new Event('input'));
      await editor._save();

      const putCalls = mockFetch.mock.calls.filter(c =>
        typeof c[0] === 'string' && c[0].includes('/api/kb/files/') && c[1]?.method === 'PUT'
      );
      expect(putCalls.length).toBe(1);
    });
  });

  describe('AC-049-D-08: Cancel with Confirmation', () => {
    it('should prompt confirmation when closing with unsaved changes', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();

      // Make dirty
      const titleInput = document.querySelector('.kb-editor-title');
      titleInput.value = 'Unsaved';
      titleInput.dispatchEvent(new Event('input'));
      expect(editor.dirty).toBe(true);

      globalThis.confirm = vi.fn().mockReturnValue(false);
      editor.close();
      // Should NOT close because user declined
      expect(globalThis.confirm).toHaveBeenCalled();
      expect(document.querySelector('.kb-editor-overlay')).not.toBeNull();
      // Force-close to clean up escape handler for subsequent tests
      editor.close(true);
    });

    it('should close when user confirms discard', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();

      const titleInput = document.querySelector('.kb-editor-title');
      titleInput.value = 'Unsaved';
      titleInput.dispatchEvent(new Event('input'));

      globalThis.confirm = vi.fn().mockReturnValue(true);
      editor.close();
      expect(globalThis.confirm).toHaveBeenCalled();
      await new Promise(r => setTimeout(r, 350));
      expect(document.querySelector('.kb-editor-overlay')).toBeNull();
    });

    it('should close without confirmation when not dirty', async () => {
      if (!globalThis.KBArticleEditor) return;
      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      expect(editor.dirty).toBe(false);

      globalThis.confirm = vi.fn();
      editor.close();
      expect(globalThis.confirm).not.toHaveBeenCalled();
    });
  });

  describe('Edge Cases: Save Errors', () => {
    it('should show error toast on save failure', async () => {
      if (!globalThis.KBArticleEditor) return;
      globalThis.fetch = vi.fn()
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ tags: { lifecycle: [], domain: [] } }) })
        .mockResolvedValueOnce({ ok: false, json: () => Promise.resolve({ error: 'File already exists' }) });

      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      document.querySelector('.kb-editor-title').value = 'Duplicate';
      document.querySelector('.kb-editor-title').dispatchEvent(new Event('input'));
      await editor._save();

      const toast = document.querySelector('.kb-editor-toast');
      expect(toast.textContent).toBe('File already exists');
      expect(toast.classList.contains('kb-toast-error')).toBe(true);
    });

    it('should re-enable save button on error', async () => {
      if (!globalThis.KBArticleEditor) return;
      globalThis.fetch = vi.fn()
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ tags: { lifecycle: [], domain: [] } }) })
        .mockResolvedValueOnce({ ok: false, json: () => Promise.resolve({ error: 'Conflict' }) });

      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      document.querySelector('.kb-editor-title').value = 'Error Test';
      document.querySelector('.kb-editor-title').dispatchEvent(new Event('input'));
      await editor._save();

      const saveBtn = document.querySelector('.kb-editor-btn-save');
      expect(saveBtn.disabled).toBe(false);
    });

    it('should handle network error gracefully', async () => {
      if (!globalThis.KBArticleEditor) return;
      globalThis.fetch = vi.fn()
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ tags: { lifecycle: [], domain: [] } }) })
        .mockRejectedValueOnce(new Error('Network error'));

      editor = new globalThis.KBArticleEditor({ folder: 'test' });
      await editor.open();
      document.querySelector('.kb-editor-title').value = 'Net Error';
      document.querySelector('.kb-editor-title').dispatchEvent(new Event('input'));
      await editor._save();

      const toast = document.querySelector('.kb-editor-toast');
      expect(toast.textContent).toContain('Network error');
    });
  });
});
