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
        <input id="cr-vendor" type="file"><input id="cr-supporting" type="file"></form>
      <div id="cr-case-list"></div><span id="cr-case-count"></span><input id="cr-search">
      <h2 id="cr-case-title"></h2><span id="cr-case-number"></span><div id="cr-alert" hidden></div>
      <div id="cr-readiness-list"></div><button id="cr-estimate"><span id="cr-depth-label"></span></button>
      <div id="cr-depth-menu" hidden><button data-depth="quick"></button><button data-depth="standard"></button><button data-depth="deep"></button></div>
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

  it('selecting an analysis depth starts preparation', async () => {
    const view = fixture();
    view.el.search = document.querySelector('#cr-search');
    view.prepare = vi.fn();
    view._bind = CrAssessmentView.prototype._bind.bind(view);
    // Bind only the depth interaction required by this test.
    for (const option of view.el.depthMenu.querySelectorAll('[data-depth]')) {
      option.addEventListener('click', () => { view._chooseDepth(option.dataset.depth); view.prepare(); });
    }
    view.el.depthMenu.querySelector('[data-depth="deep"]').click();
    expect(view.depth).toBe('deep');
    expect(view.el.depthLabel.textContent).toBe('Deep');
    expect(view.prepare).toHaveBeenCalledOnce();
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
});
