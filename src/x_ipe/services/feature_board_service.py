"""Feature Board Service — read-only query layer over features.json.

Provides list_features (filtered, paginated), get_feature (by ID),
and epic_summary (per-epic status counts).

Location: src/x_ipe/services/feature_board_service.py
Consumer: feature_board_routes.py (FEATURE-056-B)
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SEARCH_FIELDS = ("feature_id", "title", "description", "epic_id")


class FeatureBoardService:
    """Read-only service for querying feature board data."""

    def __init__(self, project_root: str) -> None:
        self.features_dir = Path(project_root) / "x-ipe-docs" / "planning" / "features"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_features(
        self,
        epic_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """Return filtered, sorted, paginated feature list."""
        features = self._read_features()
        filtered = [f for f in features if self._matches_filters(f, epic_id, status, search)]
        filtered.sort(key=lambda f: f.get("last_updated", ""), reverse=True)
        return {"success": True, "data": self._paginate(filtered, page, page_size)}

    def get_feature(self, feature_id: str) -> dict[str, Any]:
        """Look up a single feature by ID via linear scan."""
        features = self._read_features()
        for f in features:
            if f.get("feature_id") == feature_id:
                return {"success": True, "data": {"feature": f}}
        return {
            "success": False,
            "error": "NOT_FOUND",
            "message": f"Feature '{feature_id}' not found",
        }

    def epic_summary(
        self,
        epic_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """Return per-epic status count summaries, optionally filtered."""
        features = self._read_features()
        # Apply status/search filters so summaries reflect the active filter
        filtered = [f for f in features if self._matches_filters(f, epic_id, status, search)]

        groups: dict[str, list[dict]] = defaultdict(list)
        for f in filtered:
            groups[f.get("epic_id", "UNKNOWN")].append(f)

        summaries = []
        for eid, feats in sorted(groups.items()):
            summary: dict[str, Any] = {"epic_id": eid, "total": len(feats)}
            counts: dict[str, int] = defaultdict(int)
            for f in feats:
                counts[f.get("status", "Unknown")] += 1
            summary.update(counts)
            summaries.append(summary)

        return {"success": True, "data": {"summaries": summaries}}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read_features(self) -> list[dict]:
        """Load all features from features.json. Returns [] if missing/malformed."""
        features_path = self.features_dir / "features.json"
        data = self._read_json(features_path)
        if data is None:
            return []
        return data.get("features", [])

    @staticmethod
    def _matches_filters(
        feature: dict,
        epic_id: str | None,
        status: str | None,
        search: str | None,
    ) -> bool:
        """Return True if feature passes all filters (AND logic)."""
        if epic_id and feature.get("epic_id") != epic_id:
            return False
        if status and feature.get("status") != status:
            return False
        if search:
            searchable = " ".join(
                str(feature.get(f, "")) for f in _SEARCH_FIELDS
            ).lower()
            if search.lower() not in searchable:
                return False
        return True

    @staticmethod
    def _paginate(features: list[dict], page: int, page_size: int) -> dict:
        """Slice feature list and return with pagination metadata."""
        total = len(features)
        total_pages = max(1, (total + page_size - 1) // page_size)
        start = (page - 1) * page_size
        return {
            "features": features[start : start + page_size],
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
            },
        }

    @staticmethod
    def _read_json(path: Path) -> Any | None:
        """Read and parse a JSON file, returning None on any error."""
        try:
            with open(path) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError, TypeError):
            return None
