/**
 * FEATURE-023-B: Tracing Dashboard UI
 * Matches mockup tracing-dashboard-v4.html
 */

// =============================================================================
// TracingDashboard - Main Dashboard Component
// =============================================================================

class TracingDashboard {
    constructor(container) {
        this.container = container;
        this.timerInterval = null;
        this.pollInterval = null;
        this.selectedTraceId = null;
        this.stopAt = null;
        this.config = {};
        this.currentFilter = 'all';
        this.searchQuery = '';
        this.traces = [];
        this.graphView = null;  // FEATURE-023-C: DAG visualization
    }

    // -------------------------------------------------------------------------
    // Lifecycle
    // -------------------------------------------------------------------------

    async init() {
        this.render();
        this.bindEvents();
        await this.fetchStatus();
        await this.refreshTraceList();
        this.startPolling();
        this.initGraphView();  // FEATURE-023-C: Initialize graph view
    }

    // FEATURE-023-C: Initialize graph view
    initGraphView() {
        const graphContainer = this.container.querySelector('.trace-graph-container');
        if (graphContainer && typeof TracingGraphView !== 'undefined') {
            this.graphView = new TracingGraphView(graphContainer);
            this.graphView.showEmpty();
        }
    }

    destroy() {
        this.stopCountdown();
        this.stopPolling();
        if (this.graphView) {
            this.graphView.destroy();
            this.graphView = null;
        }
    }

    // -------------------------------------------------------------------------
    // API Methods
    // -------------------------------------------------------------------------

    async fetchStatus() {
        try {
            const response = await fetch('/api/tracing/status');
            if (!response.ok) throw new Error('Failed to fetch status');
            
            this.config = await response.json();
            this.updateUIFromStatus();
        } catch (error) {
            console.error('Error fetching tracing status:', error);
            this.showToast('Failed to load tracing status', 'error');
        }
    }

