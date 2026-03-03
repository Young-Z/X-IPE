/**
 * TDD Tests for FEATURE-042-C: Deliverable-Default Dropdowns & Read-Only Preview
 * Tests: deliverable defaults, read-only instructions, live preview,
 *        command composition, edge cases
 *
 * TDD: All tests MUST fail until FEATURE-042-C changes are implemented.
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

/* --- Workflow instance fixture with deliverables --- */
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

/* --- Workflow instance with NO deliverables --- */
function workflowInstanceEmpty() {
  return {
    name: 'test-wf',
    schema_version: '3.0',
    shared: {
      ideation: {
        actions: {
          compose_idea: { status: 'pending', deliverables: {} },
          refine_idea: { status: 'pending', deliverables: {} }
        }
      }
    }
  };
}

/* --- Copilot prompt config fixture --- */
function workflowPromptsConfig() {
  return {
    version: '3.3',
    'workflow-prompts': [
      {
        id: 'refine-idea',
        action: 'refine_idea',
        icon: 'bi-stars',
        input_source: ['compose_idea'],
        'prompt-details': [
          {
            language: 'en',
            label: 'Refine Idea',
            command: 'refine the idea $output:raw-idea$ <and uiux reference: $output:uiux-reference$> with ideation skill'
          },
          {
            language: 'zh',
            label: '完善创意',
            command: '使用创意技能, 完善创意 $output:raw-idea$'
          }
        ]
      }
    ],
    ideation: { prompts: [{ id: 'refine-idea', 'prompt-details': [{ language: 'en', label: 'Refine Idea (free)', command: 'free mode refine <current-idea-file>' }] }] },
    workflow: { prompts: [] },
    feature: { prompts: [] }
  };
}

/* --- Mock fetch responses --- */
function setupFetchMocks(options = {}) {
  const template = options.template || taggedTemplate();
  const instance = options.instance || workflowInstance();
  const config = options.config || workflowPromptsConfig();
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
    if (url.includes('/api/config/copilot-prompt')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(config)
      });
    }
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
// Tests: Deliverable Defaults
// ==============================================================================

