/**
 * FEATURE-049-B / CR-002: KB Browse Modal — "Knowledge Atelier"
 * Full-featured KB interface matching mockup kb-interface-v1.html.
 * Scenes: Browse (grid/list), Article Detail, Intake placeholder.
 */
class KBBrowseModal {
    static ANIMATION_MS = 300;
    static API = Object.freeze({
        TREE: '/api/kb/tree',
        FILES: '/api/kb/files',
        CONFIG: '/api/kb/config',
    });
    static FOLDER_COLORS = [
        { bg: 'rgba(59,130,246,0.08)', color: '#3b82f6', accent: '#3b82f6', label: '#1e40af' },
        { bg: 'rgba(16,185,129,0.08)', color: '#10b981', accent: '#10b981', label: '#065f46' },
        { bg: 'rgba(245,158,11,0.08)', color: '#f59e0b', accent: '#f59e0b', label: '#92400e' },
        { bg: 'rgba(139,92,246,0.08)', color: '#8b5cf6', accent: '#8b5cf6', label: '#5b21b6' },
        { bg: 'rgba(236,72,153,0.08)', color: '#ec4899', accent: '#ec4899', label: '#9d174d' },
        { bg: 'rgba(100,116,139,0.08)', color: '#64748b', accent: '#64748b', label: '#334155' },
    ];

    constructor() {
        this.overlay = null;
        this.tree = [];
        this.files = [];
        this.config = { tags: { lifecycle: [], domain: [] } };
        this.currentScene = 'browse';
        this.currentArticle = null;
        this.viewMode = 'grid';
        this.sortBy = 'modified';
        this.searchQuery = '';
        this.lifecycleFilter = 'all';
        this.domainFilter = 'all';
        this.showUntaggedOnly = false;
        this.activeSidebarFolder = 'all';
        this.uploadFolder = '/';
        this.uploadMode = 'normal';
        this.intakeFilter = 'all';
        this._folderColorMap = {};
        this._expandedFolders = new Set();
        this._intakeItems = [];
        this._intakeStats = {};
        this._onKbChanged = () => { if (this.overlay) this._refreshData(); };
        document.addEventListener('kb:changed', this._onKbChanged);
    }

    // ─── Public API ────────────────────────────────
    async open() {
        if (this.overlay) return;
        await this._loadData();
        this._createModal();
        document.body.style.overflow = 'hidden';
        requestAnimationFrame(() => {
            if (this.overlay) this.overlay.classList.add('active');
        });
        // Load intake file count for badges
        this._refreshIntakeFiles();
    }

    close() {
        if (!this.overlay) return;
        this.overlay.classList.remove('active');
        setTimeout(() => {
            if (this.overlay?.parentNode) this.overlay.parentNode.removeChild(this.overlay);
            this.overlay = null;
            document.body.style.overflow = '';
        }, KBBrowseModal.ANIMATION_MS);
        if (this._escHandler) {
            document.removeEventListener('keydown', this._escHandler);
            this._escHandler = null;
        }
    }

    destroy() {
        document.removeEventListener('kb:changed', this._onKbChanged);
        this.close();
    }

    // ─── Data Loading ──────────────────────────────
    async _loadData() {
        const [treeRes, filesRes, configRes, intakeRes] = await Promise.allSettled([
            fetch(KBBrowseModal.API.TREE),
            fetch(`${KBBrowseModal.API.FILES}?recursive=true`),
            fetch(KBBrowseModal.API.CONFIG),
            fetch('/api/kb/intake'),
        ]);
        if (treeRes.status === 'fulfilled' && treeRes.value.ok) {
            const d = await treeRes.value.json();
            this.tree = d.tree || [];
        }
        if (filesRes.status === 'fulfilled' && filesRes.value.ok) {
            const d = await filesRes.value.json();
            this.files = d.files || [];
        }
        if (configRes.status === 'fulfilled' && configRes.value.ok) {
            const d = await configRes.value.json();
            this.config = d.config || d || { tags: { lifecycle: [], domain: [] } };
        }
        if (intakeRes.status === 'fulfilled' && intakeRes.value.ok) {
            const d = await intakeRes.value.json();
            this._intakeStats = d.stats || { total: 0, pending: 0, processing: 0, filed: 0 };
        } else {
            this._intakeStats = { total: 0, pending: 0, processing: 0, filed: 0 };
        }
        this._buildFolderColorMap();
    }

    async _refreshData() {
        await this._loadData();
        if (this.currentScene === 'browse') this._renderBrowseContent();
        this._renderSidebarFolders();
    }

    _buildFolderColorMap() {
        const folders = this._getFolderNames();
        folders.forEach((f, i) => {
            this._folderColorMap[f] = KBBrowseModal.FOLDER_COLORS[i % KBBrowseModal.FOLDER_COLORS.length];
        });
    }

    _getFolderNames() {
        const names = new Set();
        // Extract from tree API data (complete folder list)
        const walk = (nodes) => {
            for (const n of nodes) {
                if (n.type === 'folder') {
                    names.add(n.name);
                    if (n.children) walk(n.children);
                }
            }
        };
        walk(this.tree);
        // Fallback: also extract from file paths (exclude .intake)
        this.files.forEach(f => {
            const parts = f.path.split('/');
            if (parts.length > 1 && parts[0] !== '.intake') names.add(parts[0]);
        });
        return [...names].sort();
    }

    _getFolderColor(name) {
        return this._folderColorMap[name] || KBBrowseModal.FOLDER_COLORS[5];
    }

