# Feature Specification: Graph Search & AI Agent Integration

> Feature ID: FEATURE-058-F  
> Version: v1.3  
> Status: Refined  
> Last Updated: 04-17-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-09-2026 | Initial specification |
| v1.1 | 04-13-2026 | [CR-001](./CR-001.md): Added WebSocket callback from AI Agent search to graph viewer — new ACs AC-058F-09 (Socket Callback), AC-058F-10 (Frontend Listener), AC-058F-11 (Callback Script). Updated FR-4, added FR-6/FR-7. Added BR-6. |
| v1.2 | 04-13-2026 | Refinement pass: Added AC-058F-09e/09f (payload validation, endpoint auth), AC-058F-10f/10g/10h (reconnection, loading indicator, dedup), AC-058F-11d (logging). Clarified socket scoping as per-port broadcast. |
| v1.3 | 04-17-2026 | [CR-002](./CR-002.md): Added search-context graph synthesis — virtual hub node with star topology when BFS results span disconnected graph files. New ACs AC-058F-12 (Search-Context Graph Synthesis), updated AC-058F-10c (virtual node exception). Added US-8, FR-8, BR-7. Updated edge case table. |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| Ontology Graph Viewer v1 | HTML | [x-ipe-docs/requirements/EPIC-058/FEATURE-058-F/mockups/ontology-graph-viewer-v1.html](x-ipe-docs/requirements/EPIC-058/FEATURE-058-F/mockups/ontology-graph-viewer-v1.html) | AI Agent Terminal overlay, "Search with AI Agent" button, search bar with scope selector | current | 04-09-2026 |

> **Scope Note:** This mockup is shared with FEATURE-058-E. Only the following elements are in scope for FEATURE-058-F: the "Search with AI Agent" button (`.ai-agent-btn`), the terminal overlay (`.terminal-overlay`), BFS-enhanced search bar behavior, and the search results dropdown. All other mockup elements were already implemented in FEATURE-058-E.

## Overview

**What:** This feature upgrades the Ontology Graph Viewer's search capabilities and adds an AI Agent integration pathway. It has two parts: (1) **BFS-Enhanced Search** — replacing the simple text-matching search with a BFS graph traversal search that discovers matching nodes AND their graph neighbors (depth=3), returning richer, graph-aware results displayed in both a dropdown list and as highlighted nodes on the canvas; (2) **AI Agent Console Integration** — a "Search with AI Agent" button that opens the existing X-IPE Console, pre-fills a `@copilot` command scoped to the currently selected graphs, and allows the AI agent to drive multi-round BFS searches with adaptive depth.

**Why:** The current search (`GET /api/kb/ontology/search`) performs basic case-insensitive text matching — it finds exact keyword hits but misses related concepts just one hop away. For example, searching "JWT" finds the JWT node but not "Token Management" or "Auth Middleware" that depend on it. BFS traversal solves this by expanding from matched nodes to discover their neighborhood, revealing knowledge clusters. The AI Agent integration goes further — letting a human ask natural-language questions like "how does authentication relate to session management?" and having the AI orchestrate multiple targeted searches.

**Who:** Developers and knowledge workers who use the Ontology Graph Viewer to explore their KB. They need deeper search that surfaces related knowledge (not just exact matches), and they want the option to ask the AI for help when exploring unfamiliar graph territories.

## User Stories

**US-1:** As a developer, I want the search bar to return not just exact matches but also related nodes within a few hops, so that I can discover knowledge clusters around a topic.

**US-2:** As a knowledge worker, I want to see search results in a dropdown list below the search bar, so that I can quickly scan matches and click to navigate to a specific node.

**US-3:** As a developer, I want matching nodes and their BFS-expanded neighbors highlighted on the canvas (with non-matching nodes dimmed), so that I can visually see the relevant subgraph.

**US-4:** As a knowledge worker, I want to click "Search with AI Agent" to open the X-IPE Console pre-filled with a search command scoped to my selected graphs, so that I can ask natural-language questions about my knowledge base.

**US-5:** As a developer, I want the AI agent to be able to run multiple rounds of BFS search with different depths and queries, so that complex knowledge exploration is handled automatically.

**US-6:** As a knowledge worker, I want to click a result in the search dropdown to pan the canvas to that node and open its detail panel, so that I can inspect the result quickly.

