"""
Tests for FEATURE-024: Project Quality Evaluation UI

TDD test suite for the quality evaluation API endpoints and frontend integration.
Tests cover status endpoint, content retrieval, config structure, and placeholder resolution.

Run with: pytest tests/test_quality_evaluation.py -v
"""
import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
import os


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_project(temp_project_dir):
    """Return temp project dir as Path object."""
    return Path(temp_project_dir)


@pytest.fixture
def app(temp_project_dir):
    """Create Flask test app with temp project."""
    from src.app import create_app
    test_app = create_app({
        'TESTING': True,
        'PROJECT_ROOT': temp_project_dir,
        'SETTINGS_DB_PATH': os.path.join(temp_project_dir, 'test_settings.db')
    })
    return test_app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def quality_eval_folder(temp_project):
    """Create quality evaluation folder with sample files."""
    eval_folder = temp_project / "x-ipe-docs" / "quality-evaluation"
    eval_folder.mkdir(parents=True, exist_ok=True)
    return eval_folder


@pytest.fixture
def sample_evaluation_md():
    """Sample evaluation markdown content."""
    return """# Project Quality Evaluation

## Executive Summary
- **Overall Quality Score:** 85/100
- **Requirements Coverage:** 92%
- **Test Coverage:** 78%

## Gap Analysis

| Category | Status | Score |
|----------|--------|-------|
| Requirements | ✅ Good | 92% |
| Features | ⚠️ Needs Work | 75% |
| Tests | ⚠️ Needs Work | 78% |

## Recommendations

1. Add missing unit tests for `AuthService`
2. Update feature specifications for FEATURE-015
"""


@pytest.fixture
def evaluation_files(quality_eval_folder, sample_evaluation_md):
    """Create multiple evaluation version files."""
    # Latest version (no suffix)
    latest = quality_eval_folder / "project-quality-evaluation.md"
    latest.write_text(sample_evaluation_md)
    
    # Historical versions
    for v in [4, 3, 2, 1]:
        vfile = quality_eval_folder / f"project-quality-evaluation-v{v}.md"
        vfile.write_text(f"# Historical Evaluation v{v}\n\nPrevious evaluation content.")
    
    return quality_eval_folder


@pytest.fixture
def copilot_prompt_v2_config(temp_project):
    """Create v2.0 copilot-prompt.json with evaluation section."""
    config_folder = temp_project / "x-ipe-docs" / "config"
    config_folder.mkdir(parents=True, exist_ok=True)
    
    config = {
        "version": "2.0",
        "ideation": {
            "prompts": [
                {"id": "brainstorm", "label": "Brainstorm", "icon": "bi-lightbulb", "command": "brainstorm"}
            ]
        },
        "evaluation": {
            "evaluate": {
                "label": "Evaluate Project Quality",
                "icon": "bi-clipboard-check",
                "command": "Evaluate project quality and generate report to <evaluation-file>"
            },
            "refactoring": [
                {"id": "refactor-all", "label": "Refactor All", "icon": "bi-arrow-repeat", "command": "Refactor all with reference to code"},
                {"id": "refactor-requirements", "label": "Refactor Requirements", "icon": "bi-file-text", "command": "Refactor requirements with reference to code"},
                {"id": "refactor-tests", "label": "Refactor Tests", "icon": "bi-bug", "command": "Refactor tests with reference to code"}
            ]
        },
        "placeholder": {
            "current-idea-file": "x-ipe-docs/ideas/current-idea.md",
            "evaluation-file": "x-ipe-docs/quality-evaluation/project-quality-evaluation.md"
        }
    }
    
    config_file = config_folder / "copilot-prompt.json"
    config_file.write_text(json.dumps(config, indent=2))
    
    return config_file


# =============================================================================
# UNIT TESTS: Status Endpoint
# =============================================================================

