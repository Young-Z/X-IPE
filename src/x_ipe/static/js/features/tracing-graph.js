/**
 * FEATURE-023-C: Trace Viewer & DAG Visualization
 * 
 * Graph visualization component for trace data using G6 by AntV.
 * Creates interactive DAG showing function call hierarchy with timing.
 */

// =============================================================================
// TracingGraphView - DAG Visualization Component
// =============================================================================

// Static flag to track if custom G6 nodes/edges have been registered
let _g6CustomTypesRegistered = false;

class TracingGraphView {
    /**
     * Create a new TracingGraphView
     * @param {HTMLElement} container - Container element for the graph
     * @param {Object} options - Configuration options
     */
    constructor(container, options = {}) {
        this.container = container;
        this.graph = null;
        this.data = null;
        this.selectedNode = null;
        this.modal = null;
        
        // Default options
        this.options = {
            onNodeClick: options.onNodeClick || null,
            minZoom: options.minZoom || 0.2,
            maxZoom: options.maxZoom || 3,
            fitCenter: options.fitCenter !== false,
            animate: options.animate !== false,
            ...options
        };
    }

    // -------------------------------------------------------------------------
    // Graph Lifecycle
    // -------------------------------------------------------------------------

    /**
     * Initialize the graph visualization
     */
    init() {
        if (!this.container) {
            console.error('[TracingGraphView] Container not found');
            return;
        }

        // Clear existing graph
        if (this.graph) {
            this.graph.destroy();
            this.graph = null;
        }

        const { width, height } = this.getContainerSize();

        // Initialize G6 graph with dagre layout
        this.graph = new G6.Graph({
            container: this.container,
            width,
            height,
            fitView: this.options.fitCenter,
            fitViewPadding: 40,
            minZoom: this.options.minZoom,
            maxZoom: this.options.maxZoom,
            modes: {
                default: ['drag-canvas', 'zoom-canvas', 'drag-node']
            },
            layout: {
                type: 'dagre',
                rankdir: 'LR',       // Left to right
                align: 'UL',
                nodesep: 30,         // Node separation
                ranksep: 80,         // Rank separation
                controlPoints: true
            },
            defaultNode: {
                type: 'trace-node',
                size: [180, 60]
            },
            defaultEdge: {
                type: 'trace-edge',
                style: {
                    lineWidth: 2,
                    endArrow: {
                        path: G6.Arrow.triangle(6, 8, 0),
                        fill: '#aab7c4'
                    }
                }
            }
        });

        // Register custom node and edge (only once globally)
        if (!_g6CustomTypesRegistered) {
            this.registerCustomNode();
            this.registerCustomEdge();
            _g6CustomTypesRegistered = true;
        }
        
        // Bind events
        this.bindEvents();
    }

    /**
     * Destroy the graph and cleanup
     */
    destroy() {
        if (this.modal) {
            this.modal.close();
            this.modal = null;
        }
        if (this.graph) {
            this.graph.destroy();
            this.graph = null;
        }
    }

    // -------------------------------------------------------------------------
    // Custom Node Registration
    // -------------------------------------------------------------------------

