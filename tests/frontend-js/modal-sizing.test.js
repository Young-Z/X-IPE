/**
 * TASK-616: All workflow modals should have 90vw width and 90vh height.
 * Validates CSS sizing consistency across all modal windows in workflow mode.
 */
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const PROJECT_ROOT = resolve(import.meta.dirname, '..', '..');
const CSS_DIR = resolve(PROJECT_ROOT, 'src/x_ipe/static/css');
const CSS_FEATURES = resolve(CSS_DIR, 'features');

function readCSS(dir, filename) {
  return readFileSync(resolve(dir, filename), 'utf-8');
}

describe('TASK-616: Modal window sizing consistency (90vw × 90vh)', () => {

  it('deliverable-preview should have width: 90vw and height: 90vh', () => {
    const css = readCSS(CSS_DIR, 'workflow.css');
    // Match .deliverable-preview rule (not .deliverable-preview-backdrop)
    const match = css.match(/\.deliverable-preview\s*\{([^}]+)\}/);
    expect(match).toBeTruthy();
    const rule = match[1];
    expect(rule).toContain('width: 90vw');
    expect(rule).toContain('height: 90vh');
  });

  it('compose-modal should have width: 90vw and height: 90vh', () => {
    const css = readCSS(CSS_FEATURES, 'compose-idea-modal.css');
    const match = css.match(/\.compose-modal\s*\{([^}]+)\}/);
    expect(match).toBeTruthy();
    const rule = match[1];
    expect(rule).toContain('width: 90vw');
    expect(rule).toContain('height: 90vh');
  });

  it('action-execution modal-container should have width: 90vw and height: 90vh', () => {
    const css = readCSS(CSS_FEATURES, 'action-execution-modal.css');
    const match = css.match(/\.modal-overlay\s+\.modal-container\s*\{([^}]+)\}/);
    expect(match).toBeTruthy();
    const rule = match[1];
    expect(rule).toContain('width: 90vw');
    expect(rule).toContain('height: 90vh');
  });

  it('folder-browser-modal should have width: 90vw and height: 90vh', () => {
    const css = readCSS(CSS_FEATURES, 'folder-browser-modal.css');
    const match = css.match(/\.folder-browser-modal\s*\{([^}]+)\}/);
    expect(match).toBeTruthy();
    const rule = match[1];
    expect(rule).toContain('width: 90vw');
    expect(rule).toContain('height: 90vh');
  });

  it('toolbox-modal should have width: 90vw and height: 90vh', () => {
    const css = readCSS(CSS_FEATURES, 'stage-toolbox.css');
    const match = css.match(/\.toolbox-modal\s*\{([^}]+)\}/);
    expect(match).toBeTruthy();
    const rule = match[1];
    expect(rule).toContain('width: 90vw');
    expect(rule).toContain('height: 90vh');
  });
});
