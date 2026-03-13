/**
 * FEATURE-049-D: KB Article Editor
 * Modal-based markdown editor for creating and editing Knowledge Base articles.
 * Reuses compose-idea-modal pattern with EasyMDE and frontmatter tag chips.
 */
class KBArticleEditor {
    static CLOSE_ANIMATION_MS = 300;
    static TOAST_DURATION_MS = 4000;
    static MAX_FILENAME_LENGTH = 60;

    constructor(options = {}) {
        this.folder = options.folder || '';
        this.editPath = options.editPath || null;
        this.editMode = !!this.editPath;
        this.onComplete = options.onComplete || (() => {});
        this.onClose = options.onClose || null;
        
        this.overlay = null;
        this.container = null;
        this.embedded = false;
        this.easyMDE = null;
        this.dirty = false;
        this.config = { lifecycle: [], domain: [] };
        this.selectedTags = { lifecycle: new Set(), domain: new Set() };
    }

    async open() {
        await this._loadConfig();
        this._createDOM();
        this._bindEvents();
        document.body.appendChild(this.overlay);
        document.body.style.overflow = 'hidden';
        
        requestAnimationFrame(() => {
            this.overlay.classList.add('active');
            this._initEasyMDE();
            if (this.editMode) {
                this._loadExisting();
            }
        });
    }

    async openInContainer(container) {
        this.embedded = true;
        this.container = container;
        await this._loadConfig();
        this._createEmbeddedDOM(container);
        this._bindEvents();
        requestAnimationFrame(() => {
            this._initEasyMDE();
            if (this.editMode) {
                this._loadExisting();
            }
        });
    }

    async close(force = false) {
        if (!force && this.dirty) {
            const discard = await showConfirmModal('Discard Changes', 'Discard unsaved changes?', { danger: true, confirmLabel: 'Discard' });
            if (!discard) return;
        }
        this._cleanup();
        if (this.embedded) {
            if (this.container) this.container.innerHTML = '';
            if (this.onClose) this.onClose();
        } else {
            this.overlay.classList.remove('active');
            document.body.style.overflow = '';
            setTimeout(() => {
                if (this.overlay && this.overlay.parentNode) {
                    this.overlay.remove();
                }
            }, KBArticleEditor.CLOSE_ANIMATION_MS);
        }
    }

    async _loadConfig() {
        try {
            const res = await fetch('/api/kb/config');
            if (res.ok) {
                const data = await res.json();
                this.config.lifecycle = data.tags?.lifecycle || [];
                this.config.domain = data.tags?.domain || [];
            }
        } catch (e) {
            console.error('Failed to load KB config:', e);
        }
    }

