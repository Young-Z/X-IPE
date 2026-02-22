/**
 * FEATURE-039-A: Folder Browser Modal (MVP)
 *
 * Two-panel modal (tree + preview) for browsing folder-type deliverables.
 * Replaces inline tree expansion from FEATURE-038-C.
 * Reuses DeliverableViewer.buildTreeDOM() for tree rendering (DRY).
 */
class FolderBrowserModal {
    constructor({ workflowName }) {
        this.workflowName = workflowName;
        this.backdrop = null;
        this.treePanel = null;
        this.previewPanel = null;
        this.currentFile = null;
        this.abortController = null;
        this._onEscape = this._onEscape.bind(this);
    }

    static BINARY_EXTENSIONS = new Set([
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico',
        '.pdf', '.zip', '.gz', '.tar', '.7z',
        '.mp3', '.mp4', '.wav', '.avi',
        '.woff', '.woff2', '.ttf', '.eot',
        '.exe', '.dll', '.so', '.dylib'
    ]);

    open(folderPath) {
        if (this.backdrop) this.close();

        this._createDOM(folderPath);
        document.body.appendChild(this.backdrop);
        document.body.style.overflow = 'hidden';
        // Store ref for animation frame guard
        const bd = this.backdrop;
        requestAnimationFrame(() => { if (bd.parentNode) bd.classList.add('active'); });
        this._bindCloseHandlers();
        this._loadTree(folderPath);
    }

    close() {
        if (!this.backdrop) return;
        if (this.abortController) {
            this.abortController.abort();
            this.abortController = null;
        }
        document.removeEventListener('keydown', this._onEscape);

        this.backdrop.classList.remove('active');
        const bd = this.backdrop;
        setTimeout(() => { if (bd.parentNode) bd.remove(); }, 200);

        document.body.style.overflow = '';
        this.backdrop = null;
        this.treePanel = null;
        this.previewPanel = null;
        this.currentFile = null;
    }

    _createDOM(folderPath) {
        const folderName = folderPath.replace(/\/$/, '').split('/').pop() || folderPath;

        this.backdrop = document.createElement('div');
        this.backdrop.className = 'folder-browser-backdrop';

        const modal = document.createElement('div');
        modal.className = 'folder-browser-modal';

        // Header
        const header = document.createElement('div');
        header.className = 'folder-browser-header';
        const title = document.createElement('div');
        title.className = 'folder-browser-title';
        title.textContent = '📁 ' + folderName;
        header.appendChild(title);
        const closeBtn = document.createElement('button');
        closeBtn.className = 'folder-browser-close';
        closeBtn.textContent = '✕';
        header.appendChild(closeBtn);
        modal.appendChild(header);

        // Body with two panels
        const body = document.createElement('div');
        body.className = 'folder-browser-body';

        this.treePanel = document.createElement('div');
        this.treePanel.className = 'folder-browser-tree';
        body.appendChild(this.treePanel);

        this.previewPanel = document.createElement('div');
        this.previewPanel.className = 'folder-browser-preview';
        const emptyMsg = document.createElement('div');
        emptyMsg.className = 'folder-browser-preview-empty';
        emptyMsg.textContent = 'Select a file to preview';
        this.previewPanel.appendChild(emptyMsg);
        body.appendChild(this.previewPanel);

        modal.appendChild(body);
        this.backdrop.appendChild(modal);
    }

