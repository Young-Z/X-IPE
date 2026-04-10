/**
 * Bug fix test: Folder browser tree indentation should not be too wide.
 * Feedback-20260410-153039 Issue 1: nested sub-folder/file indent is too wide.
 *
 * Validates: CSS padding-left for nested .file-tree is ≤ 12px.
 */
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const CSS_PATH = resolve(
  import.meta.dirname, '..', '..',
  'src/x_ipe/static/css/features/folder-browser-modal.css'
);

describe('Feedback-20260410-153039: folder-browser tree indentation', () => {
  it('nested .file-tree padding-left should be minimal (≤ 4px)', () => {
    const css = readFileSync(CSS_PATH, 'utf-8');

    // Find the rule for .folder-browser-tree .file-tree .file-tree
    const nestedRuleMatch = css.match(
      /\.folder-browser-tree\s+\.file-tree\s+\.file-tree\s*\{([^}]+)\}/
    );
    expect(nestedRuleMatch).toBeTruthy();

    const ruleBody = nestedRuleMatch[1];
    const paddingMatch = ruleBody.match(/padding-left\s*:\s*(\d+)(?:px)?/);
    expect(paddingMatch).toBeTruthy();

    const paddingValue = parseInt(paddingMatch[1], 10);
    expect(paddingValue).toBeLessThanOrEqual(4);
  });
});
