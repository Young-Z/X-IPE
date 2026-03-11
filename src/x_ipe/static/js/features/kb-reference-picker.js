/**
 * FEATURE-049-G: KB Reference Picker Modal
 * Cross-workflow modal for selecting KB articles/folders as references.
 * Supports search, tag filters, multi-select, clipboard copy, and insert.
 */
class KBReferencePicker {
    static DEBOUNCE_MS = 300;
    static ANIMATION_MS = 300;
    static COPY_FEEDBACK_MS = 1500;
    static API = Object.freeze({
        TREE: '/api/kb/tree',
        CONFIG: '/api/kb/config',
        FILES: '/api/kb/files',
        SEARCH: '/api/kb/search',
    });

    constructor(options = {}) {
        this.onInsert = options.onInsert || null;
        this.overlay = null;
        this.tree = [];
        this.files = [];
        this.config = { lifecycle: [], domain: [] };
        this.selected = new Set();
        this.searchQuery = '';
        this.activeTagFilters = new Set();
        this._debounceTimer = null;
    }

    async open() {
        await Promise.all([this._loadTree(), this._loadConfig(), this._loadFiles()]);
        this._createModal();
        document.body.style.overflow = 'hidden';
        requestAnimationFrame(() => {
            if (this.overlay) this.overlay.classList.add('active');
        });
    }

    close() {
        if (!this.overlay) return;
        clearTimeout(this._debounceTimer);
        this._debounceTimer = null;
        this.overlay.classList.remove('active');
        setTimeout(() => {
            if (this.overlay?.parentNode) this.overlay.parentNode.removeChild(this.overlay);
            this.overlay = null;
            document.body.style.overflow = '';
        }, KBReferencePicker.ANIMATION_MS);
    }

    async _loadTree() {
        try {
            const res = await fetch(KBReferencePicker.API.TREE);
            if (res.ok) {
                const data = await res.json();
                this.tree = data.tree || [];
            }
        } catch { /* graceful degradation */ }
    }

    async _loadConfig() {
        try {
            const res = await fetch(KBReferencePicker.API.CONFIG);
            if (res.ok) {
                const data = await res.json();
                this.config.lifecycle = data.tags?.lifecycle || [];
                this.config.domain = data.tags?.domain || [];
            }
        } catch { /* graceful degradation */ }
    }

    async _loadFiles() {
        try {
            let url = KBReferencePicker.API.FILES;
            if (this.searchQuery) {
                url = `${KBReferencePicker.API.SEARCH}?q=${encodeURIComponent(this.searchQuery)}`;
            }
            const res = await fetch(url);
            if (res.ok) {
                const data = await res.json();
                this.files = data.files || data.results || [];
            }
        } catch { this.files = []; }
    }

    _createModal() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'kb-ref-overlay';