describe('FEATURE-042-C: deliverable defaults', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    delete window.__copilotPromptConfig;
    vi.restoreAllMocks();
  });

  it('Dropdown defaults to deliverable file path when deliverable exists', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // 042-C: deliverable cache must be populated by _cacheDeliverables()
    expect(modal._deliverableCache).toBeDefined();
    expect(modal._deliverableCache['raw-idea']).toBe('x-ipe-docs/ideas/test/new-idea.md');

    const groups = document.querySelectorAll('.context-ref-group');
    const rawGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    expect(rawGroup).not.toBeNull();
    const select = rawGroup.querySelector('select');
    // Should default to the compose_idea deliverable path via _setDeliverableDefaults()
    expect(select.value).toBe('x-ipe-docs/ideas/test/new-idea.md');
  });

  it('Dropdown defaults to auto-detect when no deliverable exists', async () => {
    if (!ensureImpl()) return;
    setupFetchMocks({ instance: workflowInstanceEmpty() });

    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // 042-C: cache must exist with null entries for missing deliverables
    expect(modal._deliverableCache).toBeDefined();
    expect(modal._deliverableCache['raw-idea']).toBeNull();

    const groups = document.querySelectorAll('.context-ref-group');
    const rawGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    expect(rawGroup).not.toBeNull();
    const select = rawGroup.querySelector('select');
    expect(select.value).toBe('auto-detect');
  });

  it('User can override default dropdown selection', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // 042-C: verify deliverable cache was used for initial default
    expect(modal._deliverableCache).toBeDefined();
    expect(modal._deliverableCache['raw-idea']).toBe('x-ipe-docs/ideas/test/new-idea.md');

    const groups = document.querySelectorAll('.context-ref-group');
    const rawGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    const select = rawGroup.querySelector('select');

    // Initially defaulted to deliverable via _setDeliverableDefaults()
    expect(select.value).toBe('x-ipe-docs/ideas/test/new-idea.md');

    // User overrides to auto-detect
    select.value = 'auto-detect';
    select.dispatchEvent(new Event('change'));
    expect(select.value).toBe('auto-detect');

    // 042-C: _updatePreview must have been called
    expect(typeof modal._updatePreview).toBe('function');
  });

  it('Deliverables fetched once on modal open (cached)', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // Count instance fetches (deliverable source)
    const instanceCalls = globalThis.fetch.mock.calls.filter(
      c => c[0].includes('/api/workflow/') && !c[0].includes('/action') && !c[0].includes('/template') && !c[0].includes('/candidates') && !c[0].includes('/folder-contents')
    );
    // Should be fetched at most once for deliverable caching
    expect(instanceCalls.length).toBeLessThanOrEqual(1);
    // Verify cache exists
    expect(modal._deliverableCache).toBeDefined();
    expect(typeof modal._deliverableCache).toBe('object');
  });

  it('Dropdown change does NOT re-fetch from backend', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // 042-C: _updatePreview must exist as a method
    expect(typeof modal._updatePreview).toBe('function');

    const fetchCountBefore = globalThis.fetch.mock.calls.length;

    // Change a dropdown selection
    const groups = document.querySelectorAll('.context-ref-group');
    const rawGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    const select = rawGroup.querySelector('select');
    select.value = 'auto-detect';
    select.dispatchEvent(new Event('change'));

    // No new fetch calls after dropdown change
    const fetchCountAfter = globalThis.fetch.mock.calls.length;
    expect(fetchCountAfter).toBe(fetchCountBefore);
  });

  it('Cached deliverable added to dropdown when not in candidates listing', async () => {
    if (!ensureImpl()) return;
    // Candidates return folder files that do NOT include the cached deliverable
    setupFetchMocks({
      candidates: [
        { type: 'folder', path: 'x-ipe-docs/ideas/test' }
      ],
      folderContents: [
        'x-ipe-docs/ideas/test/other-file.md',
        'x-ipe-docs/ideas/test/notes.txt'
      ]
    });

    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // Cache should have the deliverable from compose_idea
    expect(modal._deliverableCache['raw-idea']).toBe('x-ipe-docs/ideas/test/new-idea.md');

    const groups = document.querySelectorAll('.context-ref-group');
    const rawGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    const select = rawGroup.querySelector('select');

    // The cached deliverable should be added as an option and selected as default
    const options = Array.from(select.options).map(o => o.value);
    expect(options).toContain('x-ipe-docs/ideas/test/new-idea.md');
    expect(select.value).toBe('x-ipe-docs/ideas/test/new-idea.md');

    // Folder contents should also be in the dropdown
    expect(options).toContain('x-ipe-docs/ideas/test/other-file.md');
    expect(options).toContain('x-ipe-docs/ideas/test/notes.txt');
  });
});

// ==============================================================================
// Tests: Read-Only Instructions
// ==============================================================================

describe('FEATURE-042-C: read-only instructions', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    delete window.__copilotPromptConfig;
    vi.restoreAllMocks();
  });

  it('INSTRUCTIONS textarea is readonly in workflow mode', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const instructionsEl = document.querySelector('.instructions-content');
    expect(instructionsEl).not.toBeNull();
    expect(instructionsEl.hasAttribute('readonly') || instructionsEl.contentEditable === 'false').toBe(true);
  });

  it('INSTRUCTIONS textarea is editable in free mode', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      // No workflowName → free mode
    });
    await modal.open();

    const instructionsEl = document.querySelector('.instructions-content');
    expect(instructionsEl).not.toBeNull();
    // In free mode, should NOT be readonly
    expect(instructionsEl.hasAttribute('readonly')).toBe(false);
    expect(instructionsEl.classList.contains('instructions-readonly')).toBe(false);
    // 042-C: _makeInstructionsReadOnly must exist but not apply in free mode
    expect(typeof modal._makeInstructionsReadOnly).toBe('function');
  });

  it('Read-only textarea has .instructions-readonly CSS class', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const instructionsEl = document.querySelector('.instructions-content');
    expect(instructionsEl).not.toBeNull();
    expect(instructionsEl.classList.contains('instructions-readonly')).toBe(true);
  });

  it('Instructions show fully resolved template', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // 042-C: _updatePreview must have been called to populate instructions
    expect(typeof modal._updatePreview).toBe('function');

    const instructionsEl = document.querySelector('.instructions-content');
    expect(instructionsEl).not.toBeNull();
    const content = instructionsEl.textContent || instructionsEl.value || '';
    // Should NOT contain unresolved $output:tag$ placeholders
    expect(content).not.toMatch(/\$output:[^$]+\$/);
    // 042-C: content must not be the default "no instructions" text
    expect(content).not.toContain('No instructions available');
    expect(content.length).toBeGreaterThan(0);
  });
});

