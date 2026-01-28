"""
Tests for FEATURE-006 v2.0: Multi-Project Folder Support

Tests cover:
- ProjectFoldersService: CRUD operations for project folders
- Active project management (get/set active project)
- Path validation for project folders
- API endpoints: GET/POST/PUT/DELETE /api/projects
- Switch project endpoint: POST /api/projects/switch
- Default project initialization
"""
import os
import json
import pytest
import tempfile
import sqlite3
from pathlib import Path


# =============================================================================
# UNIT TESTS: ProjectFoldersService
# =============================================================================

class TestProjectFoldersServiceInit:
    """Tests for ProjectFoldersService initialization"""

    def test_init_creates_project_folders_table(self, project_folders_service, temp_db_path):
        """ProjectFoldersService creates project_folders table on init"""
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project_folders'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'project_folders'

    def test_init_creates_default_project_folder(self, project_folders_service):
        """ProjectFoldersService creates 'Default Project Folder' on first run"""
        projects = project_folders_service.get_all()
        
        assert len(projects) >= 1
        default_project = projects[0]
        assert default_project['name'] == 'Default Project Folder'
        assert default_project['path'] == '.'

    def test_init_does_not_duplicate_default_project(self, temp_db_path):
        """Re-initializing service doesn't create duplicate default project"""
        from x_ipe.services import ProjectFoldersService
        
        # Initialize twice
        service1 = ProjectFoldersService(temp_db_path)
        service2 = ProjectFoldersService(temp_db_path)
        
        projects = service2.get_all()
        default_count = sum(1 for p in projects if p['name'] == 'Default Project Folder')
        
        assert default_count == 1


class TestProjectFoldersServiceGetAll:
    """Tests for ProjectFoldersService.get_all()"""

    def test_get_all_returns_list(self, project_folders_service):
        """get_all() returns a list"""
        result = project_folders_service.get_all()
        
        assert isinstance(result, list)

    def test_get_all_contains_required_fields(self, project_folders_service):
        """Each project has id, name, and path fields"""
        projects = project_folders_service.get_all()
        
        assert len(projects) > 0
        for project in projects:
            assert 'id' in project
            assert 'name' in project
            assert 'path' in project

    def test_get_all_returns_projects_in_order(self, project_folders_service, temp_project):
        """Projects are returned in order by ID"""
        # Add more projects
        project_folders_service.add('Project B', str(temp_project))
        project_folders_service.add('Project A', str(temp_project))
        
        projects = project_folders_service.get_all()
        ids = [p['id'] for p in projects]
        
        assert ids == sorted(ids)


class TestProjectFoldersServiceGetById:
    """Tests for ProjectFoldersService.get_by_id()"""

    def test_get_by_id_returns_project(self, project_folders_service):
        """get_by_id() returns project dict for valid ID"""
        projects = project_folders_service.get_all()
        project_id = projects[0]['id']
        
        result = project_folders_service.get_by_id(project_id)
        
        assert result is not None
        assert result['id'] == project_id

    def test_get_by_id_returns_none_for_invalid_id(self, project_folders_service):
        """get_by_id() returns None for non-existent ID"""
        result = project_folders_service.get_by_id(99999)
        
        assert result is None


