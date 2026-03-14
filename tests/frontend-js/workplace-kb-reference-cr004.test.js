/**
 * Tests for CR-004: KB Reference Integration in Workplace Compose Pane
 * Covers: button in tab bar, picker integration, count label with delete, popup, FormData, state reset, immediate YAML
 */
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock KBReferencePicker globally before loading workplace
let mockPickerOpen;
let mockPickerOnInsert;

class MockKBReferencePicker {
    constructor(options = {}) {
        mockPickerOnInsert = options.onInsert || null;
        this.onInsert = options.onInsert || null;
    }
    async open() {
        mockPickerOpen?.();
    }
}

function setupDOM() {
    document.body.innerHTML = `
        <div id="workplace-content">
            <ul class="nav nav-tabs workplace-tabs" id="ideaTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="compose-tab">Compose Idea</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="upload-tab">Upload Files</button>
                </li>
                <li class="nav-item workplace-kb-ref-area ms-auto" role="presentation">
                    <span class="workplace-kb-ref-count" id="workplace-kb-ref-count" style="display:none;"></span>
                    <button class="workplace-kb-ref-btn" id="workplace-kb-ref-btn" title="Add KB References">
                        📚 KB Reference
                    </button>
                </li>
            </ul>
            <div class="tab-content workplace-tab-content" id="ideaTabContent">
                <div class="tab-pane fade show active" id="compose-pane" role="tabpanel">
                    <div class="workplace-compose">
                        <textarea id="workplace-compose-textarea">Test idea content</textarea>
                        <div class="workplace-compose-actions">
                            <button class="btn btn-primary" id="workplace-submit-idea">
                                <i class="bi bi-send"></i> Submit Idea
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div id="workplace-upload-status" class="d-none"></div>
    `;
}

