/**
 * CR-001: Action Running State tests (FEATURE-036-C v1.1)
 * Tests for: _runningActions Set, _markRunning method, .running CSS class,
 * clickable buttons during execution, removal of pointer-events:none.
 */
import { describe, it, expect, beforeAll, beforeEach } from 'vitest';
import { loadFeatureScript } from './helpers.js';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const CSS_WORKFLOW = resolve(import.meta.dirname, '../../src/x_ipe/static/css/workflow.css');
const CSS_MODAL = resolve(import.meta.dirname, '../../src/x_ipe/static/css/features/action-execution-modal.css');

beforeAll(() => {
  loadFeatureScript('deliverable-viewer.js');
  loadFeatureScript('workflow-stage.js');
});

beforeEach(() => {
  document.body.innerHTML = '<div id="root"></div>';
  // Reset running actions between tests
  if (workflowStage._runningActions) {
    workflowStage._runningActions.clear();
  }
});

describe('CR-001: _runningActions Set', () => {
  it('workflowStage should have a _runningActions property that is a Set', () => {
    expect(workflowStage._runningActions).toBeInstanceOf(Set);
  });

  it('_runningActions should start empty', () => {
    expect(workflowStage._runningActions.size).toBe(0);
  });
});

describe('CR-001: _markRunning method', () => {
  it('should add actionKey to _runningActions Set', () => {
    const btn = document.createElement('button');
    btn.className = 'action-btn normal';
    workflowStage._markRunning('compose_idea', btn);
    expect(workflowStage._runningActions.has('compose_idea')).toBe(true);
  });

  it('should add .running class to button element', () => {
    const btn = document.createElement('button');
    btn.className = 'action-btn normal';
    workflowStage._markRunning('refine_idea', btn);
    expect(btn.classList.contains('running')).toBe(true);
  });

  it('should handle multiple running actions independently', () => {
    const btn1 = document.createElement('button');
    const btn2 = document.createElement('button');
    btn1.className = 'action-btn normal';
    btn2.className = 'action-btn normal';
    workflowStage._markRunning('compose_idea', btn1);
    workflowStage._markRunning('refine_idea', btn2);
    expect(workflowStage._runningActions.size).toBe(2);
    expect(btn1.classList.contains('running')).toBe(true);
    expect(btn2.classList.contains('running')).toBe(true);
  });
});

describe('CR-001: _renderActionButton applies .running from Set', () => {
  it('should add .running class when actionKey is in _runningActions', () => {
    workflowStage._runningActions.add('compose_idea');
    const btn = workflowStage._renderActionButton(
      'compose_idea',
      { icon: '📝', label: 'Compose Idea', interaction: 'modal', mandatory: true },
      'pending', false, false, 'test-wf', false
    );
    expect(btn.classList.contains('running')).toBe(true);
  });

  it('should NOT have .running class when actionKey is not in _runningActions', () => {
    const btn = workflowStage._renderActionButton(
      'compose_idea',
      { icon: '📝', label: 'Compose Idea', interaction: 'modal', mandatory: true },
      'pending', false, false, 'test-wf', false
    );
    expect(btn.classList.contains('running')).toBe(false);
  });
});

describe('TASK-786: Clear running state when action completes', () => {
  it('should NOT have .running class when action status is done even if key is in _runningActions', () => {
    workflowStage._runningActions.add('compose_idea');
    const btn = workflowStage._renderActionButton(
      'compose_idea',
      { icon: '📝', label: 'Compose Idea', interaction: 'modal', mandatory: true },
      'done', false, false, 'test-wf', false
    );
    expect(btn.classList.contains('running')).toBe(false);
  });

  it('should remove actionKey from _runningActions when rendered with done status', () => {
    workflowStage._runningActions.add('compose_idea');
    workflowStage._renderActionButton(
      'compose_idea',
      { icon: '📝', label: 'Compose Idea', interaction: 'modal', mandatory: true },
      'done', false, false, 'test-wf', false
    );
    expect(workflowStage._runningActions.has('compose_idea')).toBe(false);
  });

  it('should not affect other running actions when one completes', () => {
    workflowStage._runningActions.add('compose_idea');
    workflowStage._runningActions.add('refine_idea');
    workflowStage._renderActionButton(
      'compose_idea',
      { icon: '📝', label: 'Compose Idea', interaction: 'modal', mandatory: true },
      'done', false, false, 'test-wf', false
    );
    expect(workflowStage._runningActions.has('compose_idea')).toBe(false);
    expect(workflowStage._runningActions.has('refine_idea')).toBe(true);
  });
});

