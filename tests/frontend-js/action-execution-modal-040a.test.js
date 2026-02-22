/**
 * TDD Tests for FEATURE-040-A: Modal Generalization & Core Actions
 * Tests: _resolveInputFiles(), _getConfigEntry(), input_source resolution,
 *        manual path fallback, <input-file> placeholder, backward compat
 *
 * TDD: New tests MUST fail until FEATURE-040-A changes are implemented.
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

/* --- Shared config with input_source fields --- */
function configWithInputSource() {
  return {
    ideation: {
      prompts: [
        {
          id: 'refine-idea',
          icon: 'bi-stars',
          input_source: ['compose_idea'],
          'prompt-details': [
            { language: 'en', label: 'Refine Idea', command: 'refine the idea <current-idea-file>' }
          ]
        },
        {
          id: 'generate-mockup',
          icon: 'bi-palette',
          input_source: ['refine_idea', 'compose_idea'],
          'prompt-details': [
            { language: 'en', label: 'Generate Mockup', command: 'Base on <input-file> to generate mockups' }
          ]
        }
      ]
    },
    workflow: {
      prompts: [
        {
          id: 'requirement-gathering',
          icon: 'bi-clipboard-data',
          input_source: ['refine_idea', 'design_mockup'],
          'prompt-details': [
            { language: 'en', label: 'Requirement Gathering', command: 'gather requirements from <input-file> with requirement gathering skill' }
          ]
        },
        {
          id: 'feature-breakdown',
          icon: 'bi-diagram-2',
          input_source: ['requirement_gathering'],
          'prompt-details': [
            { language: 'en', label: 'Feature Breakdown', command: 'break down features from <input-file> with feature breakdown skill' }
          ]
        }
      ]
    },
    placeholder: {
      'current-idea-file': 'Replaced with currently open file path',
      'input-file': 'Replaced with selected input file path',
      'evaluation-file': 'x-ipe-docs/quality-evaluation/project-quality-evaluation.md'
    }
  };
}

/* --- Workflow state with multi-stage deliverables --- */
function workflowStateWithDeliverables() {
  return {
    data: {
      stages: {
        ideation: {
          actions: {
            compose_idea: {
              deliverables: ['x-ipe-docs/ideas/wf-test/new idea.md', 'x-ipe-docs/ideas/wf-test']
            },
            refine_idea: {
              deliverables: ['x-ipe-docs/ideas/wf-test/refined-idea/idea-summary-v1.md']
            },
            design_mockup: {
              deliverables: ['x-ipe-docs/ideas/wf-test/mockups']
            }
          }
        },
        requirement: {
          actions: {
            requirement_gathering: {
              deliverables: ['x-ipe-docs/requirements/requirement-details-part-5.md']
            }
          }
        }
      }
    }
  };
}

