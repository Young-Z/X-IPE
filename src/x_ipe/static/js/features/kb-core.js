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
    activeTab: 'landing',

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
                    <div class="kb-section-tabs" id="kb-section-tabs"></div>
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
        this.activeTab = this.topics.length > 0 ? 'topics' : 'landing';
        this.renderTabs();
        this.switchTab(this.activeTab);
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
                this.updateBadges();
                // If topics were deleted and we're on topics tab, switch to landing
                if (this.activeTab === 'topics' && this.topics.length === 0) {
                    this.switchTab('landing');
                }
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
     * Render the tree in kb-sidebar, filtered by activeTab.
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

        let html = '';

        if (this.activeTab === 'landing') {
            const landing = filteredFiles.filter(f => f.path.startsWith('landing/'));
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
        } else {
            const byTopic = {};
            filteredFiles.forEach(f => {
                if (f.topic && !f.path.startsWith('landing/')) {
                    if (!byTopic[f.topic]) byTopic[f.topic] = [];
                    byTopic[f.topic].push(f);
                }
            });

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

            if (sortedTopics.length === 0) {
                html += '<div class="kb-empty-state"><i class="bi bi-archive"></i><p>No topics yet</p></div>';
            }
        }

        container.innerHTML = html;
        this._bindTreeEvents(container);
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
     * FEATURE-025-F: Render section tabs (Landing/Topics) in sidebar.
     */
    renderTabs() {
        const container = document.getElementById('kb-section-tabs');
        if (!container) return;

        const landingCount = (this.index?.files || []).filter(f => f.path.startsWith('landing/')).length;
        const topicsCount = this.topics.length;

        container.innerHTML = `
            <button class="kb-section-tab${this.activeTab === 'landing' ? ' active' : ''}" data-tab="landing">
                <i class="bi bi-inbox"></i>
                Landing
                <span class="kb-tab-badge" id="kb-badge-landing">${landingCount}</span>
            </button>
            <button class="kb-section-tab${this.activeTab === 'topics' ? ' active' : ''}" data-tab="topics">
                <i class="bi bi-layers"></i>
                Topics
                <span class="kb-tab-badge" id="kb-badge-topics">${topicsCount}</span>
            </button>
        `;

        container.querySelectorAll('.kb-section-tab').forEach(tab => {
            tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
        });
    },

    /**
     * FEATURE-025-F: Switch active tab, re-render tree and content view.
     */
    switchTab(tabName) {
        this.activeTab = tabName;

        document.querySelectorAll('.kb-section-tab').forEach(t => {
            t.classList.toggle('active', t.dataset.tab === tabName);
        });

        this.renderTree();

        const content = document.getElementById('kb-content');
        if (!content) return;

        if (tabName === 'landing') {
            const landing = (this.index?.files || []).filter(f => f.path.startsWith('landing/'));
            if (typeof kbLanding !== 'undefined') {
                kbLanding.render(content, landing);
            }
        } else if (tabName === 'topics') {
            if (typeof kbTopics !== 'undefined') {
                kbTopics.render(content, this.topics);
            }
        }
    },

    /**
     * FEATURE-025-F: Update badge counts without re-rendering tabs.
     */
    updateBadges() {
        const landingBadge = document.getElementById('kb-badge-landing');
        const topicsBadge = document.getElementById('kb-badge-topics');
        const landingCount = (this.index?.files || []).filter(f => f.path.startsWith('landing/')).length;

        if (landingBadge) landingBadge.textContent = landingCount;
        if (topicsBadge) topicsBadge.textContent = this.topics.length;
    },

    /**
     * FEATURE-025-F: Bind folder toggle and file click events on tree container.
     */
    _bindTreeEvents(container) {
        container.querySelectorAll('.kb-folder-header').forEach(header => {
            header.addEventListener('click', (e) => {
                const folder = e.currentTarget.closest('.kb-folder');
                folder.classList.toggle('collapsed');
                const icon = e.currentTarget.querySelector('i:first-child');
                icon.classList.toggle('bi-chevron-down');
                icon.classList.toggle('bi-chevron-right');
            });
        });

        container.querySelectorAll('.kb-file-item').forEach(item => {
            item.addEventListener('click', () => {
                container.querySelectorAll('.kb-file-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                this.showFilePreview(item.dataset.path);
            });
        });
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
