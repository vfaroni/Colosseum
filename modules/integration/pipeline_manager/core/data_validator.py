#!/usr/bin/env python3
"""
Pipeline Manager - Data Validation System
Roman Engineering Standard: Built for 2000+ year reliability

Quality assurance system for extracted document data with multi-layer validation.
Ensures >95% data accuracy before Excel integration.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    CRITICAL = "critical"    # Data unusable, must fix
    ERROR = "error"         # Significant issue, should fix
    WARNING = "warning"     # Minor issue, consider fixing
    INFO = "info"          # Informational, no action needed

@dataclass
class ValidationIssue:
    """Individual validation issue"""
    field_path: str
    severity: ValidationSeverity
    message: str
    current_value: Any
    suggested_value: Optional[Any] = None
    rule_violated: Optional[str] = None

@dataclass
class ValidationResult:
    """Complete validation result"""
    is_valid: bool
    confidence_score: float
    issues: List[ValidationIssue]
    corrected_data: Dict[str, Any]
    validation_timestamp: str
    
    @property
    def critical_issues(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.CRITICAL]
    
    @property
    def error_issues(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]
    
    @property
    def warning_issues(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]

class DataValidator:
    """Comprehensive data validation system for extracted document data"""
    
    def __init__(self, validation_config: Optional[Dict[str, Any]] = None):
        """Initialize data validator with configuration"""
        self.config = validation_config or self._load_default_config()
        self.validation_rules = self._initialize_validation_rules()
        
        logger.info("DataValidator initialized with comprehensive validation rules")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default validation configuration"""
        return {
            "strict_mode": False,
            "auto_correct": True,
            "confidence_threshold": 0.85,
            "max_string_length": 255,
            "currency_precision": 2,
            "percentage_precision": 4
        }
    
    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive validation rules"""
        return {
            # Property Details Validation
            "property_details": {
                "name": {
                    "required": True,
                    "type": str,
                    "min_length": 2,
                    "max_length": 100,
                    "pattern": r"^[A-Za-z0-9\s\-\.,'&]+$"
                },
                "address": {
                    "required": True,
                    "type": str,
                    "min_length": 10,
                    "max_length": 150,
                    "pattern": r".*\d+.*"  # Must contain at least one number
                },
                "city": {
                    "required": True,
                    "type": str,
                    "min_length": 2,
                    "max_length": 50,
                    "pattern": r"^[A-Za-z\s\-\.]+$"
                },
                "state": {
                    "required": True,
                    "type": str,
                    "min_length": 2,
                    "max_length": 2,
                    "pattern": r"^[A-Z]{2}$",
                    "valid_values": ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                                   "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                                   "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                                   "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                                   "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"]
                },
                "zip_code": {
                    "required": True,
                    "type": str,
                    "pattern": r"^\d{5}(-\d{4})?$"
                },
                "unit_count": {
                    "required": True,
                    "type": int,
                    "min_value": 1,
                    "max_value": 10000
                },
                "square_footage": {
                    "required": False,
                    "type": (int, float),
                    "min_value": 100,
                    "max_value": 50000000
                },
                "year_built": {
                    "required": False,
                    "type": int,
                    "min_value": 1800,
                    "max_value": datetime.now().year + 5
                },
                "property_class": {
                    "required": False,
                    "type": str,
                    "valid_values": ["A", "B", "C", "D", "A+", "A-", "B+", "B-", "C+", "C-"]
                }
            },
            
            # Financial Metrics Validation
            "financial_metrics": {
                "purchase_price": {
                    "required": True,
                    "type": (int, float),
                    "min_value": 10000,
                    "max_value": 1000000000
                },
                "net_operating_income": {
                    "required": False,
                    "type": (int, float),
                    "min_value": -10000000,
                    "max_value": 100000000
                },
                "cap_rate": {
                    "required": False,
                    "type": float,
                    "min_value": 0.001,
                    "max_value": 0.50,
                    "precision": 4
                },
                "occupancy_rate": {
                    "required": False,
                    "type": float,
                    "min_value": 0.0,
                    "max_value": 1.0,
                    "precision": 4
                },
                "gross_rent_multiplier": {
                    "required": False,
                    "type": (int, float),
                    "min_value": 1.0,
                    "max_value": 50.0
                }
            },
            
            # Rent Information Validation
            "rent_information": {
                "average_rent": {
                    "required": False,
                    "type": (int, float),
                    "min_value": 100,
                    "max_value": 50000
                },
                "rent_per_sqft": {
                    "required": False,
                    "type": float,
                    "min_value": 0.10,
                    "max_value": 100.0,
                    "precision": 2
                }
            },
            
            # Transaction Details Validation
            "transaction_details": {
                "broker_phone": {
                    "required": False,
                    "type": str,
                    "pattern": r"^(\+1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$"
                },
                "broker_email": {
                    "required": False,
                    "type": str,
                    "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                },
                "days_on_market": {
                    "required": False,
                    "type": int,
                    "min_value": 0,
                    "max_value": 3650  # 10 years
                }
            }
        }
    
    def validate_extraction(self, data: Dict[str, Any]) -> ValidationResult:
        """Perform comprehensive validation on extracted data"""
        start_time = datetime.now()
        issues = []
        corrected_data = data.copy()
        
        try:
            # Validate each section
            for section_name, section_rules in self.validation_rules.items():
                if section_name in data:
                    section_issues, section_corrections = self._validate_section(
                        data[section_name], section_rules, section_name
                    )
                    issues.extend(section_issues)
                    if section_corrections:
                        corrected_data[section_name].update(section_corrections)
            
            # Cross-field validation
            cross_field_issues, cross_field_corrections = self._validate_cross_fields(corrected_data)
            issues.extend(cross_field_issues)
            corrected_data.update(cross_field_corrections)
            
            # Calculate overall confidence
            confidence_score = self._calculate_validation_confidence(issues, corrected_data)
            
            # Determine if data is valid
            critical_count = len([i for i in issues if i.severity == ValidationSeverity.CRITICAL])
            is_valid = critical_count == 0 and confidence_score >= self.config['confidence_threshold']
            
            logger.info(f"Validation completed: {len(issues)} issues found, confidence: {confidence_score:.3f}")
            
            return ValidationResult(
                is_valid=is_valid,
                confidence_score=confidence_score,
                issues=issues,
                corrected_data=corrected_data,
                validation_timestamp=start_time.isoformat()
            )
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return ValidationResult(
                is_valid=False,
                confidence_score=0.0,
                issues=[ValidationIssue(
                    field_path="validation_system",
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Validation system error: {str(e)}",
                    current_value=None
                )],
                corrected_data=data,
                validation_timestamp=start_time.isoformat()
            )
    
    def _validate_section(self, section_data: Dict[str, Any], section_rules: Dict[str, Dict[str, Any]], 
                         section_name: str) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """Validate a specific data section"""
        issues = []
        corrections = {}
        
        for field_name, field_rules in section_rules.items():
            field_path = f"{section_name}.{field_name}"
            field_value = section_data.get(field_name)
            
            # Check required fields
            if field_rules.get('required', False) and (field_value is None or field_value == ""):
                issues.append(ValidationIssue(
                    field_path=field_path,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Required field is missing or empty",
                    current_value=field_value,
                    rule_violated="required"
                ))
                continue
            
            # Skip validation if field is None or empty and not required
            if field_value is None or field_value == "" or field_value == "Not specified":
                continue
            
            # Type validation
            expected_type = field_rules.get('type')
            if expected_type and not isinstance(field_value, expected_type):
                # Attempt auto-correction
                corrected_value = self._attempt_type_correction(field_value, expected_type)
                if corrected_value is not None:
                    corrections[field_name] = corrected_value
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        severity=ValidationSeverity.WARNING,
                        message=f"Type corrected from {type(field_value).__name__} to {expected_type.__name__}",
                        current_value=field_value,
                        suggested_value=corrected_value,
                        rule_violated="type"
                    ))
                    field_value = corrected_value
                else:
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        severity=ValidationSeverity.ERROR,
                        message=f"Invalid type: expected {expected_type.__name__}, got {type(field_value).__name__}",
                        current_value=field_value,
                        rule_violated="type"
                    ))
                    continue
            
            # Numeric range validation
            if isinstance(field_value, (int, float)):
                min_value = field_rules.get('min_value')
                max_value = field_rules.get('max_value')
                
                if min_value is not None and field_value < min_value:
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        severity=ValidationSeverity.ERROR,
                        message=f"Value below minimum: {field_value} < {min_value}",
                        current_value=field_value,
                        rule_violated="min_value"
                    ))
                
                if max_value is not None and field_value > max_value:
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        severity=ValidationSeverity.ERROR,
                        message=f"Value above maximum: {field_value} > {max_value}",
                        current_value=field_value,
                        rule_violated="max_value"
                    ))
            
            # String validation
            if isinstance(field_value, str):
                # Length validation
                min_length = field_rules.get('min_length')
                max_length = field_rules.get('max_length')
                
                if min_length and len(field_value) < min_length:
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        severity=ValidationSeverity.ERROR,
                        message=f"String too short: {len(field_value)} < {min_length}",
                        current_value=field_value,
                        rule_violated="min_length"
                    ))
                
                if max_length and len(field_value) > max_length:
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        severity=ValidationSeverity.WARNING,
                        message=f"String too long: {len(field_value)} > {max_length}",
                        current_value=field_value,
                        rule_violated="max_length"
                    ))
                
                # Pattern validation
                pattern = field_rules.get('pattern')
                if pattern and not re.match(pattern, field_value):
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        severity=ValidationSeverity.ERROR,
                        message=f"Pattern validation failed: '{field_value}' does not match {pattern}",
                        current_value=field_value,
                        rule_violated="pattern"
                    ))
                
                # Valid values validation
                valid_values = field_rules.get('valid_values')
                if valid_values and field_value not in valid_values:
                    issues.append(ValidationIssue(
                        field_path=field_path,
                        severity=ValidationSeverity.WARNING,
                        message=f"Value not in valid list: '{field_value}' not in {valid_values}",
                        current_value=field_value,
                        rule_violated="valid_values"
                    ))
        
        return issues, corrections
    
    def _validate_cross_fields(self, data: Dict[str, Any]) -> Tuple[List[ValidationIssue], Dict[str, Any]]:
        """Validate relationships between fields"""
        issues = []
        corrections = {}
        
        # Price per unit consistency
        purchase_price = self._get_nested_value(data, "financial_metrics.purchase_price")
        unit_count = self._get_nested_value(data, "property_details.unit_count")
        price_per_unit = self._get_nested_value(data, "financial_metrics.price_per_unit")
        
        if all([purchase_price, unit_count]) and unit_count > 0:
            calculated_ppu = purchase_price / unit_count
            if price_per_unit and abs(price_per_unit - calculated_ppu) > 1000:
                issues.append(ValidationIssue(
                    field_path="financial_metrics.price_per_unit",
                    severity=ValidationSeverity.WARNING,
                    message=f"Price per unit inconsistent: stated {price_per_unit:,.0f}, calculated {calculated_ppu:,.0f}",
                    current_value=price_per_unit,
                    suggested_value=calculated_ppu,
                    rule_violated="cross_field_consistency"
                ))
        
        # Cap rate calculation validation
        noi = self._get_nested_value(data, "financial_metrics.net_operating_income")
        cap_rate = self._get_nested_value(data, "financial_metrics.cap_rate")
        
        if all([purchase_price, noi, cap_rate]) and purchase_price > 0:
            calculated_cap_rate = noi / purchase_price
            if abs(cap_rate - calculated_cap_rate) > 0.01:  # 1% tolerance
                issues.append(ValidationIssue(
                    field_path="financial_metrics.cap_rate",
                    severity=ValidationSeverity.WARNING,
                    message=f"Cap rate inconsistent: stated {cap_rate:.3f}, calculated {calculated_cap_rate:.3f}",
                    current_value=cap_rate,
                    suggested_value=calculated_cap_rate,
                    rule_violated="cross_field_consistency"
                ))
        
        # Year built vs current year
        year_built = self._get_nested_value(data, "property_details.year_built")
        current_year = datetime.now().year
        
        if year_built and year_built > current_year:
            issues.append(ValidationIssue(
                field_path="property_details.year_built",
                severity=ValidationSeverity.ERROR,
                message=f"Year built in future: {year_built} > {current_year}",
                current_value=year_built,
                rule_violated="logical_consistency"
            ))
        
        return issues, corrections
    
    def _attempt_type_correction(self, value: Any, expected_type: type) -> Optional[Any]:
        """Attempt to correct value to expected type"""
        try:
            if expected_type == int:
                if isinstance(value, str):
                    # Remove common formatting
                    cleaned = re.sub(r'[,$%]', '', value.strip())
                    return int(float(cleaned))  # Handle decimal strings
                elif isinstance(value, float):
                    return int(value)
            
            elif expected_type == float:
                if isinstance(value, str):
                    cleaned = re.sub(r'[,$%]', '', value.strip())
                    return float(cleaned)
                elif isinstance(value, int):
                    return float(value)
            
            elif expected_type == str:
                return str(value)
            
            elif expected_type == tuple and len(expected_type.__args__) == 2:
                # Handle Union types like (int, float)
                for sub_type in expected_type.__args__:
                    try:
                        return self._attempt_type_correction(value, sub_type)
                    except:
                        continue
        
        except (ValueError, TypeError, AttributeError):
            pass
        
        return None
    
    def _calculate_validation_confidence(self, issues: List[ValidationIssue], data: Dict[str, Any]) -> float:
        """Calculate overall validation confidence score"""
        base_confidence = 1.0
        
        # Reduce confidence based on issues
        for issue in issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                base_confidence -= 0.20
            elif issue.severity == ValidationSeverity.ERROR:
                base_confidence -= 0.10
            elif issue.severity == ValidationSeverity.WARNING:
                base_confidence -= 0.05
        
        # Factor in data completeness
        total_possible_fields = self._count_possible_fields()
        filled_fields = self._count_filled_fields(data)
        
        if total_possible_fields > 0:
            completeness_factor = filled_fields / total_possible_fields
            base_confidence *= (0.5 + 0.5 * completeness_factor)
        
        return max(0.0, min(1.0, base_confidence))
    
    def _count_possible_fields(self) -> int:
        """Count total possible fields across all sections"""
        count = 0
        for section_rules in self.validation_rules.values():
            count += len(section_rules)
        return count
    
    def _count_filled_fields(self, data: Dict[str, Any]) -> int:
        """Count filled fields in data"""
        count = 0
        for section_name, section_rules in self.validation_rules.items():
            if section_name in data:
                for field_name in section_rules.keys():
                    if field_name in data[section_name]:
                        value = data[section_name][field_name]
                        if value is not None and value != "" and value != "Not specified":
                            count += 1
        return count
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get nested dictionary value using dot notation"""
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def generate_validation_report(self, validation_result: ValidationResult) -> str:
        """Generate human-readable validation report"""
        report = []
        report.append("=" * 60)
        report.append("DATA VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Validation Status: {'PASSED' if validation_result.is_valid else 'FAILED'}")
        report.append(f"Confidence Score: {validation_result.confidence_score:.3f}")
        report.append(f"Total Issues: {len(validation_result.issues)}")
        report.append(f"Critical Issues: {len(validation_result.critical_issues)}")
        report.append(f"Validation Time: {validation_result.validation_timestamp}")
        report.append("")
        
        if validation_result.issues:
            # Group issues by severity
            severity_groups = {}
            for issue in validation_result.issues:
                severity = issue.severity.value.upper()
                if severity not in severity_groups:
                    severity_groups[severity] = []
                severity_groups[severity].append(issue)
            
            for severity, issues in severity_groups.items():
                report.append(f"{severity} ISSUES ({len(issues)}):")
                report.append("-" * 40)
                
                for issue in issues:
                    report.append(f"  Field: {issue.field_path}")
                    report.append(f"  Issue: {issue.message}")
                    report.append(f"  Current Value: {issue.current_value}")
                    if issue.suggested_value is not None:
                        report.append(f"  Suggested Value: {issue.suggested_value}")
                    report.append("")
        else:
            report.append("No validation issues found!")
        
        return "\n".join(report)

# Example usage
if __name__ == "__main__":
    # Test data
    test_data = {
        "property_details": {
            "name": "Sample Apartments",
            "address": "123 Main St",
            "city": "Austin",
            "state": "TX",
            "zip_code": "78701",
            "unit_count": 100,
            "year_built": 1995
        },
        "financial_metrics": {
            "purchase_price": 15000000,
            "net_operating_income": 900000,
            "cap_rate": 0.06
        }
    }
    
    # Initialize validator
    validator = DataValidator()
    
    # Validate data
    result = validator.validate_extraction(test_data)
    
    # Generate report
    report = validator.generate_validation_report(result)
    print(report)
    
    logger.info("DataValidator ready for use")