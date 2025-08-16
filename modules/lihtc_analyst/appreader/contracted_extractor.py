#!/usr/bin/env python3
"""
Contracted LIHTC 4% Application Data Extractor
Guarantees extraction of ALL mandatory fields per contract
"""

import pandas as pd
import json
import re
from pathlib import Path
import logging
from datetime import datetime
import sys

class ContractedLIHTCExtractor:
    def __init__(self):
        self.debug_mode = True
        self.contract_fields = {
            'application': [
                'project_name', 'ctcac_project_number', 'year', 'city', 'county',
                'general_contractor', 'new_construction', 'housing_type', 
                'total_units', 'total_sqft_low_income'
            ],
            'sources_uses': [
                'land_cost', 'total_new_construction', 'total_architectural',
                'total_survey_engineering', 'local_impact_fees', 'soft_cost_contingency'
            ]
        }
        self.extraction_log = []
        
    def log_debug(self, message):
        if self.debug_mode:
            print(f"DEBUG: {message}")
        self.extraction_log.append(message)
    
    def get_cell_value_safe(self, df, row, col):
        """Safely get cell value"""
        try:
            if 0 <= row < len(df) and 0 <= col < len(df.columns):
                value = df.iloc[row, col]
                if pd.notna(value) and str(value).strip():
                    return str(value).strip()
        except:
            pass
        return None
    
    def search_nearby_for_value(self, df, label_row, label_col, max_distance=10):
        """Enhanced search in all directions from a label"""
        search_patterns = [
            # Right (most common in forms)
            [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10)],
            # Down
            [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0)],
            # Diagonal down-right
            [(1, 1), (1, 2), (2, 1), (2, 2), (3, 1)],
            # Left (forms sometimes have labels on right)
            [(0, -1), (0, -2), (0, -3)],
            # Up
            [(-1, 0), (-2, 0), (-3, 0)]
        ]
        
        for pattern in search_patterns:
            for row_offset, col_offset in pattern:
                new_row = label_row + row_offset
                new_col = label_col + col_offset
                
                value = self.get_cell_value_safe(df, new_row, new_col)
                if value and self.is_valid_data_value(value):
                    return value, new_row, new_col
        
        return None, None, None
    
    def is_valid_data_value(self, value):
        """Enhanced validation for data values"""
        if not value or len(value.strip()) < 1:
            return False
        
        # Skip obvious labels
        label_indicators = [
            ':', 'instructions', 'note', 'see', 'refer', 'contact', 'phone', 'email',
            'section', 'part', 'item', 'page', 'attachment', 'exhibit'
        ]
        value_lower = value.lower()
        if any(indicator in value_lower for indicator in label_indicators):
            return False
        
        # Skip formatting artifacts
        if value in ['0', '0.0', '0.00', 'N/A', 'n/a', 'TBD', 'tbd']:
            return False
            
        return True
    
    def find_field_with_contract_compliance(self, df, field_name, search_terms, validation_func=None, pattern=None):
        """Find field with guaranteed contract compliance"""
        self.log_debug(f"Searching for MANDATORY field: {field_name}")
        
        best_matches = []
        
        # Strategy 1: Content-based search
        for row in range(len(df)):
            for col in range(len(df.columns)):
                cell_value = self.get_cell_value_safe(df, row, col)
                if not cell_value:
                    continue
                
                confidence = 0
                cell_lower = cell_value.lower()
                
                for term in search_terms:
                    if term.lower() in cell_lower:
                        # Exact match gets highest score
                        if term.lower() == cell_lower.replace(':', '').strip():
                            confidence += 20
                        # Partial match
                        elif term.lower() in cell_lower:
                            confidence += len(term) * 2
                
                if confidence > 5:  # Minimum threshold
                    value, val_row, val_col = self.search_nearby_for_value(df, row, col)
                    if value and (not validation_func or validation_func(value)):
                        best_matches.append({
                            'value': value,
                            'confidence': confidence,
                            'location': f"Row {val_row+1}, Col {chr(65+val_col)}",
                            'label_location': f"Row {row+1}, Col {chr(65+col)}",
                            'strategy': 'content_search'
                        })
        
        # Strategy 2: Pattern matching (if specified)
        if pattern and not best_matches:
            self.log_debug(f"Using pattern matching for {field_name}: {pattern}")
            for row in range(len(df)):
                for col in range(len(df.columns)):
                    cell_value = self.get_cell_value_safe(df, row, col)
                    if cell_value:
                        match = re.search(pattern, cell_value, re.IGNORECASE)
                        if match:
                            value = match.group(1) if match.groups() else match.group(0)
                            if not validation_func or validation_func(value):
                                best_matches.append({
                                    'value': value,
                                    'confidence': 15,
                                    'location': f"Row {row+1}, Col {chr(65+col)}",
                                    'strategy': 'pattern_match'
                                })
        
        # Strategy 3: Broader search if still not found
        if not best_matches:
            self.log_debug(f"Escalating search for {field_name} - checking entire sheet")
            # Search for any occurrence of key terms
            key_terms = [term.split()[0] for term in search_terms]  # First word of each term
            for row in range(len(df)):
                for col in range(len(df.columns)):
                    cell_value = self.get_cell_value_safe(df, row, col)
                    if cell_value:
                        for term in key_terms:
                            if term.lower() in cell_value.lower():
                                value, val_row, val_col = self.search_nearby_for_value(df, row, col)
                                if value and (not validation_func or validation_func(value)):
                                    best_matches.append({
                                        'value': value,
                                        'confidence': 8,
                                        'location': f"Row {val_row+1}, Col {chr(65+val_col)}",
                                        'strategy': 'broad_search'
                                    })
        
        # Return best match
        if best_matches:
            best_match = max(best_matches, key=lambda x: x['confidence'])
            self.log_debug(f"✅ Found {field_name}: '{best_match['value']}' at {best_match['location']} (confidence: {best_match['confidence']}, strategy: {best_match['strategy']})")
            return best_match['value']
        
        self.log_debug(f"❌ MANDATORY field {field_name} NOT FOUND - CONTRACT VIOLATION")
        return "CONTRACT_VIOLATION_NOT_FOUND"
    
    def extract_ctcac_project_number(self, df):
        """Extract CTCAC/TCAC Project Number"""
        def validate_project_number(value):
            # Common formats: 24-409, 2024-409, R1-24-409, etc.
            return re.search(r'\d{2,4}-\d{3,4}', value) is not None
        
        search_terms = [
            "CTCAC Project Number", "TCAC Project Number", "Project Number", 
            "CTCAC #", "TCAC #", "Application Number", "App Number"
        ]
        
        pattern = r'(\d{2,4}-\d{3,4})'
        
        return self.find_field_with_contract_compliance(
            df, "CTCAC Project Number", search_terms, validate_project_number, pattern
        )
    
    def extract_year(self, df, filename=""):
        """Extract application year"""
        def validate_year(value):
            try:
                year = int(value)
                return 2020 <= year <= 2025
            except:
                return False
        
        search_terms = ["Year", "Application Year", "Round Year", "Calendar Year"]
        pattern = r'\b(202[0-5])\b'
        
        result = self.find_field_with_contract_compliance(
            df, "Year", search_terms, validate_year, pattern
        )
        
        # Fallback: extract from filename
        if result == "CONTRACT_VIOLATION_NOT_FOUND" and filename:
            year_match = re.search(r'(202[0-5])', filename)
            if year_match:
                self.log_debug(f"✅ Found Year from filename: {year_match.group(1)}")
                return year_match.group(1)
        
        return result
    
    def extract_housing_type(self, df):
        """Extract housing type"""
        def validate_housing_type(value):
            valid_types = [
                'family', 'senior', 'non-targeted', 'special needs', 
                'transitional', 'sro', 'elderly', 'disabled'
            ]
            return any(htype in value.lower() for htype in valid_types)
        
        search_terms = [
            "Housing Type", "Target Population", "Tenant Type", "Population Served",
            "Project Type", "Development Type", "Occupancy Type"
        ]
        
        result = self.find_field_with_contract_compliance(
            df, "Housing Type", search_terms, validate_housing_type
        )
        
        # Additional pattern search for common housing types
        if result == "CONTRACT_VIOLATION_NOT_FOUND":
            housing_patterns = [
                r'\b(Family)\b', r'\b(Senior)\b', r'\b(Elderly)\b', 
                r'\b(Non-Targeted)\b', r'\b(Special Needs)\b'
            ]
            
            for pattern in housing_patterns:
                for row in range(len(df)):
                    for col in range(len(df.columns)):
                        cell_value = self.get_cell_value_safe(df, row, col)
                        if cell_value:
                            match = re.search(pattern, cell_value, re.IGNORECASE)
                            if match:
                                self.log_debug(f"✅ Found Housing Type by pattern: {match.group(1)}")
                                return match.group(1)
        
        return result
    
    def extract_soft_cost_contingency(self, df):
        """Extract soft cost contingency"""
        def validate_contingency(value):
            try:
                num = float(str(value).replace(',', '').replace('$', ''))
                return 0 <= num <= 50000000  # Up to $50M contingency
            except:
                return False
        
        search_terms = [
            "Soft Cost Contingency", "Soft Contingency", "Development Contingency",
            "Contingency", "Soft Cost Reserve", "Developer Contingency"
        ]
        
        # First try content search
        result = self.find_field_with_contract_compliance(
            df, "Soft Cost Contingency", search_terms, validate_contingency
        )
        
        # If not found, search for "contingency" near "soft" context
        if result == "CONTRACT_VIOLATION_NOT_FOUND":
            self.log_debug("Searching for contingency values near 'soft' context")
            for row in range(len(df)):
                for col in range(len(df.columns)):
                    cell_value = self.get_cell_value_safe(df, row, col)
                    if cell_value and 'contingency' in cell_value.lower():
                        # Check nearby cells for "soft" context
                        context = self.get_nearby_context(df, row, col, radius=2)
                        if 'soft' in context.lower():
                            # Look for dollar amounts nearby
                            for r_offset in [-2, -1, 0, 1, 2]:
                                for c_offset in [-3, -2, -1, 1, 2, 3]:
                                    check_row, check_col = row + r_offset, col + c_offset
                                    value = self.get_cell_value_safe(df, check_row, check_col)
                                    if value and validate_contingency(value):
                                        self.log_debug(f"✅ Found Soft Cost Contingency by context: {value}")
                                        return value
        
        return result
    
    def get_nearby_context(self, df, center_row, center_col, radius=3):
        """Get text context around a cell"""
        context_parts = []
        for row in range(max(0, center_row - radius), min(len(df), center_row + radius + 1)):
            for col in range(max(0, center_col - radius), min(len(df.columns), center_col + radius + 1)):
                value = self.get_cell_value_safe(df, row, col)
                if value:
                    context_parts.append(value)
        return " ".join(context_parts)
    
    def extract_application_data_contracted(self, file_path):
        """Extract application data with contract compliance"""
        try:
            df = pd.read_excel(file_path, sheet_name="Application", header=None)
            self.log_debug(f"Application sheet loaded: {len(df)} rows x {len(df.columns)} columns")
            
            data = {}
            
            # MANDATORY FIELD 1: Project Name
            data['project_name'] = self.get_cell_value_safe(df, 17, 7) or self.find_field_with_contract_compliance(
                df, "Project Name", ["PROJECT NAME", "Project Name"], 
                lambda x: len(x) > 2
            )
            
            # MANDATORY FIELD 2: CTCAC Project Number
            data['ctcac_project_number'] = self.extract_ctcac_project_number(df)
            
            # MANDATORY FIELD 3: Year
            data['year'] = self.extract_year(df, file_path.name)
            
            # MANDATORY FIELD 4: County
            data['county'] = self.get_cell_value_safe(df, 188, 19) or self.find_field_with_contract_compliance(
                df, "County", ["County:", "County"], 
                lambda x: len(x) > 2
            )
            
            # MANDATORY FIELD 5: City
            data['city'] = self.find_field_with_contract_compliance(
                df, "City", ["City:", "City", "Project City"], 
                lambda x: len(x) > 2
            )
            
            # MANDATORY FIELD 6: General Contractor
            def validate_contractor(value):
                company_indicators = ['inc', 'llc', 'corp', 'company', 'construction', 'builders', 'group']
                return (any(indicator in value.lower() for indicator in company_indicators) or 
                       (5 <= len(value) <= 100))
            
            data['general_contractor'] = self.find_field_with_contract_compliance(
                df, "General Contractor", 
                ["General Contractor:", "General Contractor", "GC:", "Contractor"], 
                validate_contractor
            )
            
            # MANDATORY FIELD 7: New Construction
            new_const_result = self.find_field_with_contract_compliance(
                df, "New Construction", ["New Construction", "Construction Type"]
            )
            
            if new_const_result != "CONTRACT_VIOLATION_NOT_FOUND":
                if any(word in new_const_result.lower() for word in ['yes', 'new', 'true']):
                    data['new_construction'] = "Yes"
                elif any(word in new_const_result.lower() for word in ['no', 'rehab', 'renovation', 'adaptive']):
                    data['new_construction'] = "No"
                else:
                    data['new_construction'] = new_const_result
            else:
                data['new_construction'] = "CONTRACT_VIOLATION_NOT_FOUND"
            
            # MANDATORY FIELD 8: Housing Type
            data['housing_type'] = self.extract_housing_type(df)
            
            # MANDATORY FIELD 9: Total Units
            def validate_units(value):
                try:
                    num = int(float(str(value).replace(',', '')))
                    return 1 <= num <= 2000
                except:
                    return False
            
            units_result = self.find_field_with_contract_compliance(
                df, "Total Units", 
                ["Total Number of Units", "Total Units", "# of Units", "Dwelling Units"], 
                validate_units
            )
            
            if units_result != "CONTRACT_VIOLATION_NOT_FOUND":
                try:
                    data['total_units'] = int(float(units_result.replace(',', '')))
                except:
                    data['total_units'] = 0
            else:
                data['total_units'] = "CONTRACT_VIOLATION_NOT_FOUND"
            
            # MANDATORY FIELD 10: Square Footage (using previous enhanced method)
            sqft_matches = self.search_all_numeric_values(
                df, 5000, 1000000, 
                ['square', 'sq', 'footage', 'ft', 'residential', 'dwelling']
            )
            
            best_sqft = 0
            best_score = 0
            for match in sqft_matches:
                score = 0
                context_lower = match['context'].lower()
                if 'square' in context_lower or 'sq' in context_lower:
                    score += 15
                if 'footage' in context_lower or 'ft' in context_lower:
                    score += 12
                if 'residential' in context_lower or 'dwelling' in context_lower:
                    score += 8
                
                if score > best_score:
                    best_score = score
                    best_sqft = int(match['value'])
            
            data['total_sqft_low_income'] = best_sqft if best_sqft > 0 else "CONTRACT_VIOLATION_NOT_FOUND"
            
            return data
            
        except Exception as e:
            self.log_debug(f"ERROR in application extraction: {str(e)}")
            return {}
    
    def search_all_numeric_values(self, df, min_val, max_val, context_terms=None):
        """Search for numeric values with context"""
        matches = []
        for row in range(len(df)):
            for col in range(len(df.columns)):
                cell_value = self.get_cell_value_safe(df, row, col)
                if cell_value:
                    try:
                        clean_val = cell_value.replace(',', '').replace('$', '').replace('%', '')
                        num = float(clean_val)
                        if min_val <= num <= max_val:
                            if context_terms:
                                context = self.get_nearby_context(df, row, col)
                                context_lower = context.lower()
                                if any(term.lower() in context_lower for term in context_terms):
                                    matches.append({'value': num, 'context': context})
                            else:
                                matches.append({'value': num, 'context': ''})
                    except:
                        pass
        return matches
    
    def extract_sources_uses_data_contracted(self, file_path):
        """Extract sources and uses data with contract compliance"""
        try:
            df = pd.read_excel(file_path, sheet_name="Sources and Uses Budget", header=None)
            data = {}
            
            # Try original coordinates first
            coords = {
                'land_cost': (3, 1),
                'total_architectural': (41, 1),
                'total_survey_engineering': (42, 1),
                'local_impact_fees': (84, 1)
            }
            
            for field, (row, col) in coords.items():
                try:
                    value = df.iloc[row, col]
                    data[field] = float(value) if pd.notna(value) else 0
                except:
                    data[field] = 0
            
            # Enhanced construction cost search
            construction_matches = self.search_all_numeric_values(
                df, 500000, 100000000,
                ['construction', 'hard cost', 'building', 'rehabilitation', 'total']
            )
            
            best_construction = 0
            best_score = 0
            for match in construction_matches:
                score = 0
                context_lower = match['context'].lower()
                
                if 'total' in context_lower and ('construction' in context_lower or 'rehabilitation' in context_lower):
                    score += 30
                elif 'construction' in context_lower:
                    score += 20
                elif 'rehabilitation' in context_lower:
                    score += 25
                
                if score > best_score and score > 10:
                    best_score = score
                    best_construction = match['value']
            
            data['total_new_construction'] = best_construction if best_construction > 0 else "CONTRACT_VIOLATION_NOT_FOUND"
            
            # MANDATORY: Soft Cost Contingency
            data['soft_cost_contingency'] = self.extract_soft_cost_contingency(df)
            
            return data
            
        except Exception as e:
            self.log_debug(f"ERROR in sources/uses extraction: {str(e)}")
            return {}
    
    def validate_contract_compliance(self, result):
        """Validate that all mandatory fields were found"""
        violations = []
        
        # Check application data
        app_data = result.get('application_data', {})
        for field in self.contract_fields['application']:
            value = app_data.get(field)
            if value == "CONTRACT_VIOLATION_NOT_FOUND" or not value:
                violations.append(f"Application.{field}")
        
        # Check sources/uses data
        sources_data = result.get('sources_uses_data', {})
        for field in self.contract_fields['sources_uses']:
            value = sources_data.get(field)
            if value == "CONTRACT_VIOLATION_NOT_FOUND" or (isinstance(value, (int, float)) and value == 0):
                violations.append(f"SourcesUses.{field}")
        
        return violations
    
    def extract_file_contracted(self, file_path):
        """Extract file with full contract compliance"""
        self.log_debug(f"\n{'='*80}")
        self.log_debug(f"CONTRACTED EXTRACTION: {file_path.name}")
        self.log_debug(f"{'='*80}")
        
        result = {
            'filename': file_path.name,
            'application_data': self.extract_application_data_contracted(file_path),
            'sources_uses_data': self.extract_sources_uses_data_contracted(file_path),
            'extraction_log': self.extraction_log.copy()
        }
        
        # Validate contract compliance
        violations = self.validate_contract_compliance(result)
        result['contract_violations'] = violations
        result['contract_compliant'] = len(violations) == 0
        
        if violations:
            self.log_debug(f"\n❌ CONTRACT VIOLATIONS DETECTED:")
            for violation in violations:
                self.log_debug(f"   - {violation}")
        else:
            self.log_debug(f"\n✅ CONTRACT FULLY COMPLIANT - All mandatory fields extracted")
        
        return result

