"""
Shared configuration utilities for layered .x-ipe.yaml loading.

Provides package-default loading and deep-merge so that both
XIPEConfig (CLI path) and ConfigService (Flask path) share the
same fallback logic.
"""
import yaml
from pathlib import Path
from typing import Any


_DEFAULTS_PATH = Path(__file__).parent.parent / 'defaults' / '.x-ipe.yaml'


def load_package_defaults() -> dict:
    """Load the package-bundled default .x-ipe.yaml as a raw dict.

    Returns an empty dict if the file is missing or unparseable.
    """
    if not _DEFAULTS_PATH.exists():
        return {}
    try:
        with open(_DEFAULTS_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except (yaml.YAMLError, IOError):
        return {}


def get_package_defaults_path() -> Path:
    """Return the path to the package-bundled default config."""
    return _DEFAULTS_PATH


def deep_merge(base: dict, override: dict) -> dict:
    """Deep-merge *override* into *base*, returning a new dict.

    - Nested dicts are merged recursively.
    - All other types (scalars, lists) in *override* replace *base*.
    - Neither input dict is mutated.
    """
    merged: dict[str, Any] = dict(base)
    for key, value in override.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged
