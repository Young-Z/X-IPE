/**
 * FEATURE-022-A: Browser Simulator & Proxy
 * 
 * UIUXFeedbackManager - Renders browser simulator in content area.
 * Handles URL input, proxy requests, and viewport rendering.
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
                        <input type="text" id="url-input" class="url-input" placeholder="http://localhost:3000" />
                        <button id="go-btn" class="go-btn">Go</button>
                    </div>
                </div>

                <!-- Browser Viewport -->
                <div class="browser-viewport-container">
                    <div class="browser-viewport" id="browser-viewport">
                        <!-- Iframe for proxied content -->
                        <iframe id="viewport-iframe" class="viewport-iframe"></iframe>
                        
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
            emptyState: document.getElementById('empty-state')
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
    }
    
    /**
     * Validate URL format (client-side pre-validation)
     */
    validateUrl(url) {
        if (!url || !url.trim()) {
            return { valid: false, error: 'Please enter a URL' };
        }
        
        // Add protocol if missing
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            url = 'http://' + url;
        }
        
        try {
            const parsed = new URL(url);
            
            // Only allow localhost
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
            const data = await response.json();
            
            if (data.success) {
                this.renderContent(data.html);
                this.state.currentUrl = url;
                this.updateStatus(`Loaded: ${url}`);
            } else {
                this.showError(data.error || 'Failed to load page');
            }
        } catch (e) {
            this.showError(`Network error: ${e.message}`);
        } finally {
            this.setLoading(false);
        }
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
    }
}

// Create global instance
window.uiuxFeedbackManager = new UIUXFeedbackManager();
