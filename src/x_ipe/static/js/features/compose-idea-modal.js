/**
 * FEATURE-037-A: Compose Idea Modal — Create New
 *
 * Classes:
 *   ComposeIdeaModal  — Modal lifecycle, toggle, submit orchestration
 *   IdeaNameValidator — Name input validation + sanitization + word count
 *   AutoFolderNamer   — Generate wf-NNN-{name} from ideas tree
 */

/* =========================================================================
   IdeaNameValidator
   ========================================================================= */
class IdeaNameValidator {
    constructor(inputEl, counterEl, errorEl, maxWords = 10) {
        this.input = inputEl;
        this.counter = counterEl;
        this.error = errorEl;
        this.maxWords = maxWords;
    }

    validate(text) {
        const count = this.getWordCount(text);
        const valid = count > 0 && count <= this.maxWords;
        return { valid, wordCount: count, sanitized: this.sanitize(text) };
    }

    sanitize(text) {
        return text
            .toLowerCase()
            .replace(/[^\p{L}\p{N}\s-]/gu, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .substring(0, 50)
            .replace(/-$/, '');
    }

    getWordCount(text) {
        const trimmed = text.trim();
        return trimmed ? trimmed.split(/\s+/).length : 0;
    }

    bindLiveValidation() {
        this.input.addEventListener('input', () => {
            const { valid, wordCount } = this.validate(this.input.value);
            this.counter.textContent = `${wordCount} / ${this.maxWords} words`;
            this.counter.classList.toggle('over-limit', !valid && wordCount > 0);
            if (wordCount > this.maxWords) {
                this.error.textContent = `Name must be ${this.maxWords} words or fewer`;
            } else if (wordCount === 0 && this.input.value.trim().length > 0) {
                this.error.textContent = '';
            } else {
                this.error.textContent = '';
            }
            // Update folder preview
            if (this.folderPreview) {
                const sanitized = this.sanitize(this.input.value);
                this.folderPreview.textContent = sanitized ? `Folder: x-ipe-docs/ideas/wf-???-${sanitized}` : '';
            }
            // Notify modal to update submit button state
            if (this.onValidationChange) this.onValidationChange(valid && wordCount > 0);
        });
    }
}

/* =========================================================================
   AutoFolderNamer
   ========================================================================= */
class AutoFolderNamer {
    async generate(sanitizedName) {
        const tree = await this.fetchTree();
        const highest = this.findHighestWfNumber(tree);
        const nnn = String(highest + 1).padStart(3, '0');
        return `wf-${nnn}-${sanitizedName}`;
    }

    async fetchTree() {
        const res = await fetch('/api/ideas/tree');
        if (!res.ok) throw new Error('Failed to fetch ideas tree');
        const data = await res.json();
        return data.tree || [];
    }

    findHighestWfNumber(tree) {
        let max = 0;
        const traverse = (nodes) => {
            for (const node of nodes) {
                const match = node.name?.match(/^wf-(\d{3})/);
                if (match) max = Math.max(max, parseInt(match[1], 10));
                if (node.children) traverse(node.children);
            }
        };
        traverse(Array.isArray(tree) ? tree : [tree]);
        return max;
    }
}

/* =========================================================================
   ComposeIdeaModal
   ========================================================================= */
class ComposeIdeaModal {
    constructor({ workflowName, onComplete, mode, filePath, folderPath, folderName }) {
        this.workflowName = workflowName;
        this.onComplete = onComplete || (() => {});
        this.overlay = null;
        this.easyMDE = null;
        this.activeMode = (mode === 'edit') ? 'create' : (mode || 'create');
        this.activeTab = 'compose';
        this.validator = null;
        this.namer = new AutoFolderNamer();
        this.pendingFiles = [];
        this.abortController = null;
        this.nameValid = false;
        // FEATURE-037-B: Edit mode params
        this.editMode = mode === 'edit';
        this.filePath = filePath || '';
        this.folderPath = folderPath || '';
        this.folderName = folderName || '';
        this.linkPanel = null;
    }

    /* --- Lifecycle -------------------------------------------------------- */