    async startTracing(durationMinutes) {
        try {
            const response = await fetch('/api/tracing/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ duration_minutes: durationMinutes })
            });
            
            if (!response.ok) throw new Error('Failed to start tracing');
            
            const data = await response.json();
            this.stopAt = new Date(data.stop_at);
            this.startCountdown();
            this.updateDurationButtons(durationMinutes);
            this.showToast(`Tracing started for ${durationMinutes} minutes`, 'success');
        } catch (error) {
            console.error('Error starting tracing:', error);
            this.showToast('Failed to start tracing', 'error');
        }
    }

    async stopTracing() {
        try {
            const response = await fetch('/api/tracing/stop', {
                method: 'POST'
            });
            
            if (!response.ok) throw new Error('Failed to stop tracing');
            
            this.stopAt = null;
            this.stopCountdown();
            this.updateDurationButtons(null);
            this.updateTimerDisplay();
            this.showToast('Tracing stopped', 'success');
        } catch (error) {
            console.error('Error stopping tracing:', error);
            this.showToast('Failed to stop tracing', 'error');
        }
    }

    async refreshTraceList() {
        try {
            const response = await fetch('/api/tracing/logs');
            if (!response.ok) throw new Error('Failed to fetch trace logs');
            
            this.traces = await response.json();
            this.renderTraceList();
        } catch (error) {
            console.error('Error fetching trace logs:', error);
        }
    }

    // -------------------------------------------------------------------------
    // Rendering
    // -------------------------------------------------------------------------

    render() {
        this.container.innerHTML = `
            <div class="tracing-dashboard">
                <!-- Header -->
                <div class="tracing-header">
                    <div class="tracing-header-left">
                        <h2>
                            <i class="bi bi-graph-up"></i>
                            Application Tracing
                        </h2>
                    </div>
                    <div class="tracing-header-controls">
                        <div class="tracing-control">
                            <!-- Countdown Timer (left side like mockup) -->
                            <div class="countdown-container inactive">
                                <svg class="countdown-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="10"/>
                                    <path d="M12 6v6l4 2"/>
                                </svg>
                                <span class="countdown-text">--:--</span>
                                <span class="countdown-label">Inactive</span>
                            </div>
                            
                            <button class="stop-btn hidden">Stop</button>
                            
                            <span class="tracing-label">Start Tracing</span>
                            <div class="duration-toggle">
                                <button class="duration-option" data-minutes="3">3 min</button>
                                <button class="duration-option" data-minutes="15">15 min</button>
                                <button class="duration-option" data-minutes="30">30 min</button>
                            </div>
                        </div>
                        
                        <button class="icon-btn btn-config" title="Configuration">
                            <i class="bi bi-gear"></i>
                        </button>
                        <button class="icon-btn btn-ignored" title="Ignored APIs">
                            <i class="bi bi-slash-circle"></i>
                        </button>
                        <button class="icon-btn btn-clear" title="Clear All Traces">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Main Content -->
                <div class="tracing-content">
                    <!-- Sidebar -->
                    <div class="trace-list-sidebar">
                        <div class="trace-list-header">
                            <div class="trace-list-title">Trace Logs</div>
                            <div class="trace-search-box">
                                <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="11" cy="11" r="8"/>
                                    <path d="m21 21-4.35-4.35"/>
                                </svg>
                                <input type="text" placeholder="Search traces..." id="trace-search">
                            </div>
                        </div>
                        <div class="filter-row">
                            <button class="filter-chip active" data-filter="all">All</button>
                            <button class="filter-chip" data-filter="success">
                                <span class="dot success"></span>Success
                            </button>
                            <button class="filter-chip" data-filter="error">
                                <span class="dot error"></span>Errors
                            </button>
                        </div>
                        <div class="trace-list-items">
                            <div class="trace-list-empty">
                                <div class="trace-list-empty-icon">📭</div>
                                <div>No traces captured</div>
                                <div>Start tracing to begin</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Detail Panel / Graph Container (FEATURE-023-C) -->
                    <div class="trace-detail-panel">
                        <div class="trace-graph-container">
                            <!-- Graph will be initialized here by TracingGraphView -->
                        </div>
                        <div class="trace-graph-zoom-controls">
                            <button class="trace-graph-zoom-btn" data-action="zoom-in" title="Zoom In">
                                <i class="bi bi-zoom-in"></i>
                            </button>
                            <button class="trace-graph-zoom-btn" data-action="zoom-out" title="Zoom Out">
                                <i class="bi bi-zoom-out"></i>
                            </button>
                            <button class="trace-graph-zoom-btn" data-action="zoom-reset" title="Fit to View">
                                <i class="bi bi-arrows-fullscreen"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderTraceList() {
        const listContainer = this.container.querySelector('.trace-list-items');
        
        // Filter traces
        let filteredTraces = this.traces;
        if (this.currentFilter === 'success') {
            filteredTraces = this.traces.filter(t => !t.has_error);
        } else if (this.currentFilter === 'error') {
            filteredTraces = this.traces.filter(t => t.has_error);
        }
        
        // Search filter
        if (this.searchQuery) {
            const query = this.searchQuery.toLowerCase();
            filteredTraces = filteredTraces.filter(t => 
                (t.api || t.path || '').toLowerCase().includes(query) ||
                (t.trace_id || '').toLowerCase().includes(query)
            );
        }
        
        if (!filteredTraces || filteredTraces.length === 0) {
            listContainer.innerHTML = `
                <div class="trace-list-empty">
                    <div class="trace-list-empty-icon">📭</div>
                    <div>${this.searchQuery || this.currentFilter !== 'all' ? 'No matching traces' : 'No traces captured'}</div>
                    <div>${!this.searchQuery && this.currentFilter === 'all' ? 'Start tracing to begin' : 'Try adjusting your filters'}</div>
                </div>
            `;
            return;
        }

        // Sort by timestamp descending (newest first)
        filteredTraces.sort((a, b) => {
            const timeA = new Date(a.timestamp || a.created || 0);
            const timeB = new Date(b.timestamp || b.created || 0);
            return timeB - timeA;
        });

        listContainer.innerHTML = filteredTraces.map(trace => {
            const traceId = trace.trace_id || trace.id || 'unknown';
            const api = trace.api || trace.path || trace.name || '/unknown';
            const timestamp = trace.timestamp || trace.created || '';
            const hasError = trace.has_error || trace.status === 'error';
            const statusClass = hasError ? 'error' : 'success';
            const isSelected = traceId === this.selectedTraceId;
            const method = trace.method || 'GET';
            const duration = trace.duration_ms || trace.duration || 0;
            const nestedCount = trace.nested_count || trace.spans || 0;
            
            // Format timestamp
            let formattedTime = '';
            if (timestamp) {
                const date = new Date(timestamp);
                formattedTime = date.toLocaleTimeString();
            }
            
            // Truncate trace ID
            const shortId = traceId.substring(0, 8);
            
            // Extract just the path from API (e.g., "GET /api/projects" -> "/api/projects")
            const apiPath = api.includes(' ') ? api.split(' ').slice(1).join(' ') : api;
            
            return `
                <div class="trace-item ${statusClass} ${isSelected ? 'selected' : ''}" 
                     data-trace-id="${traceId}" data-api-path="${this.escapeHtml(apiPath)}">
                    <div class="trace-id-row">
                        <span class="trace-id">${shortId}...</span>
                        <button class="trace-block-btn" title="Add to ignored APIs" data-api="${this.escapeHtml(apiPath)}">
                            <i class="bi bi-slash-circle"></i>
                        </button>
                        <span class="trace-status-dot ${statusClass}"></span>
                    </div>
                    <div class="trace-entry-api">
                        <span class="method-badge ${method.toLowerCase()}">${method}</span>
                        <span class="trace-path">${this.escapeHtml(api)}</span>
                        ${nestedCount > 0 ? `<span class="trace-nested">+${nestedCount}</span>` : ''}
                    </div>
                    <div class="trace-meta">
                        <span>
                            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/>
                                <polyline points="12 6 12 12 16 14"/>
                            </svg>
                            ${formattedTime}
                        </span>
                        ${duration > 0 ? `<span>${duration}ms</span>` : ''}
                    </div>
                </div>
            `;
        }).join('');

        // Rebind click events
        listContainer.querySelectorAll('.trace-item').forEach(item => {
            item.addEventListener('click', (e) => {
                // Don't select trace if clicking the block button
                if (e.target.closest('.trace-block-btn')) return;
                this.selectTrace(item.dataset.traceId);
            });
        });
        
        // Bind block button events
        listContainer.querySelectorAll('.trace-block-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const apiPath = btn.dataset.api;
                this.addToIgnoredApis(apiPath);
            });
        });
    }

    // -------------------------------------------------------------------------
    // Timer Logic
    // -------------------------------------------------------------------------

    startCountdown() {
        this.stopCountdown();
        this.updateTimerDisplay();
        
        this.timerInterval = setInterval(() => {
            this.updateTimerDisplay();
            
            // Auto-stop when timer reaches 0
            if (this.stopAt && new Date() >= this.stopAt) {
                this.stopCountdown();
                this.stopAt = null;
                this.updateDurationButtons(null);
                this.updateTimerDisplay();
                this.showToast('Tracing completed', 'success');
            }
        }, 1000);
        
        // Show stop button
        const stopBtn = this.container.querySelector('.stop-btn');
        if (stopBtn) stopBtn.classList.remove('hidden');
    }

    stopCountdown() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        
        // Hide stop button
        const stopBtn = this.container.querySelector('.stop-btn');
        if (stopBtn) stopBtn.classList.add('hidden');
    }

    updateTimerDisplay() {
        const container = this.container.querySelector('.countdown-container');
        const timerText = this.container.querySelector('.countdown-text');
        const timerLabel = this.container.querySelector('.countdown-label');
        if (!container || !timerText) return;
        
        if (!this.stopAt) {
            timerText.textContent = '--:--';
            if (timerLabel) timerLabel.textContent = 'Inactive';
            container.classList.remove('warning');
            container.classList.add('inactive');
            return;
        }
        
        const now = new Date();
        const remaining = Math.max(0, Math.floor((this.stopAt - now) / 1000));
        
        const minutes = Math.floor(remaining / 60);
        const seconds = remaining % 60;
        timerText.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        if (timerLabel) timerLabel.textContent = 'remaining';
        
        container.classList.remove('inactive');
        
        // Warning state when < 1 minute
        if (remaining < 60 && remaining > 0) {
            container.classList.add('warning');
        } else {
            container.classList.remove('warning');
        }
    }

    updateUIFromStatus() {
        const stopAtStr = this.config.stop_at;
        if (stopAtStr && this.config.active) {
            this.stopAt = new Date(stopAtStr);
            if (this.stopAt > new Date()) {
                this.startCountdown();
                // Estimate which duration was selected
                const remaining = (this.stopAt - new Date()) / 1000 / 60;
                if (remaining <= 3) this.updateDurationButtons(3);
                else if (remaining <= 15) this.updateDurationButtons(15);
                else this.updateDurationButtons(30);
            } else {
                this.stopAt = null;
            }
        }
        this.updateTimerDisplay();
    }

    updateDurationButtons(activeMinutes) {
        this.container.querySelectorAll('.duration-option').forEach(btn => {
            const minutes = parseInt(btn.dataset.minutes);
            btn.classList.toggle('active', minutes === activeMinutes);
        });
    }

    // -------------------------------------------------------------------------
    // Polling
    // -------------------------------------------------------------------------

    startPolling() {
        this.pollInterval = setInterval(() => {
            if (this.stopAt) {
                this.refreshTraceList();
            }
        }, 5000);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    // -------------------------------------------------------------------------
    // Event Handling
    // -------------------------------------------------------------------------

    bindEvents() {
        // Duration buttons
        this.container.querySelectorAll('.duration-option').forEach(btn => {
            btn.addEventListener('click', () => {
                const minutes = parseInt(btn.dataset.minutes);
                this.startTracing(minutes);
            });
        });

        // Stop button
        const stopBtn = this.container.querySelector('.stop-btn');
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopTracing());
        }

        // Config button
        const configBtn = this.container.querySelector('.btn-config');
        if (configBtn) {
            configBtn.addEventListener('click', () => this.openConfigModal());
        }

        // Ignored APIs button
        const ignoredBtn = this.container.querySelector('.btn-ignored');
        if (ignoredBtn) {
            ignoredBtn.addEventListener('click', () => this.openIgnoredModal());
        }
        
        // Clear all traces button
        const clearBtn = this.container.querySelector('.btn-clear');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearAllTraces());
        }
        
        // Filter chips
        this.container.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                this.container.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                this.currentFilter = chip.dataset.filter;
                this.renderTraceList();
            });
        });
        
        // Search
        const searchInput = this.container.querySelector('#trace-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value;
                this.renderTraceList();
            });
        }
        
        // FEATURE-023-C: Zoom controls
        this.container.querySelectorAll('.trace-graph-zoom-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                if (!this.graphView) return;
                const action = btn.dataset.action;
                if (action === 'zoom-in') this.graphView.zoomIn();
                else if (action === 'zoom-out') this.graphView.zoomOut();
                else if (action === 'zoom-reset') this.graphView.resetZoom();
            });
        });
    }

    selectTrace(traceId) {
        this.selectedTraceId = traceId;
        
        // Update selection UI
        this.container.querySelectorAll('.trace-item').forEach(item => {
            item.classList.toggle('selected', item.dataset.traceId === traceId);
        });

        // FEATURE-023-C: Load trace into graph view
        if (this.graphView) {
            this.graphView.loadTrace(traceId);
        } else {
            // Fallback if graph view not initialized
            const graphContainer = this.container.querySelector('.trace-graph-container');
            if (graphContainer) {
                graphContainer.innerHTML = `
                    <div class="trace-graph-loading">
                        <div class="spinner-border spinner-border-sm" role="status"></div>
                        <span>Loading trace: ${traceId.substring(0, 12)}...</span>
                    </div>
                `;
            }
        }
    }

    // -------------------------------------------------------------------------
    // Modals
    // -------------------------------------------------------------------------

    openConfigModal() {
        const modal = new TracingConfigModal(async (config) => {
            await this.updateConfig(config);
        });
        modal.open(this.config);
    }

    async updateConfig(config) {
        try {
            const response = await fetch('/api/tracing/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            
            if (response.ok) {
                this.config = { ...this.config, ...config };
                this.showToast('Configuration saved', 'success');
            } else {
                this.showToast('Failed to save configuration', 'error');
            }
        } catch (error) {
            console.error('Error updating config:', error);
            this.showToast('Failed to save configuration', 'error');
        }
    }

    openIgnoredModal() {
        const modal = new TracingIgnoredModal(async (patterns) => {
            await this.updateIgnoredApis(patterns);
        });
        modal.open(this.config.ignored_apis || []);
    }

    async updateIgnoredApis(patterns) {
        try {
            const response = await fetch('/api/tracing/ignored', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ patterns })
            });
            
            if (response.ok) {
                this.config.ignored_apis = patterns;
                this.showToast('Ignored APIs updated', 'success');
            } else {
                this.showToast('Failed to update ignored APIs', 'error');
            }
        } catch (error) {
            console.error('Error updating ignored APIs:', error);
            this.showToast('Failed to update ignored APIs', 'error');
        }
    }
    
    async addToIgnoredApis(apiPath) {
        if (!apiPath) return;
        
        // Get current ignored APIs
        const currentIgnored = this.config.ignored_apis || [];
        
        // Check if already in list
        if (currentIgnored.includes(apiPath)) {
            this.showToast('API already in ignored list', 'info');
            return;
        }
        
        // Add to list and save
        const newIgnored = [...currentIgnored, apiPath];
        await this.updateIgnoredApis(newIgnored);
    }
    
    async clearAllTraces() {
        if (!confirm('Are you sure you want to delete all trace logs? This cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch('/api/tracing/logs', {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.traces = [];
                this.renderTraceList();
                this.graph.showEmpty();
                this.showToast('All traces cleared', 'success');
            } else {
                this.showToast('Failed to clear traces', 'error');
            }
        } catch (error) {
            console.error('Error clearing traces:', error);
            this.showToast('Failed to clear traces', 'error');
        }
    }

    // -------------------------------------------------------------------------
    // Utilities
    // -------------------------------------------------------------------------

    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `tracing-toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}


