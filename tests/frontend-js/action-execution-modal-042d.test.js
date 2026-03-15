/**
 * TDD Tests for FEATURE-042-D: Full Migration & i18n
 * Tests: workflow-prompts completeness, i18n translations, tag correctness,
 *        deprecation markers, backward compatibility
 *
 * TDD: All tests MUST fail until FEATURE-042-D changes are implemented.
 */
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const config = JSON.parse(
  readFileSync(
    resolve(import.meta.dirname, '../../src/x_ipe/resources/config/copilot-prompt.json'),
    'utf-8'
  )
);

const EXPECTED_ACTIONS = [
  'refine_idea',
  'design_mockup',
  'requirement_gathering',
  'feature_breakdown',
  'feature_refinement',
  'technical_design',
  'implementation',
  'acceptance_testing',
  'code_refactor',
  'feature_closing',
  'human_playground',
  'change_request',
];

// ==============================================================================
// Tests: workflow-prompts completeness
// ==============================================================================

describe('FEATURE-042-D: workflow-prompts completeness', () => {
  it('workflow-prompts array has exactly 12 entries', () => {
    expect(config['workflow-prompts']).toBeDefined();
    expect(config['workflow-prompts']).toHaveLength(12);
  });

  it('all 12 action keys present', () => {
    const actions = config['workflow-prompts'].map((e) => e.action);
    for (const key of EXPECTED_ACTIONS) {
      expect(actions).toContain(key);
    }
  });

  it('no duplicate action keys', () => {
    const actions = config['workflow-prompts'].map((e) => e.action);
    const unique = new Set(actions);
    expect(unique.size).toBe(actions.length);
  });

  it('each entry has id, action, icon, input_source, prompt-details', () => {
    for (const entry of config['workflow-prompts']) {
      expect(entry).toHaveProperty('id');
      expect(entry).toHaveProperty('action');
      expect(entry).toHaveProperty('icon');
      expect(entry).toHaveProperty('input_source');
      expect(entry).toHaveProperty('prompt-details');
    }
  });
});

// ==============================================================================
// Tests: i18n translations
// ==============================================================================

describe('FEATURE-042-D: i18n translations', () => {
  it('each entry has English (en) prompt-details', () => {
    for (const entry of config['workflow-prompts']) {
      const en = entry['prompt-details'].find((p) => p.language === 'en');
      expect(en, `missing en for ${entry.action}`).toBeDefined();
    }
  });

  it('each entry has Chinese (zh) prompt-details', () => {
    for (const entry of config['workflow-prompts']) {
      const zh = entry['prompt-details'].find((p) => p.language === 'zh');
      expect(zh, `missing zh for ${entry.action}`).toBeDefined();
    }
  });

  it('each prompt-details has language, label, command', () => {
    for (const entry of config['workflow-prompts']) {
      for (const pd of entry['prompt-details']) {
        expect(pd).toHaveProperty('language');
        expect(pd).toHaveProperty('label');
        expect(pd).toHaveProperty('command');
        expect(pd.label).not.toBe('');
        expect(pd.command).not.toBe('');
      }
    }
  });

  it('English commands contain $output: or $feature-id$ tags', () => {
    for (const entry of config['workflow-prompts']) {
      const en = entry['prompt-details'].find((p) => p.language === 'en');
      const hasOutputTag = /\$output:[a-z-]+\$/.test(en.command);
      const hasFeatureTag = /\$feature-id\$/.test(en.command);
      expect(
        hasOutputTag || hasFeatureTag,
        `en command for ${entry.action} missing tags: "${en.command}"`
      ).toBe(true);
    }
  });

  it('Chinese commands contain appropriate tags', () => {
    for (const entry of config['workflow-prompts']) {
      const zh = entry['prompt-details'].find((p) => p.language === 'zh');
      const hasOutputTag = /\$output:[a-z-]+\$/.test(zh.command);
      const hasFeatureTag = /\$feature-id\$/.test(zh.command);
      expect(
        hasOutputTag || hasFeatureTag,
        `zh command for ${entry.action} missing tags: "${zh.command}"`
      ).toBe(true);
    }
  });
});

// ==============================================================================
// Tests: tag correctness
// ==============================================================================

