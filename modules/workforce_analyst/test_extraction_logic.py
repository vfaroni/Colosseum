#!/usr/bin/env python3
"""
Unit tests for rent roll extraction logic
Following TDD principles from CLAUDE.md
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestUnitCountCalculations(unittest.TestCase):
    """Test suite for unit count calculations"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample rent roll data similar to Sunset Gardens format
        self.sample_data = pd.DataFrame({
            'Unit': ['A01', 'A02', 'A03', 'B01', 'B02', 'VACANT', 'Total'],
            'Unit_Type': ['sg01', 'sg01', 'sg02', 'sg02', 'sg02', 'sg01', 'Summary'],
            'Actual_Rent': [2000, 1950, 2500, 2600, 0, 0, 210050],
            'Market_Rent': [2100, 2100, 2700, 2700, 2700, 2100, 240300]
        })
    
    def test_identify_rent_column_standard_names(self):
        """Test identification of rent columns with standard names"""
        df = pd.DataFrame({
            'Unit': ['A01', 'A02'],
            'Current Rent': [2000, 1950],
            'Market Rent': [2100, 2100]
        })
        
        rent_col = find_rent_column(df)
        self.assertEqual(rent_col, 'Current Rent')
    
    def test_identify_rent_column_actual_rent(self):
        """Test identification with 'Actual Rent' column name"""
        df = pd.DataFrame({
            'Unit': ['A01', 'A02'],
            'Actual Rent': [2000, 1950],
            'Market Rent': [2100, 2100]
        })
        
        rent_col = find_rent_column(df)
        self.assertEqual(rent_col, 'Actual Rent')
    
    def test_count_total_units_including_vacant(self):
        """Ensure total unit count includes vacant units"""
        result = count_total_units(self.sample_data)
        
        # Should count all units except summary rows
        self.assertEqual(result['total_units'], 6)  # A01, A02, A03, B01, B02, VACANT
    
    def test_count_occupied_units_only(self):
        """Ensure occupied unit count excludes vacant units"""
        result = count_occupied_units(self.sample_data)
        
        # Should only count units with rent > 0
        self.assertEqual(result['occupied_units'], 4)  # A01, A02, B01, B02 (B02 has 0 rent)
        
    def test_calculate_average_rent_from_occupied_only(self):
        """Test average rent calculation from occupied units only"""
        result = calculate_average_rent(self.sample_data)
        
        # Average of 2000, 1950, 2500, 2600 = 8050/4 = 2012.5
        expected_avg = (2000 + 1950 + 2500 + 2600) / 4
        self.assertAlmostEqual(result['avg_rent'], expected_avg, places=2)
    
    def test_skip_summary_rows(self):
        """Test that summary rows are properly excluded"""
        result = count_total_units(self.sample_data)
        
        # Should not count 'Total' row
        unit_list = result['unit_list']
        self.assertNotIn('Total', unit_list)

class TestRentCalculations(unittest.TestCase):
    """Test suite for rent calculations"""
    
    def setUp(self):
        """Set up test data"""
        self.sample_data = pd.DataFrame({
            'Unit': ['A01', 'A02', 'A03', 'B01', 'B02'],
            'Unit_Type': ['sg01', 'sg01', 'sg02', 'sg02', 'sg01'],
            'Actual_Rent': [2000, 1950, 2500, 2600, 0],  # B02 is vacant
        })
    
    def test_parse_unit_type_bedrooms_sg_format(self):
        """Test parsing of sg01, sg02 format unit types"""
        self.assertEqual(parse_unit_type_bedrooms('sg01'), 1)
        self.assertEqual(parse_unit_type_bedrooms('sg02'), 2)
        self.assertEqual(parse_unit_type_bedrooms('sg03'), 3)
        self.assertEqual(parse_unit_type_bedrooms('sg00'), 0)
    
    def test_parse_unit_type_bedrooms_standard_format(self):
        """Test parsing of standard bedroom format"""
        self.assertEqual(parse_unit_type_bedrooms('1BR'), 1)
        self.assertEqual(parse_unit_type_bedrooms('2 BR'), 2)
        self.assertEqual(parse_unit_type_bedrooms('Studio'), 0)
        self.assertEqual(parse_unit_type_bedrooms('3BR'), 3)
    
    def test_calculate_unit_type_breakdown_total_units(self):
        """Test unit type breakdown includes all units (occupied + vacant)"""
        result = calculate_unit_type_breakdown(self.sample_data)
        
        # Should count ALL units by type: 3x sg01 (1BR), 2x sg02 (2BR)
        self.assertEqual(result['1BR']['total_units'], 3)
        self.assertEqual(result['2BR']['total_units'], 2)
    
    def test_calculate_unit_type_breakdown_occupied_only(self):
        """Test unit type breakdown calculates rents from occupied units only"""
        result = calculate_unit_type_breakdown(self.sample_data)
        
        # 1BR: occupied = 2 units (A01=2000, A02=1950), avg = 1975
        self.assertEqual(result['1BR']['occupied_units'], 2)
        self.assertAlmostEqual(result['1BR']['avg_rent'], 1975.0, places=2)
        
        # 2BR: occupied = 2 units (A03=2500, B01=2600), avg = 2550
        self.assertEqual(result['2BR']['occupied_units'], 2)
        self.assertAlmostEqual(result['2BR']['avg_rent'], 2550.0, places=2)

