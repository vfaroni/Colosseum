#!/usr/bin/env python3
"""
Environment Setup Script for LIHTC Site Scorer

This script helps set up the development environment and verify dependencies.
"""

import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_config_file():
    """Create configuration file from example"""
    config_path = Path("config/config.json")
    example_path = Path("config/config.example.json")
    
    if config_path.exists():
        print("✅ Configuration file already exists")
        return True
    
    if not example_path.exists():
        print("❌ Example configuration file not found")
        return False
    
    try:
        # Copy example to actual config
        example_config = json.loads(example_path.read_text())
        config_path.write_text(json.dumps(example_config, indent=2))
        print("✅ Configuration file created from example")
        print("⚠️  Please edit config/config.json with your API keys")
        return True
    except Exception as e:
        print(f"❌ Failed to create config file: {e}")
        return False

def verify_directory_structure():
    """Verify all required directories exist"""
    required_dirs = [
        "src", "tests", "data", "docs", "contracts", 
        "config", "scripts", "outputs", "examples",
        "src/core", "src/analyzers", "src/data_managers", 
        "src/utils", "src/api", "data/qap", "data/rents",
        "data/amenities", "data/boundaries", "data/cache"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ Missing directories:", missing_dirs)
        return False
    
    print("✅ Directory structure verified")
    return True

def test_basic_imports():
    """Test that basic imports work"""
    try:
        import pandas
        import geopandas  
        import shapely
        import requests
        import folium
        print("✅ Core dependencies import successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def create_sample_data():
    """Create sample data files for testing"""
    sample_data_dir = Path("tests/sample_data")
    sample_data_dir.mkdir(exist_ok=True)
    
    # Sample site coordinates
    sample_sites = {
        "test_sites": [
            {
                "name": "Simi Valley Test Site",
                "latitude": 34.282556,
                "longitude": -118.708943,
                "state": "CA",
                "expected_qct": True,
                "expected_points": 23
            },
            {
                "name": "Los Angeles Test Site", 
                "latitude": 34.0522,
                "longitude": -118.2437,
                "state": "CA",
                "expected_qct": False,
                "expected_points": 15
            }
        ]
    }
    
    sample_file = sample_data_dir / "test_sites.json"
    sample_file.write_text(json.dumps(sample_sites, indent=2))
    print("✅ Sample test data created")

def main():
    """Main setup routine"""
    print("LIHTC Site Scorer - Environment Setup")
    print("=" * 50)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Verify directory structure
    if not verify_directory_structure():
        success = False
    
    # Install dependencies
    if not install_dependencies():
        success = False
    
    # Test imports
    if not test_basic_imports():
        success = False
    
    # Create config file
    if not create_config_file():
        success = False
    
    # Create sample data
    create_sample_data()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Environment setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit config/config.json with your API keys")
        print("2. Run: python examples/basic_usage.py")
        print("3. Run tests: python -m pytest tests/")
    else:
        print("❌ Environment setup failed. Please fix the issues above.")
    
    return success

if __name__ == "__main__":
    main()