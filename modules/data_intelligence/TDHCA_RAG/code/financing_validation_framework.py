#!/usr/bin/env python3
"""
Financial Term Validation and Cross-Reference Framework
Ensures accuracy and consistency of financing intelligence extraction

Key Features:
- Cross-field mathematical validation
- Market rate benchmarking
- Contact information validation
- Term consistency checking
- Completeness scoring
- Quality flags and alerts

Author: QAP RAG Enhanced Extraction Team
Date: July 27, 2025
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class ValidationResult:
    """Results of financial term validation"""
    is_valid: bool = True
    confidence_score: float = 1.0
    validation_flags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    cross_references: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MarketBenchmarks:
    """Current market benchmarks for LIHTC financing"""
    
    # Construction Loan Benchmarks (2025)
    construction_rate_range: Tuple[float, float] = (7.5, 12.0)  # Prime + 0.5% to Prime + 3.5%
    construction_term_range: Tuple[int, int] = (18, 36)  # 18-36 months typical
    construction_ltc_range: Tuple[float, float] = (70.0, 85.0)  # 70-85% loan-to-cost
    
    # Permanent Loan Benchmarks  
    permanent_rate_range: Tuple[float, float] = (5.5, 8.5)  # Fixed rates
    permanent_amortization_range: Tuple[int, int] = (300, 420)  # 25-35 years
    permanent_term_range: Tuple[int, int] = (120, 300)  # 10-25 years
    permanent_ltv_range: Tuple[float, float] = (70.0, 85.0)  # 70-85% LTV
    permanent_dscr_range: Tuple[float, float] = (1.15, 1.35)  # 1.15x-1.35x DSCR
    
    # Tax Credit Benchmarks
    tax_credit_factor_range: Tuple[float, float] = (0.85, 0.95)  # $0.85-$0.95 per credit
    
    # Developer Fee Benchmarks
    developer_fee_percentage_range: Tuple[float, float] = (12.0, 18.0)  # 12-18% of TDC

class FinancingValidationFramework:
    """Comprehensive validation framework for financing intelligence"""
    
    def __init__(self):
        self.benchmarks = MarketBenchmarks()
        self.logger = logging.getLogger(__name__)
        
        # Email validation pattern
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        # Phone validation pattern (US format)
        self.phone_pattern = re.compile(r'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
        
        # Known LIHTC lenders for validation
        self.known_lihtc_lenders = {
            "wells fargo", "bank of america", "chase", "citi", "pnc bank",
            "regions bank", "truist", "bb&t", "suntrust", "comerica",
            "capital one", "huntington bank", "fifth third", "us bank",
            "first national", "texas capital bank", "frost bank",
            "red stone bank", "southern bancorp", "national cooperative bank"
        }
        
        # Known tax credit syndicators
        self.known_syndicators = {
            "boston capital", "enterprise community investment", "raymond james",
            "rbc capital", "citi community capital", "hunt capital partners",
            "wells fargo equity", "pnc real estate", "national equity fund",
            "ohio capital", "red stone equity partners", "wisconsin housing"
        }
    
    def validate_financing_data(self, financing_data: Dict[str, Any]) -> ValidationResult:
        """Comprehensive validation of extracted financing data"""
        
        result = ValidationResult()
        
        # Cross-field mathematical validation
        self._validate_mathematical_consistency(financing_data, result)
        
        # Market benchmark validation  
        self._validate_market_benchmarks(financing_data, result)
        
        # Contact information validation
        self._validate_contact_information(financing_data, result)
        
        # Term consistency validation
        self._validate_term_consistency(financing_data, result)
        
        # Completeness scoring
        self._calculate_completeness_score(financing_data, result)
        
        # Entity recognition validation
        self._validate_entity_recognition(financing_data, result)
        
        # Calculate overall confidence
        result.confidence_score = self._calculate_overall_confidence(result)
        result.is_valid = result.confidence_score >= 0.7 and len(result.errors) == 0
        
        return result
    
    def _validate_mathematical_consistency(self, data: Dict[str, Any], result: ValidationResult):
        """Validate mathematical relationships between financing fields"""
        
        # Construction vs Permanent Loan Amounts
        construction_amt = data.get('construction_loan_amount', 0)
        permanent_amt = data.get('permanent_loan_amount', 0)
        
        if construction_amt > 0 and permanent_amt > 0:
            if permanent_amt > construction_amt * 1.1:
                result.warnings.append(
                    f"Permanent loan ({permanent_amt:,.0f}) significantly higher than construction loan ({construction_amt:,.0f})"
                )
            elif permanent_amt < construction_amt * 0.7:
                result.warnings.append(
                    f"Permanent loan ({permanent_amt:,.0f}) much lower than construction loan ({construction_amt:,.0f})"
                )
        
        # DSCR Validation (NOI / Debt Service)
        dscr = data.get('permanent_loan_dscr', 0)
        if dscr > 0:
            if dscr < 1.0:
                result.errors.append(f"DSCR ({dscr:.2f}) below 1.0 - project cannot service debt")
            elif dscr < 1.15:
                result.warnings.append(f"DSCR ({dscr:.2f}) below typical LIHTC minimum of 1.15")
            elif dscr > 2.0:
                result.warnings.append(f"DSCR ({dscr:.2f}) unusually high - verify calculation")
        
        # LTV Validation
        ltv = data.get('permanent_loan_ltv', 0)
        if ltv > 0:
            if ltv > 90:
                result.warnings.append(f"LTV ({ltv:.1f}%) above typical LIHTC maximum of 85%")
            elif ltv < 50:
                result.warnings.append(f"LTV ({ltv:.1f}%) unusually low for LIHTC")
        
        # Tax Credit Factor Validation
        factor = data.get('tax_credit_factor', 0)
        equity = data.get('total_tax_credit_equity', 0)
        credits = data.get('annual_tax_credits', 0)
        
        if factor > 0 and equity > 0 and credits > 0:
            calculated_equity = credits * 10 * factor  # 10-year credits
            if abs(calculated_equity - equity) / equity > 0.1:  # >10% difference
                result.warnings.append(
                    f"Tax credit equity calculation mismatch: calculated {calculated_equity:,.0f} vs reported {equity:,.0f}"
                )
    
    def _validate_market_benchmarks(self, data: Dict[str, Any], result: ValidationResult):
        """Validate against current market benchmarks"""
        
        # Construction loan rate validation
        construction_rate = data.get('construction_loan_rate', 0)
        if construction_rate > 0:
            min_rate, max_rate = self.benchmarks.construction_rate_range
            if construction_rate < min_rate:
                result.warnings.append(f"Construction rate ({construction_rate:.2f}%) below market range ({min_rate}-{max_rate}%)")
            elif construction_rate > max_rate:
                result.warnings.append(f"Construction rate ({construction_rate:.2f}%) above market range ({min_rate}-{max_rate}%)")
        
        # Permanent loan rate validation
        permanent_rate = data.get('permanent_loan_rate', 0)
        if permanent_rate > 0:
            min_rate, max_rate = self.benchmarks.permanent_rate_range
            if permanent_rate < min_rate:
                result.warnings.append(f"Permanent rate ({permanent_rate:.2f}%) below market range ({min_rate}-{max_rate}%)")
            elif permanent_rate > max_rate:
                result.warnings.append(f"Permanent rate ({permanent_rate:.2f}%) above market range ({min_rate}-{max_rate}%)")
        
        # Construction term validation
        construction_term = data.get('construction_loan_term_months', 0)
        if construction_term > 0:
            min_term, max_term = self.benchmarks.construction_term_range
            if construction_term < min_term:
                result.warnings.append(f"Construction term ({construction_term} months) shorter than typical ({min_term}-{max_term} months)")
            elif construction_term > max_term:
                result.warnings.append(f"Construction term ({construction_term} months) longer than typical ({min_term}-{max_term} months)")
        
        # Tax credit factor validation
        factor = data.get('tax_credit_factor', 0)
        if factor > 0:
            min_factor, max_factor = self.benchmarks.tax_credit_factor_range
            if factor < min_factor:
                result.warnings.append(f"Tax credit factor ({factor:.3f}) below market range ({min_factor}-{max_factor})")
            elif factor > max_factor:
                result.warnings.append(f"Tax credit factor ({factor:.3f}) above market range ({min_factor}-{max_factor})")
    
    def _validate_contact_information(self, data: Dict[str, Any], result: ValidationResult):
        """Validate contact information format and completeness"""
        
        contact_fields = [
            ('construction_lender_email', 'Construction lender email'),
            ('permanent_lender_email', 'Permanent lender email'),
            ('equity_investor_contact', 'Equity investor email'),
            ('syndicator_contact', 'Syndicator email')
        ]
        
        for field, description in contact_fields:
            email = data.get(field, '')
            if email and not self.email_pattern.match(email):
                result.validation_flags.append(f"Invalid email format: {description} ({email})")
        
        phone_fields = [
            ('construction_lender_phone', 'Construction lender phone'),
            ('permanent_lender_phone', 'Permanent lender phone')
        ]
        
        for field, description in phone_fields:
            phone = data.get(field, '')
            if phone and not self.phone_pattern.match(re.sub(r'[^\d]', '', phone)):
                result.validation_flags.append(f"Invalid phone format: {description} ({phone})")
    
    def _validate_term_consistency(self, data: Dict[str, Any], result: ValidationResult):
        """Validate consistency of financing terms"""
        
        # Rate type consistency
        construction_rate_type = data.get('construction_rate_type', '').lower()
        construction_rate = data.get('construction_loan_rate', 0)
        
        if 'variable' in construction_rate_type or 'prime' in construction_rate_type:
            if construction_rate > 0 and construction_rate < 5.0:
                result.warnings.append(f"Variable rate ({construction_rate:.2f}%) seems low - verify against current prime rate")
        
        # Amortization vs Term consistency
        amortization = data.get('permanent_loan_amortization_months', 0)
        term = data.get('permanent_loan_term_months', 0)
        
        if amortization > 0 and term > 0:
            if term >= amortization:
                result.warnings.append(f"Loan term ({term} months) >= amortization ({amortization} months) - unusual for LIHTC")
            elif term < amortization * 0.3:
                result.warnings.append(f"Very short term ({term} months) vs amortization ({amortization} months)")
    
    def _validate_entity_recognition(self, data: Dict[str, Any], result: ValidationResult):
        """Validate recognized lenders and syndicators against known entities"""
        
        # Construction lender validation
        construction_lender = data.get('construction_loan_lender', '').lower()
        if construction_lender:
            if not any(known in construction_lender for known in self.known_lihtc_lenders):
                result.validation_flags.append(f"Construction lender '{construction_lender}' not in known LIHTC lender database")
        
        # Permanent lender validation
        permanent_lender = data.get('permanent_loan_lender', '').lower()
        if permanent_lender:
            if not any(known in permanent_lender for known in self.known_lihtc_lenders):
                result.validation_flags.append(f"Permanent lender '{permanent_lender}' not in known LIHTC lender database")
        
        # Syndicator validation
        syndicator = data.get('tax_credit_syndicator', '').lower()
        if syndicator:
            if not any(known in syndicator for known in self.known_syndicators):
                result.validation_flags.append(f"Syndicator '{syndicator}' not in known syndicator database")
    
    def _calculate_completeness_score(self, data: Dict[str, Any], result: ValidationResult):
        """Calculate completeness score based on field coverage"""
        
        # Phase 1 Critical Fields (Construction & Permanent)
        phase1_fields = [
            'construction_loan_amount', 'construction_loan_lender', 'construction_loan_rate',
            'permanent_loan_amount', 'permanent_loan_lender', 'permanent_loan_rate',
            'permanent_loan_dscr', 'permanent_loan_ltv'
        ]
        
        # Phase 2 Important Fields (Subordinate & Equity)
        phase2_fields = [
            'total_tax_credit_equity', 'tax_credit_factor', 'tax_credit_investor',
            'second_lien_amount', 'grants_received'
        ]
        
        # Contact Intelligence Fields
        contact_fields = [
            'construction_lender_contact', 'construction_lender_email',
            'permanent_lender_contact', 'permanent_lender_email',
            'equity_investor_contact'
        ]
        
        # Calculate completion rates
        phase1_complete = sum(1 for field in phase1_fields if data.get(field, 0 if isinstance(data.get(field, 0), (int, float)) else '') != (0 if isinstance(data.get(field, 0), (int, float)) else ''))
        phase2_complete = sum(1 for field in phase2_fields if data.get(field, 0 if isinstance(data.get(field, 0), (int, float)) else '') != (0 if isinstance(data.get(field, 0), (int, float)) else ''))
        contact_complete = sum(1 for field in contact_fields if data.get(field, '') != '')
        
        # Weight the scores
        phase1_score = phase1_complete / len(phase1_fields) * 0.5  # 50% weight
        phase2_score = phase2_complete / len(phase2_fields) * 0.3  # 30% weight
        contact_score = contact_complete / len(contact_fields) * 0.2  # 20% weight
        
        completeness = phase1_score + phase2_score + contact_score
        
        result.cross_references['completeness_breakdown'] = {
            'phase1_critical': f"{phase1_complete}/{len(phase1_fields)} ({phase1_score*100:.1f}%)",
            'phase2_important': f"{phase2_complete}/{len(phase2_fields)} ({phase2_score*100:.1f}%)",
            'contact_intelligence': f"{contact_complete}/{len(contact_fields)} ({contact_score*100:.1f}%)",
            'overall_completeness': f"{completeness*100:.1f}%"
        }
        
        if completeness < 0.3:
            result.warnings.append(f"Low completeness score ({completeness*100:.1f}%) - critical financing data missing")
        elif completeness < 0.6:
            result.validation_flags.append(f"Moderate completeness ({completeness*100:.1f}%) - some financing details missing")
    
    def _calculate_overall_confidence(self, result: ValidationResult) -> float:
        """Calculate overall confidence score based on validation results"""
        
        base_confidence = 1.0
        
        # Deduct for errors (major issues)
        base_confidence -= len(result.errors) * 0.2
        
        # Deduct for warnings (moderate issues)
        base_confidence -= len(result.warnings) * 0.1
        
        # Deduct for validation flags (minor issues)
        base_confidence -= len(result.validation_flags) * 0.05
        
        # Ensure confidence stays between 0 and 1
        return max(0.0, min(1.0, base_confidence))
    
    def generate_validation_report(self, validation_result: ValidationResult, financing_data: Dict[str, Any]) -> str:
        """Generate human-readable validation report"""
        
        report = [
            "🔍 FINANCING INTELLIGENCE VALIDATION REPORT",
            "=" * 60,
            f"Overall Valid: {'✅ YES' if validation_result.is_valid else '❌ NO'}",
            f"Confidence Score: {validation_result.confidence_score:.2f}/1.00",
            f"Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        # Completeness breakdown
        if 'completeness_breakdown' in validation_result.cross_references:
            report.extend([
                "📊 COMPLETENESS ANALYSIS:",
                "-" * 30
            ])
            breakdown = validation_result.cross_references['completeness_breakdown']
            for category, score in breakdown.items():
                report.append(f"{category.replace('_', ' ').title()}: {score}")
            report.append("")
        
        # Errors (critical issues)
        if validation_result.errors:
            report.extend([
                "🚨 CRITICAL ERRORS:",
                "-" * 20
            ])
            for error in validation_result.errors:
                report.append(f"❌ {error}")
            report.append("")
        
        # Warnings (moderate issues)
        if validation_result.warnings:
            report.extend([
                "⚠️ WARNINGS:",
                "-" * 15
            ])
            for warning in validation_result.warnings:
                report.append(f"⚠️ {warning}")
            report.append("")
        
        # Validation flags (minor issues)
        if validation_result.validation_flags:
            report.extend([
                "🏷️ VALIDATION FLAGS:",
                "-" * 20
            ])
            for flag in validation_result.validation_flags:
                report.append(f"🏷️ {flag}")
            report.append("")
        
        # Key financing metrics summary
        report.extend([
            "💰 KEY FINANCING METRICS:",
            "-" * 30
        ])
        
        key_metrics = [
            ('construction_loan_amount', 'Construction Loan', 'currency'),
            ('construction_loan_rate', 'Construction Rate', 'percent'),
            ('permanent_loan_amount', 'Permanent Loan', 'currency'),
            ('permanent_loan_rate', 'Permanent Rate', 'percent'),
            ('permanent_loan_dscr', 'DSCR', 'ratio'),
            ('total_tax_credit_equity', 'Tax Credit Equity', 'currency'),
            ('tax_credit_factor', 'Credit Factor', 'factor')
        ]
        
        for field, label, format_type in key_metrics:
            value = financing_data.get(field, 0)
            if value > 0:
                if format_type == 'currency':
                    formatted = f"${value:,.0f}"
                elif format_type == 'percent':
                    formatted = f"{value:.2f}%"
                elif format_type == 'ratio':
                    formatted = f"{value:.2f}x"
                elif format_type == 'factor':
                    formatted = f"${value:.3f}"
                else:
                    formatted = str(value)
                
                report.append(f"{label}: {formatted}")
        
        report.extend([
            "",
            "📞 CONTACT INTELLIGENCE:",
            "-" * 25
        ])
        
        contact_fields = [
            ('construction_lender_contact', 'Construction Lender Contact'),
            ('permanent_lender_contact', 'Permanent Lender Contact'),
            ('equity_investor_contact', 'Equity Investor Contact')
        ]
        
        for field, label in contact_fields:
            contact = financing_data.get(field, '')
            if contact:
                report.append(f"{label}: {contact}")
        
        return '\n'.join(report)

def test_validation_framework():
    """Test the validation framework with sample data"""
    
    # Sample financing data for testing
    test_data = {
        'construction_loan_amount': 15500000,
        'construction_loan_lender': 'Bank of America',
        'construction_loan_rate': 8.75,
        'construction_loan_term_months': 24,
        'construction_lender_contact': 'Sarah Mitchell',
        'construction_lender_email': 'smitchell@bofa.com',
        'permanent_loan_amount': 12800000,
        'permanent_loan_lender': 'Wells Fargo',
        'permanent_loan_rate': 6.25,
        'permanent_loan_dscr': 1.25,
        'permanent_loan_ltv': 75.0,
        'permanent_lender_contact': 'Michael Johnson',
        'total_tax_credit_equity': 8500000,
        'tax_credit_factor': 0.91,
        'annual_tax_credits': 934000,
        'tax_credit_investor': 'Boston Capital'
    }
    
    # Run validation
    validator = FinancingValidationFramework()
    result = validator.validate_financing_data(test_data)
    
    # Generate report
    report = validator.generate_validation_report(result, test_data)
    
    print(report)
    print(f"\n✅ Validation Framework Test Complete")
    print(f"Overall Valid: {result.is_valid}")
    print(f"Confidence: {result.confidence_score:.2f}")

if __name__ == "__main__":
    test_validation_framework()