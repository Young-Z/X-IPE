/**
 * TASK-676: Bug fix — workflow panel ⋮ button not aligned to right side.
 * CSS: .workflow-panel-info needs flex:1, .workflow-panel-actions needs position:relative.
 * Also verifies action menu toggle and delete button wiring.
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

describe('workflow panel action menu behavior', () => {
  let panel;

  beforeEach(() => {
    panel = workflow._renderPanel({
      name: 'test-wf',
      current_stage: 'Ideation',
      feature_count: 0,
      created: '2026-01-01',
      last_activity: null,
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