    registerCustomNode() {
        G6.registerNode('trace-node', {
            draw(cfg, group) {
                const { label, timing, status, level, error } = cfg;
                const width = 180;
                const height = 60;
                
                // Determine colors based on status and level
                const isError = status === 'error';
                const isApi = level === 'API';
                
                let bgColor = '#ffffff';
                let borderColor = '#d0d7de';
                let labelColor = '#1f2328';
                let timingColor = '#656d76';
                
                if (isError) {
                    bgColor = '#ffebe9';
                    borderColor = '#ff8182';
                    labelColor = '#cf222e';
                }
                if (isApi) {
                    bgColor = isError ? '#ffebe9' : '#ddf4ff';
                    borderColor = isError ? '#ff8182' : '#54aeff';
                    labelColor = isError ? '#cf222e' : '#0969da';
                }
                
                // Main rectangle
                const shape = group.addShape('rect', {
                    attrs: {
                        x: -width / 2,
                        y: -height / 2,
                        width,
                        height,
                        radius: 8,
                        fill: bgColor,
                        stroke: borderColor,
                        lineWidth: 2,
                        cursor: 'pointer',
                        shadowColor: 'rgba(0,0,0,0.1)',
                        shadowBlur: 4,
                        shadowOffsetY: 2
                    },
                    name: 'main-box'
                });
                
                // Function name
                const displayLabel = label.length > 20 ? label.substring(0, 17) + '...' : label;
                group.addShape('text', {
                    attrs: {
                        x: 0,
                        y: -8,
                        text: displayLabel,
                        fontSize: 13,
                        fontWeight: 600,
                        fill: labelColor,
                        textAlign: 'center',
                        textBaseline: 'middle',
                        cursor: 'pointer'
                    },
                    name: 'label'
                });
                
                // Timing badge
                if (timing) {
                    group.addShape('text', {
                        attrs: {
                            x: 0,
                            y: 14,
                            text: timing,
                            fontSize: 11,
                            fill: timingColor,
                            textAlign: 'center',
                            textBaseline: 'middle'
                        },
                        name: 'timing'
                    });
                }
                
                // Error indicator
                if (isError && error) {
                    group.addShape('text', {
                        attrs: {
                            x: width / 2 - 16,
                            y: -height / 2 + 12,
                            text: '⚠',
                            fontSize: 12,
                            fill: '#cf222e',
                            textAlign: 'center'
                        },
                        name: 'error-icon'
                    });
                }
                
                // Level badge (for non-API nodes)
                if (!isApi) {
                    const badgeColor = level === 'DEBUG' ? '#8250df' : '#2da44e';
                    group.addShape('rect', {
                        attrs: {
                            x: -width / 2 + 6,
                            y: -height / 2 + 6,
                            width: level === 'DEBUG' ? 42 : 32,
                            height: 16,
                            radius: 3,
                            fill: badgeColor
                        },
                        name: 'level-badge-bg'
                    });
                    group.addShape('text', {
                        attrs: {
                            x: -width / 2 + (level === 'DEBUG' ? 27 : 22),
                            y: -height / 2 + 14,
                            text: level,
                            fontSize: 9,
                            fontWeight: 500,
                            fill: '#ffffff',
                            textAlign: 'center',
                            textBaseline: 'middle'
                        },
                        name: 'level-badge'
                    });
                }
                
                return shape;
            },
            
            setState(name, value, item) {
                const group = item.getContainer();
                const mainBox = group.find(e => e.get('name') === 'main-box');
                
                if (name === 'hover') {
                    if (value) {
                        mainBox.attr('shadowBlur', 8);
                        mainBox.attr('shadowOffsetY', 4);
                    } else {
                        mainBox.attr('shadowBlur', 4);
                        mainBox.attr('shadowOffsetY', 2);
                    }
                }
                
                if (name === 'selected') {
                    const cfg = item.getModel();
                    const isError = cfg.status === 'error';
                    const isApi = cfg.level === 'API';
                    
                    if (value) {
                        mainBox.attr('lineWidth', 3);
                        mainBox.attr('stroke', isError ? '#cf222e' : (isApi ? '#0969da' : '#1f883d'));
                    } else {
                        mainBox.attr('lineWidth', 2);
                        mainBox.attr('stroke', isError ? '#ff8182' : (isApi ? '#54aeff' : '#d0d7de'));
                    }
                }
            }
        }, 'single-node');
    }

    // -------------------------------------------------------------------------
    // Custom Edge Registration
    // -------------------------------------------------------------------------

