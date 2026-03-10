/**
 * TASK-676: Bug fix — workflow panel ⋮ button not aligned to right side.
 * CSS: .workflow-panel-info needs flex:1, .workflow-panel-actions needs position:relative.
 * Also verifies action menu toggle and delete button wiring.
 * TASK-785: Auto-proceed dropdown moved from feature toolbar to panel header.
 */
import { describe, it, expect, beforeAll, beforeEach, vi, afterEach } from 'vitest';
import { loadFeatureScript, mockFetch } from './helpers.js';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const CSS_PATH = resolve(import.meta.dirname, '../../src/x_ipe/static/css/workflow.css');

beforeAll(() => {
  loadFeatureScript('workflow.js');
});

beforeEach(() => {
  document.body.innerHTML = '<div id="workflow-panels"></div>';
});

describe('workflow panel ⋮ button alignment (CSS)', () => {
  it('.workflow-panel-info should have flex:1 to push actions right', () => {
    const css = readFileSync(CSS_PATH, 'utf-8');
    const infoRule = css.match(/\.workflow-panel-info\s*\{[^}]*\}/);
    expect(infoRule).not.toBeNull();
    expect(infoRule[0]).toMatch(/flex\s*:\s*1/);
  });

  it('.workflow-panel-actions should have position:relative for dropdown', () => {
    const css = readFileSync(CSS_PATH, 'utf-8');
    const actionsRule = css.match(/\.workflow-panel-actions\s*\{[^}]*\}/);
    expect(actionsRule).not.toBeNull();
    expect(actionsRule[0]).toMatch(/position\s*:\s*relative/);
  });
});

describe('TASK-677: workflow panel dropdown menu positioning', () => {
  it('.workflow-panel-actions should have position:relative so dropdown escapes panel overflow', () => {
    const css = readFileSync(CSS_PATH, 'utf-8');
    const actionsRule = css.match(/\.workflow-panel-actions\s*\{[^}]*\}/);
    expect(actionsRule).not.toBeNull();
    expect(actionsRule[0]).toMatch(/position\s*:\s*relative/);
  });
});

describe('workflow panel action menu behavior', () => {
  let panel;

  beforeEach(() => {
    panel = workflow._renderPanel({
      name: 'test-wf',
      current_stage: 'Ideation',
      feature_count: 0,
      created: '2026-01-01',
      last_activity: null,
      auto_proceed: 'manual',  // legacy field — dropdown reads interaction_mode || auto_proceed
    });
    document.getElementById('workflow-panels').appendChild(panel);
  });

  it('renders ⋮ button inside .workflow-panel-actions', () => {
    const btn = panel.querySelector('.workflow-action-btn');
    expect(btn).not.toBeNull();
    expect(btn.textContent.trim()).toBe('⋮');
    expect(btn.closest('.workflow-panel-actions')).not.toBeNull();
  });

  it('renders delete button inside action menu', () => {
    const menu = panel.querySelector('.workflow-action-menu');
    expect(menu).not.toBeNull();
    const delBtn = menu.querySelector('button');
    expect(delBtn).not.toBeNull();
    expect(delBtn.textContent).toContain('Delete');
  });

  it('clicking ⋮ toggles menu open class', () => {
    const btn = panel.querySelector('.workflow-action-btn');
    const menu = panel.querySelector('.workflow-action-menu');
    expect(menu.classList.contains('open')).toBe(false);
    btn.click();
    expect(menu.classList.contains('open')).toBe(true);
  });

  it('delete button calls _handleDelete with workflow name', async () => {
    const spy = vi.spyOn(workflow, '_handleDelete').mockResolvedValue();
    const menu = panel.querySelector('.workflow-action-menu');
    const delBtn = menu.querySelector('button');
    delBtn.click();
    expect(spy).toHaveBeenCalledWith('test-wf');
    spy.mockRestore();
  });
});

describe('delete confirm modal structure', () => {
  afterEach(() => {
    document.body.innerHTML = '<div id="workflow-panels"></div>';
  });

  it('has workflow-modal-header with title and close button', async () => {
    const promise = workflow._showConfirmModal('Delete?', 'Cannot undo.');
    const modal = document.querySelector('.workflow-modal');
    expect(modal).not.toBeNull();
    const header = modal.querySelector('.workflow-modal-header');
    expect(header).not.toBeNull();
    expect(header.querySelector('.workflow-modal-title').textContent).toBe('Delete?');
    expect(header.querySelector('.workflow-modal-close')).not.toBeNull();
    document.getElementById('wf-confirm-cancel').click();
    await promise;
  });

  it('has workflow-modal-body with message', async () => {
    const promise = workflow._showConfirmModal('Delete?', 'Cannot undo.');
    const body = document.querySelector('.workflow-modal .workflow-modal-body');
    expect(body).not.toBeNull();
    expect(body.textContent).toContain('Cannot undo.');
    document.getElementById('wf-confirm-cancel').click();
    await promise;
  });

  it('close button dismisses the modal (resolves false)', async () => {
    const promise = workflow._showConfirmModal('Delete?', 'Nope');
    document.getElementById('wf-confirm-close').click();
    const result = await promise;
    expect(result).toBe(false);
    expect(document.querySelector('.workflow-modal-overlay')).toBeNull();
  });
});

