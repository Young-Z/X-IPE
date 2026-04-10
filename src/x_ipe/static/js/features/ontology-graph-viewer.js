/**
 * FEATURE-058-E/F: Ontology Graph Viewer — Orchestrator
 *
 * Top-level class that manages the viewer lifecycle: CDN loading,
 * sidebar graph list, scope pills, search, BFS search with dropdown,
 * AI Agent Console bridge, layout picker, status bar, and wiring to
 * OntologyGraphCanvas + OntologyDetailPanel.
 */

class OntologyGraphViewer {
    constructor() {
        this.container = null;
        this.canvas = null;
        this.detailPanel = null;
        this._selectedGraphs = new Set();
        this._graphIndex = [];
        this._cdnLoaded = false;
        this._destroyed = false;
        this._selectedDropdownIndex = -1;
        this._searchAbortController = null;
        this._lastSearchQuery = '';
    }

    // -----------------------------------------------------------------------
    // CDN Loading
    // -----------------------------------------------------------------------

    async _loadCDN() {
        if (this._cdnLoaded) return;
        const loadScript = (url) => new Promise((resolve, reject) => {
            if (document.querySelector(`script[src="${url}"]`)) { resolve(); return; }
            const s = document.createElement('script');
            s.src = url;
            s.onload = resolve;
            s.onerror = () => reject(new Error(`Failed to load ${url}`));
            document.head.appendChild(s);
        });
        const loadCSS = (url) => {
            if (document.querySelector(`link[href="${url}"]`)) return;
            const l = document.createElement('link');
            l.rel = 'stylesheet';
            l.href = url;
            document.head.appendChild(l);
        };

        // Tippy.js CSS
        loadCSS('https://unpkg.com/tippy.js@6.3.7/themes/light.css');

        // Phase 1: core libs (parallel)
        await Promise.all([
            loadScript('https://unpkg.com/cytoscape@3.30.4/dist/cytoscape.min.js'),
            loadScript('https://unpkg.com/dagre@0.8.5/dist/dagre.min.js'),
            loadScript('https://unpkg.com/@popperjs/core@2.11.8/dist/umd/popper.min.js'),
            loadScript('https://unpkg.com/layout-base@2.0.1/layout-base.js'),
        ]);

        // Phase 1b: cose-base depends on layout-base
        await loadScript('https://unpkg.com/cose-base@2.2.0/cose-base.js');

        // Phase 2: plugins (parallel, depend on phase 1)
        await Promise.all([
            loadScript('https://unpkg.com/cytoscape-fcose@2.2.0/cytoscape-fcose.js'),
            loadScript('https://unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js'),
            loadScript('https://unpkg.com/cytoscape-cxtmenu@3.5.0/cytoscape-cxtmenu.js'),
            loadScript('https://unpkg.com/tippy.js@6.3.7/dist/tippy-bundle.umd.min.js'),
        ]);

        // Phase 3: register plugins
        if (typeof cytoscape !== 'undefined') {
            if (typeof cytoscapeFcose !== 'undefined') cytoscape.use(cytoscapeFcose);
            if (typeof cytoscapeDagre !== 'undefined') cytoscape.use(cytoscapeDagre);
            if (typeof cytoscapeCxtmenu !== 'undefined') cytoscape.use(cytoscapeCxtmenu);
        }

        this._cdnLoaded = true;
    }

    // -----------------------------------------------------------------------
    // Render
    // -----------------------------------------------------------------------

    async render(containerEl) {
        this.container = containerEl;
        this.container.innerHTML = '';
        this.container.appendChild(this._buildDOM());

        // Show loading
        const canvasArea = this.container.querySelector('.ogv-canvas-area');
        const loadingEl = document.createElement('div');
        loadingEl.className = 'ogv-loading';
        loadingEl.innerHTML = '<div class="ogv-spinner"></div>';
        canvasArea.appendChild(loadingEl);

        try {
            await this._loadCDN();
        } catch (err) {
            loadingEl.remove();
            this._showError('Failed to load graph libraries. Check network connectivity.');
            return;
        }

        if (this._destroyed) return;

        // Init canvas
        const canvasContainer = canvasArea.querySelector('.ogv-canvas-container');
        this.canvas = new OntologyGraphCanvas(canvasContainer, {
            onNodeSelect: (nodeId) => this._onNodeSelect(nodeId),
            onNodeDeselect: () => this._onNodeDeselect(),
        });
        this.canvas.init();

        // Init detail panel
        const panelEl = this.container.querySelector('.ogv-detail-panel');
        this.detailPanel = new OntologyDetailPanel(panelEl);

        // Init navigator
        const navEl = canvasArea.querySelector('.ogv-navigator');
        this.canvas.initNavigator(navEl);

        loadingEl.remove();

        // Wire up controls
        this._wireLayoutPicker(canvasArea);
        this._wireZoomControls(canvasArea);
        this._wireSearch();
        this._wireAIAgentButton();
        this._wireScopeBar();

        // Load graph index
        await this._loadGraphIndex();
    }

    // -----------------------------------------------------------------------
    // DOM Construction
    // -----------------------------------------------------------------------

