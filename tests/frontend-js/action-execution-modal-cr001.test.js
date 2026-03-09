/**
 * Tests for CR-001/CR-002: Append --interaction@mode flag to CLI command
 * based on workflow interaction mode dropdown value.
 *
 * Feedback: Feedback-20260307-190453
 * Task: TASK-788, TASK-796 (CR-002 rename)
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

describe('CR-001/CR-002: --interaction@ flag based on interaction mode', () => {
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

  function mockFetchWithInteractionMode(mode) {
    globalThis.fetch = vi.fn((url) => {
      if (url.includes('/api/workflow/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            data: {
              global: { process_preference: { interaction_mode: mode } },
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

  function mockFetchWithLegacyAutoProceed(mode) {
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

  describe('_loadInteractionMode', () => {
    it('should load interaction_mode from workflow API', async () => {
      mockFetchWithInteractionMode('dao-represent-human-to-interact');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadInteractionMode();
      expect(modal._interactionMode).toBe('dao-represent-human-to-interact');
    });

    it('should default to interact-with-human when no workflow name', async () => {
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea' });
      await modal._loadInteractionMode();
      expect(modal._interactionMode).toBe('interact-with-human');
    });

    it('should default to interact-with-human when API fails', async () => {
      globalThis.fetch = vi.fn().mockResolvedValue({ ok: false });
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadInteractionMode();
      expect(modal._interactionMode).toBe('interact-with-human');
    });

    it('should handle dao-represent-human-to-interact-for-questions-in-skill mode', async () => {
      mockFetchWithInteractionMode('dao-represent-human-to-interact-for-questions-in-skill');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadInteractionMode();
      expect(modal._interactionMode).toBe('dao-represent-human-to-interact-for-questions-in-skill');
    });

    it('should migrate legacy auto_proceed "auto" to dao-represent-human-to-interact', async () => {
      mockFetchWithLegacyAutoProceed('auto');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadInteractionMode();
      expect(modal._interactionMode).toBe('dao-represent-human-to-interact');
    });

    it('should migrate legacy auto_proceed "manual" to interact-with-human', async () => {
      mockFetchWithLegacyAutoProceed('manual');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadInteractionMode();
      expect(modal._interactionMode).toBe('interact-with-human');
    });

    it('should migrate legacy auto_proceed "stop_for_question" to dao-represent-human-to-interact-for-questions-in-skill', async () => {
      mockFetchWithLegacyAutoProceed('stop_for_question');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadInteractionMode();
      expect(modal._interactionMode).toBe('dao-represent-human-to-interact-for-questions-in-skill');
    });
  });

  describe('_buildExecutionFlag', () => {
    it('should return --interaction@dao-represent-human-to-interact for DAO mode', () => {
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal._interactionMode = 'dao-represent-human-to-interact';
      expect(modal._buildExecutionFlag()).toBe(' --interaction@dao-represent-human-to-interact');
    });

    it('should return --interaction@dao-represent-human-to-interact-for-questions-in-skill for DAO inner-skill only', () => {
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal._interactionMode = 'dao-represent-human-to-interact-for-questions-in-skill';
      expect(modal._buildExecutionFlag()).toBe(' --interaction@dao-represent-human-to-interact-for-questions-in-skill');
    });

    it('should return empty string for interact-with-human mode', () => {
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      modal._interactionMode = 'interact-with-human';
      expect(modal._buildExecutionFlag()).toBe('');
    });
  });

  describe('_buildCommand with interaction flag', () => {
    it('should include --interaction@ flag when DAO mode', async () => {
      mockFetchWithInteractionMode('dao-represent-human-to-interact');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadInstructions();
      modal._interactionMode = 'dao-represent-human-to-interact';
      const cmd = modal._buildCommand('');
      expect(cmd).toContain('--interaction@dao-represent-human-to-interact');
    });

    it('should include --interaction@ flag when DAO inner-skill only mode', async () => {
      mockFetchWithInteractionMode('dao-represent-human-to-interact-for-questions-in-skill');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadInstructions();
      modal._interactionMode = 'dao-represent-human-to-interact-for-questions-in-skill';
      const cmd = modal._buildCommand('');
      expect(cmd).toContain('--interaction@dao-represent-human-to-interact-for-questions-in-skill');
    });

    it('should NOT include --interaction@ flag when interact-with-human mode', async () => {
      mockFetchWithInteractionMode('interact-with-human');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadInstructions();
      modal._interactionMode = 'interact-with-human';
      const cmd = modal._buildCommand('');
      expect(cmd).not.toContain('--interaction@');
    });

    it('should place --interaction@ after --workflow-mode', async () => {
      mockFetchWithInteractionMode('dao-represent-human-to-interact');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal._loadInstructions();
      modal._interactionMode = 'dao-represent-human-to-interact';
      const cmd = modal._buildCommand('');
      const execIdx = cmd.indexOf('--interaction@');
      const wfIdx = cmd.indexOf('--workflow-mode');
      expect(execIdx).toBeGreaterThan(-1);
      expect(execIdx).toBeGreaterThan(wfIdx);
    });
  });

  describe('_handleExecute with interaction flag', () => {
    it('should send command with --interaction@ flag to terminal', async () => {
      mockFetchWithInteractionMode('dao-represent-human-to-interact');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal.open();
      await modal._handleExecute();
      const sentCmd = mockTerminalManager.sendCopilotPromptCommandNoEnter.mock.calls[0][0];
      expect(sentCmd).toContain('--interaction@dao-represent-human-to-interact');
    });

    it('should NOT include --interaction@ in interact-with-human mode', async () => {
      mockFetchWithInteractionMode('interact-with-human');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal.open();
      await modal._handleExecute();
      const sentCmd = mockTerminalManager.sendCopilotPromptCommandNoEnter.mock.calls[0][0];
      expect(sentCmd).not.toContain('--interaction@');
    });
  });

  describe('Instruction preview shows CLI flags', () => {
    it('should show --interaction@ flag in preview when DAO mode', async () => {
      mockFetchWithInteractionMode('dao-represent-human-to-interact');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal.open();
      const preview = document.querySelector('.instructions-content');
      expect(preview.textContent).toContain('--interaction@dao-represent-human-to-interact');
    });

    it('should show --workflow-mode in preview', async () => {
      mockFetchWithInteractionMode('dao-represent-human-to-interact');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal.open();
      const preview = document.querySelector('.instructions-content');
      expect(preview.textContent).toContain('--workflow-mode@hello');
    });

    it('should NOT show --interaction@ in preview when interact-with-human mode', async () => {
      mockFetchWithInteractionMode('interact-with-human');
      const Modal = globalThis.ActionExecutionModal;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'hello' });
      await modal.open();
      const preview = document.querySelector('.instructions-content');
      expect(preview.textContent).not.toContain('--interaction@');
    });
  });
});
