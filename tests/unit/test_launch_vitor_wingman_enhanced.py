"""
Unit tests for launch_vitor_wingman_enhanced.py
Tests specific Wingman launcher functionality
"""

import subprocess
import sys
import os
from pathlib import Path
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestWingmanLauncher:
    """Test suite for Wingman enhanced launcher"""
    
    def setup_method(self):
        """Set up test environment"""
        self.launcher_path = project_root / "launchers" / "launch_vitor_wingman_enhanced.py"
        
    def test_launcher_exists_and_executable(self):
        """Test launcher file exists and is executable"""
        assert self.launcher_path.exists(), "Wingman launcher should exist"
        assert os.access(self.launcher_path, os.X_OK), "Wingman launcher should be executable"
        
    def test_launcher_valid_python_syntax(self):
        """Test launcher has valid Python syntax"""
        result = subprocess.run([
            sys.executable, "-m", "py_compile", str(self.launcher_path)
        ], capture_output=True, text=True)
        assert result.returncode == 0, f"Should have valid syntax: {result.stderr}"
        
    def test_launcher_produces_wingman_output(self):
        """Test launcher produces Wingman specific output"""
        result = subprocess.run([
            sys.executable, str(self.launcher_path)
        ], capture_output=True, text=True, timeout=10)
        
        assert result.returncode == 0, f"Launcher should execute: {result.stderr}"
        assert "WINGMAN" in result.stdout, "Should indicate Wingman context"
        assert "Technical Implementation" in result.stdout, "Should show Technical Implementation role"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])