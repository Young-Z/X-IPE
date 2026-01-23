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