    async _loadTree(folderPath) {
        // Show spinner
        this.treePanel.innerHTML = '';
        const spinner = document.createElement('div');
        spinner.className = 'folder-browser-spinner';
        this.treePanel.appendChild(spinner);

        this.abortController = new AbortController();
        try {
            const resp = await fetch(
                `/api/workflow/${encodeURIComponent(this.workflowName)}/deliverables/tree?path=${encodeURIComponent(folderPath)}`,
                { signal: this.abortController.signal }
            );
            if (!resp.ok) {
                this._showTreeError(folderPath);
                return;
            }
            const entries = await resp.json();
            this.treePanel.innerHTML = '';

            if (!entries || entries.length === 0) {
                const empty = document.createElement('div');
                empty.className = 'folder-browser-error';
                empty.textContent = 'No files in this folder';
                this.treePanel.appendChild(empty);
                return;
            }

            const tree = typeof DeliverableViewer !== 'undefined'
                ? DeliverableViewer.buildTreeDOM(entries)
                : this._buildSimpleTree(entries);
            this.treePanel.appendChild(tree);

            // Wire file clicks
            tree.querySelectorAll('.file-item[data-path]').forEach(item => {
                item.style.cursor = 'pointer';
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this._selectFile(item.dataset.path, item);
                });
            });
        } catch (err) {
            if (err.name === 'AbortError') return;
            this._showTreeError(folderPath);
        }
    }

    _showTreeError(folderPath) {
        if (!this.treePanel) return;
        this.treePanel.innerHTML = '';
        const errDiv = document.createElement('div');
        errDiv.className = 'folder-browser-error';
        errDiv.textContent = 'Failed to load folder contents';
        const retryBtn = document.createElement('button');
        retryBtn.textContent = 'Retry';
        retryBtn.addEventListener('click', () => this._loadTree(folderPath));
        errDiv.appendChild(retryBtn);
        this.treePanel.appendChild(errDiv);
    }

    async _selectFile(filePath, itemEl) {
        if (filePath === this.currentFile) return;

        // Deselect previous
        const prev = this.treePanel.querySelector('.tree-item.selected');
        if (prev) prev.classList.remove('selected');

        // Select new
        if (itemEl) itemEl.classList.add('selected');
        this.currentFile = filePath;

        // Check binary
        const ext = filePath.substring(filePath.lastIndexOf('.')).toLowerCase();
        if (FolderBrowserModal.BINARY_EXTENSIONS.has(ext)) {
            this._renderBinaryMessage(filePath);
            return;
        }

        // Abort previous preview fetch
        if (this.abortController) {
            this.abortController.abort();
        }
        this.abortController = new AbortController();

        try {
            const resp = await fetch(
                `/api/ideas/file?path=${encodeURIComponent(filePath)}`,
                { signal: this.abortController.signal }
            );
            if (!resp.ok) {
                this._renderPreviewError(resp.status === 404 ? 'File not found' : 'Failed to load preview');
                return;
            }
            const content = await resp.text();
            this._renderPreview(content, filePath);
        } catch (err) {
            if (err.name === 'AbortError') return;
            this._renderPreviewError('Failed to load preview');
        }
    }

    _renderPreview(content, filePath) {
        this.previewPanel.innerHTML = '';

        const header = document.createElement('div');
        header.className = 'folder-browser-preview-header';
        header.textContent = filePath.split('/').pop();
        this.previewPanel.appendChild(header);

        const contentEl = document.createElement('div');
        contentEl.className = 'folder-browser-preview-content';

        if (filePath.endsWith('.md')) {
            contentEl.innerHTML = typeof marked !== 'undefined' && marked.parse
                ? marked.parse(content)
                : '<pre>' + this._escapeHtml(content) + '</pre>';
        } else {
            const pre = document.createElement('pre');
            pre.textContent = content;
            contentEl.appendChild(pre);
        }
        this.previewPanel.appendChild(contentEl);
    }

    _renderBinaryMessage(filePath) {
        this.previewPanel.innerHTML = '';
        const header = document.createElement('div');
        header.className = 'folder-browser-preview-header';
        header.textContent = filePath.split('/').pop();
        this.previewPanel.appendChild(header);

        const content = document.createElement('div');
        content.className = 'folder-browser-preview-content';
        content.textContent = 'Binary file — cannot preview';
        this.previewPanel.appendChild(content);
    }

    _renderPreviewError(msg) {
        this.previewPanel.innerHTML = '';
        const content = document.createElement('div');
        content.className = 'folder-browser-preview-content';
        content.textContent = msg;
        this.previewPanel.appendChild(content);
    }

    _bindCloseHandlers() {
        // Close button
        const closeBtn = this.backdrop.querySelector('.folder-browser-close');
        if (closeBtn) closeBtn.addEventListener('click', () => this.close());

        // Backdrop click (not on modal content)
        this.backdrop.addEventListener('click', (e) => {
            if (e.target === this.backdrop) this.close();
        });

        // Escape key
        document.addEventListener('keydown', this._onEscape);
    }

    _onEscape(event) {
        if (event.key === 'Escape') this.close();
    }

    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    _buildSimpleTree(entries) {
        // Fallback if DeliverableViewer not loaded
        const ul = document.createElement('ul');
        ul.className = 'file-tree';
        for (const e of entries) {
            const li = document.createElement('li');
            li.className = 'tree-item ' + (e.type === 'dir' ? 'dir-item' : 'file-item');
            li.textContent = (e.type === 'dir' ? '📁 ' : '📄 ') + e.name;
            if (e.type !== 'dir') li.dataset.path = e.path || '';
            ul.appendChild(li);
        }
        return ul;
    }
}