class TestExcelHeaderHandling(unittest.TestCase):
    """Test suite for Excel header row handling"""
    
    def test_detect_header_rows(self):
        """Test detection of header rows in Excel data"""
        # Simulate Excel data with headers
        df = pd.DataFrame({
            'Col0': ['Property Name', 'As Of Date', 'Headers', 'Unit', 'A01', 'A02'],
            'Col1': [None, None, None, 'Unit Type', 'sg01', 'sg01'],
            'Col2': [None, None, None, 'Rent', 2000, 1950]
        })
        
        header_row = detect_header_row(df)
        self.assertEqual(header_row, 3)  # Row with 'Unit', 'Unit Type', 'Rent'
    
    def test_extract_data_after_headers(self):
        """Test extraction of data rows after headers"""
        df = pd.DataFrame({
            'Col0': ['Title', 'Unit', 'A01', 'A02', 'Total'],
            'Col1': ['Info', 'Type', 'sg01', 'sg01', 'Summary'],
            'Col2': ['More', 'Rent', 2000, 1950, 3950]
        })
        
        data_df = extract_data_rows(df, header_row=1)
        
        # Should get rows A01 and A02, but not Total
        self.assertEqual(len(data_df), 2)
        self.assertIn('A01', data_df.iloc[0, 0])
        self.assertIn('A02', data_df.iloc[1, 0])

# Helper functions to be implemented
def find_rent_column(df):
    """Find the rent column in DataFrame"""
    for col in df.columns:
        col_lower = str(col).lower()
        if any(term in col_lower for term in ['current rent', 'actual rent', 'rent']) and 'market' not in col_lower:
            return col
    return None

def count_total_units(df):
    """Count total units including vacant"""
    # Filter out summary rows
    data_df = df[~df['Unit'].astype(str).str.contains('Total|Summary', na=False, case=False)]
    data_df = data_df[data_df['Unit'].notna()]
    
    return {
        'total_units': len(data_df),
        'unit_list': data_df['Unit'].tolist()
    }

def count_occupied_units(df):
    """Count only occupied units (rent > 0)"""
    # Convert rent to numeric
    df_clean = df.copy()
    df_clean['Actual_Rent'] = pd.to_numeric(df_clean['Actual_Rent'], errors='coerce')
    
    # Filter occupied and non-summary rows
    occupied_df = df_clean[(df_clean['Actual_Rent'] > 0) & 
                          (~df_clean['Unit'].astype(str).str.contains('Total|Summary', na=False, case=False))]
    
    return {'occupied_units': len(occupied_df)}

def calculate_average_rent(df):
    """Calculate average rent from occupied units only"""
    df_clean = df.copy()
    df_clean['Actual_Rent'] = pd.to_numeric(df_clean['Actual_Rent'], errors='coerce')
    
    occupied_df = df_clean[(df_clean['Actual_Rent'] > 0) & 
                          (~df_clean['Unit'].astype(str).str.contains('Total|Summary', na=False, case=False))]
    
    if len(occupied_df) > 0:
        return {'avg_rent': occupied_df['Actual_Rent'].mean()}
    return {'avg_rent': 0}

def parse_unit_type_bedrooms(unit_type_str):
    """Parse unit type to extract bedroom count"""
    try:
        unit_str = str(unit_type_str).strip().lower()
        
        # Handle sg format (Sunset Gardens style)
        if 'sg01' in unit_str:
            return 1
        elif 'sg02' in unit_str:
            return 2
        elif 'sg03' in unit_str:
            return 3
        elif 'sg00' in unit_str:
            return 0
        
        # Handle standard formats
        if 'studio' in unit_str or '0br' in unit_str:
            return 0
        elif '1br' in unit_str or '1 br' in unit_str:
            return 1
        elif '2br' in unit_str or '2 br' in unit_str:
            return 2
        elif '3br' in unit_str or '3 br' in unit_str:
            return 3
        elif '4br' in unit_str or '4 br' in unit_str:
            return 4
        
    except:
        pass
    
    return -1  # Unknown

def calculate_unit_type_breakdown(df):
    """Calculate unit breakdown by bedroom type"""
    df_clean = df.copy()
    df_clean['Actual_Rent'] = pd.to_numeric(df_clean['Actual_Rent'], errors='coerce')
    
    # Filter out summary rows
    data_df = df_clean[~df_clean['Unit'].astype(str).str.contains('Total|Summary', na=False, case=False)]
    
    breakdown = {}
    
    for _, row in data_df.iterrows():
        bedroom_count = parse_unit_type_bedrooms(row['Unit_Type'])
        
        if bedroom_count >= 0:
            br_label = 'Studio' if bedroom_count == 0 else f'{bedroom_count}BR'
            
            if br_label not in breakdown:
                breakdown[br_label] = {
                    'total_units': 0,
                    'occupied_units': 0,
                    'rents': []
                }
            
            breakdown[br_label]['total_units'] += 1
            
            if row['Actual_Rent'] > 0:
                breakdown[br_label]['occupied_units'] += 1
                breakdown[br_label]['rents'].append(row['Actual_Rent'])
    
    # Calculate averages
    for br_label in breakdown:
        rents = breakdown[br_label]['rents']
        breakdown[br_label]['avg_rent'] = sum(rents) / len(rents) if rents else 0
    
    return breakdown

def detect_header_row(df):
    """Detect which row contains the headers"""
    for idx, row in df.iterrows():
        row_str = ' '.join([str(val).lower() for val in row if pd.notna(val)])
        if 'unit' in row_str and ('rent' in row_str or 'type' in row_str):
            return idx
    return 0

def extract_data_rows(df, header_row):
    """Extract data rows after header row, excluding summary rows"""
    data_df = df.iloc[header_row + 1:].copy()
    
    # Filter out summary rows
    if len(data_df.columns) > 0:
        data_df = data_df[~data_df.iloc[:, 0].astype(str).str.contains('Total|Summary', na=False, case=False)]
        data_df = data_df[data_df.iloc[:, 0].notna()]
    
    return data_df

if __name__ == '__main__':
    unittest.main(verbosity=2)