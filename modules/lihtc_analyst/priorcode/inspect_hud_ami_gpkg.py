#!/usr/bin/env python3
"""
Inspect the Texas HUD AMI GeoPackage file to understand its structure
and see if it contains county names that can help fix the economic viability analyzer.
"""

import geopandas as gpd
import pandas as pd

def inspect_hud_ami_gpkg():
    # Load the GeoPackage file
    gpkg_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD_AMI_Geographic/States/tx_counties_hud_ami_2025.gpkg'
    
    try:
        # Read the GeoPackage
        print(f"Loading GeoPackage from: {gpkg_path}")
        gdf = gpd.read_file(gpkg_path)
        
        print('\nGeoPackage loaded successfully!')
        print(f'Total records: {len(gdf)}')
        print(f'\nColumns: {list(gdf.columns)}')
        print(f'\nData types:\n{gdf.dtypes}')
        
        # Display first few records without geometry
        print('\nFirst 5 records (without geometry):')
        print(gdf.drop('geometry', axis=1).head())
        
        # Check for county name columns
        print('\nChecking for county-related columns:')
        county_cols = [col for col in gdf.columns if 'county' in col.lower() or 'name' in col.lower()]
        print(f'County-related columns: {county_cols}')
        
        # Show unique values in potential county columns
        for col in county_cols:
            if col != 'geometry':
                print(f'\nUnique values in {col} (first 20):')
                unique_vals = gdf[col].unique()
                for i, val in enumerate(unique_vals[:20]):
                    print(f"  {i+1}. {val}")
                if len(unique_vals) > 20:
                    print(f"  ... and {len(unique_vals) - 20} more")
        
        # Look for AMI-related columns
        print('\nChecking for AMI-related columns:')
        ami_cols = [col for col in gdf.columns if 'ami' in col.lower() or 'median' in col.lower() or 'income' in col.lower()]
        print(f'AMI-related columns: {ami_cols}')
        
        # Show sample AMI values
        if ami_cols:
            print('\nSample AMI values:')
            for col in ami_cols[:5]:  # Show first 5 AMI columns
                if col != 'geometry':
                    print(f'\n{col}:')
                    print(gdf[col].head())
        
        # Check if there's a specific county identifier
        print('\nLooking for county identifiers (FIPS codes, etc.):')
        id_cols = [col for col in gdf.columns if 'fips' in col.lower() or 'code' in col.lower() or 'id' in col.lower()]
        print(f'Identifier columns: {id_cols}')
        
        if id_cols:
            for col in id_cols:
                if col != 'geometry':
                    print(f'\nSample values from {col}:')
                    print(gdf[col].head())
        
        return gdf
        
    except Exception as e:
        print(f'Error loading GeoPackage: {e}')
        return None

if __name__ == "__main__":
    inspect_hud_ami_gpkg()