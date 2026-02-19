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
            .replace(/[^a-z0-9\s-]/g, '')
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
                this.folderPreview.textContent = sanitized ? `Folder: wf-???-${sanitized}` : '';
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
        return res.json();
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
    constructor({ workflowName, onComplete }) {
        this.workflowName = workflowName;
        this.onComplete = onComplete || (() => {});
        this.overlay = null;
        this.easyMDE = null;
        this.activeMode = 'create';
        this.activeTab = 'compose';
        this.validator = null;
        this.namer = new AutoFolderNamer();
        this.pendingFiles = [];
        this.abortController = null;
        this.nameValid = false;
    }

    /* --- Lifecycle -------------------------------------------------------- */

    open() {
        this.createDOM();
        this.bindEvents();
        document.body.appendChild(this.overlay);
        requestAnimationFrame(() => {
            this.overlay.classList.add('active');
            this.initEasyMDE();
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
                    <h3>Compose Idea</h3>
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
                    <button class="compose-modal-btn compose-modal-btn-submit" disabled>Submit Idea</button>
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
        const hasContent = this.activeTab === 'compose'
            ? (this.easyMDE ? this.easyMDE.value().trim().length > 0 : false)
            : this.pendingFiles.length > 0;
        this.submitBtn.disabled = !(this.nameValid && hasContent && this.activeMode === 'create');
    }

    async handleSubmit() {
        if (this.submitBtn.disabled) return;

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
                formData.append('files', blob, 'idea.md');
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
            const filePath = uploadData.file_path || uploadData.files_uploaded?.[0] || folderName;

            // Auto-complete compose_idea action
            await fetch(`/api/workflow/${this.workflowName}/action`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'compose_idea',
                    status: 'done',
                    deliverables: [filePath, folderName]
                }),
                signal: this.abortController.signal
            });

            this.onComplete({ file: filePath, folder: folderName });
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
        this.submitBtn.textContent = submitting ? 'Submitting...' : 'Submit Idea';
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
}
