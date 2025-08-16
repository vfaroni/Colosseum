#!/usr/bin/env python3
"""
Corrected LIHTC 4% Application Data Extractor
Fixes specific issues identified in Marina Towers
"""

import pandas as pd
import json
import re
from pathlib import Path

class CorrectedLIHTCExtractor:
    def __init__(self):
        self.debug_mode = True
        
    def log_debug(self, message):
        if self.debug_mode:
            print(f"DEBUG: {message}")
    
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
        """Search in all directions from a label"""
        search_patterns = [
            [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8)],  # Right
            [(1, 0), (2, 0), (3, 0), (4, 0)],  # Down
            [(1, 1), (1, 2), (2, 1), (2, 2)],  # Diagonal
            [(0, -1), (0, -2)],  # Left
            [(-1, 0), (-2, 0)]  # Up
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
        """Check if a value looks like actual data"""
        if not value or len(value.strip()) < 1:
            return False
        
        label_indicators = [':', 'instructions', 'note', 'see', 'refer', 'section', 'part']
        if any(indicator in value.lower() for indicator in label_indicators):
            return False
            
        return True
    
    def extract_ctcac_project_number_corrected(self, filename):
        """Extract CTCAC Project Number from filename - CORRECTED"""
        self.log_debug(f"Extracting CTCAC Project Number from filename: {filename}")
        
        # Pattern: 2 digits, dash, 3 digits (e.g., 24-409)
        pattern = r'(\d{2}-\d{3})'
        match = re.search(pattern, filename)
        
        if match:
            project_number = match.group(1)
            self.log_debug(f"✅ Found CTCAC Project Number: {project_number}")
            return project_number
        else:
            self.log_debug(f"❌ Could not extract project number from filename")
            return "Not found"
    
    def extract_total_residential_sqft_corrected(self, df):
        """Extract Total Residential Square Footage - CORRECTED"""
        self.log_debug("Searching for Total Residential Square Footage")
        
        # Search for the specific phrase "Total square footage of all residential units"
        search_terms = [
            "Total square footage of all residential units",
            "Total residential square footage",
            "Total Residential Square Footage",
            "residential square footage",
            "residential sq ft"
        ]
        
        best_match = None
        best_confidence = 0
        
        for row in range(len(df)):
            for col in range(len(df.columns)):
                cell_value = self.get_cell_value_safe(df, row, col)
                if not cell_value:
                    continue
                
                cell_lower = cell_value.lower()
                
                # Check for exact or partial matches
                for term in search_terms:
                    if term.lower() in cell_lower:
                        confidence = len(term) if term.lower() in cell_lower else 0
                        
                        # Special bonus for exact phrase
                        if "total square footage of all residential units" in cell_lower:
                            confidence += 50
                        elif "residential" in cell_lower and "square footage" in cell_lower:
                            confidence += 30
                        
                        if confidence > best_confidence:
                            # Look for numeric value nearby
                            value, val_row, val_col = self.search_nearby_for_value(df, row, col)
                            if value:
                                try:
                                    # Try to convert to number
                                    num_value = float(value.replace(',', ''))
                                    if 50000 <= num_value <= 500000:  # Reasonable range for residential sqft
                                        best_match = {
                                            'value': int(num_value),
                                            'confidence': confidence,
                                            'location': f"Row {val_row+1}, Col {chr(65+val_col)}",
                                            'label': cell_value
                                        }
                                        best_confidence = confidence
                                        self.log_debug(f"Found residential sqft candidate: {num_value:,.0f} (confidence: {confidence})")
                                except:
                                    pass
        
        if best_match:
            self.log_debug(f"✅ Found Total Residential Square Footage: {best_match['value']:,} at {best_match['location']}")
            return best_match['value']
        else:
            self.log_debug(f"❌ Could not find Total Residential Square Footage")
            return 0
    
    def extract_new_construction_corrected(self, df):
        """Extract New Construction from Type of Credit Requested section - CORRECTED"""
        self.log_debug("Searching for New Construction in Type of Credit Requested section")
        
        # First find the "Type of Credit Requested" section
        credit_section_row = None
        for row in range(len(df)):
            for col in range(len(df.columns)):
                cell_value = self.get_cell_value_safe(df, row, col)
                if cell_value and "type of credit requested" in cell_value.lower():
                    credit_section_row = row
                    self.log_debug(f"Found 'Type of Credit Requested' section at row {row+1}")
                    break
            if credit_section_row:
                break
        
        if not credit_section_row:
            self.log_debug("Could not find 'Type of Credit Requested' section")
            return "Not found"
        
        # Search within 20 rows of the section header
        search_start = credit_section_row
        search_end = min(len(df), credit_section_row + 20)
        
        self.log_debug(f"Searching for New Construction indicators in rows {search_start+1} to {search_end}")
        
        for row in range(search_start, search_end):
            for col in range(len(df.columns)):
                cell_value = self.get_cell_value_safe(df, row, col)
                if cell_value:
                    cell_lower = cell_value.lower()
                    
                    # Look for New Construction indicators
                    if "new construction" in cell_lower:
                        self.log_debug(f"Found 'new construction' at Row {row+1}, Col {chr(65+col)}: {cell_value}")
                        
                        # Check nearby cells for checkboxes or indicators
                        for r_offset in [-1, 0, 1]:
                            for c_offset in [-3, -2, -1, 1, 2, 3]:
                                check_row, check_col = row + r_offset, col + c_offset
                                check_value = self.get_cell_value_safe(df, check_row, check_col)
                                if check_value:
                                    check_lower = check_value.lower()
                                    
                                    # Look for indicators
                                    if any(indicator in check_lower for indicator in ['x', '✓', 'yes', 'selected']):
                                        self.log_debug(f"✅ Found New Construction = YES (indicator: {check_value})")
                                        return "Yes"
                                    elif check_lower in ['n/a', 'na', 'not applicable']:
                                        self.log_debug(f"✅ Found New Construction = N/A")
                                        return "N/A"
                    
                    # Also check for rehabilitation/acquisition+rehab
                    elif any(term in cell_lower for term in ['rehabilitation', 'acquisition', 'rehab']):
                        # Check for checkboxes nearby
                        for r_offset in [-1, 0, 1]:
                            for c_offset in [-3, -2, -1, 1, 2, 3]:
                                check_row, check_col = row + r_offset, col + c_offset
                                check_value = self.get_cell_value_safe(df, check_row, check_col)
                                if check_value and any(indicator in check_value.lower() for indicator in ['x', '✓', 'yes']):
                                    self.log_debug(f"✅ Found Rehabilitation/Acquisition selected = NO (for new construction)")
                                    return "No"
        
        self.log_debug(f"❌ Could not determine New Construction status in Type of Credit section")
        return "Not specified"
    
    def extract_total_new_construction_cost_corrected(self, df):
        """Extract Total New Construction Cost - CORRECTED"""
        self.log_debug("Searching for Total New Construction Cost")
        
        # Search for various construction cost labels
        search_terms = [
            "Total New Construction Cost",
            "New Construction Cost", 
            "Construction Cost",
            "Hard Costs - New Construction",
            "Hard Construction Costs",
            "Total Construction"
        ]
        
        matches = []
        
        for row in range(len(df)):
            for col in range(len(df.columns)):
                cell_value = self.get_cell_value_safe(df, row, col)
                if not cell_value:
                    continue
                
                cell_lower = cell_value.lower()
                
                for term in search_terms:
                    if term.lower() in cell_lower:
                        self.log_debug(f"Found construction cost label at Row {row+1}, Col {chr(65+col)}: {cell_value}")
                        
                        # Look for dollar amounts nearby
                        for r_offset in [-2, -1, 0, 1, 2]:
                            for c_offset in [-3, -2, -1, 1, 2, 3, 4, 5]:
                                check_row, check_col = row + r_offset, col + c_offset
                                check_value = self.get_cell_value_safe(df, check_row, check_col)
                                if check_value:
                                    try:
                                        # Clean and convert to number
                                        clean_val = check_value.replace(',', '').replace('$', '').replace('(', '').replace(')', '')
                                        num_value = float(clean_val)
                                        
                                        # Construction costs should be substantial (>$100K, <$100M)
                                        if 100000 <= num_value <= 100000000:
                                            confidence = len(term)
                                            
                                            # Higher confidence for "total" and "new construction"
                                            if "total" in term.lower():
                                                confidence += 20
                                            if "new construction" in term.lower():
                                                confidence += 30
                                            
                                            matches.append({
                                                'value': num_value,
                                                'confidence': confidence,
                                                'location': f"Row {check_row+1}, Col {chr(65+check_col)}",
                                                'label': cell_value,
                                                'context': f"{cell_value} -> {check_value}"
                                            })
                                            
                                            self.log_debug(f"Found construction cost: ${num_value:,.0f} (confidence: {confidence})")
                                    except:
                                        pass
        
        if matches:
            # Sort by confidence and return best match
            best_match = max(matches, key=lambda x: x['confidence'])
            self.log_debug(f"✅ Best Total New Construction Cost: ${best_match['value']:,.0f} at {best_match['location']}")
            return best_match['value']
        else:
            self.log_debug(f"❌ Could not find Total New Construction Cost")
            return 0
    
    def extract_application_data_corrected(self, file_path):
        """Extract application data with corrections"""
        try:
            df = pd.read_excel(file_path, sheet_name="Application", header=None)
            data = {}
            
            # Use previous working extractions for fields that were correct
            data['project_name'] = self.get_cell_value_safe(df, 17, 7) or "Not found"
            data['county'] = self.get_cell_value_safe(df, 188, 19) or "Not found"
            
            # Simple search for working fields
            def find_simple_field(search_terms, validation_func=None):
                for row in range(len(df)):
                    for col in range(len(df.columns)):
                        cell_value = self.get_cell_value_safe(df, row, col)
                        if cell_value:
                            for term in search_terms:
                                if term.lower() in cell_value.lower():
                                    value, _, _ = self.search_nearby_for_value(df, row, col)
                                    if value and (not validation_func or validation_func(value)):
                                        return value
                return "Not found"
            
            data['city'] = find_simple_field(["City:", "City"])
            data['general_contractor'] = find_simple_field(["General Contractor", "GC:"])
            data['housing_type'] = find_simple_field(["Housing Type", "Population Served"])
            
            # Units extraction
            units_result = find_simple_field(["Total Number of Units", "Total Units"], 
                                           lambda x: x.isdigit() and 1 <= int(x) <= 2000)
            data['total_units'] = int(units_result) if units_result.isdigit() else 0
            
            data['year'] = find_simple_field(["Year", "Application Year"])
            
            # CORRECTED EXTRACTIONS
            data['ctcac_project_number'] = self.extract_ctcac_project_number_corrected(file_path.name)
            data['total_sqft_low_income'] = self.extract_total_residential_sqft_corrected(df)
            data['new_construction'] = self.extract_new_construction_corrected(df)
            
            return data
            
        except Exception as e:
            self.log_debug(f"Error in application extraction: {str(e)}")
            return {}
    
    def extract_sources_uses_data_corrected(self, file_path):
        """Extract sources and uses data with corrections"""
        try:
            df = pd.read_excel(file_path, sheet_name="Sources and Uses Budget", header=None)
            data = {}
            
            # Use working coordinate extractions
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
            
            # CORRECTED: Total New Construction Cost
            data['total_new_construction'] = self.extract_total_new_construction_cost_corrected(df)
            
            # Soft Cost Contingency (this was working)
            def find_contingency():
                for row in range(len(df)):
                    for col in range(len(df.columns)):
                        cell_value = self.get_cell_value_safe(df, row, col)
                        if cell_value and 'contingency' in cell_value.lower() and 'soft' in cell_value.lower():
                            for r_offset in [-1, 0, 1]:
                                for c_offset in [-2, -1, 1, 2, 3]:
                                    check_value = self.get_cell_value_safe(df, row + r_offset, col + c_offset)
                                    if check_value:
                                        try:
                                            return float(check_value.replace(',', '').replace('$', ''))
                                        except:
                                            pass
                return 0
            
            data['soft_cost_contingency'] = find_contingency()
            
            return data
            
        except Exception as e:
            self.log_debug(f"Error in sources/uses extraction: {str(e)}")
            return {}
    
    def extract_file_corrected(self, file_path):
        """Extract file with corrections applied"""
        self.log_debug(f"\n{'='*80}")
        self.log_debug(f"CORRECTED EXTRACTION: {file_path.name}")
        self.log_debug(f"{'='*80}")
        
        result = {
            'filename': file_path.name,
            'application_data': self.extract_application_data_corrected(file_path),
            'sources_uses_data': self.extract_sources_uses_data_corrected(file_path)
        }
        
        return result

