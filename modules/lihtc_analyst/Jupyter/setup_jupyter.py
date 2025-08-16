#!/usr/bin/env python3
"""
Jupyter Setup Script for LIHTC Analysis
This script installs and configures Jupyter for financial modeling
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a shell command and report status"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} - Success")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"✗ {description} - Failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ {description} - Error: {str(e)}")
        return False

def main():
    print("===================================")
    print("Jupyter Setup for LIHTC Analysis")
    print("===================================")
    
    # Check Python version
    python_version = sys.version_info
    print(f"\nPython version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3:
        print("Error: Python 3 is required")
        sys.exit(1)
    
    # List of packages to install
    packages = [
        "jupyter",
        "notebook",
        "ipywidgets",
        "plotly",
        "seaborn",
        "pandas",
        "numpy",
        "matplotlib",
        "openpyxl"  # For Excel file handling
    ]
    
    # Install packages
    print("\nInstalling required packages...")
    for package in packages:
        run_command(f"{sys.executable} -m pip install {package}", f"Installing {package}")
    
    # Enable widget extension
    run_command("jupyter nbextension enable --py widgetsnbextension --sys-prefix", 
                "Enabling Jupyter widget extensions")
    
    # Create directories
    notebooks_dir = os.path.join(os.getcwd(), "notebooks")
    data_dir = os.path.join(os.getcwd(), "data")
    
    for directory in [notebooks_dir, data_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created directory: {directory}")
    
    print("\n===================================")
    print("Setup Complete!")
    print("===================================")
    print("\nTo start Jupyter Notebook, run:")
    print("  jupyter notebook")
    print("\nOr to use Jupyter Lab (modern interface):")
    print("  jupyter lab")
    print("\nThe sample notebook 'LIHTC_Analysis_Sample.ipynb' has been created.")
    print("\nTips:")
    print("- Use Shift+Enter to run cells")
    print("- The notebook will open in your default browser")
    print("- Interactive widgets will update in real-time")

if __name__ == "__main__":
    main()