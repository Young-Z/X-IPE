/**
 * FolderViewManager - Detailed folder view panel
 * FEATURE-008 CR-006: Folder Tree UX Enhancement
 * 
 * Provides:
 * - Folder contents view replacing preview panel
 * - Breadcrumb navigation
 * - Action bar (Add File, Add Folder, Rename, Delete)
 * - File/folder items with hover actions
 * - Subfolder expansion in place
 */
class FolderViewManager {
    constructor(options) {
        this.container = options.container;
        this.onAction = options.onAction; // Callback: (action, path, data) => Promise<boolean>
        this.onNavigate = options.onNavigate; // Callback: (path) => void (when clicking file)
        this.onClose = options.onClose; // Callback: () => void (when closing folder view)
        this.currentPath = null;
        this.expandedFolders = new Set();
        this.confirmDialog = null;
    }

    /**
     * Initialize folder view
     */
    async init() {
        // Lazy load ConfirmDialog
        if (typeof ConfirmDialog !== 'undefined') {
            this.confirmDialog = new ConfirmDialog();
        }
    }

    /**
     * Render folder view for given path
     * @param {string} folderPath - Folder path to display
     */
    async render(folderPath) {
        this.currentPath = folderPath;
        
        try {
            const contents = await this._loadContents(folderPath);
            
            this.container.innerHTML = `
                <div class="folder-view">
                    <header class="folder-view-header">
                        <div class="folder-view-header-row">
                            ${this._renderPathBar(folderPath)}
                            <button class="folder-view-close" title="Close folder view">
                                <i class="bi bi-x-lg"></i>
                            </button>
                        </div>
                        ${this._renderActionBar()}
                    </header>
                    <div class="folder-view-content">
                        ${this._renderContents(contents)}
                    </div>
                </div>
            `;
            
            this._bindEvents();
        } catch (error) {
            console.error('Failed to load folder contents:', error);
            this.container.innerHTML = `
                <div class="folder-view folder-view-error">
                    <i class="bi bi-exclamation-triangle"></i>
                    <p>Failed to load folder contents</p>
                    <button class="btn btn-sm btn-outline-primary" onclick="location.reload()">
                        Retry
                    </button>
                </div>
            `;
        }
    }

    /**
     * Load folder contents from API
     * @param {string} folderPath 
     * @returns {Promise<Array>}
     */
    async _loadContents(folderPath) {
        const response = await fetch(`/api/ideas/folder-contents?path=${encodeURIComponent(folderPath)}`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to load folder');
        }
        
        return data.items || [];
    }

    /**
     * Render breadcrumb path bar
     * @param {string} path 
     * @returns {string} HTML
     */
    _renderPathBar(path) {
        const parts = path.split('/').filter(Boolean);
        
        const breadcrumbs = parts.map((part, i) => {
            const fullPath = parts.slice(0, i + 1).join('/');
            const isLast = i === parts.length - 1;
            return `<span class="breadcrumb-item ${isLast ? 'current' : 'clickable'}" 
                         data-path="${fullPath}">${this._escapeHtml(part)}</span>`;
        }).join('<span class="breadcrumb-sep"><i class="bi bi-chevron-right"></i></span>');
        
        return `<nav class="folder-view-breadcrumb" aria-label="Folder path">
            <span class="breadcrumb-item clickable" data-path="">
                <i class="bi bi-house"></i> Ideas
            </span>
            ${breadcrumbs ? '<span class="breadcrumb-sep"><i class="bi bi-chevron-right"></i></span>' + breadcrumbs : ''}
        </nav>`;
    }

    /**
     * Render action bar with buttons
     * @returns {string} HTML
     */
    _renderActionBar() {
        return `<div class="folder-view-actions">
            <button class="folder-view-action-btn" data-action="add-file" title="Add new file">
                <i class="bi bi-file-earmark-plus"></i>
                <span>Add File</span>
            </button>
            <button class="folder-view-action-btn" data-action="add-folder" title="Create new folder">
                <i class="bi bi-folder-plus"></i>
                <span>Add Folder</span>
            </button>
            <button class="folder-view-action-btn" data-action="rename" title="Rename folder">
                <i class="bi bi-pencil"></i>
                <span>Rename</span>
            </button>
            <button class="folder-view-action-btn danger" data-action="delete" title="Delete folder">
                <i class="bi bi-trash"></i>
                <span>Delete</span>
            </button>
        </div>`;
    }

