/**
 * FEATURE-037-B: ComposeIdeaModal mode switching tests (Vitest + jsdom)
 * Tests create/link mode toggle, edit mode initialization, submit state.
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

describe('ComposeIdeaModal — constructor modes', () => {
  it('defaults to create mode', () => {
    const modal = new ComposeIdeaModal({ workflowName: 'test' });
    expect(modal.activeMode).toBe('create');
    expect(modal.editMode).toBe(false);
  });

  it('sets editMode when mode=edit', () => {
    const modal = new ComposeIdeaModal({ workflowName: 'test', mode: 'edit' });
    expect(modal.editMode).toBe(true);
    // activeMode is 'create' even in edit mode (for toggle UI)
    expect(modal.activeMode).toBe('create');
  });

  it('stores file/folder paths for edit mode', () => {
    const modal = new ComposeIdeaModal({
      workflowName: 'test',
      mode: 'edit',
      filePath: 'x-ipe-docs/ideas/My Idea/summary.md',
      folderPath: 'x-ipe-docs/ideas/My Idea',
      folderName: 'My Idea',
    });
    expect(modal.filePath).toBe('x-ipe-docs/ideas/My Idea/summary.md');
    expect(modal.folderPath).toBe('x-ipe-docs/ideas/My Idea');
    expect(modal.folderName).toBe('My Idea');
  });

  it('initializes linkPanel as null', () => {
    const modal = new ComposeIdeaModal({ workflowName: 'test' });
    expect(modal.linkPanel).toBeNull();
  });
});

describe('ComposeIdeaModal — switchMode', () => {
  let modal;

  beforeEach(() => {
    document.body.innerHTML = '';
    // Mock EasyMDE and fetch
    globalThis.EasyMDE = class { constructor() {} value() { return ''; } toTextArea() {} };
    globalThis.fetch = vi.fn(async () => ({ ok: true, json: async () => ({ tree: [] }), text: async () => '' }));
    globalThis.marked = { parse: (s) => s };

    modal = new ComposeIdeaModal({ workflowName: 'test' });
    modal.createDOM();
    modal.bindEvents();
    document.body.appendChild(modal.overlay);
  });

  it('updates activeMode to link', () => {
    modal.switchMode('link');
    expect(modal.activeMode).toBe('link');
  });

  it('updates activeMode to create', () => {
    modal.switchMode('link');
    modal.switchMode('create');
    expect(modal.activeMode).toBe('create');
  });

  it('toggles active class on toggle buttons', () => {
    modal.switchMode('link');
    const buttons = modal.overlay.querySelectorAll('.compose-modal-toggle button');
    const linkBtn = [...buttons].find(b => b.dataset.mode === 'link');
    const createBtn = [...buttons].find(b => b.dataset.mode === 'create');
    expect(linkBtn.classList.contains('active')).toBe(true);
    expect(createBtn.classList.contains('active')).toBe(false);
  });

  it('hides create content when switching to link', () => {
    modal.switchMode('link');
    expect(modal.createContent.style.display).toBe('none');
    expect(modal.linkContent.style.display).toBe('');
  });

  it('shows create content when switching back to create', () => {
    modal.switchMode('link');
    modal.switchMode('create');
    expect(modal.createContent.style.display).toBe('');
    expect(modal.linkContent.style.display).toBe('none');
  });

  it('sets submit button text to "Confirm Link" in link mode', () => {
    modal.switchMode('link');
    expect(modal.submitBtn.textContent).toBe('Confirm Link');
  });

  it('sets submit button text to "Submit Idea" in create mode', () => {
    modal.switchMode('link');
    modal.switchMode('create');
    expect(modal.submitBtn.textContent).toBe('Submit Idea');
  });

  it('sets submit button text to "Update Idea" when in edit+create mode', () => {
    const editModal = new ComposeIdeaModal({ workflowName: 'test', mode: 'edit' });
    editModal.createDOM();
    editModal.bindEvents();
    document.body.appendChild(editModal.overlay);

    editModal.switchMode('link');
    editModal.switchMode('create');
    expect(editModal.submitBtn.textContent).toBe('Update Idea');
  });

  it('instantiates LinkExistingPanel on first link switch', () => {
    expect(modal.linkPanel).toBeNull();
    modal.switchMode('link');
    expect(modal.linkPanel).not.toBeNull();
    expect(modal.linkPanel).toBeInstanceOf(LinkExistingPanel);
  });

  it('does not re-create LinkExistingPanel on subsequent switches', () => {
    modal.switchMode('link');
    const firstPanel = modal.linkPanel;
    modal.switchMode('create');
    modal.switchMode('link');
    expect(modal.linkPanel).toBe(firstPanel);
  });
});

describe('ComposeIdeaModal — _linkedPath tracking', () => {
  it('stores selected path via onSelect callback', () => {
    document.body.innerHTML = '';
    globalThis.EasyMDE = class { constructor() {} value() { return ''; } toTextArea() {} };
    globalThis.fetch = vi.fn(async () => ({ ok: true, json: async () => ({ tree: [] }), text: async () => '' }));

    const modal = new ComposeIdeaModal({ workflowName: 'test' });
    modal.createDOM();
    modal.bindEvents();
    document.body.appendChild(modal.overlay);

    modal.switchMode('link');
    // Simulate onSelect callback from LinkExistingPanel
    modal.linkPanel.onSelect('x-ipe-docs/ideas/Test/file.md');
    expect(modal._linkedPath).toBe('x-ipe-docs/ideas/Test/file.md');
  });
});

describe('ComposeIdeaModal — workflow name auto-fill validation (TASK-790)', () => {
  let modal;

  beforeEach(() => {
    document.body.innerHTML = '';
    globalThis.EasyMDE = class { constructor() {} value() { return 'some content'; } toTextArea() {} };
    globalThis.fetch = vi.fn(async () => ({ ok: true, json: async () => ({ tree: [] }), text: async () => '' }));
    globalThis.marked = { parse: (s) => s };
  });

  it('sets nameValid=true when workflowName auto-fills the name input', () => {
    modal = new ComposeIdeaModal({ workflowName: 'workflow-test' });
    modal.createDOM();
    modal.bindEvents();
    document.body.appendChild(modal.overlay);

    expect(modal.nameInput.value).toBe('workflow-test');
    expect(modal.nameValid).toBe(true);
  });

  it('enables Submit button when workflowName is auto-filled and content exists', () => {
    modal = new ComposeIdeaModal({ workflowName: 'workflow-test' });
    modal.createDOM();
    modal.bindEvents();
    document.body.appendChild(modal.overlay);

    // Simulate EasyMDE having content
    modal.easyMDE = { value: () => 'some content' };
    modal.updateSubmitState();

    expect(modal.submitBtn.disabled).toBe(false);
  });

  it('updates word counter when workflowName is auto-filled', () => {
    modal = new ComposeIdeaModal({ workflowName: 'workflow-test' });
    modal.createDOM();
    modal.bindEvents();
    document.body.appendChild(modal.overlay);

    expect(modal.wordCounter.textContent).toContain('1');
  });
});

describe('AutoFolderNamer — incremental wf-NNN naming', () => {
  it('extracts tree array from API response and increments highest wf number', async () => {
    const namer = new AutoFolderNamer();
    // Mock fetch to return the actual API response shape: { success: true, tree: [...] }
    globalThis.fetch = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        success: true,
        tree: [
          { name: 'wf-001-first-idea', type: 'folder', children: [] },
          { name: 'wf-002-second-idea', type: 'folder', children: [] },
          { name: '003. Some Other Idea', type: 'folder', children: [] },
        ]
      })
    }));

    const result = await namer.generate('my-idea');
    expect(result).toBe('wf-003-my-idea');
  });

  it('returns wf-001 when no existing wf folders', async () => {
    const namer = new AutoFolderNamer();
    globalThis.fetch = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        success: true,
        tree: [
          { name: '001. Regular Folder', type: 'folder', children: [] },
        ]
      })
    }));

    const result = await namer.generate('fresh-idea');
    expect(result).toBe('wf-001-fresh-idea');
  });
});

describe('IdeaNameValidator — sanitize with Unicode', () => {
  it('preserves Chinese characters in sanitized output', () => {
    const validator = new IdeaNameValidator(
      document.createElement('input'),
      document.createElement('span'),
      document.createElement('span')
    );
    const result = validator.sanitize('五子棋');
    expect(result).toBe('五子棋');
  });

  it('preserves mixed Chinese and ASCII', () => {
    const validator = new IdeaNameValidator(
      document.createElement('input'),
      document.createElement('span'),
      document.createElement('span')
    );
    const result = validator.sanitize('My 五子棋 Game');
    expect(result).toBe('my-五子棋-game');
  });

  it('still strips filesystem-unsafe characters', () => {
    const validator = new IdeaNameValidator(
      document.createElement('input'),
      document.createElement('span'),
      document.createElement('span')
    );
    const result = validator.sanitize('bad/name*test');
    expect(result).not.toContain('/');
    expect(result).not.toContain('*');
  });

  it('produces valid folder name for pure Chinese input', () => {
    const validator = new IdeaNameValidator(
      document.createElement('input'),
      document.createElement('span'),
      document.createElement('span')
    );
    const result = validator.sanitize('五子棋游戏');
    expect(result.length).toBeGreaterThan(0);
    expect(result).not.toMatch(/^-|-$/);
  });
});

describe('ComposeIdeaModal — upload files included in compose submit', () => {
  let modal;
  let capturedFormData;

  beforeEach(() => {
    document.body.innerHTML = '';
    capturedFormData = null;
    globalThis.EasyMDE = class {
      constructor() { this.codemirror = { on: () => {} }; }
      value() { return 'My idea content'; }
      toTextArea() {}
    };
    globalThis.fetch = vi.fn(async (url, opts) => {
      if (url === '/api/ideas/upload' && opts?.body instanceof FormData) {
        capturedFormData = opts.body;
        return {
          ok: true,
          status: 200,
          json: async () => ({ folder_path: 'x-ipe-docs/ideas/wf-001-test', files_uploaded: ['new idea.md', 'extra.txt'] })
        };
      }
      return { ok: true, json: async () => ({ tree: [], success: true }), text: async () => '' };
    });
    globalThis.marked = { parse: (s) => s };

    modal = new ComposeIdeaModal({ workflowName: 'test' });
    modal.createDOM();
    modal.bindEvents();
    modal.initEasyMDE();
    document.body.appendChild(modal.overlay);
  });

  it('includes pendingFiles when submitting from compose tab', async () => {
    // Simulate adding an uploaded file
    const fakeFile = new File(['hello'], 'extra.txt', { type: 'text/plain' });
    modal.pendingFiles = [fakeFile];
    modal.activeTab = 'compose';
    modal.namer.generate = vi.fn(async () => 'wf-001-test');

    // Set valid name and enable submit
    modal.nameInput.value = 'test-idea';
    modal.nameValid = true;
    modal.submitBtn.disabled = false;
    modal.validator.validate = vi.fn(() => ({ valid: true, sanitized: 'test-idea' }));

    await modal.handleSubmit();

    expect(capturedFormData).not.toBeNull();
    const allFiles = capturedFormData.getAll('files');
    // Should have both: compose blob (new idea.md) AND the uploaded file
    expect(allFiles.length).toBe(2);
    expect(allFiles[0].name).toBe('new idea.md');
    expect(allFiles[1].name).toBe('extra.txt');
  });
});

/* --------------------------------------------------------------------------
   TASK-874: Multi-file deliverables bug fix
   Bug: uploading 2 files in compose idea only shows 1 in deliverables
   -------------------------------------------------------------------------- */
