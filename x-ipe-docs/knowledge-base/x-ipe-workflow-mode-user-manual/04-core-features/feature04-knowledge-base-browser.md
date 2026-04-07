---
title: "Knowledge Base Browser"
section: "04-core-features"
extraction_round: 2
source_files:
  - src/x_ipe/static/js/features/kb-browse-modal.js
  - src/x_ipe/static/js/init.js
---

# Knowledge Base Browser

## Overview

The Knowledge Base (KB) Browser — called the "Knowledge Atelier" — is a full-featured modal for browsing, searching, and managing KB articles. It provides grid/list views, filtering, and article detail viewing.

## How to Access

1. Click the **📚 KB** button in the top header bar (labeled "Knowledge Base")
2. The Knowledge Atelier modal opens

![KB Button](screenshots/kb-button-clicked.png)

## Modal Scenes

The KB Browser has a multi-scene interface:

### 1. Browse Scene (Default)
- **Grid view:** Articles displayed as cards with folder color coding
- **List view:** Table with columns: name, modified date, tags
- **Sort options:** By name or by modified date
- **Sidebar:** Folder tree navigation for quick directory access

### 2. Article Detail Scene
- Click any article → shows full content with rendered markdown
- **Edit button** → opens KB Article Editor modal
- **Tags display:** lifecycle tags (draft, review, published) + domain tags
- **Metadata:** file path, last modified, size

### 3. Intake Scene
- Placeholder for future KB submission workflow
- Shows count of pending intake items

## Filtering & Search

| Filter | Description |
|--------|-------------|
| **Search query** | Full-text search across article names and content |
| **Lifecycle filter** | All / Draft / Review / Published |
| **Domain filter** | Filter by category/domain tags |
| **Untagged toggle** | Show only articles without tags |

## Data Sources

| API Endpoint | Purpose |
|-------------|---------|
| `GET /api/kb/tree` | Folder structure |
| `GET /api/kb/files?recursive=true` | All KB files |
| `GET /api/kb/config` | Tag configuration |
| `GET /api/kb/intake` | Intake item count |

## Error Handling

- Load failure → error message with retry button
- Graceful degradation if endpoints unavailable
- Empty state → "No articles found" placeholder

## UI Elements

| Element | Selector | Purpose |
|---------|----------|---------|
| Trigger button | `#btn-kb-browse` | Opens the modal |
| Grid view toggle | View switcher | Grid/list layout |
| Sidebar | Folder tree | Directory navigation |
