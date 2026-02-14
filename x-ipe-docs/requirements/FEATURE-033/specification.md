# Feature Specification: App-Agent Interaction MCP

> Feature ID: FEATURE-033
> Version: v1.1
> Status: Refined
> Last Updated: 02-14-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.1 | 02-14-2026 | Add `inject_script` tool for browser script injection via CDP | [CR-001](./CR-001.md) |
| v1.0 | 02-13-2026 | Initial specification | - |

## Overview

FEATURE-033 introduces a new standalone MCP (Model Context Protocol) server called `x-ipe-app-and-agent-interaction` that provides a general-purpose communication bridge between the X-IPE web application (Flask backend) and CLI agents (Copilot, Claude Code, OpenCode). The MCP server exposes tools that call new REST endpoints on the existing Flask backend, enabling agents to push data into the X-IPE application.

The first use case is UIUX Reference data persistence: agents extract design reference data from external web pages via Chrome DevTools and need to save that data (colors, elements, screenshots, design tokens) back to the X-IPE idea folder structure. The MCP server is designed with extensible tool registration so future app↔agent interaction endpoints can be added without architectural changes.

The primary users are CLI agents that interact with the X-IPE system. The Flask endpoint serves as the data persistence layer, validating incoming data and organizing it into the correct folder structure.

## User Stories

- As a **CLI agent**, I want to **call a `save_uiux_reference` MCP tool with reference data JSON**, so that **the data is validated and saved to the correct idea folder without needing to know the folder structure**.
- As a **CLI agent**, I want to **receive descriptive error messages when submitting invalid data**, so that **I can correct the request and retry**.
- As a **developer**, I want to **add new MCP tools for future app-agent interactions**, so that **the MCP server can be extended without architectural changes**.
- As a **CLI agent**, I want to **save multiple reference sessions for the same idea**, so that **each session is preserved and a merged view is maintained**.
- As a **CLI agent**, I want to **include base64-encoded screenshots in the reference data**, so that **the Flask endpoint decodes and saves them as image files**.
- As a **CLI agent**, I want to **inject a JavaScript file into the currently active browser page via an MCP tool**, so that **I can set up toolbars and utilities without wasting context tokens on inline script content**. *(v1.1 — CR-001)*
- As a **CLI agent**, I want to **inject inline JavaScript code into the browser page via an MCP tool**, so that **I can execute small scripts without needing a file on disk**. *(v1.1 — CR-001)*
- As a **CLI agent**, I want to **receive clear feedback when script injection fails** (e.g., no browser, wrong page), so that **I can diagnose and retry**. *(v1.1 — CR-001)*

## Acceptance Criteria

### AC-033.1: Save Valid Reference Data
- [ ] Given the MCP server is running and Flask backend is accessible
- [ ] When the agent calls `save_uiux_reference` with valid reference JSON containing `idea_folder`, `session_id`, `source_url`, `timestamp`, and at least one of `colors`, `elements`, or `design_tokens`
- [ ] Then the Flask backend receives the POST request, saves a session JSON file to `x-ipe-docs/ideas/{idea_folder}/uiux-references/sessions/ref-session-{NNN}.json`, and returns a success response with the saved file path

### AC-033.2: Screenshot Persistence
- [ ] Given reference data includes `elements` with `screenshots` containing base64-encoded PNG data
- [ ] When the agent sends the data via MCP `save_uiux_reference`
- [ ] Then the Flask endpoint decodes each base64 screenshot and saves it to `x-ipe-docs/ideas/{idea_folder}/uiux-references/screenshots/` using the naming convention (`full-page-{NNN}.png`, `elem-{NNN}-crop.png`)
- [ ] And the saved session JSON references the local file paths instead of base64 data

### AC-033.3: Schema Validation Error
- [ ] Given the agent sends malformed or incomplete reference JSON (e.g., missing `idea_folder`, missing `session_id`, invalid `version`)
- [ ] When the MCP tool calls the Flask endpoint
- [ ] Then the endpoint returns HTTP 400 with a JSON error body containing `error` (error code) and `message` (human-readable description of what is missing/invalid)
- [ ] And the MCP tool returns the error message to the agent

