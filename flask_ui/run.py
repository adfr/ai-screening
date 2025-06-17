#!/usr/bin/env python3
import subprocess
import sys
import os

def run():
    # Activate virtual environment
    venv_python = os.path.join('.venv', 'bin', 'python')
    
    # Check if venv exists
    if not os.path.exists(venv_python):
        print("Virtual environment not found. Please run 'uv venv' first.")
        sys.exit(1)
    
    # Run Flask app
    subprocess.run([venv_python, 'app/app.py'])

if __name__ == "__main__":
    run()