# Specification: FEATURE-056-B — Feature Board API

> **Feature ID:** FEATURE-056-B
> **Epic:** EPIC-056 (Feature Board Manager)
> **Version:** v1.0
> **Status:** Refined
> **Created:** 04-03-2026
> **Last Updated:** 04-03-2026

## Overview

Flask read-only API endpoints for querying features and epic summaries. Mirrors FEATURE-055-C (Task Board API) pattern: service class reads `features.json` directly, blueprint exposes GET routes. Supports flat list, single lookup, and epic summary modes.

## Dependencies

| Dependency | Type | Description |
|-----------|------|-------------|
| FEATURE-056-A | Feature | `features.json` data + CRUD scripts |
| FEATURE-055-C | Feature | Pattern reference (Task Board API) |

## Linked Mockups

N/A — API-only feature.

## DAO Design Decisions

| # | Decision | Detail |
|---|----------|--------|
| 1 | Routes | Action-based: `/api/features/list`, `/api/features/get/<id>`, `/api/features/epic-summary` |
| 2 | Implementation | Direct JSON read (same as 055-C, no subprocess) |
| 3 | Epic summary | Separate endpoint `/api/features/epic-summary` (not default grouping) |
| 4 | Pagination defaults | page=1, page_size=50 (consistent) |
| 5 | No CORS | Same-origin (YAGNI) |
| 6 | Cache-Control | no-store (same as 055-C) |

---

## Acceptance Criteria

### Group 1: List Endpoint — Basic (4 ACs)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-056B-01a | GIVEN features exist WHEN `GET /api/features/list` is called THEN 200 with `{"success": true, "data": {"features": [...], "total": N, ...}}` | API |
| AC-056B-01b | GIVEN no parameters WHEN list is called THEN defaults page=1, page_size=50 | API |
| AC-056B-01c | GIVEN features exist WHEN list is called THEN features sorted by `last_updated` descending | API |
| AC-056B-01d | GIVEN features WHEN returned THEN each has all FEATURE_SCHEMA_V1 fields | API |

### Group 2: List Endpoint — Filtering (5 ACs)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-056B-02a | GIVEN `?epic_id=EPIC-001` WHEN list is called THEN only features in that epic returned | API |
| AC-056B-02b | GIVEN `?status=Completed` WHEN list is called THEN only matching status returned | API |
| AC-056B-02c | GIVEN `?search=auth` WHEN list is called THEN case-insensitive match across feature_id, title, description, epic_id | API |
| AC-056B-02d | GIVEN multiple filters WHEN list is called THEN combined with AND logic | API |
| AC-056B-02e | GIVEN no matching features WHEN list is called THEN empty list with total=0, total_pages=1 | API |

### Group 3: List Endpoint — Pagination (3 ACs)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-056B-03a | GIVEN `?page=2&page_size=5` WHEN list is called THEN correct slice with pagination metadata | API |
| AC-056B-03b | GIVEN page beyond range WHEN list is called THEN empty features list with correct total | API |
| AC-056B-03c | GIVEN invalid page or page_size WHEN list is called THEN 400 with VALIDATION_ERROR | API |

### Group 4: Get Endpoint (3 ACs)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-056B-04a | GIVEN existing feature_id WHEN `GET /api/features/get/<id>` is called THEN 200 with feature data | API |
| AC-056B-04b | GIVEN non-existent feature_id WHEN get is called THEN 404 with NOT_FOUND | API |
| AC-056B-04c | GIVEN feature returned WHEN get is called THEN all schema fields present | API |

### Group 5: Epic Summary Endpoint (4 ACs)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-056B-05a | GIVEN features across epics WHEN `GET /api/features/epic-summary` is called THEN per-epic count returned | API |
| AC-056B-05b | GIVEN `?epic_id=EPIC-001` WHEN summary is called THEN only that epic's summary returned | API |
| AC-056B-05c | GIVEN no features WHEN summary is called THEN empty summaries list | API |
| AC-056B-05d | GIVEN all features completed WHEN summary is called THEN counts reflect correctly | API |

### Group 6: Error Handling & Blueprint (4 ACs)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-056B-06a | GIVEN internal error WHEN any endpoint is called THEN 500 with INTERNAL_ERROR | API |
| AC-056B-06b | GIVEN any response WHEN returned THEN `Cache-Control: no-store` header present | API |
| AC-056B-06c | GIVEN app startup WHEN blueprints registered THEN all 3 routes in url_map | Integration |
| AC-056B-06d | GIVEN service WHEN instantiated THEN reads JSON directly (no subprocess) | Unit |

### Group 7: Service Layer (3 ACs)

| AC ID | Criterion (Given/When/Then) | Test Type |
|-------|---------------------------|-----------|
| AC-056B-07a | GIVEN features_dir missing WHEN list called THEN empty result with total_pages=1 | Unit |
| AC-056B-07b | GIVEN malformed features.json WHEN list called THEN treated as empty | Unit |
| AC-056B-07c | GIVEN valid features.json WHEN get called THEN linear scan finds feature | Unit |

---

## Summary

| Metric | Value |
|--------|-------|
| Total ACs | 26 |
| Groups | 7 |
| Endpoints | 3 (list, get, epic-summary) |
| Blueprint | feature_board_bp |
