#!/usr/bin/env python3
"""
Human Simulation Tests for FEATURE-006 v2.0: Multi-Project Folder Support

These tests simulate real user workflows and validate the feature
from a human perspective, testing end-to-end scenarios.

Run with:
    python playground/tests/test_playground_project_folders.py
"""
import os
import sys
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class HumanSimulationTest:
    """Base class for human simulation tests."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.assertions = []
    
    def assert_true(self, condition, message):
        """Assert a condition is true."""
        if condition:
            self.passed += 1
            self.assertions.append(('PASS', message))
        else:
            self.failed += 1
            self.assertions.append(('FAIL', message))
    
    def assert_equal(self, actual, expected, message):
        """Assert two values are equal."""
        if actual == expected:
            self.passed += 1
            self.assertions.append(('PASS', message))
        else:
            self.failed += 1
            self.assertions.append(('FAIL', f"{message} (expected {expected}, got {actual})"))
    
    def assert_in(self, item, collection, message):
        """Assert item is in collection."""
        if item in collection:
            self.passed += 1
            self.assertions.append(('PASS', message))
        else:
            self.failed += 1
            self.assertions.append(('FAIL', f"{message} ({item} not found)"))
    
    def print_results(self):
        """Print test results."""
        for status, message in self.assertions:
            symbol = "✅" if status == 'PASS' else "❌"
            print(f"  {symbol} {message}")


def get_service(temp_dir):
    """Get ProjectFoldersService with temp database."""
    from x_ipe.services import ProjectFoldersService
    db_path = os.path.join(temp_dir, 'test_projects.db')
    return ProjectFoldersService(db_path)


# =============================================================================
# HUMAN SIMULATION SCENARIOS
# =============================================================================

def test_scenario_first_time_user():
    """
    Scenario: First-time user sees default project
    
    Given: User opens app for the first time
    When: They view project folders
    Then: They see "Default Project Folder" pointing to "."
    """
    print("\n📋 Scenario: First-time user sees default project")
    
    temp_dir = tempfile.mkdtemp()
    test = HumanSimulationTest()
    
    try:
        service = get_service(temp_dir)
        
        # User views project list
        projects = service.get_all()
        
        test.assert_equal(len(projects), 1, "Should have exactly 1 project")
        test.assert_equal(projects[0]['name'], 'Default Project Folder', 
                         "Default project should be named 'Default Project Folder'")
        test.assert_equal(projects[0]['path'], '.', 
                         "Default project path should be '.'")
        test.assert_equal(service.get_active_id(), 1, 
                         "Default project should be active")
        
        test.print_results()
        return test.failed == 0
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scenario_add_project_folder():
    """
    Scenario: User adds a new project folder
    
    Given: User is on settings page
    When: They click "Add Project" and enter name/path
    Then: New project appears in the list
    """
    print("\n📋 Scenario: User adds a new project folder")
    
    temp_dir = tempfile.mkdtemp()
    test = HumanSimulationTest()
    
    try:
        service = get_service(temp_dir)
        
        # Create a test project directory
        project_path = os.path.join(temp_dir, 'my_new_project')
        os.makedirs(project_path)
        
        # User adds new project
        result = service.add('My New Project', project_path)
        
        test.assert_true(result['success'], "Add project should succeed")
        test.assert_equal(result['project']['name'], 'My New Project',
                         "Project name should match")
        
        # Verify it appears in list
        projects = service.get_all()
        names = [p['name'] for p in projects]
        
        test.assert_in('My New Project', names, "New project should appear in list")
        test.assert_equal(len(projects), 2, "Should now have 2 projects")
        
        test.print_results()
        return test.failed == 0
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scenario_switch_project():
    """
    Scenario: User switches between projects
    
    Given: User has multiple projects
    When: They select a different project from dropdown
    Then: Active project changes and sidebar reloads
    """
    print("\n📋 Scenario: User switches between projects")
    
    temp_dir = tempfile.mkdtemp()
    test = HumanSimulationTest()
    
    try:
        service = get_service(temp_dir)
        
        # Create two project directories
        project_a = os.path.join(temp_dir, 'project_a')
        project_b = os.path.join(temp_dir, 'project_b')
        os.makedirs(project_a)
        os.makedirs(project_b)
        
        # Add projects
        result_a = service.add('Project A', project_a)
        result_b = service.add('Project B', project_b)
        
        id_a = result_a['project']['id']
        id_b = result_b['project']['id']
        
        # User switches to Project A
        result = service.set_active(id_a)
        
        test.assert_true(result['success'], "Switch to Project A should succeed")
        test.assert_equal(result['active_project_id'], id_a,
                         "Active project ID should be Project A")
        
        # User switches to Project B
        result = service.set_active(id_b)
        
        test.assert_true(result['success'], "Switch to Project B should succeed")
        test.assert_equal(service.get_active_id(), id_b,
                         "Active project should now be Project B")
        
        test.print_results()
        return test.failed == 0
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scenario_rename_project():
    """
    Scenario: User renames a project
    
    Given: User has a project
    When: They edit the project name
    Then: Project name is updated in the list
    """
    print("\n📋 Scenario: User renames a project")
    
    temp_dir = tempfile.mkdtemp()
    test = HumanSimulationTest()
    
    try:
        service = get_service(temp_dir)
        
        # Create project
        project_path = os.path.join(temp_dir, 'my_project')
        os.makedirs(project_path)
        result = service.add('Old Name', project_path)
        project_id = result['project']['id']
        
        # User renames it
        result = service.update(project_id, name='New Name')
        
        test.assert_true(result['success'], "Rename should succeed")
        test.assert_equal(result['project']['name'], 'New Name',
                         "Project name should be updated")
        
        # Verify in list
        project = service.get_by_id(project_id)
        test.assert_equal(project['name'], 'New Name',
                         "Name should persist after retrieval")
        
        test.print_results()
        return test.failed == 0
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scenario_delete_project():
    """
    Scenario: User deletes a project
    
    Given: User has multiple projects
    When: They delete a non-active project
    Then: Project is removed from the list
    """
    print("\n📋 Scenario: User deletes a project")
    
    temp_dir = tempfile.mkdtemp()
    test = HumanSimulationTest()
    
    try:
        service = get_service(temp_dir)
        
        # Create project
        project_path = os.path.join(temp_dir, 'to_delete')
        os.makedirs(project_path)
        result = service.add('To Delete', project_path)
        project_id = result['project']['id']
        
        initial_count = len(service.get_all())
        
        # User deletes it
        result = service.delete(project_id)
        
        test.assert_true(result['success'], "Delete should succeed")
        
        # Verify it's gone
        projects = service.get_all()
        test.assert_equal(len(projects), initial_count - 1,
                         "Project count should decrease by 1")
        
        ids = [p['id'] for p in projects]
        test.assert_true(project_id not in ids,
                        "Deleted project ID should not be in list")
        
        test.print_results()
        return test.failed == 0
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scenario_cannot_delete_last_project():
    """
    Scenario: User tries to delete the only project
    
    Given: User has only one project
    When: They try to delete it
    Then: Error message appears, project remains
    """
    print("\n📋 Scenario: User cannot delete the last project")
    
    temp_dir = tempfile.mkdtemp()
    test = HumanSimulationTest()
    
    try:
        service = get_service(temp_dir)
        
        # Only default project exists
        projects = service.get_all()
        test.assert_equal(len(projects), 1, "Should have only 1 project")
        
        default_id = projects[0]['id']
        
        # User tries to delete it
        result = service.delete(default_id)
        
        test.assert_true(not result['success'], "Delete should fail")
        test.assert_in('last', result['error'].lower(),
                      "Error should mention 'last' project")
        
        # Verify project still exists
        test.assert_equal(len(service.get_all()), 1,
                         "Project should still exist")
        
        test.print_results()
        return test.failed == 0
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scenario_cannot_delete_active_project():
    """
    Scenario: User tries to delete the active project
    
    Given: User has the project active
    When: They try to delete it
    Then: Error message tells them to switch first
    """
    print("\n📋 Scenario: User cannot delete the active project")
    
    temp_dir = tempfile.mkdtemp()
    test = HumanSimulationTest()
    
    try:
        service = get_service(temp_dir)
        
        # Create and activate a project
        project_path = os.path.join(temp_dir, 'active_project')
        os.makedirs(project_path)
        result = service.add('Active Project', project_path)
        project_id = result['project']['id']
        
        service.set_active(project_id)
        
        # User tries to delete active project
        result = service.delete(project_id, active_project_id=project_id)
        
        test.assert_true(not result['success'], "Delete should fail")
        test.assert_true('switch' in result['error'].lower() or 'active' in result['error'].lower(),
                        "Error should mention switching")
        
        test.print_results()
        return test.failed == 0
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scenario_validation_errors():
    """
    Scenario: User enters invalid data
    
    Given: User is adding/editing a project
    When: They enter invalid name/path
    Then: Appropriate error messages appear
    """
    print("\n📋 Scenario: User sees validation errors")
    
    temp_dir = tempfile.mkdtemp()
    test = HumanSimulationTest()
    
    try:
        service = get_service(temp_dir)
        valid_path = os.path.join(temp_dir, 'valid')
        os.makedirs(valid_path)
        
        # Empty name
        result = service.add('', valid_path)
        test.assert_true('name' in result.get('errors', {}),
                        "Empty name should show error")
        
        # Empty path
        result = service.add('Valid Name', '')
        test.assert_true('path' in result.get('errors', {}),
                        "Empty path should show error")
        
        # Non-existent path
        result = service.add('Bad Path', '/nonexistent/xyz')
        test.assert_true('not exist' in result.get('errors', {}).get('path', '').lower(),
                        "Non-existent path should show error")
        
        # Duplicate name
        service.add('Unique', valid_path)
        result = service.add('Unique', valid_path)
        test.assert_true('already exists' in result.get('errors', {}).get('name', '').lower(),
                        "Duplicate name should show error")
        
        test.print_results()
        return test.failed == 0
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scenario_project_persistence():
    """
    Scenario: User's projects persist across sessions
    
    Given: User has added projects
    When: They close and reopen the app
    Then: All projects are still there
    """
    print("\n📋 Scenario: Projects persist across sessions")
    
    temp_dir = tempfile.mkdtemp()
    test = HumanSimulationTest()
    
    try:
        from x_ipe.services import ProjectFoldersService
        db_path = os.path.join(temp_dir, 'persist_test.db')
        
        # Create projects
        project_path = os.path.join(temp_dir, 'persistent')
        os.makedirs(project_path)
        
        # Session 1: Add projects
        service1 = ProjectFoldersService(db_path)
        service1.add('Persistent Project', project_path)
        service1.set_active(2)  # Switch to new project
        
        # Session 2: Verify they're still there
        service2 = ProjectFoldersService(db_path)
        projects = service2.get_all()
        
        names = [p['name'] for p in projects]
        test.assert_in('Persistent Project', names,
                      "Project should persist across sessions")
        test.assert_equal(service2.get_active_id(), 2,
                         "Active project should persist")
        
        test.print_results()
        return test.failed == 0
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """Run all human simulation tests."""
    print("\n" + "=" * 60)
    print("HUMAN SIMULATION TESTS")
    print("FEATURE-006 v2.0: Multi-Project Folder Support")
    print("=" * 60)
    
    tests = [
        test_scenario_first_time_user,
        test_scenario_add_project_folder,
        test_scenario_switch_project,
        test_scenario_rename_project,
        test_scenario_delete_project,
        test_scenario_cannot_delete_last_project,
        test_scenario_cannot_delete_active_project,
        test_scenario_validation_errors,
        test_scenario_project_persistence,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ {test_func.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    total = passed + failed
    print(f"RESULTS: {passed}/{total} scenarios passed")
    
    if failed == 0:
        print("✅ All human simulation tests PASSED")
    else:
        print(f"❌ {failed} scenario(s) FAILED")
    
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
