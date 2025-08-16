#!/usr/bin/env python3
"""
Direct test of extraction methods without importing the full AcquisitionAnalyst module
"""

import pandas as pd
import numpy as np
import re
from typing import Dict

def parse_unit_type_bedrooms_improved(unit_type_str: str) -> int:
    """Improved unit type parsing with better format handling"""
    try:
        unit_str = str(unit_type_str).strip().lower()
        
        # Handle property-specific formats first
        if 'sg01' in unit_str:
            return 1
        elif 'sg02' in unit_str:
            return 2
        elif 'sg03' in unit_str:
            return 3
        elif 'sg00' in unit_str:
            return 0
        
        # Handle standard formats
        if 'studio' in unit_str or '0br' in unit_str or '0 br' in unit_str:
            return 0
        elif '1br' in unit_str or '1 br' in unit_str or 'one bed' in unit_str:
            return 1
        elif '2br' in unit_str or '2 br' in unit_str or 'two bed' in unit_str:
            return 2
        elif '3br' in unit_str or '3 br' in unit_str or 'three bed' in unit_str:
            return 3
        elif '4br' in unit_str or '4 br' in unit_str or 'four bed' in unit_str:
            return 4
        
        # Try to extract numbers from coded formats
        numbers = re.findall(r'\d+', unit_str)
        if numbers:
            # Take the last number as it's often the bedroom count
            last_num = int(numbers[-1])
            if 0 <= last_num <= 4:
                return last_num
        
    except Exception as e:
        print(f"Error parsing unit type '{unit_type_str}': {e}")
    
    return -1  # Unknown

def detect_rent_roll_structure(df: pd.DataFrame) -> Dict:
    """Detect the structure of rent roll data including header row and column mappings"""
    result = {
        'success': False,
        'header_row': -1,
        'unit_col': None,
        'unit_type_col': None,
        'rent_col': None,
        'market_rent_col': None
    }
    
    try:
        # Look for header row by scanning for key terms
        for idx, row in df.iterrows():
            row_values = [str(val).lower().strip() for val in row if pd.notna(val)]
            row_text = ' '.join(row_values)
            
            # Check if this row contains rent roll headers
            if ('unit' in row_text and 
                ('rent' in row_text or 'type' in row_text) and
                idx < len(df) - 10):  # Not in the last few rows (summary area)
                
                result['header_row'] = idx
                result['success'] = True
                
                # Map columns based on header content
                for col_idx, val in enumerate(row):
                    val_str = str(val).lower().strip() if pd.notna(val) else ''
                    col_name = df.columns[col_idx]
                    
                    if val_str == 'unit' and not result['unit_col']:
                        result['unit_col'] = col_name
                    elif any(term in val_str for term in ['unit type', 'type', 'floorplan']) and not result['unit_type_col']:
                        result['unit_type_col'] = col_name
                    elif any(term in val_str for term in ['actual rent', 'current rent', 'rent']) and 'market' not in val_str and not result['rent_col']:
                        result['rent_col'] = col_name
                    elif any(term in val_str for term in ['market rent', 'market']) and not result['market_rent_col']:
                        result['market_rent_col'] = col_name
                
                print(f"Detected header row {idx} with mappings: "
                       f"Unit={result['unit_col']}, Type={result['unit_type_col']}, Rent={result['rent_col']}")
                break
        
        # If we found a header row but couldn't map all columns, try positional mapping
        if result['success'] and result['header_row'] >= 0:
            if not result['unit_col'] or not result['rent_col']:
                print("Trying positional column mapping")
                cols = list(df.columns)
                
                # Common patterns: Unit | Unit Type | ... | Market Rent | Actual Rent
                if len(cols) >= 6:
                    result['unit_col'] = cols[0] if not result['unit_col'] else result['unit_col']
                    result['unit_type_col'] = cols[1] if not result['unit_type_col'] else result['unit_type_col']
                    result['market_rent_col'] = cols[5] if not result['market_rent_col'] else result['market_rent_col']
                    result['rent_col'] = cols[6] if not result['rent_col'] else result['rent_col']
                    print(f"Positional mapping: Unit={result['unit_col']}, Type={result['unit_type_col']}, Rent={result['rent_col']}")
                
    except Exception as e:
        print(f"Error detecting rent roll structure: {e}")
        result['success'] = False
    
    return result

