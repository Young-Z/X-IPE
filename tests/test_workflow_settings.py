"""
Acceptance tests for EPIC-044: Interaction Mode Process Preference

Covers:
- FEATURE-044-E: global.process_preference in workflow state & PATCH settings API
- FEATURE-044-F: Settings validation (interaction_mode enum)
- Integration: initial state includes global section, update persists
"""

import json
import os
import tempfile
import shutil

import pytest
import re
from pathlib import Path
from tests.test_architecture_draw_skill import frontmatter, linked_resource, section, yaml_contract

ROOT = Path(__file__).resolve().parents[1]
MODE_SPEC = ROOT / 'x-ipe-docs/requirements/EPIC-044/FEATURE-044-E/specification.md'
LIFECYCLE_TARGET = '.github/skills/x-ipe-workflow-task-execution/references/lifecycle.md'
HYBRID = 'dao-represent-human-to-interact-for-questions-in-skill'


def specification_modes():
    content = MODE_SPEC.read_text()
    acceptance = content.split('**AC-044-E.4:**', 1)[1].split('**AC-044-E.5:**', 1)[0]
    modes = dict(re.findall(r'^- `"([^"]+)"` — (.+)$', acceptance, re.M))
    assert len(modes) == 3 and 'inner-skill questions only' in modes[HYBRID]
    return modes


def interaction_rows(content):
    """Parse only the named three-column enum table, rejecting duplicate rows."""
    table = section(content, 'Interaction modes')
    assert '| interaction_mode | Actual within-skill decision | Completion / next-task boundary |' in table
    rows = {}
    for line in table.splitlines():
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if cells[0] in specification_modes():
            assert len(cells) == 3 and cells[0] not in rows, 'Malformed/duplicate mode row'
            rows[cells[0]] = tuple(cells[1:])
    assert set(rows) == set(specification_modes()), 'Missing named interaction mode'
    return rows


def validate_mode_policy(rows):
    expected = {
        'interact-with-human': ('Ask human and wait', 'Human review and route confirmation'),
        'dao-represent-human-to-interact': ('DAO bounded answer/guidance', 'DAO selects authorized route; no invented scope'),
        HYBRID: ('DAO bounded answer/guidance', 'Human review and route confirmation'),
    }
    assert rows == expected, 'Interaction policy conflicts with current specification/authority'


def current_candidate_policy():
    """Read-only correction evidence; never substitute candidate for installed bytes."""
    path = ROOT / 'x-ipe-docs/skill-meta/x-ipe-workflow-task-execution/candidate/references/lifecycle.md'
    assert path.is_file()
    content = path.read_text()
    assert 'FEATURE-044-E specification AC-044-E.4' in content
    return interaction_rows(content)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def temp_project_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def workflow_service(temp_project_dir):
    from x_ipe.services.workflow_manager_service import WorkflowManagerService
    return WorkflowManagerService(temp_project_dir)


@pytest.fixture
def sample_workflow(workflow_service):
    result = workflow_service.create_workflow("test-044")
    assert result["success"]
    return "test-044"


@pytest.fixture
def app(temp_project_dir):
    from x_ipe.app import create_app
    app = create_app({"TESTING": True, "PROJECT_ROOT": temp_project_dir})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# ==============================================================================
# Service-level tests: initial state includes global.process_preference
# ==============================================================================

class TestInitialStateProcessPreference:
    """FEATURE-044-E: New workflows include global.process_preference."""

    def test_initial_state_has_global_section(self, workflow_service, sample_workflow):
        state = workflow_service.get_workflow(sample_workflow)
        assert "global" in state

    def test_initial_state_has_process_preference(self, workflow_service, sample_workflow):
        state = workflow_service.get_workflow(sample_workflow)
        pp = state["global"]["process_preference"]
        assert pp["interaction_mode"] == "interact-with-human"

    def test_initial_state_default_is_interact_with_human(self, workflow_service, sample_workflow):
        state = workflow_service.get_workflow(sample_workflow)
        assert state["global"]["process_preference"]["interaction_mode"] == "interact-with-human"


# ==============================================================================
# Service-level tests: update_settings
# ==============================================================================

