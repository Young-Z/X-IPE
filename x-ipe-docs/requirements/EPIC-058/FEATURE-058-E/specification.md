# Feature Specification: Ontology Graph Viewer UI

> Feature ID: FEATURE-058-E
> Version: v1.0
> Status: Refined
> Last Updated: 07-13-2026

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | 07-13-2026 | Initial specification |

## Linked Mockups

| Mockup | Type | Path | Description | Status | Linked Date |
|--------|------|------|-------------|--------|-------------|
| Ontology Graph Viewer v1 | HTML | [x-ipe-docs/requirements/EPIC-058/FEATURE-058-E/mockups/ontology-graph-viewer-v1.html](x-ipe-docs/requirements/EPIC-058/FEATURE-058-E/mockups/ontology-graph-viewer-v1.html) | Full interactive Cytoscape.js graph viewer with sidebar, canvas, detail panel, 3 layouts, context menus, minimap, tooltips, zoom controls, search bar, status bar | current | 07-13-2026 |

> **Note:** The mockup includes an "AI Agent Terminal" overlay and "Search with AI Agent" button that are **OUT OF SCOPE** for FEATURE-058-E — those belong to FEATURE-058-F (Graph Search & AI Agent Integration). All other mockup elements are in-scope.

## Overview

**What:** An interactive, browser-based knowledge graph viewer integrated into the X-IPE Flask application. The viewer renders ontology graph data produced by the Ontology Tool Skill (FEATURE-058-A) using Cytoscape.js with five plugins, three layout algorithms, and a rich set of interaction patterns including context menus, tooltips, a minimap, zoom controls, and a slide-out detail panel.

**Why:** Knowledge graphs created by the KB Librarian (FEATURE-058-D) exist only as JSONL files on disk. Without a visual frontend, users cannot explore entity relationships, discover clusters, or understand the structure of their knowledge base. A graph viewer enables intuitive exploration of concepts, documents, entities, and dimensions — making the ontology actionable rather than opaque.

**Who:** Developers and knowledge workers who use X-IPE to manage knowledge bases. They need to visually explore how KB articles relate to each other, identify knowledge clusters, find orphaned entities, and understand dependency chains. The primary interaction is read-only exploration (graph creation/editing is handled by FEATURE-058-A).

## User Stories

**US-1:** As a developer, I want to open a Knowledge Graph view from the main navigation, so that I can visually explore my KB's ontology without leaving the X-IPE application.

**US-2:** As a knowledge worker, I want to select one or more graph files from a sidebar list, so that I can control which portion of my knowledge base is visualized.

**US-3:** As a developer, I want to click on a node to see its full metadata (description, dimensions, source files, related nodes), so that I can understand what each entity represents.

**US-4:** As a knowledge worker, I want to switch between Force-Directed, Hierarchical, and Radial layouts, so that I can view the graph from different structural perspectives.

**US-5:** As a developer, I want to search for nodes by name and see matching results highlighted on the graph, so that I can quickly locate specific entities.

**US-6:** As a knowledge worker, I want to click on the source files label in the detail panel and browse the associated KB files in a modal, so that I can read the original content behind an entity.

**US-7:** As a developer, I want to see a minimap of the full graph while zoomed into a section, so that I can maintain spatial awareness.

## Acceptance Criteria

### AC-058E-01: Navigation & Mode Switching

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-01a | GIVEN the X-IPE app is loaded WHEN the user views the header/menu bar THEN a "Knowledge Graph" icon is visible beside the existing KB icon | UI |
| AC-058E-01b | GIVEN the user is in Free mode or Workflow mode WHEN the user clicks the Knowledge Graph icon THEN the main content area switches to the Ontology Graph Viewer (sidebar hidden, content header hidden, graph viewer fills the content area — same pattern as Workflow mode switching) | UI |
| AC-058E-01c | GIVEN the Ontology Graph Viewer is active WHEN the user clicks the Knowledge Graph icon again (or another nav icon) THEN the viewer is dismissed and the previous mode (Free/Workflow) is restored | UI |
| AC-058E-01d | GIVEN the Ontology Graph Viewer is active WHEN the page is displayed THEN the viewer renders the graph collection sidebar on the left, the graph canvas in the center, and the status bar at the bottom (per mockup layout) | UI |