describe('ComposeIdeaModal — multi-file deliverables (TASK-874)', () => {
  let modal;
  let capturedWorkflowBody;

  beforeEach(() => {
    document.body.innerHTML = '';
    capturedWorkflowBody = null;
    globalThis.EasyMDE = class {
      constructor() { this.codemirror = { on: () => {} }; }
      value() { return 'My idea content'; }
      toTextArea() {}
    };
    globalThis.fetch = vi.fn(async (url, opts) => {
      if (url === '/api/ideas/upload' && opts?.body instanceof FormData) {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            folder_path: 'x-ipe-docs/ideas/wf-001-test',
            files_uploaded: ['new idea.md', 'sketch1.png', 'sketch2.png']
          })
        };
      }
      if (url.includes('/api/workflow/') && url.includes('/action')) {
        capturedWorkflowBody = JSON.parse(opts.body);
        return { ok: true, json: async () => ({ success: true }), text: async () => '' };
      }
      return { ok: true, json: async () => ({ tree: [], success: true }), text: async () => '' };
    });
    globalThis.marked = { parse: (s) => s };

    modal = new ComposeIdeaModal({ workflowName: 'test' });
    modal.createDOM();
    modal.bindEvents();
    modal.initEasyMDE();
    document.body.appendChild(modal.overlay);
  });

  it('sends all uploaded files as array deliverables to workflow API', async () => {
    const fakeFile1 = new File(['img1'], 'sketch1.png', { type: 'image/png' });
    const fakeFile2 = new File(['img2'], 'sketch2.png', { type: 'image/png' });
    modal.pendingFiles = [fakeFile1, fakeFile2];
    modal.activeTab = 'compose';
    modal.namer.generate = vi.fn(async () => 'wf-001-test');
    modal.nameInput.value = 'test-idea';
    modal.nameValid = true;
    modal.submitBtn.disabled = false;
    modal.validator.validate = vi.fn(() => ({ valid: true, sanitized: 'test-idea' }));

    await modal.handleSubmit();

    expect(capturedWorkflowBody).not.toBeNull();
    expect(capturedWorkflowBody.action).toBe('compose_idea');
    expect(capturedWorkflowBody.status).toBe('done');
    // Deliverables should include ALL files as keyed dict with array
    const deliverables = capturedWorkflowBody.deliverables;
    expect(deliverables['raw-ideas']).toEqual([
      'x-ipe-docs/ideas/wf-001-test/new idea.md',
      'x-ipe-docs/ideas/wf-001-test/sketch1.png',
      'x-ipe-docs/ideas/wf-001-test/sketch2.png'
    ]);
    expect(deliverables['ideas-folder']).toBe('x-ipe-docs/ideas/wf-001-test');
  });

  it('sends single file as string deliverable (backward compat)', async () => {
    modal.pendingFiles = [];
    modal.activeTab = 'compose';
    modal.namer.generate = vi.fn(async () => 'wf-001-test');
    modal.nameInput.value = 'test-idea';
    modal.nameValid = true;
    modal.submitBtn.disabled = false;
    modal.validator.validate = vi.fn(() => ({ valid: true, sanitized: 'test-idea' }));

    globalThis.fetch = vi.fn(async (url, opts) => {
      if (url === '/api/ideas/upload') {
        return {
          ok: true, status: 200,
          json: async () => ({
            folder_path: 'x-ipe-docs/ideas/wf-001-test',
            files_uploaded: ['new idea.md']
          })
        };
      }
      if (url.includes('/api/workflow/') && url.includes('/action')) {
        capturedWorkflowBody = JSON.parse(opts.body);
        return { ok: true, json: async () => ({ success: true }), text: async () => '' };
      }
      return { ok: true, json: async () => ({ tree: [], success: true }), text: async () => '' };
    });

    await modal.handleSubmit();

    expect(capturedWorkflowBody).not.toBeNull();
    const deliverables = capturedWorkflowBody.deliverables;
    expect(deliverables['raw-ideas']).toBe('x-ipe-docs/ideas/wf-001-test/new idea.md');
    expect(deliverables['ideas-folder']).toBe('x-ipe-docs/ideas/wf-001-test');
  });

  it('passes all file paths in onComplete callback', async () => {
    let completedData = null;
    modal.onComplete = (data) => { completedData = data; };
    const fakeFile = new File(['img'], 'sketch.png', { type: 'image/png' });
    modal.pendingFiles = [fakeFile];
    modal.activeTab = 'compose';
    modal.namer.generate = vi.fn(async () => 'wf-001-test');
    modal.nameInput.value = 'test-idea';
    modal.nameValid = true;
    modal.submitBtn.disabled = false;
    modal.validator.validate = vi.fn(() => ({ valid: true, sanitized: 'test-idea' }));

    globalThis.fetch = vi.fn(async (url, opts) => {
      if (url === '/api/ideas/upload') {
        return {
          ok: true, status: 200,
          json: async () => ({
            folder_path: 'x-ipe-docs/ideas/wf-001-test',
            files_uploaded: ['new idea.md', 'sketch.png']
          })
        };
      }
      if (url.includes('/api/workflow/') && url.includes('/action')) {
        return { ok: true, json: async () => ({ success: true }), text: async () => '' };
      }
      return { ok: true, json: async () => ({ tree: [], success: true }), text: async () => '' };
    });

    await modal.handleSubmit();

    expect(completedData).not.toBeNull();
    expect(completedData.file).toBe('x-ipe-docs/ideas/wf-001-test/new idea.md');
    expect(completedData.files).toEqual([
      'x-ipe-docs/ideas/wf-001-test/new idea.md',
      'x-ipe-docs/ideas/wf-001-test/sketch.png'
    ]);
    expect(completedData.folder).toBe('x-ipe-docs/ideas/wf-001-test');
  });
});

