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

        it('should render purpose as textarea (not input)', async () => {
            const mgr = new globalThis.LearnPanelManager();
            global.fetch = vi.fn().mockResolvedValue({
                json: () => Promise.resolve({ success: true, sessions: [] })
            });
            const container = document.getElementById('content-body');
            await mgr.render(container);

            const textarea = container.querySelector('#learn-purpose-input');
            expect(textarea).not.toBeNull();
            expect(textarea.tagName).toBe('TEXTAREA');
        });

        it('should mark purpose as required (not optional)', async () => {
            const mgr = new globalThis.LearnPanelManager();
            global.fetch = vi.fn().mockResolvedValue({
                json: () => Promise.resolve({ success: true, sessions: [] })
            });
            const container = document.getElementById('content-body');
            await mgr.render(container);

            const label = container.innerHTML;
            expect(label).not.toContain('(optional)');
        });

        it('should disable track button when purpose is empty', async () => {
            const mgr = new globalThis.LearnPanelManager();
            global.fetch = vi.fn().mockResolvedValue({
                json: () => Promise.resolve({ success: true, sessions: [] })
            });
            const container = document.getElementById('content-body');
            await mgr.render(container);

            // Set valid URL but leave purpose empty
            const urlInput = container.querySelector('#learn-url-input');
            urlInput.value = 'https://example.com';
            urlInput.dispatchEvent(new Event('input'));

            const btn = container.querySelector('#learn-track-btn');
            expect(btn.disabled).toBe(true);
        });

        it('should show word count and enforce 200-word limit', async () => {
            const mgr = new globalThis.LearnPanelManager();
            global.fetch = vi.fn().mockResolvedValue({
                json: () => Promise.resolve({ success: true, sessions: [] })
            });
            const container = document.getElementById('content-body');
            await mgr.render(container);

            const wordCounter = container.querySelector('#learn-purpose-word-count');
            expect(wordCounter).not.toBeNull();
            expect(wordCounter.textContent).toContain('0');
            expect(wordCounter.textContent).toContain('200');
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

    describe('Track Behavior Button', () => {
        it('should send command to terminalManager when clicked', async () => {
            const mgr = new globalThis.LearnPanelManager();
            global.fetch = vi.fn().mockResolvedValue({
                json: () => Promise.resolve({ success: true, sessions: [] })
            });

            const container = document.getElementById('content-body');
            await mgr.render(container);

            // Set up valid URL and purpose
            const urlInput = container.querySelector('#learn-url-input');
            const purposeInput = container.querySelector('#learn-purpose-input');
            urlInput.value = 'https://example.com';
            urlInput.dispatchEvent(new Event('input'));
            purposeInput.value = 'Test checkout flow';
            purposeInput.dispatchEvent(new Event('input'));

            // Mock terminalManager
            globalThis.window.terminalManager = {
                sendCopilotPromptCommandNoEnter: vi.fn()
            };
            globalThis.window.terminalPanel = {
                expand: vi.fn()
            };

            const btn = container.querySelector('#learn-track-btn');
            btn.click();

            expect(globalThis.window.terminalManager.sendCopilotPromptCommandNoEnter).toHaveBeenCalledTimes(1);
            const calledWith = globalThis.window.terminalManager.sendCopilotPromptCommandNoEnter.mock.calls[0][0];
            expect(calledWith).toContain('https://example.com');
            expect(calledWith).toContain('Test checkout flow');

            // Cleanup
            delete globalThis.window.terminalManager;
            delete globalThis.window.terminalPanel;
        });

        it('should expand terminal panel before sending command', async () => {
            const mgr = new globalThis.LearnPanelManager();
            global.fetch = vi.fn().mockResolvedValue({
                json: () => Promise.resolve({ success: true, sessions: [] })
            });

            const container = document.getElementById('content-body');
            await mgr.render(container);

            const urlInput = container.querySelector('#learn-url-input');
            const purposeInput = container.querySelector('#learn-purpose-input');
            urlInput.value = 'https://example.com';
            urlInput.dispatchEvent(new Event('input'));
            purposeInput.value = 'Test flow';
            purposeInput.dispatchEvent(new Event('input'));

            globalThis.window.terminalManager = {
                sendCopilotPromptCommandNoEnter: vi.fn()
            };
            globalThis.window.terminalPanel = {
                expand: vi.fn()
            };

            const btn = container.querySelector('#learn-track-btn');
            btn.click();

            expect(globalThis.window.terminalPanel.expand).toHaveBeenCalledTimes(1);

            delete globalThis.window.terminalManager;
            delete globalThis.window.terminalPanel;
        });
    });
});