### AC-058E-02: Graph Collection Sidebar

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-02a | GIVEN the graph viewer is open AND the active KB has `.ontology/` folder with graph files WHEN the sidebar loads THEN it lists all `.jsonl` graph files from `knowledge-base/.ontology/` with their node count, edge count, and dominant-type badge | UI |
| AC-058E-02b | GIVEN the sidebar has graph items WHEN the user clicks a graph item or its checkbox THEN the graph's checkbox toggles (checked/unchecked) AND the graph canvas updates to show/hide that graph's nodes and edges | UI |
| AC-058E-02c | GIVEN the sidebar has graph items WHEN the user clicks "Select All" THEN all graph checkboxes are checked AND all graph data is loaded into the canvas as a merged view | UI |
| AC-058E-02d | GIVEN some but not all graphs are selected WHEN the user views the Select All checkbox THEN it shows an indeterminate state ("–") AND the counter shows "X / N" (selected / total) | UI |
| AC-058E-02e | GIVEN the sidebar has graph items WHEN no graphs are selected THEN the canvas shows an empty state with an illustration and message "Select a graph to begin exploring" | UI |
| AC-058E-02f | GIVEN the API returns graph list WHEN the sidebar renders THEN each graph item displays: checkbox, graph name, node count, edge count, and a color-coded badge indicating the dominant node type (concept=emerald, document=blue, entity=amber) | UI |
| AC-058E-02g | GIVEN the sidebar has loaded WHEN the user views the bottom of the sidebar THEN a legend section shows 4 node types (Concept, Document, Entity, Dimension) with their corresponding colored dots | UI |

