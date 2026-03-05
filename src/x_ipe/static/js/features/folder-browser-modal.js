/**
 * FEATURE-039-A + 039-B: Folder Browser Modal
 *
 * Two-panel modal (tree + preview) for browsing folder-type deliverables.
 * Enhanced with search/filter, breadcrumb, typed icons, image preview,
 * download, keyboard a11y, and ARIA roles.
 */
class FolderBrowserModal {
    constructor({ workflowName }) {
        this.workflowName = workflowName;
        this.backdrop = null;
        this.treePanel = null;
        this.previewPanel = null;
        this.currentFile = null;
        this.currentFolder = null;
        this.abortController = null;
        this._onEscape = this._onEscape.bind(this);
        this._searchTimeout = null;
        this._focusedIdx = -1;
    }

    static BINARY_EXTENSIONS = new Set([
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico',
        '.pdf', '.zip', '.gz', '.tar', '.7z',
        '.mp3', '.mp4', '.wav', '.avi',
        '.woff', '.woff2', '.ttf', '.eot',
        '.exe', '.dll', '.so', '.dylib'
    ]);

    static IMAGE_EXTENSIONS = new Set(['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']);

    static MAX_TEXT_SIZE = 1_048_576;

    static FILE_ICONS = {
        md: '📝',
        png: '🖼️', jpg: '🖼️', jpeg: '🖼️', gif: '🖼️', svg: '🖼️', webp: '🖼️',
        js: '💻', py: '💻', ts: '💻', css: '💻', html: '💻', htm: '💻',
        json: '💻', yaml: '💻', yml: '💻', sh: '💻',
    };

    open(folderPath) {
        if (this.backdrop) this.close();

        this.currentFolder = folderPath;
        this._createDOM(folderPath);
        document.body.appendChild(this.backdrop);
        document.body.style.overflow = 'hidden';
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
        this.currentFolder = null;
        this._focusedIdx = -1;
    }

    _createDOM(folderPath) {
        const folderName = folderPath.replace(/\/$/, '').split('/').pop() || folderPath;

        this.backdrop = document.createElement('div');
        this.backdrop.className = 'folder-browser-backdrop';

        const modal = document.createElement('div');
        modal.className = 'folder-browser-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'folder-browser-title');

        // Header
        const header = document.createElement('div');
        header.className = 'folder-browser-header';
        const title = document.createElement('div');
        title.className = 'folder-browser-title';
        title.id = 'folder-browser-title';
        title.textContent = '📁 ' + folderName;
        header.appendChild(title);
        const closeBtn = document.createElement('button');
        closeBtn.className = 'folder-browser-close';
        closeBtn.textContent = '✕';
        closeBtn.setAttribute('aria-label', 'Close');
        header.appendChild(closeBtn);
        modal.appendChild(header);

        // Breadcrumb
        this.breadcrumb = document.createElement('div');
        this.breadcrumb.className = 'folder-browser-breadcrumb';
        modal.appendChild(this.breadcrumb);
        this._updateBreadcrumb(folderPath);

        // Body with two panels
        const body = document.createElement('div');
        body.className = 'folder-browser-body';

        this.treePanel = document.createElement('div');
        this.treePanel.className = 'folder-browser-tree';
        this.treePanel.setAttribute('tabindex', '0');

        // Search input
        const searchWrap = document.createElement('div');
        searchWrap.className = 'folder-browser-search';
        this.searchInput = document.createElement('input');
        this.searchInput.type = 'text';
        this.searchInput.placeholder = 'Filter files\u2026';
        this.searchInput.className = 'folder-browser-search-input';
        searchWrap.appendChild(this.searchInput);
        this.treePanel.appendChild(searchWrap);

        this.treeContent = document.createElement('div');
        this.treeContent.className = 'folder-browser-tree-content';
        this.treePanel.appendChild(this.treeContent);
        body.appendChild(this.treePanel);

        this.previewPanel = document.createElement('div');
        this.previewPanel.className = 'folder-browser-preview';
        this.previewPanel.setAttribute('tabindex', '0');
        const emptyMsg = document.createElement('div');
        emptyMsg.className = 'folder-browser-preview-empty';
        emptyMsg.textContent = 'Select a file to preview';
        this.previewPanel.appendChild(emptyMsg);
        body.appendChild(this.previewPanel);

        modal.appendChild(body);
        this.backdrop.appendChild(modal);

        this._setupSearch();
        this._setupKeyboard();
    }

