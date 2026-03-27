/**
 * FEATURE-038-C: Enhanced Deliverable Viewer
 * FEATURE-039-A: Folder card simplified — modal handled by FolderBrowserModal
 *
 * Provides folder-type deliverable card rendering, file-tree builder,
 * and inline preview for individual file cards.
 */
class DeliverableViewer {
    constructor({ workflowName }) {
        this.workflowName = workflowName;
        this._previewContainer = null;
    }

    /**
     * Strip x-ipe-docs/ prefix from display paths.
     */
    static stripDocsPrefix(path) {
        return typeof path === 'string' ? path.replace(/^x-ipe-docs\//, '') : path;
    }

    /**
     * Resolve a display name for folder paths, preserving trailing slash for explicit folders.
     */
    static getFolderDisplayName(path, fallbackName = '') {
        if (typeof path !== 'string' || path.length === 0) return fallbackName;
        const hasTrailingSlash = path.endsWith('/');
        const trimmedPath = hasTrailingSlash ? path.slice(0, -1) : path;
        const basename = trimmedPath.split('/').pop();
        if (!basename) return fallbackName;
        return hasTrailingSlash ? `${basename}/` : basename;
    }

    /**
     * Check if a deliverable path represents a folder.
     * Uses file-extension detection: a dot followed by 1-10 non-space chars at end
     * indicates a file. Folder names may contain dots (e.g. "001. Feature Name").
     */
    static isFolderType(path) {
        if (typeof path !== 'string') return false;
        if (path.endsWith('/')) return true;
        const basename = path.split('/').pop();
        if (!basename) return false;
        const hasExtension = /\.[^\s.]{1,10}$/.test(basename);
        return !hasExtension;
    }

    /**
     * Render a small inline folder chip (beside section subtitle).
     */
    renderFolderChip(item) {
        const chip = document.createElement('span');
        chip.className = 'deliverable-folder-chip clickable';
        chip.style.cursor = 'pointer';
        const label = DeliverableViewer.getFolderDisplayName(item.path, item.name);
        chip.textContent = `📁 ${label}`;
        chip.title = item.path || '';
        return chip;
    }

    /**
     * Render a folder deliverable card (click opens FolderBrowserModal externally).
     */
    renderFolderDeliverable(item) {
        const card = document.createElement('div');
        card.className = 'deliverable-card folder-type clickable';

        const iconEl = document.createElement('div');
        iconEl.className = `deliverable-icon ${item.category || 'folders'}`;
        iconEl.textContent = '📁';
        card.appendChild(iconEl);

        const info = document.createElement('div');
        info.className = 'deliverable-info';

        const nameEl = document.createElement('div');
        nameEl.className = 'deliverable-name';
        nameEl.textContent = DeliverableViewer.getFolderDisplayName(item.path, item.name);
        nameEl.title = item.path;
        info.appendChild(nameEl);

        const pathEl = document.createElement('div');
        pathEl.className = 'deliverable-path';
        pathEl.textContent = DeliverableViewer.stripDocsPrefix(item.path);
        info.appendChild(pathEl);

        card.appendChild(info);
        return card;
    }

    /**
     * Build a nested UL/LI tree from entries array.
     */
    static buildTreeDOM(entries) {
        const ul = document.createElement('ul');
        ul.className = 'file-tree';

        if (!entries || entries.length === 0) {
            const li = document.createElement('li');
            li.className = 'tree-item empty';
            li.textContent = 'No files';
            ul.appendChild(li);
            return ul;
        }

        for (const entry of entries) {
            const li = document.createElement('li');
            if (entry.type === 'dir') {
                li.className = 'tree-item dir-item';
                li.dataset.path = entry.path || '';
                const dirIcon = document.createElement('span');
                dirIcon.className = 'dir-icon';
                dirIcon.textContent = '📁';
                li.appendChild(dirIcon);
                const name = document.createTextNode(' ' + entry.name);
                li.appendChild(name);

                // Nested children
                if (entry.children && entry.children.length > 0) {
                    const childUl = DeliverableViewer.buildTreeDOM(entry.children);
                    li.appendChild(childUl);
                    li.addEventListener('click', (e) => {
                        e.stopPropagation();
                        childUl.style.display = childUl.style.display === 'none' ? '' : 'none';
                    });
                }
            } else {
                li.className = 'tree-item file-item';
                const fileIcon = document.createElement('span');
                fileIcon.className = 'file-icon';
                fileIcon.textContent = '📄';
                li.appendChild(fileIcon);
                const name = document.createTextNode(' ' + entry.name);
                li.appendChild(name);
                li.dataset.path = entry.path || '';
            }
            ul.appendChild(li);
        }

        return ul;
    }

    /**
     * Make a deliverable card clickable for file preview.
     */
    makeClickableForPreview(card, filePath, opts = {}) {
        if (opts.exists === false) return;
        card.style.cursor = 'pointer';
        card.classList.add('clickable');
        card.addEventListener('click', () => this.showPreview(filePath));
    }

    /**
     * Show inline preview for a file.
     * CR-008: Delegates rendering to shared FilePreviewRenderer.
     * CR-002: Enhanced header with download, toggle, and smart defaults.
     */
    async showPreview(filePath) {
        // Security: reject path traversal
        if (filePath.includes('..')) {
            throw new Error('Path traversal not allowed');
        }

        // Remove existing preview
        const existingBackdrop = document.querySelector('.deliverable-preview-backdrop');
        if (existingBackdrop) existingBackdrop.remove();

        // Cleanup previous renderer
        if (this._filePreviewRenderer) {
            this._filePreviewRenderer.destroy();
        }

        const close = () => {
            if (this._filePreviewRenderer) {
                this._filePreviewRenderer.destroy();
            }
            backdrop.remove();
        };

        // Backdrop overlay (contains the modal)
        const backdrop = document.createElement('div');
        backdrop.className = 'deliverable-preview-backdrop';
        backdrop.onclick = (e) => { if (e.target === backdrop) close(); };

        const preview = document.createElement('div');
        preview.className = 'deliverable-preview';

        const content = document.createElement('div');
        content.className = 'preview-content';

        // CR-002: Determine smart default render mode
        const smartDefault = this._getSmartDefault(filePath);
        const isTextRenderable = FilePreviewRenderer.isTextRenderable(filePath);

        // CR-008: Use shared FilePreviewRenderer
        this._filePreviewRenderer = new FilePreviewRenderer({
            apiEndpoint: '/api/ideas/file?path={path}',
            endpointStyle: 'query',
            renderMode: isTextRenderable ? smartDefault : 'auto'
        });

        // CR-002: Build enhanced header with toolbar
        const header = this._buildPreviewHeader(filePath, content, close);
        preview.appendChild(header);
        preview.appendChild(content);

        backdrop.appendChild(preview);
        document.body.appendChild(backdrop);
        requestAnimationFrame(() => backdrop.classList.add('active'));
        this._previewContainer = preview;

        await this._filePreviewRenderer.renderPreview(filePath, content);
    }

    /**
     * CR-002: Build preview header with download, toggle, and close buttons.
     */
    _buildPreviewHeader(filePath, contentEl, closeFn) {
        const header = document.createElement('div');
        header.className = 'preview-header';

        const titleSpan = document.createElement('span');
        titleSpan.className = 'preview-title';
        titleSpan.textContent = filePath.split('/').pop();
        header.appendChild(titleSpan);

        const toolbar = document.createElement('span');
        toolbar.className = 'preview-toolbar-group';

        // Download button
        const downloadBtn = document.createElement('a');
        downloadBtn.className = 'preview-download-btn';
        downloadBtn.title = 'Download';
        const downloadUrl = `/api/ideas/file?path=${encodeURIComponent(filePath)}&download=true`;
        downloadBtn.href = downloadUrl;
        downloadBtn.download = filePath.split('/').pop();
        downloadBtn.innerHTML = '⬇';
        toolbar.appendChild(downloadBtn);

        // Toggle button (only for text-renderable files)
        const isTextRenderable = FilePreviewRenderer.isTextRenderable(filePath);
        if (isTextRenderable) {
            const toggleBtn = document.createElement('span');
            toggleBtn.className = 'preview-toggle-btn';
            toggleBtn.title = this._filePreviewRenderer.getRenderMode() === 'raw' ? 'Preview' : 'Raw';
            toggleBtn.innerHTML = this._filePreviewRenderer.getRenderMode() === 'raw' ? '👁' : '&lt;/&gt;';
            toggleBtn.onclick = () => {
                const current = this._filePreviewRenderer.getRenderMode();
                const next = current === 'raw' ? 'auto' : 'raw';
                this._filePreviewRenderer.setRenderMode(next, contentEl);
                toggleBtn.innerHTML = next === 'raw' ? '👁' : '&lt;/&gt;';
                toggleBtn.title = next === 'raw' ? 'Preview' : 'Raw';
            };
            toolbar.appendChild(toggleBtn);
        }

        // Close button
        const closeBtn = document.createElement('span');
        closeBtn.className = 'preview-close';
        closeBtn.textContent = '✕';
        closeBtn.onclick = closeFn;
        toolbar.appendChild(closeBtn);

        header.appendChild(toolbar);
        return header;
    }

    /**
     * CR-002: Determine smart default render mode based on file path.
     * Files under a /src/ path segment default to 'raw', others to 'auto'.
     */
    _getSmartDefault(filePath) {
        return /\/src\//.test(filePath) ? 'raw' : 'auto';
    }

    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
