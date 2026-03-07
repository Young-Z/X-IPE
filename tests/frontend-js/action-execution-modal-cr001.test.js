/**
 * Tests for CR-001: Append --execute@mode flag to CLI command
 * based on workflow auto-proceed dropdown value.
 *
 * Feedback: Feedback-20260307-190453
 * Task: TASK-788
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { loadFeatureScript } from './helpers.js';

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

describe('CR-001: --execute@ flag based on auto-proceed', () => {
  let mockTerminalManager;

  beforeEach(() => {
    document.body.innerHTML = '';

    mockTerminalManager = {
      findIdleSession: vi.fn().mockResolvedValue({ sessionId: 'sess-1', key: 'tab-1' }),
      claimSessionForAction: vi.fn().mockResolvedValue(true),
      switchSession: vi.fn(),
      sendCopilotPromptCommandNoEnter: vi.fn(),
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

  function mockFetchWithAutoProceed(mode) {
    globalThis.fetch = vi.fn((url) => {
      if (url.includes('/api/workflow/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            data: {
              global: { process_preference: { auto_proceed: mode } },
              stages: { ideation: { actions: { compose_idea: {
                deliverables: ['x-ipe-docs/ideas/wf-hello/idea.md']
              }}}}
            }
          })
        });
      }
      if (url.includes('/api/config/copilot-prompt')) {
        return Promise.resolve({ ok: false });
      }
      return Promise.resolve({ ok: false });
    });
  }

  describe('_loadAutoProceed', () => {
    it('should load auto_proceed from workflow API', async () => {
      mockFetchWithAutoProceed('auto');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadAutoProceed();
      expect(modal._autoProceed).toBe('auto');
    });

    it('should default to manual when no workflow name', async () => {
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea' });
      await modal._loadAutoProceed();
      expect(modal._autoProceed).toBe('manual');
    });

    it('should default to manual when API fails', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({ ok: false });
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadAutoProceed();
      expect(modal._autoProceed).toBe('manual');
    });

    it('should handle stop_for_question mode', async () => {
      mockFetchWithAutoProceed('stop_for_question');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadAutoProceed();
      expect(modal._autoProceed).toBe('stop_for_question');
    });
  });

  describe('_buildExecutionFlag', () => {
    it('should return --execute@keep-running-forever for auto mode', () => {
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal._autoProceed = 'auto';
      expect(modal._buildExecutionFlag()).toBe(' --execute@keep-running-forever');
    });

    it('should return --execute@keep-running-forever-stop-only-on-question for stop_for_question', () => {
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal._autoProceed = 'stop_for_question';
      expect(modal._buildExecutionFlag()).toBe(' --execute@keep-running-forever-stop-only-on-question');
    });

    it('should return empty string for manual mode', () => {
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal._autoProceed = 'manual';
      expect(modal._buildExecutionFlag()).toBe('');
    });
  });

  describe('_buildCommand with execution flag', () => {
    it('should include --execute@ flag when auto mode', async () => {
      mockFetchWithAutoProceed('auto');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadInstructions();
      modal._autoProceed = 'auto';
      const cmd = modal._buildCommand('');
      expect(cmd).toContain('--execute@keep-running-forever');
    });

    it('should include --execute@ flag when stop_for_question mode', async () => {
      mockFetchWithAutoProceed('stop_for_question');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadInstructions();
      modal._autoProceed = 'stop_for_question';
      const cmd = modal._buildCommand('');
      expect(cmd).toContain('--execute@keep-running-forever-stop-only-on-question');
    });

    it('should NOT include --execute@ flag when manual mode', async () => {
      mockFetchWithAutoProceed('manual');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadInstructions();
      modal._autoProceed = 'manual';
      const cmd = modal._buildCommand('');
      expect(cmd).not.toContain('--execute@');
    });

    it('should place --execute@ after --workflow-mode', async () => {
      mockFetchWithAutoProceed('auto');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadInstructions();
      modal._autoProceed = 'auto';
      const cmd = modal._buildCommand('');
      const execIdx = cmd.indexOf('--execute@');
      const wfIdx = cmd.indexOf('--workflow-mode');
      expect(execIdx).toBeGreaterThan(-1);
      expect(execIdx).toBeGreaterThan(wfIdx);
    });
  });

  describe('_handleExecute with execution flag', () => {
    it('should send command with --execute@ flag to terminal', async () => {
      mockFetchWithAutoProceed('auto');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal.open();
      await modal._handleExecute();
      const sentCmd = mockTerminalManager.sendCopilotPromptCommandNoEnter.mock.calls[0][0];
      expect(sentCmd).toContain('--execute@keep-running-forever');
    });

    it('should NOT include --execution@ in manual mode', async () => {
      mockFetchWithAutoProceed('manual');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal.open();
      await modal._handleExecute();
      const sentCmd = mockTerminalManager.sendCopilotPromptCommandNoEnter.mock.calls[0][0];
      expect(sentCmd).not.toContain('--execute@');
    });
  });

  describe('Instruction preview shows CLI flags', () => {
    it('should show --execute@ flag in preview when auto mode', async () => {
      mockFetchWithAutoProceed('auto');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal.open();
      const preview = document.querySelector('.instructions-content');
      expect(preview.textContent).toContain('--execute@keep-running-forever');
    });

    it('should show --workflow-mode in preview', async () => {
      mockFetchWithAutoProceed('auto');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal.open();
      const preview = document.querySelector('.instructions-content');
      expect(preview.textContent).toContain('--workflow-mode@hello');
    });

    it('should NOT show --execution@ in preview when manual mode', async () => {
      mockFetchWithAutoProceed('manual');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal.open();
      const preview = document.querySelector('.instructions-content');
      expect(preview.textContent).not.toContain('--execute@');
    });
  });
});
