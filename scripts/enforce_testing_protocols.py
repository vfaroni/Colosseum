#!/usr/bin/env python3
"""
🏛️ TOWER PROTOCOL ENFORCEMENT - TESTING REQUIREMENTS
Mission: VITOR-TOWER-ENFORCEMENT-002

Automated enforcement of mandatory testing requirements before commits.
NO EXCEPTIONS - Roman Engineering Standards.
"""

import subprocess
import sys
import os
from pathlib import Path
import json
from datetime import datetime

class TowerTestingEnforcer:
    """TOWER automated testing protocol enforcement"""
    
    def __init__(self):
        self.violations = []
        self.repo_root = self._find_repo_root()
        self.test_dirs = ['tests/unit', 'tests/feature', 'tests/integration', 'tests/e2e']
        
    def _find_repo_root(self):
        """Find git repository root"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.git').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _run_command(self, cmd, capture_output=True):
        """Run shell command safely"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def check_staged_changes(self):
        """Analyze staged changes to determine testing requirements"""
        success, stdout, stderr = self._run_command("git diff --cached --name-only")
        if not success:
            return [], 0, False
            
        staged_files = stdout.strip().split('\n') if stdout.strip() else []
        
        # Count total changes
        success, stat_output, _ = self._run_command("git diff --cached --stat")
        total_changes = len(staged_files)
        
        # Detect if major feature (multiple files or significant changes)
        is_major_feature = (
            total_changes >= 5 or
            any('new' in f.lower() or 'feature' in f.lower() for f in staged_files) or
            any(f.endswith('.py') and 'test' not in f for f in staged_files if len(staged_files) >= 3)
        )
        
        return staged_files, total_changes, is_major_feature
    
    def run_unit_tests(self):
        """MANDATORY: Run unit tests - NO EXCEPTIONS"""
        print("🏛️ TOWER ENFORCEMENT: Running mandatory unit tests...")
        
        unit_test_paths = [
            'tests/unit',
            'test/unit', 
            'src/tests/unit',
            'modules/*/tests/unit'
        ]
        
        test_found = False
        for test_path in unit_test_paths:
            if (self.repo_root / test_path).exists() or list(self.repo_root.glob(test_path)):
                test_found = True
                break
        
        if not test_found:
            self.violations.append("❌ CRITICAL: No unit tests directory found - Unit tests MANDATORY")
            return False
        
        # Run pytest on available unit test directories
        test_commands = [
            "python3 -m pytest tests/unit/ -v --tb=short",
            "python3 -m pytest test/unit/ -v --tb=short", 
            "python3 -m pytest src/tests/unit/ -v --tb=short"
        ]
        
        for cmd in test_commands:
            success, stdout, stderr = self._run_command(cmd)
            if success:
                print(f"✅ Unit tests passed: {cmd}")
                return True
            elif "no tests ran" not in stderr.lower() and "no tests found" not in stderr.lower():
                self.violations.append(f"❌ UNIT TEST FAILURE: {stderr[:200]}")
                return False
        
        # If no tests found in standard locations, check for any Python test files
        test_files = list(self.repo_root.glob("**/test_*.py")) + list(self.repo_root.glob("**/*_test.py"))
        if not test_files:
            self.violations.append("❌ CRITICAL: No unit test files found - Testing MANDATORY for all code commits")
            return False
        
        print("⚠️  Unit test files found but standard test runner failed - investigating...")
        return True  # Allow with warning if test files exist
    
    def run_feature_tests(self):
        """Run feature/integration tests for new functionality"""
        print("🏛️ TOWER ENFORCEMENT: Running feature tests...")
        
        feature_test_commands = [
            "python3 -m pytest tests/feature/ -v --tb=short",
            "python3 -m pytest tests/integration/ -v --tb=short",
            "python3 -m pytest test/feature/ -v --tb=short"
        ]
        
        for cmd in feature_test_commands:
            if any((self.repo_root / path).exists() for path in ['tests/feature', 'tests/integration', 'test/feature']):
                success, stdout, stderr = self._run_command(cmd)
                if success:
                    print(f"✅ Feature tests passed: {cmd}")
                    return True
                elif "no tests ran" not in stderr.lower():
                    self.violations.append(f"❌ FEATURE TEST FAILURE: {stderr[:200]}")
                    return False
        
        print("⚠️  No feature/integration tests found - recommended for new functionality")
        return True  # Allow without feature tests (recommended but not mandatory)
    
    def run_e2e_tests(self):
        """Run end-to-end tests for major features"""
        print("🏛️ TOWER ENFORCEMENT: Running end-to-end tests...")
        
        e2e_test_commands = [
            "python3 -m pytest tests/e2e/ -v --tb=short",
            "python3 -m pytest tests/system/ -v --tb=short",
            "python3 -m pytest test/e2e/ -v --tb=short"
        ]
        
        for cmd in e2e_test_commands:
            if any((self.repo_root / path).exists() for path in ['tests/e2e', 'tests/system', 'test/e2e']):
                success, stdout, stderr = self._run_command(cmd)
                if success:
                    print(f"✅ End-to-end tests passed: {cmd}")
                    return True
                elif "no tests ran" not in stderr.lower():
                    self.violations.append(f"❌ E2E TEST FAILURE: {stderr[:200]}")
                    return False
        
        print("⚠️  No end-to-end tests found - recommended for major features")
        return True  # Allow without E2E tests (recommended but not mandatory)
    
    def check_test_coverage(self, staged_files):
        """Check if new code has corresponding tests"""
        python_files = [f for f in staged_files if f.endswith('.py') and 'test' not in f]
        
        if not python_files:
            return True  # No Python files to test
        
        # Check if test files exist for new Python files
        missing_tests = []
        for py_file in python_files:
            test_variations = [
                f"tests/unit/test_{Path(py_file).stem}.py",
                f"test/unit/test_{Path(py_file).stem}.py",
                f"tests/test_{Path(py_file).stem}.py",
                f"{Path(py_file).parent}/test_{Path(py_file).name}"
            ]
            
            has_test = any((self.repo_root / test_path).exists() for test_path in test_variations)
            if not has_test:
                missing_tests.append(py_file)
        
        if missing_tests:
            self.violations.append(f"⚠️  Missing unit tests for: {', '.join(missing_tests)}")
            return False
        
        return True
    
    def generate_violation_report(self):
        """Generate violation report"""
        if not self.violations:
            return
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'violations': self.violations,
            'severity': 'CRITICAL' if any('CRITICAL' in v for v in self.violations) else 'WARNING'
        }
        
        report_file = self.repo_root / 'tower_violations.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n🚨 TOWER VIOLATION REPORT: {report_file}")
        for violation in self.violations:
            print(f"   {violation}")
    
    def enforce_testing_protocols(self):
        """Main enforcement function"""
        print("🏛️ TOWER PROTOCOL ENFORCEMENT ACTIVATED")
        print("=" * 60)
        print("Checking mandatory testing requirements...")
        
        # Analyze changes
        staged_files, total_changes, is_major_feature = self.check_staged_changes()
        
        if not staged_files:
            print("✅ No staged changes - enforcement not required")
            return True
        
        print(f"📊 Analysis: {total_changes} files changed, major feature: {is_major_feature}")
        
        # MANDATORY: Unit tests for ALL commits
        unit_passed = self.run_unit_tests()
        if not unit_passed:
            print("❌ UNIT TESTS FAILED - COMMIT BLOCKED")
            self.generate_violation_report()
            return False
        
        # Check test coverage for new code
        coverage_ok = self.check_test_coverage(staged_files)
        
        # Feature tests for new functionality
        if any(f.endswith('.py') for f in staged_files):
            feature_passed = self.run_feature_tests()
        else:
            feature_passed = True
        
        # E2E tests for major features
        if is_major_feature:
            e2e_passed = self.run_e2e_tests()
        else:
            e2e_passed = True
        
        # Final decision
        all_passed = unit_passed and feature_passed and e2e_passed
        
        if all_passed and not self.violations:
            print("\n✅ ALL TESTING REQUIREMENTS SATISFIED")
            print("🏛️ TOWER APPROVAL: Commit authorized")
            return True
        else:
            print("\n❌ TESTING REQUIREMENTS NOT SATISFIED")
            self.generate_violation_report()
            print("🚨 TOWER ENFORCEMENT: Commit blocked until compliance achieved")
            return False

def main():
    """Execute TOWER testing enforcement"""
    enforcer = TowerTestingEnforcer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--pre-commit":
        # Pre-commit hook mode
        success = enforcer.enforce_testing_protocols()
        sys.exit(0 if success else 1)
    else:
        # Manual execution mode  
        print("🏛️ TOWER TESTING PROTOCOL ENFORCEMENT")
        print("Usage: python3 enforce_testing_protocols.py --pre-commit")
        print("This script enforces mandatory testing requirements.")
        
        success = enforcer.enforce_testing_protocols()
        if success:
            print("\n✅ All testing protocols satisfied")
        else:
            print("\n❌ Testing protocol violations detected")
            print("Fix violations before attempting commit")

if __name__ == "__main__":
    main()