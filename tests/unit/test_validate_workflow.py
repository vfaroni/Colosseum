#!/usr/bin/env python3
"""
Unit tests for validate_workflow.py
Tests the workflow validation system for VITOR agents
"""

import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add the agents/VITOR directory to the Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agents" / "VITOR"))

from validate_workflow import WorkflowValidator


class TestWorkflowValidator:
    """Test cases for WorkflowValidator class"""
    
    def test_init_with_mission_name(self):
        """Test validator initialization with mission name"""
        validator = WorkflowValidator("test_mission")
        assert validator.mission_name == "test_mission"
        assert validator.errors == []
        assert validator.warnings == []
        assert isinstance(validator.current_dir, Path)
    
    def test_init_without_mission_name(self):
        """Test validator initialization without mission name"""
        validator = WorkflowValidator()
        assert validator.mission_name is None
        assert validator.errors == []
        assert validator.warnings == []
    
    @patch('subprocess.run')
    def test_check_git_available_success(self, mock_run):
        """Test git availability check when git is available"""
        mock_run.return_value = MagicMock(returncode=0)
        validator = WorkflowValidator()
        assert validator.git_available is True
    
    @patch('subprocess.run')
    def test_check_git_available_failure(self, mock_run):
        """Test git availability check when git is not available"""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        validator = WorkflowValidator()
        assert validator.git_available is False
    
    @patch('subprocess.run')
    def test_validate_git_branch_main_branch_error(self, mock_run):
        """Test git branch validation fails on main branch"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="main\n"
        )
        validator = WorkflowValidator()
        validator.git_available = True
        
        result = validator.validate_git_branch()
        assert result is False
        assert any("Cannot work directly on main/master branch" in error for error in validator.errors)
    
    @patch('subprocess.run')
    def test_validate_git_branch_feature_branch_success(self, mock_run):
        """Test git branch validation passes on feature branch"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="feature/test-branch\n"
        )
        validator = WorkflowValidator()
        validator.git_available = True
        
        result = validator.validate_git_branch()
        assert result is True
        assert len(validator.errors) == 0
    
    @patch('subprocess.run')
    def test_validate_git_branch_invalid_naming(self, mock_run):
        """Test git branch validation with invalid naming convention"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="random-branch-name\n"
        )
        validator = WorkflowValidator()
        validator.git_available = True
        
        result = validator.validate_git_branch()
        assert result is True
        assert any("doesn't follow naming convention" in warning for warning in validator.warnings)
    
    def test_validate_test_plan_missing(self):
        """Test test plan validation when no test_plan.md exists"""
        with tempfile.TemporaryDirectory() as temp_dir:
            validator = WorkflowValidator()
            validator.current_dir = Path(temp_dir)
            
            result = validator.validate_test_plan()
            assert result is False
            assert any("No test_plan.md found" in error for error in validator.errors)
    
    def test_validate_test_plan_exists_valid(self):
        """Test test plan validation with valid test_plan.md"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_plan = temp_path / "test_plan.md"
            
            test_plan.write_text("""
# Test Plan

## Feature Description
Test feature description

## Contracts
Test contracts

## Test Cases
Test cases
""")
            
            validator = WorkflowValidator()
            validator.current_dir = temp_path
            
            result = validator.validate_test_plan()
            assert result is True
            assert len(validator.errors) == 0
    
    def test_validate_test_plan_incomplete(self):
        """Test test plan validation with incomplete test_plan.md"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_plan = temp_path / "test_plan.md"
            
            test_plan.write_text("""
# Test Plan

## Feature Description
Test feature description
""")
            
            validator = WorkflowValidator()
            validator.current_dir = temp_path
            
            result = validator.validate_test_plan()
            assert result is False
            assert any("No valid test plans found" in error for error in validator.errors)
    
    def test_validate_tests_exist_missing(self):
        """Test test validation when no test files exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            validator = WorkflowValidator()
            validator.current_dir = Path(temp_dir)
            
            result = validator.validate_tests_exist()
            assert result is False
            assert any("No test files found" in error for error in validator.errors)
    
    def test_validate_tests_exist_present(self):
        """Test test validation when test files exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test_example.py"
            test_file.write_text("# Test file")
            
            validator = WorkflowValidator()
            validator.current_dir = temp_path
            
            result = validator.validate_tests_exist()
            assert result is True
            assert len(validator.errors) == 0
    
    @patch('subprocess.run')
    def test_run_tests_success(self, mock_run):
        """Test test execution when tests pass"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="5 passed\n",
            stderr=""
        )
        
        validator = WorkflowValidator()
        result = validator.run_tests()
        assert result is True
    
    @patch('subprocess.run')
    def test_run_tests_failure(self, mock_run):
        """Test test execution when tests fail"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="2 failed, 3 passed\n",
            stderr=""
        )
        
        validator = WorkflowValidator()
        result = validator.run_tests()
        assert result is False
        assert any("Tests failing" in error for error in validator.errors)
    
    def test_validate_code_quality_no_files(self):
        """Test code quality validation with no Python files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            validator = WorkflowValidator()
            validator.current_dir = Path(temp_dir)
            
            result = validator.validate_code_quality()
            assert result is True
            assert any("No Python files found" in warning for warning in validator.warnings)
    
    def test_validate_code_quality_with_files(self):
        """Test code quality validation with Python files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            py_file = temp_path / "example.py"
            py_file.write_text('''
def example_function():
    """This function has a docstring"""
    pass

def missing_docstring():
    pass
''')
            
            validator = WorkflowValidator()
            validator.current_dir = temp_path
            
            result = validator.validate_code_quality()
            assert result is True
            # Should find the missing docstring issue
            assert any("missing docstring" in str(warning).lower() for warning in validator.warnings)
    
    def test_generate_report_success(self):
        """Test report generation with successful validation"""
        validator = WorkflowValidator("test_mission")
        
        success = validator.generate_report()
        assert success is True
    
    def test_generate_report_with_errors(self):
        """Test report generation with validation errors"""
        validator = WorkflowValidator("test_mission")
        validator.errors.append("Test error")
        
        success = validator.generate_report()
        assert success is False
    
    @patch.object(WorkflowValidator, 'validate_git_branch')
    @patch.object(WorkflowValidator, 'validate_test_plan')
    @patch.object(WorkflowValidator, 'validate_tests_exist')
    @patch.object(WorkflowValidator, 'run_tests')
    @patch.object(WorkflowValidator, 'validate_code_quality')
    @patch.object(WorkflowValidator, 'validate_pull_request')
    @patch.object(WorkflowValidator, 'validate_data_organization')
    @patch.object(WorkflowValidator, 'generate_report')
    def test_run_full_validation(self, mock_report, mock_data, mock_pr, 
                                mock_quality, mock_tests_run, mock_tests_exist, 
                                mock_test_plan, mock_git):
        """Test full validation workflow"""
        # Mock all validation methods to return True
        mock_git.return_value = True
        mock_test_plan.return_value = True
        mock_tests_exist.return_value = True
        mock_tests_run.return_value = True
        mock_quality.return_value = True
        mock_pr.return_value = True
        mock_data.return_value = True
        mock_report.return_value = True
        
        validator = WorkflowValidator()
        result = validator.run_full_validation()
        
        # Verify all validation methods were called
        mock_git.assert_called_once()
        mock_test_plan.assert_called_once()
        mock_tests_exist.assert_called_once()
        mock_tests_run.assert_called_once()
        mock_quality.assert_called_once()
        mock_pr.assert_called_once()
        mock_data.assert_called_once()
        mock_report.assert_called_once()
        
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__])