/**
 * Bug fix tests: TASK-983 — Modal UI labels not localized when language=zh
 *
 * When .x-ipe.yaml has language: zh, the modal section labels
 * ("Instructions", "Extra Instructions", "Action Context", etc.)
 * should be rendered in Chinese. Technical flags like --workflow-mode
 * remain in English.
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

function workflowPromptsConfig() {
  return {
    version: '3.3',
    'workflow-prompts': [
      {
        id: 'refine-idea',
        action: 'refine_idea',
        icon: 'bi-stars',
        input_source: ['compose_idea'],
        'prompt-details': [
          {
            language: 'en',
            label: 'Refine Idea',
            command: 'refine the idea $output:raw-ideas$ with ideation skill'
          },
          {
            language: 'zh',
            label: '完善创意',
            command: '使用创意技能, 完善创意 $output:raw-ideas$'
          }
        ]
      }
    ]
  };
}

function taggedTemplate() {
  return {
    stage_order: ['ideation'],
    stages: {
      ideation: {
        type: 'shared',
        actions: {
          refine_idea: {
            optional: false,
            action_context: {
              'raw-ideas': { required: true, candidates: 'ideas-folder' },
              'uiux-reference': { required: false }
            },
            deliverables: ['$output:refined-idea'],
            next_actions_suggested: []
          }
        }
      }
    }
  };
}

function workflowInstance() {
  return {
    data: {
      stages: {
        ideation: {
          actions: {
            compose_idea: {
              status: 'done',
              deliverables: { 'raw-ideas': 'x-ipe-docs/ideas/test/idea.md' }
            },
            refine_idea: { status: 'pending' }
          }
        }
      }
    }
  };
}

function setupFetchMocks(language = 'zh') {
  const config = workflowPromptsConfig();
  const template = taggedTemplate();
  const instance = workflowInstance();

  globalThis.fetch = vi.fn((url) => {
    // /api/config returns the language setting
    if (url === '/api/config' || url.endsWith('/api/config')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ detected: true, language })
      });
    }
    if (url.includes('/api/config/copilot-prompt')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(config)
      });
    }
    if (url.includes('/api/workflow/template')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(template)
      });
    }
    if (url.includes('/candidates/')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([
          { type: 'file', path: 'x-ipe-docs/ideas/test/idea.md' }
        ])
      });
    }
    if (url.includes('/api/workflow/') && !url.includes('/action')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(instance)
      });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });
}

describe('TASK-983: Modal UI label localization (language=zh)', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    globalThis.window = globalThis.window || {};
    globalThis.window.__copilotPromptConfig = undefined;
    globalThis.window.terminalManager = {
      findIdleSession: vi.fn().mockResolvedValue({ sessionId: 's1', key: 't1' }),
      claimSessionForAction: vi.fn().mockResolvedValue(true),
      switchSession: vi.fn(),
      sendCopilotPromptCommandNoEnter: vi.fn(),
      addSession: vi.fn().mockReturnValue('new-tab'),
    };
    ensureImpl();
  });

  afterEach(() => {
    document.body.innerHTML = '';
    globalThis.window.__copilotPromptConfig = undefined;
  });

  it('should render modal title in Chinese when language=zh', async () => {
    setupFetchMocks('zh');
    const modal = new globalThis.ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
      onComplete: () => {}
    });
    await modal.open();

    const title = document.querySelector('.modal-title');
    expect(title).not.toBeNull();
    expect(title.textContent).toBe('完善创意');
    modal.close();
  });

  it('should render "Instructions" label in Chinese when language=zh', async () => {
    setupFetchMocks('zh');
    const modal = new globalThis.ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
      onComplete: () => {}
    });
    await modal.open();

    const labels = document.querySelectorAll('.instructions-label');
    const instructionsLabel = Array.from(labels).find(
      el => el.closest('.instructions-section')
    );
    expect(instructionsLabel).not.toBeNull();
    expect(instructionsLabel.textContent).toBe('指令');
    modal.close();
  });

  it('should render "Extra Instructions" label in Chinese when language=zh', async () => {
    setupFetchMocks('zh');
    const modal = new globalThis.ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
      onComplete: () => {}
    });
    await modal.open();

    const extraLabel = document.querySelector('.extra-label');
    expect(extraLabel).not.toBeNull();
    expect(extraLabel.textContent).toBe('额外指令');
    modal.close();
  });

  it('should render "Action Context" heading in Chinese when language=zh', async () => {
    setupFetchMocks('zh');
    const modal = new globalThis.ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
      onComplete: () => {}
    });
    await modal.open();

    const heading = document.querySelector('.action-context-section h4');
    expect(heading).not.toBeNull();
    expect(heading.textContent).toBe('操作上下文');
    modal.close();
  });

  it('should render extra instructions placeholder in Chinese when language=zh', async () => {
    setupFetchMocks('zh');
    const modal = new globalThis.ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
      onComplete: () => {}
    });
    await modal.open();

    const textarea = document.querySelector('.extra-input');
    expect(textarea).not.toBeNull();
    expect(textarea.placeholder).toContain('可选');
    modal.close();
  });

  it('should render Cancel button in Chinese when language=zh', async () => {
    setupFetchMocks('zh');
    const modal = new globalThis.ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
      onComplete: () => {}
    });
    await modal.open();

    const cancelBtn = document.querySelector('.cancel-btn');
    expect(cancelBtn).not.toBeNull();
    expect(cancelBtn.textContent).toBe('取消');
    modal.close();
  });

  it('should keep labels in English when language=en', async () => {
    setupFetchMocks('en');
    const modal = new globalThis.ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
      onComplete: () => {}
    });
    await modal.open();

    const title = document.querySelector('.modal-title');
    expect(title.textContent).toBe('Refine Idea');

    const extraLabel = document.querySelector('.extra-label');
    expect(extraLabel.textContent).toBe('Extra Instructions');

    const cancelBtn = document.querySelector('.cancel-btn');
    expect(cancelBtn.textContent).toBe('Cancel');
    modal.close();
  });

  it('should use instruction command text in Chinese when language=zh', async () => {
    setupFetchMocks('zh');
    const modal = new globalThis.ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
      onComplete: () => {}
    });
    await modal.open();

    const content = document.querySelector('.instructions-content');
    expect(content).not.toBeNull();
    // The command text should contain Chinese, not English
    expect(content.textContent).toContain('使用创意技能');
    expect(content.textContent).not.toContain('refine the idea');
    // Technical flags should still be English
    expect(content.textContent).toContain('--workflow-mode');
    modal.close();
  });

  it('should render (optional) marker in Chinese when language=zh', async () => {
    setupFetchMocks('zh');
    const modal = new globalThis.ActionExecutionModal({
      actionKey: 'refine_idea',
      workflowName: 'test-wf',
      onComplete: () => {}
    });
    await modal.open();

    const optionalSpan = document.querySelector('.optional');
    if (optionalSpan) {
      expect(optionalSpan.textContent).toBe('(可选)');
    }
    modal.close();
  });
});