describe('ComposeIdeaModal — edit mode stores non-.md file paths', () => {
  it('stores .pdf file path for edit mode', () => {
    const modal = new ComposeIdeaModal({
      workflowName: 'test',
      mode: 'edit',
      filePath: 'x-ipe-docs/ideas/My Idea/design.pdf',
      folderPath: 'x-ipe-docs/ideas/My Idea',
      folderName: 'My Idea',
    });
    expect(modal.filePath).toBe('x-ipe-docs/ideas/My Idea/design.pdf');
    expect(modal.editMode).toBe(true);
  });

  it('stores .txt file path for edit mode', () => {
    const modal = new ComposeIdeaModal({
      workflowName: 'test',
      mode: 'edit',
      filePath: 'x-ipe-docs/ideas/My Idea/notes.txt',
      folderPath: 'x-ipe-docs/ideas/My Idea',
      folderName: 'My Idea',
    });
    expect(modal.filePath).toBe('x-ipe-docs/ideas/My Idea/notes.txt');
  });
});

/* --------------------------------------------------------------------------
   TASK-868: KB Reference Integration in Workflow Compose
   -------------------------------------------------------------------------- */
describe('ComposeIdeaModal — KB Reference Integration', () => {
  it('initializes kbReferences as empty array', () => {
    const modal = new ComposeIdeaModal({ workflowName: 'test' });
    expect(modal.kbReferences).toEqual([]);
  });

  it('renders KB Reference button in tab bar', () => {
    const modal = new ComposeIdeaModal({ workflowName: 'test' });
    modal.createDOM();
    const btn = modal.overlay.querySelector('.compose-modal-kb-ref-btn');
    expect(btn).toBeTruthy();
    expect(btn.textContent).toContain('KB Reference');
  });

  it('renders KB Reference count label (hidden by default)', () => {
    const modal = new ComposeIdeaModal({ workflowName: 'test' });
    modal.createDOM();
    const count = modal.overlay.querySelector('.compose-modal-kb-ref-count');
    expect(count).toBeTruthy();
    expect(count.style.display).toBe('none');
  });

  it('places KB Reference area after tab buttons with ms-auto', () => {
    const modal = new ComposeIdeaModal({ workflowName: 'test' });
    modal.createDOM();
    const tabs = modal.overlay.querySelector('.compose-modal-tabs');
    const kbArea = tabs.querySelector('.compose-modal-kb-ref-area');
    expect(kbArea).toBeTruthy();
    // Should be last child in tabs
    expect(tabs.lastElementChild).toBe(kbArea);
  });

  it('_updateKbRefCount shows count when references exist', () => {
    const modal = new ComposeIdeaModal({ workflowName: 'test' });
    modal.createDOM();
    modal.kbReferences = ['kb/article1.md', 'kb/article2.md'];
    modal._updateKbRefCount();
    const count = modal.overlay.querySelector('.compose-modal-kb-ref-count');
    expect(count.style.display).toBe('');
    expect(count.textContent).toBe('2');
  });

  it('_updateKbRefCount hides count when no references', () => {
    const modal = new ComposeIdeaModal({ workflowName: 'test' });
    modal.createDOM();
    modal.kbReferences = [];
    modal._updateKbRefCount();
    const count = modal.overlay.querySelector('.compose-modal-kb-ref-count');
    expect(count.style.display).toBe('none');
  });

  it('_showKbRefPopup creates popup with references', () => {
    const modal = new ComposeIdeaModal({ workflowName: 'test' });
    modal.createDOM();
    modal.kbReferences = ['kb/guides/setup.md'];
    const anchor = modal.overlay.querySelector('.compose-modal-kb-ref-count');
    
    // Show popup
    modal._showKbRefPopup(anchor);
    let popup = modal.overlay.querySelector('.compose-modal-kb-ref-popup');
    expect(popup).toBeTruthy();
    expect(popup.textContent).toContain('setup.md');

    // Calling again replaces popup (not toggle)
    modal._showKbRefPopup(anchor);
    const popups = modal.overlay.querySelectorAll('.compose-modal-kb-ref-popup');
    expect(popups.length).toBe(1);
  });

  it('popup Clear All removes all references', () => {
    const modal = new ComposeIdeaModal({ workflowName: 'test' });
    modal.createDOM();
    modal.kbReferences = ['kb/a.md', 'kb/b.md'];
    const anchor = modal.overlay.querySelector('.compose-modal-kb-ref-count');
    modal._showKbRefPopup(anchor);

    const clearBtn = modal.overlay.querySelector('.compose-modal-kb-ref-clear-btn');
    clearBtn.click();

    expect(modal.kbReferences).toEqual([]);
    expect(modal.overlay.querySelector('.compose-modal-kb-ref-popup')).toBeNull();
  });

  it('popup individual remove deletes one reference', () => {
    const modal = new ComposeIdeaModal({ workflowName: 'test' });
    modal.createDOM();
    modal.kbReferences = ['kb/a.md', 'kb/b.md', 'kb/c.md'];
    const anchor = modal.overlay.querySelector('.compose-modal-kb-ref-count');
    modal._showKbRefPopup(anchor);

    const removeBtn = modal.overlay.querySelector('[data-idx="1"]');
    removeBtn.click();

    expect(modal.kbReferences).toEqual(['kb/a.md', 'kb/c.md']);
  });

  it('KB Reference button click should NOT switch tabs', () => {
    const modal = new ComposeIdeaModal({ workflowName: 'test' });
    modal.createDOM();
    modal.bindEvents();
    
    // Start on compose tab
    expect(modal.activeTab).toBe('compose');
    
    // Click KB Reference button
    const kbBtn = modal.overlay.querySelector('.compose-modal-kb-ref-btn');
    kbBtn.click();
    
    // Should still be on compose tab
    expect(modal.activeTab).toBe('compose');
    
    // Compose tab button should still be active
    const composeTabBtn = modal.overlay.querySelector('.compose-modal-tabs button[data-tab="compose"]');
    expect(composeTabBtn.classList.contains('active')).toBe(true);
  });

  it('switching to upload tab then clicking KB Ref should stay on upload', () => {
    const modal = new ComposeIdeaModal({ workflowName: 'test' });
    modal.createDOM();
    modal.bindEvents();
    
    // Switch to upload tab
    modal.switchTab('upload');
    expect(modal.activeTab).toBe('upload');
    
    // Click KB Reference button
    const kbBtn = modal.overlay.querySelector('.compose-modal-kb-ref-btn');
    kbBtn.click();
    
    // Should still be on upload tab
    expect(modal.activeTab).toBe('upload');
    const uploadBtn = modal.overlay.querySelector('.compose-modal-tabs button[data-tab="upload"]');
    expect(uploadBtn.classList.contains('active')).toBe(true);
  });
});

