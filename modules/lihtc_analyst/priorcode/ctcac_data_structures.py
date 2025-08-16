#!/usr/bin/env python3
"""
CTCAC Data Structures
Standardized output classes for comprehensive CTCAC extraction
WINGMAN-01 Mission Implementation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

@dataclass
class SourcesUsesData:
    """Sources and Uses Budget extraction data"""
    
    # Static Information (A3:A105)
    line_items: List[str] = field(default_factory=list)  # ["Land Cost", "Demolition", "Site Work", ...]
    
    # Total Project Costs (B3:B105)
    total_costs: List[float] = field(default_factory=list)  # [5000000, 0, 250000, ...]
    
    # Column Headers (C2:T2)
    funding_headers: List[str] = field(default_factory=list)  # ["RES. COST", "COM'L. COST", "TAX CREDIT EQUITY", ...]
    
    # Input Data Matrix (C4:T105)
    funding_matrix: List[List[float]] = field(default_factory=list)  # Complete funding allocation matrix
    
    # Validation data
    row_totals: List[float] = field(default_factory=list)  # B3:B105 calculated totals
    column_totals: List[float] = field(default_factory=list)  # Totals for each funding source
    mathematical_validation: bool = False  # Row sums = column sums validation
    
    # Extraction metadata
    extraction_range: str = ""  # "A3:T105"
    extraction_timestamp: str = ""
    processing_time_seconds: float = 0.0
    data_completeness_percent: float = 0.0

@dataclass
class BasisBreakdownData:
    """Sources and Basis Breakdown extraction data (lower section)"""
    
    # Basis Headers (C2:J2)
    basis_headers: List[str] = field(default_factory=list)  # basis categories
    
    # Basis Matrix (C4:T105)
    basis_matrix: List[List[float]] = field(default_factory=list)  # all basis calculations
    
    # Total Eligible Basis (D107) - CRITICAL LIHTC calculation
    total_eligible_basis: float = 0.0
    
    # Basis Totals (E107:J107)
    basis_totals: List[float] = field(default_factory=list)  # All category totals
    
    # Validation
    basis_mathematical_check: bool = False  # Verify calculations
    basis_calculation_errors: List[str] = field(default_factory=list)
    
    # Extraction metadata
    extraction_range: str = ""  # "C2:J107"
    extraction_timestamp: str = ""
    processing_time_seconds: float = 0.0

@dataclass
class ApplicationData:
    """Main Application tab data - Enhanced for complete LIHTC coverage"""
    
    # Project identification
    project_name: str = ""
    project_address: str = ""
    project_city: str = ""
    project_county: str = ""
    project_state: str = "CA"
    project_zip: str = ""
    census_tract: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    
    # Unit information - Enhanced
    total_units: int = 0
    affordable_units: int = 0
    market_rate_units: int = 0
    unit_mix_details: Dict[str, int] = field(default_factory=dict)  # {"1BR": 25, "2BR": 30, etc.}
    
    # AMI targeting - CRITICAL for LIHTC
    unit_mix_by_ami: Dict[str, Dict[str, int]] = field(default_factory=dict)  
    # {"30%_AMI": {"1BR": 5, "2BR": 8}, "60%_AMI": {"1BR": 10, "2BR": 15}}
    ami_levels_served: List[str] = field(default_factory=list)  # ["30%", "50%", "60%", "80%"]
    
    # Rent information - CRITICAL for financial analysis
    lihtc_rents_by_unit_type: Dict[str, float] = field(default_factory=dict)  # {"1BR": 1200, "2BR": 1440}
    market_rents_by_unit_type: Dict[str, float] = field(default_factory=dict)  # {"1BR": 2500, "2BR": 3200}
    rent_restrictions: Dict[str, str] = field(default_factory=dict)  # Unit type to restriction type
    
    # Operating expenses - CRITICAL for NOI calculations
    annual_operating_expenses: float = 0.0
    operating_expense_breakdown: Dict[str, float] = field(default_factory=dict)
    # {"Property_Taxes": 85000, "Insurance": 25000, "Management": 45000, "Maintenance": 65000}
    operating_expense_per_unit: float = 0.0
    
    # Developer information - Enhanced
    developer_name: str = ""
    developer_address: str = ""
    developer_contact_person: str = ""
    developer_phone: str = ""
    developer_email: str = ""
    general_partner: str = ""
    management_company: str = ""
    
    # Project type and construction
    project_type: str = ""  # "New Construction", "Rehabilitation", "Acquisition & Rehab"
    construction_type: str = ""  # "Type V Wood Frame", "Type III", etc.
    building_stories: int = 0
    gross_building_area: float = 0.0
    parking_spaces: int = 0
    
    # Financial structure - CRITICAL for deal analysis
    total_development_cost: float = 0.0
    tax_credit_request: float = 0.0
    financing_sources: Dict[str, float] = field(default_factory=dict)
    # {"4%_Tax_Credits": 1200000, "Bank_Loan": 8500000, "Deferred_Dev_Fee": 500000, "City_Loan": 1000000}
    
    # Critical LIHTC financial metrics
    eligible_basis: float = 0.0
    applicable_percentage: float = 0.0
    annual_credit_amount: float = 0.0
    
    # Development timeline
    construction_start_date: str = ""
    construction_completion_date: str = ""
    placed_in_service_date: str = ""
    
    # Special programs and preferences
    special_needs_population: List[str] = field(default_factory=list)  # ["Seniors", "Homeless", "Veterans"]
    green_building_certification: str = ""  # "LEED Gold", "GreenPoint", etc.
    local_preferences: List[str] = field(default_factory=list)
    
    # Extraction metadata
    extraction_confidence: float = 0.0
    fields_extracted: int = 0
    total_fields_attempted: int = 35  # Updated for enhanced fields

@dataclass
class CALHFAAddendumData:
    """CALHFA Addendum data (conditional)"""
    
    is_calhfa_deal: bool = False
    calhfa_loan_amount: float = 0.0
    calhfa_loan_terms: str = ""
    calhfa_requirements: List[str] = field(default_factory=list)
    
    # Extraction metadata
    extraction_timestamp: str = ""

@dataclass
class PointsSystemData:
    """Points System scoring data"""
    
    scoring_categories: Dict[str, float] = field(default_factory=dict)  # {"Location": 15, "Financial": 12, etc.}
    total_points_achieved: float = 0.0
    maximum_possible_points: float = 0.0
    tie_breaker_ranking: Optional[int] = None
    
    # Detailed point breakdown
    point_details: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Extraction metadata
    extraction_timestamp: str = ""

@dataclass
class TieBreakerData:
    """Tie-Breaker competitive analysis data"""
    
    tie_breaker_factors: Dict[str, Any] = field(default_factory=dict)
    tie_breaker_score: float = 0.0
    competitive_ranking: Optional[int] = None
    
    # Critical competitive metrics
    cost_per_unit: float = 0.0
    developer_experience_score: float = 0.0
    leverage_ratio: float = 0.0
    
    # Extraction metadata
    extraction_timestamp: str = ""

@dataclass
class SubsidyContractData:
    """Subsidy Contract Calculation data (conditional)"""
    
    has_rental_assistance: bool = False
    subsidy_amount_monthly: float = 0.0
    subsidy_contract_term: int = 0  # years
    subsidy_source: str = ""  # "Section 8", "Project-based vouchers", etc.
    
    # Extraction metadata
    extraction_timestamp: str = ""

@dataclass
class ProformaData:
    """15 Year Proforma financial projections"""
    
    annual_projections: List[Dict[str, float]] = field(default_factory=list)  # Year-by-year data
    income_categories: List[str] = field(default_factory=list)
    expense_categories: List[str] = field(default_factory=list)
    
    # Key metrics
    stabilized_noi: float = 0.0
    debt_service_coverage_ratio: float = 0.0
    cash_flow_projections: List[float] = field(default_factory=list)
    
    # Extraction metadata
    extraction_timestamp: str = ""

@dataclass
class CTCACExtractionResult:
    """Complete CTCAC extraction result container"""
    
    # File metadata
    filename: str = ""
    file_path: str = ""
    file_size_mb: float = 0.0
    extraction_start_time: str = ""
    extraction_end_time: str = ""
    total_processing_time_seconds: float = 0.0
    
    # Core data sections
    sources_uses_data: Optional[SourcesUsesData] = None
    basis_breakdown_data: Optional[BasisBreakdownData] = None
    application_data: Optional[ApplicationData] = None
    
    # Conditional sections
    calhfa_addendum_data: Optional[CALHFAAddendumData] = None
    points_system_data: Optional[PointsSystemData] = None
    tie_breaker_data: Optional[TieBreakerData] = None
    subsidy_contract_data: Optional[SubsidyContractData] = None
    proforma_data: Optional[ProformaData] = None
    
    # Extraction quality metrics
    overall_extraction_confidence: float = 0.0
    sections_successfully_extracted: int = 0
    sections_attempted: int = 0
    mathematical_validation_passed: bool = False
    
    # Performance metrics
    cells_processed: int = 0
    cells_per_second: float = 0.0
    memory_usage_mb: float = 0.0
    
    # Error tracking
    extraction_errors: List[str] = field(default_factory=list)
    extraction_warnings: List[str] = field(default_factory=list)
    
    def to_json(self) -> str:
        """Convert to JSON string for export"""
        return json.dumps(self.__dict__, default=str, indent=2)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get extraction summary metrics"""
        return {
            "filename": self.filename,
            "processing_time": self.total_processing_time_seconds,
            "confidence": self.overall_extraction_confidence,
            "sections_extracted": f"{self.sections_successfully_extracted}/{self.sections_attempted}",
            "mathematical_validation": self.mathematical_validation_passed,
            "performance": f"{self.cells_per_second:.0f} cells/sec",
            "has_sources_uses": self.sources_uses_data is not None,
            "has_basis_breakdown": self.basis_breakdown_data is not None,
            "has_application_data": self.application_data is not None
        }