**US-7:** *(Added by [CR-001](./CR-001.md))* As a knowledge worker, I want the AI agent's search results to automatically appear on the graph canvas (highlighting matched and related nodes), so that I can see the visual context of what the agent found without manually re-searching.

**US-8:** *(Added by [CR-002](./CR-002.md))* As a developer, I want search results that span multiple disconnected graph files to be connected by a virtual hub node on the canvas, so that I can see at a glance that these entities are all related through my search term — even when no pre-existing relations link them.

## Acceptance Criteria

### AC-058F-01: BFS Search API Endpoint

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058F-01a | GIVEN the ontology graph service is running WHEN a GET request is sent to `/api/kb/ontology/search/bfs?q=jwt&scope=all&depth=3&page=1&page_size=20` THEN the response returns JSON with `results` (matched nodes with relevance, graph name, match fields), `subgraph` (BFS-expanded nodes and edges), and `pagination` (page, page_size, total, total_pages) | API |
| AC-058F-01b | GIVEN scope is set to specific graph names (comma-separated) WHEN the BFS search is invoked THEN only graphs in the scope are searched AND the subgraph only contains nodes/edges from those graphs | API |
| AC-058F-01c | GIVEN scope is "all" WHEN the BFS search is invoked THEN all available ontology graphs are searched | API |
| AC-058F-01d | GIVEN depth=3 WHEN a search matches node X THEN the subgraph contains all nodes reachable from X within 3 hops AND all edges connecting those nodes | API |
| AC-058F-01e | GIVEN an empty or missing query string WHEN the BFS search endpoint is called THEN it returns HTTP 400 with error code `MISSING_QUERY` | API |
| AC-058F-01f | GIVEN the query matches nodes in multiple graphs WHEN the BFS search is invoked with scope=all THEN results from all graphs are merged, sorted by relevance (descending), and paginated as a single result set | API |
| AC-058F-01g | GIVEN the `.ontology/` directory does not exist WHEN the BFS search endpoint is called THEN it returns 404 with error code `ONTOLOGY_NOT_FOUND` | API |

### AC-058F-02: Search Results Dropdown

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058F-02a | GIVEN the user types a query in the search bar AND results are returned WHEN the response arrives THEN a dropdown list appears below the search bar showing each result with: node label, node type icon/color, graph name, and relevance indicator | UI |
| AC-058F-02b | GIVEN the search results dropdown is visible WHEN the user clicks a result item THEN the canvas pans to center on that node, the node is selected (highlighted), and the detail panel slides open for that node | UI |
| AC-058F-02c | GIVEN the search results dropdown is visible WHEN the user presses Escape or clicks outside the dropdown THEN the dropdown closes | UI |
| AC-058F-02d | GIVEN a search returns zero results WHEN the dropdown would appear THEN it shows a "No results found" message instead of an empty list | UI |
| AC-058F-02e | GIVEN the search results dropdown is visible WHEN the user presses ArrowDown/ArrowUp THEN the selection moves through the result items AND pressing Enter selects the highlighted item (same as clicking it) | UI |
| AC-058F-02f | GIVEN the user types a query WHEN the debounce timer (300ms) fires THEN the BFS search API is called (not the old simple search endpoint) | UI |

### AC-058F-03: Canvas Search Highlighting

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058F-03a | GIVEN a BFS search returns results with a subgraph WHEN the canvas updates THEN nodes in the subgraph are highlighted (full opacity, border glow) AND nodes NOT in the subgraph are dimmed (opacity 0.15) | UI |
| AC-058F-03b | GIVEN a BFS search returns results WHEN the canvas highlights the subgraph THEN direct match nodes have a stronger highlight (e.g., pulsing border or thicker ring) than BFS-neighbor nodes (normal highlight) | UI |
| AC-058F-03c | GIVEN the search bar is cleared (empty query) WHEN the canvas updates THEN all nodes return to normal opacity (no highlighting or dimming) | UI |
| AC-058F-03d | GIVEN a search is active AND the user switches graph scope (adds/removes graphs) WHEN the scope changes THEN the search automatically re-runs with the new scope AND highlighting updates accordingly | UI |