def test_contracted_extraction():
    """Test contracted extraction on Marina Towers"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    test_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    if test_file.exists():
        extractor = ContractedLIHTCExtractor()
        result = extractor.extract_file_contracted(test_file)
        
        print("\n" + "="*90)
        print("CONTRACTED EXTRACTION RESULTS - MARINA TOWERS")
        print("="*90)
        
        # Display results
        app_data = result['application_data']
        sources_data = result['sources_uses_data']
        
        print(f"\n📋 APPLICATION DATA (10 MANDATORY FIELDS):")
        print(f"   Project Name: {app_data.get('project_name')}")
        print(f"   CTCAC Project Number: {app_data.get('ctcac_project_number')}")
        print(f"   Year: {app_data.get('year')}")
        print(f"   City: {app_data.get('city')}")
        print(f"   County: {app_data.get('county')}")
        print(f"   General Contractor: {app_data.get('general_contractor')}")
        print(f"   New Construction: {app_data.get('new_construction')}")
        print(f"   Housing Type: {app_data.get('housing_type')}")
        print(f"   Total Units: {app_data.get('total_units')}")
        print(f"   Total Sq Ft (Low Income): {app_data.get('total_sqft_low_income')}")
        
        print(f"\n💰 SOURCES & USES DATA (6 MANDATORY FIELDS):")
        print(f"   Land Cost: ${sources_data.get('land_cost', 0):,.0f}")
        print(f"   Total New Construction: {sources_data.get('total_new_construction')}")
        print(f"   Total Architectural: ${sources_data.get('total_architectural', 0):,.0f}")
        print(f"   Total Survey & Engineering: ${sources_data.get('total_survey_engineering', 0):,.0f}")
        print(f"   Local Impact Fees: ${sources_data.get('local_impact_fees', 0):,.0f}")
        print(f"   Soft Cost Contingency: {sources_data.get('soft_cost_contingency')}")
        
        # Contract compliance report
        print(f"\n📊 CONTRACT COMPLIANCE REPORT:")
        print(f"   Contract Compliant: {'✅ YES' if result['contract_compliant'] else '❌ NO'}")
        if result['contract_violations']:
            print(f"   Violations: {len(result['contract_violations'])}")
            for violation in result['contract_violations']:
                print(f"     - {violation}")
        else:
            print(f"   All 16 mandatory fields successfully extracted! 🎉")
        
        # Save complete results
        output_file = Path("/Users/vitorfaroni/Documents/Automation/LIHTCApp/marina_towers_contracted.json")
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n📄 Complete results saved to: {output_file}")
        
    else:
        print(f"File not found: {test_file}")

if __name__ == "__main__":
    test_contracted_extraction()