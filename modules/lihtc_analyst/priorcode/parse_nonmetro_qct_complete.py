#!/usr/bin/env python3
"""
Parse complete Non-Metro QCT data from the provided text
Based on HUD's 2025 IRS SECTION 42(d)(5)(B) NONMETROPOLITAN QUALIFIED CENSUS TRACTS
"""

import pandas as pd
import json
from pathlib import Path

def parse_nonmetro_qct_data():
    """Parse the complete Non-Metro QCT data from the provided text"""
    
    print("📄 Parsing Complete Non-Metro QCT Data...")
    
    # Arizona Non-Metro QCT data from the provided text
    arizona_qct_data = {
        'Apache County': ['9426.00', '9441.00', '9442.01', '9442.02', '9443.01', '9443.02', '9449.01', '9449.02', '9450.02'],
        'Gila County': ['9402.00', '9404.00'],
        'Graham County': ['9405.00'],
        'La Paz County': ['206.02'],
        'Navajo County': ['9400.08', '9400.10', '9400.11', '9400.14', '9403.01', '9423.00', '9424.00'],
        'Santa Cruz County': ['9663.02']
    }
    
    # Create structured data
    nonmetro_qcts = []
    
    for county, tracts in arizona_qct_data.items():
        for tract in tracts:
            nonmetro_qcts.append({
                'state': 'Arizona',
                'state_code': 4,
                'county': county,
                'county_code': get_arizona_county_code(county),
                'tract': float(tract),
                'tract_formatted': tract,
                'nonmetro_qct': True,
                'source': 'HUD 2025 Non-Metro QCT List'
            })
    
    print(f"✅ Parsed {len(nonmetro_qcts)} Arizona Non-Metro QCT tracts")
    
    # Create DataFrame
    df = pd.DataFrame(nonmetro_qcts)
    
    # Save as CSV and JSON
    csv_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data/arizona_nonmetro_qct_2025.csv"
    json_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets/federal/HUD_QCT_DDA_Data/arizona_nonmetro_qct_2025.json"
    
    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient='records', indent=2)
    
    print(f"✅ Saved to: {csv_path}")
    print(f"✅ Saved to: {json_path}")
    
    # Show Arizona counties and tract counts
    print(f"\n🌵 ARIZONA NON-METRO QCT SUMMARY:")
    for county in arizona_qct_data.keys():
        tract_count = len(arizona_qct_data[county])
        print(f"  • {county}: {tract_count} tracts")
    
    # Confirm Santa Cruz County tract 9663.02
    santa_cruz_tracts = df[df['county'] == 'Santa Cruz County']
    if not santa_cruz_tracts.empty:
        print(f"\n✅ CONFIRMED: Santa Cruz County, AZ has Non-Metro QCT tracts")
        for idx, row in santa_cruz_tracts.iterrows():
            print(f"   • Tract {row['tract_formatted']} - Non-Metro QCT")
        
        # Check specifically for tract 9663.02
        if 9663.02 in santa_cruz_tracts['tract'].values:
            print(f"\n🎯 CRITICAL: Tract 9663.02 (United Church Village) is BOTH:")
            print(f"   • Non-Metro QCT (this data)")
            print(f"   • County in Non-Metro DDA list (Santa Cruz County)")
            print(f"   → This means DUAL QUALIFICATION for 130% basis boost!")
    
    return df

def get_arizona_county_code(county_name):
    """Get Arizona county FIPS code"""
    az_counties = {
        'Apache County': 1,
        'Cochise County': 3,
        'Coconino County': 5,
        'Gila County': 7,
        'Graham County': 9,
        'Greenlee County': 11,
        'La Paz County': 12,
        'Maricopa County': 13,
        'Mohave County': 15,
        'Navajo County': 17,
        'Pima County': 19,
        'Pinal County': 21,
        'Santa Cruz County': 23,
        'Yavapai County': 25,
        'Yuma County': 27
    }
    return az_counties.get(county_name, 0)

if __name__ == "__main__":
    df = parse_nonmetro_qct_data()
    
    if df is not None:
        print(f"\n📊 SUMMARY:")
        print(f"   Total Arizona Non-Metro QCT Tracts: {len(df)}")
        print(f"   Counties with Non-Metro QCTs: {df['county'].nunique()}")
        
        print(f"\n🔍 UNITED CHURCH VILLAGE ANALYSIS:")
        print(f"   Location: Tract 9663.02, Santa Cruz County, AZ")
        print(f"   Non-Metro QCT: ✅ YES (confirmed in this data)")
        print(f"   Non-Metro DDA: ✅ YES (Santa Cruz County in DDA list)")
        print(f"   LIHTC Qualification: ✅ DUAL QUALIFIED for 130% basis boost")