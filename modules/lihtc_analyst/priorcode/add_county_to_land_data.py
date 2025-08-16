#!/usr/bin/env python3
"""
Add county information to CoStar land data using spatial join with HUD AMI GeoPackage
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime

def add_counties_to_land_data():
    """Add county names to land analysis data using spatial join"""
    
    print("Loading land analysis data...")
    land_df = pd.read_excel('CoStar_Land_Analysis_20250616_203751.xlsx', sheet_name='All_Land_Analysis')
    print(f"Loaded {len(land_df)} properties")
    
    print("Loading Texas counties HUD AMI data...")
    counties_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD_AMI_Geographic/States/tx_counties_hud_ami_2025.gpkg'
    counties_gdf = gpd.read_file(counties_path)
    print(f"Loaded {len(counties_gdf)} Texas counties")
    
    # Create geometry from coordinates
    print("Creating geometry from coordinates...")
    geometry = [Point(xy) for xy in zip(land_df['Longitude'], land_df['Latitude'])]
    land_gdf = gpd.GeoDataFrame(land_df, geometry=geometry, crs='EPSG:4326')
    
    # Ensure same CRS
    counties_gdf = counties_gdf.to_crs('EPSG:4326')
    
    print("Performing spatial join...")
    # Spatial join to get county for each property
    joined = gpd.sjoin(land_gdf, counties_gdf[['county_name', 'hud_area_name', 'median_ami_2025', 
                                              'rent_2br_50pct', 'rent_2br_60pct', 'rent_2br_80pct', 'geometry']], 
                       how='left', predicate='within')
    
    # Drop duplicate geometry column and convert back to DataFrame
    joined = joined.drop(columns=['geometry'])
    
    # Count successful matches
    matched = joined['county_name'].notna().sum()
    print(f"Successfully matched {matched} of {len(joined)} properties to counties")
    
    if matched < len(joined):
        unmatched = joined[joined['county_name'].isna()]
        print(f"Unmatched properties (check coordinates):")
        for idx, row in unmatched[['Address', 'City', 'Latitude', 'Longitude']].head(5).iterrows():
            print(f"  {row['Address']}, {row['City']} - {row['Latitude']}, {row['Longitude']}")
    
    # Save enhanced dataset
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'CoStar_Land_Analysis_With_Counties_{timestamp}.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        joined.to_excel(writer, sheet_name='Land_Analysis_With_Counties', index=False)
        
        # Also save just the county matching for reference
        county_summary = joined.groupby('county_name').agg({
            'Address': 'count',
            'median_ami_2025': 'first',
            'rent_2br_60pct': 'first'
        }).rename(columns={'Address': 'Property_Count'}).reset_index()
        county_summary.to_excel(writer, sheet_name='County_Summary', index=False)
    
    print(f"\nEnhanced dataset saved to: {output_file}")
    print(f"Properties by county:")
    county_counts = joined['county_name'].value_counts().head(10)
    for county, count in county_counts.items():
        print(f"  {county}: {count} properties")
    
    return output_file

if __name__ == "__main__":
    add_counties_to_land_data()