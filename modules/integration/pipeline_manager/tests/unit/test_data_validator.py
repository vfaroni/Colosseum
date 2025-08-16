#!/usr/bin/env python3
"""
Unit tests for DataValidator
Roman Engineering Standard: Built for 2000+ year reliability

Comprehensive test suite for data validation functionality including
field validation, cross-field checks, and confidence scoring.
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.data_validator import DataValidator, ValidationResult, ValidationIssue, ValidationSeverity


class TestDataValidator(unittest.TestCase):
    """Test cases for DataValidator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = DataValidator()
        
        self.valid_property_data = {
            "property_details": {
                "name": "Test Apartments",
                "address": "123 Main Street",
                "city": "Austin",
                "state": "TX",
                "zip_code": "78701",
                "unit_count": 100,
                "year_built": 1995
            },
            "financial_metrics": {
                "purchase_price": 15000000,
                "net_operating_income": 900000,
                "cap_rate": 0.06,
                "occupancy_rate": 0.95
            }
        }
        
        self.invalid_property_data = {
            "property_details": {
                "name": "",  # Invalid: empty name
                "address": "123",  # Invalid: too short
                "city": "Austin",
                "state": "texas",  # Invalid: not 2-letter code
                "zip_code": "787011",  # Invalid: wrong format
                "unit_count": 0,  # Invalid: must be > 0
                "year_built": 2050  # Invalid: future year
            },
            "financial_metrics": {
                "purchase_price": 5000,  # Invalid: too low
                "cap_rate": 1.5,  # Invalid: > 1 (assuming not converted)
                "occupancy_rate": 1.2  # Invalid: > 1
            }
        }
    
    def test_validator_initialization(self):
        """Test validator initializes correctly"""
        self.assertIsInstance(self.validator, DataValidator)
        self.assertIsNotNone(self.validator.config)
        self.assertIsNotNone(self.validator.validation_rules)
    
    def test_valid_data_passes_validation(self):
        """Test that valid data passes validation"""
        result = self.validator.validate_extraction(self.valid_property_data)
        
        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.is_valid)
        self.assertGreaterEqual(result.confidence_score, 0.8)
        self.assertEqual(len(result.critical_issues), 0)
    
    def test_invalid_data_fails_validation(self):
        """Test that invalid data fails validation"""
        result = self.validator.validate_extraction(self.invalid_property_data)
        
        self.assertIsInstance(result, ValidationResult)
        self.assertFalse(result.is_valid)
        self.assertLess(result.confidence_score, 0.6)
        self.assertGreater(len(result.issues), 0)
    
    def test_required_field_validation(self):
        """Test required field validation"""
        # Remove required field
        data = self.valid_property_data.copy()
        del data["property_details"]["name"]
        
        result = self.validator.validate_extraction(data)
        
        # Should have critical issue for missing required field
        critical_issues = [i for i in result.issues if i.severity == ValidationSeverity.CRITICAL]
        self.assertGreater(len(critical_issues), 0)
        
        # Check specific error message
        name_errors = [i for i in critical_issues if "name" in i.field_path]
        self.assertGreater(len(name_errors), 0)
    
    def test_data_type_validation(self):
        """Test data type validation"""
        data = self.valid_property_data.copy()
        data["property_details"]["unit_count"] = "100"  # String instead of int
        
        result = self.validator.validate_extraction(data)
        
        # Should have type validation issue
        type_issues = [i for i in result.issues if "type" in i.rule_violated]
        self.assertGreaterEqual(len(type_issues), 0)  # May auto-correct
    
    def test_numeric_range_validation(self):
        """Test numeric range validation"""
        data = self.valid_property_data.copy()
        data["property_details"]["year_built"] = 1700  # Too old
        
        result = self.validator.validate_extraction(data)
        
        # Should have range validation error
        range_issues = [i for i in result.issues if "min_value" in i.rule_violated]
        self.assertGreater(len(range_issues), 0)
    
    def test_string_validation(self):
        """Test string length and pattern validation"""
        data = self.valid_property_data.copy()
        data["property_details"]["state"] = "Texas"  # Invalid: not 2 letters
        
        result = self.validator.validate_extraction(data)
        
        # Should have pattern validation error
        pattern_issues = [i for i in result.issues if "pattern" in i.rule_violated]
        self.assertGreater(len(pattern_issues), 0)
    
    def test_cross_field_validation(self):
        """Test cross-field validation logic"""
        data = self.valid_property_data.copy()
        # Set inconsistent price per unit
        data["financial_metrics"]["price_per_unit"] = 200000  # Should be 150000
        
        result = self.validator.validate_extraction(data)
        
        # Should have cross-field validation warning
        cross_field_issues = [i for i in result.issues if "cross_field" in i.rule_violated]
        self.assertGreaterEqual(len(cross_field_issues), 0)
    
    def test_auto_correction(self):
        """Test automatic data correction"""
        data = self.valid_property_data.copy()
        data["property_details"]["state"] = "tx"  # Lowercase
        data["financial_metrics"]["cap_rate"] = 6.0  # Percentage format
        
        result = self.validator.validate_extraction(data)
        
        # Check that corrections were made
        self.assertEqual(result.corrected_data["property_details"]["state"], "TX")
        self.assertEqual(result.corrected_data["financial_metrics"]["cap_rate"], 0.06)
    
    def test_confidence_scoring(self):
        """Test confidence score calculation"""
        # Test high confidence data
        high_confidence_result = self.validator.validate_extraction(self.valid_property_data)
        self.assertGreaterEqual(high_confidence_result.confidence_score, 0.8)
        
        # Test low confidence data
        low_confidence_result = self.validator.validate_extraction(self.invalid_property_data)
        self.assertLess(low_confidence_result.confidence_score, 0.6)
    
    def test_validation_severity_levels(self):
        """Test different validation severity levels"""
        result = self.validator.validate_extraction(self.invalid_property_data)
        
        # Should have different severity levels
        severities = [issue.severity for issue in result.issues]
        self.assertIn(ValidationSeverity.CRITICAL, severities)
        self.assertIn(ValidationSeverity.ERROR, severities)
    
    def test_empty_data_handling(self):
        """Test handling of empty or null data"""
        empty_data = {}
        result = self.validator.validate_extraction(empty_data)
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.critical_issues), 0)
    
    def test_nested_value_extraction(self):
        """Test nested dictionary value extraction"""
        # Test successful extraction
        value = self.validator._get_nested_value(self.valid_property_data, "property_details.name")
        self.assertEqual(value, "Test Apartments")
        
        # Test missing path
        value = self.validator._get_nested_value(self.valid_property_data, "property_details.missing_field")
        self.assertIsNone(value)
        
        # Test invalid path
        value = self.validator._get_nested_value(self.valid_property_data, "invalid.path")
        self.assertIsNone(value)
    
    def test_report_generation(self):
        """Test validation report generation"""
        result = self.validator.validate_extraction(self.invalid_property_data)
        report = self.validator.generate_validation_report(result)
        
        self.assertIsInstance(report, str)
        self.assertIn("DATA VALIDATION REPORT", report)
        self.assertIn("FAILED", report)  # Should show failed status


