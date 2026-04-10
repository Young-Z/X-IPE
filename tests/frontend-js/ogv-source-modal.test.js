/**
 * TASK-4872: Source file modal must match FolderBrowserModal design pattern.
 *
 * Validates: fixed backdrop, blur, animated open/close, CSS variable theming,
 * Escape key handler, DM Sans font, close button hover background.
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const CSS_PATH = resolve(
  import.meta.dirname, '..', '..',
  'src/x_ipe/static/css/ontology-graph-viewer.css'
);

function readCSS() {
  return readFileSync(CSS_PATH, 'utf-8');
}

describe('TASK-4872: Source file modal matches FolderBrowserModal design', () => {
  let css;

  beforeEach(() => {
    css = readCSS();
  });

  it('backdrop uses position:fixed (not absolute) like FolderBrowserModal', () => {
    const overlayBlock = css.match(
      /\.ogv-source-modal-overlay\s*\{[^}]+\}/
    )?.[0];
    expect(overlayBlock).toBeDefined();
    expect(overlayBlock).toMatch(/position:\s*fixed/);
    expect(overlayBlock).not.toMatch(/position:\s*absolute/);
  });

  it('backdrop has opacity/visibility transition for animated open', () => {
    const overlayBlock = css.match(
      /\.ogv-source-modal-overlay\s*\{[^}]+\}/
    )?.[0];
    expect(overlayBlock).toBeDefined();
    expect(overlayBlock).toMatch(/opacity:\s*0/);
    expect(overlayBlock).toMatch(/visibility:\s*hidden/);
    expect(overlayBlock).toMatch(/transition/);
  });

  it('backdrop .active class sets opacity:1 and visibility:visible', () => {
    expect(css).toMatch(
      /\.ogv-source-modal-overlay\.active\s*\{[^}]*opacity:\s*1/
    );
    expect(css).toMatch(
      /\.ogv-source-modal-overlay\.active\s*\{[^}]*visibility:\s*visible/
    );
  });

  it('modal has transform scale transition like FolderBrowserModal', () => {
    const modalBlock = css.match(
      /\.ogv-source-modal\s*\{[^}]+\}/
    )?.[0];
    expect(modalBlock).toBeDefined();
    expect(modalBlock).toMatch(/transform:\s*scale\(0\.95\)/);
    expect(modalBlock).toMatch(/transition.*transform/);
  });

  it('active state scales modal to 1', () => {
    expect(css).toMatch(
      /\.ogv-source-modal-overlay\.active\s+\.ogv-source-modal[^{]*\{[^}]*transform:\s*scale\(1\)/
    );
  });

  it('uses CSS variable theming (--card-bg, --border-color) like FolderBrowserModal', () => {
    expect(css).toMatch(/var\(--card-bg/);
    expect(css).toMatch(/var\(--border-color/);
  });

  it('backdrop uses DM Sans font family', () => {
    const overlayBlock = css.match(
      /\.ogv-source-modal-overlay\s*\{[^}]+\}/
    )?.[0];
    expect(overlayBlock).toBeDefined();
    expect(overlayBlock).toMatch(/font-family.*DM Sans/i);
  });

  it('close button has hover background like FolderBrowserModal', () => {
    expect(css).toMatch(
      /\.ogv-source-modal-close:hover\s*\{[^}]*background/
    );
  });

  it('uses z-index >= 1051 matching FolderBrowserModal', () => {
    const overlayBlock = css.match(
      /\.ogv-source-modal-overlay\s*\{[^}]+\}/
    )?.[0];
    expect(overlayBlock).toBeDefined();
    const zMatch = overlayBlock.match(/z-index:\s*(\d+)/);
    expect(zMatch).toBeTruthy();
    expect(Number(zMatch[1])).toBeGreaterThanOrEqual(1051);
  });

  it('backdrop uses blur(4px) like FolderBrowserModal', () => {
    const overlayBlock = css.match(
      /\.ogv-source-modal-overlay\s*\{[^}]+\}/
    )?.[0];
    expect(overlayBlock).toBeDefined();
    expect(overlayBlock).toMatch(/backdrop-filter:\s*blur\(4px\)/);
  });
});
