#!/usr/bin/env python3
"""
FEATURE-006 v2.0: Multi-Project Folder Support - Interactive Playground

This playground demonstrates the ProjectFoldersService functionality:
- List all project folders
- Add new project folders
- Update existing project folders
- Delete project folders
- Switch active project

Usage:
    # Demo mode (no user input required):
    python playground/playground_project_folders.py --demo
    
    # Interactive mode:
    python playground/playground_project_folders.py
"""
import os
import sys
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_service():
    """Get ProjectFoldersService with temporary database."""
    from x_ipe.services import ProjectFoldersService
    
    # Use temp database for playground
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'playground_projects.db')
    return ProjectFoldersService(db_path), temp_dir


def demo_list_projects():
    """Demo: List all project folders."""
    print("\n" + "=" * 60)
    print("DEMO: List All Project Folders")
    print("=" * 60)
    
    service, temp_dir = get_service()
    
    try:
        # Get all projects
        projects = service.get_all()
        
        print(f"\nFound {len(projects)} project folder(s):")
        for p in projects:
            print(f"  [{p['id']}] {p['name']} -> {p['path']}")
        
        # Get active project
        active_id = service.get_active_id()
        print(f"\nActive project ID: {active_id}")
        
        print("\n✅ List projects demo complete")
        return True
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def demo_add_project():
    """Demo: Add a new project folder."""
    print("\n" + "=" * 60)
    print("DEMO: Add New Project Folder")
    print("=" * 60)
    
    service, temp_dir = get_service()
    
    try:
        # Create a test directory
        test_project = os.path.join(temp_dir, 'my_project')
        os.makedirs(test_project)
        
        print(f"\n1. Creating test directory: {test_project}")
        
        # Add the project
        result = service.add('My New Project', test_project)
        
        if result['success']:
            project = result['project']
            print(f"\n2. Added project successfully:")
            print(f"   ID: {project['id']}")
            print(f"   Name: {project['name']}")
            print(f"   Path: {project['path']}")
        else:
            print(f"\n❌ Failed to add: {result.get('errors', result.get('error'))}")
            return False
        
        # Verify it appears in list
        projects = service.get_all()
        print(f"\n3. Project list now has {len(projects)} project(s)")
        
        print("\n✅ Add project demo complete")
        return True
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def demo_update_project():
    """Demo: Update an existing project folder."""
    print("\n" + "=" * 60)
    print("DEMO: Update Existing Project Folder")
    print("=" * 60)
    
    service, temp_dir = get_service()
    
    try:
        # Create test directories
        old_path = os.path.join(temp_dir, 'old_project')
        new_path = os.path.join(temp_dir, 'new_project')
        os.makedirs(old_path)
        os.makedirs(new_path)
        
        # Add a project
        result = service.add('Original Name', old_path)
        project_id = result['project']['id']
        print(f"\n1. Created project [{project_id}]: 'Original Name' -> {old_path}")
        
        # Update the name
        result = service.update(project_id, name='Updated Name')
        if result['success']:
            print(f"\n2. Updated name to: '{result['project']['name']}'")
        
        # Update the path
        result = service.update(project_id, path=new_path)
        if result['success']:
            print(f"\n3. Updated path to: {result['project']['path']}")
        
        # Update both
        result = service.update(project_id, name='Final Name', path=old_path)
        if result['success']:
            print(f"\n4. Updated both: '{result['project']['name']}' -> {result['project']['path']}")
        
        print("\n✅ Update project demo complete")
        return True
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def demo_delete_project():
    """Demo: Delete a project folder."""
    print("\n" + "=" * 60)
    print("DEMO: Delete Project Folder")
    print("=" * 60)
    
    service, temp_dir = get_service()
    
    try:
        # Create test directory
        test_path = os.path.join(temp_dir, 'to_delete')
        os.makedirs(test_path)
        
        # Add a project
        result = service.add('To Be Deleted', test_path)
        project_id = result['project']['id']
        
        print(f"\n1. Created project [{project_id}]: 'To Be Deleted'")
        print(f"   Current projects: {len(service.get_all())}")
        
        # Delete it
        result = service.delete(project_id)
        
        if result['success']:
            print(f"\n2. Deleted project [{project_id}]")
            print(f"   Current projects: {len(service.get_all())}")
        else:
            print(f"\n❌ Delete failed: {result.get('error')}")
        
        # Try to delete the last project (should fail)
        default_project = service.get_all()[0]
        result = service.delete(default_project['id'])
        
        if not result['success']:
            print(f"\n3. Cannot delete last project: {result['error']}")
        
        print("\n✅ Delete project demo complete")
        return True
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def demo_switch_project():
    """Demo: Switch active project."""
    print("\n" + "=" * 60)
    print("DEMO: Switch Active Project")
    print("=" * 60)
    
    service, temp_dir = get_service()
    
    try:
        # Create test directories
        project_a = os.path.join(temp_dir, 'project_a')
        project_b = os.path.join(temp_dir, 'project_b')
        os.makedirs(project_a)
        os.makedirs(project_b)
        
        # Add projects
        result_a = service.add('Project Alpha', project_a)
        result_b = service.add('Project Beta', project_b)
        
        id_a = result_a['project']['id']
        id_b = result_b['project']['id']
        
        print(f"\n1. Created projects:")
        print(f"   [{id_a}] Project Alpha")
        print(f"   [{id_b}] Project Beta")
        print(f"   Active: {service.get_active_id()}")
        
        # Switch to Project Alpha
        result = service.set_active(id_a)
        if result['success']:
            print(f"\n2. Switched to: {result['project']['name']}")
            print(f"   Active ID: {result['active_project_id']}")
        
        # Switch to Project Beta
        result = service.set_active(id_b)
        if result['success']:
            print(f"\n3. Switched to: {result['project']['name']}")
            print(f"   Active ID: {result['active_project_id']}")
        
        # Verify persistence
        print(f"\n4. Verifying active project persists: {service.get_active_id()}")
        
        print("\n✅ Switch project demo complete")
        return True
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def demo_validation():
    """Demo: Validation error handling."""
    print("\n" + "=" * 60)
    print("DEMO: Validation Error Handling")
    print("=" * 60)
    
    service, temp_dir = get_service()
    
    try:
        test_path = os.path.join(temp_dir, 'valid_project')
        os.makedirs(test_path)
        
        print("\n1. Testing empty name:")
        result = service.add('', test_path)
        if not result['success']:
            print(f"   ❌ Error: {result['errors'].get('name')}")
        
        print("\n2. Testing empty path:")
        result = service.add('Valid Name', '')
        if not result['success']:
            print(f"   ❌ Error: {result['errors'].get('path')}")
        
        print("\n3. Testing non-existent path:")
        result = service.add('Bad Path', '/nonexistent/path/xyz')
        if not result['success']:
            print(f"   ❌ Error: {result['errors'].get('path')}")
        
        print("\n4. Testing duplicate name:")
        service.add('Unique Name', test_path)
        result = service.add('Unique Name', test_path)
        if not result['success']:
            print(f"   ❌ Error: {result['errors'].get('name')}")
        
        print("\n5. Testing switch to invalid ID:")
        result = service.set_active(99999)
        if not result['success']:
            print(f"   ❌ Error: {result.get('error')}")
        
        print("\n✅ Validation demo complete")
        return True
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_demo():
    """Run all demos in sequence."""
    print("\n" + "=" * 60)
    print("FEATURE-006 v2.0: Multi-Project Folder Support")
    print("Interactive Playground - DEMO MODE")
    print("=" * 60)
    
    demos = [
        demo_list_projects,
        demo_add_project,
        demo_update_project,
        demo_delete_project,
        demo_switch_project,
        demo_validation,
    ]
    
    passed = 0
    for demo in demos:
        try:
            if demo():
                passed += 1
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"DEMO COMPLETE: {passed}/{len(demos)} demos passed")
    print("=" * 60)
    
    return passed == len(demos)


