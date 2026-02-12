---
name: x-ipe-kb-manager
description: Knowledge Base Manager - classify landing items into topics, generate AI summaries, search knowledge base, reorganize topics. Triggers on "classify landing items", "process knowledge base", "search kb", "search knowledge", "reorganize topics", "process topic".
version: 1.0
---

# Knowledge Base Manager Skill

## Purpose

Manage the Knowledge Base by classifying incoming files, generating topic summaries, searching indexed content, and reorganizing topic structures. This skill orchestrates AI-powered operations on the KB landing zone.

---

## Commands

### classify

Classify landing zone files into topics using AI suggestions.

**Trigger phrases:** "classify landing items", "classify files", "sort landing files"

**Procedure:**
1. Call `POST /api/kb/process` with selected file paths
2. Review AI-suggested topic classifications
3. Confirm or modify suggestions
4. Call `POST /api/kb/process/confirm` to execute moves
5. Files are moved from `landing/` to `topics/{topic}/raw/`

**Example:**
```
User: classify landing items
Agent: Processing 3 files... AI suggests:
  - report.pdf → "project-management"
  - api-spec.md → "api-design"
  - notes.txt → "uncategorized"
Confirm these classifications? [Yes/Modify/Cancel]
```

### process

Generate AI summaries for a specified topic.

**Trigger phrases:** "process topic", "generate summary for", "summarize topic"

**Procedure:**
1. Call `POST /api/kb/process` with files from the target topic
2. Confirm classification (files already in topic)
3. Summary generated at `processed/{topic}/summary-vN.md`
4. Previous summary versions are preserved

**Example:**
```
User: process topic machine-learning
Agent: Generating summary for "machine-learning" (5 files)...
Created: processed/machine-learning/summary-v2.md
```

### search

Search the knowledge base index for matching files.

**Trigger phrases:** "search knowledge", "search kb", "find in knowledge base", "search knowledge for"

**Procedure:**
1. Call `GET /api/kb/search?q={query}`
2. Return matching files with paths and topic assignments

**Example:**
```
User: search knowledge for API design
Agent: Found 3 results:
  1. api-spec.md (topic: api-design)
  2. rest-patterns.pdf (topic: api-design)
  3. graphql-notes.md (topic: api-design)
```

### reorganize

Restructure topics and regenerate organization.

**Trigger phrases:** "reorganize knowledge base", "reorganize topics", "restructure kb"

**Procedure:**
1. Call `POST /api/kb/reorganize`
2. Review proposed changes
3. Report summary of reorganization

**Example:**
```
User: reorganize knowledge base
Agent: Reorganization complete:
  - Merged "ml" and "machine-learning" into "machine-learning"
  - Created new topic "infrastructure" from scattered files
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/kb/process` | Start classification of landing files |
| POST | `/api/kb/process/confirm` | Execute confirmed classifications |
| POST | `/api/kb/process/cancel` | Cancel active processing session |
| GET | `/api/kb/search?q={query}` | Search knowledge base |
| POST | `/api/kb/reorganize` | Trigger topic reorganization |

---

## Dependencies

- `KBService` (FEATURE-025-A) — folder structure, index, metadata
- `KBManagerService` (FEATURE-025-C) — classification, summary, search, reorganize
- `LLMService` (FEATURE-025-C) — DashScope AI text completion
- `DASHSCOPE_API_KEY` environment variable for AI features

---

## Error Handling

- If AI classification fails, files are classified as "uncategorized"
- If file move fails, error is reported and file stays in landing
- If summary generation fails, classification still completes (partial success)
- Processing is atomic per file — one failure doesn't affect others
