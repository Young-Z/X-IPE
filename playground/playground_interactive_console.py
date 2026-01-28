#!/usr/bin/env python3
"""
Playground: Interactive Console (FEATURE-005)

Interactive demonstration of the TerminalService for human testing.
This playground allows you to interact with the PTY-based terminal directly.

Features demonstrated:
- PTY process spawn and lifecycle
- Real-time shell output with ANSI colors
- Keyboard input handling
- Terminal resize functionality
- Ctrl+C interrupt signal

Usage:
    uv run python playground/playground_interactive_console.py

Press Ctrl+D or type 'exit' to quit.
"""
import os
import sys
import time
import select
import threading
import termios
import tty

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from x_ipe.services import TerminalService


class InteractiveConsolePlayground:
    """Interactive playground for testing TerminalService"""
    
    def __init__(self, working_dir: str = None):
        self.working_dir = working_dir or os.getcwd()
        self.terminal: TerminalService = None
        self.running = False
        self.old_settings = None
        
    def print_header(self):
        """Print playground header"""
        print("\n" + "=" * 60)
        print("🖥️  FEATURE-005: Interactive Console Playground")
        print("=" * 60)
        print(f"Working Directory: {self.working_dir}")
        print("-" * 60)
        print("Instructions:")
        print("  • Type commands and press Enter to execute")
        print("  • Use Ctrl+C to interrupt running commands")
        print("  • Type 'exit' or press Ctrl+D to quit")
        print("=" * 60 + "\n")
        sys.stdout.flush()
        
    def output_callback(self, data: str):
        """Handle output from PTY"""
        # Write directly to stdout (preserves ANSI colors)
        sys.stdout.write(data)
        sys.stdout.flush()
        
    def start(self):
        """Start the interactive terminal"""
        self.print_header()
        
        # Create terminal service
        self.terminal = TerminalService(
            cwd=self.working_dir,
            size=(24, 80)
        )
        
        # Register output callback
        self.terminal.on_output(self.output_callback)
        
        try:
            # Spawn PTY
            print("Starting PTY shell session...")
            sys.stdout.flush()
            self.terminal.spawn()
            self.running = True
            
            # Wait for initial shell prompt
            time.sleep(0.3)
            
            # Enter raw mode for immediate character-by-character input
            self._run_interactive_loop()
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            raise
        finally:
            self.stop()
            
    def _run_interactive_loop(self):
        """Main interactive input loop in raw terminal mode"""
        # Save terminal settings
        fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(fd)
        
        try:
            # Set terminal to raw mode (no echo, immediate input)
            tty.setraw(fd)
            
            while self.running and self.terminal.is_running:
                # Check if input is available
                r, _, _ = select.select([fd], [], [], 0.1)
                
                if r:
                    # Read single character
                    char = sys.stdin.read(1)
                    
                    if char:
                        # Handle Ctrl+D (EOF)
                        if char == '\x04':  # Ctrl+D
                            self.running = False
                            break
                            
                        # Send character to PTY
                        self.terminal.write(char)
                        
        except (EOFError, KeyboardInterrupt):
            self.running = False
        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, self.old_settings)
            
    def stop(self):
        """Stop the terminal session"""
        self.running = False
        
        if self.terminal:
            self.terminal.terminate()
            self.terminal = None
            
        # Print exit message
        print("\n")
        print("=" * 60)
        print("👋 Terminal session ended.")
        print("=" * 60)


def demo_terminal_service_api():
    """
    Demonstrate TerminalService API without interactive mode.
    
    This is useful for automated testing or when interactive mode
    is not available.
    """
    print("\n" + "=" * 60)
    print("📖 TerminalService API Demo (Non-interactive)")
    print("=" * 60)
    
    import tempfile
    
    # Create a temporary directory for demo
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"\n1. Creating TerminalService with cwd={tmpdir}")
        terminal = TerminalService(cwd=tmpdir, size=(24, 80))
        
        outputs = []
        
        def capture_output(data):
            outputs.append(data)
            print(f"   Output: {repr(data[:50])}..." if len(data) > 50 else f"   Output: {repr(data)}")
        
        print("\n2. Registering output callback")
        terminal.on_output(capture_output)
        
        print("\n3. Spawning PTY process")
        terminal.spawn()
        print(f"   Running: {terminal.is_running}")
        
        # Wait for shell prompt
        time.sleep(0.5)
        
        print("\n4. Sending 'echo Hello from playground'")
        terminal.write("echo 'Hello from playground'\r")
        time.sleep(0.3)
        
        print("\n5. Sending 'pwd' command")
        terminal.write("pwd\r")
        time.sleep(0.3)
        
        print("\n6. Testing Ctrl+C interrupt")
        terminal.write("\x03")  # Ctrl+C
        time.sleep(0.1)
        
        print("\n7. Resizing terminal to 30x100")
        terminal.resize(rows=30, cols=100)
        print(f"   New size: {terminal.size}")
        
        print("\n8. Terminating terminal")
        terminal.terminate()
        print(f"   Running after terminate: {terminal.is_running}")
        
        print("\n" + "=" * 60)
        print("✅ API Demo completed successfully!")
        print(f"   Total outputs captured: {len(outputs)}")
        print("=" * 60 + "\n")
        
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Interactive Console Playground (FEATURE-005)"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run non-interactive API demo instead"
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=None,
        help="Working directory for terminal"
    )
    
    args = parser.parse_args()
    
    if args.demo:
        # Run non-interactive demo
        success = demo_terminal_service_api()
        sys.exit(0 if success else 1)
    else:
        # Run interactive playground
        working_dir = args.dir or os.getcwd()
        
        # Verify directory exists
        if not os.path.isdir(working_dir):
            print(f"Error: Directory does not exist: {working_dir}")
            sys.exit(1)
            
        playground = InteractiveConsolePlayground(working_dir)
        playground.start()


if __name__ == "__main__":
    main()
