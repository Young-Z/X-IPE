/**
 * FEATURE-022-A: Browser Simulator & Proxy
 * 
 * JavaScript for the browser simulator functionality.
 * Handles URL input, proxy requests, and viewport rendering.
 */

class BrowserSimulator {
    constructor() {
        this.state = {
            currentUrl: null,
            isLoading: false,
            error: null
        };
        
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
        
        this.init();
    }
    
    init() {
        // Bind event listeners
        this.elements.goBtn.addEventListener('click', () => this.loadUrl());
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
        
        // Set placeholder
        this.elements.urlInput.placeholder = 'http://localhost:3000';
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
        
        this.elements.goBtn.disabled = isLoading;
        this.elements.goBtn.textContent = isLoading ? 'Loading...' : 'Go';
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
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.browserSimulator = new BrowserSimulator();
});
