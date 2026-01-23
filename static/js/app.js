class ContentRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentPath = null;
        this.initMermaid();
        this.initMarked();
    }
    
    /**
     * Initialize Mermaid.js configuration
     */
    initMermaid() {
        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({
                startOnLoad: false,
                theme: 'default',
                securityLevel: 'loose'
            });
        }
    }
    
    /**
     * Initialize Marked.js configuration with highlight.js
     */
    initMarked() {
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                highlight: function(code, lang) {
                    if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (e) {
                            console.error('Highlight error:', e);
                        }
                    }
                    return code;
                },
                breaks: true,
                gfm: true
            });
        }
    }
    
    /**
     * Load and render file content
     */
    async load(path) {
        if (!path) return;
        
        this.currentPath = path;
        this.showLoading();
        
        try {
            const response = await fetch(`/api/file/content?path=${encodeURIComponent(path)}`);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || `HTTP error ${response.status}`);
            }
            
            const data = await response.json();
            this.render(data);
        } catch (error) {
            console.error('Failed to load file:', error);
            this.showError(error.message);
        }
    }
    
    /**
     * Render content based on file type
     */
    render(data) {
        const { content, type, path, extension } = data;
        
        if (type === 'markdown') {
            this.renderMarkdown(content);
        } else {
            this.renderCode(content, type);
        }
    }
    
    /**
     * Render markdown content with Mermaid diagrams and Infographic DSL
     */
    renderMarkdown(content) {
        // Pre-process Mermaid blocks
        const mermaidBlocks = [];
        let processedContent = content.replace(
            /```mermaid\n([\s\S]*?)```/g,
            (match, diagram, offset) => {
                const id = `mermaid-${mermaidBlocks.length}`;
                mermaidBlocks.push({ id, diagram: diagram.trim() });
                return `<div class="mermaid" id="${id}"></div>`;
            }
        );
        
        // Pre-process Infographic blocks
        const infographicBlocks = [];
        processedContent = processedContent.replace(
            /```infographic\n([\s\S]*?)```/g,
            (match, syntax) => {
                const id = `infographic-${infographicBlocks.length}`;
                infographicBlocks.push({ id, syntax: syntax.trim() });
                return `<div class="infographic-container" id="${id}" style="min-height: 200px; width: 100%; margin: 1rem 0;"></div>`;
            }
        );
        
        // Parse markdown
        let html;
        if (typeof marked !== 'undefined') {
            html = marked.parse(processedContent);
        } else {
            // Fallback: escape HTML and preserve whitespace
            html = '<pre>' + this.escapeHtml(content) + '</pre>';
        }
        
        // Wrap in markdown-body container
        this.container.innerHTML = `<div class="markdown-body">${html}</div>`;
        
        // Render Mermaid diagrams
        this.renderMermaidDiagrams(mermaidBlocks);
        
        // Render Infographic diagrams
        this.renderInfographicDiagrams(infographicBlocks);
        
        // Apply syntax highlighting to code blocks
        this.highlightCodeBlocks();
    }
    
    /**
     * Render Mermaid diagrams
     */
    async renderMermaidDiagrams(blocks) {
        if (typeof mermaid === 'undefined' || blocks.length === 0) return;
        
        for (const block of blocks) {
            const element = document.getElementById(block.id);
            if (element) {
                try {
                    const { svg } = await mermaid.render(block.id + '-svg', block.diagram);
                    element.innerHTML = svg;
                } catch (error) {
                    console.error('Mermaid render error:', error);
                    element.innerHTML = `<div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i>
                        Diagram rendering error: ${error.message}
                    </div>`;
                }
            }
        }
    }
    
    /**
     * Render Infographic DSL diagrams using AntV Infographic
     */
    async renderInfographicDiagrams(blocks) {
        if (typeof AntVInfographic === 'undefined' || blocks.length === 0) return;
        
        for (const block of blocks) {
            const element = document.getElementById(block.id);
            if (element) {
                try {
                    const infographic = new AntVInfographic.Infographic({
                        container: `#${block.id}`,
                        width: '100%',
                        height: '100%',
                    });
                    infographic.render(block.syntax);
                    // Re-render after fonts load for better display
                    if (document.fonts?.ready) {
                        document.fonts.ready.then(() => {
                            infographic.render(block.syntax);
                        }).catch(e => console.warn('Font loading error:', e));
                    }
                } catch (error) {
                    console.error('Infographic render error:', error);
                    element.innerHTML = `<div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i>
                        Infographic rendering error: ${error.message}
                    </div>`;
                }
            }
        }
    }
    
    /**
     * Apply syntax highlighting to code blocks
     */
    highlightCodeBlocks() {
        if (typeof hljs === 'undefined') return;
        
        this.container.querySelectorAll('pre code').forEach(block => {
            hljs.highlightElement(block);
        });
    }
    
    /**
     * Render code with syntax highlighting
     */
    renderCode(content, type) {
        let highlighted = this.escapeHtml(content);
        
        if (typeof hljs !== 'undefined') {
            try {
                if (type !== 'text' && hljs.getLanguage(type)) {
                    highlighted = hljs.highlight(content, { language: type }).value;
                } else {
                    highlighted = hljs.highlightAuto(content).value;
                }
            } catch (e) {
                console.error('Highlight error:', e);
            }
        }
        
        this.container.innerHTML = `
            <div class="code-viewer">
                <pre><code class="language-${type}">${highlighted}</code></pre>
            </div>
        `;
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        this.container.innerHTML = `
            <div class="content-loading">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.container.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                <strong>Error:</strong> ${this.escapeHtml(message)}
            </div>
        `;
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

/**
 * Content Editor
 * FEATURE-003: Content Editor
 * 
 * Provides in-place editing of document content via textarea.
 * Integrates with ContentRenderer to switch between view/edit modes.
 */
class ContentEditor {
    constructor(options) {
        this.containerId = options.containerId || 'content-body';
        this.contentRenderer = options.contentRenderer;
        
        // State
        this.isEditing = false;
        this.currentPath = null;
        this.originalContent = null;
        this.hasUnsavedChanges = false;
        
        // DOM elements
        this.container = document.getElementById(this.containerId);
        this.editorActions = document.getElementById('editor-actions');
        this.btnEdit = document.getElementById('btn-edit');
        this.btnSave = document.getElementById('btn-save');
        this.btnCancel = document.getElementById('btn-cancel');
        this.textarea = null;
        
        this._setupEventListeners();
        this._setupKeyboardShortcuts();
        this._setupBeforeUnload();
    }
    
    /**
     * Setup click event listeners for buttons
     */
    _setupEventListeners() {
        if (this.btnEdit) {
            this.btnEdit.addEventListener('click', () => this.startEditing());
        }
        if (this.btnSave) {
            this.btnSave.addEventListener('click', () => this.save());
        }
        if (this.btnCancel) {
            this.btnCancel.addEventListener('click', () => this.cancel());
        }
    }
    
    /**
     * Setup keyboard shortcuts
     */
    _setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + E: Start editing
            if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
                if (!this.isEditing && this.currentPath) {
                    e.preventDefault();
                    this.startEditing();
                }
            }
            
            // Ctrl/Cmd + S: Save
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                if (this.isEditing) {
                    e.preventDefault();
                    this.save();
                }
            }
            
            // Escape: Cancel editing
            if (e.key === 'Escape') {
                if (this.isEditing) {
                    e.preventDefault();
                    this.cancel();
                }
            }
        });
    }
    
    /**
     * Setup beforeunload handler to warn about unsaved changes
     */
    _setupBeforeUnload() {
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
                return e.returnValue;
            }
        });
    }
    
    /**
     * Set current path when a file is selected
     */
    setCurrentPath(path) {
        // If editing and path changes, warn about unsaved changes
        if (this.isEditing && this.currentPath !== path) {
            if (this.hasUnsavedChanges) {
                const confirm = window.confirm('You have unsaved changes. Do you want to discard them?');
                if (!confirm) {
                    return false;  // Block navigation
                }
            }
            // Cancel current edit
            this._exitEditMode(false);
        }
        
        this.currentPath = path;
        
        // Show edit button when file is loaded
        if (path && this.editorActions) {
            this.editorActions.classList.remove('d-none');
        }
        
        return true;
    }
    
    /**
     * Check if navigation is allowed
     */
    canNavigate() {
        if (this.hasUnsavedChanges) {
            return window.confirm('You have unsaved changes. Do you want to discard them?');
        }
        return true;
    }
    
    /**
     * Start editing the current file
     */
    async startEditing() {
        if (!this.currentPath || this.isEditing) return;
        
        // Fetch raw content
        try {
            const response = await fetch(`/api/file/content?path=${encodeURIComponent(this.currentPath)}`);
            if (!response.ok) {
                throw new Error('Failed to load file content');
            }
            const data = await response.json();
            this.originalContent = data.content;
            
            // Switch to edit mode
            this._enterEditMode(data.content);
            
        } catch (error) {
            console.error('Failed to start editing:', error);
            this._showToast('Failed to load file for editing', 'error');
        }
    }
    
    /**
     * Enter edit mode - show textarea
     */
    _enterEditMode(content) {
        this.isEditing = true;
        
        // Create textarea
        this.textarea = document.createElement('textarea');
        this.textarea.className = 'content-editor-textarea';
        this.textarea.value = content;
        this.textarea.placeholder = 'Enter content...';
        
        // Track changes
        this.textarea.addEventListener('input', () => {
            this.hasUnsavedChanges = this.textarea.value !== this.originalContent;
            this._updateSaveButtonState();
        });
        
        // Replace content with textarea
        this.container.innerHTML = '';
        this.container.appendChild(this.textarea);
        
        // Focus textarea
        this.textarea.focus();
        
        // Update button visibility
        this._updateButtonVisibility(true);
        
        // Disable auto-refresh while editing
        if (window.refreshManager) {
            window.refreshManager.disable();
        }
    }
    
    /**
     * Exit edit mode - restore viewer
     */
    _exitEditMode(rerender = true) {
        this.isEditing = false;
        this.hasUnsavedChanges = false;
        this.textarea = null;
        
        // Update button visibility
        this._updateButtonVisibility(false);
        
        // Re-enable auto-refresh
        if (window.refreshManager) {
            window.refreshManager.enable();
        }
        
        // Re-render content
        if (rerender && this.currentPath && this.contentRenderer) {
            this.contentRenderer.load(this.currentPath);
        }
    }
    
    /**
     * Update button visibility based on edit state
     */
    _updateButtonVisibility(isEditing) {
        if (this.btnEdit) {
            this.btnEdit.classList.toggle('d-none', isEditing);
        }
        if (this.btnSave) {
            this.btnSave.classList.toggle('d-none', !isEditing);
        }
        if (this.btnCancel) {
            this.btnCancel.classList.toggle('d-none', !isEditing);
        }
    }
    
    /**
     * Update save button enabled state
     */
    _updateSaveButtonState() {
        if (this.btnSave) {
            this.btnSave.disabled = !this.hasUnsavedChanges;
        }
    }
    
    /**
     * Save the file
     */
    async save() {
        if (!this.isEditing || !this.currentPath || !this.textarea) return;
        
        const content = this.textarea.value;
        
        // Disable save button during save
        if (this.btnSave) {
            this.btnSave.disabled = true;
            this.btnSave.innerHTML = '<i class="bi bi-hourglass-split"></i> Saving...';
        }
        
        try {
            const response = await fetch('/api/file/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    path: this.currentPath,
                    content: content
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this._showToast('File saved successfully', 'success');
                this.originalContent = content;
                this.hasUnsavedChanges = false;
                
                // Exit edit mode and re-render
                this._exitEditMode(true);
            } else {
                throw new Error(result.error || 'Failed to save file');
            }
            
        } catch (error) {
            console.error('Failed to save file:', error);
            this._showToast(error.message || 'Failed to save file', 'error');
            
            // Restore save button
            if (this.btnSave) {
                this.btnSave.disabled = false;
                this.btnSave.innerHTML = '<i class="bi bi-check-lg"></i> Save';
            }
        }
    }
    
    /**
     * Cancel editing
     */
    cancel() {
        if (!this.isEditing) return;
        
        // Check for unsaved changes
        if (this.hasUnsavedChanges) {
            const confirm = window.confirm('You have unsaved changes. Do you want to discard them?');
            if (!confirm) return;
        }
        
        this._exitEditMode(true);
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
}

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
    }
    
    /**
     * Render the workplace view in the content area
     */
    async render(container) {
        this.isActive = true;
        container.innerHTML = `
            <div class="workplace-container">
                <div class="workplace-sidebar" id="workplace-sidebar">
                    <div class="workplace-sidebar-icons">
                        <button class="workplace-sidebar-icon" title="Browse Ideas" id="workplace-icon-browse">
                            <i class="bi bi-folder2"></i>
                        </button>
                    </div>
                    <div class="workplace-sidebar-content">
                        <div class="workplace-sidebar-header">
                            <span class="workplace-sidebar-title">Ideas</span>
                            <button class="workplace-pin-btn" title="Pin sidebar" id="workplace-pin-btn">
                                <i class="bi bi-pin-angle"></i>
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
     * Render tree nodes recursively
     */
    renderTree(container, nodes, level = 0) {
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
                // Folder: click to toggle, double-click to rename (only top-level)
                itemContent.addEventListener('click', (e) => {
                    e.stopPropagation();
                    li.classList.toggle('expanded');
                });
                
                // Only allow rename on top-level idea folders
                if (level === 0) {
                    itemContent.addEventListener('dblclick', (e) => {
                        e.stopPropagation();
                        this.startFolderRename(li, node.name);
                    });
                }
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
                        <button class="btn btn-sm btn-outline-info workplace-copilot-btn" id="workplace-copilot-btn" title="Refine with Copilot">
                            <i class="bi bi-robot"></i> Copilot
                        </button>
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
        const binaryExts = ['docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 'pdf', 'zip', 'rar',
                           'png', 'jpg', 'jpeg', 'gif', 'bmp', 'ico', 'svg', 'webp',
                           'mp3', 'mp4', 'wav', 'avi', 'mov', 'exe', 'dll', 'bin'];
        
        if (markdownExts.includes(ext)) return 'markdown';
        if (codeExts.includes(ext)) return 'code';
        if (binaryExts.includes(ext)) return 'binary';
        return 'text';
    }
    
    /**
     * Render content based on file type (view mode)
     */
    renderContent(container, content) {
        const header = `
            <div class="workplace-editor-header">
                <span class="workplace-editor-path">${this._escapeHtml(this.currentPath)}</span>
                <div class="workplace-editor-actions">
                    <span class="workplace-editor-status" id="workplace-editor-status"></span>
                    <button class="btn btn-sm btn-outline-info workplace-copilot-btn" id="workplace-copilot-btn" title="Refine with Copilot">
                        <i class="bi bi-robot"></i> Copilot
                    </button>
                </div>
            </div>
        `;
        
        let bodyContent;
        if (this.fileType === 'binary') {
            bodyContent = this._renderBinaryPlaceholder();
        } else if (this.fileType === 'markdown') {
            bodyContent = this._renderMarkdown(content);
        } else if (this.fileType === 'code') {
            bodyContent = this._renderCode(content, this.fileExtension);
        } else {
            bodyContent = `<pre class="workplace-text-content">${this._escapeHtml(content)}</pre>`;
        }
        
        // Show hint for editable files
        const editHint = this.fileType !== 'binary' ? '<span class="workplace-edit-hint text-muted small">Double-click to edit</span>' : '';
        
        container.innerHTML = `
            <div class="workplace-editor">
                ${header}
                <div class="workplace-content-body" id="workplace-content-body" title="${this.fileType !== 'binary' ? 'Double-click to edit' : ''}">
                    ${bodyContent}
                </div>
                ${editHint ? `<div class="workplace-edit-hint-container">${editHint}</div>` : ''}
            </div>
        `;
        
        // Bind double-click to edit (for editable files)
        if (this.fileType !== 'binary') {
            const contentBody = document.getElementById('workplace-content-body');
            if (contentBody) {
                contentBody.addEventListener('dblclick', () => this.enterEditMode());
            }
        }
        
        // Bind copilot button
        const copilotBtn = document.getElementById('workplace-copilot-btn');
        if (copilotBtn) {
            copilotBtn.addEventListener('click', () => this._handleCopilotClick());
        }
        
        // Render Mermaid diagrams if any
        if (this.fileType === 'markdown' && typeof mermaid !== 'undefined') {
            this._renderMermaidDiagrams();
        }
        
        // Render Infographic diagrams if any
        if (this.fileType === 'markdown' && typeof AntVInfographic !== 'undefined') {
            this._renderInfographicDiagrams();
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
        textarea.addEventListener('input', () => {
            this.onContentChange();
        });
        textarea.focus();
        
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
        
        const textarea = document.getElementById('workplace-editor-textarea');
        if (!textarea) return;
        
        const content = textarea.value;
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

/**
 * Content Refresh Manager
 * FEATURE-004: Live Refresh (Polling Implementation)
 * 
 * Handles automatic content refresh when files change on disk.
 * Uses HTTP polling every 5 seconds to detect changes.
 */
class ContentRefreshManager {
    constructor(options) {
        this.contentRenderer = options.contentRenderer;
        this.enabled = this._loadEnabledState();
        this.scrollPosition = 0;
        this.lastContent = null;
        this.lastPath = null;
        this.pollInterval = 5000; // 5 seconds
        this.pollTimer = null;
        
        this._setupToggleListener();
        this._updateToggleUI();
        this._startPolling();
    }
    
    /**
     * Load enabled state from localStorage
     */
    _loadEnabledState() {
        const saved = localStorage.getItem('autoRefreshEnabled');
        return saved === null ? true : saved === 'true';
    }
    
    /**
     * Save enabled state to localStorage
     */
    _saveEnabledState() {
        localStorage.setItem('autoRefreshEnabled', this.enabled.toString());
    }
    
    /**
     * Setup toggle UI listener
     */
    _setupToggleListener() {
        const toggle = document.getElementById('auto-refresh-toggle');
        if (toggle) {
            toggle.addEventListener('change', (e) => {
                this.setEnabled(e.target.checked);
            });
        }
    }
    
    /**
     * Update toggle UI to match current state
     */
    _updateToggleUI() {
        const toggle = document.getElementById('auto-refresh-toggle');
        if (toggle) {
            toggle.checked = this.enabled;
        }
    }
    
    /**
     * Start polling loop
     */
    _startPolling() {
        this.pollTimer = setInterval(() => {
            this._checkForChanges();
        }, this.pollInterval);
    }
    
    /**
     * Check for content changes via HTTP polling
     */
    async _checkForChanges() {
        if (!this.enabled) return;
        
        const currentPath = this.contentRenderer?.currentPath;
        if (!currentPath) return;
        
        // Skip if path changed - reset tracking
        if (currentPath !== this.lastPath) {
            this.lastContent = null;
            this.lastPath = currentPath;
            return;
        }
        
        // Skip planning files (handled by PlanningFilePoller)
        if (/planning[\/\\](task-board|features)\.md$/i.test(currentPath)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/file/content?path=${encodeURIComponent(currentPath)}`);
            
            if (!response.ok) {
                // File might be deleted
                if (response.status === 404) {
                    this._handleFileDeletion();
                }
                return;
            }
            
            const data = await response.json();
            const newContent = data.content;
            
            // First load - just cache
            if (this.lastContent === null) {
                this.lastContent = newContent;
                return;
            }
            
            // Check if content changed
            if (this.lastContent !== newContent) {
                this.lastContent = newContent;
                this._refreshContent(data);
            }
        } catch (error) {
            // Silently ignore poll errors
        }
    }
    
    /**
     * Handle file deletion
     */
    _handleFileDeletion() {
        const container = this.contentRenderer?.container;
        if (container) {
            container.innerHTML = `
                <div class="alert alert-warning d-flex flex-column align-items-center justify-content-center h-100 m-4">
                    <i class="bi bi-file-earmark-x display-4 mb-3"></i>
                    <h5>File Not Found</h5>
                    <p class="text-muted text-center">
                        The file you were viewing has been deleted or moved.
                    </p>
                    <button class="btn btn-outline-primary" onclick="window.projectSidebar?.load()">
                        <i class="bi bi-folder2-open"></i> Browse Files
                    </button>
                </div>
            `;
        }
        this.lastContent = null;
        this.lastPath = null;
    }
    
    /**
     * Refresh the content view with scroll preservation
     */
    _refreshContent(data) {
        const contentBody = document.getElementById('content-body');
        this.scrollPosition = contentBody ? contentBody.scrollTop : 0;
        
        // Re-render using ContentRenderer
        if (this.contentRenderer) {
            this.contentRenderer.render(data);
        }
        
        // Restore scroll position
        if (contentBody) {
            requestAnimationFrame(() => {
                const maxScroll = contentBody.scrollHeight - contentBody.clientHeight;
                contentBody.scrollTop = Math.min(this.scrollPosition, maxScroll);
            });
        }
        
        // Show refresh indicator
        this._showRefreshIndicator();
    }
    
    /**
     * Refresh the current content (public method)
     */
    async refresh() {
        const currentPath = this.contentRenderer?.currentPath;
        if (!currentPath) return;
        
        // Save scroll position
        const contentBody = document.getElementById('content-body');
        this.scrollPosition = contentBody ? contentBody.scrollTop : 0;
        
        try {
            // Reload content
            await this.contentRenderer.load(currentPath);
            
            // Restore scroll position
            if (contentBody) {
                const maxScroll = contentBody.scrollHeight - contentBody.clientHeight;
                contentBody.scrollTop = Math.min(this.scrollPosition, maxScroll);
            }
            
            // Update cached content
            const response = await fetch(`/api/file/content?path=${encodeURIComponent(currentPath)}`);
            if (response.ok) {
                const data = await response.json();
                this.lastContent = data.content;
            }
            
            this._showRefreshIndicator();
        } catch (error) {
            console.error('Refresh failed:', error);
        }
    }
    
    /**
     * Show visual indicator that content was refreshed
     */
    _showRefreshIndicator() {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = 'refresh-toast';
        toast.innerHTML = `
            <i class="bi bi-arrow-repeat"></i>
            Content updated
        `;
        
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 2500);
    }
    
    /**
     * Set auto-refresh enabled state
     */
    setEnabled(enabled) {
        this.enabled = enabled;
        this._saveEnabledState();
        this._updateToggleUI();
    }
    
    /**
     * Disable auto-refresh (called when editing)
     */
    disable() {
        this.enabled = false;
        this._updateToggleUI();
    }
    
    /**
     * Enable auto-refresh (called after editing)
     */
    enable() {
        this.enabled = this._loadEnabledState();
        this._updateToggleUI();
    }
    
    /**
     * Get current enabled state
     */
    isEnabled() {
        return this.enabled;
    }
}