class TestUpdateSettings:
    """FEATURE-044-E: update_settings service method."""

    def test_update_to_dao_represent(self, workflow_service, sample_workflow):
        result = workflow_service.update_settings(
            sample_workflow, {"process_preference": {"interaction_mode": "dao-represent-human-to-interact"}})
        assert result["success"]
        assert result["data"]["process_preference"]["interaction_mode"] == "dao-represent-human-to-interact"

    def test_update_to_dao_inner_skill_only(self, workflow_service, sample_workflow):
        result = workflow_service.update_settings(
            sample_workflow, {"process_preference": {"interaction_mode": "dao-represent-human-to-interact-for-questions-in-skill"}})
        assert result["success"]
        assert result["data"]["process_preference"]["interaction_mode"] == "dao-represent-human-to-interact-for-questions-in-skill"

    def test_update_to_interact_with_human(self, workflow_service, sample_workflow):
        workflow_service.update_settings(
            sample_workflow, {"process_preference": {"interaction_mode": "dao-represent-human-to-interact"}})
        result = workflow_service.update_settings(
            sample_workflow, {"process_preference": {"interaction_mode": "interact-with-human"}})
        assert result["success"]
        assert result["data"]["process_preference"]["interaction_mode"] == "interact-with-human"

    def test_update_persists_to_disk(self, workflow_service, sample_workflow):
        workflow_service.update_settings(
            sample_workflow, {"process_preference": {"interaction_mode": "dao-represent-human-to-interact"}})
        state = workflow_service.get_workflow(sample_workflow)
        assert state["global"]["process_preference"]["interaction_mode"] == "dao-represent-human-to-interact"

    def test_invalid_mode_rejected(self, workflow_service, sample_workflow):
        result = workflow_service.update_settings(
            sample_workflow, {"process_preference": {"interaction_mode": "turbo"}})
        assert not result["success"]
        assert result["error"] == "INVALID_VALUE"

    def test_update_nonexistent_workflow(self, workflow_service):
        result = workflow_service.update_settings(
            "nonexistent", {"process_preference": {"interaction_mode": "dao-represent-human-to-interact"}})
        assert not result["success"]
        assert result["error"] == "NOT_FOUND"

    def test_update_updates_last_activity(self, workflow_service, sample_workflow):
        state_before = workflow_service.get_workflow(sample_workflow)
        workflow_service.update_settings(
            sample_workflow, {"process_preference": {"interaction_mode": "dao-represent-human-to-interact"}})
        state_after = workflow_service.get_workflow(sample_workflow)
        assert state_after["last_activity"] >= state_before["last_activity"]


# ==============================================================================
# API-level tests: PATCH /api/workflow/<name>/settings
# ==============================================================================