### AC-058E-03: Graph Rendering

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-03a | GIVEN one or more graphs are selected WHEN graph data is loaded from the API THEN Cytoscape.js renders nodes as circles with color based on `node_type` (concept=emerald #10b981, document=blue #3b82f6, entity=amber #f59e0b, dimension=violet #8b5cf6) AND node size scales with weight (width/height = 28 + weight × 4) | UI |
| AC-058E-03b | GIVEN nodes are rendered WHEN edges exist between nodes THEN edges are drawn as bezier curves with labels showing the relation type (depends_on, related_to, is_type_of, part_of, described_by) AND arrow targets for directed relations | UI |
| AC-058E-03c | GIVEN multiple graphs are selected WHEN the canvas renders THEN all selected graphs' nodes and edges appear in a single merged view (not tabs or side-by-side) | UI |
| AC-058E-03d | GIVEN graph data includes cluster information WHEN Force-Directed layout is active THEN the `idealEdgeLength` function uses cluster data (same cluster = 120, different cluster = 200) to visually group related nodes | UI |
| AC-058E-03e | GIVEN the canvas has rendered graph elements WHEN the user views the background THEN a subtle grid overlay (40×40px) with radial gradient accents is visible behind the graph (per mockup styling) | UI |

### AC-058E-04: Layout Management

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-04a | GIVEN the graph viewer is active WHEN the user views the top-left of the canvas THEN a floating layout picker panel is visible with 3 options: "Force-Directed" (default, active), "Hierarchical", and "Radial" — styled with glass-morphism (blur 10px, white 94% opacity) per mockup | UI |
| AC-058E-04b | GIVEN the layout picker is visible WHEN the user clicks "Force-Directed" THEN the graph re-renders using the fCoSE algorithm (quality=default, animate=true, animationDuration=800, nodeRepulsion=5500, gravity=0.25, randomize=true) AND the button shows active state (emerald background) | UI |
| AC-058E-04c | GIVEN the layout picker is visible WHEN the user clicks "Hierarchical" THEN the graph re-renders using the Dagre algorithm (rankDir=TB, nodeSep=60, rankSep=80, animationDuration=600) AND the button shows active state | UI |
| AC-058E-04d | GIVEN the layout picker is visible WHEN the user clicks "Radial" THEN the graph re-renders using the Concentric algorithm (concentric=node weight, minNodeSpacing=50, animationDuration=600) AND the button shows active state | UI |
| AC-058E-04e | GIVEN a layout is active WHEN the user switches to a different layout THEN the previously active button loses its active style AND the status bar updates to show the new layout name | UI |

### AC-058E-05: Node Interaction

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-05a | GIVEN nodes are rendered WHEN the user clicks a node THEN the node and its direct neighbors are highlighted AND all other nodes/edges are dimmed AND the detail panel slides open from the right | UI |
| AC-058E-05b | GIVEN nodes are rendered WHEN the user hovers over a node THEN a Tippy.js tooltip appears showing: node label (bold), type + weight, and dimension tags — styled per mockup (dark background, white text, arrow) | UI |
| AC-058E-05c | GIVEN nodes are rendered WHEN the user right-clicks a node THEN a radial context menu appears with 4 options: Details (🔍), Expand (🔗), Pin (📌), Unpin (🔓) — with dark fill (rgba 15,23,42,0.88) and emerald active color | UI |
| AC-058E-05d | GIVEN the node context menu is open WHEN the user selects "Details" THEN `selectNodeById()` is called to highlight the node and open the detail panel | UI |
| AC-058E-05e | GIVEN the node context menu is open WHEN the user selects "Expand" THEN the node's closed neighborhood is highlighted AND all other nodes are dimmed | UI |
| AC-058E-05f | GIVEN the node context menu is open WHEN the user selects "Pin" THEN the node position is locked (`ele.lock()`) so it stays fixed during layout recalculations | UI |
| AC-058E-05g | GIVEN a pinned node exists WHEN the user right-clicks it and selects "Unpin" THEN the node is unlocked (`ele.unlock()`) and resumes participation in physics-based layouts | UI |
| AC-058E-05h | GIVEN a node is selected WHEN the user clicks on empty canvas space THEN all highlighting/dimming is removed AND the detail panel closes | UI |
| AC-058E-05i | GIVEN the canvas is visible WHEN the user right-clicks on empty canvas space THEN a radial context menu appears with 5 options: Fit View (⊡), Reset (🔄), Force (🌿), Hierarchy (🏗), Radial (🎯) — with blue active color | UI |

### AC-058E-06: Detail Panel

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-06a | GIVEN a node is selected WHEN the detail panel opens THEN it slides in from the right (340px wide, 0.3s cubic-bezier animation) displaying: header with type badge (colored icon), node name (16px bold, Syne font), and entity ID in monospace (format: "know_XXXXXXXX · type") | UI |
| AC-058E-06b | GIVEN the detail panel is open WHEN the user views the body THEN it shows sections for: Description, Dimensions (topic/abstraction/technology/audience tags with type-specific colors), Source Files, Related Nodes, and Metadata (weight, connections, created, updated) | UI |
| AC-058E-06c | GIVEN the detail panel shows dimension tags WHEN the user views them THEN tags are color-coded: topic=emerald, abstraction=violet, technology=blue, audience=amber (per mockup styling: pill shape, 3×8px padding, 11px font) | UI |
| AC-058E-06d | GIVEN the detail panel is open WHEN the user clicks the close button (×) THEN the panel slides out (right) AND all node highlighting is removed | UI |
| AC-058E-06e | GIVEN the detail panel is open WHEN the user presses the ESC key THEN the panel closes (same as clicking ×) | UI |

### AC-058E-07: Source File Browser

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-07a | GIVEN the detail panel shows "Source Files" section WHEN the user clicks on the "SOURCE FILES" label THEN a modal window opens (reusing the existing FolderBrowserModal pattern) with a two-panel layout: left = folder/file tree view of the source files, right = content preview | UI |
| AC-058E-07b | GIVEN the source file modal is open WHEN the user clicks a file in the tree view THEN the right panel renders the file content using the existing `FilePreviewRenderer` (supporting markdown, YAML, and plain text) | UI |
| AC-058E-07c | GIVEN the source file modal is open WHEN the user clicks the close button, presses ESC, or clicks the backdrop THEN the modal closes and the detail panel remains open | UI |

### AC-058E-08: Related Node Navigation

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-08a | GIVEN the detail panel shows "Related Nodes" WHEN the user clicks a related node entry THEN the graph pans/zooms to center the clicked node AND selects it (highlights neighborhood, updates detail panel with that node's data) | UI |
| AC-058E-08b | GIVEN the detail panel shows "Related Nodes" WHEN the user views the list THEN each entry shows: a colored dot (matching node type), the node name, and the relation type with direction arrow (e.g., "← depends_on", "→ part_of") in monospace | UI |

### AC-058E-09: Search

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-09a | GIVEN the graph viewer is active WHEN the user types in the search bar (top area, per mockup) THEN after a 300ms debounce the query is sent to `GET /api/kb/ontology/search?q=<query>&graphs=<selected>` AND matching nodes are highlighted on the canvas AND non-matching nodes are dimmed | UI |
| AC-058E-09b | GIVEN search results have been returned WHEN the API response contains matching node IDs THEN those nodes and their direct neighborhoods are given the "highlighted" class AND all other elements receive the "dimmed" class | UI |
| AC-058E-09c | GIVEN a search is active WHEN the user clears the search input THEN all "highlighted" and "dimmed" classes are removed AND the graph returns to normal display | UI |
| AC-058E-09d | GIVEN the graph viewer is active WHEN the user presses "/" (and is not focused on another input) THEN the search input receives focus | UI |
| AC-058E-09e | GIVEN graphs are selected WHEN the user submits a search query THEN the API calls the `search.py` module's search function scoped to the selected graph files AND returns matching node IDs with relevance | API |

### AC-058E-10: Scope Management

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-10a | GIVEN graphs are selected via sidebar checkboxes WHEN the selection changes THEN the scope pills area (top bar, per mockup) updates to show a pill for each selected graph with an emerald dot and graph name | UI |
| AC-058E-10b | GIVEN scope pills are visible WHEN the user clicks the "×" on a scope pill THEN that graph is deselected (sidebar checkbox unchecked, graph data removed from canvas, pill removed) | UI |
| AC-058E-10c | GIVEN the scope pills area is visible WHEN the user clicks the "+" button THEN a dropdown appears showing unselected graphs for quick addition | UI |

### AC-058E-11: Zoom & Pan Controls

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-11a | GIVEN the graph viewer is active WHEN the user views the bottom-right corner THEN zoom controls are visible: "+" (zoom in), "−" (zoom out), "⊡" (fit to view) — styled as 36×36px buttons per mockup | UI |
| AC-058E-11b | GIVEN the zoom controls are visible WHEN the user clicks "+" THEN the graph zooms in by factor 1.2 centered on the viewport AND the status bar zoom percentage updates | UI |
| AC-058E-11c | GIVEN the zoom controls are visible WHEN the user clicks "−" THEN the graph zooms out by factor 1.2 centered on the viewport AND the status bar zoom percentage updates | UI |
| AC-058E-11d | GIVEN the zoom controls are visible WHEN the user clicks "⊡" THEN `cy.fit(undefined, 40)` is called to show all elements with 40px padding | UI |
| AC-058E-11e | GIVEN the graph is rendered WHEN the user scrolls the mouse wheel on the canvas THEN Cytoscape.js zooms with wheelSensitivity 0.3 AND the status bar zoom percentage updates | UI |

### AC-058E-12: Minimap / Navigator

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-12a | GIVEN the graph viewer is active WHEN the user views the bottom-left corner THEN a navigator minimap (160×120px, per mockup) displays a thumbnail of the entire graph with a viewport rectangle showing the currently visible area | UI |
| AC-058E-12b | GIVEN the minimap is visible WHEN the user drags the viewport rectangle on the minimap THEN the main canvas pans to match the new position | UI |

### AC-058E-13: Status Bar

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-13a | GIVEN the graph viewer is active WHEN the user views the bottom of the page THEN a 36px status bar displays: a green pulsing dot with "Connected", node count, edge count, active layout name, zoom percentage, and graph scope count — separated by "·" dots | UI |
| AC-058E-13b | GIVEN graphs are loaded WHEN the graph selection or data changes THEN the status bar node count, edge count, and scope count update dynamically | UI |
| AC-058E-13c | GIVEN a layout is switched WHEN the new layout finishes rendering THEN the status bar layout name updates (e.g., "Layout: Hierarchical") | UI |
| AC-058E-13d | GIVEN the user zooms in/out WHEN the zoom level changes THEN the status bar zoom percentage updates in real-time (e.g., "Zoom: 142%") | UI |

### AC-058E-14: Loading & Empty States

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-14a | GIVEN the graph viewer is opened WHEN graph data is being fetched from the API THEN a loading spinner is displayed on the canvas area | UI |
| AC-058E-14b | GIVEN the KB has no `.ontology/` folder or no graph files WHEN the graph viewer opens THEN an empty state illustration is shown with a message like "No ontology graphs found. Run KB Librarian intake to generate graphs." | UI |
| AC-058E-14c | GIVEN graph data is loaded WHEN the Cytoscape.js layout is computing THEN a brief loading indicator appears until the layout animation completes | UI |

### AC-058E-15: API Endpoints

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-15a | GIVEN the Flask app is running WHEN `GET /api/kb/ontology/graphs` is called THEN the API returns a JSON array of graph files from `knowledge-base/.ontology/` with each entry containing: `name`, `file_path`, `node_count`, `edge_count`, and `dominant_type` | API |
| AC-058E-15b | GIVEN a valid graph name WHEN `GET /api/kb/ontology/graph/<name>` is called THEN the API reads the corresponding `.jsonl` file from `.ontology/` AND returns JSON with `nodes` array (id, label, node_type, weight, description, dimensions, source_files, metadata) and `edges` array (source, target, relation_type, label) | API |
| AC-058E-15c | GIVEN an invalid graph name WHEN `GET /api/kb/ontology/graph/<name>` is called THEN the API returns HTTP 404 with `{"error": "Graph not found"}` | API |
| AC-058E-15d | GIVEN a search query and graph scope WHEN `GET /api/kb/ontology/search?q=<query>&graphs=<comma-separated>` is called THEN the API invokes the `search.py` module's search function scoped to the specified graphs AND returns `{"results": [{"node_id": "...", "label": "...", "graph": "...", "relevance": N}]}` | API |
| AC-058E-15e | GIVEN the `.graph-index.json` file exists in `.ontology/` WHEN `GET /api/kb/ontology/graphs` is called THEN the API reads graph metadata from the index file for fast listing (without parsing each JSONL) | API |
| AC-058E-15f | GIVEN the Flask app is running WHEN the ontology graph blueprint is registered THEN routes are registered under the `/api/kb/ontology/` prefix AND available at app startup | Integration |

### AC-058E-16: Mockup Fidelity

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|-------------------------------|-----------|
| AC-058E-16a | GIVEN the graph viewer is rendered WHEN compared to the linked mockup THEN the sidebar width (260px), graph canvas area, and status bar height (36px) match the mockup layout proportions | UI |
| AC-058E-16b | GIVEN the graph viewer is rendered WHEN compared to the linked mockup THEN node colors (emerald #10b981, blue #3b82f6, amber #f59e0b, violet #8b5cf6), circle shapes, and weight-based sizing match the mockup styling | UI |
| AC-058E-16c | GIVEN the graph viewer is rendered WHEN compared to the linked mockup THEN the glass-morphism styling on the layout picker (blur 10px, white 94% opacity) and minimap (blur 8px, white 92% opacity) match the mockup | UI |
| AC-058E-16d | GIVEN the graph viewer is rendered WHEN compared to the linked mockup THEN the Cartographic Light design system is applied: Syne font for display, Outfit for body, JetBrains Mono for monospace, and the slate color palette for backgrounds/text | UI |

## Functional Requirements

**FR-1: Graph Viewer Route & Blueprint**
A new Flask blueprint (`ontology_graph_bp`) registers API endpoints under `/api/kb/ontology/`. The graph viewer page is a client-side rendered view triggered by the Knowledge Graph nav icon (no separate Flask template — same SPA-MPA hybrid pattern as Workflow mode).

**FR-2: Graph Data Loading**
The backend reads graph data from `knowledge-base/.ontology/` directory. Graph list is derived from `.graph-index.json` (FEATURE-058-D) for metadata, and individual graph JSONL files for full node/edge data. The API transforms JSONL event-sourced data into Cytoscape.js-compatible JSON format (nodes array + edges array).

**FR-3: Multi-Graph Merged View**
When multiple graphs are selected, all their nodes and edges are merged into a single Cytoscape.js instance. Duplicate entity IDs across graphs are deduplicated (same entity appearing in multiple graphs is rendered once with edges from all graphs).

**FR-4: Server-Side Search**
Search queries are processed server-side using the `search.py` module from FEATURE-058-A. The API endpoint accepts a query string and graph scope, invokes the search function, and returns matching node IDs with relevance scores.

**FR-5: Source File Modal**
The source file browser reuses the existing `FolderBrowserModal` pattern. It displays a tree view of the entity's `source_files` paths on the left and a file content preview (via `FilePreviewRenderer`) on the right. Only files within the KB folder are browsable.

**FR-6: Real-Time Status Updates**
The status bar dynamically reflects: total node count, total edge count, active layout name, current zoom percentage, and number of graphs in scope. All values update reactively as the user interacts.

## Non-Functional Requirements

**NFR-1: Performance**
- Graph rendering must handle up to 500 nodes and 1000 edges without noticeable lag (<2s initial render).
- Layout switching animation must complete within the configured duration (600-800ms).
- Search debounce at 300ms to avoid excessive API calls.

**NFR-2: Responsiveness**
- The graph viewer must function on viewport widths ≥ 1024px.
- Sidebar and detail panel widths are fixed (260px, 340px); the canvas area fills remaining space.

**NFR-3: Browser Compatibility**
- Must work on modern browsers supporting CSS Grid, Flexbox, CSS Variables, and ES6+.
- Cytoscape.js v3.30.4 and all plugins are loaded from CDN (unpkg.com).

**NFR-4: Accessibility**
- Layout picker buttons and zoom controls must have ARIA labels.
- Keyboard navigation: "/" to focus search, "ESC" to close panels.
- Status bar text is readable by screen readers.

**NFR-5: CDN Dependencies**
- All Cytoscape.js plugins are loaded from verified CDN URLs (as documented in mockup and FEATURE-058-E technical considerations).
- Navigator plugin must use v2.0.2 (v2.0.4 returns 404).

## UI/UX Requirements

**Layout (per mockup):**
- Sidebar: 260px fixed left, full height, scrollable graph list, legend at bottom
- Canvas: fills remaining horizontal space, absolute-positioned Cytoscape container
- Detail panel: 340px fixed right, slides in/out with 0.3s animation
- Status bar: 36px fixed bottom, full width
- Layout picker: floating top-left of canvas, glass-morphism panel
- Zoom controls: floating bottom-right of canvas
- Minimap: floating bottom-left of canvas, 160×120px

**Design System (Cartographic Light, per mockup):**
- Display font: Syne (Google Fonts)
- Body font: Outfit (Google Fonts)
- Monospace font: JetBrains Mono (Google Fonts)
- Color palette: slate-50 through slate-900 for backgrounds/text
- Accent colors: emerald (#10b981), blue (#3b82f6), amber (#f59e0b), violet (#8b5cf6)
- Glass-morphism: backdrop-filter blur, semi-transparent white backgrounds
- Node styling: circles, color by type, size by weight (28 + weight × 4)
- Edge styling: bezier curves, labeled with relation type, arrow targets
- Grid overlay: 40×40px, slate-400 at 8% opacity

**Interactions (per mockup):**
- Node click → highlight neighborhood + open detail panel
- Node hover → Tippy.js tooltip (dark bg, type/weight/dimensions)
- Node right-click → radial context menu (Details/Expand/Pin/Unpin)
- Canvas right-click → radial context menu (Fit/Reset/Force/Hierarchy/Radial)
- Source files label click → modal with tree + preview
- Related node click → pan to and select that node
- Scope pill × → deselect graph
- Layout button click → switch algorithm with animation
- Zoom controls → zoom in/out/fit with status bar sync
- Search input → server-side search with 300ms debounce
- "/" key → focus search, "ESC" → close panels

## Dependencies

**Internal:**
| Dependency | Type | Description |
|------------|------|-------------|
| FEATURE-058-A | Required | Ontology Tool Skill — provides `graph_ops.py` (build/graph data), `search.py` (search), entity/relation data model |
| FEATURE-058-D | Required | KB Librarian Integration — populates `.ontology/` folder with graph files and `.graph-index.json` |
| Flask App (main) | Required | `src/x_ipe/app.py` blueprint registration, `index.html` nav icons, `init.js` mode switching |
| FolderBrowserModal | Reuse | `src/x_ipe/static/js/features/folder-browser-modal.js` — two-panel file browser modal |
| FilePreviewRenderer | Reuse | `src/x_ipe/static/js/core/file-preview-renderer.js` — markdown/YAML/text rendering |
| KB Service | Reuse | `src/x_ipe/services/kb_service.py` — file reading for source file preview |

**External (CDN):**
| Library | Version | CDN URL |
|---------|---------|---------|
| Cytoscape.js | 3.30.4 | unpkg.com/cytoscape@3.30.4/dist/cytoscape.min.js |
| cytoscape-fcose | 2.2.0 | unpkg.com/cytoscape-fcose@2.2.0/cytoscape-fcose.js |
| cytoscape-dagre | 2.5.0 | unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js |
| dagre | 0.8.5 | unpkg.com/dagre@0.8.5/dist/dagre.min.js |
| cytoscape-cxtmenu | 3.5.0 | unpkg.com/cytoscape-cxtmenu@3.5.0/cytoscape-cxtmenu.js |
| cytoscape-navigator | 2.0.2 | unpkg.com/cytoscape-navigator@2.0.2/cytoscape-navigator.js |
| @popperjs/core | 2.11.8 | unpkg.com/@popperjs/core@2.11.8/dist/umd/popper.min.js |
| tippy.js | 6.3.7 | unpkg.com/tippy.js@6.3.7/dist/tippy-bundle.umd.min.js |

## Business Rules

**BR-1:** The graph viewer is read-only — no entity creation, editing, or deletion from the UI. All mutations go through the Ontology Tool Skill CLI (FEATURE-058-A).

**BR-2:** Graph data freshness depends on KB Librarian intake runs. The viewer shows whatever data exists in `.ontology/` at the time of loading. No real-time sync.

**BR-3:** When multiple graphs contain the same entity ID, the merged view renders the entity once. Edges from all selected graphs are combined.

**BR-4:** Search scope is limited to selected graphs. If no graphs are selected, search returns empty results.

**BR-5:** Source file browsing is limited to files within the active KB folder. Paths outside the KB are displayed as text only (not clickable).

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| KB has no `.ontology/` folder | Empty state: "No ontology graphs found" illustration |
| `.ontology/` exists but has no graph files | Empty state: "No graphs available" message |
| Graph file exists but is empty (0 entities) | Graph loads with empty canvas, status bar shows "0 nodes · 0 edges" |
| Graph has 500+ nodes | Render normally; layout may take up to 2 seconds |
| Graph has orphaned nodes (no edges) | Nodes render at positions determined by layout algorithm |
| Duplicate entity IDs across selected graphs | Single node rendered with merged edges from all graphs |
| Source file path doesn't exist on disk | Display file path as text (not clickable), no error |
| Search returns no results | All nodes dimmed, status message "No matches found" |
| API endpoint unreachable | Error state on canvas: "Failed to load graph data. Check your connection." |
| User rapidly toggles graphs | Debounce graph loading by 200ms to avoid rapid re-renders |
| JSONL file is malformed | API returns error; graph excluded from list with warning in sidebar |
| Browser window resized | Cytoscape.js `cy.resize()` called on window resize; layout re-fits |

## Out of Scope

- **AI Agent Terminal**: UI and functionality for the "Search with AI Agent" button → FEATURE-058-F
- **BFS Graph Search**: Advanced graph traversal search → FEATURE-058-F
- **Cross-graph aggregated search**: Multi-graph deep search with pagination → FEATURE-058-F
- **Graph editing**: Creating, updating, or deleting entities/relations from the UI
- **Export/print**: PNG/SVG export, PDF generation, or print styles
- **Theme switching**: Only Cartographic Light theme (no dark mode toggle)
- **Node batch operations**: Multi-select with shift/ctrl click
- **Undo/redo history**: No action history or state restoration
- **Pin position persistence**: Pinned node positions are session-only (lost on page reload)
- **Custom node types**: Only the 4 built-in types (concept, document, entity, dimension)
- **Dimension filtering from UI**: Filtering graph by dimension tags (e.g., show only "Python" nodes)

## Technical Considerations

- The graph viewer follows the same SPA content-switching pattern as Workflow mode: a nav icon toggles the view, hiding the sidebar and rendering the viewer into the main content area.
- New Flask blueprint with 3-4 API endpoints; data read from `.ontology/` directory using existing `graph_ops.py` and `search.py` modules.
- CDN-loaded Cytoscape.js libraries — no npm bundling required. Scripts loaded dynamically when the graph viewer is activated.
- The source file browser modal reuses `FolderBrowserModal` and `FilePreviewRenderer` — existing code, no new file preview logic needed.
- JSONL → Cytoscape.js JSON transformation happens server-side in the API endpoint, not in the browser.
- The `.graph-index.json` manifest (FEATURE-058-D) provides fast graph listing without parsing every JSONL file.

## Open Questions

*None — all design questions resolved during refinement.*
