#!/usr/bin/env python3
"""
Enhanced LIHTC 4% Application Data Extractor
Uses multiple strategies to handle merged cells and inconsistent positioning
"""

import pandas as pd
import json
import re
from pathlib import Path
import logging
from openpyxl import load_workbook
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EnhancedLIHTCExtractor:
    def __init__(self):
        self.debug_mode = True
        
    def log_debug(self, message):
        """Debug logging"""
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
    
    def search_nearby_for_value(self, df, label_row, label_col, max_distance=8):
        """Search in all directions from a label for the actual value"""
        search_patterns = [
            # Right (most common)
            [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8)],
            # Down
            [(1, 0), (2, 0), (3, 0), (4, 0)],
            # Diagonal down-right
            [(1, 1), (1, 2), (2, 1), (2, 2)],
            # Left (less common)
            [(0, -1), (0, -2)],
            # Up
            [(-1, 0), (-2, 0)]
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
        """Check if a value looks like actual data rather than a label"""
        if not value or len(value.strip()) < 2:
            return False
        
        # Skip values that are clearly labels
        label_indicators = [':', 'instructions', 'note', 'see', 'refer', 'contact', 'phone', 'email']
        if any(indicator in value.lower() for indicator in label_indicators):
            return False
        
        # Skip values that are mostly punctuation or formatting
        if len(re.sub(r'[^a-zA-Z0-9\s]', '', value)) < len(value) * 0.5:
            return False
            
        return True
    
    def find_field_by_content_search(self, df, search_terms, validation_func=None):
        """Search for a field by content and return its value"""
        best_match = None
        best_confidence = 0
        
        for row in range(len(df)):
            for col in range(len(df.columns)):
                cell_value = self.get_cell_value_safe(df, row, col)
                if not cell_value:
                    continue
                
                # Calculate match confidence
                confidence = 0
                cell_lower = cell_value.lower()
                
                for term in search_terms:
                    if term.lower() in cell_lower:
                        # Exact match gets higher score
                        if term.lower() == cell_lower.replace(':', '').strip():
                            confidence += 10
                        else:
                            confidence += len(term)
                
                if confidence > best_confidence:
                    # Found a good label, now look for the value
                    value, val_row, val_col = self.search_nearby_for_value(df, row, col)
                    if value and (not validation_func or validation_func(value)):
                        best_match = {
                            'value': value,
                            'label_location': f"Row {row+1}, Col {chr(65+col)}",
                            'value_location': f"Row {val_row+1}, Col {chr(65+val_col)}",
                            'confidence': confidence
                        }
                        best_confidence = confidence
                        self.log_debug(f"Found {search_terms[0]}: '{value}' at {best_match['value_location']}")
        
        return best_match['value'] if best_match else None
    
    def extract_city_enhanced(self, df):
        """Enhanced city extraction"""
        search_terms = ["City:", "City", "Project City", "Location City"]
        
        def validate_city(value):
            # Cities should be reasonable length and contain letters
            return 2 <= len(value) <= 50 and any(c.isalpha() for c in value)
        
        city = self.find_field_by_content_search(df, search_terms, validate_city)
        
        # Fallback: look for common California city patterns
        if not city:
            self.log_debug("City not found with labels, trying pattern matching...")
            ca_cities_pattern = r'\b(San Francisco|Los Angeles|Sacramento|San Diego|Oakland|Vallejo|Berkeley|Richmond|Concord|Fremont|Hayward|Santa Rosa|Stockton|Modesto|Fresno|Bakersfield)\b'
            
            # Search entire sheet
            for row in range(len(df)):
                for col in range(len(df.columns)):
                    cell_value = self.get_cell_value_safe(df, row, col)
                    if cell_value:
                        match = re.search(ca_cities_pattern, cell_value, re.IGNORECASE)
                        if match:
                            city = match.group(1)
                            self.log_debug(f"Found city by pattern: {city}")
                            break
                if city:
                    break
        
        return city or "Not found"
    
    def extract_general_contractor_enhanced(self, df):
        """Enhanced general contractor extraction"""
        search_terms = [
            "General Contractor:", "General Contractor", "GC:", "GC", 
            "Contractor:", "Contractor", "Construction Company", "Builder"
        ]
        
        def validate_contractor(value):
            # Contractors usually have company indicators or are proper names
            company_indicators = ['inc', 'llc', 'corp', 'company', 'construction', 'builders', 'group']
            value_lower = value.lower()
            
            # Check for company indicators
            if any(indicator in value_lower for indicator in company_indicators):
                return True
            
            # Check if it looks like a proper company name (has capitals, reasonable length)
            if 5 <= len(value) <= 100 and any(c.isupper() for c in value):
                return True
                
            return False
        
        contractor = self.find_field_by_content_search(df, search_terms, validate_contractor)
        
        # Alternative approach: look for company name patterns
        if not contractor:
            self.log_debug("Contractor not found with labels, trying company pattern matching...")
            company_pattern = r'\b([A-Z][a-zA-Z\s&,.-]+(?:Inc\.?|LLC|Corp\.?|Company|Construction|Builders|Group))\b'
            
            for row in range(250, min(350, len(df))):  # Focus on likely contractor section
                for col in range(len(df.columns)):
                    cell_value = self.get_cell_value_safe(df, row, col)
                    if cell_value:
                        match = re.search(company_pattern, cell_value)
                        if match and len(match.group(1)) > 10:  # Reasonable company name length
                            contractor = match.group(1)
                            self.log_debug(f"Found contractor by pattern: {contractor}")
                            break
                if contractor:
                    break
        
        return contractor or "Not found"
    
    def extract_units_enhanced(self, df):
        """Enhanced unit count extraction"""
        search_terms = [
            "Total Number of Units", "Total Units", "# of Units", "Unit Count",
            "Total Dwelling Units", "Dwelling Units", "Residential Units", "Units:"
        ]
        
        def validate_units(value):
            try:
                num = int(float(str(value).replace(',', '')))
                return 1 <= num <= 2000  # Reasonable range for housing units
            except:
                return False
        
        units_str = self.find_field_by_content_search(df, search_terms, validate_units)
        
        if units_str:
            try:
                return int(float(units_str.replace(',', '')))
            except:
                pass
        
        # Fallback: scan for numbers in reasonable range near "unit" text
        self.log_debug("Units not found with labels, scanning for numbers near 'unit' text...")
        for row in range(len(df)):
            for col in range(len(df.columns)):
                cell_value = self.get_cell_value_safe(df, row, col)
                if cell_value and 'unit' in cell_value.lower():
                    # Look for numbers nearby
                    for r_offset in [-2, -1, 0, 1, 2]:
                        for c_offset in [-3, -2, -1, 1, 2, 3, 4, 5]:
                            check_value = self.get_cell_value_safe(df, row + r_offset, col + c_offset)
                            if check_value:
                                try:
                                    num = int(float(check_value.replace(',', '')))
                                    if 10 <= num <= 500:  # Reasonable unit range
                                        self.log_debug(f"Found units by proximity search: {num}")
                                        return num
                                except:
                                    pass
        
        return 0
    
    def extract_square_footage_enhanced(self, df):
        """Enhanced square footage extraction"""
        search_terms = [
            "Total Square Footage", "Square Footage", "Sq Ft", "Sq. Ft.",
            "Total Sq Ft", "Low Income Units Sq Ft", "Residential Sq Ft"
        ]
        
        def validate_sqft(value):
            try:
                num = int(float(str(value).replace(',', '')))
                return 1000 <= num <= 10000000  # Reasonable range for building square footage
            except:
                return False
        
        sqft_str = self.find_field_by_content_search(df, search_terms, validate_sqft)
        
        if sqft_str:
            try:
                return int(float(sqft_str.replace(',', '')))
            except:
                pass
        
        # Alternative: look for large numbers near "sq" or "square" text
        self.log_debug("Square footage not found with labels, scanning for numbers near 'sq' text...")
        for row in range(len(df)):
            for col in range(len(df.columns)):
                cell_value = self.get_cell_value_safe(df, row, col)
                if cell_value and ('sq' in cell_value.lower() or 'square' in cell_value.lower()):
                    # Look for numbers nearby
                    for r_offset in [-1, 0, 1]:
                        for c_offset in [-2, -1, 1, 2, 3]:
                            check_value = self.get_cell_value_safe(df, row + r_offset, col + c_offset)
                            if check_value:
                                try:
                                    num = int(float(check_value.replace(',', '')))
                                    if 5000 <= num <= 1000000:  # Reasonable sqft range
                                        self.log_debug(f"Found sqft by proximity search: {num}")
                                        return num
                                except:
                                    pass
        
        return 0
    
    def extract_new_construction_enhanced(self, df):
        """Enhanced new construction detection"""
        search_terms = ["New Construction", "New Const", "Type of Construction", "Construction Type"]
        
        # First try content search
        result = self.find_field_by_content_search(df, search_terms)
        if result:
            if any(word in result.lower() for word in ['yes', 'new', 'true', 'x']):
                return "Yes"
            elif any(word in result.lower() for word in ['no', 'rehab', 'renovation', 'false']):
                return "No"
        
        # Look for checkbox patterns or yes/no near construction terms
        for row in range(len(df)):
            for col in range(len(df.columns)):
                cell_value = self.get_cell_value_safe(df, row, col)
                if cell_value and 'construction' in cell_value.lower():
                    # Check nearby cells for yes/no/checkbox indicators
                    for r_offset in [-1, 0, 1]:
                        for c_offset in [-2, -1, 1, 2]:
                            check_value = self.get_cell_value_safe(df, row + r_offset, col + c_offset)
                            if check_value:
                                check_lower = check_value.lower()
                                if any(indicator in check_lower for indicator in ['yes', 'x', '✓', 'new']):
                                    return "Yes"
                                elif any(indicator in check_lower for indicator in ['no', 'rehab', 'renovation']):
                                    return "No"
        
        return "Not specified"
    
    def extract_application_data_enhanced(self, file_path):
        """Enhanced application data extraction"""
        try:
            df = pd.read_excel(file_path, sheet_name="Application", header=None)
            self.log_debug(f"Application sheet size: {len(df)} rows x {len(df.columns)} columns")
            
            data = {}
            
            # Project Name - try coordinates first, then search
            data['project_name'] = self.get_cell_value_safe(df, 17, 7) or "Not found"
            if data['project_name'] == "Not found":
                data['project_name'] = self.find_field_by_content_search(df, ["PROJECT NAME", "Project Name"]) or "Not found"
            
            # County - try coordinates first, then search
            data['county'] = self.get_cell_value_safe(df, 188, 19) or "Not found"
            if data['county'] == "Not found":
                data['county'] = self.find_field_by_content_search(df, ["County:", "County"]) or "Not found"
            
            # Enhanced extractions
            data['city'] = self.extract_city_enhanced(df)
            data['general_contractor'] = self.extract_general_contractor_enhanced(df)
            data['new_construction'] = self.extract_new_construction_enhanced(df)
            data['total_units'] = self.extract_units_enhanced(df)
            data['total_sqft_low_income'] = self.extract_square_footage_enhanced(df)
            
            return data
            
        except Exception as e:
            logging.error(f"Error in enhanced application extraction: {str(e)}")
            return {}
    
    def extract_sources_uses_data_enhanced(self, file_path):
        """Enhanced sources and uses extraction"""
        try:
            df = pd.read_excel(file_path, sheet_name="Sources and Uses Budget", header=None)
            
            data = {}
            
            # Try original coordinates first
            coords = {
                'land_cost': (3, 1),
                'total_new_construction': (37, 1),
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
            
            # For zero values, try content search
            search_mapping = {
                'land_cost': ["Land Cost", "Land Value", "Site Acquisition"],
                'total_new_construction': ["New Construction", "Construction Costs", "Hard Costs"],
                'total_architectural': ["Architectural", "Architect Fees", "Design Fees"],
                'total_survey_engineering': ["Survey", "Engineering", "Survey & Engineering"],
                'local_impact_fees': ["Impact Fees", "Development Fees", "Local Fees"]
            }
            
            for field, search_terms in search_mapping.items():
                if data[field] == 0:
                    def validate_cost(value):
                        try:
                            num = float(str(value).replace(',', '').replace('$', ''))
                            return 0 <= num <= 100000000  # Reasonable cost range
                        except:
                            return False
                    
                    cost_str = self.find_field_by_content_search(df, search_terms, validate_cost)
                    if cost_str:
                        try:
                            data[field] = float(cost_str.replace(',', '').replace('$', ''))
                            self.log_debug(f"Found {field} by search: ${data[field]:,.0f}")
                        except:
                            pass
            
            return data
            
        except Exception as e:
            logging.error(f"Error in enhanced sources/uses extraction: {str(e)}")
            return {}
    
    def extract_file_enhanced(self, file_path):
        """Enhanced file extraction using multiple strategies"""
        self.log_debug(f"\n=== Enhanced Extraction: {file_path.name} ===")
        
        result = {
            'filename': file_path.name,
            'application_data': self.extract_application_data_enhanced(file_path),
            'sources_uses_data': self.extract_sources_uses_data_enhanced(file_path)
        }
        
        return result

def test_enhanced_extraction():
    """Test the enhanced extractor on Marina Towers"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    test_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    if test_file.exists():
        extractor = EnhancedLIHTCExtractor()
        result = extractor.extract_file_enhanced(test_file)
        
        print("\n" + "="*60)
        print("ENHANCED EXTRACTION RESULTS - MARINA TOWERS")
        print("="*60)
        print(json.dumps(result, indent=2))
        
        # Save results
        output_file = Path("/Users/vitorfaroni/Documents/Automation/LIHTCApp/marina_towers_enhanced.json")
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
        
    else:
        print(f"File not found: {test_file}")

if __name__ == "__main__":
    test_enhanced_extraction()