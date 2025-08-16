#!/usr/bin/env python3
"""
Fix the tract lookup by properly converting tract numbers
"""

import pandas as pd

def fix_tract_lookup():
    """Fix the tract number conversion and lookup"""
    
    # The Census API returned tract: 966302
    # But our data shows tract: 9663.02
    # We need to convert 966302 to 9663.02 format
    
    base_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
    excel_file = f"{base_path}/qct_data_2025.xlsx"
    
    df = pd.read_excel(excel_file)
    
    # The tract from Census API: 966302
    # Convert to the format used in the Excel file: 9663.02
    census_tract = "966302"
    
    # The format appears to be: insert decimal point 2 positions from the right
    if len(census_tract) == 6:
        formatted_tract = float(census_tract[:4] + "." + census_tract[4:])
    else:
        formatted_tract = float(census_tract)
    
    print("="*70)
    print("CORRECTED TRACT LOOKUP")
    print("="*70)
    print(f"Census API tract: {census_tract}")
    print(f"Formatted tract: {formatted_tract}")
    
    # Look for this tract in Santa Cruz County, Arizona
    state_code = 4
    county_code = 23
    
    matching_tract = df[
        (df['state'] == state_code) & 
        (df['county'] == county_code) & 
        (df['tract'] == formatted_tract)
    ]
    
    if len(matching_tract) > 0:
        print(f"\n✅ FOUND TRACT IN QCT DATABASE!")
        record = matching_tract.iloc[0]
        print(f"State: {record['state']} (Arizona)")
        print(f"County: {record['county']} (Santa Cruz)")  
        print(f"Tract: {record['tract']}")
        print(f"QCT Status: {record['qct']} ({'✅ QCT DESIGNATED' if record['qct'] == 1 else '❌ Not QCT'})")
        
        # Show additional data
        print(f"\nAdditional Information:")
        print(f"Combined State-County: {record['stcnty']}")
        print(f"QCT ID: {record['qct_id']}")
        print(f"Metro/Non-metro: {record.get('metro', 'N/A')}")
        print(f"CBSA: {record.get('cbsa', 'N/A')}")
        
        if 'pov_rate_22' in record and pd.notna(record['pov_rate_22']):
            print(f"Poverty Rate 2022: {record['pov_rate_22']:.1%}")
        if 'pov_rate_21' in record and pd.notna(record['pov_rate_21']):
            print(f"Poverty Rate 2021: {record['pov_rate_21']:.1%}")
        if 'pov_rate_20' in record and pd.notna(record['pov_rate_20']):
            print(f"Poverty Rate 2020: {record['pov_rate_20']:.1%}")
            
        return record
    else:
        print(f"❌ Tract still not found!")
        print(f"Looking for: State={state_code}, County={county_code}, Tract={formatted_tract}")
        
        # Show all Santa Cruz County tracts
        santa_cruz = df[(df['state'] == 4) & (df['county'] == 23)]
        print(f"\nAll Santa Cruz County tracts:")
        print(santa_cruz[['state', 'county', 'tract', 'qct']].sort_values('tract'))
        
        return None

def check_surrounding_qct_areas():
    """Check for QCT areas in surrounding counties that might be shown on the HUD map"""
    
    base_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data"
    excel_file = f"{base_path}/qct_data_2025.xlsx"
    
    df = pd.read_excel(excel_file)
    
    print(f"\n" + "="*70)
    print("CHECKING SURROUNDING ARIZONA QCT AREAS")
    print("="*70)
    
    # Arizona QCT tracts
    az_qcts = df[(df['state'] == 4) & (df['qct'] == 1)]
    
    print(f"Total Arizona QCT tracts: {len(az_qcts)}")
    
    # Group by county to see distribution
    qct_by_county = az_qcts.groupby('county').size().sort_values(ascending=False)
    
    print(f"\nQCT tracts by Arizona county:")
    for county_code, count in qct_by_county.items():
        county_name = get_county_name(county_code)
        print(f"County {county_code:02d} ({county_name}): {count} QCT tracts")
        
    # Check if any are near the border with Mexico (similar latitude to Nogales)
    nogales_lat = 31.3713391
    
    print(f"\nThis might explain why the HUD map shows QCT areas 'around' Nogales")
    print(f"- The map might be showing QCT areas in neighboring counties")
    print(f"- Or there might be separate DDA (Difficult Development Area) designations")

def get_county_name(county_fips):
    """Get county name from FIPS code for Arizona counties"""
    
    # Arizona county FIPS codes and names
    az_counties = {
        1: "Apache", 3: "Cochise", 5: "Coconino", 7: "Gila", 9: "Graham",
        11: "Greenlee", 12: "La Paz", 13: "Maricopa", 15: "Mohave", 
        17: "Navajo", 19: "Pima", 21: "Pinal", 23: "Santa Cruz", 25: "Yavapai", 27: "Yuma"
    }
    
    return az_counties.get(county_fips, f"Unknown({county_fips})")

if __name__ == "__main__":
    record = fix_tract_lookup()
    check_surrounding_qct_areas()
    
    if record is not None and record['qct'] == 1:
        print(f"\n" + "="*70)
        print("🎉 CONCLUSION")
        print("="*70)
        print("✅ United Church Village Apartments IS in a QCT-designated census tract!")
        print(f"✅ Census Tract 9663.02 in Santa Cruz County, Arizona is QCT-designated")
        print("✅ This means the property qualifies for LIHTC QCT benefits")
    else:
        print(f"\n" + "="*70)
        print("CONCLUSION")
        print("="*70)
        print("❌ United Church Village Apartments is NOT in a QCT-designated area")
        print("❌ Census Tract 9663.02 in Santa Cruz County, Arizona is not QCT-designated")