#!/usr/bin/env python3
"""
Test AMI Fix - First 10 Sites
"""

from streamlined_comprehensive_analyzer import StreamlinedComprehensiveLIHTCAnalyzer
import pandas as pd

def test_ami_fix():
    print("🧪 TESTING AMI FIX - First 10 sites")
    print("=" * 60)
    
    analyzer = StreamlinedComprehensiveLIHTCAnalyzer()
    
    # Load base data and limit to first 10 sites
    df = pd.read_excel(analyzer.qct_dda_file)
    test_df = df.head(10).copy()
    
    print(f"📊 Testing AMI integration with {len(test_df)} sites")
    
    # Just test Step 3: AMI integration
    try:
        ami_df = pd.read_excel(analyzer.hud_ami_file)
        texas_ami = ami_df[ami_df['State'] == 'TX']
        
        # Initialize AMI columns
        ami_columns = ['HUD_Area_Name', '4_Person_AMI_100pct', 'AMI_60_1BR', 'AMI_60_2BR', 'AMI_60_3BR', 'AMI_60_4BR']
        for col in ami_columns:
            test_df[col] = 'MISSING'
        
        ami_matched = 0
        county_geocoded = 0
        for idx, site in test_df.iterrows():
            city = str(site.get('City', '')).lower()
            lat = site.get('Latitude')
            lng = site.get('Longitude')
            
            print(f"\n   Site {idx}: {city.title()}")
            
            # First try metro area matching by city
            ami_match = None
            if 'austin' in city:
                ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Austin', case=False, na=False)]
                print(f"      Metro match: Austin ({len(ami_match)} results)")
            elif any(x in city for x in ['dallas', 'plano', 'frisco', 'richardson']):
                ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Dallas', case=False, na=False)]
                print(f"      Metro match: Dallas ({len(ami_match)} results)")
            elif any(x in city for x in ['fort worth', 'arlington']):
                ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Fort Worth', case=False, na=False)]
                print(f"      Metro match: Fort Worth ({len(ami_match)} results)")
            elif any(x in city for x in ['houston', 'katy', 'pearland']):
                ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('Houston', case=False, na=False)]
                print(f"      Metro match: Houston ({len(ami_match)} results)")
            elif 'san antonio' in city:
                ami_match = texas_ami[texas_ami['HUD_Area'].str.contains('San Antonio', case=False, na=False)]
                print(f"      Metro match: San Antonio ({len(ami_match)} results)")
            
            # If no metro match, try county-based lookup using geocoding
            if (ami_match is None or len(ami_match) == 0) and pd.notna(lat) and pd.notna(lng):
                print(f"      No metro match, trying county geocoding...")
                county = analyzer.get_county_from_coordinates(lat, lng)
                if county:
                    county_geocoded += 1
                    print(f"      Geocoded county: {county}")
                    # Try exact county match
                    county_match = texas_ami[texas_ami['County'].str.contains(county, case=False, na=False)]
                    if len(county_match) > 0:
                        ami_match = county_match
                        print(f"      County match found: {len(county_match)} results")
            
            if ami_match is not None and len(ami_match) > 0:
                ami_record = ami_match.iloc[0]
                test_df.loc[idx, 'HUD_Area_Name'] = ami_record.get('HUD_Area', 'MISSING')
                test_df.loc[idx, '4_Person_AMI_100pct'] = ami_record.get('Median_AMI_100pct', 'MISSING')
                test_df.loc[idx, 'AMI_60_1BR'] = ami_record.get('60pct_AMI_1BR_Rent', 'MISSING')
                test_df.loc[idx, 'AMI_60_2BR'] = ami_record.get('60pct_AMI_2BR_Rent', 'MISSING')
                test_df.loc[idx, 'AMI_60_3BR'] = ami_record.get('60pct_AMI_3BR_Rent', 'MISSING')
                test_df.loc[idx, 'AMI_60_4BR'] = ami_record.get('60pct_AMI_4BR_Rent', 'MISSING')
                ami_matched += 1
                print(f"      ✅ AMI data assigned: {ami_record['HUD_Area']}")
            else:
                print(f"      ❌ No AMI match found")
        
        print(f"\n✅ AMI TEST COMPLETE: {ami_matched}/{len(test_df)} sites matched ({county_geocoded} counties geocoded)")
        
        # Show results
        print(f"\nAMI RESULTS:")
        for idx, site in test_df.iterrows():
            city = site.get('City', 'Unknown')
            hud_area = site.get('HUD_Area_Name', 'MISSING')
            ami_2br = site.get('AMI_60_2BR', 'MISSING')
            print(f"  {city}: {hud_area} - 2BR Rent: ${ami_2br}")
        
        return test_df
        
    except Exception as e:
        print(f"❌ AMI integration error: {e}")
        return None

if __name__ == "__main__":
    result = test_ami_fix()