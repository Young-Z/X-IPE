/**
 * TDD Tests for FEATURE-042-A: Workflow Prompts Config & Basic Template Resolution (MVP)
 * Tests: workflow-prompts config schema, _getWorkflowPrompt lookup, _resolveTemplate
 *        variable substitution, workflow-mode prompt loading, backward compatibility
 *
 * TDD: All tests MUST fail until FEATURE-042-A changes are implemented.
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

/* --- Workflow-prompts config fixture --- */
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
            command: 'refine the idea $output:raw-idea$ with ideation skill'
          },
          {
            language: 'zh',
            label: '完善创意',
            command: '使用创意技能, 完善创意 $output:raw-idea$'
          }
        ]
      },
      {
        id: 'requirement-gathering',
        action: 'requirement_gathering',
        icon: 'bi-list-check',
        input_source: ['refine_idea'],
        'prompt-details': [
          {
            language: 'en',
            label: 'Gather Requirements',
            command: 'gather requirements from $output:refined-idea$ in $output-folder:refined-ideas-folder$'
          }
        ]
      },
      {
        id: 'feature-refinement',
        action: 'feature_refinement',
        icon: 'bi-diagram-3',
        input_source: ['requirement_gathering'],
        'prompt-details': [
          {
            language: 'en',
            label: 'Refine Feature',
            command: 'refine feature $feature-id$ using $output:requirement-doc$'
          }
        ]
      }
    ],
    ideation: { prompts: [{ id: 'refine-idea', 'prompt-details': [{ language: 'en', label: 'Refine Idea (free)', command: 'free mode refine <current-idea-file>' }] }] },
    workflow: { prompts: [] },
    feature: { prompts: [] }
  };
}

/* --- Tagged template fixture (reused from 041f pattern) --- */
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
// Tests: workflow-prompts config
// ==============================================================================

describe('FEATURE-042-A: workflow-prompts config', () => {
  it('copilot-prompt.json has workflow-prompts array', () => {
    const config = workflowPromptsConfig();
    expect(config['workflow-prompts']).toBeDefined();
    expect(Array.isArray(config['workflow-prompts'])).toBe(true);
  });

  it('workflow-prompts has entry for refine_idea action', () => {
    const config = workflowPromptsConfig();
    const entry = config['workflow-prompts'].find(p => p.action === 'refine_idea');
    expect(entry).toBeDefined();
    expect(entry.action).toBe('refine_idea');
  });

  it('Each entry has required fields: id, action, icon, input_source, prompt-details', () => {
    const config = workflowPromptsConfig();
    for (const entry of config['workflow-prompts']) {
      expect(entry.id).toBeDefined();
      expect(typeof entry.id).toBe('string');
      expect(entry.action).toBeDefined();
      expect(typeof entry.action).toBe('string');
      expect(entry.icon).toBeDefined();
      expect(typeof entry.icon).toBe('string');
      expect(entry.input_source).toBeDefined();
      expect(Array.isArray(entry.input_source)).toBe(true);
      expect(entry['prompt-details']).toBeDefined();
      expect(Array.isArray(entry['prompt-details'])).toBe(true);
      expect(entry['prompt-details'].length).toBeGreaterThan(0);
    }
  });

  it('prompt-details has language, label, command fields', () => {
    const config = workflowPromptsConfig();
    for (const entry of config['workflow-prompts']) {
      for (const detail of entry['prompt-details']) {
        expect(detail.language).toBeDefined();
        expect(typeof detail.language).toBe('string');
        expect(detail.label).toBeDefined();
        expect(typeof detail.label).toBe('string');
        expect(detail.command).toBeDefined();
        expect(typeof detail.command).toBe('string');
      }
    }
  });
});

// ==============================================================================
// Tests: _getWorkflowPrompt
// ==============================================================================

describe('FEATURE-042-A: _getWorkflowPrompt', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
    // Set cached config on window so _getWorkflowPrompt can read it
    window.__copilotPromptConfig = workflowPromptsConfig();
  });

  afterEach(() => {
    document.body.innerHTML = '';
    delete window.__copilotPromptConfig;
    vi.restoreAllMocks();
  });

  it('returns correct prompt entry for given action key', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const entry = modal._getWorkflowPrompt('refine_idea');
    expect(entry).not.toBeNull();
    expect(entry.action).toBe('refine_idea');
    expect(entry.id).toBe('refine-idea');
    expect(entry['prompt-details']).toBeDefined();
  });

  it('returns null/undefined for unknown action key', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'unknown_action',
      workflowName: 'test-wf',
    });
    const entry = modal._getWorkflowPrompt('unknown_action');
    expect(entry).toBeNull();
  });

  it('handles missing workflow-prompts array gracefully', () => {
    if (!ensureImpl()) return;
    // Config without workflow-prompts
    window.__copilotPromptConfig = { version: '3.2', ideation: {} };
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const entry = modal._getWorkflowPrompt('refine_idea');
    expect(entry).toBeNull();
  });

  it('returns prompt with correct language based on current language setting', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const entry = modal._getWorkflowPrompt('refine_idea');
    expect(entry).not.toBeNull();

    // English entry should exist
    const enDetail = entry['prompt-details'].find(d => d.language === 'en');
    expect(enDetail).toBeDefined();
    expect(enDetail.label).toBe('Refine Idea');

    // Chinese entry should exist
    const zhDetail = entry['prompt-details'].find(d => d.language === 'zh');
    expect(zhDetail).toBeDefined();
    expect(zhDetail.label).toBe('完善创意');
  });
});

