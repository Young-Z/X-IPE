/**
 * FEATURE-038-C: Enhanced Deliverable Viewer
 *
 * Provides folder-type deliverable rendering with expandable file tree
 * and inline preview (markdown via marked.js, text as pre).
 */
class DeliverableViewer {
    constructor({ workflowName }) {
        this.workflowName = workflowName;
        this._previewContainer = null;
    }

    /**
     * Check if a deliverable path represents a folder.
     */
    static isFolderType(path) {
        if (typeof path !== 'string') return false;
        if (path.endsWith('/')) return true;
        // Paths without a file extension are likely folders
        const basename = path.split('/').pop();
        return basename && !basename.includes('.');
    }

    /**
     * Render a folder deliverable card with expand toggle.
     */
    renderFolderDeliverable(item) {
        const card = document.createElement('div');
        card.className = 'deliverable-card folder-type';

        const header = document.createElement('div');
        header.className = 'deliverable-card-header';

        const toggle = document.createElement('span');
        toggle.className = 'toggle-icon';
        toggle.textContent = '▸';
        header.appendChild(toggle);

        const icon = document.createElement('span');
        icon.textContent = '📁';
        header.appendChild(icon);

        const nameEl = document.createElement('span');
        nameEl.className = 'deliverable-name';
        nameEl.textContent = item.name;
        header.appendChild(nameEl);

        const pathEl = document.createElement('span');
        pathEl.className = 'deliverable-path';
        pathEl.textContent = item.path;
        header.appendChild(pathEl);

        card.appendChild(header);

        const treeContainer = document.createElement('div');
        treeContainer.className = 'deliverable-tree';
        treeContainer.style.display = 'none';
        card.appendChild(treeContainer);

        let expanded = false;
        toggle.addEventListener('click', async () => {
            expanded = !expanded;
            toggle.textContent = expanded ? '▾' : '▸';
            treeContainer.style.display = expanded ? '' : 'none';
            if (expanded && treeContainer.children.length === 0) {
                await this._expandFolderTree(treeContainer, item.path);
            }
        });

        return card;
    }

    /**
     * Fetch folder contents and build tree DOM.
     */
    async _expandFolderTree(container, folderPath) {
        try {
            const resp = await fetch(
                `/api/workflow/${encodeURIComponent(this.workflowName)}/deliverables/tree?path=${encodeURIComponent(folderPath)}`
            );
            if (!resp.ok) {
                container.textContent = '⚠️ Could not load folder';
                return;
            }
            const entries = await resp.json();
            const tree = DeliverableViewer.buildTreeDOM(entries);
            container.appendChild(tree);

            // Wire up file-item click handlers for inline preview
            tree.querySelectorAll('.file-item[data-path]').forEach(item => {
                item.style.cursor = 'pointer';
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.showPreview(item.dataset.path);
                });
            });
        } catch {
            container.textContent = '⚠️ Failed to load folder';
        }
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
     * Show inline preview for a file.
     */
    async showPreview(filePath) {
        // Security: reject path traversal
        if (filePath.includes('..')) {
            throw new Error('Path traversal not allowed');
        }

        // Remove existing preview
        const existing = document.querySelector('.deliverable-preview');
        if (existing) existing.remove();

        const preview = document.createElement('div');
        preview.className = 'deliverable-preview';

        const header = document.createElement('div');
        header.className = 'preview-header';
        header.textContent = filePath.split('/').pop();
        preview.appendChild(header);

        const content = document.createElement('div');
        content.className = 'preview-content';
        preview.appendChild(content);

        document.body.appendChild(preview);
        this._previewContainer = preview;

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
                content.innerHTML = typeof marked !== 'undefined' && marked.parse
                    ? marked.parse(text)
                    : `<pre>${this._escapeHtml(text)}</pre>`;
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
