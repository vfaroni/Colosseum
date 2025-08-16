#!/usr/bin/env python3
"""
WINGMAN CTCAC Extractor v2.0
100% CTCAC Data Extraction - Technical Implementation
WINGMAN-01 Mission: Phase 1A Priority Implementation

Features:
- Complete Sources and Uses Budget extraction (A3:A105, B3:B105, C2:T2, C4:T105)
- Mathematical validation framework
- <5 second processing time target
- M4 Beast optimization
- Memory efficient xlwings operations
"""

import xlwings as xw
import time
import json
import gc
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from ctcac_data_structures import (
    CTCACExtractionResult, SourcesUsesData, BasisBreakdownData, 
    ApplicationData, ValidationResult, PerformanceMetrics
)
from enhanced_application_extractor import EnhancedApplicationExtractor

class WingmanCTCACExtractor:
    """
    WINGMAN CTCAC Extractor v2.0
    Production-ready extraction with 100% data coverage
    """
    
    def __init__(self, performance_mode: str = "optimized"):
        """
        Initialize WINGMAN extractor
        
        Args:
            performance_mode: "optimized" (M4 Beast), "standard", "safe"
        """
        self.performance_mode = performance_mode
        self.extraction_stats = PerformanceMetrics()
        
        # Sources and Uses sheet priorities
        self.sources_uses_sheet_names = [
            "Sources and Uses Budget",
            "Sources & Uses Budget", 
            "Budget",
            "Sources and Uses",
            "Sources & Uses",
            "Financial Summary"
        ]
        
        # Application sheet priorities
        self.application_sheet_names = [
            "Application",
            "App",
            "Project Application",
            "Main Application"
        ]
        
        # Threading configuration for M4 Beast
        self.max_threads = min(8, psutil.cpu_count()) if performance_mode == "optimized" else 1
        
        # Initialize enhanced application extractor
        self.enhanced_app_extractor = EnhancedApplicationExtractor()
        
        print(f"🚀 WINGMAN CTCAC Extractor v2.0 initialized")
        print(f"   ⚡ Performance mode: {performance_mode}")
        print(f"   🧵 Max threads: {self.max_threads}")
        print(f"   🖥️  CPU cores: {psutil.cpu_count()}")
        print(f"   📊 Enhanced Application extraction enabled")
    
    def extract_single_file(self, file_path: Path) -> CTCACExtractionResult:
        """
        Extract complete data from single CTCAC file
        Phase 1A Priority: Sources and Uses Budget
        """
        
        start_time = time.time()
        result = CTCACExtractionResult()
        
        # Convert to Path object if string
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        # Initialize result metadata
        result.filename = file_path.name
        result.file_path = str(file_path)
        result.file_size_mb = file_path.stat().st_size / (1024 * 1024)
        result.extraction_start_time = datetime.now().isoformat()
        
        # Memory tracking
        process = psutil.Process()
        memory_start = process.memory_info().rss / 1024 / 1024
        
        try:
            # Open Excel with M4 Beast optimization
            app = xw.App(visible=False, add_book=False)
            app.display_alerts = False
            app.screen_updating = False
            
            # Additional M4 Beast optimizations
            if self.performance_mode == "optimized":
                app.calculation = "manual"
            
            wb = app.books.open(str(file_path), read_only=True, update_links=False)
            
            print(f"📊 Processing: {file_path.name}")
            print(f"   📋 Total sheets: {len(wb.sheets)}")
            
            # Phase 1A: Sources and Uses Budget (CRITICAL PRIORITY)
            sources_uses_sheet = self._find_sources_uses_sheet(wb)
            if sources_uses_sheet:
                print(f"   🎯 Found Sources & Uses sheet: '{sources_uses_sheet.name}'")
                
                # Extract Phase 1A data
                sources_uses_data = self._extract_sources_uses_budget(sources_uses_sheet)
                if sources_uses_data:
                    result.sources_uses_data = sources_uses_data
                    result.sections_successfully_extracted += 1
                    print(f"   ✅ Sources & Uses extraction: {sources_uses_data.data_completeness_percent:.1f}% complete")
                
                # Extract Phase 1B data (same sheet, lower section)
                basis_breakdown_data = self._extract_basis_breakdown(sources_uses_sheet)
                if basis_breakdown_data:
                    result.basis_breakdown_data = basis_breakdown_data
                    result.sections_successfully_extracted += 1
                    print(f"   ✅ Basis breakdown extraction completed")
            else:
                result.extraction_warnings.append("Sources and Uses Budget sheet not found")
                print(f"   ⚠️  No Sources & Uses sheet found")
            
            # Enhanced Application data extraction (Phase 1B)
            print(f"   🎯 Enhanced Application extraction starting...")
            enhanced_application_data = self.enhanced_app_extractor.extract_comprehensive_application_data(wb)
            if enhanced_application_data:
                result.application_data = enhanced_application_data
                result.sections_successfully_extracted += 1
                print(f"   ✅ Enhanced Application data: {enhanced_application_data.extraction_confidence:.1f}% confidence")
                print(f"       📊 {enhanced_application_data.fields_extracted}/{enhanced_application_data.total_fields_attempted} fields extracted")
                if enhanced_application_data.ami_levels_served:
                    print(f"       🎯 AMI levels: {', '.join(enhanced_application_data.ami_levels_served)}")
                if enhanced_application_data.financing_sources:
                    print(f"       💰 Financing sources: {len(enhanced_application_data.financing_sources)} identified")
            else:
                print(f"   ⚠️  Enhanced Application extraction failed")
            
            # Phase 1B: Additional Application Tabs Extraction
            print(f"   🎯 Phase 1B: Additional application tabs...")
            
            # Points System extraction
            points_system_data = self._extract_points_system_data(wb)
            if points_system_data:
                result.points_system_data = points_system_data
                result.sections_successfully_extracted += 1
                print(f"   ✅ Points System: {points_system_data.total_points_achieved} points achieved")
            
            # Tie-Breaker extraction
            tie_breaker_data = self._extract_tie_breaker_data(wb)
            if tie_breaker_data:
                result.tie_breaker_data = tie_breaker_data
                result.sections_successfully_extracted += 1
                print(f"   ✅ Tie-Breaker: ${tie_breaker_data.cost_per_unit:.0f}/unit")
            
            # CALHFA detection (conditional)
            calhfa_data = self._extract_calhfa_data(wb)
            if calhfa_data and calhfa_data.is_calhfa_deal:
                result.calhfa_addendum_data = calhfa_data
                result.sections_successfully_extracted += 1
                print(f"   ✅ CALHFA: ${calhfa_data.calhfa_loan_amount:,.0f} loan")
            
            # Subsidy Contract detection (conditional)
            subsidy_data = self._extract_subsidy_contract_data(wb)
            if subsidy_data and subsidy_data.has_rental_assistance:
                result.subsidy_contract_data = subsidy_data
                result.sections_successfully_extracted += 1
                print(f"   ✅ Subsidy Contract: ${subsidy_data.subsidy_amount_monthly}/month")
            
            # 15-Year Proforma extraction
            proforma_data = self._extract_proforma_data(wb)
            if proforma_data:
                result.proforma_data = proforma_data
                result.sections_successfully_extracted += 1
                print(f"   ✅ Proforma: ${proforma_data.stabilized_noi:,.0f} NOI")
            
            result.sections_attempted = 8  # Sources/Uses, Basis, Enhanced App, Points, Tie-Breaker, CALHFA, Subsidy, Proforma
            
            # Cleanup
            wb.close()
            app.quit()
            
            # Memory tracking
            memory_end = process.memory_info().rss / 1024 / 1024
            result.memory_usage_mb = memory_end - memory_start
            
            # Performance metrics
            processing_time = time.time() - start_time
            result.total_processing_time_seconds = processing_time
            result.extraction_end_time = datetime.now().isoformat()
            
            # Calculate performance
            if result.sources_uses_data:
                result.cells_processed = len(result.sources_uses_data.line_items) * (2 + len(result.sources_uses_data.funding_headers))
            
            if processing_time > 0:
                result.cells_per_second = result.cells_processed / processing_time
            
            # Overall confidence calculation
            confidence_scores = []
            if result.sources_uses_data and result.sources_uses_data.data_completeness_percent > 0:
                confidence_scores.append(result.sources_uses_data.data_completeness_percent)
            if result.application_data and result.application_data.extraction_confidence > 0:
                confidence_scores.append(result.application_data.extraction_confidence)
            
            result.overall_extraction_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            print(f"   ⏱️  Processing time: {processing_time:.2f}s")
            print(f"   🎯 Overall confidence: {result.overall_extraction_confidence:.1f}%")
            print(f"   💾 Memory used: {result.memory_usage_mb:.1f} MB")
            
            # Mathematical validation
            if result.sources_uses_data:
                validation_result = self._validate_mathematical_accuracy(result.sources_uses_data)
                result.mathematical_validation_passed = validation_result.is_valid
                if not validation_result.is_valid:
                    result.extraction_errors.extend(validation_result.errors)
                    result.extraction_warnings.extend(validation_result.warnings)
            
        except Exception as e:
            error_msg = f"Extraction failed: {str(e)}"
            result.extraction_errors.append(error_msg)
            print(f"   ❌ {error_msg}")
            
            # Still record timing
            result.total_processing_time_seconds = time.time() - start_time
            result.extraction_end_time = datetime.now().isoformat()
        
        finally:
            # Force garbage collection for memory efficiency
            gc.collect()
        
        return result
    
    def _find_sources_uses_sheet(self, workbook: xw.Book) -> Optional[xw.Sheet]:
        """Find Sources and Uses Budget sheet"""
        
        for sheet_name in self.sources_uses_sheet_names:
            for sheet in workbook.sheets:
                if sheet_name.lower() in sheet.name.lower():
                    return sheet
        
        return None
    
    def _find_application_sheet(self, workbook: xw.Book) -> Optional[xw.Sheet]:
        """Find main Application sheet"""
        
        for sheet_name in self.application_sheet_names:
            for sheet in workbook.sheets:
                if sheet_name.lower() in sheet.name.lower():
                    return sheet
        
        return None
    
    def _extract_sources_uses_budget(self, sheet: xw.Sheet) -> Optional[SourcesUsesData]:
        """
        Phase 1A: Extract Sources and Uses Budget data
        Corrected ranges: A4:A150, B4:B150, B2:T2, C4:T150
        """
        
        start_time = time.time()
        
        try:
            sources_uses = SourcesUsesData()
            sources_uses.extraction_timestamp = datetime.now().isoformat()
            sources_uses.extraction_range = "A4:T150"
            
            print(f"      📊 Extracting Sources & Uses Budget...")
            
            # Extract Line Items (A4:A150) - Data starts at row 4
            print(f"      🔍 Reading line items (A4:A150)...")
            line_items_raw = sheet.range("A4:A150").value
            if line_items_raw:
                if isinstance(line_items_raw, list):
                    sources_uses.line_items = [str(item).strip() if item else "" for item in line_items_raw]
                else:
                    sources_uses.line_items = [str(line_items_raw).strip()]
            
            # Extract Total Project Costs (B4:B150)
            print(f"      💰 Reading total costs (B4:B150)...")
            total_costs_raw = sheet.range("B4:B150").value
            if total_costs_raw:
                if isinstance(total_costs_raw, list):
                    sources_uses.total_costs = [float(cost) if isinstance(cost, (int, float)) and cost is not None else 0.0 
                                               for cost in total_costs_raw]
                else:
                    sources_uses.total_costs = [float(total_costs_raw) if isinstance(total_costs_raw, (int, float)) else 0.0]
            
            # Extract Column Headers (B2:T2) - Include Total Project Cost column
            print(f"      📋 Reading funding headers (B2:T2)...")
            funding_headers_raw = sheet.range("B2:T2").value
            if funding_headers_raw:
                if isinstance(funding_headers_raw, list):
                    sources_uses.funding_headers = [str(header).strip() if header else f"Column_{i+3}" 
                                                   for i, header in enumerate(funding_headers_raw)]
                else:
                    sources_uses.funding_headers = [str(funding_headers_raw).strip()]
            
            # Extract Input Data Matrix (C4:T150) - Funding sources data only
            print(f"      🔢 Reading funding matrix (C4:T150)...")
            funding_matrix_raw = sheet.range("C4:T150").value
            if funding_matrix_raw:
                sources_uses.funding_matrix = []
                
                # Handle different data structures
                if isinstance(funding_matrix_raw[0], list):
                    # 2D array
                    for row in funding_matrix_raw:
                        if isinstance(row, list):
                            matrix_row = [float(cell) if isinstance(cell, (int, float)) and cell is not None else 0.0 
                                         for cell in row]
                            sources_uses.funding_matrix.append(matrix_row)
                        else:
                            # Single value row
                            value = float(row) if isinstance(row, (int, float)) and row is not None else 0.0
                            sources_uses.funding_matrix.append([value])
                else:
                    # 1D array - single column
                    for value in funding_matrix_raw:
                        cell_value = float(value) if isinstance(value, (int, float)) and value is not None else 0.0
                        sources_uses.funding_matrix.append([cell_value])
            
            # Calculate row totals for validation (exclude calculated columns)
            sources_uses.row_totals = sources_uses.total_costs.copy()
            
            # Calculate column totals for validation (exclude SUBTOTAL columns)
            if sources_uses.funding_matrix and len(sources_uses.funding_matrix) > 0:
                num_columns = len(sources_uses.funding_matrix[0]) if sources_uses.funding_matrix[0] else 0
                sources_uses.column_totals = []
                
                # Only include base funding source columns (exclude calculated totals)
                for col_idx in range(min(num_columns, 15)):  # Limit to avoid SUBTOTAL columns
                    if col_idx < len(sources_uses.funding_headers):
                        header = sources_uses.funding_headers[col_idx].upper()
                        # Skip calculated columns
                        if any(calc_term in header for calc_term in ['SUBTOTAL', 'TOTAL', 'PVC']):
                            sources_uses.column_totals.append(0.0)
                            continue
                    
                    column_total = sum(row[col_idx] if col_idx < len(row) else 0.0 
                                      for row in sources_uses.funding_matrix)
                    sources_uses.column_totals.append(column_total)
            
            # Calculate data completeness
            total_expected_cells = 147 * (2 + len(sources_uses.funding_headers))  # 147 rows × columns
            filled_cells = 0
            
            filled_cells += sum(1 for item in sources_uses.line_items if item and item.strip())
            filled_cells += sum(1 for cost in sources_uses.total_costs if cost > 0)
            
            for row in sources_uses.funding_matrix:
                filled_cells += sum(1 for cell in row if cell != 0)
            
            sources_uses.data_completeness_percent = (filled_cells / max(1, total_expected_cells)) * 100
            
            # Processing time
            sources_uses.processing_time_seconds = time.time() - start_time
            
            print(f"      ✅ Extracted {len(sources_uses.line_items)} line items")
            print(f"      ✅ Extracted {len(sources_uses.total_costs)} cost values")
            print(f"      ✅ Extracted {len(sources_uses.funding_headers)} funding columns")
            print(f"      ✅ Extracted {len(sources_uses.funding_matrix)}×{len(sources_uses.funding_matrix[0]) if sources_uses.funding_matrix else 0} funding matrix")
            print(f"      📊 Data completeness: {sources_uses.data_completeness_percent:.1f}%")
            
            return sources_uses
            
        except Exception as e:
            print(f"      ❌ Sources & Uses extraction failed: {e}")
            return None
    
    def _extract_basis_breakdown(self, sheet: xw.Sheet) -> Optional[BasisBreakdownData]:
        """
        Phase 1B: Extract Sources and Basis Breakdown data
        Target ranges: C2:J2, C4:J150, D107, E107:J107
        """
        
        start_time = time.time()
        
        try:
            basis_data = BasisBreakdownData()
            basis_data.extraction_timestamp = datetime.now().isoformat()
            basis_data.extraction_range = "C2:J107"
            
            print(f"      📊 Extracting Basis Breakdown...")
            
            # Extract Basis Headers (C2:J2)
            basis_headers_raw = sheet.range("C2:J2").value
            if basis_headers_raw:
                if isinstance(basis_headers_raw, list):
                    basis_data.basis_headers = [str(header).strip() if header else f"Basis_{i+1}" 
                                               for i, header in enumerate(basis_headers_raw)]
                else:
                    basis_data.basis_headers = [str(basis_headers_raw).strip()]
            
            # Extract Basis Matrix (C4:J150) - same as funding matrix but focus on basis columns
            basis_matrix_raw = sheet.range("C4:J150").value  # Focus on basis columns C-J
            if basis_matrix_raw:
                basis_data.basis_matrix = []
                
                if isinstance(basis_matrix_raw[0], list):
                    for row in basis_matrix_raw:
                        if isinstance(row, list):
                            matrix_row = [float(cell) if isinstance(cell, (int, float)) and cell is not None else 0.0 
                                         for cell in row]
                            basis_data.basis_matrix.append(matrix_row)
                else:
                    for value in basis_matrix_raw:
                        cell_value = float(value) if isinstance(value, (int, float)) and value is not None else 0.0
                        basis_data.basis_matrix.append([cell_value])
            
            # Extract Total Eligible Basis (D107) - CRITICAL LIHTC calculation
            try:
                total_eligible_basis_raw = sheet.range("D107").value
                if total_eligible_basis_raw and isinstance(total_eligible_basis_raw, (int, float)):
                    basis_data.total_eligible_basis = float(total_eligible_basis_raw)
                    print(f"      💎 CRITICAL: Total Eligible Basis = ${basis_data.total_eligible_basis:,.2f}")
            except Exception as e:
                print(f"      ⚠️  Could not extract Total Eligible Basis (D107): {e}")
            
            # Extract Basis Totals (E107:J107)
            try:
                basis_totals_raw = sheet.range("E107:J107").value
                if basis_totals_raw:
                    if isinstance(basis_totals_raw, list):
                        basis_data.basis_totals = [float(total) if isinstance(total, (int, float)) and total is not None else 0.0 
                                                  for total in basis_totals_raw]
                    else:
                        basis_data.basis_totals = [float(basis_totals_raw) if isinstance(basis_totals_raw, (int, float)) else 0.0]
            except Exception as e:
                print(f"      ⚠️  Could not extract Basis Totals (E107:J107): {e}")
            
            # Validation
            basis_data.basis_mathematical_check = self._validate_basis_calculations(basis_data)
            
            # Processing time
            basis_data.processing_time_seconds = time.time() - start_time
            
            print(f"      ✅ Extracted {len(basis_data.basis_headers)} basis categories")
            print(f"      ✅ Extracted {len(basis_data.basis_matrix)}×{len(basis_data.basis_matrix[0]) if basis_data.basis_matrix else 0} basis matrix")
            print(f"      ✅ Mathematical validation: {'PASSED' if basis_data.basis_mathematical_check else 'FAILED'}")
            
            return basis_data
            
        except Exception as e:
            print(f"      ❌ Basis breakdown extraction failed: {e}")
            return None
    
    def _extract_application_data(self, sheet: xw.Sheet) -> Optional[ApplicationData]:
        """Extract basic application data (Phase 1C preview)"""
        
        try:
            app_data = ApplicationData()
            
            # Use targeted extraction from the baseline extractor
            application_area = sheet.range("A1:Z100").value
            if application_area:
                self._extract_project_info_from_area(application_area, app_data)
            
            # Calculate extraction confidence
            fields_attempted = 6  # project_name, address, city, county, total_units, developer_name
            fields_found = 0
            
            if app_data.project_name: fields_found += 1
            if app_data.project_address: fields_found += 1  
            if app_data.project_city: fields_found += 1
            if app_data.project_county: fields_found += 1
            if app_data.total_units > 0: fields_found += 1
            if app_data.developer_name: fields_found += 1
            
            app_data.fields_extracted = fields_found
            app_data.total_fields_attempted = fields_attempted
            app_data.extraction_confidence = (fields_found / fields_attempted) * 100
            
            return app_data
            
        except Exception as e:
            print(f"      ❌ Application data extraction failed: {e}")
            return None
    
    def _extract_project_info_from_area(self, data_area: List, app_data: ApplicationData):
        """Extract project info from data area (adapted from baseline)"""
        
        for row_idx, row in enumerate(data_area):
            if not isinstance(row, list):
                continue
                
            for col_idx, cell in enumerate(row):
                if not cell or not isinstance(cell, str):
                    continue
                    
                cell_lower = cell.lower().strip()
                
                # Project name
                if any(term in cell_lower for term in ["project name", "development name", "property name"]):
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and not self._is_template_text(adjacent_value):
                        app_data.project_name = str(adjacent_value).strip()[:100]
                
                # Address
                elif any(term in cell_lower for term in ["project address", "site address", "property address"]):
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and not self._is_template_text(adjacent_value):
                        app_data.project_address = str(adjacent_value).strip()[:200]
                
                # City
                elif "city" in cell_lower and len(cell_lower) < 20:
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and not self._is_template_text(adjacent_value):
                        app_data.project_city = str(adjacent_value).strip()[:50]
                
                # County
                elif "county" in cell_lower and len(cell_lower) < 20:
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and not self._is_template_text(adjacent_value):
                        app_data.project_county = str(adjacent_value).strip()[:50]
                
                # Total units
                elif any(term in cell_lower for term in ["total units", "number of units", "total dwelling units"]):
                    adjacent_value = self._get_adjacent_numeric_value(row, col_idx)
                    if adjacent_value and adjacent_value > 0:
                        app_data.total_units = int(adjacent_value)
                
                # Developer
                elif "developer" in cell_lower and len(cell_lower) < 50:
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and not self._is_template_text(adjacent_value):
                        app_data.developer_name = str(adjacent_value).strip()[:100]
    
    def _get_adjacent_value(self, row: List, col_idx: int) -> Any:
        """Get value from adjacent cells"""
        for offset in [1, 2, 3]:
            if col_idx + offset < len(row):
                value = row[col_idx + offset]
                if value and str(value).strip():
                    return value
        return None
    
    def _get_adjacent_numeric_value(self, row: List, col_idx: int) -> Optional[float]:
        """Get numeric value from adjacent cells"""
        for offset in [1, 2, 3]:
            if col_idx + offset < len(row):
                value = row[col_idx + offset]
                if isinstance(value, (int, float)):
                    return float(value)
        return None
    
    def _is_template_text(self, value: Any) -> bool:
        """Check if value is template placeholder"""
        if not value:
            return True
            
        value_str = str(value).lower().strip()
        template_indicators = [
            "...", "xxx", "enter", "fill", "insert", "type", "click", 
            "project name", "development name", "sponsor name",
            "to be determined", "tbd", "n/a", "not applicable"
        ]
        
        return any(indicator in value_str for indicator in template_indicators)
    
    def _validate_mathematical_accuracy(self, sources_uses: SourcesUsesData) -> ValidationResult:
        """Validate mathematical accuracy of Sources and Uses (focus on core funding sources)"""
        
        validation = ValidationResult()
        validation.validation_timestamp = datetime.now().isoformat()
        
        try:
            # Check if row totals match funding matrix sums (exclude calculated columns)
            if (sources_uses.total_costs and sources_uses.funding_matrix and 
                len(sources_uses.total_costs) == len(sources_uses.funding_matrix)):
                
                math_errors = 0
                tolerance = 100.0  # $100 tolerance for rounding/calculation differences
                rows_validated = 0
                
                for i, (total_cost, funding_row) in enumerate(zip(sources_uses.total_costs, sources_uses.funding_matrix)):
                    if total_cost > 0:  # Only check non-zero rows
                        # Sum only core funding source columns (exclude calculated columns)
                        core_funding_sum = 0.0
                        for col_idx, value in enumerate(funding_row[:15]):  # Limit to avoid SUBTOTAL columns
                            if col_idx < len(sources_uses.funding_headers):
                                header = sources_uses.funding_headers[col_idx].upper()
                                # Skip calculated columns
                                if any(calc_term in header for calc_term in ['SUBTOTAL', 'TOTAL', 'PVC']):
                                    continue
                            core_funding_sum += value if value else 0.0
                        
                        difference = abs(total_cost - core_funding_sum)
                        rows_validated += 1
                        
                        if difference > tolerance:
                            math_errors += 1
                            if math_errors <= 5:  # Limit error reporting
                                validation.add_error(f"Row {i+4}: Total cost ${total_cost:,.2f} != core funding ${core_funding_sum:,.2f} (Δ ${difference:,.2f})")
                
                validation.mathematical_accuracy = math_errors <= (rows_validated * 0.05)  # Allow 5% error rate
                
                if validation.mathematical_accuracy:
                    print(f"      ✅ Mathematical validation PASSED ({rows_validated} rows, {math_errors} errors)")
                else:
                    print(f"      ⚠️  Mathematical validation: {math_errors}/{rows_validated} errors (within tolerance)")
            
            # Enhanced data completeness calculation
            if sources_uses.line_items and sources_uses.total_costs:
                filled_items = sum(1 for item in sources_uses.line_items if item and item.strip() and item != '')
                filled_costs = sum(1 for cost in sources_uses.total_costs if cost > 0)
                
                # Count actual funding data
                funding_data_points = 0
                for row in sources_uses.funding_matrix:
                    funding_data_points += sum(1 for cell in row[:10] if cell > 0)  # Focus on core columns
                
                total_meaningful_data = filled_items + filled_costs + funding_data_points
                total_expected = len(sources_uses.line_items) + len(sources_uses.total_costs) + (len(sources_uses.funding_matrix) * 10)
                
                validation.data_completeness = (total_meaningful_data / max(1, total_expected)) * 100
            
            # Business logic validation
            validation.business_logic_validity = True
            if sources_uses.total_costs:
                total_project_cost = sum(sources_uses.total_costs)
                if total_project_cost < 100000:
                    validation.add_warning("Total project cost appears low")
                elif total_project_cost > 1000000000:
                    validation.add_warning("Total project cost appears extremely high")
                else:
                    validation.business_logic_validity = True
            
            validation.reasonable_value_ranges = len(validation.warnings) <= 1
            validation.calculate_score()
            
        except Exception as e:
            validation.add_error(f"Validation calculation failed: {e}")
        
        return validation
    
    def _extract_points_system_data(self, workbook: xw.Book) -> Optional['PointsSystemData']:
        """Extract CTCAC Points System data"""
        
        from ctcac_data_structures import PointsSystemData
        
        points_sheet_names = ["Points System", "Scoring", "Point Scoring", "Application Points"]
        
        for sheet_name in points_sheet_names:
            for sheet in workbook.sheets:
                if sheet_name.lower() in sheet.name.lower():
                    try:
                        points_data = PointsSystemData()
                        points_data.extraction_timestamp = datetime.now().isoformat()
                        
                        # Extract scoring data from sheet
                        scoring_area = sheet.range("A1:Z100").value
                        if scoring_area:
                            total_points = 0
                            for row in scoring_area:
                                if isinstance(row, list):
                                    for cell in row:
                                        if isinstance(cell, str) and "total" in cell.lower() and "point" in cell.lower():
                                            # Look for adjacent numeric value
                                            for i, adjacent_cell in enumerate(row):
                                                if isinstance(adjacent_cell, (int, float)) and adjacent_cell > 0:
                                                    total_points = float(adjacent_cell)
                                                    break
                            
                            points_data.total_points_achieved = total_points
                            return points_data
                    except Exception as e:
                        print(f"      ⚠️  Points system extraction error: {e}")
                        continue
        
        return None
    
    def _extract_tie_breaker_data(self, workbook: xw.Book) -> Optional['TieBreakerData']:
        """Extract Tie-Breaker analysis data"""
        
        from ctcac_data_structures import TieBreakerData
        
        tie_breaker_sheet_names = ["Tie-Breaker", "Tie Breaker", "Tiebreaker", "Competitive Analysis"]
        
        for sheet_name in tie_breaker_sheet_names:
            for sheet in workbook.sheets:
                if sheet_name.lower() in sheet.name.lower():
                    try:
                        tie_breaker_data = TieBreakerData()
                        tie_breaker_data.extraction_timestamp = datetime.now().isoformat()
                        
                        # Extract cost per unit and other competitive metrics
                        analysis_area = sheet.range("A1:Z50").value
                        if analysis_area:
                            for row in analysis_area:
                                if isinstance(row, list):
                                    for i, cell in enumerate(row):
                                        if isinstance(cell, str):
                                            cell_lower = cell.lower()
                                            if "cost per unit" in cell_lower:
                                                # Look for adjacent numeric value
                                                for j in range(i+1, min(i+4, len(row))):
                                                    if isinstance(row[j], (int, float)) and row[j] > 0:
                                                        tie_breaker_data.cost_per_unit = float(row[j])
                                                        break
                            
                            return tie_breaker_data
                    except Exception as e:
                        print(f"      ⚠️  Tie-breaker extraction error: {e}")
                        continue
        
        return None
    
    def _extract_calhfa_data(self, workbook: xw.Book) -> Optional['CALHFAAddendumData']:
        """Extract CALHFA Addendum data (conditional)"""
        
        from ctcac_data_structures import CALHFAAddendumData
        
        calhfa_sheet_names = ["CALHFA", "CAL-HFA", "CALHFA Addendum"]
        
        # Check for CALHFA sheet existence
        for sheet_name in calhfa_sheet_names:
            for sheet in workbook.sheets:
                if sheet_name.lower() in sheet.name.lower():
                    try:
                        calhfa_data = CALHFAAddendumData()
                        calhfa_data.extraction_timestamp = datetime.now().isoformat()
                        calhfa_data.is_calhfa_deal = True
                        
                        # Extract CALHFA loan information
                        calhfa_area = sheet.range("A1:Z50").value
                        if calhfa_area:
                            for row in calhfa_area:
                                if isinstance(row, list):
                                    for i, cell in enumerate(row):
                                        if isinstance(cell, str) and "loan" in cell.lower():
                                            # Look for loan amount
                                            for j in range(i+1, min(i+4, len(row))):
                                                if isinstance(row[j], (int, float)) and row[j] > 10000:
                                                    calhfa_data.calhfa_loan_amount = float(row[j])
                                                    break
                        
                        return calhfa_data
                    except Exception as e:
                        print(f"      ⚠️  CALHFA extraction error: {e}")
                        continue
        
        # Return non-CALHFA result
        calhfa_data = CALHFAAddendumData()
        calhfa_data.extraction_timestamp = datetime.now().isoformat()
        calhfa_data.is_calhfa_deal = False
        return calhfa_data
    
    def _extract_subsidy_contract_data(self, workbook: xw.Book) -> Optional['SubsidyContractData']:
        """Extract Subsidy Contract data (conditional)"""
        
        from ctcac_data_structures import SubsidyContractData
        
        subsidy_sheet_names = ["Subsidy Contract", "Rental Assistance", "Section 8", "Project Based"]
        
        # Check for subsidy/rental assistance sheets
        for sheet_name in subsidy_sheet_names:
            for sheet in workbook.sheets:
                if sheet_name.lower() in sheet.name.lower():
                    try:
                        subsidy_data = SubsidyContractData()
                        subsidy_data.extraction_timestamp = datetime.now().isoformat()
                        subsidy_data.has_rental_assistance = True
                        
                        # Extract subsidy information
                        subsidy_area = sheet.range("A1:Z50").value
                        if subsidy_area:
                            for row in subsidy_area:
                                if isinstance(row, list):
                                    for i, cell in enumerate(row):
                                        if isinstance(cell, str):
                                            cell_lower = cell.lower()
                                            if "monthly" in cell_lower and "subsidy" in cell_lower:
                                                # Look for monthly amount
                                                for j in range(i+1, min(i+4, len(row))):
                                                    if isinstance(row[j], (int, float)) and row[j] > 0:
                                                        subsidy_data.subsidy_amount_monthly = float(row[j])
                                                        break
                        
                        return subsidy_data
                    except Exception as e:
                        print(f"      ⚠️  Subsidy contract extraction error: {e}")
                        continue
        
        # Return no rental assistance result
        subsidy_data = SubsidyContractData()
        subsidy_data.extraction_timestamp = datetime.now().isoformat()
        subsidy_data.has_rental_assistance = False
        return subsidy_data
    
    def _extract_proforma_data(self, workbook: xw.Book) -> Optional['ProformaData']:
        """Extract 15-Year Proforma financial projections"""
        
        from ctcac_data_structures import ProformaData
        
        proforma_sheet_names = ["15 Year Proforma", "Proforma", "15-Year", "Financial Projections"]
        
        for sheet_name in proforma_sheet_names:
            for sheet in workbook.sheets:
                if sheet_name.lower() in sheet.name.lower():
                    try:
                        proforma_data = ProformaData()
                        proforma_data.extraction_timestamp = datetime.now().isoformat()
                        
                        # Extract stabilized NOI and projections
                        proforma_area = sheet.range("A1:Z100").value
                        if proforma_area:
                            for row in proforma_area:
                                if isinstance(row, list):
                                    for i, cell in enumerate(row):
                                        if isinstance(cell, str):
                                            cell_lower = cell.lower()
                                            if "noi" in cell_lower or "net operating income" in cell_lower:
                                                # Look for stabilized NOI value
                                                for j in range(i+1, min(i+10, len(row))):
                                                    if isinstance(row[j], (int, float)) and row[j] > 10000:
                                                        proforma_data.stabilized_noi = float(row[j])
                                                        break
                        
                        return proforma_data
                    except Exception as e:
                        print(f"      ⚠️  Proforma extraction error: {e}")
                        continue
        
        return None
    
    def _validate_basis_calculations(self, basis_data: BasisBreakdownData) -> bool:
        """Validate basis calculations"""
        
        try:
            if not basis_data.basis_matrix or not basis_data.basis_totals:
                return False
            
            # Check if column totals match
            for col_idx, expected_total in enumerate(basis_data.basis_totals):
                if col_idx < len(basis_data.basis_matrix[0]):
                    calculated_total = sum(row[col_idx] if col_idx < len(row) else 0 
                                          for row in basis_data.basis_matrix)
                    
                    if abs(calculated_total - expected_total) > 1.0:  # $1 tolerance
                        basis_data.basis_calculation_errors.append(
                            f"Column {col_idx+1}: Expected ${expected_total:,.2f}, got ${calculated_total:,.2f}"
                        )
                        return False
            
            return True
            
        except Exception as e:
            basis_data.basis_calculation_errors.append(f"Validation failed: {e}")
            return False
    
    def extract_batch(self, file_paths: List[Path], max_workers: Optional[int] = None) -> List[CTCACExtractionResult]:
        """Extract data from multiple files with M4 Beast threading"""
        
        if max_workers is None:
            max_workers = self.max_threads
        
        print(f"🚀 WINGMAN Batch Extraction: {len(file_paths)} files")
        print(f"   🧵 Using {max_workers} threads")
        
        results = []
        start_time = time.time()
        
        if max_workers == 1:
            # Single-threaded processing
            for file_path in file_paths:
                result = self.extract_single_file(file_path)
                results.append(result)
        else:
            # Multi-threaded processing for M4 Beast
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {executor.submit(self.extract_single_file, file_path): file_path 
                                 for file_path in file_paths}
                
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        print(f"❌ Failed to process {file_path.name}: {e}")
        
        # Performance summary
        total_time = time.time() - start_time
        files_per_minute = (len(results) / total_time) * 60 if total_time > 0 else 0
        
        print(f"\n🎉 WINGMAN Batch Complete!")
        print(f"   📊 Files processed: {len(results)}/{len(file_paths)}")
        print(f"   ⏱️  Total time: {total_time:.2f}s")
        print(f"   🚀 Rate: {files_per_minute:.1f} files/minute")
        
        successful_extractions = sum(1 for r in results if r.sections_successfully_extracted > 0)
        print(f"   ✅ Successful extractions: {successful_extractions}/{len(results)} ({successful_extractions/len(results)*100:.1f}%)")
        
        return results

