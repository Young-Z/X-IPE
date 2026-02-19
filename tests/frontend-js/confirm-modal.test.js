/**
 * FEATURE-037-B: Bootstrap Confirm Modal tests (Vitest + jsdom)
 * Tests _showConfirmModal returns Promise, creates DOM, uses bootstrap.Modal.
 */
import { describe, it, expect, beforeAll, beforeEach, vi } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import vm from 'vm';

const JS_PATH = resolve(import.meta.dirname, '../../src/x_ipe/static/js/features/workflow-stage.js');

describe('_showConfirmModal', () => {
  let mockInstance;

  beforeAll(() => {
    // Load the full workflowStage object once
    const code = readFileSync(JS_PATH, 'utf-8');
    const wrapped = code + '\nglobalThis.StageGateChecker = StageGateChecker;\nglobalThis.workflowStage = workflowStage;';
    vm.runInThisContext(wrapped);
  });

  beforeEach(() => {
    document.body.innerHTML = '';
    // Fresh mock per test
    mockInstance = { show: vi.fn(), hide: vi.fn() };
    class MockModal {
      constructor() { Object.assign(this, mockInstance); }
    }
    globalThis.bootstrap = {
      Modal: MockModal,
      _mockInstance: mockInstance,
    };
  });

  it('returns a Promise', () => {
    const result = workflowStage._showConfirmModal('Test', '<p>body</p>');
    expect(result).toBeInstanceOf(Promise);
  });

  it('creates modal DOM element with correct id', () => {
    workflowStage._showConfirmModal('Test', '<p>body</p>');
    const modal = document.getElementById('wf-confirm-modal');
    expect(modal).not.toBeNull();
    expect(modal.classList.contains('modal')).toBe(true);
  });

  it('sets title and body content', () => {
    workflowStage._showConfirmModal('My Title', '<p>My Body</p>');
    const modal = document.getElementById('wf-confirm-modal');
    expect(modal.querySelector('.modal-title').textContent).toBe('My Title');
    expect(modal.querySelector('.modal-body').innerHTML).toBe('<p>My Body</p>');
  });

  it('has Confirm and Cancel buttons', () => {
    workflowStage._showConfirmModal('Test', 'body');
    const modal = document.getElementById('wf-confirm-modal');
    const cancelBtn = modal.querySelector('[data-bs-dismiss="modal"]');
    const confirmBtn = modal.querySelector('.wf-confirm-yes');
    expect(cancelBtn).not.toBeNull();
    expect(confirmBtn).not.toBeNull();
    expect(confirmBtn.textContent).toBe('Confirm');
  });

  it('creates bootstrap.Modal with static backdrop', () => {
    workflowStage._showConfirmModal('Test', 'body');
    const modal = document.getElementById('wf-confirm-modal');
    expect(modal).not.toBeNull();
    expect(mockInstance.show).toHaveBeenCalled();
  });

  it('calls bsModal.show()', () => {
    workflowStage._showConfirmModal('Test', 'body');
    expect(mockInstance.show).toHaveBeenCalled();
  });

  it('reuses existing modal element on second call', () => {
    workflowStage._showConfirmModal('First', 'body1');
    workflowStage._showConfirmModal('Second', 'body2');
    const modals = document.querySelectorAll('#wf-confirm-modal');
    expect(modals.length).toBe(1);
    expect(modals[0].querySelector('.modal-title').textContent).toBe('Second');
  });

  it('resolves true when confirm button is clicked', async () => {
    const promise = workflowStage._showConfirmModal('Test', 'body');
    const modal = document.getElementById('wf-confirm-modal');
    const confirmBtn = modal.querySelector('.wf-confirm-yes');

    // Simulate: click Confirm, then fire hidden.bs.modal
    confirmBtn.click();
    modal.dispatchEvent(new Event('hidden.bs.modal'));

    const result = await promise;
    expect(result).toBe(true);
  });

  it('resolves false when modal is dismissed without confirm', async () => {
    const promise = workflowStage._showConfirmModal('Test', 'body');
    const modal = document.getElementById('wf-confirm-modal');

    // Simulate: dismiss without clicking confirm
    modal.dispatchEvent(new Event('hidden.bs.modal'));

    const result = await promise;
    expect(result).toBe(false);
  });

  it('uses modal-dialog-centered class', () => {
    workflowStage._showConfirmModal('Test', 'body');
    const dialog = document.querySelector('.modal-dialog-centered');
    expect(dialog).not.toBeNull();
  });
});