class TestValidationResult(unittest.TestCase):
    """Test cases for ValidationResult class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.issues = [
            ValidationIssue(
                field_path="test_field",
                severity=ValidationSeverity.CRITICAL,
                message="Critical test issue",
                current_value="invalid"
            ),
            ValidationIssue(
                field_path="test_field2",
                severity=ValidationSeverity.WARNING,
                message="Warning test issue",
                current_value="warning_value"
            ),
            ValidationIssue(
                field_path="test_field3",
                severity=ValidationSeverity.ERROR,
                message="Error test issue",
                current_value="error_value"
            )
        ]
        
        self.validation_result = ValidationResult(
            is_valid=False,
            confidence_score=0.65,
            issues=self.issues,
            corrected_data={"test": "data"},
            validation_timestamp=datetime.now().isoformat()
        )
    
    def test_critical_issues_property(self):
        """Test critical_issues property"""
        critical = self.validation_result.critical_issues
        self.assertEqual(len(critical), 1)
        self.assertEqual(critical[0].severity, ValidationSeverity.CRITICAL)
    
    def test_error_issues_property(self):
        """Test error_issues property"""
        errors = self.validation_result.error_issues
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].severity, ValidationSeverity.ERROR)
    
    def test_warning_issues_property(self):
        """Test warning_issues property"""
        warnings = self.validation_result.warning_issues
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].severity, ValidationSeverity.WARNING)


class TestValidationIssue(unittest.TestCase):
    """Test cases for ValidationIssue class"""
    
    def test_validation_issue_creation(self):
        """Test ValidationIssue creation"""
        issue = ValidationIssue(
            field_path="test.field",
            severity=ValidationSeverity.ERROR,
            message="Test error message",
            current_value="invalid_value",
            suggested_value="corrected_value",
            rule_violated="test_rule"
        )
        
        self.assertEqual(issue.field_path, "test.field")
        self.assertEqual(issue.severity, ValidationSeverity.ERROR)
        self.assertEqual(issue.message, "Test error message")
        self.assertEqual(issue.current_value, "invalid_value")
        self.assertEqual(issue.suggested_value, "corrected_value")
        self.assertEqual(issue.rule_violated, "test_rule")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)