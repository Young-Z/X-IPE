/**
 * ConfirmDialog - Reusable confirmation modal
 * FEATURE-008 CR-006: Folder Tree UX Enhancement
 * 
 * Usage:
 *   const dialog = new ConfirmDialog();
 *   const confirmed = await dialog.show({
 *       title: 'Delete Item',
 *       message: 'Are you sure you want to delete this item?',
 *       confirmText: 'Delete',
 *       confirmClass: 'btn-danger',
 *       cancelText: 'Cancel'
 *   });
 */
class ConfirmDialog {
    constructor() {
        this._createModal();
    }

    /**
     * Create the modal DOM structure
     */
    _createModal() {
        // Check if modal already exists
        if (document.getElementById('confirm-dialog-modal')) {
            this.modal = document.getElementById('confirm-dialog-modal');
            return;
        }

        const modalHtml = `
            <div class="confirm-dialog-overlay" id="confirm-dialog-modal">
                <div class="confirm-dialog">
                    <header class="confirm-dialog-header">
                        <h4 class="confirm-dialog-title">Confirm</h4>
                    </header>
                    <div class="confirm-dialog-body">
                        <p class="confirm-dialog-message"></p>
                        <div class="confirm-dialog-details"></div>
                    </div>
                    <footer class="confirm-dialog-footer">
                        <button class="confirm-dialog-btn cancel-btn">Cancel</button>
                        <button class="confirm-dialog-btn confirm-btn">Confirm</button>
                    </footer>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        this.modal = document.getElementById('confirm-dialog-modal');
    }

    /**
     * Show the confirmation dialog
     * @param {Object} options - Dialog options
     * @param {string} options.title - Dialog title
     * @param {string} options.message - Main message
     * @param {string} options.details - Additional details (optional)
     * @param {string} options.confirmText - Confirm button text (default: 'Confirm')
     * @param {string} options.confirmClass - Confirm button class (default: 'primary')
     * @param {string} options.cancelText - Cancel button text (default: 'Cancel')
     * @returns {Promise<boolean>} - True if confirmed, false if cancelled
     */
    show(options = {}) {
        return new Promise((resolve) => {
            const {
                title = 'Confirm',
                message = 'Are you sure?',
                details = '',
                confirmText = 'Confirm',
                confirmClass = 'primary',
                cancelText = 'Cancel'
            } = options;

            // Update content
            this.modal.querySelector('.confirm-dialog-title').textContent = title;
            this.modal.querySelector('.confirm-dialog-message').textContent = message;
            
            const detailsEl = this.modal.querySelector('.confirm-dialog-details');
            if (details) {
                detailsEl.innerHTML = details;
                detailsEl.style.display = 'block';
            } else {
                detailsEl.style.display = 'none';
            }

            const confirmBtn = this.modal.querySelector('.confirm-btn');
            confirmBtn.textContent = confirmText;
            confirmBtn.className = `confirm-dialog-btn confirm-btn ${confirmClass}`;

            this.modal.querySelector('.cancel-btn').textContent = cancelText;

            // Show modal
            this.modal.classList.add('visible');

            // Handle button clicks
            const handleConfirm = () => {
                cleanup();
                resolve(true);
            };

            const handleCancel = () => {
                cleanup();
                resolve(false);
            };

            const handleKeydown = (e) => {
                if (e.key === 'Escape') {
                    handleCancel();
                } else if (e.key === 'Enter') {
                    handleConfirm();
                }
            };

            const handleOverlayClick = (e) => {
                if (e.target === this.modal) {
                    handleCancel();
                }
            };

            const cleanup = () => {
                this.modal.classList.remove('visible');
                confirmBtn.removeEventListener('click', handleConfirm);
                this.modal.querySelector('.cancel-btn').removeEventListener('click', handleCancel);
                document.removeEventListener('keydown', handleKeydown);
                this.modal.removeEventListener('click', handleOverlayClick);
            };

            confirmBtn.addEventListener('click', handleConfirm);
            this.modal.querySelector('.cancel-btn').addEventListener('click', handleCancel);
            document.addEventListener('keydown', handleKeydown);
            this.modal.addEventListener('click', handleOverlayClick);

            // Focus confirm button for keyboard accessibility
            setTimeout(() => confirmBtn.focus(), 100);
        });
    }

    /**
     * Convenience method for delete confirmation
     * @param {string} itemName - Name of item to delete
     * @param {string} itemType - Type of item ('file' or 'folder')
     * @param {number} itemCount - Number of items (for folders)
     * @returns {Promise<boolean>}
     */
    confirmDelete(itemName, itemType = 'file', itemCount = 1) {
        const isFolder = itemType === 'folder';
        let details = '';
        
        if (isFolder && itemCount > 0) {
            details = `<p class="confirm-dialog-warning">
                <i class="bi bi-exclamation-triangle"></i>
                This folder contains ${itemCount} item${itemCount !== 1 ? 's' : ''} that will also be deleted.
            </p>`;
        }

        return this.show({
            title: `Delete ${isFolder ? 'Folder' : 'File'}`,
            message: `Are you sure you want to delete "${itemName}"?`,
            details,
            confirmText: 'Delete',
            confirmClass: 'danger'
        });
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ConfirmDialog;
}
