/**
 * FEATURE-058-E: Ontology Graph Canvas — Cytoscape.js Core
 *
 * Manages Cytoscape.js instance, layouts, context menu, tooltips,
 * navigator minimap, and detail panel display.
 */

/* global cytoscape, tippy */

class OntologyGraphCanvas {
    constructor(containerEl, options = {}) {
        this.container = containerEl;
        this.onNodeSelect = options.onNodeSelect || (() => {});
        this.onNodeDeselect = options.onNodeDeselect || (() => {});
        this.cy = null;
        this._navigator = null;
        this._tippyInstances = [];
        this._currentLayout = 'fcose';
    }

    // -----------------------------------------------------------------------
    // Initialization
    // -----------------------------------------------------------------------

    init() {
        this.cy = cytoscape({
            container: this.container,
            elements: [],
            style: this._getStylesheet(),
            minZoom: 0.1,
            maxZoom: 5,
            wheelSensitivity: 0.3,
            boxSelectionEnabled: false,
        });

        this._attachEvents();
        this._initContextMenu();
    }

    // -----------------------------------------------------------------------
    // Data Loading
    // -----------------------------------------------------------------------

    setElements(elements) {
        if (!this.cy) return;
        this.cy.elements().remove();
        if (elements && elements.length > 0) {
            this.cy.add(elements);
            this.runLayout(this._currentLayout);
        }
    }

    addElements(elements) {
        if (!this.cy || !elements || elements.length === 0) return;
        const existing = new Set(this.cy.nodes().map(n => n.id()));
        const newEls = elements.filter(el => {
            if (el.group === 'nodes') return !existing.has(el.data.id);
            if (el.group === 'edges') {
                const srcExists = existing.has(el.data.source) || elements.some(e => e.group === 'nodes' && e.data.id === el.data.source);
                const tgtExists = existing.has(el.data.target) || elements.some(e => e.group === 'nodes' && e.data.id === el.data.target);
                return srcExists && tgtExists;
            }
            return true;
        });
        if (newEls.length > 0) {
            this.cy.add(newEls);
            this.runLayout(this._currentLayout);
        }
    }

    removeGraphElements(graphName) {
        if (!this.cy) return;
        this.cy.elements(`[_graph = "${graphName}"]`).remove();
    }

    // -----------------------------------------------------------------------
    // Layout
    // -----------------------------------------------------------------------

    runLayout(name) {
        if (!this.cy || this.cy.nodes().length === 0) return;
        this._currentLayout = name;
        const config = this._getLayoutConfig(name);
        const layout = this.cy.layout(config);
        layout.run();
    }

    _getLayoutConfig(name) {
        switch (name) {
            case 'dagre':
                return {
                    name: 'dagre',
                    rankDir: 'TB',
                    rankSep: 60,
                    nodeSep: 40,
                    animate: false,
                    fit: true,
                    padding: 50,
                };
            case 'concentric':
                return {
                    name: 'concentric',
                    concentric: (node) => node.data('weight') || 1,
                    levelWidth: () => 2,
                    animate: false,
                    fit: true,
                    padding: 50,
                    minNodeSpacing: 60,
                };
            case 'fcose':
            default:
                return {
                    name: 'fcose',
                    quality: 'default',
                    randomize: true,
                    animate: false,
                    fit: true,
                    padding: 50,
                    nodeRepulsion: 8000,
                    idealEdgeLength: 120,
                    edgeElasticity: 0.45,
                    nestingFactor: 0.1,
                    gravity: 0.25,
                    numIter: 2500,
                };
        }
    }

    get currentLayout() {
        return this._currentLayout;
    }

    // -----------------------------------------------------------------------
    // Node Operations
    // -----------------------------------------------------------------------

    highlightNode(nodeId) {
        if (!this.cy) return;
        this.cy.elements().removeClass('highlighted dimmed');
        const node = this.cy.getElementById(nodeId);
        if (!node || node.empty()) return;

        const neighborhood = node.neighborhood().add(node);
        neighborhood.addClass('highlighted');
        this.cy.elements().not(neighborhood).addClass('dimmed');
    }

    clearHighlight() {
        if (!this.cy) return;
        this.cy.elements().removeClass('highlighted dimmed');
    }

