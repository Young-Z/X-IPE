/**
 * FEATURE-037-B: StageGateChecker unit tests (Vitest + jsdom)
 * Tests the actual JS class logic, not source code strings.
 */
import { describe, it, expect, beforeAll } from 'vitest';
import { loadFeatureScript } from './helpers.js';

beforeAll(() => {
  // Only load StageGateChecker class, stop before workflowStage which needs DOM
  loadFeatureScript('workflow-stage.js', { extractBefore: '\nconst workflowStage' });
});

describe('StageGateChecker', () => {
  function makeStages(overrides = {}) {
    return {
      ideation: {
        actions: {
          compose_idea: { status: 'done', ...(overrides.compose_idea || {}) },
        },
      },
      requirement: {
        actions: {
          feature_refinement: { status: 'pending', ...(overrides.feature_refinement || {}) },
          technical_design: { status: 'pending', ...(overrides.technical_design || {}) },
        },
      },
      implement: {
        actions: {
          implementation: { status: 'pending', ...(overrides.implementation || {}) },
        },
      },
      validation: {
        actions: {
          acceptance_testing: { status: 'pending', ...(overrides.acceptance_testing || {}) },
        },
      },
      feedback: {
        actions: {
          human_review: { status: 'pending', ...(overrides.human_review || {}) },
        },
      },
    };
  }

  describe('canReopen — allowed cases', () => {
    it('allows re-open when next stage has all pending actions', () => {
      const stages = makeStages();
      const result = StageGateChecker.canReopen('compose_idea', stages);
      expect(result).toEqual({ allowed: true });
    });

    it('allows re-open for action not found in any stage', () => {
      const stages = makeStages();
      const result = StageGateChecker.canReopen('nonexistent_action', stages);
      expect(result).toEqual({ allowed: true });
    });

    it('allows re-open for action in last stage (feedback)', () => {
      const stages = makeStages();
      const result = StageGateChecker.canReopen('human_review', stages);
      expect(result).toEqual({ allowed: true });
    });

    it('allows re-open when next stage has no actions property', () => {
      const stages = makeStages();
      delete stages.requirement.actions;
      const result = StageGateChecker.canReopen('compose_idea', stages);
      expect(result).toEqual({ allowed: true });
    });

    it('allows re-open when next stage is missing entirely', () => {
      const stages = makeStages();
      delete stages.requirement;
      const result = StageGateChecker.canReopen('compose_idea', stages);
      expect(result).toEqual({ allowed: true });
    });
  });

  describe('canReopen — blocked cases', () => {
    it('blocks when next stage has an in_progress action', () => {
      const stages = makeStages({ feature_refinement: { status: 'in_progress' } });
      const result = StageGateChecker.canReopen('compose_idea', stages);
      expect(result.allowed).toBe(false);
      expect(result.blocker).toBe('feature_refinement');
      expect(result.stage).toBe('requirement');
    });

    it('blocks when next stage has a done action', () => {
      const stages = makeStages({ feature_refinement: { status: 'done' } });
      const result = StageGateChecker.canReopen('compose_idea', stages);
      expect(result.allowed).toBe(false);
      expect(result.blocker).toBe('feature_refinement');
      expect(result.stage).toBe('requirement');
    });

    it('blocks on first in_progress/done action found in next stage', () => {
      const stages = makeStages({ technical_design: { status: 'done' } });
      const result = StageGateChecker.canReopen('compose_idea', stages);
      expect(result.allowed).toBe(false);
      expect(result.stage).toBe('requirement');
    });

    it('blocks requirement stage when implement has done actions', () => {
      const stages = makeStages({ implementation: { status: 'done' } });
      const result = StageGateChecker.canReopen('feature_refinement', stages);
      expect(result.allowed).toBe(false);
      expect(result.blocker).toBe('implementation');
      expect(result.stage).toBe('implement');
    });
  });

  describe('STAGE_ORDER', () => {
    it('has correct stage order', () => {
      expect(StageGateChecker.STAGE_ORDER).toEqual([
        'ideation', 'requirement', 'implement', 'validation', 'feedback',
      ]);
    });

    it('has 5 stages', () => {
      expect(StageGateChecker.STAGE_ORDER).toHaveLength(5);
    });
  });
});
