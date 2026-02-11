/**
 * FEATURE-025-B: KB Landing Zone
 * 
 * File grid, drag-and-drop upload, selection, and landing actions.
 * Integrates with kbCore via kbLanding.render(container, files).
 */

const kbLanding = {
    // State
    selectedPaths: new Set(),
    viewMode: 'grid',
    sortField: 'name',
    sortDirection: 'asc',
    files: [],
    container: null,
    _dragCounter: 0,

    /**
     * Render the landing zone view into a container.
     * @param {HTMLElement} container - The content area element
     * @param {Array} files - Landing file data from index
     */
    render(container, files) {
        this.container = container;
        this.files = files || [];
        this.selectedPaths.clear();

        container.innerHTML = '';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.height = '100%';
        container.style.position = 'relative';

        // Content header
        container.appendChild(this._renderContentHeader());

        // Processing indicator (hidden by default)
        container.appendChild(this._renderProcessingIndicator());

        if (this.files.length === 0) {
            container.appendChild(this._renderEmptyState());
        } else {
            // Action toolbar
            container.appendChild(this._renderActionToolbar());
            // File grid/list
            const gridContainer = document.createElement('div');
            gridContainer.className = 'kb-landing-content';
            gridContainer.appendChild(this._renderFileView());
            container.appendChild(gridContainer);
        }

        // Init drag-drop on entire container
        this._initDragDrop(container);
    },

    // ------------------------------------------------------------------
    // Content Header
    // ------------------------------------------------------------------

    _renderContentHeader() {
        const header = document.createElement('div');
        header.className = 'kb-content-header';

        const title = document.createElement('div');
        title.className = 'kb-content-title';
        title.innerHTML = `
            <h5>Landing Folder</h5>
            <span class="kb-status-badge">${this.files.length} file${this.files.length !== 1 ? 's' : ''}</span>
        `;

        const actions = document.createElement('div');
        actions.className = 'kb-content-actions';

        const uploadBtn = document.createElement('button');
        uploadBtn.className = 'kb-btn kb-btn-primary';
        uploadBtn.innerHTML = '<i class="bi bi-upload"></i> Upload';
        uploadBtn.addEventListener('click', () => this._triggerUpload());

        actions.appendChild(uploadBtn);
        header.appendChild(title);
        header.appendChild(actions);
        return header;
    },

    // ------------------------------------------------------------------
    // Action Toolbar
    // ------------------------------------------------------------------

    _renderActionToolbar() {
        const toolbar = document.createElement('div');
        toolbar.className = 'kb-action-toolbar';
        toolbar.id = 'kb-action-toolbar';

        // Select All / Clear
        const selGroup = document.createElement('div');
        selGroup.className = 'kb-action-group';

        const selectAllBtn = document.createElement('button');
        selectAllBtn.className = 'kb-btn';
        selectAllBtn.textContent = 'Select All';
        selectAllBtn.addEventListener('click', () => this.selectAll());

        const clearBtn = document.createElement('button');
        clearBtn.className = 'kb-btn';
        clearBtn.textContent = 'Clear';
        clearBtn.addEventListener('click', () => this.clearSelection());

        selGroup.appendChild(selectAllBtn);
        selGroup.appendChild(clearBtn);

        // Divider
        const divider1 = document.createElement('div');
        divider1.className = 'kb-divider';

        // View toggle
        const viewGroup = document.createElement('div');
        viewGroup.className = 'kb-action-group';

        const gridBtn = document.createElement('button');
        gridBtn.className = `kb-btn ${this.viewMode === 'grid' ? 'active' : ''}`;
        gridBtn.innerHTML = '<i class="bi bi-grid-3x3-gap"></i>';
        gridBtn.title = 'Grid view';
        gridBtn.addEventListener('click', () => this.setViewMode('grid'));

        const listBtn = document.createElement('button');
        listBtn.className = `kb-btn ${this.viewMode === 'list' ? 'active' : ''}`;
        listBtn.innerHTML = '<i class="bi bi-list-ul"></i>';
        listBtn.title = 'List view';
        listBtn.addEventListener('click', () => this.setViewMode('list'));

        viewGroup.appendChild(gridBtn);
        viewGroup.appendChild(listBtn);

        // Divider
        const divider2 = document.createElement('div');
        divider2.className = 'kb-divider';

        // Sort
        const sortGroup = document.createElement('div');
        sortGroup.className = 'kb-action-group';

        const sortBtn = document.createElement('button');
        sortBtn.className = 'kb-btn';
        sortBtn.innerHTML = `<i class="bi bi-sort-alpha-${this.sortDirection === 'asc' ? 'down' : 'up'}"></i> ${this._sortLabel()}`;
        sortBtn.addEventListener('click', () => this._cycleSortField());

        sortGroup.appendChild(sortBtn);

        // Delete button (shown when selection exists)
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'kb-btn kb-btn-danger';
        deleteBtn.innerHTML = '<i class="bi bi-trash"></i> Delete';
        deleteBtn.style.display = 'none';
        deleteBtn.id = 'kb-delete-btn';
        deleteBtn.addEventListener('click', () => this.deleteSelected());

        // Selection count
        const countSpan = document.createElement('span');
        countSpan.className = 'kb-selection-count';
        countSpan.id = 'kb-selection-count';

        toolbar.appendChild(selGroup);
        toolbar.appendChild(divider1);
        toolbar.appendChild(viewGroup);
        toolbar.appendChild(divider2);
        toolbar.appendChild(sortGroup);
        toolbar.appendChild(deleteBtn);
        toolbar.appendChild(countSpan);

        return toolbar;
    },

    // ------------------------------------------------------------------
    // File Grid / List
    // ------------------------------------------------------------------

    _renderFileView() {
        const sorted = this._sortFiles([...this.files]);
        if (this.viewMode === 'grid') {
            return this._renderGrid(sorted);
        }
        return this._renderList(sorted);
    },

    _renderGrid(files) {
        const grid = document.createElement('div');
        grid.className = 'kb-file-grid';
        grid.id = 'kb-file-grid';
        files.forEach(file => grid.appendChild(this._createFileCard(file)));
        return grid;
    },

    _renderList(files) {
        const list = document.createElement('div');
        list.className = 'kb-file-list';
        list.id = 'kb-file-list';
        files.forEach(file => list.appendChild(this._createFileListItem(file)));
        return list;
    },

    _createFileCard(file) {
        const card = document.createElement('div');
        card.className = 'kb-file-card';
        card.dataset.path = file.path;
        card.title = file.name;

        if (this.selectedPaths.has(file.path)) {
            card.classList.add('selected');
        }

        const iconClass = this._getIconClass(file.type);
        card.innerHTML = `
            <div class="kb-file-card-checkbox"><i class="bi bi-check"></i></div>
            <div class="kb-file-card-icon ${iconClass}">${this._getFileIconHtml(file.type)}</div>
            <div class="kb-file-card-name">${this._escapeHtml(file.name)}</div>
            <div class="kb-file-card-meta">${this._formatSize(file.size)}</div>
        `;

        card.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleSelection(file.path);
        });

        return card;
    },

    _createFileListItem(file) {
        const item = document.createElement('div');
        item.className = 'kb-file-list-item';
        item.dataset.path = file.path;

        if (this.selectedPaths.has(file.path)) {
            item.classList.add('selected');
        }

        item.innerHTML = `
            <div class="kb-list-checkbox"><i class="bi bi-check"></i></div>
            <i class="bi ${this._getFileIcon(file.type)}" style="color: ${this._getIconColor(file.type)}"></i>
            <span class="kb-list-name" title="${this._escapeHtml(file.name)}">${this._escapeHtml(file.name)}</span>
            <span class="kb-list-meta">${this._formatSize(file.size)}</span>
        `;

        item.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleSelection(file.path);
        });

        return item;
    },

    // ------------------------------------------------------------------
    // Empty State
    // ------------------------------------------------------------------

    _renderEmptyState() {
        const wrapper = document.createElement('div');
        wrapper.className = 'kb-landing-content';
        wrapper.innerHTML = `
            <div class="kb-empty-state-landing">
                <div class="kb-empty-state-icon"><i class="bi bi-cloud-arrow-up"></i></div>
                <div class="kb-empty-state-title">No files in landing</div>
                <div class="kb-empty-state-subtitle">Upload files or drag and drop them here to get started</div>
                <button class="kb-btn kb-btn-primary" id="kb-empty-upload-btn">
                    <i class="bi bi-upload"></i> Upload Files
                </button>
            </div>
            <div class="kb-drop-zone" id="kb-drop-zone">
                <div class="kb-drop-zone-icon"><i class="bi bi-cloud-arrow-up"></i></div>
                <div class="kb-drop-zone-title">Drop files here</div>
                <div class="kb-drop-zone-subtitle">PDF, Markdown, Code, Images and more</div>
            </div>
        `;

        const uploadBtn = wrapper.querySelector('#kb-empty-upload-btn');
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => this._triggerUpload());
        }

        return wrapper;
    },

    // ------------------------------------------------------------------
    // Processing Indicator
    // ------------------------------------------------------------------

    _renderProcessingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'kb-processing-indicator';
        indicator.id = 'kb-processing-indicator';
        indicator.innerHTML = `
            <div class="kb-processing-spinner"></div>
            <span class="kb-processing-text">Uploading...</span>
            <button class="kb-processing-cancel">Cancel</button>
        `;
        return indicator;
    },

    _showProcessing(text) {
        const el = document.getElementById('kb-processing-indicator');
        if (el) {
            el.classList.add('active');
            const textEl = el.querySelector('.kb-processing-text');
            if (textEl) textEl.textContent = text || 'Processing...';
        }
    },

    _hideProcessing() {
        const el = document.getElementById('kb-processing-indicator');
        if (el) el.classList.remove('active');
    },

    // ------------------------------------------------------------------
    // Selection
    // ------------------------------------------------------------------

    selectAll() {
        this.files.forEach(f => this.selectedPaths.add(f.path));
        this._updateSelectionUI();
    },

    clearSelection() {
        this.selectedPaths.clear();
        this._updateSelectionUI();
    },

    toggleSelection(path) {
        if (this.selectedPaths.has(path)) {
            this.selectedPaths.delete(path);
        } else {
            this.selectedPaths.add(path);
        }
        this._updateSelectionUI();
    },

    _updateSelectionUI() {
        // Update cards/list items
        const items = this.container.querySelectorAll('.kb-file-card, .kb-file-list-item');
        items.forEach(item => {
            const path = item.dataset.path;
            item.classList.toggle('selected', this.selectedPaths.has(path));
        });

        // Update selection count
        const countEl = document.getElementById('kb-selection-count');
        if (countEl) {
            const count = this.selectedPaths.size;
            countEl.textContent = count > 0 ? `${count} selected` : '';
        }

        // Show/hide delete button
        const deleteBtn = document.getElementById('kb-delete-btn');
        if (deleteBtn) {
            deleteBtn.style.display = this.selectedPaths.size > 0 ? '' : 'none';
        }
    },

    // ------------------------------------------------------------------
    // Sort
    // ------------------------------------------------------------------

    setSort(field, direction) {
        this.sortField = field;
        this.sortDirection = direction;
        this._reRenderFiles();
    },

    _cycleSortField() {
        const fields = ['name', 'size', 'type'];
        const idx = fields.indexOf(this.sortField);
        if (this.sortDirection === 'asc') {
            this.sortDirection = 'desc';
        } else {
            this.sortField = fields[(idx + 1) % fields.length];
            this.sortDirection = 'asc';
        }
        this._reRenderFiles();
        // Update toolbar sort button
        this._refreshToolbar();
    },

    _sortLabel() {
        const labels = { name: 'Name', size: 'Size', type: 'Type', date: 'Date' };
        return labels[this.sortField] || 'Name';
    },

    _sortFiles(files) {
        return files.sort((a, b) => {
            let cmp = 0;
            switch (this.sortField) {
                case 'name':
                    cmp = a.name.localeCompare(b.name);
                    break;
                case 'size':
                    cmp = (a.size || 0) - (b.size || 0);
                    break;
                case 'type':
                    cmp = (a.type || '').localeCompare(b.type || '');
                    break;
                default:
                    cmp = a.name.localeCompare(b.name);
            }
            return this.sortDirection === 'asc' ? cmp : -cmp;
        });
    },

    // ------------------------------------------------------------------
    // View Mode
    // ------------------------------------------------------------------

    setViewMode(mode) {
        this.viewMode = mode;
        this._reRenderFiles();
        this._refreshToolbar();
    },

    _reRenderFiles() {
        const gridEl = document.getElementById('kb-file-grid');
        const listEl = document.getElementById('kb-file-list');
        const oldEl = gridEl || listEl;
        if (oldEl) {
            const newView = this._renderFileView();
            oldEl.parentNode.replaceChild(newView, oldEl);
        }
    },

    _refreshToolbar() {
        const oldToolbar = document.getElementById('kb-action-toolbar');
        if (oldToolbar) {
            const newToolbar = this._renderActionToolbar();
            oldToolbar.parentNode.replaceChild(newToolbar, oldToolbar);
            this._updateSelectionUI();
        }
    },

    // ------------------------------------------------------------------
    // Upload
    // ------------------------------------------------------------------

    _triggerUpload() {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.addEventListener('change', () => {
            if (input.files && input.files.length > 0) {
                this.uploadFiles(input.files);
            }
        });
        input.click();
    },

    async uploadFiles(fileList) {
        if (!fileList || fileList.length === 0) return;

        const formData = new FormData();
        for (let i = 0; i < fileList.length; i++) {
            formData.append('files', fileList[i]);
        }

        this._showProcessing(`Uploading ${fileList.length} file${fileList.length > 1 ? 's' : ''}...`);

        try {
            const response = await fetch('/api/kb/upload', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            this._hideProcessing();

            if (result.uploaded && result.uploaded.length > 0) {
                this._showToast(`${result.uploaded.length} file(s) uploaded`, 'success');
            }
            if (result.skipped && result.skipped.length > 0) {
                this._showToast(`${result.skipped.length} file(s) skipped (duplicates)`, 'warning');
            }
            if (result.errors && result.errors.length > 0) {
                this._showToast(`${result.errors.length} file(s) failed`, 'error');
            }

            // Reload landing files
            await this._reloadLanding();
        } catch (err) {
            this._hideProcessing();
            this._showToast('Upload failed: ' + err.message, 'error');
        }
    },

    // ------------------------------------------------------------------
    // Delete
    // ------------------------------------------------------------------

    async deleteSelected() {
        const paths = Array.from(this.selectedPaths);
        if (paths.length === 0) return;

        const confirmed = confirm(`Delete ${paths.length} file(s)? This cannot be undone.`);
        if (!confirmed) return;

        try {
            const response = await fetch('/api/kb/landing/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ paths })
            });
            const result = await response.json();

            if (result.deleted && result.deleted.length > 0) {
                this._showToast(`${result.deleted.length} file(s) deleted`, 'success');
            }
            if (result.errors && result.errors.length > 0) {
                this._showToast(`${result.errors.length} file(s) failed to delete`, 'error');
            }

            this.selectedPaths.clear();
            await this._reloadLanding();
        } catch (err) {
            this._showToast('Delete failed: ' + err.message, 'error');
        }
    },

    // ------------------------------------------------------------------
    // Drag & Drop
    // ------------------------------------------------------------------

    _initDragDrop(element) {
        this._dragCounter = 0;

        element.addEventListener('dragenter', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this._dragCounter++;
            if (this._dragCounter === 1) {
                element.classList.add('drag-over');
                const dropZone = element.querySelector('.kb-drop-zone');
                if (dropZone) dropZone.classList.add('drag-over');
            }
        });

        element.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });

        element.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this._dragCounter--;
            if (this._dragCounter <= 0) {
                this._dragCounter = 0;
                element.classList.remove('drag-over');
                const dropZone = element.querySelector('.kb-drop-zone');
                if (dropZone) dropZone.classList.remove('drag-over');
            }
        });

        element.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this._dragCounter = 0;
            element.classList.remove('drag-over');
            const dropZone = element.querySelector('.kb-drop-zone');
            if (dropZone) dropZone.classList.remove('drag-over');

            if (e.dataTransfer && e.dataTransfer.files.length > 0) {
                this.uploadFiles(e.dataTransfer.files);
            }
        });
    },

    // ------------------------------------------------------------------
    // Reload Landing
    // ------------------------------------------------------------------

    async _reloadLanding() {
        try {
            const response = await fetch('/api/kb/landing');
            const data = await response.json();
            this.render(this.container, data.files || []);
            // Notify kbCore to refresh sidebar tree
            if (typeof kbCore !== 'undefined' && kbCore.refreshIndex) {
                kbCore.refreshIndex();
            }
        } catch (err) {
            console.error('Failed to reload landing:', err);
        }
    },

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------

    _getIconClass(type) {
        const map = {
            'pdf': 'pdf', 'docx': 'doc', 'xlsx': 'doc',
            'python': 'code', 'javascript': 'code', 'typescript': 'code',
            'java': 'code', 'go': 'code', 'rust': 'code',
            'c': 'code', 'cpp': 'code', 'header': 'code',
            'html': 'code', 'css': 'code', 'json': 'code',
            'yaml': 'code',
            'markdown': 'markdown', 'text': 'markdown',
            'image': 'image',
        };
        return map[type] || 'default';
    },

    _getFileIconHtml(type) {
        const icon = this._getFileIcon(type);
        return `<i class="bi ${icon}"></i>`;
    },

    _getFileIcon(type) {
        const map = {
            'pdf': 'bi-file-earmark-pdf',
            'docx': 'bi-file-earmark-word',
            'xlsx': 'bi-file-earmark-spreadsheet',
            'markdown': 'bi-markdown',
            'text': 'bi-file-earmark-text',
            'python': 'bi-file-earmark-code',
            'javascript': 'bi-file-earmark-code',
            'typescript': 'bi-file-earmark-code',
            'java': 'bi-file-earmark-code',
            'go': 'bi-file-earmark-code',
            'rust': 'bi-file-earmark-code',
            'c': 'bi-file-earmark-code',
            'cpp': 'bi-file-earmark-code',
            'header': 'bi-file-earmark-code',
            'html': 'bi-filetype-html',
            'css': 'bi-filetype-css',
            'json': 'bi-filetype-json',
            'yaml': 'bi-file-earmark-code',
            'image': 'bi-file-earmark-image',
        };
        return map[type] || 'bi-file-earmark';
    },

    _getIconColor(type) {
        const map = {
            'pdf': '#ef4444', 'docx': '#3b82f6', 'xlsx': '#10b981',
            'python': '#10b981', 'javascript': '#f59e0b', 'typescript': '#3b82f6',
            'java': '#ef4444', 'go': '#3b82f6', 'rust': '#ef4444',
            'c': '#9ca3af', 'cpp': '#9ca3af', 'header': '#9ca3af',
            'html': '#ef4444', 'css': '#3b82f6', 'json': '#f59e0b',
            'yaml': '#10b981', 'markdown': '#7c6aef', 'text': '#9ca3af',
            'image': '#f59e0b',
        };
        return map[type] || '#9ca3af';
    },

    _formatSize(bytes) {
        if (!bytes || bytes === 0) return '0 B';
        const units = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, i)).toFixed(i > 0 ? 1 : 0) + ' ' + units[i];
    },

    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    _showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `kb-toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    },
};
