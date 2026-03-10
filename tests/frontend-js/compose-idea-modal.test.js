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
