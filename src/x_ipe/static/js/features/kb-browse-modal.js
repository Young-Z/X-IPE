/**
 * FEATURE-049-B / CR-002: KB Browse Modal
 * Top-bar accessible modal with folder tree (left) and article content viewer (right).
 * Provides a globally accessible Knowledge Base entry point.
 */
class KBBrowseModal {
    static ANIMATION_MS = 300;
    static API = Object.freeze({
        TREE: '/api/kb/tree',
        FILE: '/api/kb/files',  // GET /api/kb/files/{path}
    });

    constructor() {
        this.overlay = null;
        this.tree = [];
        this.activePath = '';
        this._onKbChanged = () => { if (this.overlay) this._refreshTree(); };
        document.addEventListener('kb:changed', this._onKbChanged);
    }

    async open() {
        if (this.overlay) return;
        await this._loadTree();
        this._createModal();
        document.body.style.overflow = 'hidden';
        requestAnimationFrame(() => {
            if (this.overlay) this.overlay.classList.add('active');
        });
    }

    close() {
        if (!this.overlay) return;
        this.overlay.classList.remove('active');
        setTimeout(() => {
            if (this.overlay?.parentNode) this.overlay.parentNode.removeChild(this.overlay);
            this.overlay = null;
            document.body.style.overflow = '';
        }, KBBrowseModal.ANIMATION_MS);
    }

    async _loadTree() {
        try {
            const res = await fetch(KBBrowseModal.API.TREE);
            if (res.ok) {
                const data = await res.json();
                this.tree = data.tree || [];
            }
        } catch { /* graceful degradation */ }
    }

    async _refreshTree() {
        await this._loadTree();
        const treePanel = this.overlay?.querySelector('.kb-modal-tree-content');
        if (treePanel) treePanel.innerHTML = this._renderTreeNodes(this.tree);
    }

    _createModal() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'kb-modal-overlay';