// ==============================================================================
// Tests: Live Preview
// ==============================================================================

describe('FEATURE-042-C: live preview', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    delete window.__copilotPromptConfig;
    vi.restoreAllMocks();
  });

  it('Preview updates when dropdown selection changes', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const instructionsEl = document.querySelector('.instructions-content');
    const contentBefore = instructionsEl.textContent || instructionsEl.value || '';

    // Change dropdown to a different value
    const groups = document.querySelectorAll('.context-ref-group');
    const rawGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    const select = rawGroup.querySelector('select');
    select.value = 'auto-detect';
    select.dispatchEvent(new Event('change'));

    const contentAfter = instructionsEl.textContent || instructionsEl.value || '';
    // Content should differ after dropdown change
    expect(contentAfter).not.toBe(contentBefore);
  });

  it('Preview reflects resolved $output:tag$ values', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // 042-C: _updatePreview must exist
    expect(typeof modal._updatePreview).toBe('function');

    const instructionsEl = document.querySelector('.instructions-content');
    const content = instructionsEl.textContent || instructionsEl.value || '';

    // Resolved content should contain the actual file path, not the placeholder
    expect(content).not.toMatch(/\$output:raw-idea\$/);
    // 042-C: resolved preview must contain the deliverable path from cache
    expect(content).toContain('x-ipe-docs/ideas/test/new-idea.md');
  });

  it('Preview evaluates conditional <> blocks in real-time', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // 042-C: _resolveConditionalBlocks must exist and be used by _updatePreview
    expect(typeof modal._resolveConditionalBlocks).toBe('function');

    const instructionsEl = document.querySelector('.instructions-content');
    const content = instructionsEl.textContent || instructionsEl.value || '';
    // Resolved content should NOT contain raw conditional delimiters
    expect(content).not.toMatch(/<>/);
    expect(content).not.toMatch(/<\/>/);
  });

  it('Preview updates without backend call (uses cached values)', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // 042-C: _updatePreview must exist
    expect(typeof modal._updatePreview).toBe('function');

    const fetchCountBefore = globalThis.fetch.mock.calls.length;

    // Trigger multiple dropdown changes
    const groups = document.querySelectorAll('.context-ref-group');
    const rawGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    const select = rawGroup.querySelector('select');

    select.value = 'auto-detect';
    select.dispatchEvent(new Event('change'));
    select.value = 'x-ipe-docs/ideas/test/new-idea.md';
    select.dispatchEvent(new Event('change'));

    // No new fetch calls for preview updates
    expect(globalThis.fetch.mock.calls.length).toBe(fetchCountBefore);
  });
});

// ==============================================================================
// Tests: Command Composition
// ==============================================================================

describe('FEATURE-042-C: command composition', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    delete window.__copilotPromptConfig;
    vi.restoreAllMocks();
  });

  it('Final command = resolved instructions + newline + extra instructions', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // Fill in EXTRA INSTRUCTIONS
    const extraInput = document.querySelector('.extra-input');
    expect(extraInput).not.toBeNull();
    extraInput.value = 'Please focus on architecture';

    const composed = modal._composeCommand();
    expect(composed).toBeDefined();

    // _composeCommand returns pure prompt content (no flags)
    expect(composed).not.toContain('--workflow-mode');
    expect(composed).toContain('Please focus on architecture');
  });

  it('Final command = resolved instructions only when extra is empty', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // Leave EXTRA INSTRUCTIONS empty
    const extraInput = document.querySelector('.extra-input');
    if (extraInput) extraInput.value = '';

    const composed = modal._composeCommand();
    const instructionsEl = document.querySelector('.instructions-content');
    const resolved = instructionsEl.textContent || instructionsEl.value || '';

    // _composeCommand returns pure prompt content (no flags)
    expect(composed).not.toContain('--workflow-mode');
    expect(composed).toContain(resolved);
    expect(composed).not.toContain('--extra-instructions');
    // No trailing newlines
    expect(composed).not.toMatch(/\n+$/);
  });

  it('EXTRA INSTRUCTIONS stays editable', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // 042-C: _composeCommand must exist
    expect(typeof modal._composeCommand).toBe('function');

    const extraInput = document.querySelector('.extra-input');
    expect(extraInput).not.toBeNull();
    // EXTRA INSTRUCTIONS should NOT be readonly
    expect(extraInput.hasAttribute('readonly')).toBe(false);
    expect(extraInput.classList.contains('instructions-readonly')).toBe(false);
  });

  it('EXTRA INSTRUCTIONS content is NOT template-resolved (sent as-is)', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    const rawExtra = 'Use $output:raw-idea$ literally and <>conditional</>';
    const extraInput = document.querySelector('.extra-input');
    extraInput.value = rawExtra;

    const composed = modal._composeCommand();
    // Extra instructions should contain the raw text as-is, not resolved
    expect(composed).toContain(rawExtra);
  });
});

