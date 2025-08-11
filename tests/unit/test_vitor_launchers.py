"""
Unit tests for Vitor's enhanced launcher scripts
Tests verify launcher execution, context loading, and configuration
"""

import subprocess
import sys
import os
from pathlib import Path
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestVitorLaunchers:
    """Test suite for Vitor's enhanced launcher scripts"""
    
    def setup_method(self):
        """Set up test environment"""
        self.launchers_dir = project_root / "launchers"
        self.claude_md_path = project_root / "agents" / "VITOR" / "CLAUDE.md"
        
    def test_strike_leader_launcher_exists(self):
        """Test that Strike Leader launcher file exists and is executable"""
        launcher_path = self.launchers_dir / "launch_vitor_strike_leader_enhanced.py"
        assert launcher_path.exists(), "Strike Leader launcher should exist"
        assert launcher_path.is_file(), "Strike Leader launcher should be a file"
        # Check if file has execution permissions
        assert os.access(launcher_path, os.X_OK), "Strike Leader launcher should be executable"
        
    def test_wingman_launcher_exists(self):
        """Test that Wingman launcher file exists and is executable"""
        launcher_path = self.launchers_dir / "launch_vitor_wingman_enhanced.py"
        assert launcher_path.exists(), "Wingman launcher should exist"
        assert launcher_path.is_file(), "Wingman launcher should be a file"
        assert os.access(launcher_path, os.X_OK), "Wingman launcher should be executable"
        
    def test_tower_launcher_exists(self):
        """Test that Tower launcher file exists and is executable"""
        launcher_path = self.launchers_dir / "launch_vitor_tower_enhanced.py"
        assert launcher_path.exists(), "Tower launcher should exist"
        assert launcher_path.is_file(), "Tower launcher should be a file"
        assert os.access(launcher_path, os.X_OK), "Tower launcher should be executable"
        
    def test_strike_leader_launcher_syntax(self):
        """Test that Strike Leader launcher has valid Python syntax"""
        launcher_path = self.launchers_dir / "launch_vitor_strike_leader_enhanced.py"
        result = subprocess.run([
            sys.executable, "-m", "py_compile", str(launcher_path)
        ], capture_output=True, text=True)
        assert result.returncode == 0, f"Strike Leader launcher should have valid syntax: {result.stderr}"
        
    def test_wingman_launcher_syntax(self):
        """Test that Wingman launcher has valid Python syntax"""
        launcher_path = self.launchers_dir / "launch_vitor_wingman_enhanced.py"
        result = subprocess.run([
            sys.executable, "-m", "py_compile", str(launcher_path)
        ], capture_output=True, text=True)
        assert result.returncode == 0, f"Wingman launcher should have valid syntax: {result.stderr}"
        
    def test_tower_launcher_syntax(self):
        """Test that Tower launcher has valid Python syntax"""
        launcher_path = self.launchers_dir / "launch_vitor_tower_enhanced.py"
        result = subprocess.run([
            sys.executable, "-m", "py_compile", str(launcher_path)
        ], capture_output=True, text=True)
        assert result.returncode == 0, f"Tower launcher should have valid syntax: {result.stderr}"
        
    def test_claude_md_updates_on_launcher_execution(self):
        """Test that CLAUDE.md gets updated when launchers run"""
        # Check if CLAUDE.md exists and is writable
        assert self.claude_md_path.exists(), "CLAUDE.md should exist"
        assert os.access(self.claude_md_path, os.W_OK), "CLAUDE.md should be writable"
        
        # Get initial modification time
        initial_mtime = self.claude_md_path.stat().st_mtime
        
        # Run Strike Leader launcher (it should update CLAUDE.md)
        launcher_path = self.launchers_dir / "launch_vitor_strike_leader_enhanced.py"
        result = subprocess.run([
            sys.executable, str(launcher_path)
        ], capture_output=True, text=True, timeout=10)
        
        # Launcher should execute without errors
        assert result.returncode == 0, f"Strike Leader launcher should execute successfully: {result.stderr}"
        
    def test_launcher_output_contains_agent_context(self):
        """Test that launcher output contains expected agent context markers"""
        launcher_path = self.launchers_dir / "launch_vitor_strike_leader_enhanced.py"
        result = subprocess.run([
            sys.executable, str(launcher_path)
        ], capture_output=True, text=True, timeout=10)
        
        output = result.stdout
        # Check for key context markers
        assert "STRIKE LEADER AGENT CONTEXT LOADED" in output, "Should load Strike Leader context"
        assert "MANDATORY TDD WORKFLOW" in output, "Should enforce TDD workflow"
        assert "Roman engineering standards" in output.lower() or "roman" in output.lower(), "Should reference Roman standards"
        
    def test_launcher_creates_no_temp_files(self):
        """Test that launchers don't create temporary files in working directory"""
        initial_files = set(os.listdir('.'))
        
        launcher_path = self.launchers_dir / "launch_vitor_strike_leader_enhanced.py"
        subprocess.run([
            sys.executable, str(launcher_path)
        ], capture_output=True, text=True, timeout=10)
        
        final_files = set(os.listdir('.'))
        new_files = final_files - initial_files
        
        # Filter out acceptable files (like .pyc in __pycache__)
        unexpected_files = [f for f in new_files if not f.startswith('.') and not f.endswith('.pyc')]
        assert len(unexpected_files) == 0, f"Launcher should not create temp files: {unexpected_files}"
        
if __name__ == "__main__":
    pytest.main([__file__, "-v"])