describe('FEATURE-042-D: tag correctness', () => {
  function getEnCommand(action) {
    const entry = config['workflow-prompts'].find((e) => e.action === action);
    return entry['prompt-details'].find((p) => p.language === 'en').command;
  }

  it('refine_idea uses $output:raw-ideas$ and <...$output:uiux-reference$...>', () => {
    const cmd = getEnCommand('refine_idea');
    expect(cmd).toContain('$output:raw-ideas$');
    expect(cmd).toMatch(/<[^>]*\$output:uiux-reference\$[^>]*>/);
  });

  it('design_mockup uses $output:refined-idea$ and <...$output:uiux-reference$...>', () => {
    const cmd = getEnCommand('design_mockup');
    expect(cmd).toContain('$output:refined-idea$');
    expect(cmd).toMatch(/<[^>]*\$output:uiux-reference\$[^>]*>/);
  });

  it('requirement_gathering uses $output:refined-idea$ and <...$output:mockup-html$...>', () => {
    const cmd = getEnCommand('requirement_gathering');
    expect(cmd).toContain('$output:refined-idea$');
    expect(cmd).toMatch(/<[^>]*\$output:mockup-html\$[^>]*>/);
  });

  it('feature_breakdown uses $output:requirement-doc$', () => {
    const cmd = getEnCommand('feature_breakdown');
    expect(cmd).toContain('$output:requirement-doc$');
  });

  it('feature_refinement uses $feature-id$ and $output:requirement-doc$', () => {
    const cmd = getEnCommand('feature_refinement');
    expect(cmd).toContain('$feature-id$');
    expect(cmd).toContain('$output:requirement-doc$');
  });

  it('technical_design uses $feature-id$ and $output:specification$', () => {
    const cmd = getEnCommand('technical_design');
    expect(cmd).toContain('$feature-id$');
    expect(cmd).toContain('$output:specification$');
  });

  it('implementation uses $feature-id$, $output:tech-design$, $output:specification$', () => {
    const cmd = getEnCommand('implementation');
    expect(cmd).toContain('$feature-id$');
    expect(cmd).toContain('$output:tech-design$');
    expect(cmd).toContain('$output:specification$');
  });

  it('acceptance_testing uses $feature-id$ and $output:specification$', () => {
    const cmd = getEnCommand('acceptance_testing');
    expect(cmd).toContain('$feature-id$');
    expect(cmd).toContain('$output:specification$');
  });
});

// ==============================================================================
// Tests: deprecation markers
// ==============================================================================

describe('FEATURE-042-D: deprecation markers', () => {
  it('old refine-idea entry (in ideation.prompts) has _deprecated field', () => {
    const entry = config.ideation.prompts.find((p) => p.id === 'refine-idea');
    expect(entry).toBeDefined();
    expect(entry._deprecated).toBeDefined();
    expect(entry._deprecated).toContain('workflow-prompts');
  });

  it('old entries not deleted (still present)', () => {
    // ideation.prompts
    expect(config.ideation.prompts.find((p) => p.id === 'refine-idea')).toBeDefined();
    expect(config.ideation.prompts.find((p) => p.id === 'design-mockup')).toBeDefined();
    // workflow.prompts
    expect(config.workflow.prompts.find((p) => p.id === 'requirement-gathering')).toBeDefined();
    expect(config.workflow.prompts.find((p) => p.id === 'feature-breakdown')).toBeDefined();
    // feature.prompts
    expect(config.feature.prompts.find((p) => p.id === 'feature-refinement')).toBeDefined();
    expect(config.feature.prompts.find((p) => p.id === 'technical-design')).toBeDefined();
    expect(config.feature.prompts.find((p) => p.id === 'implementation')).toBeDefined();
    expect(config.feature.prompts.find((p) => p.id === 'acceptance-testing')).toBeDefined();
  });

  it('_deprecated field references workflow-prompts replacement', () => {
    const deprecatedEntries = [
      { section: config.ideation.prompts, id: 'refine-idea', action: 'refine_idea' },
      { section: config.ideation.prompts, id: 'design-mockup', action: 'design_mockup' },
      { section: config.workflow.prompts, id: 'requirement-gathering', action: 'requirement_gathering' },
      { section: config.workflow.prompts, id: 'feature-breakdown', action: 'feature_breakdown' },
      { section: config.feature.prompts, id: 'feature-refinement', action: 'feature_refinement' },
      { section: config.feature.prompts, id: 'technical-design', action: 'technical_design' },
      { section: config.feature.prompts, id: 'implementation', action: 'implementation' },
      { section: config.feature.prompts, id: 'acceptance-testing', action: 'acceptance_testing' },
    ];

    for (const { section, id, action } of deprecatedEntries) {
      const entry = section.find((p) => p.id === id);
      expect(entry, `entry ${id} missing`).toBeDefined();
      expect(entry._deprecated, `_deprecated missing on ${id}`).toBeDefined();
      expect(entry._deprecated).toContain(`workflow-prompts[${action}]`);
    }
  });
});

// ==============================================================================
// Tests: backward compatibility
// ==============================================================================

describe('FEATURE-042-D: backward compatibility', () => {
  it('free-mode prompts still exist unchanged', () => {
    const freeQuestion = config.ideation.prompts.find((p) => p.id === 'free-question');
    expect(freeQuestion).toBeDefined();
    expect(freeQuestion._deprecated).toBeUndefined();

    const genArch = config.ideation.prompts.find((p) => p.id === 'generate-architecture');
    expect(genArch).toBeDefined();
    expect(genArch._deprecated).toBeUndefined();

    const ideaReflection = config.ideation.prompts.find((p) => p.id === 'idea-reflection');
    expect(ideaReflection).toBeDefined();
    expect(ideaReflection._deprecated).toBeUndefined();

    const uiuxRef = config.ideation.prompts.find((p) => p.id === 'uiux-reference');
    expect(uiuxRef).toBeDefined();
    expect(uiuxRef._deprecated).toBeUndefined();
  });

  it('copilot-prompt.json version field present', () => {
    expect(config.version).toBeDefined();
    expect(config.version).toBe('3.3');
  });

  it('existing prompt sections (ideation, evaluation, workflow, feature) still present', () => {
    expect(config.ideation).toBeDefined();
    expect(config.evaluation).toBeDefined();
    expect(config.workflow).toBeDefined();
    expect(config.feature).toBeDefined();
  });
});
