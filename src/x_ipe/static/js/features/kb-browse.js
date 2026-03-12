/**
 * FEATURE-049-C: KB Browse & Search View
 * Grid-based article browser with search, sort, and tag filtering.
 */

const DEBOUNCE_MS = 300;
const SNIPPET_MAX_CHARS = 100;

class KBBrowseView {
    constructor(container) {
        this.container = typeof container === 'string' ? document.getElementById(container) : container;
        this.folder = '';
        this.sort = 'modified_desc';
        this.searchQuery = '';
        this.activeTagFilters = new Set();
        this.showUntaggedOnly = false;
        this.config = { lifecycle: [], domain: [] };
        this.files = [];
        this._debounceTimer = null;
        
        this._onKbChanged = () => this.refresh();
        document.addEventListener('kb:changed', this._onKbChanged);
    }

    destroy() {
        document.removeEventListener('kb:changed', this._onKbChanged);
        clearTimeout(this._debounceTimer);
        if (this.container) this.container.innerHTML = '';
    }

    async render(folder = '') {
        this.folder = folder;
        if (!this.container) return;
        
        await this._loadConfig();
        await this._loadFiles();
        this._renderUI();
    }

    async refresh() {
        await this._loadFiles();
        this._renderCards();
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

    async _loadFiles() {
        try {
            let url = `/api/kb/files?sort=${this.sort}`;
            if (this.folder) url += `&folder=${encodeURIComponent(this.folder)}`;
            
            if (this.searchQuery) {
                url = `/api/kb/search?q=${encodeURIComponent(this.searchQuery)}`;
                const activeTags = Array.from(this.activeTagFilters);
                if (activeTags.length > 0) {
                    url += `&tag=${encodeURIComponent(activeTags[0])}`;
                }
            }
            
            const res = await fetch(url);
            if (res.ok) {
                const data = await res.json();
                this.files = data.files || data.results || [];
            }
        } catch (e) {
            console.error('Failed to load KB files:', e);
            this.files = [];
        }
    }

    _renderUI() {
        this.container.innerHTML = `
            <div class="kb-browse">
                <div class="kb-browse-header">
                    <h2>📚 Knowledge Base</h2>
                    <button class="kb-browse-new-btn" title="New Article">
                        <i class="bi bi-plus-lg"></i> New Article
                    </button>
                </div>
                <div class="kb-browse-toolbar">
                    <div class="kb-browse-search">
                        <i class="bi bi-search"></i>
                        <input type="text" class="kb-search-input" placeholder="Search articles..." value="${this.searchQuery}">
                    </div>
                    <select class="kb-sort-select">
                        <option value="modified_desc" ${this.sort === 'modified_desc' ? 'selected' : ''}>Last Modified</option>
                        <option value="name_asc" ${this.sort === 'name_asc' ? 'selected' : ''}>Name A→Z</option>
                        <option value="created_desc" ${this.sort === 'created_desc' ? 'selected' : ''}>Date Created</option>
                        <option value="untagged_first" ${this.sort === 'untagged_first' ? 'selected' : ''}>Untagged First</option>
                    </select>
                </div>
                <div class="kb-browse-filters">
                    <span class="kb-filter-chip kb-filter-untagged ${this.showUntaggedOnly ? 'active' : ''}" data-filter="untagged">⚠ Untagged</span>
                    ${this.config.lifecycle.map(t => 
                        `<span class="kb-filter-chip kb-filter-lifecycle ${this.activeTagFilters.has(t) ? 'active' : ''}" data-filter="${t}" data-type="lifecycle">▸ ${t}</span>`
                    ).join('')}
                    ${this.config.domain.map(t => 
                        `<span class="kb-filter-chip kb-filter-domain ${this.activeTagFilters.has(t) ? 'active' : ''}" data-filter="${t}" data-type="domain"># ${t}</span>`
                    ).join('')}
                </div>
                <div class="kb-browse-grid"></div>
            </div>
        `;
        
        this._bindBrowseEvents();
        this._renderCards();
    }

    _renderCards() {
        const grid = this.container.querySelector('.kb-browse-grid');
        if (!grid) return;
        
        let filtered = [...this.files];
        
        // Client-side tag filtering
        if (this.activeTagFilters.size > 0) {
            filtered = filtered.filter(f => {
                const fileTags = [
                    ...(f.frontmatter?.tags?.lifecycle || []),
                    ...(f.frontmatter?.tags?.domain || [])
                ];
                return Array.from(this.activeTagFilters).some(t => fileTags.includes(t));
            });
        }
        
        // Untagged filter
        if (this.showUntaggedOnly) {
            filtered = filtered.filter(f => {
                const lc = f.frontmatter?.tags?.lifecycle || [];
                const dm = f.frontmatter?.tags?.domain || [];
                return lc.length === 0 && dm.length === 0;
            });
        }
        
        if (filtered.length === 0) {
            grid.innerHTML = `
                <div class="kb-browse-empty">
                    <p>📖 No articles yet — create one!</p>
                    <button class="kb-browse-create-btn">Create Article</button>
                </div>
            `;
            const createBtn = grid.querySelector('.kb-browse-create-btn');
            if (createBtn) {
                createBtn.addEventListener('click', () => this._openEditor());
            }
            return;
        }
        
        grid.innerHTML = filtered.map(f => this._renderCard(f)).join('');
        
        // Card click events
        grid.querySelectorAll('.kb-card').forEach(card => {
            card.addEventListener('click', () => {
                const path = card.dataset.path;
                if (window.contentRenderer) {
                    window.contentRenderer.load(path);
                }
                document.dispatchEvent(new CustomEvent('fileSelected', { detail: { path } }));
            });
        });
    }

    _renderCard(file) {
        const title = file.frontmatter?.title || file.name;
        const snippet = (file.content_preview || '').substring(0, SNIPPET_MAX_CHARS);
        const mtime = file.mtime ? new Date(file.mtime * 1000).toLocaleDateString() : 
                      file.modified_date ? new Date(file.modified_date).toLocaleDateString() : '';
        let lifecycleTags = file.frontmatter?.tags?.lifecycle || [];
        if (typeof lifecycleTags === 'string') lifecycleTags = [lifecycleTags];
        let domainTags = file.frontmatter?.tags?.domain || [];
        if (typeof domainTags === 'string') domainTags = [domainTags];
        const hasNoTags = lifecycleTags.length === 0 && domainTags.length === 0;
        
        return `
            <div class="kb-card" data-path="${file.path}">
                <div class="kb-card-title">${this._escapeHtml(title)}</div>
                ${snippet ? `<div class="kb-card-snippet">${this._escapeHtml(snippet)}</div>` : ''}
                <div class="kb-card-tags">
                    ${lifecycleTags.map(t => `<span class="kb-tag-pill kb-tag-lifecycle">▸ ${this._escapeHtml(t)}</span>`).join('')}
                    ${domainTags.map(t => `<span class="kb-tag-pill kb-tag-domain"># ${this._escapeHtml(t)}</span>`).join('')}
                    ${hasNoTags ? '<span class="kb-tag-badge-untagged">Needs Tags</span>' : ''}
                </div>
                <div class="kb-card-meta">${mtime}</div>
            </div>
        `;
    }

    _bindBrowseEvents() {
        // Search input with debounce
        const searchInput = this.container.querySelector('.kb-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                clearTimeout(this._debounceTimer);
                this._debounceTimer = setTimeout(async () => {
                    this.searchQuery = searchInput.value.trim();
                    await this._loadFiles();
                    this._renderCards();
                }, DEBOUNCE_MS);
            });
        }
        
        // Sort dropdown
        const sortSelect = this.container.querySelector('.kb-sort-select');
        if (sortSelect) {
            sortSelect.addEventListener('change', async () => {
                this.sort = sortSelect.value;
                await this._loadFiles();
                this._renderCards();
            });
        }
        
        // Tag filter chips
        this.container.querySelectorAll('.kb-filter-chip').forEach(chip => {
            chip.addEventListener('click', async () => {
                const filter = chip.dataset.filter;
                if (filter === 'untagged') {
                    this.showUntaggedOnly = !this.showUntaggedOnly;
                    chip.classList.toggle('active');
                } else {
                    if (this.activeTagFilters.has(filter)) {
                        this.activeTagFilters.delete(filter);
                        chip.classList.remove('active');
                    } else {
                        this.activeTagFilters.add(filter);
                        chip.classList.add('active');
                    }
                }
                this._renderCards();
            });
        });
        
        // New Article button
        const newBtn = this.container.querySelector('.kb-browse-new-btn');
        if (newBtn) {
            newBtn.addEventListener('click', () => this._openEditor());
        }
    }

    _openEditor() {
        if (typeof KBArticleEditor !== 'undefined') {
            const editor = new KBArticleEditor({
                folder: this.folder,
                onComplete: () => this.refresh()
            });
            editor.open();
        }
    }

    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}