    _updateBreadcrumb(folderPath) {
        if (!this.breadcrumb) return;
        this.breadcrumb.innerHTML = '';
        const segments = folderPath.replace(/\/$/, '').split('/').filter(Boolean);
        const display = segments.length > 5
            ? [segments[0], '\u2026', ...segments.slice(-3)]
            : segments;

        display.forEach((seg, i) => {
            if (i > 0) {
                const sep = document.createElement('span');
                sep.className = 'folder-browser-breadcrumb-sep';
                sep.textContent = ' / ';
                this.breadcrumb.appendChild(sep);
            }
            const span = document.createElement('span');
            span.className = 'folder-browser-breadcrumb-item';
            span.textContent = seg;
            if (seg === '\u2026') {
                span.title = folderPath;
                span.style.cursor = 'default';
            } else {
                // Compute real path up to this segment
                const realIdx = segments.indexOf(seg, i > 1 && display[1] === '\u2026' ? segments.length - 3 + (i - 2) : 0);
                const pathTo = segments.slice(0, realIdx + 1).join('/');
                span.style.cursor = 'pointer';
                span.addEventListener('click', () => {
                    this.currentFolder = pathTo;
                    this._updateBreadcrumb(pathTo);
                    this._loadTree(pathTo);
                });
            }
            this.breadcrumb.appendChild(span);
        });
    }

    _setupSearch() {
        if (!this.searchInput) return;
        this.searchInput.addEventListener('input', () => {
            clearTimeout(this._searchTimeout);
            this._searchTimeout = setTimeout(() => this._applyFilter(), 200);
        });
    }

    _applyFilter() {
        const query = (this.searchInput?.value || '').toLowerCase().trim();
        if (!this.treeContent) return;

        const items = this.treeContent.querySelectorAll('.tree-item');
        if (!query) {
            items.forEach(item => { item.style.display = ''; });
            // Remove "no matching" message
            const noMatch = this.treeContent.querySelector('.folder-browser-no-match');
            if (noMatch) noMatch.remove();
            return;
        }

        let anyVisible = false;
        items.forEach(item => {
            const name = item.textContent.toLowerCase();
            const matches = name.includes(query);
            item.style.display = matches ? '' : 'none';
            if (matches) {
                anyVisible = true;
                // Show ancestor LIs
                let parent = item.parentElement;
                while (parent && parent !== this.treeContent) {
                    if (parent.tagName === 'LI') parent.style.display = '';
                    parent = parent.parentElement;
                }
            }
        });

        // Show/hide "no matching" message
        let noMatch = this.treeContent.querySelector('.folder-browser-no-match');
        if (!anyVisible) {
            if (!noMatch) {
                noMatch = document.createElement('div');
                noMatch.className = 'folder-browser-no-match';
                noMatch.textContent = 'No matching files';
                this.treeContent.appendChild(noMatch);
            }
            noMatch.style.display = '';
        } else if (noMatch) {
            noMatch.remove();
        }
    }

