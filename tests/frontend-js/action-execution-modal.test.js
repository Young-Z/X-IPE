/**
 * TDD Tests for FEATURE-038-A: Action Execution Modal (Frontend)
 * Tests: ActionExecutionModal class — open, close, instructions loading,
 *        extra instructions validation, command construction, execution dispatch
 *
 * TDD: All tests MUST fail until action-execution-modal.js is implemented.
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { loadFeatureScript } from './helpers.js';

/**
 * Guard: loads the feature script once. Returns true if class is available.
 */
let _implLoaded = false;
function ensureImpl() {
  if (!_implLoaded) {
    try {
      loadFeatureScript('action-execution-modal.js');
      _implLoaded = true;
    } catch {
      // File not yet implemented — TDD
    }
  }
  return typeof globalThis.ActionExecutionModal !== 'undefined';
}

describe('FEATURE-038-A: Action Execution Modal', () => {
  let mockTerminalManager;

  beforeEach(() => {
    document.body.innerHTML = '';

    mockTerminalManager = {
      findIdleSession: vi.fn().mockResolvedValue({ sessionId: 'sess-1', key: 'tab-1' }),
      claimSessionForAction: vi.fn().mockResolvedValue(true),
      switchSession: vi.fn(),
      sendCopilotPromptCommandNoEnter: vi.fn(),
      _buildCopilotCmd: vi.fn((prompt) => `copilot --allow-all-tools -i "${prompt}"`),
      addSession: vi.fn().mockReturnValue('new-tab'),
    };
    globalThis.window = globalThis.window || {};
    globalThis.window.terminalManager = mockTerminalManager;

    globalThis.window.__copilotPromptConfig = {
      ideation: {
        prompts: [{
          id: 'refine-idea',
          icon: 'bi-stars',
          'prompt-details': [
            { language: 'en', label: 'Refine Idea', command: 'refine the idea <current-idea-file>' }
          ]
        }]
      }
    };

    ensureImpl();
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  describe('Modal Opening', () => {
    it('should export ActionExecutionModal class', () => {
      expect(globalThis.ActionExecutionModal).toBeDefined();
    });

    it('should create modal overlay in DOM when opened', () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal.open();
      expect(document.querySelector('.modal-overlay')).not.toBeNull();
    });

    it('should display action title from ACTION_MAP label', () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal.open();
      expect(document.querySelector('.modal-title').textContent).toContain('Refine Idea');
    });

    it('should populate readonly instructions from copilot-prompt.json', () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal.open();
      const instructions = document.querySelector('.instructions-content');
      expect(instructions).not.toBeNull();
      expect(instructions.textContent).toContain('refine the idea');
    });

    it('should show fallback message when action ID not in config', () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'unknown_action', workflowName: 'hello' });
      modal.open();
      expect(document.querySelector('.copilot-btn').disabled).toBe(true);
    });
  });

  describe('Extra Instructions', () => {
    it('should have editable textarea with character counter', () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal.open();
      expect(document.querySelector('.extra-input')).not.toBeNull();
      expect(document.querySelector('.char-counter').textContent).toBe('0/500');
    });

    it('should update counter on input', () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal.open();
      const textarea = document.querySelector('.extra-input');
      textarea.value = 'Focus on UX';
      textarea.dispatchEvent(new Event('input'));
      expect(document.querySelector('.char-counter').textContent).toBe('11/500');
    });

    it('should enforce 500 character limit', () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal.open();
      const textarea = document.querySelector('.extra-input');
      textarea.value = 'x'.repeat(600);
      textarea.dispatchEvent(new Event('input'));
      expect(textarea.value.length).toBe(500);
    });
  });

  describe('Command Construction', () => {
    it('should build CLI command from adapter config', () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      const cmd = modal._buildCommand('');
      expect(cmd).toContain('refine the idea');
    });

    it('should append extra instructions to command when provided', () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      const cmd = modal._buildCommand('Focus on UX flow');
      expect(cmd).toContain('Focus on UX flow');
    });

    it('should work without extra instructions', () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      const cmd = modal._buildCommand('');
      expect(cmd).toContain('refine the idea');
    });
  });

  describe('Execution Dispatch', () => {
    it('should find idle session and dispatch command', async () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal.open();
      await modal._handleExecute();
      expect(mockTerminalManager.findIdleSession).toHaveBeenCalled();
      expect(mockTerminalManager.claimSessionForAction).toHaveBeenCalledWith('sess-1', 'hello', 'refine_idea');
      expect(mockTerminalManager.sendCopilotPromptCommandNoEnter).toHaveBeenCalled();
    });

    it('should create new session when no idle session found', async () => {
      mockTerminalManager.findIdleSession.mockResolvedValue(null);
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal.open();
      await modal._handleExecute();
      expect(mockTerminalManager.addSession).toHaveBeenCalled();
    });

    it('should close modal after dispatching command', async () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal.open();
      await modal._handleExecute();
      expect(document.querySelector('.modal-overlay')).toBeNull();
    });
  });

  describe('Modal Lifecycle', () => {
    it('should close on X button click', () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal.open();
      document.querySelector('.modal-close-btn').click();
      expect(document.querySelector('.modal-overlay')).toBeNull();
    });

    it('should close on Escape key', () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal.open();
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
      expect(document.querySelector('.modal-overlay')).toBeNull();
    });

    it('should close on overlay backdrop click', () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal.open();
      document.querySelector('.modal-overlay').click();
      expect(document.querySelector('.modal-overlay')).toBeNull();
    });

    it('should clean up event listeners on close', () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal.open();
      modal.close();
      // Verify no error on repeated close
      expect(() => modal.close()).not.toThrow();
    });

    it('should show in-progress message when reopened during execution', () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello', status: 'in_progress' });
      modal.open();
      expect(document.querySelector('.copilot-btn')).toBeNull();
      expect(document.querySelector('.in-progress-message')).not.toBeNull();
    });
  });

  describe('Spinner/Pulse on Action Button', () => {
    it('should add in-progress class to action button after execution', async () => {
      const Modal = globalThis.ActionExecutionModal;
      expect(Modal).toBeDefined();
      // Create a mock button element
      const btn = document.createElement('button');
      btn.classList.add('action-btn');
      document.body.appendChild(btn);
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello', triggerBtn: btn });
      modal.open();
      await modal._handleExecute();
      expect(btn.classList.contains('in-progress')).toBe(true);
    });
  });
});