        const searchValue = this._escapeAttr(this.searchQuery);
        this.overlay.innerHTML = `
            <div class="kb-ref-modal">
                <div class="kb-ref-header">
                    <h3>📎 Reference Picker</h3>
                    <button class="kb-ref-close">&times;</button>
                </div>
                <div class="kb-ref-toolbar">
                    <div class="kb-ref-search">
                        <i class="bi bi-search"></i>
                        <input type="text" class="kb-ref-search-input" placeholder="Search KB..." value="${searchValue}">
                    </div>
                </div>
                <div class="kb-ref-filters">
                    ${this._renderFilterChips()}
                </div>
                <div class="kb-ref-body">
                    <div class="kb-ref-tree-panel">
                        ${this._renderTreePanel()}
                    </div>
                    <div class="kb-ref-list-panel">
                        ${this._renderFileList()}
                    </div>
                </div>
                <div class="kb-ref-footer">
                    <span class="kb-ref-count">${this.selected.size} selected</span>
                    <div class="kb-ref-actions">
                        <button class="kb-ref-copy-btn" title="Copy paths to clipboard">📋 Copy</button>
                        <button class="kb-ref-insert-btn" title="Insert references">Insert</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(this.overlay);
        this._bindEvents();
    }

    _renderFilterChips() {
        const lifecycle = this.config.lifecycle.map(t =>
            `<span class="kb-ref-chip kb-ref-chip-lifecycle" data-tag="${this._escapeAttr(t)}">▸ ${this._escapeHtml(t)}</span>`
        ).join('');
        const domain = this.config.domain.map(t =>
            `<span class="kb-ref-chip kb-ref-chip-domain" data-tag="${this._escapeAttr(t)}"># ${this._escapeHtml(t)}</span>`
        ).join('');
        return lifecycle + domain;
    }

    _renderTreePanel() {
        if (!this.tree.length) return '<div class="kb-ref-tree-empty">No folders</div>';
        return this._renderTreeNodes(this.tree, 'knowledge-base');
    }

    _renderTreeNodes(nodes, prefix) {
        let html = '';
        for (const node of nodes) {
            const path = prefix ? `${prefix}/${node.name}` : node.name;
            if (node.type === 'folder') {
                const checked = this.selected.has(path) ? 'checked' : '';
                const safePath = this._escapeAttr(path);
                html += `
                    <div class="kb-ref-tree-folder">
                        <label class="kb-ref-tree-item">
                            <input type="checkbox" class="kb-ref-check" data-path="${safePath}" data-type="folder" ${checked}>
                            📁 ${this._escapeHtml(node.name)}
                        </label>
                        <div class="kb-ref-tree-children">${this._renderTreeNodes(node.children || [], path)}</div>
                    </div>
                `;
            }
        }
        return html;
    }

    _renderFileList() {
        let filtered = [...this.files];

        if (this.activeTagFilters.size > 0) {
            filtered = filtered.filter(f => {
                const fileTags = [
                    ...(f.frontmatter?.tags?.lifecycle || []),
                    ...(f.frontmatter?.tags?.domain || [])
                ];
                return Array.from(this.activeTagFilters).some(t => fileTags.includes(t));
            });
        }

        if (!filtered.length) return '<div class="kb-ref-list-empty">No files found</div>';

        return filtered.map(f => {
            const title = f.frontmatter?.title || f.name;
            const checked = this.selected.has(f.path) ? 'checked' : '';
            const safePath = this._escapeAttr(f.path);
            const lifecycleTags = (f.frontmatter?.tags?.lifecycle || []).map(t =>
                `<span class="kb-tag-pill kb-tag-lifecycle">▸ ${this._escapeHtml(t)}</span>`
            ).join('');
            const domainTags = (f.frontmatter?.tags?.domain || []).map(t =>
                `<span class="kb-tag-pill kb-tag-domain"># ${this._escapeHtml(t)}</span>`
            ).join('');

            return `
                <label class="kb-ref-file-item">
                    <input type="checkbox" class="kb-ref-check" data-path="${safePath}" data-type="file" ${checked}>
                    <div class="kb-ref-file-info">
                        <span class="kb-ref-file-name">${this._escapeHtml(title)}</span>
                        <div class="kb-ref-file-tags">${lifecycleTags}${domainTags}</div>
                    </div>
                </label>
            `;
        }).join('');
    }

    _bindEvents() {
        this.overlay.querySelector('.kb-ref-close').addEventListener('click', () => this.close());
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.close();
        });

        const searchInput = this.overlay.querySelector('.kb-ref-search-input');
        searchInput.addEventListener('input', () => {
            clearTimeout(this._debounceTimer);
            this._debounceTimer = setTimeout(async () => {
                this.searchQuery = searchInput.value.trim();
                await this._loadFiles();
                this._refreshFileList();
            }, KBReferencePicker.DEBOUNCE_MS);
        });

        this.overlay.querySelectorAll('.kb-ref-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                const tag = chip.dataset.tag;
                if (this.activeTagFilters.has(tag)) {
                    this.activeTagFilters.delete(tag);
                    chip.classList.remove('active');
                } else {
                    this.activeTagFilters.add(tag);
                    chip.classList.add('active');
                }
                this._refreshFileList();
            });
        });

        this.overlay.addEventListener('change', (e) => {
            if (e.target.classList.contains('kb-ref-check')) {
                const path = e.target.dataset.path;
                if (e.target.checked) {
                    this.selected.add(path);
                } else {
                    this.selected.delete(path);
                }
                this._updateCount();
            }
        });

        this.overlay.querySelector('.kb-ref-copy-btn').addEventListener('click', async () => {
            const paths = Array.from(this.selected).join('\n');
            try {
                await navigator.clipboard.writeText(paths);
                const btn = this.overlay.querySelector('.kb-ref-copy-btn');
                btn.textContent = '✅ Copied!';
                setTimeout(() => { btn.textContent = '📋 Copy'; }, KBReferencePicker.COPY_FEEDBACK_MS);
            } catch {
                const ta = document.createElement('textarea');
                ta.value = paths;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
            }
        });

        this.overlay.querySelector('.kb-ref-insert-btn').addEventListener('click', () => {
            const paths = Array.from(this.selected);
            if (this.onInsert) this.onInsert(paths);
            document.dispatchEvent(new CustomEvent('kb:references-inserted', { detail: { paths } }));
            this.close();
        });
    }

    _refreshFileList() {
        const panel = this.overlay?.querySelector('.kb-ref-list-panel');
        if (panel) panel.innerHTML = this._renderFileList();
    }

    _updateCount() {
        const countEl = this.overlay?.querySelector('.kb-ref-count');
        if (countEl) countEl.textContent = `${this.selected.size} selected`;
    }

    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    _escapeAttr(str) {
        return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
}
