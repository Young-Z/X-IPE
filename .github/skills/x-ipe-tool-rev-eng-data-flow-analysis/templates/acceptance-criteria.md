# Acceptance Criteria — Section 6: Data Flow / Protocol Analysis

## Required Criteria [REQ]

### REQ-6.1: End-to-End Request Flow Documented

- **Rule:** At least 1 complete end-to-end request flow MUST be documented
- **Method:** `file_exists` + `section_parse` → `01-request-flows.md`
- **Validation:** File contains a flow with entry point → processing steps → response, each step named
- **Evidence:** Flow starts at an HTTP handler, CLI command, or event listener and terminates at a response or side effect
- **Fail if:** No complete request flow present (partial traces without resolution do not count)

### REQ-6.2: File:Line Citations at Each Step

- **Rule:** Every flow step MUST cite the source file:line where processing occurs
- **Method:** `section_parse` → all subsection files
- **Validation:** Each step entry contains a `file:line` reference matching pattern `path/to/file.ext:N`
- **Evidence:** Citations verified against actual source code at repo_path
- **Fail if:** Any flow step lacks file:line citation

### REQ-6.3: Data Shape at Transformation Steps

- **Rule:** Data shape MUST be documented at each point where data is transformed
- **Method:** `section_parse` → `01-request-flows.md` and `03-data-transformations.md`
- **Validation:** Transformation steps include input shape and output shape (field names + types)
- **Evidence:** Shapes match actual type definitions, dataclasses, or interfaces in source
- **Fail if:** Transformation steps present without data shape documentation

### REQ-6.4: Mermaid Sequence Diagram for Critical Flows

- **Rule:** At least 1 Mermaid sequenceDiagram MUST be present for critical flows
- **Method:** `section_parse` → `01-request-flows.md`
- **Validation:** Contains a valid `sequenceDiagram` code block with participants and messages
- **Evidence:** Diagram participants match the modules/services in the traced flow
- **Fail if:** No Mermaid sequence diagram present

---

## Optional Criteria [OPT]

### OPT-6.5: Event-Driven Flows Documented

- **Rule:** Event-driven communication patterns SHOULD be documented
- **Method:** `file_exists` → `02-event-propagation.md`
- **Validation:** File contains event name, publisher file:line, subscriber file:line, payload shape
- **Evidence:** Events match actual EventEmitter/signal/queue usage in source code
- **Incomplete if:** File missing or contains only placeholder text

### OPT-6.6: Communication Protocols Identified

- **Rule:** Communication protocols in use SHOULD be identified
- **Method:** `file_exists` → `04-protocol-details.md`
- **Validation:** File lists protocol type, technology, configuration location, serialization format
- **Evidence:** Protocol entries match actual library usage and configuration files
- **Incomplete if:** File missing or contains only placeholder text

---

## Validation Summary

| ID | Criterion | Level | Method |
|----|-----------|-------|--------|
| REQ-6.1 | End-to-end request flow documented | Required | file_exists + section_parse |
| REQ-6.2 | File:line citations at each step | Required | section_parse |
| REQ-6.3 | Data shape at transformation steps | Required | section_parse |
| REQ-6.4 | Mermaid sequence diagram for critical flows | Required | section_parse |
| OPT-6.5 | Event-driven flows documented | Optional | file_exists |
| OPT-6.6 | Communication protocols identified | Optional | file_exists |

---

## Status Definitions

- **PASS:** Criterion fully satisfied with evidence
- **FAIL:** Criterion attempted but content is incorrect or insufficient
- **INCOMPLETE:** Criterion not addressed (content missing)
