/**
 * TASK-962: CR-006 Full-width article content layout — CSS assertion tests
 *
 * Verifies that .kb-article-main no longer has a fixed max-width constraint,
 * allowing content to expand to fill available horizontal space.
 */
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const CSS_PATH = resolve(
  __dirname,
  '../../src/x_ipe/static/css/kb-browse-modal.css'
);
const cssContent = readFileSync(CSS_PATH, 'utf-8');

/**
 * Parse a CSS rule block for a given selector.
 * Returns the property declarations as a string.
 */
function getCssBlock(css, selector) {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp(`${escaped}\\s*\\{([^}]+)\\}`, 'g');
  const matches = [];
  let m;
  while ((m = re.exec(css)) !== null) {
    matches.push(m[1]);
  }
  return matches.join('\n');
}

describe('TASK-962 / CR-006: Full-Width Article Content Layout', () => {
  it('AC-049-F-17a: .kb-article-main has no fixed max-width constraint', () => {
    const block = getCssBlock(cssContent, '.kb-article-main');
    expect(block).toBeTruthy();
    // Should NOT contain max-width (was 780px, now removed)
    expect(block).not.toContain('max-width');
  });

  it('AC-049-F-17a: .kb-article-main uses flex: 1 to fill available space', () => {
    const block = getCssBlock(cssContent, '.kb-article-main');
    expect(block).toContain('flex: 1');
  });

  it('AC-049-F-17a: .kb-article-main has horizontal padding for readability margins', () => {
    const block = getCssBlock(cssContent, '.kb-article-main');
    // padding should include horizontal component (48px)
    expect(block).toMatch(/padding\s*:.*48px/);
  });

  it('AC-049-F-17b: .kb-article-sidebar retains fixed 260px width', () => {
    const block = getCssBlock(cssContent, '.kb-article-sidebar');
    expect(block).toContain('width: 260px');
    expect(block).toContain('min-width: 260px');
  });

  it('AC-049-F-17c: .kb-image-preview scales to 100% of container', () => {
    const block = getCssBlock(cssContent, '.kb-image-preview');
    expect(block).toContain('max-width: 100%');
  });

  it('AC-049-F-17d: sidebar is hidden below 900px viewport', () => {
    // Verify media query exists that hides sidebar
    expect(cssContent).toMatch(/@media\s*\(\s*max-width\s*:\s*900px\s*\)/);
    // Within that media query, sidebar should have display: none
    const mediaMatch = cssContent.match(
      /@media\s*\(\s*max-width\s*:\s*900px\s*\)\s*\{([\s\S]*?)\}\s*\}/
    );
    expect(mediaMatch).toBeTruthy();
    expect(mediaMatch[1]).toContain('.kb-article-sidebar');
    expect(mediaMatch[1]).toContain('display: none');
  });
});
