/**
 * TASK-985: Test kb:// URL protocol support in UIUX feedback simulator browser
 *
 * Bug: Simulator browser shows blank viewport when previewing KB content.
 * Fix: Add kb:// URL protocol support (like idea://) to fetch from /api/kb/files/{path}/raw.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import vm from 'vm';

const PROJECT_ROOT = resolve(import.meta.dirname, '..', '..');
const JS_ROOT = resolve(PROJECT_ROOT, 'src/x_ipe/static/js');

let _loaded = false;
function ensureLoaded() {
    if (_loaded) return typeof globalThis.UIUXFeedbackManager !== 'undefined';
    try {
        let code = readFileSync(resolve(JS_ROOT, 'uiux-feedback.js'), 'utf-8');
        code += '\nglobalThis.UIUXFeedbackManager = UIUXFeedbackManager;';
        vm.runInThisContext(code);
        _loaded = true;
    } catch { /* TDD: file may not have kb:// support yet */ }
    return typeof globalThis.UIUXFeedbackManager !== 'undefined';
}

function createManager() {
    document.body.innerHTML = `
        <input type="text" id="url-input" />
        <button id="go-btn">Go</button>
        <div id="loading-overlay" style="display:none"></div>
        <div id="error-overlay" style="display:none">
            <span id="error-message"></span>
        </div>
        <div id="empty-state"></div>
        <iframe id="browser-viewport"></iframe>
        <span id="status-text"></span>
    `;

    globalThis.fetch = vi.fn();
    globalThis.marked = { parse: (md) => `<p>${md}</p>` };

    const manager = new globalThis.UIUXFeedbackManager();
    manager.elements = {
        urlInput: document.getElementById('url-input'),
        goBtn: document.getElementById('go-btn'),
        loadingOverlay: document.getElementById('loading-overlay'),
        errorOverlay: document.getElementById('error-overlay'),
        errorMessage: document.getElementById('error-message'),
        emptyState: document.getElementById('empty-state'),
        iframe: document.getElementById('browser-viewport'),
        statusText: document.getElementById('status-text'),
    };

    return manager;
}

