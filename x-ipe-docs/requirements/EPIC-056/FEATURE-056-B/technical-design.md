# Technical Design: FEATURE-056-B — Feature Board API

> **Feature ID:** FEATURE-056-B
> **Epic:** EPIC-056 (Feature Board Manager)
> **Version:** v1.0
> **Created:** 04-03-2026
> **Last Updated:** 04-03-2026

## Design Change Log

| Date | Change | Reason |
|------|--------|--------|
| 04-03-2026 | Initial design | FEATURE-056-B created |

---

# Part 1 — Design Summary

## Overview

Flask service + blueprint for read-only feature board API. Mirrors FEATURE-055-C (Task Board API) architecture: `FeatureBoardService` reads `features.json` directly, blueprint validates params and delegates to service.

## Architecture

```
src/x_ipe/services/feature_board_service.py   # FeatureBoardService
src/x_ipe/routes/feature_board_routes.py       # Blueprint: feature_board_bp
```

## Class Diagram

```
┌───────────────────────────────────────┐
│       FeatureBoardService             │
├───────────────────────────────────────┤
│ - features_dir: Path                  │
├───────────────────────────────────────┤
│ + list_features(epic_id, status,      │
│     search, page, page_size) → dict   │
│ + get_feature(feature_id) → dict      │
│ + epic_summary(epic_id) → dict        │
│ - _read_features() → list[dict]       │
│ - _matches_filters(feat, ...) → bool  │
│ - _paginate(items, page, ps) → dict   │
│ @staticmethod _read_json(path) → dict │
└───────────────────────────────────────┘
         ▲
         │ uses
┌───────────────────────────────────────┐
│   feature_board_routes.py             │
├───────────────────────────────────────┤
│ + list_features()  GET /api/features/list        │
│ + get_feature(id)  GET /api/features/get/<id>    │
│ + epic_summary()   GET /api/features/epic-summary│
│ - _get_service() → FeatureBoardService           │
│ - _parse_int(val, default, name) → int           │
│ + handle_error(e)  @errorhandler                 │
│ + set_no_cache(r)  @after_request                │
└───────────────────────────────────────┘
```

## AC Coverage

All 26 ACs mapped to FeatureBoardService + feature_board_routes functions. Same pattern as 055-C.

---

# Part 2 — Implementation Guide

## FeatureBoardService

| Function | Purpose |
|----------|---------|
| `__init__(project_root)` | Set `features_dir = Path(project_root) / "x-ipe-docs/planning/features"` |
| `list_features(epic_id, status, search, page, page_size)` | Read → filter → sort → paginate |
| `get_feature(feature_id)` | Linear scan features.json for feature_id |
| `epic_summary(epic_id)` | Group by epic_id, count statuses per epic |
| `_read_features()` | Load features.json, return features array or [] |
| `_matches_filters(feat, epic_id, status, search)` | AND-combined filter |
| `_paginate(items, page, page_size)` | Slice + metadata |
| `_read_json(path)` | Static helper, returns None on error |

## feature_board_routes.py

| Route | Method | Parameters | Response |
|-------|--------|-----------|----------|
| `/api/features/list` | GET | `epic_id`, `status`, `search`, `page`, `page_size` | 200 list, 400 validation |
| `/api/features/get/<feature_id>` | GET | path param | 200 feature, 404 not found |
| `/api/features/epic-summary` | GET | `epic_id` (optional) | 200 summaries |
