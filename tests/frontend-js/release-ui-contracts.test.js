/**
 * TASK-6749: production UI behavior, not source-string emulation.
 * Sources: FEATURE-037-A AC-004/005/013/023; FEATURE-037-B AC-010..018/027;
 * FEATURE-036-D AC-1/2/3.3/4; FEATURE-036-B AC-003..005;
 * FEATURE-058-E AC-058E-01b; FEATURE-004 FR-2/4/5/6.
 * Lane click is the current focus implementation. The literal dropdown in
 * FEATURE-036-D AC-3.1/3.2 is an unresolved source discrepancy, not retired here.
 * jsdom provides runtime evidence only, not browser/visual acceptance.
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const ROOT = resolve(import.meta.dirname, '../..');
const read = path => readFileSync(resolve(ROOT, path), 'utf8');
const { workflowStage, StageGateChecker } = new Function(
  read('src/x_ipe/static/js/features/workflow-stage.js') + '\nreturn {workflowStage, StageGateChecker};'
)();
const { ComposeIdeaModal, IdeaNameValidator } = new Function(
  read('src/x_ipe/static/js/features/compose-idea-modal.js') + '\nreturn {ComposeIdeaModal, IdeaNameValidator};'
)();
const { ContentRefreshManager } = new Function(
  read('src/x_ipe/static/js/features/live-refresh.js') + '\nreturn {ContentRefreshManager};'
)();

beforeEach(() => {
  vi.useFakeTimers();
  document.body.innerHTML = '<div id="content-body"></div><div id="toast-container"></div>';
  localStorage.clear();
  workflowStage._runningActions.clear();
  vi.stubGlobal('fetch', vi.fn());
  vi.stubGlobal('requestAnimationFrame', callback => callback());
});

afterEach(() => {
  vi.clearAllTimers();
  vi.useRealTimers();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

function stages(nextStatus = 'pending') {
  return {
    ideation: { status: 'completed', actions: { compose_idea: { status: 'done' } } },
    requirement: { status: 'locked', actions: { requirement_gathering: { status: nextStatus } } },
  };
}

function response(data, status = 200) {
  return { ok: status < 400, status, json: async () => ({ success: status < 400, data }) };
}

describe('completed compose action: gate → confirm → rollback → edit', () => {
  let confirm, dispatch, toast;
  const action = { label: 'Compose Idea', interaction: 'modal' };

  beforeEach(() => {
    confirm = vi.spyOn(workflowStage, '_showConfirmModal').mockResolvedValue(true);
    dispatch = vi.spyOn(workflowStage, '_dispatchEditModalAction').mockImplementation(() => {});
    toast = vi.spyOn(workflowStage, '_showToast').mockImplementation(() => {});
  });

  it.each(['in_progress', 'done'])('blocks downstream %s without confirmation or mutation', async status => {
    fetch.mockResolvedValue(response({ shared: stages(status) }));
    await workflowStage._handleCompletedAction('release test', 'compose_idea', action);
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledWith('/api/workflow/release%20test');
    expect(confirm).not.toHaveBeenCalled();
    expect(dispatch).not.toHaveBeenCalled();
    expect(toast).toHaveBeenCalledWith(expect.stringContaining('requirement_gathering'), 'error');
  });

  it('cancel leaves action done and never opens an editor', async () => {
    fetch.mockResolvedValue(response({ shared: stages() }));
    confirm.mockResolvedValue(false);
    await workflowStage._handleCompletedAction('release', 'compose_idea', action);
    expect(confirm).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(dispatch).not.toHaveBeenCalled();
  });

  it('confirmed reopen awaits rollback before dispatch', async () => {
    const state = { shared: stages() };
    let resolveRollback;
    fetch.mockResolvedValueOnce(response(state)).mockImplementationOnce(() =>
      new Promise(resolve => { resolveRollback = resolve; }));
    const pending = workflowStage._handleCompletedAction('release', 'compose_idea', action);
    await vi.waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
    expect(dispatch).not.toHaveBeenCalled();
    const [url, options] = fetch.mock.calls[1];
    expect(url).toBe('/api/workflow/release/action');
    expect(options.method).toBe('POST');
    expect(JSON.parse(options.body)).toEqual({ action: 'compose_idea', status: 'pending' });
    resolveRollback(response({}));
    await pending;
    expect(dispatch).toHaveBeenCalledWith('release', 'compose_idea', state);
  });

  it('network rejection does not open an editor or mutate the action', async () => {
    fetch.mockRejectedValue(new Error('offline'));
    await workflowStage._handleCompletedAction('release', 'compose_idea', action);
    expect(confirm).not.toHaveBeenCalled();
    expect(dispatch).not.toHaveBeenCalled();
    expect(toast).toHaveBeenCalledWith(expect.stringContaining('Failed'), 'error');
  });

  it('failed HTTP rollback must not open edit mode (AC-015 prerequisite)', async () => {
    fetch.mockResolvedValueOnce(response({ shared: stages() })).mockResolvedValueOnce(response({}, 500));
    await workflowStage._handleCompletedAction('release', 'compose_idea', action);
    expect(dispatch).not.toHaveBeenCalled();
    expect(toast).toHaveBeenCalledWith(expect.any(String), 'error');
  });

  it('uses actual next-stage ordering rather than blocking on same-stage actions', () => {
    const state = stages();
    state.ideation.actions.refine_idea = { status: 'done' };
    expect(StageGateChecker.canReopen('compose_idea', state)).toEqual({ allowed: true });
    state.requirement.actions.feature_breakdown = { status: 'done' };
    expect(StageGateChecker.canReopen('compose_idea', state)).toEqual({
      allowed: false, blocker: 'feature_breakdown', stage: 'requirement',
    });
  });
});

describe('edit dispatch: keyed, legacy and missing deliverables', () => {
  let options, open;
  beforeEach(() => {
    open = vi.fn();
    vi.stubGlobal('ComposeIdeaModal', class {
      constructor(value) { options = value; }
      open() { open(); }
    });
  });

  it.each([
    { 'raw-ideas': 'x-ipe-docs/ideas/release/new idea.md', 'ideas-folder': 'x-ipe-docs/ideas/release' },
    ['x-ipe-docs/ideas/release/new idea.md', 'x-ipe-docs/ideas/release'],
  ])('opens the original file and folder in edit mode: %j', deliverables => {
    const state = { shared: { ideation: { actions: { compose_idea: { deliverables } } } } };
    workflowStage._dispatchEditModalAction('release', 'compose_idea', state);
    expect(open).toHaveBeenCalledOnce();
    expect(options).toMatchObject({ mode: 'edit', filePath: 'x-ipe-docs/ideas/release/new idea.md',
      folderPath: 'x-ipe-docs/ideas/release', folderName: 'release' });
  });

  it('missing deliverables falls back to create mode (FEATURE-037-B AC-027)', () => {
    workflowStage._dispatchEditModalAction('release', 'compose_idea', {
      shared: { ideation: { actions: { compose_idea: { status: 'done', deliverables: {} } } } },
    });
    expect(open).toHaveBeenCalledOnce();
    expect(options.mode).not.toBe('edit');
    expect(options.filePath || '').toBe('');
  });
});

describe('compose validation and close lifecycle', () => {
  let modal;
  beforeEach(() => {
    modal = new ComposeIdeaModal({ workflowName: 'release' });
    modal.createDOM();
    modal.bindEvents();
    document.body.appendChild(modal.overlay);
    modal.overlay.classList.add('active');
    modal.easyMDE = { value: () => 'Idea content', toTextArea: vi.fn() };
  });

  it.each(['', 'one two three four five six seven eight nine ten eleven'])('invalid name blocks submit: %j', name => {
    modal.nameInput.value = name;
    modal.nameInput.dispatchEvent(new Event('input', { bubbles: true }));
    expect(modal.submitBtn.disabled).toBe(true);
  });

  it('valid name alone cannot submit empty content; content makes it eligible', () => {
    modal.easyMDE.value = () => '';
    modal.nameInput.value = 'Valid Idea';
    modal.nameInput.dispatchEvent(new Event('input', { bubbles: true }));
    expect(modal.submitBtn.disabled).toBe(true);
    modal.easyMDE.value = () => '# Real idea';
    modal.updateSubmitState();
    expect(modal.submitBtn.disabled).toBe(false);
  });

  it('backdrop click does not discard content', () => {
    modal.overlay.click();
    expect(modal.overlay.classList.contains('active')).toBe(true);
    expect(modal.easyMDE.toTextArea).not.toHaveBeenCalled();
  });

  it.each(['escape', 'cancel', 'close'])('%s cleans up the editor and removes modal DOM', async trigger => {
    const cleanup = modal.easyMDE.toTextArea;
    if (trigger === 'escape') modal.overlay.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    if (trigger === 'cancel') modal.overlay.querySelector('.compose-modal-btn-cancel').click();
    if (trigger === 'close') modal.overlay.querySelector('.compose-modal-close').click();
    expect(cleanup).toHaveBeenCalledOnce();
    expect(modal.easyMDE).toBeNull();
    await vi.advanceTimersByTimeAsync(300);
    expect(document.querySelector('.compose-modal-overlay')).toBeNull();
  });

  it('enforces the ten-word boundary in production validator', () => {
    const validator = new IdeaNameValidator(modal.nameInput, document.createElement('span'), document.createElement('span'));
    expect(validator.validate('one two three four five six seven eight nine ten').valid).toBe(true);
    expect(validator.validate('one two three four five six seven eight nine ten eleven').valid).toBe(false);
    expect(validator.sanitize('My Idea!')).toBe('my-idea');
  });
});

function featureStages() {
  return { implement: { features: {
    'FEATURE-A': { name: 'Base', depends_on: [], actions: { feature_refinement: { status: 'done' } } },
    'FEATURE-B': { name: 'Dependent', depends_on: ['FEATURE-A'], actions: {} },
  } } };
}

describe('feature lanes: focus, dependencies and dispatch controls', () => {
  it('renders each feature once and changes focus on lane click', () => {
    const lanes = workflowStage._renderFeatureLanes(featureStages(), null, 'release');
    document.body.appendChild(lanes);
    expect(lanes.querySelectorAll('.feature-lane')).toHaveLength(2);
    expect(lanes.querySelector('.highlighted').dataset.feature).toBe('FEATURE-A');
    lanes.querySelector('[data-feature="FEATURE-B"]').click();
    expect(lanes.querySelectorAll('.highlighted')).toHaveLength(1);
    expect(lanes.querySelector('.highlighted').dataset.feature).toBe('FEATURE-B');
    expect(lanes.querySelector('[data-feature="FEATURE-A"] .dep-tag').textContent).toContain('Parallel');
    expect(lanes.querySelector('[data-feature="FEATURE-B"] .dep-tag').textContent).toContain('FEATURE-A');
  });

  it('dependencies toggle hides and restores both arrows and badges via container state', () => {
    const root = document.createElement('div');
    const state = featureStages();
    root.appendChild(workflowStage._renderToolbar(state, null, 'release', {}));
    root.appendChild(workflowStage._renderFeatureLanes(state, null, 'release'));
    const toggle = root.querySelector('.dep-toggle');
    toggle.click();
    expect(root.querySelector('.lanes-container').classList.contains('deps-hidden')).toBe(true);
    expect(toggle.classList.contains('active')).toBe(false);
    toggle.click();
    expect(root.querySelector('.lanes-container').classList.contains('deps-hidden')).toBe(false);
    expect(toggle.classList.contains('active')).toBe(true);
  });

  it('no features produces shared action UI, not phantom lanes', () => {
    vi.spyOn(workflowStage, '_renderDeliverables').mockImplementation(() => {});
    const root = document.createElement('div');
    workflowStage.render(root, { shared: stages() }, null, 'release');
    expect(root.querySelector('.stage-ribbon')).not.toBeNull();
    expect(root.querySelector('.actions-area')).not.toBeNull();
    expect(root.querySelector('.feature-lane')).toBeNull();
  });

  it('completed lane action does not dispatch and action click does not change lane focus', () => {
    const dispatch = vi.spyOn(workflowStage, '_dispatchFeatureAction').mockImplementation(() => {});
    vi.spyOn(workflowStage, '_showToast').mockImplementation(() => {});
    const lanes = workflowStage._renderFeatureLanes(featureStages(), null, 'release');
    const second = lanes.querySelector('[data-feature="FEATURE-B"]');
    second.click();
    lanes.querySelector('[data-feature="FEATURE-A"] .lane-stage.done').click();
    expect(dispatch).not.toHaveBeenCalled();
    expect(lanes.querySelector('.highlighted')).toBe(second);
  });

  it.each([false, true])('dependent action dispatch requires user override=%s', async proceed => {
    const dispatch = vi.spyOn(workflowStage, '_dispatchCliAction').mockImplementation(() => {});
    const confirm = vi.spyOn(workflowStage, '_showDependencyConfirm').mockResolvedValue(proceed);
    fetch.mockResolvedValue(response({ blocked: true, blockers: [{ feature_id: 'FEATURE-A', current_stage: 'implement' }] }));
    await workflowStage._dispatchFeatureAction('release', 'FEATURE-B', 'technical_design', { depends_on: ['FEATURE-A'] });
    expect(fetch).toHaveBeenCalledWith('/api/workflow/release/dependencies/FEATURE-B');
    expect(confirm).toHaveBeenCalledWith('FEATURE-B', 'FEATURE-A (implement)');
    expect(dispatch).toHaveBeenCalledTimes(proceed ? 1 : 0);
    if (proceed) expect(dispatch.mock.calls[0].at(-1)).toBe('FEATURE-B');
  });

  it('independent action bypasses advisory dependency check but preserves feature identity', async () => {
    const dispatch = vi.spyOn(workflowStage, '_dispatchCliAction').mockImplementation(() => {});
    await workflowStage._dispatchFeatureAction('release', 'FEATURE-A', 'technical_design', { depends_on: [] });
    expect(fetch).not.toHaveBeenCalled();
    expect(dispatch.mock.calls[0].at(-1)).toBe('FEATURE-A');
  });
});

describe('actual init navigation click wiring', () => {
  let workflow, graph;
  beforeEach(() => {
    document.body.innerHTML = read('src/x_ipe/templates/index.html');
    vi.stubGlobal('ContentRenderer', class { constructor(id) { this.container = document.getElementById(id); } });
    for (const name of ['ContentEditor', 'ContentRefreshManager', 'PlanningFilePoller', 'WorkplaceManager', 'LearnPanelManager', 'ProjectSwitcher']) {
      vi.stubGlobal(name, class {});
    }
    vi.stubGlobal('ProjectSidebar', class { load() {} });
    vi.stubGlobal('bootstrap', { Modal: class { show() {} } });
    graph = { render: vi.fn(), destroy: vi.fn() };
    vi.stubGlobal('OntologyGraphViewer', class { constructor() { return graph; } });
    workflow = { render: vi.fn(container => { container.className = 'content-body workflow-view'; }), _stopAllPolling: vi.fn() };
    vi.stubGlobal('workflow', workflow);
    const initialize = new Function(read('src/x_ipe/static/js/init.js') + '\nreturn initializeApp;')();
    document.removeEventListener('DOMContentLoaded', initialize);
    initialize();
  });

  it('Workflow click renders once, hides free-mode layout and activates only its button', () => {
    document.getElementById('btn-mode-workflow').click();
    expect(workflow.render).toHaveBeenCalledWith(document.getElementById('content-body'));
    expect(document.getElementById('sidebar').style.display).toBe('none');
    expect(document.querySelector('.content-header').style.display).toBe('none');
    expect([...document.querySelectorAll('.mode-btn.active')].map(b => b.id)).toEqual(['btn-mode-workflow']);
    document.getElementById('btn-mode-workflow').click();
    expect(workflow.render).toHaveBeenCalledOnce();
  });

  it('Free click stops workflow polling and restores content-body, sidebar and breadcrumb header', () => {
    document.getElementById('btn-mode-workflow').click();
    document.getElementById('btn-mode-free').click();
    expect(workflow._stopAllPolling).toHaveBeenCalledOnce();
    expect(document.getElementById('content-body').className).toBe('content-body');
    expect(document.getElementById('sidebar').style.display).toBe('');
    expect(document.querySelector('.sidebar-resize-handle').style.display).toBe('');
    expect(document.querySelector('.content-header').style.display).toBe('');
    expect([...document.querySelectorAll('.mode-btn.active')].map(b => b.id)).toEqual(['btn-mode-free']);
  });

  it('KG → Workflow destroys graph state and restores scroll/padding styles', () => {
    document.getElementById('btn-mode-kg').click();
    expect(graph.render).toHaveBeenCalledWith(document.getElementById('content-body'));
    document.getElementById('btn-mode-workflow').click();
    expect(graph.destroy).toHaveBeenCalledOnce();
    expect(document.getElementById('content-body').style.overflow).toBe('');
    expect(document.getElementById('content-body').style.padding).toBe('');
    expect(workflow.render).toHaveBeenCalledOnce();
  });
});

describe('live refresh: polling payloads and negative controls', () => {
  let manager, renderer;
  beforeEach(() => {
    renderer = { currentPath: 'notes.md', container: document.getElementById('content-body'), render: vi.fn() };
    manager = new ContentRefreshManager({ contentRenderer: renderer });
    manager.lastPath = renderer.currentPath;
    manager.lastContent = '# Original';
  });

  it('changed content re-renders exactly the fetched payload; unchanged content does not', async () => {
    fetch.mockResolvedValue({ ok: true, json: async () => ({ content: '# Original' }) });
    await manager._checkForChanges();
    expect(renderer.render).not.toHaveBeenCalled();
    const data = { content: '# Updated', type: 'markdown', path: 'notes.md' };
    fetch.mockResolvedValue({ ok: true, json: async () => data });
    await manager._checkForChanges();
    expect(renderer.render).toHaveBeenCalledExactlyOnceWith(data);
    expect(manager.lastContent).toBe('# Updated');
  });

  it('disabled manager never fetches, but enabling restores polling', async () => {
    manager.setEnabled(false);
    await manager._checkForChanges();
    expect(fetch).not.toHaveBeenCalled();
    expect(localStorage.getItem('autoRefreshEnabled')).toBe('false');
    manager.setEnabled(true);
    fetch.mockResolvedValue({ ok: true, json: async () => ({ content: '# Original' }) });
    await manager._checkForChanges();
    expect(fetch).toHaveBeenCalledOnce();
  });

  it('404 shows deleted-file navigation; 500 must not claim the file was deleted', async () => {
    fetch.mockResolvedValue({ ok: false, status: 500 });
    await manager._checkForChanges();
    expect(renderer.container.textContent).not.toContain('File Not Found');
    expect(manager.lastContent).toBe('# Original');
    fetch.mockResolvedValue({ ok: false, status: 404 });
    await manager._checkForChanges();
    expect(renderer.container.textContent).toContain('File Not Found');
    expect(renderer.container.textContent).toContain('Browse Files');
    expect(manager.lastContent).toBeNull();
    expect(manager.lastPath).toBeNull();
  });
});