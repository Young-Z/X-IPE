"""
Human Simulation Tests: Ideation Toolbox (CR-003)

These tests simulate human interactions with the Ideation Toolbox feature.
Run with: uv run python playground/tests/test_playground_ideation_toolbox.py
"""

import os
import sys
import json
import tempfile
import shutil
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestIdeationToolboxHumanScenarios(unittest.TestCase):
    """Human simulation tests for CR-003: Ideation Toolbox"""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp(prefix='toolbox_human_')
        self.ideas_dir = Path(self.temp_dir) / 'docs' / 'ideas'
        self.ideas_dir.mkdir(parents=True, exist_ok=True)
        
        from x_ipe.services import IdeasService
        self.service = IdeasService(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_human_opens_toolbox_first_time(self):
        """
        Scenario: Human opens Ideation Toolbox for the first time
        
        Steps:
        1. Human clicks "Ideation Toolbox" button
        2. Dropdown opens showing 3 sections
        3. Default checkboxes are: mermaid ✓, frontend-design ✓
        
        Expected:
        - mermaid is checked (True)
        - frontend-design is checked (True)
        - antv-infographic is unchecked (False)
        """
        config = self.service.get_toolbox()
        
        # Verify defaults match AC-29
        self.assertTrue(config['ideation']['mermaid'], "mermaid should be checked by default")
        self.assertTrue(config['mockup']['frontend-design'], "frontend-design should be checked by default")
        self.assertFalse(config['ideation']['antv-infographic'], "antv-infographic should be unchecked by default")
    
    def test_human_enables_antv_infographic(self):
        """
        Scenario: Human enables AntV Infographic tool
        
        Steps:
        1. Human opens toolbox
        2. Human clicks checkbox for "AntV Infographic"
        3. Checkbox becomes checked
        4. Configuration saves automatically
        
        Expected:
        - antv-infographic becomes True
        - Other settings remain unchanged
        """
        # Get defaults
        config = self.service.get_toolbox()
        
        # Human clicks checkbox
        config['ideation']['antv-infographic'] = True
        result = self.service.save_toolbox(config)
        
        self.assertTrue(result['success'])
        
        # Verify persistence
        reloaded = self.service.get_toolbox()
        self.assertTrue(reloaded['ideation']['antv-infographic'])
        self.assertTrue(reloaded['ideation']['mermaid'], "mermaid should remain checked")
    
    def test_human_disables_mermaid(self):
        """
        Scenario: Human disables Mermaid diagrams
        
        Steps:
        1. Human opens toolbox (mermaid is checked)
        2. Human unchecks "Mermaid Diagrams"
        3. Configuration saves automatically
        
        Expected:
        - mermaid becomes False
        - .ideation-tools.json is updated
        """
        config = self.service.get_toolbox()
        self.assertTrue(config['ideation']['mermaid'])  # Was checked
        
        # Human unchecks
        config['ideation']['mermaid'] = False
        self.service.save_toolbox(config)
        
        # Verify file was updated
        toolbox_path = self.ideas_dir / '.ideation-tools.json'
        self.assertTrue(toolbox_path.exists())
        
        saved = json.loads(toolbox_path.read_text())
        self.assertFalse(saved['ideation']['mermaid'])
    
    def test_human_toggles_multiple_options(self):
        """
        Scenario: Human toggles multiple checkboxes
        
        Steps:
        1. Human enables antv-infographic
        2. Human disables frontend-design
        3. Both changes persist
        
        Expected:
        - Both changes saved correctly
        - Config file reflects all changes
        """
        config = self.service.get_toolbox()
        
        # Toggle both
        config['ideation']['antv-infographic'] = True
        config['mockup']['frontend-design'] = False
        self.service.save_toolbox(config)
        
        # Verify
        reloaded = self.service.get_toolbox()
        self.assertTrue(reloaded['ideation']['antv-infographic'])
        self.assertFalse(reloaded['mockup']['frontend-design'])
    
    def test_human_closes_and_reopens_toolbox(self):
        """
        Scenario: Human makes changes, closes toolbox, reopens
        
        Steps:
        1. Human enables antv-infographic
        2. Human closes toolbox (clicks outside)
        3. Human reopens toolbox
        4. Changes are still visible
        
        Expected:
        - State persists across open/close
        """
        # Make change
        config = self.service.get_toolbox()
        config['ideation']['antv-infographic'] = True
        self.service.save_toolbox(config)
        
        # Simulate close and reopen (new service instance)
        from x_ipe.services import IdeasService
        new_service = IdeasService(self.temp_dir)
        reloaded = new_service.get_toolbox()
        
        self.assertTrue(reloaded['ideation']['antv-infographic'])
    
    def test_human_creates_idea_and_toolbox_config_exists(self):
        """
        Scenario: Human creates new idea after configuring toolbox
        
        Steps:
        1. Human configures toolbox
        2. Human creates new idea (upload/compose)
        3. .ideation-tools.json exists in x-ipe-docs/ideas/
        
        Expected:
        - Config file persists after idea creation
        """
        # Configure toolbox
        config = {
            "version": "1.0",
            "ideation": {"antv-infographic": True, "mermaid": True},
            "mockup": {"frontend-design": False},
            "sharing": {}
        }
        self.service.save_toolbox(config)
        
        # Create idea (simulated by creating folder)
        idea_folder = self.ideas_dir / 'Draft Idea - 01232026 143000'
        idea_folder.mkdir()
        (idea_folder / 'notes.md').write_text('# My Idea')
        
        # Verify toolbox config still exists
        toolbox_path = self.ideas_dir / '.ideation-tools.json'
        self.assertTrue(toolbox_path.exists())
        
        saved = json.loads(toolbox_path.read_text())
        self.assertTrue(saved['ideation']['antv-infographic'])
    
    def test_sharing_section_shows_placeholder(self):
        """
        Scenario: Human views Sharing section
        
        Steps:
        1. Human opens toolbox
        2. Human views Sharing section
        
        Expected:
        - Sharing section is empty (placeholder)
        - No checkboxes in sharing section
        """
        config = self.service.get_toolbox()
        
        # Sharing should be empty object
        self.assertEqual(config['sharing'], {})


def main():
    """Run tests with verbose output."""
    print("="*60)
    print("Human Simulation Tests: Ideation Toolbox (CR-003)")
    print("="*60)
    print()
    
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestIdeationToolboxHumanScenarios)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print()
    print("="*60)
    print("Summary")
    print("="*60)
    
    total = result.testsRun
    failures = len(result.failures) + len(result.errors)
    passed = total - failures
    
    print(f"Total: {total} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failures}")
    
    if failures == 0:
        print("\n🎉 All human scenario tests passed!")
    else:
        print("\n⚠️ Some tests failed!")
    
    return failures == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