/**
 * Planning File Poller
 * 
 * Automatically polls for updates on planning files (task-board.md, features.md)
 * every 5 seconds to ensure the latest content is always displayed.
 * Uses simple HTTP polling - no sockets.
 */
class PlanningFilePoller {
    constructor(options) {
        this.pollInterval = options.pollInterval || 5000; // 5 seconds
        this.lastContent = null;
        this.lastPath = null;
        // Match any path ending with these filenames
        this.planningFilePatterns = [
            /planning[\/\\]task-board\.md$/i,
            /planning[\/\\]features\.md$/i
        ];
        
        // Start the polling loop immediately
        this._startPollingLoop();
    }
    
    /**
     * Check if a path is a planning file
     */
    isPlanningFile(path) {
        if (!path) return false;
        return this.planningFilePatterns.some(pattern => pattern.test(path));
    }
    
    /**
     * Get the currently viewed file path from ContentRenderer
     */
    getCurrentPath() {
        return window.contentRenderer?.currentPath || null;
    }
    
    /**
     * Start the main polling loop - runs forever
     */
    _startPollingLoop() {
        setInterval(() => {
            this._checkAndRefresh();
        }, this.pollInterval);
    }
    
    /**
     * Check current file and refresh if needed
     */
    async _checkAndRefresh() {
        const currentPath = this.getCurrentPath();
        
        // Reset if path changed
        if (currentPath !== this.lastPath) {
            this.lastContent = null;
            this.lastPath = currentPath;
        }
        
        // Only poll planning files
        if (!this.isPlanningFile(currentPath)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/file/content?path=${encodeURIComponent(currentPath)}`);
            if (!response.ok) return;
            
            const data = await response.json();
            const newContent = data.content;
            
            // First load - just store content
            if (this.lastContent === null) {
                this.lastContent = newContent;
                return;
            }
            
            // Check if content changed
            if (this.lastContent !== newContent) {
                this.lastContent = newContent;
                this._refreshContent(data);
            }
        } catch (error) {
            // Silently ignore poll errors
        }
    }
    
    /**
     * Refresh the content view with scroll preservation
     */
    _refreshContent(data) {
        const contentBody = document.getElementById('content-body');
        const scrollTop = contentBody ? contentBody.scrollTop : 0;
        
        // Re-render using ContentRenderer
        if (window.contentRenderer) {
            window.contentRenderer.render(data);
        }
        
        // Restore scroll position
        if (contentBody) {
            requestAnimationFrame(() => {
                const maxScroll = contentBody.scrollHeight - contentBody.clientHeight;
                contentBody.scrollTop = Math.min(scrollTop, maxScroll);
            });
        }
        
        // Show toast notification
        this._showToast();
    }
    
    /**
     * Show refresh notification
     */
    _showToast() {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = 'refresh-toast';
        toast.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Updated';
        container.appendChild(toast);
        
        setTimeout(() => toast.remove(), 2500);
    }
}

/**
 * Project Switcher
 * FEATURE-006 v2.0: Multi-Project Folder Support
 * 
 * Loads project folders from API and handles switching between projects.
 * When a project is switched, it refreshes the sidebar.
 */
class ProjectSwitcher {
    constructor(selectId, onSwitch) {
        this.select = document.getElementById(selectId);
        this.onSwitch = onSwitch;
        this.projects = [];
        this.activeProjectId = null;
        
        this.bindEvents();
        this.load();
    }
    
    bindEvents() {
        this.select.addEventListener('change', (e) => this.handleSwitch(e));
    }
    
    async load() {
        try {
            const response = await fetch('/api/projects');
            const data = await response.json();
            
            this.projects = data.projects;
            this.activeProjectId = data.active_project_id;
            this.render();
        } catch (error) {
            console.error('Failed to load projects:', error);
            this.select.innerHTML = '<option value="">Failed to load</option>';
        }
    }
    
    render() {
        if (this.projects.length === 0) {
            this.select.innerHTML = '<option value="">No projects</option>';
            return;
        }
        
        this.select.innerHTML = this.projects.map(project => {
            const isActive = project.id === this.activeProjectId;
            return `<option value="${project.id}" ${isActive ? 'selected' : ''}>
                ${isActive ? '✓ ' : ''}${this.escapeHtml(project.name)}
            </option>`;
        }).join('');
    }
    
    async handleSwitch(e) {
        const projectId = parseInt(e.target.value);
        if (!projectId || projectId === this.activeProjectId) return;
        
        try {
            const response = await fetch('/api/projects/switch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ project_id: projectId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.activeProjectId = data.active_project_id;
                this.render();
                
                // Show toast
                this.showToast(`Switched to ${data.project.name}`);
                
                // Callback to refresh sidebar
                if (this.onSwitch) {
                    this.onSwitch(data.project);
                }
            } else {
                console.error('Switch failed:', data.error);
                this.showToast('Failed to switch project', 'danger');
            }
        } catch (error) {
            console.error('Switch error:', error);
            this.showToast('Network error', 'danger');
        }
    }
    
    showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = type === 'success' ? 'refresh-toast' : 'refresh-toast bg-danger';
        toast.innerHTML = `<i class="bi bi-folder-check"></i> ${this.escapeHtml(message)}`;
        container.appendChild(toast);
        
        setTimeout(() => toast.remove(), 2500);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

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
        
        // Special handling for Workplace section - no expandable content
        if (section.id === 'workplace') {
            return `
                <div class="nav-section" data-section-id="${section.id}">
                    <div class="nav-section-header nav-workplace-header" data-section-id="${section.id}">
                        <i class="bi ${icon}"></i>
                        <span>${section.label}</span>
                    </div>
                </div>
            `;
        }
        
        let html = `
            <div class="nav-section" data-section-id="${section.id}">
                <div class="nav-section-header" data-bs-toggle="collapse" data-bs-target="#section-${section.id}">
                    <i class="bi ${icon}"></i>
                    <span>${section.label}</span>
                    <i class="bi bi-chevron-down chevron"></i>
                </div>
                <div class="collapse show nav-section-content" id="section-${section.id}">
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
     */
    renderChildren(children, depth = 0) {
        if (!children || children.length === 0) {
            return '';
        }
        
        let html = '';
        const indent = depth * 1; // rem
        
        for (const item of children) {
            if (item.type === 'folder') {
                html += this.renderFolder(item, depth);
            } else {
                html += this.renderFile(item, depth);
            }
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
                <div class="collapse show nav-folder-content" id="folder-${folderId}">
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
                // Remove active from all
                fileItems.forEach(f => f.classList.remove('active'));
                // Add active to clicked
                item.classList.add('active');
                
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
        
        // Workplace section click handler
        const workplaceHeader = this.container.querySelector('.nav-workplace-header');
        if (workplaceHeader) {
            workplaceHeader.addEventListener('click', () => {
                // Clear file selection
                fileItems.forEach(f => f.classList.remove('active'));
                this.selectedFile = null;
                
                // BUGFIX: Clear contentRenderer.currentPath to prevent auto-refresh
                // from redirecting back to previously viewed file when on Workplace
                if (window.contentRenderer) {
                    window.contentRenderer.currentPath = null;
                }
                
                // Update breadcrumb
                const breadcrumb = document.getElementById('breadcrumb');
                breadcrumb.innerHTML = '<li class="breadcrumb-item active">Workplace</li>';
                
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
        
        // Section header collapse tracking
        const sectionHeaders = this.container.querySelectorAll('.nav-section-header:not(.nav-workplace-header)');
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
