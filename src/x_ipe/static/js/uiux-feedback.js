/**
 * FEATURE-022-A: Browser Simulator & Proxy
 * FEATURE-022-B: Element Inspector
 * 
 * UIUXFeedbackManager - Renders browser simulator in content area.
 * Handles URL input, proxy requests, viewport rendering, and element inspection.
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
        
        // Listen for messages from iframe
        window.addEventListener('message', this._handleInspectorMessage.bind(this));
    }
    
    /**
     * Render the browser simulator UI into the given container
     */
    render(container) {
        this.isActive = true;
        
        container.innerHTML = `
            <div class="uiux-container">
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
            inspectorTooltip: document.getElementById('inspector-tooltip')
        };
        
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
}

// Create global instance
window.uiuxFeedbackManager = new UIUXFeedbackManager();