class TestQualityEvaluationStatus:
    """Unit tests for GET /api/quality-evaluation/status endpoint."""
    
    def test_status_returns_exists_false_when_no_folder(self, client, temp_project):
        """AC-2.1: Returns exists=false when quality-evaluation folder doesn't exist."""
        response = client.get('/api/quality-evaluation/status')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['exists'] is False
        assert data['folder_path'] == 'x-ipe-docs/quality-evaluation'
        assert data['versions'] == []
    
    def test_status_returns_exists_false_when_folder_empty(self, client, quality_eval_folder):
        """AC-2.1: Returns exists=false when folder exists but has no evaluation files."""
        response = client.get('/api/quality-evaluation/status')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['exists'] is False
        assert data['versions'] == []
    
    def test_status_returns_exists_true_with_evaluation_file(self, client, evaluation_files):
        """AC-3.1: Returns exists=true when evaluation file exists."""
        response = client.get('/api/quality-evaluation/status')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['exists'] is True
        assert len(data['versions']) > 0
    
    def test_status_returns_up_to_5_versions(self, client, evaluation_files):
        """AC-7.2: Timeline shows up to 5 most recent versions."""
        response = client.get('/api/quality-evaluation/status')
        data = response.get_json()
        
        assert len(data['versions']) <= 5
    
    def test_status_versions_ordered_newest_first(self, client, evaluation_files):
        """AC-7.3: Most recent version appears first in list."""
        response = client.get('/api/quality-evaluation/status')
        data = response.get_json()
        
        versions = data['versions']
        assert len(versions) >= 2
        
        # First version should be the current (latest)
        assert versions[0]['is_current'] is True
        assert versions[0]['version'] == 'v5' or versions[0]['filename'] == 'project-quality-evaluation.md'
    
    def test_status_version_has_required_fields(self, client, evaluation_files):
        """AC-7.4, AC-7.5: Each version entry has version number and date."""
        response = client.get('/api/quality-evaluation/status')
        data = response.get_json()
        
        version = data['versions'][0]
        
        assert 'version' in version
        assert 'filename' in version
        assert 'date' in version
        assert 'is_current' in version
    
    def test_status_marks_current_version(self, client, evaluation_files):
        """AC-7.6: Active version has is_current=true marker."""
        response = client.get('/api/quality-evaluation/status')
        data = response.get_json()
        
        current_versions = [v for v in data['versions'] if v['is_current']]
        assert len(current_versions) == 1


# =============================================================================
# UNIT TESTS: Content Endpoint
# =============================================================================

class TestQualityEvaluationContent:
    """Unit tests for GET /api/quality-evaluation/content endpoint."""
    
    def test_content_returns_404_when_no_file(self, client, temp_project):
        """Error handling: Returns 404 when no evaluation file exists."""
        response = client.get('/api/quality-evaluation/content')
        
        assert response.status_code == 404
    
    def test_content_returns_latest_by_default(self, client, evaluation_files, sample_evaluation_md):
        """AC-3.3: Returns latest evaluation content when no version specified."""
        response = client.get('/api/quality-evaluation/content')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'content' in data
        assert 'Executive Summary' in data['content']
        assert data['filename'] == 'project-quality-evaluation.md'
    
    def test_content_returns_specific_version(self, client, evaluation_files):
        """AC-7.7: Clicking a tab loads that version's content."""
        response = client.get('/api/quality-evaluation/content?version=v4')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'Historical Evaluation v4' in data['content']
        assert 'v4' in data['filename']
    
    def test_content_returns_404_for_invalid_version(self, client, evaluation_files):
        """Error handling: Returns 404 for non-existent version."""
        response = client.get('/api/quality-evaluation/content?version=v99')
        
        assert response.status_code == 404
    
    def test_content_includes_metadata(self, client, evaluation_files):
        """Content response includes version and path metadata."""
        response = client.get('/api/quality-evaluation/content')
        data = response.get_json()
        
        assert 'version' in data
        assert 'filename' in data
        assert 'path' in data
    
    def test_content_path_matches_storage_location(self, client, evaluation_files):
        """AC-8.1: Files stored in x-ipe-docs/quality-evaluation/ folder."""
        response = client.get('/api/quality-evaluation/content')
        data = response.get_json()
        
        assert 'x-ipe-docs/quality-evaluation' in data['path']