class TestSettingsEndpoint:
    """FEATURE-044-F: PATCH endpoint for workflow settings."""

    def test_patch_settings_200(self, client):
        client.post("/api/workflow/create", json={"name": "api-test-044"})
        resp = client.patch("/api/workflow/api-test-044/settings",
                            json={"process_preference": {"interaction_mode": "dao-represent-human-to-interact"}})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"]
        assert data["data"]["process_preference"]["interaction_mode"] == "dao-represent-human-to-interact"

    def test_patch_settings_not_found_404(self, client):
        resp = client.patch("/api/workflow/nonexistent/settings",
                            json={"process_preference": {"interaction_mode": "dao-represent-human-to-interact"}})
        assert resp.status_code == 404

    def test_patch_settings_invalid_mode_400(self, client):
        client.post("/api/workflow/create", json={"name": "api-test-044b"})
        resp = client.patch("/api/workflow/api-test-044b/settings",
                            json={"process_preference": {"interaction_mode": "invalid"}})
        assert resp.status_code == 400

    def test_get_workflow_includes_global(self, client):
        client.post("/api/workflow/create", json={"name": "api-test-044c"})
        resp = client.get("/api/workflow/api-test-044c")
        data = resp.get_json()
        state = data.get("data", data) if isinstance(data, dict) and "data" in data else data
        assert "global" in state
        assert state["global"]["process_preference"]["interaction_mode"] == "interact-with-human"

    def test_roundtrip_toggle(self, client):
        """Simulate UI toggle: create → read default → change mode → read back."""
        client.post("/api/workflow/create", json={"name": "toggle-test"})

        # Read default
        resp = client.get("/api/workflow/toggle-test")
        state = resp.get_json()
        if "data" in state:
            state = state["data"]
        assert state["global"]["process_preference"]["interaction_mode"] == "interact-with-human"

        # Toggle to dao-represent-human-to-interact
        resp = client.patch("/api/workflow/toggle-test/settings",
                            json={"process_preference": {"interaction_mode": "dao-represent-human-to-interact"}})
        assert resp.status_code == 200

        # Read back
        resp = client.get("/api/workflow/toggle-test")
        state = resp.get_json()
        if "data" in state:
            state = state["data"]
        assert state["global"]["process_preference"]["interaction_mode"] == "dao-represent-human-to-interact"

        # Toggle to dao-represent-human-to-interact-for-questions-in-skill
        resp = client.patch("/api/workflow/toggle-test/settings",
                            json={"process_preference": {"interaction_mode": "dao-represent-human-to-interact-for-questions-in-skill"}})
        assert resp.status_code == 200

        # Read back
        resp = client.get("/api/workflow/toggle-test")
        state = resp.get_json()
        if "data" in state:
            state = state["data"]
        assert state["global"]["process_preference"]["interaction_mode"] == "dao-represent-human-to-interact-for-questions-in-skill"


# ==============================================================================
# Template tests: workflow-template.json includes global.process_preference
# ==============================================================================

class TestWorkflowTemplate:
    """FEATURE-044-E: workflow-template.json has global section."""

    def test_docs_template_has_global(self):
        path = os.path.join(os.path.dirname(__file__), "..",
                            "x-ipe-docs", "config", "workflow-template.json")
        with open(path) as f:
            tpl = json.load(f)
        assert "global" in tpl
        assert tpl["global"]["process_preference"]["interaction_mode"] == "interact-with-human"

    def test_src_template_has_global(self):
        path = os.path.join(os.path.dirname(__file__), "..",
                            "src", "x_ipe", "resources", "config", "workflow-template.json")
        with open(path) as f:
            tpl = json.load(f)
        assert "global" in tpl
        assert tpl["global"]["process_preference"]["interaction_mode"] == "interact-with-human"


# ==============================================================================
# Skill template tests: process_preference replaces old booleans
# ==============================================================================

class TestSkillTemplateUpdate:
    """FEATURE-044-B/C: All task-based skills use process_preference."""

    def _get_skill_files(self):
        files = sorted((ROOT / '.github/skills').glob('x-ipe-task-based-*/SKILL.md'))
        assert files, 'No discovered task skills'
        for path in files:
            frontmatter(path.read_text(), path.parent.name)
        return files

    def test_review_field_mentions_do_not_override_human_authority(self):
        """A legitimate optional output field is not a forbidden token."""
        for path in self._get_skill_files():
            data = yaml_contract(path.read_text(), 'Input Parameters', 'input')
            assert 'interaction_mode' in data['process_preference']
            assert 'require_human_review' not in data['process_preference']
        entry = ROOT / '.github/skills/x-ipe-workflow-task-execution/SKILL.md'
        common = linked_resource(entry, LIFECYCLE_TARGET)
        contract = section(common, 'Exact child output contract (no renamed schemas)')
        assert 'require_human_review is optional: preserve only if declared by child' in contract
        assert 'explicit domain approval gate remains binding in every mode' in contract

    def test_no_skill_has_auto_proceed(self):
        for path in self._get_skill_files():
            data = yaml_contract(path.read_text(), 'Input Parameters', 'input')
            assert 'auto_proceed' not in data.get('process_preference', {})

    def test_all_skills_have_process_preference(self):
        for path in self._get_skill_files():
            data = yaml_contract(path.read_text(), 'Input Parameters', 'input')
            preference = data['process_preference']['interaction_mode']
            assert preference == '{from input process_preference.interaction_mode}' or set(preference.split(' | ')) == set(specification_modes())

    def test_skill_discovery_uses_canonical_frontmatter_not_fixed_count(self):
        files = self._get_skill_files()
        names = [frontmatter(path.read_text(), path.parent.name)['name'] for path in files]
        assert len(set(names)) == len(files)
        assert set(names) == {path.parent.name for path in files}