    open() {
        this.createDOM();
        this.bindEvents();
        document.body.appendChild(this.overlay);
        requestAnimationFrame(() => {
            this.overlay.classList.add('active');
            this.initEasyMDE();
            if (this.editMode) {
                this.loadEditContent();
            }
        });
    }

    close() {
        this.cleanup();
        this.overlay.classList.remove('active');
        setTimeout(() => {
            if (this.overlay && this.overlay.parentNode) {
                this.overlay.remove();
            }
        }, 300);
    }

    cleanup() {
        if (this.easyMDE) {
            this.easyMDE.toTextArea();
            this.easyMDE = null;
        }
        if (this.linkPanel) {
            this.linkPanel.destroy();
            this.linkPanel = null;
        }
        if (this.abortController) {
            this.abortController.abort();
            this.abortController = null;
        }
    }

    /* --- DOM Creation ----------------------------------------------------- */

    createDOM() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'compose-modal-overlay';

        const acceptedTypes = '.md,.txt,.pdf,.png,.jpg,.py,.js,.docx';

        this.overlay.innerHTML = `
            <div class="compose-modal">
                <div class="compose-modal-header">
                    <h3>${this.editMode ? 'Edit Idea' : 'Compose Idea'}</h3>
                    <button class="compose-modal-close" title="Close">&times;</button>
                </div>
                <div class="compose-modal-body">
                    <!-- Mode Toggle -->
                    <div class="compose-modal-toggle">
                        <button class="active" data-mode="create">Create New</button>
                        <button data-mode="link">Link Existing</button>
                    </div>

                    <!-- Create New Content -->
                    <div class="compose-modal-create-content">
                        <!-- Name Input -->
                        <div class="compose-modal-name">
                            <label for="compose-idea-name">Idea Name <span style="color:#ef4444">*</span></label>
                            <input type="text" id="compose-idea-name" placeholder="Enter a short, descriptive name (max 10 words)">
                            <div class="compose-modal-name-meta">
                                <span class="compose-modal-name-error"></span>
                                <span class="compose-modal-word-counter">0 / 10 words</span>
                            </div>
                            <div class="compose-modal-folder-preview"></div>
                        </div>

                        <!-- Tab Bar -->
                        <div class="compose-modal-tabs">
                            <button class="active" data-tab="compose">Compose</button>
                            <button data-tab="upload">Upload</button>
                        </div>

                        <!-- Compose Editor -->
                        <div class="compose-modal-editor" data-content="compose">
                            <textarea id="compose-idea-textarea" placeholder="Write your idea in Markdown..."></textarea>
                        </div>

                        <!-- Upload Zone -->
                        <div class="compose-modal-upload" data-content="upload">
                            <div class="compose-modal-dropzone">
                                <div class="compose-modal-dropzone-icon"><i class="bi bi-cloud-arrow-up"></i></div>
                                <div class="compose-modal-dropzone-text">Drag & drop files here or click to browse</div>
                                <div class="compose-modal-dropzone-hint">Accepts: md, txt, pdf, png, jpg, py, js, docx</div>
                                <input type="file" class="compose-modal-file-input" multiple accept="${acceptedTypes}" style="display:none">
                            </div>
                            <div class="compose-modal-file-list"></div>
                        </div>

                        <!-- Error Toast -->
                        <div class="compose-modal-toast"></div>
                    </div>

                    <!-- Link Existing Placeholder -->
                    <div class="compose-modal-link-content" style="display:none">
                        <div class="compose-modal-placeholder">
                            <i class="bi bi-link-45deg"></i>
                            <p>Available in next update</p>
                        </div>
                    </div>
                </div>
                <div class="compose-modal-footer">
                    <button class="compose-modal-btn compose-modal-btn-cancel">Cancel</button>
                    <button class="compose-modal-btn compose-modal-btn-submit" disabled>${this.editMode ? 'Update Idea' : 'Submit Idea'}</button>
                </div>
            </div>
        `;

