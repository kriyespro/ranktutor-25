#!/usr/bin/env python
"""
Durga - Development server script
Clears cache and starts Django development server
"""
import os
import sys
import subprocess
from pathlib import Path

def clear_cache():
    """Clear Django cache and pycache files"""
    print("🧹 Clearing cache...")
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                import shutil
                shutil.rmtree(pycache_path)
                print(f"   Removed {pycache_path}")
            except Exception as e:
                print(f"   Error removing {pycache_path}: {e}")
    
    # Remove .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                try:
                    os.remove(pyc_path)
                    print(f"   Removed {pyc_path}")
                except Exception as e:
                    print(f"   Error removing {pyc_path}: {e}")
    
    print("✅ Cache cleared!")

def start_server():
    """Start Django development server"""
    print("\n🚀 Starting Django development server...")
    print("   Server will be available at http://127.0.0.1:8000/")
    print("   Press Ctrl+C to stop the server\n")
    
    # Activate virtual environment and run server
    if sys.platform == 'win32':
        # Windows
        subprocess.run(['venv\\Scripts\\python.exe', 'manage.py', 'runserver'])
    else:
        # Unix/Linux/Mac
        subprocess.run(['venv/bin/python', 'manage.py', 'runserver'])

if __name__ == '__main__':
    # Check if we're in the project root
    if not Path('manage.py').exists():
        print("❌ Error: manage.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Clear cache
    clear_cache()
    
    # Start server
    start_server()

