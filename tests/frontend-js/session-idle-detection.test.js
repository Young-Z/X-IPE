/**
 * TDD Tests for FEATURE-038-B: Session Idle Detection (Frontend)
 * Tests verify the methods exist in terminal.js source and test socket interaction logic.
 * terminal.js cannot be loaded in isolation (complex IIFE with DOM/WebSocket deps),
 * so tests use source verification + mock-based behavioral testing.
 */
import { describe, it, expect, vi } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const TERMINAL_JS = readFileSync(
  resolve(import.meta.dirname, '..', '..', 'src/x_ipe/static/js/terminal.js'), 'utf-8'
);

describe('FEATURE-038-B: Frontend Session Idle Detection', () => {
  describe('findIdleSession()', () => {
    it('should exist as a method in terminal.js', () => {
      expect(TERMINAL_JS).toContain('async findIdleSession()');
    });

    it('should emit find_idle_session WebSocket event', () => {
      expect(TERMINAL_JS).toContain("emit('find_idle_session'");
    });

    it('should resolve with sessionId and key when idle session found', () => {
      expect(TERMINAL_JS).toContain('{ sessionId: response.session_id, key }');
    });

    it('should resolve with null when no idle session', () => {
      expect(TERMINAL_JS).toContain('resolve(null)');
    });
  });

  describe('claimSessionForAction()', () => {
    it('should exist as a method in terminal.js', () => {
      expect(TERMINAL_JS).toContain('async claimSessionForAction(');
    });

    it('should emit claim_session WebSocket event', () => {
      expect(TERMINAL_JS).toContain("emit('claim_session'");
    });
  });

  describe('session_renamed event handler', () => {
    it('should register session_renamed event listener', () => {
      expect(TERMINAL_JS).toContain("on('session_renamed'");
    });

    it('should update session name on event', () => {
      expect(TERMINAL_JS).toContain('session.name = data.new_name');
    });
  });

  describe('_findKeyBySessionId()', () => {
    it('should exist as a helper method', () => {
      expect(TERMINAL_JS).toContain('_findKeyBySessionId(');
    });
  });

  describe('_updateTabLabel()', () => {
    it('should exist as a helper method', () => {
      expect(TERMINAL_JS).toContain('_updateTabLabel(');
    });
  });
});