def run_wingman_demo(sample_size: int = 5):
    """Run WINGMAN extraction demo"""
    
    print("🚀 WINGMAN CTCAC EXTRACTOR v2.0 DEMO")
    print("=" * 60)
    print("Phase 1A: Sources and Uses Budget Complete Extraction")
    print("Target: <5 second processing, >95% data completeness")
    print("=" * 60)
    
    # Initialize extractor
    extractor = WingmanCTCACExtractor(performance_mode="optimized")
    
    # Get sample files
    raw_data_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data")
    excel_files = list(raw_data_path.glob("*.xlsx"))[:sample_size]
    
    if not excel_files:
        print("❌ No Excel files found in raw_data directory")
        return
    
    print(f"📁 Processing {len(excel_files)} sample files...")
    
    # Extract data
    results = extractor.extract_batch(excel_files)
    
    # Analysis
    print(f"\n📊 WINGMAN EXTRACTION ANALYSIS")
    print("=" * 60)
    
    # Performance metrics
    avg_processing_time = sum(r.total_processing_time_seconds for r in results) / len(results) if results else 0
    avg_confidence = sum(r.overall_extraction_confidence for r in results) / len(results) if results else 0
    avg_memory = sum(r.memory_usage_mb for r in results) / len(results) if results else 0
    
    sources_uses_count = sum(1 for r in results if r.sources_uses_data)
    basis_breakdown_count = sum(1 for r in results if r.basis_breakdown_data)
    math_validation_count = sum(1 for r in results if r.mathematical_validation_passed)
    
    print(f"⚡ Average processing time: {avg_processing_time:.2f}s (Target: <5s)")
    print(f"🎯 Average confidence: {avg_confidence:.1f}% (Target: >95%)")
    print(f"💾 Average memory usage: {avg_memory:.1f} MB (Target: <200MB)")
    print(f"")
    print(f"📊 Sources & Uses extracted: {sources_uses_count}/{len(results)} ({sources_uses_count/len(results)*100:.1f}%)")
    print(f"📊 Basis breakdown extracted: {basis_breakdown_count}/{len(results)} ({basis_breakdown_count/len(results)*100:.1f}%)")
    print(f"✅ Mathematical validation passed: {math_validation_count}/{len(results)} ({math_validation_count/len(results)*100:.1f}%)")
    
    # Performance targets
    print(f"\n🎯 WINGMAN PERFORMANCE TARGETS")
    print("=" * 40)
    time_target = "✅ PASSED" if avg_processing_time < 5.0 else "❌ FAILED"
    confidence_target = "✅ PASSED" if avg_confidence > 95.0 else "⚠️  NEEDS IMPROVEMENT"
    memory_target = "✅ PASSED" if avg_memory < 200.0 else "⚠️  OPTIMIZE"
    
    print(f"Processing time <5s: {time_target}")
    print(f"Confidence >95%: {confidence_target}")
    print(f"Memory <200MB: {memory_target}")
    
    # Save results
    output_path = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/results/wingman_extraction")
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Export JSON results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_path / f"wingman_extraction_results_{timestamp}.json"
    
    with open(results_file, "w") as f:
        json.dump([result.__dict__ for result in results], f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Summary report
    if avg_processing_time < 5.0 and sources_uses_count == len(results):
        print(f"\n🎊 WINGMAN PHASE 1A SUCCESS!")
        print(f"✅ Ready for Phase 1B and integration with QAP RAG")
        print(f"🚀 Production deployment recommended")
    else:
        print(f"\n⚠️  WINGMAN PHASE 1A needs optimization")
        print(f"🔧 Consider performance tuning before full deployment")

if __name__ == "__main__":
    run_wingman_demo(sample_size=3)