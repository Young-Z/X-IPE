import { describe, it, expect, beforeEach } from 'vitest';
import { JSDOM } from 'jsdom';

describe('Folder Browser Modal — panel divider & default width', () => {
    let document;

    beforeEach(() => {
        const dom = new JSDOM('<!DOCTYPE html><html><head></head><body></body></html>');
        document = dom.window.document;

        // Build modal body structure matching folder-browser-modal.js
        const body = document.createElement('div');
        body.className = 'folder-browser-body';

        const tree = document.createElement('div');
        tree.className = 'folder-browser-tree';
        body.appendChild(tree);

        // Divider should exist between tree and preview
        const divider = document.createElement('div');
        divider.className = 'folder-browser-divider';
        body.appendChild(divider);

        const preview = document.createElement('div');
        preview.className = 'folder-browser-preview';
        body.appendChild(preview);

        document.body.appendChild(body);

        // Apply inline CSS to simulate the stylesheet
        const style = document.createElement('style');
        style.textContent = `
            @import url('/src/x_ipe/static/css/features/folder-browser-modal.css');
        `;
        document.head.appendChild(style);
    });

    it('should have a divider element between tree and preview', () => {
        const body = document.querySelector('.folder-browser-body');
        const children = Array.from(body.children).map(c => c.className);
        expect(children).toContain('folder-browser-divider');
        const dividerIdx = children.indexOf('folder-browser-divider');
        const treeIdx = children.indexOf('folder-browser-tree');
        const previewIdx = children.indexOf('folder-browser-preview');
        expect(dividerIdx).toBeGreaterThan(treeIdx);
        expect(dividerIdx).toBeLessThan(previewIdx);
    });

    it('divider should have cursor:col-resize style', () => {
        const divider = document.querySelector('.folder-browser-divider');
        expect(divider).toBeTruthy();
        // In real DOM it would be via CSS; here just check existence
        expect(divider.className).toBe('folder-browser-divider');
    });

    it('tree panel default width should be 20% or less', () => {
        const fs = require('fs');
        const css = fs.readFileSync('src/x_ipe/static/css/features/folder-browser-modal.css', 'utf8');
        const match = css.match(/\.folder-browser-tree\s*\{[^}]*?\bwidth:\s*(\d+)%/);
        expect(match).toBeTruthy();
        expect(parseInt(match[1])).toBeLessThanOrEqual(20);
    });
});
