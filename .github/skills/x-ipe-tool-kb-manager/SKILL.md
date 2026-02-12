---
name: x-ipe-tool-kb-manager
description: Knowledge Base Manager - classify landing items into topics, generate AI summaries, search knowledge base, reorganize topics. Use when managing KB content. Triggers on "classify landing items", "process knowledge base", "search kb", "search knowledge", "reorganize topics", "cancel processing".
---

# Knowledge Base Manager

## Purpose

AI Agents follow this skill to manage Knowledge Base content by:
1. Classifying landing zone files into topics via AI suggestions
2. Searching indexed knowledge base content
3. Reorganizing topic structures
4. Cancelling active processing sessions

---

## Important Notes

BLOCKING: Classify operation uses a two-step flow: first `POST /api/kb/process` returns suggestions, then `POST /api/kb/process/confirm` executes. Do NOT skip the confirm step.

CRITICAL: Only one processing session can be active at a time. Cancel any active session before starting a new one.

MANDATORY: `DASHSCOPE_API_KEY` environment variable must be set for AI-powered classification. Without it, files are classified as "uncategorized".

---

## About

The KB Manager provides AI-powered operations on the project Knowledge Base. It works with the KB landing zone (FEATURE-025-B) where users upload files, and processes them into organized topics with generated summaries.

**Key Concepts:**
- **Landing Zone** — Inbox folder where new files arrive before classification
- **Topics** — Organized folders under `topics/{topic-name}/raw/` containing classified files
- **Classification** — AI-suggested topic assignment for landing zone files
- **Session** — Temporary state tracking a classify → confirm/cancel flow
- **Summary** — AI-generated markdown overview of topic contents, versioned (v1, v2, ...)

---

## When to Use

```yaml
triggers:
  - "classify landing items"
  - "classify files"
  - "sort landing files"
  - "process topic"
  - "generate summary"
  - "search kb"
  - "search knowledge"
  - "search knowledge for"
  - "find in knowledge base"
  - "reorganize topics"
  - "reorganize knowledge base"
  - "cancel processing"

not_for:
  - "Uploading files to landing zone — use KB Landing UI (FEATURE-025-B)"
  - "Creating KB folder structure — use KBService directly (FEATURE-025-A)"
```

---

## Input Parameters

```yaml
input:
  operation: "classify | confirm | search | reorganize | cancel"
  classify:
    paths: ["landing/file1.md", "landing/file2.pdf"]  # File paths to classify
  confirm:
    session_id: "{uuid}"  # From classify response
    classifications: [{path: "landing/file.md", topic: "api-design"}]  # Confirmed mappings
  search:
    query: "{search terms}"  # Required search string
  reorganize: {}  # No parameters needed
  cancel:
    session_id: "{uuid}"  # Session to cancel
```

---

## Definition of Ready

```xml
<definition_of_ready>
  <checkpoint required="true">
    <name>KB API endpoints available</name>
    <verification>App running with /api/kb/ routes registered</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>KBService initialized</name>
    <verification>KB root folder exists with index structure</verification>
  </checkpoint>
  <checkpoint required="recommended">
    <name>DASHSCOPE_API_KEY configured</name>
    <verification>Environment variable set for AI classification</verification>
  </checkpoint>
</definition_of_ready>
```

---

## Operations

### Operation: Classify

**When:** User wants to sort landing zone files into topics

```xml
<operation name="classify">
  <action>
    1. Collect file paths from landing zone
    2. POST /api/kb/process with {"paths": [...]}
    3. Receive {"session_id": "uuid", "suggestions": [{file, topic, confidence}]}
    4. Present suggestions to user for review
    5. IF user confirms:
       POST /api/kb/process/confirm with {"session_id": "...", "classifications": [...]}
       Receive {"moved": [...], "errors": [...], "summaries_generated": [...]}
    6. IF user modifies: update topic assignments, then confirm
    7. IF user cancels: call Cancel operation
  </action>
  <constraints>
    - BLOCKING: Must confirm before files are moved
    - CRITICAL: Only one session active at a time
    - CRITICAL: Files not found on disk are reported in errors array, not silently skipped
  </constraints>
  <output>session_id, suggestions (step 2) OR moved, errors, summaries_generated (step 5)</output>
</operation>
```

### Operation: Search

**When:** User wants to find files in the knowledge base

```xml
<operation name="search">
  <action>
    1. GET /api/kb/search?q={query}
    2. Receive {"query": "...", "results": [...], "total": N}
    3. Present results to user
  </action>
  <constraints>
    - BLOCKING: Query parameter q is required (400 error if missing)
  </constraints>
  <output>query echo, results array, total count</output>
</operation>
```

### Operation: Reorganize

**When:** User wants to restructure topic organization

```xml
<operation name="reorganize">
  <action>
    1. POST /api/kb/reorganize with {}
    2. Receive {"changes": [...], "summary": "..."}
    3. Present reorganization summary to user
  </action>
  <output>changes array, summary text</output>
</operation>
```

### Operation: Cancel

**When:** User wants to stop an active processing session

```xml
<operation name="cancel">
  <action>
    1. POST /api/kb/process/cancel with {"session_id": "..."}
    2. Receive {"status": "cancelled"}
    3. Session is removed, new classify can proceed
  </action>
  <constraints>
    - BLOCKING: session_id must reference an active session (404 if not found)
  </constraints>
  <output>status: cancelled</output>
</operation>
```

---

## Output Result

```yaml
operation_output:
  success: true | false
  result:
    # Classify
    session_id: "{uuid}"
    suggestions: [{file, path, topic, suggested_topic, confidence}]
    # Confirm
    moved: [{file, from, to}]
    errors: [{file, error}]
    summaries_generated: ["{topic}"]
    # Search
    query: "{echo}"
    results: [{path, topic, ...}]
    total: N
    # Reorganize
    changes: [{description}]
    summary: "{text}"
    # Cancel
    status: "cancelled"
  errors: []
```

---

## Definition of Done

```xml
<definition_of_done>
  <checkpoint required="true">
    <name>Operation completed</name>
    <verification>API endpoint returned 200 with expected response structure</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Error cases handled</name>
    <verification>Invalid inputs return 400/404 with descriptive error messages</verification>
  </checkpoint>
  <checkpoint required="true">
    <name>Results presented to user</name>
    <verification>Agent communicated results (suggestions, search results, changes) to user</verification>
  </checkpoint>
</definition_of_done>
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `400: No paths provided` | Empty or missing paths array | Provide at least one file path |
| `400: Query parameter q is required` | Missing search query | Add ?q={query} parameter |
| `400: JSON required` | Request without Content-Type: application/json | Set correct content type |
| `404: Session not found` | Invalid or expired session_id | Start new classify operation |
| `409: A processing session is already active` | Concurrent session attempt | Cancel active session first |
| `500: Internal server error` | LLM API failure or server error | Check DASHSCOPE_API_KEY, retry |

---

## Examples

See [references/examples.md](references/examples.md) for usage examples including:
- Classify landing files with AI suggestions
- Search knowledge base
- Reorganize topics
- Cancel active session
- Error handling scenarios
