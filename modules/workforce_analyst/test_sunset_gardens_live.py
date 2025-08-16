#!/usr/bin/env python3
"""
Live test of the fixed extraction logic on Sunset Gardens deal
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit for testing
class MockStreamlit:
    def write(self, msg):
        print(f"[DEBUG] {msg}")
    def error(self, msg):
        print(f"[ERROR] {msg}")
    def warning(self, msg):
        print(f"[WARNING] {msg}")

# Mock the streamlit module
sys.modules['streamlit'] = MockStreamlit()
import streamlit as st

# Import the DataExtractor with our fixes
from AcquisitionAnalyst import DataExtractor

def test_live_extraction():
    """Test the fixed extraction on actual Sunset Gardens files"""
    
    print("=== LIVE TEST: SUNSET GARDENS EXTRACTION ===")
    print("Testing fixed extraction logic on real deal files...")
    
    # Create a DataExtractor instance
    extractor = DataExtractor("fake-openai-key")  # We won't use OpenAI for this test
    
    # Path to the actual rent roll file
    rent_roll_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Deals/Sunset Gardens - El Cajon, CA/02. Rent Roll/Sunset Gardens - Rent Roll - 6.23.2025.xlsx"
    
    print(f"Reading rent roll: {rent_roll_path}")
    
    try:
        # Test the extract_from_excel method with the real file
        result = extractor.extract_from_excel(Path(rent_roll_path))
        
        print("\n=== EXTRACTION RESULTS ===")
        
        # Display all non-empty results
        for key, value in result.items():
            if value and value.strip():
                print(f"{key}: {value}")
        
        print("\n=== VALIDATION AGAINST EXPECTED VALUES ===")
        
        # Expected correct values for Sunset Gardens
        expected = {
            "Number of Units": "102",
            "Avg In Place Rents": "$2,243",  # Allow some rounding
            "# 1 Bed Units": "53",  # Approximately
            "# 2 Bed Units": "49",  # Approximately
            "1 Bed Current Rents": "$1,968",  # Approximately  
            "2 Bed Current Rents": "$2,507"   # Approximately
        }
        
        success = True
        
        # Validate key metrics
        for field, expected_value in expected.items():
            actual_value = result.get(field, "")
            
            if field == "Number of Units":
                if actual_value == expected_value:
                    print(f"✅ {field}: {actual_value} (CORRECT)")
                else:
                    print(f"❌ {field}: Expected {expected_value}, got {actual_value}")
                    success = False
                    
            elif field == "Avg In Place Rents":
                if actual_value:
                    # Extract numeric value
                    actual_num = float(actual_value.replace("$", "").replace(",", ""))
                    expected_num = float(expected_value.replace("$", "").replace(",", ""))
                    
                    if abs(actual_num - expected_num) <= 50:  # Allow $50 tolerance
                        print(f"✅ {field}: {actual_value} (CORRECT - within tolerance)")
                    else:
                        print(f"❌ {field}: Expected ~{expected_value}, got {actual_value}")
                        success = False
                else:
                    print(f"❌ {field}: Not calculated")
                    success = False
                    
            elif field in ["# 1 Bed Units", "# 2 Bed Units"]:
                if actual_value:
                    actual_num = int(actual_value)
                    expected_num = int(expected_value)
                    
                    if abs(actual_num - expected_num) <= 3:  # Allow small variance
                        print(f"✅ {field}: {actual_value} (CORRECT - within tolerance)")
                    else:
                        print(f"❌ {field}: Expected ~{expected_value}, got {actual_value}")
                        success = False
                else:
                    print(f"❌ {field}: Not calculated")
                    success = False
                    
            elif "Rents" in field:
                if actual_value:
                    actual_num = float(actual_value.replace("$", "").replace(",", ""))
                    expected_num = float(expected_value.replace("$", "").replace(",", ""))
                    
                    if abs(actual_num - expected_num) <= 100:  # Allow $100 tolerance
                        print(f"✅ {field}: {actual_value} (CORRECT - within tolerance)")
                    else:
                        print(f"❌ {field}: Expected ~{expected_value}, got {actual_value}")
                        success = False
                else:
                    print(f"❌ {field}: Not calculated")
                    success = False
        
        # Check that we don't have studio or 3BR units (Sunset Gardens only has 1BR and 2BR)
        studio_units = result.get("# Studio Units", "")
        three_br_units = result.get("# 3 Bed Units", "")
        
        if not studio_units and not three_br_units:
            print("✅ Unit mix: Correctly shows only 1BR and 2BR units")
        else:
            print(f"❌ Unit mix: Incorrectly shows Studio:{studio_units}, 3BR:{three_br_units}")
            success = False
        
        # Final result
        print("\n" + "="*50)
        if success:
            print("🎉 LIVE TEST PASSED!")
            print("The fixed extraction logic correctly processes Sunset Gardens data.")
        else:
            print("❌ LIVE TEST FAILED!")
            print("The extraction logic needs further adjustments.")
        
        print("="*50)
        return success
        
    except Exception as e:
        print(f"ERROR: Failed to test extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_live_extraction()