    focusNode(nodeId) {
        if (!this.cy) return;
        const node = this.cy.getElementById(nodeId);
        if (!node || node.empty()) return;
        this.cy.animate({
            center: { eles: node },
            zoom: 2,
        }, { duration: 400 });
        this.highlightNode(nodeId);
    }

    getNodeData(nodeId) {
        if (!this.cy) return null;
        const node = this.cy.getElementById(nodeId);
        if (!node || node.empty()) return null;
        return node.data();
    }

    getConnectedEdges(nodeId) {
        if (!this.cy) return [];
        const node = this.cy.getElementById(nodeId);
        if (!node || node.empty()) return [];
        return node.connectedEdges().map(edge => ({
            id: edge.id(),
            source: edge.data('source'),
            target: edge.data('target'),
            rel: edge.data('rel') || edge.data('label') || '',
        }));
    }

    getNeighborNodes(nodeId) {
        if (!this.cy) return [];
        const node = this.cy.getElementById(nodeId);
        if (!node || node.empty()) return [];
        return node.neighborhood('node').map(n => ({
            id: n.id(),
            label: n.data('label'),
            node_type: n.data('node_type'),
        }));
    }

    // -----------------------------------------------------------------------
    // Zoom
    // -----------------------------------------------------------------------

    zoomIn() {
        if (!this.cy) return;
        this.cy.zoom({ level: this.cy.zoom() * 1.3, renderedPosition: this._center() });
    }

    zoomOut() {
        if (!this.cy) return;
        this.cy.zoom({ level: this.cy.zoom() / 1.3, renderedPosition: this._center() });
    }

    fitAll() {
        if (!this.cy) return;
        this.cy.fit(undefined, 50);
    }

    _center() {
        const w = this.container.clientWidth;
        const h = this.container.clientHeight;
        return { x: w / 2, y: h / 2 };
    }

    // -----------------------------------------------------------------------
    // Navigator Minimap
    // -----------------------------------------------------------------------

    initNavigator(navContainer) {
        if (!this.cy || !navContainer) return;
        if (typeof this.cy.navigator === 'function') {
            this._navigator = this.cy.navigator({
                container: navContainer,
                viewLiveFramerate: 0,
                thumbnailLiveFramerate: false,
                dblClickDelay: 200,
            });
        }
    }

    // -----------------------------------------------------------------------
    // Context Menu
    // -----------------------------------------------------------------------

    _initContextMenu() {
        if (!this.cy || typeof this.cy.cxtmenu !== 'function') return;
        this.cy.cxtmenu({
            selector: 'node',
            commands: [
                {
                    content: '<i class="bi bi-info-circle"></i>',
                    select: (ele) => this.onNodeSelect(ele.id()),
                },
                {
                    content: '<i class="bi bi-crosshair"></i>',
                    select: (ele) => this.focusNode(ele.id()),
                },
                {
                    content: '<i class="bi bi-eye-slash"></i>',
                    select: (ele) => {
                        ele.addClass('dimmed');
                        ele.connectedEdges().addClass('dimmed');
                    },
                },
            ],
            fillColor: 'rgba(15, 23, 42, 0.85)',
            activeFillColor: '#10b981',
            activePadding: 10,
            indicatorSize: 12,
            separatorWidth: 3,
            spotlightPadding: 4,
            adaptativeNodeSpotlightRadius: true,
            minSpotlightRadius: 24,
            maxSpotlightRadius: 38,
            itemTextShadowColor: 'transparent',
        });
    }

    // -----------------------------------------------------------------------
    // Events
    // -----------------------------------------------------------------------

    _attachEvents() {
        this.cy.on('tap', 'node', (evt) => {
            const nodeId = evt.target.id();
            this.highlightNode(nodeId);
            this.onNodeSelect(nodeId);
        });

        this.cy.on('tap', (evt) => {
            if (evt.target === this.cy) {
                this.clearHighlight();
                this.onNodeDeselect();
            }
        });

        // Tooltips on hover
        this.cy.on('mouseover', 'node', (evt) => {
            this._showTooltip(evt.target);
        });

        this.cy.on('mouseout', 'node', () => {
            this._hideTooltips();
        });
    }