### AC-058F-04: AI Agent Console Integration — Button

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058F-04a | GIVEN the Ontology Graph Viewer is active WHEN the user views the search bar area THEN a "Search with AI Agent" button is visible with a terminal icon (per mockup styling: violet gradient border, monospace text) | UI |
| AC-058F-04b | GIVEN graphs are selected in the scope WHEN the user clicks "Search with AI Agent" THEN the X-IPE Console panel expands (if collapsed), an idle session is found or a new one created, and a `@copilot` command is pre-filled with the selected graph names as scope context (command is NOT auto-executed — cursor is placed at the end for the user to type their question) | UI |
| AC-058F-04c | GIVEN no graphs are selected WHEN the user clicks "Search with AI Agent" THEN an error toast "Select at least one graph before using AI Agent search." is shown AND no console action is triggered | UI |
| AC-058F-04d | GIVEN the Console is already expanded with an active session WHEN the user clicks "Search with AI Agent" THEN a new idle session is found or created (does not interrupt the active session) AND the scope-prefilled command is inserted into the new session | UI |

### AC-058F-05: AI Agent Console Integration — Command Format

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058F-05a | GIVEN two graphs are in scope: "security-architecture" and "system-architecture" WHEN the "Search with AI Agent" button is clicked THEN the pre-filled console command follows the format: `search the knowledge graph scoped to security-architecture, system-architecture for: ` (with trailing space for user input) | Unit |
| AC-058F-05b | GIVEN a single graph is in scope WHEN the "Search with AI Agent" button is clicked THEN the command references that single graph name without comma separator | Unit |
| AC-058F-05c | GIVEN the AI agent receives a search command WHEN it processes the query THEN it can invoke the BFS search API endpoint (`/api/kb/ontology/search/bfs`) with appropriate depth and scope parameters (this confirms the endpoint is agent-callable) | Integration |