// =============================================================================
// TracingConfigModal - Configuration Modal
// =============================================================================

class TracingConfigModal {
    constructor(onSave) {
        this.onSave = onSave;
        this.overlay = null;
    }

    open(currentConfig) {
        this.overlay = document.createElement('div');
        this.overlay.className = 'tracing-modal-overlay';
        this.overlay.innerHTML = `
            <div class="tracing-modal">
                <div class="tracing-modal-header">
                    <h3>Tracing Configuration</h3>
                    <button class="tracing-modal-close">&times;</button>
                </div>
                <div class="tracing-modal-body">
                    <div class="tracing-form-group">
                        <label>Retention Hours</label>
                        <input type="number" id="retention-hours" min="1" max="168" 
                               value="${currentConfig.retention_hours || 24}">
                    </div>
                    <div class="tracing-form-group">
                        <label>Log Path</label>
                        <input type="text" id="log-path" 
                               value="${currentConfig.log_path || 'instance/traces/'}">
                    </div>
                </div>
                <div class="tracing-modal-footer">
                    <button class="btn-secondary btn-cancel">Cancel</button>
                    <button class="btn-primary btn-save">Save</button>
                </div>
            </div>
        `;

        document.body.appendChild(this.overlay);
        this.bindEvents();
    }

    bindEvents() {
        this.overlay.querySelector('.tracing-modal-close').addEventListener('click', () => this.close());
        this.overlay.querySelector('.btn-cancel').addEventListener('click', () => this.close());
        this.overlay.querySelector('.btn-save').addEventListener('click', () => this.handleSave());
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.close();
        });
    }

    handleSave() {
        const retentionHours = parseInt(this.overlay.querySelector('#retention-hours').value);
        const logPath = this.overlay.querySelector('#log-path').value;
        
        this.onSave({ retention_hours: retentionHours, log_path: logPath });
        this.close();
    }

    close() {
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
    }
}


