#!/usr/bin/env python3
"""
Check specific counties in the HUD AMI GeoPackage to understand the data structure better
"""

import geopandas as gpd
import pandas as pd

def check_specific_counties():
    # Load the GeoPackage file
    gpkg_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD_AMI_Geographic/States/tx_counties_hud_ami_2025.gpkg'
    
    # Read the GeoPackage
    gdf = gpd.read_file(gpkg_path)
    
    # Look for specific counties we know should exist
    test_counties = ['Harris', 'Dallas', 'Travis', 'Bexar', 'Tarrant']
    
    print("Searching for specific counties:")
    for county in test_counties:
        # Search in different name columns
        mask = (gdf['NAME'].str.contains(county, case=False, na=False) | 
                gdf['county_name'].str.contains(county, case=False, na=False) |
                gdf['county_name_census'].str.contains(county, case=False, na=False))
        
        matches = gdf[mask]
        if len(matches) > 0:
            print(f"\n{county} County found:")
            for idx, row in matches.iterrows():
                print(f"  NAME: {row['NAME']}")
                print(f"  county_name: {row['county_name']}")
                print(f"  county_name_census: {row['county_name_census']}")
                print(f"  hud_area_name: {row['hud_area_name']}")
                print(f"  county_fips: {row['county_fips']}")
                print(f"  median_ami_2025: ${row['median_ami_2025']:,.0f}")
                print(f"  rent_2br_50pct: ${row['rent_2br_50pct']:,.0f}")
                print(f"  metro_status: {row['metro_status']}")
        else:
            print(f"\n{county} County NOT FOUND")
    
    # Show all unique county names (sorted)
    print("\n\nAll Texas counties in the dataset (sorted):")
    all_counties = sorted(gdf['county_name'].unique())
    for i, county in enumerate(all_counties[:30], 1):
        print(f"{i:3d}. {county}")
    print(f"... and {len(all_counties) - 30} more counties")
    
    # Check for any null values in key columns
    print("\n\nChecking for null values in key columns:")
    key_cols = ['county_name', 'hud_area_name', 'median_ami_2025', 'rent_2br_50pct']
    for col in key_cols:
        null_count = gdf[col].isnull().sum()
        print(f"{col}: {null_count} null values")

if __name__ == "__main__":
    check_specific_counties()