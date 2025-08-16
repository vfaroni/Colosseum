#!/usr/bin/env python3
"""
CTCAC Validation Suite
Mathematical and business validation framework
WINGMAN-01 Mission Implementation
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from ctcac_data_structures import (
    SourcesUsesData, BasisBreakdownData, ApplicationData, 
    CTCACExtractionResult, ValidationResult
)

class CTCACValidationSuite:
    """
    Comprehensive validation suite for CTCAC extraction data
    Ensures 100% mathematical accuracy and business logic compliance
    """
    
    def __init__(self, tolerance: float = 1.0):
        """
        Initialize validation suite
        
        Args:
            tolerance: Dollar tolerance for mathematical comparisons (default $1.00)
        """
        self.tolerance = tolerance
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize business validation rules"""
        return {
            "min_project_cost": 100000,      # Minimum reasonable project cost
            "max_project_cost": 1000000000,  # Maximum reasonable project cost  
            "min_units": 1,                  # Minimum units
            "max_units": 1000,               # Maximum reasonable units
            "min_cost_per_unit": 50000,      # Minimum cost per unit
            "max_cost_per_unit": 2000000,    # Maximum cost per unit
            "min_eligible_basis": 10000,     # Minimum eligible basis
            "max_leverage_ratio": 10.0,      # Maximum debt-to-equity ratio
            "required_line_items": [         # Required Sources & Uses line items
                "land", "construction", "soft costs"
            ]
        }
    
    def validate_sources_uses_math(self, data: SourcesUsesData) -> ValidationResult:
        """
        Validate Sources and Uses mathematical accuracy
        Verifies row totals = sum of funding sources
        """
        
        validation = ValidationResult()
        validation.validation_timestamp = datetime.now().isoformat()
        
        try:
            print(f"🔍 Validating Sources & Uses mathematics...")
            
            if not data.total_costs or not data.funding_matrix:
                validation.add_error("Missing essential data for validation")
                return validation
            
            # Ensure equal dimensions
            if len(data.total_costs) != len(data.funding_matrix):
                validation.add_error(f"Dimension mismatch: {len(data.total_costs)} total costs vs {len(data.funding_matrix)} funding rows")
                return validation
            
            math_errors = 0
            total_discrepancy = 0.0
            rows_checked = 0
            
            # Validate each row: total cost = sum of funding sources
            for i, (total_cost, funding_row) in enumerate(zip(data.total_costs, data.funding_matrix)):
                if total_cost > 0:  # Only validate non-zero rows
                    funding_sum = sum(funding_row) if funding_row else 0.0
                    discrepancy = abs(total_cost - funding_sum)
                    
                    if discrepancy > self.tolerance:
                        math_errors += 1
                        total_discrepancy += discrepancy
                        line_item = data.line_items[i] if i < len(data.line_items) else f"Row {i+3}"
                        validation.add_error(
                            f"{line_item}: Total ${total_cost:,.2f} ≠ Funding Sum ${funding_sum:,.2f} (Δ ${discrepancy:,.2f})"
                        )
                    
                    rows_checked += 1
            
            # Validate column totals
            if data.column_totals:
                for col_idx, expected_total in enumerate(data.column_totals):
                    calculated_total = sum(row[col_idx] if col_idx < len(row) else 0 
                                          for row in data.funding_matrix)
                    discrepancy = abs(expected_total - calculated_total)
                    
                    if discrepancy > self.tolerance:
                        math_errors += 1
                        funding_source = (data.funding_headers[col_idx] if col_idx < len(data.funding_headers) 
                                         else f"Column {col_idx+1}")
                        validation.add_error(
                            f"{funding_source}: Expected total ${expected_total:,.2f} ≠ Calculated ${calculated_total:,.2f}"
                        )
            
            # Mathematical accuracy assessment
            validation.mathematical_accuracy = math_errors == 0
            
            if validation.mathematical_accuracy:
                print(f"   ✅ Mathematical validation PASSED ({rows_checked} rows checked)")
            else:
                print(f"   ❌ Mathematical validation FAILED ({math_errors} errors, ${total_discrepancy:,.2f} total discrepancy)")
                validation.add_error(f"Total mathematical errors: {math_errors}")
            
            # Data completeness check
            filled_costs = sum(1 for cost in data.total_costs if cost > 0)
            filled_items = sum(1 for item in data.line_items if item and item.strip())
            total_data_points = len(data.total_costs) + len(data.line_items)
            
            if data.funding_matrix:
                for row in data.funding_matrix:
                    total_data_points += len(row)
                    filled_costs += sum(1 for cell in row if cell != 0)
            
            validation.data_completeness = (filled_costs + filled_items) / max(1, total_data_points) * 100
            
            print(f"   📊 Data completeness: {validation.data_completeness:.1f}%")
            
        except Exception as e:
            validation.add_error(f"Validation calculation failed: {e}")
            print(f"   ❌ Validation error: {e}")
        
        validation.calculate_score()
        return validation
    
    def validate_basis_calculations(self, data: BasisBreakdownData) -> ValidationResult:
        """
        Validate eligible basis calculations against IRS regulations
        """
        
        validation = ValidationResult()
        validation.validation_timestamp = datetime.now().isoformat()
        
        try:
            print(f"🔍 Validating Basis calculations...")
            
            if not data.basis_matrix or not data.basis_totals:
                validation.add_error("Missing basis data for validation")
                return validation
            
            math_errors = 0
            
            # Validate column totals match calculated sums
            for col_idx, expected_total in enumerate(data.basis_totals):
                if col_idx < len(data.basis_matrix[0]) if data.basis_matrix else 0:
                    calculated_total = sum(row[col_idx] if col_idx < len(row) else 0 
                                          for row in data.basis_matrix)
                    discrepancy = abs(expected_total - calculated_total)
                    
                    if discrepancy > self.tolerance:
                        math_errors += 1
                        basis_category = (data.basis_headers[col_idx] if col_idx < len(data.basis_headers) 
                                        else f"Basis Column {col_idx+1}")
                        validation.add_error(
                            f"{basis_category}: Expected ${expected_total:,.2f} ≠ Calculated ${calculated_total:,.2f}"
                        )
            
            # Validate Total Eligible Basis reasonableness
            if data.total_eligible_basis > 0:
                if data.total_eligible_basis < self.validation_rules["min_eligible_basis"]:
                    validation.add_warning(f"Total Eligible Basis ${data.total_eligible_basis:,.2f} appears low")
                elif data.total_eligible_basis > self.validation_rules["max_project_cost"]:
                    validation.add_warning(f"Total Eligible Basis ${data.total_eligible_basis:,.2f} appears extremely high")
                
                print(f"   💎 Total Eligible Basis: ${data.total_eligible_basis:,.2f}")
            else:
                validation.add_error("Total Eligible Basis is zero or missing")
            
            validation.mathematical_accuracy = math_errors == 0
            validation.business_logic_validity = len(validation.errors) == 0
            
            if validation.mathematical_accuracy:
                print(f"   ✅ Basis calculations PASSED")
            else:
                print(f"   ❌ Basis calculations FAILED ({math_errors} errors)")
            
        except Exception as e:
            validation.add_error(f"Basis validation failed: {e}")
            print(f"   ❌ Basis validation error: {e}")
        
        validation.calculate_score()
        return validation
    
    def validate_application_completeness(self, data: ApplicationData) -> ValidationResult:
        """
        Validate application data completeness and business logic
        """
        
        validation = ValidationResult()
        validation.validation_timestamp = datetime.now().isoformat()
        
        try:
            print(f"🔍 Validating Application completeness...")
            
            required_fields = [
                ("project_name", data.project_name),
                ("project_address", data.project_address),
                ("project_city", data.project_city),
                ("total_units", data.total_units),
                ("developer_name", data.developer_name)
            ]
            
            missing_fields = []
            for field_name, field_value in required_fields:
                if not field_value or (isinstance(field_value, str) and not field_value.strip()):
                    missing_fields.append(field_name)
            
            if missing_fields:
                validation.add_warning(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Business logic validation
            if data.total_units > 0:
                if data.total_units < self.validation_rules["min_units"]:
                    validation.add_warning(f"Total units ({data.total_units}) appears low")
                elif data.total_units > self.validation_rules["max_units"]:
                    validation.add_warning(f"Total units ({data.total_units}) appears high")
                
                # Cost per unit validation
                if data.total_development_cost > 0:
                    cost_per_unit = data.total_development_cost / data.total_units
                    if cost_per_unit < self.validation_rules["min_cost_per_unit"]:
                        validation.add_warning(f"Cost per unit ${cost_per_unit:,.0f} appears low")
                    elif cost_per_unit > self.validation_rules["max_cost_per_unit"]:
                        validation.add_warning(f"Cost per unit ${cost_per_unit:,.0f} appears high")
                    
                    print(f"   🏠 Cost per unit: ${cost_per_unit:,.0f}")
            else:
                validation.add_error("Total units is zero or missing")
            
            # Calculate completeness
            total_fields = len(required_fields)
            completed_fields = total_fields - len(missing_fields)
            validation.data_completeness = (completed_fields / total_fields) * 100
            
            validation.business_logic_validity = len(validation.errors) == 0
            validation.reasonable_value_ranges = len([w for w in validation.warnings if "appears" in w]) == 0
            
            print(f"   📊 Application completeness: {validation.data_completeness:.1f}%")
            print(f"   🏠 Project: {data.project_name or 'Not specified'}")
            print(f"   📍 Location: {data.project_city or 'Not specified'}")
            print(f"   🏢 Units: {data.total_units}")
            
        except Exception as e:
            validation.add_error(f"Application validation failed: {e}")
            print(f"   ❌ Application validation error: {e}")
        
        validation.calculate_score()
        return validation
    
    def validate_financial_reasonableness(self, sources_uses: SourcesUsesData, 
                                        application: ApplicationData) -> ValidationResult:
        """
        Cross-validate financial data for reasonableness
        """
        
        validation = ValidationResult()
        validation.validation_timestamp = datetime.now().isoformat()
        
        try:
            print(f"🔍 Validating Financial reasonableness...")
            
            # Calculate total project cost from sources & uses
            total_project_cost = sum(sources_uses.total_costs) if sources_uses.total_costs else 0
            
            # Basic reasonableness checks
            if total_project_cost < self.validation_rules["min_project_cost"]:
                validation.add_warning(f"Total project cost ${total_project_cost:,.0f} appears low")
            elif total_project_cost > self.validation_rules["max_project_cost"]:
                validation.add_warning(f"Total project cost ${total_project_cost:,.0f} appears extremely high")
            
            # Cross-check with application data
            if application.total_development_cost > 0:
                cost_discrepancy = abs(total_project_cost - application.total_development_cost)
                if cost_discrepancy > 10000:  # $10k tolerance
                    validation.add_warning(
                        f"Cost mismatch: Sources & Uses ${total_project_cost:,.0f} vs Application ${application.total_development_cost:,.0f}"
                    )
            
            # Funding source distribution analysis
            if sources_uses.funding_matrix and sources_uses.funding_headers:
                funding_totals = sources_uses.column_totals if sources_uses.column_totals else []
                if funding_totals:
                    equity_percentage = 0
                    debt_percentage = 0
                    
                    for i, header in enumerate(sources_uses.funding_headers):
                        if i < len(funding_totals) and total_project_cost > 0:
                            percentage = (funding_totals[i] / total_project_cost) * 100
                            
                            if any(term in header.lower() for term in ["equity", "tax credit"]):
                                equity_percentage += percentage
                            elif any(term in header.lower() for term in ["loan", "debt", "mortgage"]):
                                debt_percentage += percentage
                    
                    # Leverage ratio check
                    if equity_percentage > 0:
                        leverage_ratio = debt_percentage / equity_percentage
                        if leverage_ratio > self.validation_rules["max_leverage_ratio"]:
                            validation.add_warning(f"High leverage ratio: {leverage_ratio:.1f}:1")
                        
                        print(f"   💰 Debt/Equity ratio: {leverage_ratio:.2f}:1")
                        print(f"   📊 Equity: {equity_percentage:.1f}%, Debt: {debt_percentage:.1f}%")
            
            validation.business_logic_validity = len(validation.errors) == 0
            validation.reasonable_value_ranges = len(validation.warnings) <= 2  # Allow some warnings
            
        except Exception as e:
            validation.add_error(f"Financial validation failed: {e}")
            print(f"   ❌ Financial validation error: {e}")
        
        validation.calculate_score()
        return validation
    
    def validate_complete_extraction(self, result: CTCACExtractionResult) -> ValidationResult:
        """
        Comprehensive validation of complete extraction result
        """
        
        validation = ValidationResult()
        validation.validation_timestamp = datetime.now().isoformat()
        
        print(f"🔍 Comprehensive validation: {result.filename}")
        print("=" * 50)
        
        try:
            # Individual component validations
            component_validations = []
            
            # Sources & Uses validation
            if result.sources_uses_data:
                sources_validation = self.validate_sources_uses_math(result.sources_uses_data)
                component_validations.append(("Sources & Uses", sources_validation))
            else:
                validation.add_error("Sources & Uses data missing")
            
            # Basis breakdown validation
            if result.basis_breakdown_data:
                basis_validation = self.validate_basis_calculations(result.basis_breakdown_data)
                component_validations.append(("Basis Breakdown", basis_validation))
            
            # Application validation
            if result.application_data:
                app_validation = self.validate_application_completeness(result.application_data)
                component_validations.append(("Application", app_validation))
            
            # Cross-validation
            if result.sources_uses_data and result.application_data:
                financial_validation = self.validate_financial_reasonableness(
                    result.sources_uses_data, result.application_data
                )
                component_validations.append(("Financial Cross-Check", financial_validation))
            
            # Aggregate results
            total_score = 0
            total_weight = 0
            all_mathematical_accurate = True
            all_business_logic_valid = True
            
            for component_name, comp_validation in component_validations:
                weight = 1.0
                if component_name == "Sources & Uses":
                    weight = 2.0  # Higher weight for critical component
                
                total_score += comp_validation.validation_score * weight
                total_weight += weight
                
                if not comp_validation.mathematical_accuracy:
                    all_mathematical_accurate = False
                if not comp_validation.business_logic_validity:
                    all_business_logic_valid = False
                
                # Aggregate errors and warnings
                validation.errors.extend([f"{component_name}: {error}" for error in comp_validation.errors])
                validation.warnings.extend([f"{component_name}: {warning}" for warning in comp_validation.warnings])
                
                status = "✅ PASSED" if comp_validation.is_valid else "❌ FAILED"
                print(f"   {component_name}: {status} (Score: {comp_validation.validation_score:.1f})")
            
            # Final validation scores
            validation.validation_score = total_score / total_weight if total_weight > 0 else 0
            validation.mathematical_accuracy = all_mathematical_accurate
            validation.business_logic_validity = all_business_logic_valid
            validation.reasonable_value_ranges = len(validation.warnings) <= 5  # Allow some warnings
            
            # Overall completion assessment
            extraction_completeness = (result.sections_successfully_extracted / 
                                     max(1, result.sections_attempted)) * 100
            validation.data_completeness = extraction_completeness
            
            # Final validation determination
            validation.is_valid = (validation.validation_score >= 70 and 
                                 validation.mathematical_accuracy and 
                                 len(validation.errors) == 0)
            
            # Performance assessment
            performance_pass = (result.total_processing_time_seconds < 5.0 and 
                              result.memory_usage_mb < 200.0)
            
            print("=" * 50)
            print(f"📊 VALIDATION SUMMARY")
            print(f"   Overall Score: {validation.validation_score:.1f}/100")
            print(f"   Mathematical Accuracy: {'✅ PASSED' if validation.mathematical_accuracy else '❌ FAILED'}")
            print(f"   Business Logic: {'✅ PASSED' if validation.business_logic_validity else '❌ FAILED'}")
            print(f"   Data Completeness: {validation.data_completeness:.1f}%")
            print(f"   Processing Time: {result.total_processing_time_seconds:.2f}s {'✅' if result.total_processing_time_seconds < 5.0 else '⚠️'}")
            print(f"   Memory Usage: {result.memory_usage_mb:.1f} MB {'✅' if result.memory_usage_mb < 200.0 else '⚠️'}")
            print(f"   Overall Status: {'✅ PASSED' if validation.is_valid else '❌ FAILED'}")
            
            if validation.errors:
                print(f"\n❌ ERRORS ({len(validation.errors)}):")
                for error in validation.errors[:5]:  # Show first 5 errors
                    print(f"   • {error}")
            
            if validation.warnings:
                print(f"\n⚠️  WARNINGS ({len(validation.warnings)}):")
                for warning in validation.warnings[:3]:  # Show first 3 warnings
                    print(f"   • {warning}")
            
        except Exception as e:
            validation.add_error(f"Comprehensive validation failed: {e}")
            print(f"❌ Validation system error: {e}")
        
        return validation
    
    def generate_validation_report(self, results: List[CTCACExtractionResult]) -> Dict[str, Any]:
        """
        Generate comprehensive validation report for batch results
        """
        
        print(f"\n📋 WINGMAN VALIDATION REPORT")
        print("=" * 60)
        print(f"Files validated: {len(results)}")
        
        # Aggregate statistics
        validation_results = []
        for result in results:
            validation = self.validate_complete_extraction(result)
            validation_results.append(validation)
        
        # Calculate aggregate metrics
        total_files = len(validation_results)
        passed_validations = sum(1 for v in validation_results if v.is_valid)
        avg_validation_score = sum(v.validation_score for v in validation_results) / total_files if total_files > 0 else 0
        math_accuracy_rate = sum(1 for v in validation_results if v.mathematical_accuracy) / total_files * 100
        business_logic_rate = sum(1 for v in validation_results if v.business_logic_validity) / total_files * 100
        avg_completeness = sum(v.data_completeness for v in validation_results) / total_files if total_files > 0 else 0
        
        # Performance metrics
        avg_processing_time = sum(r.total_processing_time_seconds for r in results) / total_files if total_files > 0 else 0
        avg_memory_usage = sum(r.memory_usage_mb for r in results) / total_files if total_files > 0 else 0
        performance_target_met = sum(1 for r in results if r.total_processing_time_seconds < 5.0) / total_files * 100
        
        report = {
            "validation_summary": {
                "total_files": total_files,
                "passed_validations": passed_validations,
                "pass_rate": (passed_validations / total_files * 100) if total_files > 0 else 0,
                "average_validation_score": avg_validation_score,
                "mathematical_accuracy_rate": math_accuracy_rate,
                "business_logic_validity_rate": business_logic_rate,
                "average_data_completeness": avg_completeness
            },
            "performance_summary": {
                "average_processing_time": avg_processing_time,
                "average_memory_usage": avg_memory_usage,
                "performance_target_met_rate": performance_target_met,
                "target_processing_time": 5.0,
                "target_memory_usage": 200.0
            },
            "mission_targets": {
                "processing_time_target": avg_processing_time < 5.0,
                "data_completeness_target": avg_completeness > 95.0,
                "mathematical_accuracy_target": math_accuracy_rate > 99.0,
                "overall_mission_success": (passed_validations / total_files >= 0.95 and 
                                           avg_processing_time < 5.0 and 
                                           math_accuracy_rate > 99.0)
            }
        }
        
        # Print summary
        print(f"\n📊 VALIDATION METRICS")
        print("=" * 40)
        print(f"Validation pass rate: {report['validation_summary']['pass_rate']:.1f}%")
        print(f"Mathematical accuracy: {math_accuracy_rate:.1f}%")
        print(f"Business logic validity: {business_logic_rate:.1f}%")
        print(f"Data completeness: {avg_completeness:.1f}%")
        print(f"Average processing time: {avg_processing_time:.2f}s")
        print(f"Performance target met: {performance_target_met:.1f}%")
        
        # Mission success assessment
        mission_success = report["mission_targets"]["overall_mission_success"]
        print(f"\n🎯 MISSION SUCCESS: {'✅ ACHIEVED' if mission_success else '❌ NOT MET'}")
        
        if mission_success:
            print("🎊 WINGMAN Phase 1A ready for production deployment!")
        else:
            print("🔧 WINGMAN Phase 1A requires optimization before deployment")
        
        return report