# =============================================================================
# UNIT TESTS: Config API (copilot-prompt.json v2.0)
# =============================================================================

class TestCopilotPromptConfigV2:
    """Unit tests for v2.0 config structure with evaluation section."""
    
    def test_config_returns_v2_structure(self, client, copilot_prompt_v2_config):
        """AC-9.1: Config has top-level ideation and evaluation sections."""
        response = client.get('/api/config/copilot-prompt')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'version' in data
        assert data['version'] == '2.0'
        assert 'ideation' in data
        assert 'evaluation' in data
    
    def test_config_ideation_backward_compatible(self, client, copilot_prompt_v2_config):
        """AC-9.2: Existing ideation prompts continue working."""
        response = client.get('/api/config/copilot-prompt')
        data = response.get_json()
        
        assert 'prompts' in data['ideation']
        prompts = data['ideation']['prompts']
        assert len(prompts) > 0
        assert prompts[0]['id'] == 'brainstorm'
    
    def test_config_evaluation_has_evaluate_command(self, client, copilot_prompt_v2_config):
        """AC-9.3: evaluation.evaluate has label, icon, and command."""
        response = client.get('/api/config/copilot-prompt')
        data = response.get_json()
        
        evaluate = data['evaluation']['evaluate']
        
        assert 'label' in evaluate
        assert 'icon' in evaluate
        assert 'command' in evaluate
    
    def test_config_evaluation_has_refactoring_array(self, client, copilot_prompt_v2_config):
        """AC-9.4: evaluation.refactoring is array of prompt objects."""
        response = client.get('/api/config/copilot-prompt')
        data = response.get_json()
        
        refactoring = data['evaluation']['refactoring']
        
        assert isinstance(refactoring, list)
        assert len(refactoring) >= 1
    
    def test_config_refactoring_prompt_structure(self, client, copilot_prompt_v2_config):
        """AC-9.5: Each refactoring prompt has id, label, icon, and command."""
        response = client.get('/api/config/copilot-prompt')
        data = response.get_json()
        
        prompt = data['evaluation']['refactoring'][0]
        
        assert 'id' in prompt
        assert 'label' in prompt
        assert 'icon' in prompt
        assert 'command' in prompt
    
    def test_config_has_evaluation_placeholder(self, client, copilot_prompt_v2_config):
        """AC-9.6: placeholder.evaluation-file is defined."""
        response = client.get('/api/config/copilot-prompt')
        data = response.get_json()
        
        assert 'placeholder' in data
        assert 'evaluation-file' in data['placeholder']


# =============================================================================
# INTEGRATION TESTS: Placeholder Resolution
# =============================================================================

class TestPlaceholderResolution:
    """Integration tests for placeholder resolution in commands."""
    
    def test_placeholder_evaluation_file_defined(self, client, copilot_prompt_v2_config):
        """AC-10.1: <evaluation-file> placeholder is defined for runtime substitution."""
        response = client.get('/api/config/copilot-prompt')
        data = response.get_json()
        
        placeholder = data['placeholder']['evaluation-file']
        
        assert placeholder == 'x-ipe-docs/quality-evaluation/project-quality-evaluation.md'
    
    def test_evaluate_command_contains_placeholder(self, client, copilot_prompt_v2_config):
        """AC-10.2: Evaluate command contains <evaluation-file> placeholder."""
        response = client.get('/api/config/copilot-prompt')
        data = response.get_json()
        
        command = data['evaluation']['evaluate']['command']
        
        assert '<evaluation-file>' in command


# =============================================================================
# INTEGRATION TESTS: View State Management
# =============================================================================