### AC-033.4: Merged Reference Data
- [ ] Given multiple sessions have been saved for the same idea (e.g., `ref-session-001.json`, `ref-session-002.json`)
- [ ] When the Flask endpoint saves a new session
- [ ] Then `x-ipe-docs/ideas/{idea_folder}/uiux-references/reference-data.json` is created or updated as a merged view containing all sessions' colors, elements, and design tokens

### AC-033.5: Auto-Increment Session Numbering
- [ ] Given an idea folder already has `ref-session-001.json` and `ref-session-002.json`
- [ ] When a new reference session is saved
- [ ] Then the Flask endpoint auto-assigns `ref-session-003.json` regardless of the `session_id` value in the request
- [ ] And the response includes the assigned session filename

### AC-033.6: Idea Folder Not Found
- [ ] Given the `idea_folder` value does not match any existing folder under `x-ipe-docs/ideas/`
- [ ] When the agent calls `save_uiux_reference`
- [ ] Then the endpoint returns HTTP 404 with a descriptive error message: `Idea folder not found: {idea_folder}`

### AC-033.7: MCP Server Connectivity
- [ ] Given the MCP server is running but the Flask backend is unreachable (server down or wrong URL)
- [ ] When the agent calls `save_uiux_reference`
- [ ] Then the MCP tool returns a clear error message indicating the backend is unreachable, with the attempted URL

### AC-033.8: Directory Auto-Creation
- [ ] Given an idea folder exists but has no `uiux-references/` subfolder
- [ ] When the first reference session is saved
- [ ] Then the Flask endpoint automatically creates the `uiux-references/`, `uiux-references/sessions/`, and `uiux-references/screenshots/` directories

### AC-033.9: Inject Script from File *(v1.1 — CR-001)*
- [ ] Given the MCP server is running and a browser page is open with Chrome remote debugging enabled (`--remote-debugging-port`)
- [ ] When the agent calls `inject_script` with `file_path` pointing to a valid JavaScript file (e.g., `toolbar.min.js`)
- [ ] Then the MCP server reads the file content, connects to the browser via CDP WebSocket, executes `Runtime.evaluate` with the file content on the active page, and returns a success response
- [ ] And the script executes in the page context with full DOM access

### AC-033.10: Inject Inline Script *(v1.1 — CR-001)*
- [ ] Given the MCP server is running and a browser page is open with Chrome remote debugging enabled
- [ ] When the agent calls `inject_script` with `script` containing inline JavaScript code (and no `file_path`)
- [ ] Then the MCP server connects via CDP and executes the inline script on the active page
- [ ] And returns the script's return value (if JSON-serializable) in the response

### AC-033.11: CDP Connection Discovery *(v1.1 — CR-001)*
- [ ] Given Chrome is running with `--remote-debugging-port=9222`
- [ ] When the agent calls `inject_script`
- [ ] Then the MCP server discovers available pages via `GET http://localhost:{port}/json`
- [ ] And selects the first non-extension, non-devtools page (or the page matching an optional `target_url` parameter)
- [ ] And connects via the page's `webSocketDebuggerUrl`

### AC-033.12: Injection Error — No Browser *(v1.1 — CR-001)*
- [ ] Given Chrome is not running or remote debugging is not enabled
- [ ] When the agent calls `inject_script`
- [ ] Then the MCP tool returns a structured error: `{ "error": "CDP_CONNECTION_FAILED", "message": "Cannot connect to Chrome DevTools at localhost:{port}. Ensure Chrome is running with --remote-debugging-port={port}" }`

### AC-033.13: Injection Error — Script Evaluation Failure *(v1.1 — CR-001)*
- [ ] Given a browser page is available via CDP
- [ ] When the agent calls `inject_script` with a script that throws a runtime error
- [ ] Then the MCP tool returns a structured error containing the exception message and stack trace from the browser

## Functional Requirements

### FR-033.1: MCP Server Process

**Description:** A new standalone MCP server named `x-ipe-app-and-agent-interaction` that runs as an independent process.

**Details:**
- Input: MCP server configuration (Flask backend URL, default: `http://localhost:5000`)
- Process: Start MCP server using FastMCP (Python) or MCP SDK; register tools; listen for agent requests via stdio transport
- Output: Running MCP server process that agents can connect to

