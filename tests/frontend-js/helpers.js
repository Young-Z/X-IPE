/**
 * Test helper: loads browser-global JS files into the Vitest jsdom context.
 * Since the project uses plain <script> tags (no ES modules), this helper
 * reads the file and executes it via vm.runInThisContext so class/const
 * declarations become available, then exposes them on globalThis.
 */
import { readFileSync } from 'fs';
import { resolve } from 'path';
import vm from 'vm';

const PROJECT_ROOT = resolve(import.meta.dirname, '..', '..');
const JS_FEATURES = resolve(PROJECT_ROOT, 'src/x_ipe/static/js/features');

/**
 * Load a JS feature file into the global scope.
 * @param {string} filename - e.g. 'workflow-stage.js'
 * @param {object} [options]
 * @param {string} [options.extractBefore] - Only load code before this marker string.
 * @param {string[]} [options.expose] - Names to assign to globalThis after execution.
 */
export function loadFeatureScript(filename, options = {}) {
  const filepath = resolve(JS_FEATURES, filename);
  let code = readFileSync(filepath, 'utf-8');
  if (options.extractBefore) {
    const idx = code.indexOf(options.extractBefore);
    if (idx > 0) code = code.substring(0, idx);
  }
  // Auto-detect top-level class/const/function declarations to expose
  const expose = options.expose || [];
  const classMatches = code.matchAll(/^class\s+(\w+)/gm);
  for (const m of classMatches) expose.push(m[1]);
  const constMatches = code.matchAll(/^const\s+(\w+)/gm);
  for (const m of constMatches) expose.push(m[1]);

  // Append assignments to globalThis
  const assignments = [...new Set(expose)]
    .map(name => `globalThis.${name} = ${name};`)
    .join('\n');
  code += '\n' + assignments;

  vm.runInThisContext(code);
}

/**
 * Mock the bootstrap global (Modal, etc.) for tests that need it.
 */
export function mockBootstrap() {
  const mockModalInstance = {
    show: vi.fn(),
    hide: vi.fn(),
    dispose: vi.fn(),
  };

  globalThis.bootstrap = {
    Modal: vi.fn(() => mockModalInstance),
    _mockInstance: mockModalInstance,
  };

  return globalThis.bootstrap;
}

/**
 * Mock fetch for API tests.
 */
export function mockFetch(responses = {}) {
  const original = globalThis.fetch;
  globalThis.fetch = vi.fn(async (url, options) => {
    const key = typeof url === 'string' ? url.split('?')[0] : url;
    const handler = responses[key];
    if (handler) return handler(url, options);
    return { ok: true, json: async () => ({}), text: async () => '' };
  });
  return () => { globalThis.fetch = original; };
}
