#!/usr/bin/env python3
"""
Comprehensive LIHTC 4% Application Data Extractor
Combines all strategies for maximum accuracy
"""

import pandas as pd
import json
import re
from pathlib import Path
import logging
from datetime import datetime
import sys

class ComprehensiveLIHTCExtractor:
    def __init__(self):
        self.debug_mode = False  # Set to True for detailed debugging
        
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
    
    def search_nearby_for_value(self, df, label_row, label_col, max_distance=8):
        """Search in all directions from a label for the actual value"""
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
        """Check if a value looks like actual data rather than a label"""
        if not value or len(value.strip()) < 2:
            return False
        
        label_indicators = [':', 'instructions', 'note', 'see', 'refer', 'contact', 'phone', 'email']
        if any(indicator in value.lower() for indicator in label_indicators):
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
                
                confidence = 0
                cell_lower = cell_value.lower()
                
                for term in search_terms:
                    if term.lower() in cell_lower:
                        if term.lower() == cell_lower.replace(':', '').strip():
                            confidence += 10
                        else:
                            confidence += len(term)
                
                if confidence > best_confidence:
                    value, val_row, val_col = self.search_nearby_for_value(df, row, col)
                    if value and (not validation_func or validation_func(value)):
                        best_match = {
                            'value': value,
                            'confidence': confidence
                        }
                        best_confidence = confidence
        
        return best_match['value'] if best_match else None
    
    def search_all_numeric_values(self, df, min_val, max_val, context_terms=None):
        """Find all numeric values within a range with optional context filtering"""
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
    
    def get_nearby_context(self, df, center_row, center_col, radius=3):
        """Get text context around a cell"""
        context_parts = []
        
        for row in range(max(0, center_row - radius), min(len(df), center_row + radius + 1)):
            for col in range(max(0, center_col - radius), min(len(df.columns), center_col + radius + 1)):
                value = self.get_cell_value_safe(df, row, col)
                if value:
                    context_parts.append(value)
        
        return " ".join(context_parts)
    
    def extract_application_data_comprehensive(self, file_path):
        """Comprehensive application data extraction"""
        try:
            df = pd.read_excel(file_path, sheet_name="Application", header=None)
            data = {}
            
            # Project Name - try coordinates first, then search
            data['project_name'] = self.get_cell_value_safe(df, 17, 7) or "Not found"
            if data['project_name'] == "Not found":
                data['project_name'] = self.find_field_by_content_search(df, ["PROJECT NAME", "Project Name"]) or "Not found"
            
            # County - try coordinates first, then search
            data['county'] = self.get_cell_value_safe(df, 188, 19) or "Not found"
            if data['county'] == "Not found":
                data['county'] = self.find_field_by_content_search(df, ["County:", "County"]) or "Not found"
            
            # City - enhanced search
            data['city'] = self.find_field_by_content_search(df, ["City:", "City", "Project City"])
            if not data['city']:
                # Try pattern matching for CA cities
                ca_cities_pattern = r'\\b(San Francisco|Los Angeles|Sacramento|San Diego|Oakland|Vallejo|Berkeley|Richmond|Concord|Fremont|Hayward|Santa Rosa|Stockton|Modesto|Fresno|Bakersfield)\\b'
                for row in range(len(df)):
                    for col in range(len(df.columns)):
                        cell_value = self.get_cell_value_safe(df, row, col)
                        if cell_value:
                            match = re.search(ca_cities_pattern, cell_value, re.IGNORECASE)
                            if match:
                                data['city'] = match.group(1)
                                break
                    if data['city']:
                        break
            data['city'] = data['city'] or "Not found"
            
            # General Contractor - enhanced search
            def validate_contractor(value):
                company_indicators = ['inc', 'llc', 'corp', 'company', 'construction', 'builders', 'group']
                value_lower = value.lower()
                return (any(indicator in value_lower for indicator in company_indicators) or 
                       (5 <= len(value) <= 100 and any(c.isupper() for c in value)))
            
            data['general_contractor'] = self.find_field_by_content_search(
                df, ["General Contractor:", "General Contractor", "GC:", "Contractor"], validate_contractor
            ) or "Not found"
            
            # New Construction - enhanced detection
            new_const_result = self.find_field_by_content_search(df, ["New Construction", "Construction Type"])
            if new_const_result:
                if any(word in new_const_result.lower() for word in ['yes', 'new', 'true', 'x']):
                    data['new_construction'] = "Yes"
                elif any(word in new_const_result.lower() for word in ['no', 'rehab', 'renovation', 'false', 'adaptive']):
                    data['new_construction'] = "No"
                else:
                    data['new_construction'] = "Not specified"
            else:
                data['new_construction'] = "Not specified"
            
            # Total Units - enhanced search
            def validate_units(value):
                try:
                    num = int(float(str(value).replace(',', '')))
                    return 1 <= num <= 2000
                except:
                    return False
            
            units_result = self.find_field_by_content_search(
                df, ["Total Number of Units", "Total Units", "# of Units", "Dwelling Units"], validate_units
            )
            
            if units_result:
                try:
                    data['total_units'] = int(float(units_result.replace(',', '')))
                except:
                    data['total_units'] = 0
            else:
                data['total_units'] = 0
            
            # Square Footage - deep search approach
            sqft_matches = self.search_all_numeric_values(
                df, 10000, 1000000, 
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
                if any(bad_term in context_lower for bad_term in ['cost', 'dollar', '$']):
                    score -= 10
                
                if score > best_score:
                    best_score = score
                    best_sqft = int(match['value'])
            
            data['total_sqft_low_income'] = best_sqft
            
            return data
            
        except Exception as e:
            logging.error(f"Error in comprehensive application extraction: {str(e)}")
            return {}
    
    def extract_sources_uses_data_comprehensive(self, file_path):
        """Comprehensive sources and uses extraction"""
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
            
            # Special handling for construction costs - use deep search
            construction_matches = self.search_all_numeric_values(
                df, 500000, 100000000,  # $500K to $100M range
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
                elif 'hard cost' in context_lower:
                    score += 15
                elif 'rehabilitation' in context_lower:
                    score += 25
                
                # Penalty for other specific cost types
                if any(bad_term in context_lower for bad_term in ['land', 'architectural', 'engineering', 'fee', 'soft']):
                    score -= 15
                
                if score > best_score and score > 10:  # Minimum threshold
                    best_score = score
                    best_construction = match['value']
            
            data['total_new_construction'] = best_construction
            
            # Content search for missing fields
            search_mapping = {
                'land_cost': ["Land Cost", "Land Value", "Site Acquisition"],
                'total_architectural': ["Architectural", "Architect Fees", "Design Fees"],
                'total_survey_engineering': ["Survey", "Engineering", "Survey & Engineering"],
                'local_impact_fees': ["Impact Fees", "Development Fees", "Local Fees"]
            }
            
            for field, search_terms in search_mapping.items():
                if data[field] == 0:
                    def validate_cost(value):
                        try:
                            num = float(str(value).replace(',', '').replace('$', ''))
                            return 0 <= num <= 100000000
                        except:
                            return False
                    
                    cost_result = self.find_field_by_content_search(df, search_terms, validate_cost)
                    if cost_result:
                        try:
                            data[field] = float(cost_result.replace(',', '').replace('$', ''))
                        except:
                            pass
            
            return data
            
        except Exception as e:
            logging.error(f"Error in comprehensive sources/uses extraction: {str(e)}")
            return {}
    
    def extract_file_comprehensive(self, file_path):
        """Comprehensive file extraction"""
        result = {
            'filename': file_path.name,
            'application_data': self.extract_application_data_comprehensive(file_path),
            'sources_uses_data': self.extract_sources_uses_data_comprehensive(file_path)
        }
        
        return result

def test_comprehensive_extraction():
    """Test comprehensive extraction on Marina Towers"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    test_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    if test_file.exists():
        extractor = ComprehensiveLIHTCExtractor()
        result = extractor.extract_file_comprehensive(test_file)
        
        print("\\n" + "="*80)
        print("COMPREHENSIVE EXTRACTION RESULTS - MARINA TOWERS")
        print("="*80)
        
        # Format the output nicely
        app_data = result['application_data']
        sources_data = result['sources_uses_data']
        
        print(f"\\n📋 APPLICATION DATA:")
        print(f"   Project Name: {app_data.get('project_name')}")
        print(f"   City: {app_data.get('city')}")
        print(f"   County: {app_data.get('county')}")
        print(f"   General Contractor: {app_data.get('general_contractor')}")
        print(f"   New Construction: {app_data.get('new_construction')}")
        print(f"   Total Units: {app_data.get('total_units'):,}")
        print(f"   Total Sq Ft (Low Income): {app_data.get('total_sqft_low_income'):,}")
        
        print(f"\\n💰 SOURCES & USES DATA:")
        print(f"   Land Cost: ${sources_data.get('land_cost'):,.0f}")
        print(f"   Total New Construction: ${sources_data.get('total_new_construction'):,.0f}")
        print(f"   Total Architectural: ${sources_data.get('total_architectural'):,.0f}")
        print(f"   Total Survey & Engineering: ${sources_data.get('total_survey_engineering'):,.0f}")
        print(f"   Local Impact Fees: ${sources_data.get('local_impact_fees'):,.0f}")
        
        # Save complete results
        output_file = Path("/Users/vitorfaroni/Documents/Automation/LIHTCApp/marina_towers_complete.json")
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\\n📄 Complete results saved to: {output_file}")
        
        # Calculate totals
        total_project_cost = sum([
            sources_data.get('land_cost', 0),
            sources_data.get('total_new_construction', 0),
            sources_data.get('total_architectural', 0),
            sources_data.get('total_survey_engineering', 0),
            sources_data.get('local_impact_fees', 0)
        ])
        
        print(f"\\n📊 SUMMARY:")
        print(f"   Total Tracked Costs: ${total_project_cost:,.0f}")
        print(f"   Cost per Unit: ${total_project_cost/max(1, app_data.get('total_units', 1)):,.0f}")
        print(f"   Cost per Sq Ft: ${total_project_cost/max(1, app_data.get('total_sqft_low_income', 1)):,.0f}")
        
    else:
        print(f"File not found: {test_file}")

if __name__ == "__main__":
    test_comprehensive_extraction()