### AC-058F-06: Search Scope Awareness

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058F-06a | GIVEN no graphs are selected in the sidebar WHEN the user types in the search bar THEN the search queries all available graphs (scope defaults to "all") | UI |
| AC-058F-06b | GIVEN 2 of 3 available graphs are selected WHEN the user searches THEN only the 2 selected graphs are searched (the unselected graph's nodes are excluded from results and subgraph) | API |
| AC-058F-06c | GIVEN a search is active with results displayed WHEN the user deselects a graph that contributed to the results THEN the search re-runs AND results from the deselected graph are removed from both dropdown and canvas highlighting | UI |

### AC-058F-07: Status Bar Search Updates

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058F-07a | GIVEN a BFS search returns N direct matches and M total subgraph nodes WHEN the status bar updates THEN it shows a search indicator like "Search: N matches · M related" | UI |
| AC-058F-07b | GIVEN a search is cleared WHEN the status bar updates THEN the search indicator is removed and the status bar returns to its default display (node count, edge count, layout, zoom) | UI |

### AC-058F-08: Mockup Comparison — AI Agent Button & Terminal

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058F-08a | GIVEN the mockup shows a "Search with AI Agent" button with violet gradient border and terminal icon WHEN the implementation renders the button THEN it visually matches the mockup styling (gradient background, violet color scheme, terminal SVG icon, 12px font) | UI |
| AC-058F-08b | GIVEN the mockup shows the AI Agent button positioned after a vertical divider in the search/header area WHEN the implementation renders THEN the button is in the same position relative to the search bar (right side, separated by a divider) | UI |

### AC-058F-09: AI Agent Socket Callback — Backend *(Added by [CR-001](./CR-001.md))*

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058F-09a | GIVEN the Flask-SocketIO server is running WHEN a client connects and joins a session room THEN the server accepts the connection and registers the client in the ontology search callback channel | Integration |
| AC-058F-09b | GIVEN the AI Agent has completed a search via `search.py` WHEN `ui-callback.py` is invoked with the search results THEN the server emits an `ontology_search_result` SocketIO event to the session room containing `{ results, subgraph, query, scope }` | Integration |
| AC-058F-09c | GIVEN the `ontology_search_result` event payload WHEN the frontend receives it THEN `results` contains an array of `{ node_id, label, node_type, graph, relevance }` AND `subgraph` contains `{ nodes: [ids], edges: [{ from, rel, to }] }` matching the BFS API response format | API |
| AC-058F-09d | GIVEN no frontend client is listening on the ontology search channel WHEN `ui-callback.py` emits a search result THEN the event is silently dropped (no error, no blocking) | Integration |
| AC-058F-09e | GIVEN the `ontology_search_result` event payload is malformed (missing `results` or `subgraph` fields, or either is null) WHEN the frontend receives it THEN it logs a debug warning and silently ignores the event (no exception, no partial UI render) | Unit |
| AC-058F-09f | GIVEN the Flask server receives a POST request to `/api/internal/ontology/callback` WHEN the request lacks a valid internal authorization token THEN it returns HTTP 401 Unauthorized AND does not emit the SocketIO event | API |

### AC-058F-10: AI Agent Socket Callback — Frontend Listener *(Added by [CR-001](./CR-001.md))*

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058F-10a | GIVEN the user clicks "Search with AI Agent" WHEN the console opens THEN the graph viewer subscribes to `ontology_search_result` SocketIO events for the current session | UI |
| AC-058F-10b | GIVEN the graph viewer is subscribed AND an `ontology_search_result` event arrives WHEN the event contains valid search data THEN the canvas calls `highlightSubgraph(allNodeIds, directMatchIds)` to highlight the agent's results on the graph | UI |
| AC-058F-10c | GIVEN the graph viewer is subscribed AND an `ontology_search_result` event arrives WHEN the subgraph contains entity node IDs not currently loaded in the canvas THEN unmatched entity node IDs are silently ignored (only nodes already in the canvas are highlighted) — EXCEPT virtual nodes (IDs prefixed `__search_hub__`) which are dynamically added to the canvas via `cy.add()` *(Updated by [CR-002](./CR-002.md))* | UI |
| AC-058F-10d | GIVEN a previous agent search highlight is active on the canvas WHEN a new `ontology_search_result` event arrives THEN the previous highlighting is cleared and replaced with the new search results | UI |
| AC-058F-10e | GIVEN the graph viewer is subscribed WHEN the viewer component is closed or destroyed THEN the socket listener is unsubscribed (no memory leaks or stale listeners) | UI |
| AC-058F-10f | GIVEN the socket connection drops mid-session WHEN the Flask server remains reachable THEN the frontend automatically attempts to reconnect within 5 seconds AND if reconnection succeeds, subsequent agent search results are still received | Integration |
| AC-058F-10g | GIVEN "Search with AI Agent" is clicked AND the socket listener is subscribed WHEN no `ontology_search_result` event arrives within 3 seconds THEN the canvas shows a subtle "Agent search in progress…" indicator (e.g., small spinner badge in the search bar area) AND the indicator is removed when results arrive or a socket error occurs | UI |
| AC-058F-10h | GIVEN multiple agent searches are triggered rapidly (within 5 seconds of each other) AND `ontology_search_result` events arrive out-of-order WHEN rendering highlighting THEN only the event with the latest `request_id` timestamp is rendered AND prior out-of-order results are discarded | Integration |

### AC-058F-11: AI Agent Callback Script *(Added by [CR-001](./CR-001.md))*

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058F-11a | GIVEN `ui-callback.py` exists in `.github/skills/x-ipe-tool-ontology/scripts/` WHEN invoked with `--session-id <sid> --results-json <path>` THEN it reads the search results file and emits the data via the SocketIO callback channel | Integration |
| AC-058F-11b | GIVEN `ui-callback.py` is invoked without a valid `--session-id` WHEN it attempts to emit THEN it exits with a non-zero code and logs an error (does not crash silently) | Unit |
| AC-058F-11c | GIVEN `ui-callback.py` is invoked AND the Flask server is not reachable WHEN it attempts to emit THEN it retries once, then exits with a warning log (does not block the AI agent session) | Integration |
| AC-058F-11d | GIVEN `ui-callback.py` is invoked WHEN emission succeeds or fails THEN it logs: timestamp, session_id, query summary, result count, and emit status (success/retry/fail) to stdout | Unit |

### AC-058F-12: Search-Context Graph Synthesis *(Added by [CR-002](./CR-002.md))*

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058F-12a | GIVEN a BFS search matches entities from multiple graph files WHEN those matched entities have no pre-existing edges connecting them (disconnected components in the subgraph) THEN a virtual hub node is injected into the subgraph with ID `__search_hub__{query}`, label set to the search query, and `node_type` set to `search_hub` | API |
| AC-058F-12b | GIVEN a virtual hub node is created WHEN the subgraph is returned THEN virtual edges with relation `search_match` connect the hub to each direct-match entity node (star topology) AND these edges are included in `subgraph.edges` | API |
| AC-058F-12c | GIVEN a BFS search matches entities that are already connected (single connected component in the subgraph) WHEN the subgraph is returned THEN no virtual hub node or edges are injected (subgraph is returned as-is) | API |
| AC-058F-12d | GIVEN the subgraph contains a virtual hub node WHEN the frontend receives the subgraph THEN the canvas renders the hub node at the centroid of matched nodes with a distinct visual style (dashed border, search icon, `search-hub` CSS class) AND virtual edges are rendered as dashed lines | UI |
| AC-058F-12e | GIVEN a search highlight with a virtual hub is active WHEN the user clears the search or starts a new search THEN all virtual nodes and edges are removed from the Cytoscape canvas (no leftover virtual elements) | UI |
| AC-058F-12f | GIVEN the subgraph response WHEN it contains virtual nodes THEN the `virtual_nodes` field is an array of objects `[{ id, label, node_type: "search_hub" }]` providing metadata for the frontend to render virtual elements | API |

## Functional Requirements

**FR-1: BFS Search API Endpoint**  
A new endpoint `GET /api/kb/ontology/search/bfs` wraps the existing `search.py` BFS module from the ontology tool skill. Parameters: `q` (query string), `scope` (comma-separated graph names or "all"), `depth` (integer, default 3), `page` (integer, default 1), `page_size` (integer, default 20). The response includes direct match results with relevance scores, a BFS-expanded subgraph (node IDs and edge triples), and pagination metadata.

**FR-2: Search Results Dropdown**  
When the search bar has results, a dropdown list appears below it. Each item shows: node label, a colored dot matching the node type, the graph name in muted text, and a relevance bar/indicator. Clicking an item pans the canvas and opens the detail panel. Keyboard navigation (↑↓ + Enter) is supported.

**FR-3: Canvas Highlighting with Subgraph**  
When BFS results arrive, the frontend receives both direct matches and the subgraph. Direct matches get a strong highlight (e.g., colored ring + pulse). BFS-neighbor nodes get a softer highlight (e.g., normal border but full opacity). All other nodes are dimmed to 15% opacity. Clearing the search restores all nodes.

**FR-4: AI Agent Console Bridge**  
The "Search with AI Agent" button uses the existing `window.terminalManager` API to:
1. Expand the Console panel if collapsed
2. Find an idle session or create a new one
3. Pre-fill a natural-language search command scoped to the selected graphs
4. Place the cursor at the end (no auto-execute) — the user types their question and presses Enter
5. *(CR-001)* Subscribe the graph viewer to `ontology_search_result` SocketIO events for the session, so agent search results are displayed on the canvas in real-time

**FR-5: Search Re-run on Scope Change**  
If a search query is active and the user changes graph scope (adds/removes graphs via sidebar checkboxes), the search automatically re-runs with the updated scope. This applies to both the dropdown results and canvas highlighting.

**FR-6: Socket Callback Handler** *(Added by [CR-001](./CR-001.md))*  
A new SocketIO handler module (`ontology_handlers.py`) registers the `ontology_search_result` event namespace. When `ui-callback.py` emits search results to a session room, the server relays them to all connected clients in that room. The handler follows the same `register_X_handlers(socketio)` pattern used by `terminal_handlers.py` and `voice_handlers.py`.

**FR-7: UI Callback Script** *(Added by [CR-001](./CR-001.md))*  
A new `ui-callback.py` script in `.github/skills/x-ipe-tool-ontology/scripts/` accepts search results (from `search.py`) and a session ID, then emits them to the Flask server's SocketIO channel. This script is called by the AI agent (or by `search.py` itself) after a search completes. It transforms the raw search output into the Cytoscape-compatible format expected by `highlightSubgraph()` and emits via HTTP POST to an internal callback endpoint or direct SocketIO client emission.

**FR-8: Search-Context Graph Synthesis** *(Added by [CR-002](./CR-002.md))*  
After BFS search completes and the subgraph is assembled, a connectivity check determines whether direct-match entities form a single connected component or multiple disconnected components. If disconnected, a virtual hub node (ID: `__search_hub__{query}`, node_type: `search_hub`) is created and connected to each direct-match entity via virtual `search_match` edges (star topology). The virtual hub and edges are injected into the `subgraph` response alongside a `virtual_nodes` metadata array. The frontend detects virtual nodes by ID prefix (`__search_hub__`), adds them to the Cytoscape canvas via `cy.add()` with a distinct dashed-border style, and removes them on `clearHighlight()`.

## Non-Functional Requirements

- **Performance**: BFS search with depth=3 across all graphs must return within 2 seconds for ontologies up to 500 nodes total.
- **Debounce**: Search bar input debounced at 300ms (same as current).
- **Pagination**: API supports pagination (default page_size=20) but the dropdown shows up to 10 results inline.
- **Accessibility**: Search dropdown is keyboard-navigable (ArrowUp/Down + Enter); focus management returns to search input when dropdown closes.
- **No data mutation**: All operations are read-only. No graph editing from search or AI agent.

## UI/UX Requirements

*(Derived from the linked mockup — in-scope elements only)*

**Search Bar Area (per mockup):**
- The existing search input remains unchanged
- A vertical divider separates the search input from the "Search with AI Agent" button
- "Search with AI Agent" button: violet gradient border (`rgba(139,92,246,.3)`), terminal SVG icon (`>_`), 12px font, hover state with stronger gradient and box shadow
- Search results dropdown appears directly below the search bar, overlapping the canvas

**Search Results Dropdown (new — not in mockup, but implied by design):**
- White background, subtle border and shadow matching the sidebar style
- Each result row: colored type dot (same palette as node types), label text, graph name in muted color, relevance bar
- Hover state highlights the row
- Maximum 10 visible items; scrollable if more
- "No results" empty state message

**Canvas Highlighting (enhancement of FEATURE-058-E behavior):**
- Direct match nodes: emerald glow ring (2px wider than normal border)
- BFS-neighbor nodes: full opacity, normal border
- Non-matching nodes: opacity 0.15
- Edges connected to highlighted nodes remain visible; edges between dimmed nodes are dimmed (opacity 0.15)

**Status Bar (addition to existing):**
- When search active: append "· Search: N matches · M related" to existing status fields
- Font and style match existing status bar (JetBrains Mono, 11px)

## Dependencies

**Internal:**
- FEATURE-058-A (Ontology Tool Skill) — provides `search.py` BFS module
- FEATURE-058-E (Ontology Graph Viewer UI) — provides the canvas, sidebar, status bar, search bar shell
- X-IPE Console (`window.terminalManager`) — provides the terminal session API for AI Agent integration
- Flask-SocketIO infrastructure (`app.py`, handler registration pattern) — provides the socket transport layer *(CR-001)*

**External:**
- Cytoscape.js (already loaded by FEATURE-058-E) — node highlighting/dimming via style manipulation
- Flask-SocketIO (already in `pyproject.toml`: `flask-socketio>=5.6.0`) *(CR-001)*
- No new external dependencies

## Business Rules

**BR-1:** Search scope is always determined by the sidebar graph selections. When no graphs are selected, the search defaults to all available graphs.

**BR-2:** The AI Agent button shows an error toast when clicked with no graphs selected and does not trigger any console action.

**BR-3:** BFS depth defaults to 3 for both manual search bar and AI agent searches. The AI agent may override depth via API parameters.

**BR-4:** The "Search with AI Agent" command is pre-filled but never auto-executed — the user must press Enter to send it to the AI.

**BR-5:** If a search is active and the user clears the search bar, all highlighting is removed and the dropdown closes immediately (no lingering state).

**BR-6:** *(Added by [CR-001](./CR-001.md))* The socket callback delivers **search results** (read-only, from the same `.ontology/` data at rest) to the graph viewer — it does NOT inject new graph data or modify the ontology. This is distinct from real-time data sync (which remains out of scope per FEATURE-058-E BR-2).

**BR-7:** *(Added by [CR-002](./CR-002.md))* Virtual hub nodes are ephemeral canvas elements — they exist ONLY during an active search highlight and are removed when the search is cleared. They are NOT persisted to the ontology graph data, do NOT appear in entity counts, and do NOT affect BFS traversal of subsequent searches.

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Search with no graphs selected | Empty results; search bar shows subtle hint "Select graphs to search" |
| BFS search on disconnected graph | BFS expansion stays within the connected component; disconnected nodes are not reached. *(CR-002)* If direct-match entities span disconnected components, a virtual hub node connects them via star topology. |
| Search while graph data is still loading | Show loading spinner in dropdown; debounce prevents premature API call |
| Very long search query (>200 chars) | No client-side truncation; API handles gracefully |
| AI Agent button clicked but Console not available | Show toast notification "Console not available" |
| Multiple rapid scope changes while search is active | Scope-change re-search fires immediately per toggle (no additional debounce) |
| Search result references a node from a graph that was just deselected | Filter it out client-side before displaying |
| BFS returns >100 subgraph nodes | Canvas still renders all of them but the dropdown only shows top 10 direct matches |

## Out of Scope

- **Graph editing**: Creating, updating, or deleting entities from search results
- **Natural language understanding**: The BFS search API is keyword-based; NLU is handled by the AI agent in the Console
- **Search history**: No persistent search history or "recent searches" feature
- **Cross-session search**: Search state is not shared between browser tabs/sessions
- **Custom depth UI control**: No depth slider in the search bar (depth is fixed at 3 for manual search; AI controls depth for agent searches)
- **Search result export**: No CSV/JSON export of search results
- **Faceted search/filtering**: No filter-by-type, filter-by-dimension in the search dropdown

## Technical Considerations

- The BFS search endpoint should call the ontology tool skill's `search.py` module (which has tested BFS implementation) rather than reimplementing BFS logic in the graph service.
- The existing simple search endpoint (`/api/kb/ontology/search`) can be kept for backward compatibility or deprecated — the BFS endpoint replaces its functionality.
- Canvas highlighting needs efficient Cytoscape.js batch operations (`cy.batch(() => {...})`) to avoid per-node render thrashing with large graphs.
- The Console integration should reuse the established pattern from `action-execution-modal.js` — `window.terminalManager.findIdleSession()` → `sendCopilotPromptCommandNoEnter()`.
- The dropdown should use absolute positioning relative to the search bar container and handle z-index correctly so it appears above the canvas but below modal overlays.
- *(CR-001)* The `ontology_handlers.py` module should follow the `register_X_handlers(socketio)` pattern from `terminal_handlers.py` and `voice_handlers.py`. Register it in `app.py` alongside the existing handler registrations.
- *(CR-001)* The `ui-callback.py` script should use the `python-socketio` client library (already in `pyproject.toml`) to connect to the Flask server and emit the `ontology_search_result` event. Alternatively, it can POST to an internal HTTP endpoint that triggers the emit server-side.
- *(CR-001)* The frontend socket listener should be set up when "Search with AI Agent" is clicked and torn down when the viewer is closed, to avoid stale listeners.
- *(CR-001, Refinement)* Socket scoping is **per-port broadcast**: `ui-callback.py` POSTs to `http://localhost:{port}/api/internal/ontology/callback` (port from `.x-ipe.yaml`, default 5858). The server emits `ontology_search_result` to all connected clients on that server instance. No room-based isolation — all graph viewer instances on the same server see the result.
- *(CR-001, Refinement)* The internal callback endpoint (`/api/internal/ontology/callback`) must validate an internal authorization token to prevent unauthorized result injection. The token can be a shared secret configured in `.x-ipe.yaml` or an environment variable.
- *(CR-001, Refinement)* Each `ontology_search_result` event payload should include a `request_id` (UUID) for deduplication. The frontend tracks the latest `request_id` and discards out-of-order arrivals from earlier searches.
- *(CR-002)* Disconnected-component detection in `search.py` should use a simple union-find or BFS reachability check on the subgraph's direct-match nodes. Only direct-match nodes are checked — BFS-neighbor connectivity is not relevant for hub injection.
- *(CR-002)* Virtual hub node ID format is `__search_hub__{query}` (double-underscore prefix/suffix) to avoid collision with real entity IDs. The `virtual_nodes` array in the subgraph response provides metadata (label, node_type) for the frontend to render without additional lookups.
- *(CR-002)* The frontend should use `cy.add()` to inject virtual hub nodes/edges and `cy.remove()` on `clearHighlight()`. Virtual elements should have a `virtual: true` data flag for easy batch removal.

## Open Questions

*None — all design decisions resolved during refinement.*
