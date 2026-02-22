/**
 * TASK-602: Test copy-path button in feedback panel entries
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { JSDOM } from 'jsdom';

describe('Feedback Entry Copy Path Button', () => {
    let dom, document;

    function createEntryHTML(folder) {
        const folderBtn = folder
            ? `<button class="entry-action-btn copy-path" title="Copy folder path" data-folder="${folder}"><i class="bi bi-clipboard"></i></button>`
            : '';
        return `
            <div class="feedback-entry status-submitted" data-entry-id="test-1">
                <div class="feedback-entry-header">
                    <div class="entry-info">
                        <span class="entry-name">Feedback-Test</span>
                    </div>
                    <div class="entry-actions">
                        ${folderBtn}
                        <button class="entry-action-btn delete-entry" title="Delete"><i class="bi bi-trash"></i></button>
                    </div>
                </div>
            </div>`;
    }

    beforeEach(() => {
        dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');
        document = dom.window.document;
    });

    it('should render copy-path button for submitted entry with folder', () => {
        document.body.innerHTML = createEntryHTML('x-ipe-docs/uiux-feedback/Feedback-20260222-133420');
        const copyBtn = document.querySelector('.copy-path');
        expect(copyBtn).not.toBeNull();
        expect(copyBtn.dataset.folder).toBe('x-ipe-docs/uiux-feedback/Feedback-20260222-133420');
    });

    it('should NOT render copy-path button when no folder', () => {
        document.body.innerHTML = createEntryHTML(null);
        const copyBtn = document.querySelector('.copy-path');
        expect(copyBtn).toBeNull();
    });

    it('should render copy-path button before delete button', () => {
        document.body.innerHTML = createEntryHTML('x-ipe-docs/uiux-feedback/Feedback-Test');
        const actions = document.querySelector('.entry-actions');
        const buttons = actions.querySelectorAll('.entry-action-btn');
        expect(buttons.length).toBe(2);
        expect(buttons[0].classList.contains('copy-path')).toBe(true);
        expect(buttons[1].classList.contains('delete-entry')).toBe(true);
    });

    it('should have clipboard icon', () => {
        document.body.innerHTML = createEntryHTML('x-ipe-docs/uiux-feedback/Feedback-Test');
        const icon = document.querySelector('.copy-path i');
        expect(icon.classList.contains('bi-clipboard')).toBe(true);
    });
});
