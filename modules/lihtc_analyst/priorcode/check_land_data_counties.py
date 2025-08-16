#!/usr/bin/env python3
"""
Check county names in the land analysis data to see what format they're in
"""

import pandas as pd
from pathlib import Path

def check_counties():
    """Check county names in the land analysis data"""
    
    # Load land analysis results
    land_files = list(Path('.').glob('CoStar_Land_Analysis_*.xlsx'))
    if land_files:
        latest_land = sorted(land_files)[-1]
        print(f"Loading land analysis from: {latest_land}")
        land_data = pd.read_excel(latest_land, sheet_name='All_Land_Analysis')
    else:
        print("No land analysis files found")
        return
    
    print(f"Loaded {len(land_data)} properties")
    print(f"\nColumns: {list(land_data.columns)}")
    
    # Look for county-related columns
    county_cols = [col for col in land_data.columns if 'county' in col.lower()]
    print(f"\nCounty-related columns: {county_cols}")
    
    # Show unique values in County column
    if 'County' in land_data.columns:
        unique_counties = land_data['County'].unique()
        print(f"\nUnique counties ({len(unique_counties)}):")
        for i, county in enumerate(sorted(unique_counties), 1):
            print(f"{i:3d}. {county}")
    else:
        print("\nNo 'County' column found")
    
    # Show a few sample rows
    print("\nSample data:")
    print(land_data[['Address', 'City', 'County']].head(10) if 'County' in land_data.columns else land_data.head(3))

if __name__ == "__main__":
    check_counties()