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
                            <input type="text" id="url-input" class="url-input" placeholder="http://localhost:3000 or idea://folder/file.html" list="url-hints" />
                            <datalist id="url-hints">
                                <option value="idea://">
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
                        <div class="toolbar-divider"></div>
                        <button id="feedback-btn" class="toolbar-btn toolbar-btn-primary" title="Quick feedback with screenshot">
                            <i class="bi bi-chat-square-text"></i>
                            <span>Feedback</span>
                        </button>
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
                                    <small class="text-muted">Supported: localhost, 127.0.0.1, idea://</small>
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
                <aside class="feedback-panel collapsed" id="feedback-panel">
                    <div class="panel-collapse-tab" id="panel-collapse-tab">
                        <i class="bi bi-chat-square-text"></i>
                        <span class="tab-badge" id="tab-badge">0</span>
                        <i class="bi bi-chevron-left"></i>
                    </div>
                    <div class="panel-header" id="panel-header">
                        <div>
                            <div class="panel-title">
                                <i class="bi bi-chat-square-text"></i>
                                Feedback
                            </div>
                            <div class="panel-subtitle">Session feedback entries</div>
                        </div>
                        <div class="panel-header-right">
                            <span class="panel-badge" id="panel-badge">0</span>
                            <button class="panel-collapse-btn" id="panel-collapse-btn" title="Collapse panel">
                                <i class="bi bi-chevron-right"></i>
                            </button>
                        </div>
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
            feedbackBtn: document.getElementById('feedback-btn'),
            selectionCount: document.getElementById('selection-count'),
            inspectorHighlight: document.getElementById('inspector-highlight'),
            inspectorTooltip: document.getElementById('inspector-tooltip'),
            // FEATURE-022-C: Feedback panel elements
            feedbackPanel: document.getElementById('feedback-panel'),
            feedbackList: document.getElementById('feedback-list'),
            panelBadge: document.getElementById('panel-badge'),
            tabBadge: document.getElementById('tab-badge'),
            panelCollapseTab: document.getElementById('panel-collapse-tab'),
            panelCollapseBtn: document.getElementById('panel-collapse-btn'),
            panelHeader: document.getElementById('panel-header')
        };
        
        // Add context menu to DOM
        this._createContextMenu();
        
        this._bindEvents();
        this._bindPanelEvents();
        
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
        if (this.elements.feedbackBtn) {
            this.elements.feedbackBtn.addEventListener('click', () => this._quickFeedback());
        }
        
        // Clear selections when loading new URL
        if (this.elements.iframe) {
            this.elements.iframe.addEventListener('load', () => {
                this._clearSelections();
            });
        }
    }
    
    /**
     * Bind panel collapse/expand events
     */
    _bindPanelEvents() {
        // Click on collapsed tab to expand
        if (this.elements.panelCollapseTab) {
            this.elements.panelCollapseTab.addEventListener('click', (e) => {
                e.stopPropagation();
                this._expandPanel();
            });
        }
        
        // Click collapse button to collapse
        if (this.elements.panelCollapseBtn) {
            this.elements.panelCollapseBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this._collapsePanel();
            });
        }
        
        // Click header to collapse when expanded
        if (this.elements.panelHeader) {
            this.elements.panelHeader.addEventListener('click', (e) => {
                e.stopPropagation();
                if (!this.elements.feedbackPanel.classList.contains('collapsed')) {
                    this._collapsePanel();
                }
            });
        }
        
        // Click anywhere on collapsed panel to expand
        if (this.elements.feedbackPanel) {
            this.elements.feedbackPanel.addEventListener('click', (e) => {
                if (this.elements.feedbackPanel.classList.contains('collapsed')) {
                    e.stopPropagation();
                    this._expandPanel();
                } else {
                    // Prevent clicks inside expanded panel from collapsing
                    e.stopPropagation();
                }
            });
        }
        
        // Click outside panel to collapse
        document.addEventListener('click', (e) => {
            if (this.elements.feedbackPanel && 
                !this.elements.feedbackPanel.classList.contains('collapsed') &&
                !this.elements.feedbackPanel.contains(e.target)) {
                this._collapsePanel();
            }
        });
    }
    
    /**
     * Expand the feedback panel
     */
    _expandPanel() {
        if (this.elements.feedbackPanel) {
            this.elements.feedbackPanel.classList.remove('collapsed');
        }
    }
    
    /**
     * Collapse the feedback panel
     */
    _collapsePanel() {
        if (this.elements.feedbackPanel) {
            this.elements.feedbackPanel.classList.add('collapsed');
        }
    }
    
    /**
     * Validate URL format (client-side pre-validation)
     */
    validateUrl(url) {
        if (!url || !url.trim()) {
            return { valid: false, error: 'Please enter a URL' };
        }
        
        // Handle idea:// URLs (for x-ipe-docs/ideas files)
        if (url.startsWith('idea://')) {
            return { valid: true, url: url, isIdea: true };
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
            // Handle idea:// protocol - fetch from x-ipe-docs/ideas
            if (validation.isIdea) {
                await this._loadIdeaUrl(url);
                return;
            }
            
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
     * Load an idea:// URL from x-ipe-docs/ideas folder
     * @param {string} ideaUrl - URL in format idea://folder/file.html
     */
    async _loadIdeaUrl(ideaUrl) {
        try {
            // Parse idea:// URL to get path
            // idea://folder/file.html -> x-ipe-docs/ideas/folder/file.html
            const ideaPath = ideaUrl.replace('idea://', '');
            const filePath = `x-ipe-docs/ideas/${ideaPath}`;
            
            // Fetch file content with raw=true to get HTML directly
            const response = await fetch(`/api/file/content?path=${encodeURIComponent(filePath)}&raw=true`);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                this.showError(errorData.error || `Failed to load idea file: ${response.status}`);
                return;
            }
            
            let html = await response.text();
            
            // Inject inspector script for element inspection support
            html = this._injectInspectorScript(html);
            
            this.renderContent(html);
            this.state.currentUrl = ideaUrl;
            this.updateStatus(`Loaded: ${ideaUrl}`);
        } catch (e) {
            this.showError(`Failed to load idea: ${e.message}`);
        } finally {
            this.setLoading(false);
        }
    }
    
    /**
     * Inject inspector script into HTML for element inspection
     * @param {string} html - Raw HTML content
     * @returns {string} - HTML with inspector script injected
     */
    _injectInspectorScript(html) {
        // Inspector script for element hover, selection, and context menu
        const inspectorScript = `
<script data-x-ipe-inspector="true">
(function() {
    let inspectEnabled = false;
    
    window.addEventListener('message', function(e) {
        if (e.data && e.data.type === 'inspect-mode') {
            inspectEnabled = e.data.enabled;
        }
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!inspectEnabled) return;
        const el = document.elementFromPoint(e.clientX, e.clientY);
        if (!el || el === document.body || el === document.documentElement) {
            window.parent.postMessage({type: 'hover-leave'}, '*');
            return;
        }
        window.parent.postMessage({
            type: 'hover',
            element: {
                tag: el.tagName.toLowerCase(),
                className: (el.className || '').toString().split(' ')[0] || '',
                id: el.id || '',
                selector: generateSelector(el),
                rect: el.getBoundingClientRect()
            }
        }, '*');
    }, true);
    
    document.addEventListener('click', function(e) {
        if (!inspectEnabled) return;
        e.preventDefault();
        e.stopPropagation();
        const el = e.target;
        window.parent.postMessage({
            type: 'select',
            element: {
                tag: el.tagName.toLowerCase(),
                className: (el.className || '').toString().split(' ')[0] || '',
                id: el.id || '',
                selector: generateSelector(el),
                rect: el.getBoundingClientRect()
            },
            multiSelect: e.ctrlKey || e.metaKey
        }, '*');
    }, true);
    
    document.addEventListener('contextmenu', function(e) {
        if (!inspectEnabled) return;
        e.preventDefault();
        e.stopPropagation();
        window.parent.postMessage({
            type: 'contextmenu',
            x: e.screenX,
            y: e.screenY,
            clientX: e.clientX,
            clientY: e.clientY
        }, '*');
    }, true);
    
    function generateSelector(el) {
        if (el.id) return '#' + el.id;
        const tag = el.tagName.toLowerCase();
        const cls = (el.className || '').toString().split(' ')[0];
        if (cls) {
            const siblings = el.parentElement ? el.parentElement.querySelectorAll(tag + '.' + cls) : [];
            if (siblings.length === 1) return tag + '.' + cls;
            const idx = Array.from(siblings).indexOf(el);
            return tag + '.' + cls + ':nth-of-type(' + (idx + 1) + ')';
        }
        const siblings = el.parentElement ? el.parentElement.children : [];
        const idx = Array.from(siblings).indexOf(el);
        return tag + ':nth-child(' + (idx + 1) + ')';
    }
})();
</script>`;

        // Check if inspector script already present
        if (html.includes('data-x-ipe-inspector')) {
            return html;
        }
        
        // Inject before </body> if present, otherwise append
        if (html.includes('</body>')) {
            return html.replace('</body>', inspectorScript + '</body>');
        } else {
            return html + inspectorScript;
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
        if (!this.isActive) return;
        
        const { type, element, multiSelect, x, y, clientX, clientY } = event.data || {};
        
        // Context menu works even when inspector is disabled (if elements are already selected)
        if (type === 'contextmenu') {
            console.log('[UIUXFeedback] contextmenu message received', { clientX, clientY, selectedCount: this.inspector.selectedElements.length });
            if (this.inspector.selectedElements.length > 0) {
                const iframe = this.elements.iframe;
                if (iframe) {
                    const iframeRect = iframe.getBoundingClientRect();
                    const menuX = iframeRect.left + clientX;
                    const menuY = iframeRect.top + clientY;
                    console.log('[UIUXFeedback] showing context menu at', { menuX, menuY });
                    this._showContextMenu(menuX, menuY);
                }
            }
            return;
        }
        
        // Other messages require inspector to be enabled
        if (!this.inspector.enabled) return;
        
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
            // Format: <tag.class> or <tag> with dimensions
            const tagText = element.className 
                ? `<${element.tag}.${element.className}>`
                : `<${element.tag}>`;
            const width = Math.round(element.rect.width);
            const height = Math.round(element.rect.height);
            
            tooltip.textContent = `${tagText} ${width} × ${height}`;
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
        if (!menu) {
            console.error('[UIUXFeedback] Context menu element not found!');
            return;
        }
        
        console.log('[UIUXFeedback] _showContextMenu called', { x, y, menu });
        
        // Position menu ensuring it stays on screen
        const maxX = window.innerWidth - 200;  // menu width
        const maxY = window.innerHeight - 150; // menu height
        
        menu.style.left = `${Math.min(x, maxX)}px`;
        menu.style.top = `${Math.min(y, maxY)}px`;
        menu.style.display = 'block';
        this.contextMenu.visible = true;
        
        console.log('[UIUXFeedback] Menu display set to block');
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
                // Capture screenshot also creates a feedback entry
                this._createFeedbackEntry();
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
            this.updateStatus('No elements selected');
            return null;
        }
        
        try {
            // Check if html2canvas is available
            if (typeof html2canvas === 'undefined') {
                throw new Error('html2canvas library not loaded');
            }
            
            // Get iframe and its content document
            const iframe = this.elements.iframe;
            if (!iframe || !iframe.contentDocument || !iframe.contentDocument.body) {
                throw new Error('Cannot access iframe content');
            }
            
            console.log('[UIUXFeedback] Capturing iframe content screenshot...');
            
            // Capture the entire iframe body
            const canvas = await html2canvas(iframe.contentDocument.body, {
                useCORS: true,
                allowTaint: true,
                logging: false,
                backgroundColor: '#ffffff',
                width: iframe.contentDocument.body.scrollWidth,
                height: iframe.contentDocument.body.scrollHeight
            });
            
            const dataUrl = canvas.toDataURL('image/png');
            console.log('[UIUXFeedback] Screenshot captured, length:', dataUrl.length);
            
            if (dataUrl && dataUrl.length > 1000) {
                this.updateStatus('Screenshot captured');
                return dataUrl;
            } else {
                console.warn('[UIUXFeedback] Screenshot appears empty');
                return null;
            }
            
        } catch (error) {
            console.error('Screenshot capture failed:', error);
            this.updateStatus('Screenshot unavailable');
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
     * Get element with parent context (up to 4 levels)
     * Returns an object with selector and parent chain
     */
    _getElementWithContext(selector) {
        const iframe = this.elements.iframe;
        if (!iframe || !iframe.contentDocument) return { selector, parents: [] };
        
        try {
            const el = iframe.contentDocument.querySelector(selector);
            if (!el) return { selector, parents: [] };
            
            const parents = [];
            let current = el.parentElement;
            let level = 0;
            
            while (current && level < 4 && current !== iframe.contentDocument.body) {
                const parentSelector = this._generateSelector(current);
                if (parentSelector) {
                    parents.push(parentSelector);
                }
                current = current.parentElement;
                level++;
            }
            
            return { selector, parents };
        } catch (e) {
            return { selector, parents: [] };
        }
    }
    
    /**
     * Generate a readable selector for an element
     */
    _generateSelector(el) {
        if (!el || el.nodeType !== 1) return null;
        
        let selector = el.tagName.toLowerCase();
        
        if (el.id) {
            selector += `#${el.id}`;
        } else if (el.className && typeof el.className === 'string') {
            const classes = el.className.trim().split(/\s+/).filter(c => c).slice(0, 2);
            if (classes.length > 0) {
                selector += '.' + classes.join('.');
            }
        }
        
        return selector;
    }
    
    /**
     * Create a new feedback entry
     */
    async _createFeedbackEntry() {
        if (this.inspector.selectedElements.length === 0) {
            this.updateStatus('No elements selected');
            return;
        }
        
        try {
            // Generate unique ID and name
            const now = new Date();
            const id = `fb-${Date.now()}`;
            const name = `Feedback-${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}-${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}`;
            
            // Capture screenshot (may fail due to CORS, continue without it)
            let screenshot = null;
            try {
                screenshot = await this._captureScreenshot();
                console.log('[UIUXFeedback] Screenshot result:', screenshot ? `${screenshot.length} chars` : 'null');
            } catch (screenshotError) {
                console.warn('[UIUXFeedback] Screenshot capture failed:', screenshotError);
            }
            
            // Debug: log if screenshot will be shown
            if (screenshot) {
                console.log('[UIUXFeedback] Screenshot will be included in entry');
            } else {
                console.log('[UIUXFeedback] No screenshot to include');
            }
            
            // Get elements with parent context (4 levels)
            const elementsWithContext = this.inspector.selectedElements.map(sel => 
                this._getElementWithContext(sel)
            );
            
            // Create entry
            const entry = {
                id,
                name,
                url: this.state.currentUrl,
                elements: elementsWithContext,
                screenshot,
                description: '',
                createdAt: now.toISOString(),
                status: 'draft'
            };
            
            this.feedbackEntries.push(entry);
            this._renderFeedbackPanel();
            
            // Auto-expand panel when adding feedback
            this._expandPanel();
            
            // Expand the new entry
            this.expandedEntryId = id;
            this._updateExpandedEntry();
            
            this.updateStatus(`Feedback entry created: ${name}`);
        } catch (error) {
            console.error('[UIUXFeedback] Failed to create feedback entry:', error);
            this.updateStatus(`Failed to create feedback: ${error.message}`);
        }
    }
    
    /**
     * Quick feedback - captures full page screenshot without element selection
     */
    async _quickFeedback() {
        if (!this.state.currentUrl) {
            this.updateStatus('Load a page first');
            return;
        }
        
        try {
            // Generate unique ID and name
            const now = new Date();
            const id = `fb-${Date.now()}`;
            const name = `Feedback-${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}-${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}`;
            
            // Capture full page screenshot
            let screenshot = null;
            try {
                screenshot = await this._captureFullPageScreenshot();
                console.log('[UIUXFeedback] Full page screenshot result:', screenshot ? `${screenshot.length} chars` : 'null');
            } catch (screenshotError) {
                console.warn('[UIUXFeedback] Full page screenshot capture failed:', screenshotError);
            }
            
            // Create entry without element selection
            const entry = {
                id,
                name,
                url: this.state.currentUrl,
                elements: [],  // No elements selected
                screenshot,
                description: '',
                createdAt: now.toISOString(),
                status: 'draft'
            };
            
            this.feedbackEntries.push(entry);
            this._renderFeedbackPanel();
            
            // Auto-expand panel when adding feedback
            this._expandPanel();
            
            // Expand the new entry
            this.expandedEntryId = id;
            this._updateExpandedEntry();
            
            this.updateStatus(`Quick feedback created: ${name}`);
        } catch (error) {
            console.error('[UIUXFeedback] Failed to create quick feedback:', error);
            this.updateStatus(`Failed to create feedback: ${error.message}`);
        }
    }
    
    /**
     * Capture full page screenshot (no element bounding box)
     */
    async _captureFullPageScreenshot() {
        const iframe = this.elements.iframe;
        if (!iframe || !iframe.contentDocument) {
            throw new Error('Cannot access iframe content');
        }
        
        // Check if html2canvas is available
        if (typeof html2canvas === 'undefined') {
            throw new Error('html2canvas library not loaded');
        }
        
        // Capture the entire iframe content
        const canvas = await html2canvas(iframe.contentDocument.body, {
            useCORS: true,
            allowTaint: true,
            logging: false,
            backgroundColor: '#ffffff'
        });
        
        return canvas.toDataURL('image/png');
    }
    
    /**
     * Render the feedback panel
     */
    _renderFeedbackPanel() {
        const list = this.elements.feedbackList;
        const badge = this.elements.panelBadge;
        const tabBadge = this.elements.tabBadge;
        
        if (!list) return;
        
        // Update badge counts
        const count = this.feedbackEntries.length;
        if (badge) {
            badge.textContent = count;
        }
        if (tabBadge) {
            tabBadge.textContent = count;
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
        
        // Status styling
        const statusClass = `status-${entry.status}`;
        const statusIcon = {
            'draft': 'bi-pencil',
            'submitting': 'bi-arrow-repeat spin',
            'submitted': 'bi-check-circle-fill',
            'failed': 'bi-exclamation-circle-fill'
        }[entry.status] || 'bi-pencil';
        
        const statusText = {
            'draft': 'Draft',
            'submitting': 'Submitting...',
            'submitted': 'Submitted',
            'failed': 'Failed'
        }[entry.status] || 'Draft';
        
        // Disable submit button if not draft or failed
        const canSubmit = entry.status === 'draft' || entry.status === 'failed';
        
        return `
            <div class="feedback-entry ${isExpanded ? 'expanded' : ''} ${statusClass}" data-entry-id="${entry.id}">
                <div class="feedback-entry-header">
                    <div class="entry-info">
                        <i class="bi bi-chevron-${isExpanded ? 'down' : 'right'} entry-chevron"></i>
                        <span class="entry-name">${entry.name}</span>
                        <span class="entry-status"><i class="bi ${statusIcon}"></i> ${statusText}</span>
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
                            ${entry.elements.map(el => {
                                // Handle both old format (string) and new format (object with parents)
                                if (typeof el === 'string') {
                                    return `<li><code>${el}</code></li>`;
                                }
                                const parentChain = el.parents && el.parents.length > 0 
                                    ? `<span class="parent-chain">${el.parents.reverse().join(' > ')} > </span>` 
                                    : '';
                                return `<li>${parentChain}<code class="selected-el">${el.selector}</code></li>`;
                            }).join('')}
                        </ul>
                    </div>
                    <div class="entry-description">
                        <label>Description:</label>
                        <textarea class="entry-description-input" placeholder="Describe the feedback...">${entry.description}</textarea>
                    </div>
                    ${entry.status === 'failed' && entry.error ? `
                        <div class="entry-error">
                            <i class="bi bi-exclamation-triangle"></i>
                            ${entry.error}
                        </div>
                    ` : ''}
                    <div class="entry-actions-footer">
                        ${entry.status === 'submitted' && entry.folder ? `
                            <button class="btn-copilot" data-folder="${entry.folder}">
                                <i class="bi bi-robot"></i>
                                Copilot
                            </button>
                        ` : `
                            <button class="btn-submit" ${canSubmit ? '' : 'disabled'}>
                                <i class="bi bi-send"></i>
                                ${entry.status === 'submitting' ? 'Submitting...' : 'Submit'}
                            </button>
                        `}
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
            const submitBtn = entry.querySelector('.btn-submit');
            const copilotBtn = entry.querySelector('.btn-copilot');
            
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
            
            // Submit entry
            if (submitBtn) {
                submitBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this._submitEntry(id);
                });
            }
            
            // Copilot button - open terminal and type command
            if (copilotBtn) {
                copilotBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const folderPath = copilotBtn.dataset.folder;
                    this._openTerminalWithCommand(folderPath);
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
            this.updateStatus(`Deleted: ${name}`);
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
    
    // ========================================
    // FEATURE-022-D: Feedback Submission
    // ========================================
    
    /**
     * Submit feedback entry to backend
     */
    async _submitEntry(id) {
        const entry = this.feedbackEntries.find(e => e.id === id);
        if (!entry) return;
        
        // Update status
        entry.status = 'submitting';
        this._renderFeedbackPanel();
        
        try {
            const response = await fetch('/api/uiux-feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: entry.name,
                    url: entry.url,
                    elements: entry.elements,
                    screenshot: entry.screenshot,
                    description: entry.description
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                entry.status = 'submitted';
                entry.folder = result.folder;
                this._showToast('Feedback saved successfully', 'success');
                this._clearSelections();
                // Note: Copilot button now shown in entry footer instead of auto-typing
            } else {
                entry.status = 'failed';
                entry.error = result.error;
                this._showToast(`Failed to save: ${result.error}`, 'error');
            }
        } catch (error) {
            entry.status = 'failed';
            entry.error = error.message;
            this._showToast(`Network error: ${error.message}`, 'error');
        }
        
        this._renderFeedbackPanel();
    }
    
    /**
     * Open terminal, start copilot, and type command (without executing)
     */
    _openTerminalWithCommand(folderPath) {
        const command = `Get uiux feedback, please visit feedback folder ${folderPath} to get details.`;
        
        // Expand terminal panel first
        if (window.terminalPanel) {
            window.terminalPanel.expand();
        }
        
        // Use terminalManager's sendCopilotPromptCommandNoEnter which:
        // 1. Creates terminal if needed
        // 2. Types 'copilot' and presses Enter
        // 3. Waits for Copilot CLI to be ready
        // 4. Types the command WITHOUT pressing Enter (user can review/edit)
        if (window.terminalManager && window.terminalManager.sendCopilotPromptCommandNoEnter) {
            window.terminalManager.sendCopilotPromptCommandNoEnter(command);
        } else {
            console.warn('Terminal manager not available');
        }
    }

    /**
     * Show toast notification
     */
    _showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'x-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        document.body.appendChild(toast);
        
        // Animate in
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Create global instance
window.uiuxFeedbackManager = new UIUXFeedbackManager();
