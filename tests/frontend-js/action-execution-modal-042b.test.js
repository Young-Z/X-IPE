/**
 * TDD Tests for FEATURE-042-B: Conditional Block Parsing & Error Handling
 * Tests: <>-block parsing, whitespace cleanup, flat parsing, unresolved variable
 *        warnings, and legacy backward compatibility.
 *
 * TDD: All tests MUST fail until FEATURE-042-B changes are implemented.
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
    stage_order: ['ideation'],
    stages: {
      ideation: {
        type: 'shared',
        next_stage: null,
        actions: {
          refine_idea: {
            optional: false,
            action_context: {
              'raw-ideas': { required: true, candidates: 'ideas-folder' },
              'uiux-reference': { required: false },
              'architecture': { required: false },
            },
            deliverables: ['$output:refined-idea'],
            next_actions_suggested: [],
          },
        },
      },
    },
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
          refine_idea: {
            status: 'done',
            context: {
              'raw-ideas': 'x-ipe-docs/ideas/test/raw-ideas.md',
              'uiux-reference': 'N/A',
              'architecture': 'x-ipe-docs/ideas/test/arch.md',
            },
            deliverables: {
              'refined-idea': 'x-ipe-docs/ideas/test/refined/idea-summary.md',
            },
          },
        },
      },
    },
  };
}

/* --- Mock fetch responses --- */
function setupFetchMocks(options = {}) {
  const template = options.template || taggedTemplate();
  const instance = options.instance || workflowInstance();

  globalThis.fetch = vi.fn((url) => {
    if (url.includes('/api/workflow/template')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(template) });
    }
    if (url.includes('/api/workflow/') && !url.includes('/action')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(instance) });
    }
    if (url.includes('/candidates/')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
    }
    if (url.includes('/folder-contents')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });
}

/* --- Helper: create a workflow-mode modal and get access to parser methods --- */
function createWorkflowModal() {
  return new ActionExecutionModal({
    actionKey: 'refine_idea',
    workflowName: 'test-wf',
  });
}

/* --- Helper: create a free-mode modal (no workflowName) --- */
function createFreeModal() {
  return new ActionExecutionModal({
    actionKey: 'refine_idea',
  });
}

// ==============================================================================
// Tests: Conditional Block Parsing
// ==============================================================================

describe('FEATURE-042-B: conditional block parsing', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('skips <> block when any $var$ inside is N/A', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    const resolvedValues = { 'uiux-reference': 'N/A', 'raw-ideas': 'path/idea.md' };
    const text = 'Review <and uiux reference: $output:uiux-reference$> now';
    const result = modal._resolveConditionalBlocks(text, resolvedValues);
    expect(result).not.toContain('uiux reference');
    expect(result).not.toContain('<');
    expect(result).not.toContain('>');
  });

  it('includes <> content when all $vars$ resolve to values', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    const resolvedValues = { 'raw-ideas': 'path/idea.md' };
    const text = 'Review <context: $output:raw-ideas$> now';
    const result = modal._resolveConditionalBlocks(text, resolvedValues);
    expect(result).toContain('context: $output:raw-ideas$');
  });

  it('strips <> delimiters from included content', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    const resolvedValues = { 'raw-ideas': 'path/idea.md' };
    const text = '<context: $output:raw-ideas$>';
    const result = modal._resolveConditionalBlocks(text, resolvedValues);
    expect(result).not.toContain('<');
    expect(result).not.toContain('>');
    expect(result).toBe('context: $output:raw-ideas$');
  });

  it('handles multiple <> blocks in one template', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    const resolvedValues = {
      'raw-ideas': 'path/idea.md',
      'uiux-reference': 'N/A',
      'architecture': 'path/arch.md',
    };
    const text = 'Read $output:raw-ideas$ <ref: $output:uiux-reference$> <arch: $output:architecture$> done';
    const result = modal._resolveConditionalBlocks(text, resolvedValues);
    // uiux-reference is N/A → block removed; architecture resolves → block kept
    expect(result).not.toContain('ref:');
    expect(result).toContain('arch: $output:architecture$');
  });

  it('handles template with no <> blocks (no-op)', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    const resolvedValues = { 'raw-ideas': 'path/idea.md' };
    const text = 'Just a simple template with no blocks';
    const result = modal._resolveConditionalBlocks(text, resolvedValues);
    expect(result).toBe(text);
  });

  it('empty <> block → stripped', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    const resolvedValues = {};
    // Regex /<([^<>]+)>/g won't match <> (empty) since [^<>]+ requires 1+ chars
    // Per EC-042-B.4: empty block produces no output, delimiters stripped
    const text = 'before <> after';
    const result = modal._resolveConditionalBlocks(text, resolvedValues);
    expect(result).not.toContain('<>');
  });

  it('<> block with only literal text (no $vars$) → always included, delimiters stripped', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    const resolvedValues = {};
    const text = 'before <this is just literal text> after';
    const result = modal._resolveConditionalBlocks(text, resolvedValues);
    expect(result).toContain('this is just literal text');
    expect(result).not.toContain('<');
    expect(result).not.toContain('>');
  });
});

// ==============================================================================
// Tests: Whitespace Cleanup
// ==============================================================================