describe('CR-001: CSS .action-btn.running in workflow.css', () => {
  it('should have .action-btn.running rule', () => {
    const css = readFileSync(CSS_WORKFLOW, 'utf-8');
    expect(css).toMatch(/\.action-btn\.running\s*\{/);
  });

  it('should NOT have pointer-events: none in .action-btn.running', () => {
    const css = readFileSync(CSS_WORKFLOW, 'utf-8');
    const runningRule = css.match(/\.action-btn\.running\s*\{[^}]*\}/);
    if (runningRule) {
      expect(runningRule[0]).not.toMatch(/pointer-events\s*:\s*none/);
    }
  });

  it('should have .action-btn.running::after with animation', () => {
    const css = readFileSync(CSS_WORKFLOW, 'utf-8');
    expect(css).toMatch(/\.action-btn\.running::after\s*\{/);
  });

  it('should have @keyframes action-running-pulse', () => {
    const css = readFileSync(CSS_WORKFLOW, 'utf-8');
    expect(css).toMatch(/@keyframes\s+action-running-pulse/);
  });
});

describe('CR-001: Remove pointer-events:none from action-execution-modal.css', () => {
  it('.action-btn.in-progress should NOT have pointer-events: none', () => {
    const css = readFileSync(CSS_MODAL, 'utf-8');
    const inProgressRule = css.match(/\.action-btn\.in-progress\s*\{[^}]*\}/);
    if (inProgressRule) {
      expect(inProgressRule[0]).not.toMatch(/pointer-events\s*:\s*none/);
    }
  });
});

/* --------------------------------------------------------------------------
   TASK-876: _dispatchEditModalAction handles keyed dict deliverables
   -------------------------------------------------------------------------- */
import { vi, afterEach } from 'vitest';

describe('TASK-876: _dispatchEditModalAction with keyed dict deliverables', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="workflow-view"></div>';
  });

  afterEach(() => {
    delete globalThis.ComposeIdeaModal;
  });

  it('extracts filePath from raw-ideas string (keyed dict, single file)', () => {
    let captured = null;
    globalThis.ComposeIdeaModal = class {
      constructor(opts) { captured = opts; }
      open() {}
    };
    const wfData = {
      shared: {
        ideation: {
          actions: {
            compose_idea: {
              status: 'done',
              deliverables: {
                'raw-ideas': 'x-ipe-docs/ideas/test/new idea.md',
                'ideas-folder': 'x-ipe-docs/ideas/test'
              }
            }
          }
        }
      }
    };
    workflowStage._dispatchEditModalAction('test-wf', 'compose_idea', wfData);
    expect(captured).not.toBeNull();
    expect(captured.filePath).toBe('x-ipe-docs/ideas/test/new idea.md');
    expect(captured.folderPath).toBe('x-ipe-docs/ideas/test');
    expect(captured.folderName).toBe('test');
    expect(captured.mode).toBe('edit');
  });

  it('extracts filePath from raw-ideas array (keyed dict, multiple files)', () => {
    let captured = null;
    globalThis.ComposeIdeaModal = class {
      constructor(opts) { captured = opts; }
      open() {}
    };
    const wfData = {
      shared: {
        ideation: {
          actions: {
            compose_idea: {
              status: 'done',
              deliverables: {
                'raw-ideas': ['x-ipe-docs/ideas/test/new idea.md', 'x-ipe-docs/ideas/test/sketch.png'],
                'ideas-folder': 'x-ipe-docs/ideas/test'
              }
            }
          }
        }
      }
    };
    workflowStage._dispatchEditModalAction('test-wf', 'compose_idea', wfData);
    expect(captured).not.toBeNull();
    expect(captured.filePath).toBe('x-ipe-docs/ideas/test/new idea.md');
    expect(captured.folderPath).toBe('x-ipe-docs/ideas/test');
    expect(captured.mode).toBe('edit');
  });

  it('uses shared folder display naming for ideas-folder paths with trailing slash', () => {
    let captured = null;
    globalThis.ComposeIdeaModal = class {
      constructor(opts) { captured = opts; }
      open() {}
    };
    const wfData = {
      shared: {
        ideation: {
          actions: {
            compose_idea: {
              status: 'done',
              deliverables: {
                'raw-ideas': 'x-ipe-docs/ideas/wf-008-knowledge-extraction/new idea.md',
                'ideas-folder': 'x-ipe-docs/ideas/wf-008-knowledge-extraction/'
              }
            }
          }
        }
      }
    };
    workflowStage._dispatchEditModalAction('test-wf', 'compose_idea', wfData);
    expect(captured).not.toBeNull();
    expect(captured.folderPath).toBe('x-ipe-docs/ideas/wf-008-knowledge-extraction/');
    expect(captured.folderName).toBe('wf-008-knowledge-extraction/');
    expect(captured.mode).toBe('edit');
  });

  it('still works with legacy array deliverables', () => {
    let captured = null;
    globalThis.ComposeIdeaModal = class {
      constructor(opts) { captured = opts; }
      open() {}
    };
    const wfData = {
      shared: {
        ideation: {
          actions: {
            compose_idea: {
              status: 'done',
              deliverables: ['x-ipe-docs/ideas/test/new idea.md', 'x-ipe-docs/ideas/test']
            }
          }
        }
      }
    };
    workflowStage._dispatchEditModalAction('test-wf', 'compose_idea', wfData);
    expect(captured).not.toBeNull();
    expect(captured.filePath).toBe('x-ipe-docs/ideas/test/new idea.md');
    expect(captured.folderPath).toBe('x-ipe-docs/ideas/test');
    expect(captured.mode).toBe('edit');
  });
});
