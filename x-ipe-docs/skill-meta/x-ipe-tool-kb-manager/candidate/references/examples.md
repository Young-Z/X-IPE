# Examples

## Example 1: Classify Landing Files

**Scenario:** User has 3 files in the landing zone and wants to classify them.

```
User: classify landing items

Agent:
1. Calls POST /api/kb/process with {"paths": ["landing/api-spec.md", "landing/ml-paper.pdf", "landing/notes.txt"]}
2. Receives:
   {
     "session_id": "a1b2c3d4-...",
     "suggestions": [
       {"file": "api-spec.md", "path": "landing/api-spec.md", "topic": "api-design", "confidence": 0.85},
       {"file": "ml-paper.pdf", "path": "landing/ml-paper.pdf", "topic": "machine-learning", "confidence": 0.92},
       {"file": "notes.txt", "path": "landing/notes.txt", "topic": "uncategorized", "confidence": 0.0}
     ]
   }
3. Presents: "AI suggests: api-spec.md → api-design (85%), ml-paper.pdf → machine-learning (92%), notes.txt → uncategorized. Confirm?"
4. User confirms
5. Calls POST /api/kb/process/confirm with session_id and classifications
6. Reports: "Moved 3 files. Summary generated for api-design and machine-learning."
```

## Example 2: Search Knowledge Base

**Scenario:** User searches for API-related content.

```
User: search knowledge for API design patterns

Agent:
1. Calls GET /api/kb/search?q=API%20design%20patterns
2. Receives:
   {
     "query": "API design patterns",
     "results": [
       {"path": "topics/api-design/raw/api-spec.md", "topic": "api-design"},
       {"path": "topics/api-design/raw/rest-patterns.pdf", "topic": "api-design"}
     ],
     "total": 2
   }
3. Reports: "Found 2 results in topic 'api-design': api-spec.md, rest-patterns.pdf"
```

## Example 3: Cancel Active Session

**Scenario:** User started classification but wants to cancel.

```
User: cancel processing

Agent:
1. Calls POST /api/kb/process/cancel with {"session_id": "a1b2c3d4-..."}
2. Receives: {"status": "cancelled"}
3. Reports: "Processing cancelled. Files remain in landing zone."
```

## Example 4: Error — Concurrent Session

**Scenario:** User tries to classify while another session is active.

```
User: classify landing items

Agent:
1. Calls POST /api/kb/process with {"paths": ["landing/new-file.md"]}
2. Receives 409: {"error": "A processing session is already active"}
3. Reports: "A processing session is already active. Cancel it first or wait for it to complete."
4. Asks: "Would you like to cancel the active session?"
```

## Example 5: Reorganize Topics

**Scenario:** User wants to restructure topic organization.

```
User: reorganize knowledge base

Agent:
1. Calls POST /api/kb/reorganize with {}
2. Receives: {"changes": [], "summary": "No reorganization needed"}
3. Reports: "Knowledge base is already well-organized. No changes needed."
```