    _showTooltip(node) {
        this._hideTooltips();
        if (typeof tippy === 'undefined') return;

        const pos = node.renderedPosition();
        const container = this.cy.container();
        const rect = container.getBoundingClientRect();
        const dummy = document.createElement('div');
        dummy.style.position = 'fixed';
        dummy.style.left = `${rect.left + pos.x}px`;
        dummy.style.top = `${rect.top + pos.y}px`;
        dummy.style.width = '1px';
        dummy.style.height = '1px';
        dummy.style.pointerEvents = 'none';
        document.body.appendChild(dummy);

        const t = tippy(dummy, {
            content: `<strong>${node.data('label') || node.id()}</strong><br><span style="font-size:11px;color:#94a3b8;">${node.data('node_type') || 'node'}</span>`,
            allowHTML: true,
            placement: 'top',
            animation: false,
            appendTo: document.body,
            theme: 'light',
            showOnCreate: true,
            onHidden: () => { dummy.remove(); },
        });
        this._tippyInstances.push(t);
    }

    _hideTooltips() {
        this._tippyInstances.forEach(t => {
            try { t.destroy(); } catch (_e) { /* ignore */ }
        });
        this._tippyInstances = [];
    }

    // -----------------------------------------------------------------------
    // Cytoscape.js Stylesheet
    // -----------------------------------------------------------------------

    _getStylesheet() {
        return [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'font-family': 'Outfit, sans-serif',
                    'font-size': '11px',
                    'font-weight': 500,
                    'color': '#0f172a',
                    'text-wrap': 'ellipsis',
                    'text-max-width': '90px',
                    'width': 'mapData(weight, 1, 10, 32, 72)',
                    'height': 'mapData(weight, 1, 10, 32, 72)',
                    'background-color': '#94a3b8',
                    'border-width': 2,
                    'border-color': '#ffffff',
                    'text-outline-color': '#ffffff',
                    'text-outline-width': 2,
                    'overlay-padding': 6,
                },
            },
            // Node type colors
            { selector: 'node[node_type = "concept"]', style: { 'background-color': '#10b981' } },
            { selector: 'node[node_type = "document"]', style: { 'background-color': '#3b82f6' } },
            { selector: 'node[node_type = "entity"]', style: { 'background-color': '#f59e0b' } },
            { selector: 'node[node_type = "dimension"]', style: { 'background-color': '#8b5cf6' } },

            // Highlighted & dimmed states
            {
                selector: 'node.highlighted',
                style: {
                    'border-width': 4,
                    'border-color': '#0f172a',
                    'z-index': 10,
                },
            },
            {
                selector: '.dimmed',
                style: { 'opacity': 0.15 },
            },

            // Edge styles
            {
                selector: 'edge',
                style: {
                    'width': 1.5,
                    'line-color': '#cbd5e1',
                    'target-arrow-color': '#cbd5e1',
                    'target-arrow-shape': 'triangle',
                    'arrow-scale': 0.8,
                    'curve-style': 'bezier',
                    'label': 'data(label)',
                    'font-family': 'JetBrains Mono, monospace',
                    'font-size': '9px',
                    'color': '#94a3b8',
                    'text-rotation': 'autorotate',
                    'text-outline-color': '#f8fafc',
                    'text-outline-width': 2,
                },
            },
            {
                selector: 'edge.highlighted',
                style: {
                    'width': 2.5,
                    'line-color': '#10b981',
                    'target-arrow-color': '#10b981',
                    'z-index': 10,
                },
            },
        ];
    }

    // -----------------------------------------------------------------------
    // Stats
    // -----------------------------------------------------------------------

    getStats() {
        if (!this.cy) return { nodes: 0, edges: 0 };
        return {
            nodes: this.cy.nodes().length,
            edges: this.cy.edges().length,
        };
    }

    // -----------------------------------------------------------------------
    // Cleanup
    // -----------------------------------------------------------------------

    destroy() {
        this._hideTooltips();
        if (this._navigator) {
            try { this._navigator.destroy(); } catch (_e) { /* ignore */ }
            this._navigator = null;
        }
        if (this.cy) {
            this.cy.destroy();
            this.cy = null;
        }
    }
}

// ---------------------------------------------------------------------------
// Detail Panel Helper
// ---------------------------------------------------------------------------

class OntologyDetailPanel {
    constructor(panelEl) {
        this.panel = panelEl;
    }