def extract_clean_rent_data(df: pd.DataFrame, header_info: Dict) -> pd.DataFrame:
    """Extract clean rent data using detected structure"""
    try:
        # Start from row after headers
        data_start_row = header_info['header_row'] + 1
        data_df = df.iloc[data_start_row:].copy()
        
        # Create clean dataframe with standardized column names
        clean_data = pd.DataFrame()
        
        if header_info['unit_col']:
            clean_data['unit'] = data_df[header_info['unit_col']]
        if header_info['unit_type_col']:
            clean_data['unit_type'] = data_df[header_info['unit_type_col']]
        if header_info['rent_col']:
            clean_data['rent'] = pd.to_numeric(data_df[header_info['rent_col']], errors='coerce')
        if header_info['market_rent_col']:
            clean_data['market_rent'] = pd.to_numeric(data_df[header_info['market_rent_col']], errors='coerce')
        
        # Filter out summary rows and invalid data
        if 'unit' in clean_data.columns:
            # First, find where the "Future Residents/Applicants" section starts
            future_cutoff_idx = None
            for idx, val in clean_data['unit'].items():
                val_str = str(val).lower()
                if 'future' in val_str and ('residents' in val_str or 'applicants' in val_str):
                    future_cutoff_idx = idx
                    break
            
            # If found, cut off everything from that point onward
            if future_cutoff_idx is not None:
                clean_data = clean_data.loc[:future_cutoff_idx-1]
                print(f"Cut off data at 'Future Residents/Applicants' section at index {future_cutoff_idx}")
            
            # Remove rows where unit is null or contains summary terms
            clean_data = clean_data[clean_data['unit'].notna()]
            clean_data = clean_data[~clean_data['unit'].astype(str).str.contains(
                'total|summary|occupied units|vacant residents', case=False, na=False)]
        
        # Fill missing rent with 0 (vacant units)
        if 'rent' in clean_data.columns:
            clean_data['rent'] = clean_data['rent'].fillna(0)
        
        print(f"Extracted {len(clean_data)} clean data rows")
        return clean_data
        
    except Exception as e:
        print(f"Error extracting clean rent data: {e}")
        return pd.DataFrame()

def calculate_improved_unit_type_data(clean_data: pd.DataFrame) -> Dict[str, str]:
    """Calculate unit type breakdown using improved logic"""
    result = {}
    
    try:
        if 'unit_type' not in clean_data.columns or 'rent' not in clean_data.columns:
            print("Missing required columns for unit type calculation")
            return result
        
        # Group by bedroom count
        bedroom_stats = {}
        
        for _, row in clean_data.iterrows():
            unit_type = str(row['unit_type']) if pd.notna(row['unit_type']) else ''
            rent = row['rent'] if pd.notna(row['rent']) else 0
            
            bedroom_count = parse_unit_type_bedrooms_improved(unit_type)
            
            if bedroom_count >= 0:
                if bedroom_count not in bedroom_stats:
                    bedroom_stats[bedroom_count] = {
                        'total_units': 0,
                        'occupied_rents': []
                    }
                
                bedroom_stats[bedroom_count]['total_units'] += 1
                if rent > 0:
                    bedroom_stats[bedroom_count]['occupied_rents'].append(rent)
        
        # Convert to result format
        for bedroom_count, stats in bedroom_stats.items():
            total_units = stats['total_units']
            rents = stats['occupied_rents']
            avg_rent = sum(rents) / len(rents) if rents else 0
            
            if bedroom_count == 0:  # Studio
                result["# Studio Units"] = str(total_units)
                if avg_rent > 0:
                    result["Studio Rents"] = f"${avg_rent:,.0f}"
            elif bedroom_count == 1:  # 1 Bedroom
                result["# 1 Bed Units"] = str(total_units)
                if avg_rent > 0:
                    result["1 Bed Current Rents"] = f"${avg_rent:,.0f}"
            elif bedroom_count == 2:  # 2 Bedroom
                result["# 2 Bed Units"] = str(total_units)
                if avg_rent > 0:
                    result["2 Bed Current Rents"] = f"${avg_rent:,.0f}"
            elif bedroom_count == 3:  # 3 Bedroom
                result["# 3 Bed Units"] = str(total_units)
                if avg_rent > 0:
                    result["3 Bed Current Rents"] = f"${avg_rent:,.0f}"
            elif bedroom_count == 4:  # 4 Bedroom
                result["# 4 Bed Units"] = str(total_units)
                if avg_rent > 0:
                    result["4 Bed Current Rents"] = f"${avg_rent:,.0f}"
        
        print(f"Unit type breakdown: {[(k, v['total_units']) for k, v in bedroom_stats.items()]}")
        
    except Exception as e:
        print(f"Error calculating improved unit type data: {e}")
    
    return result

