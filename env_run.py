#!/usr/bin/env python3
import subprocess
import sys
import os

def run():
    # Change to ai-screening-main directory
    os.chdir('ai-screening-main')
    
    # Activate virtual environment
    venv_python = os.path.join('.venv', 'bin', 'python')
    
    # Check if venv exists
    if not os.path.exists(venv_python):
        print("Virtual environment not found. Creating it...")
        subprocess.run(['uv', 'venv'], check=True)
        print("Installing dependencies...")
        try:
            subprocess.run(['uv', 'sync'], check=True)
        except subprocess.CalledProcessError:
            print("uv sync failed, trying pip install...")
            subprocess.run([venv_python, '-m', 'pip', 'install', '-e', '.'], check=True)
    
    # Run Flask app
    subprocess.run([venv_python, 'run_api.py'])

if __name__ == "__main__":
    run()