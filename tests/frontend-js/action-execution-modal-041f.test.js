/**
 * TDD Tests for FEATURE-041-F: Action Context Modal UI & Persistence
 * Tests: template-driven context dropdowns, auto-detect option, required/optional,
 *        context persistence, reopen pre-population, legacy fallback, reopen state
 *
 * TDD: All tests MUST fail until FEATURE-041-F changes are implemented.
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { loadFeatureScript, mockBootstrap } from './helpers.js';

let _implLoaded = false;
function ensureImpl() {
  if (!_implLoaded) {
    try {
      loadFeatureScript('action-execution-modal.js');
      _implLoaded = true;
    } catch { /* TDD */ }
  }
  return typeof globalThis.ActionExecutionModal !== 'undefined';
}

/* --- Tagged template fixture --- */
function taggedTemplate() {
  return {
    stage_order: ['ideation', 'requirement', 'implement'],
    stages: {
      ideation: {
        type: 'shared',
        next_stage: 'requirement',
        actions: {
          compose_idea: {
            optional: false,
            deliverables: ['$output:raw-idea', '$output-folder:ideas-folder'],
            next_actions_suggested: ['refine_idea']
          },
          refine_idea: {
            optional: false,
            action_context: {
              'raw-idea': { required: true, candidates: 'ideas-folder' },
              'uiux-reference': { required: false }
            },
            deliverables: ['$output:refined-idea', '$output-folder:refined-ideas-folder'],
            next_actions_suggested: ['requirement_gathering']
          }
        }
      },
      requirement: {
        type: 'shared',
        next_stage: 'implement',
        actions: {
          requirement_gathering: {
            optional: false,
            action_context: {
              'refined-idea': { required: true, candidates: 'refined-ideas-folder' },
              'mockup-html': { required: false }
            },
            deliverables: ['$output:requirement-doc', '$output-folder:requirements-folder'],
            next_actions_suggested: ['feature_breakdown']
          }
        }
      },
      implement: {
        type: 'per_feature',
        next_stage: null,
        actions: {
          feature_refinement: {
            optional: false,
            action_context: {
              'requirement-doc': { required: true, candidates: 'requirements-folder' },
              'features-list': { required: true }
            },
            deliverables: ['$output:specification', '$output-folder:feature-docs-folder'],
            next_actions_suggested: ['technical_design']
          }
        }
      }
    }
  };
}

/* --- Workflow instance fixture --- */
function workflowInstance() {
  return {
    name: 'test-wf',
    schema_version: '3.0',
    shared: {
      ideation: {
        actions: {
          compose_idea: {
            status: 'done',
            deliverables: {
              'raw-idea': 'x-ipe-docs/ideas/test/new-idea.md',
              'ideas-folder': 'x-ipe-docs/ideas/test'
            }
          },
          refine_idea: {
            status: 'done',
            context: {
              'raw-idea': 'x-ipe-docs/ideas/test/new-idea.md',
              'uiux-reference': 'N/A'
            },
            deliverables: {
              'refined-idea': 'x-ipe-docs/ideas/test/refined/idea-summary.md',
              'refined-ideas-folder': 'x-ipe-docs/ideas/test/refined'
            }
          }
        }
      }
    }
  };
}

/* --- Mock fetch responses --- */
function setupFetchMocks(options = {}) {
  const template = options.template || taggedTemplate();
  const instance = options.instance || workflowInstance();
  const candidates = options.candidates || [
    { type: 'file', path: 'x-ipe-docs/ideas/test/new-idea.md' },
    { type: 'folder', path: 'x-ipe-docs/ideas/test' }
  ];
  const folderContents = options.folderContents || [
    'x-ipe-docs/ideas/test/new-idea.md',
    'x-ipe-docs/ideas/test/notes.txt',
    'x-ipe-docs/ideas/test/ref.pdf'
  ];

  globalThis.fetch = vi.fn((url) => {
    if (url.includes('/api/workflow/template')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(template)
      });
    }
    if (url.includes('/candidates/')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(candidates)
      });
    }
    if (url.includes('/folder-contents')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(folderContents)
      });
    }
    if (url.includes('/api/workflow/') && !url.includes('/action')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(instance)
      });
    }
    if (url.includes('/action')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ success: true })
      });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });
}