// =============================================================================
// TracingIgnoredModal - Ignored APIs Modal
// =============================================================================

class TracingIgnoredModal {
    constructor(onSave) {
        this.onSave = onSave;
        this.overlay = null;
        this.patterns = [];
    }

    open(patterns) {
        this.patterns = [...patterns];
        
        this.overlay = document.createElement('div');
        this.overlay.className = 'tracing-modal-overlay';
        this.render();
        document.body.appendChild(this.overlay);
        this.bindEvents();
    }

    render() {
        this.overlay.innerHTML = `
            <div class="tracing-modal">
                <div class="tracing-modal-header">
                    <h3>Ignored APIs</h3>
                    <button class="tracing-modal-close">&times;</button>
                </div>
                <div class="tracing-modal-body">
                    <p style="font-size: 13px; color: #64748b; margin-bottom: 16px;">
                        API patterns that will be excluded from tracing.
                    </p>
                    <div class="ignored-apis-list">
                        ${this.patterns.map((pattern, i) => `
                            <div class="ignored-api-item">
                                <span>${this.escapeHtml(pattern)}</span>
                                <button data-index="${i}" title="Remove">×</button>
                            </div>
                        `).join('')}
                    </div>
                    <div class="add-ignored-api">
                        <input type="text" id="new-pattern" placeholder="/api/health/*">
                        <button class="btn-secondary btn-add">Add</button>
                    </div>
                </div>
                <div class="tracing-modal-footer">
                    <button class="btn-secondary btn-cancel">Cancel</button>
                    <button class="btn-primary btn-save">Save</button>
                </div>
            </div>
        `;
    }

