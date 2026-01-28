#!/usr/bin/env python3
"""
Playground: Ideation Toolbox (CR-003)

Interactive demonstration of the Ideation Toolbox feature:
- GET /api/ideas/toolbox - Load configuration
- POST /api/ideas/toolbox - Save configuration
- Default values: mermaid=True, frontend-design=True
- Configuration persists to .ideation-tools.json

Usage:
    # Demo mode - run all scenarios
    uv run python playground/playground_ideation_toolbox.py --demo
    
    # Interactive mode - manual testing
    uv run python playground/playground_ideation_toolbox.py
"""

import os
import sys
import json
import argparse
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def create_test_environment():
    """Create a temporary test environment."""
    temp_dir = tempfile.mkdtemp(prefix='toolbox_test_')
    ideas_dir = Path(temp_dir) / 'docs' / 'ideas'
    ideas_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def cleanup_test_environment(temp_dir):
    """Clean up test environment."""
    shutil.rmtree(temp_dir, ignore_errors=True)


def demo_get_defaults(service):
    """Demo: Get default toolbox configuration."""
    print("\n" + "="*60)
    print("Demo 1: Get Default Toolbox Configuration")
    print("="*60)
    
    config = service.get_toolbox()
    
    print(f"Version: {config.get('version')}")
    print(f"Ideation:")
    print(f"  - antv-infographic: {config['ideation'].get('antv-infographic', False)}")
    print(f"  - mermaid: {config['ideation'].get('mermaid', True)}")
    print(f"Mockup:")
    print(f"  - frontend-design: {config['mockup'].get('frontend-design', True)}")
    print(f"Sharing: {config.get('sharing', {})}")
    
    # Verify defaults
    assert config['ideation']['mermaid'] is True, "mermaid should be True by default"
    assert config['mockup']['frontend-design'] is True, "frontend-design should be True by default"
    assert config['ideation']['antv-infographic'] is False, "antv-infographic should be False by default"
    
    print("\n✅ Default configuration loaded correctly!")
    return True


def demo_save_config(service, temp_dir):
    """Demo: Save custom toolbox configuration."""
    print("\n" + "="*60)
    print("Demo 2: Save Custom Toolbox Configuration")
    print("="*60)
    
    # New configuration
    custom_config = {
        "version": "1.0",
        "ideation": {
            "antv-infographic": True,
            "mermaid": False
        },
        "mockup": {
            "frontend-design": True
        },
        "sharing": {}
    }
    
    print(f"Saving configuration:")
    print(f"  antv-infographic: True (changed)")
    print(f"  mermaid: False (changed)")
    print(f"  frontend-design: True")
    
    result = service.save_toolbox(custom_config)
    
    if result['success']:
        print("\n✅ Configuration saved successfully!")
        
        # Verify file exists
        toolbox_path = Path(temp_dir) / 'docs' / 'ideas' / '.ideation-tools.json'
        if toolbox_path.exists():
            print(f"✅ File created at: {toolbox_path}")
            saved_content = json.loads(toolbox_path.read_text())
            print(f"✅ File content: {json.dumps(saved_content, indent=2)}")
        return True
    else:
        print(f"\n❌ Failed to save: {result.get('error')}")
        return False


def demo_load_saved(service):
    """Demo: Load previously saved configuration."""
    print("\n" + "="*60)
    print("Demo 3: Load Saved Configuration")
    print("="*60)
    
    config = service.get_toolbox()
    
    print(f"Loaded configuration:")
    print(f"  antv-infographic: {config['ideation'].get('antv-infographic')}")
    print(f"  mermaid: {config['ideation'].get('mermaid')}")
    print(f"  frontend-design: {config['mockup'].get('frontend-design')}")
    
    # Verify saved values
    if config['ideation']['antv-infographic'] is True and config['ideation']['mermaid'] is False:
        print("\n✅ Saved configuration loaded correctly!")
        return True
    else:
        print("\n❌ Configuration did not match saved values!")
        return False