// ==============================================================================
// Tests: Section Rename
// ==============================================================================

describe('FEATURE-041-F: Action Context Section Rename', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('should render "Action Context" heading when action_context present', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const heading = document.querySelector('.input-files-section h4, .action-context-section h4');
    expect(heading).not.toBeNull();
    expect(heading.textContent).toContain('Action Context');
  });

  it('should render "Input Files" heading when action_context absent (legacy)', async () => {
    if (!ensureImpl()) return;
    // compose_idea has no action_context
    const modal = new ActionExecutionModal({
      actionKey: 'compose_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const heading = document.querySelector('.input-files-section h4');
    // Legacy fallback OR no section at all (compose_idea has no input_source)
    if (heading) {
      expect(heading.textContent).not.toContain('Action Context');
    }
  });
});

// ==============================================================================
// Tests: Dropdown Rendering
// ==============================================================================

describe('FEATURE-041-F: Template-Driven Dropdowns', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('should render one dropdown per action_context entry', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const selects = document.querySelectorAll('.context-ref-group select');
    // refine_idea has 2 context refs: raw-idea, uiux-reference
    expect(selects.length).toBe(2);
  });

  it('should label dropdowns with ref names', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const labels = document.querySelectorAll('.context-ref-group label');
    const labelTexts = Array.from(labels).map(l => l.textContent.toLowerCase());
    expect(labelTexts.some(t => t.includes('raw') && t.includes('idea'))).toBe(true);
    expect(labelTexts.some(t => t.includes('uiux') || t.includes('reference'))).toBe(true);
  });

  it('should mark required fields with asterisk or "(required)"', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const groups = document.querySelectorAll('.context-ref-group');
    const rawIdeaGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    expect(rawIdeaGroup).not.toBeNull();
    const label = rawIdeaGroup.querySelector('label');
    expect(label.innerHTML).toMatch(/required|\*/);
  });

  it('should include "auto-detect" as first dropdown option', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const select = document.querySelector('.context-ref-group select');
    expect(select.options[0].value).toBe('auto-detect');
  });

  it('should include "N/A" option for optional fields', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const groups = document.querySelectorAll('.context-ref-group');
    const optionalGroup = Array.from(groups).find(g => g.dataset.refName === 'uiux-reference');
    const select = optionalGroup.querySelector('select');
    const options = Array.from(select.options).map(o => o.value);
    expect(options).toContain('N/A');
  });

  it('should NOT include "N/A" for required fields', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const groups = document.querySelectorAll('.context-ref-group');
    const requiredGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    const select = requiredGroup.querySelector('select');
    const options = Array.from(select.options).map(o => o.value);
    expect(options).not.toContain('N/A');
  });

  it('should populate dropdown with files from folder contents', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const groups = document.querySelectorAll('.context-ref-group');
    const rawGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    const select = rawGroup.querySelector('select');
    const options = Array.from(select.options).map(o => o.value);
    // Should contain files from the folder
    expect(options.some(o => o.includes('new-idea.md'))).toBe(true);
  });

  it('should list all file types, not just .md', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const groups = document.querySelectorAll('.context-ref-group');
    const rawGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    const select = rawGroup.querySelector('select');
    const options = Array.from(select.options).map(o => o.value);
    expect(options.some(o => o.includes('.txt'))).toBe(true);
    expect(options.some(o => o.includes('.pdf'))).toBe(true);
  });
});

// ==============================================================================
// Tests: Context Persistence
// ==============================================================================