# ==============================================================================
# Orchestrator tests: workflow-task-execution uses 3-mode routing
# ==============================================================================

class TestOrchestratorUpdate:
    """FEATURE-044-D: Workflow orchestrator uses process_preference."""

    def _read_orchestrator(self):
        path = os.path.join(os.path.dirname(__file__), "..", ".github", "skills",
                            "x-ipe-workflow-task-execution", "SKILL.md")
        return open(path).read()

    def test_optional_review_output_is_preserved_not_a_mode_bypass(self):
        entry = ROOT / '.github/skills/x-ipe-workflow-task-execution/SKILL.md'
        common = linked_resource(entry, LIFECYCLE_TARGET)
        assert 'Do not reject a child solely for omitting require_human_review' in common
        assert 'approval` is guidance, NOT human approval' in common

    def test_has_process_preference(self):
        content = self._read_orchestrator()
        assert "process_preference" in content

    def test_has_3_mode_routing(self):
        content = self._read_orchestrator()
        data = yaml_contract(content, 'Input Parameters', 'input')
        assert set(data['execution']['process_preference']['interaction_mode'].split(' | ')) == set(specification_modes())
        initialization = section(content, 'Input Parameters')
        for flag in ('--proceed@auto', '--proceed@stop-for-question', 'interact-with-human'):
            assert flag in initialization

    def test_references_dao_representative_skill(self):
        content = self._read_orchestrator()
        assert "x-ipe-assistant-user-representative-Engineer" in content


def test_candidate_named_enum_table_matches_current_specification():
    validate_mode_policy(current_candidate_policy())


def test_installed_lifecycle_named_enum_table_matches_current_authority():
    """Disk resource is authoritative for execution; preserve actual enum semantics."""
    entry = ROOT / '.github/skills/x-ipe-workflow-task-execution/SKILL.md'
    common = linked_resource(entry, LIFECYCLE_TARGET)
    installed = interaction_rows(common)
    corrected = current_candidate_policy()
    assert installed == corrected
    validate_mode_policy(installed)


@pytest.mark.parametrize('mutation', ['missing', 'inverted', 'duplicate'])
def test_mode_table_corruption_controls(mutation):
    path = ROOT / 'x-ipe-docs/skill-meta/x-ipe-workflow-task-execution/candidate/references/lifecycle.md'
    content = path.read_text()
    row = next(line for line in content.splitlines() if line.startswith(f'| {HYBRID} |'))
    if mutation == 'missing':
        content = content.replace(row, '')
    elif mutation == 'duplicate':
        content = content.replace(row, row + '\n' + row)
    else:
        content = content.replace(row, row.replace('DAO bounded answer/guidance', 'Ask human and wait'))
    with pytest.raises(AssertionError):
        validate_mode_policy(interaction_rows(content))


@pytest.mark.parametrize('mode', list(specification_modes()))
def test_all_specification_modes_roundtrip_service(workflow_service, sample_workflow, mode):
    result = workflow_service.update_settings(sample_workflow, {'process_preference': {'interaction_mode': mode}})
    assert result['success']
    assert workflow_service.get_workflow(sample_workflow)['global']['process_preference']['interaction_mode'] == mode


@pytest.mark.parametrize('key', ['auto_proceed', 'interaction_mode'])
@pytest.mark.parametrize('legacy,mode', [
    ('manual', 'interact-with-human'),
    ('auto', 'dao-represent-human-to-interact'),
    ('stop_for_question', HYBRID),
])
def test_current_spec_legacy_transport_mapping(workflow_service, sample_workflow, legacy, mode, key):
    spec = MODE_SPEC.read_text().split('**AC-044-E.8:**', 1)[1].split('**AC-044-E.9:**', 1)[0]
    mapping = dict(re.findall(r'\| `"([^"]+)"` \| `"([^"]+)"` \|', spec))
    assert mapping[legacy] == mode
    settings = {'process_preference': {key: legacy}}
    result = workflow_service.update_settings(sample_workflow, settings)
    assert result['success']
    assert result['data']['process_preference'] == {'interaction_mode': mode}
    assert settings == {'process_preference': {key: legacy}}
    preference = workflow_service.get_workflow(sample_workflow)['global']['process_preference']
    assert preference['interaction_mode'] == mode
    assert 'auto_proceed' not in preference
    path = workflow_service._get_workflow_path(sample_workflow)
    assert json.loads(path.read_text())['global']['process_preference'] == {'interaction_mode': mode}


