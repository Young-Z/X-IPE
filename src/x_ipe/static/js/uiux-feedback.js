/**
 * FEATURE-022-A: Browser Simulator & Proxy
 * FEATURE-022-B: Element Inspector
 * FEATURE-022-C: Feedback Capture & Panel
 * 
 * UIUXFeedbackManager - Renders browser simulator in content area.
 * Handles URL input, proxy requests, viewport rendering, element inspection,
 * and feedback capture with context menu and panel.
 */

class UIUXFeedbackManager {
    constructor() {
        this.state = {
            currentUrl: null,
            isLoading: false,
            error: null
        };
        this.elements = {};
        this.isActive = false;
        
        // FEATURE-022-B: Inspector state
        this.inspector = {
            enabled: false,
            hoverElement: null,
            selectedElements: []  // CSS selectors
        };
        
        // FEATURE-022-C: Feedback state
        this.feedbackEntries = [];
        this.expandedEntryId = null;
        this.contextMenu = {
            visible: false
        };
        
        // Listen for messages from iframe
        window.addEventListener('message', this._handleInspectorMessage.bind(this));
        
        // Close context menu on click outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.context-menu')) {
                this._hideContextMenu();
            }
        });
        
        // Close context menu on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this._hideContextMenu();
            }
        });
    }
    
    /**
     * Render the browser simulator UI into the given container
     */
    render(container) {
        this.isActive = true;
        
        container.innerHTML = `
            <div class="uiux-container">
                <!-- Browser Main Area -->
                <div class="browser-main">
                    <!-- Browser Chrome -->
                    <div class="browser-chrome">
                        <div class="browser-dots">
                            <span class="browser-dot red"></span>
                            <span class="browser-dot yellow"></span>
                            <span class="browser-dot green"></span>
                        </div>
                        <div class="url-bar">
                            <input type="text" id="url-input" class="url-input" placeholder="http://localhost:3000" list="url-hints" />
                            <datalist id="url-hints">
                                <option value="http://localhost:3000">
                                <option value="http://localhost:5173">
                                <option value="http://localhost:8080">
                                <option value="http://127.0.0.1:5000">
                            </datalist>
                            <button id="go-btn" class="go-btn">Go</button>
                        </div>
                    </div>

                    <!-- FEATURE-022-B: Toolbar -->
                    <div class="browser-toolbar" id="browser-toolbar">
                        <button id="refresh-btn" class="toolbar-btn" title="Refresh page">
                            <i class="bi bi-arrow-clockwise"></i>
                            <span>Refresh</span>
                        </button>
                        <div class="toolbar-divider"></div>
                        <button id="inspect-btn" class="toolbar-btn" title="Toggle element inspector">
                            <i class="bi bi-crosshair"></i>
                            <span>Inspect</span>
                        </button>
                        <span id="selection-count" class="toolbar-info"></span>
                    </div>

                    <!-- Browser Viewport -->
                    <div class="browser-viewport-container">
                        <div class="browser-viewport" id="browser-viewport">
                            <!-- Iframe for proxied content -->
                            <iframe id="viewport-iframe" class="viewport-iframe"></iframe>
                            
                            <!-- FEATURE-022-B: Highlight overlay (positioned over iframe) -->
                            <div id="inspector-highlight" class="inspector-highlight" style="display: none;"></div>
                            <div id="inspector-tooltip" class="inspector-tooltip" style="display: none;"></div>
                            
                            <!-- Empty State -->
                            <div class="empty-state" id="empty-state">
                                <div class="empty-state-icon">
                                    <i class="bi bi-globe2"></i>
                                </div>
                                <div class="empty-state-title">Browser Simulator</div>
                                <div class="empty-state-description">
                                    Enter a localhost URL above to preview your application.
                                    <br><br>
                                    <small class="text-muted">Supported: localhost, 127.0.0.1</small>
                                </div>
                            </div>
                            
                            <!-- Loading Overlay -->
                            <div class="loading-overlay" id="loading-overlay">
                                <div class="loading-spinner"></div>
                                <div class="loading-text">Loading page...</div>
                            </div>
                            
                            <!-- Error Overlay -->
                            <div class="error-overlay" id="error-overlay">
                                <div class="error-icon">
                                    <i class="bi bi-exclamation-triangle-fill"></i>
                                </div>
                                <div class="error-message" id="error-message">Connection failed</div>
                                <div class="error-hint">Click to dismiss</div>
                            </div>
                        </div>
                    </div>

                    <!-- Status Bar -->
                    <div class="browser-status">
                        <div class="status-indicator"></div>
                        <div class="status-text" id="status-text">Ready - Enter a localhost URL to begin</div>
                    </div>
                </div>

                <!-- FEATURE-022-C: Feedback Panel -->
                <aside class="feedback-panel" id="feedback-panel">
                    <div class="panel-header">
                        <div>
                            <div class="panel-title">
                                <i class="bi bi-chat-square-text"></i>
                                Feedback
                            </div>
                            <div class="panel-subtitle">Session feedback entries</div>
                        </div>
                        <span class="panel-badge" id="panel-badge">0</span>
                    </div>
                    <div class="feedback-list" id="feedback-list">
                        <div class="empty-feedback">
                            <i class="bi bi-chat-square-text"></i>
                            <p>No feedback yet</p>
                            <small>Right-click on selected elements to add feedback</small>
                        </div>
                    </div>
                </aside>
            </div>
        `;
        
        // Cache element references
        this.elements = {
            urlInput: document.getElementById('url-input'),
            goBtn: document.getElementById('go-btn'),
            viewport: document.getElementById('browser-viewport'),
            iframe: document.getElementById('viewport-iframe'),
            loadingOverlay: document.getElementById('loading-overlay'),
            errorOverlay: document.getElementById('error-overlay'),
            errorMessage: document.getElementById('error-message'),
            statusText: document.getElementById('status-text'),
            emptyState: document.getElementById('empty-state'),
            // FEATURE-022-B: Inspector elements
            toolbar: document.getElementById('browser-toolbar'),
            refreshBtn: document.getElementById('refresh-btn'),
            inspectBtn: document.getElementById('inspect-btn'),
            selectionCount: document.getElementById('selection-count'),
            inspectorHighlight: document.getElementById('inspector-highlight'),
            inspectorTooltip: document.getElementById('inspector-tooltip'),
            // FEATURE-022-C: Feedback panel elements
            feedbackPanel: document.getElementById('feedback-panel'),
            feedbackList: document.getElementById('feedback-list'),
            panelBadge: document.getElementById('panel-badge')
        };
        
        // Add context menu to DOM
        this._createContextMenu();
        
        this._bindEvents();
        
        // Restore previous URL if exists
        if (this.state.currentUrl) {
            this.elements.urlInput.value = this.state.currentUrl;
        }
    }
    
    /**
     * Bind event listeners
     */
    _bindEvents() {
        // Go button click
        this.elements.goBtn.addEventListener('click', () => this.loadUrl());
        
        // Enter key in URL input
        this.elements.urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.loadUrl();
            }
        });
        
        // Dismiss error on click
        if (this.elements.errorOverlay) {
            this.elements.errorOverlay.addEventListener('click', () => {
                this.hideError();
            });
        }
        
        // FEATURE-022-B: Toolbar buttons
        if (this.elements.refreshBtn) {
            this.elements.refreshBtn.addEventListener('click', () => this.refresh());
        }
        if (this.elements.inspectBtn) {
            this.elements.inspectBtn.addEventListener('click', () => this.toggleInspect());
        }
        
        // Clear selections when loading new URL
        if (this.elements.iframe) {
            this.elements.iframe.addEventListener('load', () => {
                this._clearSelections();
            });
        }
    }
    
    /**
     * Validate URL format (client-side pre-validation)
     */
    validateUrl(url) {
        if (!url || !url.trim()) {
            return { valid: false, error: 'Please enter a URL' };
        }
        
        // Handle file:// URLs
        if (url.startsWith('file://')) {
            return { valid: true, url: url };
        }
        
        // Add protocol if missing (for http/https)
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            url = 'http://' + url;
        }
        
        try {
            const parsed = new URL(url);
            
            // Only allow localhost for http/https
            if (parsed.hostname !== 'localhost' && parsed.hostname !== '127.0.0.1') {
                return { valid: false, error: 'Only localhost URLs are supported in this version' };
            }
            
            return { valid: true, url: url };
        } catch (e) {
            return { valid: false, error: 'Invalid URL format' };
        }
    }
    
    /**
     * Load a URL through the proxy
     */
    async loadUrl() {
        const rawUrl = this.elements.urlInput.value.trim();
        
        // Validate
        const validation = this.validateUrl(rawUrl);
        if (!validation.valid) {
            this.showError(validation.error);
            return;
        }
        
        const url = validation.url;
        this.elements.urlInput.value = url; // Update with normalized URL
        
        this.setLoading(true);
        this.hideError();
        
        try {
            const encodedUrl = encodeURIComponent(url);
            const response = await fetch(`/api/proxy?url=${encodedUrl}`);
            const contentType = response.headers.get('Content-Type') || '';
            
            // Check if response is JSON (HTML proxied content) or raw content
            if (contentType.includes('application/json')) {
                const data = await response.json();
                
                if (data.success) {
                    this.renderContent(data.html);
                    this.state.currentUrl = url;
                    this.updateStatus(`Loaded: ${url}`);
                } else {
                    this.showError(data.error || 'Failed to load page');
                }
            } else {
                // Non-HTML content - wrap in basic HTML to display
                const text = await response.text();
                const wrappedHtml = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: monospace; white-space: pre-wrap; padding: 20px; margin: 0; background: #f5f5f5; }
    </style>
</head>
<body>${this._escapeHtml(text)}</body>
</html>`;
                this.renderContent(wrappedHtml);
                this.state.currentUrl = url;
                this.updateStatus(`Loaded (raw): ${url}`);
            }
        } catch (e) {
            this.showError(`Network error: ${e.message}`);
        } finally {
            this.setLoading(false);
        }
    }
    
    /**
     * Escape HTML special characters
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Render HTML content in the viewport iframe
     */
    renderContent(html) {
        // Hide empty state
        if (this.elements.emptyState) {
            this.elements.emptyState.style.display = 'none';
        }
        
        if (this.elements.iframe) {
            this.elements.iframe.srcdoc = html;
        }
    }
    
    /**
     * Show/hide loading state
     */
    setLoading(isLoading) {
        this.state.isLoading = isLoading;
        
        if (this.elements.loadingOverlay) {
            this.elements.loadingOverlay.style.display = isLoading ? 'flex' : 'none';
        }
        
        if (this.elements.goBtn) {
            this.elements.goBtn.disabled = isLoading;
            this.elements.goBtn.textContent = isLoading ? 'Loading...' : 'Go';
        }
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.state.error = message;
        
        if (this.elements.errorOverlay && this.elements.errorMessage) {
            this.elements.errorMessage.textContent = message;
            this.elements.errorOverlay.style.display = 'flex';
        }
        
        this.updateStatus(`Error: ${message}`);
    }
    
    /**
     * Hide error overlay
     */
    hideError() {
        this.state.error = null;
        
        if (this.elements.errorOverlay) {
            this.elements.errorOverlay.style.display = 'none';
        }
    }
    
    /**
     * Update status text
     */
    updateStatus(text) {
        if (this.elements.statusText) {
            this.elements.statusText.textContent = text;
        }
    }
    
    /**
     * Deactivate the manager (called when switching to another view)
     */
    deactivate() {
        this.isActive = false;
        // Disable inspect mode when deactivating
        if (this.inspector.enabled) {
            this.toggleInspect();
        }
    }
    
    // =========================================
    // FEATURE-022-B: Element Inspector Methods
    // =========================================
    
    /**
     * Refresh the current page
     */
    refresh() {
        if (this.state.currentUrl) {
            this.loadUrl();
        }
    }
    
    /**
     * Toggle inspect mode
     */
    toggleInspect() {
        this.inspector.enabled = !this.inspector.enabled;
        this._updateInspectButton();
        
        // Send message to iframe
        const iframe = this.elements.iframe;
        if (iframe?.contentWindow) {
            iframe.contentWindow.postMessage({
                type: 'inspect-mode',
                enabled: this.inspector.enabled
            }, '*');
        }
        
        // Update status
        if (this.inspector.enabled) {
            this.updateStatus('Inspect mode ON - Hover over elements to highlight');
        } else {
            this.updateStatus('Inspect mode OFF');
            this._hideHighlight();
        }
    }
    
    /**
     * Update inspect button visual state
     */
    _updateInspectButton() {
        if (this.elements.inspectBtn) {
            if (this.inspector.enabled) {
                this.elements.inspectBtn.classList.add('active');
            } else {
                this.elements.inspectBtn.classList.remove('active');
            }
        }
    }
    
    /**
     * Handle messages from iframe inspector script
     */
    _handleInspectorMessage(event) {
        if (!this.isActive || !this.inspector.enabled) return;
        
        const { type, element, multiSelect } = event.data || {};
        
        switch (type) {
            case 'hover':
                this._showHoverHighlight(element);
                break;
            case 'hover-leave':
                this._hideHighlight();
                break;
            case 'select':
                this._handleElementSelect(element, multiSelect);
                break;
        }
    }
    
    /**
     * Show highlight overlay for hovered element
     */
    _showHoverHighlight(element) {
        if (!element || !element.rect) return;
        
        this.inspector.hoverElement = element;
        
        // Get iframe position to offset the highlight
        const iframe = this.elements.iframe;
        if (!iframe) return;
        
        const iframeRect = iframe.getBoundingClientRect();
        const viewportContainer = this.elements.viewport;
        if (!viewportContainer) return;
        
        const containerRect = viewportContainer.getBoundingClientRect();
        
        // Calculate position relative to viewport container
        const highlight = this.elements.inspectorHighlight;
        const tooltip = this.elements.inspectorTooltip;
        
        if (highlight) {
            // Check if this element is selected
            const isSelected = this.inspector.selectedElements.includes(element.selector);
            
            highlight.style.display = 'block';
            highlight.style.left = `${element.rect.x}px`;
            highlight.style.top = `${element.rect.y}px`;
            highlight.style.width = `${element.rect.width}px`;
            highlight.style.height = `${element.rect.height}px`;
            
            if (isSelected) {
                highlight.classList.add('selected');
            } else {
                highlight.classList.remove('selected');
            }
        }
        
        if (tooltip) {
            // Format: <tag.class> or <tag>
            const tagText = element.className 
                ? `<${element.tag}.${element.className}>`
                : `<${element.tag}>`;
            
            tooltip.textContent = tagText;
            tooltip.style.display = 'block';
            tooltip.style.left = `${element.rect.x}px`;
            tooltip.style.top = `${element.rect.y - 28}px`;
        }
    }
    
    /**
     * Hide highlight overlay
     */
    _hideHighlight() {
        this.inspector.hoverElement = null;
        
        if (this.elements.inspectorHighlight) {
            this.elements.inspectorHighlight.style.display = 'none';
        }
        if (this.elements.inspectorTooltip) {
            this.elements.inspectorTooltip.style.display = 'none';
        }
    }
    
    /**
     * Handle element selection (click)
     */
    _handleElementSelect(element, multiSelect) {
        if (!element || !element.selector) return;
        
        const selector = element.selector;
        const index = this.inspector.selectedElements.indexOf(selector);
        
        if (multiSelect) {
            // Multi-select: toggle this element
            if (index >= 0) {
                this.inspector.selectedElements.splice(index, 1);
            } else {
                this.inspector.selectedElements.push(selector);
            }
        } else {
            // Single select: replace selection
            if (index >= 0 && this.inspector.selectedElements.length === 1) {
                // Clicking same element again deselects
                this.inspector.selectedElements = [];
            } else {
                this.inspector.selectedElements = [selector];
            }
        }
        
        this._updateSelectionCount();
        this._updateHighlightState();
    }
    
    /**
     * Clear all selections
     */
    _clearSelections() {
        this.inspector.selectedElements = [];
        this._updateSelectionCount();
        this._hideHighlight();
    }
    
    /**
     * Update selection count display
     */
    _updateSelectionCount() {
        if (this.elements.selectionCount) {
            const count = this.inspector.selectedElements.length;
            if (count > 0) {
                this.elements.selectionCount.textContent = `${count} element${count !== 1 ? 's' : ''} selected`;
                this.elements.selectionCount.style.display = 'inline';
            } else {
                this.elements.selectionCount.style.display = 'none';
            }
        }
    }
    
    /**
     * Update highlight appearance based on selection state
     */
    _updateHighlightState() {
        const highlight = this.elements.inspectorHighlight;
        if (!highlight) return;
        
        const hoverElement = this.inspector.hoverElement;
        if (hoverElement) {
            const isSelected = this.inspector.selectedElements.includes(hoverElement.selector);
            if (isSelected) {
                highlight.classList.add('selected');
            } else {
                highlight.classList.remove('selected');
            }
        }
    }
    
    // ========================================
    // FEATURE-022-C: Feedback Capture & Panel
    // ========================================
    
    /**
     * Create context menu element
     */
    _createContextMenu() {
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.id = 'inspector-context-menu';
        menu.innerHTML = `
            <div class="context-menu-item" data-action="capture">
                <i class="bi bi-camera"></i>
                <span>Capture Screenshot</span>
            </div>
            <div class="context-menu-item" data-action="feedback">
                <i class="bi bi-chat-square-text"></i>
                <span>Add Feedback</span>
            </div>
            <div class="context-menu-divider"></div>
            <div class="context-menu-item" data-action="clear">
                <i class="bi bi-x-circle"></i>
                <span>Clear Selection</span>
            </div>
        `;
        
        document.body.appendChild(menu);
        this.elements.contextMenu = menu;
        
        // Bind context menu click
        menu.addEventListener('click', (e) => {
            const item = e.target.closest('.context-menu-item');
            if (!item) return;
            
            const action = item.dataset.action;
            this._handleContextMenuAction(action);
            this._hideContextMenu();
        });
        
        // Bind right-click on viewport to show context menu
        this.elements.viewport.addEventListener('contextmenu', (e) => {
            // Only show if inspector enabled and elements selected
            if (this.inspector.enabled && this.inspector.selectedElements.length > 0) {
                e.preventDefault();
                this._showContextMenu(e.clientX, e.clientY);
            }
        });
    }
    
    /**
     * Show context menu at position
     */
    _showContextMenu(x, y) {
        const menu = this.elements.contextMenu;
        if (!menu) return;
        
        // Position menu ensuring it stays on screen
        const menuRect = menu.getBoundingClientRect();
        const maxX = window.innerWidth - 200;  // menu width
        const maxY = window.innerHeight - 150; // menu height
        
        menu.style.left = `${Math.min(x, maxX)}px`;
        menu.style.top = `${Math.min(y, maxY)}px`;
        menu.style.display = 'block';
        this.contextMenu.visible = true;
    }
    
    /**
     * Hide context menu
     */
    _hideContextMenu() {
        const menu = this.elements.contextMenu;
        if (menu) {
            menu.style.display = 'none';
        }
        this.contextMenu.visible = false;
    }
    
    /**
     * Handle context menu action
     */
    _handleContextMenuAction(action) {
        switch (action) {
            case 'capture':
                this._captureScreenshot();
                break;
            case 'feedback':
                this._createFeedbackEntry();
                break;
            case 'clear':
                this._clearSelections();
                break;
        }
    }
    
    /**
     * Capture screenshot of selected elements
     */
    async _captureScreenshot() {
        if (this.inspector.selectedElements.length === 0) {
            this.setStatus('error', 'No elements selected');
            return null;
        }
        
        try {
            // Get iframe content document
            const iframe = this.elements.iframe;
            if (!iframe || !iframe.contentDocument) {
                throw new Error('Cannot access iframe content');
            }
            
            // Calculate combined bounding box of all selected elements
            const boundingBox = this._getCombinedBoundingBox();
            if (!boundingBox) {
                throw new Error('Cannot determine element bounds');
            }
            
            // Check if html2canvas is available
            if (typeof html2canvas === 'undefined') {
                throw new Error('html2canvas library not loaded');
            }
            
            // Capture the iframe content
            const canvas = await html2canvas(iframe.contentDocument.body, {
                x: boundingBox.x,
                y: boundingBox.y,
                width: boundingBox.width,
                height: boundingBox.height,
                useCORS: true,
                allowTaint: true,
                logging: false
            });
            
            const dataUrl = canvas.toDataURL('image/png');
            this.setStatus('success', 'Screenshot captured');
            return dataUrl;
            
        } catch (error) {
            console.error('Screenshot capture failed:', error);
            this.setStatus('error', `Screenshot failed: ${error.message}`);
            return null;
        }
    }
    
    /**
     * Get combined bounding box of all selected elements
     */
    _getCombinedBoundingBox() {
        const iframe = this.elements.iframe;
        if (!iframe || !iframe.contentDocument) return null;
        
        let minX = Infinity, minY = Infinity;
        let maxX = -Infinity, maxY = -Infinity;
        
        for (const selector of this.inspector.selectedElements) {
            try {
                const el = iframe.contentDocument.querySelector(selector);
                if (el) {
                    const rect = el.getBoundingClientRect();
                    minX = Math.min(minX, rect.left);
                    minY = Math.min(minY, rect.top);
                    maxX = Math.max(maxX, rect.right);
                    maxY = Math.max(maxY, rect.bottom);
                }
            } catch (e) {
                // Invalid selector, skip
            }
        }
        
        if (minX === Infinity) return null;
        
        // Add padding
        const padding = 10;
        return {
            x: Math.max(0, minX - padding),
            y: Math.max(0, minY - padding),
            width: (maxX - minX) + (padding * 2),
            height: (maxY - minY) + (padding * 2)
        };
    }
    
    /**
     * Create a new feedback entry
     */
    async _createFeedbackEntry() {
        if (this.inspector.selectedElements.length === 0) {
            this.setStatus('error', 'No elements selected');
            return;
        }
        
        // Generate unique ID and name
        const now = new Date();
        const id = `fb-${Date.now()}`;
        const name = `Feedback-${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}-${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}`;
        
        // Capture screenshot
        const screenshot = await this._captureScreenshot();
        
        // Create entry
        const entry = {
            id,
            name,
            url: this.state.currentUrl,
            elements: [...this.inspector.selectedElements],
            screenshot,
            description: '',
            createdAt: now.toISOString(),
            status: 'draft'
        };
        
        this.feedbackEntries.push(entry);
        this._renderFeedbackPanel();
        
        // Expand the new entry
        this.expandedEntryId = id;
        this._updateExpandedEntry();
        
        this.setStatus('success', `Feedback entry created: ${name}`);
    }
    
    /**
     * Render the feedback panel
     */
    _renderFeedbackPanel() {
        const list = this.elements.feedbackList;
        const badge = this.elements.panelBadge;
        
        if (!list) return;
        
        // Update badge count
        if (badge) {
            badge.textContent = this.feedbackEntries.length;
        }
        
        // Render empty state or entries
        if (this.feedbackEntries.length === 0) {
            list.innerHTML = `
                <div class="empty-feedback">
                    <i class="bi bi-chat-square-text"></i>
                    <p>No feedback yet</p>
                    <small>Right-click on selected elements to add feedback</small>
                </div>
            `;
            return;
        }
        
        // Render entries
        list.innerHTML = this.feedbackEntries.map(entry => this._renderEntry(entry)).join('');
        
        // Bind entry events
        this._bindEntryEvents();
    }
    
    /**
     * Render a single feedback entry
     */
    _renderEntry(entry) {
        const isExpanded = entry.id === this.expandedEntryId;
        const time = this._formatTime(entry.createdAt);
        
        return `
            <div class="feedback-entry ${isExpanded ? 'expanded' : ''}" data-entry-id="${entry.id}">
                <div class="feedback-entry-header">
                    <div class="entry-info">
                        <i class="bi bi-chevron-${isExpanded ? 'down' : 'right'} entry-chevron"></i>
                        <span class="entry-name">${entry.name}</span>
                    </div>
                    <div class="entry-actions">
                        <button class="entry-action-btn delete-entry" title="Delete">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="feedback-entry-body" style="display: ${isExpanded ? 'block' : 'none'}">
                    <div class="entry-meta">
                        <span class="entry-time"><i class="bi bi-clock"></i> ${time}</span>
                        <span class="entry-elements"><i class="bi bi-layers"></i> ${entry.elements.length} element${entry.elements.length !== 1 ? 's' : ''}</span>
                    </div>
                    ${entry.screenshot ? `
                        <div class="entry-screenshot">
                            <img src="${entry.screenshot}" alt="Screenshot" />
                        </div>
                    ` : ''}
                    <div class="entry-url">
                        <i class="bi bi-link-45deg"></i>
                        <span>${entry.url || 'No URL'}</span>
                    </div>
                    <div class="entry-selectors">
                        <strong>Elements:</strong>
                        <ul>
                            ${entry.elements.map(sel => `<li><code>${sel}</code></li>`).join('')}
                        </ul>
                    </div>
                    <div class="entry-description">
                        <label>Description:</label>
                        <textarea class="entry-description-input" placeholder="Describe the feedback...">${entry.description}</textarea>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Format timestamp to relative or absolute time
     */
    _formatTime(isoString) {
        const date = new Date(isoString);
        const now = new Date();
        const diff = now - date;
        
        // Less than 1 minute
        if (diff < 60000) {
            return 'Just now';
        }
        // Less than 1 hour
        if (diff < 3600000) {
            const mins = Math.floor(diff / 60000);
            return `${mins} min${mins !== 1 ? 's' : ''} ago`;
        }
        // Less than 24 hours
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
        }
        // Otherwise show date
        return date.toLocaleDateString();
    }
    
    /**
     * Bind events to feedback entries
     */
    _bindEntryEvents() {
        const entries = this.elements.feedbackList.querySelectorAll('.feedback-entry');
        
        entries.forEach(entry => {
            const id = entry.dataset.entryId;
            const header = entry.querySelector('.feedback-entry-header');
            const deleteBtn = entry.querySelector('.delete-entry');
            const descInput = entry.querySelector('.entry-description-input');
            
            // Toggle expand on header click
            header.addEventListener('click', (e) => {
                if (!e.target.closest('.entry-action-btn')) {
                    this._toggleEntry(id);
                }
            });
            
            // Delete entry
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this._deleteEntry(id);
            });
            
            // Save description on blur
            if (descInput) {
                descInput.addEventListener('blur', () => {
                    this._updateEntryDescription(id, descInput.value);
                });
            }
        });
    }
    
    /**
     * Toggle entry expansion
     */
    _toggleEntry(id) {
        if (this.expandedEntryId === id) {
            this.expandedEntryId = null;
        } else {
            this.expandedEntryId = id;
        }
        this._renderFeedbackPanel();
    }
    
    /**
     * Update expanded entry without re-rendering all
     */
    _updateExpandedEntry() {
        this._renderFeedbackPanel();
    }
    
    /**
     * Delete a feedback entry
     */
    _deleteEntry(id) {
        const index = this.feedbackEntries.findIndex(e => e.id === id);
        if (index >= 0) {
            const name = this.feedbackEntries[index].name;
            this.feedbackEntries.splice(index, 1);
            this._renderFeedbackPanel();
            this.setStatus('info', `Deleted: ${name}`);
        }
    }
    
    /**
     * Update entry description
     */
    _updateEntryDescription(id, description) {
        const entry = this.feedbackEntries.find(e => e.id === id);
        if (entry) {
            entry.description = description;
        }
    }
    
    /**
     * Get all feedback entries (for export)
     */
    getFeedbackEntries() {
        return this.feedbackEntries;
    }
}

// Create global instance
window.uiuxFeedbackManager = new UIUXFeedbackManager();