@dataclass
class ValidationResult:
    """Validation result for mathematical and business logic checks"""
    
    is_valid: bool = False
    validation_score: float = 0.0  # 0-100
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Specific validation checks
    mathematical_accuracy: bool = False
    business_logic_validity: bool = False
    data_completeness: float = 0.0
    reasonable_value_ranges: bool = False
    
    validation_timestamp: str = ""
    
    def add_error(self, error_message: str):
        """Add validation error"""
        self.errors.append(error_message)
        self.is_valid = False
    
    def add_warning(self, warning_message: str):
        """Add validation warning"""
        self.warnings.append(warning_message)
    
    def calculate_score(self):
        """Calculate overall validation score"""
        score_components = []
        
        if self.mathematical_accuracy:
            score_components.append(30)  # 30% for math accuracy
        
        if self.business_logic_validity:
            score_components.append(25)  # 25% for business logic
        
        score_components.append(self.data_completeness * 0.25)  # 25% for completeness
        
        if self.reasonable_value_ranges:
            score_components.append(20)  # 20% for reasonable values
        
        self.validation_score = sum(score_components)
        self.is_valid = self.validation_score >= 70 and len(self.errors) == 0

@dataclass
class PerformanceMetrics:
    """Performance tracking for extraction operations"""
    
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    processing_time_seconds: float = 0.0
    
    # Resource usage
    memory_start_mb: float = 0.0
    memory_peak_mb: float = 0.0
    memory_end_mb: float = 0.0
    
    # Processing metrics
    files_processed: int = 0
    cells_processed: int = 0
    sheets_processed: int = 0
    
    # Performance rates
    files_per_minute: float = 0.0
    cells_per_second: float = 0.0
    
    # Error tracking
    successful_extractions: int = 0
    failed_extractions: int = 0
    partial_extractions: int = 0
    
    def finalize_metrics(self):
        """Calculate final performance metrics"""
        if self.end_time:
            self.processing_time_seconds = (self.end_time - self.start_time).total_seconds()
            
            if self.processing_time_seconds > 0:
                self.files_per_minute = (self.files_processed / self.processing_time_seconds) * 60
                self.cells_per_second = self.cells_processed / self.processing_time_seconds
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            "processing_time": f"{self.processing_time_seconds:.2f}s",
            "files_processed": self.files_processed,
            "files_per_minute": f"{self.files_per_minute:.1f}",
            "cells_per_second": f"{self.cells_per_second:.0f}",
            "memory_peak": f"{self.memory_peak_mb:.1f} MB",
            "success_rate": f"{(self.successful_extractions/max(1,self.files_processed))*100:.1f}%"
        }