    registerCustomEdge() {
        G6.registerEdge('trace-edge', {
            draw(cfg, group) {
                const startPoint = cfg.startPoint;
                const endPoint = cfg.endPoint;
                const controlPoints = cfg.controlPoints || [];
                
                // Build path through control points
                let path = [['M', startPoint.x, startPoint.y]];
                
                if (controlPoints.length > 0) {
                    controlPoints.forEach(cp => {
                        path.push(['L', cp.x, cp.y]);
                    });
                }
                
                path.push(['L', endPoint.x, endPoint.y]);
                
                // Get source node status for edge color
                const sourceNode = cfg.sourceNode;
                const model = sourceNode ? sourceNode.getModel() : {};
                const isError = model.status === 'error';
                
                const shape = group.addShape('path', {
                    attrs: {
                        path,
                        stroke: isError ? '#ff8182' : '#aab7c4',
                        lineWidth: 2,
                        endArrow: {
                            path: G6.Arrow.triangle(6, 8, 0),
                            fill: isError ? '#ff8182' : '#aab7c4'
                        }
                    },
                    name: 'edge-path'
                });
                
                return shape;
            },
            
            setState(name, value, item) {
                const group = item.getContainer();
                const edgePath = group.find(e => e.get('name') === 'edge-path');
                
                if (name === 'highlight') {
                    if (value) {
                        edgePath.attr('lineWidth', 3);
                        edgePath.attr('stroke', '#0969da');
                    } else {
                        const model = item.getSource().getModel();
                        const isError = model.status === 'error';
                        edgePath.attr('lineWidth', 2);
                        edgePath.attr('stroke', isError ? '#ff8182' : '#aab7c4');
                    }
                }
            }
        }, 'polyline');
    }

    // -------------------------------------------------------------------------
    // Event Binding
    // -------------------------------------------------------------------------

    bindEvents() {
        if (!this.graph) return;
        
        // Node hover
        this.graph.on('node:mouseenter', (evt) => {
            this.graph.setItemState(evt.item, 'hover', true);
            this.container.style.cursor = 'pointer';
        });
        
        this.graph.on('node:mouseleave', (evt) => {
            this.graph.setItemState(evt.item, 'hover', false);
            this.container.style.cursor = 'default';
        });
        
        // Node click
        this.graph.on('node:click', (evt) => {
            const node = evt.item;
            const model = node.getModel();
            
            // Deselect previous
            if (this.selectedNode) {
                this.graph.setItemState(this.selectedNode, 'selected', false);
            }
            
            // Select new
            this.graph.setItemState(node, 'selected', true);
            this.selectedNode = node;
            
            // Show modal or callback
            if (this.options.onNodeClick) {
                this.options.onNodeClick(model);
            } else {
                this.showNodeModal(model);
            }
        });
        
        // Canvas click (deselect)
        this.graph.on('canvas:click', () => {
            if (this.selectedNode) {
                this.graph.setItemState(this.selectedNode, 'selected', false);
                this.selectedNode = null;
            }
        });
        
        // Window resize
        window.addEventListener('resize', this.handleResize.bind(this));
    }

    // -------------------------------------------------------------------------
    // Data Loading
    // -------------------------------------------------------------------------

    /**
     * Load trace data from API
     * @param {string} traceId - Trace ID to load
     */
    async loadTrace(traceId) {
        this.showLoading();
        
        try {
            const response = await fetch(`/api/tracing/logs/${encodeURIComponent(traceId)}`);
            
            if (!response.ok) {
                if (response.status === 404) {
                    this.showError('Trace not found');
                } else {
                    throw new Error(`API error: ${response.status}`);
                }
                return;
            }
            
            const data = await response.json();
            this.data = data;
            this.renderGraph(data);
            
        } catch (error) {
            console.error('[TracingGraphView] Load error:', error);
            this.showError('Failed to load trace data');
        }
    }

    /**
     * Load trace data directly (without API call)
     * @param {Object} data - Pre-loaded trace data
     */
    setData(data) {
        this.data = data;
        if (!this.graph) {
            this.init();
        }
        this.renderGraph(data);
    }

    // -------------------------------------------------------------------------
    // Graph Rendering
    // -------------------------------------------------------------------------

