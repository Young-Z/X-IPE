#!/usr/bin/env python3
"""
Human Simulation Tests: Settings & Configuration (FEATURE-006)

These tests simulate human interaction scenarios to validate the user experience.
NOT unit tests - these test the behavior from a human perspective.

Usage:
    uv run python playground/tests/test_playground_settings.py
"""
import os
import sys
import tempfile

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from x_ipe.services import SettingsService


class Colors:
    """ANSI color codes for output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_scenario(name: str):
    """Print scenario header."""
    print(f"\n{Colors.BOLD}📋 Scenario: {name}{Colors.RESET}")
    print("-" * 50)


def print_pass(message: str):
    """Print pass message."""
    print(f"   {Colors.GREEN}✅ PASS:{Colors.RESET} {message}")


def print_fail(message: str):
    """Print fail message."""
    print(f"   {Colors.RED}❌ FAIL:{Colors.RESET} {message}")


def print_step(step: str):
    """Print step description."""
    print(f"   → {step}")


class SettingsPlaygroundTests:
    """Human simulation tests for Settings feature."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.temp_dir = None
    
    def setup(self):
        """Create temp directory and service."""
        self.temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(self.temp_dir, 'test_settings.db')
        self.service = SettingsService(db_path)
        return self.service
    
    def teardown(self):
        """Cleanup temp files."""
        import shutil
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def assert_true(self, condition: bool, message: str):
        """Assert condition is true."""
        if condition:
            print_pass(message)
            self.passed += 1
        else:
            print_fail(message)
            self.failed += 1
    
    def assert_equal(self, actual, expected, message: str):
        """Assert actual equals expected."""
        if actual == expected:
            print_pass(f"{message} (got: {actual})")
            self.passed += 1
        else:
            print_fail(f"{message} (expected: {expected}, got: {actual})")
            self.failed += 1
    
    # =========================================================================
    # Scenario 1: First-time User Experience
    # =========================================================================
    def test_scenario_first_time_user(self):
        """
        Scenario: User opens app for the first time
        Expected: Settings should have sensible defaults
        """
        print_scenario("First-time User Experience")
        
        service = self.setup()
        
        print_step("User opens the app for the first time")
        settings = service.get_all()
        
        print_step("Checking default values are sensible")
        self.assert_true('project_root' in settings, "project_root exists in settings")
        self.assert_equal(settings['project_root'], '.', "project_root defaults to '.'")
        
        self.teardown()
    
    # =========================================================================
    # Scenario 2: User Changes Project Root
    # =========================================================================
    def test_scenario_change_project_root(self):
        """
        Scenario: User changes project root to a valid path
        Expected: Path should update and persist
        """
        print_scenario("User Changes Project Root")
        
        service = self.setup()
        
        print_step("User opens settings page")
        settings = service.get_all()
        original = settings.get('project_root', '.')
        
        print_step("User enters a new valid project path")
        # Use the temp directory as valid path
        service.set('project_root', self.temp_dir)
        
        print_step("User refreshes page (simulating page reload)")
        db_path = os.path.join(self.temp_dir, 'test_settings.db')
        new_service = SettingsService(db_path)
        settings = new_service.get_all()
        self.assert_equal(settings['project_root'], self.temp_dir, "Project root persisted")
        
        self.teardown()
    
    # =========================================================================
    # Scenario 3: User Adds Custom Setting
    # =========================================================================
    def test_scenario_add_custom_setting(self):
        """
        Scenario: User/app adds a custom setting
        Expected: Custom setting should be stored and retrieved
        """
        print_scenario("User Adds Custom Setting")
        
        service = self.setup()
        
        print_step("App stores a custom preference")
        service.set('theme', 'dark')
        
        print_step("Verifying custom setting is stored")
        theme = service.get('theme')
        self.assert_equal(theme, 'dark', "Custom setting stored")
        
        print_step("Verifying it appears in get_all()")
        settings = service.get_all()
        self.assert_true('theme' in settings, "Custom setting in get_all()")
        
        self.teardown()
    
    # =========================================================================
    # Scenario 4: User Sets Invalid Project Root
    # =========================================================================
    def test_scenario_invalid_project_root(self):
        """
        Scenario: User enters a non-existent path for project root
        Expected: Validation should fail
        """
        print_scenario("User Sets Invalid Project Root")
        
        service = self.setup()
        
        print_step("User enters a non-existent path")
        errors = service.validate_project_root('/path/that/does/not/exist')
        
        print_step("App should show error message")
        self.assert_true(len(errors) > 0, "Invalid path rejected")
        self.assert_true('project_root' in errors, "Error message for project_root")
        
        self.teardown()
    
    # =========================================================================
    # Scenario 5: User Validates Empty Path
    # =========================================================================
    def test_scenario_validate_empty_path(self):
        """
        Scenario: User tries to set empty project root
        Expected: Validation should fail with clear message
        """
        print_scenario("User Validates Empty Path")
        
        service = self.setup()
        
        print_step("User clears the project root field")
        errors = service.validate_project_root('')
        
        print_step("App should show required field error")
        self.assert_true(len(errors) > 0, "Empty path rejected")
        self.assert_true('required' in errors.get('project_root', '').lower(), "Error mentions 'required'")
        
        self.teardown()
    
    # =========================================================================
    # Scenario 6: Settings Persist Across Restarts
    # =========================================================================
    def test_scenario_persistence(self):
        """
        Scenario: User changes settings and restarts app
        Expected: Settings should persist
        """
        print_scenario("Settings Persist Across Restarts")
        
        service = self.setup()
        db_path = os.path.join(self.temp_dir, 'test_settings.db')
        
        print_step("User changes multiple settings")
        service.set('project_root', '/custom/path')
        service.set('refresh_interval', '10000')
        
        print_step("User restarts the app (new service instance)")
        new_service = SettingsService(db_path)
        
        print_step("Checking settings persisted")
        self.assert_equal(new_service.get('project_root'), '/custom/path', "project_root persisted")
        self.assert_equal(new_service.get('refresh_interval'), '10000', "refresh_interval persisted")
        
        self.teardown()
    
    def run_all(self):
        """Run all human simulation tests."""
        print("\n" + "=" * 60)
        print("  FEATURE-006: Settings & Configuration")
        print("  Human Simulation Tests")
        print("=" * 60)
        
        self.test_scenario_first_time_user()
        self.test_scenario_change_project_root()
        self.test_scenario_add_custom_setting()
        self.test_scenario_invalid_project_root()
        self.test_scenario_validate_empty_path()
        self.test_scenario_persistence()
        
        print("\n" + "=" * 60)
        print(f"  Results: {Colors.GREEN}{self.passed} passed{Colors.RESET}, "
              f"{Colors.RED}{self.failed} failed{Colors.RESET}")
        print("=" * 60 + "\n")
        
        return self.failed == 0


if __name__ == '__main__':
    tests = SettingsPlaygroundTests()
    success = tests.run_all()
    sys.exit(0 if success else 1)
