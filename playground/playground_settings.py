#!/usr/bin/env python3
"""
Playground: Settings & Configuration (FEATURE-006)

Interactive demonstration of the Settings service and API.

Usage:
    uv run python playground/playground_settings.py

This playground demonstrates:
1. SettingsService initialization and SQLite persistence
2. Getting default settings
3. Updating settings with validation
4. Resetting to defaults
5. Validating project_root paths
"""
import os
import sys
import json
import tempfile
import argparse

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from x_ipe.services import SettingsService


def print_header(text: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_settings(settings: dict, title: str = "Current Settings"):
    """Pretty print settings dictionary."""
    print(f"\n📋 {title}:")
    print("-" * 40)
    for key, value in settings.items():
        print(f"  {key}: {value}")
    print("-" * 40)


def demo_basic_operations(service: SettingsService):
    """Demonstrate basic CRUD operations."""
    print_header("Basic Settings Operations")
    
    # 1. Get all settings
    print("\n1️⃣ Getting all settings...")
    settings = service.get_all()
    print_settings(settings, "All Settings")
    
    # 2. Get single setting
    print("\n2️⃣ Getting single setting 'project_root'...")
    project_root_val = service.get('project_root')
    print(f"   project_root = {project_root_val}")
    
    # 3. Set a new value
    print("\n3️⃣ Setting project_root to current project...")
    service.set('project_root', project_root)
    updated = service.get('project_root')
    print(f"   ✅ project_root = {updated}")
    
    # 4. Get non-existent key with default
    print("\n4️⃣ Getting non-existent key with default...")
    theme = service.get('theme', 'light')
    print(f"   theme (default) = {theme}")


def demo_path_validation(service: SettingsService):
    """Demonstrate project_root path validation."""
    print_header("Project Root Path Validation")
    
    # 1. Valid path (project root)
    print("\n1️⃣ Validating valid path (project root)...")
    errors = service.validate_project_root(project_root)
    if not errors:
        print(f"   ✅ Valid: {project_root}")
        service.set('project_root', project_root)
    else:
        print(f"   ❌ Error: {errors.get('project_root')}")
    
    # 2. Invalid path (non-existent)
    print("\n2️⃣ Validating invalid path (non-existent)...")
    errors = service.validate_project_root('/nonexistent/path')
    if not errors:
        print("   ✅ Accepted (unexpected)")
    else:
        print(f"   ❌ Rejected: {errors.get('project_root')}")
    
    # 3. Invalid path (empty)
    print("\n3️⃣ Validating empty path...")
    errors = service.validate_project_root('')
    if not errors:
        print("   ✅ Accepted (unexpected)")
    else:
        print(f"   ❌ Rejected: {errors.get('project_root')}")
    
    # 4. Check current setting
    current = service.get('project_root')
    print(f"\n   Current project_root: {current}")


def demo_reset_settings(service: SettingsService):
    """Demonstrate resetting to defaults."""
    print_header("Reset to Defaults")
    
    # 1. Make some changes
    print("\n1️⃣ Making changes to settings...")
    service.set('project_root', '/some/custom/path')
    service.set('custom_key', 'custom_value')
    
    settings = service.get_all()
    print_settings(settings, "Modified Settings")
    
    # 2. Show that defaults are still accessible
    print("\n2️⃣ Default settings (reference):")
    print(f"   project_root default = {SettingsService.DEFAULT_SETTINGS.get('project_root')}")
    
    # Note: SettingsService doesn't have a reset method, so we demonstrate
    # that you can manually reset by setting back to defaults
    print("\n3️⃣ Manually resetting project_root to default...")
    default_root = SettingsService.DEFAULT_SETTINGS.get('project_root', '.')
    service.set('project_root', default_root)
    print(f"   ✅ project_root = {service.get('project_root')}")


def demo_persistence(db_path: str):
    """Demonstrate persistence across service instances."""
    print_header("Persistence Demo")
    
    # 1. Create first instance and set values
    print("\n1️⃣ Creating first SettingsService instance...")
    service1 = SettingsService(db_path)
    service1.set('project_root', '/demo/project/path')
    service1.set('custom_setting', 'test_value')
    print("   Set project_root='/demo/project/path', custom_setting='test_value'")
    
    # 2. Create second instance (simulating app restart)
    print("\n2️⃣ Creating NEW SettingsService instance (simulating restart)...")
    service2 = SettingsService(db_path)
    settings = service2.get_all()
    print_settings(settings, "Settings from New Instance")
    
    # 3. Verify persistence
    print("\n3️⃣ Verifying persistence...")
    pr = service2.get('project_root')
    cs = service2.get('custom_setting')
    if pr == '/demo/project/path' and cs == 'test_value':
        print("   ✅ Settings persisted correctly!")
    else:
        print("   ❌ Settings did NOT persist!")


def interactive_mode(service: SettingsService):
    """Interactive CLI for testing settings."""
    print_header("Interactive Settings Mode")
    print("""
Commands:
  get              - Show all settings
  get <key>        - Show single setting
  set <key> <val>  - Update a setting
  validate <path>  - Validate a project root path
  help             - Show this help
  quit / exit      - Exit interactive mode
""")
    
    while True:
        try:
            command = input("\n📝 Enter command: ").strip()
            if not command:
                continue
            
            parts = command.split(maxsplit=2)
            cmd = parts[0].lower()
            
            if cmd in ('quit', 'exit', 'q'):
                print("👋 Goodbye!")
                break
            
            elif cmd == 'help':
                print("Commands: get, get <key>, set <key> <value>, validate <path>, quit")
            
            elif cmd == 'get':
                if len(parts) == 1:
                    settings = service.get_all()
                    print_settings(settings)
                else:
                    key = parts[1]
                    value = service.get(key)
                    if value is None:
                        print(f"   ❌ Unknown key: {key}")
                    else:
                        print(f"   {key} = {value}")
            
            elif cmd == 'set':
                if len(parts) < 3:
                    print("   Usage: set <key> <value>")
                else:
                    key = parts[1]
                    value = parts[2]
                    service.set(key, value)
                    print(f"   ✅ {key} = {value}")
            
            elif cmd == 'validate':
                if len(parts) < 2:
                    print("   Usage: validate <path>")
                else:
                    path = parts[1]
                    errors = service.validate_project_root(path)
                    if errors:
                        print(f"   ❌ {errors.get('project_root')}")
                    else:
                        print(f"   ✅ Valid path: {path}")
            
            else:
                print(f"   Unknown command: {cmd}")
                print("   Type 'help' for available commands")
                
        except KeyboardInterrupt:
            print("\n👋 Interrupted. Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break


def main():
    parser = argparse.ArgumentParser(description='Settings & Configuration Playground')
    parser.add_argument('--demo', action='store_true', help='Run automated demo')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    args = parser.parse_args()
    
    print("\n" + "🎮" * 30)
    print("  FEATURE-006: Settings & Configuration Playground")
    print("🎮" * 30)
    
    # Create temp database for playground
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'playground_settings.db')
        service = SettingsService(db_path)
        
        if args.interactive:
            interactive_mode(service)
        elif args.demo or not (args.interactive):
            # Run all demos
            demo_basic_operations(service)
            demo_path_validation(service)
            demo_reset_settings(service)
            demo_persistence(db_path)
            
            print_header("Demo Complete!")
            print("\n✅ All demonstrations completed successfully.")
            print("💡 Try interactive mode with: --interactive or -i")
            print()


if __name__ == '__main__':
    main()