describe('TASK-785: interaction mode dropdown in panel header', () => {
  let panel;

  beforeEach(() => {
    panel = workflow._renderPanel({
      name: 'test-wf',
      current_stage: 'Ideation',
      feature_count: 2,
      created: '2026-01-01',
      last_activity: null,
      interaction_mode: 'interact-with-human',
    });
    document.getElementById('workflow-panels').appendChild(panel);
  });

  it('renders interaction mode dropdown inside panel header actions', () => {
    const apDropdown = panel.querySelector('.auto-proceed-header');
    expect(apDropdown).not.toBeNull();
    expect(apDropdown.closest('.workflow-panel-actions')).not.toBeNull();
  });

  it('renders three mode options with new enum values', () => {
    const items = panel.querySelectorAll('.auto-proceed-header .dropdown-item');
    expect(items.length).toBe(3);
    expect(items[0].dataset.mode).toBe('interact-with-human');
    expect(items[1].dataset.mode).toBe('dao-represent-human-to-interact');
    expect(items[2].dataset.mode).toBe('dao-represent-human-to-interact-for-questions-in-skill');
  });

  it('marks current mode as active', () => {
    const active = panel.querySelector('.auto-proceed-header .dropdown-item.active');
    expect(active).not.toBeNull();
    expect(active.dataset.mode).toBe('interact-with-human');
  });

  it('shows correct badge for dao-represent-human-to-interact mode', () => {
    const daoPanel = workflow._renderPanel({
      name: 'dao-wf', current_stage: 'Implement', feature_count: 1,
      created: '2026-01-01', last_activity: null, interaction_mode: 'dao-represent-human-to-interact',
    });
    const badge = daoPanel.querySelector('.auto-proceed-btn .badge');
    expect(badge.textContent).toContain('DAO Represents Human');
    expect(badge.classList.contains('text-bg-success')).toBe(true);
  });

  it('defaults to interact-with-human when interaction_mode is missing', () => {
    const noModePanel = workflow._renderPanel({
      name: 'no-mode', current_stage: 'Ideation', feature_count: 0,
      created: '2026-01-01', last_activity: null,
    });
    const badge = noModePanel.querySelector('.auto-proceed-btn .badge');
    expect(badge.textContent).toContain('Human Direct');
  });

  it('migrates legacy auto_proceed value to new mode', () => {
    const legacyPanel = workflow._renderPanel({
      name: 'legacy-wf', current_stage: 'Ideation', feature_count: 0,
      created: '2026-01-01', last_activity: null, auto_proceed: 'auto',
    });
    const badge = legacyPanel.querySelector('.auto-proceed-btn .badge');
    expect(badge.textContent).toContain('DAO Represents Human');
  });

  it('dropdown click does not propagate to panel header (no toggle)', () => {
    const apDropdown = panel.querySelector('.auto-proceed-header');
    const expandedBefore = panel.classList.contains('expanded');
    const evt = new MouseEvent('click', { bubbles: true });
    apDropdown.dispatchEvent(evt);
    expect(panel.classList.contains('expanded')).toBe(expandedBefore);
  });

  it('CSS: .workflow-panel-actions has display:flex and gap', () => {
    const css = readFileSync(CSS_PATH, 'utf-8');
    const actionsRule = css.match(/\.workflow-panel-actions\s*\{[^}]*\}/);
    expect(actionsRule).not.toBeNull();
    expect(actionsRule[0]).toMatch(/display\s*:\s*flex/);
    expect(actionsRule[0]).toMatch(/gap/);
  });

  it('mode selection calls PATCH settings API with interaction_mode key', async () => {
    const restore = mockFetch();
    const daoItem = panel.querySelector('.auto-proceed-header .dropdown-item[data-mode="dao-represent-human-to-interact"]');
    await daoItem.click();
    const patchCall = globalThis.fetch.mock.calls.find(c => c[0].includes('/settings') && c[1]?.method === 'PATCH');
    expect(patchCall).toBeDefined();
    expect(patchCall[0]).toContain('/api/workflow/test-wf/settings');
    const body = JSON.parse(patchCall[1].body);
    expect(body.process_preference.interaction_mode).toBe('dao-represent-human-to-interact');
    restore();
  });
});