    _buildDOM() {
        const wrapper = document.createElement('div');
        wrapper.className = 'ontology-graph-viewer';

        wrapper.innerHTML = `
            <!-- Sidebar -->
            <div class="ogv-sidebar">
                <div class="ogv-sidebar-header">
                    <div class="ogv-sidebar-title">
                        <span class="ogv-sidebar-icon">◈</span> ONTOLOGY
                    </div>
                </div>
                <div class="ogv-section-header">GRAPH COLLECTIONS</div>
                <div class="ogv-select-all">
                    <label><input type="checkbox" class="ogv-select-all-cb" /> Select All</label>
                    <span class="ogv-graph-count"></span>
                </div>
                <div class="ogv-graph-list"></div>
                <div class="ogv-legend">
                    <div class="ogv-section-header ogv-section-header--legend">NODE TYPES</div>
                    <div class="ogv-legend-items">
                        <div class="ogv-legend-item"><span class="ogv-type-badge ogv-type-badge--concept"></span>Concept</div>
                        <div class="ogv-legend-item"><span class="ogv-type-badge ogv-type-badge--document"></span>Document</div>
                        <div class="ogv-legend-item"><span class="ogv-type-badge ogv-type-badge--entity"></span>Entity</div>
                        <div class="ogv-legend-item"><span class="ogv-type-badge ogv-type-badge--dimension"></span>Dimension</div>
                    </div>
                </div>
            </div>

            <!-- Topbar (Scope + Search + AI Agent) -->
            <header class="ogv-topbar">
                <div class="ogv-scope-bar">
                    <span class="ogv-scope-label">SCOPE</span>
                </div>
                <div class="ogv-topbar-divider"></div>
                <div class="ogv-search-bar">
                    <i class="bi bi-search ogv-search-icon"></i>
                    <input class="ogv-search-input" type="text" placeholder="Search nodes… (e.g. authentication, token)" />
                </div>
                <div class="ogv-search-dropdown"></div>
                <div class="ogv-topbar-divider"></div>
                <button class="ogv-ai-agent-btn" title="Search with AI Agent">
                    <svg class="ogv-ai-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                        <polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>
                    </svg>
                    <span>Search with AI Agent</span>
                </button>
            </header>

            <!-- Canvas Area -->
            <div class="ogv-canvas-area">
                <div class="ogv-layout-picker">
                    <div class="ogv-layout-picker-title">LAYOUT</div>
                    <button class="ogv-layout-btn active" data-layout="fcose">
                        <svg class="ogv-layout-icon" viewBox="0 0 16 16" width="14" height="14"><circle cx="4" cy="4" r="2" fill="currentColor"/><circle cx="12" cy="4" r="2" fill="currentColor"/><circle cx="8" cy="12" r="2" fill="currentColor"/><line x1="5.5" y1="5" x2="7" y2="10.5" stroke="currentColor" stroke-width="1"/><line x1="10.5" y1="5" x2="9" y2="10.5" stroke="currentColor" stroke-width="1"/><line x1="6" y1="4" x2="10" y2="4" stroke="currentColor" stroke-width="1"/></svg>
                        Force-Directed
                    </button>
                    <button class="ogv-layout-btn" data-layout="dagre">
                        <svg class="ogv-layout-icon" viewBox="0 0 16 16" width="14" height="14"><rect x="5" y="1" width="6" height="3" rx="1" fill="currentColor"/><rect x="1" y="11" width="6" height="3" rx="1" fill="currentColor"/><rect x="9" y="11" width="6" height="3" rx="1" fill="currentColor"/><line x1="8" y1="4" x2="4" y2="11" stroke="currentColor" stroke-width="1"/><line x1="8" y1="4" x2="12" y2="11" stroke="currentColor" stroke-width="1"/></svg>
                        Hierarchical
                    </button>
                    <button class="ogv-layout-btn" data-layout="concentric">
                        <svg class="ogv-layout-icon" viewBox="0 0 16 16" width="14" height="14"><circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" stroke-width="1"/><circle cx="8" cy="8" r="3.5" fill="none" stroke="currentColor" stroke-width="1"/><circle cx="8" cy="8" r="1.5" fill="currentColor"/></svg>
                        Radial
                    </button>
                </div>

                <div class="ogv-canvas-container"></div>

                <div class="ogv-navigator"></div>

                <div class="ogv-zoom-controls">
                    <button class="ogv-zoom-btn" data-action="in" title="Zoom In">+</button>
                    <button class="ogv-zoom-btn" data-action="out" title="Zoom Out">−</button>
                    <button class="ogv-zoom-btn" data-action="fit" title="Fit All">⊡</button>
                </div>
            </div>

            <!-- Status Bar -->
            <footer class="ogv-status-bar">
                <span class="ogv-status-dot"></span>
                <span class="ogv-status-text">Connected</span>
                <span class="ogv-status-sep">·</span>
                <span class="ogv-status-nodes">0 nodes</span>
                <span class="ogv-status-sep">·</span>
                <span class="ogv-status-edges">0 edges</span>
                <span class="ogv-status-sep">·</span>
                <span class="ogv-status-layout">Layout: Force-directed</span>
                <span class="ogv-status-sep">·</span>
                <span class="ogv-status-zoom">Zoom: 100%</span>
                <span class="ogv-status-scope-count"></span>
            </footer>

            <!-- Detail Panel -->
            <div class="ogv-detail-panel">
                <div class="ogv-detail-inner"></div>
            </div>`;

        return wrapper;
    }

    // -----------------------------------------------------------------------
    // API Calls
    // -----------------------------------------------------------------------

    async _loadGraphIndex() {
        this._updateStatus('Loading graphs…');
        try {
            const resp = await fetch('/api/kb/ontology/graphs');
            if (!resp.ok) {
                if (resp.status === 404) {
                    this._showEmptyState('No Ontology Found', 'Run ontology extraction on your knowledge base to generate graph data.');
                    this._updateStatus('No ontology');
                    return;
                }
                throw new Error(`HTTP ${resp.status}`);
            }
            const data = await resp.json();
            this._graphIndex = data.graphs || [];
            this._renderGraphList();
            this._updateStatus('Connected');
        } catch (err) {
            this._showError(`Failed to load graphs: ${err.message}`);
            this._updateStatus('Error');
        }
    }

