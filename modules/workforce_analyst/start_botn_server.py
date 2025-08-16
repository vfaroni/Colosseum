#!/usr/bin/env python3
"""
BOTN Server Launcher
Quick launcher for the BOTN API server with dependency checking

Author: Claude Code Assistant
Date: 2025-08-04
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = ['flask', 'flask-cors', 'openpyxl']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - missing")
    
    if missing_packages:
        print(f"\n🔧 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")
            return False
    
    return True

def main():
    print("🚀 BOTN Server Launcher")
    print("=" * 50)
    
    # Check if we're in the right directory
    current_dir = os.getcwd()
    expected_files = ['botn_api.py', 'botn_file_creator.py']
    
    missing_files = [f for f in expected_files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print(f"📁 Current directory: {current_dir}")
        print("🔧 Please run this script from the workforce_analyst directory")
        return
    
    print("📁 Directory check: ✅")
    
    # Check dependencies
    print("\n🔍 Checking Python dependencies...")
    if not check_dependencies():
        print("❌ Dependency check failed. Please install missing packages manually.")
        return
    
    print("\n🌐 Starting BOTN API server...")
    print("📋 Server will be available at: http://localhost:5002")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Launch the BOTN API server
        subprocess.run([sys.executable, 'botn_api.py'])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()