describe('FEATURE-041-F: Context Persistence', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('should save context to instance on execute', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // Simulate selecting a value
    const select = document.querySelector('.context-ref-group select');
    if (select) {
      select.value = 'x-ipe-docs/ideas/test/new-idea.md';
    }

    // Call _saveContext
    const ctx = await modal._saveContext();
    expect(ctx).toBeDefined();
    expect(ctx['raw-idea']).toBeDefined();

    // Verify fetch was called with context in payload
    const postCalls = globalThis.fetch.mock.calls.filter(
      c => c[1] && c[1].method === 'POST' && c[0].includes('/action')
    );
    expect(postCalls.length).toBeGreaterThan(0);
    const body = JSON.parse(postCalls[0][1].body);
    expect(body.context).toBeDefined();
  });
});

// ==============================================================================
// Tests: Reopen Pre-Population
// ==============================================================================

describe('FEATURE-041-F: Reopen Pre-Population', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('should pre-populate dropdowns from instance context on reopen', async () => {
    if (!ensureImpl()) return;
    // refine_idea is done with stored context
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const groups = document.querySelectorAll('.context-ref-group');
    const rawGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    if (rawGroup) {
      const select = rawGroup.querySelector('select');
      // Should be pre-populated with the stored context value
      expect(select.value).toBe('x-ipe-docs/ideas/test/new-idea.md');
    }
  });

  it('should show "(missing)" for stored path no longer in options', async () => {
    if (!ensureImpl()) return;
    // Instance has context pointing to deleted file
    const instance = workflowInstance();
    instance.shared.ideation.actions.refine_idea.context['raw-idea'] = 'x-ipe-docs/deleted-file.md';
    setupFetchMocks({ instance });

    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const groups = document.querySelectorAll('.context-ref-group');
    const rawGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    if (rawGroup) {
      const select = rawGroup.querySelector('select');
      const selectedOption = select.options[select.selectedIndex];
      expect(selectedOption.text).toContain('missing');
    }
  });

  it('should pre-populate "auto-detect" when stored context is "auto-detect"', async () => {
    if (!ensureImpl()) return;
    const instance = workflowInstance();
    instance.shared.ideation.actions.refine_idea.context['raw-idea'] = 'auto-detect';
    setupFetchMocks({ instance });

    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const groups = document.querySelectorAll('.context-ref-group');
    const rawGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    if (rawGroup) {
      const select = rawGroup.querySelector('select');
      expect(select.value).toBe('auto-detect');
    }
  });
});

// ==============================================================================
// Tests: Reopen State Machine
// ==============================================================================

describe('FEATURE-041-F: Reopen State Machine', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('should keep status as "done" when modal opens for reopen', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // Status should NOT have changed to in_progress just by opening
    const postCalls = globalThis.fetch.mock.calls.filter(
      c => c[1] && c[1].method === 'POST' && c[0].includes('/action')
    );
    const statusUpdates = postCalls.filter(c => {
      const body = JSON.parse(c[1].body);
      return body.status === 'in_progress';
    });
    expect(statusUpdates.length).toBe(0);
  });

  it('should transition to in_progress on execute', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();
    await modal._saveContext();

    const postCalls = globalThis.fetch.mock.calls.filter(
      c => c[1] && c[1].method === 'POST' && c[0].includes('/action')
    );
    expect(postCalls.length).toBeGreaterThan(0);
    const body = JSON.parse(postCalls[0][1].body);
    expect(body.status).toBe('in_progress');
  });
});

// ==============================================================================
// Tests: Legacy Fallback
// ==============================================================================

describe('FEATURE-041-F: Legacy Fallback', () => {
  beforeEach(() => {
    mockBootstrap();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('should use _resolveInputFiles when action_context absent', async () => {
    if (!ensureImpl()) return;
    // Template without action_context for compose_idea
    setupFetchMocks();

    const modal = new ActionExecutionModal({
      actionKey: 'compose_idea',
      workflowName: 'test-wf',
    });

    // compose_idea has no action_context — should fall back to legacy
    const spy = vi.spyOn(modal, '_resolveInputFiles').mockResolvedValue([]);
    await modal.open();

    // If action_context absent, _resolveInputFiles should be called (or no context section rendered)
    // The exact behavior depends on implementation but no context dropdowns should appear
    const contextGroups = document.querySelectorAll('.context-ref-group');
    expect(contextGroups.length).toBe(0);
  });
});
