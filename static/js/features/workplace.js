/**
 * Workplace Manager
 * FEATURE-008: Workplace (Idea Management)
 * 
 * Two-column view for managing ideas with upload, tree navigation,
 * inline editing with auto-save, and folder rename.
 */
class WorkplaceManager {
    constructor() {
        this.currentView = 'tree'; // tree | upload | editor
        this.currentPath = null;
        this.saveTimer = null;
        this.saveDelay = 5000; // 5 seconds auto-save delay
        this.hasUnsavedChanges = false;
        this.originalContent = '';
        this.renamingFolder = null;
        this.pollInterval = 5000; // 5 seconds tree refresh
        this.pollTimer = null;
        this.lastTreeHash = null;
        this.isActive = false; // Track if workplace view is active
        this.isEditing = false; // Track view/edit mode
        this.fileType = null; // markdown | code | text
        this.fileExtension = null;
        this.easyMDE = null; // EasyMDE editor instance for compose view
        this.copilotPrompts = []; // Loaded from config/copilot-prompt.json
        this._loadCopilotPrompts();
    }
    
    /**
     * Load Copilot prompts from config file
     */
    async _loadCopilotPrompts() {
        try {
            const response = await fetch('/api/config/copilot-prompt');
            if (response.ok) {
                const data = await response.json();
                this.copilotPrompts = data.prompts || [];
            }
        } catch (error) {
            console.warn('Failed to load copilot prompts:', error);
            this.copilotPrompts = [];
        }
    }
    
    /**
     * Render the workplace view in the content area
     */
    async render(container) {
        this.isActive = true;
        container.innerHTML = `
            <div class="workplace-container">
                <div class="workplace-sidebar pinned" id="workplace-sidebar">
                    <div class="workplace-sidebar-icons">
                        <button class="workplace-sidebar-icon" title="Browse Ideas" id="workplace-icon-browse">
                            <i class="bi bi-folder2"></i>
                        </button>
                    </div>
                    <div class="workplace-sidebar-content">
                        <div class="workplace-sidebar-header">
                            <span class="workplace-sidebar-title">Ideas</span>
                            <button class="workplace-pin-btn" title="Unpin sidebar" id="workplace-pin-btn">
                                <i class="bi bi-pin-angle-fill"></i>
                            </button>
                        </div>
                        <div class="workplace-tree" id="workplace-tree">
                            <div class="loading-spinner">
                                <div class="spinner-border spinner-border-sm" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="workplace-content" id="workplace-content">
                    <div class="workplace-placeholder">
                        <i class="bi bi-lightbulb"></i>
                        <h5>Welcome to Workplace</h5>
                        <p class="text-muted">Hover sidebar to browse ideas, or click pin to keep it open</p>
                    </div>
                </div>
            </div>
        `;
        
        // Bind sidebar icon events
        document.getElementById('workplace-icon-browse').addEventListener('click', () => {
            // Toggle expanded state on mobile/touch
            const sidebar = document.getElementById('workplace-sidebar');
            sidebar.classList.toggle('expanded');
        });
        
        // Bind pin button
        document.getElementById('workplace-pin-btn').addEventListener('click', () => {
            const sidebar = document.getElementById('workplace-sidebar');
            const pinBtn = document.getElementById('workplace-pin-btn');
            const isPinned = sidebar.classList.toggle('pinned');
            
            // Update icon and title
            const icon = pinBtn.querySelector('i');
            if (isPinned) {
                icon.classList.remove('bi-pin-angle');
                icon.classList.add('bi-pin-angle-fill');
                pinBtn.title = 'Unpin sidebar';
            } else {
                icon.classList.remove('bi-pin-angle-fill');
                icon.classList.add('bi-pin-angle');
                pinBtn.title = 'Pin sidebar';
            }
        });
        
        // Load tree and start polling
        await this.loadTree();
        this._startPolling();
    }
    
    /**
     * Stop workplace (called when navigating away)
     */
    stop() {
        this.isActive = false;
        this._stopPolling();
    }
    
    /**
     * Start polling for tree changes
     */
    _startPolling() {
        this._stopPolling(); // Clear any existing timer
        this.pollTimer = setInterval(() => {
            if (this.isActive) {
                this._checkForTreeChanges();
            }
        }, this.pollInterval);
    }
    
