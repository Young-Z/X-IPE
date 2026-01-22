import os
import time
import sys
import logging
from src.services import TerminalService

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def on_output(data):
    print(f"[{time.time():.2f}] OUTPUT: {repr(data)}")
    sys.stdout.flush()

def test_terminal():
    print(f"Current PID: {os.getpid()}")
    cwd = os.getcwd()
    print(f"CWD: {cwd}")
    print(f"SHELL: {os.environ.get('SHELL', '/bin/zsh')}")
    
    try:
        ts = TerminalService(working_dir=cwd)
        print("Starting terminal...")
        ts.start(on_output)
        
        # Give it a moment to start up and print prompt
        print("Waiting for shell to start (5s)...")
        time.sleep(5)
        
        print(f"After 5s - is_running: {ts.is_running}")
        
        if not ts.is_running:
            print("ERROR: Terminal died within 5 seconds!")
            if ts.pty:
                print(f"  exitstatus: {ts.pty.exitstatus}")
                print(f"  signalstatus: {ts.pty.signalstatus}")
            return
        
        print("Sending 'echo hello'...")
        ts.write("echo hello\n")
        time.sleep(2)
        
        print(f"After echo - is_running: {ts.is_running}")
        
        # Now wait longer to see if it dies
        print("Waiting 30 seconds to see if terminal stays alive...")
        for i in range(6):
            time.sleep(5)
            alive = ts.is_running
            print(f"  {(i+1)*5}s - is_running: {alive}")
            if not alive:
                print("ERROR: Terminal died during idle wait!")
                if ts.pty:
                    print(f"  exitstatus: {ts.pty.exitstatus}")
                    print(f"  signalstatus: {ts.pty.signalstatus}")
                return
        
        print("Terminal stayed alive for 30s. Stopping...")
        ts.stop()
        print("Done.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_terminal()
