import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { loadFeatureScript } from './helpers.js';

beforeAll(() => {
  globalThis.CrAssessmentApi = class {};
  globalThis.LocalDirectoryPicker = class {};
  loadFeatureScript('cr-assessment.js');
});

function fixture() {
  document.body.innerHTML = `
    <div id="root">
      <form id="cr-case-form"><input id="cr-case-name" name="case_name"><input id="cr-case-id">
        <textarea id="cr-description" name="cr_description_text"></textarea><input id="cr-description-file" type="file">
        <input id="cr-codebase" name="codebase_path"><textarea id="cr-comments"></textarea>
        <input id="cr-vendor" type="file"><span id="cr-vendor-file"></span>
        <input id="cr-supporting" type="file"><span id="cr-supporting-list"></span></form>
      <div id="cr-case-list"></div><span id="cr-case-count"></span><input id="cr-search">
      <h2 id="cr-case-title"></h2><span id="cr-case-number"></span><div id="cr-alert" hidden></div>
      <div id="cr-readiness-list"></div><button id="cr-estimate"><span id="cr-depth-label"></span></button>
      <button id="cr-depth-toggle"></button>
      <div id="cr-depth-menu" hidden><button data-depth="quick"></button><button data-depth="standard"></button><button data-depth="deep"></button></div>
      <button id="cr-new-case"></button><button id="cr-mobile-list"></button><button id="cr-browse"></button>
      <button id="cr-open-report"></button><button id="cr-prev-slide"></button><button id="cr-next-slide"></button>
      <button id="cr-tab-information"></button><button id="cr-tab-report"></button>
      <section id="cr-information-panel"></section><section id="cr-report-panel" hidden></section>
      <div id="cr-report-empty"></div><div id="cr-report-content"></div><div id="cr-slide-stage"></div>
      <div id="cr-slide-dots"></div><span id="cr-slide-position"></span><div id="cr-report-links"></div><div id="cr-toast"></div>
    </div>`;
  const view = new CrAssessmentView(document.querySelector('#root'), {});
  view.picker = {};
  view._cache();
  return view;
}