        // Cache references
        this.dialog = this.overlay.querySelector('.compose-modal');
        this.nameInput = this.overlay.querySelector('#compose-idea-name');
        this.wordCounter = this.overlay.querySelector('.compose-modal-word-counter');
        this.nameError = this.overlay.querySelector('.compose-modal-name-error');
        this.folderPreview = this.overlay.querySelector('.compose-modal-folder-preview');
        this.submitBtn = this.overlay.querySelector('.compose-modal-btn-submit');
        this.toast = this.overlay.querySelector('.compose-modal-toast');
        this.createContent = this.overlay.querySelector('.compose-modal-create-content');
        this.linkContent = this.overlay.querySelector('.compose-modal-link-content');

        // Setup validator
        this.validator = new IdeaNameValidator(
            this.nameInput, this.wordCounter, this.nameError
        );
        this.validator.folderPreview = this.folderPreview;
        this.validator.onValidationChange = (valid) => {
            this.nameValid = valid;
            this.updateSubmitState();
        };

        // FEATURE-037-B: Edit mode — pre-fill folder name and make read-only
        if (this.editMode && this.folderName) {
            this.nameInput.value = this.folderName;
            this.nameInput.disabled = true;
            this.nameValid = true;
            if (this.folderPreview) {
                this.folderPreview.textContent = `📁 x-ipe-docs/ideas/${this.folderName}`;
            }
        } else if (this.workflowName) {
            // Auto-fill with workflow name (from workflow-{name}.json)
            this.nameInput.value = this.workflowName;
            this.nameInput.dispatchEvent(new Event('input'));
        }
    }

    /* --- Event Binding ---------------------------------------------------- */

