#!/usr/bin/env python3
"""
Human Simulation Tests for FEATURE-008 v1.2: Upload to Existing Folders (CR-002)

These tests simulate human interaction scenarios to validate the user experience.
They are NOT unit tests - they validate behavior from a human perspective.

Run:
    uv run python playground/tests/test_playground_ideas_upload.py
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from x_ipe.services import IdeasService


class TestPlaygroundIdeasUpload:
    """Human simulation tests for upload to existing folders."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.temp_dir = tempfile.mkdtemp(prefix="test_ideas_upload_")
        self.ideas_path = Path(self.temp_dir) / 'docs' / 'ideas'
        self.ideas_path.mkdir(parents=True)
        
        # Create sample folders
        (self.ideas_path / 'project-alpha').mkdir()
        (self.ideas_path / 'project-alpha' / 'notes.md').write_text('# Alpha Notes')
        
        (self.ideas_path / 'project-beta').mkdir()
        (self.ideas_path / 'project-beta' / 'overview.md').write_text('# Beta Overview')
        
        self.service = IdeasService(self.temp_dir)
    
    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    # =========================================================================
    # Scenario 1: Human drags file onto existing folder
    # =========================================================================
    
    def test_scenario_1_drag_file_to_existing_folder(self):
        """
        Scenario: Human drags a file from desktop onto 'project-alpha' folder
        Expected: File appears in project-alpha folder
        """
        print("\n📋 Scenario 1: Drag file to existing folder")
        
        # Human drags 'design.md' onto 'project-alpha'
        files = [('design.md', b'# Design Document\n\nUI mockups here.')]
        result = self.service.upload(files, target_folder='project-alpha')
        
        # Verify success
        assert result['success'] is True, "Upload should succeed"
        assert result['folder_name'] == 'project-alpha', "Should use target folder"
        
        # Verify file exists
        file_path = self.ideas_path / 'project-alpha' / 'design.md'
        assert file_path.exists(), "File should exist in target folder"
        assert b'UI mockups' in file_path.read_bytes(), "Content should match"
        
        print("   ✅ File uploaded to existing folder successfully")
    
    def test_scenario_1b_multiple_files_drag(self):
        """
        Scenario: Human drags multiple files onto folder
        Expected: All files appear in folder
        """
        print("\n📋 Scenario 1b: Drag multiple files to folder")
        
        files = [
            ('file1.md', b'# File 1'),
            ('file2.txt', b'Content 2'),
            ('file3.py', b'print("hello")')
        ]
        result = self.service.upload(files, target_folder='project-alpha')
        
        assert result['success'] is True
        assert len(result['files_uploaded']) == 3
        
        for filename, _ in files:
            assert (self.ideas_path / 'project-alpha' / filename).exists()
        
        print("   ✅ All 3 files uploaded successfully")
    
    # =========================================================================
    # Scenario 2: Human drags file onto non-existent folder
    # =========================================================================
    
    def test_scenario_2_drag_to_nonexistent_folder(self):
        """
        Scenario: Human drags file onto folder that was deleted
        Expected: Error message shown, file not uploaded
        """
        print("\n📋 Scenario 2: Drag to non-existent folder")
        
        files = [('test.md', b'# Test')]
        result = self.service.upload(files, target_folder='deleted-folder')
        
        assert result['success'] is False, "Should fail"
        assert 'does not exist' in result['error'], "Should explain error"
        
        print(f"   ✅ Expected error shown: {result['error']}")
    
    # =========================================================================
    # Scenario 3: Human replaces existing file
    # =========================================================================
    
    def test_scenario_3_replace_existing_file(self):
        """
        Scenario: Human drags file with same name as existing file
        Expected: File is overwritten with new content
        """
        print("\n📋 Scenario 3: Replace existing file")
        
        # Verify original content
        original = self.ideas_path / 'project-alpha' / 'notes.md'
        assert original.read_text() == '# Alpha Notes'
        
        # Upload file with same name
        files = [('notes.md', b'# Updated Alpha Notes\n\nNew content here.')]
        result = self.service.upload(files, target_folder='project-alpha')
        
        assert result['success'] is True
        assert original.read_text() == '# Updated Alpha Notes\n\nNew content here.'
        
        print("   ✅ File overwritten with new content")
    
    # =========================================================================
    # Scenario 4: Human uses New Idea button (no target folder)
    # =========================================================================
    
    def test_scenario_4_new_idea_creates_new_folder(self):
        """
        Scenario: Human uses "New Idea" button (no target folder)
        Expected: New timestamped folder created
        """
        print("\n📋 Scenario 4: New Idea button (creates new folder)")
        
        files = [('idea.md', b'# Brand New Idea')]
        result = self.service.upload(files)  # No target_folder
        
        assert result['success'] is True
        assert result['folder_name'].startswith('Draft Idea - ')
        assert (self.ideas_path / result['folder_name'] / 'idea.md').exists()
        
        print(f"   ✅ New folder created: {result['folder_name']}")
    
    # =========================================================================
    # Scenario 5: Original files preserved after upload
    # =========================================================================
    
    def test_scenario_5_original_files_preserved(self):
        """
        Scenario: Human adds new file to folder with existing files
        Expected: Original files remain unchanged
        """
        print("\n📋 Scenario 5: Original files preserved")
        
        # Verify original file exists
        original = self.ideas_path / 'project-alpha' / 'notes.md'
        original_content = original.read_text()
        
        # Upload new file
        files = [('newfile.md', b'# New File')]
        result = self.service.upload(files, target_folder='project-alpha')
        
        assert result['success'] is True
        
        # Original file should be unchanged
        assert original.read_text() == original_content
        # New file should exist
        assert (self.ideas_path / 'project-alpha' / 'newfile.md').exists()
        
        print("   ✅ Original files preserved, new file added")
    
    # =========================================================================
    # Scenario 6: Binary file upload
    # =========================================================================
    
    def test_scenario_6_binary_file_upload(self):
        """
        Scenario: Human drags an image file onto folder
        Expected: Binary file uploaded correctly
        """
        print("\n📋 Scenario 6: Binary file (image) upload")
        
        # PNG file header
        png_content = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
        files = [('screenshot.png', png_content)]
        
        result = self.service.upload(files, target_folder='project-alpha')
        
        assert result['success'] is True
        
        uploaded_file = self.ideas_path / 'project-alpha' / 'screenshot.png'
        assert uploaded_file.read_bytes() == png_content
        
        print("   ✅ Binary file uploaded with correct content")


def run_tests():
    """Run all human simulation tests."""
    print("\n" + "="*60)
    print("  Human Simulation Tests: Upload to Existing Folders (CR-002)")
    print("="*60)
    
    test_instance = TestPlaygroundIdeasUpload()
    tests = [
        test_instance.test_scenario_1_drag_file_to_existing_folder,
        test_instance.test_scenario_1b_multiple_files_drag,
        test_instance.test_scenario_2_drag_to_nonexistent_folder,
        test_instance.test_scenario_3_replace_existing_file,
        test_instance.test_scenario_4_new_idea_creates_new_folder,
        test_instance.test_scenario_5_original_files_preserved,
        test_instance.test_scenario_6_binary_file_upload,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        test_instance.setup_method()
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"   ❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1
        finally:
            test_instance.teardown_method()
    
    print("\n" + "="*60)
    print(f"  Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
