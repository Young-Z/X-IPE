/**
 * Tests for FEATURE-049-E: KB File Upload
 * Tests: Modal, dropzone, folder selector, file validation, upload, archive extraction
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { loadFeatureScript } from './helpers.js';

let _implLoaded = false;
function ensureImpl() {
  if (!_implLoaded) {
    try {
      loadFeatureScript('kb-file-upload.js');
      _implLoaded = true;
    } catch { /* not yet implemented */ }
  }
  return typeof globalThis.KBFileUpload !== 'undefined';
}

describe('FEATURE-049-E: KB File Upload', () => {
  let uploader;
  let fetchMock;

  beforeEach(() => {
    if (!ensureImpl()) return;
    fetchMock = vi.fn((url) => {
      if (url === '/api/kb/tree') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            tree: [
              { name: 'guides', type: 'folder', children: [
                { name: 'intro', type: 'folder', children: [] }
              ]},
              { name: 'readme.md', type: 'file' }
            ]
          })
        });
      }
      if (url === '/api/kb/folders') {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ path: 'new-folder' }) });
      }
      if (url === '/api/kb/upload') {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ uploaded: [{}], errors: [], total: 1, failed: 0 }) });
      }
      return Promise.resolve({ ok: false });
    });
    globalThis.fetch = fetchMock;
  });

  afterEach(() => {
    if (uploader) {
      try { uploader.close(); } catch { /* ignore */ }
    }
    // Clean up any orphaned overlays
    document.querySelectorAll('.kb-upload-overlay').forEach(el => el.remove());
    document.body.style.overflow = '';
    vi.restoreAllMocks();
  });

  describe('Modal', () => {
    it('should export KBFileUpload class', () => {
      if (!globalThis.KBFileUpload) return;
      expect(typeof globalThis.KBFileUpload).toBe('function');
    });

    it('should create overlay on open', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      
      const overlay = document.querySelector('.kb-upload-overlay');
      expect(overlay).not.toBeNull();
    });

    it('should add active class after open', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      await new Promise(r => setTimeout(r, 50));
      
      const overlay = document.querySelector('.kb-upload-overlay');
      expect(overlay.classList.contains('active')).toBe(true);
    });

    it('should remove overlay on close', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      uploader.close();
      await new Promise(r => setTimeout(r, 350));
      
      const overlay = document.querySelector('.kb-upload-overlay');
      expect(overlay).toBeNull();
    });

    it('should close on overlay background click', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();

      const overlay = document.querySelector('.kb-upload-overlay');
      overlay.click();
      await new Promise(r => setTimeout(r, 350));

      expect(document.querySelector('.kb-upload-overlay')).toBeNull();
    });

    it('should lock body scroll when open and restore on close', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      expect(document.body.style.overflow).toBe('hidden');

      uploader.close();
      await new Promise(r => setTimeout(r, 350));
      expect(document.body.style.overflow).toBe('');
    });

    it('should show upload header', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      
      const header = document.querySelector('.kb-upload-header h3');
      expect(header.textContent).toContain('Upload');
    });
  });

  describe('Folder Selector', () => {
    it('should render folder dropdown', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      
      const dropdown = document.querySelector('.kb-upload-folder-dropdown');
      expect(dropdown).not.toBeNull();
    });

    it('should include root option', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      
      const options = document.querySelectorAll('.kb-upload-folder-dropdown option');
      expect(options[0].value).toBe('');
      expect(options[0].textContent).toContain('root');
    });

    it('should list folders from tree', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      
      const options = document.querySelectorAll('.kb-upload-folder-dropdown option');
      // root + guides + intro = 3
      expect(options.length).toBe(3);
    });

    it('should show new folder button', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      
      const btn = document.querySelector('.kb-upload-newfolder-btn');
      expect(btn).not.toBeNull();
    });

    it('should toggle new folder input on button click', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      
      const btn = document.querySelector('.kb-upload-newfolder-btn');
      const input = document.querySelector('.kb-upload-newfolder-input');
      expect(input.style.display).toBe('none');
      btn.click();
      expect(input.style.display).toBe('flex');
    });

    it('should update folder on dropdown change', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();

      const dropdown = document.querySelector('.kb-upload-folder-dropdown');
      dropdown.value = 'guides';
      dropdown.dispatchEvent(new Event('change'));

      expect(uploader.folder).toBe('guides');
    });

    it('should pre-select folder from constructor option', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload({ folder: 'guides' });
      await uploader.open();

      const dropdown = document.querySelector('.kb-upload-folder-dropdown');
      expect(dropdown.value).toBe('guides');
    });

    it('should create new folder via API and refresh dropdown', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();

      const nameInput = document.querySelector('.kb-newfolder-name');
      nameInput.value = 'new-folder';
      const createBtn = document.querySelector('.kb-newfolder-create-btn');

      let changed = false;
      document.addEventListener('kb:changed', () => { changed = true; }, { once: true });

      await createBtn.click();
      await new Promise(r => setTimeout(r, 50));

      const folderCall = fetchMock.mock.calls.find(c =>
        typeof c[0] === 'string' && c[0].includes('/api/kb/folders')
      );
      expect(folderCall).toBeDefined();
      expect(uploader.folder).toBe('new-folder');
      expect(changed).toBe(true);
    });

    it('should ignore empty folder name on create', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();

      const nameInput = document.querySelector('.kb-newfolder-name');
      nameInput.value = '   ';
      const createBtn = document.querySelector('.kb-newfolder-create-btn');
      createBtn.click();

      const folderCall = fetchMock.mock.calls.find(c =>
        typeof c[0] === 'string' && c[0].includes('/api/kb/folders')
      );
      expect(folderCall).toBeUndefined();
    });

    it('should hide new folder input on cancel', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();

      const newFolderBtn = document.querySelector('.kb-upload-newfolder-btn');
      newFolderBtn.click();
      expect(document.querySelector('.kb-upload-newfolder-input').style.display).toBe('flex');

      const cancelBtn = document.querySelector('.kb-newfolder-cancel-btn');
      cancelBtn.click();
      expect(document.querySelector('.kb-upload-newfolder-input').style.display).toBe('none');
    });
  });

  describe('Dropzone', () => {
    it('should render dropzone', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      
      const dropzone = document.querySelector('.kb-upload-dropzone');
      expect(dropzone).not.toBeNull();
    });

    it('should render file input', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      
      const fileInput = document.querySelector('.kb-upload-file-input');
      expect(fileInput).not.toBeNull();
      expect(fileInput.multiple).toBe(true);
    });

    it('should add dragover class on dragover', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      
      const dropzone = document.querySelector('.kb-upload-dropzone');
      const event = new Event('dragover', { bubbles: true });
      event.preventDefault = vi.fn();
      event.dataTransfer = { files: [] };
      dropzone.dispatchEvent(event);
      
      expect(dropzone.classList.contains('dragover')).toBe(true);
    });

    it('should remove dragover class on dragleave', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      
      const dropzone = document.querySelector('.kb-upload-dropzone');
      dropzone.classList.add('dragover');
      dropzone.dispatchEvent(new Event('dragleave'));
      
      expect(dropzone.classList.contains('dragover')).toBe(false);
    });

    it('should trigger upload on drop', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();

      const dropzone = document.querySelector('.kb-upload-dropzone');
      const file = new File(['hello'], 'test.md', { type: 'text/markdown' });
      const dropEvent = new Event('drop', { bubbles: true });
      dropEvent.preventDefault = vi.fn();
      dropEvent.dataTransfer = { files: [file] };
      dropzone.dispatchEvent(dropEvent);

      await new Promise(r => setTimeout(r, 50));
      const uploadCall = fetchMock.mock.calls.find(c =>
        typeof c[0] === 'string' && c[0].includes('/api/kb/upload')
      );
      expect(uploadCall).toBeDefined();
    });
  });

  describe('File Validation', () => {
    it('should reject files over 10MB', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      
      // Simulate upload of large file
      const largeFile = new File(['x'.repeat(100)], 'big.md', { type: 'text/markdown' });
      Object.defineProperty(largeFile, 'size', { value: 11 * 1024 * 1024 });
      
      await uploader._uploadFiles([largeFile]);
      
      const errorItems = document.querySelectorAll('.kb-upload-error');
      expect(errorItems.length).toBe(1);
      expect(errorItems[0].textContent).toContain('Too large');
    });
  });

  describe('Upload', () => {
    it('should call upload API with FormData', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload({ folder: 'guides' });
      await uploader.open();
      
      const file = new File(['hello'], 'test.md', { type: 'text/markdown' });
      await uploader._uploadFiles([file]);
      
      const uploadCall = fetchMock.mock.calls.find(c => 
        typeof c[0] === 'string' && c[0].includes('/api/kb/upload')
      );
      expect(uploadCall).toBeDefined();
    });

    it('should dispatch kb:changed on successful upload', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      
      let changed = false;
      document.addEventListener('kb:changed', () => { changed = true; }, { once: true });
      
      const file = new File(['hello'], 'test.md', { type: 'text/markdown' });
      await uploader._uploadFiles([file]);
      
      expect(changed).toBe(true);
    });

    it('should show success status for uploaded files', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();
      
      const file = new File(['hello'], 'test.md', { type: 'text/markdown' });
      await uploader._uploadFiles([file]);
      
      const successItems = document.querySelectorAll('.kb-upload-success');
      expect(successItems.length).toBe(1);
    });

    it('should show error status for server-rejected files', async () => {
      if (!globalThis.KBFileUpload) return;
      globalThis.fetch = vi.fn((url) => {
        if (url === '/api/kb/tree') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve({ tree: [] }) });
        }
        if (url === '/api/kb/upload') {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({
              uploaded: [], errors: [{ file: 'bad.txt', error: 'Invalid format' }], total: 0, failed: 1
            })
          });
        }
        return Promise.resolve({ ok: false });
      });

      uploader = new globalThis.KBFileUpload();
      await uploader.open();

      const file = new File(['data'], 'bad.txt', { type: 'text/plain' });
      await uploader._uploadFiles([file]);

      const errorItems = document.querySelectorAll('.kb-upload-error');
      expect(errorItems.length).toBe(1);
      expect(errorItems[0].textContent).toContain('Invalid format');
    });

    it('should handle network error gracefully', async () => {
      if (!globalThis.KBFileUpload) return;
      globalThis.fetch = vi.fn((url) => {
        if (url === '/api/kb/tree') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve({ tree: [] }) });
        }
        if (url === '/api/kb/upload') {
          return Promise.reject(new Error('Network failure'));
        }
        return Promise.resolve({ ok: false });
      });

      uploader = new globalThis.KBFileUpload();
      await uploader.open();

      const file = new File(['data'], 'test.md', { type: 'text/markdown' });
      await uploader._uploadFiles([file]);

      const errorItems = document.querySelectorAll('.kb-upload-error');
      expect(errorItems.length).toBe(1);
      expect(errorItems[0].textContent).toContain('Upload failed');
    });

    it('should call onComplete callback on successful upload', async () => {
      if (!globalThis.KBFileUpload) return;
      const cb = vi.fn();
      uploader = new globalThis.KBFileUpload({ onComplete: cb });
      await uploader.open();

      const file = new File(['hello'], 'test.md', { type: 'text/markdown' });
      await uploader._uploadFiles([file]);

      expect(cb).toHaveBeenCalledTimes(1);
    });

    it('should handle mixed valid and oversized files', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();

      const validFile = new File(['hello'], 'ok.md', { type: 'text/markdown' });
      const largeFile = new File(['x'], 'huge.md', { type: 'text/markdown' });
      Object.defineProperty(largeFile, 'size', { value: 11 * 1024 * 1024 });

      await uploader._uploadFiles([validFile, largeFile]);

      const successItems = document.querySelectorAll('.kb-upload-success');
      const errorItems = document.querySelectorAll('.kb-upload-error');
      expect(successItems.length).toBe(1);
      expect(errorItems.length).toBe(1);
    });

    it('should escape HTML in file names', async () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload();
      await uploader.open();

      const file = new File(['data'], '<script>alert(1)</script>.md', { type: 'text/markdown' });
      await uploader._uploadFiles([file]);

      const fnameEl = document.querySelector('.kb-upload-fname');
      expect(fnameEl.innerHTML).not.toContain('<script>');
    });
  });

  describe('Constructor Options', () => {
    it('should accept folder option', () => {
      if (!globalThis.KBFileUpload) return;
      uploader = new globalThis.KBFileUpload({ folder: 'guides/intro' });
      expect(uploader.folder).toBe('guides/intro');
    });

    it('should accept onComplete callback', () => {
      if (!globalThis.KBFileUpload) return;
      const cb = vi.fn();
      uploader = new globalThis.KBFileUpload({ onComplete: cb });
      expect(uploader.onComplete).toBe(cb);
    });
  });
});
