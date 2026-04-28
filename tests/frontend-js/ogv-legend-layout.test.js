/**
 * TASK-4897: KG legend should sit at the bottom-right and not overlap the
 * bottom-left minimap. Zoom controls must be lifted above the legend.
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const CSS_PATH = resolve(
  import.meta.dirname, '..', '..',
  'src/x_ipe/static/css/ontology-graph-viewer.css'
);

function loadGraphCss() {
  const style = document.createElement('style');
  style.textContent = readFileSync(CSS_PATH, 'utf-8');
  document.head.appendChild(style);
}

describe('TASK-4897: OGV legend placement', () => {
  beforeEach(() => {
    document.head.innerHTML = '';
    document.body.innerHTML = '';
    loadGraphCss();
  });

  it('positions legend at the bottom-right away from the minimap', () => {
    const canvasArea = document.createElement('div');
    canvasArea.className = 'ogv-canvas-area';
    canvasArea.innerHTML = `
      <div class="ogv-navigator"></div>
      <div class="ogv-legend-overlay"></div>
    `;
    document.body.appendChild(canvasArea);

    const legendStyle = getComputedStyle(canvasArea.querySelector('.ogv-legend-overlay'));
    const navigatorStyle = getComputedStyle(canvasArea.querySelector('.ogv-navigator'));

    expect(legendStyle.right).toBe('16px');
    expect(legendStyle.left).toBe('auto');
    expect(legendStyle.bottom).toBe('16px');
    expect(navigatorStyle.left).toBe('12px');
    expect(['', 'auto']).toContain(navigatorStyle.right);
  });

  it('keeps zoom controls above the bottom-right legend', () => {
    const canvasArea = document.createElement('div');
    canvasArea.className = 'ogv-canvas-area';
    canvasArea.innerHTML = `
      <div class="ogv-zoom-controls"></div>
      <div class="ogv-legend-overlay"></div>
    `;
    document.body.appendChild(canvasArea);

    const zoomStyle = getComputedStyle(canvasArea.querySelector('.ogv-zoom-controls'));
    const legendStyle = getComputedStyle(canvasArea.querySelector('.ogv-legend-overlay'));

    expect(zoomStyle.right).toBe('12px');
    expect(Number.parseInt(zoomStyle.bottom, 10)).toBeGreaterThan(
      Number.parseInt(legendStyle.bottom, 10) + 120
    );
  });
});