### FR-033.2: MCP Tool — `save_uiux_reference`

**Description:** An MCP tool that accepts reference data JSON and forwards it to the Flask backend endpoint.

**Details:**
- Input: Reference data JSON object with fields: `version` (string), `source_url` (string), `auth_url` (string, optional), `timestamp` (ISO 8601 string), `idea_folder` (string), `colors` (array, optional), `elements` (array, optional), `design_tokens` (object, optional)
- Process: Validate required fields locally, POST the data to `{base_url}/api/ideas/uiux-reference`, return the Flask response to the agent
- Output: Success response with saved file path, or error response with descriptive message

### FR-033.3: Flask Endpoint — `POST /api/ideas/uiux-reference`

**Description:** A new Flask endpoint that validates and persists UIUX reference data to the idea folder structure.

**Details:**
- Input: JSON request body conforming to the Reference Data JSON Schema (see Technical Considerations)
- Process: Validate JSON schema, resolve idea folder path, auto-create subdirectories, assign session number, decode base64 screenshots, save session JSON, update merged `reference-data.json`
- Output: JSON response with `status: "success"`, `session_file` (saved filename), `session_number` (assigned number)

### FR-033.4: Session File Persistence

**Description:** Each reference session is saved as an individual JSON file with auto-incrementing numbering.

**Details:**
- Input: Validated reference data JSON
- Process: Scan `uiux-references/sessions/` for existing `ref-session-{NNN}.json` files, determine next number (zero-padded 3 digits), save session JSON
- Output: File at `x-ipe-docs/ideas/{idea_folder}/uiux-references/sessions/ref-session-{NNN}.json`

### FR-033.5: Merged Reference Data

**Description:** A top-level `reference-data.json` file that merges all session data for an idea.

**Details:**
- Input: All `ref-session-{NNN}.json` files in the sessions folder
- Process: Read all session files, merge `colors` arrays (deduplicate by `id`), merge `elements` arrays (deduplicate by `id`), use latest session's `design_tokens`, record `source_urls` list and `last_updated` timestamp
- Output: `x-ipe-docs/ideas/{idea_folder}/uiux-references/reference-data.json`

### FR-033.6: Screenshot Decoding and Storage

**Description:** Base64-encoded screenshots in the reference data are decoded and saved as image files.

**Details:**
- Input: Reference data with `elements[].screenshots.full_page` and/or `elements[].screenshots.element_crop` as base64 strings (prefixed with `base64:` to distinguish from file paths)
- Process: Detect base64 prefix, decode, save to `uiux-references/screenshots/` using naming conventions, replace base64 data in session JSON with relative file path
- Output: PNG files in screenshots folder, session JSON with file path references

### FR-033.7: Extensible Tool Registration

**Description:** The MCP server architecture supports adding new tools without structural changes.

**Details:**
- Input: New tool definition (name, description, parameters, handler function)
- Process: Register tool with the MCP server framework; each tool maps to a Flask backend endpoint
- Output: Tool available for agent use

### FR-033.8: MCP Tool — `inject_script` *(v1.1 — CR-001)*

**Description:** An MCP tool that injects JavaScript into the active browser page via Chrome DevTools Protocol (CDP).

**Details:**
- Input: One of the following (mutually exclusive):
  - `file_path` (string): Absolute or project-relative path to a `.js` file to inject
  - `script` (string): Inline JavaScript code to execute
- Optional input:
  - `target_url` (string, optional): URL pattern to match a specific browser tab (default: first non-extension page)
  - `cdp_port` (integer, optional): Chrome remote debugging port (default: 9222)
- Process: Read file content (if `file_path`), discover browser pages via CDP HTTP endpoint, select target page, connect via WebSocket, send `Runtime.evaluate` command, return result or error
- Output: Success response with script evaluation result, or structured error

### FR-033.9: CDP Client Module *(v1.1 — CR-001)*

**Description:** A lightweight CDP (Chrome DevTools Protocol) client for browser communication.

**Details:**
- Input: CDP port number, optional target URL pattern
- Process: HTTP GET `localhost:{port}/json` for page discovery, WebSocket connect to `webSocketDebuggerUrl`, send/receive CDP JSON messages
- Output: Page list for discovery, script evaluation result for injection
- Constraints: Short-lived connections (connect → evaluate → disconnect) to avoid conflicts with Chrome DevTools MCP; no Playwright/Puppeteer dependency; use `websockets` Python package