def test_corrected_extraction():
    """Test corrected extraction on Marina Towers"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    test_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    if test_file.exists():
        extractor = CorrectedLIHTCExtractor()
        result = extractor.extract_file_corrected(test_file)
        
        print("\n" + "="*90)
        print("🔧 CORRECTED EXTRACTION RESULTS - MARINA TOWERS")
        print("="*90)
        
        app_data = result['application_data']
        sources_data = result['sources_uses_data']
        
        print(f"\n📋 APPLICATION DATA - CORRECTED FIELDS:")
        
        # Highlight the corrected fields
        corrections = {
            'ctcac_project_number': '(CORRECTED - from filename)',
            'total_sqft_low_income': '(CORRECTED - residential sqft)',
            'new_construction': '(CORRECTED - from credit type section)'
        }
        
        fields = [
            ('Project Name', app_data.get('project_name')),
            ('CTCAC Project Number', app_data.get('ctcac_project_number')),
            ('Year', app_data.get('year')),
            ('City', app_data.get('city')),
            ('County', app_data.get('county')),
            ('General Contractor', app_data.get('general_contractor')),
            ('New Construction', app_data.get('new_construction')),
            ('Housing Type', app_data.get('housing_type')),
            ('Total Units', app_data.get('total_units')),
            ('Total Residential Sq Ft', app_data.get('total_sqft_low_income'))
        ]
        
        for field, value in fields:
            key = field.lower().replace(' ', '_').replace('residential_', '').replace('total_', 'total_sqft_low_income' if 'sq ft' in field.lower() else 'total_units')
            correction_note = corrections.get(key, '')
            print(f"   {field}: {value} {correction_note}")
        
        print(f"\n💰 SOURCES & USES DATA - CORRECTED FIELDS:")
        print(f"   Land Cost: ${sources_data.get('land_cost', 0):,.0f}")
        print(f"   Total New Construction: ${sources_data.get('total_new_construction'):,.0f} (CORRECTED)")
        print(f"   Total Architectural: ${sources_data.get('total_architectural', 0):,.0f}")
        print(f"   Total Survey & Engineering: ${sources_data.get('total_survey_engineering', 0):,.0f}")
        print(f"   Local Impact Fees: ${sources_data.get('local_impact_fees', 0):,.0f}")
        print(f"   Soft Cost Contingency: ${sources_data.get('soft_cost_contingency', 0):,.0f}")
        
        # Save results
        output_file = Path("/Users/vitorfaroni/Documents/Automation/LIHTCApp/marina_towers_corrected.json")
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\n📄 Corrected results saved to: {output_file}")
        
    else:
        print(f"File not found: {test_file}")

if __name__ == "__main__":
    test_corrected_extraction()