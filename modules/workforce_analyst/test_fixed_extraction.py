#!/usr/bin/env python3
"""
Test the fixed extraction logic on Sunset Gardens data
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the DataExtractor class to test the fixes
class MockStreamlit:
    """Mock streamlit for testing"""
    def write(self, msg):
        print(f"[DEBUG] {msg}")

# Mock the streamlit module
sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

from AcquisitionAnalyst import DataExtractor

def test_fixed_extraction():
    """Test the fixed extraction logic"""
    
    print("=== TESTING FIXED EXTRACTION LOGIC ===")
    
    # Create a DataExtractor instance (we'll mock the OpenAI key)
    extractor = DataExtractor("fake-key")
    
    # Load the Sunset Gardens rent roll
    rent_roll_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Deals/Sunset Gardens - El Cajon, CA/02. Rent Roll/Sunset Gardens - Rent Roll - 6.23.2025.xlsx"
    
    try:
        # Read the Excel file
        df_data = {}
        excel_file = pd.ExcelFile(rent_roll_path)
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(rent_roll_path, sheet_name=sheet_name)
            df_data[sheet_name] = df
        
        print(f"Loaded Excel file with sheets: {list(df_data.keys())}")
        
        # Test our fixed extraction logic
        result = extractor._analyze_rent_roll_data(df_data, "Sunset Gardens - Rent Roll - 6.23.2025.xlsx")
        
        print("\n=== EXTRACTION RESULTS ===")
        for key, value in result.items():
            if value:  # Only show non-empty values
                print(f"{key}: {value}")
        
        # Expected correct values for comparison
        print("\n=== EXPECTED VALUES ===")
        print("Number of Units: 102")
        print("Avg In Place Rents: $2,243")
        print("# 1 Bed Units: ~54")
        print("# 2 Bed Units: ~50") 
        print("1 Bed Current Rents: ~$1,968")
        print("2 Bed Current Rents: ~$2,507")
        
        # Validate results
        print("\n=== VALIDATION ===")
        
        success = True
        
        # Check total units
        if result.get("Number of Units") == "102":
            print("✅ Total units count: CORRECT")
        else:
            print(f"❌ Total units count: Expected 102, got {result.get('Number of Units')}")
            success = False
        
        # Check average rent (should be around $2,243)
        avg_rent_str = result.get("Avg In Place Rents", "")
        if avg_rent_str:
            avg_rent_num = float(avg_rent_str.replace("$", "").replace(",", ""))
            if 2200 <= avg_rent_num <= 2300:
                print(f"✅ Average rent: CORRECT ({avg_rent_str})")
            else:
                print(f"❌ Average rent: Expected ~$2,243, got {avg_rent_str}")
                success = False
        else:
            print("❌ Average rent: Not calculated")
            success = False
        
        # Check unit mix (should be 1BR and 2BR only)
        unit_1br = result.get("# 1 Bed Units", "")
        unit_2br = result.get("# 2 Bed Units", "")
        unit_studio = result.get("# Studio Units", "")
        unit_3br = result.get("# 3 Bed Units", "")
        
        if unit_1br and unit_2br and not unit_studio and not unit_3br:
            total_mix = int(unit_1br) + int(unit_2br)
            if total_mix == 102:
                print(f"✅ Unit mix: CORRECT ({unit_1br} x 1BR + {unit_2br} x 2BR = {total_mix})")
            else:
                print(f"❌ Unit mix total: Expected 102, got {total_mix}")
                success = False
        else:
            print(f"❌ Unit mix: Expected only 1BR and 2BR, got Studio:{unit_studio}, 1BR:{unit_1br}, 2BR:{unit_2br}, 3BR:{unit_3br}")
            success = False
        
        # Overall result
        if success:
            print("\n🎉 ALL TESTS PASSED! The fixed extraction logic is working correctly.")
        else:
            print("\n❌ Some tests failed. The extraction logic needs further adjustments.")
        
        return success
        
    except Exception as e:
        print(f"Error testing extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fixed_extraction()