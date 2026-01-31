/**
 * TreeDragManager - Drag-drop file/folder reorganization
 * FEATURE-008 CR-006: Folder Tree UX Enhancement
 * 
 * Provides:
 * - Drag-and-drop to move files/folders
 * - Visual feedback (dragging state, valid/invalid targets)
 * - Validation (prevent drop into self/children)
 * - API integration for move operations
 */
class TreeDragManager {
    constructor(options) {
        this.treeContainer = options.treeContainer;
        this.onMove = options.onMove; // Callback: async (sourcePath, targetPath) => boolean
        this.onMoveComplete = options.onMoveComplete || null; // Called after successful move
        this.draggedItem = null;
        this.draggedPath = null;
        this.draggedType = null;
    }

    /**
     * Initialize drag-drop functionality
     */
    init() {
        this._bindEvents();
    }

    /**
     * Bind drag-drop event listeners using event delegation
     */
    _bindEvents() {
        // Use event delegation on tree container
        this.treeContainer.addEventListener('dragstart', this._onDragStart.bind(this));
        this.treeContainer.addEventListener('dragend', this._onDragEnd.bind(this));
        this.treeContainer.addEventListener('dragover', this._onDragOver.bind(this));
        this.treeContainer.addEventListener('dragleave', this._onDragLeave.bind(this));
        this.treeContainer.addEventListener('drop', this._onDrop.bind(this));
    }

    /**
     * Make an item draggable
     * @param {HTMLElement} item - Tree item element
     */
    enableDrag(item) {
        item.setAttribute('draggable', 'true');
        item.dataset.draggable = 'true';
    }

    /**
     * Handle drag start
     */
    _onDragStart(e) {
        const item = e.target.closest('.tree-item[data-draggable="true"]');
        if (!item) return;

        this.draggedItem = item;
        this.draggedPath = item.dataset.path;
        this.draggedType = item.dataset.type;

        // Set drag data
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', this.draggedPath);

        // Add dragging class after a small delay (to allow drag image to be captured)
        setTimeout(() => {
            item.classList.add('dragging');
        }, 0);
    }

    /**
     * Handle drag end
     */
    _onDragEnd(e) {
        if (this.draggedItem) {
            this.draggedItem.classList.remove('dragging');
        }
        
        // Clear all drag states
        this.treeContainer.querySelectorAll('.drag-over, .drag-invalid').forEach(el => {
            el.classList.remove('drag-over', 'drag-invalid');
        });

        this.draggedItem = null;
        this.draggedPath = null;
        this.draggedType = null;
    }

    /**
     * Handle drag over
     */
    _onDragOver(e) {
        e.preventDefault();
        
        if (!this.draggedItem) return;

        const target = e.target.closest('.tree-item[data-type="folder"]');
        if (!target || target === this.draggedItem) {
            e.dataTransfer.dropEffect = 'none';
            return;
        }

        const targetPath = target.dataset.path;
        
        if (this._isValidDrop(targetPath)) {
            e.dataTransfer.dropEffect = 'move';
            target.classList.add('drag-over');
            target.classList.remove('drag-invalid');
        } else {
            e.dataTransfer.dropEffect = 'none';
            target.classList.add('drag-invalid');
            target.classList.remove('drag-over');
        }
    }

    /**
     * Handle drag leave
     */
    _onDragLeave(e) {
        const target = e.target.closest('.tree-item');
        if (target) {
            // Only remove if we're actually leaving (not entering a child)
            const relatedTarget = e.relatedTarget;
            if (!target.contains(relatedTarget)) {
                target.classList.remove('drag-over', 'drag-invalid');
            }
        }
    }

    /**
     * Handle drop
     */
    async _onDrop(e) {
        e.preventDefault();
        
        const target = e.target.closest('.tree-item[data-type="folder"]');
        
        if (!target || !this.draggedItem) {
            return;
        }

        const targetPath = target.dataset.path;
        
        // Clear visual states
        target.classList.remove('drag-over', 'drag-invalid');

        if (!this._isValidDrop(targetPath)) {
            this._showInvalidFeedback(target);
            return;
        }

        // Perform the move
        const sourcePath = this.draggedPath;
        
        try {
            // Show loading state
            this.draggedItem.classList.add('moving');
            
            if (this.onMove) {
                const success = await this.onMove(sourcePath, targetPath);
                
                if (success && this.onMoveComplete) {
                    this.onMoveComplete(sourcePath, targetPath);
                }
            }
        } catch (error) {
            console.error('Move failed:', error);
            this._showInvalidFeedback(this.draggedItem);
        } finally {
            if (this.draggedItem) {
                this.draggedItem.classList.remove('moving');
            }
        }
    }

    /**
     * Check if drop is valid
     * @param {string} targetPath - Target folder path
     * @returns {boolean}
     */
    _isValidDrop(targetPath) {
        if (!this.draggedPath) return false;
        
        // Cannot drop onto self
        if (this.draggedPath === targetPath) return false;
        
        // Cannot drop folder into its own child
        if (this.draggedType === 'folder') {
            if (targetPath.startsWith(this.draggedPath + '/')) {
                return false;
            }
        }
        
        return true;
    }

    /**
     * Show invalid drop feedback (shake animation)
     * @param {HTMLElement} target - Target element
     */
    _showInvalidFeedback(target) {
        if (!target) return;
        
        target.classList.add('drag-invalid');
        target.style.animation = 'shake 0.3s ease';
        
        setTimeout(() => {
            target.classList.remove('drag-invalid');
            target.style.animation = '';
        }, 300);
    }

    /**
     * Destroy the drag manager
     */
    destroy() {
        this.treeContainer.removeEventListener('dragstart', this._onDragStart);
        this.treeContainer.removeEventListener('dragend', this._onDragEnd);
        this.treeContainer.removeEventListener('dragover', this._onDragOver);
        this.treeContainer.removeEventListener('dragleave', this._onDragLeave);
        this.treeContainer.removeEventListener('drop', this._onDrop);
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TreeDragManager;
}
