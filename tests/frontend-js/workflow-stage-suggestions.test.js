/**
 * TASK-590: Bug fix — next_actions_suggested not applied in completed stages.
 * When a done action in a completed stage lists next_actions_suggested,
 * pending actions in that same stage should render with the 'suggested' class.
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { loadFeatureScript } from './helpers.js';

beforeEach(() => {
  document.body.innerHTML = '<div id="root"></div>';
  loadFeatureScript('workflow-stage.js');
});

describe('next_actions_suggested in completed stages', () => {
  it('should mark design_mockup as suggested when refine_idea suggests it', () => {
    const container = document.getElementById('root');
    const workflowState = {
      stages: {
        ideation: {
          status: 'completed',
          actions: {
            compose_idea: { status: 'done', deliverables: [] },
            reference_uiux: { status: 'pending', deliverables: [], optional: true },
            refine_idea: {
              status: 'done',
              deliverables: [],
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
        }
      }
    };

    const nextAction = { stage: 'requirement', action: 'requirement_gathering' };
    workflowStage.render(container, workflowState, nextAction, 'test-wf');

    // design_mockup is in the completed ideation stage; it should have 'suggested' class
    const buttons = container.querySelectorAll('.action-btn');
    const designMockupBtn = Array.from(buttons).find(b => b.textContent.includes('Design Mockup'));
    expect(designMockupBtn).toBeTruthy();
    expect(designMockupBtn.classList.contains('suggested')).toBe(true);
  });
});