    async _loadGraph(name) {
        try {
            const resp = await fetch(`/api/kb/ontology/graph/${encodeURIComponent(name)}`);
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const data = await resp.json();
            const raw = data.elements;
            if (!raw) return [];
            // Flatten {nodes:[...], edges:[...]} into Cytoscape-compatible flat array
            if (raw.nodes || raw.edges) {
                const flat = [];
                (raw.nodes || []).forEach(n => flat.push({ group: 'nodes', data: { ...n.data, _graph: name } }));
                (raw.edges || []).forEach(e => flat.push({ group: 'edges', data: { ...e.data, _graph: name } }));
                return flat;
            }
            // Already a flat array
            return Array.isArray(raw) ? raw : [];
        } catch (err) {
            this._showError(`Failed to load graph "${name}": ${err.message}`);
            return [];
        }
    }

    async _searchNodes(query) {
        const graphsParam = Array.from(this._selectedGraphs).join(',');
        try {
            const resp = await fetch(`/api/kb/ontology/search?q=${encodeURIComponent(query)}&graphs=${encodeURIComponent(graphsParam)}`);
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const data = await resp.json();
            return data.results || [];
        } catch (_err) {
            return [];
        }
    }

    async _searchBFS(query) {
        // Cancel any in-flight search
        if (this._searchAbortController) {
            this._searchAbortController.abort();
        }
        this._searchAbortController = new AbortController();

        const scope = this._selectedGraphs.size > 0
            ? Array.from(this._selectedGraphs).join(',')
            : 'all';
        try {
            const resp = await fetch(
                `/api/kb/ontology/search/bfs?q=${encodeURIComponent(query)}&scope=${encodeURIComponent(scope)}&depth=3&page=1&page_size=20`,
                { signal: this._searchAbortController.signal }
            );
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            return await resp.json();
        } catch (err) {
            if (err.name === 'AbortError') return null;
            return { results: [], subgraph: { nodes: [], edges: [] }, pagination: { total: 0 } };
        }
    }

    // -----------------------------------------------------------------------
    // Search Dropdown
    // -----------------------------------------------------------------------

    _renderDropdown(results) {
        const dropdown = this.container.querySelector('.ogv-search-dropdown');
        if (!dropdown) return;

        this._selectedDropdownIndex = -1;

        if (!results || results.length === 0) {
            dropdown.innerHTML = '<div class="ogv-search-dropdown-empty">No results found</div>';
            dropdown.classList.add('ogv-search-dropdown--visible');
            return;
        }

        const typeColors = {
            concept: '#10b981', document: '#3b82f6',
            entity: '#f59e0b', dimension: '#8b5cf6',
        };

        const items = results.slice(0, 10).map((r, i) => {
            const color = typeColors[r.node_type] || '#94a3b8';
            const relevanceWidth = Math.round((r.relevance || 0) * 100);
            return `<div class="ogv-search-dropdown-item" data-index="${i}" data-node-id="${r.node_id}" data-graph="${r.graph}">
                <span class="ogv-dropdown-type-dot" style="background:${color}"></span>
                <span class="ogv-dropdown-label">${this._escapeHtml(r.label)}</span>
                <span class="ogv-dropdown-graph">${this._escapeHtml(r.graph)}</span>
                <span class="ogv-dropdown-relevance"><span class="ogv-dropdown-relevance-bar" style="width:${relevanceWidth}%"></span></span>
            </div>`;
        }).join('');

        dropdown.innerHTML = items;
        dropdown.classList.add('ogv-search-dropdown--visible');

        // Wire click handlers
        dropdown.querySelectorAll('.ogv-search-dropdown-item').forEach(item => {
            item.addEventListener('click', () => {
                const nodeId = item.dataset.nodeId;
                this.canvas.focusNode(nodeId);
                this._onNodeSelect(nodeId);
                this._clearDropdown();
            });
        });
    }

    _clearDropdown() {
        const dropdown = this.container.querySelector('.ogv-search-dropdown');
        if (dropdown) {
            dropdown.innerHTML = '';
            dropdown.classList.remove('ogv-search-dropdown--visible');
        }
        this._selectedDropdownIndex = -1;
    }

    _handleDropdownKeyboard(event) {
        const dropdown = this.container.querySelector('.ogv-search-dropdown');
        if (!dropdown || !dropdown.classList.contains('ogv-search-dropdown--visible')) return false;

        const items = dropdown.querySelectorAll('.ogv-search-dropdown-item');
        if (items.length === 0) return false;

        if (event.key === 'ArrowDown') {
            event.preventDefault();
            this._selectedDropdownIndex = Math.min(this._selectedDropdownIndex + 1, items.length - 1);
            this._highlightDropdownItem(items);
            return true;
        }
        if (event.key === 'ArrowUp') {
            event.preventDefault();
            this._selectedDropdownIndex = Math.max(this._selectedDropdownIndex - 1, 0);
            this._highlightDropdownItem(items);
            return true;
        }
        if (event.key === 'Enter' && this._selectedDropdownIndex >= 0) {
            event.preventDefault();
            const selected = items[this._selectedDropdownIndex];
            if (selected) {
                const nodeId = selected.dataset.nodeId;
                this.canvas.focusNode(nodeId);
                this._onNodeSelect(nodeId);
                this._clearDropdown();
            }
            return true;
        }
        if (event.key === 'Escape') {
            event.preventDefault();
            this._clearDropdown();
            this.canvas.clearHighlight();
            this._updateSearchStatus(null);
            return true;
        }
        return false;
    }

