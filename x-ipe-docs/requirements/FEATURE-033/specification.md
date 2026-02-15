# Feature Specification: App-Agent Interaction MCP

> Feature ID: FEATURE-033
> Version: v1.1
> Status: Refined
> Last Updated: 02-15-2026

## Version History

| Version | Date | Description | Change Request |
|---------|------|-------------|----------------|
| v1.0 | 02-13-2026 | Initial specification — MCP server with save_uiux_reference tool | - |
| v1.1 | 02-15-2026 | Extended data schema (html_css, static_resources), auto-generated structured output (page-element-references, summarized-uiux-reference.md, mimic-strategy.md) | [CR-001](./CR-001.md) |

## Overview

FEATURE-033 introduces a new standalone MCP (Model Context Protocol) server called `x-ipe-app-and-agent-interaction` that provides a general-purpose communication bridge between the X-IPE web application (Flask backend) and CLI agents (Copilot, Claude Code, OpenCode). The MCP server exposes tools that call new REST endpoints on the existing Flask backend, enabling agents to push data into the X-IPE application.

The first use case is UIUX Reference data persistence: agents extract design reference data from external web pages via Chrome DevTools and need to save that data (colors, elements, screenshots, design tokens) back to the X-IPE idea folder structure. The MCP server is designed with extensible tool registration so future app↔agent interaction endpoints can be added without architectural changes.

## User Stories

- As a **CLI agent**, I want to **call a `save_uiux_reference` MCP tool with reference data JSON**, so that **the data is validated and saved to the correct idea folder without needing to know the folder structure**.
- As a **CLI agent**, I want to **receive descriptive error messages when submitting invalid data**, so that **I can correct the request and retry**.
- As a **developer**, I want to **add new MCP tools for future app-agent interactions**, so that **the MCP server can be extended without architectural changes**.
- As a **CLI agent**, I want to **save multiple reference sessions for the same idea**, so that **each session is preserved and a merged view is maintained**.
- As a **CLI agent**, I want to **include base64-encoded screenshots in the reference data**, so that **the Flask endpoint decodes and saves them as image files**.

## Acceptance Criteria

### AC-033.1: Save Valid Reference Data
- [ ] Given the MCP server is running and Flask backend is accessible
- [ ] When the agent calls `save_uiux_reference` with valid reference JSON
- [ ] Then the Flask backend saves a session JSON file and returns success

### AC-033.2: Screenshot Persistence
- [ ] Given reference data includes base64-encoded screenshots
- [ ] When the agent sends the data via MCP
- [ ] Then screenshots are decoded and saved as image files

### AC-033.3: Schema Validation Error
- [ ] Given malformed or incomplete reference JSON
- [ ] Then HTTP 400 with descriptive error message

### AC-033.4: Merged Reference Data
- [ ] Given multiple sessions saved for same idea
- [ ] Then `reference-data.json` is created/updated as merged view

### AC-033.5: Auto-Increment Session Numbering
- [ ] Session files auto-increment regardless of client-provided session_id

### AC-033.6: Idea Folder Not Found
- [ ] Returns HTTP 404 with descriptive error message

### AC-033.7: MCP Server Connectivity
- [ ] Returns clear error when Flask backend unreachable

### AC-033.8: Directory Auto-Creation
- [ ] Auto-creates `uiux-references/` subdirectories on first save

### AC-033.9: Extended Element Schema (v1.1)
- [ ] Given element data includes `html_css` with `outer_html` and `computed_styles`
- [ ] Then service saves `{id}-structure.html` and `{id}-styles.css` in `page-element-references/resources/`

### AC-033.10: Static Resources (v1.1)
- [ ] Given reference data includes `static_resources` list with `{type, src, usage}` entries
- [ ] Then resources are included in `summarized-uiux-reference.md` and `mimic-strategy.md`

### AC-033.11: Structured Output Generation (v1.1)
- [ ] Given elements contain `html_css` data
- [ ] Then service auto-generates `page-element-references/summarized-uiux-reference.md` and `mimic-strategy.md`
- [ ] Backward compatible: v1.0 payloads (no `html_css`) produce no structured output

## Functional Requirements

### FR-033.1: MCP Server Process
Standalone MCP server using FastMCP, stdio transport.

### FR-033.2: MCP Tool — `save_uiux_reference`
Accepts reference data JSON, forwards to Flask backend.

### FR-033.3: Flask Endpoint — `POST /api/ideas/uiux-reference`
Validates and persists UIUX reference data.

### FR-033.4: Session File Persistence
Auto-incrementing `ref-session-{NNN}.json` files.

### FR-033.5: Merged Reference Data
Top-level `reference-data.json` merging all sessions.

### FR-033.6: Screenshot Decoding and Storage
Base64 screenshots decoded and saved as image files.

### FR-033.7: Extensible Tool Registration
Architecture supports adding new tools without structural changes.

## Non-Functional Requirements

### NFR-033.1: MCP Convention Compliance
FastMCP, stdio transport, deployed via MCPDeployerService.

### NFR-033.2: JSON Schema Validation
Required fields validated before processing.

### NFR-033.3: Error Response Quality
Structured error responses for agent consumption.

### NFR-033.4: Performance
Response within 5 seconds for data up to 10MB. Atomic writes.

### NFR-033.5: Compatibility
Works with all 3 CLI adapters (Copilot, Claude Code, OpenCode).

## Dependencies

### External Dependencies
- **FastMCP** — MCP server framework
- **Flask** (existing) — Web framework
- **Chrome DevTools MCP** (existing, external) — Browser interaction

## Business Rules

- **BR-033.1:** Session files are append-only
- **BR-033.2:** `reference-data.json` regenerated on each save
- **BR-033.3:** Base64 data must be prefixed with `base64:`
- **BR-033.4:** Only write to existing idea folders
- **BR-033.5:** Sequential session numbering by scanning existing files