/* --------------------------------------------------------------------------
   TASK-876: loadEditContent skips non-text (binary) files
   -------------------------------------------------------------------------- */
describe('TASK-876: loadEditContent skips binary files', () => {
  it('should NOT fetch/load a .png file into the editor', async () => {
    const fetchSpy = vi.fn(async () => ({ ok: true, json: async () => ({ success: true, kb_references: [] }) }));
    globalThis.fetch = fetchSpy;

    const modal = new ComposeIdeaModal({
      workflowName: 'test',
      mode: 'edit',
      filePath: 'x-ipe-docs/ideas/test/sketch.png',
      folderPath: 'x-ipe-docs/ideas/test',
      folderName: 'test'
    });
    modal.createDOM();
    modal.bindEvents();
    // Mock easyMDE
    modal.easyMDE = { value: vi.fn() };

    await modal.loadEditContent();

    // Should NOT have fetched the binary file content
    const fileCall = fetchSpy.mock.calls.find(c => c[0].includes('/api/ideas/file'));
    expect(fileCall).toBeUndefined();
    // Should NOT have set editor value
    expect(modal.easyMDE.value).not.toHaveBeenCalled();
  });

  it('should NOT fetch/load a .jpg file into the editor', async () => {
    const fetchSpy = vi.fn(async () => ({ ok: true, json: async () => ({ success: true, kb_references: [] }) }));
    globalThis.fetch = fetchSpy;

    const modal = new ComposeIdeaModal({
      workflowName: 'test',
      mode: 'edit',
      filePath: 'x-ipe-docs/ideas/test/photo.jpg',
      folderPath: 'x-ipe-docs/ideas/test',
      folderName: 'test'
    });
    modal.createDOM();
    modal.bindEvents();
    modal.easyMDE = { value: vi.fn() };

    await modal.loadEditContent();
    const fileCall = fetchSpy.mock.calls.find(c => c[0].includes('/api/ideas/file'));
    expect(fileCall).toBeUndefined();
  });

  it('should NOT fetch/load a .pdf file into the editor', async () => {
    const fetchSpy = vi.fn(async () => ({ ok: true, json: async () => ({ success: true, kb_references: [] }) }));
    globalThis.fetch = fetchSpy;

    const modal = new ComposeIdeaModal({
      workflowName: 'test',
      mode: 'edit',
      filePath: 'x-ipe-docs/ideas/test/doc.pdf',
      folderPath: 'x-ipe-docs/ideas/test',
      folderName: 'test'
    });
    modal.createDOM();
    modal.bindEvents();
    modal.easyMDE = { value: vi.fn() };

    await modal.loadEditContent();
    const fileCall = fetchSpy.mock.calls.find(c => c[0].includes('/api/ideas/file'));
    expect(fileCall).toBeUndefined();
  });

  it('SHOULD still load a .md file normally', async () => {
    globalThis.fetch = vi.fn(async () => ({
      ok: true,
      text: async () => '# My Idea'
    }));

    const modal = new ComposeIdeaModal({
      workflowName: 'test',
      mode: 'edit',
      filePath: 'x-ipe-docs/ideas/test/new idea.md',
      folderPath: 'x-ipe-docs/ideas/test',
      folderName: 'test'
    });
    modal.createDOM();
    modal.bindEvents();
    modal.easyMDE = { value: vi.fn() };

    await modal.loadEditContent();
    expect(globalThis.fetch).toHaveBeenCalled();
    expect(modal.easyMDE.value).toHaveBeenCalledWith('# My Idea');
  });

  it('SHOULD still load a .txt file normally', async () => {
    globalThis.fetch = vi.fn(async () => ({
      ok: true,
      text: async () => 'plain text idea'
    }));

    const modal = new ComposeIdeaModal({
      workflowName: 'test',
      mode: 'edit',
      filePath: 'x-ipe-docs/ideas/test/notes.txt',
      folderPath: 'x-ipe-docs/ideas/test',
      folderName: 'test'
    });
    modal.createDOM();
    modal.bindEvents();
    modal.easyMDE = { value: vi.fn() };

    await modal.loadEditContent();
    expect(globalThis.fetch).toHaveBeenCalled();
    expect(modal.easyMDE.value).toHaveBeenCalledWith('plain text idea');
  });
});