@pytest.mark.parametrize('legacy,mode', [
    ('manual', 'interact-with-human'),
    ('auto', 'dao-represent-human-to-interact'),
    ('stop_for_question', HYBRID),
])
def test_legacy_settings_api_roundtrip(client, temp_project_dir, legacy, mode):
    assert client.post('/api/workflow/create', json={'name': 'legacy-api'}).status_code == 201
    response = client.patch('/api/workflow/legacy-api/settings',
                            json={'process_preference': {'auto_proceed': legacy}})
    assert response.status_code == 200
    assert response.get_json()['data']['process_preference'] == {'interaction_mode': mode}
    path = Path(temp_project_dir) / 'x-ipe-docs/engineering-workflow/workflow-legacy-api.json'
    assert json.loads(path.read_text())['global']['process_preference'] == {'interaction_mode': mode}


@pytest.mark.parametrize('key', ['auto_proceed', 'interaction_mode'])
@pytest.mark.parametrize('invalid', ['turbo', None, True, [], {}])
def test_invalid_legacy_or_current_mode_rejected_without_write(
        client, temp_project_dir, key, invalid):
    assert client.post('/api/workflow/create', json={'name': 'invalid-mode'}).status_code == 201
    path = Path(temp_project_dir) / 'x-ipe-docs/engineering-workflow/workflow-invalid-mode.json'
    before = path.read_bytes()
    response = client.patch('/api/workflow/invalid-mode/settings',
                            json={'process_preference': {key: invalid}})
    assert response.status_code == 400
    assert response.get_json()['error'] == 'INVALID_VALUE'
    assert path.read_bytes() == before


def test_current_mode_precedence_preserves_other_settings(workflow_service, sample_workflow):
    settings = {'process_preference': {
        'interaction_mode': HYBRID, 'auto_proceed': 'turbo', 'other_setting': 'keep'}}
    result = workflow_service.update_settings(sample_workflow, settings)
    assert result['success']
    assert result['data']['process_preference'] == {
        'interaction_mode': HYBRID, 'other_setting': 'keep'}
    assert settings['process_preference']['auto_proceed'] == 'turbo'


@pytest.mark.parametrize('preference,mode', [
    ({'auto_proceed': 'manual'}, 'interact-with-human'),
    ({'auto_proceed': 'auto'}, 'dao-represent-human-to-interact'),
    ({'auto_proceed': 'stop_for_question'}, HYBRID),
    ({'interaction_mode': 'auto'}, 'dao-represent-human-to-interact'),
    ({'interaction_mode': HYBRID, 'auto_proceed': 'auto'}, HYBRID),
    (None, 'interact-with-human'),
])
def test_persisted_legacy_read_list_and_next_write(
        workflow_service, sample_workflow, preference, mode):
    """AC-044-E.11: normalize in memory on read, canonicalize on the next write."""
    path = workflow_service._get_workflow_path(sample_workflow)
    state = json.loads(path.read_text())
    if preference is None:
        state.pop('global')
    else:
        state['global']['process_preference'] = preference
    path.write_text(json.dumps(state))
    before = path.read_bytes()
    loaded = workflow_service.get_workflow(sample_workflow)
    assert loaded['global']['process_preference'] == {'interaction_mode': mode}
    assert workflow_service.list_workflows()[0]['interaction_mode'] == mode
    assert path.read_bytes() == before
    assert workflow_service.update_action_status(sample_workflow, 'compose_idea', 'done')['success']
    assert json.loads(path.read_text())['global']['process_preference'] == {'interaction_mode': mode}
