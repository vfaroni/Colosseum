#!/usr/bin/env python3
"""
Explore CTCAC Opportunity Data Structure
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path

def explore_opportunity_data():
    """Explore the structure of the opportunity data"""
    
    filepath = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/CTCAC_2025_Opp_MAP_shapefile/final_opp_2025_public.gpkg")
    
    print("🔍 Exploring CTCAC Opportunity Data Structure")
    print("=" * 60)
    
    # Load the data
    gdf = gpd.read_file(filepath)
    
    print(f"Total areas: {len(gdf)}")
    print(f"Columns: {list(gdf.columns)}")
    
    # Check opportunity categories
    if 'oppcat' in gdf.columns:
        print(f"\n📊 'oppcat' (Opportunity Category) values:")
        oppcat_counts = gdf['oppcat'].value_counts()
        for category, count in oppcat_counts.items():
            print(f"   {category}: {count} areas")
    
    # Check opportunity scores
    if 'oppscore' in gdf.columns:
        print(f"\n📊 'oppscore' (Opportunity Score) statistics:")
        print(f"   Min: {gdf['oppscore'].min()}")
        print(f"   Max: {gdf['oppscore'].max()}")
        print(f"   Mean: {gdf['oppscore'].mean():.2f}")
        print(f"   Unique values: {sorted(gdf['oppscore'].unique())}")
    
    # Sample some data
    print(f"\n📋 Sample records:")
    sample_cols = ['county_name', 'oppcat', 'oppscore'] if all(col in gdf.columns for col in ['county_name', 'oppcat', 'oppscore']) else ['oppcat', 'oppscore']
    if sample_cols[0] in gdf.columns:
        print(gdf[sample_cols].head(10))
    
    # Check for Contra Costa County specifically
    if 'county_name' in gdf.columns:
        contra_costa = gdf[gdf['county_name'].str.contains('Contra Costa', case=False, na=False)]
        print(f"\n🎯 Contra Costa County areas: {len(contra_costa)}")
        if len(contra_costa) > 0:
            print("Opportunity categories in Contra Costa:")
            cc_cats = contra_costa['oppcat'].value_counts()
            for category, count in cc_cats.items():
                print(f"   {category}: {count} areas")

if __name__ == "__main__":
    explore_opportunity_data()