def interactive_mode():
    """Interactive menu for testing ProjectFoldersService."""
    service, temp_dir = get_service()
    
    print("\n" + "=" * 60)
    print("FEATURE-006 v2.0: Multi-Project Folder Support")
    print("Interactive Mode")
    print("=" * 60)
    print(f"\nUsing temp database in: {temp_dir}")
    
    try:
        while True:
            print("\n--- Menu ---")
            print("1. List all projects")
            print("2. Add new project")
            print("3. Update project")
            print("4. Delete project")
            print("5. Switch active project")
            print("6. Show active project")
            print("q. Quit")
            
            choice = input("\nChoice: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == '1':
                projects = service.get_all()
                active_id = service.get_active_id()
                print(f"\nProjects ({len(projects)} total):")
                for p in projects:
                    marker = " ⭐" if p['id'] == active_id else ""
                    print(f"  [{p['id']}] {p['name']} -> {p['path']}{marker}")
                    
            elif choice == '2':
                name = input("Project name: ").strip()
                path = input("Project path: ").strip()
                result = service.add(name, path)
                if result['success']:
                    print(f"✅ Added: [{result['project']['id']}] {result['project']['name']}")
                else:
                    print(f"❌ Error: {result.get('errors', result.get('error'))}")
                    
            elif choice == '3':
                project_id = input("Project ID to update: ").strip()
                name = input("New name (empty to skip): ").strip() or None
                path = input("New path (empty to skip): ").strip() or None
                result = service.update(int(project_id), name=name, path=path)
                if result['success']:
                    print(f"✅ Updated: {result['project']}")
                else:
                    print(f"❌ Error: {result.get('errors', result.get('error'))}")
                    
            elif choice == '4':
                project_id = input("Project ID to delete: ").strip()
                result = service.delete(int(project_id), active_project_id=service.get_active_id())
                if result['success']:
                    print("✅ Deleted")
                else:
                    print(f"❌ Error: {result.get('error')}")
                    
            elif choice == '5':
                project_id = input("Project ID to switch to: ").strip()
                result = service.set_active(int(project_id))
                if result['success']:
                    print(f"✅ Switched to: {result['project']['name']}")
                else:
                    print(f"❌ Error: {result.get('error')}")
                    
            elif choice == '6':
                active_id = service.get_active_id()
                project = service.get_by_id(active_id)
                if project:
                    print(f"\nActive: [{project['id']}] {project['name']} -> {project['path']}")
                else:
                    print("No active project")
                    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("\nCleanup complete.")


if __name__ == '__main__':
    if '--demo' in sys.argv:
        success = run_demo()
        sys.exit(0 if success else 1)
    else:
        interactive_mode()
