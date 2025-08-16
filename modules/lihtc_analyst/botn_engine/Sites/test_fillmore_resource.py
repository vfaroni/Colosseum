#!/usr/bin/env python3
"""Test Fillmore coordinates against real CTCAC data"""

import sys
sys.path.insert(0, '../src/analyzers')
import geopandas as gpd
from shapely.geometry import Point

print('🔍 TESTING FILLMORE COORDINATES AGAINST REAL CTCAC DATA')
print('=' * 60)

# Load California opportunity area data
data_path = '/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Data_Sets/california/CA_CTCAC_2025_Opp_MAP_shapefile/final_opp_2025_public.gpkg'

print('Loading California CTCAC opportunity area data...')
ca_data = gpd.read_file(data_path)

if ca_data.crs != 'EPSG:4326':
    ca_data = ca_data.to_crs('EPSG:4326')

print(f'Loaded {len(ca_data)} opportunity areas')

# Check available columns
print(f'\nAvailable columns: {list(ca_data.columns)}')

# Check resource categories available
if 'resource' in str(ca_data.columns).lower():
    print('\nResource categories in data:')
    for col in ca_data.columns:
        if 'resource' in col.lower():
            print(f'  {col}: {ca_data[col].unique()[:10]}')

# Test Fillmore coordinates (first site in portfolio)
fillmore_lat = 34.4098499
fillmore_lng = -118.9211499

print(f'\nTesting Fillmore coordinates: {fillmore_lat}, {fillmore_lng}')

point = Point(fillmore_lng, fillmore_lat)
intersects = ca_data[ca_data.contains(point)]

if not intersects.empty:
    result_row = intersects.iloc[0]
    print('✅ FOUND IN OPPORTUNITY AREA DATA:')
    
    # Print all columns for the match
    print('\nAll data for this area:')
    for col, val in result_row.items():
        if col != 'geometry':
            print(f'  {col}: {val}')
            
    # Check if High/Highest Resource
    resource_cols = [col for col in result_row.index if 'resource' in col.lower()]
    if resource_cols:
        for col in resource_cols:
            val = str(result_row[col]).upper()
            if 'HIGH' in val:
                print(f'\n🎯 RESOURCE STATUS: {val}')
                if 'HIGHEST' in val:
                    print('✅ HIGHEST RESOURCE - Should be KEPT')
                elif 'HIGH' in val and 'HIGHEST' not in val:
                    print('✅ HIGH RESOURCE - Should be KEPT') 
                else:
                    print('❌ NOT High/Highest Resource - Should be ELIMINATED')
            else:
                print(f'\n❌ RESOURCE STATUS: {val} - Should be ELIMINATED')
else:
    print('❌ NOT FOUND in opportunity area data')
    print('This confirms Fillmore is NOT in High/Highest Resource Area')
    print('Phase 3 filtering ERROR: Should have been eliminated')