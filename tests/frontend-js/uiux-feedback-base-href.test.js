/**
 * TASK-985: Test that renderContent() injects <base href> into srcdoc HTML
 * to fix relative URL resolution when iframe origin is about:blank.
 *
 * Root cause: simulator uses iframe.srcdoc which sets origin to about:blank,
 * breaking relative API calls like fetch('/api/kb/files/.../raw').
 * Fix: inject <base href="${origin}/"> so relative URLs resolve correctly.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import vm from 'vm';
import fs from 'fs';
import path from 'path';

// Load the UIUXFeedbackManager source
const srcPath = path.resolve(__dirname, '../../src/x_ipe/static/js/uiux-feedback.js');
const srcCode = fs.readFileSync(srcPath, 'utf-8');

// Stub browser globals before running the script
globalThis.marked = { parse: (md) => `<p>${md}</p>` };
globalThis.DOMParser = class {
    parseFromString(str) { return { body: { textContent: str } }; }
};

// Compile and run in this context so UIUXFeedbackManager is available
vm.runInThisContext(srcCode, { filename: srcPath });

describe('TASK-985: renderContent() base href injection', () => {
    let manager;
    let mockIframe;

    beforeEach(() => {
        // Mock window.location.origin
        if (!globalThis.window) globalThis.window = {};
        globalThis.window.location = { origin: 'http://127.0.0.1:5858' };

        mockIframe = { srcdoc: '' };
        manager = new UIUXFeedbackManager();
        manager.elements = {
            iframe: mockIframe,
            emptyState: { style: {} },
        };
    });

    it('should inject <base href> into HTML with <head> tag', () => {
        const html = '<!DOCTYPE html><html><head><title>Test</title></head><body><p>Hello</p></body></html>';
        manager.renderContent(html);
        expect(mockIframe.srcdoc).toContain('<base href="http://127.0.0.1:5858/">');
        expect(mockIframe.srcdoc).toContain('<head><base href="http://127.0.0.1:5858/"><title>Test</title>');
    });

    it('should inject <base href> into HTML with <html> but no <head>', () => {
        const html = '<html><body><p>Hello</p></body></html>';
        manager.renderContent(html);
        expect(mockIframe.srcdoc).toContain('<base href="http://127.0.0.1:5858/">');
        expect(mockIframe.srcdoc).toContain('<head><base href="http://127.0.0.1:5858/"></head>');
    });

    it('should inject <base href> into plain HTML fragment', () => {
        const html = '<div>Just a fragment</div>';
        manager.renderContent(html);
        expect(mockIframe.srcdoc).toContain('<base href="http://127.0.0.1:5858/">');
        expect(mockIframe.srcdoc).toMatch(/^<head><base href="http:\/\/127\.0\.0\.1:5858\/">/);
    });

    it('should NOT add duplicate <base> if one already exists', () => {
        const html = '<html><head><base href="http://other.com/"></head><body>OK</body></html>';
        manager.renderContent(html);
        // Should leave existing base tag alone
        expect(mockIframe.srcdoc).toBe(html);
        // Should not have double base tags
        const baseCount = (mockIframe.srcdoc.match(/<base/g) || []).length;
        expect(baseCount).toBe(1);
    });

    it('should hide empty state when rendering', () => {
        const emptyState = { style: { display: 'block' } };
        manager.elements.emptyState = emptyState;
        manager.renderContent('<html><head></head><body>Hi</body></html>');
        expect(emptyState.style.display).toBe('none');
    });

    it('should use current window.location.origin', () => {
        globalThis.window.location.origin = 'http://localhost:3000';
        manager.renderContent('<html><head></head><body></body></html>');
        expect(mockIframe.srcdoc).toContain('<base href="http://localhost:3000/">');
    });

    it('should preserve all original HTML content', () => {
        const html = '<html><head><style>body{color:red}</style></head><body><div id="app">Content</div></body></html>';
        manager.renderContent(html);
        expect(mockIframe.srcdoc).toContain('<style>body{color:red}</style>');
        expect(mockIframe.srcdoc).toContain('<div id="app">Content</div>');
    });
});
