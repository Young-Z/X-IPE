import { beforeAll, expect, it } from 'vitest';
import { loadFeatureScript } from './helpers.js';

beforeAll(() => loadFeatureScript('workflow-stage.js'));

it('keeps acceptance and closing mandatory but offers refactoring only when useful', () => {
  const actions = workflowStage.ACTION_MAP.validation.actions;
  expect(actions.acceptance_testing.mandatory).toBe(true);
  expect(actions.feature_closing.mandatory).toBe(true);
  expect(actions.code_refactor.mandatory).toBe(false);
});
