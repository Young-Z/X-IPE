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
        
        // Track expanded/pinned state to preserve across re-renders
        this.pinnedSections = new Set();  // Set of section IDs
        this.pinnedFolders = new Set();   // Set of folder paths
        this.expandedSections = new Set(); // Set of section IDs
        this.expandedFolders = new Set();  // Set of folder paths
        
        this._startPolling();
        
        // FEATURE-049-B: Listen for KB changes to auto-refresh sidebar tree
        document.addEventListener('kb:changed', () => {
            this.load();
        });
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
        
        // Save current expanded/pinned state before re-rendering
        this._saveExpandedState();
        
        let html = '';
        
        for (const section of this.sections) {
            html += this.renderSection(section);
        }
        
        this.container.innerHTML = html;
        this.bindEvents();
        
        // Restore expanded/pinned state after re-rendering
        this._restoreExpandedState();
    }
    
    /**
     * Save current expanded and pinned state from DOM
     */
    _saveExpandedState() {
        // Save expanded sections
        this.container.querySelectorAll('.nav-section-content.show').forEach(content => {
            const sectionId = content.id.replace('section-', '');
            this.expandedSections.add(sectionId);
        });
        
        // Save pinned sections
        this.container.querySelectorAll('.nav-section-header.pinned').forEach(header => {
            const target = header.dataset.bsTarget;
            if (target) {
                const sectionId = target.replace('#section-', '');
                this.pinnedSections.add(sectionId);
            }
        });
        
        // Save expanded folders
        this.container.querySelectorAll('.nav-folder-content.show').forEach(content => {
            const folderHeader = this.container.querySelector(`[data-bs-target="#${content.id}"]`);
            if (folderHeader && folderHeader.dataset.path) {
                this.expandedFolders.add(folderHeader.dataset.path);
            }
        });
        
        // Save pinned folders
        this.container.querySelectorAll('.nav-folder.pinned').forEach(folder => {
            if (folder.dataset.path) {
                this.pinnedFolders.add(folder.dataset.path);
            }
        });
    }
    
    /**
     * Restore expanded and pinned state after render
     */
    _restoreExpandedState() {
        // Restore expanded sections
        this.expandedSections.forEach(sectionId => {
            const content = document.getElementById(`section-${sectionId}`);
            const header = this.container.querySelector(`[data-bs-target="#section-${sectionId}"]`);
            if (content && header) {
                content.classList.add('show');
                header.classList.remove('collapsed');
            }
        });
        
        // Restore pinned sections (also expand them)
        this.pinnedSections.forEach(sectionId => {
            const content = document.getElementById(`section-${sectionId}`);
            const header = this.container.querySelector(`[data-bs-target="#section-${sectionId}"]`);
            if (content && header) {
                content.classList.add('show');
                header.classList.remove('collapsed');
                header.classList.add('pinned');
            }
        });
        
        // Restore expanded folders
        this.expandedFolders.forEach(folderPath => {
            const folder = this.container.querySelector(`.nav-folder[data-path="${folderPath}"]`);
            if (folder) {
                const targetSelector = folder.dataset.bsTarget;
                const content = document.querySelector(targetSelector);
                if (content) {
                    content.classList.add('show');
                }
            }
        });
        
        // Restore pinned folders (also expand them)
        this.pinnedFolders.forEach(folderPath => {
            const folder = this.container.querySelector(`.nav-folder[data-path="${folderPath}"]`);
            if (folder) {
                folder.classList.add('pinned');
                const targetSelector = folder.dataset.bsTarget;
                const content = document.querySelector(targetSelector);
                if (content) {
                    content.classList.add('show');
                }
            }
        });
    }
    
    /**
     * Render a single section
     */
    renderSection(section) {
        const icon = section.icon || 'bi-folder';
        const hasChildren = section.children && section.children.length > 0;
        
        // CR-004: Special handling for Workplace section - show submenu with Ideation and UIUX Feedbacks
        // FEATURE-023-B: Added Tracing submenu item
        // FEATURE-024: Added Quality Evaluation submenu item
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
                        <div class="nav-section-header sidebar-child nav-tracing" data-section-id="tracing">
                            <i class="bi bi-graph-up"></i>
                            <span>Application Tracing</span>
                        </div>
                        <div class="nav-section-header sidebar-child nav-quality-evaluation" data-section-id="quality-evaluation">
                            <i class="bi bi-clipboard-check"></i>
                            <span>Quality Evaluation</span>
                        </div>
                        <div class="nav-section-header sidebar-child nav-learn-panel" data-section-id="learn">
                            <i class="bi bi-mortarboard"></i>
                            <span>Learn</span>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // FEATURE-057: Special handling for Project Plan section - show Task Board and Feature Board links
        if (section.id === 'planning') {
            return `
                <div class="nav-section" data-section-id="${section.id}">
                    <div class="nav-section-header sidebar-parent" data-section-id="${section.id}" data-no-action="true">
                        <i class="bi ${icon}"></i>
                        <span>${section.label}</span>
                        <i class="bi bi-chevron-down submenu-indicator"></i>
                    </div>
                    <div class="sidebar-submenu">
                        <div class="nav-section-header sidebar-child nav-task-board" data-section-id="task-board">
                            <i class="bi bi-kanban"></i>
                            <span>Task Board</span>
                        </div>
                        <div class="nav-section-header sidebar-child nav-feature-board" data-section-id="feature-board">
                            <i class="bi bi-list-check"></i>
                            <span>Feature Board</span>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // FEATURE-049-B: Knowledge Base section with folder tree, drag-drop, and Intake placeholder
        if (section.id === 'knowledge-base') {
            return this._renderKBSection(section, icon, hasChildren);
        }
        
        let html = `
            <div class="nav-section" data-section-id="${section.id}">
                <div class="nav-section-header collapsed" data-bs-target="#section-${section.id}">
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
    
    // FEATURE-049-B: Render Knowledge Base sidebar section
    _renderKBSection(section, icon, hasChildren) {
        let html = `
            <div class="nav-section" data-section-id="${section.id}">
                <div class="nav-section-header collapsed" data-bs-target="#section-${section.id}">
                    <i class="bi ${icon}"></i>
                    <span>${section.label}</span>
                    <i class="bi bi-chevron-down chevron"></i>
                </div>
                <div class="collapse nav-section-content" id="section-${section.id}">
        `;
        
        if (!section.exists || !hasChildren) {
            html += '<div class="nav-empty kb-empty-state">📖 No articles yet</div>';
        } else {
            html += this._renderKBChildren(section.children);
        }
        
        // Intake placeholder (FEATURE-049-F future)
        html += `
            <div class="nav-item kb-intake-placeholder" data-section-id="kb-intake" style="padding-left: 2rem; opacity: 0.6;">
                <i class="bi bi-inbox"></i>
                <span>📥 Intake</span>
            </div>
        `;
        
        html += '</div></div>';
        return html;
    }
    
    // FEATURE-049-B: Render KB children with drag-drop attributes on folders
    _renderKBChildren(children, depth = 0) {
        if (!children || children.length === 0) return '';
        
        let html = '';
        const files = children.filter(item => item.type !== 'folder');
        const folders = children.filter(item => item.type === 'folder');
        
        for (const item of files) {
            html += this.renderFile(item, depth);
        }
        for (const item of folders) {
            html += this._renderKBFolder(item, depth);
        }
        return html;
    }
    
    // FEATURE-049-B: Render KB folder with drag-drop support
    _renderKBFolder(folder, depth) {
        const folderId = folder.path.replace(/[\/\.]/g, '-');
        const hasChildren = folder.children && folder.children.length > 0;
        const paddingLeft = 2 + (depth * 0.75);
        const isChanged = this.changedPaths.has(folder.path);
        
        let html = `
            <div class="nav-item nav-folder kb-folder${isChanged ? ' has-changes' : ''}" 
                 style="padding-left: ${paddingLeft}rem"
                 data-bs-target="#folder-${folderId}"
                 data-path="${folder.path}"
                 data-kb-folder="true"
                 draggable="true">
                ${isChanged ? '<span class="change-indicator"></span>' : ''}
                <i class="bi bi-folder"></i>
                <span>${folder.name}</span>
                ${hasChildren ? '<i class="bi bi-chevron-down chevron ms-auto" style="font-size: 0.7rem;"></i>' : ''}
            </div>
        `;
        
        if (hasChildren) {
            html += `
                <div class="collapse nav-folder-content" id="folder-${folderId}">
                    ${this._renderKBChildren(folder.children, depth + 1)}
                </div>
            `;
        }
        
        return html;
    }
    
    // FEATURE-049-B: Bind KB drag-drop events on sidebar KB folders
    _bindKBDragDrop() {
        const kbFolders = this.container.querySelectorAll('[data-kb-folder="true"]');
        const kbFiles = this.container.querySelectorAll('.nav-section[data-section-id="knowledge-base"] .nav-file');
        
        this._bindKBDragSources(kbFiles, kbFolders, 'file');
        this._bindKBDragSources(kbFolders, kbFolders, 'folder');
        this._bindKBDropTargets(kbFolders);
    }
    
    // FEATURE-049-B: Make elements draggable with KB drag data
    _bindKBDragSources(elements, allFolders, itemType) {
        const isFolder = itemType === 'folder';
        elements.forEach(el => {
            if (!isFolder) el.setAttribute('draggable', 'true');
            el.addEventListener('dragstart', (e) => {
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', el.dataset.path);
                e.dataTransfer.setData('application/x-kb-type', itemType);
                el.classList.add('kb-dragging');
                if (isFolder) e.stopPropagation();
            });
            el.addEventListener('dragend', () => {
                el.classList.remove('kb-dragging');
                allFolders.forEach(f => f.classList.remove('kb-drag-over'));
            });
        });
    }
    
    // FEATURE-049-B: Set up KB folders as drop targets
    _bindKBDropTargets(kbFolders) {
        kbFolders.forEach(folder => {
            folder.addEventListener('dragover', (e) => {
                e.preventDefault();
                if (!e.dataTransfer.types.includes('text/plain')) return;
                e.dataTransfer.dropEffect = 'move';
                folder.classList.add('kb-drag-over');
            });
            
            folder.addEventListener('dragleave', (e) => {
                if (!folder.contains(e.relatedTarget)) {
                    folder.classList.remove('kb-drag-over');
                }
            });
            
            folder.addEventListener('drop', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                folder.classList.remove('kb-drag-over');
                
                const sourcePath = e.dataTransfer.getData('text/plain');
                const sourceType = e.dataTransfer.getData('application/x-kb-type');
                const targetPath = folder.dataset.path;
                
                if (!sourcePath || !targetPath || sourcePath === targetPath) return;
                if (sourceType === 'folder' && targetPath.startsWith(sourcePath + '/')) return;
                
                await this._kbMoveItem(sourcePath, targetPath, sourceType);
            });
        });
    }
    
    // FEATURE-049-B: Move KB item via API
    async _kbMoveItem(sourcePath, targetFolderPath, sourceType) {
        try {
            // Strip KB root prefix to get relative paths for the KB API
            const kbRoot = 'x-ipe-docs/knowledge-base/';
            const relSource = sourcePath.startsWith(kbRoot) ? sourcePath.slice(kbRoot.length) : sourcePath;
            const relTarget = targetFolderPath.startsWith(kbRoot) ? targetFolderPath.slice(kbRoot.length) : targetFolderPath;
            
            const endpoint = sourceType === 'folder' ? '/api/kb/folders/move' : '/api/kb/files/move';
            const body = sourceType === 'folder'
                ? { path: relSource, new_parent: relTarget }
                : { path: relSource, destination: relTarget };
            
            const response = await fetch(endpoint, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            
            if (response.ok) {
                document.dispatchEvent(new CustomEvent('kb:changed'));
            } else {
                let message = 'Unknown error';
                try { message = (await response.json()).error || message; } catch { /* non-JSON body */ }
                console.error('KB move failed:', message);
            }
        } catch (error) {
            console.error('KB move failed:', error);
        }
    }
    
    // FEATURE-049-C: KB folder/section clicks open browse view in content area
    _bindKBFolderClicks() {
        // KB section header click → show browse view for root
        const kbSection = this.container.querySelector('[data-section-id="knowledge-base"]');
        if (kbSection) {
            const header = kbSection.querySelector('.nav-section-header');
            if (header) {
                header.addEventListener('dblclick', () => {
                    this._openKBBrowse('');
                });
            }
        }
        
        // KB folder clicks → show browse view for that folder
        this.container.querySelectorAll('.kb-folder .nav-folder-header').forEach(fh => {
            fh.addEventListener('dblclick', (e) => {
                e.stopPropagation();
                const folderPath = fh.closest('.kb-folder')?.dataset?.kbPath || '';
                this._openKBBrowse(folderPath);
            });
        });
    }
    
    _openKBBrowse(folder) {
        if (typeof KBBrowseView === 'undefined') return;
        const contentArea = document.getElementById('content-area') || document.querySelector('.content-area');
        if (!contentArea) return;
        
        if (!this._kbBrowseView) {
            this._kbBrowseView = new KBBrowseView(contentArea);
        }
        this._kbBrowseView.render(folder);
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
        
        // FEATURE-023-B: Tracing click handler - render Tracing Dashboard in content area
        const tracingHeader = this.container.querySelector('.nav-tracing');
        if (tracingHeader) {
            tracingHeader.addEventListener('click', () => {
                // Clear file selection
                fileItems.forEach(f => f.classList.remove('active'));
                this.selectedFile = null;
                
                // Update sidebar-child active state
                const sidebarChildren = this.container.querySelectorAll('.sidebar-child');
                sidebarChildren.forEach(child => child.classList.remove('active'));
                tracingHeader.classList.add('active');
                
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
                breadcrumb.innerHTML = '<li class="breadcrumb-item active">Application Tracing</li>';
                
                // Render Tracing Dashboard in content area
                const container = document.getElementById('content-body');
                if (window.TracingDashboard) {
                    // Clean up any existing dashboard
                    if (window._tracingDashboardInstance) {
                        window._tracingDashboardInstance.destroy();
                    }
                    window._tracingDashboardInstance = new window.TracingDashboard(container);
                    window._tracingDashboardInstance.init();
                }
            });
        }
        
        // FEATURE-024: Quality Evaluation submenu click handler
        const qualityEvalHeader = this.container.querySelector('.nav-quality-evaluation');
        if (qualityEvalHeader) {
            qualityEvalHeader.addEventListener('click', () => {
                // Clear file selection
                fileItems.forEach(f => f.classList.remove('active'));
                this.selectedFile = null;
                
                // Update sidebar-child active state
                const sidebarChildren = this.container.querySelectorAll('.sidebar-child');
                sidebarChildren.forEach(child => child.classList.remove('active'));
                qualityEvalHeader.classList.add('active');
                
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
                breadcrumb.innerHTML = '<li class="breadcrumb-item active">Quality Evaluation</li>';
                
                // Render Quality Evaluation view in content area
                const container = document.getElementById('content-body');
                if (window.QualityEvaluationView) {
                    // Clean up any existing view
                    if (window._qualityEvaluationInstance) {
                        window._qualityEvaluationInstance.destroy();
                    }
                    window._qualityEvaluationInstance = new window.QualityEvaluationView(container);
                    window._qualityEvaluationInstance.init();
                }
            });
        }
        
        // CR-004: Prevent parent item click action
        // FEATURE-054-A: Learn Panel click handler
        const learnHeader = this.container.querySelector('.nav-learn-panel');
        if (learnHeader) {
            learnHeader.addEventListener('click', () => {
                fileItems.forEach(f => f.classList.remove('active'));
                this.selectedFile = null;
                const sidebarChildren = this.container.querySelectorAll('.sidebar-child');
                sidebarChildren.forEach(child => child.classList.remove('active'));
                learnHeader.classList.add('active');
                if (window.contentRenderer) {
                    window.contentRenderer.currentPath = null;
                }
                const createIdeaBtn = document.getElementById('btn-create-idea');
                if (createIdeaBtn) {
                    createIdeaBtn.classList.add('d-none');
                }
                const breadcrumb = document.getElementById('breadcrumb');
                breadcrumb.innerHTML = '<li class="breadcrumb-item active">Learn</li>';
                const container = document.getElementById('content-body');
                if (window.learnPanelManager) {
                    window.learnPanelManager.render(container);
                }
            });
        }

        // FEATURE-057: Task Board sidebar link → renders inline SPA panel
        const taskBoardHeader = this.container.querySelector('.nav-task-board');
        if (taskBoardHeader) {
            taskBoardHeader.addEventListener('click', () => {
                fileItems.forEach(f => f.classList.remove('active'));
                this.selectedFile = null;
                const sidebarChildren = this.container.querySelectorAll('.sidebar-child');
                sidebarChildren.forEach(child => child.classList.remove('active'));
                taskBoardHeader.classList.add('active');
                if (window.contentRenderer) {
                    window.contentRenderer.currentPath = null;
                }
                const createIdeaBtn = document.getElementById('btn-create-idea');
                if (createIdeaBtn) {
                    createIdeaBtn.classList.add('d-none');
                }
                const breadcrumb = document.getElementById('breadcrumb');
                breadcrumb.innerHTML = '<li class="breadcrumb-item active">Task Board</li>';
                const container = document.getElementById('content-body');
                if (window.TaskBoardPanel) {
                    window.TaskBoardPanel.render(container);
                }
            });
        }

        // FEATURE-057: Feature Board sidebar link → renders inline SPA panel
        const featureBoardHeader = this.container.querySelector('.nav-feature-board');
        if (featureBoardHeader) {
            featureBoardHeader.addEventListener('click', () => {
                fileItems.forEach(f => f.classList.remove('active'));
                this.selectedFile = null;
                const sidebarChildren = this.container.querySelectorAll('.sidebar-child');
                sidebarChildren.forEach(child => child.classList.remove('active'));
                featureBoardHeader.classList.add('active');
                if (window.contentRenderer) {
                    window.contentRenderer.currentPath = null;
                }
                const createIdeaBtn = document.getElementById('btn-create-idea');
                if (createIdeaBtn) {
                    createIdeaBtn.classList.add('d-none');
                }
                const breadcrumb = document.getElementById('breadcrumb');
                breadcrumb.innerHTML = '<li class="breadcrumb-item active">Feature Board</li>';
                const container = document.getElementById('content-body');
                if (window.FeatureBoardPanel) {
                    window.FeatureBoardPanel.render(container);
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
        
        // FEATURE-049-B: KB sidebar drag-drop
        this._bindKBDragDrop();
        
        // FEATURE-049-C: KB folder click opens browse view
        this._bindKBFolderClicks();
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
            // Initialize isPinned from persisted state
            const sectionId = targetSelector.replace('#section-', '');
            let isPinned = this.pinnedSections.has(sectionId);
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
                    this.pinnedSections.delete(sectionId);
                    this.expandedSections.delete(sectionId);
                    header.classList.remove('pinned');
                    bootstrap.Collapse.getOrCreateInstance(target).hide();
                } else {
                    // Pin and expand - always show to ensure it stays open
                    isPinned = true;
                    this.pinnedSections.add(sectionId);
                    this.expandedSections.add(sectionId);
                    header.classList.add('pinned');
                    bootstrap.Collapse.getOrCreateInstance(target).show();
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
            // Initialize isPinned from persisted state
            const folderPath = folder.dataset.path;
            let isPinned = this.pinnedFolders.has(folderPath);
            
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
                    this.pinnedFolders.delete(folderPath);
                    this.expandedFolders.delete(folderPath);
                    folder.classList.remove('pinned');
                    bootstrap.Collapse.getOrCreateInstance(target).hide();
                } else {
                    // Pin and expand - always show to ensure it stays open
                    isPinned = true;
                    this.pinnedFolders.add(folderPath);
                    this.expandedFolders.add(folderPath);
                    folder.classList.add('pinned');
                    bootstrap.Collapse.getOrCreateInstance(target).show();
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
     * FEATURE-026: Expand a sidebar section by ID
     * @param {string} sectionId - Section ID to expand
     */
    expandSection(sectionId) {
        const sectionHeader = document.querySelector(`[data-section="${sectionId}"] .section-header`);
        if (sectionHeader) {
            const section = sectionHeader.closest('.sidebar-section');
            if (section && !section.classList.contains('expanded')) {
                sectionHeader.click();
            }
        }
    }
    
    /**
     * FEATURE-026: Highlight a sidebar item
     * @param {string} selector - CSS selector for target item
     * @param {Object} options - Highlight options
     * @param {number} options.duration - Highlight duration in ms (default 3000)
     */
    highlightItem(selector, options = {}) {
        const duration = options.duration || 3000;
        const item = document.querySelector(selector);
        
        if (!item) {
            console.warn(`Sidebar item not found: ${selector}`);
            return;
        }
        
        // Remove any existing highlights
        document.querySelectorAll('.homepage-highlight').forEach(el => {
            el.classList.remove('homepage-highlight');
        });
        
        // Add highlight class
        item.classList.add('homepage-highlight');
        
        // Scroll into view
        item.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Remove highlight after delay
        setTimeout(() => {
            item.classList.remove('homepage-highlight');
        }, duration);
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