    bindEvents() {
        // Close button
        this.overlay.querySelector('.compose-modal-close').addEventListener('click', () => this.close());
        this.overlay.querySelector('.compose-modal-btn-cancel').addEventListener('click', () => this.close());

        // Escape key
        this._keyHandler = (e) => {
            if (e.key === 'Escape') this.close();
        };
        document.addEventListener('keydown', this._keyHandler);

        // Overlay click — check target to prevent accidental close
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                // AC-005: Do NOT close on overlay click
            }
        });

        // Mode toggle
        this.overlay.querySelectorAll('.compose-modal-toggle button').forEach(btn => {
            btn.addEventListener('click', () => this.switchMode(btn.dataset.mode));
        });

        // Tab switching
        this.overlay.querySelectorAll('.compose-modal-tabs button').forEach(btn => {
            btn.addEventListener('click', () => this.switchTab(btn.dataset.tab));
        });

        // Upload zone
        const dropzone = this.overlay.querySelector('.compose-modal-dropzone');
        const fileInput = this.overlay.querySelector('.compose-modal-file-input');

        dropzone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) this.addFiles(e.target.files);
        });
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });
        dropzone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
        });
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) this.addFiles(e.dataTransfer.files);
        });

        // Submit
        this.submitBtn.addEventListener('click', () => this.handleSubmit());

        // Name validation
        this.validator.bindLiveValidation();
    }

    /* --- Mode & Tab Switching --------------------------------------------- */

    switchMode(mode) {
        this.activeMode = mode;
        this.overlay.querySelectorAll('.compose-modal-toggle button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });
        this.createContent.style.display = mode === 'create' ? '' : 'none';
        this.linkContent.style.display = mode === 'link' ? '' : 'none';

        // FEATURE-037-B: Instantiate LinkExistingPanel on first switch
        if (mode === 'link' && !this.linkPanel && typeof LinkExistingPanel !== 'undefined') {
            this.linkPanel = new LinkExistingPanel(this.linkContent, {
                onSelect: (path) => {
                    this._linkedPath = path;
                    this.updateSubmitState();
                }
            });
            this.linkPanel.render();
        }
        if (mode === 'link') {
            this.submitBtn.textContent = 'Confirm Link';
        } else {
            this.submitBtn.textContent = this.editMode ? 'Update Idea' : 'Submit Idea';
        }

        this.updateSubmitState();
    }

    switchTab(tab) {
        this.activeTab = tab;
        this.overlay.querySelectorAll('.compose-modal-tabs button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tab);
        });
        const editor = this.overlay.querySelector('[data-content="compose"]');
        const upload = this.overlay.querySelector('[data-content="upload"]');
        editor.style.display = tab === 'compose' ? '' : 'none';
        upload.style.display = tab === 'upload' ? '' : 'none';
        if (tab === 'upload') upload.classList.add('active');
        else upload.classList.remove('active');
        this.updateSubmitState();
    }

    /* --- EasyMDE Init ----------------------------------------------------- */

    initEasyMDE() {
        const textarea = this.overlay.querySelector('#compose-idea-textarea');
        if (!textarea || typeof EasyMDE === 'undefined') return;

        this.easyMDE = new EasyMDE({
            element: textarea,
            autofocus: false,
            spellChecker: false,
            placeholder: 'Write your idea in Markdown...',
            toolbar: [
                'bold', 'italic', 'heading', '|',
                'unordered-list', 'ordered-list', '|',
                'link', 'code', '|',
                'preview'
            ],
            status: false,
            minHeight: '180px'
        });

        this.easyMDE.codemirror.on('change', () => this.updateSubmitState());
    }

    /* --- File Management -------------------------------------------------- */

    addFiles(fileList) {
        for (const file of fileList) {
            if (!this.pendingFiles.find(f => f.name === file.name && f.size === file.size)) {
                this.pendingFiles.push(file);
            }
        }
        this.renderFileList();
        this.updateSubmitState();
    }

    removeFile(index) {
        this.pendingFiles.splice(index, 1);
        this.renderFileList();
        this.updateSubmitState();
    }

    renderFileList() {
        const list = this.overlay.querySelector('.compose-modal-file-list');
        if (!list) return;

        list.innerHTML = this.pendingFiles.map((file, i) => `
            <div class="compose-modal-file-item">
                <div class="compose-modal-file-item-info">
                    <i class="bi bi-file-earmark"></i>
                    <span>${this._escapeHtml(file.name)}</span>
                    <span class="compose-modal-file-item-size">${this._formatSize(file.size)}</span>
                </div>
                <button class="compose-modal-file-remove" data-index="${i}" title="Remove">&times;</button>
            </div>
        `).join('');

        list.querySelectorAll('.compose-modal-file-remove').forEach(btn => {
            btn.addEventListener('click', () => this.removeFile(parseInt(btn.dataset.index)));
        });
    }

    /* --- Submit ----------------------------------------------------------- */

    updateSubmitState() {
        if (!this.submitBtn) return;
        if (this.activeMode === 'link') {
            this.submitBtn.disabled = !this._linkedPath;
            return;
        }
        const hasContent = this.activeTab === 'compose'
            ? (this.easyMDE ? this.easyMDE.value().trim().length > 0 : false)
            : this.pendingFiles.length > 0;
        this.submitBtn.disabled = !(this.nameValid && hasContent && (this.activeMode === 'create' || this.editMode));
    }

    async handleSubmit() {
        if (this.submitBtn.disabled) return;

        // FEATURE-037-B: Link Existing mode
        if (this.activeMode === 'link' && this._linkedPath) {
            this.setSubmitting(true);
            try {
                const folderPath = this._linkedPath.split('/').slice(0, -1).join('/');
                await fetch(`/api/workflow/${this.workflowName}/action`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        action: 'compose_idea',
                        status: 'done',
                        deliverables: [this._linkedPath, folderPath]
                    })
                });
                this.onComplete({ file: this._linkedPath, folder: folderPath });
                this.close();
            } catch (err) {
                this.showToast('Failed to link idea', 'error');
                this.setSubmitting(false);
            }
            return;
        }

        // FEATURE-037-B: Edit mode — overwrite in place
        if (this.editMode) {
            return this.handleUpdate();
        }

        const nameResult = this.validator.validate(this.nameInput.value);
        if (!nameResult.valid) return;

        this.setSubmitting(true);
        this.hideToast();

        try {
            this.abortController = new AbortController();

            const folderName = await this.namer.generate(nameResult.sanitized);

            const formData = new FormData();
            formData.append('target_folder', folderName);

            if (this.activeTab === 'compose') {
                const content = this.easyMDE.value();
                const blob = new Blob([content], { type: 'text/markdown' });
                formData.append('files', blob, 'new idea.md');
            } else {
                for (const file of this.pendingFiles) {
                    formData.append('files', file);
                }
            }

            const uploadRes = await fetch('/api/ideas/upload', {
                method: 'POST',
                body: formData,
                signal: this.abortController.signal
            });

            if (uploadRes.status === 409) {
                this.showToast('Folder already exists. Try a different name.', 'error');
                this.setSubmitting(false);
                return;
            }

            if (!uploadRes.ok) throw new Error(await uploadRes.text());

            const uploadData = await uploadRes.json();
            const folder_path = uploadData.folder_path || `x-ipe-docs/ideas/${folderName}`;
            const fileName = uploadData.files_uploaded?.[0] || 'new idea.md';
            const filePath = `${folder_path}/${fileName}`;

            // Auto-complete compose_idea action
            await fetch(`/api/workflow/${this.workflowName}/action`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'compose_idea',
                    status: 'done',
                    deliverables: [filePath, folder_path]
                }),
                signal: this.abortController.signal
            });

            this.onComplete({ file: filePath, folder: folder_path });
            this.close();

        } catch (err) {
            if (err.name === 'AbortError') return;
            console.error('Compose idea submit failed:', err);
            this.showToast('Failed to save idea. Please try again.', 'error');
            this.setSubmitting(false);
        }
    }

    /* --- UI Helpers ------------------------------------------------------- */

    setSubmitting(submitting) {
        this.submitBtn.disabled = submitting;
        if (submitting) {
            this.submitBtn.textContent = 'Submitting...';
        } else if (this.activeMode === 'link') {
            this.submitBtn.textContent = 'Confirm Link';
        } else {
            this.submitBtn.textContent = this.editMode ? 'Update Idea' : 'Submit Idea';
        }
    }

    showToast(message, type = 'error') {
        if (!this.toast) return;
        this.toast.textContent = message;
        this.toast.className = `compose-modal-toast ${type}`;
    }

    hideToast() {
        if (!this.toast) return;
        this.toast.className = 'compose-modal-toast';
        this.toast.textContent = '';
    }

    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    _formatSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    /* --- FEATURE-037-B: Edit Mode ---------------------------------------- */

    async loadEditContent() {
        if (!this.filePath) {
            this.showToast('No file path — opening in create mode', 'error');
            return;
        }
        try {
            const resp = await fetch(`/api/ideas/file?path=${encodeURIComponent(this.filePath)}`);
            if (!resp.ok) {
                this.showToast('Could not load file content', 'error');
                return;
            }
            const content = await resp.text();
            if (this.easyMDE) {
                this.easyMDE.value(content);
            }
            this.updateSubmitState();
        } catch (err) {
            this.showToast('Failed to load file for editing', 'error');
        }
    }

    async handleUpdate() {
        this.setSubmitting(true);
        this.hideToast();
        try {
            this.abortController = new AbortController();
            const content = this.easyMDE ? this.easyMDE.value() : '';
            const blob = new Blob([content], { type: 'text/markdown' });

            const formData = new FormData();
            formData.append('target_folder', this.folderName);
            formData.append('files', blob, this.filePath.split('/').pop() || 'new idea.md');

            const uploadRes = await fetch('/api/ideas/upload', {
                method: 'POST',
                body: formData,
                signal: this.abortController.signal
            });

            // 409 expected for overwrite — continue
            if (!uploadRes.ok && uploadRes.status !== 409) {
                throw new Error(await uploadRes.text());
            }

            const uploadData = await uploadRes.json();
            const folder_path = uploadData.folder_path || this.folderPath;
            const fileName = uploadData.files_uploaded?.[0] || this.filePath.split('/').pop();
            const filePath = `${folder_path}/${fileName}`;

            await fetch(`/api/workflow/${this.workflowName}/action`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'compose_idea',
                    status: 'done',
                    deliverables: [filePath, folder_path]
                }),
                signal: this.abortController.signal
            });

            this.onComplete({ file: filePath, folder: folder_path });
            this.close();
        } catch (err) {
            if (err.name === 'AbortError') return;
            this.showToast('Failed to update idea', 'error');
            this.setSubmitting(false);
        }
    }
}

