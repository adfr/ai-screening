#!/usr/bin/env python3
import subprocess
import sys
import os

def run():
    # Use current directory (ai-screening)
    current_dir = os.getcwd()
    
    # Use current Python environment
    python_executable = sys.executable
    
    print(f"Starting merged SDN application from {current_dir}")
    print(f"Using Python: {python_executable}")
    
    # Run merged Flask app
    subprocess.run([python_executable, 'run_merged_app.py'])

if __name__ == "__main__":
    run()