    renderGraph(data) {
        if (!data) return;
        
        // Clear any loading/empty state and re-initialize graph
        // (showLoading/showEmpty may have replaced the container's innerHTML)
        this.container.innerHTML = '';
        
        // Reset selected node reference (old node belongs to destroyed graph)
        this.selectedNode = null;
        
        // Close any existing modal
        if (this.modal) {
            this.modal.close();
            this.modal = null;
        }
        
        // Destroy existing graph if any (may fail if DOM was already cleared)
        if (this.graph) {
            try {
                this.graph.destroy();
            } catch (e) {
                // Graph's DOM element may have been cleared by showLoading
            }
            this.graph = null;
        }
        
        // Initialize fresh graph
        this.init();
        
        if (!this.graph) return;
        
        // Transform to G6 format
        const graphData = {
            nodes: (data.nodes || []).map(node => ({
                id: node.id,
                label: node.label,
                timing: node.timing,
                status: node.status,
                level: node.level,
                input: node.input,
                output: node.output,
                error: node.error
            })),
            edges: (data.edges || []).map(edge => ({
                source: edge.source,
                target: edge.target
            }))
        };
        
        // Render graph
        this.graph.data(graphData);
        this.graph.render();
        
        // Fit view with animation
        if (this.options.animate) {
            setTimeout(() => {
                this.graph.fitView(40);
            }, 100);
        } else {
            this.graph.fitView(40);
        }
    }

    // -------------------------------------------------------------------------
    // UI States
    // -------------------------------------------------------------------------

    showLoading() {
        this.container.innerHTML = `
            <div class="trace-graph-loading">
                <div class="spinner-border spinner-border-sm" role="status"></div>
                <span>Loading trace...</span>
            </div>
        `;
    }

    showError(message) {
        this.container.innerHTML = `
            <div class="trace-graph-error">
                <i class="bi bi-exclamation-triangle"></i>
                <span>${message}</span>
            </div>
        `;
    }

    showEmpty() {
        this.container.innerHTML = `
            <div class="trace-graph-empty">
                <i class="bi bi-diagram-3"></i>
                <span>Select a trace to visualize</span>
            </div>
        `;
    }

    // -------------------------------------------------------------------------
    // Node Modal
    // -------------------------------------------------------------------------

    showNodeModal(node) {
        if (this.modal) {
            this.modal.close();
        }
        this.modal = new TracingNodeModal(node);
        this.modal.open();
    }

    // -------------------------------------------------------------------------
    // Zoom Controls
    // -------------------------------------------------------------------------

    zoomIn() {
        if (!this.graph) return;
        const currentZoom = this.graph.getZoom();
        const newZoom = Math.min(currentZoom * 1.2, this.options.maxZoom);
        this.graph.zoomTo(newZoom, undefined, true);
    }

    zoomOut() {
        if (!this.graph) return;
        const currentZoom = this.graph.getZoom();
        const newZoom = Math.max(currentZoom / 1.2, this.options.minZoom);
        this.graph.zoomTo(newZoom, undefined, true);
    }

    resetZoom() {
        if (!this.graph) return;
        this.graph.fitView(40, undefined, true);
    }

    // -------------------------------------------------------------------------
    // Utilities
    // -------------------------------------------------------------------------

    getContainerSize() {
        const rect = this.container.getBoundingClientRect();
        return {
            width: rect.width || 800,
            height: rect.height || 400
        };
    }

    handleResize() {
        if (!this.graph) return;
        const { width, height } = this.getContainerSize();
        this.graph.changeSize(width, height);
    }
}


// =============================================================================
// TracingNodeModal - Node Detail Modal
// =============================================================================

class TracingNodeModal {
    constructor(node) {
        this.node = node;
        this.overlay = null;
    }

    open() {
        this.createOverlay();
        document.body.appendChild(this.overlay);
        
        // Animate in
        requestAnimationFrame(() => {
            this.overlay.classList.add('show');
        });
    }

    close() {
        if (!this.overlay) return;
        
        this.overlay.classList.remove('show');
        setTimeout(() => {
            this.overlay?.remove();
            this.overlay = null;
        }, 200);
    }