    _highlightDropdownItem(items) {
        items.forEach((item, i) => {
            item.classList.toggle('ogv-search-dropdown-item--selected', i === this._selectedDropdownIndex);
        });
        // Scroll into view
        if (this._selectedDropdownIndex >= 0 && items[this._selectedDropdownIndex]) {
            items[this._selectedDropdownIndex].scrollIntoView({ block: 'nearest' });
        }
    }

    _escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str || '';
        return div.innerHTML;
    }

    // -----------------------------------------------------------------------
    // AI Agent Console Bridge
    // -----------------------------------------------------------------------

    _wireAIAgentButton() {
        const btn = this.container.querySelector('.ogv-ai-agent-btn');
        if (!btn) return;
        btn.addEventListener('click', () => this._openAIAgentConsole());
    }

    _openAIAgentConsole() {
        // Get selected graphs
        const graphs = Array.from(this._selectedGraphs);
        if (graphs.length === 0) {
            this._showError('Select at least one graph before using AI Agent search.');
            return;
        }

        // Check terminal manager availability
        if (!window.terminalManager) {
            this._showError('Console not available. Terminal manager is not loaded.');
            return;
        }

        const tm = window.terminalManager;

        // Expand console if collapsed
        const terminalPanel = document.getElementById('terminal-panel');
        if (terminalPanel && terminalPanel.classList.contains('collapsed')) {
            const toggle = document.getElementById('terminal-toggle');
            if (toggle) toggle.click();
        }

        // Find idle session or create new
        const idle = tm.findIdleSession ? tm.findIdleSession() : null;
        if (idle) {
            if (tm.claimSessionForAction) tm.claimSessionForAction(idle.id);
            if (tm.switchSession) tm.switchSession(idle.id);
        } else if (tm.addSession) {
            tm.addSession();
        }

        // Build and send command
        const scopeStr = graphs.join(', ');
        const command = `search the knowledge graph scoped to ${scopeStr} for: `;
        if (tm.sendCopilotPromptCommandNoEnter) {
            tm.sendCopilotPromptCommandNoEnter(command);
        }
    }

    // -----------------------------------------------------------------------
    // Graph Selection
    // -----------------------------------------------------------------------

    async _toggleGraph(name, selected) {
        if (selected) {
            this._selectedGraphs.add(name);
            this._updateStatus(`Loading ${name}…`);
            const elements = await this._loadGraph(name);
            if (this._destroyed) return;
            this.canvas.addElements(elements);
            this._addScopePill(name);
        } else {
            this._selectedGraphs.delete(name);
            this.canvas.removeGraphElements(name);
            this._removeScopePill(name);
        }
        // Update selected styling on graph items
        const item = this.container.querySelector(`.ogv-graph-item[data-graph="${name}"]`);
        if (item) item.classList.toggle('ogv-graph-item--selected', selected);
        this._updateStats();
        this._refreshNav();
        this._updateStatus('Connected');
        if (this._lastSearchQuery) {
            const data = await this._searchBFS(this._lastSearchQuery);
            if (!data) return;
            if (data.results && data.results.length > 0) {
                this._renderDropdown(data.results);
                this.canvas.highlightSubgraph(
                    data.subgraph ? data.subgraph.nodes : [],
                    data.results.map(r => r.node_id)
                );
                this._updateSearchStatus(data);
            } else {
                this._renderDropdown([]);
                this.canvas.clearHighlight();
                this._updateSearchStatus(data);
            }
        }
    }

    async _selectAll(selected) {
        if (selected) {
            this._updateStatus('Loading all graphs…');
            const allElements = [];
            for (const g of this._graphIndex) {
                this._selectedGraphs.add(g.name);
                const elements = await this._loadGraph(g.name);
                allElements.push(...elements);
            }
            if (this._destroyed) return;
            this.canvas.setElements(allElements);
            this._renderScopePills();
        } else {
            this._selectedGraphs.clear();
            this.canvas.setElements([]);
            this._renderScopePills();
        }
        this._updateGraphListCheckboxes();
        this._updateStats();
        this._refreshNav();
        this._updateStatus('Connected');
    }

    // -----------------------------------------------------------------------
    // Sidebar Graph List
    // -----------------------------------------------------------------------

    _renderGraphList() {
        const listEl = this.container.querySelector('.ogv-graph-list');
        const countEl = this.container.querySelector('.ogv-graph-count');

        if (!this._graphIndex || this._graphIndex.length === 0) {
            listEl.innerHTML = '<div style="padding:16px;text-align:center;color:#94a3b8;font-size:13px;">No graphs available</div>';
            countEl.textContent = '0 graphs';
            return;
        }

        countEl.textContent = `${this._graphIndex.length} graph${this._graphIndex.length !== 1 ? 's' : ''}`;

        listEl.innerHTML = this._graphIndex.map(g => {
            const checked = this._selectedGraphs.has(g.name) ? 'checked' : '';
            const nodeCount = g.node_count || 0;
            const edgeCount = g.edge_count || 0;
            const dominantType = g.dominant_type || 'concept';
            const badgeLabel = dominantType + '-heavy';
            return `<div class="ogv-graph-item ${checked ? 'ogv-graph-item--selected' : ''}" data-graph="${g.name}">
                <input type="checkbox" ${checked} />
                <div class="ogv-graph-info">
                    <div class="ogv-graph-name" title="${g.name}">${g.name}</div>
                    <div class="ogv-graph-meta">${nodeCount} nodes · ${edgeCount} edges</div>
                    <span class="ogv-dominant-badge ogv-dominant-badge--${dominantType}">${badgeLabel}</span>
                </div>
            </div>`;
        }).join('');

        // Bind checkbox events
        listEl.querySelectorAll('.ogv-graph-item').forEach(item => {
            const cb = item.querySelector('input[type="checkbox"]');
            const graphName = item.dataset.graph;

            item.addEventListener('click', (e) => {
                if (e.target !== cb) {
                    cb.checked = !cb.checked;
                }
                this._toggleGraph(graphName, cb.checked);
            });
        });
    }

    _updateGraphListCheckboxes() {
        const items = this.container.querySelectorAll('.ogv-graph-item');
        items.forEach(item => {
            const cb = item.querySelector('input[type="checkbox"]');
            const isSelected = this._selectedGraphs.has(item.dataset.graph);
            cb.checked = isSelected;
            item.classList.toggle('ogv-graph-item--selected', isSelected);
        });
        const selectAllCb = this.container.querySelector('.ogv-select-all-cb');
        if (selectAllCb) {
            selectAllCb.checked = this._selectedGraphs.size === this._graphIndex.length && this._graphIndex.length > 0;
        }
    }

    // -----------------------------------------------------------------------
    // Scope Pills
    // -----------------------------------------------------------------------

    _renderScopePills() {
        const bar = this.container.querySelector('.ogv-scope-bar');
        if (!bar) return;
        bar.innerHTML = '<span class="ogv-scope-label">SCOPE</span>';
        this._selectedGraphs.forEach(name => {
            this._addScopePillToBar(bar, name);
        });
        this._appendScopeAddBtn(bar);
    }

    _addScopePill(name) {
        const bar = this.container.querySelector('.ogv-scope-bar');
        if (!bar) return;
        if (bar.querySelector(`[data-scope="${name}"]`)) return;
        this._addScopePillToBar(bar, name);
    }

    _addScopePillToBar(bar, name) {
        const pill = document.createElement('span');
        pill.className = 'ogv-scope-pill';
        pill.dataset.scope = name;
        pill.innerHTML = `<span class="ogv-scope-pill-dot"></span>${name}<span class="ogv-scope-pill-close">&times;</span>`;

        pill.querySelector('.ogv-scope-pill-close').addEventListener('click', (e) => {
            e.stopPropagation();
            this._toggleGraph(name, false);
            this._updateGraphListCheckboxes();
        });

        bar.appendChild(pill);
    }

    _removeScopePill(name) {
        const bar = this.container.querySelector('.ogv-scope-bar');
        if (!bar) return;
        const pill = bar.querySelector(`[data-scope="${name}"]`);
        if (pill) pill.remove();
    }

    _appendScopeAddBtn(bar) {
        if (bar.querySelector('.ogv-scope-add-btn')) return;
        const btn = document.createElement('div');
        btn.className = 'ogv-scope-add-btn';
        btn.title = 'Add graph to scope';
        btn.textContent = '+';
        btn.addEventListener('click', () => {
            const selectAllCb = this.container.querySelector('.ogv-select-all-cb');
            if (selectAllCb && !selectAllCb.checked) {
                selectAllCb.checked = true;
                this._selectAll(true);
            }
        });
        bar.appendChild(btn);
    }

    _wireScopeBar() {
        const selectAllCb = this.container.querySelector('.ogv-select-all-cb');
        if (selectAllCb) {
            selectAllCb.addEventListener('change', () => {
                this._selectAll(selectAllCb.checked);
            });
        }
    }

    // -----------------------------------------------------------------------
    // Layout Picker
    // -----------------------------------------------------------------------

    _wireLayoutPicker(canvasArea) {
        const buttons = canvasArea.querySelectorAll('.ogv-layout-btn');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.canvas.runLayout(btn.dataset.layout);
                this._updateStats();
            });
        });
    }

    // -----------------------------------------------------------------------
    // Zoom Controls
    // -----------------------------------------------------------------------

    _wireZoomControls(canvasArea) {
        canvasArea.querySelectorAll('.ogv-zoom-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                if (action === 'in') this.canvas.zoomIn();
                else if (action === 'out') this.canvas.zoomOut();
                else if (action === 'fit') this.canvas.fitAll();
            });
        });
    }

    // -----------------------------------------------------------------------
    // Search
    // -----------------------------------------------------------------------

    _wireSearch() {
        const input = this.container.querySelector('.ogv-search-input');
        let debounceTimer = null;

        input.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(async () => {
                const query = input.value.trim();
                if (!query) {
                    this._clearDropdown();
                    this.canvas.clearHighlight();
                    this._lastSearchQuery = '';
                    this._updateSearchStatus(null);
                    return;
                }
                this._lastSearchQuery = query;
                const data = await this._searchBFS(query);
                if (!data) return; // aborted
                if (data.results && data.results.length > 0) {
                    this._renderDropdown(data.results);
                    this.canvas.highlightSubgraph(
                        data.subgraph ? data.subgraph.nodes : [],
                        data.results.map(r => r.node_id)
                    );
                    this._updateSearchStatus(data);
                } else {
                    this._renderDropdown([]);
                    this.canvas.clearHighlight();
                    this._updateSearchStatus(data);
                }
            }, 300);
        });

        input.addEventListener('keydown', (event) => {
            this._handleDropdownKeyboard(event);
        });

        // Close dropdown on click outside
        document.addEventListener('click', (e) => {
            if (this.container && !this.container.querySelector('.ogv-topbar')?.contains(e.target)) {
                this._clearDropdown();
            }
        });
    }

    // -----------------------------------------------------------------------
    // Node Selection Events
    // -----------------------------------------------------------------------

    _onNodeSelect(nodeId) {
        if (!this.canvas || !this.detailPanel) return;
        const nodeData = this.canvas.getNodeData(nodeId);
        if (!nodeData) return;
        const neighbors = this.canvas.getNeighborNodes(nodeId);
        const edges = this.canvas.getConnectedEdges(nodeId);
        this.detailPanel.open(nodeData, neighbors, edges);

        // Wire related node clicks in detail panel
        setTimeout(() => {
            const relNodes = this.container.querySelectorAll('.ogv-related-node');
            relNodes.forEach(el => {
                el.addEventListener('click', () => {
                    const targetId = el.dataset.nodeId;
                    this.canvas.focusNode(targetId);
                    this._onNodeSelect(targetId);
                });
            });

            // Wire source files click
            const srcLink = this.container.querySelector('.ogv-source-files-link');
            if (srcLink) {
                srcLink.addEventListener('click', () => {
                    try {
                        const files = JSON.parse(srcLink.dataset.files || '[]');
                        this._showSourceFilesModal(files, nodeData);
                    } catch (_e) { /* ignore parse error */ }
                });
            }
        }, 50);
    }

    _onNodeDeselect() {
        if (this.detailPanel) {
            this.detailPanel.close();
        }
    }

    // -----------------------------------------------------------------------
    // Source Files Modal
    // -----------------------------------------------------------------------

    _showSourceFilesModal(files, nodeData) {
        // Remove existing modal
        const old = document.body.querySelector('.folder-browser-backdrop.ogv-source-browser');
        if (old) old.remove();

        const label = nodeData.label || nodeData.id || 'Source Files';
        const filePaths = files.map(f =>
            typeof f === 'string' ? f : (f.path || f.name || String(f))
        );

        // Build DOM using folder-browser CSS classes (same as FolderBrowserModal)
        const backdrop = document.createElement('div');
        backdrop.className = 'folder-browser-backdrop ogv-source-browser';

        const modal = document.createElement('div');
        modal.className = 'folder-browser-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'ogv-source-browser-title');

        // Header
        const header = document.createElement('div');
        header.className = 'folder-browser-header';
        const title = document.createElement('div');
        title.className = 'folder-browser-title';
        title.id = 'ogv-source-browser-title';
        title.textContent = '📂 Source Files — ' + label;
        header.appendChild(title);
        const closeBtn = document.createElement('button');
        closeBtn.className = 'folder-browser-close';
        closeBtn.textContent = '✕';
        closeBtn.setAttribute('aria-label', 'Close');
        header.appendChild(closeBtn);
        modal.appendChild(header);

        // Breadcrumb
        const breadcrumb = document.createElement('div');
        breadcrumb.className = 'folder-browser-breadcrumb';
        const bcItem = document.createElement('span');
        bcItem.className = 'folder-browser-breadcrumb-item';
        bcItem.textContent = label;
        breadcrumb.appendChild(bcItem);
        const bcSep = document.createElement('span');
        bcSep.className = 'folder-browser-breadcrumb-sep';
        bcSep.textContent = ' / ';
        breadcrumb.appendChild(bcSep);
        const bcFiles = document.createElement('span');
        bcFiles.className = 'folder-browser-breadcrumb-item';
        bcFiles.textContent = `${filePaths.length} file${filePaths.length !== 1 ? 's' : ''}`;
        breadcrumb.appendChild(bcFiles);
        modal.appendChild(breadcrumb);

        // Body (two panels)
        const body = document.createElement('div');
        body.className = 'folder-browser-body';

        // Left: tree panel
        const treePanel = document.createElement('div');
        treePanel.className = 'folder-browser-tree';
        treePanel.setAttribute('tabindex', '0');

        const searchWrap = document.createElement('div');
        searchWrap.className = 'folder-browser-search';
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Filter files\u2026';
        searchInput.className = 'folder-browser-search-input';
        searchWrap.appendChild(searchInput);
        treePanel.appendChild(searchWrap);

        const treeContent = document.createElement('div');
        treeContent.className = 'folder-browser-tree-content';
        treePanel.appendChild(treeContent);
        body.appendChild(treePanel);

        // Right: preview panel
        const previewPanel = document.createElement('div');
        previewPanel.className = 'folder-browser-preview';
        previewPanel.setAttribute('tabindex', '0');
        const emptyMsg = document.createElement('div');
        emptyMsg.className = 'folder-browser-preview-empty';
        emptyMsg.textContent = 'Select a file to preview';
        previewPanel.appendChild(emptyMsg);
        body.appendChild(previewPanel);

        modal.appendChild(body);
        backdrop.appendChild(modal);

        // Build tree from flat file paths
        if (filePaths.length === 0) {
            const emptyTree = document.createElement('div');
            emptyTree.className = 'folder-browser-error';
            emptyTree.textContent = 'No source files available';
            treeContent.appendChild(emptyTree);
        } else {
            const tree = this._buildSourceFileTree(filePaths);
            treeContent.appendChild(tree);
            this._wireSourceTreeHandlers(tree, previewPanel);
        }

        // Search/filter
        let searchTimeout;
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = searchInput.value.toLowerCase().trim();
                const items = treeContent.querySelectorAll('.tree-item');
                if (!query) {
                    items.forEach(item => { item.style.display = ''; });
                    return;
                }
                items.forEach(item => {
                    const name = item.textContent.toLowerCase();
                    item.style.display = name.includes(query) ? '' : 'none';
                    // Show parent dirs of matching items
                    if (name.includes(query)) {
                        let parent = item.parentElement;
                        while (parent && parent !== treeContent) {
                            if (parent.tagName === 'LI') parent.style.display = '';
                            parent = parent.parentElement;
                        }
                    }
                });
            }, 200);
        });

        // Keyboard navigation in tree
        let focusedIdx = -1;
        treePanel.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                const items = Array.from(treeContent.querySelectorAll('.tree-item:not([style*="display: none"])'));
                if (!items.length) return;
                if (e.key === 'ArrowDown') focusedIdx = Math.min(focusedIdx + 1, items.length - 1);
                else focusedIdx = Math.max(focusedIdx - 1, 0);
                items.forEach((it, i) => it.classList.toggle('keyboard-focus', i === focusedIdx));
                items[focusedIdx]?.scrollIntoView?.({ block: 'nearest' });
            } else if (e.key === 'Enter') {
                const items = Array.from(treeContent.querySelectorAll('.tree-item:not([style*="display: none"])'));
                if (focusedIdx >= 0 && focusedIdx < items.length) items[focusedIdx].click();
            }
        });

        // Close handlers
        const closeFn = () => {
            backdrop.classList.remove('active');
            setTimeout(() => backdrop.remove(), 200);
            document.removeEventListener('keydown', onEsc);
        };
        const onEsc = (e) => { if (e.key === 'Escape') closeFn(); };
        closeBtn.addEventListener('click', closeFn);
        backdrop.addEventListener('click', (e) => { if (e.target === backdrop) closeFn(); });
        document.addEventListener('keydown', onEsc);

        document.body.appendChild(backdrop);
        document.body.style.overflow = 'hidden';
        requestAnimationFrame(() => backdrop.classList.add('active'));
    }

    /**
     * Build a nested tree DOM from flat file paths (e.g., ["docs/auth.md", "src/api.py"]).
     */
    _buildSourceFileTree(filePaths) {
        // Build a nested object: { dir: { subdir: { ... }, _files: [...] } }
        const root = {};
        for (const fp of filePaths) {
            const parts = fp.split('/');
            let node = root;
            for (let i = 0; i < parts.length - 1; i++) {
                if (!node[parts[i]]) node[parts[i]] = {};
                node = node[parts[i]];
            }
            if (!node._files) node._files = [];
            node._files.push({ name: parts[parts.length - 1], path: fp });
        }

        const FILE_ICONS = {
            md: '📝', py: '💻', js: '💻', ts: '💻', css: '💻', html: '💻',
            json: '💻', yaml: '💻', yml: '💻', sh: '💻',
            png: '🖼️', jpg: '🖼️', jpeg: '🖼️', gif: '🖼️', svg: '🖼️',
        };
        const getIcon = (name) => {
            const ext = name.split('.').pop()?.toLowerCase();
            return FILE_ICONS[ext] || '📄';
        };

        const buildUl = (obj) => {
            const ul = document.createElement('ul');
            ul.className = 'file-tree';
            ul.setAttribute('role', 'tree');

            // Directories first (sorted)
            const dirs = Object.keys(obj).filter(k => k !== '_files').sort();
            for (const dir of dirs) {
                const li = document.createElement('li');
                li.className = 'tree-item dir-item';
                li.setAttribute('role', 'treeitem');
                li.textContent = '📁 ' + dir;
                li.dataset.path = dir;
                li.style.cursor = 'pointer';
                const childUl = buildUl(obj[dir]);
                childUl.style.display = '';
                li.appendChild(childUl);
                // Toggle on click
                li.addEventListener('click', (e) => {
                    if (e.target !== li) return;
                    childUl.style.display = childUl.style.display === 'none' ? '' : 'none';
                });
                ul.appendChild(li);
            }

            // Files (sorted)
            const fileList = obj._files || [];
            for (const f of fileList.sort((a, b) => a.name.localeCompare(b.name))) {
                const li = document.createElement('li');
                li.className = 'tree-item file-item';
                li.setAttribute('role', 'treeitem');
                li.textContent = getIcon(f.name) + ' ' + f.name;
                li.dataset.path = f.path;
                li.style.cursor = 'pointer';
                ul.appendChild(li);
            }

            return ul;
        };

        return buildUl(root);
    }

    /**
     * Wire click handlers on tree file items to load file preview.
     */
    _wireSourceTreeHandlers(tree, previewPanel) {
        tree.querySelectorAll('.file-item[data-path]').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                // Mark selected
                const prev = tree.querySelector('.tree-item.selected');
                if (prev) prev.classList.remove('selected');
                item.classList.add('selected');
                this._loadSourceFilePreview(item.dataset.path, previewPanel);
            });
        });
    }

    /**
     * Load and render file content in the preview panel.
     */
    async _loadSourceFilePreview(filePath, previewPanel) {
        previewPanel.innerHTML = '';

        // Preview header
        const previewHeader = document.createElement('div');
        previewHeader.className = 'folder-browser-preview-header';
        const nameSpan = document.createElement('span');
        nameSpan.className = 'folder-browser-preview-title';
        nameSpan.textContent = filePath.split('/').pop();
        previewHeader.appendChild(nameSpan);
        previewPanel.appendChild(previewHeader);

        const contentEl = document.createElement('div');
        contentEl.className = 'folder-browser-preview-content';
        previewPanel.appendChild(contentEl);

        // Use FilePreviewRenderer if available (shared with FolderBrowserModal)
        if (typeof FilePreviewRenderer !== 'undefined') {
            const renderer = new FilePreviewRenderer({
                apiEndpoint: '/api/ideas/file?path={path}',
                endpointStyle: 'query',
                downloadUrl: '/api/ideas/file?path={path}',
                renderMode: 'auto',
            });
            await renderer.renderPreview(filePath, contentEl);
            return;
        }

        // Fallback: fetch and render manually
        try {
            const resp = await fetch(`/api/ideas/file?path=${encodeURIComponent(filePath)}`);
            if (!resp.ok) {
                contentEl.textContent = resp.status === 404 ? 'File not found' : 'Failed to load preview';
                return;
            }
            const content = await resp.text();
            if (filePath.endsWith('.md') && typeof marked !== 'undefined' && marked.parse) {
                contentEl.innerHTML = '<div class="markdown-body">' + marked.parse(content) + '</div>';
            } else {
                const pre = document.createElement('pre');
                pre.textContent = content;
                contentEl.appendChild(pre);
            }
        } catch (err) {
            contentEl.textContent = 'Failed to load preview';
        }
    }

    // -----------------------------------------------------------------------
    // Navigator refresh
    // -----------------------------------------------------------------------

    _refreshNav() {
        if (this.canvas && typeof this.canvas.refreshNavigator === 'function') {
            setTimeout(() => this.canvas.refreshNavigator(), 300);
        }
    }

    // -----------------------------------------------------------------------
    // Status & Messaging
    // -----------------------------------------------------------------------

    _updateStats() {
        if (!this.canvas || !this.container) return;
        const stats = this.canvas.getStats();
        const nodesEl = this.container.querySelector('.ogv-status-nodes');
        const edgesEl = this.container.querySelector('.ogv-status-edges');
        const layoutEl = this.container.querySelector('.ogv-status-layout');
        const zoomEl = this.container.querySelector('.ogv-status-zoom');
        const scopeEl = this.container.querySelector('.ogv-status-scope-count');
        if (nodesEl) nodesEl.textContent = `${stats.nodes} node${stats.nodes !== 1 ? 's' : ''}`;
        if (edgesEl) edgesEl.textContent = `${stats.edges} edge${stats.edges !== 1 ? 's' : ''}`;

        // Layout name mapping
        const layoutNames = { fcose: 'Force-directed', dagre: 'Hierarchical', concentric: 'Radial' };
        const currentLayout = this.canvas.currentLayout || 'fcose';
        if (layoutEl) layoutEl.textContent = `Layout: ${layoutNames[currentLayout] || currentLayout}`;

        // Zoom percentage
        if (zoomEl && this.canvas.cy) {
            const pct = Math.round(this.canvas.cy.zoom() * 100);
            zoomEl.textContent = `Zoom: ${pct}%`;
        }

        // Scope count
        if (scopeEl) {
            const count = this._selectedGraphs.size;
            scopeEl.textContent = count > 0 ? `${count} graph${count !== 1 ? 's' : ''} in scope` : '';
        }
    }

    _updateSearchStatus(data) {
        if (!this.container) return;
        let searchEl = this.container.querySelector('.ogv-status-search');
        if (!data) {
            if (searchEl) searchEl.remove();
            return;
        }
        if (!searchEl) {
            const statusBar = this.container.querySelector('.ogv-status-bar');
            if (!statusBar) return;
            const sep = document.createElement('span');
            sep.className = 'ogv-status-sep ogv-status-search-sep';
            sep.textContent = '·';
            statusBar.appendChild(sep);
            searchEl = document.createElement('span');
            searchEl.className = 'ogv-status-search';
            statusBar.appendChild(searchEl);
        }
        const matches = data.results ? data.results.length : 0;
        const related = data.subgraph ? data.subgraph.nodes.length - matches : 0;
        searchEl.textContent = `Search: ${matches} match${matches !== 1 ? 'es' : ''}${related > 0 ? ` · ${related} related` : ''}`;
    }

    _updateStatus(text) {
        if (!this.container) return;
        const el = this.container.querySelector('.ogv-status-text');
        if (el) el.textContent = text;
        // Also update layout/zoom on every status update
        this._updateStats();
    }

    _showEmptyState(title, message) {
        const canvasArea = this.container.querySelector('.ogv-canvas-area');
        if (!canvasArea) return;
        const existing = canvasArea.querySelector('.ogv-empty-state');
        if (existing) existing.remove();

        const el = document.createElement('div');
        el.className = 'ogv-empty-state';
        el.innerHTML = `
            <div class="ogv-empty-icon"><i class="bi bi-diagram-3"></i></div>
            <div class="ogv-empty-title">${title}</div>
            <div class="ogv-empty-message">${message}</div>`;
        canvasArea.appendChild(el);
    }

    _showError(message) {
        const canvasArea = this.container.querySelector('.ogv-canvas-area');
        if (!canvasArea) return;
        const toast = document.createElement('div');
        toast.className = 'ogv-error-toast';
        toast.textContent = message;
        canvasArea.appendChild(toast);
        setTimeout(() => toast.remove(), 5000);
    }

    // -----------------------------------------------------------------------
    // Cleanup
    // -----------------------------------------------------------------------

    destroy() {
        this._destroyed = true;
        if (this._searchAbortController) {
            this._searchAbortController.abort();
            this._searchAbortController = null;
        }
        if (this.canvas) {
            this.canvas.destroy();
            this.canvas = null;
        }
        this.detailPanel = null;
        if (this.container) {
            this.container.innerHTML = '';
        }
        this._selectedGraphs.clear();
        this._graphIndex = [];
        this._lastSearchQuery = '';
    }
}

// Export to global scope
window.OntologyGraphViewer = OntologyGraphViewer;