## Non-Functional Requirements

### NFR-033.1: MCP Convention Compliance

The MCP server must follow X-IPE MCP conventions:
- Use Python FastMCP framework (consistent with existing Python codebase)
- Stdio transport (same as chrome-devtools MCP)
- Server entry point: `x_ipe.mcp.app_agent_interaction` (invoked as `uv run python -m x_ipe.mcp.app_agent_interaction`)
- Configuration added to both `.github/copilot/mcp-config.json` and `src/x_ipe/resources/copilot/mcp-config.json`
- Deployed via existing MCPDeployerService during `x-ipe init` or `x-ipe upgrade` — the deployer handles format conversion for all 3 CLI adapters:
  - **Copilot** (global format): merges into `~/.copilot/mcp-config.json`
  - **Claude Code** (project format): merges into `.mcp.json` at project root
  - **OpenCode** (nested format): merges into `opencode.json` with `command` as array and `enabled: true`

### NFR-033.2: JSON Schema Validation

The Flask endpoint must validate the incoming JSON against a defined schema before processing:
- Required fields: `version`, `source_url`, `timestamp`, `idea_folder`
- At least one data section must be present: `colors`, `elements`, or `design_tokens`
- Validation errors must specify which field failed and why

### NFR-033.3: Error Response Quality

All error responses must be structured for agent consumption:
- JSON format: `{ "error": "ERROR_CODE", "message": "Human-readable description", "details": {} }`
- Error codes: `VALIDATION_ERROR`, `IDEA_NOT_FOUND`, `WRITE_ERROR`, `BACKEND_UNREACHABLE`
- HTTP status codes: 400 (validation), 404 (not found), 500 (server error)

### NFR-033.4: Performance

- Flask endpoint must respond within 5 seconds for reference data up to 10MB (including base64 screenshots)
- Session file write must be atomic (write to temp file, then rename) to prevent corruption

### NFR-033.5: Compatibility

- MCP server must work with all 3 supported CLI adapters (Copilot, Claude Code, OpenCode)
- Flask endpoint must be accessible on the same port as the existing app (default: 5000)

## UI/UX Requirements

Not applicable — FEATURE-033 is a backend-only feature (MCP server + Flask endpoint). No UI components are involved.

## Dependencies

### Internal Dependencies

- **Existing Flask backend** (`src/x_ipe/app.py`): The new endpoint is registered as a new blueprint on the existing Flask application
- **MCPDeployerService** (`src/x_ipe/services/mcp_deployer_service.py`): Deploys the MCP server configuration to CLI adapter config files
- **Ideas folder structure** (`x-ipe-docs/ideas/`): The endpoint writes data into existing idea folders

### External Dependencies

- **FastMCP** (Python package): MCP server framework for creating the standalone server
- **Flask** (existing): Web framework for the new endpoint
- **Chrome DevTools MCP** (existing, external): Provides the browser interaction that generates the reference data (upstream dependency, not direct)
- **websockets** (Python package): WebSocket client for CDP communication *(v1.1 — CR-001)*

## Business Rules

- **BR-033.1:** Session files are append-only — saving a new session never overwrites or deletes existing session files
- **BR-033.2:** The `reference-data.json` merged file is regenerated on each session save by reading all session files
- **BR-033.3:** Base64 screenshot data in submitted JSON must be prefixed with `base64:` to distinguish from file path references
- **BR-033.4:** The Flask endpoint must only write to idea folders that already exist — it must not create new idea folders
- **BR-033.5:** Session numbering is sequential and gap-free within an idea; determined by scanning existing files, not by trusting client-provided `session_id`
- **BR-033.6:** CDP connections for `inject_script` must be short-lived (connect → evaluate → disconnect) to avoid conflicts with Chrome DevTools MCP server sessions *(v1.1 — CR-001)*
- **BR-033.7:** The `inject_script` tool requires exactly one of `file_path` or `script` — providing both or neither is a validation error *(v1.1 — CR-001)*
- **BR-033.8:** File paths provided to `inject_script` must be resolved relative to the project root; absolute paths are also accepted *(v1.1 — CR-001)*

