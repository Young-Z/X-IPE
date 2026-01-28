"""
Routes Package

Flask Blueprints for X-IPE application routes.
"""

from .main_routes import main_bp
from .settings_routes import settings_bp
from .project_routes import project_bp
from .ideas_routes import ideas_bp
from .tools_routes import tools_bp
from .proxy_routes import proxy_bp

__all__ = [
    'main_bp',
    'settings_bp',
    'project_bp',
    'ideas_bp',
    'tools_bp',
    'proxy_bp',
]