    createOverlay() {
        const { label, timing, status, level, input, output, error } = this.node;
        const isError = status === 'error';
        
        this.overlay = document.createElement('div');
        this.overlay.className = 'trace-node-modal-overlay';
        this.overlay.innerHTML = `
            <div class="trace-node-modal">
                <div class="trace-node-modal-header ${isError ? 'error' : ''}">
                    <div class="trace-node-modal-title">
                        <span class="trace-node-level-badge ${level.toLowerCase()}">${level}</span>
                        <span class="trace-node-name">${this.escapeHtml(label)}</span>
                    </div>
                    <button class="trace-node-modal-close" aria-label="Close">×</button>
                </div>
                
                <div class="trace-node-modal-body">
                    <div class="trace-node-info-row">
                        <span class="trace-node-info-label">Status:</span>
                        <span class="trace-node-status ${status}">${status}</span>
                    </div>
                    
                    ${timing ? `
                    <div class="trace-node-info-row">
                        <span class="trace-node-info-label">Duration:</span>
                        <span class="trace-node-timing">${timing}</span>
                    </div>
                    ` : ''}
                    
                    ${error ? `
                    <div class="trace-node-section error">
                        <div class="trace-node-section-title">
                            <i class="bi bi-exclamation-triangle"></i> Error
                        </div>
                        <div class="trace-node-error-type">${this.escapeHtml(error.type)}</div>
                        <div class="trace-node-error-message">${this.escapeHtml(error.message)}</div>
                        ${error.stack && error.stack.length > 0 ? `
                        <div class="trace-node-stack">
                            <div class="trace-node-section-title">Stack Trace</div>
                            ${error.stack.map(s => `
                                <div class="trace-node-stack-line">
                                    at <strong>${this.escapeHtml(s.func)}</strong> 
                                    (${this.escapeHtml(s.file)}${s.line ? ':' + s.line : ''})
                                </div>
                            `).join('')}
                        </div>
                        ` : ''}
                    </div>
                    ` : ''}
                    
                    <div class="trace-node-section">
                        <div class="trace-node-section-title">
                            <i class="bi bi-box-arrow-in-right"></i> Input
                        </div>
                        <pre class="trace-node-json">${this.formatJson(input)}</pre>
                    </div>
                    
                    ${!error ? `
                    <div class="trace-node-section">
                        <div class="trace-node-section-title">
                            <i class="bi bi-box-arrow-right"></i> Output
                        </div>
                        <pre class="trace-node-json">${this.formatJson(output)}</pre>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        // Bind events
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.close();
            }
        });
        
        this.overlay.querySelector('.trace-node-modal-close').addEventListener('click', () => {
            this.close();
        });
        
        // ESC key to close
        document.addEventListener('keydown', this.handleKeyDown = (e) => {
            if (e.key === 'Escape') {
                this.close();
                document.removeEventListener('keydown', this.handleKeyDown);
            }
        });
    }

    formatJson(jsonStr) {
        if (!jsonStr || jsonStr === '{}') {
            return '<span class="trace-json-empty">(empty)</span>';
        }
        try {
            const obj = typeof jsonStr === 'string' ? JSON.parse(jsonStr) : jsonStr;
            return this.escapeHtml(JSON.stringify(obj, null, 2));
        } catch {
            return this.escapeHtml(jsonStr);
        }
    }

    escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}


// =============================================================================
// CSS Styles (injected on first use)
// =============================================================================

