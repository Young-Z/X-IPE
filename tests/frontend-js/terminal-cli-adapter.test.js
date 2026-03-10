/**
 * TASK-673 / TASK-819: Terminal CLI Adapter
 *
 * Tests that _buildCopilotCmd, _insertCopilotCommand, and the copilot-cmd-btn
 * button title all use the active CLI adapter config instead of hardcoding 'copilot'.
 */
import { describe, it, expect, beforeAll, beforeEach, vi } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import vm from 'vm';

const JS_PATH = resolve(import.meta.dirname, '../../src/x_ipe/static/js/terminal.js');

beforeAll(() => {
  // Provide minimal DOM stubs required by TerminalManager + TerminalPanel constructors
  document.body.innerHTML = `
    <div id="terminal-content"></div>
    <div id="terminal-status-indicator"></div>
    <div id="terminal-status-text"></div>
    <div id="terminal-panel">
      <div id="terminal-header">
        <button id="terminal-toggle"></button>
        <button id="copilot-cmd-btn" title="Insert Copilot command"><i class="bi bi-robot"></i></button>
      </div>
      <div id="terminal-resize-handle"></div>
    </div>
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
            run_args: '--allow-all-tools --allow-all-paths',
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

  it('exposes _cliAdapterReady promise', () => {
    expect(tm._cliAdapterReady).toBeInstanceOf(Promise);
  });
});

describe('TerminalPanel — copilot-cmd-btn adapts to active CLI', () => {
  function stubFetchFor(adapterName, displayName, command, runArgs = '') {
    globalThis.fetch = vi.fn(async (url) => {
      if (url === '/api/config/cli-adapter') {
        return {
          ok: true,
          json: async () => ({
            success: true,
            adapter_name: adapterName,
            display_name: displayName,
            command,
            run_args: runArgs,
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
  }

  it('updates button title to reflect opencode adapter', async () => {
    stubFetchFor('opencode', 'OpenCode CLI', 'opencode');
    const tm = new window.TerminalManager('terminal-content');
    const panel = new window.TerminalPanel(tm);
    await tm._cliAdapterReady;
    // Allow microtask to settle
    await new Promise(r => setTimeout(r, 50));
    expect(panel.copilotCmdBtn.title).toContain('OpenCode');
  });

  it('updates button title to reflect copilot adapter', async () => {
    stubFetchFor('copilot', 'GitHub Copilot CLI', 'copilot', '--allow-all-tools --allow-all-paths');
    const tm = new window.TerminalManager('terminal-content');
    const panel = new window.TerminalPanel(tm);
    await tm._cliAdapterReady;
    await new Promise(r => setTimeout(r, 50));
    expect(panel.copilotCmdBtn.title).toContain('Copilot');
  });

  it('updates button title to reflect claude-code adapter', async () => {
    stubFetchFor('claude-code', 'Claude Code CLI', 'claude');
    const tm = new window.TerminalManager('terminal-content');
    const panel = new window.TerminalPanel(tm);
    await tm._cliAdapterReady;
    await new Promise(r => setTimeout(r, 50));
    expect(panel.copilotCmdBtn.title).toContain('Claude');
  });

  it('keeps default title if adapter fails to load', async () => {
    globalThis.fetch = vi.fn(async () => ({ ok: false }));
    const btn = document.getElementById('copilot-cmd-btn');
    btn.title = 'Insert Copilot command';
    const tm = new window.TerminalManager('terminal-content');
    const panel = new window.TerminalPanel(tm);
    await tm._cliAdapterReady;
    await new Promise(r => setTimeout(r, 50));
    expect(panel.copilotCmdBtn.title).toBe('Insert Copilot command');
  });

  it('_insertCopilotCommand uses adapter command + run_args', async () => {
    stubFetchFor('copilot', 'GitHub Copilot CLI', 'copilot', '--allow-all-tools --allow-all-paths');
    const tm = new window.TerminalManager('terminal-content');
    const panel = new window.TerminalPanel(tm);
    await tm._cliAdapterReady;
    await new Promise(r => setTimeout(r, 50));
    // Mock _sendWithTypingEffect to capture the command
    let captured = null;
    tm._sendWithTypingEffect = (_key, cmd) => { captured = cmd; };
    // Need an active session
    tm.sessions = new Map([['s1', { key: 's1', socket: { connected: true } }]]);
    tm.activeSessionKey = 's1';
    tm._getActiveSession = () => tm.sessions.get('s1');
    panel._insertCopilotCommand();
    expect(captured).toBe('copilot --allow-all-tools --allow-all-paths');
  });
});