class TestQualityEvaluationViewState:
    """Integration tests for view state and content switching."""
    
    def test_empty_state_to_content_transition(self, client, quality_eval_folder, sample_evaluation_md):
        """View transitions from empty state to content when file is created."""
        # Initial state: no file
        response = client.get('/api/quality-evaluation/status')
        assert response.get_json()['exists'] is False
        
        # Create evaluation file
        eval_file = quality_eval_folder / "project-quality-evaluation.md"
        eval_file.write_text(sample_evaluation_md)
        
        # After creation: file exists
        response = client.get('/api/quality-evaluation/status')
        assert response.get_json()['exists'] is True
    
    def test_version_switching(self, client, evaluation_files):
        """AC-7.7: Switching versions loads correct content."""
        # Load v4
        response = client.get('/api/quality-evaluation/content?version=v4')
        assert 'v4' in response.get_json()['content']
        
        # Switch to v3
        response = client.get('/api/quality-evaluation/content?version=v3')
        assert 'v3' in response.get_json()['content']
        
        # Switch to latest
        response = client.get('/api/quality-evaluation/content')
        assert 'Executive Summary' in response.get_json()['content']


# =============================================================================
# UNIT TESTS: File Naming Convention
# =============================================================================

class TestFileNamingConvention:
    """Unit tests for file naming and storage conventions."""
    
    def test_latest_file_naming(self, client, evaluation_files):
        """AC-8.2: Latest evaluation named project-quality-evaluation.md."""
        response = client.get('/api/quality-evaluation/status')
        data = response.get_json()
        
        current = [v for v in data['versions'] if v['is_current']][0]
        
        assert current['filename'] == 'project-quality-evaluation.md'
    
    def test_historical_file_naming(self, client, evaluation_files):
        """AC-8.3: Historical versions named project-quality-evaluation-vN.md."""
        response = client.get('/api/quality-evaluation/status')
        data = response.get_json()
        
        historical = [v for v in data['versions'] if not v['is_current']]
        
        for version in historical:
            assert version['filename'].startswith('project-quality-evaluation-v')
            assert version['filename'].endswith('.md')


# =============================================================================
# UNIT TESTS: Error Handling
# =============================================================================

class TestQualityEvaluationErrors:
    """Unit tests for error handling scenarios."""
    
    def test_malformed_markdown_handled(self, client, quality_eval_folder):
        """Malformed markdown is returned as-is (frontend handles rendering)."""
        eval_file = quality_eval_folder / "project-quality-evaluation.md"
        eval_file.write_text("# Broken\n\n| col | missing end |")
        
        response = client.get('/api/quality-evaluation/content')
        
        assert response.status_code == 200
        assert 'Broken' in response.get_json()['content']
    
    def test_empty_file_handled(self, client, quality_eval_folder):
        """Empty evaluation file handled gracefully."""
        eval_file = quality_eval_folder / "project-quality-evaluation.md"
        eval_file.write_text("")
        
        response = client.get('/api/quality-evaluation/content')
        
        assert response.status_code == 200
        assert response.get_json()['content'] == ""


# =============================================================================
# TRACING TESTS (FEATURE-023-D)
# =============================================================================

class TestQualityEvaluationTracing:
    """Tests for tracing decorator presence on quality evaluation routes."""
    
    def test_routes_have_tracing_decorators(self):
        """Verify quality evaluation routes have @x_ipe_tracing decorators."""
        import inspect
        try:
            from x_ipe.routes import quality_evaluation_routes
            
            # Check if module has tracing imports and decorators
            source = inspect.getsource(quality_evaluation_routes)
            assert "@x_ipe_tracing" in source, "Missing @x_ipe_tracing decorators"
            assert "from x_ipe.tracing import x_ipe_tracing" in source, "Missing tracing import"
        except ImportError:
            pytest.skip("Module not implemented yet - TDD phase")


# =============================================================================
# TEST COVERAGE SUMMARY
# =============================================================================
"""
Test Coverage Summary for FEATURE-024:

| Component | Unit Tests | Integration | Total |
|-----------|------------|-------------|-------|
| Status API | 7 | - | 7 |
| Content API | 6 | - | 6 |
| Config API (v2.0) | 6 | - | 6 |
| Placeholder | - | 2 | 2 |
| View State | - | 2 | 2 |
| File Naming | 2 | - | 2 |
| Error Handling | 2 | - | 2 |
| Tracing | 1 | - | 1 |
| **TOTAL** | **24** | **4** | **28** |

Baseline Status: 28 tests failing, 0 passing (TDD ready)
"""