/* =========================================================================
   FEATURE-037-B: LinkExistingPanel
   Two-column panel: file tree (left) + preview (right).
   ========================================================================= */
class LinkExistingPanel {
    constructor(container, { onSelect }) {
        this.container = container;
        this.onSelect = onSelect || (() => {});
        this.selectedPath = null;
    }

    render() {
        this.container.innerHTML = `
            <div class="link-existing-panel">
                <div class="link-existing-search">
                    <input type="text" class="link-existing-search-input" placeholder="Search ideas...">
                </div>
                <div class="link-existing-columns">
                    <div class="link-existing-tree">
                        <div class="link-existing-empty">Loading ideas...</div>
                    </div>
                    <div class="link-existing-preview">
                        <div class="link-existing-empty">Select a file to preview</div>
                    </div>
                </div>
            </div>
        `;

        this.treeEl = this.container.querySelector('.link-existing-tree');
        this.previewEl = this.container.querySelector('.link-existing-preview');
        this.searchInput = this.container.querySelector('.link-existing-search-input');

        this.searchInput.addEventListener('input', () => this._filterTree());
        this._loadTree();
    }

    async _loadTree() {
        try {
            const resp = await fetch('/api/ideas/tree');
            const json = await resp.json();
            this.treeData = json.tree || [];
            this._renderTree(this.treeData);
        } catch (err) {
            this.treeEl.innerHTML = '<div class="link-existing-empty">Failed to load ideas</div>';
        }
    }

