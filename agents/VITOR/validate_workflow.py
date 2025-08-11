#!/usr/bin/env python3
"""
Workflow Validation Script for VITOR Agents
Ensures compliance with TDD and development protocols

USAGE: python3 validate_workflow.py [mission_name]
PURPOSE: Validate that all development rules are followed before mission completion
ENFORCEMENT: Mandatory execution before any mission can be marked complete
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import re


class WorkflowValidator:
    def __init__(self, mission_name=None):
        self.mission_name = mission_name
        self.errors = []
        self.warnings = []
        self.current_dir = Path.cwd()
        self.git_available = self._check_git_available()
        
    def _check_git_available(self):
        """Check if git is available and we're in a git repository"""
        try:
            result = subprocess.run(['git', 'status'], 
                                  capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def validate_git_branch(self):
        """Validate git branch requirements"""
        print("🔍 Validating Git Branch Requirements...")
        
        if not self.git_available:
            self.errors.append("❌ Git not available or not in a git repository")
            return False
            
        # Check current branch
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, check=True)
            current_branch = result.stdout.strip()
            
            if current_branch == 'main' or current_branch == 'master':
                self.errors.append("❌ Cannot work directly on main/master branch - create feature branch")
                return False
            
            # Check if branch follows naming convention
            if not (current_branch.startswith('feature/') or 
                   current_branch.startswith('bugfix/') or
                   current_branch.startswith('hotfix/')):
                self.warnings.append(f"⚠️  Branch '{current_branch}' doesn't follow naming convention (feature/, bugfix/, hotfix/)")
            
            print(f"✅ Git branch: {current_branch}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.errors.append(f"❌ Git branch validation failed: {e}")
            return False
    
    def validate_test_plan(self):
        """Validate test_plan.md exists and has required content"""
        print("🔍 Validating Test Plan Requirements...")
        
        # Look for test_plan.md files in current and subdirectories
        test_plans = list(self.current_dir.rglob("test_plan.md"))
        
        if not test_plans:
            self.errors.append("❌ No test_plan.md found - TDD requires test contracts first")
            return False
        
        valid_plans = 0
        for test_plan in test_plans:
            content = test_plan.read_text()
            required_sections = [
                "Feature Description",
                "Contracts", 
                "Test Cases"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            
            if missing_sections:
                self.warnings.append(f"⚠️  {test_plan} missing sections: {missing_sections}")
            else:
                valid_plans += 1
                print(f"✅ Valid test plan: {test_plan.relative_to(self.current_dir)}")
        
        if valid_plans == 0:
            self.errors.append("❌ No valid test plans found - must include Feature Description, Contracts, Test Cases")
            return False
            
        return True
    
    def validate_tests_exist(self):
        """Validate that actual test files exist"""
        print("🔍 Validating Test Implementation...")
        
        # Look for test files
        test_files = []
        test_files.extend(list(self.current_dir.rglob("test_*.py")))
        test_files.extend(list(self.current_dir.rglob("*_test.py")))
        test_files.extend(list(self.current_dir.rglob("tests/*.py")))
        
        if not test_files:
            self.errors.append("❌ No test files found - TDD requires tests before implementation")
            return False
        
        print(f"✅ Found {len(test_files)} test files")
        for test_file in test_files[:5]:  # Show first 5
            print(f"   📝 {test_file.relative_to(self.current_dir)}")
        
        return True
    
    def run_tests(self):
        """Run tests and validate they pass"""
        print("🔍 Running Tests...")
        
        # Try pytest first, then unittest
        test_runners = [
            ['python3', '-m', 'pytest', '-v', '--tb=short'],
            ['python3', '-m', 'unittest', 'discover', '-v']
        ]
        
        for runner in test_runners:
            try:
                result = subprocess.run(runner, capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    print("✅ All tests passing")
                    # Extract test count if possible
                    output = result.stdout + result.stderr
                    if "passed" in output:
                        print(f"   📊 Test output: {output.split('passed')[0].split()[-1]} tests passed")
                    return True
                else:
                    self.errors.append(f"❌ Tests failing - must fix before mission completion")
                    print(f"   💥 Test output: {result.stdout[:200]}...")
                    return False
                    
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        self.warnings.append("⚠️  Could not run tests automatically - manual verification required")
        return True  # Don't fail if we can't run tests automatically
    
    def validate_code_quality(self):
        """Validate code quality standards"""
        print("🔍 Validating Code Quality...")
        
        python_files = list(self.current_dir.rglob("*.py"))
        python_files = [f for f in python_files if not f.name.startswith('.') and 'venv' not in str(f)]
        
        if not python_files:
            self.warnings.append("⚠️  No Python files found to validate")
            return True
        
        quality_issues = []
        
        for py_file in python_files[:10]:  # Check first 10 files
            try:
                content = py_file.read_text()
                
                # Check for basic quality indicators
                functions = re.findall(r'def\s+(\w+)\s*\(', content)
                
                for func in functions:
                    # Check for docstrings (simplified check)
                    func_pattern = rf'def\s+{re.escape(func)}\s*\([^)]*\):\s*"""'
                    if not re.search(func_pattern, content):
                        quality_issues.append(f"Function {func} in {py_file.name} missing docstring")
                
            except Exception as e:
                self.warnings.append(f"⚠️  Could not analyze {py_file.name}: {e}")
        
        if quality_issues:
            self.warnings.extend([f"⚠️  {issue}" for issue in quality_issues[:5]])
            print("⚠️  Some code quality issues found - consider addressing")
        else:
            print("✅ Code quality looks good")
        
        return True
    
    def validate_pull_request(self):
        """Check if pull request exists or is needed"""
        print("🔍 Validating Pull Request Status...")
        
        if not self.git_available:
            return True
        
        try:
            # Check if there are unpushed commits
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                self.warnings.append("⚠️  Uncommitted changes found - commit before creating PR")
            
            # Check if current branch is pushed
            current_branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                                 capture_output=True, text=True, check=True)
            current_branch = current_branch_result.stdout.strip()
            
            # Check if branch exists on remote
            remote_check = subprocess.run(['git', 'ls-remote', '--heads', 'origin', current_branch],
                                        capture_output=True, text=True)
            
            if not remote_check.stdout.strip():
                self.warnings.append(f"⚠️  Branch '{current_branch}' not pushed to remote - push before creating PR")
            else:
                print(f"✅ Branch '{current_branch}' exists on remote")
            
            return True
            
        except subprocess.CalledProcessError:
            self.warnings.append("⚠️  Could not validate PR status - manual verification required")
            return True
    
    def validate_data_organization(self):
        """Validate data is properly organized"""
        print("🔍 Validating Data Organization...")
        
        data_sets_path = Path("/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets")
        
        if not data_sets_path.exists():
            self.errors.append("❌ Data_Sets directory not found at expected location")
            return False
        
        # Check for common data files in wrong locations
        wrong_locations = []
        common_data_extensions = ['.csv', '.json', '.xlsx', '.shp', '.geojson']
        
        for ext in common_data_extensions:
            files = list(self.current_dir.rglob(f"*{ext}"))
            # Filter out files that are in the correct Data_Sets location
            wrong_files = [f for f in files if not str(f).startswith(str(data_sets_path))]
            wrong_locations.extend(wrong_files)
        
        if wrong_locations:
            self.warnings.append(f"⚠️  Found {len(wrong_locations)} data files outside Data_Sets directory")
            for file in wrong_locations[:3]:
                print(f"   📁 {file.relative_to(self.current_dir)} should be in Data_Sets/")
        else:
            print("✅ Data organization looks good")
        
        return True
    
    def generate_report(self):
        """Generate validation report"""
        print("\n" + "="*60)
        print("📋 WORKFLOW VALIDATION REPORT")
        print("="*60)
        
        if self.mission_name:
            print(f"Mission: {self.mission_name}")
        print(f"Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Directory: {self.current_dir}")
        
        print(f"\n📊 Summary:")
        print(f"   ❌ Errors: {len(self.errors)}")
        print(f"   ⚠️  Warnings: {len(self.warnings)}")
        
        if self.errors:
            print("\n❌ CRITICAL ERRORS (Must Fix):")
            for error in self.errors:
                print(f"   {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS (Should Address):")
            for warning in self.warnings:
                print(f"   {warning}")
        
        success = len(self.errors) == 0
        
        if success:
            print("\n✅ VALIDATION PASSED")
            print("   Mission can proceed to completion")
        else:
            print("\n❌ VALIDATION FAILED")
            print("   Fix errors before marking mission complete")
        
        print("="*60)
        
        return success
    
    def run_full_validation(self):
        """Run complete workflow validation"""
        print("🚀 Starting Workflow Validation...")
        print(f"📁 Working Directory: {self.current_dir}")
        
        # Run all validation checks
        validations = [
            self.validate_git_branch,
            self.validate_test_plan,
            self.validate_tests_exist,
            self.run_tests,
            self.validate_code_quality,
            self.validate_pull_request,
            self.validate_data_organization
        ]
        
        for validation in validations:
            try:
                validation()
            except Exception as e:
                self.errors.append(f"❌ Validation error: {validation.__name__} failed: {e}")
            print()  # Add space between validations
        
        return self.generate_report()


def main():
    """Main validation script entry point"""
    mission_name = None
    if len(sys.argv) > 1:
        mission_name = sys.argv[1]
    
    validator = WorkflowValidator(mission_name)
    success = validator.run_full_validation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()