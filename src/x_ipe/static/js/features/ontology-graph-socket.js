/**
 * FEATURE-058-F CR-001: Ontology Graph Socket Listener
 *
 * Manages Socket.IO connection on the /ontology namespace to receive
 * AI Agent search results pushed via ui-callback.py → internal endpoint.
 * Delegates graph highlighting to OntologyGraphCanvas.highlightSubgraph().
 */

class OntologyGraphSocket {
    /**
     * @param {object} canvas — OntologyGraphCanvas instance with highlightSubgraph()
     */
    constructor(canvas) {
        this._canvas = canvas;
        this._socket = null;
        this._lastRequestId = null;
        this._progressTimer = null;
        this._subscribed = false;
    }

    /**
     * Connect to /ontology namespace and start listening for search results.
     * Safe to call multiple times — subsequent calls are no-ops.
     */
    subscribe() {
        if (this._subscribed || !window.io) return;
        this._subscribed = true;

        this._socket = io('/ontology', {
            transports: ['websocket'],
            upgrade: false,
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: 10,
        });

        this._socket.on('connect', () => {
            console.log('[OntologySocket] Connected to /ontology');
        });

        this._socket.on('disconnect', (reason) => {
            console.log(`[OntologySocket] Disconnected: ${reason}`);
        });

        this._socket.on('ontology_search_result', (data) => {
            this._handleSearchResult(data);
        });

        // Show progress indicator after 3s delay (AC-058F-10g)
        this._startProgressTimer();
    }

    /**
     * Disconnect socket and clean up. Safe to call multiple times.
     */
    destroy() {
        this._subscribed = false;
        this._clearProgressTimer();
        if (this._socket) {
            this._socket.disconnect();
            this._socket = null;
        }
        this._lastRequestId = null;
    }

    /**
     * Handle incoming search result event.
     * @param {object} data — {results, subgraph, query, scope, request_id}
     */
    _handleSearchResult(data) {
        // Validate payload (AC-058F-09e)
        if (!data || !Array.isArray(data.results) || !data.subgraph) {
            console.debug('[OntologySocket] Malformed payload ignored:', data);
            return;
        }

        // Dedup: discard if request_id is same or older (AC-058F-10h)
        if (data.request_id && this._lastRequestId && data.request_id === this._lastRequestId) {
            console.debug('[OntologySocket] Duplicate request_id ignored:', data.request_id);
            return;
        }
        if (data.request_id) {
            this._lastRequestId = data.request_id;
        }

        // Clear progress indicator
        this._clearProgressTimer();
        this._hideProgress();

        // Extract node IDs for highlighting (AC-058F-10b)
        // Nodes may be plain string IDs (from search.py) or objects with {data:{id}} or {id}
        const allNodeIds = (data.subgraph.nodes || []).map(n =>
            typeof n === 'string' ? n : (n.data?.id || n.id)
        ).filter(Boolean);
        const directMatchIds = data.results.map(r =>
            typeof r === 'string' ? r : (r.node_id || r.entity?.id)
        ).filter(Boolean);

        // CR-002: extract virtual nodes metadata for hub rendering
        const virtualNodes = data.subgraph.virtual_nodes || [];

        // Delegate to canvas: highlight direct matches + their immediate neighbors
        if (this._canvas && directMatchIds.length > 0) {
            this._canvas.highlightSubgraph(allNodeIds, directMatchIds, virtualNodes);
        }
    }

    /**
     * Start a 3-second timer that shows the progress indicator if no results arrive.
     */
    _startProgressTimer() {
        this._clearProgressTimer();
        this._progressTimer = setTimeout(() => {
            this._showProgress();
        }, 3000);
    }

    _clearProgressTimer() {
        if (this._progressTimer) {
            clearTimeout(this._progressTimer);
            this._progressTimer = null;
        }
    }

    _showProgress() {
        const el = document.getElementById('ontology-agent-progress');
        if (el) el.classList.add('active');
    }

    _hideProgress() {
        const el = document.getElementById('ontology-agent-progress');
        if (el) el.classList.remove('active');
    }
}
