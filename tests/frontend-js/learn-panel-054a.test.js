/**
 * FEATURE-054-A: LearnPanelManager Tests
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { loadFeatureScript, mockFetch } from './helpers.js';

let _loaded = false;
function ensureLoaded() {
    if (!_loaded) {
        loadFeatureScript('learn-panel.js');
        _loaded = true;
    }
    return typeof globalThis.LearnPanelManager !== 'undefined';
}

describe('LearnPanelManager', () => {
    beforeEach(() => {
        ensureLoaded();
        document.body.innerHTML = '<div id="content-body"></div>';
        globalThis.fetch = vi.fn();
    });

    describe('URL Validation', () => {
        it('should accept valid https URL', () => {
            const mgr = new globalThis.LearnPanelManager();
            expect(mgr._validateURL('https://example.com')).toBe(true);
        });

        it('should accept valid http URL', () => {
            const mgr = new globalThis.LearnPanelManager();
            expect(mgr._validateURL('http://example.com/path')).toBe(true);
        });

        it('should reject empty string', () => {
            const mgr = new globalThis.LearnPanelManager();
            expect(mgr._validateURL('')).toBe(false);
        });

        it('should reject null', () => {
            const mgr = new globalThis.LearnPanelManager();
            expect(mgr._validateURL(null)).toBe(false);
        });

        it('should reject invalid protocol', () => {
            const mgr = new globalThis.LearnPanelManager();
            expect(mgr._validateURL('ftp://example.com')).toBe(false);
        });

        it('should reject malformed URL', () => {
            const mgr = new globalThis.LearnPanelManager();
            expect(mgr._validateURL('not-a-url')).toBe(false);
        });

        it('should reject whitespace-only', () => {
            const mgr = new globalThis.LearnPanelManager();
            expect(mgr._validateURL('   ')).toBe(false);
        });
    });

    describe('Duration Formatting', () => {
        it('should format seconds', () => {
            const mgr = new globalThis.LearnPanelManager();
            expect(mgr._formatDuration(5000)).toBe('5s');
        });

        it('should format minutes and seconds', () => {
            const mgr = new globalThis.LearnPanelManager();
            expect(mgr._formatDuration(125000)).toBe('2m 5s');
        });

        it('should format hours and minutes', () => {
            const mgr = new globalThis.LearnPanelManager();
            expect(mgr._formatDuration(3720000)).toBe('1h 2m');
        });

        it('should return empty for zero', () => {
            const mgr = new globalThis.LearnPanelManager();
            expect(mgr._formatDuration(0)).toBe('');
        });

        it('should return empty for negative', () => {
            const mgr = new globalThis.LearnPanelManager();
            expect(mgr._formatDuration(-1000)).toBe('');
        });
    });

    describe('HTML Escaping', () => {
        it('should escape HTML entities', () => {
            const mgr = new globalThis.LearnPanelManager();
            expect(mgr._escapeHtml('<script>alert("xss")</script>')).toContain('&lt;');
            expect(mgr._escapeHtml('<script>alert("xss")</script>')).not.toContain('<script>');
        });

        it('should handle empty string', () => {
            const mgr = new globalThis.LearnPanelManager();
            expect(mgr._escapeHtml('')).toBe('');
        });
    });

    describe('Render', () => {
        it('should render template into container', async () => {
            const mgr = new globalThis.LearnPanelManager();
            global.fetch = vi.fn().mockResolvedValue({
                json: () => Promise.resolve({ success: true, sessions: [] })
            });

            const container = document.getElementById('content-body');
            await mgr.render(container);

            expect(container.querySelector('.learn-panel')).not.toBeNull();
            expect(container.querySelector('#learn-url-input')).not.toBeNull();
            expect(container.querySelector('#learn-track-btn')).not.toBeNull();
        });

        it('should disable track button initially', async () => {
            const mgr = new globalThis.LearnPanelManager();
            global.fetch = vi.fn().mockResolvedValue({
                json: () => Promise.resolve({ success: true, sessions: [] })
            });

            const container = document.getElementById('content-body');
            await mgr.render(container);

            const btn = container.querySelector('#learn-track-btn');
            expect(btn.disabled).toBe(true);
        });
    });

    describe('Session Card Rendering', () => {
        it('should render completed session card', () => {
            const mgr = new globalThis.LearnPanelManager();
            const html = mgr._renderSessionCard({
                sessionId: 'test-123',
                domain: 'example.com',
                purpose: 'Test purpose',
                status: 'completed',
                startedAt: '2026-04-02T10:00:00Z',
                stoppedAt: '2026-04-02T10:30:00Z',
                eventCount: 142,
                pageCount: 5,
                fileName: 'behavior-recording-test-123.json'
            });

            expect(html).toContain('example.com');
            expect(html).toContain('142 events');
            expect(html).toContain('5 pages');
            expect(html).toContain('Completed');
            expect(html).toContain('View Recording');
        });

        it('should render recording session with pulsing badge', () => {
            const mgr = new globalThis.LearnPanelManager();
            const html = mgr._renderSessionCard({
                sessionId: 'test-456',
                domain: 'example.com',
                purpose: '',
                status: 'recording',
                startedAt: '2026-04-02T10:00:00Z',
                stoppedAt: null,
                eventCount: 42,
                pageCount: 2,
                fileName: ''
            });

            expect(html).toContain('Recording');
            expect(html).not.toContain('View Recording');
        });
    });
});
