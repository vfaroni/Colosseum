#!/usr/bin/env python3
"""
Debug tract format matching issue
"""

import pandas as pd
import os

def debug_tract_formats():
    """Debug tract format conversion issues"""
    
    print("🧪 DEBUGGING TRACT FORMAT CONVERSION")
    print("="*50)
    
    # Load QCT data
    qct_file = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data/qct_data_2025.xlsx"
    qct_data = pd.read_excel(qct_file)
    
    print(f"Loaded {len(qct_data)} QCT records")
    
    # Check Texas Harris County tracts
    harris_tracts = qct_data[
        (qct_data['state'] == 48) &  # Texas
        (qct_data['county'] == 201)   # Harris County
    ]
    
    print(f"\nFound {len(harris_tracts)} Harris County tracts")
    
    # Show sample tract formats
    print("\nSample Harris County tract formats:")
    sample_tracts = harris_tracts[['state', 'county', 'tract', 'qct']].head(10)
    print(sample_tracts)
    
    # Test the conversion with our specific tract
    census_tract = "312300"  # From Census API
    
    print(f"\n🎯 Converting Census tract: {census_tract}")
    
    # Try different conversion methods
    conversions = [
        float(census_tract[:4] + "." + census_tract[4:]),  # 3123.00
        float(census_tract),  # 312300.0
        float(census_tract) / 100,  # 3123.0
        int(census_tract) / 100,  # 3123
    ]
    
    for i, converted in enumerate(conversions, 1):
        print(f"Method {i}: {converted}")
        
        # Check if this format exists in Harris County data
        matches = harris_tracts[harris_tracts['tract'] == converted]
        if len(matches) > 0:
            match = matches.iloc[0]
            print(f"  ✅ MATCH FOUND! QCT status: {match['qct']}")
            print(f"  Record: State={match['state']}, County={match['county']}, Tract={match['tract']}")
            break
        else:
            print(f"  ❌ No match")
    
    # Show tract range in Harris County for context
    print(f"\nHarris County tract range:")
    print(f"Min tract: {harris_tracts['tract'].min()}")
    print(f"Max tract: {harris_tracts['tract'].max()}")
    
    # Show some QCT tracts in Harris County
    qct_tracts = harris_tracts[harris_tracts['qct'] == 1]
    print(f"\nFound {len(qct_tracts)} QCT tracts in Harris County")
    if len(qct_tracts) > 0:
        print("Sample QCT tracts:")
        print(qct_tracts[['tract', 'qct']].head())

if __name__ == "__main__":
    debug_tract_formats()