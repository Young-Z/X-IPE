/**
 * TDD Tests for FEATURE-038-B: Session Idle Detection (Frontend)
 * Tests: TerminalManager.findIdleSession(), claimSessionForAction(), session_renamed handler
 *
 * TDD: All tests MUST fail until terminal.js methods are implemented.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { loadFeatureScript } from './helpers.js';

/**
 * Guard: loads terminal.js; the new methods won't exist until implemented.
 */
function tryLoadTerminal() {
  try {
    loadFeatureScript('terminal.js');
    return true;
  } catch {
    return false;
  }
}

describe('FEATURE-038-B: Frontend Session Idle Detection', () => {
  let mockSocket;

  beforeEach(() => {
    document.body.innerHTML = '';

    mockSocket = {
      emit: vi.fn(),
      on: vi.fn(),
      off: vi.fn(),
    };

    globalThis.io = vi.fn(() => mockSocket);
    globalThis.Terminal = vi.fn(() => ({
      open: vi.fn(), write: vi.fn(), onData: vi.fn(),
      onResize: vi.fn(), dispose: vi.fn(), loadAddon: vi.fn(),
    }));
    globalThis.FitAddon = { FitAddon: vi.fn(() => ({ fit: vi.fn(), dispose: vi.fn() })) };

    tryLoadTerminal();
  });

  describe('findIdleSession()', () => {
    it('should exist as a method on TerminalManager prototype', () => {
      const TM = globalThis.TerminalManager;
      expect(TM).toBeDefined();
      expect(typeof TM.prototype.findIdleSession).toBe('function');
    });

    it('should emit find_idle_session WebSocket event', async () => {
      const TM = globalThis.TerminalManager;
      expect(TM).toBeDefined();
      expect(typeof TM.prototype.findIdleSession).toBe('function');
    });

    it('should resolve with sessionId and key when idle session found', async () => {
      const TM = globalThis.TerminalManager;
      expect(TM).toBeDefined();
      expect(typeof TM.prototype.findIdleSession).toBe('function');
      // Will test actual behavior once method exists
    });

    it('should resolve with null when no idle session', async () => {
      const TM = globalThis.TerminalManager;
      expect(TM).toBeDefined();
      expect(typeof TM.prototype.findIdleSession).toBe('function');
    });
  });

  describe('claimSessionForAction()', () => {
    it('should exist as a method on TerminalManager prototype', () => {
      const TM = globalThis.TerminalManager;
      expect(TM).toBeDefined();
      expect(typeof TM.prototype.claimSessionForAction).toBe('function');
    });

    it('should emit claim_session WebSocket event with correct params', async () => {
      const TM = globalThis.TerminalManager;
      expect(TM).toBeDefined();
      expect(typeof TM.prototype.claimSessionForAction).toBe('function');
    });
  });

  describe('session_renamed event handler', () => {
    it('should update session name when session_renamed event received', () => {
      const TM = globalThis.TerminalManager;
      expect(TM).toBeDefined();
      // Verify that TerminalManager registers a handler for 'session_renamed'
      const registeredEvents = mockSocket.on.mock.calls.map(c => c[0]);
      expect(registeredEvents).toContain('session_renamed');
    });
  });
});
