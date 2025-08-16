#!/usr/bin/env python3
"""
Get ACS Poverty Rate for Concord Census Tract 3280 (06013328000)
Uses the existing Census ACS poverty data system
"""

import requests
import pandas as pd
import sys
import os

# Census API Key from the existing system
API_KEY = '06ece0121263282cd9ffd753215b007b8f9a3dfc'

def get_poverty_rate_for_tract(geoid, state_fips='06', year=2022):
    """
    Get poverty rate for a specific census tract using ACS 5-year estimates
    """
    print(f"📊 Fetching poverty data for Census Tract GEOID: {geoid}")
    
    # Extract county and tract from full GEOID
    # GEOID format: SSCCCTTTTTT (SS=state, CCC=county, TTTTTT=tract)
    if len(geoid) == 11:
        county_fips = geoid[2:5]  # Characters 3-5 are county
        tract_code = geoid[5:]    # Characters 6-11 are tract
    else:
        print(f"❌ Invalid GEOID format: {geoid}")
        return None
    
    # Use 2022 ACS 5-year estimates
    url = f'https://api.census.gov/data/{year}/acs/acs5'
    
    # Census variables:
    # B17001_002E = Income in the past 12 months below poverty level
    # B17001_001E = Total population for whom poverty status is determined
    params = {
        'get': 'NAME,B17001_001E,B17001_002E',
        'for': f'tract:{tract_code}',
        'in': f'state:{state_fips} county:{county_fips}',
        'key': API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if len(data) < 2:
            print("❌ No data returned from Census API")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])
        
        if len(df) == 0:
            print("❌ No tract data found")
            return None
        
        row = df.iloc[0]
        
        # Calculate poverty percentage with error handling
        total_pop = pd.to_numeric(row['B17001_001E'], errors='coerce')
        poverty_pop = pd.to_numeric(row['B17001_002E'], errors='coerce')
        
        if pd.isna(total_pop) or pd.isna(poverty_pop) or total_pop == 0:
            print("❌ Invalid population data")
            return None
        
        poverty_rate = (poverty_pop / total_pop) * 100
        
        result = {
            'geoid': geoid,
            'name': row['NAME'],
            'total_population': int(total_pop),
            'poverty_population': int(poverty_pop),
            'poverty_rate': round(poverty_rate, 2),
            'year': year
        }
        
        print(f"✅ Successfully retrieved poverty data:")
        print(f"   Census Tract: {result['name']}")
        print(f"   Total Population: {result['total_population']:,}")
        print(f"   Population Below Poverty: {result['poverty_population']:,}")
        print(f"   Poverty Rate: {result['poverty_rate']}%")
        
        # Determine LIHTC low poverty bonus eligibility
        lihtc_eligible = result['poverty_rate'] <= 20.0
        print(f"   CTCAC Low Poverty Bonus Eligible: {'✅ YES' if lihtc_eligible else '❌ NO'} (≤20% threshold)")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return None

def check_existing_data_files():
    """Check if we already have California poverty data downloaded"""
    data_dir = '/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/Lvg_Bond_Execution/Data Sets/Poverty Rate Census Tracts (ACS)'
    
    ca_files = [
        'poverty_tracts_CA_2022.gpkg',
        'poverty_summary_CA_2022.csv'
    ]
    
    existing_files = []
    for filename in ca_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            existing_files.append(filepath)
    
    if existing_files:
        print(f"📁 Found existing California poverty data files:")
        for f in existing_files:
            print(f"   {f}")
        
        # Try to read from CSV if available
        csv_file = os.path.join(data_dir, 'poverty_summary_CA_2022.csv')
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                # Look for our tract
                tract_data = df[df['GEOID'] == '06013328000']
                if not tract_data.empty:
                    row = tract_data.iloc[0]
                    print(f"✅ Found tract data in existing CSV:")
                    print(f"   Poverty Rate: {row['poverty_rate']}%")
                    return row['poverty_rate']
            except Exception as e:
                print(f"⚠️  Could not read existing CSV: {e}")
    
    return None

def main():
    """Main function to get poverty rate for Concord tract"""
    print("🏠 Census Tract Poverty Rate Lookup")
    print("2451 Olivera Road, Concord, CA 94520")
    print("=" * 60)
    
    # Our specific tract GEOID
    concord_geoid = '06013328000'  # California (06) + Contra Costa County (013) + Tract (328000)
    
    # First check if we already have the data
    existing_rate = check_existing_data_files()
    if existing_rate is not None:
        print(f"\n🎯 FINAL RESULT: {existing_rate}% poverty rate")
        return existing_rate
    
    # If not found in existing data, fetch from API
    print(f"\n🔍 Fetching fresh data from Census API...")
    result = get_poverty_rate_for_tract(concord_geoid)
    
    if result:
        print(f"\n🎯 FINAL RESULT: {result['poverty_rate']}% poverty rate")
        return result['poverty_rate']
    else:
        print(f"\n❌ Could not retrieve poverty rate")
        return None

if __name__ == "__main__":
    main()