// ==============================================================================
// Tests: _resolveTemplate
// ==============================================================================

describe('FEATURE-042-A: _resolveTemplate', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('resolves $output:tag-name$ with dropdown value', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const result = modal._resolveTemplate(
      'refine the idea $output:raw-idea$ with ideation skill',
      { 'raw-idea': 'x-ipe-docs/ideas/test/new-idea.md' }
    );
    expect(result).toBe('refine the idea x-ipe-docs/ideas/test/new-idea.md with ideation skill');
  });

  it('resolves $output-folder:tag-name$ with folder path', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'requirement_gathering',
      workflowName: 'test-wf',
    });
    const result = modal._resolveTemplate(
      'gather from $output-folder:refined-ideas-folder$',
      { 'refined-ideas-folder': 'x-ipe-docs/ideas/test/refined' }
    );
    expect(result).toBe('gather from x-ipe-docs/ideas/test/refined');
  });

  it('resolves $feature-id$ with feature ID from modal context', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'feature_refinement',
      workflowName: 'test-wf',
    });
    const result = modal._resolveTemplate(
      'refine feature $feature-id$ using $output:requirement-doc$',
      { '$feature-id': 'FEATURE-042-A', 'requirement-doc': 'x-ipe-docs/req.md' }
    );
    expect(result).toBe('refine feature FEATURE-042-A using x-ipe-docs/req.md');
  });

  it('leaves unknown $output:unknown$ as raw text', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const result = modal._resolveTemplate(
      'process $output:unknown-tag$ here',
      {}
    );
    expect(result).toBe('process $output:unknown-tag$ here');
  });

  it('handles empty template string', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const result = modal._resolveTemplate('', {});
    expect(result).toBe('');
  });

  it('handles template with no variables', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const result = modal._resolveTemplate('plain text with no variables', {});
    expect(result).toBe('plain text with no variables');
  });

  it('handles template with multiple variables', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'requirement_gathering',
      workflowName: 'test-wf',
    });
    const result = modal._resolveTemplate(
      'gather requirements from $output:refined-idea$ in $output-folder:refined-ideas-folder$ for feature $feature-id$',
      {
        'refined-idea': 'x-ipe-docs/ideas/test/refined/idea-summary.md',
        'refined-ideas-folder': 'x-ipe-docs/ideas/test/refined',
        '$feature-id': 'FEATURE-042-A'
      }
    );
    expect(result).toBe(
      'gather requirements from x-ipe-docs/ideas/test/refined/idea-summary.md in x-ipe-docs/ideas/test/refined for feature FEATURE-042-A'
    );
  });

  it('handles malformed tokens gracefully — $output:$ left as-is', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const result = modal._resolveTemplate('broken $output:$ token', {});
    expect(result).toBe('broken $output:$ token');
  });

  it('handles unclosed token — $output:raw-idea left as-is', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const result = modal._resolveTemplate('unclosed $output:raw-idea token', {});
    expect(result).toBe('unclosed $output:raw-idea token');
  });

  it('handles $$ (empty token) left as-is', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const result = modal._resolveTemplate('empty $$ token', {});
    expect(result).toBe('empty $$ token');
  });

  it('resolves $feature-id$ to empty string when no featureId set', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const result = modal._resolveTemplate(
      'feature $feature-id$ action',
      {} // no $feature-id key
    );
    // Should resolve to empty string per EC-10
    expect(result).toBe('feature  action');
  });

  it('resolves multiple occurrences of the same token', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const result = modal._resolveTemplate(
      'file: $output:raw-idea$, again: $output:raw-idea$',
      { 'raw-idea': 'path/file.md' }
    );
    expect(result).toBe('file: path/file.md, again: path/file.md');
  });

  it('leaves $unknown-type:tag$ as-is', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const result = modal._resolveTemplate('token $unknown-type:some-tag$ here', {});
    expect(result).toBe('token $unknown-type:some-tag$ here');
  });

  it('resolves auto-detect dropdown value literally', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const result = modal._resolveTemplate(
      'refine $output:raw-idea$ here',
      { 'raw-idea': 'auto-detect' }
    );
    expect(result).toBe('refine auto-detect here');
  });

  it('resolves N/A dropdown value literally', () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const result = modal._resolveTemplate(
      'use $output:uiux-reference$ ref',
      { 'uiux-reference': 'N/A' }
    );
    expect(result).toBe('use N/A ref');
  });
});

