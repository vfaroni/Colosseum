"""
Unit tests for launch_vitor_strike_leader_enhanced.py
Tests specific Strike Leader launcher functionality
"""

import subprocess
import sys
import os
from pathlib import Path
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestStrikeLeaderLauncher:
    """Test suite for Strike Leader enhanced launcher"""
    
    def setup_method(self):
        """Set up test environment"""
        self.launcher_path = project_root / "launchers" / "launch_vitor_strike_leader_enhanced.py"
        
    def test_launcher_exists_and_executable(self):
        """Test launcher file exists and is executable"""
        assert self.launcher_path.exists(), "Strike Leader launcher should exist"
        assert os.access(self.launcher_path, os.X_OK), "Strike Leader launcher should be executable"
        
    def test_launcher_valid_python_syntax(self):
        """Test launcher has valid Python syntax"""
        result = subprocess.run([
            sys.executable, "-m", "py_compile", str(self.launcher_path)
        ], capture_output=True, text=True)
        assert result.returncode == 0, f"Should have valid syntax: {result.stderr}"
        
    def test_launcher_produces_strike_leader_output(self):
        """Test launcher produces Strike Leader specific output"""
        result = subprocess.run([
            sys.executable, str(self.launcher_path)
        ], capture_output=True, text=True, timeout=10)
        
        assert result.returncode == 0, f"Launcher should execute: {result.stderr}"
        assert "STRIKE LEADER" in result.stdout, "Should indicate Strike Leader context"
        assert "Strategic Coordination" in result.stdout, "Should show Strategic Coordination role"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])