## Edge Cases & Constraints

| Scenario | Expected Behavior |
|----------|-------------------|
| Idea folder name contains special characters (e.g., `018. Feature-UIUX Reference`) | URL-encode when resolving path; validate folder exists on disk |
| Request body exceeds 10MB | Flask returns 413 (Request Entity Too Large) with descriptive message |
| Concurrent saves to the same idea | Use file locking or atomic writes to prevent corruption; second request waits or retries |
| Empty `colors`, `elements`, and `design_tokens` arrays/objects | Return 400 — at least one data section must contain data |
| `screenshots` field contains a file path instead of base64 | Leave as-is (no decoding); only decode values prefixed with `base64:` |
| Flask backend restarts between MCP tool calls | MCP tool retries once after a connection error before returning failure |
| Session folder already has files with gaps (e.g., 001, 003) | Next session is 004 (use max existing + 1, not count) |
| Reference data contains `colors` with duplicate `id` values within the same session | Accept as-is (validation is per-field, not cross-field); merging deduplicates by `id` keeping latest |
| CDP port is in use by another service (not Chrome) | `inject_script` returns `CDP_CONNECTION_FAILED` with descriptive message *(v1.1)* |
| Multiple Chrome pages open; no `target_url` provided | Select the first non-extension, non-devtools page from the page list *(v1.1)* |
| Script file does not exist at `file_path` | Return `FILE_NOT_FOUND` error with the resolved path *(v1.1)* |
| Script file is very large (>1MB) | Accept and inject — `Runtime.evaluate` handles large scripts; log a warning *(v1.1)* |
| Chrome DevTools MCP has an active session on the same page | Short-lived CDP connection avoids conflicts; connect → evaluate → disconnect immediately *(v1.1)* |
| `file_path` points outside project directory | Accept the path — agent may need to inject scripts from skill folders or other locations *(v1.1)* |

## Out of Scope

- **GET endpoint** for retrieving reference data (Phase 2 — read operations)
- **DELETE/PATCH endpoints** for modifying or removing reference data (Phase 2)
- **Asset download** (fonts, icons, images) — handled by FEATURE-030-B agent skill, not by this MCP server
- **Design system generation** from design tokens — handled by FEATURE-032
- **MCP authentication/authorization** — not needed for local-only communication
- **WebSocket/SSE real-time updates** — not needed for Phase 1 (simple request-response)
- **Binary asset storage** (computed-styles.json, rules.css, fonts, icons) — Phase 1 only handles screenshots; extended asset storage is Phase 2
- **Browser lifecycle management** via `inject_script` — the tool does not launch, close, or navigate Chrome; it only injects into an already-open page *(v1.1)*
- **Persistent CDP sessions** — `inject_script` uses ephemeral connections; persistent page monitoring or event subscriptions are not supported *(v1.1)*

## Technical Considerations

- The MCP server should be a small Python script using FastMCP, following the pattern of existing MCP servers deployed via MCPDeployerService
- The Flask endpoint should follow the existing blueprint pattern (see `ideas_routes.py`) with a new blueprint registered in `app.py`
- The Reference Data JSON Schema from the idea summary (version 1.0) defines the contract between the MCP tool and Flask endpoint
- Atomic file writes (write to `.tmp`, then `os.rename`) should be used for both session files and `reference-data.json` to prevent partial writes
- The MCP server needs to know the Flask backend URL; this should be configurable (default `http://localhost:5000`)
- The `x_ipe_tracing` decorator should be applied to the Flask endpoint for consistency with existing routes
- The `inject_script` tool should use a lightweight CDP client (~50 lines) built on the `websockets` Python package — no Playwright/Puppeteer dependency *(v1.1 — CR-001)*
- CDP page discovery via `GET http://localhost:{port}/json` returns a JSON array of page descriptors; filter by `type == "page"` and exclude `chrome-extension://` URLs *(v1.1 — CR-001)*
- The `inject_script` tool does not route through the Flask backend — it communicates directly with Chrome via CDP WebSocket, keeping the tool self-contained within the MCP server *(v1.1 — CR-001)*

## Open Questions

None — all clarifications resolved during requirement gathering (see requirement-details-part-8.md).