    bindEvents() {
        this.overlay.querySelector('.tracing-modal-close').addEventListener('click', () => this.close());
        this.overlay.querySelector('.btn-cancel').addEventListener('click', () => this.close());
        this.overlay.querySelector('.btn-save').addEventListener('click', () => this.handleSave());
        this.overlay.querySelector('.btn-add').addEventListener('click', () => this.addPattern());
        
        // Remove buttons
        this.overlay.querySelectorAll('.ignored-api-item button').forEach(btn => {
            btn.addEventListener('click', () => {
                const index = parseInt(btn.dataset.index);
                this.removePattern(index);
            });
        });

        // Enter key to add
        this.overlay.querySelector('#new-pattern').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.addPattern();
        });

        // Click outside to close
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.close();
        });
    }

    addPattern() {
        const input = this.overlay.querySelector('#new-pattern');
        const pattern = input.value.trim();
        if (pattern && !this.patterns.includes(pattern)) {
            this.patterns.push(pattern);
            this.render();
            this.bindEvents();
        }
    }

    removePattern(index) {
        this.patterns.splice(index, 1);
        this.render();
        this.bindEvents();
    }

    handleSave() {
        this.onSave(this.patterns);
        this.close();
    }

    close() {
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}


// =============================================================================
// Export for module usage
// =============================================================================

if (typeof window !== 'undefined') {
    window.TracingDashboard = TracingDashboard;
    window.TracingConfigModal = TracingConfigModal;
    window.TracingIgnoredModal = TracingIgnoredModal;
}
