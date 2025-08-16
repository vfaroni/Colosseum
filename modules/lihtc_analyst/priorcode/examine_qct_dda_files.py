#!/usr/bin/env python3
"""
Examine QCT/DDA files to understand their structure and content
"""

import geopandas as gpd
import pandas as pd
import os

def examine_qct_dda_files():
    """Examine all QCT/DDA files to understand their structure"""
    
    base_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
    
    # List of files to examine
    files_to_check = [
        "HUD_DDA_QCT_2025_Combined.gpkg",
        "HUD QCT DDA 2025 Merged.gpkg", 
        "HUD_DDA-QCT_2025_Fixed_linework.gpkg",
        "HUD QCT DDA 2025 Reprojected.gpkg",
        "U-QCT-DDA_TX_Fix_Geo_2025.gpkg"
    ]
    
    for filename in files_to_check:
        file_path = os.path.join(base_path, filename)
        
        if os.path.exists(file_path):
            print(f"\n{'='*60}")
            print(f"EXAMINING: {filename}")
            print(f"{'='*60}")
            
            try:
                # Read the file
                gdf = gpd.read_file(file_path)
                
                print(f"Shape: {gdf.shape}")
                print(f"CRS: {gdf.crs}")
                print(f"\nColumns: {list(gdf.columns)}")
                
                # Show sample data
                print(f"\nFirst 3 rows:")
                print(gdf.head(3))
                
                # Check for QCT and DDA related fields
                qct_fields = [col for col in gdf.columns if 'qct' in col.lower()]
                dda_fields = [col for col in gdf.columns if 'dda' in col.lower()]
                
                if qct_fields:
                    print(f"\nQCT-related fields: {qct_fields}")
                if dda_fields:
                    print(f"\nDDA-related fields: {dda_fields}")
                    
                # Check unique values in key fields
                for col in gdf.columns:
                    if any(keyword in col.lower() for keyword in ['qct', 'dda', 'type', 'designation']):
                        unique_vals = gdf[col].unique()
                        print(f"\nUnique values in '{col}': {unique_vals[:10]}...")  # Show first 10
                        
                # Check for Arizona data specifically
                if 'STATE' in gdf.columns:
                    az_data = gdf[gdf['STATE'] == 'AZ']
                    print(f"\nArizona records: {len(az_data)}")
                elif 'state' in gdf.columns:
                    az_data = gdf[gdf['state'] == 'AZ']
                    print(f"\nArizona records: {len(az_data)}")
                elif 'State' in gdf.columns:
                    az_data = gdf[gdf['State'] == 'AZ']
                    print(f"\nArizona records: {len(az_data)}")
                else:
                    print("\nNo obvious state field found")
                    
            except Exception as e:
                print(f"Error reading {filename}: {e}")
        else:
            print(f"File not found: {filename}")

if __name__ == "__main__":
    examine_qct_dda_files()