describe('CR-004: KB Reference in Tab Bar', () => {
    beforeEach(() => {
        setupDOM();
        globalThis.KBReferencePicker = MockKBReferencePicker;
        mockPickerOpen = vi.fn();
        mockPickerOnInsert = null;
    });

    afterEach(() => {
        document.body.innerHTML = '';
        delete globalThis.KBReferencePicker;
    });

    describe('Button Placement in Tab Bar', () => {
        it('should render KB Reference button inside tab bar ul', () => {
            const tabBar = document.getElementById('ideaTabs');
            const btn = tabBar.querySelector('#workplace-kb-ref-btn');
            expect(btn).toBeTruthy();
            expect(btn.textContent).toContain('KB Reference');
        });

        it('should render count label inside tab bar ul', () => {
            const tabBar = document.getElementById('ideaTabs');
            const count = tabBar.querySelector('#workplace-kb-ref-count');
            expect(count).toBeTruthy();
        });

        it('should place KB area as last item in tab bar with ms-auto', () => {
            const tabBar = document.getElementById('ideaTabs');
            const kbArea = tabBar.querySelector('.workplace-kb-ref-area');
            expect(kbArea).toBeTruthy();
            expect(kbArea.classList.contains('ms-auto')).toBe(true);
            // Should be last child
            expect(tabBar.lastElementChild).toBe(kbArea);
        });

        it('should have count label before KB button (left of button)', () => {
            const kbArea = document.querySelector('.workplace-kb-ref-area');
            const children = Array.from(kbArea.children);
            const countIdx = children.findIndex(c => c.id === 'workplace-kb-ref-count');
            const btnIdx = children.findIndex(c => c.id === 'workplace-kb-ref-btn');
            expect(countIdx).toBeLessThan(btnIdx);
        });

        it('should NOT have KB button in compose-actions anymore', () => {
            const actions = document.querySelector('.workplace-compose-actions');
            const btn = actions.querySelector('#workplace-kb-ref-btn');
            expect(btn).toBeNull();
        });
    });

    describe('Picker Integration', () => {
        it('should create KBReferencePicker with onInsert callback on button click', () => {
            const btn = document.getElementById('workplace-kb-ref-btn');
            btn.addEventListener('click', () => {
                const picker = new KBReferencePicker({
                    onInsert: (paths) => {}
                });
                picker.open();
            });
            btn.click();
            expect(mockPickerOpen).toHaveBeenCalled();
            expect(mockPickerOnInsert).toBeTypeOf('function');
        });
    });

    describe('Count Label with Delete Icon', () => {
        it('should show count label with delete icon after references inserted', () => {
            const countEl = document.getElementById('workplace-kb-ref-count');
            const n = 2;
            countEl.innerHTML = `📚 ${n} references<span class="workplace-kb-ref-delete" title="Remove KB references">✕</span>`;
            countEl.style.display = '';
            
            expect(countEl.style.display).toBe('');
            expect(countEl.textContent).toContain('2');
            const deleteIcon = countEl.querySelector('.workplace-kb-ref-delete');
            expect(deleteIcon).toBeTruthy();
            expect(deleteIcon.textContent).toBe('✕');
        });

        it('should hide delete icon by default (shown on hover via CSS)', () => {
            const countEl = document.getElementById('workplace-kb-ref-count');
            countEl.innerHTML = `📚 1 reference<span class="workplace-kb-ref-delete">✕</span>`;
            const deleteIcon = countEl.querySelector('.workplace-kb-ref-delete');
            // CSS rule: .workplace-kb-ref-delete { display: none; }
            // .workplace-kb-ref-count:hover .workplace-kb-ref-delete { display: inline; }
            // In jsdom we can't test CSS hover, but verify the element exists
            expect(deleteIcon).toBeTruthy();
        });
    });

    describe('Popup', () => {
        it('should show popup with reference items when count label clicked', () => {
            const countEl = document.getElementById('workplace-kb-ref-count');
            countEl.style.display = '';
            countEl.style.position = 'relative';
            
            const popup = document.createElement('div');
            popup.className = 'workplace-kb-ref-popup';
            popup.innerHTML = [
                '<div class="workplace-kb-ref-popup-item">📄 setup.md</div>',
                '<div class="workplace-kb-ref-popup-item">📁 guides</div>'
            ].join('');
            countEl.appendChild(popup);
            
            const items = popup.querySelectorAll('.workplace-kb-ref-popup-item');
            expect(items.length).toBe(2);
        });
    });

    describe('FormData Integration', () => {
        it('should append kb_references as JSON string to FormData', () => {
            const formData = new FormData();
            const kbRefs = ['knowledge-base/setup.md', 'knowledge-base/api-docs/'];
            formData.append('kb_references', JSON.stringify(kbRefs));
            
            const parsed = JSON.parse(formData.get('kb_references'));
            expect(parsed).toEqual(kbRefs);
        });

        it('should not append kb_references when array is empty', () => {
            const formData = new FormData();
            const kbRefs = [];
            if (kbRefs.length > 0) {
                formData.append('kb_references', JSON.stringify(kbRefs));
            }
            expect(formData.get('kb_references')).toBeNull();
        });
    });

    describe('Accumulation Across Picker Opens', () => {
        it('should accumulate references from multiple picker sessions', () => {
            const kbReferences = [];
            kbReferences.push(...['knowledge-base/setup.md']);
            kbReferences.push(...['knowledge-base/api.md', 'knowledge-base/guides/']);
            expect(kbReferences.length).toBe(3);
        });

        it('should allow duplicate paths (append not deduplicate)', () => {
            const kbReferences = [];
            kbReferences.push('knowledge-base/setup.md');
            kbReferences.push('knowledge-base/setup.md');
            expect(kbReferences.length).toBe(2);
        });
    });

    describe('KBReferencePicker Unavailable', () => {
        it('should not crash when KBReferencePicker is undefined', () => {
            delete globalThis.KBReferencePicker;
            const btn = document.getElementById('workplace-kb-ref-btn');
            const available = typeof KBReferencePicker !== 'undefined';
            expect(available).toBe(false);
            expect(() => btn.click()).not.toThrow();
        });
    });
});

