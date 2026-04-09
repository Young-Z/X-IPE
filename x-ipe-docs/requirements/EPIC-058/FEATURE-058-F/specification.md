# Feature Specification: Graph Search & AI Agent Integration

> Feature ID: FEATURE-058-F  
> Version: v1.0  
> Status: Refined  
> Last Updated: 04-09-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 04-09-2026 | Initial specification |

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

**FR-5: Search Re-run on Scope Change**  
If a search query is active and the user changes graph scope (adds/removes graphs via sidebar checkboxes), the search automatically re-runs with the updated scope. This applies to both the dropdown results and canvas highlighting.

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

**External:**
- Cytoscape.js (already loaded by FEATURE-058-E) — node highlighting/dimming via style manipulation
- No new external dependencies

## Business Rules

**BR-1:** Search scope is always determined by the sidebar graph selections. When no graphs are selected, the search defaults to all available graphs.

**BR-2:** The AI Agent button shows an error toast when clicked with no graphs selected and does not trigger any console action.

**BR-3:** BFS depth defaults to 3 for both manual search bar and AI agent searches. The AI agent may override depth via API parameters.

**BR-4:** The "Search with AI Agent" command is pre-filled but never auto-executed — the user must press Enter to send it to the AI.

**BR-5:** If a search is active and the user clears the search bar, all highlighting is removed and the dropdown closes immediately (no lingering state).

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Search with no graphs selected | Empty results; search bar shows subtle hint "Select graphs to search" |
| BFS search on disconnected graph | BFS expansion stays within the connected component; disconnected nodes are not reached |
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

## Open Questions

*None — all design decisions resolved during refinement.*