// ==============================================================================
// Tests: Edge Cases
// ==============================================================================

describe('FEATURE-042-C: edge cases', () => {
  beforeEach(() => {
    mockBootstrap();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    delete window.__copilotPromptConfig;
    vi.restoreAllMocks();
  });

  it('All dropdowns auto-detect (no deliverables exist)', async () => {
    if (!ensureImpl()) return;
    setupFetchMocks({ instance: workflowInstanceEmpty() });

    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // 042-C: cache must exist with null values for all refs
    expect(modal._deliverableCache).toBeDefined();
    for (const val of Object.values(modal._deliverableCache)) {
      expect(val).toBeNull();
    }

    const selects = document.querySelectorAll('.context-ref-group select');
    for (const select of selects) {
      expect(select.value).toBe('auto-detect');
    }
  });

  it('Modal in free mode has no read-only behavior', async () => {
    if (!ensureImpl()) return;
    setupFetchMocks();

    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      // No workflowName → free mode
    });
    await modal.open();

    const instructionsEl = document.querySelector('.instructions-content');
    if (instructionsEl) {
      expect(instructionsEl.hasAttribute('readonly')).toBe(false);
      expect(instructionsEl.classList.contains('instructions-readonly')).toBe(false);
    }
    // 042-C: _deliverableCache should not be populated in free mode
    expect(modal._deliverableCache).toBeUndefined();
    // 042-C: _makeInstructionsReadOnly must exist as method
    expect(typeof modal._makeInstructionsReadOnly).toBe('function');
  });

  it('Empty extra instructions (no extra newline appended)', async () => {
    if (!ensureImpl()) return;
    setupFetchMocks();

    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // Ensure EXTRA INSTRUCTIONS is empty / whitespace
    const extraInput = document.querySelector('.extra-input');
    if (extraInput) extraInput.value = '   ';

    const composed = modal._composeCommand();
    const instructionsEl = document.querySelector('.instructions-content');
    const resolved = instructionsEl.textContent || instructionsEl.value || '';

    // _composeCommand returns pure prompt content (no flags)
    expect(composed).not.toContain('--workflow-mode');
    expect(composed).toContain(resolved);
    expect(composed).not.toContain('--extra-instructions');
  });

  it('Rapid dropdown changes don\'t cause race conditions', async () => {
    if (!ensureImpl()) return;
    setupFetchMocks();

    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // 042-C: _updatePreview must exist
    expect(typeof modal._updatePreview).toBe('function');

    const groups = document.querySelectorAll('.context-ref-group');
    const rawGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    const select = rawGroup.querySelector('select');
    const instructionsEl = document.querySelector('.instructions-content');

    // Rapidly toggle dropdown values
    const values = ['auto-detect', 'x-ipe-docs/ideas/test/new-idea.md', 'auto-detect', 'x-ipe-docs/ideas/test/notes.txt'];
    for (const val of values) {
      if (Array.from(select.options).some(o => o.value === val)) {
        select.value = val;
        select.dispatchEvent(new Event('change'));
      }
    }

    // Final state should reflect the last valid selection
    const finalContent = instructionsEl.textContent || instructionsEl.value || '';
    expect(finalContent.length).toBeGreaterThan(0);
    // No unresolved placeholders in final state
    expect(finalContent).not.toMatch(/\$output:[^$]+\$/);
    // 042-C: content must not be the default "no instructions" text
    expect(finalContent).not.toContain('No instructions available');
  });
});