(function injectStyles() {
    if (document.getElementById('tracing-graph-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'tracing-graph-styles';
    style.textContent = `
        /* Graph container states */
        .trace-graph-loading,
        .trace-graph-error,
        .trace-graph-empty {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            min-height: 300px;
            gap: 8px;
            color: #656d76;
            font-size: 14px;
        }
        
        .trace-graph-loading .spinner-border {
            margin-right: 8px;
        }
        
        .trace-graph-error {
            color: #cf222e;
        }
        
        .trace-graph-error i,
        .trace-graph-empty i {
            font-size: 32px;
            opacity: 0.5;
        }
        
        /* Node modal overlay */
        .trace-node-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.2s ease;
        }
        
        .trace-node-modal-overlay.show {
            opacity: 1;
        }
        
        /* Node modal */
        .trace-node-modal {
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            width: 90%;
            max-width: 560px;
            max-height: 80vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transform: scale(0.95);
            transition: transform 0.2s ease;
        }
        
        .trace-node-modal-overlay.show .trace-node-modal {
            transform: scale(1);
        }
        
        /* Modal header */
        .trace-node-modal-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 20px;
            border-bottom: 1px solid #d0d7de;
            background: #f6f8fa;
        }
        
        .trace-node-modal-header.error {
            background: #ffebe9;
            border-color: #ff8182;
        }
        
        .trace-node-modal-title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
        }
        
        .trace-node-name {
            font-size: 16px;
            color: #1f2328;
        }
        
        .trace-node-level-badge {
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .trace-node-level-badge.api {
            background: #ddf4ff;
            color: #0969da;
        }
        
        .trace-node-level-badge.info {
            background: #dafbe1;
            color: #1a7f37;
        }
        
        .trace-node-level-badge.debug {
            background: #fbefff;
            color: #8250df;
        }
        
        .trace-node-modal-close {
            background: none;
            border: none;
            font-size: 24px;
            color: #656d76;
            cursor: pointer;
            padding: 0;
            width: 32px;
            height: 32px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .trace-node-modal-close:hover {
            background: rgba(0, 0, 0, 0.05);
            color: #1f2328;
        }
        
        /* Modal body */
        .trace-node-modal-body {
            padding: 20px;
            overflow-y: auto;
        }
        
        .trace-node-info-row {
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
        }
        
        .trace-node-info-label {
            color: #656d76;
            min-width: 70px;
        }
        
        .trace-node-status {
            font-weight: 500;
        }
        
        .trace-node-status.success {
            color: #1a7f37;
        }
        
        .trace-node-status.error {
            color: #cf222e;
        }
        
        .trace-node-timing {
            font-family: ui-monospace, monospace;
            color: #0969da;
        }
        
        /* Sections */
        .trace-node-section {
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #d0d7de;
        }
        
        .trace-node-section.error {
            background: #ffebe9;
            margin: 16px -20px;
            padding: 16px 20px;
            border-top: none;
        }
        
        .trace-node-section-title {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            color: #656d76;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .trace-node-section.error .trace-node-section-title {
            color: #cf222e;
        }
        
        .trace-node-error-type {
            font-weight: 600;
            color: #cf222e;
            margin-bottom: 4px;
        }
        
        .trace-node-error-message {
            color: #57606a;
        }
        
        .trace-node-stack {
            margin-top: 12px;
        }
        
        .trace-node-stack-line {
            font-family: ui-monospace, monospace;
            font-size: 12px;
            color: #57606a;
            padding: 2px 0;
        }
        
        .trace-node-stack-line strong {
            color: #1f2328;
        }
        
        /* JSON display */
        .trace-node-json {
            background: #f6f8fa;
            border: 1px solid #d0d7de;
            border-radius: 6px;
            padding: 12px;
            font-family: ui-monospace, monospace;
            font-size: 12px;
            overflow-x: auto;
            margin: 0;
            max-height: 150px;
            overflow-y: auto;
        }
        
        .trace-json-empty {
            color: #656d76;
            font-style: italic;
        }
        
        /* Zoom controls */
        .trace-graph-zoom-controls {
            position: absolute;
            bottom: 16px;
            right: 16px;
            display: flex;
            gap: 4px;
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 6px;
            padding: 4px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .trace-graph-zoom-btn {
            width: 32px;
            height: 32px;
            border: none;
            background: transparent;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #656d76;
        }
        
        .trace-graph-zoom-btn:hover {
            background: #f6f8fa;
            color: #1f2328;
        }
    `;
    document.head.appendChild(style);
})();


// =============================================================================
// Export for module usage
// =============================================================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TracingGraphView, TracingNodeModal };
}