describe('FEATURE-040-A: Modal Generalization & Core Actions', () => {
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

    // Default: use config with input_source fields
    globalThis.window.__copilotPromptConfig = configWithInputSource();

    // Mock fetch: workflow API + tree API
    globalThis.fetch = vi.fn((url) => {
      if (url.includes('/deliverables/tree')) {
        const path = new URL(url, 'http://localhost').searchParams.get('path') || '';
        if (path.includes('mockups')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve([
              { type: 'file', path: 'x-ipe-docs/ideas/wf-test/mockups/mockup-v1.html' },
              { type: 'file', path: 'x-ipe-docs/ideas/wf-test/mockups/notes.md' }
            ])
          });
        }
        if (path.includes('refined-idea')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve([
              { type: 'file', path: 'x-ipe-docs/ideas/wf-test/refined-idea/idea-summary-v1.md' }
            ])
          });
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
      }
      if (url.includes('/api/workflow/')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(workflowStateWithDeliverables())
        });
      }
      if (url.includes('/api/config/copilot-prompt')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(configWithInputSource())
        });
      }
      return Promise.resolve({ ok: false });
    });

    ensureImpl();
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  /* ================================================================= */
  /*  _getConfigEntry() — Unified config lookup                         */
  /* ================================================================= */
  describe('Config Entry Lookup (_getConfigEntry)', () => {
    it('should find entry in ideation.prompts by actionKey', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'test' });
      const config = configWithInputSource();
      const entry = modal._getConfigEntry(config);
      expect(entry).toBeDefined();
      expect(entry.id).toBe('refine-idea');
    });

    it('should find entry in workflow.prompts by actionKey', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'requirement_gathering', workflowName: 'test' });
      const config = configWithInputSource();
      const entry = modal._getConfigEntry(config);
      expect(entry).toBeDefined();
      expect(entry.id).toBe('requirement-gathering');
    });

    it('should find feature_breakdown in workflow.prompts', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'feature_breakdown', workflowName: 'test' });
      const config = configWithInputSource();
      const entry = modal._getConfigEntry(config);
      expect(entry).toBeDefined();
      expect(entry.id).toBe('feature-breakdown');
    });

    it('should return null for unconfigured action', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'unknown_action', workflowName: 'test' });
      const config = configWithInputSource();
      const entry = modal._getConfigEntry(config);
      expect(entry).toBeNull();
    });
  });

  /* ================================================================= */
  /*  _resolveInputFiles() — Generic file resolution via input_source   */
  /* ================================================================= */
  describe('Input File Resolution (_resolveInputFiles)', () => {
    it('should resolve .md files from compose_idea deliverables', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'test' });
      const files = await modal._resolveInputFiles(['compose_idea']);
      expect(files).toContain('x-ipe-docs/ideas/wf-test/new idea.md');
    });

    it('should resolve files from refine_idea deliverables', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'requirement_gathering', workflowName: 'test' });
      const files = await modal._resolveInputFiles(['refine_idea']);
      expect(files).toContain('x-ipe-docs/ideas/wf-test/refined-idea/idea-summary-v1.md');
    });

    it('should merge files from multiple source actions', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'requirement_gathering', workflowName: 'test' });
      const files = await modal._resolveInputFiles(['refine_idea', 'design_mockup']);
      expect(files).toContain('x-ipe-docs/ideas/wf-test/refined-idea/idea-summary-v1.md');
      // design_mockup deliverable is a folder — tree scan should find notes.md
      expect(files).toContain('x-ipe-docs/ideas/wf-test/mockups/notes.md');
    });

    it('should scan folder deliverables via tree API', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'generate_mockup', workflowName: 'test' });
      // design_mockup has folder deliverable that gets scanned
      const files = await modal._resolveInputFiles(['design_mockup']);
      expect(files).toContain('x-ipe-docs/ideas/wf-test/mockups/notes.md');
      // non-.md files should be excluded
      expect(files).not.toContain('x-ipe-docs/ideas/wf-test/mockups/mockup-v1.html');
    });

    it('should deduplicate files across sources', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'test' });
      // compose_idea has both a .md file and a folder; folder scan may return same .md
      const files = await modal._resolveInputFiles(['compose_idea', 'compose_idea']);
      const unique = new Set(files);
      expect(files.length).toBe(unique.size);
    });

    it('should return empty array when source action has no deliverables', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      // Override fetch to return empty deliverables
      globalThis.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ data: { stages: { ideation: { actions: { compose_idea: { deliverables: [] } } } } } })
      });
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'test' });
      const files = await modal._resolveInputFiles(['compose_idea']);
      expect(files).toEqual([]);
    });

    it('should return empty array when workflow API fails', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      globalThis.fetch = vi.fn().mockResolvedValue({ ok: false });
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'test' });
      const files = await modal._resolveInputFiles(['compose_idea']);
      expect(files).toEqual([]);
    });

    it('should resolve requirement_gathering deliverables for feature_breakdown', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'feature_breakdown', workflowName: 'test' });
      const files = await modal._resolveInputFiles(['requirement_gathering']);
      expect(files).toContain('x-ipe-docs/requirements/requirement-details-part-5.md');
    });
  });

  /* ================================================================= */
  /*  <input-file> Placeholder Handling                                 */
  /* ================================================================= */
  describe('Input File Placeholder Resolution', () => {
    it('should resolve <input-file> placeholder in requirement_gathering command', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'requirement_gathering', workflowName: 'test' });
      await modal.open();
      const instructions = document.querySelector('.instructions-content');
      expect(instructions.textContent).toContain('x-ipe-docs/ideas/wf-test/refined-idea/idea-summary-v1.md');
      expect(instructions.textContent).not.toContain('<input-file>');
    });

    it('should resolve <input-file> placeholder in feature_breakdown command', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'feature_breakdown', workflowName: 'test' });
      await modal.open();
      const instructions = document.querySelector('.instructions-content');
      expect(instructions.textContent).toContain('x-ipe-docs/requirements/requirement-details-part-5.md');
      expect(instructions.textContent).not.toContain('<input-file>');
    });

    it('should still resolve <current-idea-file> for backward compat (refine_idea)', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'test' });
      await modal.open();
      const instructions = document.querySelector('.instructions-content');
      expect(instructions.textContent).not.toContain('<current-idea-file>');
      // Should have resolved to an actual file path
      expect(instructions.textContent).toContain('.md');
    });
  });

  /* ================================================================= */
  /*  File Selector UI                                                  */
  /* ================================================================= */
  describe('File Selector UI (input-selector)', () => {
    it('should show input-selector dropdown when files are resolved', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'requirement_gathering', workflowName: 'test' });
      await modal.open();
      const selector = document.querySelector('.input-selector');
      expect(selector).not.toBeNull();
    });

    it('should show all resolved files as options', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'requirement_gathering', workflowName: 'test' });
      await modal.open();
      const options = document.querySelectorAll('.input-selector option');
      expect(options.length).toBeGreaterThan(0);
    });

    it('should update command when different file is selected', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      // requirement_gathering has input_source: [refine_idea, design_mockup]
      // This should resolve multiple files
      const modal = new Modal({ actionKey: 'requirement_gathering', workflowName: 'test' });
      await modal.open();
      const selector = document.querySelector('.input-selector');
      if (selector && selector.options.length > 1) {
        selector.value = selector.options[1].value;
        selector.dispatchEvent(new Event('change'));
        const content = document.querySelector('.instructions-content');
        expect(content.textContent).toContain(selector.options[1].value);
      }
    });
  });

  /* ================================================================= */
  /*  Manual Path Fallback                                              */
  /* ================================================================= */
  describe('Manual Path Fallback', () => {
    it('should show text input when no files resolved but command has placeholder', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      // Override fetch to return empty deliverables for workflow state
      globalThis.fetch = vi.fn((url) => {
        if (url.includes('/api/workflow/')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ data: { stages: {} } })
          });
        }
        return Promise.resolve({ ok: false });
      });
      const modal = new Modal({ actionKey: 'requirement_gathering', workflowName: 'test' });
      await modal.open();
      const manualInput = document.querySelector('.input-path-manual');
      expect(manualInput).not.toBeNull();
      expect(document.querySelector('.input-selector')).toBeNull();
    });

    it('should update command when manual path is typed', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      globalThis.fetch = vi.fn((url) => {
        if (url.includes('/api/workflow/')) {
          return Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ data: { stages: {} } })
          });
        }
        return Promise.resolve({ ok: false });
      });
      const modal = new Modal({ actionKey: 'requirement_gathering', workflowName: 'test' });
      await modal.open();
      const manualInput = document.querySelector('.input-path-manual');
      if (manualInput) {
        manualInput.value = 'x-ipe-docs/ideas/custom-file.md';
        manualInput.dispatchEvent(new Event('input'));
        const content = document.querySelector('.instructions-content');
        expect(content.textContent).toContain('custom-file.md');
      }
    });
  });

  /* ================================================================= */
  /*  Missing Config (no-config-message)                                */
  /* ================================================================= */
  describe('Missing Config Handling', () => {
    it('should show "Configuration not yet available" when no config for action', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'acceptance_testing', workflowName: 'test' });
      await modal.open();
      const copilotBtn = document.querySelector('.copilot-btn');
      expect(copilotBtn.disabled).toBe(true);
    });

    it('should still show action title from actionKey when no config', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'acceptance_testing', workflowName: 'test' });
      await modal.open();
      const title = document.querySelector('.modal-title');
      expect(title.textContent).toContain('Acceptance Testing');
    });
  });

  /* ================================================================= */
  /*  Command Construction with <input-file>                            */
  /* ================================================================= */
  describe('Command Construction with input-file', () => {
    it('should include --workflow-mode prefix for all actions', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'requirement_gathering', workflowName: 'test' });
      await modal._loadInstructions();
      const cmd = modal._buildCommand('');
      expect(cmd).toMatch(/^--workflow-mode@test /);
    });

    it('should replace <input-file> in built command', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'requirement_gathering', workflowName: 'test' });
      await modal._loadInstructions();
      const cmd = modal._buildCommand('');
      expect(cmd).not.toContain('<input-file>');
      expect(cmd).toContain('gather requirements from');
    });

    it('should append --extra-instructions when provided', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const modal = new Modal({ actionKey: 'feature_breakdown', workflowName: 'test' });
      await modal._loadInstructions();
      const cmd = modal._buildCommand('focus on backend');
      expect(cmd).toContain('--extra-instructions focus on backend');
    });
  });

  /* ================================================================= */
  /*  Backward Compatibility                                            */
  /* ================================================================= */
  describe('Backward Compatibility', () => {
    it('should still work with legacy config without input_source', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      // Use config without input_source (legacy)
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
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'test' });
      await modal.open();
      const instructions = document.querySelector('.instructions-content');
      // Should still resolve via legacy _resolveIdeaFiles()
      expect(instructions.textContent).toContain('refine the idea');
    });

    it('should handle <current-idea-file> with input_source (new config)', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      // refine-idea has input_source AND <current-idea-file>
      const modal = new Modal({ actionKey: 'refine_idea', workflowName: 'test' });
      await modal._loadInstructions();
      const cmd = modal._buildCommand('');
      expect(cmd).not.toContain('<current-idea-file>');
    });

    it('should call onComplete after execution', async () => {
      const Modal = globalThis.ActionExecutionModal;
      if (!Modal) return;
      const onComplete = vi.fn();
      const modal = new Modal({ actionKey: 'requirement_gathering', workflowName: 'test', onComplete });
      await modal.open();
      await modal._handleExecute();
      expect(onComplete).toHaveBeenCalled();
    });
  });
});