class TestProjectFoldersServiceAdd:
    """Tests for ProjectFoldersService.add()"""

    def test_add_project_success(self, project_folders_service, temp_project):
        """add() creates new project folder"""
        result = project_folders_service.add('My Project', str(temp_project))
        
        assert result['success'] is True
        assert 'project' in result
        assert result['project']['name'] == 'My Project'
        assert result['project']['path'] == str(temp_project)

    def test_add_project_returns_id(self, project_folders_service, temp_project):
        """add() returns project with generated ID"""
        result = project_folders_service.add('New Project', str(temp_project))
        
        assert 'id' in result['project']
        assert isinstance(result['project']['id'], int)

    def test_add_project_strips_whitespace(self, project_folders_service, temp_project):
        """add() strips whitespace from name and path"""
        result = project_folders_service.add('  Spaced Name  ', f'  {temp_project}  ')
        
        assert result['project']['name'] == 'Spaced Name'
        assert result['project']['path'] == str(temp_project)

    def test_add_duplicate_name_fails(self, project_folders_service, temp_project):
        """add() fails for duplicate project name"""
        project_folders_service.add('Unique Name', str(temp_project))
        result = project_folders_service.add('Unique Name', str(temp_project))
        
        assert result['success'] is False
        assert 'errors' in result
        assert 'name' in result['errors']

    def test_add_empty_name_fails(self, project_folders_service, temp_project):
        """add() fails for empty name"""
        result = project_folders_service.add('', str(temp_project))
        
        assert result['success'] is False
        assert 'errors' in result
        assert 'name' in result['errors']
        assert 'required' in result['errors']['name'].lower()

    def test_add_empty_path_fails(self, project_folders_service):
        """add() fails for empty path"""
        result = project_folders_service.add('Valid Name', '')
        
        assert result['success'] is False
        assert 'errors' in result
        assert 'path' in result['errors']
        assert 'required' in result['errors']['path'].lower()

    def test_add_nonexistent_path_fails(self, project_folders_service):
        """add() fails for non-existent path"""
        result = project_folders_service.add('Test Project', '/nonexistent/path/xyz/123')
        
        assert result['success'] is False
        assert 'errors' in result
        assert 'path' in result['errors']
        assert 'not exist' in result['errors']['path'].lower()

    def test_add_file_path_fails(self, project_folders_service, temp_project):
        """add() fails when path is a file, not directory"""
        test_file = temp_project / 'test.txt'
        test_file.write_text('test content')
        
        result = project_folders_service.add('File Project', str(test_file))
        
        assert result['success'] is False
        assert 'errors' in result
        assert 'path' in result['errors']
        assert 'not a directory' in result['errors']['path'].lower()


class TestProjectFoldersServiceUpdate:
    """Tests for ProjectFoldersService.update()"""

    def test_update_project_name_success(self, project_folders_service, temp_project):
        """update() changes project name"""
        add_result = project_folders_service.add('Original Name', str(temp_project))
        project_id = add_result['project']['id']
        
        result = project_folders_service.update(project_id, name='New Name')
        
        assert result['success'] is True
        assert result['project']['name'] == 'New Name'
        assert result['project']['path'] == str(temp_project)  # Path unchanged

    def test_update_project_path_success(self, project_folders_service, temp_project, tmp_path):
        """update() changes project path"""
        new_path = tmp_path / 'new_project'
        new_path.mkdir()
        
        add_result = project_folders_service.add('Test Project', str(temp_project))
        project_id = add_result['project']['id']
        
        result = project_folders_service.update(project_id, path=str(new_path))
        
        assert result['success'] is True
        assert result['project']['path'] == str(new_path)

    def test_update_both_name_and_path(self, project_folders_service, temp_project, tmp_path):
        """update() can change both name and path"""
        new_path = tmp_path / 'updated_project'
        new_path.mkdir()
        
        add_result = project_folders_service.add('Old Name', str(temp_project))
        project_id = add_result['project']['id']
        
        result = project_folders_service.update(project_id, name='Updated Name', path=str(new_path))
        
        assert result['success'] is True
        assert result['project']['name'] == 'Updated Name'
        assert result['project']['path'] == str(new_path)

    def test_update_nonexistent_project_fails(self, project_folders_service):
        """update() fails for non-existent project ID"""
        result = project_folders_service.update(99999, name='New Name')
        
        assert result['success'] is False
        assert 'error' in result

    def test_update_to_duplicate_name_fails(self, project_folders_service, temp_project):
        """update() fails when changing to existing name"""
        project_folders_service.add('Project A', str(temp_project))
        add_result = project_folders_service.add('Project B', str(temp_project))
        project_b_id = add_result['project']['id']
        
        result = project_folders_service.update(project_b_id, name='Project A')
        
        assert result['success'] is False
        assert 'errors' in result
        assert 'name' in result['errors']

    def test_update_to_invalid_path_fails(self, project_folders_service, temp_project):
        """update() fails for invalid path"""
        add_result = project_folders_service.add('Test Project', str(temp_project))
        project_id = add_result['project']['id']
        
        result = project_folders_service.update(project_id, path='/nonexistent/path')
        
        assert result['success'] is False
        assert 'errors' in result
        assert 'path' in result['errors']