/* --------------------------------------------------------------------------
   TASK-878: loadEditContent should also load KB references on reopen
   -------------------------------------------------------------------------- */
describe('TASK-878: loadEditContent loads KB references on reopen', () => {
  it('should fetch KB references and populate kbReferences array', async () => {
    const kbRefs = ['kb/articles/guide.md', 'kb/articles/setup.md'];
    let callCount = 0;
    globalThis.fetch = vi.fn(async (url) => {
      callCount++;
      if (url.includes('/api/ideas/kb-references')) {
        return {
          ok: true,
          json: async () => ({ success: true, kb_references: kbRefs })
        };
      }
      // File content fetch
      return { ok: true, text: async () => '# My Idea Content' };
    });

    const modal = new ComposeIdeaModal({
      workflowName: 'test',
      mode: 'edit',
      filePath: 'x-ipe-docs/ideas/wf-001-test/new idea.md',
      folderPath: 'x-ipe-docs/ideas/wf-001-test',
      folderName: 'wf-001-test'
    });
    modal.createDOM();
    modal.bindEvents();
    modal.easyMDE = { value: vi.fn() };

    await modal.loadEditContent();

    // Should have fetched both file content AND KB references
    const kbCall = globalThis.fetch.mock.calls.find(c => c[0].includes('/api/ideas/kb-references'));
    expect(kbCall).toBeTruthy();
    expect(kbCall[0]).toContain('folder_path=');
    expect(modal.kbReferences).toEqual(kbRefs);
  });

  it('should update KB reference count badge after loading', async () => {
    globalThis.fetch = vi.fn(async (url) => {
      if (url.includes('/api/ideas/kb-references')) {
        return {
          ok: true,
          json: async () => ({ success: true, kb_references: ['kb/a.md'] })
        };
      }
      return { ok: true, text: async () => '# Content' };
    });

    const modal = new ComposeIdeaModal({
      workflowName: 'test',
      mode: 'edit',
      filePath: 'x-ipe-docs/ideas/wf-001-test/new idea.md',
      folderPath: 'x-ipe-docs/ideas/wf-001-test',
      folderName: 'wf-001-test'
    });
    modal.createDOM();
    modal.bindEvents();
    modal.easyMDE = { value: vi.fn() };

    await modal.loadEditContent();

    const countEl = modal.overlay.querySelector('.compose-modal-kb-ref-count');
    expect(countEl.textContent).toBe('1');
    expect(countEl.style.display).not.toBe('none');
  });

  it('should gracefully handle missing KB references (404 or empty)', async () => {
    globalThis.fetch = vi.fn(async (url) => {
      if (url.includes('/api/ideas/kb-references')) {
        return {
          ok: true,
          json: async () => ({ success: true, kb_references: [] })
        };
      }
      return { ok: true, text: async () => '# Content' };
    });

    const modal = new ComposeIdeaModal({
      workflowName: 'test',
      mode: 'edit',
      filePath: 'x-ipe-docs/ideas/wf-001-test/new idea.md',
      folderPath: 'x-ipe-docs/ideas/wf-001-test',
      folderName: 'wf-001-test'
    });
    modal.createDOM();
    modal.bindEvents();
    modal.easyMDE = { value: vi.fn() };

    await modal.loadEditContent();

    expect(modal.kbReferences).toEqual([]);
    const countEl = modal.overlay.querySelector('.compose-modal-kb-ref-count');
    expect(countEl.style.display).toBe('none');
  });
});

