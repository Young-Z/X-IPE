"""
Test Architecture DSL Canvas Renderer

This script tests the Canvas renderer by:
1. Loading the demo page (using file:// protocol)
2. Verifying the DSL parses correctly  
3. Checking the canvas renders
4. Taking a screenshot for visual verification
"""
from playwright.sync_api import sync_playwright
import time
import os

def test_architecture_canvas_renderer():
    # Get absolute path to the demo file
    demo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'architecture-canvas-demo.html'))
    demo_url = f'file://{demo_path}'
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Capture console logs
        logs = []
        page.on('console', lambda msg: logs.append(f"{msg.type}: {msg.text}"))
        
        # Load the demo page
        print(f"Loading demo page: {demo_url}")
        page.goto(demo_url)
        page.wait_for_load_state('domcontentloaded')
        
        # Wait for rendering to complete
        time.sleep(2)
        
        # Check for any errors
        errors = [log for log in logs if 'error' in log.lower()]
        if errors:
            print("❌ Console Errors:")
            for err in errors:
                print(f"  {err}")
        else:
            print("✓ No console errors")
        
        # Check if canvas exists and has content
        canvas = page.locator('#diagram-canvas')
        if canvas.count() > 0:
            print("✓ Canvas element found")
            
            # Get canvas dimensions
            dimensions = page.evaluate('''() => {
                const canvas = document.getElementById('diagram-canvas');
                return {
                    width: canvas.width,
                    height: canvas.height,
                    styleWidth: canvas.style.width,
                    styleHeight: canvas.style.height
                };
            }''')
            print(f"  Canvas size: {dimensions['width']}x{dimensions['height']} (style: {dimensions['styleWidth']}x{dimensions['styleHeight']})")
            
            # Check if canvas has actual rendered content (non-empty)
            has_content = page.evaluate('''() => {
                const canvas = document.getElementById('diagram-canvas');
                const ctx = canvas.getContext('2d');
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                // Check if any pixel is non-transparent
                for (let i = 3; i < imageData.data.length; i += 4) {
                    if (imageData.data[i] > 0) return true;
                }
                return false;
            }''')
            
            if has_content:
                print("✓ Canvas has rendered content")
            else:
                print("❌ Canvas appears empty")
        else:
            print("❌ Canvas element not found")
        
        # Check status text
        status = page.locator('#status')
        if status.count() > 0:
            status_text = status.text_content()
            print(f"  Status: {status_text}")
        
        # Take screenshot for visual verification
        screenshot_path = '/tmp/architecture-canvas-test.png'
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n📸 Screenshot saved to: {screenshot_path}")
        
        # Print all console logs
        if logs:
            print("\n📋 Console Logs:")
            for log in logs:
                print(f"  {log}")
        
        browser.close()
        
        return len(errors) == 0 and has_content

if __name__ == '__main__':
    success = test_architecture_canvas_renderer()
    exit(0 if success else 1)