    _renderTree(nodes) {
        if (!nodes || nodes.length === 0) {
            this.treeEl.innerHTML = '<div class="link-existing-empty">No ideas found</div>';
            return;
        }
        this.treeEl.innerHTML = '';
        this._renderNodes(nodes, this.treeEl, 0);
    }

    _renderNodes(nodes, parent, depth) {
        for (const node of nodes) {
            const item = document.createElement('div');
            item.className = 'link-existing-item';
            item.style.paddingLeft = `${depth * 16 + 8}px`;

            if (node.type === 'directory' || node.type === 'folder') {
                item.innerHTML = `<span class="link-item-icon">📁</span> ${this._escapeHtml(node.name)}`;
                parent.appendChild(item);
                if (node.children) {
                    this._renderNodes(node.children, parent, depth + 1);
                }
            } else {
                item.innerHTML = `<span class="link-item-icon">📄</span> ${this._escapeHtml(node.name)}`;
                item.dataset.path = node.path || '';
                item.addEventListener('click', () => this._selectFile(item, node.path));
                parent.appendChild(item);
            }
        }
    }

    async _selectFile(itemEl, path) {
        this.treeEl.querySelectorAll('.link-existing-item.selected').forEach(el => el.classList.remove('selected'));
        itemEl.classList.add('selected');
        this.selectedPath = path;
        this.onSelect(path);

        // Fetch file preview
        this.previewEl.innerHTML = '<div class="link-existing-empty">Loading preview...</div>';
        try {
            const resp = await fetch(`/api/ideas/file?path=${encodeURIComponent(path)}`);
            if (!resp.ok) throw new Error('Not found');
            const content = await resp.text();
            if (typeof marked !== 'undefined') {
                this.previewEl.innerHTML = `<div class="link-existing-preview-content">${marked.parse(content)}</div>`;
            } else {
                this.previewEl.innerHTML = `<pre class="link-existing-preview-content">${this._escapeHtml(content)}</pre>`;
            }
        } catch {
            this.previewEl.innerHTML = '<div class="link-existing-empty">Cannot preview this file</div>';
        }
    }

    _filterTree() {
        const query = this.searchInput.value.toLowerCase();
        const items = this.treeEl.querySelectorAll('.link-existing-item');
        items.forEach(item => {
            item.style.display = item.textContent.toLowerCase().includes(query) ? '' : 'none';
        });
    }

    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    destroy() {
        this.container.innerHTML = '';
        this.selectedPath = null;
    }
}
