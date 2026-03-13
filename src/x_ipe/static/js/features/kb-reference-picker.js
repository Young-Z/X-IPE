/**
 * FEATURE-049-G: KB Reference Picker Modal (v4 — CR-004)
 * Cross-workflow modal for selecting KB articles/folders as references.
 * Supports folder navigation, breadcrumb, search, tag filters, multi-select,
 * list/icon view toggle, click-to-check, double-click folder nav,
 * clipboard copy, and insert. Light theme, standard modal, full paths.
 */
class KBReferencePicker {
    static DEBOUNCE_MS = 300;
    static ANIMATION_MS = 300;
    static COPY_FEEDBACK_MS = 1500;
    static PATH_PREFIX = 'x-ipe-docs/knowledge-base';
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
        this.currentFolder = '';
        this.viewMode = 'list';
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

    _getFullPath(relativePath) {
        if (!relativePath) return KBReferencePicker.PATH_PREFIX;
        return `${KBReferencePicker.PATH_PREFIX}/${relativePath}`;
    }

    _getCurrentFolderNode() {
        if (!this.currentFolder) return { name: 'knowledge-base', children: this.tree };
        const parts = this.currentFolder.split('/');
        let current = { children: this.tree };
        for (const part of parts) {
            const found = (current.children || []).find(n => n.name === part && n.type === 'folder');
            if (!found) return { children: [] };
            current = found;
        }
        return current;
    }

    _getSubFolders() {
        const node = this._getCurrentFolderNode();
        return (node.children || []).filter(n => n.type === 'folder');
    }

    _getFilesInCurrentFolder() {
        // Prefer tree node children with path data (real API provides this)
        const node = this._getCurrentFolderNode();
        const treeFiles = (node.children || []).filter(n => n.type === 'file' && n.path);
        if (treeFiles.length) return treeFiles;
        // Fallback: match from flat files list
        const folder = this.currentFolder;
        return this.files.filter(f => {
            if (!f.path) return false;
            // Try with knowledge-base prefix (backward compat)
            const kbPrefix = folder ? `knowledge-base/${folder}/` : 'knowledge-base/';
            if (f.path.startsWith(kbPrefix)) {
                return !f.path.substring(kbPrefix.length).includes('/');
            }
            // Try without prefix (relative paths)
            if (!folder) return !f.path.includes('/');
            const prefix = `${folder}/`;
            if (f.path.startsWith(prefix)) {
                return !f.path.substring(prefix.length).includes('/');
            }
            return false;
        });
    }

    _navigateToFolder(folderPath) {
        this.currentFolder = folderPath;
        this._refreshRightPanel();
        this._highlightActiveFolder();
    }