    // ─── Modal Creation ────────────────────────────
    _createModal() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'kb-modal-overlay';
        this.overlay.innerHTML = `
            <div class="kb-modal-dialog">
                <div class="kb-modal-header">
                    <div class="kb-modal-header-left">
                        <div class="kb-modal-header-title">
                            <i class="bi bi-book"></i> Knowledge Base
                        </div>
                    </div>
                    <div class="kb-modal-header-actions">
                        <button class="kb-modal-hdr-btn primary" data-action="new-article">
                            <i class="bi bi-plus-lg"></i> New Article
                        </button>
                        <button class="kb-modal-hdr-btn" data-action="reference-kb">
                            <i class="bi bi-link-45deg"></i> Reference KB
                        </button>
                        <button class="kb-modal-close" title="Close">&times;</button>
                    </div>
                </div>
                <div class="kb-modal-body">
                    <div class="kb-modal-sidebar">
                        <div class="kb-modal-sidebar-search">
                            <i class="bi bi-search"></i>
                            <input type="text" placeholder="Search KB…" data-role="sidebar-search" />
                        </div>
                        <div class="kb-modal-sidebar-content" data-role="sidebar-folders"></div>
                    </div>
                    <div class="kb-modal-content">
                        <div class="kb-scene active" data-scene="browse"></div>
                        <div class="kb-scene" data-scene="article"></div>
                        <div class="kb-scene" data-scene="edit"></div>
                        <div class="kb-scene" data-scene="intake"></div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(this.overlay);
        this._renderSidebarFolders();
        this._renderBrowseScene();
        this._bindEvents();
    }

    // ─── Sidebar ───────────────────────────────────
    _renderSidebarFolders() {
        const el = this.overlay?.querySelector('[data-role="sidebar-folders"]');
        if (!el) return;
        const folders = this._getFolderNames();
        const browseFiles = this.files.filter(f => !f.path.startsWith('.intake/') && !f.path.startsWith('.intake\\'));
        const totalFiles = browseFiles.length;

        let html = `
            <div class="kb-sidebar-section">
                <div class="kb-sidebar-section-header expanded">
                    <i class="bi bi-book section-icon" style="color:#10b981;"></i>
                    <span style="color:#fff;font-weight:600;">Knowledge Base</span>
                    <i class="bi bi-chevron-down chevron"></i>
                </div>
                <div class="kb-sidebar-section-content open">
                    <div class="kb-sidebar-folder${this.activeSidebarFolder === 'all' ? ' active' : ''}" data-folder="all">
                        <div class="folder-dot" style="background:#10b981;"></div>
                        <span>All Articles</span>
                        <span class="folder-count">${totalFiles}</span>
                    </div>`;

        folders.forEach(name => {
            const count = browseFiles.filter(f => f.path.startsWith(name + '/')).length;
            const color = this._getFolderColor(name);
            const isActive = this.activeSidebarFolder === name;
            html += `
                    <div class="kb-sidebar-folder${isActive ? ' active' : ''}" data-folder="${this._escapeAttr(name)}">
                        <div class="folder-dot" style="background:${color.color};"></div>
                        <span>\u{1F4C1} ${this._escapeHtml(name)}</span>
                        <span class="folder-count">${count}</span>
                    </div>`;

            // Show files in expanded folder
            if (isActive && isActive !== 'all') {
                browseFiles.filter(f => f.path.startsWith(name + '/')).forEach(f => {
                    const fName = f.path.split('/').pop();
                    html += `
                    <div class="kb-sidebar-file" data-path="${this._escapeAttr(f.path)}">
                        <i class="bi bi-file-earmark-text"></i> ${this._escapeHtml(fName)}
                    </div>`;
                });
            }
        });

        html += `
                    <div class="kb-sidebar-intake-link" data-action="show-intake">
                        <i class="bi bi-inbox"></i>
                        <span>\u{1F4E5} Intake</span>
                        <span class="intake-badge">${this._intakeStats?.pending || 0}</span>
                    </div>
                </div>
            </div>`;

        el.innerHTML = html;
    }

    // ─── Browse Scene ──────────────────────────────
    _renderBrowseScene() {
        const scene = this.overlay?.querySelector('[data-scene="browse"]');
        if (!scene) return;

        const lifecycleTags = this.config.tags?.lifecycle || [];
        const domainTags = this.config.tags?.domain || [];

        scene.innerHTML = `
            <div class="kb-content-header">
                <div class="kb-content-header-left">
                    <div class="kb-content-title"><i class="bi bi-book"></i> Knowledge Base</div>
                </div>
                <div class="kb-content-header-right">
                    <button class="kb-content-btn" data-action="toggle-upload-view">
                        <i class="bi bi-cloud-arrow-up"></i> Upload
                    </button>
                </div>
            </div>
            <div data-role="browse-preview">
                <div class="kb-stats-bar" data-role="stats-bar"></div>
                <div class="kb-toolbar">
                    <div class="kb-search-row">
                        <div class="kb-search-box">
                            <i class="bi bi-search"></i>
                            <input type="text" placeholder="Search articles by keyword, title, or content\u2026" data-role="content-search" />
                        </div>
                    <div class="kb-view-toggle">
                        <button class="kb-view-btn${this.viewMode === 'grid' ? ' active' : ''}" data-view="grid" title="Grid view"><i class="bi bi-grid-3x3-gap"></i></button>
                        <button class="kb-view-btn${this.viewMode === 'list' ? ' active' : ''}" data-view="list" title="List view"><i class="bi bi-list-ul"></i></button>
                    </div>
                    <div class="kb-sort-group">
                        <span class="kb-sort-label">Sort:</span>
                        <select class="kb-sort-select" data-role="sort-select">
                            <option value="modified"${this.sortBy === 'modified' ? ' selected' : ''}>Last Modified</option>
                            <option value="name"${this.sortBy === 'name' ? ' selected' : ''}>Name A \u2192 Z</option>
                            <option value="created"${this.sortBy === 'created' ? ' selected' : ''}>Date Created</option>
                            <option value="untagged"${this.sortBy === 'untagged' ? ' selected' : ''}>Untagged First</option>
                        </select>
                    </div>
                </div>
                <div class="kb-filter-row" data-role="lifecycle-filters">
                    <span class="kb-filter-dimension kb-filter-dimension-lifecycle">\u25B8 Lifecycle</span>
                    <span class="kb-filter-chip${this.lifecycleFilter === 'all' ? ' active' : ''}" data-lifecycle="all">All</span>
                    ${lifecycleTags.map(t => `<span class="kb-filter-chip${this.lifecycleFilter === t ? ' active' : ''}" data-lifecycle="${this._escapeAttr(t)}">${this._escapeHtml(t)}</span>`).join('')}
                    <span class="kb-filter-separator"></span>
                    <span class="kb-filter-chip-untagged${this.showUntaggedOnly ? ' active' : ''}" data-action="toggle-untagged"><i class="bi bi-exclamation-triangle"></i> Untagged <strong style="font-size:10px;" data-role="untagged-count"></strong></span>
                </div>
                <div class="kb-filter-row" data-role="domain-filters">
                    <span class="kb-filter-dimension kb-filter-dimension-domain"># Domain</span>
                    <span class="kb-filter-chip${this.domainFilter === 'all' ? ' active' : ''}" data-domain="all">All</span>
                    ${domainTags.map(t => `<span class="kb-filter-chip${this.domainFilter === t ? ' active' : ''}" data-domain="${this._escapeAttr(t)}">${this._escapeHtml(t)}</span>`).join('')}
                </div>
                <div class="kb-filter-hint">
                    <i class="bi bi-info-circle"></i>
                    2D taxonomy from <code>knowledgebase-config.json</code> \u2014
                    <span class="kb-tag-lifecycle sm">lifecycle</span> \u00D7 <span class="kb-tag-domain sm">domain</span>
                </div>
            </div>
            <div class="kb-cards-scroll" data-role="cards-container">
                <div class="kb-cards-grid" data-role="cards-grid"></div>
            </div>
            <div class="kb-list-view" data-role="list-view">
                <div class="kb-list-header">
                    <div class="kb-list-col"></div>
                    <div class="kb-list-col sorted">Name <span class="sort-arrow">\u25BE</span></div>
                    <div class="kb-list-col">Folder</div>
                    <div class="kb-list-col">Lifecycle</div>
                    <div class="kb-list-col">Domain</div>
                    <div class="kb-list-col">Modified</div>
                </div>
                <div class="kb-list-rows" data-role="list-rows"></div>
            </div>
            </div>
            <div data-role="browse-upload" style="display:none;flex:1;overflow-y:auto;">
                ${this._renderUploadSection()}
            </div>
        `;

        this._renderBrowseContent();
    }

    _renderBrowseContent() {
        const filtered = this._getFilteredFiles();
        const sorted = this._getSortedFiles(filtered);

        // Stats
        this._renderStats(sorted);

        // Untagged count
        const untaggedCount = this.files.filter(f => this._isUntagged(f)).length;
        const ucEl = this.overlay?.querySelector('[data-role="untagged-count"]');
        if (ucEl) ucEl.textContent = `(${untaggedCount})`;

        // Cards
        const grid = this.overlay?.querySelector('[data-role="cards-grid"]');
        if (grid) grid.innerHTML = sorted.length ? this._renderCards(sorted) : '<div class="kb-empty-state"><i class="bi bi-journal-text"></i><p>No articles match your filters</p></div>';

        // List
        const rows = this.overlay?.querySelector('[data-role="list-rows"]');
        if (rows) rows.innerHTML = sorted.length ? this._renderListRows(sorted) : '<div class="kb-empty-state"><i class="bi bi-journal-text"></i><p>No articles match your filters</p></div>';
    }

    _renderStats(files) {
        const bar = this.overlay?.querySelector('[data-role="stats-bar"]');
        if (!bar) return;
        const folders = this._getFolderNames();
        const browseFiles = this.files.filter(f => !f.path.startsWith('.intake/') && !f.path.startsWith('.intake\\'));
        const lcCount = new Set();
        const dmCount = new Set();
        let autoGen = 0, untagged = 0;
        browseFiles.forEach(f => {
            const tags = f.frontmatter?.tags || {};
            (Array.isArray(tags.lifecycle) ? tags.lifecycle : tags.lifecycle ? [tags.lifecycle] : []).forEach(t => lcCount.add(t));
            (Array.isArray(tags.domain) ? tags.domain : tags.domain ? [tags.domain] : []).forEach(t => dmCount.add(t));
            if (f.frontmatter?.auto_generated) autoGen++;
            if (this._isUntagged(f)) untagged++;
        });
        bar.innerHTML = `
            <div class="kb-stat-item"><span class="kb-stat-num">${browseFiles.length}</span> articles</div>
            <div class="kb-stat-item"><span class="kb-stat-num">${folders.length}</span> folders</div>
            <div class="kb-stat-item"><span class="kb-stat-num">${lcCount.size}</span> lifecycle tags</div>
            <div class="kb-stat-item"><span class="kb-stat-num">${dmCount.size}</span> domain tags</div>
            <div class="kb-stat-item"><span class="kb-stat-num">${autoGen}</span> auto-generated</div>
            ${untagged ? `<div class="kb-stat-item" style="color:#b45309;"><span class="kb-stat-num" style="color:#b45309;">${untagged}</span> untagged</div>` : ''}
        `;
    }

    _renderCards(files) {
        return files.map((f, i) => {
            const fm = f.frontmatter || {};
            const tags = fm.tags || {};
            const lc = Array.isArray(tags.lifecycle) ? tags.lifecycle : (tags.lifecycle ? [tags.lifecycle] : []);
            const dm = Array.isArray(tags.domain) ? tags.domain : (tags.domain ? [tags.domain] : []);
            const folder = f.path.includes('/') ? f.path.split('/')[0] : '';
            const color = folder ? this._getFolderColor(folder) : KBBrowseModal.FOLDER_COLORS[5];
            const title = fm.title || f.name;
            const isHero = i === 0;
            const isAuto = fm.auto_generated;
            const isUntagged = this._isUntagged(f);
            const date = this._formatDate(fm.created || f.modified_date);

            const lcTags = lc.map(t => `<span class="kb-tag-lifecycle sm">${this._escapeHtml(t)}</span>`).join('');
            const dmTags = dm.map(t => `<span class="kb-tag-domain sm">${this._escapeHtml(t)}</span>`).join('');

            return `
                <div class="kb-card${isHero ? ' hero' : ''}" data-path="${this._escapeAttr(f.path)}">
                    <div class="kb-card-accent" style="background:${color.accent};"></div>
                    <div class="kb-card-body">
                        <div class="kb-card-meta">
                            <span class="kb-card-category" style="background:${color.bg};color:${color.label};">\u{1F4C1} ${this._escapeHtml(folder || 'root')}</span>
                            ${isAuto ? '<span class="kb-auto-badge"><i class="bi bi-robot"></i> Auto</span>' : ''}
                            ${isUntagged ? '<span class="kb-needs-tags-badge"><i class="bi bi-tag"></i> Needs Tags</span>' : ''}
                            <span class="kb-card-date">${this._escapeHtml(date)}</span>
                        </div>
                        <div class="kb-card-title">${this._escapeHtml(title)}</div>
                        <div class="kb-card-excerpt">${this._escapeHtml(this._getExcerpt(f))}</div>
                        <div class="kb-card-footer">
                            ${lcTags}${dmTags}
                            ${isUntagged && !lcTags && !dmTags ? '<span style="font-size:10px;color:#b45309;font-style:italic;">No tags assigned</span>' : ''}
                            <span class="kb-card-author">
                                <span class="author-dot" style="background:${color.color};">${(fm.author || 'U')[0].toUpperCase()}</span>
                                ${this._escapeHtml(fm.author || 'unknown')}
                            </span>
                        </div>
                    </div>
                </div>`;
        }).join('');
    }

    _renderListRows(files) {
        return files.map(f => {
            const fm = f.frontmatter || {};
            const tags = fm.tags || {};
            const lc = Array.isArray(tags.lifecycle) ? tags.lifecycle : (tags.lifecycle ? [tags.lifecycle] : []);
            const dm = Array.isArray(tags.domain) ? tags.domain : (tags.domain ? [tags.domain] : []);
            const folder = f.path.includes('/') ? f.path.split('/')[0] : '';
            const title = fm.title || f.name;
            const isUntagged = this._isUntagged(f);
            const date = this._formatDate(fm.created || f.modified_date);

            const lcTags = lc.length ? lc.map(t => `<span class="kb-tag-lifecycle sm">${this._escapeHtml(t)}</span>`).join(' ') : (isUntagged ? '<span style="font-size:10px;color:#b45309;font-style:italic;">\u2014</span>' : '');
            const dmTags = dm.length ? dm.map(t => `<span class="kb-tag-domain sm">${this._escapeHtml(t)}</span>`).join(' ') : (isUntagged ? '<span style="font-size:10px;color:#b45309;font-style:italic;">\u2014</span>' : '');

            return `
                <div class="kb-list-row${isUntagged ? '" style="background:#fffbeb;' : ''}" data-path="${this._escapeAttr(f.path)}">
                    <i class="bi bi-file-earmark-text list-icon"${isUntagged ? ' style="color:#b45309;"' : ''}></i>
                    <span class="list-name">${this._escapeHtml(title)}${isUntagged ? ' <span class="kb-needs-tags-badge" style="margin-left:6px;"><i class="bi bi-tag"></i> Needs Tags</span>' : ''}</span>
                    <span class="list-folder">\u{1F4C1} ${this._escapeHtml(folder || 'root')}</span>
                    <span class="list-tags">${lcTags}</span>
                    <span class="list-tags">${dmTags}</span>
                    <span class="list-date">${this._escapeHtml(date)}</span>
                </div>`;
        }).join('');
    }

    _renderUploadSection() {
        return `
            <div class="kb-upload-section">
                <div class="kb-upload-mode-bar">
                    <button class="kb-upload-mode-btn mode-normal active" data-upload-mode="normal">
                        <i class="bi bi-cloud-arrow-up"></i> Normal Upload
                    </button>
                    <button class="kb-upload-mode-btn mode-librarian" data-upload-mode="librarian">
                        <i class="bi bi-robot"></i> \u{1F4DA} AI Librarian
                        <span class="intake-badge" style="background:#8b5cf6;color:#fff;font-size:9px;font-weight:700;padding:1px 6px;border-radius:8px;">0</span>
                    </button>
                </div>
                <div class="kb-upload-mode-content">
                    <div class="kb-upload-panel${this.uploadMode === 'normal' ? ' active' : ''}" data-upload-panel="normal">
                        <div class="kb-upload-folder-picker">
                            <span class="kb-upload-folder-label">Upload to:</span>
                            <div class="kb-upload-folder-breadcrumb" data-action="toggle-folder-dropdown">
                                <i class="bi bi-folder2-open" style="color:#10b981;font-size:13px;"></i>
                                <span data-role="upload-folder-path">${this._escapeHtml(this.uploadFolder)}</span>
                                <i class="bi bi-chevron-down" style="font-size:10px;color:#94a3b8;margin-left:auto;"></i>
                            </div>
                        </div>
                        <div class="kb-upload-zone" data-action="trigger-upload">
                            <i class="bi bi-cloud-arrow-up"></i>
                            <div class="kb-upload-zone-text">Drag & drop files here, or <strong>browse</strong></div>
                            <div class="kb-upload-zone-hint">Supports all file types \u00B7 Max 10MB</div>
                        </div>
                    </div>
                    <div class="kb-upload-panel${this.uploadMode === 'librarian' ? ' active' : ''}" data-upload-panel="librarian">
                        <div class="kb-intake-header">
                            <div class="kb-intake-title">
                                <span>\u{1F4E5}</span> Intake
                                <span class="intake-badge" style="background:#8b5cf6;color:#fff;font-size:10px;font-weight:700;padding:1px 7px;border-radius:10px;">0</span>
                            </div>
                        </div>
                        <button class="kb-btn-ai-librarian" data-action="run-librarian">
                            <span>\u2728</span> Run AI Librarian
                            <span style="font-size:11px;font-weight:400;opacity:0.8;">\u2014 Organize files</span>
                        </button>
                        <div class="kb-btn-ai-librarian-hint">Opens a Copilot CLI session to classify, move & tag your files</div>
                        <div class="kb-intake-subtitle">Drop files here for AI-assisted organization. The AI Librarian will analyze content, suggest folder placement, and auto-tag lifecycle & domain dimensions.</div>
                        <div class="kb-intake-dropzone" data-action="trigger-intake-upload">
                            <i class="bi bi-inbox"></i>
                            <div class="kb-intake-dropzone-text">Drop files into <strong>Intake</strong> for AI processing</div>
                        </div>
                        <div class="kb-intake-files" data-role="intake-files"></div>
                    </div>
                </div>
            </div>`;
    }

    // ─── Article Scene ─────────────────────────────
    async _showArticle(filePath) {
        const scene = this.overlay?.querySelector('[data-scene="article"]');
        if (!scene) return;

        // Show loading
        this._showScene('article');
        scene.innerHTML = '<div class="kb-empty-state"><div class="spinner-border spinner-border-sm"></div> Loading article\u2026</div>';

        try {
            const res = await fetch(`${KBBrowseModal.API.FILES}/${encodeURIComponent(filePath)}`);
            if (!res.ok) throw new Error('Failed to load');
            const data = await res.json();
            this.currentArticle = data;
            this._renderArticleScene(data);
        } catch (err) {
            scene.innerHTML = `<div class="kb-empty-state"><i class="bi bi-exclamation-triangle"></i><p>Failed to load article: ${this._escapeHtml(err.message)}</p></div>`;
        }
    }

    _renderArticleScene(data) {
        const scene = this.overlay?.querySelector('[data-scene="article"]');
        if (!scene) return;

        const fm = data.frontmatter || {};
        const tags = fm.tags || {};
        const lc = Array.isArray(tags.lifecycle) ? tags.lifecycle : (tags.lifecycle ? [tags.lifecycle] : []);
        const dm = Array.isArray(tags.domain) ? tags.domain : (tags.domain ? [tags.domain] : []);
        const title = fm.title || data.name || 'Untitled';
        const folder = data.path?.includes('/') ? data.path.split('/')[0] : '';
        const fileName = data.path?.split('/').pop() || '';
        const description = typeof fm.description === 'string' ? fm.description.trim() : '';
        const created = this._formatDate(fm.created || data.modified_date);
        const fileSize = this._formatFileSize(data.size_bytes || 0);

        // Render markdown
        let rendered = '';
        if (typeof marked !== 'undefined') {
            try { rendered = marked.parse(data.content || ''); } catch { rendered = this._escapeHtml(data.content || ''); }
        } else {
            rendered = `<pre>${this._escapeHtml(data.content || '')}</pre>`;
        }

        const breadcrumbParts = data.path ? data.path.split('/') : [fileName];

        scene.innerHTML = `
            <div class="kb-content-header">
                <div class="kb-content-header-left">
                    <div class="kb-content-title">
                        <i class="bi bi-file-earmark-text" style="color:${this._getFolderColor(folder).color};"></i>
                        ${this._escapeHtml(fileName)}
                    </div>
                </div>
                <div class="kb-content-header-right">
                    <button class="kb-content-btn" data-action="back-to-browse"><i class="bi bi-arrow-left"></i> Back</button>
                </div>
            </div>
            <div class="kb-article-layout">
                <div class="kb-article-main">
                    <div class="kb-article-header-block">
                        <div class="kb-article-breadcrumb">
                            <a data-action="back-to-browse">Knowledge Base</a>
                            <span>\u203A</span>
                            ${breadcrumbParts.length > 1 ? `<a>${this._escapeHtml(breadcrumbParts.slice(0, -1).join('/'))}</a><span>\u203A</span>` : ''}
                            <span>${this._escapeHtml(breadcrumbParts[breadcrumbParts.length - 1])}</span>
                        </div>
                        <h1 class="kb-article-title">${this._escapeHtml(title)}</h1>
                        <div class="kb-article-meta-row">
                            <span class="kb-article-meta-item"><i class="bi bi-person"></i> ${this._escapeHtml(fm.author || 'unknown')}</span>
                            <span class="kb-article-meta-item"><i class="bi bi-calendar3"></i> ${this._escapeHtml(created)}</span>
                            <span class="kb-article-meta-item"><i class="bi bi-file-earmark"></i> ${this._escapeHtml(fileSize)}</span>
                        </div>
                    </div>
                    <div class="kb-article-content">${rendered}</div>
                </div>
                <div class="kb-article-sidebar">
                    <div class="kb-meta-section">
                        <div class="kb-meta-section-title">Actions</div>
                        <div class="kb-meta-actions">
                            <button class="kb-meta-action-btn primary" data-action="edit-article"><i class="bi bi-pencil"></i> Edit Article</button>
                            <button class="kb-meta-action-btn" data-action="download-article"><i class="bi bi-download"></i> Download</button>
                            <button class="kb-meta-action-btn" data-action="delete-article"><i class="bi bi-trash3"></i> Delete</button>
                        </div>
                    </div>
                    ${lc.length ? `
                    <div class="kb-meta-section">
                        <div class="kb-meta-section-title">Lifecycle</div>
                        <div class="kb-meta-tags">${lc.map(t => `<span class="kb-meta-tag-lifecycle">${this._escapeHtml(t)}</span>`).join('')}</div>
                    </div>` : ''}
                    ${dm.length ? `
                    <div class="kb-meta-section">
                        <div class="kb-meta-section-title">Domain</div>
                        <div class="kb-meta-tags">${dm.map(t => `<span class="kb-meta-tag-domain">${this._escapeHtml(t)}</span>`).join('')}</div>
                    </div>` : ''}
                    <div class="kb-meta-section">
                        <div class="kb-meta-section-title">Details</div>
                        <div class="kb-meta-field"><span class="kb-meta-field-label">Folder</span><span class="kb-meta-field-value">${this._escapeHtml(folder || '/')}</span></div>
                        ${description ? `<div class="kb-meta-field kb-meta-field-wrap"><span class="kb-meta-field-label">Description</span><span class="kb-meta-field-value">${this._escapeHtml(description)}</span></div>` : ''}
                        <div class="kb-meta-field"><span class="kb-meta-field-label">Author</span><span class="kb-meta-field-value">${this._escapeHtml(fm.author || 'unknown')}</span></div>
                        <div class="kb-meta-field"><span class="kb-meta-field-label">Created</span><span class="kb-meta-field-value">${this._escapeHtml(created)}</span></div>
                        <div class="kb-meta-field"><span class="kb-meta-field-label">Auto-generated</span><span class="kb-meta-field-value">${fm.auto_generated ? 'Yes' : 'No'}</span></div>
                        <div class="kb-meta-field"><span class="kb-meta-field-label">File size</span><span class="kb-meta-field-value">${this._escapeHtml(fileSize)}</span></div>
                    </div>
                    <div class="kb-meta-section">
                        <div class="kb-meta-section-title">File Path</div>
                        <div class="kb-meta-filepath">${this._escapeHtml('knowledge-base/' + (data.path || ''))}</div>
                    </div>
                </div>
            </div>
        `;

        // Syntax highlighting
        if (typeof hljs !== 'undefined') {
            scene.querySelectorAll('pre code').forEach(block => hljs.highlightElement(block));
        }
    }

    // ─── Intake Scene ──────────────────────────────
    async _renderIntakeScene() {
        const scene = this.overlay?.querySelector('[data-scene="intake"]');
        if (!scene) return;
        const data = await this._loadIntakeFiles();
        const allItems = data.items || data.files || [];
        const stats = data.stats || { total: 0, pending: 0, processing: 0, filed: 0 };
        this._intakeItems = allItems;
        this._intakeStats = stats;
        this._updateIntakeBadges(data.pending_deep_count ?? stats.pending ?? 0);

        const filter = this.intakeFilter || 'all';
        const items = this._filterIntakeItems(allItems, filter);

        const filterPill = (label, value, count) => {
            const active = filter === value ? ' active' : '';
            return `<span class="kb-filter-chip${active}" data-intake-filter="${value}">${label} <span style="opacity:0.7;">(${count})</span></span>`;
        };

        const tableHtml = items.length > 0
            ? `<table style="width:100%;border-collapse:collapse;font-size:13px;">
                <thead><tr style="border-bottom:1px solid #e2e8f0;color:#64748b;font-size:11px;text-transform:uppercase;">
                    <th style="padding:8px 12px;text-align:left;">Name</th>
                    <th style="padding:8px 12px;text-align:right;">Size / Items</th>
                    <th style="padding:8px 12px;text-align:left;">Uploaded</th>
                    <th style="padding:8px 12px;text-align:center;">Status</th>
                    <th style="padding:8px 12px;text-align:left;">Destination</th>
                    <th style="padding:8px 12px;text-align:right;">Actions</th>
                </tr></thead>
                <tbody>${items.map(item => this._renderIntakeRow(item, 0)).join('')}</tbody></table>`
            : `<div style="text-align:center;padding:40px 20px;color:#94a3b8;">
                <i class="bi bi-inbox" style="font-size:40px;display:block;margin-bottom:12px;color:#c4b5fd;"></i>
                <p style="font-size:14px;margin:0 0 8px;">No files in intake</p>
                <p style="font-size:12px;margin:0;">Drop files here or click "Add files" to get started.</p>
               </div>`;

        scene.innerHTML = `
            <div class="kb-content-header">
                <div class="kb-content-header-left">
                    <div class="kb-content-title"><i class="bi bi-inbox" style="color:#8b5cf6;"></i> AI Librarian — Intake</div>
                </div>
                <div class="kb-content-header-right">
                    <button class="kb-btn-ai-librarian" data-action="run-librarian" ${stats.pending === 0 ? 'disabled' : ''}>
                        <span>✨</span> Run AI Librarian
                    </button>
                    <button class="kb-content-btn" data-action="back-to-browse"><i class="bi bi-arrow-left"></i> Back</button>
                </div>
            </div>
            <div class="kb-stats-bar" style="display:flex;gap:16px;padding:8px 24px;flex-wrap:wrap;">
                <div class="kb-stat-item" style="color:#8b5cf6;"><span class="kb-stat-num" style="font-weight:700;">${stats.total}</span> total</div>
                <div class="kb-stat-item" style="color:#f59e0b;"><span class="kb-stat-num" style="font-weight:700;">${stats.pending}</span> pending</div>
                <div class="kb-stat-item" style="color:#3b82f6;"><span class="kb-stat-num" style="font-weight:700;">${stats.processing}</span> processing</div>
                <div class="kb-stat-item" style="color:#10b981;"><span class="kb-stat-num" style="font-weight:700;">${stats.filed}</span> filed</div>
            </div>
            <div style="padding:6px 24px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
                ${filterPill('All', 'all', stats.total)}
                ${filterPill('Pending', 'pending', stats.pending)}
                ${filterPill('Processing', 'processing', stats.processing)}
                ${filterPill('Filed', 'filed', stats.filed)}
                <div style="flex:1;"></div>
                <div class="kb-intake-dropzone" data-action="trigger-intake-upload" style="padding:8px 14px;text-align:center;border:2px dashed #c4b5fd;border-radius:10px;cursor:pointer;display:inline-flex;align-items:center;gap:6px;">
                    <i class="bi bi-plus-circle" style="font-size:14px;color:#8b5cf6;"></i>
                    <span style="font-size:12px;color:#475569;">Add files</span>
                </div>
            </div>
            <div style="flex:1;overflow-y:auto;padding:12px 24px;">
                ${tableHtml}
            </div>
        `;
        const intakeZone = scene.querySelector('.kb-intake-dropzone');
        if (intakeZone) this._attachDropHandlers(intakeZone, 'intake');
    }

    // ─── Intake Tree Helpers (CR-005) ────────────────
    _renderIntakeRow(item, depth = 0) {
        const indent = depth * 20;
        const isFolder = item.type === 'folder';
        const isExpanded = this._expandedFolders.has(item.path);

        const statusColors = { pending: '#f59e0b', processing: '#3b82f6', filed: '#10b981' };
        const statusBgs = { pending: '#fef3c7', processing: '#dbeafe', filed: '#d1fae5' };
        const statusBadge = `<span style="font-size:10px;color:${statusColors[item.status] || '#94a3b8'};background:${statusBgs[item.status] || '#f1f5f9'};padding:2px 8px;border-radius:6px;font-weight:600;">${item.status}</span>`;

        const rowStyle = item.status === 'processing' ? 'background:rgba(59,130,246,0.05);' : item.status === 'filed' ? 'opacity:0.7;' : '';

        let nameCell;
        if (isFolder) {
            const chevron = isExpanded ? 'bi-chevron-down' : 'bi-chevron-right';
            const folderIcon = isExpanded ? 'bi-folder2-open' : 'bi-folder';
            nameCell = `<td style="padding:8px 12px;padding-left:${indent + 8}px;">
                <span class="kb-intake-toggle" data-intake-toggle="${this._escapeAttr(item.path)}" style="cursor:pointer;margin-right:4px;">
                    <i class="bi ${chevron}"></i>
                </span>
                <i class="bi ${folderIcon}" style="margin-right:6px;color:#8b5cf6;"></i>
                ${this._escapeHtml(item.name)}
            </td>`;
        } else {
            nameCell = `<td style="padding:8px 12px;padding-left:${indent + 24}px;">
                <i class="bi bi-file-earmark-text" style="margin-right:6px;opacity:0.6;"></i>
                ${this._escapeHtml(item.name)}
            </td>`;
        }

        const sizeCell = isFolder
            ? `<td style="padding:8px 12px;text-align:right;color:#94a3b8;">${item.item_count} item${item.item_count !== 1 ? 's' : ''}</td>`
            : `<td style="padding:8px 12px;text-align:right;color:#94a3b8;">${this._formatFileSize(item.size_bytes || 0)}</td>`;

        const dateCell = isFolder
            ? `<td style="padding:8px 12px;color:#94a3b8;">—</td>`
            : `<td style="padding:8px 12px;color:#94a3b8;">${this._formatDate(item.modified_date)}</td>`;

        const destCell = `<td style="padding:8px 12px;color:#64748b;">${item.destination ? this._escapeHtml(item.destination) : '—'}</td>`;

        const actions = this._intakeActionButtons(item);
        const actionsCell = `<td style="padding:8px 12px;text-align:right;white-space:nowrap;">${actions}</td>`;

        let rows = `<tr style="border-bottom:1px solid #f1f5f9;${rowStyle}" data-item-path="${this._escapeAttr(item.path)}">${nameCell}${sizeCell}${dateCell}<td style="padding:8px 12px;text-align:center;">${statusBadge}</td>${destCell}${actionsCell}</tr>`;

        if (isFolder && isExpanded && item.children) {
            for (const child of item.children) {
                rows += this._renderIntakeRow(child, depth + 1);
            }
        }
        return rows;
    }

    _intakeActionButtons(item) {
        const isFolder = item.type === 'folder';
        const path = this._escapeAttr(item.path);
        const dest = this._escapeAttr(item.destination || '');
        const itemType = isFolder ? 'folder' : 'file';

        if (item.status === 'processing') {
            return `<span style="font-size:11px;color:#94a3b8;font-style:italic;">processing…</span>`;
        }
        if (item.status === 'filed') {
            let btns = '';
            if (!isFolder) {
                btns += `<button class="kb-content-btn sm" data-action="intake-action" data-intake-op="view" data-intake-file="${path}" data-intake-dest="${dest}" data-intake-type="${itemType}" title="View in KB"><i class="bi bi-arrow-right-circle"></i></button>`;
            }
            btns += `<button class="kb-content-btn sm" data-action="intake-action" data-intake-op="undo" data-intake-file="${path}" data-intake-dest="${dest}" data-intake-type="${itemType}" title="Undo"><i class="bi bi-arrow-counterclockwise"></i></button>`;
            return btns;
        }
        // pending
        let btns = '';
        if (!isFolder) {
            btns += `<button class="kb-content-btn sm" data-action="intake-action" data-intake-op="preview" data-intake-file="${path}" data-intake-type="${itemType}" title="Preview"><i class="bi bi-eye"></i></button>`;
        }
        btns += `<button class="kb-content-btn sm" data-action="intake-action" data-intake-op="assign" data-intake-file="${path}" data-intake-type="${itemType}" title="Assign folder"><i class="bi bi-folder-symlink"></i></button>`;
        btns += `<button class="kb-content-btn sm" data-action="intake-action" data-intake-op="remove" data-intake-file="${path}" data-intake-type="${itemType}" title="Remove"><i class="bi bi-x-circle"></i></button>`;
        return btns;
    }

    _toggleFolder(path) {
        if (this._expandedFolders.has(path)) {
            this._expandedFolders.delete(path);
        } else {
            this._expandedFolders.add(path);
        }
        this._renderIntakeScene();
    }

    _filterIntakeItems(items, status) {
        if (!status || status === 'all') return items;
        return items.filter(item => {
            if (item.type === 'file') return item.status === status;
            const filteredChildren = this._filterIntakeItems(item.children || [], status);
            return filteredChildren.length > 0;
        }).map(item => {
            if (item.type === 'folder') {
                return { ...item, children: this._filterIntakeItems(item.children || [], status) };
            }
            return item;
        });
    }

    // ─── Scene Navigation ──────────────────────────
    _showScene(name) {
        this.currentScene = name;
        this.overlay?.querySelectorAll('.kb-scene').forEach(s => s.classList.remove('active'));
        const target = this.overlay?.querySelector(`[data-scene="${name}"]`);
        if (target) target.classList.add('active');
    }

    // ─── Filtering & Sorting ───────────────────────
    _getFilteredFiles() {
        let files = [...this.files];

        // Exclude .intake files from browse view
        files = files.filter(f => !f.path.startsWith('.intake/') && !f.path.startsWith('.intake\\'));

        // Sidebar folder filter
        if (this.activeSidebarFolder !== 'all') {
            files = files.filter(f => f.path.startsWith(this.activeSidebarFolder + '/'));
        }

        // Search
        if (this.searchQuery) {
            const q = this.searchQuery.toLowerCase();
            files = files.filter(f => {
                const title = (f.frontmatter?.title || f.name || '').toLowerCase();
                const path = (f.path || '').toLowerCase();
                return title.includes(q) || path.includes(q);
            });
        }

        // Lifecycle filter
        if (this.lifecycleFilter !== 'all') {
            files = files.filter(f => {
                const tags = f.frontmatter?.tags?.lifecycle;
                const arr = Array.isArray(tags) ? tags : (tags ? [tags] : []);
                return arr.includes(this.lifecycleFilter);
            });
        }

        // Domain filter
        if (this.domainFilter !== 'all') {
            files = files.filter(f => {
                const tags = f.frontmatter?.tags?.domain;
                const arr = Array.isArray(tags) ? tags : (tags ? [tags] : []);
                return arr.includes(this.domainFilter);
            });
        }

        // Untagged only
        if (this.showUntaggedOnly) {
            files = files.filter(f => this._isUntagged(f));
        }

        return files;
    }

    _getSortedFiles(files) {
        const sorted = [...files];
        switch (this.sortBy) {
            case 'name':
                sorted.sort((a, b) => (a.frontmatter?.title || a.name || '').localeCompare(b.frontmatter?.title || b.name || ''));
                break;
            case 'created':
                sorted.sort((a, b) => (b.frontmatter?.created || '').localeCompare(a.frontmatter?.created || ''));
                break;
            case 'untagged':
                sorted.sort((a, b) => (this._isUntagged(b) ? 1 : 0) - (this._isUntagged(a) ? 1 : 0));
                break;
            case 'modified':
            default:
                sorted.sort((a, b) => (b.modified_date || '').localeCompare(a.modified_date || ''));
                break;
        }
        return sorted;
    }

    _isUntagged(f) {
        const tags = f.frontmatter?.tags || {};
        const lc = Array.isArray(tags.lifecycle) ? tags.lifecycle : (tags.lifecycle ? [tags.lifecycle] : []);
        const dm = Array.isArray(tags.domain) ? tags.domain : (tags.domain ? [tags.domain] : []);
        return lc.length === 0 && dm.length === 0;
    }

    _getExcerpt(f) {
        const title = f.frontmatter?.title || '';
        const path = f.path || '';
        return `Article in ${path.includes('/') ? path.split('/')[0] : 'root'} \u2014 ${title || f.name || 'Untitled'}`;
    }

    // ─── Event Handling ────────────────────────────
    _bindEvents() {
        // Close
        this.overlay.querySelector('.kb-modal-close').addEventListener('click', () => this.close());
        this.overlay.addEventListener('click', (e) => { if (e.target === this.overlay) this.close(); });
        this._escHandler = (e) => { if (e.key === 'Escape') this.close(); };
        document.addEventListener('keydown', this._escHandler);

        // Delegated click handler
        this.overlay.addEventListener('click', (e) => {
            const target = e.target;

            // Action buttons
            const actionEl = target.closest('[data-action]');
            if (actionEl) {
                this._handleAction(actionEl.dataset.action, actionEl);
                return;
            }

            // Card click
            const card = target.closest('.kb-card[data-path]');
            if (card) {
                this._showArticle(card.dataset.path);
                return;
            }

            // List row click
            const row = target.closest('.kb-list-row[data-path]');
            if (row) {
                this._showArticle(row.dataset.path);
                return;
            }

            // Sidebar folder click
            const folder = target.closest('.kb-sidebar-folder[data-folder]');
            if (folder) {
                this.activeSidebarFolder = folder.dataset.folder;
                this._renderSidebarFolders();
                this._renderBrowseContent();
                return;
            }

            // Sidebar file click
            const sFile = target.closest('.kb-sidebar-file[data-path]');
            if (sFile) {
                this._showArticle(sFile.dataset.path);
                return;
            }

            // Sidebar section toggle
            const sHeader = target.closest('.kb-sidebar-section-header');
            if (sHeader) {
                sHeader.classList.toggle('expanded');
                const content = sHeader.nextElementSibling;
                if (content) content.classList.toggle('open');
                return;
            }

            // View toggle
            const viewBtn = target.closest('.kb-view-btn[data-view]');
            if (viewBtn) {
                this._switchView(viewBtn.dataset.view);
                return;
            }

            // Lifecycle filter
            const lcChip = target.closest('[data-lifecycle]');
            if (lcChip) {
                this.lifecycleFilter = lcChip.dataset.lifecycle;
                this._updateFilterChips('lifecycle');
                this._renderBrowseContent();
                return;
            }

            // Domain filter
            const dmChip = target.closest('[data-domain]');
            if (dmChip) {
                this.domainFilter = dmChip.dataset.domain;
                this._updateFilterChips('domain');
                this._renderBrowseContent();
                return;
            }

            // Upload mode toggle
            const uploadModeBtn = target.closest('[data-upload-mode]');
            if (uploadModeBtn) {
                this._switchUploadMode(uploadModeBtn.dataset.uploadMode);
                return;
            }

            // Intake folder toggle click (CR-005)
            const toggle = target.closest('[data-intake-toggle]');
            if (toggle) {
                this._toggleFolder(toggle.dataset.intakeToggle);
                return;
            }

            // Intake filter pill click
            const intakeFilterChip = target.closest('[data-intake-filter]');
            if (intakeFilterChip) {
                this.intakeFilter = intakeFilterChip.dataset.intakeFilter;
                this._renderIntakeScene();
                return;
            }
        });

        // Search inputs (debounced)
        let searchTimer;
        this.overlay.addEventListener('input', (e) => {
            if (e.target.matches('[data-role="content-search"]')) {
                clearTimeout(searchTimer);
                searchTimer = setTimeout(() => {
                    this.searchQuery = e.target.value.trim();
                    this._renderBrowseContent();
                }, 200);
            }
            if (e.target.matches('[data-role="sidebar-search"]')) {
                // Sidebar search syncs with content search
                clearTimeout(searchTimer);
                searchTimer = setTimeout(() => {
                    this.searchQuery = e.target.value.trim();
                    const cs = this.overlay.querySelector('[data-role="content-search"]');
                    if (cs) cs.value = this.searchQuery;
                    this._renderBrowseContent();
                }, 200);
            }
        });

        // Sort select
        this.overlay.addEventListener('change', (e) => {
            if (e.target.matches('[data-role="sort-select"]')) {
                this.sortBy = e.target.value;
                this._renderBrowseContent();
            }
        });

        // Drag & drop on upload zones
        this._bindDragDrop();
    }

    _handleAction(action, el) {
        switch (action) {
            case 'back-to-browse':
                this._showScene('browse');
                this.currentArticle = null;
                break;
            case 'show-intake':
                this._renderIntakeScene();
                this._showScene('intake');
                break;
            case 'toggle-untagged':
                this.showUntaggedOnly = !this.showUntaggedOnly;
                el.classList.toggle('active', this.showUntaggedOnly);
                this._renderBrowseContent();
                break;
            case 'new-article': {
                const folder = this.activeSidebarFolder !== 'all' ? this.activeSidebarFolder : '';
                if (typeof KBArticleEditor !== 'undefined') {
                    const editScene = this.overlay?.querySelector('[data-scene="edit"]');
                    if (editScene) {
                        this._showScene('edit');
                        const editor = new KBArticleEditor({
                            folder,
                            onClose: () => {
                                this._showScene('browse');
                                this._refreshData();
                            }
                        });
                        editor.openInContainer(editScene);
                    }
                }
                break;
            }
            case 'reference-kb':
                this.close();
                if (typeof window.kbReferencePicker !== 'undefined') {
                    window.kbReferencePicker.open();
                }
                break;
            case 'edit-article': {
                if (this.currentArticle && typeof KBArticleEditor !== 'undefined') {
                    const editScene = this.overlay?.querySelector('[data-scene="edit"]');
                    if (editScene) {
                        this._showScene('edit');
                        const editor = new KBArticleEditor({
                            editPath: this.currentArticle.path,
                            onClose: () => {
                                this._showArticle(this.currentArticle.path);
                            }
                        });
                        editor.openInContainer(editScene);
                    }
                }
                break;
            }
            case 'delete-article':
                if (this.currentArticle && typeof showConfirmModal === 'function') {
                    showConfirmModal(
                        'Delete Article',
                        `Are you sure you want to delete "${this.currentArticle.frontmatter?.title || this.currentArticle.name}"?`
                    ).then(ok => {
                        if (ok) this._deleteArticle(this.currentArticle.path);
                    });
                }
                break;
            case 'download-article':
                if (this.currentArticle) this._downloadArticle(this.currentArticle);
                break;
            case 'trigger-upload':
                if (typeof window.kbFileUpload !== 'undefined') {
                    this.close();
                    window.kbFileUpload.open();
                }
                break;
            case 'trigger-intake-upload':
                this._triggerIntakeFileInput();
                break;
            case 'run-librarian':
                this._runAILibrarian();
                break;
            case 'intake-action':
                this._handleIntakeAction(
                    el.dataset.intakeOp,
                    el.dataset.intakeFile,
                    el.dataset.intakeDest || null,
                    el.dataset.intakeType || 'file'
                );
                break;
            case 'toggle-upload-view':
                this._toggleUploadView();
                break;
            case 'toggle-folder-dropdown':
                this._toggleFolderDropdown(el);
                break;
        }
    }

    async _deleteArticle(path) {
        try {
            const res = await fetch(`${KBBrowseModal.API.FILES}/${encodeURIComponent(path)}`, { method: 'DELETE' });
            if (res.ok) {
                document.dispatchEvent(new CustomEvent('kb:changed'));
                this._showScene('browse');
            }
        } catch { /* ignore */ }
    }

    _downloadArticle(data) {
        const blob = new Blob([data.content || ''], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = data.name || 'article.md';
        a.click();
        URL.revokeObjectURL(url);
    }

    _switchView(mode) {
        this.viewMode = mode;
        this.overlay?.querySelectorAll('.kb-view-btn').forEach(b => b.classList.toggle('active', b.dataset.view === mode));
        const cards = this.overlay?.querySelector('[data-role="cards-container"]');
        const list = this.overlay?.querySelector('[data-role="list-view"]');
        if (cards) cards.classList.toggle('hidden', mode === 'list');
        if (list) list.classList.toggle('active', mode === 'list');
    }

    _updateFilterChips(dimension) {
        const row = this.overlay?.querySelector(`[data-role="${dimension}-filters"]`);
        if (!row) return;
        const attr = `data-${dimension}`;
        row.querySelectorAll(`[${attr}]`).forEach(chip => {
            const val = chip.getAttribute(attr);
            chip.classList.toggle('active', val === (dimension === 'lifecycle' ? this.lifecycleFilter : this.domainFilter));
        });
    }

    _switchUploadMode(mode) {
        this.uploadMode = mode;
        this.overlay?.querySelectorAll('.kb-upload-mode-btn').forEach(b => b.classList.toggle('active', b.dataset.uploadMode === mode));
        this.overlay?.querySelectorAll('.kb-upload-panel').forEach(p => p.classList.toggle('active', p.dataset.uploadPanel === mode));
    }

    // ─── Folder Dropdown ──────────────────────────────
    _toggleFolderDropdown(el) {
        const picker = el.closest('.kb-upload-folder-picker');
        if (!picker) return;
        let dropdown = picker.querySelector('.kb-upload-folder-dropdown');
        if (dropdown) {
            dropdown.remove();
            return;
        }
        const folders = this._getFolderNames();
        dropdown = document.createElement('div');
        dropdown.className = 'kb-upload-folder-dropdown';
        const rootItem = document.createElement('div');
        rootItem.className = `kb-upload-folder-dropdown-item${this.uploadFolder === '/' ? ' active' : ''}`;
        rootItem.innerHTML = '<i class="bi bi-folder2" style="font-size:12px;"></i> / (root)';
        rootItem.addEventListener('click', () => this._selectUploadFolder('/', picker));
        dropdown.appendChild(rootItem);
        folders.forEach(name => {
            const item = document.createElement('div');
            item.className = `kb-upload-folder-dropdown-item${this.uploadFolder === name ? ' active' : ''}`;
            item.innerHTML = `<i class="bi bi-folder2" style="font-size:12px;"></i> ${this._escapeHtml(name)}`;
            item.addEventListener('click', () => this._selectUploadFolder(name, picker));
            dropdown.appendChild(item);
        });
        picker.appendChild(dropdown);
        // Close on outside click
        const closeHandler = (e) => {
            if (!picker.contains(e.target)) {
                dropdown.remove();
                document.removeEventListener('click', closeHandler, true);
            }
        };
        setTimeout(() => document.addEventListener('click', closeHandler, true), 0);
    }

    _selectUploadFolder(folder, picker) {
        this.uploadFolder = folder;
        const pathEl = picker.querySelector('[data-role="upload-folder-path"]');
        if (pathEl) pathEl.textContent = folder;
        const dropdown = picker.querySelector('.kb-upload-folder-dropdown');
        if (dropdown) dropdown.remove();
    }

    // ─── Drag & Drop ──────────────────────────────────
    _bindDragDrop() {
        if (!this.overlay) return;
        // Normal upload zone
        const uploadZone = this.overlay.querySelector('.kb-upload-zone');
        if (uploadZone) this._attachDropHandlers(uploadZone, 'normal');
        // Intake dropzone
        const intakeZone = this.overlay.querySelector('.kb-intake-dropzone');
        if (intakeZone) this._attachDropHandlers(intakeZone, 'intake');
    }

    _attachDropHandlers(zone, mode) {
        let dragCounter = 0;
        zone.addEventListener('dragenter', (e) => {
            e.preventDefault();
            dragCounter++;
            zone.classList.add('drag-over');
        });
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
        });
        zone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dragCounter--;
            if (dragCounter <= 0) { dragCounter = 0; zone.classList.remove('drag-over'); }
        });
        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            dragCounter = 0;
            zone.classList.remove('drag-over');
            const files = e.dataTransfer?.files;
            if (!files || files.length === 0) return;
            if (mode === 'intake') {
                this._handleIntakeDrop(files);
            } else {
                this._handleNormalDrop(files);
            }
        });
    }

    _handleNormalDrop(files) {
        if (typeof window.kbFileUpload !== 'undefined' && window.kbFileUpload.uploadFiles) {
            // Use kbFileUpload's upload with current folder
            const folder = this.uploadFolder === '/' ? '' : this.uploadFolder;
            window.kbFileUpload.uploadFiles(files, folder);
        } else {
            // Fallback: POST directly to API
            this._uploadFiles(files, this.uploadFolder === '/' ? '' : this.uploadFolder);
        }
    }

    _handleIntakeDrop(files) {
        this._uploadIntakeFiles(files);
    }

    async _handleIntakeAction(action, itemPath, destination, itemType = 'file') {
        const isFolder = itemType === 'folder';
        const displayName = itemPath.includes('/') ? itemPath : itemPath;

        switch (action) {
            case 'preview':
                if (isFolder) return;
                this._showArticle(`.intake/${itemPath}`);
                break;
            case 'assign': {
                const folders = this._getFolderNames();
                if (folders.length === 0) {
                    if (typeof showToast === 'function') showToast('No folders available — create a folder first', 'warning');
                    return;
                }
                const picker = document.createElement('div');
                picker.className = 'kb-upload-folder-dropdown';
                picker.style.cssText = 'position:fixed;z-index:99999;background:#fff;border:1px solid #e2e8f0;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.15);max-height:200px;overflow-y:auto;padding:4px 0;';
                const rect = document.activeElement?.getBoundingClientRect() || { top: 200, left: 200 };
                picker.style.top = `${rect.bottom || 200}px`;
                picker.style.left = `${rect.left || 200}px`;
                folders.forEach(name => {
                    const item = document.createElement('div');
                    item.style.cssText = 'padding:8px 14px;cursor:pointer;font-size:13px;';
                    item.textContent = `📁 ${name}`;
                    item.addEventListener('mouseenter', () => item.style.background = '#f1f5f9');
                    item.addEventListener('mouseleave', () => item.style.background = '');
                    item.addEventListener('click', async () => {
                        picker.remove();
                        try {
                            await fetch('/api/kb/intake/status', {
                                method: 'PUT',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ filename: itemPath, status: 'pending', destination: name })
                            });
                            this._refreshIntakeFiles();
                        } catch { /* ignore */ }
                    });
                    picker.appendChild(item);
                });
                document.body.appendChild(picker);
                const closePicker = (e) => { if (!picker.contains(e.target)) { picker.remove(); document.removeEventListener('click', closePicker); } };
                setTimeout(() => document.addEventListener('click', closePicker), 0);
                break;
            }
            case 'remove': {
                const label = isFolder ? 'folder and all its contents' : 'file';
                if (typeof showConfirmModal === 'function') {
                    const ok = await showConfirmModal('Remove', `Remove ${label} "${displayName}" from intake?`);
                    if (!ok) return;
                }
                try {
                    await fetch(`/api/kb/files/${encodeURIComponent('.intake/' + itemPath)}`, { method: 'DELETE' });
                    document.dispatchEvent(new CustomEvent('kb:changed'));
                    this._refreshIntakeFiles();
                } catch { /* ignore */ }
                break;
            }
            case 'view':
                if (isFolder) return;
                if (destination) {
                    this.activeSidebarFolder = destination;
                    this._showScene('browse');
                    this._renderSidebarFolders();
                    this._renderBrowseContent();
                }
                break;
            case 'undo':
                if (!destination) return;
                try {
                    if (!isFolder) {
                        await fetch('/api/kb/files/move', {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ source: `${destination}/${itemPath}`, target: `.intake/${itemPath}` })
                        });
                    }
                    await fetch('/api/kb/intake/status', {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ filename: itemPath, status: 'pending', destination: null })
                    });
                    document.dispatchEvent(new CustomEvent('kb:changed'));
                    this._refreshIntakeFiles();
                } catch (err) {
                    if (typeof showToast === 'function') showToast(`Undo failed: ${err.message || 'unknown error'}`, 'error');
                }
                break;
        }
    }

    _runAILibrarian() {
        const command = 'organize knowledge base intake files with AI Librarian';
        if (!window.terminalManager?.sendCopilotPromptCommand) {
            navigator.clipboard?.writeText(command);
            if (typeof showToast === 'function') showToast('Command copied — paste into Copilot CLI', 'info');
            return;
        }
        this.close();
        // Ensure terminal panel is expanded (collapsed = ~36px status bar only)
        const termPanel = document.getElementById('terminal-panel');
        if (termPanel && termPanel.offsetHeight < 100) {
            const toggle = document.querySelector('[title="Toggle terminal"]');
            if (toggle) toggle.click();
        }
        setTimeout(() => {
            window.terminalManager.sendCopilotPromptCommand(command);
        }, 300);
    }

    _toggleUploadView() {
        const scene = this.overlay?.querySelector('[data-scene="browse"]');
        if (!scene) return;
        const preview = scene.querySelector('[data-role="browse-preview"]');
        const upload = scene.querySelector('[data-role="browse-upload"]');
        const btn = scene.querySelector('[data-action="toggle-upload-view"]');
        if (!preview || !upload) return;
        const showingUpload = upload.style.display !== 'none';
        preview.style.display = showingUpload ? '' : 'none';
        upload.style.display = showingUpload ? 'none' : '';
        if (btn) {
            btn.innerHTML = showingUpload
                ? '<i class="bi bi-cloud-arrow-up"></i> Upload'
                : '<i class="bi bi-journal-text"></i> Browse Articles';
        }
    }

    _triggerIntakeFileInput() {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.accept = '';
        input.addEventListener('change', () => {
            if (input.files?.length) this._uploadIntakeFiles(input.files);
        });
        input.click();
    }

    async _uploadIntakeFiles(files) {
        const formData = new FormData();
        for (const file of files) formData.append('files', file);
        formData.append('folder', '.intake');
        try {
            const res = await fetch('/api/kb/upload', { method: 'POST', body: formData });
            if (res.ok) {
                document.dispatchEvent(new CustomEvent('kb:changed'));
                await this._refreshIntakeFiles();
            }
        } catch { /* ignore */ }
    }

    async _refreshIntakeFiles() {
        const data = await this._loadIntakeFiles();
        const intakeFiles = data.items || data.files || [];
        this._intakeItems = intakeFiles;
        this._intakeStats = data.stats || {};
        this._updateIntakeBadges(data.pending_deep_count ?? data.stats?.pending ?? 0);
        this._renderIntakeFileList(intakeFiles);
        if (this.currentScene === 'intake') {
            this._renderIntakeScene();
        }
    }

    async _loadIntakeFiles() {
        const empty = { items: [], stats: { total: 0, pending: 0, processing: 0, filed: 0 }, pending_deep_count: 0 };
        try {
            const res = await fetch('/api/kb/intake');
            if (!res.ok) return empty;
            return await res.json();
        } catch { return empty; }
    }

    _updateIntakeBadges(count) {
        const badges = this.overlay?.querySelectorAll('.intake-badge');
        badges?.forEach(b => b.textContent = count);
    }

    _renderIntakeFileList(files) {
        const container = this.overlay?.querySelector('[data-role="intake-files"]');
        if (!container) return;
        if (!files || files.length === 0) {
            container.innerHTML = '';
            return;
        }
        const statusClass = (s) => `kb-file-status-${s || 'pending'}`;
        container.innerHTML = files.map(f => `
            <div class="kb-intake-file">
                <span class="file-icon"><i class="bi bi-file-earmark-text"></i></span>
                <span class="file-name">${this._escapeHtml(f.name)}</span>
                <span class="file-size">${this._formatFileSize(f.size_bytes || 0)}</span>
                <span class="file-status ${statusClass(f.status)}">${f.status || 'pending'}</span>
            </div>`).join('');
    }

    async _uploadFiles(files, folder) {
        const formData = new FormData();
        for (const file of files) formData.append('files', file);
        if (folder) formData.append('folder', folder);
        try {
            const res = await fetch('/api/kb/upload', { method: 'POST', body: formData });
            if (res.ok) {
                document.dispatchEvent(new CustomEvent('kb:changed'));
            }
        } catch { /* ignore */ }
    }

    // ─── Utilities ─────────────────────────────────
    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = String(str || '');
        return div.innerHTML;
    }

    _escapeAttr(str) {
        return String(str || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    _formatDate(dateStr) {
        if (!dateStr) return '';
        try {
            const d = new Date(dateStr);
            if (isNaN(d.getTime())) return dateStr;
            const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
            return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
        } catch { return dateStr; }
    }

    _formatFileSize(bytes) {
        if (!bytes || bytes === 0) return '0 B';
        const units = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(i > 0 ? 1 : 0)} ${units[i]}`;
    }
}