def demo_update_config(service):
    """Demo: Update configuration (toggle checkboxes)."""
    print("\n" + "="*60)
    print("Demo 4: Toggle Checkbox (Update Configuration)")
    print("="*60)
    
    # Get current config
    config = service.get_toolbox()
    print(f"Current mermaid value: {config['ideation']['mermaid']}")
    
    # Toggle mermaid
    config['ideation']['mermaid'] = not config['ideation']['mermaid']
    print(f"Toggling mermaid to: {config['ideation']['mermaid']}")
    
    result = service.save_toolbox(config)
    
    if result['success']:
        # Verify the change
        new_config = service.get_toolbox()
        if new_config['ideation']['mermaid'] == config['ideation']['mermaid']:
            print("\n✅ Checkbox toggle saved correctly!")
            return True
    
    print("\n❌ Failed to update configuration!")
    return False


def run_demo():
    """Run all demo scenarios."""
    from x_ipe.services import IdeasService
    
    print("="*60)
    print("CR-003: Ideation Toolbox Demo")
    print("="*60)
    
    # Create test environment
    temp_dir = create_test_environment()
    print(f"\nTest environment: {temp_dir}")
    
    try:
        service = IdeasService(temp_dir)
        
        results = []
        results.append(("Get Defaults", demo_get_defaults(service)))
        results.append(("Save Config", demo_save_config(service, temp_dir)))
        results.append(("Load Saved", demo_load_saved(service)))
        results.append(("Update Config", demo_update_config(service)))
        
        # Summary
        print("\n" + "="*60)
        print("Demo Summary")
        print("="*60)
        
        all_passed = True
        for name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {name}: {status}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🎉 All demos passed!")
        else:
            print("\n⚠️ Some demos failed!")
        
        return all_passed
    
    finally:
        cleanup_test_environment(temp_dir)


def run_interactive():
    """Run interactive mode."""
    from x_ipe.services import IdeasService
    
    print("="*60)
    print("CR-003: Ideation Toolbox - Interactive Mode")
    print("="*60)
    
    # Use current project root
    project_root = Path(__file__).parent.parent
    service = IdeasService(str(project_root))
    
    while True:
        print("\nOptions:")
        print("  1. Load current configuration")
        print("  2. Toggle antv-infographic")
        print("  3. Toggle mermaid")
        print("  4. Toggle frontend-design")
        print("  5. Show JSON file path")
        print("  q. Quit")
        
        choice = input("\nChoice: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == '1':
            config = service.get_toolbox()
            print("\nCurrent configuration:")
            print(json.dumps(config, indent=2))
        elif choice in ['2', '3', '4']:
            config = service.get_toolbox()
            
            if choice == '2':
                key = 'antv-infographic'
                section = 'ideation'
            elif choice == '3':
                key = 'mermaid'
                section = 'ideation'
            else:
                key = 'frontend-design'
                section = 'mockup'
            
            current = config[section].get(key, False)
            config[section][key] = not current
            
            result = service.save_toolbox(config)
            if result['success']:
                print(f"\n✅ {key}: {current} → {not current}")
            else:
                print(f"\n❌ Failed: {result.get('error')}")
        elif choice == '5':
            path = project_root / 'docs' / 'ideas' / '.ideation-tools.json'
            print(f"\nJSON file path: {path}")
            if path.exists():
                print("File exists: ✅")
            else:
                print("File exists: ❌ (will be created on first save)")
    
    print("\nGoodbye!")


def main():
    parser = argparse.ArgumentParser(description='Ideation Toolbox Playground')
    parser.add_argument('--demo', action='store_true', help='Run demo mode')
    args = parser.parse_args()
    
    if args.demo:
        success = run_demo()
        sys.exit(0 if success else 1)
    else:
        run_interactive()


if __name__ == '__main__':
    main()
