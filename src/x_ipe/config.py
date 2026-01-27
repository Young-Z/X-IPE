"""
Configuration for the Document Viewer application.
"""
import os
from pathlib import Path


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Project root to monitor - defaults to project root (3 levels up from src/x_ipe/config.py)
    PROJECT_ROOT = os.environ.get('X_IPE_PROJECT_ROOT', os.environ.get('PROJECT_ROOT', str(Path(__file__).parent.parent.parent)))
    
    # Section mappings
    SECTIONS = [
        {
            'id': 'planning',
            'label': 'Project Plan',
            'path': 'x-ipe-docs/planning',
            'icon': 'bi-kanban'
        },
        {
            'id': 'requirements',
            'label': 'Requirements',
            'path': 'x-ipe-docs/requirements',
            'icon': 'bi-file-text'
        },
        {
            'id': 'code',
            'label': 'Code',
            'path': 'src',
            'icon': 'bi-code-slash'
        }
    ]
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        'documents': ['.md', '.txt', '.json', '.yaml', '.yml'],
        'code': ['.py', '.js', '.ts', '.html', '.css', '.jsx', '.tsx']
    }
    
    # File watcher debounce time (seconds)
    FILE_WATCHER_DEBOUNCE = 0.1


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
