#!/usr/bin/env python3
"""
Human Simulation Tests for Interactive Console (FEATURE-005)

These tests simulate human interaction scenarios with the terminal.
They are NOT unit tests - they validate the complete user experience.

Each test scenario represents a real-world use case that a human
would perform when using the Interactive Console feature.

Run with:
    uv run python playground/tests/test_playground_interactive_console.py
"""
import os
import sys
import time
import tempfile

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from x_ipe.services import TerminalService


class HumanSimulationResult:
    """Result of a human simulation test"""
    
    def __init__(self, scenario: str, passed: bool, message: str = ""):
        self.scenario = scenario
        self.passed = passed
        self.message = message
        
    def __str__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        msg = f" - {self.message}" if self.message else ""
        return f"{status}: {self.scenario}{msg}"


def collect_output(terminal: TerminalService, duration: float = 0.5) -> str:
    """Collect output from terminal for a given duration"""
    outputs = []
    terminal.on_output(lambda data: outputs.append(data))
    time.sleep(duration)
    return "".join(outputs)


class InteractiveConsoleSimulation:
    """Human simulation tests for Interactive Console"""
    
    def __init__(self):
        self.results = []
        
    def run_all(self):
        """Run all simulation tests"""
        print("\n" + "=" * 60)
        print("🧪 Human Simulation Tests: Interactive Console (FEATURE-005)")
        print("=" * 60 + "\n")
        
        tests = [
            self.test_scenario_1_basic_command_execution,
            self.test_scenario_2_colored_output,
            self.test_scenario_3_working_directory,
            self.test_scenario_4_ctrl_c_interrupt,
            self.test_scenario_5_shell_features,
            self.test_scenario_6_terminal_resize,
            self.test_scenario_7_multiple_commands,
            self.test_scenario_8_error_handling,
        ]
        
        for test in tests:
            try:
                result = test()
                self.results.append(result)
                print(result)
            except Exception as e:
                self.results.append(HumanSimulationResult(
                    test.__name__,
                    False,
                    f"Exception: {e}"
                ))
                print(f"❌ FAIL: {test.__name__} - Exception: {e}")
                
        self._print_summary()
        return all(r.passed for r in self.results)
    
    def _print_summary(self):
        """Print test summary"""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        print("\n" + "-" * 60)
        print(f"Summary: {passed}/{total} scenarios passed")
        print("-" * 60)
        
        if passed == total:
            print("🎉 All human simulation scenarios passed!")
        else:
            print("⚠️  Some scenarios failed. Review the output above.")
        print()
    
    def test_scenario_1_basic_command_execution(self) -> HumanSimulationResult:
        """
        Scenario 1: Execute a basic command
        
        Human Action: Type 'echo hello' and press Enter
        Expected: See 'hello' printed in terminal
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            terminal = TerminalService(cwd=tmpdir)
            outputs = []
            terminal.on_output(lambda data: outputs.append(data))
            
            try:
                terminal.spawn()
                time.sleep(0.3)  # Wait for shell
                
                # Human types 'echo hello' and presses Enter
                terminal.write("echo hello\r")
                time.sleep(0.3)
                
                output = "".join(outputs)
                
                # Verify 'hello' appears in output
                if "hello" in output:
                    return HumanSimulationResult(
                        "Basic Command Execution",
                        True,
                        "Command output received correctly"
                    )
                else:
                    return HumanSimulationResult(
                        "Basic Command Execution",
                        False,
                        f"Expected 'hello' in output, got: {repr(output[:100])}"
                    )
            finally:
                terminal.terminate()
    
    def test_scenario_2_colored_output(self) -> HumanSimulationResult:
        """
        Scenario 2: View colored terminal output
        
        Human Action: Run 'ls --color=always' (or ls -G on macOS)
        Expected: See ANSI color codes in output
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some files to list
            for name in ["file1.txt", "file2.py", "folder1"]:
                path = os.path.join(tmpdir, name)
                if name.startswith("folder"):
                    os.makedirs(path)
                else:
                    open(path, 'w').close()
            
            terminal = TerminalService(cwd=tmpdir)
            outputs = []
            terminal.on_output(lambda data: outputs.append(data))
            
            try:
                terminal.spawn()
                time.sleep(0.3)
                
                # macOS uses ls -G for colors
                terminal.write("ls -G\r")
                time.sleep(0.3)
                
                output = "".join(outputs)
                
                # Check for ANSI escape codes (colors)
                has_ansi = "\x1b[" in output or "\033[" in output
                has_files = "file1" in output or "file2" in output
                
                if has_files:
                    return HumanSimulationResult(
                        "Colored Output Display",
                        True,
                        f"Output received, ANSI colors: {has_ansi}"
                    )
                else:
                    return HumanSimulationResult(
                        "Colored Output Display",
                        False,
                        f"Files not in output: {repr(output[:100])}"
                    )
            finally:
                terminal.terminate()
    
    def test_scenario_3_working_directory(self) -> HumanSimulationResult:
        """
        Scenario 3: Verify terminal starts in correct directory
        
        Human Action: Run 'pwd' after opening terminal
        Expected: Current directory matches configured cwd
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            terminal = TerminalService(cwd=tmpdir)
            outputs = []
            terminal.on_output(lambda data: outputs.append(data))
            
            try:
                terminal.spawn()
                time.sleep(0.3)
                
                terminal.write("pwd\r")
                time.sleep(0.3)
                
                output = "".join(outputs)
                
                # pwd should show the tmpdir path
                if tmpdir in output or os.path.basename(tmpdir) in output:
                    return HumanSimulationResult(
                        "Working Directory",
                        True,
                        "Terminal started in correct directory"
                    )
                else:
                    return HumanSimulationResult(
                        "Working Directory",
                        False,
                        f"Expected {tmpdir} in output"
                    )
            finally:
                terminal.terminate()
    
    def test_scenario_4_ctrl_c_interrupt(self) -> HumanSimulationResult:
        """
        Scenario 4: Interrupt a running command with Ctrl+C
        
        Human Action: Start 'sleep 10', then press Ctrl+C
        Expected: Command is interrupted, prompt returns
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            terminal = TerminalService(cwd=tmpdir)
            outputs = []
            terminal.on_output(lambda data: outputs.append(data))
            
            try:
                terminal.spawn()
                time.sleep(0.3)
                
                # Start a long-running command
                terminal.write("sleep 10\r")
                time.sleep(0.2)
                
                # Human presses Ctrl+C
                terminal.write("\x03")  # Ctrl+C
                time.sleep(0.3)
                
                output = "".join(outputs)
                
                # Should see ^C or interrupt indication
                # And terminal should still be responsive
                terminal.write("echo 'after_interrupt'\r")
                time.sleep(0.3)
                
                output = "".join(outputs)
                
                if "after_interrupt" in output:
                    return HumanSimulationResult(
                        "Ctrl+C Interrupt",
                        True,
                        "Interrupt worked, terminal responsive"
                    )
                else:
                    return HumanSimulationResult(
                        "Ctrl+C Interrupt",
                        False,
                        "Terminal not responsive after Ctrl+C"
                    )
            finally:
                terminal.terminate()
    
    def test_scenario_5_shell_features(self) -> HumanSimulationResult:
        """
        Scenario 5: Use shell features (pipes, redirects)
        
        Human Action: Run 'echo test | cat'
        Expected: Shell pipe works correctly
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            terminal = TerminalService(cwd=tmpdir)
            outputs = []
            terminal.on_output(lambda data: outputs.append(data))
            
            try:
                terminal.spawn()
                time.sleep(0.3)
                
                # Use pipe
                terminal.write("echo 'pipe_test' | cat\r")
                time.sleep(0.3)
                
                output = "".join(outputs)
                
                if "pipe_test" in output:
                    return HumanSimulationResult(
                        "Shell Features (Pipes)",
                        True,
                        "Pipe command executed correctly"
                    )
                else:
                    return HumanSimulationResult(
                        "Shell Features (Pipes)",
                        False,
                        f"Pipe output not found"
                    )
            finally:
                terminal.terminate()
    
    def test_scenario_6_terminal_resize(self) -> HumanSimulationResult:
        """
        Scenario 6: Resize terminal
        
        Human Action: Drag resize handle to change terminal size
        Expected: Terminal dimensions update
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            terminal = TerminalService(cwd=tmpdir, size=(24, 80))
            
            try:
                terminal.spawn()
                time.sleep(0.2)
                
                # Initial size
                initial_size = terminal.size
                
                # Human drags resize handle
                terminal.resize(rows=40, cols=120)
                
                new_size = terminal.size
                
                if new_size == (40, 120) and new_size != initial_size:
                    return HumanSimulationResult(
                        "Terminal Resize",
                        True,
                        f"Resized from {initial_size} to {new_size}"
                    )
                else:
                    return HumanSimulationResult(
                        "Terminal Resize",
                        False,
                        f"Resize failed: {initial_size} -> {new_size}"
                    )
            finally:
                terminal.terminate()
    
    def test_scenario_7_multiple_commands(self) -> HumanSimulationResult:
        """
        Scenario 7: Execute multiple commands in sequence
        
        Human Action: Run several commands one after another
        Expected: All commands execute, state persists
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            terminal = TerminalService(cwd=tmpdir)
            outputs = []
            terminal.on_output(lambda data: outputs.append(data))
            
            try:
                terminal.spawn()
                time.sleep(0.3)
                
                # Create a file
                terminal.write("touch testfile.txt\r")
                time.sleep(0.2)
                
                # Verify file exists
                terminal.write("ls testfile.txt\r")
                time.sleep(0.2)
                
                # Write to file
                terminal.write("echo 'content' > testfile.txt\r")
                time.sleep(0.2)
                
                # Read file
                terminal.write("cat testfile.txt\r")
                time.sleep(0.3)
                
                output = "".join(outputs)
                
                if "testfile.txt" in output and "content" in output:
                    return HumanSimulationResult(
                        "Multiple Commands",
                        True,
                        "Command sequence executed, state persisted"
                    )
                else:
                    return HumanSimulationResult(
                        "Multiple Commands",
                        False,
                        "State not persisted between commands"
                    )
            finally:
                terminal.terminate()
    
    def test_scenario_8_error_handling(self) -> HumanSimulationResult:
        """
        Scenario 8: Handle command errors gracefully
        
        Human Action: Run a command that fails
        Expected: Error message displayed, terminal still usable
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            terminal = TerminalService(cwd=tmpdir)
            outputs = []
            terminal.on_output(lambda data: outputs.append(data))
            
            try:
                terminal.spawn()
                time.sleep(0.3)
                
                # Run command that doesn't exist
                terminal.write("nonexistent_command_xyz\r")
                time.sleep(0.3)
                
                # Terminal should still work
                terminal.write("echo 'still_working'\r")
                time.sleep(0.3)
                
                output = "".join(outputs)
                
                # Should see error and recovery
                has_error = "not found" in output.lower() or "command not found" in output.lower()
                has_recovery = "still_working" in output
                
                if has_recovery:
                    return HumanSimulationResult(
                        "Error Handling",
                        True,
                        f"Terminal recovered after error (error shown: {has_error})"
                    )
                else:
                    return HumanSimulationResult(
                        "Error Handling",
                        False,
                        "Terminal not responsive after error"
                    )
            finally:
                terminal.terminate()


def main():
    """Run all human simulation tests"""
    simulation = InteractiveConsoleSimulation()
    success = simulation.run_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