    /**
     * Render folder contents
     * @param {Array} items 
     * @returns {string} HTML
     */
    _renderContents(items) {
        if (!items || items.length === 0) {
            return `<div class="folder-view-empty">
                <i class="bi bi-folder2-open"></i>
                <p>This folder is empty</p>
                <p class="text-muted">Use the buttons above to add files or folders</p>
            </div>`;
        }

        // Sort: folders first, then files, alphabetically
        const sorted = [...items].sort((a, b) => {
            if (a.type !== b.type) {
                return a.type === 'folder' ? -1 : 1;
            }
            return a.name.localeCompare(b.name);
        });

        return `<div class="folder-view-list">
            ${sorted.map(item => this._renderItem(item)).join('')}
        </div>`;
    }

    /**
     * Render a single item (file or folder)
     * @param {Object} item 
     * @returns {string} HTML
     */
    _renderItem(item) {
        const isFolder = item.type === 'folder';
        const icon = isFolder ? 'bi-folder-fill folder-icon' : this._getFileIcon(item.name);
        const isExpanded = this.expandedFolders.has(item.path);
        
        // TASK-240: Add 'into' action for folders (enter folder view)
        const actions = isFolder 
            ? ['into', 'rename', 'delete', 'duplicate']
            : ['rename', 'delete', 'duplicate', 'download'];

        // TASK-241: Add draggable support
        return `
            <div class="folder-view-item ${isFolder ? 'is-folder' : 'is-file'} ${isExpanded ? 'expanded' : ''}" 
                 data-path="${item.path}" 
                 data-type="${item.type}"
                 data-name="${this._escapeHtml(item.name)}"
                 draggable="true">
                <div class="folder-view-item-main">
                    ${isFolder ? `
                        <button class="folder-view-item-toggle" title="Expand folder">
                            <i class="bi bi-chevron-right"></i>
                        </button>
                    ` : '<span class="folder-view-item-spacer"></span>'}
                    <i class="folder-view-item-icon bi ${icon}"></i>
                    <span class="folder-view-item-name">${this._escapeHtml(item.name)}</span>
                    <div class="folder-view-item-actions">
                        ${actions.map(action => `
                            <button class="folder-view-item-action ${action === 'delete' ? 'danger' : ''} ${action === 'into' ? 'into-btn' : ''}" 
                                    data-action="${action}" 
                                    title="${this._getActionTitle(action)}">
                                <i class="bi bi-${this._getActionIcon(action)}"></i>
                            </button>
                        `).join('')}
                    </div>
                </div>
                ${isFolder ? '<div class="folder-view-item-children"></div>' : ''}
            </div>
        `;
    }

    /**
     * Get file icon based on extension
     * @param {string} filename 
     * @returns {string} Bootstrap icon class
     */
    _getFileIcon(filename) {
        const ext = filename.split('.').pop()?.toLowerCase();
        const iconMap = {
            'md': 'bi-markdown',
            'txt': 'bi-file-text',
            'json': 'bi-braces',
            'html': 'bi-filetype-html',
            'css': 'bi-filetype-css',
            'js': 'bi-filetype-js',
            'py': 'bi-filetype-py',
            'pdf': 'bi-file-pdf',
            'png': 'bi-file-image',
            'jpg': 'bi-file-image',
            'jpeg': 'bi-file-image',
            'gif': 'bi-file-image',
            'svg': 'bi-file-image'
        };
        return iconMap[ext] || 'bi-file-earmark';
    }

    /**
     * Get action icon
     * @param {string} action 
     * @returns {string}
     */
    _getActionIcon(action) {
        const icons = {
            'into': 'box-arrow-in-right',  // TASK-240: Enter folder icon
            'rename': 'pencil',
            'delete': 'trash',
            'duplicate': 'copy',
            'download': 'download'
        };
        return icons[action] || action;
    }