        this.overlay.innerHTML = `
            <div class="kb-modal-dialog">
                <div class="kb-modal-header">
                    <h3><i class="bi bi-book"></i> Knowledge Base</h3>
                    <button class="kb-modal-close" title="Close">&times;</button>
                </div>
                <div class="kb-modal-body">
                    <div class="kb-modal-tree-panel">
                        <div class="kb-modal-tree-header">Folders</div>
                        <div class="kb-modal-tree-content">
                            ${this._renderTreeNodes(this.tree)}
                        </div>
                    </div>
                    <div class="kb-modal-content-panel">
                        <div class="kb-modal-content-placeholder">
                            <i class="bi bi-journal-text"></i>
                            <p>Select an article from the tree to view its content</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(this.overlay);
        this._bindEvents();
    }

    _renderTreeNodes(nodes) {
        if (!nodes.length) return '<div class="kb-modal-tree-empty">No articles yet</div>';
        let html = '';
        for (const node of nodes) {
            if (node.type === 'folder') {
                html += this._renderFolder(node);
            } else {
                html += this._renderFile(node);
            }
        }
        return html;
    }

    _renderFolder(node) {
        const safePath = this._escapeAttr(node.path);
        const children = node.children || [];
        const hasChildren = children.length > 0;
        const childHtml = hasChildren ? this._renderTreeNodes(children) : '';
        return `
            <div class="kb-modal-tree-folder" data-path="${safePath}">
                <div class="kb-modal-tree-folder-label" data-path="${safePath}">
                    <i class="bi bi-chevron-right kb-modal-chevron"></i>
                    <i class="bi bi-folder"></i>
                    <span>${this._escapeHtml(node.name)}</span>
                </div>
                <div class="kb-modal-tree-children" style="display:none;">
                    ${childHtml}
                </div>
            </div>
        `;
    }

    _renderFile(node) {
        const safePath = this._escapeAttr(node.path);
        const title = node.frontmatter?.title || node.name;
        return `
            <div class="kb-modal-tree-file" data-path="${safePath}" title="${this._escapeAttr(title)}">
                <i class="bi bi-file-text"></i>
                <span>${this._escapeHtml(title)}</span>
            </div>
        `;
    }

    _bindEvents() {
        // Close button
        this.overlay.querySelector('.kb-modal-close').addEventListener('click', () => this.close());
        // Click outside
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.close();
        });
        // Escape key
        this._escHandler = (e) => { if (e.key === 'Escape') this.close(); };
        document.addEventListener('keydown', this._escHandler);

        // Tree interactions (delegated)
        const treeContent = this.overlay.querySelector('.kb-modal-tree-content');
        treeContent.addEventListener('click', (e) => {
            const folderLabel = e.target.closest('.kb-modal-tree-folder-label');
            if (folderLabel) {
                this._toggleFolder(folderLabel);
                return;
            }
            const fileEl = e.target.closest('.kb-modal-tree-file');
            if (fileEl) {
                this._selectFile(fileEl);
            }
        });
    }

    _toggleFolder(label) {
        const folder = label.closest('.kb-modal-tree-folder');
        const children = folder.querySelector('.kb-modal-tree-children');
        const chevron = label.querySelector('.kb-modal-chevron');
        if (!children) return;

        const isOpen = children.style.display !== 'none';
        children.style.display = isOpen ? 'none' : 'block';
        if (chevron) chevron.classList.toggle('expanded', !isOpen);
    }

    async _selectFile(fileEl) {
        const path = fileEl.dataset.path;
        if (!path) return;

        // Highlight active
        this.overlay.querySelectorAll('.kb-modal-tree-file.active').forEach(el => el.classList.remove('active'));
        fileEl.classList.add('active');
        this.activePath = path;

        // Show loading
        const contentPanel = this.overlay.querySelector('.kb-modal-content-panel');
        contentPanel.innerHTML = '<div class="kb-modal-content-loading"><div class="spinner-border spinner-border-sm"></div> Loading…</div>';

        try {
            const res = await fetch(`${KBBrowseModal.API.FILE}/${encodeURIComponent(path)}`);
            if (!res.ok) throw new Error('Failed to load');
            const data = await res.json();
            this._renderContent(data, contentPanel);
        } catch (err) {
            contentPanel.innerHTML = `<div class="kb-modal-content-error">Failed to load article: ${this._escapeHtml(err.message)}</div>`;
        }
    }

    _renderContent(data, panel) {
        const title = data.frontmatter?.title || data.name || 'Untitled';
        const tags = data.frontmatter?.tags || {};
        const lifecycle = Array.isArray(tags.lifecycle) ? tags.lifecycle : (tags.lifecycle ? [tags.lifecycle] : []);
        const domain = Array.isArray(tags.domain) ? tags.domain : (tags.domain ? [tags.domain] : []);
        const created = data.frontmatter?.created || '';
        const body = data.content || '';

        // Render markdown
        let renderedBody = '';
        if (typeof marked !== 'undefined') {
            try { renderedBody = marked.parse(body); } catch { renderedBody = this._escapeHtml(body); }
        } else {
            renderedBody = `<pre>${this._escapeHtml(body)}</pre>`;
        }

        const lifecycleChips = lifecycle.map(t =>
            `<span class="kb-modal-tag kb-modal-tag-lifecycle">▸ ${this._escapeHtml(t)}</span>`
        ).join('');
        const domainChips = domain.map(t =>
            `<span class="kb-modal-tag kb-modal-tag-domain"># ${this._escapeHtml(t)}</span>`
        ).join('');

        panel.innerHTML = `
            <div class="kb-modal-article">
                <div class="kb-modal-article-header">
                    <h4>${this._escapeHtml(title)}</h4>
                    <div class="kb-modal-article-meta">
                        <span class="kb-modal-article-path"><i class="bi bi-file-text"></i> ${this._escapeHtml(data.path || '')}</span>
                        ${created ? `<span class="kb-modal-article-date"><i class="bi bi-calendar"></i> ${this._escapeHtml(created)}</span>` : ''}
                    </div>
                    <div class="kb-modal-article-tags">${lifecycleChips}${domainChips}</div>
                </div>
                <div class="kb-modal-article-body">${renderedBody}</div>
            </div>
        `;

        // Syntax highlighting
        if (typeof hljs !== 'undefined') {
            panel.querySelectorAll('pre code').forEach(block => hljs.highlightElement(block));
        }
    }

    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    _escapeAttr(str) {
        return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    destroy() {
        document.removeEventListener('kb:changed', this._onKbChanged);
        if (this._escHandler) document.removeEventListener('keydown', this._escHandler);
        this.close();
    }
}