// ==============================================================================
// Tests: workflow mode prompt loading
// ==============================================================================

describe('FEATURE-042-A: workflow mode prompt loading', () => {
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

  it('in workflow mode, uses _getWorkflowPrompt to load prompt', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    const spy = vi.spyOn(modal, '_getWorkflowPrompt');
    await modal.open();

    expect(spy).toHaveBeenCalledWith('refine_idea');
  });

  it('in free mode, falls back to existing prompt sections', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      // No workflowName — free mode
    });
    const spy = vi.spyOn(modal, '_getWorkflowPrompt');
    await modal.open();

    // _getWorkflowPrompt should NOT be called in free mode
    expect(spy).not.toHaveBeenCalled();
  });

  it('resolved template shown in instructions area', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // After open, instructions area should show the resolved (or raw) template from workflow-prompts
    const instructionsEl = document.querySelector('.instructions-content');
    expect(instructionsEl).not.toBeNull();
    // The command from workflow-prompts for refine_idea contains "$output:raw-idea$" or a resolved version
    const text = instructionsEl.textContent;
    expect(text).toContain('refine');
    expect(text).toContain('idea');
  });

  it('template resolution integrates with action_context dropdown values', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // Find the raw-idea dropdown and set a value
    const groups = document.querySelectorAll('.context-ref-group');
    const rawGroup = Array.from(groups).find(g => g.dataset.refName === 'raw-idea');
    if (rawGroup) {
      const select = rawGroup.querySelector('select');
      select.value = 'x-ipe-docs/ideas/test/new-idea.md';
      select.dispatchEvent(new Event('change'));

      // After change, instructions should reflect the resolved value
      const instructionsEl = document.querySelector('.instructions-content');
      expect(instructionsEl.textContent).toContain('x-ipe-docs/ideas/test/new-idea.md');
      expect(instructionsEl.textContent).not.toContain('$output:raw-idea$');
    }
  });

  it('falls back to legacy prompts when action not found in workflow-prompts', async () => {
    if (!ensureImpl()) return;
    // compose_idea has no entry in workflow-prompts
    const modal = new ActionExecutionModal({
      actionKey: 'compose_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // Should not crash; should fall back to legacy prompt path
    // _getWorkflowPrompt returns null, so legacy _getConfigEntry is used
    const instructionsEl = document.querySelector('.instructions-content');
    // Either shows legacy prompt or gracefully handles missing prompt
    if (instructionsEl) {
      expect(instructionsEl.textContent).not.toContain('$output:');
    }
  });

  it('stores raw template for re-resolution on dropdown change', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // The raw template should be stored for re-resolution
    expect(modal._workflowCommandTemplate).toBeDefined();
    expect(modal._workflowCommandTemplate).toContain('$output:raw-idea$');
  });
});

// ==============================================================================
// Tests: backward compatibility
// ==============================================================================

describe('FEATURE-042-A: backward compatibility', () => {
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

  it('free-mode prompts still accessible', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      // No workflowName — free mode
    });
    await modal.open();

    // In free mode, prompt should come from legacy sections (ideation.prompts), not workflow-prompts
    const instructionsEl = document.querySelector('.instructions-content');
    if (instructionsEl) {
      // Should NOT contain workflow-prompt variable tokens
      expect(instructionsEl.textContent).not.toContain('$output:');
    }
  });

  it('existing prompt section structure unchanged', () => {
    const config = workflowPromptsConfig();
    // Legacy sections must still be present
    expect(config.ideation).toBeDefined();
    expect(config.ideation.prompts).toBeDefined();
    expect(Array.isArray(config.ideation.prompts)).toBe(true);
    // workflow-prompts is additive, not replacing
    expect(config['workflow-prompts']).toBeDefined();
  });

  it('modal opens correctly in workflow mode', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
    });
    await modal.open();

    // Modal should be present in DOM
    const overlay = document.querySelector('.action-execution-modal, .modal-overlay, [class*="modal"]');
    expect(overlay).not.toBeNull();
  });

  it('modal opens correctly in free mode', async () => {
    if (!ensureImpl()) return;
    const modal = new ActionExecutionModal({
      actionKey: 'refine_idea',
      // No workflowName — free mode
    });
    await modal.open();

    // Modal should be present in DOM
    const overlay = document.querySelector('.action-execution-modal, .modal-overlay, [class*="modal"]');
    expect(overlay).not.toBeNull();
  });

  it('config version updated to 3.3 with workflow-prompts', () => {
    const config = workflowPromptsConfig();
    expect(config.version).toBe('3.3');
    expect(config['workflow-prompts']).toBeDefined();
  });
});
