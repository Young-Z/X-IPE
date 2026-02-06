/**
 * FEATURE-025-A: KB Core Infrastructure
 * 
 * Frontend JavaScript for Knowledge Base page.
 * Uses two-column layout (like Ideation view) with tree on left of content area.
 */

const kbCore = {
    index: null,
    topics: [],
    searchTerm: '',
    container: null,

    /**
     * Render the Knowledge Base view in a container (like WorkplaceManager)
     */
    render(container) {
        this.container = container;
        container.innerHTML = `
            <div class="kb-container">
                <div class="kb-sidebar pinned" id="kb-sidebar">
                    <div class="kb-sidebar-header">
                        <span class="kb-sidebar-title">Knowledge Base</span>
                        <button class="kb-refresh-btn" id="btn-refresh-index" title="Refresh index">
                            <i class="bi bi-arrow-clockwise"></i>
                        </button>
                    </div>
                    <div class="kb-search-box">
                        <input type="text" class="kb-search-input" id="kb-search" placeholder="Search files...">
                    </div>
                    <div class="kb-tree" id="kb-tree">
                        <div class="kb-loading"><i class="bi bi-hourglass-split"></i> Loading...</div>
                    </div>
                </div>
                <div class="kb-content" id="kb-content">
                    <div class="kb-placeholder">
                        <i class="bi bi-archive"></i>
                        <h5>Knowledge Base</h5>
                        <p class="text-muted">Select a file from the tree to view</p>
                    </div>
                </div>
            </div>
        `;
        this.init();
    },

    /**
     * Initialize the Knowledge Base view.
     * Fetches index and renders tree + content.
     */
    async init() {
        console.log('[KB] Initializing Knowledge Base view');
        
        // Bind event handlers
        this.bindEvents();
        
        // Load initial data
        await this.loadIndex();
        
        // Render UI
        this.renderTree();
        this.renderWelcome();
    },

    /**
     * Bind DOM event handlers.
     */
    bindEvents() {
        // Refresh button
        const refreshBtn = document.getElementById('btn-refresh-index');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshIndex());
        }

        // Search input
        const searchInput = document.getElementById('kb-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value.toLowerCase();
                this.renderTree();
            });
        }
    },

    /**
     * Load file index from API.
     */
    async loadIndex() {
        try {
            const response = await fetch('/api/kb/index');
            if (response.ok) {
                this.index = await response.json();
                console.log('[KB] Index loaded:', this.index.files?.length || 0, 'files');
            } else {
                console.error('[KB] Failed to load index:', response.status);
                this.index = { version: '1.0', last_updated: null, files: [] };
            }
        } catch (error) {
            console.error('[KB] Error loading index:', error);
            this.index = { version: '1.0', last_updated: null, files: [] };
        }

        // Also load topics
        try {
            const response = await fetch('/api/kb/topics');
            if (response.ok) {
                const data = await response.json();
                this.topics = data.topics || [];
            }
        } catch (error) {
            console.error('[KB] Error loading topics:', error);
            this.topics = [];
        }
    },

    /**
     * Refresh index from file system.
     */
    async refreshIndex() {
        const refreshBtn = document.getElementById('btn-refresh-index');
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="bi bi-hourglass-split"></i>';
        }

        try {
            const response = await fetch('/api/kb/index/refresh', { method: 'POST' });
            if (response.ok) {
                this.index = await response.json();
                console.log('[KB] Index refreshed:', this.index.files?.length || 0, 'files');
                
                // Reload topics
                await this.loadIndex();
                
                // Re-render
                this.renderTree();
            }
        } catch (error) {
            console.error('[KB] Error refreshing index:', error);
        } finally {
            if (refreshBtn) {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '<i class="bi bi-arrow-clockwise"></i>';
            }
        }
    },

    /**
     * Render the tree in kb-sidebar (within content area).
     */
    renderTree() {
        const container = document.getElementById('kb-tree');
        if (!container) return;

        const files = this.index?.files || [];
        
        // Filter by search term
        const filteredFiles = this.searchTerm
            ? files.filter(f => 
                f.name.toLowerCase().includes(this.searchTerm) ||
                f.topic?.toLowerCase().includes(this.searchTerm) ||
                f.keywords?.some(k => k.includes(this.searchTerm))
              )
            : files;

        // Group by folder structure
        const landing = filteredFiles.filter(f => f.path.startsWith('landing/'));
        const byTopic = {};
        
        filteredFiles.forEach(f => {
            if (f.topic && !f.path.startsWith('landing/')) {
                if (!byTopic[f.topic]) byTopic[f.topic] = [];
                byTopic[f.topic].push(f);
            }
        });

        // Build HTML
        let html = '';
        
        // Landing folder
        html += `
            <div class="kb-folder">
                <div class="kb-folder-header" data-folder="landing">
                    <i class="bi bi-chevron-down"></i>
                    <i class="bi bi-inbox text-warning"></i>
                    <span>Landing (${landing.length})</span>
                </div>
                <div class="kb-folder-files">
                    ${landing.map(f => this.renderFileItem(f)).join('')}
                    ${landing.length === 0 ? '<div class="kb-empty">No files</div>' : ''}
                </div>
            </div>
        `;

        // Topic folders
        const sortedTopics = Object.keys(byTopic).sort();
        sortedTopics.forEach(topic => {
            const topicFiles = byTopic[topic];
            html += `
                <div class="kb-folder">
                    <div class="kb-folder-header" data-folder="${topic}">
                        <i class="bi bi-chevron-down"></i>
                        <i class="bi bi-folder text-info"></i>
                        <span>${topic} (${topicFiles.length})</span>
                    </div>
                    <div class="kb-folder-files">
                        ${topicFiles.map(f => this.renderFileItem(f)).join('')}
                    </div>
                </div>
            `;
        });

        // Empty topics placeholder
        if (sortedTopics.length === 0 && landing.length === 0) {
            html += '<div class="kb-empty-state"><i class="bi bi-archive"></i><p>No files in Knowledge Base</p></div>';
        }

        container.innerHTML = html;

        // Bind folder toggle events
        container.querySelectorAll('.kb-folder-header').forEach(header => {
            header.addEventListener('click', (e) => {
                const folder = e.currentTarget.closest('.kb-folder');
                folder.classList.toggle('collapsed');
                const icon = e.currentTarget.querySelector('i:first-child');
                icon.classList.toggle('bi-chevron-down');
                icon.classList.toggle('bi-chevron-right');
            });
        });

        // Bind file click events
        container.querySelectorAll('.kb-file-item').forEach(item => {
            item.addEventListener('click', () => {
                // Remove active from others
                container.querySelectorAll('.kb-file-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                
                const path = item.dataset.path;
                this.showFilePreview(path);
            });
        });
    },

    /**
     * Render a single file item in the sidebar.
     */
    renderFileItem(file) {
        const icon = this.getFileIcon(file.type);
        return `
            <div class="kb-file-item" data-path="${file.path}" title="${file.name}">
                <i class="bi ${icon}"></i>
                <span class="kb-file-name">${file.name}</span>
            </div>
        `;
    },

    /**
     * Get Bootstrap icon class for file type.
     */
    getFileIcon(type) {
        const icons = {
            'pdf': 'bi-file-earmark-pdf text-danger',
            'markdown': 'bi-markdown text-info',
            'text': 'bi-file-text',
            'docx': 'bi-file-earmark-word text-primary',
            'xlsx': 'bi-file-earmark-excel text-success',
            'python': 'bi-filetype-py text-warning',
            'javascript': 'bi-filetype-js text-warning',
            'typescript': 'bi-filetype-tsx text-primary',
            'java': 'bi-filetype-java text-danger',
            'json': 'bi-filetype-json text-warning',
            'html': 'bi-filetype-html text-danger',
            'css': 'bi-filetype-css text-info',
            'image': 'bi-file-image text-success',
            'unknown': 'bi-file-earmark'
        };
        return icons[type] || icons['unknown'];
    },

    /**
     * Render welcome/placeholder in content area.
     */
    renderWelcome() {
        const content = document.getElementById('kb-content');
        if (!content) return;
        
        const files = this.index?.files || [];
        const landing = files.filter(f => f.path.startsWith('landing/'));
        
        content.innerHTML = `
            <div class="kb-welcome">
                <div class="kb-stats mb-4">
                    <span class="badge bg-secondary me-2">${files.length} files</span>
                    <span class="badge bg-info">${this.topics.length} topics</span>
                </div>
                <div class="kb-section">
                    <h6><i class="bi bi-inbox text-warning me-2"></i>Landing (Unprocessed)</h6>
                    <div class="kb-landing-list">
                        ${landing.length > 0 ? landing.map(f => `
                            <div class="kb-landing-file">
                                <i class="bi ${this.getFileIcon(f.type)}"></i>
                                <span>${f.name}</span>
                                <span class="text-muted small ms-auto">${this.formatSize(f.size)}</span>
                            </div>
                        `).join('') : '<p class="text-muted small">No files in landing folder</p>'}
                    </div>
                </div>
                <div class="kb-section mt-4">
                    <h6><i class="bi bi-folder text-info me-2"></i>Topics</h6>
                    <div class="kb-topics-grid">
                        ${this.topics.length > 0 ? this.topics.map(topic => {
                            const topicFiles = files.filter(f => f.topic === topic);
                            return `
                                <div class="kb-topic-card">
                                    <i class="bi bi-folder me-2"></i>${topic}
                                    <span class="badge bg-secondary ms-auto">${topicFiles.length}</span>
                                </div>
                            `;
                        }).join('') : '<p class="text-muted small">No topics created yet</p>'}
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Show file preview in content area.
     */
    async showFilePreview(path) {
        const content = document.getElementById('kb-content');
        if (!content) return;
        
        const file = this.index?.files?.find(f => f.path === path);
        if (!file) {
            content.innerHTML = '<div class="kb-error">File not found</div>';
            return;
        }
        
        content.innerHTML = `
            <div class="kb-file-preview">
                <div class="kb-file-header">
                    <i class="bi ${this.getFileIcon(file.type)} fs-4"></i>
                    <div class="kb-file-info">
                        <h6 class="mb-0">${file.name}</h6>
                        <small class="text-muted">${file.path} · ${this.formatSize(file.size)}</small>
                    </div>
                </div>
                <div class="kb-file-meta mt-3">
                    <span class="badge bg-secondary me-1">${file.type}</span>
                    ${file.topic ? `<span class="badge bg-info me-1">${file.topic}</span>` : ''}
                    ${(file.keywords || []).map(k => `<span class="badge bg-outline-secondary me-1">${k}</span>`).join('')}
                </div>
                <div class="kb-file-content mt-3">
                    <p class="text-muted small">File preview coming in a future release.</p>
                </div>
            </div>
        `;
    },

    /**
     * Format file size for display.
     */
    formatSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
};

// Export for use in template
window.kbCore = kbCore;
