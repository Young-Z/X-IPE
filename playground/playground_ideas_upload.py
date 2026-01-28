#!/usr/bin/env python3
"""
Playground for FEATURE-008 v1.2: Drag-Drop Upload to Existing Folders (CR-002)

This playground demonstrates the IdeasService.upload() method with target_folder
parameter, allowing files to be uploaded directly into existing idea folders.

Usage:
    # Demo mode (default) - shows all operations
    uv run python playground/playground_ideas_upload.py --demo

    # Interactive mode - menu-driven testing
    uv run python playground/playground_ideas_upload.py
"""

import sys
import os
import argparse
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from x_ipe.services import IdeasService


def create_test_environment():
    """Create a temporary project directory with sample ideas."""
    temp_dir = tempfile.mkdtemp(prefix="ideas_playground_")
    ideas_path = Path(temp_dir) / 'docs' / 'ideas'
    ideas_path.mkdir(parents=True)
    
    # Create sample idea folders
    idea1 = ideas_path / 'mobile-app-idea'
    idea1.mkdir()
    (idea1 / 'notes.md').write_text('# Mobile App Notes\n\nInitial brainstorming.')
    (idea1 / 'requirements.txt').write_text('- Feature A\n- Feature B')
    
    idea2 = ideas_path / 'web-platform-idea'
    idea2.mkdir()
    (idea2 / 'overview.md').write_text('# Web Platform\n\nPlatform concept.')
    
    return temp_dir


def cleanup_test_environment(temp_dir):
    """Clean up temporary directory."""
    shutil.rmtree(temp_dir, ignore_errors=True)


def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def print_tree(ideas_path, indent=0):
    """Print directory tree."""
    for item in sorted(ideas_path.iterdir()):
        prefix = "  " * indent
        if item.is_dir():
            print(f"{prefix}📁 {item.name}/")
            print_tree(item, indent + 1)
        else:
            print(f"{prefix}📄 {item.name}")


def demo_upload_to_existing_folder(service, ideas_path):
    """Demo: Upload files to an existing folder."""
    print_section("Demo: Upload to Existing Folder (CR-002)")
    
    print("\n📂 Before upload:")
    print_tree(ideas_path)
    
    # Upload new files to existing folder
    files = [
        ('extra-notes.md', b'# Extra Notes\n\nAdditional thoughts.'),
        ('diagram.txt', b'Box 1 --> Box 2 --> Box 3')
    ]
    
    print(f"\n📤 Uploading 2 files to 'mobile-app-idea'...")
    result = service.upload(files, target_folder='mobile-app-idea')
    
    if result['success']:
        print(f"✅ Success!")
        print(f"   Folder: {result['folder_name']}")
        print(f"   Files: {result['files_uploaded']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n📂 After upload:")
    print_tree(ideas_path)


def demo_upload_to_nonexistent_folder(service):
    """Demo: Attempt to upload to non-existent folder."""
    print_section("Demo: Upload to Non-Existent Folder (Error Case)")
    
    files = [('test.md', b'# Test')]
    
    print(f"\n📤 Attempting to upload to 'does-not-exist'...")
    result = service.upload(files, target_folder='does-not-exist')
    
    if result['success']:
        print(f"✅ Success (unexpected!)")
    else:
        print(f"❌ Expected error: {result['error']}")


def demo_upload_new_folder(service, ideas_path):
    """Demo: Upload without target_folder (creates new folder)."""
    print_section("Demo: Upload Without target_folder (New Folder)")
    
    files = [('new-idea.md', b'# Brand New Idea\n\nThis creates a new folder.')]
    
    print(f"\n📤 Uploading without target_folder...")
    result = service.upload(files)
    
    if result['success']:
        print(f"✅ Success!")
        print(f"   New folder: {result['folder_name']}")
        print(f"   Files: {result['files_uploaded']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n📂 Current ideas structure:")
    print_tree(ideas_path)