    _createDOM() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'kb-editor-overlay';
        this.overlay.innerHTML = `
            <div class="kb-editor-modal">
                ${this._editorInnerHTML()}
            </div>
        `;
    }

    _createEmbeddedDOM(container) {
        container.innerHTML = `<div class="kb-editor-embedded">${this._editorInnerHTML()}</div>`;
        this.overlay = container.querySelector('.kb-editor-embedded');
    }

    _editorInnerHTML() {
        return `
                <div class="kb-editor-header">
                    <h3>${this.editMode ? '✏️ Edit Article' : '📝 New Article'}</h3>
                    <button class="kb-editor-close" title="Close">&times;</button>
                </div>
                <div class="kb-editor-body">
                    <div class="kb-editor-form">
                        <div class="kb-editor-field">
                            <label>Title <span class="kb-required">*</span></label>
                            <input type="text" class="kb-editor-title" placeholder="Article title...">
                        </div>
                        <div class="kb-editor-field">
                            <label>Lifecycle Tags</label>
                            <div class="kb-tag-chips kb-tag-lifecycle">
                                ${this.config.lifecycle.map(t => 
                                    `<span class="kb-chip kb-chip-lifecycle" data-tag="${t}" data-type="lifecycle">▸ ${t}</span>`
                                ).join('')}
                            </div>
                        </div>
                        <div class="kb-editor-field">
                            <label>Domain Tags</label>
                            <div class="kb-tag-chips kb-tag-domain">
                                ${this.config.domain.map(t => 
                                    `<span class="kb-chip kb-chip-domain" data-tag="${t}" data-type="domain"># ${t}</span>`
                                ).join('')}
                            </div>
                        </div>
                    </div>
                    <div class="kb-editor-content">
                        <textarea class="kb-editor-textarea" placeholder="Write your article in Markdown..."></textarea>
                    </div>
                </div>
                <div class="kb-editor-footer">
                    <span class="kb-editor-toast"></span>
                    <button class="kb-editor-btn kb-editor-btn-cancel">Cancel</button>
                    <button class="kb-editor-btn kb-editor-btn-save" disabled>
                        ${this.editMode ? 'Update Article' : 'Save Article'}
                    </button>
                </div>`;
    }

    _bindEvents() {
        this.overlay.querySelector('.kb-editor-close').addEventListener('click', () => this.close());
        this.overlay.querySelector('.kb-editor-btn-cancel').addEventListener('click', () => this.close());
        this.overlay.querySelector('.kb-editor-btn-save').addEventListener('click', () => this._save());
        
        // Backdrop click
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.close();
        });
        
        // Escape key
        this._escHandler = (e) => {
            if (e.key === 'Escape') this.close();
        };
        document.addEventListener('keydown', this._escHandler);
        
        // Title input
        const titleInput = this.overlay.querySelector('.kb-editor-title');
        titleInput.addEventListener('input', () => {
            this.dirty = true;
            this._updateSaveState();
        });
        
        // Tag chips
        this.overlay.querySelectorAll('.kb-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                const tag = chip.dataset.tag;
                const type = chip.dataset.type;
                if (this.selectedTags[type].has(tag)) {
                    this.selectedTags[type].delete(tag);
                    chip.classList.remove('active');
                } else {
                    this.selectedTags[type].add(tag);
                    chip.classList.add('active');
                }
                this.dirty = true;
            });
        });
    }

    _initEasyMDE() {
        const textarea = this.overlay.querySelector('.kb-editor-textarea');
        if (!textarea || typeof EasyMDE === 'undefined') return;

        this.easyMDE = new EasyMDE({
            element: textarea,
            autofocus: false,
            spellChecker: false,
            placeholder: 'Write your article in Markdown...',
            toolbar: [
                'bold', 'italic', 'heading', '|',
                'unordered-list', 'ordered-list', '|',
                'link', 'code', '|',
                'preview'
            ],
            status: false,
            minHeight: '250px'
        });

        this.easyMDE.codemirror.on('change', () => {
            this.dirty = true;
            this._updateSaveState();
        });
    }

    async _loadExisting() {
        try {
            const res = await fetch(`/api/kb/files/${encodeURIComponent(this.editPath)}`);
            if (!res.ok) throw new Error('Failed to load article');
            const data = await res.json();
            
            // Parse frontmatter from content
            const { frontmatter, body } = this._parseFrontmatter(data.content || '');
            
            // Populate form
            const titleInput = this.overlay.querySelector('.kb-editor-title');
            titleInput.value = frontmatter.title || '';
            
            // Set tags
            if (frontmatter.tags) {
                (frontmatter.tags.lifecycle || []).forEach(t => {
                    this.selectedTags.lifecycle.add(t);
                    const chip = this.overlay.querySelector(`.kb-chip-lifecycle[data-tag="${t}"]`);
                    if (chip) chip.classList.add('active');
                });
                (frontmatter.tags.domain || []).forEach(t => {
                    this.selectedTags.domain.add(t);
                    const chip = this.overlay.querySelector(`.kb-chip-domain[data-tag="${t}"]`);
                    if (chip) chip.classList.add('active');
                });
            }
            
            // Set content
            if (this.easyMDE) {
                this.easyMDE.value(body);
            }
            
            this.dirty = false;
            this._updateSaveState();
        } catch (e) {
            this._showToast('Failed to load article', 'error');
        }
    }

    _parseFrontmatter(content) {
        const match = content.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
        if (!match) return { frontmatter: {}, body: content };
        
        try {
            const frontmatter = {};
            const lines = match[1].split('\n');
            let currentKey = null;
            let inList = false;
            let listKey = null;
            
            for (const line of lines) {
                const kvMatch = line.match(/^(\w+):\s*(.*)$/);
                if (kvMatch && !line.startsWith('  ')) {
                    currentKey = kvMatch[1];
                    const val = kvMatch[2].trim();
                    if (val === '' || val === '{}') {
                        frontmatter[currentKey] = {};
                    } else {
                        frontmatter[currentKey] = val;
                    }
                    inList = false;
                } else if (line.match(/^\s+(\w+):/) && currentKey === 'tags') {
                    const tagMatch = line.match(/^\s+(\w+):\s*$/);
                    if (tagMatch) {
                        listKey = tagMatch[1];
                        if (!frontmatter.tags || typeof frontmatter.tags !== 'object') frontmatter.tags = {};
                        frontmatter.tags[listKey] = [];
                        inList = true;
                    }
                } else if (inList && line.match(/^\s+- /)) {
                    const item = line.replace(/^\s+- /, '').trim();
                    if (frontmatter.tags && listKey) {
                        frontmatter.tags[listKey].push(item);
                    }
                }
            }
            
            return { frontmatter, body: match[2] };
        } catch {
            return { frontmatter: {}, body: content };
        }
    }

    _buildFrontmatter() {
        const title = this.overlay.querySelector('.kb-editor-title').value.trim();
        const today = new Date().toISOString().split('T')[0];
        
        let fm = '---\n';
        fm += `title: "${title}"\n`;
        fm += `author: user\n`;
        fm += `created: "${today}"\n`;
        fm += `auto_generated: false\n`;
        
        const lifecycle = Array.from(this.selectedTags.lifecycle);
        const domain = Array.from(this.selectedTags.domain);
        
        if (lifecycle.length > 0 || domain.length > 0) {
            fm += 'tags:\n';
            if (lifecycle.length > 0) {
                fm += '  lifecycle:\n';
                lifecycle.forEach(t => { fm += `    - ${t}\n`; });
            }
            if (domain.length > 0) {
                fm += '  domain:\n';
                domain.forEach(t => { fm += `    - ${t}\n`; });
            }
        }
        
        fm += '---\n';
        return fm;
    }

    async _save() {
        const title = this.overlay.querySelector('.kb-editor-title').value.trim();
        if (!title) return;
        
        const saveBtn = this.overlay.querySelector('.kb-editor-btn-save');
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';
        
        const fullContent = this._buildContent();
        
        try {
            const res = this.editMode
                ? await this._putArticle(fullContent)
                : await this._postArticle(title, fullContent);
            
            if (res.ok) {
                document.dispatchEvent(new CustomEvent('kb:changed'));
                this.dirty = false;
                this.onComplete();
                this.close(true);
            } else {
                const err = await res.json();
                this._showToast(err.error || 'Save failed', 'error');
                this._resetSaveButton(saveBtn);
            }
        } catch (e) {
            this._showToast('Save failed: ' + e.message, 'error');
            this._resetSaveButton(saveBtn);
        }
    }

    _buildContent() {
        const frontmatter = this._buildFrontmatter();
        const body = this.easyMDE ? this.easyMDE.value() : '';
        return frontmatter + '\n' + body;
    }

    _postArticle(title, content) {
        const filename = this._sanitizeFilename(title) + '.md';
        return fetch('/api/kb/files', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ folder: this.folder, filename, content })
        });
    }

    _putArticle(content) {
        return fetch(`/api/kb/files/${encodeURIComponent(this.editPath)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
    }

    _resetSaveButton(saveBtn) {
        saveBtn.disabled = false;
        saveBtn.textContent = this.editMode ? 'Update Article' : 'Save Article';
    }

    _sanitizeFilename(title) {
        return title
            .toLowerCase()
            .replace(/[^a-z0-9\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .substring(0, KBArticleEditor.MAX_FILENAME_LENGTH);
    }

    _updateSaveState() {
        const title = this.overlay.querySelector('.kb-editor-title').value.trim();
        const saveBtn = this.overlay.querySelector('.kb-editor-btn-save');
        saveBtn.disabled = !title;
    }

    _showToast(message, type = 'info') {
        const toast = this.overlay.querySelector('.kb-editor-toast');
        toast.textContent = message;
        toast.className = `kb-editor-toast kb-toast-${type}`;
        setTimeout(() => { toast.textContent = ''; toast.className = 'kb-editor-toast'; }, KBArticleEditor.TOAST_DURATION_MS);
    }

    _cleanup() {
        if (this.easyMDE) {
            this.easyMDE.toTextArea();
            this.easyMDE = null;
        }
        if (this._escHandler) {
            document.removeEventListener('keydown', this._escHandler);
            this._escHandler = null;
        }
    }
}