describe('TASK-985: kb:// URL protocol support', () => {

    beforeEach(() => {
        if (!ensureLoaded()) return;
    });

    // ─── validateUrl ────────────────────────────────────────

    describe('validateUrl()', () => {
        let manager;

        beforeEach(() => {
            if (!ensureLoaded()) return;
            manager = createManager();
        });

        it('should accept kb:// URLs as valid', () => {
            const result = manager.validateUrl('kb://guides/getting-started.md');
            expect(result.valid).toBe(true);
            expect(result.url).toBe('kb://guides/getting-started.md');
        });

        it('should mark kb:// URLs with isKb flag', () => {
            const result = manager.validateUrl('kb://folder/file.md');
            expect(result.isKb).toBe(true);
        });

        it('should not mark kb:// URLs as idea', () => {
            const result = manager.validateUrl('kb://folder/file.md');
            expect(result.isIdea).toBeFalsy();
        });

        it('should handle kb:// URL with nested path', () => {
            const result = manager.validateUrl('kb://deep/nested/path/file.txt');
            expect(result.valid).toBe(true);
            expect(result.isKb).toBe(true);
        });

        it('should handle kb:// URL with just filename', () => {
            const result = manager.validateUrl('kb://readme.md');
            expect(result.valid).toBe(true);
            expect(result.isKb).toBe(true);
        });

        it('should still accept idea:// URLs', () => {
            const result = manager.validateUrl('idea://folder/file.html');
            expect(result.valid).toBe(true);
            expect(result.isIdea).toBe(true);
        });

        it('should still accept localhost URLs', () => {
            const result = manager.validateUrl('http://localhost:3000');
            expect(result.valid).toBe(true);
        });
    });

    // ─── _loadKbUrl ─────────────────────────────────────────

    describe('_loadKbUrl()', () => {
        let manager;

        beforeEach(() => {
            if (!ensureLoaded()) return;
            manager = createManager();
        });

        it('should exist as a method', () => {
            expect(typeof manager._loadKbUrl).toBe('function');
        });

        it('should fetch from /api/kb/files/{path}/raw endpoint', async () => {
            globalThis.fetch.mockResolvedValueOnce({
                ok: true,
                headers: new Headers({ 'Content-Type': 'text/plain' }),
                text: async () => '# Hello KB',
            });

            await manager._loadKbUrl('kb://guides/hello.md');

            expect(globalThis.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/api/kb/files/')
            );
            expect(globalThis.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/raw')
            );
        });

        it('should render markdown content as HTML in iframe', async () => {
            globalThis.fetch.mockResolvedValueOnce({
                ok: true,
                headers: new Headers({ 'Content-Type': 'text/markdown' }),
                text: async () => '# Hello World',
            });

            await manager._loadKbUrl('kb://guides/hello.md');

            const srcdoc = manager.elements.iframe.srcdoc;
            expect(srcdoc).toBeTruthy();
            expect(srcdoc).toContain('Hello World');
        });

        it('should render HTML files directly in iframe', async () => {
            const htmlContent = '<html><body><h1>Test</h1></body></html>';
            globalThis.fetch.mockResolvedValueOnce({
                ok: true,
                headers: new Headers({ 'Content-Type': 'text/html' }),
                text: async () => htmlContent,
            });

            await manager._loadKbUrl('kb://pages/test.html');

            const srcdoc = manager.elements.iframe.srcdoc;
            expect(srcdoc).toContain('Test');
        });

        it('should render images using img tag with API URL', async () => {
            await manager._loadKbUrl('kb://images/logo.png');

            const srcdoc = manager.elements.iframe.srcdoc;
            expect(srcdoc).toBeTruthy();
            expect(srcdoc).toContain('<img');
            expect(srcdoc).toContain('/api/kb/files/');
            expect(srcdoc).toContain('logo.png');
        });

        it('should render code files with syntax highlighting wrapper', async () => {
            globalThis.fetch.mockResolvedValueOnce({
                ok: true,
                headers: new Headers({ 'Content-Type': 'text/plain' }),
                text: async () => 'def hello():\n    print("world")',
            });

            await manager._loadKbUrl('kb://scripts/hello.py');

            const srcdoc = manager.elements.iframe.srcdoc;
            expect(srcdoc).toBeTruthy();
            expect(srcdoc).toContain('def hello()');
        });

        it('should show error for failed fetch', async () => {
            globalThis.fetch.mockResolvedValueOnce({
                ok: false,
                status: 404,
            });

            await manager._loadKbUrl('kb://missing/file.md');

            expect(manager.state.error).toBeTruthy();
        });

        it('should show error for 413 (file too large)', async () => {
            globalThis.fetch.mockResolvedValueOnce({
                ok: false,
                status: 413,
            });

            await manager._loadKbUrl('kb://big/file.docx');

            expect(manager.state.error).toContain('too large');
        });

        it('should update currentUrl after successful load', async () => {
            globalThis.fetch.mockResolvedValueOnce({
                ok: true,
                headers: new Headers({ 'Content-Type': 'text/plain' }),
                text: async () => 'content',
            });

            await manager._loadKbUrl('kb://test/file.txt');

            expect(manager.state.currentUrl).toBe('kb://test/file.txt');
        });

        it('should update status after successful load', async () => {
            globalThis.fetch.mockResolvedValueOnce({
                ok: true,
                headers: new Headers({ 'Content-Type': 'text/plain' }),
                text: async () => 'content',
            });

            await manager._loadKbUrl('kb://test/file.txt');

            expect(manager.elements.statusText.textContent).toContain('kb://test/file.txt');
        });

        it('should handle converted DOCX/MSG content (X-Converted header)', async () => {
            globalThis.fetch.mockResolvedValueOnce({
                ok: true,
                headers: new Headers({
                    'Content-Type': 'text/html',
                    'X-Converted': 'true',
                }),
                text: async () => '<h1>Converted Document</h1><p>Content</p>',
            });

            await manager._loadKbUrl('kb://docs/report.docx');

            const srcdoc = manager.elements.iframe.srcdoc;
            expect(srcdoc).toContain('Converted Document');
        });
    });

    // ─── loadUrl integration ────────────────────────────────

    describe('loadUrl() kb:// routing', () => {
        let manager;

        beforeEach(() => {
            if (!ensureLoaded()) return;
            manager = createManager();
        });

        it('should route kb:// URLs to _loadKbUrl', async () => {
            const spy = vi.spyOn(manager, '_loadKbUrl').mockResolvedValue();
            manager.elements.urlInput.value = 'kb://folder/file.md';

            await manager.loadUrl();

            expect(spy).toHaveBeenCalledWith('kb://folder/file.md');
        });

        it('should not route kb:// URLs to proxy', async () => {
            vi.spyOn(manager, '_loadKbUrl').mockResolvedValue();
            manager.elements.urlInput.value = 'kb://folder/file.md';

            await manager.loadUrl();

            expect(globalThis.fetch).not.toHaveBeenCalledWith(
                expect.stringContaining('/api/proxy')
            );
        });
    });
});