class TestProjectFoldersServiceDelete:
    """Tests for ProjectFoldersService.delete()"""

    def test_delete_project_success(self, project_folders_service, temp_project):
        """delete() removes project folder"""
        add_result = project_folders_service.add('To Delete', str(temp_project))
        project_id = add_result['project']['id']
        
        result = project_folders_service.delete(project_id)
        
        assert result['success'] is True
        assert project_folders_service.get_by_id(project_id) is None

    def test_delete_nonexistent_project_fails(self, project_folders_service):
        """delete() fails for non-existent project ID"""
        result = project_folders_service.delete(99999)
        
        assert result['success'] is False
        assert 'error' in result

    def test_delete_last_project_fails(self, project_folders_service):
        """delete() fails when trying to delete the only project"""
        projects = project_folders_service.get_all()
        # Should only have default project
        assert len(projects) == 1
        
        result = project_folders_service.delete(projects[0]['id'])
        
        assert result['success'] is False
        assert 'last project' in result['error'].lower()

    def test_delete_active_project_fails(self, project_folders_service, temp_project):
        """delete() fails when deleting the active project"""
        add_result = project_folders_service.add('New Active', str(temp_project))
        project_id = add_result['project']['id']
        
        # Set as active
        project_folders_service.set_active(project_id)
        
        # Try to delete
        result = project_folders_service.delete(project_id, active_project_id=project_id)
        
        assert result['success'] is False
        assert 'switch' in result['error'].lower() or 'active' in result['error'].lower()


class TestProjectFoldersServiceActiveProject:
    """Tests for active project management"""

    def test_get_active_id_returns_default(self, project_folders_service):
        """get_active_id() returns 1 (default project) initially"""
        result = project_folders_service.get_active_id()
        
        assert result == 1

    def test_set_active_success(self, project_folders_service, temp_project):
        """set_active() changes active project"""
        add_result = project_folders_service.add('New Project', str(temp_project))
        new_id = add_result['project']['id']
        
        result = project_folders_service.set_active(new_id)
        
        assert result['success'] is True
        assert result['active_project_id'] == new_id
        assert project_folders_service.get_active_id() == new_id

    def test_set_active_returns_project_details(self, project_folders_service, temp_project):
        """set_active() returns project details"""
        add_result = project_folders_service.add('Details Project', str(temp_project))
        new_id = add_result['project']['id']
        
        result = project_folders_service.set_active(new_id)
        
        assert 'project' in result
        assert result['project']['id'] == new_id
        assert result['project']['name'] == 'Details Project'

    def test_set_active_invalid_id_fails(self, project_folders_service):
        """set_active() fails for non-existent project ID"""
        result = project_folders_service.set_active(99999)
        
        assert result['success'] is False
        assert 'error' in result

    def test_active_project_persists(self, temp_db_path, temp_project):
        """Active project ID persists across service instances"""
        from x_ipe.services import ProjectFoldersService
        
        service1 = ProjectFoldersService(temp_db_path)
        add_result = service1.add('Persistent Project', str(temp_project))
        new_id = add_result['project']['id']
        service1.set_active(new_id)
        
        # Create new instance
        service2 = ProjectFoldersService(temp_db_path)
        
        assert service2.get_active_id() == new_id


# =============================================================================
# API TESTS: /api/projects
# =============================================================================

class TestProjectsAPIGetAll:
    """Tests for GET /api/projects endpoint"""

    def test_get_projects_returns_200(self, client):
        """GET /api/projects returns 200 OK"""
        response = client.get('/api/projects')
        
        assert response.status_code == 200

    def test_get_projects_returns_json(self, client):
        """GET /api/projects returns JSON"""
        response = client.get('/api/projects')
        
        assert response.content_type == 'application/json'

    def test_get_projects_contains_projects_list(self, client):
        """GET /api/projects includes projects array"""
        response = client.get('/api/projects')
        data = json.loads(response.data)
        
        assert 'projects' in data
        assert isinstance(data['projects'], list)

    def test_get_projects_contains_active_project_id(self, client):
        """GET /api/projects includes active_project_id"""
        response = client.get('/api/projects')
        data = json.loads(response.data)
        
        assert 'active_project_id' in data

    def test_get_projects_includes_default_project(self, client):
        """GET /api/projects includes default project"""
        response = client.get('/api/projects')
        data = json.loads(response.data)
        
        project_names = [p['name'] for p in data['projects']]
        assert 'Default Project Folder' in project_names