    _createModal() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'kb-ref-overlay';
        const searchValue = this._escapeAttr(this.searchQuery);
        this.overlay.innerHTML = `
            <div class="kb-ref-modal">
                <div class="kb-ref-header">
                    <h3>\u{1F4CE} Reference Picker</h3>
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
                        ${this._renderRightPanel()}
                    </div>
                </div>
                <div class="kb-ref-footer">
                    <span class="kb-ref-count">${this.selected.size} selected</span>
                    <span class="kb-ref-tip">\u{1F4A1} Double-click a folder to browse its contents</span>
                    <div class="kb-ref-actions">
                        <button class="kb-ref-copy-btn" title="Copy paths to clipboard">\u{1F4CB} Copy</button>
                        <button class="kb-ref-insert-btn" title="Insert references">Insert</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(this.overlay);
        this._bindEvents();
        this._highlightActiveFolder();
    }

    _renderFilterChips() {
        const lifecycle = this.config.lifecycle.map(t =>
            `<span class="kb-ref-chip kb-ref-chip-lifecycle" data-tag="${this._escapeAttr(t)}">\u25B8 ${this._escapeHtml(t)}</span>`
        ).join('');
        const domain = this.config.domain.map(t =>
            `<span class="kb-ref-chip kb-ref-chip-domain" data-tag="${this._escapeAttr(t)}"># ${this._escapeHtml(t)}</span>`
        ).join('');
        return `<div class="kb-ref-chip-row">${lifecycle}</div><div class="kb-ref-chip-row">${domain}</div>`;
    }

    _renderTreePanel() {
        if (!this.tree.length) return '<div class="kb-ref-tree-empty">No folders</div>';
        const rootActive = this.currentFolder === '' ? 'kb-ref-tree-active' : '';
        return `
            <div class="kb-ref-tree-folder">
                <div class="kb-ref-tree-item ${rootActive}" data-folder-path="">
                    \u{1F4C1} Knowledge Base
                </div>
                <div class="kb-ref-tree-children">
                    ${this._renderTreeNodes(this.tree, '')}
                </div>
            </div>
        `;
    }

    _renderTreeNodes(nodes, prefix) {
        let html = '';
        for (const node of nodes) {
            if (node.type !== 'folder') continue;
            const path = prefix ? `${prefix}/${node.name}` : node.name;
            const isActive = this.currentFolder === path ? 'kb-ref-tree-active' : '';
            const safePath = this._escapeAttr(path);
            const children = (node.children || []).filter(n => n.type === 'folder');
            html += `
                <div class="kb-ref-tree-folder">
                    <div class="kb-ref-tree-item ${isActive}" data-folder-path="${safePath}">
                        \u{1F4C1} ${this._escapeHtml(node.name)}
                    </div>
                    ${children.length ? `<div class="kb-ref-tree-children">${this._renderTreeNodes(node.children || [], path)}</div>` : ''}
                </div>
            `;
        }
        return html;
    }

    _renderBreadcrumb() {
        const parts = this.currentFolder ? this.currentFolder.split('/') : [];
        let crumbs = '<span class="kb-ref-crumb" data-folder-path="">KB Root</span>';
        let accumulated = '';
        for (const part of parts) {
            accumulated = accumulated ? `${accumulated}/${part}` : part;
            const safePath = this._escapeAttr(accumulated);
            crumbs += ` <span class="kb-ref-crumb-sep">\u203A</span> <span class="kb-ref-crumb" data-folder-path="${safePath}">${this._escapeHtml(part)}</span>`;
        }
        const currentFullPath = this._getFullPath(this.currentFolder);
        const checked = this.selected.has(currentFullPath) ? 'checked' : '';
        const safeFolderPath = this._escapeAttr(currentFullPath);
        const listActive = this.viewMode === 'list' ? 'active' : '';
        const iconActive = this.viewMode === 'icon' ? 'active' : '';
        return `
            <div class="kb-ref-breadcrumb">
                <div class="kb-ref-crumb-trail">${crumbs}</div>
                <div class="kb-ref-view-toggle">
                    <button class="kb-ref-view-btn ${listActive}" data-view="list" title="List view"><i class="bi bi-list-ul"></i></button>
                    <button class="kb-ref-view-btn ${iconActive}" data-view="icon" title="Icon view"><i class="bi bi-grid-3x3-gap"></i></button>
                </div>
                <label class="kb-ref-folder-select" title="Select this folder">
                    <input type="checkbox" class="kb-ref-check kb-ref-folder-check" data-path="${safeFolderPath}" data-type="folder" ${checked}>
                </label>
            </div>
        `;
    }

    _renderRightPanel() {
        const breadcrumb = this._renderBreadcrumb();
        let subFolderHtml = '';
        if (!this.searchQuery) {
            const subFolders = this._getSubFolders();
            if (subFolders.length) {
                if (this.viewMode === 'icon') {
                    subFolderHtml = subFolders.map(f => {
                        const path = this.currentFolder ? `${this.currentFolder}/${f.name}` : f.name;
                        const fullPath = this._getFullPath(path);
                        const safePath = this._escapeAttr(fullPath);
                        const safeNavPath = this._escapeAttr(path);
                        const checked = this.selected.has(fullPath) ? 'checked' : '';
                        return `<div class="kb-ref-icon-card kb-ref-icon-folder" data-folder-path="${safeNavPath}" data-select-path="${safePath}">
                            <div class="kb-ref-icon-graphic">\u{1F4C1}</div>
                            <div class="kb-ref-icon-name">${this._escapeHtml(f.name)}</div>
                            <input type="checkbox" class="kb-ref-check kb-ref-icon-check" data-path="${safePath}" data-type="folder" ${checked}>
                        </div>`;
                    }).join('');
                } else {
                    subFolderHtml = subFolders.map(f => {
                        const path = this.currentFolder ? `${this.currentFolder}/${f.name}` : f.name;
                        const fullPath = this._getFullPath(path);
                        const safePath = this._escapeAttr(fullPath);
                        const safeNavPath = this._escapeAttr(path);
                        const checked = this.selected.has(fullPath) ? 'checked' : '';
                        return `<div class="kb-ref-subfolder" data-folder-path="${safeNavPath}" data-select-path="${safePath}">
                            <input type="checkbox" class="kb-ref-check" data-path="${safePath}" data-type="folder" ${checked}>
                            \u{1F4C1} ${this._escapeHtml(f.name)}
                        </div>`;
                    }).join('');
                }
            }
        }
        const fileHtml = this.viewMode === 'icon' ? this._renderIconView() : this._renderFileList();
        const viewClass = this.viewMode === 'icon' ? 'kb-ref-right-content kb-ref-icon-grid' : 'kb-ref-right-content';
        return `${breadcrumb}<div class="${viewClass}">${subFolderHtml}${fileHtml}</div>`;
    }

    _renderFileList() {
        let filtered = this.searchQuery ? [...this.files] : this._getFilesInCurrentFolder();
        if (this.activeTagFilters.size > 0) {
            filtered = filtered.filter(f => {
                const fileTags = [
                    ...(f.frontmatter?.tags?.lifecycle || []),
                    ...(f.frontmatter?.tags?.domain || [])
                ];
                return Array.from(this.activeTagFilters).some(t => fileTags.includes(t));
            });
        }
        if (!filtered.length) {
            if (!this.searchQuery && this._getSubFolders().length > 0) return '';
            return '<div class="kb-ref-list-empty">No files found</div>';
        }
        return filtered.map(f => {
            const title = f.frontmatter?.title || f.name;
            const rawPath = f.path || f.name || '';
            const fullPath = rawPath.startsWith('x-ipe-docs/')
                ? rawPath
                : rawPath.startsWith('knowledge-base/')
                    ? `x-ipe-docs/${rawPath}`
                    : this._getFullPath(rawPath);
            const checked = this.selected.has(fullPath) ? 'checked' : '';
            const safePath = this._escapeAttr(fullPath);
            const lifecycleTags = (f.frontmatter?.tags?.lifecycle || []).map(t =>
                `<span class="kb-tag-pill kb-tag-lifecycle">\u25B8 ${this._escapeHtml(t)}</span>`
            ).join('');
            const domainTags = (f.frontmatter?.tags?.domain || []).map(t =>
                `<span class="kb-tag-pill kb-tag-domain"># ${this._escapeHtml(t)}</span>`
            ).join('');
            return `
                <div class="kb-ref-file-item" data-select-path="${safePath}">
                    <input type="checkbox" class="kb-ref-check" data-path="${safePath}" data-type="file" ${checked}>
                    <div class="kb-ref-file-info">
                        <span class="kb-ref-file-name">${this._escapeHtml(title)}</span>
                        <div class="kb-ref-file-tags">
                            ${lifecycleTags}${domainTags}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    _renderIconView() {
        let filtered = this.searchQuery ? [...this.files] : this._getFilesInCurrentFolder();
        if (this.activeTagFilters.size > 0) {
            filtered = filtered.filter(f => {
                const fileTags = [
                    ...(f.frontmatter?.tags?.lifecycle || []),
                    ...(f.frontmatter?.tags?.domain || [])
                ];
                return Array.from(this.activeTagFilters).some(t => fileTags.includes(t));
            });
        }
        if (!filtered.length) {
            if (!this.searchQuery && this._getSubFolders().length > 0) return '';
            return '<div class="kb-ref-list-empty">No files found</div>';
        }
        return filtered.map(f => {
            const title = f.frontmatter?.title || f.name;
            const rawPath = f.path || f.name || '';
            const fullPath = rawPath.startsWith('x-ipe-docs/')
                ? rawPath
                : rawPath.startsWith('knowledge-base/')
                    ? `x-ipe-docs/${rawPath}`
                    : this._getFullPath(rawPath);
            const checked = this.selected.has(fullPath) ? 'checked' : '';
            const safePath = this._escapeAttr(fullPath);
            return `<div class="kb-ref-icon-card kb-ref-icon-file" data-select-path="${safePath}">
                <div class="kb-ref-icon-graphic">\u{1F4C4}</div>
                <div class="kb-ref-icon-name">${this._escapeHtml(title)}</div>
                <input type="checkbox" class="kb-ref-check kb-ref-icon-check" data-path="${safePath}" data-type="file" ${checked}>
            </div>`;
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
                this._refreshRightPanel();
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
                this._refreshRightPanel();
            });
        });

        const body = this.overlay.querySelector('.kb-ref-body');

        // Single click: tree nav, breadcrumb nav, view toggle, and click-to-check on items
        body.addEventListener('click', (e) => {
            // View toggle buttons
            const viewBtn = e.target.closest('.kb-ref-view-btn');
            if (viewBtn) {
                const mode = viewBtn.dataset.view;
                if (mode && mode !== this.viewMode) {
                    this.viewMode = mode;
                    this._refreshRightPanel();
                }
                return;
            }

            // Tree panel: navigate on click (left panel)
            const treeItem = e.target.closest('.kb-ref-tree-item');
            if (treeItem) {
                const folderPath = treeItem.dataset.folderPath;
                if (folderPath !== undefined) { this._navigateToFolder(folderPath); return; }
            }

            // Breadcrumb nav
            const crumb = e.target.closest('.kb-ref-crumb');
            if (crumb) {
                const folderPath = crumb.dataset.folderPath;
                if (folderPath !== undefined) { this._navigateToFolder(folderPath); return; }
            }

            // Don't handle direct checkbox clicks — let change event handle them
            if (e.target.classList.contains('kb-ref-check')) return;

            // Click-to-check: subfolder items in right panel
            const subfolder = e.target.closest('.kb-ref-subfolder');
            if (subfolder) {
                const checkbox = subfolder.querySelector('.kb-ref-check');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                }
                return;
            }

            // Click-to-check: icon cards (folder or file)
            const iconCard = e.target.closest('.kb-ref-icon-card');
            if (iconCard) {
                const checkbox = iconCard.querySelector('.kb-ref-check');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                }
                return;
            }

            // Click-to-check: file items in list view
            const fileItem = e.target.closest('.kb-ref-file-item');
            if (fileItem) {
                const checkbox = fileItem.querySelector('.kb-ref-check');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                }
                return;
            }
        });

        // Double-click: navigate into sub-folders (right panel only)
        body.addEventListener('dblclick', (e) => {
            const subfolder = e.target.closest('.kb-ref-subfolder');
            if (subfolder) {
                const folderPath = subfolder.dataset.folderPath;
                if (folderPath !== undefined) this._navigateToFolder(folderPath);
                return;
            }
            const iconFolder = e.target.closest('.kb-ref-icon-folder');
            if (iconFolder) {
                const folderPath = iconFolder.dataset.folderPath;
                if (folderPath !== undefined) this._navigateToFolder(folderPath);
                return;
            }
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
                btn.textContent = '\u2705 Copied!';
                setTimeout(() => { btn.textContent = '\u{1F4CB} Copy'; }, KBReferencePicker.COPY_FEEDBACK_MS);
            } catch {
                const ta = document.createElement('textarea');
                ta.value = paths;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
            }
        });

        this.overlay.querySelector('.kb-ref-insert-btn').addEventListener('click', async () => {
            const paths = Array.from(this.selected);
            if (this.onInsert) {
                this.onInsert(paths);
            } else {
                await this._persistReferences(paths);
            }
            document.dispatchEvent(new CustomEvent('kb:references-inserted', { detail: { paths } }));
            this.close();
        });
    }

    _refreshRightPanel() {
        const panel = this.overlay?.querySelector('.kb-ref-list-panel');
        if (panel) panel.innerHTML = this._renderRightPanel();
    }

    _refreshFileList() {
        this._refreshRightPanel();
    }

    _highlightActiveFolder() {
        if (!this.overlay) return;
        this.overlay.querySelectorAll('.kb-ref-tree-item').forEach(item => {
            item.classList.toggle('kb-ref-tree-active', item.dataset.folderPath === this.currentFolder);
        });
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

    _detectIdeationFolder() {
        const current = document.querySelector('.breadcrumb-item.current[data-path]');
        if (current) {
            const path = current.dataset.path;
            if (path && path.startsWith('x-ipe-docs/ideas/')) return path;
        }
        return null;
    }

    async _persistReferences(paths) {
        if (!paths || paths.length === 0) return;
        const folderPath = this._detectIdeationFolder();
        if (!folderPath) return;
        try {
            const response = await fetch('/api/ideas/kb-references', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ folder_path: folderPath, kb_references: paths })
            });
            const result = await response.json();
            if (!result.success) {
                console.error('Failed to save KB references:', result.error);
            }
        } catch (err) {
            console.error('Failed to save KB references:', err);
        }
    }
}