    /**
     * Get action title
     * @param {string} action 
     * @returns {string}
     */
    _getActionTitle(action) {
        const titles = {
            'into': 'Enter folder',  // TASK-240: Enter folder tooltip
            'rename': 'Rename',
            'delete': 'Delete',
            'duplicate': 'Duplicate',
            'download': 'Download'
        };
        return titles[action] || action;
    }

    /**
     * Bind event listeners
     */
    _bindEvents() {
        const container = this.container.querySelector('.folder-view');
        if (!container) return;

        // Close button
        const closeBtn = container.querySelector('.folder-view-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                if (this.onClose) this.onClose();
            });
        }

        // Breadcrumb navigation
        container.querySelectorAll('.breadcrumb-item.clickable').forEach(item => {
            item.addEventListener('click', () => {
                const path = item.dataset.path;
                if (path === '') {
                    // Navigate to root - close folder view
                    if (this.onClose) this.onClose();
                } else {
                    this.render(path);
                }
            });
        });

        // Action bar buttons
        container.querySelectorAll('.folder-view-action-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                this._handleFolderAction(action);
            });
        });

        // Item clicks (file navigation, folder expansion)
        container.querySelectorAll('.folder-view-item').forEach(item => {
            // Main area click (not action buttons)
            const mainArea = item.querySelector('.folder-view-item-main');
            mainArea.addEventListener('click', (e) => {
                // Ignore if clicking on action buttons or toggle
                if (e.target.closest('.folder-view-item-actions') || 
                    e.target.closest('.folder-view-item-toggle')) {
                    return;
                }
                
                const path = item.dataset.path;
                const type = item.dataset.type;
                
                if (type === 'file' && this.onNavigate) {
                    this.onNavigate(path);
                } else if (type === 'folder') {
                    this._toggleFolder(item);
                }
            });

            // Toggle button for folders
            const toggle = item.querySelector('.folder-view-item-toggle');
            if (toggle) {
                toggle.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this._toggleFolder(item);
                });
            }

            // Item action buttons
            item.querySelectorAll('.folder-view-item-action').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const action = btn.dataset.action;
                    const path = item.dataset.path;
                    const name = item.dataset.name;
                    const type = item.dataset.type;
                    this._handleItemAction(action, path, name, type);
                });
            });
            
            // TASK-241: Drag and drop events
            this._bindDragEvents(item);
        });
        
        // TASK-241: Allow dropping on the folder view content area (move to current folder)
        const contentArea = container.querySelector('.folder-view-content');
        if (contentArea) {
            this._bindDropZone(contentArea);
        }
    }
    
    /**
     * TASK-241: Bind drag events to an item
     * @param {HTMLElement} item 
     */
    _bindDragEvents(item) {
        item.addEventListener('dragstart', (e) => {
            e.stopPropagation();
            const path = item.dataset.path;
            const type = item.dataset.type;
            const name = item.dataset.name;
            
            e.dataTransfer.setData('text/plain', JSON.stringify({ path, type, name }));
            e.dataTransfer.effectAllowed = 'move';
            item.classList.add('dragging');
            
            // Store reference for drop validation
            this._draggingItem = { path, type, name };
        });
        
        item.addEventListener('dragend', (e) => {
            item.classList.remove('dragging');
            this._draggingItem = null;
            
            // Clean up any drop-target classes
            this.container.querySelectorAll('.drop-target').forEach(el => {
                el.classList.remove('drop-target');
            });
        });
        
        // Only folders can be drop targets
        if (item.dataset.type === 'folder') {
            item.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                // Validate drop is allowed
                if (this._canDropOn(item.dataset.path)) {
                    e.dataTransfer.dropEffect = 'move';
                    item.classList.add('drop-target');
                } else {
                    e.dataTransfer.dropEffect = 'none';
                }
            });
            
            item.addEventListener('dragleave', (e) => {
                // Only remove if actually leaving this element
                if (!item.contains(e.relatedTarget)) {
                    item.classList.remove('drop-target');
                }
            });
            
            item.addEventListener('drop', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                item.classList.remove('drop-target');
                
                const targetPath = item.dataset.path;
                await this._handleDrop(e, targetPath);
            });
        }
    }
    
    /**
     * TASK-241: Bind drop zone events (for dropping into current folder)
     * @param {HTMLElement} zone 
     */
    _bindDropZone(zone) {
        zone.addEventListener('dragover', (e) => {
            // Only handle if not over a folder item
            if (!e.target.closest('.folder-view-item.is-folder')) {
                e.preventDefault();
                if (this._canDropOn(this.currentPath)) {
                    e.dataTransfer.dropEffect = 'move';
                    zone.classList.add('drop-target-zone');
                }
            }
        });
        
        zone.addEventListener('dragleave', (e) => {
            if (!zone.contains(e.relatedTarget)) {
                zone.classList.remove('drop-target-zone');
            }
        });
        
        zone.addEventListener('drop', async (e) => {
            // Only handle if not over a folder item
            if (!e.target.closest('.folder-view-item.is-folder')) {
                e.preventDefault();
                zone.classList.remove('drop-target-zone');
                await this._handleDrop(e, this.currentPath);
            }
        });
    }
    
    /**
     * TASK-241: Check if item can be dropped on target
     * @param {string} targetPath 
     * @returns {boolean}
     */
    _canDropOn(targetPath) {
        if (!this._draggingItem) return false;
        
        const sourcePath = this._draggingItem.path;
        
        // Can't drop on self
        if (sourcePath === targetPath) return false;
        
        // Can't drop parent into child
        if (targetPath.startsWith(sourcePath + '/')) return false;
        
        // Can't drop into same parent (already there)
        const sourceParent = sourcePath.substring(0, sourcePath.lastIndexOf('/'));
        if (sourceParent === targetPath) return false;
        
        return true;
    }
    
    /**
     * TASK-241: Handle drop event
     * @param {DragEvent} e 
     * @param {string} targetPath 
     */
    async _handleDrop(e, targetPath) {
        try {
            const data = JSON.parse(e.dataTransfer.getData('text/plain'));
            const sourcePath = data.path;
            
            if (!this._canDropOn(targetPath)) {
                return;
            }
            
            // Call move action through onAction callback
            if (this.onAction) {
                const success = await this.onAction('move', sourcePath, { 
                    targetPath,
                    name: data.name,
                    type: data.type 
                });
                
                if (success) {
                    await this.refresh();
                }
            }
        } catch (error) {
            console.error('Drop failed:', error);
        }
    }

    /**
     * Handle folder-level actions (from action bar)
     * @param {string} action 
     */
    async _handleFolderAction(action) {
        switch (action) {
            case 'add-file':
                if (this.onAction) {
                    await this.onAction('add-file', this.currentPath, {});
                }
                break;
            case 'add-folder':
                if (this.onAction) {
                    await this.onAction('add-folder', this.currentPath, {});
                }
                break;
            case 'rename':
                if (this.onAction) {
                    await this.onAction('rename', this.currentPath, { type: 'folder' });
                }
                break;
            case 'delete':
                await this._confirmAndDelete(this.currentPath, 'folder');
                break;
        }
    }

    /**
     * Handle item-level actions
     * @param {string} action 
     * @param {string} path 
     * @param {string} name 
     * @param {string} type 
     */
    async _handleItemAction(action, path, name, type) {
        switch (action) {
            case 'into':  // TASK-240: Navigate into folder
                if (type === 'folder') {
                    await this.render(path);
                }
                break;
            case 'rename':
                if (this.onAction) {
                    await this.onAction('rename', path, { name, type });
                }
                break;
            case 'delete':
                await this._confirmAndDelete(path, type, name);
                break;
            case 'duplicate':
                if (this.onAction) {
                    const success = await this.onAction('duplicate', path, { name, type });
                    if (success) {
                        await this.refresh();
                    }
                }
                break;
            case 'download':
                this._downloadFile(path);
                break;
        }
    }

    /**
     * Confirm and delete an item
     * @param {string} path 
     * @param {string} type 
     * @param {string} name 
     */
    async _confirmAndDelete(path, type, name = null) {
        // Get delete info for confirmation
        let itemCount = 0;
        const itemName = name || path.split('/').pop();
        
        if (type === 'folder') {
            try {
                const response = await fetch(`/api/ideas/delete-info?path=${encodeURIComponent(path)}`);
                const data = await response.json();
                if (data.success) {
                    itemCount = data.item_count || 0;
                }
            } catch (e) {
                console.warn('Failed to get delete info:', e);
            }
        }

        // Show confirmation
        let confirmed = true;
        if (this.confirmDialog) {
            confirmed = await this.confirmDialog.confirmDelete(itemName, type, itemCount);
        } else {
            const msg = type === 'folder' && itemCount > 0
                ? `Delete "${itemName}" and all ${itemCount} items inside?`
                : `Delete "${itemName}"?`;
            confirmed = confirm(msg);
        }

        if (confirmed && this.onAction) {
            const success = await this.onAction('delete', path, { name: itemName, type });
            if (success) {
                if (path === this.currentPath) {
                    // Deleted current folder - close view
                    if (this.onClose) this.onClose();
                } else {
                    await this.refresh();
                }
            }
        }
    }

    /**
     * Download a file
     * @param {string} path 
     */
    _downloadFile(path) {
        const url = `/api/ideas/download?path=${encodeURIComponent(path)}`;
        const link = document.createElement('a');
        link.href = url;
        link.download = path.split('/').pop();
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    /**
     * Toggle folder expansion
     * @param {HTMLElement} folderItem 
     */
    async _toggleFolder(folderItem) {
        const path = folderItem.dataset.path;
        const childrenContainer = folderItem.querySelector('.folder-view-item-children');
        
        if (!childrenContainer) return;

        const isExpanded = folderItem.classList.contains('expanded');
        
        if (isExpanded) {
            // Collapse
            folderItem.classList.remove('expanded');
            childrenContainer.innerHTML = '';
            this.expandedFolders.delete(path);
        } else {
            // Expand - load children
            try {
                const contents = await this._loadContents(path);
                childrenContainer.innerHTML = this._renderContents(contents);
                folderItem.classList.add('expanded');
                this.expandedFolders.add(path);
                
                // Rebind events for new items
                this._bindChildEvents(childrenContainer);
            } catch (error) {
                console.error('Failed to expand folder:', error);
            }
        }
    }

    /**
     * Bind events for dynamically loaded children
     * @param {HTMLElement} container 
     */
    _bindChildEvents(container) {
        container.querySelectorAll('.folder-view-item').forEach(item => {
            const mainArea = item.querySelector('.folder-view-item-main');
            mainArea.addEventListener('click', (e) => {
                if (e.target.closest('.folder-view-item-actions') || 
                    e.target.closest('.folder-view-item-toggle')) {
                    return;
                }
                
                const path = item.dataset.path;
                const type = item.dataset.type;
                
                if (type === 'file' && this.onNavigate) {
                    this.onNavigate(path);
                } else if (type === 'folder') {
                    this._toggleFolder(item);
                }
            });

            const toggle = item.querySelector('.folder-view-item-toggle');
            if (toggle) {
                toggle.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this._toggleFolder(item);
                });
            }

            item.querySelectorAll('.folder-view-item-action').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const action = btn.dataset.action;
                    const path = item.dataset.path;
                    const name = item.dataset.name;
                    const type = item.dataset.type;
                    this._handleItemAction(action, path, name, type);
                });
            });
            
            // TASK-241: Bind drag events for dynamically loaded children
            this._bindDragEvents(item);
        });
    }

    /**
     * Refresh current folder view
     */
    async refresh() {
        if (this.currentPath) {
            await this.render(this.currentPath);
        }
    }

    /**
     * Close the folder view
     */
    close() {
        this.currentPath = null;
        this.expandedFolders.clear();
        this.container.innerHTML = '';
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} str 
     * @returns {string}
     */
    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FolderViewManager;
}