class TestProjectsAPICreate:
    """Tests for POST /api/projects endpoint"""

    def test_post_projects_returns_201_on_success(self, client, temp_project):
        """POST /api/projects returns 201 Created on valid data"""
        response = client.post(
            '/api/projects',
            json={'name': 'Test Project', 'path': str(temp_project)},
            content_type='application/json'
        )
        
        assert response.status_code == 201

    def test_post_projects_returns_success_true(self, client, temp_project):
        """POST /api/projects returns success: true"""
        response = client.post(
            '/api/projects',
            json={'name': 'Success Test', 'path': str(temp_project)},
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert data['success'] is True

    def test_post_projects_returns_created_project(self, client, temp_project):
        """POST /api/projects returns created project details"""
        response = client.post(
            '/api/projects',
            json={'name': 'Details Test', 'path': str(temp_project)},
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert 'project' in data
        assert data['project']['name'] == 'Details Test'
        assert 'id' in data['project']

    def test_post_projects_returns_400_on_invalid_path(self, client):
        """POST /api/projects returns 400 on invalid path"""
        response = client.post(
            '/api/projects',
            json={'name': 'Bad Path', 'path': '/nonexistent/path/xyz'},
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_post_projects_returns_400_on_duplicate_name(self, client, temp_project):
        """POST /api/projects returns 400 on duplicate name"""
        client.post('/api/projects', json={'name': 'Duplicate', 'path': str(temp_project)})
        
        response = client.post(
            '/api/projects',
            json={'name': 'Duplicate', 'path': str(temp_project)},
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_post_projects_returns_400_on_missing_name(self, client, temp_project):
        """POST /api/projects returns 400 when name missing"""
        response = client.post(
            '/api/projects',
            json={'path': str(temp_project)},
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_post_projects_returns_400_without_json(self, client):
        """POST /api/projects returns 400 without JSON content"""
        response = client.post('/api/projects', data='not json')
        
        assert response.status_code == 400


class TestProjectsAPIUpdate:
    """Tests for PUT /api/projects/<id> endpoint"""

    def test_put_project_returns_200_on_success(self, client, temp_project):
        """PUT /api/projects/<id> returns 200 on valid update"""
        # Create a project first
        create_resp = client.post(
            '/api/projects',
            json={'name': 'To Update', 'path': str(temp_project)}
        )
        project_id = json.loads(create_resp.data)['project']['id']
        
        response = client.put(
            f'/api/projects/{project_id}',
            json={'name': 'Updated Name'},
            content_type='application/json'
        )
        
        assert response.status_code == 200

    def test_put_project_updates_name(self, client, temp_project):
        """PUT /api/projects/<id> updates project name"""
        create_resp = client.post(
            '/api/projects',
            json={'name': 'Original', 'path': str(temp_project)}
        )
        project_id = json.loads(create_resp.data)['project']['id']
        
        response = client.put(
            f'/api/projects/{project_id}',
            json={'name': 'Modified'},
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert data['project']['name'] == 'Modified'

    def test_put_project_returns_400_on_invalid_id(self, client):
        """PUT /api/projects/<id> returns 400 for non-existent ID"""
        response = client.put(
            '/api/projects/99999',
            json={'name': 'New Name'},
            content_type='application/json'
        )
        
        assert response.status_code == 400


class TestProjectsAPIDelete:
    """Tests for DELETE /api/projects/<id> endpoint"""

    def test_delete_project_returns_200_on_success(self, client, temp_project):
        """DELETE /api/projects/<id> returns 200 on successful deletion"""
        create_resp = client.post(
            '/api/projects',
            json={'name': 'To Delete', 'path': str(temp_project)}
        )
        project_id = json.loads(create_resp.data)['project']['id']
        
        response = client.delete(f'/api/projects/{project_id}')
        
        assert response.status_code == 200

    def test_delete_project_removes_from_list(self, client, temp_project):
        """DELETE /api/projects/<id> removes project from list"""
        create_resp = client.post(
            '/api/projects',
            json={'name': 'Deletable', 'path': str(temp_project)}
        )
        project_id = json.loads(create_resp.data)['project']['id']
        
        client.delete(f'/api/projects/{project_id}')
        
        get_resp = client.get('/api/projects')
        data = json.loads(get_resp.data)
        project_ids = [p['id'] for p in data['projects']]
        
        assert project_id not in project_ids

    def test_delete_last_project_returns_400(self, client):
        """DELETE /api/projects/<id> returns 400 when deleting last project"""
        # Get the default project (should be only one)
        get_resp = client.get('/api/projects')
        data = json.loads(get_resp.data)
        project_id = data['projects'][0]['id']
        
        response = client.delete(f'/api/projects/{project_id}')
        
        assert response.status_code == 400


class TestProjectsAPISwitch:
    """Tests for POST /api/projects/switch endpoint"""

    def test_switch_project_returns_200_on_success(self, client, temp_project):
        """POST /api/projects/switch returns 200 on valid switch"""
        # Create a project
        create_resp = client.post(
            '/api/projects',
            json={'name': 'Switch Target', 'path': str(temp_project)}
        )
        project_id = json.loads(create_resp.data)['project']['id']
        
        response = client.post(
            '/api/projects/switch',
            json={'project_id': project_id},
            content_type='application/json'
        )
        
        assert response.status_code == 200

    def test_switch_project_returns_active_id(self, client, temp_project):
        """POST /api/projects/switch returns new active_project_id"""
        create_resp = client.post(
            '/api/projects',
            json={'name': 'Active Target', 'path': str(temp_project)}
        )
        project_id = json.loads(create_resp.data)['project']['id']
        
        response = client.post(
            '/api/projects/switch',
            json={'project_id': project_id},
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert data['active_project_id'] == project_id

    def test_switch_project_updates_active(self, client, temp_project):
        """POST /api/projects/switch updates active project in subsequent GET"""
        create_resp = client.post(
            '/api/projects',
            json={'name': 'Check Active', 'path': str(temp_project)}
        )
        project_id = json.loads(create_resp.data)['project']['id']
        
        client.post('/api/projects/switch', json={'project_id': project_id})
        
        get_resp = client.get('/api/projects')
        data = json.loads(get_resp.data)
        
        assert data['active_project_id'] == project_id

    def test_switch_project_returns_400_for_invalid_id(self, client):
        """POST /api/projects/switch returns 400 for non-existent ID"""
        response = client.post(
            '/api/projects/switch',
            json={'project_id': 99999},
            content_type='application/json'
        )
        
        assert response.status_code == 400

    def test_switch_project_returns_400_without_project_id(self, client):
        """POST /api/projects/switch returns 400 when project_id missing"""
        response = client.post(
            '/api/projects/switch',
            json={},
            content_type='application/json'
        )
        
        assert response.status_code == 400


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestProjectFoldersIntegration:
    """Integration tests for project folders feature"""

    def test_add_project_appears_in_api_response(self, client, temp_project):
        """Added project appears in GET /api/projects"""
        client.post('/api/projects', json={'name': 'Integration Test', 'path': str(temp_project)})
        
        response = client.get('/api/projects')
        data = json.loads(response.data)
        
        project_names = [p['name'] for p in data['projects']]
        assert 'Integration Test' in project_names

    def test_switch_and_delete_workflow(self, client, temp_project):
        """Can switch away from a project, then delete it"""
        # Add project
        create_resp = client.post(
            '/api/projects',
            json={'name': 'Workflow Test', 'path': str(temp_project)}
        )
        project_id = json.loads(create_resp.data)['project']['id']
        
        # Switch to it
        client.post('/api/projects/switch', json={'project_id': project_id})
        
        # Switch back to default
        client.post('/api/projects/switch', json={'project_id': 1})
        
        # Now can delete
        delete_resp = client.delete(f'/api/projects/{project_id}')
        
        assert delete_resp.status_code == 200

    def test_full_crud_workflow(self, client, temp_project, tmp_path):
        """Full Create-Read-Update-Delete workflow"""
        # CREATE
        create_resp = client.post(
            '/api/projects',
            json={'name': 'CRUD Test', 'path': str(temp_project)}
        )
        assert create_resp.status_code == 201
        project_id = json.loads(create_resp.data)['project']['id']
        
        # READ
        get_resp = client.get('/api/projects')
        data = json.loads(get_resp.data)
        project_names = [p['name'] for p in data['projects']]
        assert 'CRUD Test' in project_names
        
        # UPDATE
        new_path = tmp_path / 'updated_path'
        new_path.mkdir()
        update_resp = client.put(
            f'/api/projects/{project_id}',
            json={'name': 'CRUD Updated', 'path': str(new_path)}
        )
        assert update_resp.status_code == 200
        updated_data = json.loads(update_resp.data)
        assert updated_data['project']['name'] == 'CRUD Updated'
        
        # DELETE
        delete_resp = client.delete(f'/api/projects/{project_id}')
        assert delete_resp.status_code == 200


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path"""
    return str(tmp_path / "test_project_folders.db")


@pytest.fixture
def project_folders_service(temp_db_path):
    """Create ProjectFoldersService instance with temp database"""
    from x_ipe.services import ProjectFoldersService
    return ProjectFoldersService(temp_db_path)


@pytest.fixture
def app(temp_project, temp_db_path):
    """Create Flask app with test configuration"""
    from src.app import create_app
    
    app = create_app({
        'TESTING': True,
        'PROJECT_ROOT': str(temp_project),
        'SETTINGS_DB': temp_db_path
    })
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()