    /**
     * Stop polling
     */
    _stopPolling() {
        if (this.pollTimer) {
            clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    }
    
    /**
     * Check for tree changes and refresh if needed
     */
    async _checkForTreeChanges() {
        try {
            const response = await fetch('/api/ideas/tree');
            const data = await response.json();
            
            if (data.success && data.tree) {
                const newHash = JSON.stringify(data.tree);
                if (this.lastTreeHash && this.lastTreeHash !== newHash) {
                    // Tree changed, refresh it
                    const treeContainer = document.getElementById('workplace-tree');
                    if (treeContainer) {
                        this.renderTree(treeContainer, data.tree);
                        this._showToast('Ideas updated', 'info');
                    }
                }
                this.lastTreeHash = newHash;
            }
        } catch (error) {
            console.error('Failed to check for tree changes:', error);
        }
    }
    
    /**
     * Load and render the idea tree
     */
    async loadTree() {
        const treeContainer = document.getElementById('workplace-tree');
        if (!treeContainer) return;
        
        try {
            const response = await fetch('/api/ideas/tree');
            const data = await response.json();
            
            if (data.success && data.tree) {
                this.lastTreeHash = JSON.stringify(data.tree);
                this.renderTree(treeContainer, data.tree);
            } else {
                this.lastTreeHash = null;
                treeContainer.innerHTML = `
                    <div class="workplace-empty">
                        <i class="bi bi-folder-x"></i>
                        <p>No ideas yet</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Failed to load idea tree:', error);
            treeContainer.innerHTML = `
                <div class="workplace-error">
                    <i class="bi bi-exclamation-triangle"></i>
                    <p>Failed to load ideas</p>
                </div>
            `;
        }
    }
    
    /**
     * Collect expanded folder paths before re-rendering
     */
    _getExpandedPaths(container) {
        const expanded = new Set();
        const expandedItems = container.querySelectorAll('.workplace-tree-item.expanded');
        expandedItems.forEach(item => {
            if (item.dataset.path) {
                expanded.add(item.dataset.path);
            }
        });
        return expanded;
    }
    
    /**
     * Restore expanded state to folders after re-rendering
     */
    _restoreExpandedPaths(container, expandedPaths) {
        if (!expandedPaths || expandedPaths.size === 0) return;
        const items = container.querySelectorAll('.workplace-tree-item[data-type="folder"]');
        items.forEach(item => {
            if (expandedPaths.has(item.dataset.path)) {
                item.classList.add('expanded');
            }
        });
    }
    
    /**
     * Render tree nodes recursively
     */
    renderTree(container, nodes, level = 0) {
        // Preserve expanded state before re-rendering
        let expandedPaths = null;
        if (level === 0) {
            expandedPaths = this._getExpandedPaths(container);
        }
        
        if (!nodes || nodes.length === 0) {
            if (level === 0) {
                container.innerHTML = `
                    <div class="workplace-empty">
                        <i class="bi bi-folder-x"></i>
                        <p>No ideas yet</p>
                    </div>
                `;
            }
            return;
        }
        
        const ul = document.createElement('ul');
        ul.className = 'workplace-tree-list';
        if (level === 0) ul.classList.add('workplace-tree-root');
        
        for (const node of nodes) {
            const li = document.createElement('li');
            li.className = 'workplace-tree-item';
            li.dataset.path = node.path;
            li.dataset.type = node.type;
            li.dataset.name = node.name;
            
            const itemContent = document.createElement('div');
            itemContent.className = 'workplace-tree-item-content';
            // CR-002: Add idea-folder-node class and data for drag-drop targets
            if (node.type === 'folder') {
                itemContent.classList.add('idea-folder-node');
                // Use full path (relative to docs/ideas/) for nested folder support
                itemContent.dataset.folderPath = node.path;
            }
            itemContent.style.paddingLeft = `${level * 16 + 8}px`;
            
            const icon = document.createElement('i');
            icon.className = node.type === 'folder' ? 'bi bi-folder' : 'bi bi-file-earmark';
            
            const nameSpan = document.createElement('span');
            nameSpan.className = 'workplace-tree-name';
            nameSpan.textContent = node.name;
            
            // Action buttons container
            const actionBtns = document.createElement('div');
            actionBtns.className = 'workplace-tree-actions';
            
            // Rename button (only for top-level folders)
            if (node.type === 'folder' && level === 0) {
                const renameBtn = document.createElement('button');
                renameBtn.className = 'workplace-tree-action-btn workplace-tree-rename-btn';
                renameBtn.innerHTML = '<i class="bi bi-pencil"></i>';
                renameBtn.title = 'Rename folder';
                renameBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.startFolderRename(li, node.name);
                });
                actionBtns.appendChild(renameBtn);
            }
            
            // Download button (only for files)
            if (node.type === 'file') {
                const downloadBtn = document.createElement('button');
                downloadBtn.className = 'workplace-tree-action-btn workplace-tree-download-btn';
                downloadBtn.innerHTML = '<i class="bi bi-download"></i>';
                downloadBtn.title = 'Download file';
                downloadBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.downloadFile(node.path, node.name);
                });
                actionBtns.appendChild(downloadBtn);
            }
            
            // Delete button
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'workplace-tree-action-btn workplace-tree-delete-btn';
            deleteBtn.innerHTML = '<i class="bi bi-trash"></i>';
            deleteBtn.title = `Delete ${node.type}`;
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.confirmDelete(node.path, node.name, node.type);
            });
            actionBtns.appendChild(deleteBtn);
            
            itemContent.appendChild(icon);
            itemContent.appendChild(nameSpan);
            itemContent.appendChild(actionBtns);
            li.appendChild(itemContent);
            
            // Event handlers
            if (node.type === 'file') {
                itemContent.addEventListener('click', () => this.openFile(node.path));
            } else {
                // Folder: click to toggle
                itemContent.addEventListener('click', (e) => {
                    e.stopPropagation();
                    li.classList.toggle('expanded');
                });
            }
            
            // Render children (append to li, don't clear it)
            if (node.children && node.children.length > 0) {
                const childUl = this._buildTreeList(node.children, level + 1);
                li.appendChild(childUl);
                li.classList.add('has-children');
            }
            
            ul.appendChild(li);
        }
        
        // Only clear container at root level
        if (level === 0) {
            container.innerHTML = '';
        }
        container.appendChild(ul);
        
        // CR-002: Setup drag-drop on folder nodes after tree is rendered
        if (level === 0) {
            this._setupFolderDragDrop();
            // Restore expanded state after rendering
            this._restoreExpandedPaths(container, expandedPaths);
        }
    }
    
    /**
     * Build tree list recursively (returns ul element)
     */
    _buildTreeList(nodes, level) {
        const ul = document.createElement('ul');
        ul.className = 'workplace-tree-list';
        
        for (const node of nodes) {
            const li = document.createElement('li');
            li.className = 'workplace-tree-item';
            li.dataset.path = node.path;
            li.dataset.type = node.type;
            li.dataset.name = node.name;
            
            const itemContent = document.createElement('div');
            itemContent.className = 'workplace-tree-item-content';
            // CR-002: Add idea-folder-node class and data for drag-drop targets
            if (node.type === 'folder') {
                itemContent.classList.add('idea-folder-node');
                // Use full path (relative to docs/ideas/) for nested folder support
                itemContent.dataset.folderPath = node.path;
            }
            itemContent.style.paddingLeft = `${level * 16 + 8}px`;
            
            const icon = document.createElement('i');
            icon.className = node.type === 'folder' ? 'bi bi-folder' : 'bi bi-file-earmark';
            
            const nameSpan = document.createElement('span');
            nameSpan.className = 'workplace-tree-name';
            nameSpan.textContent = node.name;
            
            // Action buttons container
            const actionBtns = document.createElement('div');
            actionBtns.className = 'workplace-tree-actions';
            
            // Download button (only for files)
            if (node.type === 'file') {
                const downloadBtn = document.createElement('button');
                downloadBtn.className = 'workplace-tree-action-btn workplace-tree-download-btn';
                downloadBtn.innerHTML = '<i class="bi bi-download"></i>';
                downloadBtn.title = 'Download file';
                downloadBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.downloadFile(node.path, node.name);
                });
                actionBtns.appendChild(downloadBtn);
            }
            
            // Delete button
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'workplace-tree-action-btn workplace-tree-delete-btn';
            deleteBtn.innerHTML = '<i class="bi bi-trash"></i>';
            deleteBtn.title = `Delete ${node.type}`;
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.confirmDelete(node.path, node.name, node.type);
            });
            actionBtns.appendChild(deleteBtn);
            
            itemContent.appendChild(icon);
            itemContent.appendChild(nameSpan);
            itemContent.appendChild(actionBtns);
            li.appendChild(itemContent);
            
            // Event handlers
            if (node.type === 'file') {
                itemContent.addEventListener('click', () => this.openFile(node.path));
            } else {
                // Folder: click to toggle
                itemContent.addEventListener('click', (e) => {
                    e.stopPropagation();
                    li.classList.toggle('expanded');
                });
            }
            
            // Render children
            if (node.children && node.children.length > 0) {
                const childUl = this._buildTreeList(node.children, level + 1);
                li.appendChild(childUl);
                li.classList.add('has-children');
            }
            
            ul.appendChild(li);
        }
        
        return ul;
    }
    
    /**
     * Start inline folder rename
     */
    startFolderRename(li, currentName) {
        if (this.renamingFolder) return;
        
        this.renamingFolder = li;
        const nameSpan = li.querySelector('.workplace-tree-name');
        const originalName = currentName;
        
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'workplace-rename-input';
        input.value = currentName;
        
        nameSpan.replaceWith(input);
        input.focus();
        input.select();
        
        const finishRename = async (save) => {
            if (!this.renamingFolder) return;
            
            const newName = input.value.trim();
            this.renamingFolder = null;
            
            if (save && newName && newName !== originalName) {
                try {
                    const response = await fetch('/api/ideas/rename', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            old_name: originalName,
                            new_name: newName
                        })
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        this._showToast('Folder renamed successfully', 'success');
                        await this.loadTree();
                    } else {
                        this._showToast(result.error || 'Failed to rename folder', 'error');
                        // Restore original name
                        const newSpan = document.createElement('span');
                        newSpan.className = 'workplace-tree-name';
                        newSpan.textContent = originalName;
                        input.replaceWith(newSpan);
                    }
                } catch (error) {
                    console.error('Failed to rename folder:', error);
                    this._showToast('Failed to rename folder', 'error');
                    const newSpan = document.createElement('span');
                    newSpan.className = 'workplace-tree-name';
                    newSpan.textContent = originalName;
                    input.replaceWith(newSpan);
                }
            } else {
                const newSpan = document.createElement('span');
                newSpan.className = 'workplace-tree-name';
                newSpan.textContent = originalName;
                input.replaceWith(newSpan);
            }
        };
        
        input.addEventListener('blur', () => finishRename(true));
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                finishRename(true);
            } else if (e.key === 'Escape') {
                e.preventDefault();
                finishRename(false);
            }
        });
    }
    
    /**
     * Open a file - show rendered content by default
     */
    async openFile(path) {
        // Check for unsaved changes
        if (this.hasUnsavedChanges) {
            if (!window.confirm('You have unsaved changes. Do you want to discard them?')) {
                return;
            }
        }
        
        // Clean up previous EasyMDE instance
        if (this.easyMDE) {
            this.easyMDE.toTextArea();
            this.easyMDE = null;
        }
        
        this.currentView = 'editor';
        this.currentPath = path;
        this.hasUnsavedChanges = false;
        this.isEditing = false;
        
        // Detect file type
        const ext = path.split('.').pop().toLowerCase();
        this.fileExtension = ext;
        this.fileType = this._getFileType(ext);
        
        const contentArea = document.getElementById('workplace-content');
        contentArea.innerHTML = `
            <div class="workplace-editor">
                <div class="workplace-editor-header">
                    <span class="workplace-editor-path">${this._escapeHtml(path)}</span>
                    <div class="workplace-editor-actions">
                        <span class="workplace-editor-status" id="workplace-editor-status"></span>
                        ${this._renderCopilotButton()}
                    </div>
                </div>
                <div class="workplace-editor-loading">
                    <div class="spinner-border spinner-border-sm" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            </div>
        `;
        
        try {
            const response = await fetch(`/api/file/content?path=${encodeURIComponent(path)}`);
            const data = await response.json();
            
            this.originalContent = data.content || '';
            this.renderContent(contentArea, data.content || '');
        } catch (error) {
            console.error('Failed to load file:', error);
            contentArea.innerHTML = `
                <div class="workplace-error">
                    <i class="bi bi-exclamation-triangle"></i>
                    <p>Failed to load file</p>
                </div>
            `;
        }
    }
    
    /**
     * Determine file type from extension
     */
    _getFileType(ext) {
        const markdownExts = ['md', 'markdown', 'mdown', 'mkd'];
        const codeExts = ['js', 'ts', 'jsx', 'tsx', 'py', 'java', 'c', 'cpp', 'h', 'hpp', 
                         'cs', 'go', 'rs', 'rb', 'php', 'swift', 'kt', 'scala', 'sh', 'bash',
                         'html', 'css', 'scss', 'less', 'json', 'xml', 'yaml', 'yml', 'toml',
                         'sql', 'r', 'lua', 'pl', 'pm'];
        const imageExts = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'ico', 'svg', 'webp'];
        const binaryExts = ['docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 'pdf', 'zip', 'rar',
                           'mp3', 'mp4', 'wav', 'avi', 'mov', 'exe', 'dll', 'bin'];
        
        if (markdownExts.includes(ext)) return 'markdown';
        if (codeExts.includes(ext)) return 'code';
        if (imageExts.includes(ext)) return 'image';
        if (binaryExts.includes(ext)) return 'binary';
        return 'text';
    }
    
    /**
     * Render content based on file type (view mode)
     */
    renderContent(container, content) {
        const isEditable = this.fileType !== 'binary' && this.fileType !== 'image';
        const isHtmlFile = this.fileExtension === 'html' || this.fileExtension === 'htm';
        const isPreviewable = isHtmlFile || this.fileType === 'markdown';
        
        const header = `
            <div class="workplace-editor-header">
                <span class="workplace-editor-path">${this._escapeHtml(this.currentPath)}</span>
                <div class="workplace-editor-actions">
                    <span class="workplace-editor-status" id="workplace-editor-status"></span>
                    ${isEditable ? `
                    <button class="btn btn-sm btn-outline-secondary workplace-edit-btn" id="workplace-edit-btn" title="Edit file">
                        <i class="bi bi-pencil"></i> Edit
                    </button>
                    ` : ''}
                    ${this._renderCopilotButton()}
                </div>
            </div>
        `;
        
        let bodyContent;
        if (this.fileType === 'image') {
            bodyContent = this._renderImage();
        } else if (this.fileType === 'binary') {
            bodyContent = this._renderBinaryPlaceholder();
        } else if (isHtmlFile) {
            // HTML file: show rendered preview
            bodyContent = this._renderHtmlPreview(content);
        } else if (this.fileType === 'markdown') {
            // Markdown: show rendered preview with same design
            bodyContent = this._renderMarkdownPreview(content);
        } else if (this.fileType === 'code') {
            bodyContent = this._renderCode(content, this.fileExtension);
        } else {
            bodyContent = `<pre class="workplace-text-content">${this._escapeHtml(content)}</pre>`;
        }
        
        container.innerHTML = `
            <div class="workplace-editor">
                ${header}
                <div class="workplace-content-body" id="workplace-content-body">
                    ${bodyContent}
                </div>
            </div>
        `;
        
        // Bind edit button
        const editBtn = document.getElementById('workplace-edit-btn');
        if (editBtn) {
            editBtn.addEventListener('click', () => this.enterEditMode());
        }
        
        // Bind copilot button with hover dropdown
        this._bindCopilotButton();
        
        // Render Mermaid diagrams if any
        if (this.fileType === 'markdown' && typeof mermaid !== 'undefined') {
            this._renderMermaidDiagrams();
        }
        
        // Render Infographic diagrams if any
        if (this.fileType === 'markdown' && typeof AntVInfographic !== 'undefined') {
            this._renderInfographicDiagrams();
        }
        
        // Render Architecture DSL diagrams if any
        if (this.fileType === 'markdown') {
            this._renderArchitectureDiagrams();
        }
    }
    
    /**
     * Handle Copilot button click - open terminal and send refine command
     */
    _handleCopilotClick() {
        if (!this.currentPath) return;
        
        // Expand terminal panel
        if (window.terminalPanel) {
            window.terminalPanel.expand();
        }
        
        // Send copilot command to terminal with typing simulation
        if (window.terminalManager) {
            window.terminalManager.sendCopilotRefineCommand(this.currentPath);
        }
    }
    
    /**
     * Render Copilot button with dropdown container
     */
    _renderCopilotButton() {
        const dropdownItems = this.copilotPrompts.map(prompt => `
            <div class="copilot-dropdown-item" data-prompt-id="${prompt.id}">
                <i class="${prompt.icon || 'bi bi-arrow-right'}"></i>
                <span>${this._escapeHtml(prompt.label)}</span>
            </div>
        `).join('');
        
        return `
            <div class="copilot-btn-container" id="copilot-btn-container">
                <button class="btn btn-sm btn-outline-info workplace-copilot-btn" id="workplace-copilot-btn" title="Refine with Copilot">
                    <i class="bi bi-robot"></i> Copilot
                </button>
                ${this.copilotPrompts.length > 0 ? `
                <div class="copilot-dropdown" id="copilot-dropdown">
                    ${dropdownItems}
                </div>
                ` : ''}
            </div>
        `;
    }
    
    /**
     * Bind Copilot button click and hover events
     */
    _bindCopilotButton() {
        const container = document.getElementById('copilot-btn-container');
        const copilotBtn = document.getElementById('workplace-copilot-btn');
        const dropdown = document.getElementById('copilot-dropdown');
        
        if (!copilotBtn) return;
        
        // Click handler - same as before
        copilotBtn.addEventListener('click', () => this._handleCopilotClick());
        
        if (!dropdown || !container) return;
        
        // Show dropdown on hover
        container.addEventListener('mouseenter', () => {
            dropdown.classList.add('show');
        });
        
        container.addEventListener('mouseleave', () => {
            dropdown.classList.remove('show');
        });
        
        // Handle dropdown item clicks
        dropdown.querySelectorAll('.copilot-dropdown-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const promptId = item.getAttribute('data-prompt-id');
                this._handleCopilotPromptClick(promptId);
                dropdown.classList.remove('show');
            });
        });
    }
    
    /**
     * Handle click on a specific Copilot prompt from dropdown
     */
    _handleCopilotPromptClick(promptId) {
        if (!this.currentPath) return;
        
        const prompt = this.copilotPrompts.find(p => p.id === promptId);
        if (!prompt) return;
        
        // Replace <current-idea-file> placeholder with actual file path
        const command = prompt.command.replace(/<current-idea-file>/g, this.currentPath);
        
        // Expand terminal panel
        if (window.terminalPanel) {
            window.terminalPanel.expand();
        }
        
        // Send the prompt command to terminal
        if (window.terminalManager) {
            window.terminalManager.sendCopilotPromptCommand(command);
        }
    }
    
    /**
     * Render HTML file as iframe preview
     */
    _renderHtmlPreview(content) {
        // Create a blob URL for the HTML content
        const blob = new Blob([content], { type: 'text/html' });
        const blobUrl = URL.createObjectURL(blob);
        
        // Store for cleanup
        if (this._htmlBlobUrl) {
            URL.revokeObjectURL(this._htmlBlobUrl);
        }
        this._htmlBlobUrl = blobUrl;
        
        return `
            <div class="workplace-preview">
                <div class="workplace-preview-toolbar">
                    <span class="badge bg-success"><i class="bi bi-eye"></i> Preview</span>
                </div>
                <iframe class="workplace-preview-iframe" src="${blobUrl}" sandbox="allow-scripts allow-same-origin"></iframe>
            </div>
        `;
    }
    
    /**
     * Render Markdown file as preview with same design as HTML
     */
    _renderMarkdownPreview(content) {
        const renderedHtml = this._renderMarkdown(content);
        
        return `
            <div class="workplace-preview">
                <div class="workplace-preview-toolbar">
                    <span class="badge bg-success"><i class="bi bi-eye"></i> Preview</span>
                </div>
                <div class="workplace-preview-content">
                    ${renderedHtml}
                </div>
            </div>
        `;
    }
    
    /**
     * Render image preview
     */
    _renderImage() {
        const fileName = this.currentPath.split('/').pop();
        // Use the file API to serve the image
        const imageSrc = `/api/file/content?path=${encodeURIComponent(this.currentPath)}&raw=true`;
        return `
            <div class="workplace-image-preview">
                <img src="${imageSrc}" alt="${this._escapeHtml(fileName)}" class="workplace-preview-img" />
                <p class="text-muted small mt-2 text-center">${this._escapeHtml(fileName)}</p>
            </div>
        `;
    }
    
    /**
     * Render placeholder for binary files
     */
    _renderBinaryPlaceholder() {
        const ext = this.fileExtension.toUpperCase();
        const fileName = this.currentPath.split('/').pop();
        return `
            <div class="workplace-binary-placeholder">
                <i class="bi bi-file-earmark-binary"></i>
                <h5>${ext} File</h5>
                <p class="text-muted">"${this._escapeHtml(fileName)}" cannot be previewed in the browser.</p>
                <p class="text-muted small">Binary files like .docx, .xlsx, .pdf require external applications to view.</p>
            </div>
        `;
    }
    
    /**
     * Render markdown content
     */
    _renderMarkdown(content) {
        // Pre-process Mermaid blocks
        const mermaidBlocks = [];
        let processedContent = content.replace(
            /```mermaid\n([\s\S]*?)```/g,
            (match, diagram) => {
                const id = `workplace-mermaid-${mermaidBlocks.length}`;
                mermaidBlocks.push({ id, diagram: diagram.trim() });
                return `<div class="mermaid" id="${id}"></div>`;
            }
        );
        this._mermaidBlocks = mermaidBlocks;
        
        // Pre-process Infographic blocks
        const infographicBlocks = [];
        processedContent = processedContent.replace(
            /```infographic\n([\s\S]*?)```/g,
            (match, syntax) => {
                const id = `workplace-infographic-${infographicBlocks.length}`;
                infographicBlocks.push({ id, syntax: syntax.trim() });
                return `<div class="infographic-container" id="${id}" style="min-height: 200px; width: 100%; margin: 1rem 0;"></div>`;
            }
        );
        this._infographicBlocks = infographicBlocks;
        
        // Pre-process Architecture DSL blocks
        const architectureBlocks = [];
        processedContent = processedContent.replace(
            /```(?:architecture-dsl|arch-dsl|architecture)\n([\s\S]*?)```/g,
            (match, dsl) => {
                const id = `workplace-architecture-${architectureBlocks.length}`;
                architectureBlocks.push({ id, dsl: dsl.trim() });
                return `<div class="architecture-diagram-container" id="${id}" style="min-height: 200px; width: 100%; margin: 1rem 0; overflow: auto;"></div>`;
            }
        );
        this._architectureBlocks = architectureBlocks;
        
        // Parse markdown
        let html;
        if (typeof marked !== 'undefined') {
            html = marked.parse(processedContent);
        } else {
            html = `<pre>${this._escapeHtml(content)}</pre>`;
        }
        
        return `<div class="workplace-markdown-content markdown-body">${html}</div>`;
    }
    
    /**
     * Render code with syntax highlighting
     */
    _renderCode(content, ext) {
        let highlighted = this._escapeHtml(content);
        if (typeof hljs !== 'undefined') {
            const lang = this._mapExtToLanguage(ext);
            if (lang && hljs.getLanguage(lang)) {
                try {
                    highlighted = hljs.highlight(content, { language: lang }).value;
                } catch (e) {
                    console.error('Highlight error:', e);
                }
            }
        }
        return `<pre class="workplace-code-content"><code class="hljs">${highlighted}</code></pre>`;
    }
    
    /**
     * Map file extension to highlight.js language
     */
    _mapExtToLanguage(ext) {
        const map = {
            'js': 'javascript', 'ts': 'typescript', 'jsx': 'javascript', 'tsx': 'typescript',
            'py': 'python', 'rb': 'ruby', 'sh': 'bash', 'bash': 'bash',
            'yml': 'yaml', 'md': 'markdown', 'htm': 'html'
        };
        return map[ext] || ext;
    }
    
    /**
     * Render Mermaid diagrams
     */
    async _renderMermaidDiagrams() {
        if (!this._mermaidBlocks || this._mermaidBlocks.length === 0) return;
        
        for (const block of this._mermaidBlocks) {
            const el = document.getElementById(block.id);
            if (el) {
                try {
                    const { svg } = await mermaid.render(block.id + '-svg', block.diagram);
                    el.innerHTML = svg;
                } catch (e) {
                    el.innerHTML = `<pre class="text-danger">Mermaid error: ${e.message}</pre>`;
                }
            }
        }
    }
    
    /**
     * Render Infographic DSL diagrams using AntV Infographic
     */
    async _renderInfographicDiagrams() {
        if (!this._infographicBlocks || this._infographicBlocks.length === 0) return;
        
        for (const block of this._infographicBlocks) {
            const el = document.getElementById(block.id);
            if (el) {
                try {
                    const infographic = new AntVInfographic.Infographic({
                        container: `#${block.id}`,
                        width: '100%',
                        height: '100%',
                    });
                    infographic.render(block.syntax);
                    // Re-render after fonts load
                    if (document.fonts?.ready) {
                        document.fonts.ready.then(() => {
                            infographic.render(block.syntax);
                        }).catch(e => console.warn('Font loading error:', e));
                    }
                } catch (e) {
                    el.innerHTML = `<pre class="text-danger">Infographic error: ${e.message}</pre>`;
                }
            }
        }
    }
    
    /**
     * Render Architecture DSL diagrams
     */
    async _renderArchitectureDiagrams() {
        if (!this._architectureBlocks || this._architectureBlocks.length === 0) return;
        
        for (const block of this._architectureBlocks) {
            const el = document.getElementById(block.id);
            if (el) {
                try {
                    const html = this._renderArchitectureHTML(this._parseArchitectureDSL(block.dsl));
                    el.innerHTML = html;
                } catch (e) {
                    el.innerHTML = `<pre class="text-danger">Architecture DSL error: ${e.message}</pre>`;
                }
            }
        }
    }
    
    /**
     * Parse Architecture DSL into AST
     */
    _parseArchitectureDSL(dsl) {
        const errors = [];
        const warnings = [];
        const lines = dsl.split('\n');
        
        const ast = {
            type: 'document', viewType: null, title: null, theme: 'theme-default',
            direction: 'top-to-bottom', grid: { cols: 12, rows: 6 }, textAlign: 'left',
            layers: [], errors, warnings
        };

        let currentLayer = null;
        let currentModule = null;
        let inMultiLineComment = false;

        for (const rawLine of lines) {
            let line = rawLine.trim();
            if (inMultiLineComment) { if (line.includes("'/")) inMultiLineComment = false; continue; }
            if (line.startsWith("/'")) { inMultiLineComment = true; continue; }
            if (line.startsWith("'") || line === '') continue;
            const commentIdx = line.indexOf("'");
            if (commentIdx > 0) line = line.substring(0, commentIdx).trim();

            if (line.startsWith('@startuml')) { const m = line.match(/@startuml\s+(module-view|landscape-view)/); if (m) ast.viewType = m[1]; continue; }
            if (line === '@enduml') continue;
            if (line.startsWith('title ')) { const m = line.match(/title\s+"([^"]+)"/); if (m) ast.title = m[1]; continue; }
            if (line.startsWith('grid ') && !currentModule) { const m = line.match(/grid\s+(\d+)\s*x\s*(\d+)/); if (m) ast.grid = { cols: parseInt(m[1]), rows: parseInt(m[2]) }; continue; }
            
            if (line.startsWith('layer ')) {
                const m = line.match(/layer\s+"([^"]+)"(?:\s+as\s+(\w+))?\s*\{?/);
                if (m) {
                    currentLayer = { type: 'layer', name: m[1], alias: m[2] || null, rows: 1, color: null, borderColor: null, textAlign: ast.textAlign, modules: [] };
                    ast.layers.push(currentLayer);
                }
                continue;
            }
            if (currentLayer && !currentModule) {
                if (line.startsWith('rows ')) { const m = line.match(/rows\s+(\d+)/); if (m) currentLayer.rows = parseInt(m[1]); continue; }
                if (line.startsWith('color ')) { const m = line.match(/color\s+"([^"]+)"/); if (m) currentLayer.color = m[1]; continue; }
                if (line.startsWith('border-color ')) { const m = line.match(/border-color\s+"([^"]+)"/); if (m) currentLayer.borderColor = m[1]; continue; }
                if (line.startsWith('module ')) {
                    const m = line.match(/module\s+"([^"]+)"(?:\s+as\s+(\w+))?\s*\{?/);
                    if (m) {
                        currentModule = { type: 'module', name: m[1], alias: m[2] || null, cols: 12, rows: 1, grid: { cols: 1, rows: 1 }, gap: '8px', components: [] };
                        currentLayer.modules.push(currentModule);
                    }
                    continue;
                }
                if (line === '}') { currentLayer = null; continue; }
            }
            if (currentModule) {
                if (line.startsWith('cols ')) { const m = line.match(/cols\s+(\d+)/); if (m) currentModule.cols = parseInt(m[1]); continue; }
                if (line.startsWith('rows ') && !line.includes(',')) { const m = line.match(/rows\s+(\d+)/); if (m) currentModule.rows = parseInt(m[1]); continue; }
                if (line.startsWith('grid ')) { const m = line.match(/grid\s+(\d+)\s*x\s*(\d+)/); if (m) currentModule.grid = { cols: parseInt(m[1]), rows: parseInt(m[2]) }; continue; }
                if (line.startsWith('gap ')) { const m = line.match(/gap\s+(\d+(?:px|rem))/); if (m) currentModule.gap = m[1]; continue; }
                if (line.startsWith('component ')) {
                    const m = line.match(/component\s+"([^"]+)"(?:\s*\{\s*cols\s+(\d+)(?:\s*,\s*rows\s+(\d+))?\s*\})?(?:\s*<<(\w+)>>)?/);
                    if (m) currentModule.components.push({ type: 'component', name: m[1], cols: m[2] ? parseInt(m[2]) : 1, rows: m[3] ? parseInt(m[3]) : 1, stereotype: m[4] || null });
                    continue;
                }
                if (line === '}') { currentModule = null; continue; }
            }
        }
        return ast;
    }
    
    /**
     * Render Architecture AST to HTML
     */
    _renderArchitectureHTML(ast) {
        const c = 'arch-diagram';
        const patterns = [
            { p: ['presentation', 'ui', 'frontend', 'view'], bg: '#fce7f3', border: '#ec4899' },
            { p: ['service', 'api', 'gateway'], bg: '#fef3c7', border: '#f97316' },
            { p: ['business', 'domain', 'logic', 'core'], bg: '#dbeafe', border: '#3b82f6' },
            { p: ['data', 'persistence', 'storage', 'db'], bg: '#dcfce7', border: '#22c55e' },
            { p: ['infrastructure', 'infra', 'platform'], bg: '#f3e8ff', border: '#a855f7' }
        ];
        const detectColors = (name) => {
            const n = name.toLowerCase();
            for (const pat of patterns) if (pat.p.some(x => n.includes(x))) return { bg: pat.bg, border: pat.border };
            return { bg: '#ffffff', border: '#374151' };
        };
        const esc = (t) => { const d = document.createElement('div'); d.textContent = t; return d.innerHTML; };
        
        let html = `<style>
            .${c} { font-family: 'Inter', system-ui, sans-serif; max-width: 1200px; margin: 0 auto; }
            .${c}-title { font-size: 22px; font-weight: 700; color: #374151; text-align: center; margin-bottom: 20px; }
            .${c}-content { display: flex; flex-direction: column; gap: 16px; }
            .${c}-layer-wrapper { display: flex; gap: 0; border-radius: 8px; transition: transform 0.3s, box-shadow 0.3s; }
            .${c}-layer-wrapper:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1); }
            .${c}-layer-label { writing-mode: vertical-rl; text-orientation: mixed; transform: rotate(180deg); background: #1f2937; padding: 16px 8px; font-size: 12px; font-weight: 600; color: #fff; display: flex; align-items: center; justify-content: center; border-radius: 0 8px 8px 0; min-width: 36px; transition: background 0.2s, min-width 0.2s; }
            .${c}-layer-wrapper:hover .${c}-layer-label { background: #6366f1; min-width: 40px; }
            .${c}-layer-wrapper:hover .${c}-layer { border-color: #6366f1; }
            .${c}-layer { flex: 1; padding: 20px; border: 2px solid; border-left: none; border-radius: 0 8px 8px 0; transition: border-color 0.2s; }
            .${c}-layer-row { display: grid; grid-template-columns: repeat(12, 1fr); gap: 14px; }
            .${c}-module { background: #fff; border: 1.5px dashed #d1d5db; border-radius: 8px; padding: 14px; display: flex; flex-direction: column; gap: 12px; transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s; }
            .${c}-module:hover { border-color: #3b82f6; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); transform: scale(1.01); }
            .${c}-module-title { font-size: 14px; font-weight: 700; color: #374151; }
            .${c}-module-content { display: grid; gap: 10px; }
            .${c}-component { background: #1f2937; color: #fff; border-radius: 18px; padding: 8px 16px; font-size: 12px; font-weight: 500; text-align: center; display: flex; align-items: center; justify-content: center; min-height: 36px; transition: all 0.2s; cursor: default; }
            .${c}-component:hover { background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%); transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
            .${c}-icon-component { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 8px; min-height: 60px; transition: transform 0.2s; cursor: default; }
            .${c}-icon-component:hover { transform: scale(1.1); }
            .${c}-icon { font-size: 28px; }
            .${c}-icon-label { font-size: 11px; color: #6b7280; }
        </style><div class="${c}">`;
        
        if (ast.title) html += `<div class="${c}-title">${esc(ast.title)}</div>`;
        html += `<div class="${c}-content">`;
        
        for (const layer of ast.layers) {
            const colors = layer.color ? { bg: layer.color, border: layer.borderColor || '#374151' } : detectColors(layer.name);
            html += `<div class="${c}-layer-wrapper"><div class="${c}-layer-label">${esc(layer.name.toUpperCase())}</div>`;
            html += `<div class="${c}-layer" style="background: ${colors.bg}; border-color: ${colors.border};"><div class="${c}-layer-row">`;
            
            for (const module of layer.modules) {
                const gridCols = module.grid?.cols || 1;
                const gap = parseInt(module.gap) || 10;
                html += `<div class="${c}-module" style="grid-column: span ${module.cols || 12};"><div class="${c}-module-title">${esc(module.name)}</div>`;
                html += `<div class="${c}-module-content" style="grid-template-columns: repeat(${gridCols}, 1fr); gap: ${gap}px;">`;
                
                for (const comp of module.components) {
                    const gs = `grid-column: span ${comp.cols || 1}; grid-row: span ${comp.rows || 1};`;
                    if (comp.stereotype && ['icon', 'folder', 'file', 'db'].includes(comp.stereotype)) {
                        const icons = { folder: '📁', file: '📄', db: '🗄️', icon: '⚙️' };
                        html += `<div class="${c}-icon-component" style="${gs}"><span class="${c}-icon">${icons[comp.stereotype] || '📦'}</span><span class="${c}-icon-label">${esc(comp.name)}</span></div>`;
                    } else {
                        html += `<div class="${c}-component" style="${gs}">${esc(comp.name)}</div>`;
                    }
                }
                html += '</div></div>';
            }
            html += '</div></div></div>';
        }
        html += '</div></div>';
        return html;
    }
    
    /**
     * Enter edit mode
     */
    enterEditMode() {
        this.isEditing = true;
        this.renderEditor();
    }
    
    /**
     * Exit edit mode (cancel changes)
     */
    exitEditMode() {
        if (this.hasUnsavedChanges) {
            if (!window.confirm('You have unsaved changes. Do you want to discard them?')) {
                return;
            }
        }
        // Clean up EasyMDE if active
        if (this.easyMDE) {
            this.easyMDE.toTextArea();
            this.easyMDE = null;
        }
        this.isEditing = false;
        this.hasUnsavedChanges = false;
        const contentArea = document.getElementById('workplace-content');
        this.renderContent(contentArea, this.originalContent);
    }
    
    /**
     * Render the editor (edit mode)
     */
    renderEditor() {
        const container = document.getElementById('workplace-content');
        const isMarkdown = this.fileType === 'markdown';
        
        container.innerHTML = `
            <div class="workplace-editor">
                <div class="workplace-editor-header">
                    <span class="workplace-editor-path">${this._escapeHtml(this.currentPath)}</span>
                    <div class="workplace-editor-actions">
                        <span class="workplace-editor-status" id="workplace-editor-status"></span>
                        <button class="btn btn-sm btn-outline-secondary workplace-cancel-btn" id="workplace-cancel-btn" title="Cancel editing">
                            <i class="bi bi-x-lg"></i> Cancel
                        </button>
                    </div>
                </div>
                <textarea class="workplace-editor-textarea" id="workplace-editor-textarea">${this._escapeHtml(this.originalContent)}</textarea>
            </div>
        `;
        
        const textarea = document.getElementById('workplace-editor-textarea');
        
        if (isMarkdown && typeof EasyMDE !== 'undefined') {
            // Use EasyMDE for markdown files
            this.easyMDE = new EasyMDE({
                element: textarea,
                spellChecker: false,
                autosave: { enabled: false },
                toolbar: [
                    'bold', 'italic', 'heading', '|',
                    'quote', 'unordered-list', 'ordered-list', '|',
                    'link', 'image', 'code', '|',
                    'preview', 'side-by-side', 'fullscreen', '|',
                    'guide'
                ],
                status: false,
                minHeight: '300px',
                placeholder: 'Start writing...',
                renderingConfig: { codeSyntaxHighlighting: true }
            });
            
            this.easyMDE.codemirror.on('change', () => {
                this.onContentChange();
            });
        } else {
            // Plain textarea for HTML and other files
            textarea.addEventListener('input', () => {
                this.onContentChange();
            });
            textarea.focus();
        }
        
        // Bind cancel button
        const cancelBtn = document.getElementById('workplace-cancel-btn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.exitEditMode());
        }
    }
    
    /**
     * Handle content change - schedule auto-save
     */
    onContentChange() {
        this.hasUnsavedChanges = true;
        this.updateStatus('modified');
        
        // Clear existing timer
        if (this.saveTimer) {
            clearTimeout(this.saveTimer);
        }
        
        // Schedule save after 5 seconds
        this.saveTimer = setTimeout(() => {
            this.saveContent();
        }, this.saveDelay);
    }
    
    /**
     * Save the current content
     */
    async saveContent() {
        if (!this.currentPath || !this.hasUnsavedChanges) return;
        
        let content;
        if (this.easyMDE) {
            content = this.easyMDE.value();
        } else {
            const textarea = document.getElementById('workplace-editor-textarea');
            if (!textarea) return;
            content = textarea.value;
        }
        
        this.updateStatus('saving');
        
        try {
            const response = await fetch('/api/file/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    path: this.currentPath,
                    content: content
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.originalContent = content;
                this.hasUnsavedChanges = false;
                this.updateStatus('saved');
                
                // Clear saved status after 2 seconds
                setTimeout(() => {
                    if (!this.hasUnsavedChanges) {
                        this.updateStatus('');
                    }
                }, 2000);
            } else {
                throw new Error(result.error || 'Failed to save');
            }
        } catch (error) {
            console.error('Failed to save file:', error);
            this.updateStatus('error');
            this._showToast('Failed to save file', 'error');
        }
    }
    
    /**
     * Update editor status indicator
     */
    updateStatus(status) {
        const statusEl = document.getElementById('workplace-editor-status');
        if (!statusEl) return;
        
        switch (status) {
            case 'modified':
                statusEl.innerHTML = '<i class="bi bi-circle-fill text-warning"></i> Modified';
                break;
            case 'saving':
                statusEl.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Saving...';
                break;
            case 'saved':
                statusEl.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i> Saved';
                break;
            case 'error':
                statusEl.innerHTML = '<i class="bi bi-exclamation-circle-fill text-danger"></i> Save failed';
                break;
            default:
                statusEl.innerHTML = '';
        }
    }
    
    /**
     * Show upload/compose view
     */
    showUploadView() {
        // Check for unsaved changes
        if (this.hasUnsavedChanges) {
            if (!window.confirm('You have unsaved changes. Do you want to discard them?')) {
                return;
            }
        }
        
        // Clean up previous EasyMDE instance
        if (this.easyMDE) {
            this.easyMDE.toTextArea();
            this.easyMDE = null;
        }
        
        this.currentView = 'upload';
        this.currentPath = null;
        this.hasUnsavedChanges = false;
        
        const contentArea = document.getElementById('workplace-content');
        contentArea.innerHTML = `
            <div class="workplace-uploader">
                <!-- Tab Navigation -->
                <ul class="nav nav-tabs workplace-tabs" id="ideaTabs" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="compose-tab" data-bs-toggle="tab" data-bs-target="#compose-pane" type="button" role="tab">
                            <i class="bi bi-pencil-square"></i> Compose Idea
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="upload-tab" data-bs-toggle="tab" data-bs-target="#upload-pane" type="button" role="tab">
                            <i class="bi bi-cloud-upload"></i> Upload Files
                        </button>
                    </li>
                </ul>
                
                <!-- Tab Content -->
                <div class="tab-content workplace-tab-content" id="ideaTabContent">
                    <!-- Compose Tab -->
                    <div class="tab-pane fade show active" id="compose-pane" role="tabpanel">
                        <div class="workplace-compose">
                            <textarea class="workplace-compose-textarea" id="workplace-compose-textarea" 
                                      placeholder="Write your idea here...&#10;&#10;You can use Markdown formatting:&#10;- **bold** and *italic*&#10;- # Headers&#10;- - Bullet lists&#10;- \`code\` blocks"></textarea>
                            <div class="workplace-compose-actions">
                                <button class="btn btn-primary" id="workplace-submit-idea">
                                    <i class="bi bi-send"></i> Submit Idea
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Upload Tab -->
                    <div class="tab-pane fade" id="upload-pane" role="tabpanel">
                        <div class="workplace-dropzone" id="workplace-dropzone">
                            <i class="bi bi-cloud-upload"></i>
                            <h5>Drag & Drop Files Here</h5>
                            <p class="text-muted mb-3">or click to browse</p>
                            <input type="file" id="workplace-file-input" multiple style="display: none;"
                                   accept=".md,.txt,.json,.yaml,.yml,.xml,.csv,.py,.js,.ts,.jsx,.tsx,.html,.css,.sh,.sql,.java,.c,.cpp,.h,.go,.rs,.rb,.php,.swift,.kt,.png,.jpg,.jpeg,.gif,.svg,.webp,.bmp,.ico">
                        </div>
                        <div class="workplace-supported-formats">
                            <p class="mb-2"><i class="bi bi-check-circle text-success me-1"></i><strong>Supported formats:</strong></p>
                            <div class="format-tags">
                                <span class="format-tag format-tag-docs"><i class="bi bi-file-text"></i> .md .txt</span>
                                <span class="format-tag format-tag-data"><i class="bi bi-braces"></i> .json .yaml .xml .csv</span>
                                <span class="format-tag format-tag-code"><i class="bi bi-code-slash"></i> .py .js .ts .jsx .tsx</span>
                                <span class="format-tag format-tag-code"><i class="bi bi-file-code"></i> .html .css .sh .sql</span>
                                <span class="format-tag format-tag-code"><i class="bi bi-terminal"></i> .java .c .cpp .go .rs .rb</span>
                                <span class="format-tag format-tag-image"><i class="bi bi-image"></i> .png .jpg .gif .svg .webp</span>
                            </div>
                            <p class="text-muted small mt-2 mb-0">
                                <i class="bi bi-info-circle me-1"></i>
                                Text-based files work best for AI analysis. Images can be uploaded for visual reference.
                            </p>
                        </div>
                    </div>
                </div>
                
                <div class="workplace-upload-status d-none" id="workplace-upload-status">
                    <div class="spinner-border spinner-border-sm" role="status"></div>
                    <span>Processing...</span>
                </div>
            </div>
        `;
        
        this.setupUploader();
        this.setupComposer();
    }
    
    /**
     * Setup compose event handlers
     */
    setupComposer() {
        const submitBtn = document.getElementById('workplace-submit-idea');
        const textarea = document.getElementById('workplace-compose-textarea');
        
        if (!submitBtn || !textarea) return;
        
        // Initialize EasyMDE markdown editor
        if (typeof EasyMDE !== 'undefined') {
            this.easyMDE = new EasyMDE({
                element: textarea,
                autofocus: true,
                spellChecker: false,
                placeholder: 'Write your idea here...\n\nYou can use Markdown formatting:\n- **bold** and *italic*\n- # Headers\n- - Bullet lists\n- `code` blocks',
                toolbar: [
                    'bold', 'italic', 'heading', '|',
                    'quote', 'unordered-list', 'ordered-list', '|',
                    'link', 'code', '|',
                    'preview', 'side-by-side', '|',
                    'guide'
                ],
                status: ['lines', 'words'],
                renderingConfig: {
                    codeSyntaxHighlighting: true
                },
                shortcuts: {
                    'toggleSideBySide': null // Disable side-by-side shortcut to avoid conflicts
                }
            });
            
            // Fix z-index when side-by-side is toggled and exit fullscreen when side-by-side is turned off
            const middleSection = document.getElementById('middle-section');
            let wasSideBySideActive = false;
            
            const observer = new MutationObserver(() => {
                const container = this.easyMDE.element.closest('.EasyMDEContainer');
                const isSideBySideActive = container && container.classList.contains('sided--no-fullscreen');
                const isFullscreen = container && container.classList.contains('EasyMDEContainer--fullscreen');
                
                if (isSideBySideActive) {
                    // Side-by-side is ON
                    middleSection.style.zIndex = '400';
                    wasSideBySideActive = true;
                } else {
                    // Side-by-side is OFF
                    middleSection.style.zIndex = '';
                    
                    // If side-by-side was just turned off but still in fullscreen, exit fullscreen
                    if (wasSideBySideActive && isFullscreen) {
                        EasyMDE.toggleFullScreen(this.easyMDE);
                    }
                    wasSideBySideActive = false;
                }
            });
            const container = this.easyMDE.element.closest('.EasyMDEContainer');
            if (container) {
                observer.observe(container, { attributes: true, attributeFilter: ['class'] });
            }
            
            // Ctrl+Enter to submit
            this.easyMDE.codemirror.on('keydown', (cm, e) => {
                if (e.ctrlKey && e.key === 'Enter') {
                    e.preventDefault();
                    this.submitComposedIdea();
                }
            });
        } else {
            // Fallback to basic textarea behavior
            textarea.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.key === 'Enter') {
                    e.preventDefault();
                    this.submitComposedIdea();
                }
            });
        }
        
        submitBtn.addEventListener('click', () => {
            this.submitComposedIdea();
        });
    }
    
    /**
     * Submit composed idea as a new markdown file
     */
    async submitComposedIdea() {
        const statusEl = document.getElementById('workplace-upload-status');
        
        // Get content from EasyMDE or fallback to textarea
        let content;
        if (this.easyMDE) {
            content = this.easyMDE.value().trim();
        } else {
            const textarea = document.getElementById('workplace-compose-textarea');
            if (!textarea) return;
            content = textarea.value.trim();
        }
        
        if (!content) {
            this._showToast('Please write something before submitting', 'warning');
            return;
        }
        
        if (statusEl) statusEl.classList.remove('d-none');
        
        try {
            // Create a Blob with the content as a markdown file
            const blob = new Blob([content], { type: 'text/markdown' });
            const file = new File([blob], 'new idea.md', { type: 'text/markdown' });
            
            const formData = new FormData();
            formData.append('files', file);
            
            const response = await fetch('/api/ideas/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this._showToast(`Idea created in ${result.folder_name}`, 'success');
                await this.loadTree();
                
                // Show success message
                const contentArea = document.getElementById('workplace-content');
                contentArea.innerHTML = `
                    <div class="workplace-placeholder">
                        <i class="bi bi-check-circle text-success"></i>
                        <h5>Idea Created!</h5>
                        <p class="text-muted">Your idea has been saved to "${result.folder_name}"</p>
                    </div>
                `;
            } else {
                throw new Error(result.error || 'Failed to create idea');
            }
        } catch (error) {
            console.error('Failed to submit idea:', error);
            this._showToast('Failed to create idea: ' + error.message, 'error');
        } finally {
            if (statusEl) statusEl.classList.add('d-none');
        }
    }
    
    /**
     * Setup upload event handlers
     */
    setupUploader() {
        const dropzone = document.getElementById('workplace-dropzone');
        const fileInput = document.getElementById('workplace-file-input');
        
        if (!dropzone || !fileInput) return;
        
        // Click to browse
        dropzone.addEventListener('click', () => {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.uploadFiles(e.target.files);
            }
        });
        
        // Drag and drop
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });
        
        dropzone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
        });
        
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            
            if (e.dataTransfer.files.length > 0) {
                this.uploadFiles(e.dataTransfer.files);
            }
        });
    }
    
    /**
     * Upload files to the server
     */
    async uploadFiles(files) {
        const statusEl = document.getElementById('workplace-upload-status');
        const dropzone = document.getElementById('workplace-dropzone');
        
        if (statusEl) statusEl.classList.remove('d-none');
        if (dropzone) dropzone.classList.add('uploading');
        
        try {
            const formData = new FormData();
            for (const file of files) {
                formData.append('files', file);
            }
            
            const response = await fetch('/api/ideas/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this._showToast(`Uploaded ${result.files_uploaded.length} file(s) to ${result.folder_name}`, 'success');
                await this.loadTree();
                
                // Show placeholder after successful upload
                const contentArea = document.getElementById('workplace-content');
                contentArea.innerHTML = `
                    <div class="workplace-placeholder">
                        <i class="bi bi-check-circle text-success"></i>
                        <h5>Upload Complete</h5>
                        <p class="text-muted">Files uploaded to ${this._escapeHtml(result.folder_name)}</p>
                    </div>
                `;
            } else {
                throw new Error(result.error || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload failed:', error);
            this._showToast(error.message || 'Upload failed', 'error');
            
            if (statusEl) statusEl.classList.add('d-none');
            if (dropzone) dropzone.classList.remove('uploading');
        }
    }
    
    /**
     * CR-002: Setup drag-drop handlers on folder nodes in the tree
     * Called after tree render
     */
    _setupFolderDragDrop() {
        const folderNodes = document.querySelectorAll('.idea-folder-node');
        
        folderNodes.forEach(node => {
            const folderPath = node.dataset.folderPath;
            if (!folderPath) return;
            
            // Prevent default to allow drop
            node.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.stopPropagation();
                node.classList.add('drop-target');
            });
            
            node.addEventListener('dragleave', (e) => {
                e.preventDefault();
                e.stopPropagation();
                // Only remove if leaving the node itself, not entering a child
                if (!node.contains(e.relatedTarget)) {
                    node.classList.remove('drop-target');
                }
            });
            
            node.addEventListener('drop', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                node.classList.remove('drop-target');
                
                if (e.dataTransfer.files.length > 0) {
                    await this._uploadToFolder(e.dataTransfer.files, folderPath);
                }
            });
        });
    }
    
    /**
     * CR-002: Upload files to a specific existing folder
     * @param {FileList} files - Files to upload
     * @param {string} folderPath - Target folder path (relative to docs/ideas/)
     */
    async _uploadToFolder(files, folderPath) {
        try {
            const formData = new FormData();
            for (const file of files) {
                formData.append('files', file);
            }
            formData.append('target_folder', folderPath);
            
            const response = await fetch('/api/ideas/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Extract folder name from path for display
                const folderName = folderPath.split('/').pop();
                this._showToast(
                    `Uploaded ${result.files_uploaded.length} file(s) to ${folderName}`,
                    'success'
                );
                await this.loadTree();
            } else {
                this._showToast(result.error || 'Upload failed', 'error');
            }
        } catch (error) {
            console.error('Upload to folder failed:', error);
            this._showToast('Upload failed: ' + error.message, 'error');
        }
    }
    
    /**
     * Show toast notification
     */
    _showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;
        
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        
        const icon = type === 'success' ? 'bi-check-circle' : 
                     type === 'error' ? 'bi-exclamation-circle' : 'bi-info-circle';
        
        toast.innerHTML = `
            <i class="bi ${icon}"></i>
            <span>${message}</span>
        `;
        
        toastContainer.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Remove after delay
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    // =========================================================================
    // CR-003: Ideation Toolbox Methods
    // =========================================================================
    
    /**
     * Show delete confirmation dialog using Bootstrap 5 modal
     */
    confirmDelete(path, name, type) {
        const typeLabel = type === 'folder' ? 'folder' : 'file';
        const warningText = type === 'folder' ? 'This will delete the folder and all its contents.' : 'This will permanently delete the file.';
        
        // Create modal if it doesn't exist
        let modal = document.getElementById('workplace-delete-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'workplace-delete-modal';
            modal.className = 'modal fade';
            modal.tabIndex = -1;
            modal.setAttribute('aria-labelledby', 'deleteModalLabel');
            modal.setAttribute('aria-hidden', 'true');
            document.body.appendChild(modal);
        }
        
        // Set modal content
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header border-0 pb-0">
                        <h5 class="modal-title" id="deleteModalLabel">
                            <i class="bi bi-exclamation-triangle-fill text-danger me-2"></i>
                            Delete ${typeLabel}?
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-2">You are about to delete:</p>
                        <div class="alert alert-light border d-flex align-items-center py-2 mb-3">
                            <i class="bi ${type === 'folder' ? 'bi-folder-fill text-warning' : 'bi-file-earmark-fill text-secondary'} me-2"></i>
                            <strong class="text-break">${this._escapeHtml(name)}</strong>
                        </div>
                        <p class="text-muted small mb-0">
                            <i class="bi bi-info-circle me-1"></i>
                            ${warningText} This action cannot be undone.
                        </p>
                    </div>
                    <div class="modal-footer border-0 pt-0">
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                            <i class="bi bi-x-lg me-1"></i>Cancel
                        </button>
                        <button type="button" class="btn btn-danger" id="workplace-delete-confirm-btn">
                            <i class="bi bi-trash me-1"></i>Delete
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Initialize Bootstrap modal
        const bsModal = new bootstrap.Modal(modal);
        
        // Handle confirm button click
        const confirmBtn = document.getElementById('workplace-delete-confirm-btn');
        const handleConfirm = () => {
            bsModal.hide();
            this.deleteItem(path, name, type);
        };
        confirmBtn.addEventListener('click', handleConfirm, { once: true });
        
        // Clean up event listener if modal is dismissed
        modal.addEventListener('hidden.bs.modal', () => {
            confirmBtn.removeEventListener('click', handleConfirm);
        }, { once: true });
        
        // Show modal
        bsModal.show();
    }
    
    /**
     * Delete a file or folder
     */
    async deleteItem(path, name, type) {
        try {
            const response = await fetch('/api/ideas/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: path })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this._showToast(`Deleted ${type}: ${name}`, 'success');
                
                // If currently viewing the deleted file, clear the editor
                if (this.currentPath && (this.currentPath === path || this.currentPath.startsWith(path + '/'))) {
                    this.currentPath = null;
                    this.hasUnsavedChanges = false;
                    const contentArea = document.getElementById('workplace-content');
                    if (contentArea) {
                        contentArea.innerHTML = `
                            <div class="workplace-placeholder">
                                <i class="bi bi-lightbulb"></i>
                                <h5>Welcome to Workplace</h5>
                                <p class="text-muted">Upload an idea or select a file from the tree</p>
                            </div>
                        `;
                    }
                }
                
                // Refresh the tree
                await this.loadTree();
            } else {
                this._showToast(result.error || 'Failed to delete', 'error');
            }
        } catch (error) {
            console.error('Failed to delete:', error);
            this._showToast('Failed to delete', 'error');
        }
    }
    
    /**
     * Download a file from the idea folder
     */
    async downloadFile(path, name) {
        try {
            // Fetch file content via the existing API
            const response = await fetch(`/api/file/content?path=${encodeURIComponent(path)}`);
            
            if (!response.ok) {
                throw new Error('Failed to fetch file');
            }
            
            const data = await response.json();
            const content = data.content || '';
            
            // Create a blob and download link
            const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = name;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // Clean up the URL object
            URL.revokeObjectURL(url);
            
            this._showToast(`Downloaded: ${name}`, 'success');
        } catch (error) {
            console.error('Failed to download file:', error);
            this._showToast('Failed to download file', 'error');
        }
    }
    
    /**
     * Escape HTML special characters
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }
}
