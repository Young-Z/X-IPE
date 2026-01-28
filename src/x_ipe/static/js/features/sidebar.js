/**
 * Project Sidebar Navigation
 * FEATURE-001: Project Navigation (Polling Implementation)
 * 
 * Uses HTTP polling every 5 seconds to detect structure changes.
 */
class ProjectSidebar {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.selectedFile = null;
        this.sections = [];
        this.lastStructureHash = null;
        this.pollInterval = 5000; // 5 seconds
        
        // FEATURE-009: Track changed paths for visual indicator
        this.changedPaths = new Set();
        this.previousPathMtimes = new Map();  // Map<path, mtime> for content change detection
        
        this._startPolling();
    }
    
    /**
     * Start polling for structure changes
     */
    _startPolling() {
        setInterval(() => {
            this._checkForChanges();
        }, this.pollInterval);
    }
    
    /**
     * Check for structure changes via HTTP polling
     */
    async _checkForChanges() {
        try {
            const response = await fetch('/api/project/structure');
            if (!response.ok) return;
            
            const data = await response.json();
            const newHash = this._hashStructure(data.sections);
            
            // First load - initialize paths
            if (this.lastStructureHash === null) {
                this.lastStructureHash = newHash;
                this.previousPathMtimes = this._extractAllPathMtimes(data.sections);
                return;
            }
            
            // Check if structure changed (includes mtime changes since JSON hash includes mtime)
            if (this.lastStructureHash !== newHash) {
                // Detect which paths changed (structure + content)
                const currentPathMtimes = this._extractAllPathMtimes(data.sections);
                this._detectChangedPaths(this.previousPathMtimes, currentPathMtimes);
                
                this.lastStructureHash = newHash;
                this.previousPathMtimes = currentPathMtimes;
                this.sections = data.sections;
                this.render();
                this.showToast('File structure updated', 'info');
            }
        } catch (error) {
            console.error('[ProjectSidebar] Poll error:', error);
        }
    }
    
    /**
     * Create a simple hash of the structure for comparison
     */
    _hashStructure(sections) {
        return JSON.stringify(sections);
    }
    
    // =========================================================================
    // FEATURE-009: File Change Indicator
    // =========================================================================
    
    /**
     * Extract all file/folder paths with mtimes from structure
     * Returns Map<path, mtime> where mtime is null for folders
     */
    _extractAllPathMtimes(sections) {
        const pathMtimes = new Map();
        
        const traverse = (items) => {
            for (const item of items) {
                if (item.path) {
                    // Store mtime for files (used for content change detection)
                    pathMtimes.set(item.path, item.mtime || null);
                }
                if (item.children) {
                    traverse(item.children);
                }
            }
        };
        
        for (const section of sections) {
            if (section.children) {
                traverse(section.children);
            }
        }
        
        return pathMtimes;
    }
    
    /**
     * Detect changed paths between old and new structure
     * Detects: new files, removed files, and content modifications (mtime changes)
     */
    _detectChangedPaths(oldPathMtimes, newPathMtimes) {
        // Find new paths (added)
        for (const [path, mtime] of newPathMtimes) {
            if (!oldPathMtimes.has(path)) {
                this._addChangedPath(path);
            }
        }
        
        // Find removed paths (mark parent as changed)
        for (const [path, mtime] of oldPathMtimes) {
            if (!newPathMtimes.has(path)) {
                const parent = this._getParentPath(path);
                if (parent) {
                    this._addChangedPath(parent);
                }
            }
        }
        
        // Find modified files (mtime changed)
        for (const [path, newMtime] of newPathMtimes) {
            if (newMtime !== null && oldPathMtimes.has(path)) {
                const oldMtime = oldPathMtimes.get(path);
                if (oldMtime !== null && newMtime !== oldMtime) {
                    this._addChangedPath(path);
                }
            }
        }
    }
    
    /**
     * Add path and bubble up to parents
     */
    _addChangedPath(path) {
        if (!path) return;
        
        this.changedPaths.add(path);
        
        // Bubble up to parents
        const parts = path.split('/');
        for (let i = parts.length - 1; i > 0; i--) {
            const parentPath = parts.slice(0, i).join('/');
            this.changedPaths.add(parentPath);
        }
    }
    
    /**
     * Clear path and cleanup parents if no changed children
     */
    _clearChangedPath(path) {
        if (!this.changedPaths.has(path)) return;
        
        this.changedPaths.delete(path);
        
        // Check parents - clear if no other changed children
        const parts = path.split('/');
        for (let i = parts.length - 1; i > 0; i--) {
            const parentPath = parts.slice(0, i).join('/');
            if (!this._hasChangedChildren(parentPath)) {
                this.changedPaths.delete(parentPath);
            }
        }
    }
    
    /**
     * Check if folder has any changed children
     */
    _hasChangedChildren(folderPath) {
        const prefix = folderPath + '/';
        for (const path of this.changedPaths) {
            if (path.startsWith(prefix)) {
                return true;
            }
        }
        return false;
    }
    
    /**
     * Get parent path
     */
    _getParentPath(path) {
        const parts = path.split('/');
        if (parts.length <= 1) return null;
        return parts.slice(0, -1).join('/');
    }
    
    /**
     * Load project structure from API
     */
    async load() {
        try {
            const response = await fetch('/api/project/structure');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.sections = data.sections;
            this.lastStructureHash = this._hashStructure(data.sections);
            this.previousPathMtimes = this._extractAllPathMtimes(data.sections);
            this.render();
        } catch (error) {
            console.error('Failed to load project structure:', error);
            this.container.innerHTML = `
                <div class="nav-empty text-danger">
                    <i class="bi bi-exclamation-triangle"></i> Failed to load project structure
                </div>
            `;
        }
    }
    
    /**
     * Render the navigation tree
     */
    render() {
        if (!this.sections || this.sections.length === 0) {
            this.container.innerHTML = '<div class="nav-empty">No sections found</div>';
            return;
        }
        
        let html = '';
        
        for (const section of this.sections) {
            html += this.renderSection(section);
        }
        
        this.container.innerHTML = html;
        this.bindEvents();
    }
    
    /**
     * Render a single section
     */
    renderSection(section) {
        const icon = section.icon || 'bi-folder';
        const hasChildren = section.children && section.children.length > 0;
        
        // CR-004: Special handling for Workplace section - show submenu with Ideation and UIUX Feedbacks
        if (section.id === 'workplace') {
            return `
                <div class="nav-section" data-section-id="${section.id}">
                    <div class="nav-section-header sidebar-parent" data-section-id="${section.id}" data-no-action="true">
                        <i class="bi bi-briefcase"></i>
                        <span>Workplace</span>
                        <i class="bi bi-chevron-down submenu-indicator"></i>
                    </div>
                    <div class="sidebar-submenu">
                        <div class="nav-section-header sidebar-child nav-workplace-header" data-section-id="ideation">
                            <i class="bi ${icon}"></i>
                            <span>Ideation</span>
                        </div>
                        <div class="nav-section-header sidebar-child nav-uiux-feedbacks" data-section-id="uiux-feedbacks">
                            <i class="bi bi-chat-square-text"></i>
                            <span>UIUX Feedbacks</span>
                        </div>
                    </div>
                </div>
            `;
        }
        
        let html = `
            <div class="nav-section" data-section-id="${section.id}">
                <div class="nav-section-header collapsed" data-bs-toggle="collapse" data-bs-target="#section-${section.id}">
                    <i class="bi ${icon}"></i>
                    <span>${section.label}</span>
                    <i class="bi bi-chevron-down chevron"></i>
                </div>
                <div class="collapse nav-section-content" id="section-${section.id}">
        `;
        
        if (!section.exists) {
            html += '<div class="nav-empty">Folder not found</div>';
        } else if (!hasChildren) {
            html += '<div class="nav-empty">No files</div>';
        } else {
            html += this.renderChildren(section.children);
        }
        
        html += '</div></div>';
        return html;
    }
    
    /**
     * Render children (files and folders)
     * Files are rendered above folders
     */
    renderChildren(children, depth = 0) {
        if (!children || children.length === 0) {
            return '';
        }
        
        let html = '';
        const indent = depth * 1; // rem
        
        // Separate files and folders
        const files = children.filter(item => item.type !== 'folder');
        const folders = children.filter(item => item.type === 'folder');
        
        // Render files first
        for (const item of files) {
            html += this.renderFile(item, depth);
        }
        
        // Then render folders
        for (const item of folders) {
            html += this.renderFolder(item, depth);
        }
        
        return html;
    }
    
    /**
     * Render a folder item
     */
    renderFolder(folder, depth) {
        const folderId = folder.path.replace(/[\/\.]/g, '-');
        const hasChildren = folder.children && folder.children.length > 0;
        const paddingLeft = 2 + (depth * 0.75);
        const isChanged = this.changedPaths.has(folder.path);
        
        let html = `
            <div class="nav-item nav-folder${isChanged ? ' has-changes' : ''}" 
                 style="padding-left: ${paddingLeft}rem"
                 data-bs-toggle="collapse" 
                 data-bs-target="#folder-${folderId}"
                 data-path="${folder.path}">
                ${isChanged ? '<span class="change-indicator"></span>' : ''}
                <i class="bi bi-folder"></i>
                <span>${folder.name}</span>
                ${hasChildren ? '<i class="bi bi-chevron-down chevron ms-auto" style="font-size: 0.7rem;"></i>' : ''}
            </div>
        `;
        
        if (hasChildren) {
            html += `
                <div class="collapse nav-folder-content" id="folder-${folderId}">
                    ${this.renderChildren(folder.children, depth + 1)}
                </div>
            `;
        }
        
        return html;
    }
    
    /**
     * Render a file item
     */
    renderFile(file, depth) {
        const icon = this.getFileIcon(file.name);
        const paddingLeft = 2 + (depth * 0.75);
        const isActive = this.selectedFile === file.path;
        const isChanged = this.changedPaths.has(file.path);
        
        return `
            <div class="nav-item nav-file${isActive ? ' active' : ''}${isChanged ? ' has-changes' : ''}" 
                 style="padding-left: ${paddingLeft}rem"
                 data-path="${file.path}">
                ${isChanged ? '<span class="change-indicator"></span>' : ''}
                <i class="bi ${icon}"></i>
                <span>${file.name}</span>
            </div>
        `;
    }
    
    /**
     * Get icon for file type
     */
    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const icons = {
            'md': 'bi-file-earmark-text',
            'py': 'bi-filetype-py',
            'js': 'bi-filetype-js',
            'ts': 'bi-filetype-tsx',
            'html': 'bi-filetype-html',
            'css': 'bi-filetype-css',
            'json': 'bi-filetype-json',
            'yaml': 'bi-file-code',
            'yml': 'bi-file-code',
            'txt': 'bi-file-text',
            'png': 'bi-file-image',
            'jpg': 'bi-file-image',
            'jpeg': 'bi-file-image',
            'gif': 'bi-file-image',
            'svg': 'bi-file-image',
            'webp': 'bi-file-image',
            'bmp': 'bi-file-image',
            'ico': 'bi-file-image'
        };
        return icons[ext] || 'bi-file-earmark';
    }
    
    /**
     * Bind click events to file items
     */
    bindEvents() {
        // File click events
        const fileItems = this.container.querySelectorAll('.nav-file');
        fileItems.forEach(item => {
            item.addEventListener('click', (e) => {
                // Remove active from all files
                fileItems.forEach(f => f.classList.remove('active'));
                // Add active to clicked
                item.classList.add('active');
                
                // FEATURE-022-A: Clear sidebar-child active state when selecting a file
                const sidebarChildren = this.container.querySelectorAll('.sidebar-child');
                sidebarChildren.forEach(child => child.classList.remove('active'));
                
                const path = item.dataset.path;
                this.selectedFile = path;
                
                // FEATURE-009: Clear change indicator for this file
                if (this.changedPaths.has(path)) {
                    this._clearChangedPath(path);
                    // Update UI - remove indicator and class
                    item.classList.remove('has-changes');
                    const indicator = item.querySelector('.change-indicator');
                    if (indicator) indicator.remove();
                    // Update parent folders if needed
                    this._updateParentIndicators(path);
                }
                
                this.onFileSelect(path);
            });
        });
        
        // Workplace section click handler - CR-004: Now Ideation submenu item
        const workplaceHeader = this.container.querySelector('.nav-workplace-header');
        if (workplaceHeader) {
            workplaceHeader.addEventListener('click', () => {
                // Clear file selection
                fileItems.forEach(f => f.classList.remove('active'));
                this.selectedFile = null;
                
                // FEATURE-022-A: Update sidebar-child active state
                const sidebarChildren = this.container.querySelectorAll('.sidebar-child');
                sidebarChildren.forEach(child => child.classList.remove('active'));
                workplaceHeader.classList.add('active');
                
                // BUGFIX: Clear contentRenderer.currentPath to prevent auto-refresh
                // from redirecting back to previously viewed file when on Workplace
                if (window.contentRenderer) {
                    window.contentRenderer.currentPath = null;
                }
                
                // Update breadcrumb - CR-004: Show "Ideation" instead of "Workplace"
                const breadcrumb = document.getElementById('breadcrumb');
                breadcrumb.innerHTML = '<li class="breadcrumb-item active">Ideation</li>';
                
                // Show Create Idea button in top bar
                const createIdeaBtn = document.getElementById('btn-create-idea');
                if (createIdeaBtn) {
                    createIdeaBtn.classList.remove('d-none');
                }
                
                // Render WorkplaceManager view
                const container = document.getElementById('content-body');
                if (window.workplaceManager) {
                    window.workplaceManager.render(container);
                }
            });
        }
        
        // FEATURE-022-A: UIUX Feedbacks click handler - render browser simulator in content area
        const uiuxFeedbacksHeader = this.container.querySelector('.nav-uiux-feedbacks');
        if (uiuxFeedbacksHeader) {
            uiuxFeedbacksHeader.addEventListener('click', () => {
                // Clear file selection
                fileItems.forEach(f => f.classList.remove('active'));
                this.selectedFile = null;
                
                // Update sidebar-child active state
                const sidebarChildren = this.container.querySelectorAll('.sidebar-child');
                sidebarChildren.forEach(child => child.classList.remove('active'));
                uiuxFeedbacksHeader.classList.add('active');
                
                // Clear contentRenderer.currentPath to prevent auto-refresh
                if (window.contentRenderer) {
                    window.contentRenderer.currentPath = null;
                }
                
                // Hide Create Idea button
                const createIdeaBtn = document.getElementById('btn-create-idea');
                if (createIdeaBtn) {
                    createIdeaBtn.classList.add('d-none');
                }
                
                // Update breadcrumb
                const breadcrumb = document.getElementById('breadcrumb');
                breadcrumb.innerHTML = '<li class="breadcrumb-item active">UI/UX Feedbacks</li>';
                
                // Render Browser Simulator in content area
                const container = document.getElementById('content-body');
                if (window.uiuxFeedbackManager) {
                    window.uiuxFeedbackManager.render(container);
                }
            });
        }
        
        // CR-004: Prevent parent item click action
        const parentItems = this.container.querySelectorAll('.sidebar-parent[data-no-action="true"]');
        parentItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                // Parent item does nothing - children are always visible
            });
        });
        
        // Section header collapse tracking - CR-004: Exclude sidebar-parent and sidebar-child
        const sectionHeaders = this.container.querySelectorAll('.nav-section-header:not(.nav-workplace-header):not(.sidebar-parent):not(.sidebar-child)');
        sectionHeaders.forEach(header => {
            const target = document.querySelector(header.dataset.bsTarget);
            if (target) {
                target.addEventListener('hide.bs.collapse', () => {
                    header.classList.add('collapsed');
                });
                target.addEventListener('show.bs.collapse', () => {
                    header.classList.remove('collapsed');
                });
            }
        });
        
        // Hover expand/collapse for sections and folders
        this._bindHoverExpand();
    }
    
    /**
     * Bind hover expand/collapse behavior to sections and folders
     * Expands after 1 sec hover, collapses 1 second after mouse leaves
     * Click pins the item (won't auto-collapse)
     */
    _bindHoverExpand() {
        // Section headers (not workplace, sidebar-parent, or sidebar-child) - CR-004
        const sectionHeaders = this.container.querySelectorAll('.nav-section-header:not(.nav-workplace-header):not(.sidebar-parent):not(.sidebar-child)');
        sectionHeaders.forEach(header => {
            const targetSelector = header.dataset.bsTarget;
            const target = document.querySelector(targetSelector);
            if (!target) return;
            
            let collapseTimeout = null;
            let expandTimeout = null;
            let isPinned = false;
            const section = header.closest('.nav-section');
            
            // Click to pin/unpin
            header.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                if (expandTimeout) {
                    clearTimeout(expandTimeout);
                    expandTimeout = null;
                }
                if (collapseTimeout) {
                    clearTimeout(collapseTimeout);
                    collapseTimeout = null;
                }
                
                if (isPinned) {
                    // Unpin and collapse
                    isPinned = false;
                    header.classList.remove('pinned');
                    bootstrap.Collapse.getOrCreateInstance(target).hide();
                } else {
                    // Pin and expand
                    isPinned = true;
                    header.classList.add('pinned');
                    if (!target.classList.contains('show')) {
                        bootstrap.Collapse.getOrCreateInstance(target).show();
                    }
                }
            });
            
            // Expand after 1 sec hover
            header.addEventListener('mouseenter', () => {
                if (collapseTimeout) {
                    clearTimeout(collapseTimeout);
                    collapseTimeout = null;
                }
                if (!target.classList.contains('show') && !isPinned) {
                    expandTimeout = setTimeout(() => {
                        bootstrap.Collapse.getOrCreateInstance(target).show();
                    }, 500);
                }
            });
            
            header.addEventListener('mouseleave', () => {
                if (expandTimeout) {
                    clearTimeout(expandTimeout);
                    expandTimeout = null;
                }
            });
            
            // Collapse after 1 sec when leaving the entire section (if not pinned)
            section.addEventListener('mouseleave', () => {
                if (expandTimeout) {
                    clearTimeout(expandTimeout);
                    expandTimeout = null;
                }
                if (!isPinned) {
                    collapseTimeout = setTimeout(() => {
                        if (target.classList.contains('show')) {
                            bootstrap.Collapse.getOrCreateInstance(target).hide();
                        }
                    }, 500);
                }
            });
            
            // Cancel collapse if re-entering section
            section.addEventListener('mouseenter', () => {
                if (collapseTimeout) {
                    clearTimeout(collapseTimeout);
                    collapseTimeout = null;
                }
            });
        });
        
        // Folder items
        const folderItems = this.container.querySelectorAll('.nav-folder');
        folderItems.forEach(folder => {
            const targetSelector = folder.dataset.bsTarget;
            const target = document.querySelector(targetSelector);
            if (!target) return;
            
            let collapseTimeout = null;
            let expandTimeout = null;
            let isPinned = false;
            
            // Click to pin/unpin
            folder.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                if (expandTimeout) {
                    clearTimeout(expandTimeout);
                    expandTimeout = null;
                }
                if (collapseTimeout) {
                    clearTimeout(collapseTimeout);
                    collapseTimeout = null;
                }
                
                if (isPinned) {
                    // Unpin and collapse
                    isPinned = false;
                    folder.classList.remove('pinned');
                    bootstrap.Collapse.getOrCreateInstance(target).hide();
                } else {
                    // Pin and expand
                    isPinned = true;
                    folder.classList.add('pinned');
                    if (!target.classList.contains('show')) {
                        bootstrap.Collapse.getOrCreateInstance(target).show();
                    }
                }
            });
            
            // Expand after 1 sec hover
            folder.addEventListener('mouseenter', () => {
                if (collapseTimeout) {
                    clearTimeout(collapseTimeout);
                    collapseTimeout = null;
                }
                if (!target.classList.contains('show') && !isPinned) {
                    expandTimeout = setTimeout(() => {
                        bootstrap.Collapse.getOrCreateInstance(target).show();
                    }, 500);
                }
            });
            
            folder.addEventListener('mouseleave', (e) => {
                if (expandTimeout) {
                    clearTimeout(expandTimeout);
                    expandTimeout = null;
                }
                // Only start collapse timer if not entering the folder content and not pinned
                if (!target.contains(e.relatedTarget) && !isPinned) {
                    collapseTimeout = setTimeout(() => {
                        if (target.classList.contains('show')) {
                            bootstrap.Collapse.getOrCreateInstance(target).hide();
                        }
                    }, 500);
                }
            });
            
            target.addEventListener('mouseleave', (e) => {
                // Only start collapse timer if not re-entering the folder header and not pinned
                if (e.relatedTarget !== folder && !folder.contains(e.relatedTarget) && !isPinned) {
                    collapseTimeout = setTimeout(() => {
                        if (target.classList.contains('show')) {
                            bootstrap.Collapse.getOrCreateInstance(target).hide();
                        }
                    }, 500);
                }
            });
            
            // Cancel collapse if hovering folder or its content
            target.addEventListener('mouseenter', () => {
                if (collapseTimeout) {
                    clearTimeout(collapseTimeout);
                    collapseTimeout = null;
                }
            });
        });
    }
    
    /**
     * FEATURE-009: Update parent folder indicators after clearing a file
     */
    _updateParentIndicators(path) {
        const parts = path.split('/');
        for (let i = parts.length - 1; i > 0; i--) {
            const parentPath = parts.slice(0, i).join('/');
            if (!this.changedPaths.has(parentPath)) {
                // Find and update the parent folder element
                const parentEl = this.container.querySelector(`.nav-folder[data-path="${parentPath}"]`);
                if (parentEl) {
                    parentEl.classList.remove('has-changes');
                    const indicator = parentEl.querySelector('.change-indicator');
                    if (indicator) indicator.remove();
                }
            }
        }
    }
    
    /**
     * Handle file selection - loads content via ContentRenderer
     */
    onFileSelect(path) {
        // Stop workplace polling when navigating to a file
        if (window.workplaceManager) {
            window.workplaceManager.stop();
        }
        
        // Hide Create Idea button when leaving Workplace
        const createIdeaBtn = document.getElementById('btn-create-idea');
        if (createIdeaBtn) {
            createIdeaBtn.classList.add('d-none');
        }
        
        // Check with ContentEditor if navigation is allowed (unsaved changes)
        if (window.contentEditor) {
            const canNavigate = window.contentEditor.setCurrentPath(path);
            if (!canNavigate) {
                return;  // Navigation blocked due to unsaved changes
            }
        }
        
        // Update breadcrumb
        const breadcrumb = document.getElementById('breadcrumb');
        const parts = path.split('/');
        breadcrumb.innerHTML = parts.map((part, index) => {
            const isLast = index === parts.length - 1;
            return `<li class="breadcrumb-item ${isLast ? 'active' : ''}">${part}</li>`;
        }).join('');
        
        // Load content via ContentRenderer
        if (window.contentRenderer) {
            window.contentRenderer.load(path);
        }
        
        // Emit custom event for other components
        const event = new CustomEvent('fileSelected', { detail: { path } });
        document.dispatchEvent(event);
    }
    
    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toastId = 'toast-' + Date.now();
        
        const bgClass = {
            'info': 'bg-info',
            'success': 'bg-success',
            'warning': 'bg-warning',
            'error': 'bg-danger'
        }[type] || 'bg-info';
        
        const toastHtml = `
            <div id="${toastId}" class="toast ${bgClass} text-white" role="alert">
                <div class="toast-body d-flex align-items-center">
                    <span>${message}</span>
                    <button type="button" class="btn-close btn-close-white ms-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', toastHtml);
        const toastEl = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
        toast.show();
        
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }
}