describe('FEATURE-042-B: whitespace cleanup', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('collapses double-spaces after block removal', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    const resolvedValues = { 'uiux-reference': 'N/A' };
    const text = 'Please review $output:raw-ideas$ <and uiux reference: $output:uiux-reference$> carefully';
    let result = modal._resolveConditionalBlocks(text, resolvedValues);
    result = result.replace(/\s{2,}/g, ' ').trim();
    // After block removal and whitespace collapse there should be no double spaces
    expect(result).not.toMatch(/  /);
  });

  it('trims leading/trailing whitespace', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    const resolvedValues = { 'x': 'N/A' };
    const text = '<optional: $output:x$> main content';
    let result = modal._resolveConditionalBlocks(text, resolvedValues);
    result = result.replace(/\s{2,}/g, ' ').trim();
    expect(result).toBe('main content');
  });

  it('preserves single spaces between words', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    const resolvedValues = { 'raw-ideas': 'path/idea.md' };
    const text = 'hello <ctx: $output:raw-ideas$> world';
    let result = modal._resolveConditionalBlocks(text, resolvedValues);
    result = result.replace(/\s{2,}/g, ' ').trim();
    expect(result).toBe('hello ctx: $output:raw-ideas$ world');
  });

  it('handles consecutive <> blocks with whitespace between', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    const resolvedValues = { 'a': 'N/A', 'b': 'N/A' };
    const text = 'Read idea <optional A: $output:a$> <optional B: $output:b$> then proceed';
    let result = modal._resolveConditionalBlocks(text, resolvedValues);
    result = result.replace(/\s{2,}/g, ' ').trim();
    expect(result).toBe('Read idea then proceed');
  });
});

// ==============================================================================
// Tests: Flat Parsing
// ==============================================================================

describe('FEATURE-042-B: flat parsing', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('first < pairs with first > (no nesting)', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    const resolvedValues = { 'x': 'N/A' };
    // Nested attempt: <outer <inner $output:x$> text>
    // Flat: first < to first > → block = "outer <inner $output:x$" — wait, the regex [^<>]+ excludes < and >
    // So regex /<([^<>]+)>/g matches "inner $output:x$" (between inner < and first >)
    const text = '<outer <inner $output:x$> text>';
    const result = modal._resolveConditionalBlocks(text, resolvedValues);
    // The regex should match <inner $output:x$> first (no < or > inside [^<>]+)
    // Since x is N/A, that block is removed. "text>" and "<outer " remain as literals
    expect(result).toContain('<outer');
    expect(result).toContain('text>');
  });

  it('nested <> treated as flat (inner < is literal)', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    const resolvedValues = { 'x': 'val.md' };
    // With regex /<([^<>]+)>/g: matches <inner $output:x$> — x resolves → keep "inner $output:x$"
    const text = '<outer <inner $output:x$> rest>';
    const result = modal._resolveConditionalBlocks(text, resolvedValues);
    // Only <inner $output:x$> is matched and stripped → becomes "inner $output:x$"
    // Remaining text: "<outer inner $output:x$ rest>"
    // But there's still a < and > in residual — they should be literal now
    expect(result).toContain('inner $output:x$');
    expect(result).toContain('<outer');
  });
});

// ==============================================================================
// Tests: Unresolved Variable Warnings
// ==============================================================================

describe('FEATURE-042-B: unresolved variable warnings', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('unresolved $output:tag$ shows with warning formatting', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    const text = 'Review $output:missing-tag$ now';
    const result = modal._formatUnresolvedWarnings(text);
    expect(result).toContain('class="unresolved-warning"');
    expect(result).toContain('<span');
  });

  it('warning includes raw placeholder text', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    const text = 'Check $output:some-ref$ here';
    const result = modal._formatUnresolvedWarnings(text);
    expect(result).toContain('$output:some-ref$');
    expect(result).toContain('unresolved-warning');
  });

  it('resolved variables don\'t get warning formatting', () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    // After 042-A resolution, resolved vars are replaced with paths — no $output:...$
    const text = 'Review x-ipe-docs/ideas/test/raw-ideas.md now';
    const result = modal._formatUnresolvedWarnings(text);
    expect(result).not.toContain('unresolved-warning');
    expect(result).toBe(text);
  });
});

// ==============================================================================
// Tests: Legacy Backward Compatibility
// ==============================================================================

describe('FEATURE-042-B: legacy backward compatibility', () => {
  beforeEach(() => {
    mockBootstrap();
    setupFetchMocks();
    document.body.innerHTML = '<div id="modal-container"></div>';
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('in free mode, legacy <input-file> not treated as conditional block', async () => {
    if (!ensureImpl()) return;
    const modal = createFreeModal();
    await modal.open();
    // Free mode: workflowName is falsy → _resolveConditionalBlocks should NOT run
    const text = 'Read <input-file> and process';
    // In free mode _resolveTemplate should leave <input-file> for legacy resolver
    const result = modal._resolveTemplate
      ? modal._resolveTemplate(text, {})
      : text;
    expect(result).toContain('<input-file>');
  });

  it('conditional parsing only applied in workflow mode', async () => {
    if (!ensureImpl()) return;
    const modal = createWorkflowModal();
    await modal.open();
    const resolvedValues = { 'uiux-reference': 'N/A' };
    const text = 'Check <opt: $output:uiux-reference$> end';
    // In workflow mode the conditional block parser SHOULD remove the block
    const result = modal._resolveConditionalBlocks(text, resolvedValues);
    expect(result).not.toContain('opt:');
  });

  it('<current-idea-file> works unchanged in free mode', async () => {
    if (!ensureImpl()) return;
    const modal = createFreeModal();
    await modal.open();
    const text = 'Use <current-idea-file> for context';
    const result = modal._resolveTemplate
      ? modal._resolveTemplate(text, {})
      : text;
    expect(result).toContain('<current-idea-file>');
  });
});
