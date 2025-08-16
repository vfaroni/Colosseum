#!/usr/bin/env python3
"""
Enhanced Application Tab Extractor
Comprehensive LIHTC data extraction from CTCAC Application sheets
WINGMAN-01 Phase 1B Implementation
"""

import xlwings as xw
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from ctcac_data_structures import ApplicationData

class EnhancedApplicationExtractor:
    """
    Enhanced Application tab extractor with comprehensive LIHTC data coverage
    """
    
    def __init__(self):
        # Application sheet priorities
        self.application_sheet_names = [
            "Application",
            "App", 
            "Project Application",
            "Main Application"
        ]
        
        # Search patterns for key data
        self.unit_type_patterns = [
            r"studio|efficiency|eff\.?",
            r"1\s*br|one\s*bedroom",
            r"2\s*br|two\s*bedroom", 
            r"3\s*br|three\s*bedroom",
            r"4\s*br|four\s*bedroom",
            r"5\s*br|five\s*bedroom"
        ]
        
        self.ami_patterns = [
            r"30%?\s*ami|30%?\s*area\s*median",
            r"50%?\s*ami|50%?\s*area\s*median", 
            r"60%?\s*ami|60%?\s*area\s*median",
            r"80%?\s*ami|80%?\s*area\s*median",
            r"100%?\s*ami|100%?\s*area\s*median|market\s*rate"
        ]
        
        print("🔧 Enhanced Application Extractor initialized")
        print("   📊 Targeting 35+ critical LIHTC data fields")
        print("   🎯 AMI levels, rents, operating expenses, financing")

    def extract_comprehensive_application_data(self, workbook: xw.Book) -> Optional[ApplicationData]:
        """
        Extract comprehensive application data from CTCAC Application sheet
        """
        
        # Find Application sheet
        application_sheet = self._find_application_sheet(workbook)
        if not application_sheet:
            print("   ⚠️  No Application sheet found")
            return None
        
        print(f"   🎯 Found Application sheet: '{application_sheet.name}'")
        
        app_data = ApplicationData()
        app_data.extraction_timestamp = datetime.now().isoformat()
        
        try:
            # Extract data in large area for comprehensive coverage
            print("   📊 Reading comprehensive application area...")
            application_area = application_sheet.range("A1:AZ500").value
            
            if not application_area:
                print("   ❌ Application sheet appears empty")
                return None
            
            # Extract different categories of data
            self._extract_project_identification(application_area, app_data)
            self._extract_unit_information(application_area, app_data)
            self._extract_ami_and_rent_data(application_area, app_data)
            self._extract_operating_expenses(application_area, app_data)
            self._extract_developer_information(application_area, app_data)
            self._extract_financing_structure(application_area, app_data)
            self._extract_construction_details(application_area, app_data)
            self._extract_timeline_information(application_area, app_data)
            self._extract_special_programs(application_area, app_data)
            
            # Calculate extraction confidence
            self._calculate_extraction_confidence(app_data)
            
            print(f"   ✅ Enhanced extraction: {app_data.fields_extracted}/{app_data.total_fields_attempted} fields ({app_data.extraction_confidence:.1f}% confidence)")
            
            return app_data
            
        except Exception as e:
            print(f"   ❌ Enhanced application extraction failed: {e}")
            return None

    def _find_application_sheet(self, workbook: xw.Book) -> Optional[xw.Sheet]:
        """Find main Application sheet"""
        
        for sheet_name in self.application_sheet_names:
            for sheet in workbook.sheets:
                if sheet_name.lower() in sheet.name.lower():
                    return sheet
        
        return None

    def _extract_project_identification(self, data_area: List, app_data: ApplicationData):
        """Extract project identification data"""
        
        print("      🏗️  Extracting project identification...")
        
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
                        app_data.fields_extracted += 1
                
                # Address components
                elif any(term in cell_lower for term in ["project address", "site address", "property address"]):
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and not self._is_template_text(adjacent_value):
                        app_data.project_address = str(adjacent_value).strip()[:200]
                        app_data.fields_extracted += 1
                
                elif "city" in cell_lower and len(cell_lower) < 20:
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and not self._is_template_text(adjacent_value):
                        app_data.project_city = str(adjacent_value).strip()[:50]
                        app_data.fields_extracted += 1
                
                elif "county" in cell_lower and len(cell_lower) < 20:
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and not self._is_template_text(adjacent_value):
                        app_data.project_county = str(adjacent_value).strip()[:50]
                        app_data.fields_extracted += 1
                
                elif any(term in cell_lower for term in ["zip", "postal"]):
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and str(adjacent_value).isdigit():
                        app_data.project_zip = str(adjacent_value).strip()[:10]
                        app_data.fields_extracted += 1
                
                elif any(term in cell_lower for term in ["census tract", "tract number"]):
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value:
                        app_data.census_tract = str(adjacent_value).strip()[:20]
                        app_data.fields_extracted += 1

    def _extract_unit_information(self, data_area: List, app_data: ApplicationData):
        """Extract unit mix and count information"""
        
        print("      🏠 Extracting unit information...")
        
        for row_idx, row in enumerate(data_area):
            if not isinstance(row, list):
                continue
                
            for col_idx, cell in enumerate(row):
                if not cell or not isinstance(cell, str):
                    continue
                    
                cell_lower = cell.lower().strip()
                
                # Total units
                if any(term in cell_lower for term in ["total units", "number of units", "total dwelling units"]):
                    adjacent_value = self._get_adjacent_numeric_value(row, col_idx)
                    if adjacent_value and adjacent_value > 0:
                        app_data.total_units = int(adjacent_value)
                        app_data.fields_extracted += 1
                
                # Affordable units
                elif any(term in cell_lower for term in ["affordable units", "low income units", "lihtc units"]):
                    adjacent_value = self._get_adjacent_numeric_value(row, col_idx)
                    if adjacent_value and adjacent_value > 0:
                        app_data.affordable_units = int(adjacent_value)
                        app_data.fields_extracted += 1
                
                # Unit mix by bedroom count
                for i, unit_pattern in enumerate(self.unit_type_patterns):
                    if re.search(unit_pattern, cell_lower):
                        unit_type = ["Studio", "1BR", "2BR", "3BR", "4BR", "5BR"][i]
                        adjacent_value = self._get_adjacent_numeric_value(row, col_idx)
                        if adjacent_value and adjacent_value > 0:
                            app_data.unit_mix_details[unit_type] = int(adjacent_value)
                            app_data.fields_extracted += 1

    def _extract_ami_and_rent_data(self, data_area: List, app_data: ApplicationData):
        """Extract AMI targeting and rent information"""
        
        print("      💰 Extracting AMI and rent data...")
        
        # Look for AMI unit tables and rent schedules
        for row_idx, row in enumerate(data_area):
            if not isinstance(row, list):
                continue
            
            # Check for AMI level indicators in headers or labels
            for col_idx, cell in enumerate(row):
                if not cell or not isinstance(cell, str):
                    continue
                    
                cell_lower = cell.lower().strip()
                
                # AMI level detection
                for ami_pattern in self.ami_patterns:
                    if re.search(ami_pattern, cell_lower):
                        ami_level = self._extract_ami_percentage(cell_lower)
                        if ami_level and ami_level not in app_data.ami_levels_served:
                            app_data.ami_levels_served.append(ami_level)
                            app_data.fields_extracted += 1
                
                # Rent information
                if any(term in cell_lower for term in ["rent", "rental rate"]):
                    # Look for unit type and rent amount in surrounding cells
                    unit_type, rent_amount = self._extract_rent_data_from_context(data_area, row_idx, col_idx)
                    if unit_type and rent_amount:
                        if "market" in cell_lower or "100%" in cell_lower:
                            app_data.market_rents_by_unit_type[unit_type] = rent_amount
                        else:
                            app_data.lihtc_rents_by_unit_type[unit_type] = rent_amount
                        app_data.fields_extracted += 1

    def _extract_operating_expenses(self, data_area: List, app_data: ApplicationData):
        """Extract operating expense information"""
        
        print("      📊 Extracting operating expenses...")
        
        expense_categories = {
            "property tax": "Property_Taxes",
            "insurance": "Insurance", 
            "management": "Management",
            "maintenance": "Maintenance",
            "utilities": "Utilities",
            "replacement reserve": "Replacement_Reserve",
            "administrative": "Administrative"
        }
        
        for row_idx, row in enumerate(data_area):
            if not isinstance(row, list):
                continue
                
            for col_idx, cell in enumerate(row):
                if not cell or not isinstance(cell, str):
                    continue
                    
                cell_lower = cell.lower().strip()
                
                # Total operating expenses
                if any(term in cell_lower for term in ["total operating", "annual operating", "operating expense"]):
                    adjacent_value = self._get_adjacent_numeric_value(row, col_idx)
                    if adjacent_value and adjacent_value > 0:
                        app_data.annual_operating_expenses = float(adjacent_value)
                        app_data.fields_extracted += 1
                
                # Individual expense categories
                for expense_term, expense_key in expense_categories.items():
                    if expense_term in cell_lower and len(cell_lower) < 50:
                        adjacent_value = self._get_adjacent_numeric_value(row, col_idx)
                        if adjacent_value and adjacent_value > 0:
                            app_data.operating_expense_breakdown[expense_key] = float(adjacent_value)
                            app_data.fields_extracted += 1

    def _extract_developer_information(self, data_area: List, app_data: ApplicationData):
        """Extract developer and team information"""
        
        print("      👥 Extracting developer information...")
        
        for row_idx, row in enumerate(data_area):
            if not isinstance(row, list):
                continue
                
            for col_idx, cell in enumerate(row):
                if not cell or not isinstance(cell, str):
                    continue
                    
                cell_lower = cell.lower().strip()
                
                # Developer name
                if "developer" in cell_lower and len(cell_lower) < 50:
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and not self._is_template_text(adjacent_value):
                        app_data.developer_name = str(adjacent_value).strip()[:100]
                        app_data.fields_extracted += 1
                
                # Contact information
                elif any(term in cell_lower for term in ["contact person", "contact name"]):
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and not self._is_template_text(adjacent_value):
                        app_data.developer_contact_person = str(adjacent_value).strip()[:100]
                        app_data.fields_extracted += 1
                
                elif "phone" in cell_lower:
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and self._is_phone_number(str(adjacent_value)):
                        app_data.developer_phone = str(adjacent_value).strip()[:20]
                        app_data.fields_extracted += 1
                
                elif "email" in cell_lower:
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and "@" in str(adjacent_value):
                        app_data.developer_email = str(adjacent_value).strip()[:100]
                        app_data.fields_extracted += 1
                
                # General Partner
                elif any(term in cell_lower for term in ["general partner", "gp name"]):
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and not self._is_template_text(adjacent_value):
                        app_data.general_partner = str(adjacent_value).strip()[:100]
                        app_data.fields_extracted += 1
                
                # Management Company
                elif any(term in cell_lower for term in ["management company", "property management"]):
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and not self._is_template_text(adjacent_value):
                        app_data.management_company = str(adjacent_value).strip()[:100]
                        app_data.fields_extracted += 1

    def _extract_financing_structure(self, data_area: List, app_data: ApplicationData):
        """Extract financing sources and structure"""
        
        print("      💳 Extracting financing structure...")
        
        financing_sources = {
            "tax credit": "Tax_Credit_Equity",
            "bank loan": "Bank_Loan",
            "construction loan": "Construction_Loan", 
            "permanent loan": "Permanent_Loan",
            "city loan": "City_Loan",
            "county loan": "County_Loan",
            "state loan": "State_Loan",
            "deferred developer fee": "Deferred_Dev_Fee",
            "gap funding": "Gap_Funding",
            "seller financing": "Seller_Financing"
        }
        
        for row_idx, row in enumerate(data_area):
            if not isinstance(row, list):
                continue
                
            for col_idx, cell in enumerate(row):
                if not cell or not isinstance(cell, str):
                    continue
                    
                cell_lower = cell.lower().strip()
                
                # Total development cost
                if any(term in cell_lower for term in ["total development cost", "total project cost"]):
                    adjacent_value = self._get_adjacent_numeric_value(row, col_idx)
                    if adjacent_value and adjacent_value > 0:
                        app_data.total_development_cost = float(adjacent_value)
                        app_data.fields_extracted += 1
                
                # Tax credit request
                elif any(term in cell_lower for term in ["tax credit request", "credit amount"]):
                    adjacent_value = self._get_adjacent_numeric_value(row, col_idx)
                    if adjacent_value and adjacent_value > 0:
                        app_data.tax_credit_request = float(adjacent_value)
                        app_data.fields_extracted += 1
                
                # Individual financing sources
                for source_term, source_key in financing_sources.items():
                    if source_term in cell_lower:
                        adjacent_value = self._get_adjacent_numeric_value(row, col_idx)
                        if adjacent_value and adjacent_value > 0:
                            app_data.financing_sources[source_key] = float(adjacent_value)
                            app_data.fields_extracted += 1

    def _extract_construction_details(self, data_area: List, app_data: ApplicationData):
        """Extract construction and building details"""
        
        print("      🏗️  Extracting construction details...")
        
        for row_idx, row in enumerate(data_area):
            if not isinstance(row, list):
                continue
                
            for col_idx, cell in enumerate(row):
                if not cell or not isinstance(cell, str):
                    continue
                    
                cell_lower = cell.lower().strip()
                
                # Project type
                if any(term in cell_lower for term in ["project type", "construction type"]):
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and not self._is_template_text(adjacent_value):
                        project_type = str(adjacent_value).strip()
                        if any(pt in project_type.lower() for pt in ["new", "rehab", "acquisition"]):
                            app_data.project_type = project_type[:50]
                            app_data.fields_extracted += 1
                
                # Building stories
                elif any(term in cell_lower for term in ["stories", "floors"]):
                    adjacent_value = self._get_adjacent_numeric_value(row, col_idx)
                    if adjacent_value and 1 <= adjacent_value <= 20:
                        app_data.building_stories = int(adjacent_value)
                        app_data.fields_extracted += 1
                
                # Building area
                elif any(term in cell_lower for term in ["building area", "gross area", "square feet"]):
                    adjacent_value = self._get_adjacent_numeric_value(row, col_idx)
                    if adjacent_value and adjacent_value > 1000:
                        app_data.gross_building_area = float(adjacent_value)
                        app_data.fields_extracted += 1
                
                # Parking spaces
                elif any(term in cell_lower for term in ["parking spaces", "parking stalls"]):
                    adjacent_value = self._get_adjacent_numeric_value(row, col_idx)
                    if adjacent_value and adjacent_value > 0:
                        app_data.parking_spaces = int(adjacent_value)
                        app_data.fields_extracted += 1

    def _extract_timeline_information(self, data_area: List, app_data: ApplicationData):
        """Extract development timeline dates"""
        
        print("      📅 Extracting timeline information...")
        
        for row_idx, row in enumerate(data_area):
            if not isinstance(row, list):
                continue
                
            for col_idx, cell in enumerate(row):
                if not cell or not isinstance(cell, str):
                    continue
                    
                cell_lower = cell.lower().strip()
                
                # Construction start
                if any(term in cell_lower for term in ["construction start", "start of construction"]):
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and self._is_date_like(str(adjacent_value)):
                        app_data.construction_start_date = str(adjacent_value).strip()[:20]
                        app_data.fields_extracted += 1
                
                # Construction completion
                elif any(term in cell_lower for term in ["construction completion", "completion date"]):
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and self._is_date_like(str(adjacent_value)):
                        app_data.construction_completion_date = str(adjacent_value).strip()[:20]
                        app_data.fields_extracted += 1
                
                # Placed in service
                elif any(term in cell_lower for term in ["placed in service", "pis date"]):
                    adjacent_value = self._get_adjacent_value(row, col_idx)
                    if adjacent_value and self._is_date_like(str(adjacent_value)):
                        app_data.placed_in_service_date = str(adjacent_value).strip()[:20]
                        app_data.fields_extracted += 1

    def _extract_special_programs(self, data_area: List, app_data: ApplicationData):
        """Extract special programs and certifications"""
        
        print("      🌟 Extracting special programs...")
        
        special_populations = ["senior", "homeless", "veteran", "disabled", "farmworker"]
        green_certifications = ["leed", "greenpoint", "energy star", "zero net energy"]
        
        for row_idx, row in enumerate(data_area):
            if not isinstance(row, list):
                continue
                
            for col_idx, cell in enumerate(row):
                if not cell or not isinstance(cell, str):
                    continue
                    
                cell_lower = cell.lower().strip()
                
                # Special needs populations
                for population in special_populations:
                    if population in cell_lower:
                        if population.title() not in app_data.special_needs_population:
                            app_data.special_needs_population.append(population.title())
                            app_data.fields_extracted += 1
                
                # Green building certifications
                for certification in green_certifications:
                    if certification in cell_lower:
                        app_data.green_building_certification = certification.upper()
                        app_data.fields_extracted += 1
                        break

    # Helper methods
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
                elif isinstance(value, str) and value.replace(',', '').replace('$', '').replace('.', '').isdigit():
                    try:
                        return float(value.replace(',', '').replace('$', ''))
                    except:
                        continue
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

    def _is_phone_number(self, value: str) -> bool:
        """Check if value looks like a phone number"""
        phone_pattern = r'[\(\)\-\s\d]{10,}'
        return bool(re.search(phone_pattern, value))

    def _is_date_like(self, value: str) -> bool:
        """Check if value looks like a date"""
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{1,2}-\d{1,2}-\d{2,4}',
            r'\w+\s+\d{1,2},?\s+\d{4}'
        ]
        return any(re.search(pattern, value) for pattern in date_patterns)

    def _extract_ami_percentage(self, text: str) -> Optional[str]:
        """Extract AMI percentage from text"""
        ami_match = re.search(r'(\d{1,3})%?\s*ami', text.lower())
        if ami_match:
            return f"{ami_match.group(1)}%"
        return None

    def _extract_rent_data_from_context(self, data_area: List, row_idx: int, col_idx: int) -> Tuple[Optional[str], Optional[float]]:
        """Extract unit type and rent amount from surrounding context"""
        # Look in current row and adjacent rows for unit type and rent amount
        for r_offset in [-1, 0, 1]:
            if 0 <= row_idx + r_offset < len(data_area):
                row = data_area[row_idx + r_offset]
                if isinstance(row, list):
                    for c_offset in range(-3, 4):
                        if 0 <= col_idx + c_offset < len(row):
                            cell = row[col_idx + c_offset]
                            if isinstance(cell, str):
                                # Check for unit type
                                for i, pattern in enumerate(self.unit_type_patterns):
                                    if re.search(pattern, cell.lower()):
                                        unit_type = ["Studio", "1BR", "2BR", "3BR", "4BR", "5BR"][i]
                                        # Look for rent amount nearby
                                        rent_amount = self._find_rent_amount_nearby(data_area, row_idx, col_idx)
                                        if rent_amount:
                                            return unit_type, rent_amount
        return None, None

    def _find_rent_amount_nearby(self, data_area: List, row_idx: int, col_idx: int) -> Optional[float]:
        """Find rent amount in nearby cells"""
        for r_offset in [-2, -1, 0, 1, 2]:
            if 0 <= row_idx + r_offset < len(data_area):
                row = data_area[row_idx + r_offset]
                if isinstance(row, list):
                    for c_offset in range(-5, 6):
                        if 0 <= col_idx + c_offset < len(row):
                            cell = row[col_idx + c_offset]
                            if isinstance(cell, (int, float)) and 500 <= cell <= 5000:
                                return float(cell)
                            elif isinstance(cell, str):
                                # Try to extract numeric value from string
                                rent_match = re.search(r'\$?(\d{1,4})', cell.replace(',', ''))
                                if rent_match:
                                    rent_val = int(rent_match.group(1))
                                    if 500 <= rent_val <= 5000:
                                        return float(rent_val)
        return None

    def _calculate_extraction_confidence(self, app_data: ApplicationData):
        """Calculate overall extraction confidence"""
        
        # Calculate per-unit operating expenses if possible
        if app_data.annual_operating_expenses > 0 and app_data.total_units > 0:
            app_data.operating_expense_per_unit = app_data.annual_operating_expenses / app_data.total_units
        
        # Calculate market rate units
        if app_data.total_units > 0 and app_data.affordable_units > 0:
            app_data.market_rate_units = app_data.total_units - app_data.affordable_units
        
        # Calculate extraction confidence
        app_data.extraction_confidence = (app_data.fields_extracted / app_data.total_fields_attempted) * 100
        
        print(f"      📊 Extraction summary:")
        print(f"         Fields extracted: {app_data.fields_extracted}/{app_data.total_fields_attempted}")
        print(f"         Confidence: {app_data.extraction_confidence:.1f}%")
        print(f"         Project: {app_data.project_name or 'Not found'}")
        print(f"         Developer: {app_data.developer_name or 'Not found'}")
        print(f"         Total units: {app_data.total_units or 'Not found'}")
        print(f"         AMI levels: {len(app_data.ami_levels_served)} found")
        print(f"         Financing sources: {len(app_data.financing_sources)} found")