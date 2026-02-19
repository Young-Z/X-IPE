/**
 * FEATURE-025-E: KB Search & Preview
 *
 * Search modal (Cmd+K), preview panel, sidebar search highlighting,
 * and filter chips for the Knowledge Base.
 */

const kbSearch = {
    modal: null,
    previewPanel: null,
    activeResultIndex: -1,
    results: [],
    debounceTimer: null,
    recentItems: [],
    activeFilters: { types: [], topic: null },

    /* ── Initialisation ─────────────────────────────────────── */

    init() {
        this.activeResultIndex = -1;
        this.results = [];
        this.activeFilters = { types: [], topic: null };
        this._bindGlobalKeys();
    },

    _bindGlobalKeys() {
        document.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                this.openModal();
            }
            if (e.key === 'Escape' && this.modal?.classList.contains('active')) {
                this.closeModal();
            }
        });
    },

    /* ── Search Modal ───────────────────────────────────────── */

    _createModalDOM() {
        if (this.modal) return;
        const div = document.createElement('div');
        div.id = 'kb-search-modal';
        div.className = 'kb-search-modal';
        div.innerHTML = `
            <div class="kb-search-modal-content">
                <div class="kb-search-modal-header">
                    <i class="bi bi-search"></i>
                    <input type="text" placeholder="Search knowledge base..." autocomplete="off">
                    <kbd>ESC</kbd>
                </div>
                <div class="kb-search-filter-bar"></div>
                <div class="kb-search-modal-body"></div>
                <div class="kb-search-modal-footer">
                    <span><kbd>↑</kbd> <kbd>↓</kbd> to navigate</span>
                    <span><kbd>Enter</kbd> to select</span>
                </div>
            </div>
        `;
        document.body.appendChild(div);
        this.modal = div;

        // Backdrop click closes
        div.addEventListener('click', (e) => {
            if (e.target === div) this.closeModal();
        });

        // Input events
        const input = div.querySelector('input');
        input.addEventListener('input', () => this._onSearchInput(input.value));
        input.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown') { e.preventDefault(); this._navigateResults(1); }
            if (e.key === 'ArrowUp') { e.preventDefault(); this._navigateResults(-1); }
            if (e.key === 'Enter') { e.preventDefault(); this._selectActiveResult(); }
        });
    },

    openModal() {
        this._createModalDOM();
        this.modal.classList.add('active');
        this.activeResultIndex = -1;
        this.activeFilters = { types: [], topic: null };
        const input = this.modal.querySelector('input');
        if (input) {
            input.value = '';
            setTimeout(() => input.focus(), 50);
        }
        this._renderFilterChips();
        this._renderResults({ files: [], topics: [], summaries: [] });
    },

    closeModal() {
        if (this.modal) this.modal.classList.remove('active');
        this.activeResultIndex = -1;
    },

    _onSearchInput(value) {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => this._fetchResults(value), 300);
    },

    async _fetchResults(query) {
        const params = new URLSearchParams();
        if (query) params.set('q', query);
        const typeFilters = this.activeFilters.types;
        if (typeFilters.length === 1) params.set('type', typeFilters[0]);
        if (this.activeFilters.topic) params.set('topic', this.activeFilters.topic);

        // If no params at all, don't call
        if (!params.toString()) {
            this._renderResults({ files: [], topics: [], summaries: [] });
            return;
        }

        try {
            const resp = await fetch(`/api/kb/search?${params}`);
            if (!resp.ok) return;
            const data = await resp.json();
            let grouped = data.results || { files: [], topics: [], summaries: [] };

            // Client-side multi-type filter (API only supports single type)
            if (typeFilters.length > 1) {
                grouped.files = grouped.files.filter(f => typeFilters.includes(f.type));
            }

            this._renderResults(grouped, query);
        } catch (_) { /* ignore network errors */ }
    },

    _renderResults(grouped, query) {
        const body = this.modal?.querySelector('.kb-search-modal-body');
        if (!body) return;

        this.results = [];
        const sections = [];

        const addSection = (title, items, type) => {
            if (!items || items.length === 0) return;
            sections.push(`<div class="search-section-title">${title}</div>`);
            items.forEach((item) => {
                const idx = this.results.length;
                this.results.push({ ...item, _type: type });
                const icon = type === 'topic' ? 'bi-folder'
                    : type === 'summary' ? 'bi-file-text'
                    : this._fileIcon(item.type);
                const title = type === 'topic' ? item.name
                    : type === 'summary' ? `${item.topic} — ${item.version}`
                    : item.name;
                const path = type === 'topic' ? `topics / ${item.name} (${item.file_count} items)`
                    : type === 'summary' ? item.path
                    : item.path;
                sections.push(`
                    <div class="search-result" data-idx="${idx}">
                        <div class="search-result-icon"><i class="bi ${icon}"></i></div>
                        <div class="search-result-content">
                            <div class="search-result-title">${query ? this._highlightMatch(title, query) : title}</div>
                            <div class="search-result-path">${path}</div>
                        </div>
                    </div>
                `);
            });
        };

        addSection('Files', grouped.files, 'file');
        addSection('Topics', grouped.topics, 'topic');
        addSection('Summaries', grouped.summaries, 'summary');

        if (sections.length === 0) {
            body.innerHTML = '<div class="search-no-results">No results found</div>';
        } else {
            body.innerHTML = sections.join('');
        }

        // Click handlers on results
        body.querySelectorAll('.search-result').forEach(el => {
            el.addEventListener('click', () => {
                const idx = parseInt(el.dataset.idx, 10);
                this._selectResult(this.results[idx]);
            });
        });

        this.activeResultIndex = -1;
    },

    _highlightMatch(text, query) {
        if (!query) return text;
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        const result = text.replace(regex, '<span class="search-result-highlight">$1</span>');
        return result;
    },

    _navigateResults(direction) {
        const newIdx = this.activeResultIndex + direction;
        if (newIdx < -1) return;
        if (newIdx >= this.results.length) return;
        this.activeResultIndex = newIdx;

        // Update visual active state
        const items = this.modal?.querySelectorAll('.search-result');
        items?.forEach((el, i) => {
            el.classList.toggle('active', i === this.activeResultIndex);
        });
    },

    _selectActiveResult() {
        if (this.activeResultIndex >= 0 && this.activeResultIndex < this.results.length) {
            this._selectResult(this.results[this.activeResultIndex]);
        }
    },

    _selectResult(result) {
        if (!result) return;
        this.closeModal();
        if (result._type === 'file') {
            this.showPreview(result);
        } else if (result._type === 'topic' && window.kbTopics) {
            window.kbTopics.loadTopic(result.name);
        }
    },

    _fileIcon(type) {
        const icons = {
            pdf: 'bi-file-pdf',
            markdown: 'bi-markdown',
            code: 'bi-code-square',
            image: 'bi-file-image',
        };
        return icons[type] || 'bi-file-earmark';
    },

    /* ── Filter Chips ───────────────────────────────────────── */

    _toggleTypeFilter(type) {
        const idx = this.activeFilters.types.indexOf(type);
        if (idx >= 0) {
            this.activeFilters.types.splice(idx, 1);
        } else {
            this.activeFilters.types.push(type);
        }
    },

    _setTopicFilter(topic) {
        this.activeFilters.topic = topic;
    },

    _renderFilterChips() {
        const bar = this.modal?.querySelector('.kb-search-filter-bar');
        if (!bar) return;
        const types = ['pdf', 'markdown', 'code'];
        bar.innerHTML = types.map(t => {
            const active = this.activeFilters.types.includes(t) ? ' active' : '';
            return `<button class="kb-filter-chip${active}" data-type="${t}">${t.toUpperCase()}</button>`;
        }).join('');

        bar.querySelectorAll('.kb-filter-chip').forEach(btn => {
            btn.addEventListener('click', () => {
                this._toggleTypeFilter(btn.dataset.type);
                this._renderFilterChips();
                const input = this.modal.querySelector('input');
                this._onSearchInput(input?.value || '');
            });
        });
    },

    /* ── Preview Panel ──────────────────────────────────────── */

    _createPreviewDOM() {
        if (this.previewPanel) return;
        const container = document.querySelector('.kb-container') || document.getElementById('kb-container') || document.querySelector('.content-area');
        if (!container) return;

        const panel = document.createElement('aside');
        panel.id = 'kb-preview-panel';
        panel.className = 'kb-preview-panel';
        panel.style.display = 'none';
        panel.innerHTML = `
            <div class="kb-preview-header">
                <h6>Preview</h6>
                <button class="btn-close btn-close-white" id="btn-close-preview" aria-label="Close"></button>
            </div>
            <div class="kb-preview-content">
                <div class="kb-preview-thumbnail"><i class="bi bi-file-earmark"></i></div>
                <div class="kb-preview-info"></div>
                <div class="kb-preview-tags"></div>
            </div>
            <div class="kb-preview-actions">
                <button class="btn btn-primary btn-sm kb-preview-process"><i class="bi bi-cpu"></i> Process</button>
                <button class="btn btn-outline-light btn-sm kb-preview-open"><i class="bi bi-eye"></i> Open</button>
            </div>
        `;
        container.appendChild(panel);
        this.previewPanel = panel;

        panel.querySelector('#btn-close-preview').addEventListener('click', () => this.hidePreview());
    },

    showPreview(fileEntry) {
        this._createPreviewDOM();
        if (!this.previewPanel) return;

        const icon = this._fileIcon(fileEntry.type);
        const thumb = this.previewPanel.querySelector('.kb-preview-thumbnail');
        thumb.innerHTML = `<i class="bi ${icon}"></i>`;

        const info = this.previewPanel.querySelector('.kb-preview-info');
        const status = fileEntry.topic ? 'Processed' : 'Pending';
        const statusClass = fileEntry.topic ? 'text-success' : 'text-warning';
        info.innerHTML = `
            <div class="kb-preview-info-row"><span class="kb-preview-info-label">Name</span><span class="kb-preview-info-value">${fileEntry.name}</span></div>
            <div class="kb-preview-info-row"><span class="kb-preview-info-label">Type</span><span class="kb-preview-info-value">${(fileEntry.type || 'unknown').toUpperCase()}</span></div>
            <div class="kb-preview-info-row"><span class="kb-preview-info-label">Size</span><span class="kb-preview-info-value">${this._formatSize(fileEntry.size)}</span></div>
            <div class="kb-preview-info-row"><span class="kb-preview-info-label">Added</span><span class="kb-preview-info-value">${this._formatDate(fileEntry.created_date)}</span></div>
            <div class="kb-preview-info-row"><span class="kb-preview-info-label">Status</span><span class="kb-preview-info-value ${statusClass}">${status}</span></div>
        `;

        const tags = this.previewPanel.querySelector('.kb-preview-tags');
        tags.innerHTML = (fileEntry.keywords || [])
            .map(k => `<span class="kb-preview-tag">${k}</span>`)
            .join('');

        // Wire actions
        const processBtn = this.previewPanel.querySelector('.kb-preview-process');
        const openBtn = this.previewPanel.querySelector('.kb-preview-open');
        processBtn.onclick = () => this._onProcess(fileEntry.path);
        openBtn.onclick = () => this._onOpen(fileEntry.path);

        this.previewPanel.style.display = 'flex';
    },

    hidePreview() {
        if (this.previewPanel) this.previewPanel.style.display = 'none';
    },

    async _onProcess(filePath) {
        try {
            await fetch('/api/kb/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ paths: [filePath] }),
            });
        } catch (_) { /* ignore */ }
    },

    _onOpen(filePath) {
        if (window.kbCore?.showFilePreview) {
            window.kbCore.showFilePreview(filePath);
        }
    },

    /* ── Sidebar Search Enhancement ─────────────────────────── */

    enhanceSidebarSearch() {
        // Override kbCore's showFilePreview to use preview panel
        if (window.kbCore) {
            window.kbCore._originalShowFilePreview = window.kbCore.showFilePreview;
            window.kbCore.showFilePreview = (path) => {
                const file = window.kbCore.index?.files?.find(f => f.path === path);
                if (file) this.showPreview(file);
            };
        }
    },

    /* ── Utility ────────────────────────────────────────────── */

    _formatSize(bytes) {
        if (!bytes) return '0 B';
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    },

    _formatDate(isoStr) {
        if (!isoStr) return '—';
        try {
            return new Date(isoStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        } catch (_) { return isoStr; }
    },
};

window.kbSearch = kbSearch;
