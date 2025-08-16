#!/usr/bin/env python3
"""
Add county information to the land analysis data using coordinates and the HUD GeoPackage - FIXED VERSION
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point

def add_counties_to_land_data():
    """Add county information to land analysis data using spatial join"""
    
    # Load the HUD GeoPackage
    gpkg_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD_AMI_Geographic/States/tx_counties_hud_ami_2025.gpkg'
    print(f"Loading HUD GeoPackage from: {gpkg_path}")
    counties_gdf = gpd.read_file(gpkg_path)
    print(f"Loaded {len(counties_gdf)} counties")
    
    # Load land analysis results
    land_files = list(Path('.').glob('CoStar_Land_Analysis_*.xlsx'))
    if not land_files:
        print("No land analysis files found")
        return
        
    latest_land = sorted(land_files)[-1]
    print(f"Loading land analysis from: {latest_land}")
    land_data = pd.read_excel(latest_land, sheet_name='All_Land_Analysis')
    print(f"Loaded {len(land_data)} properties")
    
    # Check for coordinates
    if 'Latitude' not in land_data.columns or 'Longitude' not in land_data.columns:
        print("No Latitude/Longitude columns found in land data")
        return
    
    # Remove properties without coordinates
    valid_coords = land_data.dropna(subset=['Latitude', 'Longitude']).copy()
    print(f"Properties with valid coordinates: {len(valid_coords)}")
    
    if len(valid_coords) == 0:
        print("No properties have valid coordinates")
        return
    
    # Create GeoDataFrame from land data points
    print("Creating points from coordinates...")
    geometry = [Point(xy) for xy in zip(valid_coords.Longitude, valid_coords.Latitude)]
    land_gdf = gpd.GeoDataFrame(valid_coords, geometry=geometry, crs='EPSG:4326')
    
    # Ensure both GeoDataFrames use the same CRS
    counties_gdf = counties_gdf.to_crs('EPSG:4326')
    
    # Perform spatial join to find which county each property is in
    print("Performing spatial join to determine counties...")
    # Reset index to avoid duplicate issues
    land_gdf = land_gdf.reset_index(drop=True)
    land_with_counties = gpd.sjoin(land_gdf, counties_gdf, how='left', predicate='within')
    
    # Create the result dataframe
    result = land_data.copy()
    
    # Initialize new columns
    result['County'] = None
    result['County_Full_Name'] = None
    result['HUD_Area_Name'] = None
    result['Median_AMI_2025'] = None
    result['Rent_2BR_60pct'] = None
    
    # Map the results back to the original indices
    for i, row in land_with_counties.iterrows():
        original_idx = valid_coords.index[i]  # Get the original index
        
        if not pd.isna(row.get('county_name_census')):
            result.loc[original_idx, 'County'] = row['county_name_census']
            result.loc[original_idx, 'County_Full_Name'] = row['county_name']
            result.loc[original_idx, 'HUD_Area_Name'] = row['hud_area_name']
            result.loc[original_idx, 'Median_AMI_2025'] = row['median_ami_2025']
            result.loc[original_idx, 'Rent_2BR_60pct'] = row['rent_2br_60pct']
    
    # Show results
    print("\nCounty assignment results:")
    counties_found = result['County'].value_counts()
    print(counties_found.head(10))
    
    # Show properties without county assignment
    no_county = result[result['County'].isna()]
    print(f"\nProperties without county assignment: {len(no_county)}")
    if len(no_county) > 0:
        print("Sample properties without counties:")
        print(no_county[['Address', 'City', 'Latitude', 'Longitude']].head())
    
    # Save the updated data
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'CoStar_Land_Analysis_With_Counties_{timestamp}.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        result.to_excel(writer, sheet_name='All_Land_Analysis', index=False)
        
        # Also save just the properties with county data
        with_counties = result.dropna(subset=['County'])
        with_counties.to_excel(writer, sheet_name='Properties_With_Counties', index=False)
        
        # County summary
        if len(with_counties) > 0:
            county_summary = with_counties.groupby('County').agg({
                'Sale Price': ['count', 'mean', 'median'],
                'Land SF Gross': 'mean',
                'Rent_2BR_60pct': 'first',
                'Median_AMI_2025': 'first'
            }).round(0)
            county_summary.to_excel(writer, sheet_name='County_Summary')
    
    print(f"\nSaved updated data to: {output_file}")
    print(f"Properties with county data: {len(result.dropna(subset=['County']))}")
    
    # Show sample of successful assignments
    with_counties = result.dropna(subset=['County'])
    if len(with_counties) > 0:
        print("\nSample successful county assignments:")
        sample_cols = ['Address', 'City', 'County', 'County_Full_Name', 'Rent_2BR_60pct']
        print(with_counties[sample_cols].head())
    
    return result

if __name__ == "__main__":
    add_counties_to_land_data()