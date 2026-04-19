#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

def main():
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("Starting XivMind API Tester...")
    print()
    print("Make sure the main XivMind application is running on port 8000")
    print()
    
    venv_dir = script_dir / "venv"
    
    if not venv_dir.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    
    if sys.platform == "win32":
        pip_path = venv_dir / "Scripts" / "pip.exe"
        python_path = venv_dir / "Scripts" / "python.exe"
    else:
        pip_path = venv_dir / "bin" / "pip"
        python_path = venv_dir / "bin" / "python"
    
    print("Installing dependencies...")
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt", "-q"], check=True)
    
    print()
    print("Starting API Tester on port 8001...")
    print("Open http://localhost:8001 in your browser")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    subprocess.run([
        str(python_path), "-m", "uvicorn", 
        "app.main:app", "--reload", "--port", "8001"
    ])

if __name__ == "__main__":
    main()
