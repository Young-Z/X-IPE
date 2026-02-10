"""
X-IPE: Intelligent Project Environment

A tool for managing project documentation, ideas, requirements,
and AI-assisted development workflows.
"""

try:
    from importlib.metadata import version as _pkg_version
    __version__ = _pkg_version("x-ipe")
except Exception:
    __version__ = "0.0.0"
__author__ = "X-IPE Team"