    _setupKeyboard() {
        if (!this.treePanel) return;
        this.treePanel.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                const items = Array.from(this.treeContent.querySelectorAll('.tree-item:not([style*="display: none"])'));
                if (!items.length) return;
                if (e.key === 'ArrowDown') this._focusedIdx = Math.min(this._focusedIdx + 1, items.length - 1);
                else this._focusedIdx = Math.max(this._focusedIdx - 1, 0);
                items.forEach((it, i) => it.classList.toggle('keyboard-focus', i === this._focusedIdx));
                items[this._focusedIdx]?.scrollIntoView?.({ block: 'nearest' });
            } else if (e.key === 'Enter') {
                const items = Array.from(this.treeContent.querySelectorAll('.tree-item:not([style*="display: none"])'));
                if (this._focusedIdx >= 0 && this._focusedIdx < items.length) {
                    items[this._focusedIdx].click();
                }
            }
        });
    }

    _getFileIcon(name) {
        const ext = name.split('.').pop()?.toLowerCase();
        return FolderBrowserModal.FILE_ICONS[ext] || '📄';
    }

    async _loadTree(folderPath) {
        if (!this.treeContent) return;
        this.treeContent.innerHTML = '';
        const spinner = document.createElement('div');
        spinner.className = 'folder-browser-spinner';
        this.treeContent.appendChild(spinner);

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
            this.treeContent.innerHTML = '';

            if (!entries || entries.length === 0) {
                const empty = document.createElement('div');
                empty.className = 'folder-browser-error';
                empty.textContent = 'This folder is empty';
                this.treeContent.appendChild(empty);
                return;
            }

            const tree = typeof DeliverableViewer !== 'undefined'
                ? DeliverableViewer.buildTreeDOM(entries)
                : this._buildSimpleTree(entries);
            this._applyAriaToTree(tree);
            this.treeContent.appendChild(tree);
            this._wireTreeHandlers(tree);
        } catch (err) {
            if (err.name === 'AbortError') return;
            this._showTreeError(folderPath);
        }
    }

    _applyAriaToTree(tree) {
        if (tree.tagName === 'UL') tree.setAttribute('role', 'tree');
        tree.querySelectorAll('.tree-item').forEach(li => li.setAttribute('role', 'treeitem'));
        tree.querySelectorAll('ul.file-tree').forEach(ul => ul.setAttribute('role', 'group'));
    }

    _wireTreeHandlers(tree) {
        tree.querySelectorAll('.file-item[data-path]').forEach(item => {
            item.style.cursor = 'pointer';
            // Re-apply typed icons (handles trees from DeliverableViewer)
            const pathParts = (item.dataset.path || '').split('/');
            const fileName = pathParts[pathParts.length - 1] || item.textContent.trim();
            const icon = this._getFileIcon(fileName);
            const baseName = fileName.replace(/^.*\//, '');
            item.textContent = icon + ' ' + baseName;
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                this._selectFile(item.dataset.path, item);
            });
        });

        tree.querySelectorAll('.dir-item').forEach(dirItem => {
            if (dirItem.querySelector('ul')) return;
            dirItem.style.cursor = 'pointer';
            dirItem.addEventListener('click', (e) => {
                e.stopPropagation();
                this._lazyLoadDir(dirItem);
            });
        });
    }

    async _lazyLoadDir(dirItem) {
        const dirPath = dirItem.dataset.path;
        if (!dirPath) return;

        const existingUl = dirItem.querySelector('ul');
        if (existingUl) {
            existingUl.style.display = existingUl.style.display === 'none' ? '' : 'none';
            return;
        }

        const loadingSpan = document.createElement('span');
        loadingSpan.className = 'folder-browser-dir-loading';
        loadingSpan.textContent = ' \u2026';
        dirItem.appendChild(loadingSpan);

        try {
            const resp = await fetch(
                `/api/workflow/${encodeURIComponent(this.workflowName)}/deliverables/tree?path=${encodeURIComponent(dirPath)}`
            );
            loadingSpan.remove();

            if (!resp.ok) return;
            const entries = await resp.json();

            if (!entries || entries.length === 0) {
                const emptyUl = document.createElement('ul');
                emptyUl.className = 'file-tree';
                emptyUl.setAttribute('role', 'group');
                const li = document.createElement('li');
                li.className = 'tree-item empty';
                li.setAttribute('role', 'treeitem');
                li.textContent = 'This folder is empty';
                emptyUl.appendChild(li);
                dirItem.appendChild(emptyUl);
                return;
            }

            const childTree = typeof DeliverableViewer !== 'undefined'
                ? DeliverableViewer.buildTreeDOM(entries)
                : this._buildSimpleTree(entries);
            this._applyAriaToTree(childTree);
            dirItem.appendChild(childTree);
            this._wireTreeHandlers(childTree);
        } catch {
            loadingSpan.remove();
        }
    }

    _showTreeError(folderPath) {
        if (!this.treeContent) return;
        this.treeContent.innerHTML = '';
        const errDiv = document.createElement('div');
        errDiv.className = 'folder-browser-error';
        errDiv.textContent = 'Failed to load folder contents';
        const retryBtn = document.createElement('button');
        retryBtn.textContent = 'Retry';
        retryBtn.addEventListener('click', () => this._loadTree(folderPath));
        errDiv.appendChild(retryBtn);
        this.treeContent.appendChild(errDiv);
    }

    async _selectFile(filePath, itemEl) {
        if (filePath === this.currentFile) return;

        const prev = this.treePanel?.querySelector('.tree-item.selected');
        if (prev) prev.classList.remove('selected');
        if (itemEl) itemEl.classList.add('selected');
        this.currentFile = filePath;

        const ext = filePath.substring(filePath.lastIndexOf('.')).toLowerCase();

        // Image preview
        if (FolderBrowserModal.IMAGE_EXTENSIONS.has(ext)) {
            this._renderImagePreview(filePath);
            return;
        }

        // Binary (non-image)
        if (FolderBrowserModal.BINARY_EXTENSIONS.has(ext)) {
            this._renderBinaryMessage(filePath);
            return;
        }

        if (this.abortController) this.abortController.abort();
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

            // Large file check
            if (content.length > FolderBrowserModal.MAX_TEXT_SIZE) {
                this._renderLargeFileMessage(filePath);
                return;
            }

            this._renderPreview(content, filePath);
        } catch (err) {
            if (err.name === 'AbortError') return;
            this._renderPreviewError('Failed to load preview');
        }
    }

    _makePreviewHeader(filePath) {
        const header = document.createElement('div');
        header.className = 'folder-browser-preview-header';
        const nameSpan = document.createElement('span');
        nameSpan.textContent = filePath.split('/').pop();
        header.appendChild(nameSpan);

        const dlBtn = document.createElement('a');
        dlBtn.className = 'folder-browser-download-btn';
        dlBtn.href = `/api/ideas/file?path=${encodeURIComponent(filePath)}`;
        dlBtn.download = filePath.split('/').pop();
        dlBtn.textContent = '\u2B07\uFE0F';
        dlBtn.title = 'Download';
        header.appendChild(dlBtn);

        return header;
    }

    _renderPreview(content, filePath) {
        this.previewPanel.innerHTML = '';
        this.previewPanel.appendChild(this._makePreviewHeader(filePath));

        const contentEl = document.createElement('div');
        contentEl.className = 'folder-browser-preview-content';

        if (filePath.endsWith('.md')) {
            this.previewPanel.appendChild(contentEl);
            if (typeof ContentRenderer !== 'undefined') {
                const renderer = new ContentRenderer(contentEl);
                renderer.renderMarkdown(content);
            } else {
                contentEl.innerHTML = typeof marked !== 'undefined' && marked.parse
                    ? '<div class="markdown-body">' + marked.parse(content) + '</div>'
                    : '<pre>' + this._escapeHtml(content) + '</pre>';
            }
            return;
        } else if (filePath.endsWith('.html') || filePath.endsWith('.htm')) {
            const blob = new Blob([content], { type: 'text/html' });
            const blobUrl = URL.createObjectURL(blob);
            const iframe = document.createElement('iframe');
            iframe.src = blobUrl;
            iframe.setAttribute('sandbox', 'allow-scripts allow-same-origin');
            iframe.style.width = '100%';
            iframe.style.height = '100%';
            iframe.style.border = 'none';
            contentEl.appendChild(iframe);
        } else {
            const pre = document.createElement('pre');
            pre.textContent = content;
            contentEl.appendChild(pre);
        }
        this.previewPanel.appendChild(contentEl);
    }

    _renderImagePreview(filePath) {
        this.previewPanel.innerHTML = '';
        this.previewPanel.appendChild(this._makePreviewHeader(filePath));

        const contentEl = document.createElement('div');
        contentEl.className = 'folder-browser-preview-content folder-browser-image-preview';
        const img = document.createElement('img');
        img.src = `/api/ideas/file?path=${encodeURIComponent(filePath)}`;
        img.alt = filePath.split('/').pop();
        img.onerror = () => {
            contentEl.innerHTML = '';
            contentEl.textContent = 'Failed to load image';
            const dlBtn = document.createElement('a');
            dlBtn.href = `/api/ideas/file?path=${encodeURIComponent(filePath)}`;
            dlBtn.download = filePath.split('/').pop();
            dlBtn.textContent = 'Download instead';
            dlBtn.className = 'folder-browser-download-link';
            contentEl.appendChild(dlBtn);
        };
        contentEl.appendChild(img);
        this.previewPanel.appendChild(contentEl);
    }

    _renderBinaryMessage(filePath) {
        this.previewPanel.innerHTML = '';
        this.previewPanel.appendChild(this._makePreviewHeader(filePath));

        const content = document.createElement('div');
        content.className = 'folder-browser-preview-content folder-browser-binary-info';
        const fileName = filePath.split('/').pop();
        const ext = fileName.substring(fileName.lastIndexOf('.')).toUpperCase();
        content.innerHTML = '';
        const info = document.createElement('div');
        info.textContent = `${ext} file \u2014 binary content cannot be previewed`;
        content.appendChild(info);
        const dlBtn = document.createElement('a');
        dlBtn.href = `/api/ideas/file?path=${encodeURIComponent(filePath)}`;
        dlBtn.download = fileName;
        dlBtn.textContent = '\u2B07\uFE0F Download';
        dlBtn.className = 'folder-browser-download-link';
        content.appendChild(dlBtn);
        this.previewPanel.appendChild(content);
    }

    _renderLargeFileMessage(filePath) {
        this.previewPanel.innerHTML = '';
        this.previewPanel.appendChild(this._makePreviewHeader(filePath));

        const content = document.createElement('div');
        content.className = 'folder-browser-preview-content folder-browser-binary-info';
        const info = document.createElement('div');
        info.textContent = 'File too large \u2014 download instead';
        content.appendChild(info);
        const dlBtn = document.createElement('a');
        dlBtn.href = `/api/ideas/file?path=${encodeURIComponent(filePath)}`;
        dlBtn.download = filePath.split('/').pop();
        dlBtn.textContent = '\u2B07\uFE0F Download';
        dlBtn.className = 'folder-browser-download-link';
        content.appendChild(dlBtn);
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
        const closeBtn = this.backdrop.querySelector('.folder-browser-close');
        if (closeBtn) closeBtn.addEventListener('click', () => this.close());
        this.backdrop.addEventListener('click', (e) => {
            if (e.target === this.backdrop) this.close();
        });
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
        const ul = document.createElement('ul');
        ul.className = 'file-tree';
        ul.setAttribute('role', 'tree');
        for (const e of entries) {
            const li = document.createElement('li');
            li.className = 'tree-item ' + (e.type === 'dir' ? 'dir-item' : 'file-item');
            li.setAttribute('role', 'treeitem');
            const icon = e.type === 'dir' ? '📁' : this._getFileIcon(e.name);
            li.textContent = icon + ' ' + e.name;
            if (e.type !== 'dir') li.dataset.path = e.path || '';
            else li.dataset.path = e.path || '';
            ul.appendChild(li);
        }
        return ul;
    }
}
