#!/usr/bin/env python3
"""
Docker build script that automatically extracts version from version.py

Usage:
    # Build CPU version
    python backend/scripts/build_docker.py
    
    # Build GPU version
    python backend/scripts/build_docker.py --gpu
    
    # Or run from backend directory
    cd backend
    python scripts/build_docker.py
    python scripts/build_docker.py --gpu

The script will:
    1. Read APP_VERSION from backend/app/version.py
    2. Pass it to docker build via --build-arg
    3. Build the image with correct version label
"""

import os
import re
import subprocess
import sys

def get_version():
    """Extract version from version.py"""
    version_file = os.path.join(os.path.dirname(__file__), '..', 'app', 'version.py')
    with open(version_file, 'r') as f:
        content = f.read()
        match = re.search(r"APP_VERSION\s*=\s*'([^']+)'", content)
        if match:
            return match.group(1)
    return '0.7.1'

def build_docker(gpu=False):
    """Build Docker image with version"""
    version = get_version()
    print(f"Building Docker image with version: {version}")
    
    context = os.path.join(os.path.dirname(__file__), '..')
    dockerfile = os.path.join(context, 'docker', f'Dockerfile{".gpu" if gpu else ""}')
    image_tag = f"xivmind:{'gpu' if gpu else 'latest'}"
    
    cmd = [
        'docker', 'build',
        '-t', image_tag,
        '-f', dockerfile,
        '--build-arg', f'APP_VERSION={version}',
        context
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"Successfully built {image_tag}")

if __name__ == '__main__':
    gpu = '--gpu' in sys.argv
    build_docker(gpu)