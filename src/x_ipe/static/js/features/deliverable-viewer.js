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
        const label = item.path ? item.path.split('/').pop() || item.name : item.name;
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
        nameEl.textContent = item.path ? item.path.split('/').pop() || item.name : item.name;
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
     */
    async showPreview(filePath) {
        // Security: reject path traversal
        if (filePath.includes('..')) {
            throw new Error('Path traversal not allowed');
        }

        // Remove existing preview
        const existingBackdrop = document.querySelector('.deliverable-preview-backdrop');
        if (existingBackdrop) existingBackdrop.remove();

        const close = () => backdrop.remove();

        // Backdrop overlay (contains the modal)
        const backdrop = document.createElement('div');
        backdrop.className = 'deliverable-preview-backdrop';
        backdrop.onclick = (e) => { if (e.target === backdrop) close(); };

        const preview = document.createElement('div');
        preview.className = 'deliverable-preview';

        const header = document.createElement('div');
        header.className = 'preview-header';
        const titleSpan = document.createElement('span');
        titleSpan.textContent = filePath.split('/').pop();
        header.appendChild(titleSpan);
        const closeBtn = document.createElement('span');
        closeBtn.className = 'preview-close';
        closeBtn.textContent = '✕';
        closeBtn.onclick = close;
        header.appendChild(closeBtn);
        preview.appendChild(header);

        const content = document.createElement('div');
        content.className = 'preview-content';
        preview.appendChild(content);

        backdrop.appendChild(preview);
        document.body.appendChild(backdrop);
        // Trigger animation
        requestAnimationFrame(() => backdrop.classList.add('active'));
        this._previewContainer = preview;

        const ext = filePath.split('.').pop().toLowerCase();

        // Handle image files directly (no text API needed)
        if (['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'bmp', 'ico'].includes(ext)) {
            const img = document.createElement('img');
            img.src = `/api/ideas/file?path=${encodeURIComponent(filePath)}`;
            img.alt = filePath.split('/').pop();
            img.style.maxWidth = '100%';
            img.style.maxHeight = '100%';
            img.style.objectFit = 'contain';
            img.onerror = () => { content.textContent = 'Cannot preview this image'; };
            content.appendChild(img);
            return;
        }

        // Handle PDF files directly
        if (ext === 'pdf') {
            const iframe = document.createElement('iframe');
            iframe.src = `/api/ideas/file?path=${encodeURIComponent(filePath)}`;
            iframe.style.width = '100%';
            iframe.style.height = '100%';
            iframe.style.border = 'none';
            content.appendChild(iframe);
            return;
        }

        try {
            const resp = await fetch(`/api/ideas/file?path=${encodeURIComponent(filePath)}`);
            if (!resp.ok) {
                if (resp.status === 415) {
                    content.textContent = 'Binary file — cannot preview';
                } else {
                    content.textContent = 'Failed to load file';
                }
                return;
            }

            const text = await resp.text();
            if (filePath.endsWith('.md')) {
                if (typeof ContentRenderer !== 'undefined') {
                    const renderer = new ContentRenderer(content);
                    renderer.renderMarkdown(text);
                } else {
                    content.innerHTML = typeof marked !== 'undefined' && marked.parse
                        ? marked.parse(text)
                        : `<pre>${this._escapeHtml(text)}</pre>`;
                }
            } else if (filePath.endsWith('.html') || filePath.endsWith('.htm')) {
                const blob = new Blob([text], { type: 'text/html' });
                const blobUrl = URL.createObjectURL(blob);
                const iframe = document.createElement('iframe');
                iframe.src = blobUrl;
                iframe.setAttribute('sandbox', 'allow-scripts allow-same-origin');
                iframe.style.width = '100%';
                iframe.style.height = '100%';
                iframe.style.border = 'none';
                content.appendChild(iframe);
            } else {
                const pre = document.createElement('pre');
                pre.textContent = text;
                content.appendChild(pre);
            }
        } catch {
            content.textContent = 'Error loading preview';
        }
    }

    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
