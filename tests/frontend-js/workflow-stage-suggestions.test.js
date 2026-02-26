/**
 * TASK-590: Bug fix — next_actions_suggested not applied in completed stages.
 * When a done action in a completed stage lists next_actions_suggested,
 * pending actions in that same stage should render with the 'suggested' class.
 */
import { describe, it, expect, beforeAll, beforeEach } from 'vitest';
import { loadFeatureScript } from './helpers.js';

beforeAll(() => {
  loadFeatureScript('workflow-stage.js');
});

beforeEach(() => {
  document.body.innerHTML = '<div id="root"></div>';
});

describe('next_actions_suggested in completed stages', () => {
  function buildState(overrides = {}) {
    return {
      shared: {
        ideation: {
          status: 'completed',
          actions: {
            compose_idea: {
              status: 'done', deliverables: [],
              next_actions_suggested: ['refine_idea', 'reference_uiux']
            },
            reference_uiux: { status: 'pending', deliverables: [], optional: true },
            refine_idea: {
              status: 'done', deliverables: [],
              next_actions_suggested: ['design_mockup', 'requirement_gathering']
            },
            design_mockup: { status: 'pending', deliverables: [], optional: true }
          }
        },
        requirement: {
          status: 'in_progress',
          actions: {
            requirement_gathering: { status: 'pending', deliverables: [] },
            feature_breakdown: { status: 'pending', deliverables: [] }
          }
        },
        ...overrides
      },
      features: []
    };
  }

  function findBtn(container, label) {
    return Array.from(container.querySelectorAll('.action-btn')).find(b => b.textContent.includes(label));
  }

  it('should mark design_mockup as suggested (latest done action suggests it)', () => {
    const container = document.getElementById('root');
    workflowStage.render(container, buildState(), { stage: 'requirement', action: 'requirement_gathering' }, 'test-wf');

    expect(findBtn(container, 'Design Mockup').classList.contains('suggested')).toBe(true);
  });

  it('should NOT mark reference_uiux as suggested (only earlier compose_idea suggests it)', () => {
    const container = document.getElementById('root');
    workflowStage.render(container, buildState(), { stage: 'requirement', action: 'requirement_gathering' }, 'test-wf');

    // reference_uiux was suggested by compose_idea, but refine_idea is the latest done action
    expect(findBtn(container, 'Reference UIUX').classList.contains('suggested')).toBe(false);
  });
});