def test_fixed_extraction():
    """Test the fixed extraction logic directly"""
    
    print("=== TESTING FIXED EXTRACTION LOGIC ===")
    
    rent_roll_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Deals/Sunset Gardens - El Cajon, CA/02. Rent Roll/Sunset Gardens - Rent Roll - 6.23.2025.xlsx"
    
    try:
        # Read the Excel file
        df = pd.read_excel(rent_roll_path, sheet_name='Report1')
        print(f"Loaded Excel file with {len(df)} rows")
        
        # Test structure detection
        header_info = detect_rent_roll_structure(df)
        
        if header_info['success']:
            print("✅ Successfully detected rent roll structure")
            
            # Extract clean data
            clean_data = extract_clean_rent_data(df, header_info)
            
            if len(clean_data) > 0:
                print(f"✅ Extracted {len(clean_data)} clean data rows")
                
                # Calculate totals
                total_units = len(clean_data)
                occupied_data = clean_data[clean_data['rent'] > 0]
                occupied_units = len(occupied_data)
                avg_rent = occupied_data['rent'].mean() if occupied_units > 0 else 0
                
                print(f"\n=== CALCULATED RESULTS ===")
                print(f"Total Units: {total_units}")
                print(f"Occupied Units: {occupied_units}")
                print(f"Average Rent: ${avg_rent:,.2f}")
                
                # Calculate unit type breakdown
                unit_type_data = calculate_improved_unit_type_data(clean_data)
                
                print(f"\n=== UNIT TYPE BREAKDOWN ===")
                for key, value in unit_type_data.items():
                    if value:
                        print(f"{key}: {value}")
                
                # Validation
                print(f"\n=== VALIDATION ===")
                success = True
                
                if total_units == 102:
                    print("✅ Total units: CORRECT (102)")
                else:
                    print(f"❌ Total units: Expected 102, got {total_units}")
                    success = False
                
                if 2200 <= avg_rent <= 2300:
                    print(f"✅ Average rent: CORRECT (${avg_rent:,.2f})")
                else:
                    print(f"❌ Average rent: Expected ~$2,243, got ${avg_rent:,.2f}")
                    success = False
                
                # Check unit mix
                unit_1br = int(unit_type_data.get("# 1 Bed Units", "0"))
                unit_2br = int(unit_type_data.get("# 2 Bed Units", "0"))
                
                if unit_1br > 0 and unit_2br > 0 and unit_1br + unit_2br == total_units:
                    print(f"✅ Unit mix: CORRECT ({unit_1br} x 1BR + {unit_2br} x 2BR)")
                else:
                    print(f"❌ Unit mix: Expected 1BR + 2BR = 102, got {unit_1br} + {unit_2br} = {unit_1br + unit_2br}")
                    success = False
                
                if success:
                    print("\n🎉 ALL TESTS PASSED! Fixed extraction logic works correctly.")
                else:
                    print("\n❌ Some tests failed.")
                
                return success
            else:
                print("❌ Failed to extract clean data")
                return False
        else:
            print("❌ Failed to detect rent roll structure")
            return False
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fixed_extraction()