describe('FEATURE-060-A CR assessment UI', () => {
  beforeEach(() => vi.restoreAllMocks());

  it('requires a persisted case and all three evidence inputs', () => {
    const view = fixture();
    view.el.description.value = 'Change login flow';
    view.el.codebase.value = '/project';
    view._renderReadiness(true);
    expect(view.el.estimate.disabled).toBe(true);

    view.selectedCase = { case: { id: 'CR-2026-001', status: 'Created' }, readiness: { cr_brief: true, codebase: true, vendor_estimate: true } };
    view._renderReadiness();
    expect(view.el.estimate.disabled).toBe(false);
    expect(view.el.readiness.querySelectorAll('[data-ready="true"]')).toHaveLength(3);
  });

  it('selecting an analysis depth updates the next estimation', async () => {
    const view = fixture();
    view.el.search = document.querySelector('#cr-search');
    view.prepare = vi.fn();
    view._bind = CrAssessmentView.prototype._bind.bind(view);
    // Bind only the depth interaction required by this test.
    for (const option of view.el.depthMenu.querySelectorAll('[data-depth]')) {
      option.addEventListener('click', () => view._chooseDepth(option.dataset.depth));
    }
    view.el.depthMenu.querySelector('[data-depth="deep"]').click();
    expect(view.depth).toBe('deep');
    expect(view.el.depthLabel.textContent).toBe('Deep');
    expect(view.prepare).not.toHaveBeenCalled();
  });

  it('clicking AI Estimation prepares the selected depth immediately', () => {
    const view = fixture();
    view.prepare = vi.fn();
    view._bind();

    view.el.estimate.click();

    expect(view.prepare).toHaveBeenCalledOnce();
  });

  it('expands the Console and types the prepared command without Enter', () => {
    const view = fixture();
    window.terminalPanel = { expand: vi.fn() };
    window.terminalManager = { sendCopilotPromptCommandNoEnter: vi.fn() };

    view._insertCommand('evaluate-cr-effort --depth standard');

    expect(window.terminalPanel.expand).toHaveBeenCalledOnce();
    expect(window.terminalManager.sendCopilotPromptCommandNoEnter).toHaveBeenCalledWith('evaluate-cr-effort --depth standard');
  });

  it('poller prevents overlapping requests', async () => {
    let release;
    const callback = vi.fn(() => new Promise((resolve) => { release = resolve; }));
    const poller = new CrAssessmentPoller(callback);
    const first = poller.pollNow();
    await poller.pollNow();
    expect(callback).toHaveBeenCalledOnce();
    release();
    await first;
  });

  it('does not rerender when polling reports no changes', async () => {
    const view = fixture();
    view.api = { pollChanges: vi.fn().mockResolvedValue({ changed: [], removed: [], markers: {} }) };
    view.renderList = vi.fn();
    await view._poll();
    expect(view.renderList).not.toHaveBeenCalled();
  });

  it('ignores a stale search response that resolves after the current query', async () => {
    const view = fixture();
    view.selectedCase = { case: { id: 'CR-2026-001' } };
    let resolveOld;
    let resolveCurrent;
    view.api = {
      listCases: vi.fn()
        .mockImplementationOnce(() => new Promise(resolve => { resolveOld = resolve; }))
        .mockImplementationOnce(() => new Promise(resolve => { resolveCurrent = resolve; }))
    };

    const oldRequest = view.loadCases('no-such-case');
    const currentRequest = view.loadCases('');
    resolveCurrent({ cases: [{ id: 'CR-2026-002', name: 'Current', marker: '2', updated_at: new Date().toISOString() }] });
    await currentRequest;
    resolveOld({ cases: [] });
    await oldRequest;

    expect(view.summaries.map(item => item.id)).toEqual(['CR-2026-002']);
  });

  it('renders persisted file names and relative case update time', () => {
    const view = fixture();
    view.el.search.value = '';
    view.summaries = [{ id: 'CR-2026-001', name: 'SSO', status: 'Created', updated_at: new Date().toISOString() }];
    view.renderList();
    expect(view.el.list.textContent).toContain('Updated just now');

    view.selectedCase = {
      case: { id: 'CR-2026-001', name: 'SSO', status: 'Created' }, record_revision: 1,
      inputs: { cr_description: { text: 'brief' }, codebase_path: '/repo', supporting_documents: [{ original_name: 'scope.pdf' }], vendor_estimate: { original_name: 'estimate.xlsx' } },
      readiness: { cr_brief: true, codebase: true, vendor_estimate: true }, reports: {}, invocation: {},
    };
    view.renderCase();
    expect(document.querySelector('#cr-supporting-list').textContent).toContain('scope.pdf');
    expect(document.querySelector('#cr-vendor-file').textContent).toContain('estimate.xlsx');
  });

  it('does not leave stale detail visible while selecting a case', async () => {
    const view = fixture();
    let resolveCase;
    view.api = { getCase: vi.fn(() => new Promise((resolve) => { resolveCase = resolve; })) };
    const pending = view.selectCase('CR-2026-002');
    expect(view.root.getAttribute('aria-busy')).toBe('true');
    expect(view.el.title.textContent).toContain('Loading');
    resolveCase({ case: { id: 'CR-2026-002', name: 'Loaded', status: 'Created' }, record_revision: 1, inputs: {}, readiness: {}, reports: {}, invocation: {} });
    await pending;
    expect(view.root.getAttribute('aria-busy')).toBe('false');
    expect(view.el.title.textContent).toBe('Loaded');
  });

  it('renders an accessible report module disclosure', () => {
    const view = fixture();
    view.selectedCase = { case: { id: 'CR-2026-001', name: 'SSO', status: 'Completed' }, reports: { latest: { effort: 'effort.html' }, history: [] } };
    view._renderReports();
    view.showSlide(1);
    expect(view.el.stage.querySelector('details summary')).not.toBeNull();
  });
});
