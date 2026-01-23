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
