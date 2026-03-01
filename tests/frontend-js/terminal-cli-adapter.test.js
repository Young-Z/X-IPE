/**
 * TASK-673: Terminal CLI Adapter — _buildCopilotCmd uses active CLI adapter
 *
 * Tests that _buildCopilotCmd and _insertCopilotCommand use the CLI adapter
 * config instead of hardcoding 'copilot'.
 */
import { describe, it, expect, beforeAll, beforeEach, vi } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import vm from 'vm';

const JS_PATH = resolve(import.meta.dirname, '../../src/x_ipe/static/js/terminal.js');

beforeAll(() => {
  // Provide minimal DOM stubs required by TerminalManager constructor
  document.body.innerHTML = `
    <div id="terminal-content"></div>
    <div id="terminal-status-indicator"></div>
    <div id="terminal-status-text"></div>
  `;

  // Stub ResizeObserver
  globalThis.ResizeObserver = class { observe() {} disconnect() {} };

  // Stub fetch to return CLI adapter config
  globalThis.fetch = vi.fn(async (url) => {
    if (url === '/api/config/cli-adapter') {
      return {
        ok: true,
        json: async () => ({
          success: true,
          adapter_name: 'opencode',
          display_name: 'OpenCode CLI',
          command: 'opencode',
          run_args: '',
          inline_prompt_flag: '--prompt',
          prompt_format: '{command} {inline_prompt_flag} "{escaped_prompt}"',
        }),
      };
    }
    if (url === '/api/config') {
      return { ok: true, json: async () => ({ auto_execute_prompt: false }) };
    }
    return { ok: false };
  });

  const code = readFileSync(JS_PATH, 'utf-8');
  vm.runInThisContext(code);
});

describe('TerminalManager — _buildCopilotCmd uses CLI adapter', () => {
  let tm;

  beforeEach(async () => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn(async (url) => {
      if (url === '/api/config/cli-adapter') {
        return {
          ok: true,
          json: async () => ({
            success: true,
            adapter_name: 'opencode',
            display_name: 'OpenCode CLI',
            command: 'opencode',
            run_args: '',
            inline_prompt_flag: '--prompt',
            prompt_format: '{command} {inline_prompt_flag} "{escaped_prompt}"',
          }),
        };
      }
      if (url === '/api/config') {
        return { ok: true, json: async () => ({ auto_execute_prompt: false }) };
      }
      return { ok: false };
    });

    tm = new window.TerminalManager('terminal-content');
    // Wait for async config loading
    await new Promise(r => setTimeout(r, 50));
  });

  it('fetches CLI adapter config on construction', () => {
    const calls = globalThis.fetch.mock.calls.map(c => c[0]);
    expect(calls).toContain('/api/config/cli-adapter');
  });

  it('stores CLI adapter config', () => {
    expect(tm._cliAdapter).toBeDefined();
    expect(tm._cliAdapter.command).toBe('opencode');
  });

  it('builds command using adapter prompt_format', () => {
    const cmd = tm._buildCopilotCmd('do something');
    expect(cmd).toContain('opencode');
    expect(cmd).toContain('--prompt');
    expect(cmd).toContain('do something');
    expect(cmd).not.toContain('copilot');
  });

  it('escapes double quotes in prompt', () => {
    const cmd = tm._buildCopilotCmd('say "hello"');
    expect(cmd).toContain('\\"hello\\"');
  });

  it('falls back to copilot when adapter not loaded', () => {
    tm._cliAdapter = null;
    const cmd = tm._buildCopilotCmd('test prompt');
    expect(cmd).toContain('copilot');
    expect(cmd).toContain('test prompt');
  });

  it('uses copilot adapter format when copilot is active', async () => {
    globalThis.fetch = vi.fn(async (url) => {
      if (url === '/api/config/cli-adapter') {
        return {
          ok: true,
          json: async () => ({
            success: true,
            command: 'copilot',
            run_args: '--allow-all-tools',
            inline_prompt_flag: '-i',
            prompt_format: '{command} {run_args} {inline_prompt_flag} "{escaped_prompt}"',
          }),
        };
      }
      if (url === '/api/config') {
        return { ok: true, json: async () => ({}) };
      }
      return { ok: false };
    });

    const tm2 = new window.TerminalManager('terminal-content');
    await new Promise(r => setTimeout(r, 50));

    const cmd = tm2._buildCopilotCmd('hello world');
    expect(cmd).toContain('copilot');
    expect(cmd).toContain('--allow-all-tools');
    expect(cmd).toContain('-i');
    expect(cmd).toContain('hello world');
  });
});
