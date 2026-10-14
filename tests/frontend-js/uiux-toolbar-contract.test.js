// Executed scripts and linked snippets in jsdom, not browser/agent acceptance.
import { afterEach, describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { JSDOM } from 'jsdom';

const root = resolve(import.meta.dirname, '../..');
const read = path => readFileSync(resolve(root, path), 'utf8');
const entry = read('.github/skills/x-ipe-tool-uiux-reference/SKILL.md');
const snippets = read('.github/skills/x-ipe-tool-uiux-reference/references/code-snippets.md');
const primary = read('.github/skills/x-ipe-tool-uiux-reference/references/toolbar.min.js');
const modular = read('src/x_ipe/static/js/injected/xipe-toolbar-core.js') + '\n' +
  read('src/x_ipe/static/js/injected/xipe-toolbar-mockup.js');
const opened = [];

function snippet(name) {
  expect(entry).toContain(`references/code-snippets.md#${name}`);
  const section = snippets.split(`## ${name}\n`)[1]?.split('\n## ')[0];
  const code = section?.match(/```js\n([\s\S]*?)\n```/)?.[1];
  expect(code, `missing named snippet ${name}`).toBeTruthy();
  return code;
}

function runtime(script) {
  const dom = new JSDOM('<body><section id="area" style="color:rgb(1,2,3)">Area</section></body>', {
    url: 'https://example.com', runScripts: 'outside-only',
  });
  opened.push(dom);
  const w = dom.window;
  const intervals = [];
  // Capture actual polling callbacks; no real delays or network rendering.
  w.setInterval = (fn, ms) => { intervals.push({ fn, ms }); return intervals.length; };
  w.setTimeout = () => 0;
  w.eval(script);
  w.evaluate_script = (fn, argument) => fn(argument);
  return { w, intervals };
}

function mockupStep(w, step, withArea = true) {
  [...w.document.querySelectorAll('button')].find(b => b.textContent.includes('Copy Mockup')).click();
  if (withArea) w.__xipeRefData.areas.push({
    id: 'area-1', selector: '#area', snap_selector: '#area', snap_tag: 'SECTION',
    bounding_box: { x: 10, y: 20, width: 100, height: 50 }, instruction: '',
    html_css: { level: 'minimal', computed_styles: {} },
  });
  // Both mode containers remain in DOM; last Next belongs to mockup, not hidden theme.
  for (let i = 1; i < step; i++) {
    [...w.document.querySelectorAll('button')].filter(b => b.textContent === 'Next').at(-1).click();
  }
}

function assertReenabled(w) {
  expect(w.__xipeAnalyzeEnabled).toBe(true);
  expect(w.__xipeGenerateMockupEnabled).toBe(true);
  expect(w.__xipeRefReady).toBe(false);
  for (const button of w.document.querySelectorAll('[data-xipe-analyze], [data-xipe-generate]')) {
    expect(button.disabled).toBe(false);
    expect(button.classList.contains('xb-proc')).toBe(false);
    expect(button.classList.contains('xipe-btn-processing')).toBe(false);
  }
}

afterEach(() => { for (const dom of opened.splice(0)) dom.window.close(); });

describe.each([['primary skill IIFE', primary], ['modular source', modular]])('%s', (_label, script) => {
  it('initializes actual data/globals and ignores double injection', () => {
    const { w } = runtime(script);
    expect(w.__xipeToolbarReady).toBe(true);
    expect(w.__xipeRefData).toEqual({ mode: 'theme', colors: [], areas: [], design_tokens: null });
    expect(w.__xipeRefReady).toBe(false);
    expect(w.__xipeRefCommand).toBeNull();
    const data = w.__xipeRefData;
    const count = w.document.querySelectorAll('*').length;
    // Reinject only the guarded shell for modular source; mode extensions are separate.
    w.eval(_label === 'modular source' ? read('src/x_ipe/static/js/injected/xipe-toolbar-core.js') : script);
    expect(w.__xipeRefData).toBe(data);
    expect(w.document.querySelectorAll('*').length).toBe(count);
  });

  it.each([['analyze', 3], ['generate', 4]])('%s click signals only that action and disables during processing', (action, step) => {
    const { w } = runtime(script);
    mockupStep(w, step);
    const button = w.document.querySelector(`[data-xipe-${action}]`);
    expect(button).not.toBeNull();
    button.click();
    expect(w.__xipeRefData.action).toBe(action);
    expect(w.__xipeRefData.mode).toBe('mockup');
    expect(w.__xipeRefReady).toBe(true);
    expect(button.disabled).toBe(true);
    expect(w[action === 'analyze' ? '__xipeAnalyzeEnabled' : '__xipeGenerateMockupEnabled']).toBe(false);
    w.eval(snippet('re-enable-buttons'));
    assertReenabled(w);
    // Re-enabling does not silently invoke generation or change user action.
    expect(w.__xipeRefData.action).toBe(action);
  });

  it('500ms polling clears actual processing class after an analyze completion', () => {
    const { w, intervals } = runtime(script);
    mockupStep(w, 3);
    const button = w.document.querySelector('[data-xipe-analyze]');
    button.click();
    w.__xipeAnalyzeEnabled = true;
    const polls = intervals.filter(item => item.ms === 500);
    expect(polls).toHaveLength(1);
    polls[0].fn();
    expect(button.disabled).toBe(false);
    expect(button.classList.contains('xb-proc') || button.classList.contains('xipe-btn-processing')).toBe(false);
  });

  it('generate with no area stays disabled and sends no ready signal', () => {
    const { w } = runtime(script);
    mockupStep(w, 4, false);
    const button = w.document.querySelector('[data-xipe-generate]');
    expect(button.disabled).toBe(true);
    button.click();
    expect(w.__xipeRefReady).toBe(false);
    expect(w.__xipeRefData.action).toBeUndefined();
  });

  it('executes the real deep_capture command and clears it', () => {
    const { w, intervals } = runtime(script);
    mockupStep(w, 1);
    w.__xipeRefCommand = { action: 'deep_capture', target: 'area-1' };
    const polls = intervals.filter(item => item.ms === 1000);
    expect(polls).toHaveLength(1);
    polls[0].fn();
    expect(w.__xipeRefCommand).toBeNull();
    expect(w.__xipeRefReady).toBe(true);
    expect(w.__xipeRefData.areas[0].html_css.level).toBe('deep');
    expect(w.__xipeRefData.areas[0].html_css.outer_html).toContain('id="area"');
  });
});

it('executes discovery intersection/classification and excludes its declared container fixture', () => {
  const { w } = runtime(primary);
  const tags = ['img', 'svg', 'canvas', 'video', 'div'];
  for (const tag of tags) {
    const el = w.document.createElement(tag);
    el.id = `target-${tag}`;
    el.getBoundingClientRect = () => ({ x: 1, y: 1, left: 1, top: 1, right: 11, bottom: 11, width: 10, height: 10 });
    w.document.body.appendChild(el);
  }
  const toolbarChild = w.document.createElement('img');
  toolbarChild.id = 'excluded';
  toolbarChild.getBoundingClientRect = () => ({ left: 1, top: 1, right: 11, bottom: 11, width: 10, height: 10 });
  // The snippet's named exclusion target is a fixture, not the actual IIFE root.
  const declaredContainer = w.document.createElement('div');
  declaredContainer.id = 'xipe-toolbar-container';
  declaredContainer.appendChild(toolbarChild);
  w.document.body.appendChild(declaredContainer);
  const code = snippet('element-discovery');
  w.area = { bounding_box: { x: 0, y: 0, width: 20, height: 20 } };
  const discovered = w.eval(code);
  expect(discovered.map(el => el.type)).toEqual(['image', 'svg', 'canvas', 'video', 'dom']);
  expect(discovered.map(el => el.id)).not.toContain('excluded');
  w.area.bounding_box = { x: 11, y: 11, width: 20, height: 20 };
  expect(w.eval(code)).toEqual([]); // Boundary contact is not intersection.
});

it('exposes the immutable actual-root versus discovery-exclusion selector gap', () => {
  const { w } = runtime(primary);
  const toolbar = w.document.querySelector('.xipe-toolbar');
  expect(toolbar).not.toBeNull();
  expect(toolbar.closest('#xipe-toolbar-container')).toBeNull();
  toolbar.getBoundingClientRect = () => ({ x: 1, y: 1, left: 1, top: 1, right: 11, bottom: 11, width: 10, height: 10 });
  w.area = { bounding_box: { x: 0, y: 0, width: 20, height: 20 } };
  const discovered = w.eval(snippet('element-discovery'));
  // Detection is not a repaired production selector or full acceptance claim.
  expect(discovered.some(el => el.classes.includes('xipe-toolbar'))).toBe(true);
});

it.each(['disabled = false', "classList.remove('xb-proc', 'xipe-btn-processing')"])(
  'negative control catches missing re-enable effect: %s', effect => {
    const { w } = runtime(primary);
    mockupStep(w, 3);
    w.document.querySelector('[data-xipe-analyze]').click();
    const corrupt = snippet('re-enable-buttons').replaceAll(effect, effect === 'disabled = false' ? 'disabled = true' : 'classList.remove()');
    w.eval(corrupt);
    expect(() => assertReenabled(w)).toThrow();
  },
);