/* --------------------------------------------------------------------------
   TASK-878: handleUpdate should include KB references in formData
   -------------------------------------------------------------------------- */
describe('TASK-878: handleUpdate sends KB references', () => {
  it('should include kb_references in formData when kbReferences is non-empty', async () => {
    let capturedFormData = null;
    globalThis.fetch = vi.fn(async (url, opts) => {
      if (url === '/api/ideas/upload' && opts?.body instanceof FormData) {
        capturedFormData = opts.body;
      }
      return { ok: true, json: async () => ({ folder_path: 'x-ipe-docs/ideas/wf-001-test', files_uploaded: ['new idea.md'] }), status: 200 };
    });

    const modal = new ComposeIdeaModal({
      workflowName: 'test',
      mode: 'edit',
      filePath: 'x-ipe-docs/ideas/wf-001-test/new idea.md',
      folderPath: 'x-ipe-docs/ideas/wf-001-test',
      folderName: 'wf-001-test'
    });
    modal.createDOM();
    modal.bindEvents();
    modal.easyMDE = { value: () => '# Updated idea', toTextArea: () => {} };
    modal.kbReferences = ['kb/guide.md', 'kb/setup.md'];
    modal.submitBtn = { disabled: false, set textContent(v) {} };

    await modal.handleUpdate();

    expect(capturedFormData).toBeTruthy();
    const kbRefsValue = capturedFormData.get('kb_references');
    expect(kbRefsValue).toBeTruthy();
    expect(JSON.parse(kbRefsValue)).toEqual(['kb/guide.md', 'kb/setup.md']);
  });

  it('should NOT include kb_references in formData when kbReferences is empty', async () => {
    let capturedFormData = null;
    globalThis.fetch = vi.fn(async (url, opts) => {
      if (url === '/api/ideas/upload' && opts?.body instanceof FormData) {
        capturedFormData = opts.body;
      }
      return { ok: true, json: async () => ({ folder_path: 'x-ipe-docs/ideas/wf-001-test', files_uploaded: ['new idea.md'] }), status: 200 };
    });

    const modal = new ComposeIdeaModal({
      workflowName: 'test',
      mode: 'edit',
      filePath: 'x-ipe-docs/ideas/wf-001-test/new idea.md',
      folderPath: 'x-ipe-docs/ideas/wf-001-test',
      folderName: 'wf-001-test'
    });
    modal.createDOM();
    modal.bindEvents();
    modal.easyMDE = { value: () => '# Updated', toTextArea: () => {} };
    modal.kbReferences = [];
    modal.submitBtn = { disabled: false, set textContent(v) {} };

    await modal.handleUpdate();

    expect(capturedFormData).toBeTruthy();
    const kbRefsValue = capturedFormData.get('kb_references');
    expect(kbRefsValue).toBeNull();
  });
});
