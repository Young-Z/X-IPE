/**
 * TASK-791: Bug fix — refactoring dropdown items show no text because
 * quality-evaluation.js reads opt.label / opt.command directly, but the
 * copilot-prompt.json config now uses the prompt-details format.
 *
 * Also covers: evaluate button command and empty-state label resolution.
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { loadFeatureScript, mockFetch } from './helpers.js';

let _implLoaded = false;
function ensureImpl() {
  if (!_implLoaded) {
    try {
      loadFeatureScript('quality-evaluation.js');
      _implLoaded = true;
    } catch { /* TDD */ }
  }
  return typeof globalThis.QualityEvaluationView !== 'undefined';
}

/** Config using prompt-details format (v3.0 style) — no top-level label/command */
const PROMPT_DETAILS_CONFIG = {
  version: '3.0',
  evaluation: {
    evaluate: {
      id: 'evaluate',
      icon: 'bi-clipboard-check',
      'prompt-details': [
        { language: 'en', label: 'Evaluate Project Quality', command: 'Evaluate project quality and generate report' },
        { language: 'zh', label: '评估项目质量', command: '评估项目质量并生成报告' },
      ],
    },
    refactoring: [
      {
        id: 'refactor-all',
        icon: 'bi-arrow-repeat',
        'prompt-details': [
          { language: 'en', label: 'Refactor All', command: 'Refactor all with reference to <evaluation-file>' },
          { language: 'zh', label: '全面重构', command: '参照<evaluation-file>进行全面重构' },
        ],
      },
      {
        id: 'refactor-tests',
        icon: 'bi-bug',
        'prompt-details': [
          { language: 'en', label: 'Align Tests to Code', command: 'Update test cases to match current code' },
          { language: 'zh', label: '对齐测试与代码', command: '更新测试用例以匹配当前代码实现' },
        ],
      },
    ],
  },
  placeholder: { 'evaluation-file': 'x-ipe-docs/quality-evaluation/report.md' },
};

/** Legacy flat config — label/command at top level */
const LEGACY_CONFIG = {
  version: '2.0',
  evaluation: {
    evaluate: {
      label: 'Evaluate Project Quality',
      icon: 'bi-clipboard-check',
      command: 'Evaluate project quality and generate report',
    },
    refactoring: [
      {
        id: 'refactor-all',
        icon: 'bi-arrow-repeat',
        label: 'Refactor All',
        command: 'Refactor all with reference to <evaluation-file>',
      },
    ],
  },
  placeholder: { 'evaluation-file': 'x-ipe-docs/quality-evaluation/report.md' },
};

describe('TASK-791: Quality Evaluation prompt-details resolution', () => {
  let container;
  let view;
  let cleanupFetch;

  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);

    // Stub globals that sendToConsole may touch
    globalThis.window.terminalPanel = { expand: vi.fn() };
    globalThis.window.terminalManager = { sendCopilotPromptCommand: vi.fn() };
  });

  afterEach(() => {
    document.body.innerHTML = '';
    if (cleanupFetch) cleanupFetch();
  });

  // ---------- Refactoring dropdown text (the primary bug) ----------

  describe('renderRefactoringDropdown with prompt-details config', () => {
    it('should display English labels when config uses prompt-details', () => {
      if (!ensureImpl()) return;

      view = new QualityEvaluationView(container);
      view.config = PROMPT_DETAILS_CONFIG;

      const html = view.renderRefactoringDropdown(PROMPT_DETAILS_CONFIG.evaluation.refactoring);

      expect(html).toContain('Refactor All');
      expect(html).toContain('Align Tests to Code');
    });

    it('should set data-command from prompt-details', () => {
      if (!ensureImpl()) return;

      view = new QualityEvaluationView(container);
      view.config = PROMPT_DETAILS_CONFIG;

      const html = view.renderRefactoringDropdown(PROMPT_DETAILS_CONFIG.evaluation.refactoring);

      expect(html).toContain('data-command="Refactor all with reference to &lt;evaluation-file&gt;"');
      expect(html).toContain('data-command="Update test cases to match current code"');
    });

    it('should NOT show "undefined" for label or command', () => {
      if (!ensureImpl()) return;

      view = new QualityEvaluationView(container);
      view.config = PROMPT_DETAILS_CONFIG;

      const html = view.renderRefactoringDropdown(PROMPT_DETAILS_CONFIG.evaluation.refactoring);

      expect(html).not.toContain('undefined');
    });
  });

  // ---------- Legacy flat config backward compat ----------

  describe('renderRefactoringDropdown with legacy flat config', () => {
    it('should still work with top-level label/command', () => {
      if (!ensureImpl()) return;

      view = new QualityEvaluationView(container);
      view.config = LEGACY_CONFIG;

      const html = view.renderRefactoringDropdown(LEGACY_CONFIG.evaluation.refactoring);

      expect(html).toContain('Refactor All');
      expect(html).not.toContain('undefined');
    });
  });

  // ---------- Evaluate button command ----------

  describe('handleEvaluateClick with prompt-details config', () => {
    it('should resolve evaluate command from prompt-details and send to console', () => {
      if (!ensureImpl()) return;

      view = new QualityEvaluationView(container);
      view.config = PROMPT_DETAILS_CONFIG;

      view.handleEvaluateClick();

      expect(window.terminalManager.sendCopilotPromptCommand).toHaveBeenCalledWith(
        'Evaluate project quality and generate report'
      );
    });
  });

  // ---------- Empty state label ----------

  describe('renderEmptyState with prompt-details config', () => {
    it('should display resolved label in empty state CTA button', () => {
      if (!ensureImpl()) return;

      view = new QualityEvaluationView(container);
      view.config = PROMPT_DETAILS_CONFIG;
      view.status = { exists: false, versions: [] };

      view.renderEmptyState();

      const ctaBtn = document.getElementById('quality-empty-cta');
      expect(ctaBtn).toBeTruthy();
      expect(ctaBtn.textContent).toContain('Evaluate Project Quality');
      expect(ctaBtn.textContent).not.toContain('undefined');
    });
  });

  // ---------- _resolvePromptDetails helper ----------

  describe('_resolvePromptDetails', () => {
    it('should return label+command for matching language', () => {
      if (!ensureImpl()) return;

      view = new QualityEvaluationView(container);
      const result = view._resolvePromptDetails(PROMPT_DETAILS_CONFIG.evaluation.evaluate, 'en');

      expect(result).toEqual({ label: 'Evaluate Project Quality', command: 'Evaluate project quality and generate report' });
    });

    it('should fall back to English when requested language is missing', () => {
      if (!ensureImpl()) return;

      view = new QualityEvaluationView(container);
      const result = view._resolvePromptDetails(PROMPT_DETAILS_CONFIG.evaluation.evaluate, 'fr');

      expect(result).toEqual({ label: 'Evaluate Project Quality', command: 'Evaluate project quality and generate report' });
    });

    it('should fall back to top-level label/command for legacy config', () => {
      if (!ensureImpl()) return;

      view = new QualityEvaluationView(container);
      const result = view._resolvePromptDetails(LEGACY_CONFIG.evaluation.evaluate, 'en');

      expect(result).toEqual({ label: 'Evaluate Project Quality', command: 'Evaluate project quality and generate report' });
    });

    it('should return null when no label/command found', () => {
      if (!ensureImpl()) return;

      view = new QualityEvaluationView(container);
      const result = view._resolvePromptDetails({ icon: 'bi-test' }, 'en');

      expect(result).toBeNull();
    });
  });
});
