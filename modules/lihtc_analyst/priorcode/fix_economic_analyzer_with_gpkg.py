#!/usr/bin/env python3
"""
Fix the Texas Economic Viability Analyzer to use the HUD AMI GeoPackage
which has proper county names and all the required data
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path

def create_county_lookup_from_gpkg():
    """Create a county lookup dictionary from the GeoPackage"""
    
    # Load the GeoPackage
    gpkg_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD_AMI_Geographic/States/tx_counties_hud_ami_2025.gpkg'
    gdf = gpd.read_file(gpkg_path)
    
    # Create lookup dictionaries for various county name formats
    lookups = {}
    
    # Create lookups by different name formats
    for idx, row in gdf.iterrows():
        # Get base county name (without "County" suffix)
        base_name = row['county_name_census']
        full_name = row['county_name']  # e.g., "Harris County"
        
        # Store the row data (without geometry for easier handling)
        row_data = {
            'county_name': row['county_name'],
            'county_name_census': row['county_name_census'],
            'hud_area_name': row['hud_area_name'],
            'county_fips': row['county_fips'],
            'median_ami_2025': row['median_ami_2025'],
            'rent_2br_50pct': row['rent_2br_50pct'],
            'rent_2br_60pct': row['rent_2br_60pct'],
            'rent_2br_80pct': row['rent_2br_80pct'],
            'is_metro': row['is_metro'],
            'metro_status': row['metro_status']
        }
        
        # Add various lookup keys
        lookups[base_name.upper()] = row_data
        lookups[full_name.upper()] = row_data
        lookups[base_name.lower()] = row_data
        lookups[full_name.lower()] = row_data
        lookups[base_name] = row_data
        lookups[full_name] = row_data
    
    return lookups, gdf

def test_lookup():
    """Test the lookup functionality"""
    lookups, gdf = create_county_lookup_from_gpkg()
    
    print("Testing county lookups:")
    print("="*50)
    
    test_counties = ['Harris', 'HARRIS', 'harris county', 'Dallas', 'Travis County', 'Bexar']
    
    for county in test_counties:
        result = lookups.get(county.upper())
        if result:
            print(f"\nCounty: {county}")
            print(f"  Found as: {result['county_name']}")
            print(f"  HUD Area: {result['hud_area_name']}")
            print(f"  2BR 60% Rent: ${result['rent_2br_60pct']:,.0f}")
            print(f"  Metro Status: {result['metro_status']}")
        else:
            print(f"\nCounty: {county} - NOT FOUND")
    
    # Show some statistics
    print("\n" + "="*50)
    print("DATASET STATISTICS:")
    print(f"Total counties: {len(gdf)}")
    print(f"Metro counties: {len(gdf[gdf['is_metro'] == 1])}")
    print(f"Non-metro counties: {len(gdf[gdf['is_metro'] == 0])}")
    print(f"Average 2BR 60% rent: ${gdf['rent_2br_60pct'].mean():,.0f}")
    print(f"Highest 2BR 60% rent: ${gdf['rent_2br_60pct'].max():,.0f} ({gdf.loc[gdf['rent_2br_60pct'].idxmax(), 'county_name']})")
    print(f"Lowest 2BR 60% rent: ${gdf['rent_2br_60pct'].min():,.0f} ({gdf.loc[gdf['rent_2br_60pct'].idxmin(), 'county_name']})")

def create_fixed_analyzer():
    """Create a fixed version of the economic analyzer that uses the GeoPackage"""
    
    # Read the original analyzer
    original_path = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/texas_economic_viability_analyzer.py'
    with open(original_path, 'r') as f:
        content = f.read()
    
    # Create the modifications
    modifications = """
    def load_data(self):
        \"\"\"Load all required data files\"\"\"
        print("Loading data files...")
        
        # Load HUD AMI data from GeoPackage
        gpkg_path = self.base_path / 'HUD_AMI_Geographic' / 'States' / 'tx_counties_hud_ami_2025.gpkg'
        print(f"Loading HUD data from: {gpkg_path}")
        self.texas_hud_gdf = gpd.read_file(gpkg_path)
        
        # Create county lookup dictionary
        self.county_lookup = {}
        for idx, row in self.texas_hud_gdf.iterrows():
            # Multiple lookup keys for flexibility
            base_name = row['county_name_census']
            full_name = row['county_name']
            
            # Store by various formats
            for key in [base_name.upper(), full_name.upper(), base_name, full_name]:
                self.county_lookup[key] = row
        
        print(f"Loaded {len(self.texas_hud_gdf)} Texas counties from HUD GeoPackage")
        
        # Load land analysis results (from previous analyzer)
        land_files = list(Path('.').glob('CoStar_Land_Analysis_*.xlsx'))
        if land_files:
            latest_land = sorted(land_files)[-1]
            print(f"Loading land analysis from: {latest_land}")
            self.land_data = pd.read_excel(latest_land, sheet_name='All_Land_Analysis')
        else:
            raise FileNotFoundError("No land analysis files found. Run costar_land_specific_analyzer.py first.")
            
        print(f"Loaded {len(self.land_data)} properties from land analysis")
"""

    # Save the test version
    print("\nCreating test files to verify the fix...")
    
    # First, let's create a minimal test to verify the approach
    test_content = """#!/usr/bin/env python3
import geopandas as gpd
from pathlib import Path

# Test loading the GeoPackage
gpkg_path = Path('/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/HUD_AMI_Geographic/States/tx_counties_hud_ami_2025.gpkg')
print(f"Loading from: {gpkg_path}")
print(f"File exists: {gpkg_path.exists()}")

if gpkg_path.exists():
    gdf = gpd.read_file(gpkg_path)
    print(f"Loaded {len(gdf)} counties")
    print(f"Columns: {list(gdf.columns)}")
    
    # Test a specific county
    harris = gdf[gdf['county_name_census'].str.upper() == 'HARRIS']
    if not harris.empty:
        print(f"\\nHarris County 2BR 60% rent: ${harris.iloc[0]['rent_2br_60pct']:,.0f}")
"""
    
    with open('test_gpkg_load.py', 'w') as f:
        f.write(test_content)
    
    print("Created test_gpkg_load.py")
    print("\nNext steps:")
    print("1. Run: python3 test_gpkg_load.py")
    print("2. If successful, we'll create the fixed analyzer")

if __name__ == "__main__":
    # Test the lookup functionality
    test_lookup()
    
    # Create the fixed analyzer
    create_fixed_analyzer()