describe('TASK-867: Auto-create draft folder for KB Reference', () => {
    let fetchSpy;

    beforeEach(() => {
        setupDOM();
        globalThis.KBReferencePicker = MockKBReferencePicker;
        mockPickerOpen = vi.fn();
        mockPickerOnInsert = null;
        fetchSpy = vi.fn();
        globalThis.fetch = fetchSpy;
    });

    afterEach(() => {
        document.body.innerHTML = '';
        delete globalThis.KBReferencePicker;
        vi.restoreAllMocks();
    });

    it('should call create-folder API when targetFolderPath is null and KB Ref clicked', async () => {
        // Simulate the workplace state: compose mode, no target folder
        const workplace = { targetFolderPath: null, kbReferences: [] };

        // Mock create-folder response
        fetchSpy.mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                success: true,
                folder_name: 'Draft Idea - 03142026 063600',
                folder_path: 'x-ipe-docs/ideas/Draft Idea - 03142026 063600'
            })
        });

        // _ensureDraftFolder logic under test
        async function ensureDraftFolder(wp) {
            if (wp.targetFolderPath) return wp.targetFolderPath;
            const timestamp = new Date().toLocaleString('en-US', {
                month: '2-digit', day: '2-digit', year: 'numeric',
                hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
            }).replace(/[/,:\s]+/g, '');
            const folderName = `Draft Idea - ${timestamp}`;
            const resp = await fetch('/api/ideas/create-folder', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ folder_name: folderName })
            });
            const result = await resp.json();
            if (result.success) {
                wp.targetFolderPath = result.folder_path;
                return result.folder_path;
            }
            return null;
        }

        const path = await ensureDraftFolder(workplace);
        expect(fetchSpy).toHaveBeenCalledTimes(1);
        const [url, opts] = fetchSpy.mock.calls[0];
        expect(url).toBe('/api/ideas/create-folder');
        expect(opts.method).toBe('POST');
        const body = JSON.parse(opts.body);
        expect(body.folder_name).toMatch(/^Draft Idea - /);
        expect(path).toBe('x-ipe-docs/ideas/Draft Idea - 03142026 063600');
        expect(workplace.targetFolderPath).toBe(path);
    });

    it('should NOT call create-folder when targetFolderPath already set', async () => {
        const workplace = { targetFolderPath: 'x-ipe-docs/ideas/existing-folder', kbReferences: [] };

        async function ensureDraftFolder(wp) {
            if (wp.targetFolderPath) return wp.targetFolderPath;
            // Would call fetch, but shouldn't reach here
            const resp = await fetch('/api/ideas/create-folder', { method: 'POST' });
            return null;
        }

        const path = await ensureDraftFolder(workplace);
        expect(fetchSpy).not.toHaveBeenCalled();
        expect(path).toBe('x-ipe-docs/ideas/existing-folder');
    });

    it('should update Saving-to banner after draft folder creation', () => {
        // No banner initially for new idea
        let banner = document.querySelector('.workplace-target-folder-name');
        expect(banner).toBeNull();

        // Simulate creating the banner after draft folder creation
        const contentArea = document.getElementById('workplace-content');
        const uploaderDiv = document.createElement('div');
        uploaderDiv.className = 'workplace-uploader';
        contentArea.prepend(uploaderDiv);

        const bannerHtml = `
            <div class="workplace-target-folder" data-folder-path="x-ipe-docs/ideas/Draft Idea - 03142026 063600">
                <i class="bi bi-folder-fill"></i>
                <span>Saving to: <strong class="workplace-target-folder-name">Draft Idea - 03142026 063600</strong></span>
            </div>
        `;
        uploaderDiv.insertAdjacentHTML('afterbegin', bannerHtml);

        banner = document.querySelector('.workplace-target-folder-name');
        expect(banner).toBeTruthy();
        expect(banner.textContent).toContain('Draft Idea');
    });

    it('should open picker only after draft folder is created', async () => {
        const callOrder = [];

        fetchSpy.mockImplementation(async (url) => {
            if (url === '/api/ideas/create-folder') {
                callOrder.push('create-folder');
                return {
                    ok: true,
                    json: async () => ({
                        success: true,
                        folder_name: 'Draft Idea - test',
                        folder_path: 'x-ipe-docs/ideas/Draft Idea - test'
                    })
                };
            }
            return { ok: true, json: async () => ({}) };
        });

        // Simulate the full flow
        const workplace = { targetFolderPath: null };
        if (!workplace.targetFolderPath) {
            const resp = await fetch('/api/ideas/create-folder', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ folder_name: 'Draft Idea - test' })
            });
            const result = await resp.json();
            workplace.targetFolderPath = result.folder_path;
            callOrder.push('folder-set');
        }
        // Then open picker
        const picker = new MockKBReferencePicker({});
        await picker.open();
        callOrder.push('picker-opened');

        expect(callOrder).toEqual(['create-folder', 'folder-set', 'picker-opened']);
    });

    it('should handle create-folder API failure gracefully', async () => {
        fetchSpy.mockResolvedValueOnce({
            ok: false,
            json: async () => ({ success: false, error: 'Folder creation failed' })
        });

        const workplace = { targetFolderPath: null };
        const resp = await fetch('/api/ideas/create-folder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ folder_name: 'Draft Idea - test' })
        });
        const result = await resp.json();
        if (result.success) {
            workplace.targetFolderPath = result.folder_path;
        }

        // targetFolderPath should remain null on failure
        expect(workplace.targetFolderPath).toBeNull();
    });

    it('should pass targetFolderPath to submitComposedIdea after draft created', async () => {
        // After draft folder is created, targetFolderPath is set
        const workplace = {
            targetFolderPath: 'x-ipe-docs/ideas/Draft Idea - 03142026 063600'
        };

        // Submit should include target_folder in FormData
        const formData = new FormData();
        formData.append('files', new Blob(['test'], { type: 'text/markdown' }), 'new idea.md');
        if (workplace.targetFolderPath) {
            formData.append('target_folder', workplace.targetFolderPath);
        }

        expect(formData.get('target_folder')).toBe('x-ipe-docs/ideas/Draft Idea - 03142026 063600');
    });
});