def demo_overwrite_file(service, ideas_path):
    """Demo: Upload file that overwrites existing file."""
    print_section("Demo: Overwrite Existing File")
    
    # Show original content
    original_file = ideas_path / 'mobile-app-idea' / 'notes.md'
    print(f"\n📄 Original content of notes.md:")
    print(f"   {original_file.read_text()[:50]}...")
    
    # Upload file with same name
    files = [('notes.md', b'# Updated Notes\n\nThis replaces the original.')]
    
    print(f"\n📤 Uploading 'notes.md' to 'mobile-app-idea' (overwrite)...")
    result = service.upload(files, target_folder='mobile-app-idea')
    
    if result['success']:
        print(f"✅ Success!")
        print(f"\n📄 New content of notes.md:")
        print(f"   {original_file.read_text()[:50]}...")
    else:
        print(f"❌ Error: {result['error']}")


def run_demo():
    """Run all demonstrations."""
    print("\n" + "="*60)
    print("  FEATURE-008 v1.2: Upload to Existing Folders (CR-002)")
    print("="*60)
    
    # Setup
    temp_dir = create_test_environment()
    ideas_path = Path(temp_dir) / 'docs' / 'ideas'
    service = IdeasService(temp_dir)
    
    try:
        # Run demos
        demo_upload_to_existing_folder(service, ideas_path)
        demo_upload_to_nonexistent_folder(service)
        demo_upload_new_folder(service, ideas_path)
        demo_overwrite_file(service, ideas_path)
        
        print_section("Demo Complete!")
        print("\n✅ All demonstrations completed successfully.")
        print(f"\nTemp directory: {temp_dir}")
        print("(Will be cleaned up on exit)")
        
    finally:
        cleanup_test_environment(temp_dir)


def interactive_mode():
    """Interactive menu for testing."""
    print("\n" + "="*60)
    print("  FEATURE-008 v1.2: Upload to Existing Folders (CR-002)")
    print("  Interactive Mode")
    print("="*60)
    
    temp_dir = create_test_environment()
    ideas_path = Path(temp_dir) / 'docs' / 'ideas'
    service = IdeasService(temp_dir)
    
    try:
        while True:
            print("\n" + "-"*40)
            print("Menu:")
            print("  1. List all ideas")
            print("  2. Upload to existing folder")
            print("  3. Upload to create new folder")
            print("  4. View folder contents")
            print("  5. Quit")
            print("-"*40)
            
            choice = input("Choice [1-5]: ").strip()
            
            if choice == '1':
                print("\n📂 Ideas:")
                print_tree(ideas_path)
                
            elif choice == '2':
                folder = input("Target folder name: ").strip()
                filename = input("Filename to upload: ").strip() or "test.md"
                content = input("Content (or press Enter for default): ").strip()
                content = content or f"# Test File\n\nUploaded to {folder}"
                
                result = service.upload([(filename, content.encode())], target_folder=folder)
                if result['success']:
                    print(f"✅ Uploaded to {result['folder_name']}")
                else:
                    print(f"❌ Error: {result['error']}")
                    
            elif choice == '3':
                filename = input("Filename to upload: ").strip() or "new-idea.md"
                content = input("Content (or press Enter for default): ").strip()
                content = content or "# New Idea\n\nCreated via playground."
                
                result = service.upload([(filename, content.encode())])
                if result['success']:
                    print(f"✅ Created folder: {result['folder_name']}")
                else:
                    print(f"❌ Error: {result['error']}")
                    
            elif choice == '4':
                folder = input("Folder name: ").strip()
                folder_path = ideas_path / folder
                if folder_path.exists():
                    print(f"\n📂 {folder}/")
                    for f in folder_path.iterdir():
                        if f.is_file():
                            print(f"  📄 {f.name} ({f.stat().st_size} bytes)")
                else:
                    print(f"❌ Folder '{folder}' not found")
                    
            elif choice == '5':
                print("\nGoodbye!")
                break
                
            else:
                print("Invalid choice. Please enter 1-5.")
                
    finally:
        cleanup_test_environment(temp_dir)


def main():
    parser = argparse.ArgumentParser(
        description='Playground for FEATURE-008 v1.2: Upload to Existing Folders'
    )
    parser.add_argument('--demo', action='store_true', 
                        help='Run in demo mode (default if no args)')
    
    args = parser.parse_args()
    
    # Default to demo mode if no arguments
    if args.demo or len(sys.argv) == 1:
        run_demo()
    else:
        interactive_mode()


if __name__ == '__main__':
    main()