    open(nodeData, neighbors, edges) {
        if (!this.panel) return;
        this.panel.classList.add('open');
        const inner = this.panel.querySelector('.ogv-detail-inner');
        if (!inner) return;

        const nodeType = nodeData.node_type || 'node';
        const description = nodeData.description || 'No description available.';
        const dims = nodeData.dimensions || {};
        const sourceFiles = nodeData.source_files || [];

        let dimsHtml = '';
        for (const [key, values] of Object.entries(dims)) {
            if (Array.isArray(values) && values.length > 0) {
                const tagsHtml = values.map(v =>
                    `<span class="ogv-dim-tag ogv-dim-tag--${key}">${v}</span>`
                ).join('');
                dimsHtml += `<div class="ogv-dim-group">
                    <div class="ogv-dim-label">${key}</div>
                    <div class="ogv-dim-tags">${tagsHtml}</div>
                </div>`;
            }
        }

        let relatedHtml = '';
        if (neighbors && neighbors.length > 0) {
            relatedHtml = neighbors.map(n => {
                const edge = edges.find(e =>
                    (e.source === nodeData.id && e.target === n.id) ||
                    (e.target === nodeData.id && e.source === n.id)
                );
                const rel = edge ? edge.rel : '';
                return `<div class="ogv-related-node" data-node-id="${n.id}">
                    <span class="ogv-type-badge ogv-type-badge--${n.node_type || 'concept'}"></span>
                    <span class="ogv-related-node-name">${n.label || n.id}</span>
                    <span class="ogv-related-node-rel">${rel}</span>
                </div>`;
            }).join('');
        }

        let sourceHtml = '';
        if (sourceFiles.length > 0) {
            sourceHtml = `<div class="ogv-detail-section">
                <div class="ogv-detail-section-title">Source Files</div>
                <div class="ogv-source-files-link" data-files='${JSON.stringify(sourceFiles)}'>
                    <i class="bi bi-folder2-open"></i>
                    ${sourceFiles.length} source file${sourceFiles.length !== 1 ? 's' : ''}
                </div>
            </div>`;
        }

        inner.innerHTML = `
            <div class="ogv-detail-header">
                <div class="ogv-detail-header-info">
                    <div class="ogv-detail-node-name">${nodeData.label || nodeData.id}</div>
                    <div class="ogv-detail-node-id">${nodeData.id}</div>
                </div>
                <button class="ogv-detail-close" title="Close">&times;</button>
            </div>
            <div class="ogv-detail-section">
                <div class="ogv-detail-section-title">Type</div>
                <div style="display:flex;align-items:center;gap:6px;">
                    <span class="ogv-type-badge ogv-type-badge--${nodeType}"></span>
                    <span style="font-size:13px;font-weight:500;text-transform:capitalize;">${nodeType}</span>
                </div>
            </div>
            <div class="ogv-detail-section">
                <div class="ogv-detail-section-title">Description</div>
                <div class="ogv-detail-description">${description}</div>
            </div>
            ${dimsHtml ? `<div class="ogv-detail-section"><div class="ogv-detail-section-title">Dimensions</div>${dimsHtml}</div>` : ''}
            ${sourceHtml}
            ${relatedHtml ? `<div class="ogv-detail-section"><div class="ogv-detail-section-title">Related Nodes</div>${relatedHtml}</div>` : ''}
            <div class="ogv-detail-section">
                <div class="ogv-detail-section-title">Metadata</div>
                <div class="ogv-metadata-grid">
                    <div class="ogv-metadata-item">
                        <div class="ogv-metadata-label">Weight</div>
                        <div class="ogv-metadata-value">${nodeData.weight || 1}</div>
                    </div>
                    <div class="ogv-metadata-item">
                        <div class="ogv-metadata-label">Connections</div>
                        <div class="ogv-metadata-value">${(neighbors || []).length}</div>
                    </div>
                    ${nodeData.graph ? `<div class="ogv-metadata-item">
                        <div class="ogv-metadata-label">Graph</div>
                        <div class="ogv-metadata-value">${nodeData.graph}</div>
                    </div>` : ''}
                </div>
            </div>`;

        // Bind close button
        const closeBtn = inner.querySelector('.ogv-detail-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }
    }

    close() {
        if (this.panel) {
            this.panel.classList.remove('open');
        }
    }

    isOpen() {
        return this.panel ? this.panel.classList.contains('open') : false;
    }
}

// Export to global scope
window.OntologyGraphCanvas = OntologyGraphCanvas;
window.OntologyDetailPanel = OntologyDetailPanel;
