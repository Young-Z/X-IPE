/**
 * Bug fix test: OGV navigator minimap image should not show broken icon.
 * Feedback-20260410-153039 Issue 2: the nav-thumb img is created without src,
 * causing a broken image icon before the graph renders.
 *
 * Validates: img starts hidden, becomes visible after thumbnail is set.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import vm from 'vm';

const JS_FEATURES = resolve(
  import.meta.dirname, '..', '..',
  'src/x_ipe/static/js/features'
);

function loadScript(filename) {
  let code = readFileSync(resolve(JS_FEATURES, filename), 'utf-8');
  const classMatches = code.matchAll(/^class\s+(\w+)/gm);
  const expose = [];
  for (const m of classMatches) expose.push(m[1]);
  const assignments = [...new Set(expose)]
    .map(name => `globalThis.${name} = ${name};`)
    .join('\n');
  code += '\n' + assignments;
  vm.runInThisContext(code);
}

describe('Feedback-20260410-153039: OGV navigator thumbnail visibility', () => {
  let mockCy;

  beforeEach(() => {
    document.body.innerHTML = '';

    if (!globalThis._ogvNavThumbTestLoaded) {
      // Mock cytoscape
      mockCy = {
        on: vi.fn(),
        style: vi.fn().mockReturnThis(),
        layout: vi.fn().mockReturnValue({ run: vi.fn() }),
        nodes: vi.fn().mockReturnValue({ length: 3, on: vi.fn(), forEach: vi.fn() }),
        edges: vi.fn().mockReturnValue({ length: 0, on: vi.fn(), forEach: vi.fn() }),
        fit: vi.fn(), zoom: vi.fn().mockReturnValue(1), pan: vi.fn(), resize: vi.fn(),
        png: vi.fn(() => 'data:image/png;base64,TESTPNG'),
        destroy: vi.fn(), container: vi.fn(), getElementById: vi.fn(),
        extent: vi.fn(() => ({ x1: 0, y1: 0, x2: 100, y2: 100 })),
        elements: vi.fn(() => ({ boundingBox: () => ({ x1: 0, y1: 0, w: 200, h: 200 }) })),
      };
      globalThis.cytoscape = vi.fn(() => mockCy);
      loadScript('ontology-graph-canvas.js');
      globalThis._ogvNavThumbTestLoaded = true;
    }
  });

  it('navigator img should be hidden (not visible) before thumbnail is generated', () => {
    const container = document.createElement('div');
    document.body.appendChild(container);
    const canvas = new OntologyGraphCanvas(container);
    canvas.cy = globalThis.cytoscape();
    const navContainer = document.createElement('div');
    navContainer.className = 'ogv-navigator';
    document.body.appendChild(navContainer);

    canvas.initNavigator(navContainer);

    const thumb = navContainer.querySelector('.ogv-nav-thumb');
    expect(thumb).toBeTruthy();
    // The img must NOT be visible when it has no src (prevents broken image icon)
    expect(thumb.style.visibility).toBe('hidden');
  });

  it('navigator img should become visible after thumbnail is set', () => {
    const container = document.createElement('div');
    document.body.appendChild(container);
    const canvas = new OntologyGraphCanvas(container);
    canvas.cy = globalThis.cytoscape();
    const navContainer = document.createElement('div');
    navContainer.className = 'ogv-navigator';
    document.body.appendChild(navContainer);

    canvas.initNavigator(navContainer);

    // Simulate thumbnail update (normally called on cy render event)
    canvas._updateNavThumbnail();

    const thumb = navContainer.querySelector('.ogv-nav-thumb');
    expect(thumb.style.visibility).toBe('visible');
  });
});
