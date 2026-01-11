#!/usr/bin/env python3
"""
Photo Gallery NAS Startup Script

This script starts the photo gallery backend server for NAS deployment
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

# Configuration
DEFAULT_PORT = 5050  # Default server port
PHOTOS_PATH = "/share/Photos"  # Path to photos directory
PID_FILE = "/tmp/photo_gallery.pid"  # Process ID file

def check_photos_directory():
    """
    Check if photos directory exists and is accessible
    """
    if not os.path.exists(PHOTOS_PATH):
        print(f"Error: Photos directory {PHOTOS_PATH} does not exist!")
        return False
    
    if not os.access(PHOTOS_PATH, os.R_OK):
        print(f"Error: No read access to {PHOTOS_PATH}")
        return False
    
    print(f"Photos directory OK: {PHOTOS_PATH}")
    return True

def start_server():
    """
    Start the photo gallery server
    """
    if not check_photos_directory():
        sys.exit(1)
    
    # Get current script directory
    script_dir = Path(__file__).parent
    app_file = script_dir / "app.py"
    
    if not app_file.exists():
        print(f"Error: app.py not found in {script_dir}")
        sys.exit(1)
    
    # Start server in production mode
    print(f"Starting Photo Gallery Server on port {DEFAULT_PORT}")
    
    try:
        # Change to script directory
        os.chdir(script_dir)
        
        # Start the Flask application
        subprocess.run([sys.executable, "app.py", "production"], check=True)
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()